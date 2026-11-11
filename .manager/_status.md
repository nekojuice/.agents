# Project Status

Updated: 2026-11-05

## Current milestone

M7 進行中：下一版 skill 進化（run `2026-11-04-next-skill-evolution`）。新增 `orchestrator-helper` 1.0（SK-H），orchestrator-factory 1.13 加入討論與收斂（SK-DC），code-review 1.2 規格軸加入成品設計檢查（SK-CR）；2026-11-10 起 orchestrator-factory 1.14 與 change review 1.2 加入非實作計畫路線（SK-PR）；皆已修改、審查並沖入 manager，skill commit `82af4c8`、`e8232a9`，待試用。2026-11-11 起新增 `skill-feedback-notes` 1.0，orchestrator-factory 1.15、orchestrator-pm 1.7 引用（SK-FN），已修改、審查並沖入 manager，skill commit `f46066e`，待試用。

M6 進行中：factory 插入 agent E2E review。2026-11-04 起第二輪實用回饋修正（run `2026-11-04-skill-feedback-round`）：e2e-review 1.3、orchestrator-factory 1.12、orchestrator-pm 1.6、pm-factory-handoff 1.5，並新增 `.factory/archive/` 收尾歸檔；已修改、審查（八輪）、沖入 manager 並 commit（`0210cc7`、`9ebb2e1`）。skill 已 commit（`aecd92e`、`6bccacb`），第一階段試用成功。e2e-review 1.2（API surface、測試資料、recipes）在 run `2026-11-04-e2e-review-surfaces-recipes` 修改並經兩輪審查修正，commit `981f2af`；factory 1.11 與 opsx guide 對齊 commit `d731431`。M4、M5 已完成並沖入 manager。

## Active cases

| ID | Type | Outcome or question | Stage | Confidence | Factory run | Next checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| SK-E | initiative | factory 插入 agent E2E review | verifying | medium | none | 持續試用，穩定後由使用者驗收 |
| SK-E2 | initiative | e2e-review 1.2 實用回饋修正（V1～V32、1.1 未解回饋、factory 收尾與跨 run 檔歸檔） | verifying | high | none | 已 commit；持續試用 |
| SK-H | initiative | 新增 orchestrator-helper 輔助指揮者 | verifying | medium | none | 已 commit（82af4c8）；試用 |
| SK-DC | initiative | factory 討論與收斂（orchestrator-factory 1.13） | verifying | medium | none | 已 commit（82af4c8）；試用 |
| SK-CR | initiative | code-review 規格軸加入成品設計檢查（code-review 1.2） | verifying | medium | none | 已 commit（82af4c8）；試用 |
| SK-PR | initiative | factory 非實作計畫路線（orchestrator-factory 1.14、change review 1.2） | verifying | medium | none | 已 commit（e8232a9）；試用 |
| SK-FN | initiative | skill 使用後改良的回饋迴圈（skill-feedback-notes 1.0、orchestrator-factory 1.15、orchestrator-pm 1.7） | verifying | medium | none | 已 commit（f46066e）；試用 |
| SK-R2 | debt | 元素對照重拆時發現的殘留不一致 | inbox | medium | none | 下一輪修改 skill 時併入 |
| SK-X2 | initiative | 從歷次工作紀錄抽取通用規則 | inbox | medium | none | 使用者決定何時開蒐集輪 |

## Known gaps

- 歷次工作紀錄尚未蒐集（SK-X2）。
- 殘留不一致未修（SK-R2；正文在各元素對照 §3）。
- agent E2E review 只完成第一階段試用，長期穩定度待觀察。
- SK-E2 的 e2e-review 修改尚未在實際專案重跑驗證（冒煙測試在暫存專案）。
- SK-H、SK-DC、SK-CR、SK-PR、SK-FN 尚未試用。

## Decisions needed

- 章程草案是否定稿。

## Recently accepted

- 2026-11-04 第一階段 agent E2E 試用成功，commit `aecd92e`、`6bccacb`、`981f2af`、`d731431`：SK-E（持續試用）。
- 2026-11-02 非產品路線規範化，commit `f668f77`、`ce63c61`：SK-R。
- 2026-11-02 pm 與 factory 協調、自動化，commit `481d881`、`576d71a`：SK-C。
- 2026-10-20 第一輪 skill 改善，tag v1.1：SK-F、SK-P、SK-D、SK-D2。
