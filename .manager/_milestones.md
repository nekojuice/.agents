# Milestones and Progress Ledger

Updated: 2026-11-04

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
| M6 | factory 插入 agent E2E review | 實作 | 🟡 | commit aecd92e、6bccacb、981f2af、d731431；run 2026-11-03-agent-e2e-review、2026-11-04-e2e-review-surfaces-recipes | 第一階段試用成功（2026-11-04），整體未驗收 |

## Feature progress

| Capability | 拆解 | 異動決策 | 沖入 | Overall | Note |
| --- | --- | --- | --- | --- | --- |
| factory 分支 | ✅ | ✅ | ✅ | ✅ | |
| pm 分支 | ✅ | ✅ | ✅ | ✅ | |
| 文件分支 | ✅ | ✅ | ✅ | ✅ | 新增 doc-tutorial-guide、doc-openapi-guide |
| pm 與 factory 協調、自動化 | ✅ | ✅ | ✅ | ✅ | 委派預設 peer；自動化兩段流程 |
| 非產品路線流程 | ✅ | ✅ | ✅ | ✅ | references/non-product-route.md |
| agent E2E review | ✅ | ✅ | ✅ | 🟡 | 已沖入；1.2 加入 API surface 與 recipes；持續試用 |

## In progress

| Work item | Axis | Target | Stage | Evidence |
| --- | --- | --- | --- | --- |
| SK-E | 實作 | M6 | verifying | commit aecd92e、6bccacb、981f2af、d731431 |

## Backlog / not started

| Item | Type | Related case | Evidence |
| --- | --- | --- | --- |
| SK-X2 | initiative | M3 | — |
| SK-R2 | debt | — | 各元素對照 §3 |
