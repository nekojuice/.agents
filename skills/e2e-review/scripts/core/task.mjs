// Execution workspace and task (round) folders: creation, current-task pointer, step log, result.json edits.
import { execFileSync } from 'node:child_process'
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { projectSkillVersion, skillVersion } from './project.mjs'
import { isSecretKey, redact } from './secrets.mjs'

export const WORKSPACE = 'e2e-review'

// Local time without zone, comparable with audit timestamps stored as local time.
export function localIso(d = new Date()) {
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().replace('Z', '')
}

function stamp(d = new Date()) {
    const p = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`
}

// A dev server runs the working tree, so uncommitted changes are part of the tested version.
function gitVersion(dir) {
    try {
        const head = execFileSync('git', ['-C', dir, 'rev-parse', '--short', 'HEAD'], { encoding: 'utf8' }).trim()
        const dirty = execFileSync('git', ['-C', dir, 'status', '--porcelain'], { encoding: 'utf8' }).split('\n').filter(Boolean).length
        return dirty ? `${head} (+${dirty} uncommitted)` : head
    } catch {
        return null
    }
}

// The workspace folder ignores itself so it never enters version control, wherever it is placed.
export function ensureWorkspace(parent) {
    const ws = join(resolve(parent), WORKSPACE)
    mkdirSync(ws, { recursive: true })
    if (!existsSync(join(ws, '.gitignore'))) writeFileSync(join(ws, '.gitignore'), '*\n')
    return ws
}

// Pointer to the current task folder, one per browser session. Lives in .e2e/state/ when assets exist, else in the workspace.
function pointerPath(project, session, ws) {
    const base = project.assets ? join(project.assets, 'state') : ws
    mkdirSync(base, { recursive: true })
    return join(base, `current-${session}`)
}

export function readCurrent(project, session, cwd = process.cwd()) {
    const candidates = [project.assets && join(project.assets, 'state', `current-${session}`), join(cwd, WORKSPACE, `current-${session}`)].filter(Boolean)
    for (const p of candidates) if (existsSync(p)) return readFileSync(p, 'utf8').trim()
    return null
}

export const KINDS = ['review', 'prep', 'init']

export function newTask({ project, env, session, parent, short = 'task', prev, basis, kind = 'review' }) {
    if (!KINDS.includes(kind)) throw new Error(`--kind must be one of: ${KINDS.join(', ')}`)
    const ws = ensureWorkspace(parent)
    const prevDir = prev ? resolve(prev) : null
    const prevResult = prevDir && existsSync(join(prevDir, 'result.json')) ? JSON.parse(readFileSync(join(prevDir, 'result.json'), 'utf8')) : null
    const round = (prevResult?.round ?? 0) + 1
    const dir = join(ws, `${stamp()}-r${String(round).padStart(2, '0')}-${short}`)
    for (const sub of ['shots', 'values', 'scratch', 'exchanges', 'data']) mkdirSync(join(dir, sub), { recursive: true })
    const versions = Object.fromEntries(Object.entries(env.repos ?? {}).map(([k, rel]) => [k, gitVersion(resolve(project.root, rel))]))
    const result = {
        task: { title: '', source: '', requester: '', kind },
        round,
        previousReport: prevDir,
        basis: basis ?? '',
        verdict: 'inconclusive',
        summary: '',
        env: {
            url: env.surfaces?.web?.baseUrl ?? env.baseUrl ?? '',
            surfaces: Object.fromEntries(Object.entries(env.surfaces ?? {}).map(([k, v]) => [k, { driver: v.driver, baseUrl: v.baseUrl ?? '' }])),
            dataScope: env.dataScope ?? '',
            accounts: [],
            browser: env.surfaces?.web?.browser ?? env.browser ?? '',
            startedAt: localIso(),
            versions,
            skillVersion: skillVersion(),
            projectVerifiedSkillVersion: projectSkillVersion(project.assets)
        },
        items: [],
        checks: [],
        uiFindings: [],
        writes: [],
        limits: [],
        issues: [],
        observations: [],
        reproduce: []
    }
    writeFileSync(join(dir, 'result.json'), JSON.stringify(result, null, 2))
    writeFileSync(pointerPath(project, session, ws), dir)
    return dir
}

// Dry runs log into <round>/dry/ so rehearsals never enter the formal step table or report.
export function logDir(dir, dry) {
    if (!dry) return dir
    const d = join(dir, 'dry')
    for (const sub of ['values', 'exchanges', 'data']) mkdirSync(join(d, sub), { recursive: true })
    return d
}

// One line per step: surface, kind (script | agent | adhoc), driver. Secret-looking keys are dropped and secret values redacted.
export function logStep(dir, step) {
    const args = Object.fromEntries(Object.entries(step.args ?? {}).filter(([k, v]) => v !== undefined && !isSecretKey(k)))
    appendFileSync(join(dir, 'steps.jsonl'), JSON.stringify(redact({ ...step, args })) + '\n')
}

export function readSteps(dir) {
    const p = join(dir, 'steps.jsonl')
    // Agent steps are written when they end, so order by start time for the timeline and audit attribution.
    const steps = existsSync(p) ? readFileSync(p, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l)) : []
    return steps.sort((a, b) => String(a.startedAt).localeCompare(String(b.startedAt)))
}

export const RESULT_ARRAYS = ['items', 'checks', 'uiFindings', 'writes', 'limits', 'issues', 'observations']

export function addToResult(dir, field, value) {
    if (!RESULT_ARRAYS.includes(field)) throw new Error(`field must be one of: ${RESULT_ARRAYS.join(', ')}`)
    const p = join(dir, 'result.json')
    const r = JSON.parse(readFileSync(p, 'utf8'))
    ;(r[field] ??= []).push(value)
    writeFileSync(p, JSON.stringify(r, null, 2))
    return r[field].length
}
