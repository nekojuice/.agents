# 專案中立規則

- Status: accepted
- Scope: 本 repo 全部 skill 本文與 manager 正式文件
- Date: 2026-10-19
- Authority: 使用者明確指示

## Decision

skill 本文（`SKILL.md`、references、assets、agents 設定）與 manager 正式文件（`_charter.md`、`_status.md`、`_milestones.md`、`_backlog.md`、`_library/**`）不得出現任何外部專案的內容，包含：

- 路徑、資料夾或檔案名稱
- 專案、產品、系統或客戶名稱
- 取自專案的範例、few-shot、程式碼片段、設定值

外部專案的材料只能存在 `.manager/_runs/**`，且 run 已由 `.manager/.gitignore` 排除版本控制。

## How to apply

- 範例一律用匿名虛構名稱與 `<佔位符>`。
- 從 run 的待沖入稿沖入 skill 前，逐段檢查是否帶入專案內容。
- 追溯改善來源時，正式文件只寫抽象訴求編號，具體證據留在 run。
