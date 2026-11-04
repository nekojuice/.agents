// Render report.md from result.json. Stored values are English enums; labels come from the round's locale
// (task.locale, from PROJECT.md "Report language"; zh-TW or en, default zh-TW).
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { readManifest } from './manifest.mjs'
import { readSteps, updateResult, verdictOf } from './task.mjs'
import { attribute } from './trace.mjs'
import { sideAndFormal } from './audit.mjs'

const LOCALES = {
    'zh-TW': {
        sep: '、', colon: '：', yes: '是', no: '否', none: '- 無', par: (x) => `（${x}）`,
        verdict: { pass: '通過', fail: '失敗', inconclusive: '無法判定' },
        by: { script: '腳本', value: '比值', visual: '目視', 'not-run': '未執行', 'run-error': '執行失敗' },
        status: { 'product-fail': '產品失敗', 'run-error': 'agent 執行失敗', 'needs-human': '需人工驗', 'verified-with-limits': 'agent 已驗（有前提限制）', verified: 'agent 已驗' },
        kind: { review: '驗收', prep: '資料準備', init: '初始化' },
        via: { web: '畫面', api: 'API', db: 'DB' },
        stepKind: { script: '腳本', agent: 'agent', adhoc: '即興' },
        mode: { dry: '試跑', rehearse: '預演' },
        uiType: { operation: '操作', layout: '排版', wording: '用字', display: '顯示', error: '錯誤' },
        rule: { 'iso-datetime': '時間以原始格式顯示', 'clipped-text': '文字被容器切掉', 'stacked-header': '表頭被擠成三行以上', 'readonly-counter': '唯讀欄位仍顯示字數計數', 'overflow-x': '頁面出現水平捲軸' },
        agentHuman: (id) => `${id}：依 agent 步驟判定，需人工確認`,
        stats: (n, p, f, i) => `共 ${n} 個檢查點：通過 ${p}、失敗 ${f}、無法判定 ${i}`,
        noChecks: (k) => `**結論：本輪為${k}，沒有驗收檢查點。**`,
        passed: (s) => `**結論：通過**　${s}`,
        whyFail: (n) => `${n} 項失敗`, whyPending: (n) => `${n} 項無法判定，需人工驗`,
        notPassed: (v, why) => `**結論：整體不算通過（${v}）**　原因：${why || '尚無檢查點'}。`,
        kindNote: (k) => `本輪類型為${k}，依檢查點判定。`,
        agentChecks: (ids) => `判定依據含 agent 操作步驟的檢查點：${ids}（重現性低於腳本，請覆核證據）。`,
        failedH: ['### 失敗項目', '| 編號 | 檢查 | 差異 |'],
        pendingH: ['### 需人工驗', '| 編號 | 檢查 | 原因與需要的條件 |'], pendingBy: (b) => `判定來源為${b}`,
        limitsH: ['### 通過項目的前提限制', '| 檢查點 | 限制 | 何時補驗 |'],
        itemsH: ['## 清單項目對照', '建議狀態供上級覆核，是否視為完成由上級決定。', '| 項目 | 建議狀態 | 檢查點 | 剩下的人工工作 |'],
        prevH: (p) => ['## 與上一輪比較', `上一輪：${p}`, '| 項目 | 上一輪 | 本輪 | 變化 |'], change: { added: '新增', same: '不變', better: '改善', worse: '退步' },
        task: { h: '## 任務', source: '- 來源：', requester: '- 委派者：', round: (n, k) => `- 輪次：第 ${n} 輪（${k}）`, basis: '- 本輪依據：', parts: '- 情境：' },
        env: { h: '## 環境', head: '| 項目 | 值 |', url: '網址', surface: 'surface', scope: '資料範圍', accounts: '帳號', browser: '瀏覽器', started: '執行時間', versions: '受測版本', skill: (v, p) => `${v}（專案檔驗證版本：${p ?? '未記錄'}）`, skillL: 'skill 版本' },
        checksH: ['## 檢查點', '| 編號 | 檢查 | 預期 | 實際 | 判定 | 來源 | 途徑 | 證據 |'], agentMark: '（agent）', amendedMark: '（已更正）',
        shotsH: '## 截圖',
        uiH: ['## UI 問題（不影響判定）', '| 類別 | 位置 | 現象 | 證據 |'],
        writesH: '## 寫入紀錄', writesNone: '- 無，僅登入紀錄',
        apiWritesH: ['### API 寫入呼叫', '| 時間 | surface | 帳號 | 呼叫 | 狀態 |'],
        traceH: '## 步驟與稽核紀錄', traceSrc: (s, u, w) => `稽核紀錄：${s}，帳號 ${u}，時間窗 ${w}`,
        traceHead: '| 時間 | surface | 類型 | 步驟 | 成功 | 對應的稽核紀錄 |', orphansH: '### 對不到步驟的稽核紀錄',
        ambiguous: '（整秒時間，歸屬不確定）', byExpects: '（依步驟宣告）', nested: '↳ ',
        sideH: '## 試跑與預演期間的稽核紀錄', sideNote: (w) => `不計入判定；時間窗 ${w}`, sideHead: '| 時間 | 模式 | 步驟 | 稽核紀錄 |', unattributed: '對不到步驟', formal: '正式步驟',
        assetsH: ['## .e2e/ 異動', '本輪新增或修改、進版控的 .e2e/ 檔案（與 new 時的狀態比較）。'], assetsNone: '- 無', assetsUnknown: '- 無法比較（沒有 git 基準），由 worker 自行列出',
        keptH: ['## 重跑時保留的舊值檔', '報告以最新的值檔為準；下列為同名重跑前的舊檔。'],
        amendH: ['## 檢查點更正紀錄', '原判定與更正並列，供上級覆核。', '| 時間 | 檢查點 | 原判定 | 更正的欄位 | 更正後 | 原因 | 證據 |'],
        issuesH: '## 阻礙與偏差', obsH: '## 其他觀察', reproH: '## 重現方式'
    },
    en: {
        sep: ', ', colon: ': ', yes: 'yes', no: 'no', none: '- none', par: (x) => ` (${x})`,
        verdict: { pass: 'pass', fail: 'fail', inconclusive: 'inconclusive' },
        by: { script: 'script', value: 'value', visual: 'visual', 'not-run': 'not run', 'run-error': 'run error' },
        status: { 'product-fail': 'product failure', 'run-error': 'agent run error', 'needs-human': 'needs human check', 'verified-with-limits': 'agent verified (with limits)', verified: 'agent verified' },
        kind: { review: 'review', prep: 'data preparation', init: 'initialization' },
        via: { web: 'screen', api: 'API', db: 'DB' },
        stepKind: { script: 'script', agent: 'agent', adhoc: 'ad-hoc' },
        mode: { dry: 'dry run', rehearse: 'rehearsal' },
        uiType: { operation: 'operation', layout: 'layout', wording: 'wording', display: 'display', error: 'error' },
        rule: { 'iso-datetime': 'timestamp shown in raw format', 'clipped-text': 'text clipped by its container', 'stacked-header': 'header squeezed into three or more lines', 'readonly-counter': 'read-only field shows a character counter', 'overflow-x': 'horizontal page scrollbar' },
        agentHuman: (id) => `${id}: judged on an agent step, needs human confirmation`,
        stats: (n, p, f, i) => `${n} checks: ${p} passed, ${f} failed, ${i} inconclusive`,
        noChecks: (k) => `**Conclusion: this was a ${k} round with no acceptance checks.**`,
        passed: (s) => `**Conclusion: pass**  ${s}`,
        whyFail: (n) => `${n} failed`, whyPending: (n) => `${n} inconclusive, need human verification`,
        notPassed: (v, why) => `**Conclusion: not passed overall (${v})**  Reason: ${why || 'no checks yet'}.`,
        kindNote: (k) => `Round kind: ${k}; judged by its checks.`,
        agentChecks: (ids) => `Checks judged on agent-operated steps: ${ids} (less reproducible than scripts; review the evidence).`,
        failedH: ['### Failed checks', '| ID | Check | Difference |'],
        pendingH: ['### Needs human verification', '| ID | Check | Reason and condition needed |'], pendingBy: (b) => `source: ${b}`,
        limitsH: ['### Limits on passed checks', '| Check | Limit | When to re-verify |'],
        itemsH: ['## Checklist items', 'Suggested statuses for the superior to review; the superior decides what counts as done.', '| Item | Suggested status | Checks | Remaining human work |'],
        prevH: (p) => ['## Compared with the previous round', `Previous round: ${p}`, '| Item | Previous | Now | Change |'], change: { added: 'new', same: 'unchanged', better: 'improved', worse: 'regressed' },
        task: { h: '## Task', source: '- Source: ', requester: '- Requester: ', round: (n, k) => `- Round: ${n} (${k})`, basis: '- Round basis: ', parts: '- Scenarios: ' },
        env: { h: '## Environment', head: '| Item | Value |', url: 'URL', surface: 'surface', scope: 'Data scope', accounts: 'Accounts', browser: 'Browser', started: 'Started', versions: 'Tested versions', skill: (v, p) => `${v} (PROJECT.md verified with: ${p ?? 'not recorded'})`, skillL: 'Skill version' },
        checksH: ['## Checks', '| ID | Check | Expected | Actual | Verdict | Source | Route | Evidence |'], agentMark: ' (agent)', amendedMark: ' (amended)',
        shotsH: '## Screenshots',
        uiH: ['## UI findings (do not affect verdicts)', '| Type | Where | What | Evidence |'],
        writesH: '## Writes', writesNone: '- none, login entries only',
        apiWritesH: ['### API write calls', '| Time | surface | Account | Call | Status |'],
        traceH: '## Steps and audit trail', traceSrc: (s, u, w) => `Audit source: ${s}; users ${u}; window ${w}`,
        traceHead: '| Time | surface | Kind | Step | OK | Audit rows |', orphansH: '### Audit rows without a step',
        ambiguous: ' (whole-second time, attribution uncertain)', byExpects: ' (by step declaration)', nested: '↳ ',
        sideH: '## Audit rows during dry runs and rehearsals', sideNote: (w) => `Not part of the verdict; window ${w}`, sideHead: '| Time | Mode | Step | Audit row |', unattributed: 'no step', formal: 'formal step',
        assetsH: ['## .e2e/ changes', 'Versioned .e2e/ files added or changed in this round (compared with the state at new).'], assetsNone: '- none', assetsUnknown: '- cannot compare (no git baseline); the worker lists them',
        keptH: ['## Value files kept from reruns', 'The report uses the latest value file; these are the older files of the same name.'],
        amendH: ['## Check amendments', 'The original judgment beside the correction, for the superior to review.', '| Time | Check | Original | Fields before | After | Reason | Evidence |'],
        issuesH: '## Issues', obsH: '## Observations', reproH: '## Reproduce'
    }
}
const RANK = { verified: 4, 'verified-with-limits': 3, 'needs-human': 2, 'run-error': 1, 'product-fail': 0 }

