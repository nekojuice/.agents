// Audit row attribution, shared by the report and scenarios. Rules: references/report-spec.md "Write traceability".
export const AFTER_MS = 1500

export function toMs(s) {
    const m = String(s).match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})[ T](\d{1,2}):(\d{2}):(\d{2})(?:\.(\d+))?/)
    if (!m) return NaN
    const [, y, mo, d, h, mi, se, f = '0'] = m
    return new Date(+y, +mo - 1, +d, +h, +mi, +se, +f.padEnd(3, '0').slice(0, 3)).getTime()
}

// A time without a fraction, or with an all-zero fraction, was cut to whole seconds by its source.
export const wholeSecond = (s) => !/\.\d*[1-9]/.test(String(s))

// A step's expects: [{ object, action, ... }]; every key given must match the row field (object ↔ target) exactly,
// or match its first word, so an action code matches "<code> <label>" but not a longer code that starts with the same digits.
function declared(step, row) {
    return (step.expects ?? []).some((e) => e && typeof e === 'object' && Object.entries(e).every(([k, v]) => {
        const field = k === 'object' ? row.target : row[k]
        if (field == null) return false
        const f = String(field).trim()
        const want = String(v).trim()
        return f === want || f.split(/\s+/)[0] === want
    }))
}

// Returns, per row, { step: index or -1, how: 'expects' | 'time' | 'ambiguous' | null }.
// 1. A step whose expects match the row and whose window covers it wins (the latest such step).
// 2. Precise times: the last step started at or before the row, if the row is within AFTER_MS of its end;
//    otherwise an agent step still open at that time (its own operation, after script steps nested in it ended).
// 3. Whole-second times: the one step active in that second (script steps before agent steps); several → ambiguous.
export function attribute(steps, rows) {
    const win = steps.map((st) => [toMs(st.startedAt), toMs(st.endedAt)])
    return rows.map((row) => {
        const t = toMs(row.time)
        const coarse = wholeSecond(row.time)
        const hi = coarse ? t + 999 : t
        const covers = (i) => win[i][0] <= hi && win[i][1] + AFTER_MS >= t
        const byDecl = steps.map((_, i) => i).filter((i) => covers(i) && declared(steps[i], row))
        if (byDecl.length) return { step: byDecl.at(-1), how: 'expects' }
        if (coarse) {
            const active = steps.map((_, i) => i).filter((i) => win[i][0] <= hi && win[i][1] >= t)
            const pool = active.filter((i) => steps[i].kind !== 'agent')
            const use = pool.length ? pool : active
            if (use.length === 1) return { step: use[0], how: 'time' }
            if (use.length > 1) return { step: use[0], how: 'ambiguous' }
        }
        let k = -1
        win.forEach(([s], i) => { if (s <= hi) k = i })
        if (k >= 0 && t <= win[k][1] + AFTER_MS) return { step: k, how: 'time' }
        let open = -1
        win.forEach(([s, e], i) => { if (steps[i].kind === 'agent' && s <= t && t <= e + AFTER_MS) open = i })
        return open >= 0 ? { step: open, how: 'time' } : { step: -1, how: null }
    })
}

// The step a single timestamp (and optional row fields for expects) belongs to, or null.
export function ownerOf(steps, t, row = {}) {
    const [a] = attribute(steps, [{ ...row, time: t }])
    return a.step >= 0 ? steps[a.step] : null
}
