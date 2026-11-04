// Scenario context: what a solidified scenario receives. Scenarios are `export default async (ctx, opts) => {}` and import nothing from the skill.
// Several scenarios may share one round: each owns the entries it records (tagged src: <scenario name>), and a rerun
// replaces only its own entries. Manual additions (src "manual") and other scenarios' entries are kept.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { addManifest } from './manifest.mjs'
import { redact } from './secrets.mjs'
import { localIso, readSteps, readValue, slugName, verdictOf, writeValue as storeValue } from './task.mjs'
import { ownerOf, toMs } from './trace.mjs'

export { toMs }

// UTC ISO strings (ending in Z or carrying an offset) become local time; anything else is kept.
export function toLocal(t) {
    if (typeof t !== 'string' || !/(Z|[+-]\d{2}:?\d{2})$/.test(t)) return t
    const d = new Date(t)
    return Number.isNaN(d.getTime()) ? t : localIso(d)
}

// Deep equality of JSON values that ignores object key order; arrays keep their order.
// Dates compare by time; other non-plain objects (Map, Set, class instances) are equal only when they are the same object.
export function same(a, b) {
    if (a === b) return true
    if (typeof a !== typeof b || a === null || b === null || typeof a !== 'object') return Number.isNaN(a) && Number.isNaN(b)
    if (a instanceof Date || b instanceof Date) return a instanceof Date && b instanceof Date && a.getTime() === b.getTime()
    if (Array.isArray(a) !== Array.isArray(b)) return false
    if (Array.isArray(a)) return a.length === b.length && a.every((x, i) => same(x, b[i]))
    const plain = (o) => [Object.prototype, null].includes(Object.getPrototypeOf(o))
    if (!plain(a) || !plain(b)) return false
    const ka = Object.keys(a)
    const kb = Object.keys(b)
    return ka.length === kb.length && ka.every((k) => Object.hasOwn(b, k) && same(a[k], b[k]))
}

export const PART_FIELDS = ['checks', 'items', 'limits', 'issues', 'uiFindings', 'observations']
const srcOf = (e) => (e && typeof e === 'object' ? e.src : undefined)
const tag = (e, name) => (typeof e === 'string' ? { text: e, src: name } : { ...e, src: name })
const isWriteRef = (ref) => /(^|[:/\\])actions[/\\]/.test(String(ref))
const surfaceOf = (ref) => String(ref).match(/^([a-z][\w-]*):(?![\\/])/i)?.[1] ?? null
const WRITE_FIELDS = ['what', 'where', 'how']

