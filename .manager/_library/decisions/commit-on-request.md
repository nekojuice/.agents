# 代為 commit 的授權範圍

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

使用者明確要求時，orchestrator 才可代為 commit，依 commit-message-suggestion 撰寫訊息；未要求時只給建議。

## How to apply

- 授權預設只對當次有效；使用者明說延續時，到該 run 或 session 結束。
- 相關檔含 agent 與其派出 worker 產生或修改的檔，不確定的列出詢問。
- worker 永不 commit；未要求不 push。
- commit type：新增 skill 用 feat；其他 skill 變更依性質選 type；純文件調整用 docs。
- orchestrator-factory 與 orchestrator-reverse-spec 規則一致。
