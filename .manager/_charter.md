# Project Charter

> 狀態：草案，待使用者確認方向後定稿

## Purpose

維護一套個人 agent skill 包：研究 skill 在實際運作中的落差，並把可通用的規則實作回 skill 本文。

## Target state

- 每個 skill 的文字與實際運作一致；允許的偏離有明文記載。
- 每項 skill 修改都能追溯到一個觀察到的現象或使用者訴求。
- 同類 skill 之間不互相矛盾；需依情境區分的規則以適用條件分開寫明。

## Constraints

- **專案中立**：skill 本文與 manager 正式文件（`_charter.md`、`_status.md`、`_milestones.md`、`_backlog.md`、`_library/**`）不得出現任何外部專案的內容，包含路徑、專案名稱、範例、few-shot 程式碼。外部專案的材料只能存在 `_runs/` 之下。
- **先待沖入、後沖入**：skill 修改先寫成 run 內的待沖入稿，經使用者檢查後才寫入 skill 本文。
- 建立或修改 skill 時遵守 `create-skill-guide`：雙宿主調用設定、metadata、版本與時間戳。
- 規則改善以抽象、可重用的形式表達；具體案例只作為 run 內的追溯證據。

## Explicit exclusions

- 不在此處實作或修改任何外部專案。
- 不把單一專案的決策寫成 skill 規則。

## Authority

- PM authority：維護 `.manager`、拆解與分析 skill、整理訴求與待沖入稿、提出修改候選。
- Human authority：核可方向、核可待沖入稿、決定何時沖入 skill 本文。
- 沖入執行者：manager session。本 repo 的產品是 skill 文字而非程式，經使用者核可的待沖入稿由 manager session 直接寫入 skill 本文，不經 factory；見 `_library/decisions/manager-edits-skills.md`。

## Success conditions

- 每個分支（factory、pm、文件）的訴求都已對應到具體 skill 元素，並有經使用者核可的沖入結果。
- 沖入後的 skill 本文通過專案中立檢查。