// Suggested status of a checklist item, derived from its checks (rules in references/report-spec.md).
export function itemStatus(r, it) {
    const ids = Array.isArray(it.checks) ? it.checks : []
    const cs = r.checks.filter((c) => ids.includes(c.id))
    if (!cs.length) return 'needs-human'
    if (cs.some((c) => c.verdict === 'fail')) return 'product-fail'
    if (cs.some((c) => c.verdict === 'inconclusive' && c.by === 'run-error')) return 'run-error'
    if (cs.some((c) => c.verdict === 'inconclusive')) return 'needs-human'
    // Recipes are not yet an acceptance basis: a pass that rests on an agent step still needs a person.
    if (cs.some((c) => c.agent)) return 'needs-human'
    if ((r.limits ?? []).some((l) => ids.includes(l?.check))) return 'verified-with-limits'
    return 'verified'
}

// Values of any shape render readably: objects and objects inside arrays as compact JSON, long JSON shortened.
const MAX_JSON = 300
const json = (v) => { const s = JSON.stringify(v); return s.length > MAX_JSON ? `${s.slice(0, MAX_JSON)}…` : s }
const textOf = (e) => (e && typeof e === 'object' && 'text' in e ? e.text : e)

export function renderReport(dir) {
    const r = refreshVerdict(dir, JSON.parse(readFileSync(join(dir, 'result.json'), 'utf8')))
    const L = LOCALES[r.task?.locale] ?? LOCALES['zh-TW']
    const fmt = (v) => (Array.isArray(v) ? v.map((x) => (x && typeof x === 'object' ? json(x) : String(x))).join(L.sep) : v == null ? '' : typeof v === 'object' ? json(v) : String(v))
    const cell = (v) => fmt(v).replace(/\|/g, '\\|').replace(/\n/g, '<br>')
    const link = (ps) => (Array.isArray(ps) ? ps : ps ? [ps] : []).map((p) => `[${p}](${p})`).join('<br>')
    const count = (v) => r.checks.filter((c) => c.verdict === v).length
    const failed = r.checks.filter((c) => c.verdict === 'fail')
    const pending = r.checks.filter((c) => c.verdict === 'inconclusive')
    const kind = r.task.kind ?? 'review'
    const kindL = L.kind[kind] ?? kind
    const stats = L.stats(r.checks.length, count('pass'), count('fail'), count('inconclusive'))
    // An item title that repeats its id (e.g. "12 …", "12. …") is shown once.
    const itemLabel = (it) => {
        const id = String(it.id ?? '')
        const esc = id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        const title = String(it.title ?? '').replace(new RegExp(`^\\s*${esc}(?=[\\s.:：、)）-])[\\s.:：、)）-]*`), '')
        return `${id} ${title}`.trim()
    }
    const lines = [`# ${r.task.title}`, '']

    if (kind !== 'review' && !r.checks.length) lines.push(L.noChecks(kindL), '', ...(r.summary ? [r.summary, ''] : []))
    else {
        if (r.verdict === 'pass') lines.push(L.passed(r.summary ?? ''), '', stats, '')
        else {
            const why = [failed.length && L.whyFail(failed.length), pending.length && L.whyPending(pending.length)].filter(Boolean).join(L.sep)
            lines.push(L.notPassed(L.verdict[r.verdict] ?? r.verdict, why), '', ...(r.summary ? [r.summary, ''] : []), stats, '')
        }
        if (kind !== 'review') lines.push(L.kindNote(kindL), '')
    }
    const agentChecks = r.checks.filter((c) => c.agent)
    if (agentChecks.length) lines.push(L.agentChecks(agentChecks.map((c) => c.id).join(L.sep)), '')
    if (failed.length) lines.push(L.failedH[0], '', L.failedH[1], '| --- | --- | --- |', ...failed.map((c) => `| ${c.id} | ${cell(c.title)} | ${cell(c.actual)} |`), '')
    if (pending.length) lines.push(L.pendingH[0], '', L.pendingH[1], '| --- | --- | --- |', ...pending.map((c) => `| ${c.id} | ${cell(c.title)} | ${cell(c.note || L.pendingBy(L.by[c.by] ?? c.by))} |`), '')
    if (r.limits?.length) {
        const row = (l) => (l && typeof l === 'object' ? `| ${cell(l.check)} | ${cell(l.limit)} | ${cell(l.retest)} |` : `| — | ${cell(l)} | — |`)
        lines.push(L.limitsH[0], '', L.limitsH[1], '| --- | --- | --- |', ...r.limits.map(row), '')
    }
    const humanWork = (it) => {
        const ids = Array.isArray(it.checks) ? it.checks : []
        const parts = it.humanWork ? [it.humanWork] : []
        for (const c of r.checks.filter((x) => ids.includes(x.id) && x.verdict !== 'pass')) parts.push(`${c.id}${L.colon}${c.note || c.title}`)
        for (const c of r.checks.filter((x) => ids.includes(x.id) && x.verdict === 'pass' && x.agent)) parts.push(L.agentHuman(c.id))
        for (const l of (r.limits ?? []).filter((x) => ids.includes(x?.check))) parts.push(`${l.check}${L.colon}${l.retest}`)
        return parts.join('\n') || '—'
    }
    if (r.items?.length) {
        lines.push(L.itemsH[0], '', L.itemsH[1], '', L.itemsH[2], '| --- | --- | --- | --- |')
        for (const it of r.items) lines.push(`| ${cell(itemLabel(it))} | ${L.status[itemStatus(r, it)]} | ${cell(it.checks)} | ${cell(humanWork(it))} |`)
        lines.push('')
    }
    if (r.previousReport && existsSync(join(r.previousReport, 'result.json'))) {
        const prev = JSON.parse(readFileSync(join(r.previousReport, 'result.json'), 'utf8'))
        const [h, p, head] = L.prevH(r.previousReport)
        lines.push(h, '', p, '', head, '| --- | --- | --- | --- |')
        for (const it of r.items ?? []) {
            const old = (prev.items ?? []).find((x) => x.id === it.id)
            const before = old ? itemStatus(prev, old) : null
            const now = itemStatus(r, it)
            const change = !old ? L.change.added : before === now ? L.change.same : RANK[now] > RANK[before] ? L.change.better : L.change.worse
            lines.push(`| ${cell(itemLabel(it))} | ${before ? L.status[before] : '—'} | ${L.status[now]} | ${change} |`)
        }
        lines.push('')
    }

    const steps = readSteps(dir)
    const src = String(r.task.source ?? '').split('\n').filter(Boolean)
    const parts = Object.entries(r.parts ?? {})
    lines.push(L.task.h, '', ...(src.length > 1 ? [L.task.source, ...src.map((s) => `  - ${s}`)] : [`${L.task.source}${src[0] ?? ''}`]),
        `${L.task.requester}${r.task.requester ?? ''}`, L.task.round(r.round ?? 1, kindL), ...(r.basis ? [`${L.task.basis}${r.basis}`] : []),
        ...(parts.length > 1 ? [`${L.task.parts}${parts.map(([k, p]) => `${k}${L.par(L.verdict[p.verdict] ?? p.verdict ?? '—')}`).join(L.sep)}`] : []),
        '')
    const e = r.env ?? {}
    // Accounts come from every step, so reruns and steps run outside scenarios all count.
    const accounts = [...new Set([...(e.accounts ?? []), ...steps.flatMap((s) => [s.args?.account, ...(s.accountsUsed ?? [])]).filter(Boolean), ...exchangeAccounts(dir)])]
    const versions = Object.entries(e.versions ?? {}).map(([k, v]) => `${k} ${v ?? '-'}`).join('／')
    lines.push(L.env.h, '', L.env.head, '| --- | --- |', `| ${L.env.url} | ${e.url ?? ''} |`, ...Object.entries(e.surfaces ?? {}).map(([k, v]) => `| ${L.env.surface} ${k} | ${v.driver}　${v.baseUrl} |`), `| ${L.env.scope} | ${e.dataScope ?? ''} |`, `| ${L.env.accounts} | ${cell(accounts)} |`,
        `| ${L.env.browser} | ${e.browser ?? ''} |`, `| ${L.env.started} | ${e.startedAt ?? ''} |`, `| ${L.env.versions} | ${versions || '—'} |`,
        `| ${L.env.skillL} | ${L.env.skill(e.skillVersion, e.projectVerifiedSkillVersion)} |`, '')

    lines.push(L.checksH[0], '', L.checksH[1], '| --- | --- | --- | --- | --- | --- | --- | --- |')
    for (const c of r.checks) lines.push(`| ${c.id} | ${cell(c.title)} | ${cell(c.expected)} | ${cell(c.actual)} | ${L.verdict[c.verdict] ?? c.verdict}${c.amended ? L.amendedMark : ''} | ${L.by[c.by] ?? c.by}${c.agent ? L.agentMark : ''} | ${c.via ? (L.via[c.via] ?? c.via) : '—'} | ${link(c.evidence)} |`)
    lines.push('')
    const shots = [...new Set(r.checks.flatMap((c) => (Array.isArray(c.evidence) ? c.evidence : [])).filter((p) => /\.(png|jpe?g)$/i.test(p)))]
    if (!shots.includes('shots/final.png') && existsSync(join(dir, 'shots/final.png'))) shots.push('shots/final.png')
    if (shots.length) lines.push(L.shotsH, '', ...shots.flatMap((p) => [`### ${p}`, '', `![${p}](${p})`, '']))

    lines.push(L.uiH[0], '')
    if (r.uiFindings?.length) {
        lines.push(L.uiH[1], '| --- | --- | --- | --- |')
        const what = (f) => `${L.rule[f.rule] ?? f.what ?? ''}${f.samples?.length ? `${L.colon}${fmt(f.samples)}` : ''}`
        for (const f of r.uiFindings) lines.push(`| ${L.uiType[f.type] ?? f.type} | ${cell(f.where)} | ${cell(what(f))} | ${link(f.evidence)} |`)
        lines.push('')
    } else lines.push(L.none, '')

    const writeLine = (w) => (w && typeof w === 'object' && w.what ? `- ${w.at ? `${String(w.at).slice(11, 19)}　` : ''}${w.what}${L.par(`${w.where ?? '—'}${L.sep}${w.how ?? '—'}`)}` : `- ${fmt(w)}`)
    lines.push(L.writesH, '', ...(r.writes?.length ? r.writes.map(writeLine) : [L.writesNone]), '')
    const apiWrites = readManifest(dir).events.filter((m) => m.auto)
    if (apiWrites.length) lines.push(L.apiWritesH[0], '', L.apiWritesH[1], '| --- | --- | --- | --- | --- |',
        ...apiWrites.map((m) => `| ${String(m.at).slice(11, 19)} | ${m.surface} | ${m.account ?? '—'} | ${cell(`${m.method} ${m.path}`)} | ${m.status} |`), '')
    if (r.assetsChanged !== undefined) lines.push(L.assetsH[0], '', L.assetsH[1], '', ...(r.assetsChanged === null ? [L.assetsUnknown] : r.assetsChanged.length ? r.assetsChanged.map((p) => `- \`${p}\``) : [L.assetsNone]), '')
    lines.push(...traceLines(dir, steps, cell, L))
    lines.push(...sideLines(dir, cell, L))
    lines.push(...keptLines(dir, L))
    const orig = (o) => (o ? `${L.verdict[o.verdict] ?? o.verdict}${L.par(`${L.by[o.by] ?? o.by}${o.actual != null && o.actual !== '' ? `${L.sep}${fmt(o.actual)}` : ''}`)}` : '—')
    if (r.amendments?.length) lines.push(L.amendH[0], '', L.amendH[1], '', L.amendH[2], '| --- | --- | --- | --- | --- | --- | --- |',
        ...r.amendments.map((a) => `| ${String(a.at).slice(0, 19)} | ${a.check} | ${cell(orig(a.original))} | ${cell(a.before)} | ${cell(a.after)} | ${cell(a.reason)} | ${link(a.evidence)} |`), '')
    lines.push(L.issuesH, '', ...(r.issues?.length ? r.issues.map((s) => `- ${fmt(textOf(s))}`) : [L.none]), '')
    if (r.observations?.length) lines.push(L.obsH, '', ...r.observations.map((s) => `- ${fmt(textOf(s))}`), '')
    lines.push(L.reproH, '', '```bash', ...(r.reproduce ?? []), '```', '')
    writeFileSync(join(dir, 'report.md'), lines.join('\n'))
    return join(dir, 'report.md')
}

