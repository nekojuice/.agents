#!/usr/bin/env node
// e2e-review entry point. Usage and command list: references/tools.md, or run without arguments.
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { fetchAudit } from './core/audit.mjs'
import { createContext } from './core/context.mjs'
import { declaredDriver, driverExists, fragmentLabel, loadDriver, parseRef, resolveFragment, surfaceConfig } from './core/drivers.mjs'
import { findProject, loadProject, projectSkillVersion, SKILL_DIR, skillVersion } from './core/project.mjs'
import { findStep } from './core/recipe.mjs'
import { renderReport } from './core/report.mjs'
import { addAccountSecrets, redact } from './core/secrets.mjs'
import { addToResult, ensureWorkspace, localIso, logDir, logStep, newTask, readCurrent, WORKSPACE } from './core/task.mjs'

// Git Bash rewrites arguments that start with "/" into Windows paths under the Git install; undo that.
// The install root comes from EXEPATH (set by Git Bash, e.g. C:\Program Files\Git\bin), else the default location.
const gitRoots = [process.env.EXEPATH && dirname(process.env.EXEPATH), 'C:\\Program Files\\Git']
    .filter(Boolean).map((r) => r.replace(/[\\/]+$/, '').replace(/[\\/]/g, '[\\\\/]').replace(/[.()+]/g, '\\$&'))
const msysPrefix = new RegExp(`^(?:${gitRoots.join('|')})(?=[\\\\/])`, 'i')
const unMsys = (v) => (typeof v === 'string' && process.platform === 'win32' && msysPrefix.test(v) ? v.replace(msysPrefix, '').replace(/\\/g, '/') : v)

function parseArgs(argv) {
    const pos = []
    const opts = {}
    for (const a of argv) {
        const m = a.match(/^--([^=]+)(?:=(.*))?$/s)
        if (m) opts[m[1]] = m[2] === undefined ? true : unMsys(m[2])
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
const taskDir = (explicit) => {
    const dir = explicit ? resolve(explicit) : readCurrent(project, SESSION)
    if (!dir) throw new Error('no task folder: run `new` first or pass --out')
    return dir
}
// Driver output (e.g. .playwright-cli/) stays inside the execution workspace, which ignores itself.
const toolCwd = (dir) => (dir ? dirname(dir) : ensureWorkspace(defaultParent()))
const userIds = (list) => String(list ?? '').split(',').filter(Boolean).map((k) => loaded.accounts[k]?.userId ?? k)

function recordAccount(dir, accountKey) {
    const p = join(dir, 'result.json')
    const r = JSON.parse(readFileSync(p, 'utf8'))
    if (!r.env.accounts.includes(accountKey)) r.env.accounts.push(accountKey)
    writeFileSync(p, JSON.stringify(r, null, 2))
}

// Run one fragment on its surface, log the step (account by key only), store the value. Dry runs log under <round>/dry/.
async function runStep(refText, args, dir, { dry = false } = {}) {
    const ref = parseRef(refText, env)
    const cfg = surfaceConfig(env, ref.surface)
    const driver = await loadDriver(cfg.driver)
    const file = resolveFragment(ref, driver, project)
    const accountKey = args.account ? String(args.account) : null
    if (accountKey && !loaded.accounts[accountKey]) return { ok: false, error: `unknown account key: ${accountKey}` }
    const out = dir ? logDir(dir, dry) : null
    const { script, kind } = fragmentLabel(file, project, ref.surface, driver.name)
    const P = { env, surface: ref.surface, surfaceConfig: cfg, config: loaded.config, account: accountKey ? loaded.accounts[accountKey] : null, accountKey, out, args, dry }
    const ctx = { project, surface: ref.surface, cfg, accounts: loaded.accounts, dir: out, dry, session: sessionFor(cfg), cwd: toolCwd(dir), label: script.split('/').pop() }
    const startedAt = localIso()
    const res = await driver.runFragment({ file, P, ctx })
    const endedAt = localIso()
    if (out) {
        logStep(out, { startedAt, endedAt, surface: ref.surface, kind, driver: driver.name, script, args, ok: res.ok, ...(dry ? { dry: true } : {}), ...(res.blockedWrites ? { blockedWrites: res.blockedWrites } : {}) })
        if (res.ok && args.save) writeFileSync(join(out, 'values', `${args.save}.json`), JSON.stringify(redact(res.value), null, 2))
        if (accountKey && !dry) recordAccount(dir, accountKey)
    }
    return { ...res, step: { startedAt, endedAt, surface: ref.surface } }
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
            const files = ['actions', 'probes', 'helpers'].flatMap((sub) => (existsSync(join(dir, sub)) ? readdirSync(join(dir, sub)).filter((f) => driver.extensions.some((e) => f.endsWith(e))).map((f) => join(dir, sub, f)) : []))
            s.fragments = files.length
            s.undeclared = files.filter((f) => !f.includes(`${join('', 'helpers')}`) && !declaredDriver(f)).length
            s.mismatched = files.filter((f) => declaredDriver(f) && declaredDriver(f) !== cfg.driver).length
        }
        out.surfaces[name] = s
    }
    const warnings = []
    if (project.assets) {
        if (!env.surfaces) warnings.push('config/env.json has no surfaces section (skill 1.2); see references/project-profile.md "Migrating from 1.1"')
        const legacy = ['actions', 'probes', 'helpers'].filter((d) => existsSync(join(project.assets, d)))
        if (legacy.length) warnings.push(`1.1 layout found (${legacy.join(', ')} at the .e2e/ root); skill 1.2 reads only surfaces/<surface>/; see "Migrating from 1.1"`)
    }
    out.auditAdapter = Boolean(project.assets && existsSync(join(project.assets, 'audit', 'fetch.mjs')))
    out.accounts = Object.keys(loaded.accounts)
    out.warnings = warnings
    return out
}

