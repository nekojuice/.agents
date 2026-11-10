# 審查分類標記

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

程式審查與 change 文件審查共用三個分類：`violates-change` 偏離 change；`conforms-but-flawed` 符合 change 但可在不改意圖下修正，含 change 措辭可直接修訂者；`change-design-flaw` 與更高優先來源衝突或需要使用者決定，包含設計對已定目標不健全、修正會改變意圖者。

## How to apply

- 正本在 code-review 的分類表與 change-review 的格式檔，其他副本保持語意一致。
- `violates-change` 與 `change-design-flaw` 只出現在規格軸。
- 只有 `change-design-flaw` 會成為使用者決策，且先經 orchestrator 判斷。
- change 文件審查也審 factory 計畫路線的 run 計畫，判定值、下一步與分類不變（2026-11-10，使用者指示）。
- 設計檢查分兩段：apply 前由 change 文件審查依已定需求與設計原則審 change；apply 後由程式審查的規格軸，依已定目標檢查做成後的設計（2026-11-05，使用者指示）。
