// Playwright driver: every call to playwright-cli goes through this module.
// Fragments are single functions `async (page, P, H) => {}` composed with injected params and browser-side helpers.
// Fragment lookup lives in core/drivers.mjs; this module only executes.
import { execSync } from 'node:child_process'
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))

export const name = 'playwright'
export const extensions = ['.js']

// playwright-cli writes snapshots and logs to <cwd>/.playwright-cli; keep cwd inside the execution workspace.
function cli(session, args, cwd) {
    mkdirSync(cwd, { recursive: true })
    const line = ['playwright-cli', `-s=${session}`, ...args].map((a) => `"${String(a).replace(/"/g, '\\"')}"`).join(' ')
    return execSync(line, { encoding: 'utf8', cwd, stdio: ['ignore', 'pipe', 'pipe'] })
}

function section(output, name) {
    const m = output.match(new RegExp(`### ${name}\\n([\\s\\S]*?)(?:\\n### |$)`))
    return m ? m[1].trim() : null
}

export function open({ session, browser, url, cwd }) {
    for (let i = 0; i < 2; i++) {
        try {
            cli(session, ['open', ...(browser ? [`--browser=${browser}`] : []), url], cwd)
            return
        } catch (e) {
            if (i === 1) throw e // first launch occasionally fails; retry once
        }
    }
}

const stripFn = (src) => src.trim().replace(/;\s*$/, '')

function loadHelpers(dirs) {
    const parts = []
    for (const d of dirs.filter((x) => x && existsSync(x)))
        for (const f of readdirSync(d).filter((x) => x.endsWith('.js'))) parts.push(`${f.slice(0, -3)}: (${stripFn(readFileSync(join(d, f), 'utf8'))})`)
    return parts
}

export function available() {
    try { return execSync('playwright-cli --version', { encoding: 'utf8' }).trim() } catch { return null }
}

// In a dry run the browser itself blocks requests, so fragments that ignore P.dry still cannot save:
// write methods (POST, PUT, PATCH, DELETE) are aborted unless the URL path contains a dryAllow entry (e.g. login, logout),
// and any method is aborted when the path contains a dryBlock entry (e.g. a GET export that writes an audit row).
// Matching uses the URL path without query string or fragment. Blocked calls are returned with the step.
function dryGuard(cfg) {
    return `const __allow = ${JSON.stringify(cfg.dryAllow ?? [])}; const __block = ${JSON.stringify(cfg.dryBlock ?? [])};
  const __path = (u) => u.replace(/^[a-z][\\w+.-]*:\\/\\/[^/]*/i, '').split(/[?#]/)[0];
  await page.route('**/*', (r) => {
    const q = r.request(); const p = __path(q.url());
    const write = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(q.method());
    if (__block.some((a) => p.includes(a)) || (write && !__allow.some((a) => p.includes(a)))) { __blocked.push(q.method() + ' ' + q.url()); return r.abort(); }
    return r.continue();
  });`
}