const usage = `usage: node e2e.mjs <command>
  check                                   startup checks (assets, versions, surfaces and drivers, layout, audit adapter, account keys)
  new <short> [--parent] [--prev] [--basis] [--kind=review|prep|init]   create a round folder under <parent>/${WORKSPACE}/
  open [--surface=web] [--url]            open the browser for a web surface
  run <[surface:]fragment> [--account=<key>] [--save=<name>] [--out] [--dry] [--k=v]   run a fragment and log the step
  scenario <file> [--out] [--dry] [--k=v] run a solidified scenario (export default async (ctx, opts) => {})
  api <METHOD> <path> [--surface=api] [--account] [--body=<json file>] [--dry] [--out]   one logged API call
  step <recipe>#<id> [--out] [--dry]      run a script step of a recipe
  log start|end <recipe>#<id> [--evidence=a,b] [--note] [--fail] [--out]   record an agent step of a recipe
  peek [--from=<text>] [--max=<n>]        condensed snapshot of the current web screen
  sheet <dir> [--prefix] [--per]          contact sheets of shots/ into review/
  add <dir> <field> '<json>'              append to a result.json array field
  audit <dir> --users=<keys or ids>       fetch audit rows for the task window via .e2e/audit/fetch.mjs
  report <dir>                            render report.md from result.json
  close <dir> [--users]                   audit (when users given) and report
  init-proposal <dir>                     write the .e2e/ skeleton proposal into <dir>/init-proposal/
  init-apply <dir> --approved-by=<who>    copy an approved proposal into <project>/.e2e/ (never overwrites)`

const dryFlag = () => opts.dry === true || opts.dry === '1' || opts.dry === 'true'

