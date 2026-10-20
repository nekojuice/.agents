# 待決事項呈現

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

檢查點回報的待決事項依 need-ask-user-guide 呈現，正本在該 skill。

## How to apply

- 決策區只列阻擋流程且尚未記錄的事項。
- 已記錄但仍阻擋的事項列為阻擋項並指向紀錄，不降為提醒。
- 提醒另列。
- 人工驗證或審查清單只收需要人判斷的項目，排除自動測試已涵蓋者與簡單邏輯檢查；畫面驗收依畫面彙整。
- 需要使用者釐清的審查結果，orchestrator 先依資訊來源優先序自行判斷，無法判斷的才彙整成一份清單交使用者。