// P must not carry secrets into logs; the composed file holds them only for the call and is deleted right after.
// H.reportBlocked(what) lets a fragment that intercepts its own requests (honoring P.dry) add them to the step's blockedWrites.
// A beforeunload dialog during the fragment is accepted (it guards only unsaved input in the browser; staying would re-trigger it on
// every later navigation) and fails the step, so an interrupted fragment is never logged as done.
export function runFragment({ file, P, ctx }) {
    const { session, cwd, project, surface, cfg = {}, dry } = ctx
    const helpers = loadHelpers([join(HERE, 'helpers'), project.assets && join(project.assets, 'surfaces', surface, 'helpers')])
    const body = `(${stripFn(readFileSync(file, 'utf8'))})(page, P, H)`
    const run = `const __dialogs = [];
  const __onDialog = (d) => { if (d.type() === 'beforeunload') { __dialogs.push(d.message() || 'beforeunload'); d.accept().catch(() => {}); } };
  page.on('dialog', __onDialog);
  ${dry ? dryGuard(cfg) : ''}
  try { const value = await ${body}; return { __e2e: 1, value: value === undefined ? null : value, blockedWrites: __blocked, dialogs: __dialogs }; }
  finally { page.off('dialog', __onDialog);${dry ? " await page.unroute('**/*');" : ''} }`
    const code = `async page => {\n  const P = ${JSON.stringify(P)};\n  const __blocked = [];\n  const H = {\n${[...helpers, `reportBlocked: (what) => { __blocked.push(String(what)); }`].join(',\n')}\n  };\n  ${run}\n}\n`
    mkdirSync(cwd, { recursive: true })
    // A composed file left behind by a killed run still holds a password; remove stale ones first.
    for (const f of readdirSync(cwd).filter((x) => /^\.run-\d+-\d+\.js$/.test(x))) rmSync(join(cwd, f), { force: true })
    const tmp = join(cwd, `.run-${process.pid}-${Date.now()}.js`)
    writeFileSync(tmp, code)
    let output
    try {
        output = cli(session, ['run-code', `--filename=${tmp}`], cwd)
    } catch (e) {
        return { ok: false, error: (e.stderr || e.stdout || e.message).toString().trim().split('\n').slice(0, 3).join(' ') }
    } finally {
        rmSync(tmp, { force: true })
    }
    const err = section(output, 'Error')
    if (err) return { ok: false, error: err.split('\n').slice(0, 3).join(' ') }
    // A dialog left open (e.g. beforeunload or confirm) makes run-code return without a result; never log that as success.
    const modal = section(output, 'Modal state')
    const res = section(output, 'Result')
    let value = null
    try { value = res ? JSON.parse(res) : null } catch { value = res }
    if (!(value && value.__e2e === 1)) {
        if (modal) {
            // The fragment's listener already accepted a beforeunload dialog, but playwright-cli keeps its own modal flag until a dialog
            // command clears it (an "already handled" error is expected). Other dialogs are left to the worker.
            const leave = /beforeunload/i.test(modal)
            if (leave) { try { cli(session, ['dialog-accept'], cwd) } catch { /* already handled */ } }
            return { ok: false, error: leave ? `beforeunload dialog interrupted the step; it was accepted (unsaved input on that page was discarded): ${modal.split('\n')[0]}` : `a dialog is open (handle it with playwright-cli dialog-accept or dialog-dismiss): ${modal.split('\n').slice(0, 2).join(' ')}` }
        }
        return { ok: false, error: 'run-code returned no fragment result' }
    }
    const blocked = value.blockedWrites ?? []
    if (value.dialogs?.length) return { ok: false, error: `beforeunload dialog interrupted the step; it was accepted: ${value.dialogs.join(' / ')}`, ...(blocked.length ? { blockedWrites: blocked } : {}) }
    // The fragment's value is returned unchanged; blocked requests are reported beside it.
    return { ok: true, value: value.value ?? null, ...(dry || blocked.length ? { blockedWrites: blocked } : {}) }
}

// Condensed accessibility snapshot for exploring a screen: drops generic-only lines and URLs.
export function peek({ session, cwd, from, max = 120 }) {
    const lines = section(cli(session, ['snapshot'], cwd), 'Snapshot')?.split('\n') ?? []
    let kept = lines.filter((l) => !/^\s*- generic \[ref=[a-z0-9]+\]:?$/.test(l) && !/^\s*- \/url:/.test(l) && !l.startsWith('```'))
    if (from) {
        const i = kept.findIndex((l) => l.includes(String(from)))
        kept = i >= 0 ? kept.slice(i) : []
    }
    return kept.slice(0, Number(max)).join('\n')
}

// Build contact-sheet HTML pages from shots/<prefix>*.png; the caller then runs probes/contact-sheet to capture them.
export function buildSheets(dir, prefix = '', per = 8) {
    const shots = readdirSync(join(dir, 'shots')).filter((f) => f.startsWith(prefix) && f.endsWith('.png')).sort()
    if (!shots.length) throw new Error('no matching screenshots in shots/')
    mkdirSync(join(dir, 'review'), { recursive: true })
    const n = Math.ceil(shots.length / per)
    for (let g = 0; g < n; g++) {
        const cells = shots.slice(g * per, (g + 1) * per).map((f) =>
            `<div style="position:relative"><img src="../shots/${f}" style="width:640px;display:block"><b style="position:absolute;top:0;left:0;background:#ff0;font:16px sans-serif">${f}</b></div>`)
        writeFileSync(join(dir, 'review', `sheet-${g + 1}.html`), `<html><body style="margin:0;background:#888;display:grid;grid-template-columns:repeat(2,640px);gap:4px">${cells.join('')}</body></html>`)
    }
    return { n, base: 'file:///' + dir.split('\\').join('/') }
}
