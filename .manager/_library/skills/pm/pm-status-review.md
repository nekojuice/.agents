# pm-status-review 元素對照

- 分支：pm
- 對照版本：`skills/pm-status-review/SKILL.md` version 1.2，last_updated 2026-10-20T15:44:48
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/reconciliation-checklist.md`、`references/evidence-ranking.md`、`references/status-transitions.md`
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`pm-status-review` 依目前的證據，核對 PM 的耐久狀態投影（`_status.md`、`_milestones.md`）。它是由人發起的拉式盤點，不是背景監控。它唯讀讀取 `.manager` 以外的專案與交付證據（含工廠 run 根目錄的 `handoff-manager-*.md`），把細節寫在 manager run 內，提出狀態變更；只有使用者要求或確認後，才由 PM 更新正典；交接檔帶來的 library、backlog、章程訂正只列在輸出，由 PM 擬成 manager 更新稿，使用者檢查後才套用。orchestrator-pm 初次進入、且工作區已有專案狀態時，也透過它的 baseline crawl 變體產出首份 `_status.md` 與 `_milestones.md`。

流程九步：

1. 讀 `.manager/_charter.md`、`_status.md`、`_milestones.md`、`_backlog.md`、`_library/index.md`。
2. 讀工作區指示，找出實際的 repo、規格區、工廠 run、驗證產物，包括工廠 run 根目錄的 `handoff-manager-*.md`；不預設固定版面。
3. 界定範圍：整個專案、里程碑、能力、案件或關聯工廠 run。
4. 比對期望成果與觀察證據。
5. 證據蒐集量大或可分割時，才派 `pm-investigation-worker`，每個 worker 都給 run 內產物路徑。
6. 為每一項分類：unchanged、progressed、regressed、ambiguous、`completed-pm`，或明確的 `completed-human`。
7. 盤點不簡單時，在 run 內寫耐久的盤點產物。
8. 呈現擬議的狀態變更、信心、證據指標、所需的人的決定。
9. 使用者要求或確認擬議的核對後才更新正典狀態，並在同一次核對中更新 `_milestones.md`，只依證據改狀態。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 使用時機 | PM 模式已明確啟動，且使用者問完成度、缺漏、里程碑是否完成、是否仍有 bug 或缺口，或要求在工廠或人的工作之後刷新 `_status.md`；`disable-model-invocation: false`，openai 允許隱式呼叫；`extends: orchestrator-pm, pm-investigation-worker` | frontmatter；`agents/openai.yaml` |
| E2 | 角色 | 拉式盤點 | 由人發起，不做背景監控 | 開頭段 |
| E3 | 硬規則 | 讀寫邊界 | 在明確的 PM 模式內，或有明確的 PM 狀態盤點請求時執行；唯讀讀取 `.manager` 以外的專案狀態與交付證據，絕不變動；詳細盤點證據只寫在提供的 manager run 內；不經人核可，不跑會在 run 外產生持久輸出的指令 | § Contract |
| E4 | 硬規則 | 正典由 PM 更新 | 綜合之後由執行中的 PM session 更新 `.manager/_status.md`；只在使用者要求或確認擬議的核對後更新；`_milestones.md` 在同一次核對中更新，只依證據改狀態 | § Contract；§ Workflow 9 |
| E5 | 硬規則 | 不推論人工驗收 | 只有人的明確陳述可以記為 `completed-human` | § Contract；status-transitions § Human transition |
| E6 | 流程步驟 | 九步流程 | 見摘要 | § Workflow |
| E7 | 流程步驟 | 不預設版面 | 從工作區指示找出實際的 repo、規格、工廠 run、驗證產物與交接檔；只使用工作區中確實存在的來源 | § Workflow 2；reconciliation-checklist 開頭 |
| E8 | 流程步驟 | 工廠交接檔處理 | 唯讀讀取工廠 run 的 `handoff-manager-*.md`；在目前的 manager run 記錄處理方式（adopted、canonical correction、new intake item）；狀態與里程碑的訂正留在本盤點內處理；對 library、backlog、章程的訂正列在盤點輸出，由 PM 在目前 run 擬成 manager 更新稿，使用者檢查後才套用；只有新問題或候選轉 `pm-intake-triage`；不回寫工廠 run、不改交接檔 | § Contract |
| E9 | 流程步驟 | baseline crawl 變體 | 適用於 orchestrator-pm 初次進入已有專案狀態的工作區、且使用者已同意 crawl（含範圍限制）時。與一般流程的差異：步驟 1 確認正典檔不存在或剛由範本產生，範本佔位不是證據；範圍是整個專案（在使用者限制內）；依區域派唯讀 worker：程式、規格、變更文件、既有工廠 run（含其 `handoff-manager-*.md`）；每項 `from` 記為 `unknown`，只依證據給階段，證據不足者標 ambiguous；依 orchestrator-pm 進入規則，同意 crawl 即視為要求寫出首份 `_status.md` 與 `_milestones.md`；crawl 不決定憲章方向，只提供依據；產物寫在 run 內，輸出 `scope: project` 並在產物註明這是 baseline | § Baseline crawl |
| E10 | 產物格式 | 盤點清單三類 | 期望狀態：章程與已接受決策、`_milestones.md`、目前里程碑成果與排除、進行中案件的成果與預期行為、已接受規格或其他權威文件。交付證據：既有 `.factory` run 狀態與產物、規格或變更狀態、repo 歷史與實作路徑與設定、測試、build、審查、驗證、部署或 E2E 證據、人的明確驗收、工廠 run 根目錄的 `handoff-manager-<topic>.md`（可能帶有 manager 內容過時或錯誤的訂正、進度、使用者在工廠確認的決定；以 `Source run:`、`Recipient:`、`Date:` 三行判斷來源與新舊）。完整性檢查：無證據指標的狀態、缺實作或驗證的完成項、期望狀態之外的實作、未反映在 PM 狀態的工廠 run、驗收後回歸、重複或過時或矛盾的案件、舊系統或參考系統缺口未處理、沒有任何 manager run 處理紀錄的交接檔、交接檔指出但尚未反映在正典的過時 manager 內容 | reconciliation-checklist |
| E11 | 產物格式 | 輸出紀律 | 分開陳述檢視的來源、觀察、推論、信心、擬議狀態；不在潤飾過的摘要裡藏不確定性 | reconciliation-checklist § Output discipline |
| E12 | 邊界條件 | 證據分級與信心 | 證據類別：human authority（決定 `completed-human` 與專案方向）、direct observation、corroborated inference、single-source inference、report or historical note（只能當調查輸入）、factory handoff files（內容屬單一來源推論或報告；其中有日期、有引述的使用者決定可當證據與人的權威候選，但設 `completed-human` 前要向使用者確認）。信心 high、medium、low 各有判準；人的權威高於 PM 評估，但之後的技術觀察仍可開關聯 bug 或風險，兩者並存 | evidence-ranking |
| E13 | 邊界條件 | 允許的 PM 轉換 | inbox → investigating → answered 或 candidate；candidate → approved-for-factory（人明確建立）→ handed-off（自足的工廠 run 存在）→ in-delivery（工廠產物顯示交付活動）→ verifying（實作在、只剩驗證）→ completed-pm；completed-pm 可退回 investigating 或 verifying。非產品路線：candidate → in-delivery（PM 依使用者核可的異動決策開始修改受管對象）→ verifying（修改完成、等使用者審 git diff 或等效前後對照），跳過 approved-for-factory 與 handed-off | status-transitions § Allowed PM transitions |
| E14 | 邊界條件 | 人的轉換與不降級 | 只有人的明確陳述可以設為 `completed-human`；PM 不得默默降級，要開關聯案並問人是否重開 | status-transitions § Human transition |
| E15 | 邊界條件 | 非進度轉換 | deferred、rejected、answered 要附理由與來源；刻意排除的工作不使用完成狀態 | status-transitions § Non-progress transitions |
| E16 | 產物格式 | 輸出 | `PM_STATUS_REVIEW_V1`：scope（project、milestone、capability、case、factory-run）、reviewed_at、changes（item、from、to、confidence、evidence）、gaps、regressions、ambiguous、human_decisions_needed、manager_corrections（交接檔帶來的 library、backlog、章程訂正，或 none）、artifact | § Output |
| E17 | 邊界條件 | 停止 | 完成核對與被要求的正典更新後停止，不進入實作 | § Output 末段 |

## 3. 其他

- **baseline crawl 的「正典檔不存在」**：E9 的步驟 1 仍寫正典檔「不存在或剛由範本產生」。`orchestrator-pm` 已寫明先初始化 `.manager/`（初始化時即實例化範本）並建立 run，再派 crawl worker；依該順序，正典檔「不存在」的情形不會出現。本 skill 本身沒有寫這個順序。
- **啟動條件的兩種寫法**：description 寫「PM 模式已明確啟動」時使用；§ Contract 另允許「明確的 PM 狀態盤點請求」時執行。
- **轉換用詞**：`investigating -> candidate` 的條件寫「coherent product outcome」，而非產品路線的候選同樣從 candidate 開始。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/pm/pm-status-review.md`（前版 version 1.1）：