const fmtRow = (x) => [String(x.time).slice(11, 19), x.user, x.action, x.target, x.detail, x.source].filter(Boolean).join(' ')
const argText = (a) => Object.entries(a ?? {}).filter(([k]) => k !== 'save').map(([k, v]) => `${k}=${v && typeof v === 'object' ? json(v) : v}`).join(' ')
const stepText = (st) => (st.kind === 'agent' ? [st.script, st.note, (st.evidence ?? []).join(' ')].filter(Boolean).join(' ') : `${st.script} ${argText(st.args)}`.trim())

// Step timeline with the audit rows each step produced (attribution rules in core/trace.mjs).
// Script steps that ran while an agent step was open are shown nested under it.
function traceLines(dir, steps, cell, L) {
    if (!steps.length) return []
    const auditPath = join(dir, 'values', 'audit.json')
    const audit = existsSync(auditPath) ? JSON.parse(readFileSync(auditPath, 'utf8')) : null
    const rows = audit?.rows ?? []
    const owner = attribute(steps, rows)
    const out = [L.traceH, '']
    if (audit) out.push(L.traceSrc(audit.source, (audit.users ?? []).join(L.sep), (audit.window ?? []).join(' ～ ')), '')
    out.push(L.traceHead, '| --- | --- | --- | --- | --- | --- |')
    const agents = steps.filter((s) => s.kind === 'agent')
    steps.forEach((st, k) => {
        const hits = rows.map((x, i) => [x, owner[i]]).filter(([, o]) => o.step === k)
            .map(([x, o]) => fmtRow(x) + (o.how === 'ambiguous' ? L.ambiguous : o.how === 'expects' ? L.byExpects : ''))
        const nested = st.kind !== 'agent' && agents.some((a) => a.startedAt <= st.startedAt && st.startedAt <= a.endedAt)
        out.push(`| ${String(st.startedAt).slice(11, 19)}–${String(st.endedAt).slice(11, 19)} | ${st.surface ?? '—'} | ${L.stepKind[st.kind] ?? st.kind ?? '—'} | ${nested ? L.nested : ''}${cell(stepText(st))} | ${st.ok ? L.yes : L.no} | ${hits.join('<br>')} |`)
    })
    out.push('')
    if (audit) {
        const orphans = rows.filter((_, i) => owner[i].step < 0)
        out.push(L.orphansH, '', ...(orphans.length ? orphans.map((x) => `- ${fmtRow(x)}`) : [L.none]), '')
    }
    return out
}

