// HTTP driver: API fragments are ES modules `export default async (api, P, H) => {}` run inside this Node process.
// Every call is logged to exchanges/ (redacted, truncated); write methods also enter data/manifest.json.
// Login comes from the project's surfaces/<surface>/helpers/auth.mjs; sessions stay in memory only.
import { existsSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { addManifest } from '../../core/manifest.mjs'
import { addSecret, redact } from '../../core/secrets.mjs'
import { localIso } from '../../core/task.mjs'

export const name = 'http'
export const extensions = ['.mjs', '.js']

export function available() {
    return typeof fetch === 'function' ? `node ${process.versions.node}` : null
}

const MAX_BODY = 20000
const WRITE = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])
const sessions = new Map() // `${surface}|${accountKey}` → { headers, cookies }

function nextExchangeFile(dir, label) {
    const ex = join(dir, 'exchanges')
    mkdirSync(ex, { recursive: true })
    const n = readdirSync(ex).filter((f) => f.endsWith('.json')).length + 1
    const slug = String(label).replace(/[^\w-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60)
    return join(ex, `${String(n).padStart(3, '0')}-${slug || 'call'}.json`)
}

function truncate(body) {
    const s = typeof body === 'string' ? body : JSON.stringify(body)
    if (s == null || s.length <= MAX_BODY) return body
    return { truncated: true, length: s.length, head: s.slice(0, MAX_BODY) }
}

async function loadHelpers(dirs) {
    const H = {}
    for (const d of dirs.filter((x) => x && existsSync(x)))
        for (const f of readdirSync(d).filter((x) => /\.m?js$/.test(x))) H[f.replace(/\.m?js$/, '')] = (await import(pathToFileURL(join(d, f)).href)).default
    return H
}

// The client a fragment receives. `as(key)` returns a client logged in as another account.
// `bound` is the session a login client writes into, so cookies set by the login response reach the account's session.
export function createClient({ surface, cfg, accounts, accountKey, dir, label, dry, H, bound = null }) {
    const base = String(cfg.baseUrl ?? '').replace(/\/$/, '')
    const key = `${surface}|${accountKey ?? ''}`

    async function raw(method, path, { body, query, headers = {}, session } = {}) {
        const url = new URL(base + path)
        for (const [k, v] of Object.entries(query ?? {})) url.searchParams.set(k, v)
        const h = { accept: 'application/json', ...(body !== undefined ? { 'content-type': 'application/json' } : {}), ...(session?.headers ?? {}), ...headers }
        const cookies = session?.cookies ?? {}
        if (Object.keys(cookies).length) h.cookie = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ')
        const at = localIso()
        const record = { at, surface, account: accountKey ?? null, method, url: url.toString(), dry: Boolean(dry), request: { headers: h, body } }
        let res = { status: 0, headers: {}, body: null, dry: Boolean(dry) }
        if (dry) res.request = { method, url: url.toString(), body }
        else {
            const r = await fetch(url, { method, headers: h, body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body) })
            const text = await r.text()
            let parsed = text
            try { parsed = text ? JSON.parse(text) : null } catch { /* keep text */ }
            const setCookie = r.headers.getSetCookie?.() ?? []
            if (session) for (const c of setCookie) {
                const [pair] = c.split(';')
                const i = pair.indexOf('=')
                if (i > 0) { session.cookies[pair.slice(0, i).trim()] = pair.slice(i + 1).trim(); addSecret(pair.slice(i + 1).trim()) }
            }
            res = { status: r.status, headers: Object.fromEntries([...r.headers.entries()].filter(([k]) => k !== 'set-cookie')), body: parsed }
        }
        record.status = res.status
        // Redact before truncating so key-based masking still applies to large bodies.
        record.request.body = truncate(redact(body))
        record.response = { headers: res.headers, body: truncate(redact(res.body)) }
        // Login exchanges carry credentials and tokens before they are known as secrets: keep only the outline.
        if (bound) {
            record.request.body = body === undefined ? undefined : '<login request body omitted>'
            record.response = { headers: '<login response headers omitted>', body: res.body == null ? null : '<login response body omitted>' }
        }
        if (dir) {
            writeFileSync(nextExchangeFile(dir, `${label}-${method}`), JSON.stringify(redact(record), null, 2))
            if (WRITE.has(method) && !dry && !bound) addManifest(dir, { auto: true, at, method, path, status: res.status, account: accountKey ?? null, surface })
        }
        return res
    }

    async function session() {
        if (bound) return bound
        // A dry run sends nothing, so it does not log in either.
        if (!accountKey || dry) return null
        if (!sessions.has(key)) {
            const s = { headers: {}, cookies: {} }
            sessions.set(key, s)
            const account = accounts[accountKey]
            if (!account) throw new Error(`unknown account key: ${accountKey}`)
            if (!H.auth) throw new Error(`surface ${surface} has no helpers/auth.mjs; cannot log in ${accountKey}`)
            const login = createClient({ surface, cfg, accounts, accountKey: null, dir, label: `${label}-login`, dry: false, H, bound: s })
            const out = (await H.auth(login, account, { surface, cfg, accountKey, session: s })) ?? {}
            Object.assign(s.headers, out.headers ?? {})
            for (const v of Object.values(out.headers ?? {})) addSecret(String(v).replace(/^Bearer\s+/i, ''))
        }
        return sessions.get(key)
    }

    const call = (method) => async (path, opts = {}) => raw(method, path, { ...opts, session: await session() })
    return {
        get: call('GET'), post: call('POST'), put: call('PUT'), patch: call('PATCH'), del: call('DELETE'),
        request: (method, path, opts) => call(String(method).toUpperCase())(path, opts),
        as: (otherKey) => createClient({ surface, cfg, accounts, accountKey: otherKey, dir, label, dry, H }),
        record: (entry) => dir && addManifest(dir, { at: localIso(), surface, ...entry }),
        dry: Boolean(dry)
    }
}

export async function runFragment({ file, P, ctx }) {
    const { project, surface, cfg, accounts, dir, dry, label } = ctx
    try {
        const H = await loadHelpers([project.assets && join(project.assets, 'surfaces', surface, 'helpers')])
        const api = createClient({ surface, cfg, accounts, accountKey: P.accountKey, dir, label, dry, H })
        const mod = await import(pathToFileURL(file).href + `?t=${Date.now()}`)
        if (typeof mod.default !== 'function') return { ok: false, error: `${file} has no default export function` }
        const value = await mod.default(api, { ...P, dry: Boolean(dry) }, H)
        return { ok: true, value: value ?? null }
    } catch (e) {
        return { ok: false, error: String(e?.message ?? e).split('\n').slice(0, 3).join(' ') }
    }
}

// Ad-hoc single call (e2e.mjs api). Same logging as fragments.
export async function call({ method, path, body, ctx, accountKey }) {
    const { project, surface, cfg, accounts, dir, dry, label } = ctx
    const H = await loadHelpers([project.assets && join(project.assets, 'surfaces', surface, 'helpers')])
    const api = createClient({ surface, cfg, accounts, accountKey, dir, label, dry, H })
    return api.request(method, path, body === undefined ? {} : { body })
}
