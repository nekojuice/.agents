# PM Library Index

## Facts

| Title | Status | Scope | Summary | Path |
| --- | --- | --- | --- | --- |

## Decisions

| Title | Status | Scope | Summary | Path |
| --- | --- | --- | --- | --- |
| manager 可修改 skill | accepted | 本 repo | skill 修改不屬程式實作；先寫異動決策，再由 manager session 直接修改，以 git diff 審查 | decisions/manager-edits-skills.md |
| 專案中立規則 | accepted | 全 repo | skill 本文與 manager 正式文件不得含外部專案內容；外部材料只存 `_runs/` | decisions/project-neutrality.md |
| 資訊來源優先序 | accepted | 工廠與審查類 | 使用者 > manager 與主規格 > run 筆記 > change；工廠可唯讀 .manager | decisions/information-source-priority.md |
| 跨對象交接檔命名 | accepted | 工廠與 PM | handoff-<recipient>-<topic>.md，收件方不回寫 | decisions/handoff-file-naming.md |
| 代為 commit 的授權範圍 | accepted | commit 相關 | 明確要求才 commit；worker 不 commit；新增 skill 用 feat | decisions/commit-on-request.md |
| 待決事項呈現 | accepted | 委派工作回報 | 只列阻擋且未記錄的決策；已記錄仍阻擋者列阻擋項 | decisions/pending-decisions-presentation.md |
| 討論模式例外提醒 | accepted | 討論模式 | 只答所問；四類嚴重風險可一行提醒 | decisions/discussion-exception-reminders.md |
| 審查分類標記 | accepted | 審查類 | 三個共用分類與判定界線 | decisions/review-finding-tags.md |
| 文件 skill 繼承架構與類型路由 | accepted | 文件 skill | 父層路由，子 skill 繼承並以覆寫表宣告衝突 | decisions/doc-skill-family.md |
| 規則正本歸屬 | accepted | 全部 skill | 一條規則一個正本，其他引用 | decisions/rule-ownership.md |
| skill 檔頭的 extends 位置 | accepted | 全部 skill | extends 放 frontmatter 最外層 | decisions/skill-frontmatter-extends.md |

## Skill element maps

各 skill 目前的元素對照，依分支存放於 `skills/<branch>/<skill>.md`，見 `skills/index.md`。
