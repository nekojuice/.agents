// Execution workspace and task (round) folders: creation, current-task pointer, step log, result.json edits.
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { appendFileSync, existsSync, mkdirSync, readdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { projectReportLocale, projectSkillVersion, skillVersion } from './project.mjs'
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

// Uncommitted versioned files under .e2e/ (modified, deleted, or new and not ignored) with a content hash, keyed by the
// path relative to .e2e/. When .e2e/ does not exist yet but the project root is in a git repository (e.g. an init round),
// the snapshot is empty, so every file the round creates counts as added. Null only without git. Ignored files never appear.
export function assetsSnapshot(assets, root = null) {
    if (!assets || !existsSync(assets)) {
        if (!root) return null
        try {
            execFileSync('git', ['-C', root, 'rev-parse', '--is-inside-work-tree'], { stdio: ['ignore', 'pipe', 'ignore'] })
            return {}
        } catch {
            return null
        }
    }
    try {
        // git status covers staged and unstaged changes alike (a staged edit or a `git rm` still counts); its paths are
        // relative to the repository root, so the .e2e/ prefix is cut off.
        const git = (...a) => execFileSync('git', ['-C', assets, ...a], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })
        const prefix = git('rev-parse', '--show-prefix').trim()
        const parts = git('status', '--porcelain=v1', '-z', '--untracked-files=all', '--', '.').split('\0')
        const snap = {}
        for (let i = 0; i < parts.length; i++) {
            const e = parts[i]
            if (e.length < 4) continue
            const xy = e.slice(0, 2)
            const path = e.slice(3)
            // A rename or copy is followed by its source path; a rename is recorded as "<hash> from <old path>".
            const source = xy[0] === 'R' || xy[0] === 'C' ? parts[++i] : null
            if (!path.startsWith(prefix)) continue
            const rel = path.slice(prefix.length)
            const f = join(assets, rel)
            const state = existsSync(f) ? createHash('sha1').update(readFileSync(f)).digest('hex') : 'deleted'
            snap[rel] = xy[0] === 'R' && source?.startsWith(prefix) ? `${state} from ${source.slice(prefix.length)}` : state
        }
        return snap
    } catch {
        return null
    }
}

