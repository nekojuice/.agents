// Locate the project assets (.e2e/), load its config and accounts, and read version markers.
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export const SKILL_DIR = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')

// Walk up from `start` until a directory containing `.e2e/` is found. `explicit` overrides the search.
export function findProject(start = process.cwd(), explicit) {
    if (explicit) {
        const root = resolve(explicit)
        return existsSync(join(root, '.e2e')) ? { root, assets: join(root, '.e2e') } : { root, assets: null }
    }
    let dir = resolve(start)
    for (;;) {
        if (existsSync(join(dir, '.e2e'))) return { root: dir, assets: join(dir, '.e2e') }
        const up = dirname(dir)
        if (up === dir) return { root: resolve(start), assets: null }
        dir = up
    }
}

const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'))

// Every *.json under .e2e/config/ becomes config.<name>; accounts.local.json is loaded separately and never echoed.
export function loadProject(assets) {
    const config = {}
    let accounts = {}
    const dir = assets ? join(assets, 'config') : null
    if (dir && existsSync(dir)) {
        for (const f of readdirSync(dir).filter((x) => x.endsWith('.json') && !x.includes('.example.'))) {
            if (f === 'accounts.local.json') accounts = readJson(join(dir, f))
            else config[f.slice(0, -5)] = readJson(join(dir, f))
        }
    }
    return { env: config.env ?? {}, config, accounts }
}

function frontmatterVersion(text) {
    return text.match(/^\s*version:\s*"?([^"\n]+)"?/m)?.[1]?.trim() ?? null
}

export function skillVersion() {
    return frontmatterVersion(readFileSync(join(SKILL_DIR, 'SKILL.md'), 'utf8'))
}

// PROJECT.md records the skill version it was last verified with, on a line "Verified skill version: x.y".
export function projectSkillVersion(assets) {
    const p = assets && join(assets, 'PROJECT.md')
    if (!p || !existsSync(p)) return null
    return readFileSync(p, 'utf8').match(/Verified skill version:\s*`?([\w.-]+)`?/i)?.[1] ?? null
}

// PROJECT.md may name the report language on a line "Report language: <locale>" (zh-TW, en); default zh-TW.
export function projectReportLocale(assets) {
    const p = assets && join(assets, 'PROJECT.md')
    if (!p || !existsSync(p)) return 'zh-TW'
    return readFileSync(p, 'utf8').match(/Report language:\s*`?([\w-]+)`?/i)?.[1] ?? 'zh-TW'
}
