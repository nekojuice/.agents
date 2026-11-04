#!/usr/bin/env node
// e2e-review entry point. Usage and command list: references/tools.md, or run without arguments.
import { execFileSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { basename, dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { fetchAudit } from './core/audit.mjs'
import { createContext } from './core/context.mjs'
import { declaredDriver, driverExists, fragmentLabel, loadDriver, parseRef, resolveFragment, surfaceConfig } from './core/drivers.mjs'
import { findProject, loadProject, projectSkillVersion, SKILL_DIR, skillVersion } from './core/project.mjs'
import { findStep } from './core/recipe.mjs'
import { renderReport } from './core/report.mjs'
import { addAccountSecrets, isSecretKey, redact } from './core/secrets.mjs'
import { addReproduce, addToResult, assetsChangedSince, ensureWorkspace, localIso, logDir, logStep, newTask, readCurrent, readSideSteps, updateResult, validateEntry, writeValue, WORKSPACE } from './core/task.mjs'

// Git Bash rewrites arguments that start with "/" into Windows paths under the Git install; undo that.
// The install root comes from EXEPATH (set by Git Bash, e.g. C:\Program Files\Git\bin), else the default location.
const gitRoots = [process.env.EXEPATH && dirname(process.env.EXEPATH), 'C:\\Program Files\\Git']
    .filter(Boolean).map((r) => r.replace(/[\\/]+$/, '').replace(/[\\/]/g, '[\\\\/]').replace(/[.()+]/g, '\\$&'))
const msysPrefix = new RegExp(`^(?:${gitRoots.join('|')})(?=[\\\\/])`, 'i')
const unMsys = (v) => (typeof v === 'string' && process.platform === 'win32' && msysPrefix.test(v) ? v.replace(msysPrefix, '').replace(/\\/g, '/') : v)

// --k=v values that are a JSON object or array become objects, so CLI and scenarios pass the same types; others stay strings.
function argValue(v) {
    if (typeof v !== 'string' || !/^\s*[[{]/.test(v)) return v
    try { return JSON.parse(v) } catch { return v }
}

function parseArgs(argv) {
    const pos = []
    const opts = {}
    for (const a of argv) {
        const m = a.match(/^--([^=]+)(?:=(.*))?$/s)
        if (m) opts[m[1]] = m[2] === undefined ? true : argValue(unMsys(m[2]))
        else pos.push(unMsys(a))
    }
    return { pos, opts }
}

const { pos, opts } = parseArgs(process.argv.slice(2))
const [cmd, arg] = pos
const project = findProject(process.cwd(), opts.project)
const loaded = loadProject(project.assets)
addAccountSecrets(loaded.accounts)
const env = loaded.env
// Without project assets (direct ad-hoc use) both built-in surfaces are implicit: web at --url, api at --api-url.
if (!project.assets && !env.surfaces) env.surfaces = { web: { driver: 'playwright', baseUrl: opts.url ?? '' }, api: { driver: 'http', baseUrl: opts['api-url'] ?? '' } }
// E2E_SESSION wins over the surface's session name everywhere (open, run, peek, current-task pointer).
const SESSION = process.env.E2E_SESSION || env.surfaces?.web?.session || env.session || 'e2e'
const sessionFor = (cfg) => process.env.E2E_SESSION || cfg.session || SESSION

const defaultParent = () => (project.assets ? join(project.assets, 'out') : process.cwd())
const given = (v) => v != null && v !== true && v !== ''
const taskDir = (explicit) => {
    const dir = given(explicit) ? resolve(explicit) : readCurrent(project, SESSION)
    if (!dir) throw new Error('no task folder: run `new` first or pass --out')
    return dir
}
// Driver output (e.g. .playwright-cli/) stays inside the execution workspace, which ignores itself.
const toolCwd = (dir) => (dir ? dirname(dir) : ensureWorkspace(defaultParent()))
const list = (v) => (!given(v) ? [] : Array.isArray(v) ? v.map(String) : String(v).split(',').filter(Boolean))
const userIds = (v) => list(v).map((k) => loaded.accounts[k]?.userId ?? k)
const flag = (v) => v === true || v === '1' || v === 'true'

// result.assetsChanged: versioned .e2e/ files added or changed since `new` took its baseline; null when there is no baseline.
function recordAssetsChanged(dir) {
    updateResult(dir, (r) => {
        const changed = r.env?.assetsBaseline ? assetsChangedSince(r.env.assetsBaseline, project.assets ?? join(project.root, '.e2e'), project.root) : null
        r.assetsChanged = changed
    })
}

function recordAccount(dir, accountKey) {
    updateResult(dir, (r) => { if (!r.env.accounts.includes(accountKey)) r.env.accounts.push(accountKey) })
}

// The command line as run, for result.reproduce. Redacted like steps.jsonl: a --key whose name looks secret has its value masked,
// a JSON value is redacted as an object (secret keys inside it masked), and every value passes value-based redaction.
// Arguments with shell characters (including < > #) are single-quoted.
const quote = (a) => (/^[\w@%+=:,./-]+$/.test(a) ? a : `'${String(a).replace(/'/g, `'\\''`)}'`)
function safeArg(a) {
    const m = a.match(/^--([^=]+)=(.*)$/s)
    if (!m) return redact(unMsys(a))
    if (isSecretKey(m[1])) return `--${m[1]}=<redacted>`
    const v = unMsys(m[2])
    const parsed = argValue(v)
    return `--${m[1]}=${parsed && typeof parsed === 'object' ? JSON.stringify(redact(parsed)) : redact(v)}`
}
const commandLine = () => `node <skill>/scripts/e2e.mjs ${process.argv.slice(2).map(safeArg).map(quote).join(' ')}`
const reproduce = (dir) => { if (dir && existsSync(join(dir, 'result.json'))) addReproduce(dir, commandLine()) }

// Run one fragment on its surface, log the step (account by key only), store the value.
// mode: null (formal), 'dry' (logs under <round>/dry/<name>/), 'rehearse' (real operation cancelled before saving; <round>/rehearse/<name>/).
async function runStep(refText, args, dir, { mode = null, name = null, expects = null } = {}) {
    const ref = parseRef(refText, env)
    const cfg = surfaceConfig(env, ref.surface)
    const driver = await loadDriver(cfg.driver)
    const file = resolveFragment(ref, driver, project)
    const accountKey = args.account ? String(args.account) : null
    if (accountKey && !loaded.accounts[accountKey]) return { ok: false, error: `unknown account key: ${accountKey}` }
    const { script, kind } = fragmentLabel(file, project, ref.surface, driver.name)
    const out = dir ? logDir(dir, mode, name ?? script.split(/[/:]/).pop()) : null
    const dry = mode === 'dry'
    const P = { env, surface: ref.surface, surfaceConfig: cfg, config: loaded.config, account: accountKey ? loaded.accounts[accountKey] : null, accountKey, out, args, dry }
    const ctx = { project, surface: ref.surface, cfg, accounts: loaded.accounts, dir: out, dry, session: sessionFor(cfg), cwd: toolCwd(dir), label: script.split('/').pop() }
    const startedAt = localIso()
    const res = await driver.runFragment({ file, P, ctx })
    const endedAt = localIso()
    if (out) {
        logStep(out, { startedAt, endedAt, surface: ref.surface, kind, driver: driver.name, script, args, ok: res.ok, ...(res.accountsUsed ? { accountsUsed: res.accountsUsed } : {}), ...(mode ? { [mode]: true } : {}), ...(expects ? { expects } : {}), ...(res.blockedWrites ? { blockedWrites: res.blockedWrites } : {}), ...(res.ok ? {} : { error: res.error }) })
        if (res.ok && args.save) writeValue(out, args.save, res.value)
        if (accountKey && !mode) recordAccount(dir, accountKey)
    }
    return { ...res, step: { startedAt, endedAt, surface: ref.surface } }
}



// Paths under .e2e/ that git ignores although they should be versioned (a parent rule such as lib/ or data/).
function ignoredAssets() {
    if (!project.assets) return []
    try {
        const ls = (extra, path) => execFileSync('git', ['-C', project.root, 'ls-files', '--others', '--ignored', '--exclude-standard', ...extra, '--', path], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })
            .split('\n').map((s) => s.trim()).filter(Boolean)
        // Paths the skeleton's own .gitignore keeps out on purpose are not reported.
        const expected = [/^\.e2e\/config\/accounts\.local\.json$/, /^\.e2e\/state\//, /^\.e2e\/out\//, /(^|\/)node_modules\//, /(^|\/)\.venv\//, /(^|\/)e2e-review\//]
        const keep = (p) => !expected.some((re) => re.test(p))
        // --directory collapses a folder whose files are all ignored into the folder itself; such a folder is reported only
        // when it holds an ignored file outside the expected ones (e.g. tools/ holding only tools/reader/.venv/ is fine).
        return ls(['--directory'], '.e2e').filter(keep).filter((p) => !p.endsWith('/') || ls([], p).some(keep))
    } catch {
        return [] // not a git repository, or git unavailable
    }
}

async function check() {
    const out = { projectRoot: project.root, assets: project.assets, skillVersion: skillVersion(), projectVerifiedSkillVersion: projectSkillVersion(project.assets) }
    out.versionMatch = out.projectVerifiedSkillVersion ? out.projectVerifiedSkillVersion === out.skillVersion : null
    out.surfaces = {}
    for (const [name, cfg] of Object.entries(env.surfaces ?? {})) {
        const s = { driver: cfg.driver, shipped: driverExists(cfg.driver) }
        if (s.shipped) {
            const d = await loadDriver(cfg.driver)
            s.available = typeof d.available === 'function' ? d.available() : null
        }
        const dir = project.assets && join(project.assets, 'surfaces', name)
        if (dir && existsSync(dir) && s.shipped) {
            const driver = await loadDriver(cfg.driver)
            // Fragments are the files in actions/ and probes/; helpers are not fragments and need no declaration.
            const files = ['actions', 'probes'].flatMap((sub) => (existsSync(join(dir, sub)) ? readdirSync(join(dir, sub)).filter((f) => driver.extensions.some((e) => f.endsWith(e))).map((f) => join(dir, sub, f)) : []))
            s.fragments = files.length
            s.undeclared = files.filter((f) => !declaredDriver(f)).length
            s.mismatched = files.filter((f) => declaredDriver(f) && declaredDriver(f) !== cfg.driver).length
        }
        out.surfaces[name] = s
    }
    const warnings = []
    for (const [name, cfg] of Object.entries(env.surfaces ?? {})) {
        // dryAllow and dryBlock match the URL path only (since 1.3); host or query parts never match.
        const odd = [...(cfg.dryAllow ?? []), ...(cfg.dryBlock ?? [])].filter((x) => /:\/\/|\?|#/.test(String(x)))
        if (odd.length) warnings.push(`surface ${name}: dryAllow/dryBlock entries are matched against the URL path only; these never match: ${odd.join(', ')}`)
        // H.account is reserved on http surfaces; a project helper of that name is ignored.
        const h = project.assets && join(project.assets, 'surfaces', name, 'helpers')
        if (cfg.driver === 'http' && h && ['account.mjs', 'account.js'].some((f) => existsSync(join(h, f)))) warnings.push(`surface ${name}: helpers/account.* is ignored; H.account is reserved for the built-in account access`)
    }
    if (project.assets) {
        if (!env.surfaces) warnings.push('config/env.json has no surfaces section (skill 1.2+); see references/project-profile.md "Migrating from 1.1"')
        const legacy = ['actions', 'probes', 'helpers'].filter((d) => existsSync(join(project.assets, d)))
        if (legacy.length) warnings.push(`1.1 layout found (${legacy.join(', ')} at the .e2e/ root); the skill reads only surfaces/<surface>/; see "Migrating from 1.1"`)
        const ignored = ignoredAssets()
        if (ignored.length) warnings.push(`git ignores paths that should be versioned: ${ignored.join(', ')}; a parent .gitignore rule matches them; add negations to .e2e/.gitignore (see references/project-profile.md)`)
    }
    out.auditAdapter = Boolean(project.assets && existsSync(join(project.assets, 'audit', 'fetch.mjs')))
    out.accounts = Object.keys(loaded.accounts)
    out.warnings = warnings
    return out
}

const usage = `usage: node e2e.mjs <command>
  check [--out[=<round>]]                 startup checks; --out also writes values/check.json in the round
  new <short> [--parent] [--prev] [--basis] [--kind=review|prep|init]   create a round folder under <parent>/${WORKSPACE}/
  open [--surface=web] [--url]            open the browser for a web surface
  run <[surface:]fragment> [--account=<key>] [--save=<name>] [--out] [--dry|--rehearse] [--expects=<json>] [--k=v]   run a fragment and log the step
  scenario <file> [--out] [--dry] [--k=v]   run a solidified scenario (export default async (ctx, opts) => {})
  api <METHOD> <path> [--surface=api] [--account] [--body=<json file>] [--dry] [--out]   one logged API call
  step <recipe>#<id> [--out] [--dry]      run a script step of a recipe
  log start|end <recipe>#<id> [--evidence=a,b] [--note] [--fail] [--out]   record an agent step of a recipe
  peek [--from=<text>] [--max=<n>]        condensed snapshot of the current web screen
  sheet <dir> [--prefix] [--per]          contact sheets of shots/ into review/
  add <dir> <field> '<json>'              append to a result.json array field (shape checked)
  amend <dir> <check id> '<json>' --reason=<text> --evidence=<paths>   correct one recorded check; original and correction are both kept
  audit <dir> [--users=<keys or ids>] [--actions=<codes>] [--system]   fetch audit rows for the formal and side (dry, rehearsal) windows
  report <dir>                            render report.md from result.json
  close <dir> [--users] [--actions] [--system]   audit (when a filter is given) and report
  init-proposal <dir>                     write the .e2e/ skeleton proposal into <dir>/init-proposal/
  init-apply <dir> --approved-by=<who>    copy an approved proposal into <project>/.e2e/ (never overwrites)`

// --rehearse exists only for `run` on web surfaces; anywhere else it would silently run for real.
const noRehearse = () => { if (opts.rehearse !== undefined) throw new Error(`--rehearse is for \`run\` on web surfaces only; \`${cmd}\` does not accept it. Use --dry to rehearse without sending writes`) }

const AMENDABLE =['verdict', 'actual', 'expected', 'by', 'via', 'note', 'evidence', 'agent']

// Without an audit adapter (deleted because the project has no audit trail), close warns and skips the audit so the report
// is still rendered. An adapter that fails (e.g. the skeleton's, not written yet) is also only a warning for close, and is
// recorded as an issue. The audit command itself reports both as errors.
async function audit(dir, { tolerant = false } = {}) {
    if (!project.assets || !existsSync(join(project.assets, 'audit', 'fetch.mjs'))) {
        const msg = 'no audit adapter (.e2e/audit/fetch.mjs); audit rows were not fetched (see references/project-profile.md "Audit adapter")'
        if (tolerant) return `warning: ${msg}`
        throw new Error(msg)
    }
    const filters = { actions: list(opts.actions), includeSystem: flag(opts.system) }
    const users = userIds(opts.users)
    try {
        const formal = await fetchAudit(project, loaded, dir, users, { ...filters, scope: 'formal' })
        const side = readSideSteps(dir).length ? await fetchAudit(project, loaded, dir, users, { ...filters, scope: 'side' }) : null
        // A successful audit clears an earlier adapter-failure note.
        updateResult(dir, (r) => { r.issues = (r.issues ?? []).filter((i) => !(i && typeof i === 'object' && i.src === 'tool:audit')) })
        return `${formal ?? 0} audit rows → values/audit.json${side != null ? `; ${side} rows during dry runs and rehearsals → values/audit-side.json` : ''}`
    } catch (e) {
        if (!tolerant) throw e
        const msg = `audit rows were not fetched: the audit adapter failed (${redact(String(e?.message ?? e).split('\n')[0])})`
        // One note owned by "tool:audit" (a colon cannot occur in a scenario file name, so it never collides with a scenario's own entries): a later close replaces it, and a successful audit removes it.
        updateResult(dir, (r) => { r.issues = [...(r.issues ?? []).filter((i) => !(i && typeof i === 'object' && i.src === 'tool:audit')), { text: msg, src: 'tool:audit' }] })
        return `warning: ${msg}`
    }
}

try {
    if (cmd === 'check') {
        const res = await check()
        if (opts.out) {
            const dir = taskDir(opts.out)
            mkdirSync(join(dir, 'values'), { recursive: true })
            writeFileSync(join(dir, 'values', 'check.json'), JSON.stringify(redact(res), null, 2))
        }
        console.log(JSON.stringify(res, null, 2))
    } else if (cmd === 'new') console.log(newTask({ project, env, session: SESSION, parent: opts.parent ?? defaultParent(), short: arg, prev: opts.prev, basis: opts.basis, kind: opts.kind ?? 'review' }))
    else if (cmd === 'open') {
        const surface = opts.surface ?? 'web'
        const cfg = surfaceConfig(env, surface)
        const driver = await loadDriver(cfg.driver)
        if (typeof driver.open !== 'function') throw new Error(`surface ${surface} (${cfg.driver}) needs no open`)
        driver.open({ session: sessionFor(cfg), browser: cfg.browser ?? env.browser, url: opts.url ?? cfg.baseUrl, cwd: toolCwd(readCurrent(project, SESSION)) })
        console.log('opened')
    } else if (cmd === 'run') {
        const { out, dry, rehearse, expects, ...args } = opts
        if (flag(dry) && flag(rehearse)) throw new Error('--dry and --rehearse cannot be combined')
        const mode = flag(dry) ? 'dry' : flag(rehearse) ? 'rehearse' : null
        // A rehearsal is an interaction cancelled before saving; an API call cannot be cancelled, so it would be a real, untracked write.
        if (mode === 'rehearse') {
            const surface = parseRef(arg, env).surface
            if (surfaceConfig(env, surface).driver !== 'playwright') throw new Error(`--rehearse is for web surfaces only; surface ${surface} uses ${surfaceConfig(env, surface).driver}. Use --dry to build requests without sending them`)
        }
        const dir = given(out) ? resolve(out) : readCurrent(project, SESSION)
        if (!mode) reproduce(dir)
        const res = await runStep(arg, args, dir, { mode, expects: given(expects) ? (Array.isArray(expects) ? expects : [expects]) : null })
        if (!res.ok) throw new Error(res.error)
        console.log(JSON.stringify(redact(res.value)))
    } else if (cmd === 'scenario') {
        noRehearse()
        // Program-replay rejudging was removed; an unknown flag must not silently fall through to a formal run that sends writes.
        if (opts.rejudge !== undefined) throw new Error('--rejudge is not supported: to recompute checks, read the round\'s value files with a scratch script and record corrections with amend (references/tools.md "Reruns and corrections")')
        const dir = taskDir(opts.out)
        const mode = flag(opts.dry) ? 'dry' : null
        const file = existsSync(resolve(arg)) ? resolve(arg) : join(project.assets ?? '', arg.endsWith('.mjs') ? arg : `${arg}.mjs`)
        const name = basename(file).replace(/\.m?js$/, '')
        if (mode !== 'dry') reproduce(dir)
        const ctx = createContext({ dir, project, loaded, name, mode, runStep: (s, a, o = {}) => runStep(s, a, dir, { mode, name, ...o }) })
        const { default: scenario } = await import(pathToFileURL(file).href)
        console.log(JSON.stringify(await scenario(ctx, opts)))
    } else if (cmd === 'api') {
        const method = String(arg ?? '').toUpperCase()
        const path = pos[2]
        if (!method || !path) throw new Error('usage: api <METHOD> <path>')
        noRehearse()
        const surface = opts.surface ?? 'api'
        const cfg = surfaceConfig(env, surface)
        if (cfg.driver !== 'http') throw new Error(`surface ${surface} does not use the http driver`)
        const driver = await loadDriver('http')
        const dir = given(opts.out) ? resolve(opts.out) : readCurrent(project, SESSION)
        const dry = flag(opts.dry)
        const outDir = dir ? logDir(dir, dry ? 'dry' : null, 'api') : null
        const accountKey = opts.account ? String(opts.account) : null
        const body = opts.body ? JSON.parse(readFileSync(resolve(opts.body), 'utf8')) : undefined
        if (!dry) reproduce(dir)
        const startedAt = localIso()
        const res = await driver.call({ method, path, body, accountKey, ctx: { project, surface, cfg, accounts: loaded.accounts, dir: outDir, dry, label: 'adhoc' } })
        if (outDir) {
            logStep(outDir, { startedAt, endedAt: localIso(), surface, kind: 'adhoc', driver: 'http', script: `api ${method} ${path}`, args: { ...(accountKey ? { account: accountKey } : {}), ...(opts.body ? { body: opts.body } : {}) }, ok: dry ? true : res.status > 0 && res.status < 400, ...(dry ? { dry: true } : {}) })
            if (accountKey && !dry) recordAccount(dir, accountKey)
        }
        console.log(JSON.stringify(redact({ status: res.status, body: res.body ?? res.request }), null, 2))
    } else if (cmd === 'step') {
        noRehearse()
        const dir = taskDir(opts.out)
        const { name, step } = findStep(arg, project)
        if (step.kind !== 'script') throw new Error(`${arg} is an agent step; record it with log start|end`)
        const dry = flag(opts.dry)
        if (!dry) reproduce(dir)
        const res = await runStep(step.run, { ...(step.args ?? {}), recipe: `${name}#${step.id}`, save: step.save ?? `${name}-${step.id}` }, dir, { mode: dry ? 'dry' : null, name: `${name}-${step.id}`, expects: step.expects ?? null })
        if (!res.ok) throw new Error(res.error)
        console.log(JSON.stringify(redact(res.value)))
    } else if (cmd === 'log') {
        const phase = arg
        const ref = pos[2]
        if (!['start', 'end'].includes(phase) || !ref) throw new Error('usage: log start|end <recipe>#<id>')
        const dir = taskDir(opts.out)
        const { name, step } = findStep(ref, project)
        if (step.kind !== 'agent') throw new Error(`${ref} is a script step; run it with step`)
        const statePath = join(dir, '.agent-steps.json')
        const state = existsSync(statePath) ? JSON.parse(readFileSync(statePath, 'utf8')) : {}
        const key = `${name}#${step.id}`
        reproduce(dir)
        if (phase === 'start') {
            state[key] = localIso()
            writeFileSync(statePath, JSON.stringify(state, null, 2))
            console.log(`started ${key}`)
        } else {
            if (!state[key]) throw new Error(`log start ${key} first`)
            logStep(dir, { startedAt: state[key], endedAt: localIso(), surface: step.surface ?? null, kind: 'agent', driver: null, script: `recipe:${key}`, args: {}, ok: !opts.fail, evidence: list(opts.evidence), note: given(opts.note) ? String(opts.note) : '' })
            delete state[key]
            writeFileSync(statePath, JSON.stringify(state, null, 2))
            console.log(`ended ${key}`)
        }
    } else if (cmd === 'peek' || cmd === 'sheet') {
        // Screen commands work on a surface whose driver offers them (playwright today).
        const surface = opts.surface ?? 'web'
        const cfg = surfaceConfig(env, surface)
        const driver = await loadDriver(cfg.driver)
        const fn = cmd === 'peek' ? driver.peek : driver.buildSheets
        if (typeof fn !== 'function') throw new Error(`surface ${surface} (${cfg.driver}) has no ${cmd}`)
        if (cmd === 'peek') {
            console.log(driver.peek({ session: sessionFor(cfg), cwd: toolCwd(readCurrent(project, SESSION)), from: opts.from, max: opts.max }))
            process.exit(0)
        }
        const dir = taskDir(arg)
        const { n, base } = driver.buildSheets(dir, opts.prefix ?? '', Number(opts.per ?? 8))
        const res = await runStep(`${surface}:probes/contact-sheet`, { n: String(n), base }, dir)
        if (!res.ok) throw new Error(res.error)
        console.log(JSON.stringify(res.value))
    } else if (cmd === 'add') {
        let value
        try { value = JSON.parse(pos[3]) } catch { value = pos[3] }
        console.log(`${pos[2]}: ${addToResult(taskDir(arg), pos[2], redact(value))} entries`)
    } else if (cmd === 'amend') {
        const dir = taskDir(arg)
        const id = pos[2]
        let patch
        try { patch = JSON.parse(pos[3]) } catch { throw new Error(`amend needs a JSON object of fields to change: ${AMENDABLE.join(', ')}`) }
        if (!given(opts.reason)) throw new Error('amend needs --reason=<why the check is corrected>')
        // Evidence of the correction (e.g. the scratch script that recomputed the check and the value file it wrote); each path
        // is relative to the round folder and must exist.
        const evidence = list(opts.evidence)
        if (!evidence.length) throw new Error('amend needs --evidence=<paths in the round folder, comma-separated> (e.g. the scratch script and its output)')
        const missingEv = evidence.filter((p) => !existsSync(join(dir, p)))
        if (missingEv.length) throw new Error(`amend evidence not found in the round folder: ${missingEv.join(', ')}`)
        const bad = Object.keys(patch ?? {}).filter((k) => !AMENDABLE.includes(k))
        if (!patch || typeof patch !== 'object' || Array.isArray(patch) || bad.length) throw new Error(`amend can change only: ${AMENDABLE.join(', ')}${bad.length ? ` (not ${bad.join(', ')})` : ''}`)
        updateResult(dir, (r) => {
            const i = (r.checks ?? []).findIndex((c) => String(c.id) === String(id))
            if (i < 0) throw new Error(`no check ${id} in this round`)
            const original = r.checks[i]
            const before = Object.fromEntries(Object.keys(patch).map((k) => [k, original[k] ?? null]))
            r.checks[i] = validateEntry('checks', { ...original, ...patch, amended: true })
            // The original judgment is kept beside the correction, so the report shows both and the superior reviews it.
            ;(r.amendments ??= []).push({ at: localIso(), check: String(id), original: { verdict: original.verdict, by: original.by, actual: original.actual ?? null }, before, after: patch, reason: String(opts.reason), evidence })
        })
        reproduce(dir)
        console.log(`amended ${id}`)
    } else if (cmd === 'audit') console.log(await audit(taskDir(arg)))
    else if (cmd === 'report') {
        const dir = taskDir(arg)
        recordAssetsChanged(dir)
        console.log(renderReport(dir))
    }
    else if (cmd === 'close') {
        const dir = taskDir(arg)
        if (given(opts.users) || given(opts.actions) || flag(opts.system)) console.log(await audit(dir, { tolerant: true }))
        recordAssetsChanged(dir)
        console.log(renderReport(dir))
    } else if (cmd === 'init-proposal') {
        const dir = taskDir(arg)
        const target = join(dir, 'init-proposal', '.e2e')
        if (existsSync(target)) throw new Error(`proposal already exists: ${target}`)
        cpSync(join(SKILL_DIR, 'assets', 'e2e-skeleton'), target, { recursive: true })
        const pm = join(target, 'PROJECT.md')
        writeFileSync(pm, readFileSync(pm, 'utf8').replace('{{SKILL_VERSION}}', skillVersion()))
        console.log(target)
    } else if (cmd === 'init-apply') {
        // <round> is the round holding the approved proposal. The current round (typically the dispatched init round, created
        // with `new --kind=init` first) stays current and records the creation of .e2e/ in its report; without a current
        // round, the proposal round records it.
        const proposal = taskDir(arg)
        if (!opts['approved-by']) throw new Error('init-apply needs --approved-by=<who approved>')
        const source = join(proposal, 'init-proposal', '.e2e')
        const target = join(resolve(opts.project ?? project.root), '.e2e')
        if (!existsSync(source)) throw new Error(`no proposal at ${source}`)
        if (existsSync(target)) throw new Error(`${target} already exists; init-apply never overwrites`)
        const current = readCurrent(project, SESSION)
        const recordIn = current && existsSync(join(current, 'result.json')) ? current : proposal
        mkdirSync(target, { recursive: true })
        cpSync(source, target, { recursive: true })
        // The current-task pointer moves from the execution workspace into the new assets (still pointing at the current round),
        // so a stale workspace pointer is never read.
        if (current) {
            mkdirSync(join(target, 'state'), { recursive: true })
            writeFileSync(join(target, 'state', `current-${SESSION}`), current)
            rmSync(join(dirname(current), `current-${SESSION}`), { force: true })
        }
        addToResult(recordIn, 'writes', { what: `created project assets .e2e/ from the approved proposal in ${basename(proposal)} (approved by ${opts['approved-by']})`, where: target, how: 'init-apply', at: localIso() })
        console.log(target)
    } else {
        console.log(usage)
        process.exit(cmd ? 1 : 0)
    }
} catch (e) {
    console.error(redact(e.message))
    process.exit(1)
}
