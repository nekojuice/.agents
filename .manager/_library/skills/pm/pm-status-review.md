# pm-status-review 元素對照

- 分支：pm
- 對照版本：`skills/pm-status-review/SKILL.md` version 1.4，last_updated 2026-11-02T13:38:09
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/reconciliation-checklist.md`、`references/evidence-ranking.md`、`references/status-transitions.md`；交叉引用核對（唯讀）：`orchestrator-pm` 的 `references/non-product-route.md` § 4、§ 6、§ 7
- 狀態：已檢查，2026-11-02 移入 manager 正式文件

## 1. 摘要

`pm-status-review` 依目前的證據，核對 PM 的耐久狀態投影（`_status.md`、`_milestones.md`）。它是由人或工廠的 peer 通知發起的拉式盤點，不是背景監控；description 也列出在人指示或 peer 通知下收到工廠交接時使用，狀態更新一律先擬稿到 `staging/`。它唯讀讀取 `.manager` 以外的專案與交付證據（含工廠 run 根目錄的 `handoff-manager-*.md`，以及交接缺漏時工廠 run 的 `_status.md` 與 git 歷史），把細節寫在 manager run 內，提出狀態變更；所有正典更新（含交接檔帶來的 status、milestones、library、backlog、章程訂正）都擬稿到 run 的 `staging/`，使用者檢查後才套用，使用者主動要求的盤點也一樣。工廠交接檔可能多寫，收件時要過濾；規格內容由專案的規格系統管理時只記指標。orchestrator-pm 初次進入、且工作區已有專案狀態時，也透過它的 baseline crawl 變體產出首份 `_status.md` 與 `_milestones.md`。

流程九步：

1. 讀 `.manager/_charter.md`、`_status.md`、`_milestones.md`、`_backlog.md`、`_library/index.md`。
2. 讀工作區指示，找出實際的 repo、規格區、工廠 run、驗證產物，包括工廠 run 根目錄的 `handoff-manager-*.md`；不預設固定版面；不假設工廠回報了一切，工廠 run 沒有交接檔或交接不完整時，以它的 `_status.md` 與 git 歷史為證據。
3. 界定範圍：整個專案、里程碑、能力、案件或關聯工廠 run。
4. 比對期望成果與觀察證據。
5. 證據蒐集量大或可分割時，才派 `pm-investigation-worker`，每個 worker 都給 run 內產物路徑。
6. 為每一項分類：unchanged、progressed、regressed、ambiguous、`completed-pm`，或明確的 `completed-human`。
7. 盤點不簡單時，在 run 內寫耐久的盤點產物。
8. 呈現擬議的狀態變更、信心、證據指標、所需的人的決定。
9. 把 `_status.md` 與 `_milestones.md` 的更新擬稿到 `staging/`，里程碑狀態只依證據改；使用者檢查草稿後才套用，使用者要求的盤點也一樣。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 使用時機 | PM 模式已明確啟動，且使用者問完成度、缺漏、里程碑是否完成、是否仍有 bug 或缺口，或要求在工廠或人的工作之後更新專案狀態；以及工廠的交接在人指示或 peer 通知下送達時。description 寫明狀態更新先擬稿到 `staging/`。`disable-model-invocation: false`，openai 允許隱式呼叫；`extends: orchestrator-pm, pm-investigation-worker` | frontmatter；`agents/openai.yaml` |
| E2 | 角色 | 拉式盤點 | 由人或工廠的 peer 通知發起，不做背景監控 | 開頭段 |
| E3 | 硬規則 | 讀寫邊界 | 在明確的 PM 模式內，或有明確的 PM 狀態盤點請求時執行；唯讀讀取 `.manager` 以外的專案狀態與交付證據，絕不變動；詳細盤點證據只寫在提供的 manager run 內；不經人核可，不跑會在 run 外產生持久輸出的指令 | § Contract |
| E4 | 硬規則 | 正典更新先擬稿 | 綜合之後由執行中的 PM session 把正典更新擬稿到 run 的 `staging/`，使用者檢查草稿後才套用；`_status.md` 與 `_milestones.md` 在同一次核對中擬稿，里程碑狀態只依證據改；使用者要求的盤點也先擬稿 | § Contract；§ Workflow 9 |
| E5 | 硬規則 | 不推論人工驗收 | 只有人的明確陳述可以記為 `completed-human` | § Contract；status-transitions § Human transition |
| E6 | 流程步驟 | 九步流程 | 見摘要 | § Workflow |
| E7 | 流程步驟 | 不預設版面、不假設完整回報 | 從工作區指示找出實際的 repo、規格、工廠 run、驗證產物與交接檔；只使用工作區中確實存在的來源。不假設工廠回報了一切：工廠 run 沒有交接檔或交接不完整時，以它的 `_status.md` 與 git 歷史為證據 | § Workflow 2；reconciliation-checklist 開頭 |
| E8 | 流程步驟 | 工廠交接檔處理 | 在人指示或 peer 通知時唯讀讀取工廠 run 的 `handoff-manager-*.md`；在目前的 manager run 記錄處理方式（adopted、canonical correction、new intake item）；由此產生的每項訂正（status、milestones、library、backlog、章程）都擬稿到 `staging/`；只有新問題或候選轉 `pm-intake-triage`；不回寫工廠 run、不改交接檔 | § Contract |
| E9 | 流程步驟 | 交接檔過濾 | 工廠可能寫得比 manager 需要的多，要過濾而不是整份採納。保留：影響方向或範圍的決定、有證據的進度、新候選與範圍外發現、阻擋、對過時 `.manager` 內容的訂正。規格內容由專案的規格系統管理時（例如 opsx），只記指向它的指標；捨棄實作細節 | § Contract |
| E10 | 流程步驟 | baseline crawl 變體 | 適用於 orchestrator-pm 初次進入已有專案狀態的工作區、且使用者已同意 crawl（含範圍限制）時。與一般流程的差異：步驟 1 確認正典檔剛由範本產生，範本佔位不是證據；範圍是整個專案（在使用者限制內）；依區域派唯讀 worker：程式、規格、變更文件、既有工廠 run（含其 `handoff-manager-*.md`）；每項 `from` 記為 `unknown`，只依證據給階段，證據不足者標 ambiguous；依 orchestrator-pm 進入規則，同意 crawl 即視為要求產出首份 `_status.md` 與 `_milestones.md`，先擬稿到 `staging/`，使用者檢查後才寫入；crawl 不決定憲章方向，只提供依據；產物寫在 run 內，輸出 `scope: project` 並在產物註明這是 baseline | § Baseline crawl |
| E11 | 產物格式 | 盤點清單三類 | 期望狀態：章程與已接受決策、`_milestones.md`、目前里程碑成果與排除、進行中案件的成果與預期行為、已接受規格或其他權威文件。交付證據：既有 `.factory` run 狀態與產物、規格或變更狀態（專案有使用時）、repo 歷史與實作路徑與設定、測試、build、審查、驗證、部署或 E2E 證據、人的明確驗收、工廠 run 根目錄的 `handoff-manager-<topic>.md`（可能帶有 manager 內容過時或錯誤的訂正、進度、使用者在工廠確認的決定；以 `Source run:`、`Recipient:`、`Date:` 三行判斷來源與新舊）。完整性檢查：無證據指標的狀態、缺實作或驗證的完成項、期望狀態之外的實作、未反映在 PM 狀態的工廠 run、驗收後回歸、重複或過時或矛盾的案件、舊系統或參考系統缺口未處理、沒有任何 manager run 處理紀錄的交接檔、交接檔指出但尚未反映在正典的過時 manager 內容 | reconciliation-checklist |
| E12 | 產物格式 | 輸出紀律 | 分開陳述檢視的來源、觀察、推論、信心、擬議狀態；不在潤飾過的摘要裡藏不確定性 | reconciliation-checklist § Output discipline |
| E13 | 邊界條件 | 證據分級與信心 | 證據類別：human authority（決定 `completed-human` 與專案方向）、direct observation、corroborated inference、single-source inference、report or historical note（只能當調查輸入）、factory handoff files（內容屬單一來源推論或報告；其中有日期、有引述的使用者決定可當證據與人的權威候選，但設 `completed-human` 前要向使用者確認）。信心 high、medium、low 各有判準；人的權威高於 PM 評估，但之後的技術觀察仍可開關聯 bug 或風險，兩者並存 | evidence-ranking |
| E14 | 邊界條件 | 允許的 PM 轉換 | inbox → investigating → answered 或 candidate；candidate → approved-for-factory（人明確建立）→ handed-off（自足的工廠 run 存在）→ in-delivery（工廠產物顯示交付活動）→ verifying（實作在、只剩驗證）→ completed-pm；completed-pm 可退回 investigating 或 verifying。非產品路線：candidate → in-delivery（PM 依使用者核可的異動決策開始修改受管對象）→ verifying（修改完成、等使用者審 git diff 或等效前後對照），跳過 approved-for-factory 與 handed-off | status-transitions § Allowed PM transitions |
| E15 | 邊界條件 | 人的轉換與不降級 | 只有人的明確陳述可以設為 `completed-human`；PM 不得默默降級，要開關聯案並問人是否重開 | status-transitions § Human transition |
| E16 | 邊界條件 | 非進度轉換 | deferred、rejected、answered 要附理由與來源；刻意排除的工作不使用完成狀態 | status-transitions § Non-progress transitions |
| E17 | 產物格式 | 輸出 | `PM_STATUS_REVIEW_V1`：scope（project、milestone、capability、case、factory-run）、reviewed_at、changes（item、from、to、confidence、evidence）、gaps、regressions、ambiguous、human_decisions_needed、manager_corrections（交接檔帶來的 library、backlog、章程訂正，或 none）、artifact、staging（上列 changes 與 manager_corrections 的草稿在 run 內的路徑，或 none） | § Output |
| E18 | 邊界條件 | 停止 | 完成核對與其 `staging/` 草稿後停止，或在使用者檢查草稿後套用完畢再停止；不進入實作 | § Output 末段 |

## 3. 其他

- **啟動條件的寫法**：description 只寫「PM 模式已明確啟動」時使用；§ Contract 另允許「明確的 PM 狀態盤點請求」時執行，description 沒有反映這個條件。peer 通知與擬稿到 `staging/` 已寫進 description。
- **轉換用詞**：`investigating -> candidate` 的條件寫「coherent product outcome」，而非產品路線的候選同樣從 candidate 開始。

## 4. 與前版差異

對照前版對照（version 1.3，last_updated 2026-11-02T12:17:40）：

- 修改 E1 使用時機：「刷新 `_status.md`」改為「更新專案狀態」；加入工廠交接在人指示或 peer 通知下送達時使用；description 寫明狀態更新先擬稿到 `staging/`。
- 修改 E9 交接檔過濾：「規格內容只記 opsx change id」改為「規格內容由專案的規格系統管理時（例如 opsx），只記指標」。
- 修改 E17 輸出：`staging` 欄寫明指向 changes 與 manager_corrections 的草稿位置。
- §3 移除兩項已修正的問題：`manager_corrections` 與 `staging` 的分工、過濾規則假設 opsx。「啟動條件」一項縮減為只剩 Contract 的盤點請求條件未反映在 description。
- 移除元素：無。元素數維持 18。
