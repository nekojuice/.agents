// data/manifest.json: machine-readable record of data this round created or changed.
// `events` keeps every write in order (automatic entries from API write calls, entries from api.record and ctx.addWrite);
// `latest` is derived from it: one entry per type + id with its fields merged in event order.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { redact } from './secrets.mjs'

function latestOf(events) {
    const out = []
    const idx = new Map()
    for (const e of events) {
        if (e.id == null || e.type == null) continue
        const k = `${e.type}\u0000${e.id}`
        if (idx.has(k)) out[idx.get(k)] = { ...out[idx.get(k)], ...e }
        else { idx.set(k, out.length); out.push({ ...e }) }
    }
    return out
}

// A 1.2 manifest ({ entries }) is read as events.
export function readManifest(dir) {
    const p = join(dir, 'data', 'manifest.json')
    const m = existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : {}
    const events = m.events ?? m.entries ?? []
    return { events, latest: latestOf(events) }
}

export function addManifest(dir, entry) {
    mkdirSync(join(dir, 'data'), { recursive: true })
    const { events } = readManifest(dir)
    events.push(entry)
    writeFileSync(join(dir, 'data', 'manifest.json'), JSON.stringify(redact({ events, latest: latestOf(events) }), null, 2))
}
