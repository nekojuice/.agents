# PM Backlog

> 只記錄專案中立的抽象訴求；來源證據在對應 run 內。

## Inbox

| ID | Type | Summary | Source | Stage | Next action |
| --- | --- | --- | --- | --- | --- |
| SK-X2 | initiative | 從歷次工作紀錄抽取通用規則，收納為 skill 元素 | 2026-10-19 交接 | inbox | 另開蒐集輪；SK-FN 的回饋筆記可作為原料來源 |
| SK-E | initiative | factory 插入 agent E2E review：新增 e2e-review、review queue 與 issue backlog 拆分、人工清單精簡 | 2026-11-03 使用者 | verifying | 已 commit（aecd92e、6bccacb、981f2af、d731431）；第一階段試用成功，持續試用 |
| SK-E2 | initiative | e2e-review 實用回饋修正：試跑、報告、更正（amend）、預演、測試資料與帳號通用規則、驅動與秘密；factory 每輪收尾、不得自行升級需人工項、跨 run 檔收尾歸檔到 `.factory/archive/`、manager 撿走長期條目 | 2026-11-04 使用者 | verifying | 已 commit（0210cc7、9ebb2e1）；持續試用 |
| SK-H | initiative | 新增 `orchestrator-helper`：獨立的輔助指揮者，契約依工作當下由發動者指定，持有自己的簡單脈絡，授權下 manager 與 factory 可指揮 | 2026-11-04 使用者 | verifying | 已 commit（82af4c8）並沖入；試用 |
| SK-DC | initiative | factory 討論與收斂：討論不當成動工計畫、自主記筆記與 manager 交接、提問前查紀錄；行動前收斂，決策每題必附推薦，零題也停下 | 2026-11-05 使用者 | verifying | 已 commit（82af4c8）並沖入；試用 |
| SK-CR | initiative | code-review 規格軸加入成品設計檢查：apply 後依已定目標判斷做成的設計，與 apply 前的 change 文件審查分工 | 2026-11-05 使用者 | verifying | 已 commit（82af4c8）並沖入；試用 |
| SK-FN | initiative | skill 使用後改良的回饋迴圈：新增 skill-feedback-notes，factory、manager 引用；收尾交接給 skill repo 的 manager | 2026-11-11 使用者 | verifying | 已 commit（f46066e）並沖入；試用 |
| SK-PR | initiative | factory 非實作工作的選用計畫路線：計畫 → 計畫審查（沿用 change review，可多輪）→ 執行；產物審查需使用者授權 | 2026-11-10 使用者 | verifying | 已 commit（e8232a9）並沖入；試用 |
| SK-R2 | debt | 元素對照重拆時發現的殘留不一致：orchestrator-pm、pm-factory-handoff、pm-status-review、orchestrator-factory、commit-message-suggestion、peer-agent-coordination 與兩份 readme（正文在各對照 §3） | 2026-11-02 元素對照 | inbox | 下一輪修改 skill 時併入 |

## Deferred

| ID | Summary | Reason | Revisit condition |
| --- | --- | --- | --- |

## Rejected or answered

| ID | Summary | Outcome | Evidence or response |
| --- | --- | --- | --- |
| SK-F | factory 分支：人工驗證清單抽象化、審查三分類與補脈絡、orchestrator 判斷力、待決事項呈現、修訂輪、代為 commit、歸檔條件、worker 續用、狀態檔防重複、討論模式邊界、propose 驗證骨架安全、範例匿名、跨 repo 契約、factory run 移入 `_runs/` | 已完成，使用者驗收 | tag v1.1；決策見 library |
| SK-P | pm 分支：非產品路線、工廠參照 manager 的邊界、交接回流、worker 多產物與拆解模式 | 已完成，使用者驗收 | tag v1.1；決策見 library |
| SK-D | 文件分支：新增 doc-tutorial-guide、子 skill 繼承架構、類型路由、通用規則補強 | 已完成，使用者驗收 | tag v1.1；決策 doc-skill-family |
| SK-D2 | 新增 doc-openapi-guide 並列入父層類型路由 | 已完成，使用者驗收 | tag v1.1 |
| SK-X1 | 建置發布結果一致性的檢查項 | 不做 | 建置與發布高敏感、各專案差異大、agent 看不到部署目標 |
| SK-X5 | java-coding-style 屬專案專用且含外部專案名稱 | 已處理 | 自使用者級移除，改由專案工作區託管 |
| SK-C | pm 與 factory 協調、自動化：factory 主動交接、檢查清單兩級、manager 委派用 peer、待沖入區、自動化兩段流程 | 已完成，使用者確認沖入 | run `2026-11-02-pm-factory-coordination`；決策 automation-authorization、manager-project-level |
| SK-R | 非產品路線的工作流程規範化：需求對照、審查輪、元素對照同步、staging 位置；併修上一輪殘留不一致 | 已完成，使用者確認沖入 | run `2026-11-02-non-product-route-workflow`；orchestrator-pm `references/non-product-route.md` |
