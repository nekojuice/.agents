# orchestrator-factory 元素對照

- 分支：factory
- 對照版本：`skills/orchestrator-factory/SKILL.md` version 1.7，last_updated 2026-10-20T15:46:00
- 讀過的檔案：`skills/orchestrator-factory/SKILL.md`、`skills/orchestrator-factory/agents/openai.yaml`；另讀 skill 外的 `orchestrator-factory-readme.md`，只用來記錄不一致；為確認跨 skill 引用的章節存在，唯讀查閱 `code-review` step 3 與 Finding tags、`opsx-apply-guide`、`opsx-propose-guide`、`need-ask-user-guide` 的章節標題
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`orchestrator-factory` 讓 agent 進入工廠模式，擔任廠長（orchestrator）：判斷階段、提出具名 worker 派工、守人閘、管理 `.factory/` run 工作區、彙整 worker 回報，然後為使用者停下。有 worker 可用時，廠長不親自做實作本體。

啟用有兩條路：使用者明確要求工廠模式，或新 session 被指派一個 `_status.md` 為 `await-factory-session` 的既有 run（冷啟動交接）。啟用本身不授權派工、apply、E2E 驗收、sync 或 archive。

進入後先分類工作。專案實作走完整 opsx 流程；非專案實作（研究、盤點、純文件等）改走較小的自訂路線，但仍須寫明產物、允許寫入範圍、worker 指派、驗證方式與人閘。整個工廠以四級資訊來源判斷：使用者確認的資訊 > 正典參考（`.manager` 正典檔、opsx 主規格、專案文件）> run 內未確認筆記 > opsx change。`.manager` 只可唯讀。

opsx 路線的順序：

1. 討論：唯讀，不建 run；階段不明時的預設，依 `discuss-first`。
2. 提案：建 run，依 `openspec-propose`、`opsx-propose-guide`、`test-first`；之後提示可選的 change 文件審查。
3. 人閘：使用者檢視 change。
4. 發布派工計畫（`_dispatch-plan.md`），停下等確認。
5. apply：確認後才開始；apply worker 結尾跑 `hard-verify`，依修復政策自修，不得跑 `code-review`；orchestrator 先記錄 `fixed_point`。
6. 機器驗證：另派 Check worker 跑 `code-review`，依資訊來源判斷；orchestrator 逐項核對 finding 後才彙整；審查或 Check 回報的需釐清項目，先依資訊來源自行判斷排除，無法判斷的才彙整成一份決策清單交使用者。
7. 人閘：人工 E2E；orchestrator 呈現功能或流程層級清單並更新 `_review-backlog.md`。之後可能有修正（只複查該修正）或修訂輪（需求變更、E2E 發現）。
8. 人閘：核可 sync／archive；只限 `main`／`master`。
9. commit 訊息建議；使用者明確要求時才代為 commit。
10. 全部完成時建議 `change-log`。

