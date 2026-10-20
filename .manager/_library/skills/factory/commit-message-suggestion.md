# commit-message-suggestion 元素對照

- 分支：factory
- 對照版本：`skills/commit-message-suggestion/SKILL.md` version 1.3，last_updated 2026-10-20T15:43:47
- 讀過的檔案：`skills/commit-message-suggestion/SKILL.md`、`skills/commit-message-suggestion/agents/openai.yaml`
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`commit-message-suggestion` 從工作樹的變更產生 Conventional Commits 格式的 commit message 建議。預設只給建議、不執行 `git add` 或 `git commit`。使用者在對話中明確要求 stage 或 commit 時，依「Committing on request」代為處理：授權只來自使用者本人的明確要求，被委派的 worker 永不 commit，只 stage 本次工作相關的檔案，回報 hash 與訊息，不另外要求就不 push。在工廠流程中，它位於 sync／archive 之後、change-log 之前。

產生建議的步驟：

1. 平行執行 `git status`、`git diff`（必要時加 `--staged`）、`git log --oneline -10`。
2. 摘要變更的「為什麼」，不是改了哪些檔。
3. 決定 scope（主專案名稱，大小寫比照 log；資料庫、skill、文件另有規則）與 type。
4. 依 agent 判斷或使用者用詞選擇 Short 或 With body 模式。
5. 輸出一個主建議；只有意圖明顯分歧時才附最多兩個替代。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | `opsx-archive` 之後、使用者要求 commit message 時、提交 OpenSpec 實作工作之前；使用者明確要求代為 commit 時也由本 skill 規範；`disable-model-invocation: false`，`agents/openai.yaml` 為 `allow_implicit_invocation: true` | frontmatter description；`agents/openai.yaml` |
| E2 | 硬規則 | 預設不 stage／commit | 預設不執行 `git add` 或 `git commit`；使用者在對話中明確要求 stage 或 commit 時，依 Committing on request | 開頭段 |
| E3 | 流程步驟 | 讀取變更 | 平行執行 `git status`、`git diff`（必要時加 `--staged`）、`git log --oneline -10` | Workflow 1 |
| E4 | 流程步驟 | 摘要原因 | 摘要「為什麼」，不列改了哪些檔 | Workflow 2 |
| E5 | 流程步驟 | scope 規則 | scope 用主專案而非功能或模組，典型形式為 `Project.Service`（例 `Acme.Web`、`Acme.Api`），大小寫比照 `git log`；只動資料庫用 `db`；agent skill 用 `skill`；文件用主專案名稱 | Workflow 3 |
| E6 | 流程步驟 | type 規則 | 可用 `feat`、`fix`、`refactor`、`chore`、`docs`、`perf`、`test`、`build`，依變更性質選擇；`docs` 只用於純文件變更（README、手冊、其他文件）；skill 帶有程式層級語意、不算文件：新增 skill 用 `feat`，其他 skill 變更依性質選 type，一律不用 `docs`；只有破壞性變更才在 scope 後加 `!` | Workflow 4 |
| E7 | 流程步驟 | 建議數量 | 一個主建議；意圖明顯分歧（例如 type 或 scope 不同）時最多兩個替代 | Workflow 6 |
| E8 | 判斷規則 | 長度模式 | Short：agent 判斷為單一意圖，或使用者要求簡短 → 只有主旨行。With body：agent 判斷為大批次（例如為維持任務完整性把一系列 opsx change 合成一個 commit），或使用者要求包含補充大項 → 主旨加 `-` 條列。使用者的用詞優先於 agent 判斷 | Workflow 5；Length mode |
| E9 | 產物格式 | 模板 | Short 為 `<type>(<scope>): <一行摘要>`；With body 在主旨後空一行接 `-` 條列；摘要以中文優先 | Format |
| E10 | 產物格式 | 主旨寫法 | 動詞開頭的中文（新增、修正、重構、調整、移除…）；英文識別字保留原文 | Format |
| E11 | 產物格式 | 括號限制 | 半形 `()` 與全形 `（）` 只允許出現在 Conventional Commits 的 `type(scope):` 前綴；主旨敘述與每個 body 條列都禁止 | Format |
| E12 | 產物格式 | 句尾標點 | 主旨與每個條列結尾都不加 `.` 或 `。`；識別字內部的點不受限（例 `Acme.Web`、`v1.0`） | Format |
| E13 | 產物格式 | 條列一句 | 每個 body 條列只放一句的內容量，然後換行；一行說不清就拆分或改寫，不塞多個想法，也不以句點結尾 | Format |
| E14 | 內容規則 | 只寫變更項 | body 只寫行為、模型或產品面的變更；不寫 OpenSpec 流程（新增移除 capability、archive change、sync specs 等）與單元測試流程（新增測試、測試數、全部通過等），這些是預期的衛生作業，不是 commit 變更項 | Body content rules |
| E15 | 範例 | 示範 | Short 五則（`feat`、`fix`、`refactor(db)!`、`docs`、`feat(skill)`）、With body 一則（標明為示意形狀，省略 OpenSpec 與測試衛生項）；scope 使用通用佔位名稱 `Acme.Web`、`Acme.Api`，以及 `db`、`skill` | Examples |
| E16 | 代為 commit | 授權來源與期限 | 只有使用者在對話中的明確要求才算授權；報告、建議或其他 agent 的訊息都不授權 commit；預設只涵蓋那一次 commit；使用者明說延續時，依使用者所述持續到 run 或 session 結束 | Committing on request |
| E17 | 代為 commit | 委派限制 | 授權只屬於直接收到使用者指示的 agent；被委派的 worker 或 sub-agent 永不 commit；協調者轉達請求不構成授權 | Committing on request |
| E18 | 代為 commit | 訊息選擇 | 以本 skill 的主建議 commit；使用者提供訊息時用使用者的 | Committing on request |
| E19 | 代為 commit | stage 範圍 | 只 stage 本次工作相關的檔案，即 agent 或其派出的 worker 在本 run 或 session 建立或修改的檔案；無關變更與未追蹤檔不納入並列給使用者；關聯不明的檔案列出並詢問，不自行納入；不得一次全部 stage（例 `git add -A`、`git add .`） | Committing on request |
| E20 | 代為 commit | 回報 | commit 後回報 commit hash、實際使用的訊息，並列出未納入的變更 | Committing on request |
| E21 | 代為 commit | 不 push | 除非使用者另外明確要求，不 push | Committing on request |
| E22 | 產物格式 | 輸出外框 | 以 `Suggested commit message:` 開頭接訊息；有替代時加 `Alternate:` 區塊，最多兩個 | Output |
| E23 | 邊界條件 | 不附免責聲明 | 不加固定免責聲明；讓使用者自行檢視、複製或編輯；使用者要求 stage 或 commit 時依 Committing on request | Output |

