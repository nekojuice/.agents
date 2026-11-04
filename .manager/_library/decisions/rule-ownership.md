# 規則正本歸屬

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20，2026-11-02 修訂（兩次），2026-11-04 修訂
- Authority: 使用者明確指示

## Decision

一條規則只有一個正本，其他 skill 引用並保持語意一致。

## How to apply

- 測試調整紀律與人工驗證清單抽象層級（broad、focused 兩級）：opsx-apply-guide。
- 修訂標註寫法：opsx-propose-guide；修訂流程與人閘：orchestrator-factory。
- 流程對子 skill 預設行為的覆寫：寫在流程 skill。
- 多 agent 協作：不主動啟用，使用者提及、協作討論需要，或使用者核可的流程（如 manager 委派）指定時才用；無即時通道時由使用者人工轉送。
- 自動化授權：orchestrator-pm `## Automation`；factory 端的執行規則在 orchestrator-factory `## Automation`。
- 非產品路線流程（需求對照、審查輪、拆解紀錄同步、分開 commit）：orchestrator-pm `references/non-product-route.md`。
- agent E2E review 的 worker 規範（邊界、判定、報告格式、腳本分層、專案 `.e2e/` 結構）：e2e-review；factory 端的派工、覆核、人工清單精簡、`_review-queue.md` 與 `_issue-backlog.md` 規則：orchestrator-factory。
- 背景接聽是否需要：peer-agent-coordination §5 第 3 點；各通道 reference 只說明該通道本身。
- 文件同步：預設只同步 README；其他文件先列清單給使用者確認，不得擅自更新，寫法依 doc 系列 skill。
- 外部來源的 openspec 原生 skill 不改。