文件同步預設只同步受影響的 README；使用者提到其他文件時，先列清單等使用者確認。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 使用者意圖啟用 | 使用者執行 `/orchestrator-factory`、說工廠模式、要求交給工廠，或使用明確的同義說法 | § Activation |
| E2 | 觸發條件 | 冷啟動交接啟用 | 新 session 被指派特定既有 `.factory/_runs/<run>/`，其 `_status.md` 為 `Stage: await-factory-session` 且 `Factory started: no`；宣告工廠模式、沿用該 run，先讀 `_status.md`、`_intake.md`、`_memory.md` 再選階段；不要求使用者重下啟用指令 | § Activation |
| E3 | 觸發條件 | 不啟用的情形 | 只因 `.factory/` 存在、有舊或已完成的 run、在說明中提到 factory 或 PM，或一般實作要求而沒有工廠意圖或具名冷啟動交接 | § Activation |
| E4 | 邊界條件 | 啟用不等於授權 | 啟用不授權派工、apply、E2E 驗收、sync、archive；所有既有人閘照舊 | § Activation |
| E5 | 觸發條件 | 隱式呼叫設定 | `disable-model-invocation: false`；`agents/openai.yaml` 為 `allow_implicit_invocation: true` | frontmatter；`agents/openai.yaml` |
| E6 | 硬規則 | 使用者指令優先（規則 1） | 依當前回合判斷階段、範圍、選配 skill；不發明固定的全平行排程；解除預設（例如規則 6）也屬此規則，但只能透過使用者在對話中的明確要求 | § Hard rules |
| E7 | 硬規則 | 預設討論（規則 2） | 使用者沒說可執行的階段或無法判斷從哪開始時，進入唯讀討論：不寫入、不派工、不建 `.factory/` run；優先依 `discuss-first` | § Hard rules |
| E8 | 硬規則 | 不得靜默派工（規則 3） | 使用者確認派工計畫（或子集、改派）前，不啟動 apply 或任何可寫入的 worker | § Hard rules |
| E9 | 硬規則 | 同系列一個 worker（規則 4） | 有順序或相依的同系列 change 由同一個具名 worker 負責；獨立 change 可分派不同 worker | § Hard rules |
| E10 | 硬規則 | 驗證分離（規則 5） | apply worker 只可跑 `hard-verify`，從不跑 `code-review`；`code-review` 一律由 orchestrator 另派 Check worker；工廠模式下 apply 內不得有巢狀自我檢查 subagent；change 文件審查也不由 apply worker 做，且審查者 ≠ Check | § Hard rules |
| E11 | 硬規則 | 預設不 commit（規則 6） | 使用者沒明確要求時不執行 `git commit`，只跑 `commit-message-suggestion` 交出建議；明確要求時可依 `commit-message-suggestion` 代為 commit（訊息格式、只 stage 相關檔、回報 hash、未要求不 push）；授權預設只涵蓋當次，使用者明說延續才持續到 run 或 session 結束，有 run 時把範圍與期限記入 `_memory.md` `## User decisions`；不得推定授權；解除不延伸到 worker；worker 永不 commit | § Hard rules |
| E12 | 硬規則 | 不自動載入 grill 類（規則 7） | 一般工廠路徑不自動載入 `grill-me`／`grill-with-docs` | § Hard rules |
| E13 | 硬規則 | worker 模型（規則 8） | worker 預設與 orchestrator 同模型；換模型須詢問並獲同意 | § Hard rules |
| E14 | 硬規則 | 執行環境降級（規則 9） | 優先使用平行 worker 或 subagent；環境無法隔離 worker 時降級，改產出逐 worker 可貼上的指令並等待，不假裝有隔離 | § Hard rules |
| E15 | 硬規則 | 不臆造（規則 10） | worker 不得發明需求；資訊不足時依資訊來源順序唯讀查閱；change 與較高來源衝突時不自行選邊，回 `needs_input`；仍不足時回 `needs_input`（stop-for-human）或寫入已揭露、可逆的本地 `assumptions_made`；不得捏造 API、欄位、行為 | § Hard rules |
| E16 | 硬規則 | 流程配合工作性質（規則 11） | 持久的專案實作走 opsx；非專案實作不強制 OpenSpec 產物或 opsx 階段，改選較小的工廠路線，寫明產物、worker 邊界、驗證、人閘 | § Hard rules |
| E17 | 硬規則 | 寫入階段以外不改專案檔（規則 12） | 討論、協助部署、草擬文件時，orchestrator 不改專案檔、設定檔、進入點程式；需要改程式時說明原因並詢問是否開 propose；例外是使用者口頭授權的修改：有 run 時記入 `_memory.md` `## User decisions`，沒有 run 時在對話中重述授權範圍；非專案路線依其宣告的允許寫入範圍 | § Hard rules |
| E18 | 硬規則 | `.manager` 唯讀（規則 13） | 工作區有 `.manager/` 時，orchestrator 與 worker 可唯讀讀取全部內容，不得寫入；`.manager/_runs/` 只當線索；`.manager` 從不是必要輸入；交接進工廠的內容保持自足 | § Hard rules |
| E64 | 硬規則 | 文件同步（規則 14） | 預設只同步受這次工作影響的 README；使用者提到其他文件（docs 資料夾、`.manager` 檔、巢狀 README、說明文件、交接檔）時，先列出會同步的文件清單並等使用者確認；`.manager` 的變更仍走 manager 交接（規則 13）；不得自行更新其他文件；各文件依對應的 doc-\* skill 撰寫 | § Hard rules |
| E19 | 資訊來源 | 四級優先序 | 適用 orchestrator 與所有 worker，高者勝：1 使用者陳述或確認的資訊（含寫成交接項的已確認決策，例如 `_memory.md` `## User decisions`、冷啟動的 `_intake.md`）；2 正典參考（`.manager` 正典檔、opsx 主規格、專案文件）；3 使用者未確認的 run 筆記（`_notes.md`）；4 opsx change（含生成與 agent 自決部分，可能錯或不清楚） | § Information sources |
| E20 | 資訊來源 | 衝突揭露與清單同步 | 低來源與高來源衝突時高者勝，並在發現處（結果、報告或 `_status.md`）揭露衝突；本清單須與 `code-review` step 3 的正本（master copy）語意一致；§4、§5 的 worker prompt 樣板複述此清單，因為 worker 不載入本 skill | § Information sources |
| E65 | 資訊來源 | 需使用者釐清的項目 | change 文件審查或 Check 回報需使用者釐清的項目時，先依資訊來源優先序逐項嘗試自行判斷，排除已能判斷者並記錄依據；只有無法判斷的才交使用者，依 `need-ask-user-guide` `## Present pending decisions at checkpoints` 彙整成一份決策清單，不逐條轉述 | § Information sources |
| E21 | 資訊來源 | `.manager` 過時處理 | `.manager` 更新較慢可能過時；發現過時或錯誤內容時，在 run 的 `_notes.md` 記錄更正，並寫 `handoff-manager-<topic>.md` 給 manager；worker 回報給 orchestrator，由其寫這兩者；絕不直接改 `.manager` | § Information sources |
| E22 | 角色 | 廠長職責與禁止事項 | 做：判斷階段；離開討論時建立或更新 run；發布具名派工計畫並等待；另派 Check；提案後提示選配 change 文件審查、選用時把回應彙整進 `_status.md`；彙整前依資訊來源核對審查報告；彙整 worker 回報；維護 `_review-backlog.md`；只在明確要求時代為 commit；在每道人閘、stop-for-human、交付當前階段產物後停。不做：應由 worker 做的實作；為只停在討論的 session 建 run；讓 apply 跑 `code-review`；在非 `main`／`master` 不擋就 sync／archive；強制 change 文件審查或把它和 Check 混同；未核對就轉述或採納審查結論；在討論、部署協助、草擬文件時改專案檔；把驗證綠燈當成可出貨；未明確要求就 commit、讓 worker commit；因 report-continue 停整個工廠 | § Role |
| E23 | 角色 | 派工深度 | orchestrator → apply／check worker；不在 apply 內巢狀驗證；Check worker 可依 `code-review` step 5 以平行、合併或依序方式跑兩軸，並回報所用模式 | § Role |
| E24 | 路線選擇 | 專案與非專案實作 | 先選路線再建產物或派工。專案實作：產品行為、原始碼、專案設定、資料或 schema、要成為專案一部分的功能或修正，走完整 opsx，除非使用者明確指定其他核可流程。非專案實作：研究、分析、盤點、規劃、純文件、稽核等，不要求 change 套件，只用相關 skill 與 worker。非專案路線仍須寫明產物、允許寫入、派工時的具名 worker、驗證方式、人工檢查點；可沿用 run 控制機制，但不為了像 opsx 而虛設 propose／apply／sync／archive 階段；分類有歧義且實質影響流程時先唯讀討論並詢問 | § Workflow selection |
| E25 | 流程步驟 | opsx 階段表 | 討論（`discuss-first`，不建 run）→ 提案（`openspec-propose`、`opsx-propose-guide`、`test-first` 必用；建 run 並提示選配審查）→ 人閘：change（預設無 skill；選配審查不自動要求）→ 派工計畫（提案後可立即發布，審查不阻擋寫計畫，等確認）→ apply（`openspec-apply-change`、`opsx-apply-guide`、`test-first`、結尾 `hard-verify`）→ 機器驗證（Check worker 跑 `code-review`，change 為審查對象）→ 人閘：E2E → 人閘：archive → sync／archive（`openspec-sync-specs`、`openspec-archive-change`，非主幹擋下）→ commit 建議 → change log（完全完成時建議） | § Factory stages |
| E26 | 選配 | 選配 skill 僅點名時載入 | 只在使用者於指令中點名時載入（例：`ponytail`、`karpathy-guidelines`、`opsx-health-check`、`code-to-docs`、`thought-palette-extract`、doc 類指引、`change-review-request`、`change-review-response`）；例外：`test-first` 在 propose 永遠啟用，apply 依 `opsx-apply-guide` 使用；不在本 skill 貼這些 skill 的全文 | § Optional skills |
| E27 | 選配 | change 文件審查定位 | 只在使用者點名或選擇提案後的提示時進行，從不自動要求；主要位置在提案後、與人閘 change 並行、apply 前；回應審查者 ≠ apply worker ≠ apply 後的 Check | § Optional skills |
| E28 | 選配 | 多 agent 協作 | `peer-agent-coordination` 供共用 run 目錄的 peer session 使用，成本高；不自行啟用，使用者提及或與使用者的協作討論需要時才啟用（見其 `## 0. When to enable`），不因 run 結構、其他 skill 的引用或 worker 數量而啟用；與指派一個 worker 多項工作、或多個 worker 同一工作的一般 subagent 派工不同 | § Optional skills |
| E29 | 修復政策 | 三層分類（N=3） | 不把所有問題標 `blocked`。self-fix：指派 change 範圍內的單元測試／lint／編譯失敗，apply worker 修實作並重跑，每個 change 最多 3 輪，仍在 change 文件範圍內，測試異動依 `opsx-apply-guide` 防作弊。report-continue：範圍外發現、略過的檢查類別、已記於 `tasks.md` 的小偏離、非阻擋註記，寫入結果或 `_memory.md` 後繼續其餘指派。stop-for-human：需求矛盾、缺秘密或環境、設計無法實作、自修 3 輪仍紅、需開新 change 的語意污染、`needs_input`，設 `blocked`／`needs_input`、寫 run 檔、附選項回報並等待，不得默默擴大範圍 | § Repair policy |
| E30 | 修復政策 | self-fix 防作弊 | self-fix 是修實作；哪些測試異動允許，以 `opsx-apply-guide` `## Test changes (anti-cheat)` 為唯一來源；修訂輪中的斷言調整依 `opsx-apply-guide` `## Amendment rounds`（流程與閘見本 skill 修訂輪） | § Self-fix anti-cheat |
| E31 | 修復政策／產物格式 | `needs_input` 處理與四選單 | 轉達前先查任務指定的紀錄（已確認的 run 決策、`.manager`、專案文件），已有答案就依紀錄恢復並揭露依據，不再問使用者（準則依 `need-ask-user-guide`）；否則轉達使用者並寫 `_needs-input.md`：一行原因 + 建議四選單（① 補定義 ② 允許唯讀查 repo／環境後恢復 ③ 佔位樣板 ④ 略過並記為延後、不宣稱完成），可附情境選項；用編號讓使用者回覆選號；③ 未經使用者選定不得執行，在那之前規則 10 仍適用 | § needs_input menu |
| E32 | 覆寫 | 對 `hard-verify` 的工廠覆寫 | 只在工廠模式：(1) apply 期間 `hard-verify` 是 apply worker 的出口閘，失敗時走 self-fix，覆寫原 skill「不自動修」，只限範圍內實作修正；Check worker 唯讀、不得自動修。(2) 覆寫原 skill「只在對話回報」：apply worker 必須把證據寫入 run 的 `hard-verify-<worker>.md`，不得寫入 `openspec/**`、change 套件或產品原始碼樹。(6) 覆寫原 skill「只在使用者明確呼叫時執行」：使用者確認派工即授權每個 apply worker 在每個 change（或其負責的批次）結束前執行；Check worker 不跑 | § Factory overrides of verify skills |
| E33 | 覆寫 | 對 `code-review` 的工廠覆寫 | (3) Spec 依據：change 是審查對象，依資訊來源判斷（使用者決策、已確認的 run 交接項、`.manager`、opsx 主規格、專案文件）；change 與較高來源衝突時標 `change-design-flaw` 交使用者；不問使用者 Spec 路徑，不搜尋資訊來源以外的來源（例如 issue tracker）；change 文件缺漏時 Spec 標為 blocked／無法審查並繼續 Standards，不自行編造 Spec。(4) orchestrator 必須在每個 Check prompt 注入 `fixed_point`，已知時記入 `_memory.md`（通常是 apply 批次前的 SHA／ref 或與 `main`／`master` 的 merge-base）；因 worker 不 commit，它是工作樹基準，diff 涵蓋未提交與未追蹤檔；有提供時 Check 不問使用者。(5) Check 報告寫入 run 的 `check-<change-id>-code-review.md`，不得寫入 change 套件或 `openspec/**`；工廠模式下只有另派的 Check worker 可跑 `code-review`。(7) Check 報告每個 finding 帶 `code-review` 定義的分類：`violates-change`、`conforms-but-flawed`、`change-design-flaw`（只用於 Spec 軸） | § Factory overrides of verify skills |
| E34 | run 工作區 | 建立時機與初始化 | 離開討論進入 propose、apply、verify 或任何寫入／派工時建立 run；只停在唯讀討論並結束則不建；建立第一個 run 時，若 `.factory/.gitignore` 不存在，建立單行 `_runs/`（run 是討論與編排的工作空間，太雜不追蹤；收斂結果在 opsx change 與規格） | § When to create |
| E35 | run 工作區 | 路徑與根目錄 | `.factory/_runs/<YYYY-MM-DD>-<slug>/`；slug 只用 `[a-z0-9-]+`，不合法字元去除或替換，資料夾名不含空白或中日韓文字；只有 orchestrator 建 run，worker 不得另建同層 run；`.factory/` 根目錄只放 `.gitignore`、`_review-backlog.md`、`_runs/`；worker 不得寫 `_review-backlog.md` | § Path |
| E36 | run 工作區 | slug 唯一性 | 一個工廠主題或一段工廠對話一個 slug；同日不同主題用不同 slug；完整路徑在 `_runs/` 下唯一，由 orchestrator 負責；目錄已存在時：使用者要恢復該 run 就沿用並先讀 `_status.md`，新主題或不明則不覆蓋，改用新 slug（例如加 `-2`）或詢問使用者；slug 以工作內容命名，不用 `work`、`task` 等泛稱 | § Slug uniqueness |
| E37 | run 工作區 | 內容範圍 | 放編排狀態、派工計畫、worker 結果、驗證報告、跨 worker 記憶；不放產品原始碼；不取代 `openspec/**` 規格或 change 套件；驗證報告只能依工廠覆寫放在 `run_dir`，不得在 repo 其他地方當檢查草稿 | § What belongs here |
| E38 | run 工作區 | 跨 run 審查待辦 | `.factory/_review-backlog.md` 累積跨 run 的人工審查項目，orchestrator 是唯一寫者；依功能或業務流程分組，畫面驗收依畫面分組；每項連回來源 run，同一功能再變更時合併並更新來源；使用者回報通過時記入來源 run 的 `_status.md` 後移除該項；只收需要人判斷的項目，依 `need-ask-user-guide` 排除自動測試或 hard-verify 已涵蓋的項目與簡單邏輯檢查 | § Cross-run review backlog |
| E39 | 產物格式 | 檔名慣例 | 控制／交接 `_*.md`：orchestrator 寫，prompt 允許時 worker 才可追加，用於控制面與工廠內部暫存交接；worker 產物 `<role>-<id>-*.md`（不以 `_` 開頭）：由該 worker 寫；跨方交接 `handoff-<recipient>-<topic>.md`：放寄件方 run 根目錄，由 orchestrator 寫，名稱只用小寫英數與連字號，檔頭三行 `Source run:`、`Recipient:`、`Date:`；收件方在自己的 run 記錄處理，不回寫寄件方 run | § File conventions |
| E40 | 產物格式 | 必要控制檔 | `_status.md`：run 建立後一律存在，每次階段轉換更新，內容為階段、分支、worker、Blockers／Decisions needed／Reminders、修訂輪、閘事件、最新產物指標；`_dispatch-plan.md`：發布派工計畫時，存放等待或已確認的具名 worker 表；`_memory.md`：有跨 worker 事實需保存時，主摘要加所有後續 worker 該讀的共享事實（決策、路徑、環境），使用者確認的決策放 `## User decisions`，保持簡短 | § File conventions |
| E41 | 產物格式 | 選用控制檔 | `_handoff-<worker>.md`：給單一 worker 的工廠內部暫存交接（恢復、部分進度），不是跨方交接；`_needs-input.md`：原因加四選單；`_notes.md`：使用者未確認的討論筆記，以及對過時 `.manager` 內容的更正（資訊來源第 3 級） | § File conventions |
| E42 | 產物格式 | 控制檔寫入方式 | `_status.md`、`_memory.md`、`_dispatch-plan.md`、`_review-backlog.md` 以編輯工具原地更新；確實需要追加時先確認相同內容不存在；不得以 shell 重導盲目追加 | § File conventions |
| E43 | 產物格式 | worker 產物範例 | `apply-w1-result.md`（`FACTORY_APPLY_RESULT_V1`）、`hard-verify-w1.md`、`check-<change-id>-code-review.md`、`change-review-request-NN.md`（選配審查簡報）、`change-review-response-NN.md`（選配審查裁決，`NN` 成對） | § File conventions |
| E44 | 產物格式 | worker prompt 共同要求與跨 run 續用 | 每份 prompt 含 `run_dir: .factory/_runs/<…>/`，存在時 worker 必讀 `_memory.md`、`_status.md`；worker 依資訊來源判斷，可唯讀讀 `.manager`；預設只在當前 run 工作；具名 worker 可跨 run 續用，prompt 須重申新 run 的 `run_dir`、限制與要讀的控制檔，並聲明前一個 run 未記錄的脈絡不沿用；對話只放短摘要，細節留在 `run_dir` | § File conventions |
| E45 | 流程步驟 | 進入工廠模式 | 1 宣告工廠模式開啟；2 判斷是使用者意圖、冷啟動交接或恢復，有提供時確認 `run_dir`；3 行動前讀該 run 的 `_status.md` 與相關 intake、memory、dispatch、最新結果，冷啟動先讀 `_intake.md`、`_memory.md`，需要時依資訊來源唯讀查 `.manager`，`.manager` 不存在不阻擋；4 分類專案或非專案實作並選路線；5 解析起訖階段或產物、範圍、選配 skill、模型偏好、驗證需求；6 階段、產物、範圍或分類缺漏或模糊時唯讀討論，說明原因，解決前不建另一個 run、不 propose、不 apply、不派工 | §1 |
| E46 | 流程步驟 | 提案 | 使用者指示 propose 時（討論已定或明確略過討論）：確保 run 存在，新建時初始化 `_status.md` 與空的 `_memory.md`；依 `openspec-propose`、`opsx-propose-guide`、`test-first`；有 change 後進 §3，不啟動 worker；提示（非閘）選配 change 文件審查是可行的下一步之一，其他下一步仍在（檢視 change、確認派工等）；預設不要求先審查才派工 | §2 |
| E47 | 流程步驟 | change 文件審查流程 | 只在使用者選用時：1 確保 `run_dir/change-review-request-NN.md` 存在（依 `change-review-request`）；2 等另一位審查者寫 `change-review-response-NN.md`；3 讀裁決與建議下一步，依資訊來源逐項標示採納、誤報排除（附依據）或與較高來源衝突，需使用者釐清的項目依 E65 處理，彙整進 `_status.md`；4 下一步是 orchestrator 核對後的建議（`confirm dispatch`／`amend change`／`needs_input`），不照抄回應；回應含 `change-design-flaw` 時裁決至少為 `needs user clarify`；裁決不是 `ready to apply` 時，派工確認不視為綠燈，直到使用者修正、釐清或明確覆寫 | §2 Optional change-doc review |
| E48 | 產物格式 | 審查者 prompt 樣板 | 欄位：`role`（change 文件審查者，非 apply、非 Check）、`run_dir`、`request`、`skills: change-review-response`、`return`（寫 `change-review-response-NN.md`）、`constraint`（審查對象為 change 文件；有疑問時唯讀查 request 列出的決策脈絡來源，不足時可唯讀查其他來源並在 Context consulted 標 "not in brief"；不 apply；不審產品程式碼） | §2 Reviewer prompt |
| E49 | 人閘／流程步驟 | 派工計畫（必停） | change 建立後（或使用者要求 apply 既有 change 時）立即發布具名 worker 指派、寫 `_dispatch-plan.md`、更新 `_status.md` 並停；選配審查不阻擋寫計畫 | §3 |
| E50 | 流程步驟 | 指派規則 | 獨立 change 可建議不同 apply worker（環境允許時平行）；同系列有序或相依的 change 由一個 apply worker 負責整組；worker 命名清楚（如 `W1`、`W2`），列出確切 change id 與順序；依使用者指令與套件內的相依說明，不套固定平行樣板；使用者可指示一個 worker 多項工作或多個 worker 同一工作（規則 1 覆寫規則 4 的預設）；可沿用前一個 run 的具名 worker，在計畫的 `Reused workers` 註明來源 run | §3 Assignment rules |
| E51 | 產物格式 | 派工計畫表樣板 | 標題 `## Dispatch plan (awaiting confirmation)`；表格欄位 Worker、Role、Changes（依序）、Rationale；另列 Parallelism、Optional skills named by user、Check workers（apply 後派，依資訊來源判斷）、Reused workers、run_dir、Next（全部確認／部分確認／改派／選配審查）；之後等使用者確認全部、子集或改派；回報計畫不等於許可；略過審查一律允許；選用審查且最新回應不是 `ready to apply` 時，確認不視為綠燈，直到修正、釐清或明確覆寫 | §3 Plan table |
| E52 | 流程步驟 | apply | 只啟動使用者核可的 worker／change；優先使用平行 worker 或 subagent，每個具名 apply worker 一份 prompt；prompt 簡短，以 change 文件與 `run_dir` 檔冷啟動，不貼長對話；apply worker 在每個 change（或其批次）結束前必跑 `hard-verify`、遵守修復政策、結果寫入 `run_dir`、不得跑 `code-review`；開始前或開始時 orchestrator 在 `_memory.md` 記錄 `fixed_point` | §4 |
| E53 | 產物格式 | apply worker prompt 樣板 | 欄位：`worker`、`role: apply`、`changes`（依序）、`run_dir`、`skills`（`openspec-apply-change`、`opsx-apply-guide`、`test-first`、`hard-verify`）、`repair`（self-fix N=3、防作弊、report-continue、stop-for-human／`needs_input` 附建議選單）、`sources`（四級優先序，與較高來源衝突回 `needs_input`，`.manager` 唯讀）、`reuse`（只用於續用 worker，聲明新 `run_dir` 取代舊 run、舊 run 未記錄脈絡不沿用）、`return`（寫 `apply-<worker>-result.md` 與 `hard-verify-<worker>.md`）、`constraint`（依 change 文件；不跑 code-review；不 sync／archive／commit；不發明需求；回報 out_of_scope；完成指派即停）；選用 `notes` | §4 Apply worker prompt |
| E54 | 產物格式 | `FACTORY_APPLY_RESULT_V1` | 欄位：`worker`、`changes`、`status`（ok／partial／blocked／needs_input）、`summary`、`self_fix_rounds_used`；`## per_change` 每個 change 列 `tasks`、`unit_tests`、`hard_verify`、`deviations`、`assumptions_made`、`developer_verification`（依 `opsx-apply-guide` 列功能或流程層級、需人判斷的項目，排除測試或 hard-verify 已涵蓋者，或指向 `tasks.md`）；另有 `## blocked`、`## out_of_scope`；`blocked`／`needs_input` 只用於 stop-for-human，report-continue 用 `partial` 加 out_of_scope 或 deviations | §4 Apply worker return |
| E55 | 流程步驟 | 機器驗證 | apply 批次完成且結果在 `run_dir` 後：1 另派 Check worker，不得沿用 apply worker 的身分或 session；2 每個 Check worker 只跑 `code-review`（唯讀），負責一或多個 change，寫 `check-<change-id>-code-review.md`；3 change 為審查對象，依資訊來源判斷，每個 finding 帶分類，不搜尋 issue tracker；4 orchestrator 從 `_memory.md` 取（或當下解析）`fixed_point` 傳入；5 彙整前逐項核對 finding：採納、誤報排除（附依據）或與較高來源衝突，需使用者釐清的項目依 E65 處理，不得未經核對轉述或採納，之後彙整進 `_status.md` 與簡短對話摘要；6 綠燈 ≠ archive 許可，也不取代人工 E2E；工廠模式不跑 `impl-verify`，由 `code-review` 取代；之後停在人工 E2E | §5 |
| E56 | 產物格式 | Check worker prompt 樣板 | 欄位：`worker`、`role: check`、`changes`、`run_dir`、`skills: code-review`、`fixed_point`（取自 `_memory.md`，可為工作樹基準，diff 含未提交與未追蹤檔）、`recheck_scope`（選用，只用於複查：修正處理的 finding 與觸及的檔案或 hunk，只審這些）、`review_basis`（四級優先序，不搜尋 issue tracker）、`amendment`（選用，只用於大規模修訂：依 `opsx-apply-guide` `## Amendment rounds` 核對 `tasks.md` 列出的每項改寫或刪除測試）、`return`（Standards 與 Spec 兩段，寫明執行模式）、`constraint`（唯讀；可讀含 `.manager` 的列出來源；finding 標分類；不修改；不擁有 hard-verify；不 sync／archive／commit；不要求 apply worker 自證；不問 Spec 路徑，也不問已提供的 `fixed_point`） | §5 Check worker prompt |
| E57 | 流程步驟 | 修正後複查 | 修正開始前 orchestrator 在 `_memory.md` 記錄複查用 `fixed_point`：修正前工作樹的快照 ref（例如 `git stash create`，工作樹乾淨時用 `HEAD`），無法快照時記錄修正觸及的檔案清單；並記錄修正範圍（處理的 finding、觸及的檔案或 hunk），因為快照不含未追蹤檔、檔案清單會帶入先前未提交內容，範圍才能縮小複查；複查只涵蓋該修正，派 Check worker 並以 `recheck_scope:` 傳入範圍；只改文件、只調測試資料，或使用者說不需要時可省略，省略與原因記入 `_status.md` | §5 Re-check after fixes |
| E58 | 人閘 | 四道人閘 | 檢視 change（提案後；提示選配審查，從不自動要求）；確認派工（派工計畫後；確認、子集或改派前不派 worker；選用審查且回應非 `ready to apply` 時暫緩綠燈）；人工 E2E（Check 完成後；呈現各 change 功能或流程層級清單、更新 `_review-backlog.md` 後等待，移除使用者回報通過的項目）；sync／archive（明確核可）。另在 stop-for-human 時停；`needs_input` 以四選單轉達並寫 `_needs-input.md`；report-continue 不停整個工廠 | §6 |
| E59 | 流程步驟 | 修訂輪 | 適用 apply 後、archive 前的需求變更或 E2E 發現。意圖與範圍不變 → 修訂既有 change；新能力或語意改變 → 開新 change。change 文件標註依 `opsx-propose-guide` `## Amendments`，可改哪些既有斷言依 `opsx-apply-guide` `## Amendment rounds`；輪次記入 `_status.md`，Stage 沿用既有值。使用者直接要求的修訂免回檢視 change 閘，但記入 `_memory.md` `## User decisions`；orchestrator 發起的修訂回到檢視 change 閘。派工確認仍適用（規則 3），使用者要求修訂並指名 worker 即視為確認。大規模修訂由 orchestrator 標記並交給 worker，Check worker 以 `amendment:` 逐項核對 worker 列出的測試變更 | §6 Amendment rounds |
| E60 | 邊界條件 | sync／archive 條件 | 只在人工 E2E 後（含使用者指示的修正）且使用者明確核可 sync 與 archive：1 偵測目前分支；2 不是 `main` 也不是 `master` → 擋下、警告在功能分支執行會損害 `main`／`master` 上的主規格檔，並停止；3 在 `main`／`master` 且已核可 → 依 `openspec-sync-specs`、`openspec-archive-change`。人工驗證項目未勾時，使用者口頭確認即可歸檔，確認內容與時間記入 `_status.md`；不得替使用者勾選或宣稱已驗證 | §7 |
| E61 | 流程步驟 | commit 建議與 change-log | 使用者要求或批次收尾時跑 `commit-message-suggestion` 並把文字交給使用者，只在明確要求時代為 commit（規則 6）；整個工廠工作完全完成時建議 `change-log`，再依該 skill 把輸出交給使用者 | §8 |
| E62 | 產物格式 | 狀態摘要樣板 | `## Factory status`：Stage（discuss／await-factory-session／propose／await-dispatch／apply／machine-verify／await-e2e／await-archive／done）、run_dir（或只討論時為 none）、Branch（是否允許 sync／archive）、Workers、Change-doc review（none 或略過／等待回應／ready to apply／needs doc fix／needs user clarify）、Blockers（最多 3 點；已記錄但仍阻擋的決策一律列出並附紀錄指標，不計入上限）、Decisions needed（尚未記錄的阻擋決策）、Reminders（非阻擋提醒）；送出前查任務指定紀錄（`.manager`、文件、run）；篩選準則依 `need-ask-user-guide` `## Present pending decisions at checkpoints` | §9 |
| E63 | 流程步驟 | 停止與恢復 | 每道人閘、stop-for-human、交付當前階段產物後停止；只依使用者指示恢復；恢復時讀 run 的 `_status.md` 與最新產物，不只依賴對話記憶 | §10 |

