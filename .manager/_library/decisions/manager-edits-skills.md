# manager 可修改 skill 本文

- Status: accepted
- Scope: 本 repo
- Date: 2026-10-19，2026-10-20 修訂流程，2026-11-02 流程移入 skill
- Authority: 使用者明確指示

## Decision

orchestrator-pm 的「不實作產品」規則針對程式實作。本 repo 的產品是 skill 文字，skill 修改不屬程式實作，由 manager session 直接修改 skill 本文，不需另開 factory。

## How to apply

- 流程依 orchestrator-pm 的 Non-product route 與 `references/non-product-route.md`：需求對照、逐輪定案、異動決策、修改、審查、git diff 驗收、擬稿與沖入、commit 與收尾。需求對照與審查為預設步驟。
- 寫入時遵守 `create-skill-guide` 與專案中立規則。
- 本 repo 的 library 保存 skill 元素對照（`_library/skills/`），屬路線第 7 節的拆解紀錄：修改後依新本文重拆並列入擬稿。
- skill 與 manager 正式檔分開 commit。
- 寫入 skill 本文以外的程式或設定，仍依一般 PM 邊界處理。