- 修改 E6 九步流程（前版 E6）：步驟 2 加入找出工廠 run 根目錄的 `handoff-manager-*.md`。
- 修改 E7 不預設版面（前版 E7）：探索對象加入交接檔。
- 新增 E8 工廠交接檔處理（處理方式三類、訂正留在本盤點、只有新問題或候選轉分流、不回寫）。
- 新增 E9 baseline crawl 變體（前版只在摘要提到，沒有規則段）。
- 修改 E10 盤點清單三類（前版 E8）：交付證據加入 `handoff-manager-<topic>.md` 與三行標頭；完整性檢查加入兩項交接檔檢查。
- 修改 E12 證據分級（前版 E10「證據五級」）：五類變六類，加入 factory handoff files。
- 修改 E13 允許的 PM 轉換（前版 E11）：加入非產品路線的兩個轉換與跳過的階段。
- 移除：無。

第二輪（2026-10-20，對照本稿前一版，即 last_updated 2026-10-20T13:32:50 的對照；依 `changes/25-round2-fixes.md`）：

- 修改 E8 工廠交接檔處理：本盤點內只處理狀態與里程碑的訂正；library、backlog、章程的訂正列在輸出，由 PM 擬成 manager 更新稿，使用者檢查後才套用（P8）；摘要同步。
- 修改 E16 輸出：`PM_STATUS_REVIEW_V1` 加入 `manager_corrections` 欄位。
- §3 移除一項已不存在的問題：正典訂正的寫入範圍。修改一項：baseline crawl 與 run 的先後，`orchestrator-pm` 已寫明順序，剩下本 skill 步驟 1 仍寫「正典檔不存在」。
- 新增元素：無。移除元素：無。元素數維持 17。
