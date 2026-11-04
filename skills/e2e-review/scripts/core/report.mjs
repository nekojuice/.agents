// Render report.md from result.json. Stored values are English enums; labels are localized here (zh-TW for now).
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { readManifest } from './manifest.mjs'
import { readSteps } from './task.mjs'

const L = {
    verdict: { pass: '通過', fail: '失敗', inconclusive: '無法判定' },
    by: { script: '腳本', value: '比值', visual: '目視', 'not-run': '未執行', 'run-error': '執行失敗' },
    status: {
        'product-fail': '產品失敗',
        'run-error': 'agent 執行失敗',
        'needs-human': '需人工驗',
        'verified-with-limits': 'agent 已驗（有前提限制）',
        verified: 'agent 已驗'
    },
    kind: { review: '驗收', prep: '資料準備', init: '初始化' },
    via: { web: '畫面', api: 'API', db: 'DB' },
    stepKind: { script: '腳本', agent: 'agent', adhoc: '即興' },
    uiType: { operation: '操作', layout: '排版', wording: '用字', display: '顯示', error: '錯誤' },
    rule: {
        'iso-datetime': '時間以原始格式顯示',
        'clipped-text': '文字被容器切掉',
        'stacked-header': '表頭被擠成三行以上',
        'readonly-counter': '唯讀欄位仍顯示字數計數',
        'overflow-x': '頁面出現水平捲軸'
    }
}
const RANK = { verified: 4, 'verified-with-limits': 3, 'needs-human': 2, 'run-error': 1, 'product-fail': 0 }

// Suggested status of a checklist item, derived from its checks (rules in references/report-spec.md).
export function itemStatus(r, it) {
    const cs = r.checks.filter((c) => it.checks.includes(c.id))
    if (!cs.length) return 'needs-human'
    if (cs.some((c) => c.verdict === 'fail')) return 'product-fail'
    if (cs.some((c) => c.verdict === 'inconclusive' && c.by === 'run-error')) return 'run-error'
    if (cs.some((c) => c.verdict === 'inconclusive')) return 'needs-human'
    // Recipes are not yet an acceptance basis: a pass that rests on an agent step still needs a person.
    if (cs.some((c) => c.agent)) return 'needs-human'
    if ((r.limits ?? []).some((l) => it.checks.includes(l.check))) return 'verified-with-limits'
    return 'verified'
}

function humanWork(r, it) {
    const parts = it.humanWork ? [it.humanWork] : []
    for (const c of r.checks.filter((x) => it.checks.includes(x.id) && x.verdict !== 'pass')) parts.push(`${c.id}：${c.note || c.title}`)
    for (const c of r.checks.filter((x) => it.checks.includes(x.id) && x.verdict === 'pass' && x.agent)) parts.push(`${c.id}：依 agent 步驟判定，需人工確認`)
    for (const l of (r.limits ?? []).filter((x) => it.checks.includes(x.check))) parts.push(`${l.check}：${l.retest}`)
    return parts.join('\n') || '—'
}

const ms = (s) => Date.parse(s.length > 19 ? s : `${s}.000`)

// Attribute each audit row to the last step that started before it; rows more than 1.5 s after that step ended are unattributed.
function traceLines(dir, cell) {
    const steps = readSteps(dir)
    if (!steps.length) return []
    const auditPath = join(dir, 'values', 'audit.json')
    const audit = existsSync(auditPath) ? JSON.parse(readFileSync(auditPath, 'utf8')) : null
    const rows = audit?.rows ?? []
    const owner = rows.map((x) => {
        const t = ms(x.time)
        let k = -1
        steps.forEach((st, i) => { if (ms(st.startedAt) - 300 <= t) k = i })
        return k >= 0 && t <= ms(steps[k].endedAt) + 1500 ? k : -1
    })
    const fmtRow = (x) => [x.time.slice(11, 19), x.user, x.action, x.target, x.detail, x.source].filter(Boolean).join(' ')
    const argText = (a) => Object.entries(a ?? {}).filter(([k]) => k !== 'save').map(([k, v]) => `${k}=${v}`).join(' ')
    const out = ['## 步驟與稽核紀錄', '']
    if (audit) out.push(`稽核紀錄：${audit.source}，帳號 ${audit.users.join('、')}，時間窗 ${audit.window.join(' ～ ')}`, '')
    out.push('| 時間 | surface | 類型 | 步驟 | 成功 | 對應的稽核紀錄 |', '| --- | --- | --- | --- | --- | --- |')
    steps.forEach((st, k) => {
        const hits = rows.filter((_, i) => owner[i] === k).map(fmtRow)
        const what = st.kind === 'agent' ? [st.script, st.note, (st.evidence ?? []).join('、')].filter(Boolean).join(' ') : `${st.script} ${argText(st.args)}`
        out.push(`| ${st.startedAt.slice(11, 19)}–${st.endedAt.slice(11, 19)} | ${st.surface ?? '—'} | ${L.stepKind[st.kind] ?? st.kind ?? '—'} | ${cell(what)} | ${st.ok ? '是' : '否'} | ${hits.join('<br>')} |`)
    })
    out.push('')
    if (audit) {
        const orphans = rows.filter((_, i) => owner[i] < 0)
        out.push('### 對不到步驟的稽核紀錄', '', ...(orphans.length ? orphans.map((x) => `- ${fmtRow(x)}`) : ['- 無']), '')
    }
    return out
}

