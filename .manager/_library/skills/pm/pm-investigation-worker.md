# pm-investigation-worker 元素對照

- 分支：pm
- 對照版本：`skills/pm-investigation-worker/SKILL.md` version 1.1，last_updated 2026-10-20T15:52:52
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/isolation-rules.md`、`references/investigation-modes.md`、`references/evidence-reporting.md`
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`pm-investigation-worker` 是 orchestrator-pm 派出的唯讀調查 worker，作用範圍限定在單一 manager run。一次只處理一個有界任務：調查問題、疑似 bug、實作涵蓋度、舊系統行為、專案缺口，或拆解一份文件或規則集；把證據寫進 PM 指定的 run 內一個或多個產物路徑，回報路徑與一行摘要。它不扮演 PM、工廠指揮者或實作者，也不修改被拆解的對象。

流程：

1. 檢查四項必要輸入，缺任一項或產物路徑落在 `run_dir` 外，就拒絕或回 `needs-input`；選用的 `constraints` 用來收緊限制，唯一的放寬方式是 PM 寫入其中、註明核可來源的使用者核可例外。
2. 使用工具前先讀隔離規則。
3. 從六種調查模式中選最小且適用的一種主模式。
4. 依任務類型執行：疑似 bug 五步、涵蓋度／進度四步，或文件／規則拆解五步。
5. 依證據回報規則寫出產物：預設 `PM_INVESTIGATION_RESULT_V1`，任務指定其他格式時照指定格式。
6. 回報產物路徑與一行摘要，不更新其他任何檔案。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 明確派遣 | 只在被明確派遣、且附帶既有 manager run、一個有界任務、讀取範圍、run 內一或多個確切產物路徑時使用；`disable-model-invocation: false`，openai 允許隱式呼叫；`extends: orchestrator-pm` | frontmatter；`agents/openai.yaml` |
| E2 | 角色 | 不越位 | 不扮演 PM、工廠指揮者或實作者 | 開頭段 |
| E3 | 邊界條件 | 四項必要輸入 | `run_dir`（一個既有的 `.manager/_runs/<run>/`）、`assignment`（一個有界問題）、`allowed_reads`（明確路徑或狹窄的探索範圍）、`artifact`（PM 指定的 `run_dir` 內一或多個唯一路徑；任務未指定子目錄時用 `findings/`）；缺任一項，或任一路徑落在 `run_dir` 外，就拒絕或回 `needs-input` | § Required input |
| E4 | 邊界條件 | 選用輸入 `constraints` | PM 給的額外限制，例如工作區章程的內容規則；用來收緊隔離規則。唯一可放寬的方式是 PM 寫入其中、註明核可來源的使用者核可例外：worker 只照例外寫明的範圍執行，其他放寬一律視為不存在；例外永不允許在 `run_dir` 外寫入 | § Required input；isolation-rules 末段 |
| E5 | 硬規則 | 讀寫隔離 | 只讀 `allowed_reads` 內必要的內容；提示允許時可讀指派的 manager run 狀態；只寫或取代被指定的產物路徑，可在 `run_dir` 內建立其缺少的上層目錄；不改 `.manager/_*.md`、`.manager/_library/**`、其他 run、產品 repo、專案規格、資料庫、外部系統、`.factory/**` | § Isolation rules；isolation-rules § Allowed |
| E6 | 硬規則 | 禁止的操作 | 不跑會在 `run_dir` 外產生持久輸出的指令（build、test、formatter、套件管理等，除非人先給特定例外）；不安裝依賴、不啟動會變動狀態的服務；不建立 worktree、branch、commit、工廠 run、manager 案件或 library 條目；不更新 manager 根狀態或 backlog；不巢狀派遣 | § Isolation rules；isolation-rules § Forbidden |
| E7 | 邊界條件 | 不擴大任務 | 不擴大任務範圍；相鄰的發現列為 out of scope | § Isolation rules；investigation-modes 末段 |
| E8 | 人閘 | 隔離阻擋時回報 | 必要的診斷會違反隔離時，回 `needs-input`，寫明確切操作與必要理由 | isolation-rules 末段 |
| E9 | 流程步驟 | 六種調查模式 | question lookup（答案、來源、範圍、限定）；suspected bug trace（預期、觀察、執行路徑、可能原因、矛盾、缺漏的重現證據）；coverage audit（單一能力對應規格、實作、驗證、工廠、人工驗收證據）；legacy comparison（單一舊行為或資料規則對照，不預設全部保留）；gap search（在一個界定區域找缺漏、矛盾或未驗證成果，只回報候選、不建正典案件）；document or rule decomposition（把一份文件或規則集拆成摘要、元素、衝突、缺口，不判定交付完成、不建案、不改被拆解對象）。選最小且適用的模式，每個任務一種主模式 | § Investigation；investigation-modes |
| E10 | 流程步驟 | 證據偏好 | 優先直接的一手證據：原始碼、已接受規格、現行設定、既有驗證報告、使用者提供的 log、範圍內的舊系統產物；拆解時以被拆解對象本身的文字為證據 | § Investigation |
| E11 | 流程步驟 | 疑似 bug 五步 | 寫明預期行為來源 → 寫明觀察或回報的行為 → 唯讀追蹤相關路徑 → 區分已確認原因、可能原因、缺漏證據 → 沒有在不違反隔離的情況下實際重現，就不宣稱重現 | § Investigation |
| E12 | 流程步驟 | 涵蓋度或進度四步 | 確認期望能力 → 找出實作與驗證證據 → 找出缺口與矛盾 → 回報證據，不做正典完成判定 | § Investigation |
| E13 | 流程步驟 | 文件或規則拆解五步 | 寫明被拆解對象與其版本 → 逐一列出元素並註明出自哪一節 → 另外記錄內部衝突、缺口、模糊處 → 任務附有訴求清單時逐項對照元素並標出缺口 → 只給修改方向，不改寫或編輯被拆解對象 | § Investigation |
| E14 | 產物格式 | 證據四分 | 每個重要主張分成：觀察、推論、信心（low／medium／high）、限定條件；盡量寫直接路徑與符號；不貼大段原文 | evidence-reporting |
| E15 | 產物格式 | 五種狀態 | answered（權威證據解答）、confirmed（證據直接支持疑似狀況或原因）、suspected（支持假設但未證明）、not-reproduced（允許的證據未能重現，不代表無效）、needs-input（缺範圍、權限、環境，或必要操作被隔離阻擋） | evidence-reporting |
| E16 | 產物格式 | 產物格式 | 預設 `PM_INVESTIGATION_RESULT_V1`：worker、assignment、status、summary、confidence、evidence、reasoning、unknowns、out_of_scope、candidate（每個候選附 `route`，值為 `factory` 或 `non-product`）。任務指定其他格式（例如 PM 分析範本）時照指定格式，但仍須帶 `status` 與 `confidence`，並把觀察與推論分開 | § Artifact |
| E17 | 邊界條件 | 候選只是建議 | 候選不論屬工廠或非產品路線，都只是給 PM 的建議，不是核可，也不是實作計畫 | evidence-reporting 末段 |
| E18 | 產物格式 | 回報 | 回報產物路徑（一或多個）與一行摘要給 PM；不更新其他檔案 | § Artifact 末段 |

## 3. 其他

- **build／test 例外與「例外不得在 run 外寫入」並存**：isolation-rules § Forbidden 第三項寫 build、test、formatter、套件管理等會在 `run_dir` 外產生檔案的工具「除非人先給特定例外」；同檔末段寫例外永不允許在 `run_dir` 外寫入。這類工具產生的 run 外檔案是否算寫入、第三項的例外是否仍可能成立，沒有寫明。SKILL.md § Isolation rules 的「不跑在 run 外產生持久輸出的指令」沒有附例外。
- **`constraints` 的地位**：本 skill 把 `constraints` 列為選用；`orchestrator-pm` 把它列為每個 worker prompt 都要提供的欄位。
- **拆解模式的兩處描述**：investigation-modes 的拆解模式產出摘要、元素、衝突、缺口；SKILL.md 的拆解五步另有「對照訴求清單」與「只給修改方向」，參考檔沒有這兩項。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/pm/pm-investigation-worker.md`（前版 version 1.0）：

- 修改 E1 明確派遣（前版 E1）：一個確切產物改為 run 內一或多個；description 加入文件或規則拆解，且不改被拆解對象。
- 修改 E3 四項必要輸入（前版 E3）：`artifact` 由 `run_dir/findings/` 下一個唯一路徑，改為 `run_dir` 內一或多個 PM 指定路徑，未指定子目錄用 `findings/`，路徑落在 run 外回 `needs-input`。
- 新增 E4 選用輸入 `constraints`（只能收緊）。
- 修改 E5 讀寫隔離（前版 E4）：只寫一個產物改為指定的一或多個路徑，可在 `run_dir` 內建立缺少的上層目錄。
- 修改 E9 調查模式（前版 E8）：五種變六種，加入 document or rule decomposition。
- 修改 E10 證據偏好（前版 E9）：加入被拆解對象本身的文字。
- 新增 E13 文件或規則拆解五步。
- 修改 E16 產物格式（前版 E14「結果信封」）：`PM_INVESTIGATION_RESULT_V1` 改為預設，可依任務改用指定格式，但仍須帶 `status`、`confidence` 並分開觀察與推論。
- 修改 E18 回報（前版 E16）：回報一或多個產物路徑。
- 移除：無。

第二輪（2026-10-20，對照本稿前一版，即 last_updated 2026-10-20T13:32:50 的對照；依 `changes/25-round2-fixes.md`）：

- 修改 E4 選用輸入 `constraints`：由「只能收緊」改為可帶 PM 寫入、註明核可來源的使用者核可例外，worker 照寫明範圍執行；例外永不允許在 `run_dir` 外寫入（P5 與複查修正）；摘要步驟 1 同步。
- 修改 E16 產物格式：`factory_candidate` 改為 `candidate`，加 `route: factory | non-product`（P10）。
- 修改 E17 候選只是建議：涵蓋工廠與非產品兩種路線的候選。
- §3 移除兩項已不存在的問題：人給的例外如何送達、候選欄位只有工廠。新增一項：isolation-rules 的 build／test 例外與「例外不得在 run 外寫入」並存。
- 新增元素：無。移除元素：無。元素數維持 18。
