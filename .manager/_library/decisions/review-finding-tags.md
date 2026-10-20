# 審查分類標記

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

程式審查與 change 文件審查共用三個分類：`violates-change` 偏離 change；`conforms-but-flawed` 符合 change 但可在不改意圖下修正，含 change 措辭可直接修訂者；`change-design-flaw` 與更高優先來源衝突或需要使用者決定。

## How to apply

- 正本在 code-review 的分類表與 change-review 的格式檔，其他副本保持語意一致。
- `violates-change` 與 `change-design-flaw` 只出現在規格軸。
- 只有 `change-design-flaw` 會成為使用者決策，且先經 orchestrator 判斷。