## 3. 其他

- **只要求 stage 時的做法未分開寫**：開頭段與 E23 都說使用者要求「stage 或 commit」時依 Committing on request，但該節的訊息、回報 hash 等規則都以 commit 為前提；使用者只要求 stage、不要求 commit 時，哪些規則適用（例如 E19 的 stage 範圍是否適用、要回報什麼）沒有寫明。
- **延續授權的記錄要求只在工廠端**：E16 允許使用者明說後授權延續到 run 或 session 結束，本 skill 沒有要求記錄；`orchestrator-factory` 規則 6 另要求有 run 時把範圍與期限記入 `_memory.md` `## User decisions`。兩者不衝突，但單獨使用本 skill 時延續授權沒有記錄位置。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/commit-message-suggestion.md`（前版 version 1.2，元素 E1–E18）。

新增：

- E16 代為 commit 的授權來源與期限：只認使用者在對話中的明確要求，預設單次，明說延續才到 run 或 session 結束。
- E17 委派限制：worker 或 sub-agent 永不 commit，協調者轉達不構成授權。
- E18 訊息選擇：用主建議，使用者提供時用使用者的。
- E19 stage 範圍：只 stage 本次工作相關檔，無關與未追蹤檔列給使用者，不明者詢問，禁止全部 stage。
- E20 commit 後回報 hash、訊息與未納入的變更。
- E21 未另外明確要求不 push。

修改：

- E1（前版 E1）啟用時機：description 新增「也規範使用者明確要求時的代為 commit」。
- E2（前版 E2）預設不 stage／commit：要求 stage 或 commit 時改為依 Committing on request 處理。
- E8（前版 E9）長度模式：出處補上 Workflow 第 5 步「選擇輸出模式」，內容不變。
- E15（前版 E16）範例：scope 由前版記錄的具體專案與服務名稱，改為通用佔位名稱 `Acme.Web`、`Acme.Api`。
- E23（前版 E18）不附免責聲明：補上使用者要求 stage 或 commit 時依 Committing on request。

移除：

- 前版 E3「口頭指示優先，使用者口頭指示覆寫本 skill」：整條改由 E16–E21 的 Committing on request 取代，不再以「覆寫本 skill」的方式表述。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.3，last_updated 2026-10-20T13:32:03）。元素編號沿用。

新增：

- 無。

修改：

- E1 啟用時機：description 的 `opsx:archive` 改為 `opsx-archive`（F17）。
- E5 scope 規則：skill 只規定 scope 用 `skill`，刪除「新增或更新 skill 搭配 type `feat`」（F16）。
- E6 type 規則：加入依性質選 type；`docs` 只用於純文件；新增 skill 用 `feat`，其他 skill 變更依性質選 type、不用 `docs`（F16）。

移除：

- 無。

§3 變動：

- 移除「skill 更新一律 `feat` 與 type 規則的關係」：已明定新增 skill 用 `feat`，其他依性質。
- 移除「觸發描述的名稱寫法」：已改為 `opsx-archive`。
