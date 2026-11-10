# orchestrator-helper 定位

- Status: accepted
- Scope: orchestrator-helper
- Date: 2026-11-05
- Authority: 使用者明確指示（manager run `2026-11-04-next-skill-evolution` 的 `orchestrator-helper-draft.md`）

## Decision

新增獨立的輔助指揮者 `orchestrator-helper`：一個可以接上任何工作的彈性幫手。它是獨立 skill，不以 factory 的條文定義或限制；規範保持非常彈性，重點是依工作當下建立的契約行事。

## How to apply

- 通常由使用者建立；平台能建立 session 時，其他角色也可以建立。
- 由使用者指揮；manager 與 factory 在授權下可直接指揮。授權通常是使用者先與上級 agent 溝通後給予，再由上級 agent 與 Helper 溝通；其他角色可用文字發動。
- 契約依發動情況指定：使用者直接呼叫時由使用者指定範圍和用法，授權角色間接呼叫時由該角色指定。
- 持有一份自己的簡單脈絡，預設固定一份檔案、可依工作調整；授權共用時才使用其他脈絡文件。
- 仍適用指揮者原則：可自建或寄宿工作區，可派遣 worker，可與 manager、factory 溝通。
- 不修改其他角色的 skill。
