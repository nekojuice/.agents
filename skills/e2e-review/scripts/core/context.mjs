// Scenario context: what a solidified scenario receives. Scenarios are `export default async (ctx, opts) => {}` and import nothing from the skill.
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { readSteps } from './task.mjs'

export function toMs(s) {
    const m = String(s).match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})[ T](\d{1,2}):(\d{2}):(\d{2})(?:\.(\d+))?/)
    if (!m) return NaN
    const [, y, mo, d, h, mi, se, f = '0'] = m
    return new Date(+y, +mo - 1, +d, +h, +mi, +se, +f.padEnd(3, '0').slice(0, 3)).getTime()
}

// runStep(script, args) runs a fragment through the driver and returns { ok, value, error }.
export function createContext({ dir, project, loaded, runStep }) {
    const resultPath = join(dir, 'result.json')
    const result = JSON.parse(readFileSync(resultPath, 'utf8'))
    // Checks, items, limits and issues describe this execution; writes accumulate because data writes survive reruns.
    Object.assign(result, { checks: [], items: [], limits: [], issues: [], writes: result.writes ?? [], uiFindings: (result.uiFindings ?? []).filter((f) => !f.auto) })
    const save = () => writeFileSync(resultPath, JSON.stringify(result, null, 2))
    const failedSteps = []
    let lintCount = 0

    async function run(script, args = {}, saveAs) {
        const res = await runStep(script, { ...args, ...(saveAs ? { save: saveAs } : {}) })
        if (!res.ok) {
            failedSteps.push(script)
            result.issues.push(`${script} failed: ${res.error}`)
            save()
        }
        return res
    }

    // pass: true → pass, false → fail, null → inconclusive. Inconclusive checks after a failed step are attributed to run-error.
    function check(id, title, expected, actual, pass, evidence = [], note = '') {
        const verdict = pass === null ? 'inconclusive' : pass ? 'pass' : 'fail'
        const by = pass === null && failedSteps.length ? 'run-error' : 'script'
        const why = by === 'run-error' && !note ? `failed steps: ${[...new Set(failedSteps)].join(', ')}` : note
        result.checks.push({ id, title, expected, actual, verdict, by, evidence, note: why })
        save()
    }

    // Checks the worker cannot run here (environment missing, human-only) or can only judge visually.
    function manual(id, title, expected, by, note, evidence = []) {
        result.checks.push({ id, title, expected, actual: by === 'not-run' ? 'not run' : '', verdict: 'inconclusive', by, evidence, note })
        save()
    }

    function addWrite(w) {
        if (!result.writes.some((x) => x.what === w.what && x.at === w.at)) result.writes.push(w)
        save()
    }

    const valueFile = (name) => {
        const p = join(dir, 'values', `${name}.json`)
        return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : null
    }
    const writeValue = (name, v) => writeFileSync(join(dir, 'values', `${name}.json`), JSON.stringify(v, null, 2))
    const lastStep = () => readSteps(dir).at(-1)
    const inStep = (t, st, before = 1000, after = 2000) => toMs(t) >= toMs(st.startedAt) - before && toMs(t) <= toMs(st.endedAt) + after

    // Run the generic UI lint probe on the current screen and record findings as auto UI findings.
    async function lint(where, { scope, shot } = {}) {
        // Numbered so non-ASCII locations never collapse into the same file name
        lintCount += 1
        const slug = String(shot ?? where).replace(/[^\w-]+/g, '-').replace(/^-+|-+$/g, '')
        const name = `lint-${String(lintCount).padStart(2, '0')}${slug ? `-${slug}` : ''}`
        const res = await run('probes/ui-lint', { ...(scope ? { scope } : {}), ...(shot ? { shot } : {}) }, name)
        for (const f of res.value?.findings ?? [])
            result.uiFindings.push({ auto: true, type: f.type, rule: f.rule, where, what: f.what, samples: f.samples, evidence: [`values/${name}.json`, ...(res.value.shot ? [res.value.shot] : [])] })
        save()
        return res.value?.findings ?? []
    }

    function finish(summary) {
        const failed = result.checks.filter((c) => c.verdict === 'fail').length
        const unknown = result.checks.filter((c) => c.verdict === 'inconclusive').length
        result.verdict = failed ? 'fail' : unknown ? 'inconclusive' : 'pass'
        result.summary = `${summary} ${result.checks.length} checks: ${failed} failed, ${unknown} inconclusive.`.trim()
        save()
        return { verdict: result.verdict, summary: result.summary }
    }

    return { dir, project, env: loaded.env, config: loaded.config, accounts: Object.keys(loaded.accounts), result, save, run, check, manual, addWrite, valueFile, writeValue, lastStep, inStep, toMs, lint, finish }
}
