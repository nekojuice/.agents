# 資訊來源優先序

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

工廠與審查類 skill 判斷時依序參照：使用者提出或確認的資訊 > manager 正典檔、主規格、專案文件 > run 內未經確認的筆記 > change 文件。change 是審查對象與設計藍圖，可能寫錯或描述不清。

## How to apply

- 工廠可唯讀查閱 `.manager` 全部內容，嚴禁寫入；`_runs/` 只當線索。
- manager 過時或有誤時，在工廠 run 的筆記訂正，並寫給 manager 的交接檔。
- PM 依使用者指示讀取交接檔，處理紀錄記在自己的 run。
- 正本在 code-review 的依據來源步驟，其他 skill 的副本保持語意一致。
