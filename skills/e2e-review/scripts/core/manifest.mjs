// data/manifest.json: machine-readable record of data this round created or changed.
// Entries with an id and type are merged; automatic entries come from API write calls.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { redact } from './secrets.mjs'

export function readManifest(dir) {
    const p = join(dir, 'data', 'manifest.json')
    return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : { entries: [] }
}

export function addManifest(dir, entry) {
    mkdirSync(join(dir, 'data'), { recursive: true })
    const m = readManifest(dir)
    const i = entry.id != null ? m.entries.findIndex((e) => e.id === entry.id && e.type === entry.type) : -1
    if (i >= 0) m.entries[i] = { ...m.entries[i], ...entry }
    else m.entries.push(entry)
    writeFileSync(join(dir, 'data', 'manifest.json'), JSON.stringify(redact(m), null, 2))
}
