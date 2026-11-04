// Scenario context: what a solidified scenario receives. Scenarios are `export default async (ctx, opts) => {}` and import nothing from the skill.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { addManifest } from './manifest.mjs'
import { redact } from './secrets.mjs'
import { localIso, readSteps } from './task.mjs'

export function toMs(s) {
    const m = String(s).match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})[ T](\d{1,2}):(\d{2}):(\d{2})(?:\.(\d+))?/)
    if (!m) return NaN
    const [, y, mo, d, h, mi, se, f = '0'] = m
    return new Date(+y, +mo - 1, +d, +h, +mi, +se, +f.padEnd(3, '0').slice(0, 3)).getTime()
}

// UTC ISO strings (ending in Z or carrying an offset) become local time; anything else is kept.
export function toLocal(t) {
    if (typeof t !== 'string' || !/(Z|[+-]\d{2}:?\d{2})$/.test(t)) return t
    const d = new Date(t)
    return Number.isNaN(d.getTime()) ? t : localIso(d)
}

// Same attribution rule as the report: the last step started before t (300 ms tolerance), if t is within 1.5 s of its end.
export function ownerOf(steps, t) {
    const x = toMs(t)
    let k = -1
    steps.forEach((st, i) => { if (toMs(st.startedAt) - 300 <= x) k = i })
    return k >= 0 && x <= toMs(steps[k].endedAt) + 1500 ? steps[k] : null
}

// runStep(ref, args) runs a fragment through the surface's driver and returns { ok, value, error, step }.
export function createContext({ dir, project, loaded, runStep, dry = false }) {
    const resultPath = join(dir, 'result.json')
    const result = JSON.parse(readFileSync(resultPath, 'utf8'))
    // A dry run rehearses without touching the formal result; it keeps its own copy under dry/.
    const savePath = dry ? join(dir, 'dry', 'result.json') : resultPath
    if (dry) mkdirSync(join(dir, 'dry'), { recursive: true })
    // Checks, items, limits and issues describe this execution; writes accumulate because data writes survive reruns.
    Object.assign(result, { checks: [], items: [], limits: [], issues: [], writes: result.writes ?? [], uiFindings: (result.uiFindings ?? []).filter((f) => !f.auto && !f.scenario) })
    const save = () => writeFileSync(savePath, JSON.stringify(redact(result), null, 2))
    const stepsDir = dry ? join(dir, 'dry') : dir
    const failedSteps = []
    let lintCount = 0

    async function run(ref, args = {}, saveAs) {
        const res = await runStep(ref, { ...args, ...(saveAs ? { save: saveAs } : {}) })
        if (!res.ok) {
            failedSteps.push(ref)
            result.issues.push(`${ref} failed: ${res.error}`)
            save()
        }
        return res
    }

    // pass: true → pass, false → fail, null → inconclusive. Inconclusive checks after a failed step are attributed to run-error.
    // opts.via: web | api | db (how the check was verified); opts.by overrides the source (e.g. 'value' for a read value awaiting a decision);
    // opts.agent: true when the judgment rests on an agent-operated recipe step.
    function check(id, title, expected, actual, pass, evidence = [], note = '', opts = {}) {
        const verdict = pass === null ? 'inconclusive' : pass ? 'pass' : 'fail'
        const by = opts.by ?? (pass === null && failedSteps.length ? 'run-error' : 'script')
        const why = by === 'run-error' && !note ? `failed steps: ${[...new Set(failedSteps)].join(', ')}` : note
        result.checks.push({ id, title, expected, actual, verdict, by, via: opts.via ?? null, agent: Boolean(opts.agent), evidence, note: why })
        save()
    }

    // Checks the worker cannot run here (environment missing, human-only) or can only judge visually.
    function manual(id, title, expected, by, note, evidence = [], opts = {}) {
        result.checks.push({ id, title, expected, actual: by === 'not-run' ? 'not run' : '', verdict: 'inconclusive', by, via: opts.via ?? null, agent: false, evidence, note })
        save()
    }

    // Data writes: kept across reruns (duplicates skipped), times normalized to local, mirrored into data/manifest.json.
    function addWrite(w) {
        const entry = { ...w, at: toLocal(w.at ?? localIso()) }
        if (!result.writes.some((x) => x.what === entry.what && x.at === entry.at)) result.writes.push(entry)
        if (!dry) addManifest(dir, { type: 'write', ...entry })
        save()
    }

    // UI findings a scenario adds; replaced on rerun like automatic ones.
    function finding(f) {
        result.uiFindings.push({ scenario: true, ...f })
        save()
    }

    const valueFile = (name) => {
        const p = join(stepsDir, 'values', `${name}.json`)
        return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : null
    }
    const writeValue = (name, v) => {
        mkdirSync(join(stepsDir, 'values'), { recursive: true })
        writeFileSync(join(stepsDir, 'values', `${name}.json`), JSON.stringify(redact(v), null, 2))
    }
    const lastStep = () => readSteps(stepsDir).at(-1)
    const inStep = (t, st, before = 1000, after = 2000) => toMs(t) >= toMs(st.startedAt) - before && toMs(t) <= toMs(st.endedAt) + after
    const ownerStep = (t) => ownerOf(readSteps(stepsDir), t)

    // Run the generic UI lint probe on the current web screen and record findings as auto UI findings.
    async function lint(where, { scope, shot, surface = 'web' } = {}) {
        // Numbered so non-ASCII locations never collapse into the same file name
        lintCount += 1
        const slug = String(shot ?? where).replace(/[^\w-]+/g, '-').replace(/^-+|-+$/g, '')
        const name = `lint-${String(lintCount).padStart(2, '0')}${slug ? `-${slug}` : ''}`
        const res = await run(`${surface}:probes/ui-lint`, { ...(scope ? { scope } : {}), ...(shot ? { shot } : {}) }, name)
        for (const f of res.value?.findings ?? [])
            result.uiFindings.push({ auto: true, type: f.type, rule: f.rule, where, what: f.what, samples: f.samples, evidence: [`values/${name}.json`, ...(res.value.shot ? [res.value.shot] : [])] })
        save()
        return res.value?.findings ?? []
    }

    // The summary keeps the scenario's own words; counts are rendered by the report in its locale.
    function finish(summary = '') {
        const failed = result.checks.filter((c) => c.verdict === 'fail').length
        const unknown = result.checks.filter((c) => c.verdict === 'inconclusive').length
        result.verdict = failed ? 'fail' : unknown ? 'inconclusive' : 'pass'
        result.summary = String(summary).trim()
        result.stats = { checks: result.checks.length, failed, inconclusive: unknown }
        save()
        return { verdict: result.verdict, summary: result.summary, stats: result.stats }
    }

    return {
        dir, project, dry, env: loaded.env, config: loaded.config, accounts: Object.keys(loaded.accounts), result, save,
        run, check, manual, addWrite, finding, valueFile, writeValue, lastStep, inStep, ownerStep, toMs, toLocal, lint, finish
    }
}