// The overall verdict always follows the recorded checks, however they were added (scenario, add, recipe work).
function refreshVerdict(dir, r) {
    if (!r.checks?.length) return r
    const failed = r.checks.filter((c) => c.verdict === 'fail').length
    const unknown = r.checks.filter((c) => c.verdict === 'inconclusive').length
    r.verdict = failed ? 'fail' : unknown ? 'inconclusive' : 'pass'
    r.stats = { checks: r.checks.length, failed, inconclusive: unknown }
    writeFileSync(join(dir, 'result.json'), JSON.stringify(r, null, 2))
    return r
}

export function renderReport(dir) {
    const r = refreshVerdict(dir, JSON.parse(readFileSync(join(dir, 'result.json'), 'utf8')))
    const fmt = (v) => (Array.isArray(v) ? v.join('、') : v == null ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v))
    const cell = (v) => fmt(v).replace(/\|/g, '\\|').replace(/\n/g, '<br>')
    const count = (v) => r.checks.filter((c) => c.verdict === v).length
    const failed = r.checks.filter((c) => c.verdict === 'fail')
    const pending = r.checks.filter((c) => c.verdict === 'inconclusive')
    const lines = [`# ${r.task.title}`, '']
    const kind = r.task.kind ?? 'review'
    const stats = `共 ${r.checks.length} 個檢查點：通過 ${count('pass')}、失敗 ${count('fail')}、無法判定 ${count('inconclusive')}`

    if (kind !== 'review' && !r.checks.length) lines.push(`**結論：本輪為${L.kind[kind]}，沒有驗收檢查點。**`, '', ...(r.summary ? [r.summary, ''] : []))
    else if (r.verdict === 'pass') lines.push(`**結論：通過**　${r.summary}`, '', stats, '')
    else {
        const why = [failed.length && `${failed.length} 項失敗`, pending.length && `${pending.length} 項無法判定，需人工驗`].filter(Boolean).join('、')
        lines.push(`**結論：整體不算通過（${L.verdict[r.verdict]}）**　原因：${why || '尚無檢查點'}。`, '', ...(r.summary ? [r.summary, ''] : []), stats, '')
    }
    const agentChecks = r.checks.filter((c) => c.agent)
    if (agentChecks.length) lines.push(`判定依據含 agent 操作步驟的檢查點：${agentChecks.map((c) => c.id).join('、')}（重現性低於腳本，請覆核證據）。`, '')
    if (failed.length) {
        lines.push('### 失敗項目', '', '| 編號 | 檢查 | 差異 |', '| --- | --- | --- |', ...failed.map((c) => `| ${c.id} | ${cell(c.title)} | ${cell(c.actual)} |`), '')
    }
    if (pending.length) {
        lines.push('### 需人工驗', '', '| 編號 | 檢查 | 原因與需要的條件 |', '| --- | --- | --- |',
            ...pending.map((c) => `| ${c.id} | ${cell(c.title)} | ${cell(c.note || `判定來源為${L.by[c.by] ?? c.by}`)} |`), '')
    }
    if (r.limits?.length) {
        lines.push('### 通過項目的前提限制', '', '| 檢查點 | 限制 | 何時補驗 |', '| --- | --- | --- |', ...r.limits.map((l) => `| ${cell(l.check)} | ${cell(l.limit)} | ${cell(l.retest)} |`), '')
    }
    if (r.items?.length) {
        lines.push('## 清單項目對照', '', '建議狀態供上級覆核，是否視為完成由上級決定。', '', '| 項目 | 建議狀態 | 檢查點 | 剩下的人工工作 |', '| --- | --- | --- | --- |')
        for (const it of r.items) lines.push(`| ${cell(`${it.id} ${it.title}`)} | ${L.status[itemStatus(r, it)]} | ${cell(it.checks)} | ${cell(humanWork(r, it))} |`)
        lines.push('')
    }
    if (r.previousReport && existsSync(join(r.previousReport, 'result.json'))) {
        const prev = JSON.parse(readFileSync(join(r.previousReport, 'result.json'), 'utf8'))
        lines.push('## 與上一輪比較', '', `上一輪：${r.previousReport}`, '', '| 項目 | 上一輪 | 本輪 | 變化 |', '| --- | --- | --- | --- |')
        for (const it of r.items ?? []) {
            const old = (prev.items ?? []).find((x) => x.id === it.id)
            const before = old ? itemStatus(prev, old) : null
            const now = itemStatus(r, it)
            const change = !old ? '新增' : before === now ? '不變' : RANK[now] > RANK[before] ? '改善' : '退步'
            lines.push(`| ${cell(`${it.id} ${it.title}`)} | ${before ? L.status[before] : '—'} | ${L.status[now]} | ${change} |`)
        }
        lines.push('')
    }

    const src = String(r.task.source).split('\n').filter(Boolean)
    lines.push('## 任務', '', ...(src.length > 1 ? ['- 來源：', ...src.map((s) => `  - ${s}`)] : [`- 來源：${src[0] ?? ''}`]),
        `- 委派者：${r.task.requester}`, `- 輪次：第 ${r.round ?? 1} 輪（${L.kind[kind] ?? kind}）`, ...(r.basis ? [`- 本輪依據：${r.basis}`] : []), '')
    const e = r.env
    const versions = Object.entries(e.versions ?? {}).map(([k, v]) => `${k} ${v ?? '-'}`).join('／')
    lines.push('## 環境', '', '| 項目 | 值 |', '| --- | --- |', `| 網址 | ${e.url} |`, ...Object.entries(e.surfaces ?? {}).map(([k, v]) => `| surface ${k} | ${v.driver}　${v.baseUrl} |`), `| 資料範圍 | ${e.dataScope} |`, `| 帳號 | ${cell(e.accounts)} |`,
        `| 瀏覽器 | ${e.browser} |`, `| 執行時間 | ${e.startedAt} |`, `| 受測版本 | ${versions || '—'} |`,
        `| skill 版本 | ${e.skillVersion}（專案檔驗證版本：${e.projectVerifiedSkillVersion ?? '未記錄'}） |`, '')

    lines.push('## 檢查點', '', '| 編號 | 檢查 | 預期 | 實際 | 判定 | 來源 | 途徑 | 證據 |', '| --- | --- | --- | --- | --- | --- | --- | --- |')
    for (const c of r.checks) {
        lines.push(`| ${c.id} | ${cell(c.title)} | ${cell(c.expected)} | ${cell(c.actual)} | ${L.verdict[c.verdict]} | ${L.by[c.by] ?? c.by}${c.agent ? '（agent）' : ''} | ${c.via ? (L.via[c.via] ?? c.via) : '—'} | ${(c.evidence ?? []).map((p) => `[${p}](${p})`).join('<br>')} |`)
    }
    lines.push('')
    const shots = [...new Set(r.checks.flatMap((c) => c.evidence ?? []).filter((p) => /\.(png|jpe?g)$/i.test(p)))]
    if (!shots.includes('shots/final.png') && existsSync(join(dir, 'shots/final.png'))) shots.push('shots/final.png')
    if (shots.length) lines.push('## 截圖', '', ...shots.flatMap((p) => [`### ${p}`, '', `![${p}](${p})`, '']))

    lines.push('## UI 問題（不影響判定）', '')
    if (r.uiFindings?.length) {
        lines.push('| 類別 | 位置 | 現象 | 證據 |', '| --- | --- | --- | --- |')
        const what = (f) => `${L.rule[f.rule] ?? f.what}${f.samples?.length ? `：${f.samples.join('、')}` : ''}`
        for (const f of r.uiFindings) lines.push(`| ${L.uiType[f.type] ?? f.type} | ${cell(f.where)} | ${cell(what(f))} | ${(f.evidence ?? []).map((p) => `[${p}](${p})`).join('<br>')} |`)
        lines.push('')
    } else lines.push('- 無', '')

    lines.push('## 寫入紀錄', '', ...(r.writes?.length ? r.writes.map((w) => `- ${w.at ? `${w.at.slice(11, 19)}　` : ''}${w.what}（${w.where}，${w.how}）`) : ['- 無，僅登入紀錄']), '')
    const apiWrites = readManifest(dir).entries.filter((m) => m.auto)
    if (apiWrites.length) lines.push('### API 寫入呼叫', '', '| 時間 | surface | 帳號 | 呼叫 | 狀態 |', '| --- | --- | --- | --- | --- |',
        ...apiWrites.map((m) => `| ${String(m.at).slice(11, 19)} | ${m.surface} | ${m.account ?? '—'} | ${cell(`${m.method} ${m.path}`)} | ${m.status} |`), '')
    lines.push(...traceLines(dir, cell))
    lines.push('## 阻礙與偏差', '', ...(r.issues?.length ? r.issues.map((s) => `- ${s}`) : ['- 無']), '')
    if (r.observations?.length) lines.push('## 其他觀察', '', ...r.observations.map((s) => `- ${s}`), '')
    lines.push('## 重現方式', '', '```bash', ...(r.reproduce ?? []), '```', '')
    writeFileSync(join(dir, 'report.md'), lines.join('\n'))
    return join(dir, 'report.md')
}
