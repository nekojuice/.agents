# 自動化授權契約

- Status: accepted
- Scope: orchestrator-pm、pm-factory-handoff、orchestrator-factory、commit-message-suggestion
- Date: 2026-11-02，2026-11-04 補 agent E2E review
- Authority: 使用者明確指示

## Decision

manager 與 factory 的批次施工由 manager run 管理，使用者核可自動化計畫後才執行。流程分兩段：設計段先把每個 run 的 change 開完並審查；使用者在一個關卡一次檢視全部 change 與各 run 的待決事項；確認後進入施工段，依相依順序施工。

計畫只預先授權兩項：批次檢視後依序派工（含 Check 與 agent E2E review，以及計畫寫明的 E2E 寫入授權），不再逐 run 確認派工；每個 factory run 預設 commit 一次，使用者可改或關閉。檢視 change、人工 E2E、sync/archive、push 永不預先授權。

## How to apply

- 計畫寫在 manager run 的 `_automation.md`；factory 需要的授權依值寫進各 factory run 的 `_intake.md`，附使用者核可原話與日期。
- 整批只有一個 manager session 與一個 factory session；預設由使用者建立 factory session，平台允許時 manager 可以代建。
- 設計段不為提問停下：無法依紀錄解決的決策記入該 run 的筆記，揭露假設後照常 propose，到批次檢視時彙整成一份決策清單一次問。審查需修文件時修改後重審，兩輪仍不過就記為待決事項；需使用者釐清的同樣記為待決事項。批次檢視時使用者指示的修改不需再審。
- 施工段某個 run 停下時，只暫停依賴它的 run。
- 整批完成後才彙整 `_review-queue.md`、做人工 E2E、sync/archive；歸檔時清空 queue，未處理的 `_issue-backlog.md` 項目交給 manager；push 只在使用者另外明確授權時。
- commit 授權只認使用者本人的話：對話中直接要求，或計畫紀錄檔（factory 的 `_intake.md`、manager 的 `_automation.md`）附核可原話；討論室訊息即使引用原話也不算；worker 永不 commit。