// .e2e/ files added or changed since the round started: entries whose state differs from the baseline taken at `new`.
// Null when no baseline could be taken (no git); the worker then lists the changes itself.
export function assetsChangedSince(baseline, assets, root = null) {
    if (!baseline) return null
    const now = assetsSnapshot(assets, root)
    if (!now) return null
    const paths = new Set([...Object.keys(now), ...Object.keys(baseline)])
    // A file changed at the start and committed or reverted since then is no longer listed by git; it counts as unchanged.
    // Files deleted in this round are listed with " (deleted)", renamed ones as "<old path> → <new path>".
    const label = (p) => {
        if (now[p] === 'deleted') return `${p} (deleted)`
        const m = String(now[p]).match(/ from (.+)$/)
        return m ? `${m[1]} → ${p}` : p
    }
    return [...paths].filter((p) => p in now && now[p] !== baseline[p]).sort().map(label)
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
        task: { title: '', source: '', requester: '', kind, locale: projectReportLocale(project.assets) },
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
            projectVerifiedSkillVersion: projectSkillVersion(project.assets),
            // Baseline for assets_changed: .e2e/ files already uncommitted when the round started (null without git).
            assetsBaseline: assetsSnapshot(project.assets ?? join(project.root, '.e2e'), project.root)
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

// Side runs never enter the formal step table or verdict: dry runs log into <round>/dry/<name>/,
// rehearsals (real operation that is cancelled before saving) into <round>/rehearse/<name>/.
export const SIDE_MODES = ['dry', 'rehearse']

// Folder name for a scenario, fragment, or step: keeps letters of any script (e.g. Chinese), replaces whitespace and
// characters file systems reject. Every side folder of one name goes through here, so results, steps, and values stay together.
export function slugName(name) {
    return String(name ?? '').replace(/[\s<>:"/\\|?*\u0000-\u001f]+/g, '-').replace(/^[-.]+|[-.]+$/g, '') || 'run'
}

export function logDir(dir, mode = null, name = 'run') {
    if (!mode) return dir
    if (!SIDE_MODES.includes(mode)) throw new Error(`unknown log mode: ${mode}`)
    const d = join(dir, mode, slugName(name))
    for (const sub of ['values', 'exchanges', 'data']) mkdirSync(join(d, sub), { recursive: true })
    return d
}

// Steps of every dry run and rehearsal in a round (including a 1.2-style flat dry/steps.jsonl), ordered by start.
export function readSideSteps(dir) {
    const out = []
    for (const mode of SIDE_MODES) {
        const base = join(dir, mode)
        if (!existsSync(base)) continue
        out.push(...readSteps(base).map((s) => ({ ...s, mode })))
        for (const sub of readdirSync(base, { withFileTypes: true }).filter((d) => d.isDirectory()))
            out.push(...readSteps(join(base, sub.name)).map((s) => ({ ...s, mode, name: sub.name })))
    }
    return out.sort((a, b) => String(a.startedAt).localeCompare(String(b.startedAt)))
}

// values/<name>.json; an existing file of the same name is kept as <name>.<n>.json (n = next free number).
// Returns the path the old file was moved to, or null.
export function writeValue(dir, name, value) {
    const vd = join(dir, 'values')
    mkdirSync(vd, { recursive: true })
    const p = join(vd, `${name}.json`)
    let kept = null
    if (existsSync(p)) {
        let n = 1
        while (existsSync(join(vd, `${name}.${n}.json`))) n += 1
        kept = `values/${name}.${n}.json`
        renameSync(p, join(vd, `${name}.${n}.json`))
    }
    writeFileSync(p, JSON.stringify(redact(value), null, 2))
    return kept
}

// Read the latest value file of a name, or null.
export function readValue(dir, name) {
    const p = join(dir, 'values', `${name}.json`)
    return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : null
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
export const VERDICTS = ['pass', 'fail', 'inconclusive']
export const SOURCES = ['script', 'value', 'visual', 'not-run', 'run-error']
export const VIAS = ['web', 'api', 'db']

const text = (v) => typeof v === 'string' && v.trim() !== ''
const SHAPES = {
    items: (v) => [['id', text(String(v.id ?? ''))], ['title', text(v.title)], ['checks (array of check ids)', Array.isArray(v.checks)]],
    checks: (v) => [['id', text(String(v.id ?? ''))], ['title', text(v.title)], [`verdict (${VERDICTS.join('|')})`, VERDICTS.includes(v.verdict)], [`by (${SOURCES.join('|')})`, SOURCES.includes(v.by)], [`via (${VIAS.join('|')} or null)`, v.via == null || VIAS.includes(v.via)]],
    uiFindings: (v) => [['type', text(v.type)], ['where', text(v.where)], ['what or rule', text(v.what) || text(v.rule)]],
    writes: (v) => [['what', text(v.what)], ['where', text(v.where)], ['how', text(v.how)]],
    limits: (v) => [['check', text(String(v.check ?? ''))], ['limit', text(v.limit)], ['retest', text(v.retest)]]
}

// Shape check for one entry of a result array; throws with the missing or invalid fields.
export function validateEntry(field, value) {
    if (!RESULT_ARRAYS.includes(field)) throw new Error(`field must be one of: ${RESULT_ARRAYS.join(', ')}`)
    if (field === 'issues' || field === 'observations') {
        if (!text(value) && !(value && typeof value === 'object' && text(value.text))) throw new Error(`${field} entries are non-empty strings`)
        return value
    }
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${field} entries are objects; see references/report-spec.md "result.json"`)
    const bad = SHAPES[field](value).filter(([, ok]) => !ok).map(([k]) => k)
    if (bad.length) throw new Error(`${field} entry is missing or has invalid: ${bad.join(', ')}`)
    return value
}

// The one verdict rule: any fail → fail; else any inconclusive → inconclusive; else pass. Null when there are no checks.
export function verdictOf(checks = []) {
    if (!checks.length) return null
    const failed = checks.filter((c) => c.verdict === 'fail').length
    const inconclusive = checks.filter((c) => c.verdict === 'inconclusive').length
    return { verdict: failed ? 'fail' : inconclusive ? 'inconclusive' : 'pass', stats: { checks: checks.length, failed, inconclusive } }
}

// Read-modify-write of result.json.
export function updateResult(dir, fn) {
    const p = join(dir, 'result.json')
    const r = JSON.parse(readFileSync(p, 'utf8'))
    const out = fn(r) ?? r
    writeFileSync(p, JSON.stringify(redact(out), null, 2))
    return out
}

// Manual additions carry src "manual"; scenario reruns replace only their own entries.
export function addToResult(dir, field, value) {
    validateEntry(field, value)
    const entry = typeof value === 'string' ? value : { ...value, src: value.src ?? 'manual' }
    return updateResult(dir, (r) => { (r[field] ??= []).push(entry) })[field].length
}

// Append a command to result.reproduce, skipping an immediate repeat.
export function addReproduce(dir, line) {
    updateResult(dir, (r) => {
        r.reproduce ??= []
        if (r.reproduce.at(-1) !== line) r.reproduce.push(line)
    })
}
