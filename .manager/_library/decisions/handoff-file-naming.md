# 跨對象交接檔命名

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

跨對象交接檔命名為 `handoff-<recipient>-<topic>.md`，放在寄件方 run 根目錄，檔頭三行為來源 run、收件方、日期。

## How to apply

- 收件方處理後記在自己的 run，不回寫寄件方 run。
- 工廠內部給 worker 的暫存交接仍用 `_handoff-<worker>.md`。
- PM 建立的冷啟動交接包不套用此命名。
