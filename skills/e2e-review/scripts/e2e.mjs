#!/usr/bin/env node
// e2e-review entry point. Usage and command list: references/tools.md, or run without arguments.
import { execSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { fetchAudit } from './core/audit.mjs'
import { createContext } from './core/context.mjs'
import { findProject, loadProject, projectSkillVersion, SKILL_DIR, skillVersion } from './core/project.mjs'
import { renderReport } from './core/report.mjs'
import { addToResult, ensureWorkspace, localIso, logStep, newTask, readCurrent, WORKSPACE } from './core/task.mjs'
import * as driver from './playwright/driver.mjs'

function parseArgs(argv) {
    const pos = []
    const opts = {}
    for (const a of argv) {
        const m = a.match(/^--([^=]+)(?:=(.*))?$/s)
        if (m) opts[m[1]] = m[2] ?? true
        else pos.push(a)
    }
    return { pos, opts }
}

const { pos, opts } = parseArgs(process.argv.slice(2))
const [cmd, arg] = pos
const project = findProject(process.cwd(), opts.project)
const loaded = loadProject(project.assets)
const env = loaded.env
const SESSION = process.env.E2E_SESSION || env.session || 'e2e'

const defaultParent = () => (project.assets ? join(project.assets, 'out') : process.cwd())
const taskDir = (explicit) => {
    const dir = explicit ? resolve(explicit) : readCurrent(project, SESSION)
    if (!dir) throw new Error('no task folder: run `new` first or pass --out')
    return dir
}
// Driver output (e.g. .playwright-cli/) stays inside the execution workspace, which ignores itself.
const toolCwd = (dir) => (dir ? dirname(dir) : ensureWorkspace(defaultParent()))
const userIds = (list) => String(list ?? '').split(',').filter(Boolean).map((k) => loaded.accounts[k]?.userId ?? k)

// Run one fragment, log the step (account by key only), store the value, and record the account key in result.env.
async function runStep(script, args, dir) {
    const file = driver.resolveFragment(script, project.assets)
    const accountKey = args.account ? String(args.account) : null
    if (accountKey && !loaded.accounts[accountKey]) return { ok: false, error: `unknown account key: ${accountKey}` }
    const P = { env, config: loaded.config, account: accountKey ? loaded.accounts[accountKey] : null, accountKey, out: dir, args }
    const startedAt = localIso()
    const res = driver.runFragment({ session: SESSION, file, P, assets: project.assets, cwd: toolCwd(dir) })
    if (dir) {
        const label = file.startsWith(SKILL_DIR) ? relative(join(SKILL_DIR, 'scripts', 'playwright'), file) : project.assets && file.startsWith(project.assets) ? relative(project.assets, file) : file
        logStep(dir, { startedAt, endedAt: localIso(), script: label.replace(/\\/g, '/').replace(/\.js$/, ''), args, ok: res.ok })
        if (res.ok && args.save) writeFileSync(join(dir, 'values', `${args.save}.json`), JSON.stringify(res.value, null, 2))
        if (accountKey) {
            const p = join(dir, 'result.json')
            const r = JSON.parse(readFileSync(p, 'utf8'))
            if (!r.env.accounts.includes(accountKey)) r.env.accounts.push(accountKey)
            writeFileSync(p, JSON.stringify(r, null, 2))
        }
    }
    return res
}

function check() {
    const out = { projectRoot: project.root, assets: project.assets, skillVersion: skillVersion(), projectVerifiedSkillVersion: projectSkillVersion(project.assets) }
    out.versionMatch = out.projectVerifiedSkillVersion ? out.projectVerifiedSkillVersion === out.skillVersion : null
    try { out.driver = execSync('playwright-cli --version', { encoding: 'utf8' }).trim() } catch { out.driver = null }
    out.auditAdapter = Boolean(project.assets && existsSync(join(project.assets, 'audit', 'fetch.mjs')))
    out.accounts = Object.keys(loaded.accounts)
    return out
}

const usage = `usage: node e2e.mjs <command>
  check                                   startup checks (assets, versions, driver, audit adapter, account keys)
  new <short> [--parent] [--prev] [--basis]  create a round folder under <parent>/${WORKSPACE}/ and make it current
  open                                    open the browser (env.browser, env.baseUrl)
  run <fragment> [--account=<key>] [--save=<name>] [--out] [--k=v]   run a fragment and log the step
  scenario <file> [--out] [--k=v]         run a solidified scenario (export default async (ctx, opts) => {})
  peek [--from=<text>] [--max=<n>]        condensed snapshot of the current screen
  sheet <dir> [--prefix] [--per]          contact sheets of shots/ into review/
  add <dir> <field> '<json>'              append to a result.json array field
  audit <dir> --users=<keys or ids>       fetch audit rows for the task window via .e2e/audit/fetch.mjs
  report <dir>                            render report.md from result.json
  close <dir> [--users]                   audit (when users given) and report
  init-proposal <dir>                     write the .e2e/ skeleton proposal into <dir>/init-proposal/
  init-apply <dir> --approved-by=<who>    copy an approved proposal into <project>/.e2e/ (never overwrites)`

try {
    if (cmd === 'check') console.log(JSON.stringify(check(), null, 2))
    else if (cmd === 'new') console.log(newTask({ project, env, session: SESSION, parent: opts.parent ?? defaultParent(), short: arg, prev: opts.prev, basis: opts.basis }))
    else if (cmd === 'open') {
        driver.open({ session: SESSION, browser: env.browser, url: opts.url ?? env.baseUrl, cwd: toolCwd(readCurrent(project, SESSION)) })
        console.log('opened')
    } else if (cmd === 'run') {
        const { out, ...args } = opts
        const res = await runStep(arg, args, out ? resolve(out) : readCurrent(project, SESSION))
        if (!res.ok) throw new Error(res.error)
        console.log(JSON.stringify(res.value))
    } else if (cmd === 'scenario') {
        const dir = taskDir(opts.out)
        const ctx = createContext({ dir, project, loaded, runStep: (s, a) => runStep(s, a, dir) })
        const file = existsSync(resolve(arg)) ? resolve(arg) : join(project.assets ?? '', arg.endsWith('.mjs') ? arg : `${arg}.mjs`)
        const { default: scenario } = await import(pathToFileURL(file).href)
        console.log(JSON.stringify(await scenario(ctx, opts)))
    } else if (cmd === 'peek') console.log(driver.peek({ session: SESSION, cwd: toolCwd(readCurrent(project, SESSION)), from: opts.from, max: opts.max }))
    else if (cmd === 'sheet') {
        const dir = taskDir(arg)
        const { n, base } = driver.buildSheets(dir, opts.prefix ?? '', Number(opts.per ?? 8))
        const res = await runStep('probes/contact-sheet', { n: String(n), base }, dir)
        if (!res.ok) throw new Error(res.error)
        console.log(JSON.stringify(res.value))
    } else if (cmd === 'add') {
        let value
        try { value = JSON.parse(pos[3]) } catch { value = pos[3] }
        console.log(`${pos[2]}: ${addToResult(taskDir(arg), pos[2], value)} entries`)
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
    console.error(e.message)
    process.exit(1)
}
