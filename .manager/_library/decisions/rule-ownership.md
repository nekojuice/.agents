# 規則正本歸屬

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

一條規則只有一個正本，其他 skill 引用並保持語意一致。

## How to apply

- 測試調整紀律與人工驗證清單抽象層級：opsx-apply-guide。
- 修訂標註寫法：opsx-propose-guide；修訂流程與人閘：orchestrator-factory。
- 流程對子 skill 預設行為的覆寫：寫在流程 skill。
- 多 agent 協作：不主動啟用，使用者提及或協作討論需要時才用；無即時通道時由使用者人工轉送。
- 文件同步：預設只同步 README；其他文件先列清單給使用者確認，不得擅自更新，寫法依 doc 系列 skill。
- 外部來源的 openspec 原生 skill 不改。
