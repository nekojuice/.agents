# factory 討論與收斂

- Status: accepted
- Scope: orchestrator-factory
- Date: 2026-11-05
- Authority: 使用者明確指示（manager run `2026-11-04-next-skill-evolution` 的 `requirements-comparison-factory-closing-questions.md` §6–§8）

## Decision

工廠模式的工作分三段：自由唯讀討論 → 行動前收斂（`converge`）＋可選的決策提問 → 行動流程。討論階段不把討論或查到的資料當成馬上要動工的計畫，也不在回覆結尾附決策區塊；只有在 propose 或其他真正的行動前，才找出需要使用者決定的問題並提問。只修改 `orchestrator-factory`，`discuss-first` 與 `need-ask-user-guide` 不改。

## How to apply

- 討論階段：專案檔唯讀，只寫 run 內檔案；出現第一個值得記錄的事項才建 run，純問答不建。
- 不需提醒就記錄：使用者說出或確認的決策寫入 `_memory.md` `## User decisions`，收斂但未確認的事項與值得保留的查詢結果寫入 `_notes.md`。
- 提問前先讀 run 筆記、`.manager`（唯讀）與專案文件，套用 `need-ask-user-guide`；紀錄已定的事不問，與已記錄決策衝突的選項當成衝突提出。
- 討論回覆不附狀態回報與 Decisions needed 清單；`discuss-first` 的待議清單照舊。
- 討論出與 `.manager` 衝突或值得記錄的事項，在收斂或討論結束時寫成一份 manager 交接，多寫無妨，是否採用由 manager 決定。
- 收斂：使用者指示行動時進入；先列已定摘要，再列阻擋行動且紀錄定不了的決策，每題一定附推薦選項；可為零題。
- 收斂後停下等使用者開始行動，零題也一樣；只有使用者已授權「沒問題就開始 propose／派工」這類語意，或 run 帶自動化授權時才直接進行。
- 狀態回報只在進入工廠模式、進入收斂、階段轉換、人閘、stop-for-human 與使用者詢問時輸出。
- 自動化 run 的設計段取代討論與收斂，不受本決策影響。