// Audit rows in the dry-run and rehearsal window (values/audit-side.json); listed, never judged. Rows with no step
// (e.g. an unlogged operation, another person on the same account) and uncertain ones are marked, never dropped.
function sideLines(dir, cell, L) {
    const p = join(dir, 'values', 'audit-side.json')
    if (!existsSync(p)) return []
    const audit = JSON.parse(readFileSync(p, 'utf8'))
    // Same timeline as the audit filter: formal and side steps together, so the marks match what was kept.
    const steps = sideAndFormal(dir)
    const owner = attribute(steps, audit.rows ?? [])
    const out = [L.sideH, '', L.sideNote((audit.window ?? []).join(' ～ ')), '', L.sideHead, '| --- | --- | --- | --- |']
    ;(audit.rows ?? []).forEach((x, i) => {
        const st = owner[i].step >= 0 ? steps[owner[i].step] : null
        const mode = !st ? L.unattributed : st.side ? (L.mode[st.mode] ?? st.mode) : L.formal
        out.push(`| ${String(x.time).slice(11, 19)} | ${mode} | ${st ? cell(stepText(st)) : '—'} | ${cell(fmtRow(x))}${owner[i].how === 'ambiguous' ? L.ambiguous : ''} |`)
    })
    if (!(audit.rows ?? []).length) out.push('| — | — | — | — |')
    out.push('')
    return out
}

