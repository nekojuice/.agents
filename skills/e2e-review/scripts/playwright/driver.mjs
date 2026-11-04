// Playwright driver: every call to playwright-cli goes through this module.
// Fragments are single functions `async (page, P, H) => {}` composed with injected params and browser-side helpers.
import { execSync } from 'node:child_process'
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))

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

// Resolve a fragment: explicit path → project .e2e/<path> → skill generic probes.
export function resolveFragment(script, assets) {
    const withExt = script.endsWith('.js') ? script : `${script}.js`
    const candidates = [resolve(withExt), assets && join(assets, withExt), join(HERE, withExt)].filter(Boolean)
    const hit = candidates.find((p) => existsSync(p))
    if (!hit) throw new Error(`fragment not found: ${script}`)
    return hit
}

// P must not carry secrets into logs; the composed file holds them only for the call and is deleted right after.
export function runFragment({ session, file, P, assets, cwd }) {
    const helpers = loadHelpers([join(HERE, 'helpers'), assets && join(assets, 'helpers')])
    const code = `async page => {\n  const P = ${JSON.stringify(P)};\n  const H = {\n${helpers.join(',\n')}\n  };\n  return await (${stripFn(readFileSync(file, 'utf8'))})(page, P, H);\n}\n`
    mkdirSync(cwd, { recursive: true })
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
    const res = section(output, 'Result')
    let value = null
    try { value = res ? JSON.parse(res) : null } catch { value = res }
    return { ok: true, value }
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
