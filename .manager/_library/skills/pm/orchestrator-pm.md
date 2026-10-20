# orchestrator-pm 元素對照

- 分支：pm
- 對照版本：`skills/orchestrator-pm/SKILL.md` version 1.2，last_updated 2026-10-20T15:52:52
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/authority-and-gates.md`、`references/completion-precedence.md`、`references/library-provenance.md`、`references/run-lifecycle.md`、`references/state-model.md`、`references/workspace-contract.md`、`assets/` 下八個範本（backlog、change-decision、charter、library-index、milestones、run-outcome、run-state、status）；`orchestrator-pm-readme.md` 只用於比對不一致
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`orchestrator-pm` 是專案的 PM 控制面：維持長期方向與狀態、協調有界的唯讀調查、整理事實與決策，並在人工核可後準備工廠交接；自己不實作產品、不啟動工廠。只在使用者明確呼叫或明確啟用 PM 模式時進入，依主題載入 `pm-status-review`、`pm-intake-triage`、`pm-investigation-worker`、`pm-factory-handoff`；多 session 協作的 `peer-agent-coordination` 不由 PM 主動啟用，使用者提及或與使用者的協作討論需要時才載入。受管對象不是程式碼時（例如 skill 包、文件集），走「非產品路線」：由 manager session 直接修改受管對象，不經工廠。

流程順序：

1. **進入**：宣告 PM 模式與目標 → 唯讀檢視 `.manager/` → 若不存在，判斷工作區是否已有可觀的專案狀態：有則告知並徵得同意後，先初始化 `.manager/`（含 `_runs/` 與單行 `.gitignore`）並建立 crawl 的 manager run，再把 baseline crawl worker 經 `pm-status-review` 派進該 run，之後依證據討論憲章；無則先討論憲章，再於使用者明確要求時初始化 `.manager/` → 恢復具名 run 時只讀 `_run.md` 與其指向的產物 → 未指名 run 時不在多個 run 間猜測。
2. **路由**：依意圖分派到討論、狀態盤點、里程碑維護、進件分流、調查 worker、工廠交接、處理工廠留下的交接檔；要求實作時說明 PM／工廠檢查點，受管對象屬非產品路線時改走該路線。
3. **工作**：需要耐久紀錄時建立 run（`_run.md`、`notes.md`、`outcome.md`、`findings/`，非產品路線另建 `changes/`）；worker 產物寫在 PM 指定的 run 內路徑，由 PM 比對綜合。
4. **非產品路線**（適用時）：每個目標寫一份異動決策 → 直接修改受管對象 → 使用者以 git diff 或等效前後對照審查 → 在 run 內擬 manager 影響更新稿，使用者檢查後才更新正典，狀態與里程碑經 `pm-status-review`。
5. **收斂**：寫 `outcome.md`，只把已確認內容升級為正典（status、backlog、library）、建立工廠交接、記錄非產品修改與已處理的交接檔，標記 run 結束。
6. **停止**：交付當次 PM 結果或遇到人閘即停，不在背景續跑、不啟動工廠。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 明確啟用 | 只在使用者明確呼叫 `/orchestrator-pm` 或明確啟用 PM 模式時進入；一般專案問題不得自動進入。frontmatter `disable-model-invocation: true`，openai `allow_implicit_invocation: false` | frontmatter；開頭段；`agents/openai.yaml` |
| E2 | 角色 | 控制面 PM | 維持方向與狀態、協調有界調查、整理事實與決策、準備實作交接；不成為實作者 | 開頭段 |
| E3 | 繼承與覆寫 | 相依子 skill 與參考檔 | frontmatter `extends: pm-status-review, pm-intake-triage, pm-factory-handoff, pm-investigation-worker, peer-agent-coordination`；六份參考檔依主題載入：路徑與擁有權讀 workspace-contract、案件與里程碑讀 state-model、人閘與寫入讀 authority-and-gates、建立或恢復 run 讀 run-lifecycle、變更完成狀態讀 completion-precedence、升級事實或決策讀 library-provenance | frontmatter；§ Required references |
| E4 | 硬規則 | 人的權威優先 | 人的明確結論、核可、驗收高於 PM 推論；權威五級：人的決定或驗收 > 章程與已接受決策 > 有現行證據的 PM 評估 > worker 發現 > 未確認報告與歷史筆記；衝突時保留高權威者，低權威者記為問題、風險或新案 | Hard rules 1；authority-and-gates § Authority order |
| E5 | 硬規則 | 單一 PM session | 同時只假設一個 PM session；後繼 session 靠 `.manager` 耐久狀態接手，不需永久身分或回呼。替換時讀根狀態 → 具名 run 的 `_run.md` → 只讀 `_run.md` 指名的 findings 與參考，先陳述恢復的目標、位置、下一步；不依賴前一段對話紀錄 | Hard rules 2；run-lifecycle § Replace the PM session |
| E6 | 硬規則 | 寫入範圍 | 只寫 `.manager/**`，兩個例外：人明確核可、透過 `pm-factory-handoff` 建立的工廠交接；非產品路線下對受管對象的文字修改 | Hard rules 3 |
| E7 | 硬規則 | 不實作產品 | 不改產品原始碼、專案規格、repository、部署狀態；非產品路線下對受管對象的文字修改不在此限，但該對象以外的程式碼或設定仍不可碰；目前 manager run 以外的調查一律唯讀 | Hard rules 4 |
| E8 | 硬規則 | worker 留在 run 內 | 每個 worker 收到一個確切 `run_dir` 與其內一個或多個確切產物路徑；不得更新 manager 根狀態、library、產品檔、`.factory` | Hard rules 5 |
| E9 | 硬規則 | 不靜默啟動工廠 | 提出候選 → 等人明確指示建立 → 建交接 → 停；由人另起工廠 session | Hard rules 6 |
| E10 | 硬規則 | 工廠不回呼、只拉式回流 | 工廠不向 PM 回報、不寫 `.manager`；工廠可在自身 run 根目錄留 `handoff-manager-<topic>.md`，PM 只在人指示時（含人要求的狀態盤點）讀取處理；處理紀錄寫在 PM 自己的 run，絕不回寫工廠 run | Hard rules 7 |
| E11 | 硬規則 | 工廠獨立 | 工廠交接須自足，不得要求讀 `.manager` 或本 skill；工廠可選擇性唯讀查閱整個 `.manager`，`_runs/` 只當線索；工廠不寫 `.manager`，manager 內容不成為工廠的必要輸入 | Hard rules 8 |
| E12 | 硬規則 | 保留出處 | 推論不得在缺少來源、範圍、日期、信心或權威的情況下升級為耐久事實或決策 | Hard rules 9 |
| E13 | 硬規則 | 不捏造進度 | 未知、模糊、矛盾的證據直說；區別重要時問人 | Hard rules 10 |
| E14 | 流程步驟 | 進入 PM 模式 | 見摘要步驟 1。baseline crawl 前須告知可能派多個唯讀 worker 讀程式、規格、變更文件且耗時，徵得同意與範圍限制；同意後順序為：先初始化 `.manager/` 並建立 crawl 的 manager run，再把 crawl worker 經 `pm-status-review` 派進該 run（唯讀），產出首份 `_status.md` 與 `_milestones.md`，再依證據討論憲章。同意 crawl 即授權初始化，否則等使用者明確要求才初始化；範本實例化時不複製佔位說明；憲章方向仍需人明確確認，crawl 只提供依據 | § Enter PM mode |
| E15 | 流程步驟 | 非產品路線的適用與宣告 | 受管對象不是程式碼（例如 skill 包、文件集）時適用；由章程或 library 決策宣告受管對象與本路線，否則由使用者明確指示、PM 記入 `_run.md` | § Non-product route |
| E16 | 流程步驟 | 非產品路線四步 | 1. 每個目標在 run 的 `changes/` 下寫一份異動決策；2. 直接修改受管對象：使用者看過異動決策後指示修改即為核可，PM 主動發起的修改要先停下詢問；3. 使用者以 git diff 審查，受管對象未納入版本控制時用等效前後對照，這是正式檢查點；4. 在 run 內依各異動決策擬 manager 影響更新稿，使用者檢查後才更新正典，狀態與里程碑影響經 `pm-status-review` | § Non-product route；run-lifecycle § Conclude |
| E17 | 邊界條件 | 非產品路線與硬規則、階段 | 所有硬規則仍適用，只有規則 3、4 帶上述例外；項目沿用既有階段但跳過 `approved-for-factory` 與 `handed-off`（`candidate` → `in-delivery` 修改中 → `verifying` 使用者審 diff 中 → `completed-pm`／`completed-human`）；產品專案維持工廠交接 | § Non-product route；state-model § Work item stages |
| E18 | 產物格式 | 異動決策文件 | 存於 `changes/<NN>-<target>.md`，每個修改目標一份，只用於非產品路線。範本欄位：Target（列出觸及的每個檔案）、Type（modify／add／documentation sync）、Status（proposed）、Basis；段落：Why（一到三句）、Changes 表（#、Location、Action add／modify／delete、Content 以規則層級描述而非完整成文）、Not changed、Dependencies、Manager impact（草稿在 run 內，使用者檢查後套用）、Acceptance（使用者在 diff 中檢查的點） | § Non-product route；workspace-contract § `changes/`；`assets/change-decision.template.md` |
| E19 | 流程步驟 | 請求路由 | 八種意圖：討論方向或早期想法（必要時才建 run）；問進度、缺漏、里程碑是否完成（`pm-status-review`）；看或更新里程碑與功能進度（維護 `_milestones.md`，經 `pm-status-review` 核對）；提交問題、bug、回饋或多個待辦方向（`pm-intake-triage`）；大量證據蒐集（派一或多個 `pm-investigation-worker`）；交接／派工／委派給工廠（`pm-factory-handoff`）；要求實作（說明檢查點、準備或指出已核可的交接，不實作；受管對象屬非產品路線時改走該路線）；處理工廠留下的交接檔（讀 `handoff-manager-*.md`，進度、狀態與 manager 正典訂正經 `pm-status-review`，只有新問題或候選經 `pm-intake-triage`，處理紀錄寫在 PM 自己的 run） | § Route the request |
| E20 | 流程步驟 | 調查協調 | 閱讀或比對量大到會污染 PM 脈絡、或範圍可獨立平行時才用 worker；prompt 五欄：`run_dir`（既有 `.manager/_runs/<YYYY-MM-DD>-<slug>/`）、`assignment`（一個有界問題或證據目標）、`allowed_reads`、`artifact`（PM 選定的 `run_dir` 內一或多個唯一路徑，預設在 `findings/` 下）、`constraints`（`run_dir` 外唯讀、不寫產品、不寫工廠、不巢狀派遣；可加入使用者核可的唯讀隔離例外，但必須寫明核可來源，即誰在哪裡核可；PM 不得憑自己的判斷放寬隔離）；回報後由 PM 比對綜合，worker 結論不直接更新正典 | § Coordinate investigations |
| E21 | 邊界條件 | 多 agent 協作 | `peer-agent-coordination` 定義多個 session 經共用 run 目錄協作；成本高，使用者提及、或與使用者的協作討論需要時才載入並遵循其協定，PM 不得只憑自身判斷啟用；一般證據蒐集仍派 `pm-investigation-worker` | § Multi-agent collaboration |
| E22 | 流程步驟 | run 生命週期 | 建立條件：需要耐久筆記、多來源、worker 或跨 session 延續；短的唯讀回答不建 run。建立：選 `.manager/_runs/<YYYY-MM-DD>-<slug>/` 並確認唯一 → 由範本產生 `_run.md`、`notes.md`、`outcome.md` → 派 worker 前建 `findings/` → 非產品路線在修改前建 `changes/` → 在 `_run.md` 記錄起始目標與來源輸入。工作中：重大決定、worker 批次或脈絡邊界後更新 `_run.md`；假設在確認前視為待定。收斂：寫 `outcome.md`（答案、案件決定、未解項、人的核可）→ 只升級已確認的事實、決策、backlog、狀態變更 → 記錄本 run 處理過的每個跨方交接檔 → 標記結束並指向 `outcome.md` → 保留為稽核歷史 | run-lifecycle |
| E23 | 產物格式 | 工作區結構 | 根目錄：`.gitignore`、`_charter.md`、`_status.md`、`_milestones.md`、`_backlog.md`、`_library/`（`index.md`、`facts/`、`decisions/`）、`_runs/`。run 內：`_run.md`、`notes.md`、`findings/`、選用的 `changes/`（非產品路線）、選用的 `handoff-<recipient>-<topic>.md`（跨方交接）、`outcome.md`。正典檔由工作區 repo 追蹤，`_runs/` 經 `.manager/.gitignore`（單行 `_runs/`）排除，前提是上層沒有忽略 `.manager/` 本身。slug 限小寫英數與連字號，完整路徑唯一；只有使用者明確恢復同主題才重用 run。`findings/` 預設放 worker 產物，PM 可在 run 內指定其他唯一路徑，worker 可在 run 內建立缺少的上層目錄 | workspace-contract § Root layout、§ Run-local files |
| E24 | 產物格式 | 正典檔用途與更新時機 | `_charter`：目的、目標狀態、限制、排除、PM 與人的權威、成功條件，只在明確方向決定後改；`_status`：當下投影，只在明確盤點或人直接要求時改；`_milestones`：耐久的里程碑與功能進度台帳，只在盤點時改且需證據；`_backlog`：未承諾的問題、疑似 bug、構想、風險、候選，條目不等於核可實作；`_library`：附出處的事實與決策，`index.md` 為路由索引。run 是工作記憶與證據，不是專案真相；已確認的 run 成果升級到 backlog 或 library；歷史驗收不改寫，新發現的回歸記為關聯案；以具名成果與證據階段取代百分比 | § Maintain durable state；workspace-contract § Canonical files |
| E25 | 產物格式 | 跨方交接檔 | 放在寄件方 run 根目錄，命名 `handoff-<recipient>-<topic>.md`（小寫英數與連字號）；開頭三行 `Source run:`、`Recipient:`、`Date:`；收件方在自己的 run 記錄處理，不回寫寄件方 run；工廠的 `handoff-manager-<topic>.md` 依此處理，PM 寄出時也適用；`pm-factory-handoff` 建立的冷啟動 `.factory` 包不屬於跨方交接檔 | workspace-contract § Cross-party handoff files |
| E26 | 邊界條件 | 擁有權表 | 六區域 × 三角色。PM：`.manager` 正典與 library 讀寫、manager runs 讀寫、產品 repo 唯讀、非產品受管對象在非產品路線下可寫、`.factory/**` 只為盤點與交接檔唯讀，只建已核可的交接，`.factory/.gitignore` 不存在時另建。worker：正典與 library 受指派時唯讀、只寫自己 run 內被指定的產物路徑、產品與受管對象在任務範圍內唯讀、不碰 `.factory`。工廠：正典與 library 選擇性唯讀、`_runs/**` 選擇性唯讀且只當線索、擁有產品 repo、不涉及非產品受管對象、人啟動後擁有 `.factory`。不得建立工廠到 manager 的回呼、事件或反向依賴；唯一回流管道是工廠 run 根目錄的 `handoff-manager-<topic>.md`，由人指示 PM 拉取 | workspace-contract § Ownership |
| E27 | 產物格式 | 狀態模型與進度台帳 | 六種工作項型別（question、suspected-bug、confirmed-bug、design-concern、initiative、risk），描述保留使用者原話；階段鏈 inbox → investigating → answered／candidate／deferred／rejected，candidate → approved-for-factory → handed-off → in-delivery → verifying → completed-pm／completed-human，用最小且真實的階段，deferred 與 rejected 保留理由；非產品路線跳過兩個工廠階段；必要欄位九項；里程碑是成果群組不是任務容器，不推估百分比；`_milestones.md` 三層（里程碑台帳、跨交付軸的功能進度矩陣、進行中層），四種符號 ✅ 🟡 ⬜ ⚠️ 投射工作項階段，不另立詞彙，只在盤點時依證據改 | state-model |
| E28 | 邊界條件 | 完成層級 | `completed-pm`（PM 依證據授予，證據改變可撤回）與 `completed-human`（人明確驗收，記錄誰、何時、驗收什麼，高於 PM 評估）；九級優先序；人工驗收後的回歸不默默降級，開關聯的疑似或確認 bug 並告知人，只有人明確決定才重開；PM 證據與人工驗收衝突時保留 `completed-human`、記錄新證據與信心、開關聯風險或 bug、問是否重開 | completion-precedence |
| E29 | 產物格式 | library 晉升 | 只升級耐久、可跨專案重用、有可辨識來源的資訊；fact 欄位九項（含狀態 observed／confirmed／disputed／superseded、來源路徑或人的決定或證據產物、日期、信心、`superseded_by`），沒有足夠來源或人確認不得標 confirmed；decision 欄位九項（含狀態 proposed／accepted／superseded、日期與權威、關聯案件或工廠 run）；`index.md` 保持簡短，每條列型別、狀態、範圍、一行摘要、相對路徑；不刪除曾被依賴的條目，改標 superseded 或 disputed 並連結替代與理由 | library-provenance |
| E30 | 人閘 | 停下等人的條件 | 方向或範圍有重大歧義；PM 判定與人工驗收衝突；候選可交接；需寫入 `.manager/**` 以外（非產品路線對受管對象的修改除外，其檢查點是使用者審 git diff 或等效前後對照）；調查需變動產品 repo 或外部系統 | § Human gates |
| E31 | 邊界條件 | PM 可寫與不可寫 | 可以：維護 `.manager/**`、派 run 內調查 worker、人明確核可後建一個自足的 `.factory/_runs/<run>`，建立該交接 run 時若 `.factory/.gitignore` 不存在則建立它（單行 `_runs/`）、在非產品路線下直接修改受管對象。不可以：實作產品變更、以改規格代替工廠規劃、啟動或監督工廠 session、沒有人的明確陳述就標記人工驗收、期待工廠更新 `.manager`、寫入工廠 run（包括回覆或修改其交接檔） | authority-and-gates § PM writes |
| E32 | 人閘 | 必要閘細節 | manager 初始化需使用者明確授權；工廠建立需明確交接指示（含中文同義詞），建議不等於核可，建立前與人確認委派摘要（候選、範圍、擬定標題），除非人明確要求不確認；調查中的產品變動要停下問，不得讓 worker 改產品檔、在 run 外產生持久輸出、改資料庫或呼叫會變動的外部操作；完成歧義要呈現證據、PM 評估、缺少的確認與所需決定 | authority-and-gates § Required gates |
| E33 | 產物格式 | 升級出口 | `run-outcome` 範本 Promotions 六列：Status、Backlog、Library、Factory handoff、Non-product edits（異動決策與修改目標）、Handoffs processed（交接檔路徑與處理結果）；其餘段落為 Summary、Answered questions、Case decisions、Human decisions、Remaining work | run-lifecycle § Conclude；`assets/run-outcome.template.md` |
| E34 | 產物格式 | PM 狀態彙整 | `PM_STATUS_V1`：mode 六值（discuss、status-review、triage、investigation、handoff、non-product-edit）、run_dir、project_state、milestone_progress、active_cases、factory_candidates、decisions_needed（至多三項）、next_human_checkpoint；聊天精簡，耐久細節留在 run | § PM status rollup |
| E35 | 產物格式 | 範本 | 八個範本：backlog（Inbox、Deferred、Rejected or answered）、change-decision（見 E18）、charter（標題 Project Charter；Purpose、Target state、Constraints、Explicit exclusions、Authority、Success conditions；Authority 寫明工廠可唯讀查閱 `.manager`、不寫入）、library-index（Facts、Decisions）、milestones（見 E27）、run-outcome（見 E33）、run-state（Purpose、Current position、Confirmed inputs、Pending、Worker artifacts、Next action）、status（Current milestone、Active cases、Known gaps、Decisions needed、Recently accepted） | `assets/` |
| E36 | 邊界條件 | 停止 | 交付當次 PM 結果或遇到人閘即停；不在背景常駐、不啟動工廠 session | § Stop |

## 3. 其他

skill 本身：

- **非產品路線的兩層核可**：§ Human gates 把非產品路線的修改排除在「寫入 `.manager/**` 以外要停下」之外，並寫檢查點是事後的 diff 審查；§ Non-product route 步驟 2 另有修改前的核可（PM 主動發起的修改要先問）。人閘段沒有提到修改前這一層。
- **`_run.md` 記錄路線無對應欄位**：E15 要求未經章程或 library 宣告時把路線記入 `_run.md`，但 run-state 範本六個段落沒有路線或偏離的位置。
- **worker 產物位置用詞**：run-lifecycle § Work 寫「worker 細節放在 `findings/`」，而 E20、E23 允許 PM 指定 run 內其他路徑。
- **`constraints` 的地位**：本 skill 把 `constraints` 列為每個 worker prompt 都要提供的欄位；`pm-investigation-worker` 把它列為選用輸入。
- **委派摘要欄位**：authority-and-gates 的委派摘要為候選、範圍、擬定標題；`pm-factory-handoff` Workflow 2 另加「目標」。
- **library 出處與內容限制**：E29 要求記錄來源路徑；skill 沒有說明當工作區章程限制正典檔內容時，來源可否改用 run 內產物或抽象編號。
- **`extends` 方向**：本 skill 的 `extends` 列出子 skill，而子 skill（例如 `pm-investigation-worker`、`pm-factory-handoff`）的 `extends` 也列 `orchestrator-pm`，兩個方向同時存在。

`orchestrator-pm-readme.md` 與 skill 的不一致：

- README 的工作區結構樹註解與「正典狀態與執行記憶」表都寫 `_status.md` 只在狀態盤點時更新；skill 另允許使用者直接要求更新專案狀態時更新 `_status.md`。`_milestones.md` 只在盤點時更新，兩邊一致。
- README 請求路由圖把「非產品受管對象」畫成獨立意圖；skill 把非產品路線放在「要求實作」那一列的分支。
- README 未提到：未指名 run 時不猜測（Enter 步驟 5）、非產品路線的宣告方式（章程、library 決策或記入 `_run.md`）與修改前核可、run 內結構（`findings/`、`changes/`、跨方交接檔）、跨方交接檔格式。屬省略，不是矛盾。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/pm/orchestrator-pm.md`（前版 version 1.1）：

- 新增 E3 相依子 skill 與參考檔：`extends` 加入 `peer-agent-coordination`，並列出六份參考檔的載入時機。
- 修改 E6 寫入範圍（前版 E5）：例外由一種變兩種，加入非產品路線的受管對象修改。
- 修改 E7 不實作產品（前版 E6）：加入非產品路線例外與「該對象以外的程式碼或設定仍不可碰」。
- 修改 E8 worker 留在 run 內（前版 E7）：一個產物路徑改為一或多個。
- 修改 E10 工廠不回呼（前版 E9）：加入拉式回流管道 `handoff-manager-<topic>.md`、人指示才處理、不回寫工廠 run。
- 修改 E11 工廠獨立（前版 E10）：工廠可選擇性唯讀查閱整個 `.manager`，`_runs/` 只當線索，不寫入，不成為必要輸入。
- 新增 E15 非產品路線的適用與宣告。
- 新增 E16 非產品路線四步。
- 新增 E17 非產品路線與硬規則、階段。
- 新增 E18 異動決策文件（`changes/<NN>-<target>.md` 與新範本）。
- 修改 E19 請求路由（前版 E14）：七種意圖變八種，加入處理工廠交接檔；要求實作一列加入非產品路線分支。
- 修改 E20 調查協調（前版 E15）：`artifact` 改為 run 內一或多個路徑，預設 `findings/`。
- 新增 E21 多 agent 協作（`peer-agent-coordination` 只在使用者明確指示時啟用）。
- 修改 E22 run 生命週期（前版 E16）：建立步驟加入非產品路線建 `changes/`；收斂加入非產品路線擬稿與記錄已處理的跨方交接檔。
- 修改 E23 工作區結構（前版 E17）：run 內加入選用 `changes/` 與跨方交接檔；`findings/` 改為預設位置，可指定其他路徑並建上層目錄。
- 新增 E25 跨方交接檔（命名、三行標頭、不回寫、與冷啟動包區分）。
- 修改 E26 擁有權表（前版 E19）：五區域變六區域（加非產品受管對象、manager runs 改為 `_runs/**`）；工廠對 `.manager` 由「No knowledge required」改為選擇性唯讀；PM 對 `.factory` 加入唯讀盤點與交接檔；加入唯一回流管道。
- 修改 E27 狀態模型（前版 E20）：加入非產品路線的階段路徑。
- 修改 E30 停下等人的條件（前版 E23）：寫入 `.manager/**` 以外加入非產品路線例外。
- 新增 E31 PM 可寫與不可寫：前版併在 E6 出處；本版加入 `.factory/_runs/<run>`、非產品路線修改、不得寫入工廠 run。
- 修改 E33 升級出口（前版 E25）：Promotions 由四列變六列（加 Non-product edits、Handoffs processed）。
- 修改 E34 PM 狀態彙整（前版 E26）：mode 加入 `non-product-edit`。
- 修改 E35 範本（前版 E27）：七個變八個（加 change-decision）；charter 的 Authority 段加入工廠可唯讀查閱、不寫入。
- 移除：無。

第二輪（2026-10-20，對照本稿前一版，即 last_updated 2026-10-20T14:08:54 的對照；依 `changes/25-round2-fixes.md`）：

- 修改 E14 進入 PM 模式：同意 crawl 後的順序寫明為先初始化 `.manager/` 並建立 crawl 的 run，再派 crawl worker 進該 run（P1）；摘要步驟 1 同步。
- 修改 E20 調查協調：`constraints` 可加入使用者核可的唯讀隔離例外，須寫明核可來源，PM 不得自行放寬（P5 與複查修正）。
- 修改 E21 多 agent 協作：啟用條件由「使用者明確指示」改為「使用者提及或與使用者的協作討論需要時」，仍不由 PM 主動啟用（peer 啟用統一）；摘要同步。
- 修改 E26 擁有權表：PM 的 `.factory/**` 權限加入 `.factory/.gitignore` 不存在時建立（P2 補）。
- 修改 E31 PM 可寫與不可寫：建立交接 run 時可建立 `.factory/.gitignore`（P2）。
- §3 移除兩項已不存在的問題：baseline crawl 與 run 的先後、`.factory/.gitignore` 未列入可寫清單。README 部分移除兩項已一致的問題（工廠交接圖的回流方向、路由圖缺里程碑列），並把「正典只在盤點時更新」一項縮小為 `_status.md` 的直接要求更新未寫入 README。
- 新增元素：無。移除元素：無。元素數維持 36。
