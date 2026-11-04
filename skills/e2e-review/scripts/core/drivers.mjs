// Surfaces and drivers: a surface is a registered target of the system under test (env.surfaces.<name>);
// its driver executes fragments. Drivers live in scripts/drivers/<driver>/driver.mjs and export
// { name, extensions, runFragment({ file, P, ctx }) } where ctx carries project, surface, dir, dry and session.
import { existsSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { SKILL_DIR } from './project.mjs'

const DRIVERS = join(SKILL_DIR, 'scripts', 'drivers')
const cache = new Map()

export function surfaces(env) {
    return env.surfaces ?? {}
}

export function defaultSurface(env) {
    const names = Object.keys(surfaces(env))
    return env.defaultSurface ?? (names.includes('web') ? 'web' : names[0]) ?? null
}

export function surfaceConfig(env, name) {
    const cfg = surfaces(env)[name]
    if (!cfg) throw new Error(`surface not registered in config/env.json surfaces: ${name}`)
    if (!cfg.driver) throw new Error(`surface ${name} has no driver`)
    return cfg
}

// "<surface>:<path>" → { surface, path }; without a prefix the default surface applies.
export function parseRef(ref, env) {
    const m = String(ref).match(/^([a-z][\w-]*):(?![\\/])(.+)$/i)
    return m ? { surface: m[1], path: m[2] } : { surface: defaultSurface(env), path: String(ref) }
}

export function driverExists(name) {
    return existsSync(join(DRIVERS, name, 'driver.mjs'))
}

export async function loadDriver(name) {
    if (!cache.has(name)) {
        const file = join(DRIVERS, name, 'driver.mjs')
        if (!existsSync(file)) throw new Error(`driver not shipped with the skill: ${name}`)
        cache.set(name, await import(pathToFileURL(file).href))
    }
    return cache.get(name)
}

// A fragment declares its driver in a comment within its first lines: "// @driver playwright".
export function declaredDriver(file) {
    const head = readFileSync(file, 'utf8').split('\n').slice(0, 5).join('\n')
    return head.match(/@driver\s+([\w-]+)/)?.[1] ?? null
}

// Lookup: explicit path → .e2e/surfaces/<surface>/<path> → skill scripts/drivers/<driver>/<path>.
export function resolveFragment(ref, driver, project) {
    const { surface, path } = ref
    const exts = driver.extensions
    const withExts = (p) => (exts.some((e) => p.endsWith(e)) ? [p] : exts.map((e) => p + e))
    const candidates = [
        ...withExts(resolve(path)),
        ...(project.assets ? withExts(join(project.assets, 'surfaces', surface, path)) : []),
        ...withExts(join(DRIVERS, driver.name, path))
    ]
    const hit = candidates.find((p) => existsSync(p))
    if (!hit) throw new Error(`fragment not found: ${surface}:${path}`)
    const declared = declaredDriver(hit)
    if (declared && declared !== driver.name) throw new Error(`${hit} declares driver ${declared}, surface ${surface} uses ${driver.name}`)
    return hit
}

// Where a fragment came from, for the step log: kind script (promoted or generic) or adhoc (anything else, e.g. scratch).
export function fragmentLabel(file, project, surface, driverName) {
    const norm = (p) => p.replace(/\\/g, '/')
    const f = norm(file)
    const proj = project.assets && norm(join(project.assets, 'surfaces', surface)) + '/'
    const skill = norm(join(DRIVERS, driverName)) + '/'
    const strip = (s) => s.replace(/\.(m?js|py)$/, '')
    if (proj && f.startsWith(proj)) return { script: `${surface}:${strip(f.slice(proj.length))}`, kind: 'script' }
    if (f.startsWith(skill)) return { script: `${surface}:${strip(f.slice(skill.length))}`, kind: 'script' }
    return { script: f, kind: 'adhoc' }
}
