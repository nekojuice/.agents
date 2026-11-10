# factory 非實作工作的計畫路線

- Status: accepted
- Scope: orchestrator-factory、change-review-request、change-review-response
- Date: 2026-11-10
- Authority: 使用者明確指示（manager run `2026-11-04-next-skill-evolution` 的 `requirements-comparison-factory-plan-route.md` §6）

## Decision

非實作工作需要派工時，factory 有一套選用的計畫路線：寫計畫 → 計畫審查 → 執行，條件符合時由 orchestrator 推薦。重點是計畫審查，避免 agent 不知道計畫有疏漏就直接動手。計畫審查沿用 change review，不另立一套規範。

## How to apply

- 收斂時推薦，使用者可不採用。
- 計畫寫在 run 內；審查另派 reviewer，可多輪修訂，不一定被人閘卡住：只在需要使用者釐清，或修改兩輪仍需修改時停下；使用者在收斂時要求先看計畫，則審查通過後停下。
- 執行產物通常是交接文件、檔案產物，或完成某個操作。
- 產物審查依任務內容提示，使用者授權才調用；有的事項沒有產物，或產物無法由 reviewer 判斷。
- 之後的 propose 可接續一次或多次計畫路線的產物。
