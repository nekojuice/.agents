// Audit trail: call the project's adapter (.e2e/audit/fetch.mjs) for a time window and store normalized rows.
import { existsSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { localIso, readSideSteps, readSteps } from './task.mjs'
import { AFTER_MS, attribute, toMs } from './trace.mjs'

// Adapter contract: export default async ({ from, to, users, actions, includeSystem, env, config }) => [{ time, user, action, target, detail, source }]
// time is local ISO (yyyy-MM-ddTHH:mm:ss[.fff]); action should be a short code with a readable label, e.g. "<code> login".
// actions (codes) and includeSystem (rows the system itself wrote, without a user) are optional; an adapter that ignores them still works.
// scope 'formal' covers the formal steps (values/audit.json); scope 'side' covers dry runs and rehearsals (values/audit-side.json).

// Formal and side steps on one timeline, side ones marked; used for attribution here and in the report.
export function sideAndFormal(dir, side = readSideSteps(dir)) {
    return [...readSteps(dir).map((s) => ({ ...s, side: false })), ...side.map((s) => ({ ...s, side: true }))]
        .sort((a, b) => String(a.startedAt).localeCompare(String(b.startedAt)))
}

// [first start, last end + AFTER_MS]: the end allowance matches attribution, so rows a step produced just after it ended are kept.
function windowOf(steps) {
    if (!steps.length) return null
    const end = steps.reduce((m, s) => Math.max(m, toMs(s.endedAt)), toMs(steps[0].endedAt))
    return [steps[0].startedAt, localIso(new Date(end + AFTER_MS))]
}

const inWindow = (w, t) => Boolean(w) && t >= w[0].slice(0, String(t).length) && t <= w[1]

// Returns the row count, or null when the scope has no steps.
// The two sections never share a row and lose none: a row clearly owned by a dry-run or rehearsal step goes to the side
// section; every other row inside the formal window goes to the formal section; every row outside the formal window goes
// to the side section (the report marks rows with no step or an uncertain one).
export async function fetchAudit(project, loaded, dir, users, { scope = 'formal', actions = [], includeSystem = false } = {}) {
    const adapter = project.assets && join(project.assets, 'audit', 'fetch.mjs')
    if (!adapter || !existsSync(adapter)) throw new Error('no audit adapter: expected .e2e/audit/fetch.mjs (see references/project-profile.md)')
    const formalSteps = readSteps(dir)
    const sideSteps = readSideSteps(dir)
    const steps = scope === 'side' ? sideSteps : formalSteps
    if (!steps.length) return null
    const [from, to] = windowOf(steps)
    const { default: fetchRows } = await import(pathToFileURL(adapter).href)
    let rows = (await fetchRows({ from, to, users, actions, includeSystem, env: loaded.env, config: loaded.config }))
        // A row cut to whole seconds compares against the window start cut the same way.
        .filter((r) => inWindow([from, to], r.time))
        .sort((a, b) => a.time.localeCompare(b.time))
    if (sideSteps.length) {
        const all = sideAndFormal(dir, sideSteps)
        const owner = attribute(all, rows)
        const formalWindow = windowOf(formalSteps)
        const sideOwned = (i) => owner[i].step >= 0 && owner[i].how !== 'ambiguous' && all[owner[i].step].side
        rows = scope === 'side'
            ? rows.filter((r, i) => sideOwned(i) || !inWindow(formalWindow, r.time))
            : rows.filter((_, i) => !sideOwned(i))
    }
    const out = { source: 'project adapter .e2e/audit/fetch.mjs', scope, users, actions, includeSystem, window: [from, to], fetchedAt: localIso(), rows }
    writeFileSync(join(dir, 'values', scope === 'side' ? 'audit-side.json' : 'audit.json'), JSON.stringify(out, null, 2))
    return rows.length
}
