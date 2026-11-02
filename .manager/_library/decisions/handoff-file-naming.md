# 跨對象交接檔命名

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20，2026-11-02 修訂位置
- Authority: 使用者明確指示

## Decision

跨對象交接檔命名為 `handoff-<recipient>-<topic>.md`，檔頭三行為來源 run、收件方、日期。manager 與 factory 之間的交接檔不論方向，一律放在 factory run 根目錄，讓 manager run 只管它負責的高抽象層。

## How to apply

- factory 給 manager 的放自己的 run；manager 給 factory 的放收件的 factory run，再用 peer 通知。
- 收件方不改交接檔，處理紀錄記在自己的 run。
- factory 給 manager 的交接檔一次完工寫一份，不再追加。
- 工廠內部給 worker 的暫存交接仍用 `_handoff-<worker>.md`。
- PM 建立的冷啟動交接包不套用此命名。
