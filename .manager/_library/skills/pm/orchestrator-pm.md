# orchestrator-pm 元素對照

- 分支：pm
- 對照版本：`skills/orchestrator-pm/SKILL.md` version 1.3，last_updated 2026-11-02T12:22:04
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/authority-and-gates.md`、`references/completion-precedence.md`、`references/library-provenance.md`、`references/run-lifecycle.md`、`references/state-model.md`、`references/workspace-contract.md`、`assets/` 下九個範本（automation、backlog、change-decision、charter、library-index、milestones、run-outcome、run-state、status）；`orchestrator-pm-readme.md` 只用於比對不一致；`peer-agent-coordination/SKILL.md` 只核對被引用的 section 5、7 與名冊、`_communication-notes.md` 是否存在
- 狀態：已檢查，2026-11-02 移入 manager 正式文件

## 1. 摘要

`orchestrator-pm` 是專案的 PM 控制面：維持長期方向與狀態、協調有界的唯讀調查、整理事實與決策，並在人工核可後準備工廠交接；自己不實作產品、不做工廠的工作。它只管專案層級的方向、範圍、排程與狀態，工廠粒度的研究、設計與實作問題留給工廠。只在使用者明確呼叫或明確啟用 PM 模式時進入，依主題載入 `pm-status-review`、`pm-intake-triage`、`pm-investigation-worker`、`pm-factory-handoff`。PM 發動的工廠委派預設使用 `peer-agent-coordination`（使用者核可委派即視為啟用），其他情況只在使用者提及或與使用者的協作討論需要時才用。使用者核可自動化計畫時，PM 以一個 manager run 管理一整批工廠 run。受管對象不是程式碼時（例如 skill 包、文件集），走「非產品路線」：由 manager session 直接修改受管對象，不經工廠。所有正典更新一律先擬稿到 run 的 `staging/`，使用者檢查後才套用。

流程順序：

1. **進入**：宣告 PM 模式與目標 → 唯讀檢視 `.manager/` → 若不存在，判斷工作區是否已有可觀的專案狀態：有則告知並徵得同意後，先初始化 `.manager/`（含 `_runs/` 與單行 `.gitignore`）並建立 crawl 的 manager run，再把 baseline crawl worker 經 `pm-status-review` 派進該 run，之後依證據討論憲章；無則先討論憲章，再於使用者明確要求時初始化 `.manager/` → 恢復具名 run 時只讀 `_run.md` 與其指向的產物 → 未指名 run 時不在多個 run 間猜測。
2. **路由**：依意圖分派到討論、狀態盤點、里程碑維護、進件分流、調查 worker、工廠交接、批次自動化、處理工廠留下的交接檔；要求實作時說明 PM／工廠檢查點，受管對象屬非產品路線時改走該路線。
3. **工作**：需要耐久紀錄時建立 run（`_run.md`、`notes.md`、`outcome.md`、`findings/`，選用 `staging/`、非產品路線另建 `changes/`、自動化另建 `_automation.md`）；worker 產物寫在 PM 指定的 run 內路徑，由 PM 比對綜合。
4. **非產品路線**（適用時）：每個目標寫一份異動決策 → 直接修改受管對象 → 使用者以 git diff 或等效前後對照審查 → 在 run 內擬 manager 影響更新稿，使用者檢查後才更新正典，狀態與里程碑經 `pm-status-review`。
5. **委派**（適用時）：PM 發動的工廠委派預設在工廠 run 建 peer 討論室、PM 任 host；補交事項以討論室訊息或交付到工廠 run 根目錄的 `handoff-factory-<topic>.md` 傳遞，非自動化時先與使用者討論。
6. **自動化**（適用時）：與使用者議定範圍寫成 `_automation.md` → 使用者核可 → 經 `pm-factory-handoff` 建立每個工廠 run → 設計段 → 使用者一次檢視全部 change → 施工段依相依順序施工 → 整批完成後彙整 `_review-backlog.md`、一次人工 E2E、sync/archive。
7. **回流**：工廠的 `handoff-manager-<topic>.md` 在人指示或 peer 通知時讀取，篩選後擬稿到 `staging/`，使用者檢查後套用；處理紀錄寫在 PM 自己的 run。
8. **收斂**：寫 `outcome.md`，只把已確認內容經 `staging/` 擬稿、使用者檢查後升級為正典（status、backlog、library），記錄工廠交接、非產品修改與已處理的交接檔，標記 run 結束。
9. **停止**：交付當次 PM 結果或遇到人閘即停；核可的自動化計畫以外不啟動工廠 session；有 peer 討論室的委派依 peer section 5 保持可被喚醒，直到使用者結束討論室。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 明確啟用 | 只在使用者明確呼叫 `/orchestrator-pm` 或明確啟用 PM 模式時進入；一般專案問題不得自動進入。frontmatter `disable-model-invocation: true`，openai `allow_implicit_invocation: false` | frontmatter；開頭段；`agents/openai.yaml` |
| E2 | 角色 | 控制面 PM | 維持方向與狀態、協調有界調查、整理事實與決策、準備實作交接；不成為實作者。description 另列：在使用者核可的自動化計畫下，以一個工廠 session 協調一批工廠 run；不做工廠的工作 | 開頭段；frontmatter description |
| E3 | 繼承與覆寫 | 相依子 skill 與參考檔 | frontmatter `extends: pm-status-review, pm-intake-triage, pm-factory-handoff, pm-investigation-worker, peer-agent-coordination`；六份參考檔依主題載入：路徑與擁有權讀 workspace-contract、案件與里程碑讀 state-model、人閘與寫入讀 authority-and-gates、建立或恢復 run 讀 run-lifecycle、變更完成狀態讀 completion-precedence、升級事實或決策讀 library-provenance | frontmatter；§ Required references |
| E4 | 硬規則 | 人的權威優先 | 人的明確結論、核可、驗收高於 PM 推論；權威五級：人的決定或驗收 > 章程與已接受決策 > 有現行證據的 PM 評估 > worker 發現 > 未確認報告與歷史筆記；衝突時保留高權威者，低權威者記為問題、風險或新案 | Hard rules 1；authority-and-gates § Authority order |
| E5 | 硬規則 | 單一 PM session | 同時只假設一個 PM session；後繼 session 靠 `.manager` 耐久狀態接手，不需永久身分。替換時讀根狀態 → 具名 run 的 `_run.md` → 只讀 `_run.md` 指名的 findings 與參考，run 有 `_automation.md` 時一併讀 → 先陳述恢復的目標、位置、下一步；不依賴前一段對話紀錄。在 PM 任 host 的 peer 討論室，於名冊以新的 `canonical_id` 取代舊 PM，並在 `_communication-notes.md` 記錄 | Hard rules 2；run-lifecycle § Replace the PM session |
| E6 | 硬規則 | 寫入範圍 | 只寫 `.manager/**`，三個例外：人明確核可、透過 `pm-factory-handoff` 建立的工廠交接；PM 交付進工廠 run 的交接檔（見 E23）；非產品路線下對受管對象的文字修改。peer 訊息是溝通管道，不算文件寫入 | Hard rules 3 |
| E7 | 硬規則 | 不實作產品 | 不改產品原始碼、專案規格、repository、部署狀態；非產品路線下對受管對象的文字修改不在此限，但該對象以外的程式碼或設定仍不可碰；目前 manager run 以外的調查一律唯讀 | Hard rules 4 |
| E8 | 硬規則 | 停在專案層級 | 管方向、範圍、排程與狀態；工廠粒度的研究、設計、實作問題留給工廠，不深入、不替它決定、不改工廠的工作檔。authority-and-gates 對應為不得改工廠 run 的工作檔或交接檔、不得替它決定工廠層級的設計 | Hard rules 5；authority-and-gates § PM writes |
| E9 | 硬規則 | worker 留在 run 內 | 每個 worker 收到一個確切 `run_dir` 與其內一個或多個確切產物路徑；不得更新 manager 根狀態、library、產品檔、`.factory` | Hard rules 6 |
| E10 | 硬規則 | 不靜默啟動工廠 | 提出候選 → 等人明確指示建立 → 建交接 → 停；由人啟動工廠 session。核可的自動化計畫改依 § Automation（見 E24） | Hard rules 7 |
| E11 | 硬規則 | 經交接檔回流 | 工廠絕不寫 `.manager`；工廠經自身 run 根目錄的 `handoff-manager-<topic>.md` 回流，可選擇經 peer 通知。PM 在人指示或 peer 通知時讀取；正典更新擬稿到 run 的 `staging/`，使用者檢查後才套用；處理紀錄寫在 PM 自己的 run，絕不修改該交接檔 | Hard rules 8 |
| E12 | 硬規則 | 工廠獨立 | 工廠交接須自足，不得要求讀 `.manager` 或本 skill；工廠可選擇性唯讀查閱整個 `.manager`，`_runs/` 只當線索；工廠不寫 `.manager`，manager 內容不成為工廠的必要輸入 | Hard rules 9 |
| E13 | 硬規則 | 保留出處 | 推論不得在缺少來源、範圍、日期、信心或權威的情況下升級為耐久事實或決策 | Hard rules 10 |
| E14 | 硬規則 | 不捏造進度 | 未知、模糊、矛盾的證據直說；區別重要時問人 | Hard rules 11 |
| E15 | 流程步驟 | 進入 PM 模式 | 見摘要步驟 1。baseline crawl 前須告知可能派多個唯讀 worker 讀程式、規格、變更文件且耗時，徵得同意與範圍限制；同意後順序為：先初始化 `.manager/` 並建立 crawl 的 manager run，再把 crawl worker 經 `pm-status-review` 派進該 run（唯讀），產出首份 `_status.md` 與 `_milestones.md`，再依證據討論憲章。同意 crawl 即授權初始化，否則等使用者明確要求才初始化；範本實例化時不複製佔位說明；憲章方向仍需人明確確認，crawl 只提供依據 | § Enter PM mode |
| E16 | 流程步驟 | 非產品路線的適用與宣告 | 受管對象不是程式碼（例如 skill 包、文件集）時適用；由章程或 library 決策宣告受管對象與本路線，否則由使用者明確指示、PM 記入 `_run.md` | § Non-product route |
| E17 | 流程步驟 | 非產品路線四步 | 1. 每個目標在 run 的 `changes/` 下寫一份異動決策；2. 直接修改受管對象：使用者看過異動決策後指示修改即為核可，PM 主動發起的修改要先停下詢問；3. 使用者以 git diff 審查，受管對象未納入版本控制時用等效前後對照，這是正式檢查點；4. 依各異動決策的 manager 影響在 run 內擬更新稿（run-lifecycle 寫明擬在 `staging/`），使用者檢查後才更新正典，狀態與里程碑影響經 `pm-status-review` | § Non-product route；run-lifecycle § Conclude |
| E18 | 邊界條件 | 非產品路線與硬規則、階段 | 所有硬規則仍適用，只有規則 3、4 帶上述例外；項目沿用既有階段但跳過 `approved-for-factory` 與 `handed-off`（`candidate` → `in-delivery` 修改中 → `verifying` 使用者審 diff 中 → `completed-pm`／`completed-human`）；產品專案維持工廠交接 | § Non-product route；state-model § Work item stages |
| E19 | 產物格式 | 異動決策文件 | 存於 `changes/<NN>-<target>.md`，每個修改目標一份，只用於非產品路線。SKILL 列內容：why；逐列、規則層級的 changes（檔案、段落、add／modify／delete）；not changed；dependencies；manager impact；acceptance。範本欄位：Target（列出觸及的每個檔案）、Type（modify／add／documentation sync）、Status（proposed）、Basis；段落：Why（一到三句）、Changes 表（#、Location、Action、Content 以規則層級描述而非完整成文）、Not changed、Dependencies、Manager impact（草稿在 run 內，使用者檢查後套用；狀態與里程碑經 pm-status-review）、Acceptance（使用者在 diff 中檢查的點） | § Non-product route；workspace-contract § `changes/`；`assets/change-decision.template.md` |
| E20 | 流程步驟 | 請求路由 | 九種意圖：討論方向或早期想法（必要時才建 run）；問進度、缺漏、里程碑是否完成（`pm-status-review`）；看或更新里程碑與功能進度（維護 `_milestones.md`，經 `pm-status-review` 核對）；提交問題、bug、回饋或多個待辦方向（`pm-intake-triage`）；大量證據蒐集（派一或多個 `pm-investigation-worker`）；交接／派工／委派給工廠（`pm-factory-handoff`）；要求實作（說明檢查點、準備或指出已核可的交接，不實作；受管對象屬非產品路線時改走該路線）；把多個已核可候選當一批交給工廠（自動化／批次施工或等義說法，依 § Automation）；在人指示或 peer 通知時處理工廠留下的交接檔（讀 `handoff-manager-*.md`，進度、狀態與 manager 正典訂正經 `pm-status-review` 擬稿到 `staging/`，只有新問題或候選經 `pm-intake-triage`，處理紀錄寫在 PM 自己的 run） | § Route the request |
| E21 | 流程步驟 | 調查協調 | 閱讀或比對量大到會污染 PM 脈絡、或範圍可獨立平行時才用 worker；prompt 五欄：`run_dir`（既有 `.manager/_runs/<YYYY-MM-DD>-<slug>/`）、`assignment`（一個有界問題或證據目標）、`allowed_reads`、`artifact`（PM 選定的 `run_dir` 內一或多個唯一路徑，預設在 `findings/` 下）、`constraints`（`run_dir` 外唯讀、不寫產品、不寫工廠、不巢狀派遣；可加入使用者核可的隔離例外，但必須寫明核可來源，即誰在哪裡核可，且例外絕不允許修改產品、規格、設定、manager 或工廠檔；PM 不得憑自己的判斷放寬隔離）；回報後由 PM 比對綜合，worker 結論不直接更新正典 | § Coordinate investigations |
| E22 | 邊界條件 | 委派與 peer 啟用 | `peer-agent-coordination` 定義 agent session 經共用 run 目錄溝通。PM 發動的工廠委派預設使用它，人核可委派即視為啟用；其他情況只在使用者提及或與使用者的協作討論需要時啟用；一般證據蒐集仍派 `pm-investigation-worker`。委派時：討論室是工廠 run 目錄，由 PM 建立並先任 host；除非使用者指定，委派給 PM 同平台的 agent；通道依 peer section 7 選擇，是否需背景接聽依 peer section 5；同一批次內 PM 與工廠身分跨工廠 run 延續，每個工廠 run 各是一個討論室；工廠自行唯讀查閱 `.manager`，不發訊息向 PM 提問，PM 也不回答工廠層級的問題 | § Delegation |
| E23 | 流程步驟 | 補交事項給既有工廠 run | 一般在該 run 的討論室發訊息；遇嚴重事項、大量內容，或為了不打斷工廠工作，在該工廠 run 根目錄寫 `handoff-factory-<topic>.md` 並經 peer 通知。自動化以外，每件補交事項都先與使用者討論才送出：交接檔先以同名草稿放在 manager run 根目錄，使用者確認後才交付。交接檔只寫問題與證據，不寫修法 | § Delegation |
| E24 | 流程步驟 | 自動化流程 | 計畫由使用者核可後才執行，PM 可提議但不自行啟動。1. 與使用者議定範圍，由範本寫成 run 的 `_automation.md`，計畫核可前不建任何工廠 run；2. 經 `pm-factory-handoff` 建立每個工廠 run，把工廠需要的授權依值寫進其 `_intake.md`；3. 整批只有一個 PM session 與一個工廠 session，預設由使用者啟動工廠 session，平台允許時 PM 可代建，PM 經 peer 把同一個工廠 session 移到下一個 run；4. 設計段：工廠先讓每個 run 走完討論、propose、change-doc review，紀錄無法解決的決策逐 run 列出；5. 批次檢視 change：使用者在一個關卡檢視全部 change 與各 run 待決事項，確認（全部或部分 run）後才開工；6. 施工段：工廠依相依順序對每個確認的 run 施工、檢查、commit、交接，每個 run 交接時擬稿到 `staging/`（規則 8），停下的 run 只暫停依賴它的 run；7. 全部完成後由工廠彙整 `_review-backlog.md`，使用者做一次 E2E，之後 sync/archive | § Automation |
| E25 | 人閘 | 自動化的預先授權範圍 | 計畫只預先授權兩項：批次檢視後依序派工確認過的 run，不再逐 run 確認派工；每個工廠 run 預設 commit 一次，使用者可改或關閉。人工 E2E 驗收、sync/archive、push 永不預先授權，push 需使用者另外明確授權 | § Automation 末段 |
| E26 | 產物格式 | 自動化計畫 `_automation.md` | 存於 manager run，由範本產生。範本：Status（proposed／approved／design／change-review／build／ended）；Approval（使用者核可原話與日期，核可前留空）；Scope；Factory runs 表（Order、Factory run、Goal、Depends on）；Flow（設計段、批次檢視、施工段依相依順序派工不再另行確認）；Commit（預設每個工廠 run 一次、使用者另定的規則或 none；未經另外明確授權絕不 push）；Stop conditions（工廠自身規則以外的條件）；Report points（每個工廠 run 到達 await-e2e 時的 manager 交接，擬稿到 `staging/`）；End of batch（工廠彙整 `.factory/_review-backlog.md`，使用者一次 E2E，之後 sync/archive）。workspace-contract 的說明與範本一致 | workspace-contract § `_automation.md`；`assets/automation.template.md` |
| E27 | 流程步驟 | run 生命週期 | 建立條件：需要耐久筆記、多來源、worker 或跨 session 延續；短的唯讀回答不建 run。建立：選 `.manager/_runs/<YYYY-MM-DD>-<slug>/` 並確認唯一 → 由範本產生 `_run.md`、`notes.md`、`outcome.md` → 派 worker 前建 `findings/` → 非產品路線在修改前建 `changes/` → 在 `_run.md` 記錄起始目標與來源輸入。工作中：重大決定、worker 批次或脈絡邊界後更新 `_run.md`；worker 細節放 `findings/` 並由 `_run.md` 指向；假設在確認前視為待定。收斂：寫 `outcome.md`（答案、案件決定、未解項、人的核可）→ 只升級已確認的事實、決策、backlog、狀態變更，擬稿在 `staging/`、使用者檢查後套用；非產品路線的稿來自各異動決策的 manager 影響，狀態與里程碑經 `pm-status-review` → 在 `outcome.md` 記錄本 run 處理過的每個跨方交接檔 → 標記結束並指向 `outcome.md` → 保留為稽核歷史 | run-lifecycle |
| E28 | 產物格式 | 工作區結構 | 根目錄：`.gitignore`、`_charter.md`、`_status.md`、`_milestones.md`、`_backlog.md`、`_library/`（`index.md`、`facts/`、`decisions/`）、`_runs/`。run 內：`_run.md`、`notes.md`、`findings/`、選用的 `staging/`（正典更新稿）、選用的 `changes/`（非產品路線）、選用的 `_automation.md`（自動化計畫）、`outcome.md`。正典檔由工作區 repo 追蹤，`_runs/` 經 `.manager/.gitignore`（單行 `_runs/`）排除，前提是上層沒有忽略 `.manager/` 本身。slug 限小寫英數與連字號，完整路徑唯一；只有使用者明確恢復同主題才重用 run。`findings/` 預設放 worker 產物，PM 可在 run 內指定其他唯一路徑，worker 可在 run 內建立缺少的上層目錄 | workspace-contract § Root layout、§ Run-local files |
| E29 | 產物格式 | 待沖入區 `staging/` | 每個正典更新（charter、status、milestones、backlog、library）都先擬稿到 run 的 `staging/`，使用者檢查後才套用，使用者要求的盤點也一樣。內容：一份 `_index.md` 審查索引，逐項列出變更與依據；草稿檔依其將取代的正典路徑對應存放 | § Maintain durable state；workspace-contract § Canonical files 開頭、§ `staging/` |
| E30 | 產物格式 | 正典檔用途與更新時機 | `_charter`：目的、目標狀態、限制、排除、PM 與人的權威、成功條件，只在明確方向決定後改；`_status`：當下投影（目前里程碑、進行中案件、已知缺口、待決事項、關聯工廠 run、近期驗收），只經明確盤點或使用者要求更新專案狀態時改；`_milestones`：耐久的里程碑與功能進度台帳，與 `_status` 的時點快照不同，只在盤點時改且需證據；`_backlog`：未承諾的問題、疑似 bug、構想、風險、候選，條目不等於核可實作；`_library`：附出處的事實與決策，`index.md` 為路由索引。以上變更都經 E29 的擬稿。run 是工作記憶與證據，不是專案真相；已確認的 run 成果升級到 backlog 或 library；歷史驗收不改寫，新發現的回歸記為關聯案；以具名成果與證據階段取代百分比 | § Maintain durable state；workspace-contract § Canonical files |
| E31 | 產物格式 | 跨方交接檔 | manager 與工廠之間的交接檔一律放在工廠 run 根目錄：工廠的 `handoff-manager-<topic>.md` 在它自己的 run，manager 的 `handoff-factory-<topic>.md` 在收件的工廠 run；PM 交付前與使用者討論的草稿以同名放在 manager run 根目錄。檔名限小寫英數與連字號；開頭三行 `Source run:`、`Recipient:`、`Date:`；收件方絕不修改該檔，處理紀錄寫在自己的 run；`pm-factory-handoff` 建立的冷啟動 `.factory` 包不屬於跨方交接檔，保有自己的控制檔 | workspace-contract § Cross-party handoff files |
| E32 | 邊界條件 | 擁有權表 | 六區域 × 三角色。PM：`.manager` 正典與 library 讀寫、manager runs 讀寫、產品 repo 唯讀、非產品受管對象在非產品路線下可寫、`.factory/**` 為盤點與交接檔唯讀，可建已核可的交接 run（`.factory/.gitignore` 不存在時另建）、自己發動的委派的 peer 檔、交付的 `handoff-factory-<topic>.md`。worker：正典與 library 受指派時唯讀、只寫自己 run 內被指定的產物路徑、產品與受管對象在任務範圍內唯讀、不碰 `.factory`。工廠：正典與 library 選擇性唯讀、`_runs/**` 選擇性唯讀且只當線索、擁有產品 repo、不涉及非產品受管對象、工廠 session 啟動後擁有 `.factory`。工廠只經自身 run 根目錄的 `handoff-manager-<topic>.md` 回流 manager，可選擇經 peer 通知；PM 在人指示或 peer 通知時讀取，擬稿到 `staging/` | workspace-contract § Ownership |
| E33 | 產物格式 | 狀態模型與進度台帳 | 六種工作項型別（question、suspected-bug、confirmed-bug、design-concern、initiative、risk），描述保留使用者原話；階段鏈 inbox → investigating → answered／candidate／deferred／rejected，candidate → approved-for-factory → handed-off → in-delivery → verifying → completed-pm／completed-human，用最小且真實的階段，deferred 與 rejected 保留理由；非產品路線跳過兩個工廠階段；必要欄位九項；里程碑是成果群組不是任務容器，不推估百分比；`_milestones.md` 三層（里程碑台帳、跨交付軸的功能進度矩陣、進行中層），四種符號 ✅ 🟡 ⬜ ⚠️ 投射工作項階段，不另立詞彙，只在盤點時依證據改 | state-model |
| E34 | 邊界條件 | 完成層級 | `completed-pm`（PM 依證據授予，證據改變可撤回）與 `completed-human`（人明確驗收，記錄誰、何時、驗收什麼，高於 PM 評估）；九級優先序；人工驗收後的回歸不默默降級，開關聯的疑似或確認 bug 並告知人，只有人明確決定才重開；PM 證據與人工驗收衝突時保留 `completed-human`、記錄新證據與信心、開關聯風險或 bug、問是否重開 | completion-precedence |
| E35 | 產物格式 | library 晉升 | 只升級耐久、可跨專案重用、有可辨識來源的資訊；fact 欄位九項（含狀態 observed／confirmed／disputed／superseded、來源路徑或人的決定或證據產物、日期、信心、`superseded_by`），沒有足夠來源或人確認不得標 confirmed；decision 欄位九項（含狀態 proposed／accepted／superseded、日期與權威、關聯案件或工廠 run）；`index.md` 保持簡短，每條列型別、狀態、範圍、一行摘要、相對路徑；不刪除曾被依賴的條目，改標 superseded 或 disputed 並連結替代與理由 | library-provenance |
| E36 | 人閘 | 停下等人的條件 | 方向或範圍有重大歧義；PM 判定與人工驗收衝突；候選可交接；自動化計畫待核可；需寫入 `.manager/**` 以外（非產品路線對受管對象的修改除外，其檢查點是使用者審 git diff 或等效前後對照）；調查需變動產品 repo 或外部系統 | § Human gates |
| E37 | 邊界條件 | PM 可寫與不可寫 | 可以：維護 `.manager/**`；派 run 內調查 worker；人明確核可後建一個自足的 `.factory/_runs/<run>`（核可的自動化計畫下可建多個），建立交接 run 時若 `.factory/.gitignore` 不存在則建立它（單行 `_runs/`）；在自己發動的委派中發 peer 訊息，並把 `handoff-factory-<topic>.md` 交付到工廠 run 根目錄；核可的自動化計畫下、平台允許時啟動工廠 session；在非產品路線下直接修改受管對象。不可以：實作產品變更；以改規格代替工廠規劃；在核可的自動化計畫以外啟動或監督工廠 session；沒有人的明確陳述就標記人工驗收；期待工廠更新 `.manager`；修改工廠 run 的工作檔或交接檔，或替它決定工廠層級的設計 | authority-and-gates § PM writes |
| E38 | 人閘 | 必要閘細節 | manager 初始化需使用者明確授權；工廠建立需明確交接指示（含中文同義詞），建議不等於核可，建立前與人確認委派摘要（候選、範圍、擬定標題），除非人明確要求不確認；核可的自動化計畫對其列出的 run 同時算作交接指示與摘要確認；自動化核可：建立批次的任何工廠 run 前須使用者核可 `_automation.md`，核可只涵蓋計畫列出的範圍、run 與預先授權，使用者的批次檢視、人工 E2E、sync/archive、push 永不預先授權；調查中的產品變動要停下問，不得讓 worker 改產品檔、在 run 外產生持久輸出、改資料庫或呼叫會變動的外部操作；完成歧義要呈現證據、PM 評估、缺少的確認與所需決定 | authority-and-gates § Required gates |
| E39 | 產物格式 | 升級出口 | `run-outcome` 範本 Promotions 六列：Status、Backlog、Library、Factory handoff、Non-product edits（異動決策與修改目標）、Handoffs processed（交接檔路徑與處理結果）；其餘段落為 Summary、Answered questions、Case decisions、Human decisions、Remaining work | run-lifecycle § Conclude；`assets/run-outcome.template.md` |
| E40 | 產物格式 | PM 狀態彙整 | `PM_STATUS_V1`：mode 七值（discuss、status-review、triage、investigation、handoff、automation、non-product-edit）、run_dir、project_state、milestone_progress、active_cases、factory_candidates、decisions_needed（至多三項）、next_human_checkpoint；聊天精簡，耐久細節留在 run | § PM status rollup |
| E41 | 產物格式 | 範本 | 九個範本：automation（見 E26）、backlog（Inbox、Deferred、Rejected or answered）、change-decision（見 E19）、charter（標題 Project Charter；Purpose、Target state、Constraints、Explicit exclusions、Authority、Success conditions；Authority 寫明工廠可唯讀查閱 `.manager`、不寫入）、library-index（Facts、Decisions）、milestones（Milestone ledger、Feature progress、In progress、Backlog / not started；見 E33）、run-outcome（見 E39）、run-state（Purpose、Current position、Confirmed inputs、Pending、Worker artifacts、Next action）、status（Current milestone、Active cases、Known gaps、Decisions needed、Recently accepted） | `assets/` |
| E42 | 邊界條件 | 停止 | 交付當次 PM 結果或遇到人閘即停；核可的自動化計畫以外不啟動工廠 session；有 peer 討論室的委派依 `peer-agent-coordination` section 5 保持可被喚醒，直到使用者結束討論室；其他情況不在背景常駐 | § Stop |

## 3. 其他

skill 本身：

- **非產品路線的兩層核可**：§ Human gates 把非產品路線的修改排除在「寫入 `.manager/**` 以外要停下」之外，並寫檢查點是事後的 diff 審查；§ Non-product route 步驟 2 另有修改前的核可（PM 主動發起的修改要先問）。人閘段沒有提到修改前這一層。
- **`_run.md` 記錄路線無對應欄位**：E16 要求未經章程或 library 宣告時把路線記入 `_run.md`，但 run-state 範本六個段落沒有路線或偏離的位置。
- **worker 產物位置用詞**：run-lifecycle § Work 寫「worker 細節放在 `findings/`」，而 E21、E28 允許 PM 指定 run 內其他路徑。
- **`constraints` 的地位**：本 skill 把 `constraints` 列為每個 worker prompt 都要提供的欄位；`pm-investigation-worker` 把它列為選用輸入。
- **委派摘要欄位**：authority-and-gates 的委派摘要為候選、範圍、擬定標題；`pm-factory-handoff` Workflow 2 另加「目標」。
- **library 出處與內容限制**：E35 要求記錄來源路徑；skill 沒有說明當工作區章程限制正典檔內容時，來源可否改用 run 內產物或抽象編號。
- **`extends` 方向**：本 skill 的 `extends` 列出子 skill，而子 skill（例如 `pm-investigation-worker`、`pm-factory-handoff`）的 `extends` 也列 `orchestrator-pm`，兩個方向同時存在。
- **manager run 根目錄的交接草稿不在結構樹**：workspace-contract § Cross-party handoff files 讓交付前的 `handoff-factory-<topic>.md` 草稿留在 manager run 根目錄，但 § Root layout 的 run 樹本版移除了交接檔一列，沒有列出這個草稿。
- **peer 檔的寫入授權分散**：擁有權表允許 PM 寫「自己發動的委派的 peer 檔」；硬規則 3 的例外只列交付的交接檔，並說 peer 訊息不算文件寫入；authority-and-gates § PM writes 只列發 peer 訊息與交付交接檔。PM 在工廠 run 建討論室（`pm-factory-handoff` Workflow 6）與換手時改名冊、寫 `_communication-notes.md`（run-lifecycle）屬於在工廠 run 內寫 peer 檔，只有擁有權表明確涵蓋。
- **初始化時實例化哪些範本**：Enter 步驟 3 寫實例化 `assets/` 下的範本，但 `assets/` 九個範本中有四個是 run 用（run-state、run-outcome、change-decision、automation），沒有區分。另外 § Maintain durable state 要求每個正典更新先擬稿到 `staging/`，初始化時直接實例化正典檔是否屬例外沒有寫明（baseline crawl 的首份 `_status.md`、`_milestones.md` 在 `pm-status-review` 已明定先擬稿）。

`orchestrator-pm-readme.md` 與 skill 的不一致：

- README 的工作區結構樹註解與「正典狀態與執行記憶」表都寫 `_status.md` 只在狀態盤點時更新；skill 另允許使用者要求更新專案狀態時更新 `_status.md`。`_milestones.md` 只在盤點時更新，兩邊一致。
- README 請求路由圖把「非產品受管對象」畫成獨立意圖；skill 把非產品路線放在「要求實作」那一列的分支。
- README 未提到：未指名 run 時不猜測（Enter 步驟 5）、非產品路線的宣告方式（章程、library 決策或記入 `_run.md`）與修改前核可、run 內的 `findings/` 與 `changes/`（README 的 run 樹只列 `staging/` 與 `_automation.md`）、跨方交接檔格式、補交事項的 `handoff-factory-<topic>.md` 與非自動化時先與使用者討論。屬省略，不是矛盾。

## 4. 與前版差異

對照前版對照（version 1.2，last_updated 2026-10-20T15:52:52）：

- 修改 E2 控制面 PM：description 加入自動化計畫下協調一批工廠 run；「never runs the factory」改為「never does the factory's work」。
- 修改 E5 單一 PM session：去掉「不需回呼」；換手時加讀 `_automation.md`，在 PM 任 host 的討論室更新名冊並記 `_communication-notes.md`。
- 修改 E6 寫入範圍：例外由兩種變三種，加入交付進工廠 run 的交接檔；peer 訊息不算文件寫入。
- 新增 E8 停在專案層級（新硬規則 5）；原硬規則 5–10 順延為 6–11，前版 E8–E36 依序後移。
- 修改 E10 不靜默啟動工廠（前版 E9）：加入核可的自動化計畫例外。
- 修改 E11 經交接檔回流（前版 E10「工廠不回呼、只拉式回流」）：觸發由「只在人指示時」改為「人指示或 peer 通知」；正典更新擬稿到 `staging/`；「不回寫工廠 run」改為「不修改交接檔」。
- 修改 E17 非產品路線四步（前版 E16）：擬稿位置依 run-lifecycle 為 `staging/`。
- 修改 E19 異動決策文件（前版 E18）：補列 SKILL 本文對異動決策內容的描述（本版未改，前版對照未列）。
- 修改 E20 請求路由（前版 E19）：八種意圖變九種，加入批次自動化；處理交接檔一列加入 peer 通知觸發與擬稿到 `staging/`。
- 修改 E21 調查協調（前版 E20）：補列隔離例外絕不允許修改產品、規格、設定、manager 或工廠檔（本版未改，前版對照未列）。
- 修改 E22 委派與 peer 啟用（前版 E21「多 agent 協作」）：段名改為 Delegation；PM 發動的工廠委派預設用 peer，人核可委派即啟用；加入討論室位置、同平台、通道與接聽、跨 run 沿用身分、工廠不向 PM 提問。
- 新增 E23 補交事項給既有工廠 run。
- 新增 E24 自動化流程、E25 自動化的預先授權範圍、E26 自動化計畫 `_automation.md`（新範本 `assets/automation.template.md`）。
- 修改 E27 run 生命週期（前版 E22）：收斂的升級改為經 `staging/` 擬稿、使用者檢查後套用。
- 修改 E28 工作區結構（前版 E23）：run 樹加入 `staging/` 與 `_automation.md`，移除 `handoff-<recipient>-<topic>.md`。
- 新增 E29 待沖入區 `staging/`。
- 修改 E30 正典檔用途與更新時機（前版 E24）：所有正典變更先擬稿；補列 `_status` 內容與 `_milestones` 和快照的區別。
- 修改 E31 跨方交接檔（前版 E25）：由「放寄件方 run 根目錄」改為「manager 與工廠之間一律放工廠 run 根目錄」，PM 草稿留在 manager run 根目錄；收件方「不回寫寄件方」改為「不修改該檔」。
- 修改 E32 擁有權表（前版 E26）：PM 對 `.factory/**` 加入委派的 peer 檔與交付的 `handoff-factory-<topic>.md`；工廠「人啟動後」改為「工廠 session 啟動後」擁有 `.factory`；去掉「不得建立回呼、事件或反向依賴」，回流改寫為可經 peer 通知、PM 擬稿到 `staging/`。
- 修改 E36 停下等人的條件（前版 E30）：加入自動化計畫待核可。
- 修改 E37 PM 可寫與不可寫（前版 E31）：加入自動化下建多個 run、發 peer 訊息與交付交接檔、平台允許時啟動工廠 session；「不得寫入工廠 run」改為「不得修改工廠 run 的工作檔或交接檔、不替它決定工廠層級設計」；啟動或監督工廠限於自動化計畫以外。
- 修改 E38 必要閘細節（前版 E32）：核可的自動化計畫算作交接指示與摘要確認；新增自動化核可閘。
- 修改 E40 PM 狀態彙整（前版 E34）：mode 加入 `automation`。
- 修改 E41 範本（前版 E35）：八個變九個（加 automation），milestones 列出四個段落。
- 修改 E42 停止（前版 E36）：自動化計畫內可啟動工廠 session；有 peer 討論室的委派依 peer section 5 保持可被喚醒。
- §3 新增三項：交接草稿不在結構樹、peer 檔寫入授權分散、初始化時實例化哪些範本。README 部分更新省略清單。
- 移除元素：無。元素數由 36 變 42。
