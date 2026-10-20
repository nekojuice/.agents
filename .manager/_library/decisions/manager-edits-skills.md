# manager 可修改 skill 本文

- Status: accepted
- Scope: 本 repo
- Date: 2026-10-19，2026-10-20 修訂流程
- Authority: 使用者明確指示

## Decision

orchestrator-pm 的「不實作產品」規則針對程式實作。本 repo 的產品是 skill 文字，skill 修改不屬程式實作，由 manager session 直接修改 skill 本文，不需另開 factory。

## How to apply

- 修改前先在 run 的 `changes/` 寫異動決策，使用者檢查後指示修改。
- 直接修改 skill 本文，使用者以 git diff 審查。
- 寫入時遵守 `create-skill-guide` 與專案中立規則。
- 異動完成後，依異動決策的「manager 影響」產出 manager 待沖入稿，使用者檢查後才更新正式文件。
- 寫入 skill 本文以外的程式或設定，仍依一般 PM 邊界處理。
- 流程依 orchestrator-pm 的 Non-product route。