// runStep(ref, args, opts) runs a fragment through the surface's driver and returns { ok, value, error, step }.
// mode: null (formal) or 'dry' (no writes sent; own result under dry/<name>/).
export function createContext({ dir, project, loaded, runStep, name = 'scenario', mode = null }) {
    const slug = slugName(name)
    const resultPath = join(dir, 'result.json')
    const sideDir = mode === 'dry' ? join(dir, 'dry', slug) : dir
    if (mode) mkdirSync(sideDir, { recursive: true })
    const savePath = mode ? join(sideDir, 'result.json') : resultPath
    // The base a save merges into: a dry run keeps its own copy; a formal run merges into the round's result.
    const basePath = () => (mode === 'dry' && existsSync(savePath) ? savePath : resultPath)
    const base = JSON.parse(readFileSync(basePath(), 'utf8'))
    // The scenario sees a fresh view: its own entries start empty, writes are shared across runs and scenarios.
    const result = { ...base, task: { ...base.task }, env: { ...base.env }, writes: [...(base.writes ?? [])], reproduce: [] }
    for (const f of PART_FIELDS) result[f] = []
    const own = { verdict: null, summary: '', stats: null }

    function merge() {
        const disk = JSON.parse(readFileSync(basePath(), 'utf8'))
        const merged = { ...disk }
        // A rerun's entries take the place of the scenario's earlier entries, so the order of blocks stays stable.
        for (const f of PART_FIELDS) {
            const mine = (result[f] ?? []).map((e) => tag(e, name))
            const old = disk[f] ?? []
            const at = old.findIndex((e) => srcOf(e) === name)
            const rest = old.filter((e) => srcOf(e) !== name)
            const cut = at < 0 ? rest.length : old.slice(0, at).filter((e) => srcOf(e) !== name).length
            merged[f] = [...rest.slice(0, cut), ...mine, ...rest.slice(cut)]
        }
        const seen = new Set((disk.writes ?? []).map((w) => `${w.what}\u0000${w.at}`))
        merged.writes = [...(disk.writes ?? []), ...result.writes.filter((w) => !seen.has(`${w.what}\u0000${w.at}`))]
        merged.task = { ...disk.task, ...Object.fromEntries(Object.entries(result.task).filter(([, v]) => v !== '' && v != null)) }
        merged.reproduce = [...(disk.reproduce ?? []), ...result.reproduce.filter((l) => !(disk.reproduce ?? []).includes(l))]
        merged.parts = { ...(disk.parts ?? {}), [name]: { ...own, mode: mode ?? 'formal', at: localIso() } }
        const sums = Object.entries(merged.parts).filter(([, p]) => p.summary)
        merged.summary = sums.length === 1 ? sums[0][1].summary : sums.map(([k, p]) => `${k}: ${p.summary}`).join('\n')
        Object.assign(merged, verdictOf(merged.checks) ?? {})
        return merged
    }

    function save() {
        writeFileSync(savePath, JSON.stringify(redact(merge()), null, 2))
        result.reproduce.length = 0
    }

    const failedSteps = []
    const skippedSteps = []
    const beforeFailure = new Set()
    let blockedBy = null
    let lintCount = 0

    // opts.always: run even after an earlier write step failed (e.g. a restore step). opts.expects: audit rows this step produces.
    // The write stop applies to formal runs only: in a dry run the guard blocks writes on purpose.
    async function run(ref, args = {}, saveAs, opts = {}) {
        const write = isWriteRef(ref)
        if (!mode && write && blockedBy && !opts.always) {
            const error = `skipped: earlier write step failed (${blockedBy})`
            const now = localIso()
            failedSteps.push(ref)
            skippedSteps.push({ ref, save: saveAs ?? null })
            if (saveAs) beforeFailure.delete(`values/${saveAs}.json`)
            result.issues.push(`${ref} ${error}`)
            save()
            return { ok: false, skipped: true, error, value: null, step: { startedAt: now, endedAt: now, surface: surfaceOf(ref), skipped: true } }
        }
        const res = await runStep(ref, { ...args, ...(saveAs ? { save: saveAs } : {}) }, { expects: opts.expects })
        // Value files written before the first write failure cannot depend on a write skipped after it. A save name written
        // again after the failure no longer counts.
        if (saveAs) {
            const f = `values/${saveAs}.json`
            if (res.ok && !blockedBy) beforeFailure.add(f)
            else beforeFailure.delete(f)
        }
        if (!res.ok) {
            failedSteps.push(ref)
            if (!mode && write && !blockedBy) blockedBy = ref
            result.issues.push(`${ref} failed: ${res.error}`)
            save()
        }
        return res
    }

    // After skipped write steps, may a false check stand as a product failure? Only when it is clearly unrelated: it cites
    // evidence, and every piece of it is a value file written before the first write failure. Evidence from steps that ran
    // after the failure (e.g. a probe reading back what the skipped write should have created), a skipped step's value,
    // or no evidence at all cannot be told apart: run-error.
    function dependsOnSkipped(evidence) {
        const ev = (Array.isArray(evidence) ? evidence : [evidence]).filter(Boolean).map((e) => String(e).replace(/\\/g, '/'))
        return !(ev.length && ev.every((e) => [...beforeFailure].some((f) => e === f || e.endsWith(`/${f}`))))
    }

    // pass: true → pass, false → fail, null → inconclusive. Run-error instead of a verdict:
    // - pass null after a failed step;
    // - pass false after a skipped write step, unless the check is clearly unrelated to it (see dependsOnSkipped).
    // opts.via: web | api | db (how the check was verified); opts.by overrides the source (e.g. 'value' for a read value awaiting a decision);
    // opts.agent: true when the judgment rests on an agent-operated recipe step.
    function check(id, title, expected, actual, pass, evidence = [], note = '', opts = {}) {
        let verdict = pass === null ? 'inconclusive' : pass ? 'pass' : 'fail'
        let by = opts.by ?? 'script'
        let why = note
        if (!opts.by) {
            if (pass === false && skippedSteps.length && dependsOnSkipped(evidence)) {
                verdict = 'inconclusive'; by = 'run-error'
                why = `skipped write steps: ${[...new Set(skippedSteps.map((s) => s.ref))].join(', ')}${note ? `; ${note}` : ''}`
            } else if (pass === null && failedSteps.length) {
                by = 'run-error'
                why = note || `failed steps: ${[...new Set(failedSteps)].join(', ')}`
            }
        }
        result.checks.push({ id, title, expected, actual, verdict, by, via: opts.via ?? null, agent: Boolean(opts.agent), evidence, note: why })
        save()
    }

    // Checks the worker cannot run here (environment missing, human-only) or can only judge visually.
    function manual(id, title, expected, by, note, evidence = [], opts = {}) {
        result.checks.push({ id, title, expected, actual: by === 'not-run' ? 'not run' : '', verdict: 'inconclusive', by, via: opts.via ?? null, agent: false, evidence, note })
        save()
    }

    // Data writes: kept across reruns (duplicates skipped), times normalized to local, mirrored into data/manifest.json.
    // A write is recorded even when fields are missing (shown as —, with an issue), so a write that already happened never loses its trace.
    function addWrite(w) {
        const src = w && typeof w === 'object' && !Array.isArray(w) ? w : { what: String(w ?? '') }
        const missing = WRITE_FIELDS.filter((k) => typeof src[k] !== 'string' || !src[k].trim())
        const entry = { ...src, ...Object.fromEntries(missing.map((k) => [k, '—'])), at: toLocal(src.at ?? localIso()) }
        if (missing.length) result.issues.push(`addWrite entry is missing ${missing.join(', ')}: ${JSON.stringify(redact(src)).slice(0, 200)}`)
        if (!result.writes.some((x) => x.what === entry.what && x.at === entry.at)) {
            result.writes.push(entry)
            if (!mode) addManifest(dir, { type: 'write', ...entry })
        }
        save()
    }

    // UI findings a scenario adds; replaced on rerun like automatic ones.
    function finding(f) {
        result.uiFindings.push({ scenario: true, ...f })
        save()
    }

    // A dry run reads and writes its own folder; a formal run reads and writes the round.
    const valueFile = (n) => readValue(sideDir, n)
    const writeValue = (n, v) => storeValue(sideDir, n, v)
    const lastStep = () => readSteps(sideDir).at(-1)
    const inStep = (t, st, before = 1000, after = 2000) => toMs(t) >= toMs(st.startedAt) - before && toMs(t) <= toMs(st.endedAt) + after
    const ownerStep = (t, row = {}) => ownerOf(readSteps(sideDir), t, row)

    // Run the generic UI lint probe on the current web screen and record findings as auto UI findings.
    async function lint(where, { scope, shot, surface = 'web' } = {}) {
        // Numbered so non-ASCII locations never collapse into the same file name
        lintCount += 1
        const s = String(shot ?? where).replace(/[^\w-]+/g, '-').replace(/^-+|-+$/g, '')
        const n = `lint-${String(lintCount).padStart(2, '0')}${s ? `-${s}` : ''}`
        const res = await run(`${surface}:probes/ui-lint`, { ...(scope ? { scope } : {}), ...(shot ? { shot } : {}) }, n)
        for (const f of res.value?.findings ?? [])
            result.uiFindings.push({ auto: true, type: f.type, rule: f.rule, where, what: f.what, samples: f.samples, evidence: [`values/${n}.json`, ...(res.value.shot ? [res.value.shot] : [])] })
        save()
        return res.value?.findings ?? []
    }

    // The summary keeps the scenario's own words; counts are rendered by the report in its locale.
    function finish(summary = '') {
        // Unchanged from 1.2: a scenario without checks reports pass with zero counts; the report shows that no checks exist.
        const v = verdictOf(result.checks) ?? { verdict: 'pass', stats: { checks: 0, failed: 0, inconclusive: 0 } }
        Object.assign(own, { verdict: v.verdict, summary: String(summary).trim(), stats: v.stats })
        Object.assign(result, own)
        save()
        return { ...own }
    }

    return {
        dir, project, name, mode, dry: mode === 'dry', env: loaded.env, config: loaded.config, accounts: Object.keys(loaded.accounts), result, save,
        run, check, manual, addWrite, finding, valueFile, writeValue, lastStep, inStep, ownerStep, toMs, toLocal, same, lint, finish
    }
}
