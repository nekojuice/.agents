# agent E2E review 階段

- Status: accepted
- Scope: orchestrator-factory、e2e-review、opsx-apply-guide、opsx-propose-guide、need-ask-user-guide、orchestrator-pm
- Date: 2026-11-03，2026-11-04 補範圍、收尾改為歸檔，2026-11-12 更正 backlog 用語、補累積設計的目的
- Authority: 使用者明確指示

## Decision

factory 在 Check 之後、人工 E2E 之前，預設派專責 E2E worker 依清單實際操作受測系統、取證交報告；這是人工檢查前最後一道 agent 自檢，不取代人工驗收。實作 session 與 orchestrator 都不操作受測系統。orchestrator 覆核報告與證據後精簡人工清單，只留重點、未測、失敗、無法判定與 agent 做不了的項目；人工接手後沿用原本的修改與收尾迴圈。

## How to apply

- 小型 run 可在確認派工時剔除 Check 或 E2E；長時間自動化在計畫核可時一併授權。
- 失敗分流與重跑次數由 orchestrator 判斷；工具操控可靠度有限，agent 執行失敗不視為產品失敗。
- `.e2e/` 是 E2E 階段的合法寫入區；初始化需使用者核可；變更由 orchestrator 依 commit-on-request 的授權 commit，worker 不 commit。
- run 的 `_review-checklist.md` 是逐項明細，打勾永久保留；跨 run 的 `_review-queue.md` 是高抽象彙總，給使用者最終驗收用；`_issue-backlog.md` 是跨 run 問題暫存區。兩份檔讓執行中發現的問題與待檢查項目先累積，不中斷主流程；agent E2E review 逐項消化 queue，只有 agent 做不了的才留給人工測試。兩份根目錄檔由 orchestrator 寫、manager 必要時可更新；queue 的未勾項目自帶原因與解除條件。收尾時已完成項目移入 `.factory/archive/`，未完成的留在根目錄檔（見 `factory-cross-run-archive.md`）。
- orchestrator 不得以自身推論把 worker 判為需人工或無法判定的項目改判通過；與 spec 不一致的觀察交使用者決定。每輪 E2E 回傳後即收尾：清單已勾附報告、未勾附報告與原因，並更新跨 run 檔與狀態。
- 報告分類、密碼處理、腳本分層等 worker 內部設計歸 e2e-review。
- 2026-11-04 範圍：透過 API 的驗證與測試資料準備也歸 e2e-review 管，資料經系統自身的 API 準備（畫面實際使用、或專案公開 API 契約定義的端點），不直接寫資料庫；surface 目前只有 web 與 api，不預先擴充；recipe 先設計，暫不作為驗收依據（依 recipe 中 agent 步驟判定的項目一律留給人工）。