## 3. 其他

- **`_intake.md` 不在檔案慣例表**：E2、E19、E45、E53、E56 都引用 `_intake.md`（冷啟動交接寫入的已確認決策），但 E40、E41 的必要與選用控制檔表都沒有列它，也沒有寫明它由誰建立、工廠是否可改寫。README 的檔案樹列了它，註明由 PM 交接建立且為選用，本文沒有對應說明。
- **Stage 列舉不涵蓋非專案路線**：E62 的 Stage 只有 opsx 路線的值；E24 的非專案路線沒有對應的階段表示法。修訂輪與修正後複查明寫「Stage 沿用既有值」，屬刻意設計，不算缺口。
- **finding 分類的軸別註記不完整**：覆寫 (7)（E33）只在 `change-design-flaw` 後註明「只用於 Spec 軸」；`code-review` 1.1 的 Finding tags 已把 `violates-change` 也限為只用於 Spec 軸（Standards 軸一律 `conforms-but-flawed`）。本 skill 沒有寫錯，但只標了其中一個。
- **跨 skill 引用的章節目前都存在**：`opsx-apply-guide` `## Test changes (anti-cheat)`、`## Amendment rounds`，`opsx-propose-guide` `## Amendments`，`need-ask-user-guide` `## Present pending decisions at checkpoints`，`code-review` step 3（資訊來源）、step 5（執行模式）與 Finding tags；反向引用方面，`opsx-apply-guide` §6 引用本 skill 規則 14。
- **README（`orchestrator-factory-readme.md`）與本文仍不一致處**：
  - 「不會啟用」只列 `.factory/` 存在、有舊 run、對話提到工廠，沒有本文 E3 的「說明中提到 PM」與「一般實作要求而無工廠意圖」。
  - README 沒有提到規則 7（不自動載入 grill 類）。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/orchestrator-factory.md`（前版 version 1.6，元素 E1–E42）。

新增：

- E17 規則 12：寫入階段以外 orchestrator 不改專案檔，口頭授權的例外與記錄方式。
- E18 規則 13：`.manager` 唯讀、`_runs/` 只當線索、不是必要輸入。
- E19 資訊來源四級優先序。
- E20 衝突揭露，以及與 `code-review` step 3 同步的要求。
- E21 `.manager` 過時時寫 `_notes.md` 與 `handoff-manager-<topic>.md`。
- E28 `peer-agent-coordination` 只在使用者明確指示時啟用。
- E34 建立第一個 run 時初始化 `.factory/.gitignore`。
- E38 跨 run 審查待辦 `_review-backlog.md`。
- E41 選用控制檔新增 `_notes.md`（前版只有 `_handoff-<worker>.md`、`_needs-input.md`）。
- E42 控制檔以編輯工具原地更新，不以 shell 盲目追加。
- E47 change 文件審查的四步流程獨立成元素（前版併在 E21）。
- E48 審查者 prompt 樣板獨立成元素（前版併在 E35），並新增脈絡補查許可與 "not in brief" 標示。
- E50 指派規則：使用者可覆寫規則 4、可沿用前 run 的具名 worker。
- E57 修正後複查：快照 ref 或檔案清單、`recheck_scope`、可省略的條件。
- E59 修訂輪：修訂或開新 change 的判準、閘、派工確認、大規模修訂。

修改：

- E6（前版 E5）規則 1：補上「解除預設只能透過使用者在對話中的明確要求」。
- E10（前版 E9）驗證分離：補上審查者 ≠ Check。
- E11（前版 E10）規則 6：由「絕不 commit」改為「預設不 commit，明確要求時可依 `commit-message-suggestion` 代為 commit」，加授權範圍、期限記錄與「worker 永不 commit」。
- E15（前版 E14）不臆造：加依資訊來源唯讀補查，與較高來源衝突時回 `needs_input`。
- E22（前版 E16）角色表：新增核對審查報告、維護 `_review-backlog.md`、不在討論等情境改專案檔、明確要求時代為 commit；「只在 stop-for-human 時停」改為每道人閘、stop-for-human、交付產物後停，不因 report-continue 停。
- E23（前版 E17）派工深度：加 Check worker 可依 `code-review` step 5 選擇執行模式。
- E27（前版 E21）change 文件審查定位：流程部分移到 E47。
- E30（前版 E26）self-fix 防作弊：由本 skill 自訂的斷言規則改為以 `opsx-apply-guide` `## Test changes (anti-cheat)` 為唯一來源，修訂輪依 `## Amendment rounds`。
- E31（前版 E27）`needs_input`：加轉達前先查任務指定紀錄，已有答案就依紀錄恢復。
- E32、E33（前版 E28）工廠覆寫：拆為 `hard-verify` 與 `code-review` 兩元素；Spec 依據由「只認 `design.md`／`proposal.md`」改為依資訊來源，衝突標 `change-design-flaw`；新增 (6) 派工確認即授權 hard-verify、(7) finding 分類；`fixed_point` 說明為工作樹基準、含未追蹤檔。
- E35（前版 E29）路徑：由 `.factory/<YYYY-MM-DD>-<slug>/` 改為 `.factory/_runs/<YYYY-MM-DD>-<slug>/`，並規定 `.factory/` 根目錄只放三項。
- E37（前版 E31）內容範圍：補上驗證報告只能依工廠覆寫放在 `run_dir`。
- E39（前版 E32）檔名慣例：新增跨方交接 `handoff-<recipient>-<topic>.md` 與其檔頭三行。
- E40（前版 E33）必要控制檔：`_status.md` 內容改為 Blockers／Decisions needed／Reminders、修訂輪、閘事件；`_memory.md` 加 `## User decisions`。
- E44（前版 E34）worker prompt 共同要求：加依資訊來源判斷、可唯讀讀 `.manager`、具名 worker 跨 run 續用的重申要求。
- E51（前版 E22）派工計畫表：新增 `Reused workers` 列，Check workers 註明依資訊來源判斷。
- E53（前版 E35 的 apply 部分）apply prompt：新增 `sources`、`reuse` 欄。
- E54（前版 E36）`FACTORY_APPLY_RESULT_V1`：`developer_verification` 改為功能或流程層級、需人判斷的項目，排除測試已涵蓋者。
- E55（前版 E24）機器驗證：Spec 依據改為資訊來源；新增彙整前逐項核對 finding；finding 帶分類。
- E56（前版 E35 的 check 部分）Check prompt：新增 `recheck_scope`、`review_basis`、`amendment` 欄，`fixed_point` 說明工作樹基準。
- E58（前版 E37）人閘：E2E 閘改為 orchestrator 呈現功能或流程層級清單並更新 `_review-backlog.md`。
- E60（前版 E38）sync／archive：新增人工驗證項目未勾時以口頭確認歸檔並記錄，不代勾。
- E61（前版 E39）commit 建議：加明確要求時代為 commit。
- E62（前版 E40）狀態摘要：Stage 加 `await-factory-session`；「阻塞或待決 ≤3」改為 Blockers／Decisions needed／Reminders 三欄與篩選規則。
- E45（前版 E18）、E46（前版 E19）、E52（前版 E23）：文字細化（`.manager` 唯讀查閱不阻擋啟用、提示其他下一步、`fixed_point` 記錄時機改為開始前或開始時），內容沒有實質改變。

