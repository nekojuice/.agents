// Audit trail: call the project's adapter (.e2e/audit/fetch.mjs) for the task's time window and store normalized rows.
import { existsSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { localIso, readSteps } from './task.mjs'

// Adapter contract: export default async ({ from, to, users, env, config }) => [{ time, user, action, target, detail, source }]
// time is local ISO (yyyy-MM-ddTHH:mm:ss[.fff]); action should be a short code with a readable label, e.g. "01 login".
export async function fetchAudit(project, loaded, dir, users) {
    const adapter = project.assets && join(project.assets, 'audit', 'fetch.mjs')
    if (!adapter || !existsSync(adapter)) throw new Error('no audit adapter: expected .e2e/audit/fetch.mjs (see references/project-profile.md)')
    const steps = readSteps(dir)
    if (!steps.length) throw new Error('no steps recorded in this task folder')
    const from = steps[0].startedAt
    const to = steps.at(-1).endedAt
    const { default: fetchRows } = await import(pathToFileURL(adapter).href)
    const rows = (await fetchRows({ from, to, users, env: loaded.env, config: loaded.config }))
        .filter((r) => r.time >= from && r.time <= to)
        .sort((a, b) => a.time.localeCompare(b.time))
    const out = { source: 'project adapter .e2e/audit/fetch.mjs', users, window: [from, to], fetchedAt: localIso(), rows }
    writeFileSync(join(dir, 'values', 'audit.json'), JSON.stringify(out, null, 2))
    return rows.length
}
