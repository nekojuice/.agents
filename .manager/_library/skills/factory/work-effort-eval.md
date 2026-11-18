# work-effort-eval 元素對照

- 分支：factory
- 對照版本：`skills/work-effort-eval/SKILL.md` version 1.0，last_updated 2026-11-18T15:40:43
- 讀過的檔案：`skills/work-effort-eval/SKILL.md`、`skills/work-effort-eval/agents/openai.yaml`；唯讀核對引用方 `orchestrator-factory`（1.16）§ Work effort、§ Manager handoff、§ File conventions、§ Automation 5、§7，`orchestrator-pm`（1.8）§ Required references、§ Maintain durable state、`references/workspace-contract.md`、`references/run-lifecycle.md`、`assets/effort-ledger.template.md`，以及 `skill-feedback-notes`（1.1）
- 狀態：已檢查，2026-11-18 移入 manager 正式文件

## 1. 摘要

`work-effort-eval` 把「多難、花多久」量化成可跨 run 比較的參考指標，評估整段工作流程（決策、方法、skill、環境、任務），skill 品質只是其中一項。分兩部分：orch 在工作中隨手記錄 `_effort.md`，收尾時派新的 eval worker 寫 `eval-effort.md`，orch 覆核。

流程：建 run 時開始記錄（Sessions、Checkpoints、Events）→ 收尾必做評估，派出前告知使用者 → eval 從檔案與 git 數訊號、補找漏記、依錨點分級、歸因 → orch 覆核並寫回最終分級與出口建議、告知報告路徑 → 方法層發現寫進 skill 筆記隨同一份交接送出；factory 有 `.manager` 時另寫評估交接，manager 擬稿進台帳。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 使用者與排除 | factory 或 manager 的 orch 使用；也可單獨評估一個 run；worker 只在被派為 eval 時使用；排除機器學習模型評估與推理強度設定 | frontmatter description |
| E2 | 觸發條件 | 隱式呼叫設定 | `disable-model-invocation: false`；`agents/openai.yaml` 為 `allow_implicit_invocation: true` | frontmatter；`agents/openai.yaml` |
| E3 | 邊界條件 | 定位 | 可選的評估 skill，引用它的 orch 自行啟用；使用者指示不用時記入狀態檔（factory `_status.md`、manager `_run.md`）並停止；指標是參考不是目標；不是稽核日誌 | Position；開頭 |
| E4 | 邊界條件 | 不做事前估計 | 工作前不估難度與時長：初期估計差異大，估錯給使用者錯誤的信心 | Position |
| E5 | 流程步驟 | 單位與獨立發動 | 以 run 為評估單位；可隨時獨立發動，發動的 agent 擔任兩部分的 orch；有 run 用現有 run，否則在現有工作區建 run 資料夾與狀態檔、不進入該角色模式與人閘；兩者都沒有時放使用者指定的資料夾、不記基準 | Unit and start |
| E6 | 判斷規則 | 缺資料 | 中途或事後發動時，抓不到的訊號標 `not recorded`，不當成零；分級時列出、不計入 | Unit and start；Anchors |
| E7 | 判斷規則 | 三軸 | 量（自動工作時間、token、檔案數、change 數，只作參考）、agent 負擔、使用者負擔，不互相換算；次數為整個 run 加總；E2E `run-error` 重派另計 | Three axes |
| E8 | 產物格式 | `_effort.md` | run 根目錄，以編輯工具原地更新；段落：Run、Sessions（每個 orch session 一列，含模型、平台、型號）、Checkpoints（時間、檢查點、距上一點的來回次數）、Events（時間、類型、來源、說明）、Evaluation（收尾後填） | Part 1 |
| E9 | 流程步驟 | 檢查點戳記 | OS 本地時間含時區；討論開始、收斂、行動開始、各人閘、派工與回報、收尾；晚於討論開始才記錄時，知道就補，否則標 `not recorded` | Part 1 Checkpoints |
| E10 | 判斷規則 | orch 記的事件 | 只記 orch 看得到的：使用者指正、agent 擅自做錯、推翻推薦、流程提醒、使用者補資訊、換手與 context 壓縮；有明確來源 skill 或角色就標上；主線優先、當下寫、不中斷工作、不抄檔案已有的訊號 | Part 1 Events |
| E11 | 判斷規則 | skill 問題雙記 | 使用者回饋指向 skill 時，照常依 `skill-feedback-notes` 記錄，並在 `_effort.md` 加一筆事件，兩者不互相取代 | Part 1 |
| E12 | 判斷規則 | 時間計算 | 使用者互動時間：互動區段內相鄰檢查點間隔不超過閒置門檻（預設 30 分鐘）全計，超過時計 `min(間隔, 來回次數 × 門檻)`，沒有來回計 0；agent 工作時間：派工到回報、自動化施工段、orch 不等使用者的連續工作區段 | Part 1 Time |
| E13 | 流程步驟 | 收尾評估時機 | 啟用時收尾必做、不設人閘；在處理 skill 筆記與使用者檢查 staging 之前執行 | Part 2 |
| E14 | 流程步驟 | 收尾三步 | 1 告知使用者；2 派新子代理為 eval worker；3 覆核、寫回最終分級與出口建議、告知報告路徑與建議出口 | Part 2 |
| E15 | 產物格式 | eval 派工格式 | `[<orchestrator> / eval]`；`role: eval`、`run_dir`、`skills: work-effort-eval`、`window`（首個檢查點到收尾）與 `fixed_point`、`return: eval-effort.md`、`constraint`（只寫 `eval-effort.md`、不派工、不改 `_effort.md` 或其他檔） | Part 2 第 2 步 |
| E16 | 邊界條件 | eval worker 範圍 | 只做計數、分級、歸因、報告；不維護 `_effort.md`、不派工、不寫交接；記錄自己的模型、平台、型號 | Part 2 |
| E17 | 判斷規則 | 檔案訊號來源 | factory：審查回應、apply 結果的 `self_fix_rounds_used`（跨 change 加總）、`check-*-code-review.md`、`_status.md` 修訂輪、閘事件與 Decisions needed、`_notes.md` 的 Pending decisions、`e2e-review/` 輪次、`_needs-input.md`、`_review-checklist.md` 剩給人的項目、commit 時間；manager：需求對照回覆輪與 Conflicts、To confirm 列、`reviews/_triage*.md`、異動決策、commit 時間；漏記的從檔案補找 | Part 2 |
| E18 | 產物格式 | `eval-effort.md` | 檔頭：run、日期、任務類型、eval 模型與平台型號、使用者匿名代號或熟練度標記（有記時）；各軸次數附來源、各軸分級附決定訊號、未記錄訊號、歸因（熱點、層級、證據、建議出口）、本質難度輪廓 | Report |
| E19 | 判斷規則 | 錨點分級 | 有錨點的訊號依整個 run 加總分低中高；一軸取其訊號中最高的分級並指名決定訊號；沒有錨點的訊號只報次數；錨點表 13 列涵蓋量、agent 負擔、使用者負擔 | Anchors |
| E20 | 判斷規則 | 歸因步驟 | 依事件歸因：找熱點 → 往上追溯 → 環境與工具歸環境層，其餘以反事實判斷決策層、方法層或本質難度 → 可查未查查證（當時查得到歸 agent 行為，skill 未要求查時歸方法層；查不到歸文件缺口）→ 本質難度輪廓（不確定性、回饋週期、驗證困難、領域知識、資源）→ 任務類型標記；單一 run 只支撐假設，跨 run 的規律才支撐修改 | Attribution |
| E21 | 產物格式 | 出口表 | 評估不改任何東西：方法層 → `skill-feedback-notes`；決策層或文件前提 → manager 交接與決策文件修訂；文件缺口 → manager 交接與文件修訂（skill 的缺口走 skill 筆記）；agent 行為 → 報告與基準，跨 run 重複時走 skill 筆記；環境與工具 → issue backlog；本質難度 → 該類任務基準 | Outlets |
| E22 | 流程步驟 | 方法層發現併入交接 | 覆核後把方法層發現與校正項目寫成 run 的 skill 筆記條目，隨同一份收尾交接送出 | Outlets |
| E23 | 人閘 | orch 覆核 | 比照其他 review，可忽略、回絕或修改，多數尊重 eval；改分級時在 `_effort.md` 保留 eval 與 orch 兩個分級並附一行理由 | Orchestrator review |
| E24 | 流程步驟 | 交回 manager | factory 有 `.manager` 時另寫 `handoff-manager-<topic>-effort.md`，沒有時評估止於報告；自動化時整批收尾為每個 run 各評估一次、各一份報告與交接；manager 擬 `staging/_effort-ledger.md` 為整份台帳加本 run 一列，台帳不存在時由 `orchestrator-pm` 的範本建立；工廠評估交接同樣擬稿進台帳；框架外的單次執行不記基準 | Hand back to the manager |
| E25 | 邊界條件 | 抽象化與匿名 | 跨到 skill repo 時比照 `skill-feedback-notes` 抽象化，專案內容留在 run；跨使用者比較只用匿名代號或熟練度標記 | Hand back to the manager |
| E26 | 流程步驟 | 校正 | 錨點、閒置門檻與評估指示都是校正對象；材料為 orch 的分級調整與使用者對評估的指正，經 `skill-feedback-notes` 交回 | Calibration |

## 3. 其他

- **引用方**：`orchestrator-factory`（§ Work effort、§ Manager handoff、§ File conventions、§ Automation 5、§7 第 5 步）與 `orchestrator-pm`（§ Required references、§ Maintain durable state、workspace-contract、run-lifecycle § Conclude 第 1 步、台帳範本）。
- **錨點與門檻是初版**：依使用者定案需經試用多輪校正。
- **台帳範本放在 orchestrator-pm**：本 skill 以名稱引用 `orchestrator-pm` 的 `assets/effort-ledger.template.md`。

## 4. 與前版差異

- 1.0（2026-11-18）：新增 skill，首次拆解（來源：manager run 2026-11-18-skill-expression-and-effort `requirements-comparison-effort-metrics.md` §6–§8、`changes/01`；審查分類 `reviews/_triage-effort.md`）。
