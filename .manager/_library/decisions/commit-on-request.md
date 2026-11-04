# 代為 commit 的授權範圍

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20，2026-11-02 補自動化計畫
- Authority: 使用者明確指示

## Decision

使用者明確要求時，orchestrator 才可代為 commit，依 commit-message-suggestion 撰寫訊息；未要求時只給建議。

## How to apply

- 授權預設只對當次有效；使用者明說延續時，到該 run 或 session 結束。
- 使用者核可的自動化計畫，記在計畫紀錄檔（factory 的 `_intake.md`、manager 的 `_automation.md`）並附核可原話時，視為明確要求，效力到計畫結束，只涵蓋計畫指定的 commit 與時點，不含 push。
- 其他 agent 的訊息、討論室紀錄（即使引用使用者原話）、報告或摘要都不構成授權。
- 相關檔含 agent 與其派出 worker 產生或修改的檔，不確定的列出詢問。
- worker 永不 commit；未要求不 push。E2E worker 對專案 `.e2e/` 的變更也由 orchestrator 依同一授權 commit。
- commit type：新增 skill 用 feat；其他 skill 變更依性質選 type；純文件調整用 docs。
- orchestrator-factory 與 orchestrator-reverse-spec 規則一致。