try {
    if (cmd === 'check') console.log(JSON.stringify(await check(), null, 2))
    else if (cmd === 'new') console.log(newTask({ project, env, session: SESSION, parent: opts.parent ?? defaultParent(), short: arg, prev: opts.prev, basis: opts.basis, kind: opts.kind ?? 'review' }))
    else if (cmd === 'open') {
        const surface = opts.surface ?? 'web'
        const cfg = surfaceConfig(env, surface)
        const driver = await loadDriver(cfg.driver)
        if (typeof driver.open !== 'function') throw new Error(`surface ${surface} (${cfg.driver}) needs no open`)
        driver.open({ session: sessionFor(cfg), browser: cfg.browser ?? env.browser, url: opts.url ?? cfg.baseUrl, cwd: toolCwd(readCurrent(project, SESSION)) })
        console.log('opened')
    } else if (cmd === 'run') {
        const { out, dry, ...args } = opts
        const res = await runStep(arg, args, out ? resolve(out) : readCurrent(project, SESSION), { dry: dryFlag() })
        if (!res.ok) throw new Error(res.error)
        console.log(JSON.stringify(redact(res.value)))
    } else if (cmd === 'scenario') {
        const dir = taskDir(opts.out)
        const dry = dryFlag()
        const ctx = createContext({ dir, project, loaded, dry, runStep: (s, a) => runStep(s, a, dir, { dry }) })
        const file = existsSync(resolve(arg)) ? resolve(arg) : join(project.assets ?? '', arg.endsWith('.mjs') ? arg : `${arg}.mjs`)
        const { default: scenario } = await import(pathToFileURL(file).href)
        console.log(JSON.stringify(await scenario(ctx, opts)))
    } else if (cmd === 'api') {
        const method = String(arg ?? '').toUpperCase()
        const path = pos[2]
        if (!method || !path) throw new Error('usage: api <METHOD> <path>')
        const surface = opts.surface ?? 'api'
        const cfg = surfaceConfig(env, surface)
        if (cfg.driver !== 'http') throw new Error(`surface ${surface} does not use the http driver`)
        const driver = await loadDriver('http')
        const dir = opts.out ? resolve(opts.out) : readCurrent(project, SESSION)
        const dry = dryFlag()
        const outDir = dir ? logDir(dir, dry) : null
        const accountKey = opts.account ? String(opts.account) : null
        const body = opts.body ? JSON.parse(readFileSync(resolve(opts.body), 'utf8')) : undefined
        const startedAt = localIso()
        const res = await driver.call({ method, path, body, accountKey, ctx: { project, surface, cfg, accounts: loaded.accounts, dir: outDir, dry, label: 'adhoc' } })
        if (outDir) {
            logStep(outDir, { startedAt, endedAt: localIso(), surface, kind: 'adhoc', driver: 'http', script: `api ${method} ${path}`, args: { ...(accountKey ? { account: accountKey } : {}), ...(opts.body ? { body: opts.body } : {}) }, ok: dry ? true : res.status > 0 && res.status < 400, ...(dry ? { dry: true } : {}) })
            if (accountKey && !dry) recordAccount(dir, accountKey)
        }
        console.log(JSON.stringify(redact({ status: res.status, body: res.body ?? res.request }), null, 2))
    } else if (cmd === 'step') {
        const dir = taskDir(opts.out)
        const { name, step } = findStep(arg, project)
        if (step.kind !== 'script') throw new Error(`${arg} is an agent step; record it with log start|end`)
        const res = await runStep(step.run, { ...(step.args ?? {}), recipe: `${name}#${step.id}`, save: step.save ?? `${name}-${step.id}` }, dir, { dry: dryFlag() })
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
        if (phase === 'start') {
            state[key] = localIso()
            writeFileSync(statePath, JSON.stringify(state, null, 2))
            console.log(`started ${key}`)
        } else {
            if (!state[key]) throw new Error(`log start ${key} first`)
            const evidence = String(opts.evidence ?? '').split(',').filter(Boolean)
            logStep(dir, { startedAt: state[key], endedAt: localIso(), surface: step.surface ?? null, kind: 'agent', driver: null, script: `recipe:${key}`, args: {}, ok: !opts.fail, evidence, note: opts.note ? String(opts.note) : '' })
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
    } else if (cmd === 'audit') console.log(`${await fetchAudit(project, loaded, taskDir(arg), userIds(opts.users))} audit rows → values/audit.json`)
    else if (cmd === 'report') console.log(renderReport(taskDir(arg)))
    else if (cmd === 'close') {
        const dir = taskDir(arg)
        if (opts.users) console.log(`${await fetchAudit(project, loaded, dir, userIds(opts.users))} audit rows`)
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
        const dir = taskDir(arg)
        if (!opts['approved-by']) throw new Error('init-apply needs --approved-by=<who approved>')
        const source = join(dir, 'init-proposal', '.e2e')
        const target = join(resolve(opts.project ?? project.root), '.e2e')
        if (!existsSync(source)) throw new Error(`no proposal at ${source}`)
        if (existsSync(target)) throw new Error(`${target} already exists; init-apply never overwrites`)
        mkdirSync(target, { recursive: true })
        cpSync(source, target, { recursive: true })
        addToResult(dir, 'writes', { what: `created project assets .e2e/ from the approved proposal (approved by ${opts['approved-by']})`, where: target, how: 'init-apply', at: localIso() })
        console.log(target)
    } else {
        console.log(usage)
        process.exit(cmd ? 1 : 0)
    }
} catch (e) {
    console.error(redact(e.message))
    process.exit(1)
}