移除：

- 無整條移除。前版 E26 的自訂防作弊規則與前版 E28(3) 的「Spec 只認 change 文件、不搜尋文件 PRD」內容已被取代，列於上方修改。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.7，last_updated 2026-10-20T14:08:54）。元素編號沿用，新元素接續編號並依章節位置插入。

新增：

- E64 規則 14 文件同步：預設只同步受影響的 README，其他文件先列清單等使用者確認，依 doc-\* skill 撰寫（F6）。
- E65 需使用者釐清的項目：先依資訊來源自行判斷排除，無法判斷的才彙整成一份決策清單（F24）。

修改：

- E13 規則 8：刪除 Multitask／subagent 的工具描述，只寫 worker 預設與 orchestrator 同模型（F4）。
- E14 規則 9：「偏好 Cursor Multitask／平行 subagent」改為「優先使用平行 worker 或 subagent」（F4）。
- E20 資訊來源同步：改寫為與 `code-review` step 3 正本語意一致（F5）。
- E27 change 文件審查定位：刪除從作用中專案 `.agents/skills/` 載入兩個 skill 的路徑規定（F3）。
- E28 多 agent 協作：「只在使用者明確指示時啟用」改為不自行啟用，使用者提及或協作討論需要時才啟用（peer 啟用統一）。
- E47 change 文件審查流程：步驟 1 刪除「作用中專案」；步驟 3 加入需釐清項目依 E65 處理（F3、F24）。
- E48 審查者 prompt 樣板：`skills` 欄刪除「從作用中專案載入」（F3）。
- E52 apply：「偏好 Multitask／subagent」改為「優先使用平行 worker 或 subagent」（F4）。
- E55 機器驗證：步驟 5 加入需釐清項目依 E65 處理（F24）。

移除：

- 無元素移除。

§3 變動：

- 移除「資訊來源同步的措辭強度不同」：`code-review` 正本與本 skill 都改為語意一致。
- 移除「change 文件審查的載入位置沒有後備」：載入路徑規定已刪除。
- 移除「執行環境用詞綁定特定工具」：規則 9 與 §4 已不寫特定產品名稱。
- README 不一致項：修訂輪流程圖、檔案樹缺 response 與 `_intake.md`、`_*.md` 寫者、規則 8／9／12 與 peer 啟用說明均已同步，移除；保留「不會啟用」的缺項與規則 7。
- 新增「finding 分類的軸別註記不完整」。
- `_intake.md` 項補記 README 已有、本文沒有的建立者說明。
