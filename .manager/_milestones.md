# Milestones and Progress Ledger

Updated: 2026-11-05

> Durable progress ledger. Status glyphs project the canonical work-item stages (see state-model), not a second vocabulary. Change a status only on evidence, during status reconciliation.
> ✅ done　🟡 in progress　⬜ not started　⚠️ transitional (usable stand-in, proper solution pending)

## Milestone ledger

| # | Milestone | Axis | Status | Evidence | Human acceptance |
| --- | --- | --- | --- | --- | --- |
| M1 | skill 改善第一輪：拆解、對應訴求、異動決策 | 分析 | ✅ | run 2026-10-19-skill-improvement | 2026-10-20 |
| M2 | 第一輪沖入 skill 本文 | 實作 | ✅ | tag v1.1；兩輪審查報告在 run 內 | 2026-10-20 |
| M3 | 歷次紀錄規則蒐集與下一輪改善 | 分析 | ⬜ | — | 未 |
| M4 | pm 與 factory 協調、自動化 | 實作 | ✅ | commit 481d881、576d71a；run 2026-11-02-pm-factory-coordination | 2026-11-02（使用者指示沖入後 commit） |
| M5 | 非產品路線工作流程規範化 | 實作 | ✅ | commit f668f77、ce63c61；run 2026-11-02-non-product-route-workflow | 2026-11-02（使用者指示沖入後 commit） |
| M6 | factory 插入 agent E2E review | 實作 | 🟡 | commit aecd92e、6bccacb、981f2af、d731431；run 2026-11-03-agent-e2e-review、2026-11-04-e2e-review-surfaces-recipes、2026-11-04-skill-feedback-round；commit 0210cc7、9ebb2e1 | 第一階段試用成功（2026-11-04），整體未驗收 |
| M7 | 下一版 skill 進化：orchestrator-helper、factory 討論與收斂、成品設計檢查、非實作計畫路線、skill 回饋迴圈 | 實作 | 🟡 | commit 82af4c8、e8232a9、f46066e；run 2026-11-04-next-skill-evolution | 未 |

## Feature progress

| Capability | 拆解 | 異動決策 | 沖入 | Overall | Note |
| --- | --- | --- | --- | --- | --- |
| factory 分支 | ✅ | ✅ | ✅ | ✅ | |
| pm 分支 | ✅ | ✅ | ✅ | ✅ | |
| 文件分支 | ✅ | ✅ | ✅ | ✅ | 新增 doc-tutorial-guide、doc-openapi-guide |
| pm 與 factory 協調、自動化 | ✅ | ✅ | ✅ | ✅ | 委派預設 peer；自動化兩段流程 |
| 非產品路線流程 | ✅ | ✅ | ✅ | ✅ | references/non-product-route.md |
| agent E2E review | ✅ | ✅ | 🟡 | 🟡 | 1.2 加入 API surface 與 recipes；1.3 實用回饋修正與 factory 收尾歸檔已沖入並 commit |
| orchestrator-helper | ✅ | ✅ | ✅ | 🟡 | 1.0 已建立並沖入，待試用 |
| factory 討論與收斂 | ✅ | ✅ | ✅ | 🟡 | orchestrator-factory 1.13 已沖入，待試用 |
| 成品設計檢查 | ✅ | ✅ | ✅ | 🟡 | code-review 1.2 已沖入，待試用 |
| 非實作計畫路線 | ✅ | ✅ | ✅ | 🟡 | orchestrator-factory 1.14、change review 1.2 已沖入，待試用 |
| skill 回饋迴圈 | ✅ | ✅ | ✅ | 🟡 | skill-feedback-notes 1.0 已建立並沖入，待試用 |

## In progress

| Work item | Axis | Target | Stage | Evidence |
| --- | --- | --- | --- | --- |
| SK-E | 實作 | M6 | verifying | commit aecd92e、6bccacb、981f2af、d731431 |
| SK-E2 | 實作 | M6 | verifying | run 2026-11-04-skill-feedback-round；commit 0210cc7、9ebb2e1 |
| SK-H | 實作 | M7 | verifying | run 2026-11-04-next-skill-evolution；`orchestrator-helper-draft.md` |
| SK-DC | 實作 | M7 | verifying | run 2026-11-04-next-skill-evolution；`requirements-comparison-factory-closing-questions.md`、`reviews/_triage.md` |
| SK-CR | 實作 | M7 | verifying | run 2026-11-04-next-skill-evolution；code-review 1.2 |
| SK-PR | 實作 | M7 | verifying | run 2026-11-04-next-skill-evolution；`changes/_index.md`、`reviews/_triage-plan-route.md` |
| SK-FN | 實作 | M7 | verifying | run 2026-11-04-next-skill-evolution；`changes/_index-skill-feedback-loop.md`、`reviews/_triage-skill-feedback-loop.md` |

## Backlog / not started

| Item | Type | Related case | Evidence |
| --- | --- | --- | --- |
| SK-X2 | initiative | M3 | — |
| SK-R2 | debt | — | 各元素對照 §3 |