// values/<name>.<n>.json files: older value files kept when a step was rerun with the same save name.
function keptLines(dir, L) {
    const vd = join(dir, 'values')
    if (!existsSync(vd)) return []
    // Only <name>.<n>.json beside an existing <name>.json is a kept file; a save name that itself ends in .<digits> is not.
    const files = new Set(readdirSync(vd))
    const kept = [...files].filter((f) => { const m = f.match(/^(.+)\.\d+\.json$/); return m && files.has(`${m[1]}.json`) }).sort()
    return kept.length ? [L.keptH[0], '', L.keptH[1], '', ...kept.map((f) => `- [values/${f}](values/${f})`), ''] : []
}

// The overall verdict always follows the recorded checks, however they were added (scenario, add, recipe work, amend).
function refreshVerdict(dir, r) {
    r.checks ??= []
    const v = verdictOf(r.checks)
    return v ? updateResult(dir, (x) => { x.checks ??= []; Object.assign(x, v) }) : r
}

// Account keys found in the round's API exchanges (including logins and clients switched with api.as).
function exchangeAccounts(dir) {
    const ex = join(dir, 'exchanges')
    if (!existsSync(ex)) return []
    return readdirSync(ex).filter((f) => f.endsWith('.json')).map((f) => { try { return JSON.parse(readFileSync(join(ex, f), 'utf8')).account } catch { return null } }).filter(Boolean)
}
