# 跨 run 檔收尾歸檔

- Status: accepted
- Scope: orchestrator-factory、orchestrator-pm
- Date: 2026-11-04
- Authority: 使用者明確指示（manager run `2026-11-04-skill-feedback-round` 需求對照第 6 節）

## Decision

`.factory/_review-queue.md` 與 `.factory/_issue-backlog.md` 的已完成項目不再於收尾時刪除，改仿 opsx 歸檔，移入 `.factory/archive/`，讓人與 agent 日後仍找得到。短期要處理的留在 factory 兩份根目錄檔；長時間沒處理的，由 manager 發動撿走。

## How to apply

- 檔名：`.factory/archive/<YYYY-MM-DD>-review-queue.md`、`.factory/archive/<YYYY-MM-DD>-issue-backlog.md`；日期為收尾當天本地日期；兩類各一檔，同一天同類寫同一檔。
- 每次收尾加一節 `## <HH:mm> <做收尾的 run slug>`（自動化批次為收尾整批的 run），只追加不改寫；檔首一行說明日期、類別與條目格式；每筆保留原條目全文，前加一行收尾時間、該項目自己的來源 run 與結果（agent 驗過附報告、使用者確認結案、不修、已開 change 名稱）。
- 只在收尾（sync／archive）時歸檔，不在條目狀態改變時歸檔。歸檔對象：queue 中本次工作已勾或使用者確認結案的項目；backlog 中不修、已開 change 的條目。
- 未完成的 queue 項目與未處理的 backlog 條目留在根目錄檔；factory 不在收尾時主動交給 manager。
- manager 發動撿走長期未處理的條目：擬稿進 run 的 `staging/`，使用者檢查後寫入 `_backlog.md`，再自 factory 根目錄檔刪除並記在 run。manager 不寫 `archive/`。
- `archive/` 預設進版控、隨收尾 commit；兩份根目錄檔仍是使用者要求才 commit。專案可自行決定 ignore。
