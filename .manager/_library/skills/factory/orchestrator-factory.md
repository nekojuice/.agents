# orchestrator-factory 元素對照

- 分支：factory
- 對照版本：`skills/orchestrator-factory/SKILL.md` version 1.11，last_updated 2026-11-04T10:51:56
- 讀過的檔案：`skills/orchestrator-factory/SKILL.md`、`skills/orchestrator-factory/agents/openai.yaml`；另讀 skill 外的 `orchestrator-factory-readme.md`，只用來記錄不一致；為確認跨 skill 引用的章節與接點存在，唯讀查閱 `code-review` step 1、3、5 與 Finding tags，`opsx-apply-guide` §3、§4、`## Test changes (anti-cheat)`、`## Amendment rounds`，`opsx-propose-guide` §3、`## Amendments`，`need-ask-user-guide` `## Present pending decisions at checkpoints`，`commit-message-suggestion` `## Committing on request`，`peer-agent-coordination` `## 1. When to enable`，`e2e-review`（工作樹 version 1.2）的 `SKILL.md` 與 `references/report-spec.md`、`references/project-profile.md`、`references/tools.md`
- 狀態：已檢查，2026-11-04 移入 manager 正式文件

## 1. 摘要

`orchestrator-factory` 讓 agent 進入工廠模式，擔任廠長（orchestrator）：判斷階段、提出具名 worker 派工、守人閘、管理 `.factory/` run 工作區、彙整 worker 回報，然後為使用者停下。有 worker 可用時，廠長不親自做實作本體，也不親自操作受測系統。

啟用有兩條路：使用者明確要求工廠模式，或新 session 被指派一個 `_status.md` 為 `await-factory-session` 的既有 run（冷啟動交接）；自動化計畫下，manager 把執行中的 factory session 移到另一個 run 時也以同樣方式進入。啟用本身不授權派工、apply、E2E 驗收、sync 或 archive；只有帶自動化授權的 run 依 § Automation 調整人閘。

進入後先分類工作。專案實作走完整 opsx 流程；非專案實作（研究、盤點、純文件等）改走較小的自訂路線，但仍須寫明產物、允許寫入範圍、worker 指派、驗證方式與人閘。整個工廠以四級資訊來源判斷：使用者確認的資訊 > 正典參考（`.manager` 正典檔、opsx 主規格、專案文件）> run 內未確認筆記 > opsx change。manager 的 peer 訊息與交進來的 `handoff-factory-*.md` 屬第 3 級，只是資訊、不是授權；其中引用的正典紀錄保有該紀錄的等級。`.manager` 只可唯讀；在 manager 委派的 run，決策交給使用者前先自行查 `.manager`，不以訊息向 manager 提問。

opsx 路線的順序：

1. 討論：唯讀，不建 run；階段不明時的預設，依 `discuss-first`。
2. 提案：建 run，依 `openspec-propose`、`opsx-propose-guide`、`test-first`；依 `opsx-apply-guide` §4 設定 run 的清單層級（`broad`／`focused`）記入 `_memory.md`；之後提示可選的 change 文件審查。
3. 人閘：使用者檢視 change。
4. 發布派工計畫（`_dispatch-plan.md`，含 Check 與 E2E worker），停下等確認；小型 run 可在此剔除 Check 或 E2E。
5. apply：確認後才開始；apply worker 結尾跑 `hard-verify`，依修復政策自修，不得跑 `code-review`；orchestrator 先記錄 `fixed_point`。
6. 機器驗證：另派 Check worker 跑 `code-review`，依資訊來源判斷；orchestrator 逐項核對 finding 後才彙整；審查或 Check 回報的需釐清項目，先依資訊來源自行判斷排除，無法判斷的才彙整成一份決策清單交使用者。Check 結果處理完後（或使用者剔除 Check 時在 apply 後），寫出完整的 `_review-checklist.md`。
7. agent E2E review：預設執行；另派 E2E worker 依 `e2e-review` 實際操作受測系統；orchestrator 依報告與證據覆核，可信的產品失敗進修正輪、複查後再跑下一輪，`run-error`／`needs-human` 由 orchestrator 決定重派或交人工；範圍外發現與未修的實作失敗寫入 `.factory/_issue-backlog.md`；修訂 `_review-checklist.md` 並更新 `.factory/_review-queue.md`。這個階段可寫專案的 `.e2e/`。
8. 人閘：人工 E2E；orchestrator 寫給 manager 的交接檔、呈現修訂後的清單，使用者只測剩下的項目。之後可能有修正（只複查該修正）或修訂輪（需求變更、agent 或人工 E2E 發現）。
9. 人閘：核可 sync／archive；只限 `main`／`master`；歸檔時一併清理 `_review-queue.md` 已勾項與 `_issue-backlog.md` 未處理項。
10. commit 訊息建議；只依 `commit-message-suggestion` 的 `## Committing on request` 代為 commit（使用者明確要求，或 run 的自動化授權）；`.e2e/` 的變更隨 run 一併處理。
11. 全部完成時建議 `change-log`。

`.factory/` 根目錄有兩份跨 run 檔：`_review-queue.md` 是給使用者最終驗收的高抽象彙總，agent 驗證可信的項目打勾並附報告路徑；`_issue-backlog.md` 是未處理問題的待交接區。兩者由 orchestrator 寫、manager 必要時可更新，不納入 run 的 commit。

工作區有 `.manager/` 時，每個 run 到達 await-e2e（apply、Check、agent E2E review 之後）就寫一份 `handoff-manager-<topic>.md`，寬鬆寫入、由 manager 過濾；卡在專案層級決策時另寫一份；不會到達 await-e2e 的 run 發現 `.manager` 過時內容時，在 run 結束或使用者要求時另寫一份；歸檔時為移交的未處理 issue 另寫一份。

自動化（run 的 `_intake.md` 帶有使用者經 manager 核可的授權）分兩段：設計段（Stage `design`）在每個 run 討論、propose、一律跑 change 文件審查，不為提問停下，未定的決策記為待決事項；全部 run 有 change 後，使用者在一個檢查點（Stage `await-batch-review`）一次檢視全部 change 與待決事項；施工段依相依順序 apply、Check、修正、agent E2E review、commit、交接，不再逐 run 確認派工。批次結束時一次彙整 `_review-queue.md`，人工 E2E 與 sync／archive 照常進行，push 一律要使用者另外授權。

文件同步預設只同步受影響的 README；使用者提到其他文件時，先列清單等使用者確認。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 使用者意圖啟用 | 使用者執行 `/orchestrator-factory`、說工廠模式、要求交給工廠，或使用明確的同義說法 | § Activation |
| E2 | 觸發條件 | 冷啟動交接啟用 | 新 session 被指派特定既有 `.factory/_runs/<run>/`，其 `_status.md` 為 `Stage: await-factory-session` 且 `Factory started: no`；manager 把執行中的 factory session 移到自動化計畫的另一個 run 時，不論該 run 的階段都以同樣方式進入。宣告工廠模式、沿用該 run，先讀 `_status.md`、`_intake.md`、`_memory.md` 再選階段；從另一個 run 移入時，不沿用該 run 未記錄的內容；不要求使用者重下啟用指令 | § Activation；frontmatter description |
| E3 | 觸發條件 | 不啟用的情形 | 只因 `.factory/` 存在、有舊或已完成的 run、在說明中提到 factory 或 PM，或一般實作要求而沒有工廠意圖或具名冷啟動交接 | § Activation |
| E4 | 邊界條件 | 啟用不等於授權 | 啟用不授權派工、apply、E2E 驗收、sync、archive；所有既有人閘照舊，只有帶自動化授權的 run 依 § Automation 調整 | § Activation |
| E5 | 觸發條件 | 隱式呼叫設定 | `disable-model-invocation: false`；`agents/openai.yaml` 為 `allow_implicit_invocation: true` | frontmatter；`agents/openai.yaml` |
| E6 | 硬規則 | 使用者指令優先（規則 1） | 依當前回合判斷階段、範圍、選配 skill；不發明固定的全平行排程；解除預設（例如規則 6）也屬此規則，但只能透過使用者在對話中的明確要求，或 run 內記錄的自動化授權 | § Hard rules |
| E7 | 硬規則 | 預設討論（規則 2） | 使用者沒說可執行的階段或無法判斷從哪開始時，進入唯讀討論：不寫入、不派工、不建 `.factory/` run；優先依 `discuss-first` | § Hard rules |
| E8 | 硬規則 | 不得靜默派工（規則 3） | 使用者確認派工計畫（或子集、改派）前，不啟動 apply 或任何可寫入的 worker；§ Automation 允許的情形除外 | § Hard rules |
| E9 | 硬規則 | 同系列一個 worker（規則 4） | 有順序或相依的同系列 change 由同一個具名 worker 負責；獨立 change 可分派不同 worker | § Hard rules |
| E10 | 硬規則 | 驗證分離（規則 5） | apply worker 只可跑 `hard-verify`，從不跑 `code-review`；`code-review` 一律由 orchestrator 另派 Check worker，除非使用者在確認派工時剔除 Check；工廠模式下 apply 內不得有巢狀自我檢查 subagent；change 文件審查也不由 apply worker 做，且審查者 ≠ Check；`e2e-review` 只在另派的 E2E worker 中執行（§5b），apply worker 與 orchestrator 都不操作受測系統 | § Hard rules |
| E11 | 硬規則 | 預設不 commit（規則 6） | 預設跑 `commit-message-suggestion` 並把建議交給使用者；orchestrator 只依該 skill 的 `## Committing on request` 代為 commit，授權來源為使用者在對話中的明確要求，或 run 自動化授權中的 commit 規則（§ Automation）；有 run 時把延續授權的範圍與期限記入 `_memory.md` `## User decisions`；不得推定授權；使用者未另外要求不 push；worker 永不 commit | § Hard rules |
| E12 | 硬規則 | 不自動載入 grill 類（規則 7） | 一般工廠路徑不自動載入 `grill-me`／`grill-with-docs` | § Hard rules |
| E13 | 硬規則 | worker 模型（規則 8） | worker 預設與 orchestrator 同模型；換模型須詢問並獲同意 | § Hard rules |
| E14 | 硬規則 | 執行環境降級（規則 9） | 優先使用平行 worker 或 subagent；環境無法隔離 worker 時降級，改產出逐 worker 可貼上的指令並等待，不假裝有隔離 | § Hard rules |
| E15 | 硬規則 | 不臆造（規則 10） | worker 不得發明需求；資訊不足時依資訊來源順序唯讀查閱；change 與較高來源衝突時不自行選邊，回 `needs_input`；仍不足時回 `needs_input`（stop-for-human）或寫入已揭露、可逆的本地 `assumptions_made`；不得捏造 API、欄位、行為 | § Hard rules |
| E16 | 硬規則 | 流程配合工作性質（規則 11） | 持久的專案實作走 opsx；非專案實作不強制 OpenSpec 產物或 opsx 階段，改選較小的工廠路線，寫明產物、worker 邊界、驗證、人閘 | § Hard rules |
| E17 | 硬規則 | 寫入階段以外不改專案檔（規則 12） | 討論、協助部署、草擬文件時，orchestrator 不改專案檔、設定檔、進入點程式；需要改程式時說明原因並詢問是否開 propose；例外是使用者口頭授權的修改：有 run 時記入 `_memory.md` `## User decisions`，沒有 run 時在對話中重述授權範圍；非專案路線依其宣告的允許寫入範圍；Agent E2E review 階段是寫入階段，但只限專案的 `.e2e/` 資料夾（§5b） | § Hard rules |
| E18 | 硬規則 | `.manager` 唯讀（規則 13） | 工作區有 `.manager/` 時，orchestrator 與 worker 可唯讀讀取全部內容，不得寫入；`.manager/_runs/` 只當線索；`.manager` 從不是必要輸入；交接進工廠的內容保持自足 | § Hard rules |
| E64 | 硬規則 | 文件同步（規則 14） | 預設只同步受這次工作影響的 README；使用者提到其他文件（docs 資料夾、`.manager` 檔、巢狀 README、說明文件、交接檔）時，先列出會同步的文件清單並等使用者確認；`.manager` 的變更仍走 manager 交接（規則 13）；不得自行更新其他文件；各文件依對應的 doc-\* skill 撰寫 | § Hard rules |
| E19 | 資訊來源 | 四級優先序 | 適用 orchestrator 與所有 worker，高者勝：1 使用者陳述或確認的資訊（含寫成交接項的已確認決策，例如 `_memory.md` `## User decisions`、冷啟動的 `_intake.md`）；2 正典參考（`.manager` 正典檔、opsx 主規格、專案文件）；3 使用者未確認的 run 筆記（`_notes.md`）；4 opsx change（含生成與 agent 自決部分，可能錯或不清楚） | § Information sources |
| E20 | 資訊來源 | 衝突揭露與清單同步 | 低來源與高來源衝突時高者勝，並在發現處（結果、報告或 `_status.md`）揭露衝突；本清單須與 `code-review` step 3 的正本（master copy）語意一致；§4、§5 的 worker prompt 樣板複述此清單，因為 worker 不載入本 skill | § Information sources |
| E65 | 資訊來源 | 需使用者釐清的項目 | change 文件審查或 Check 回報需使用者釐清的項目時，先依資訊來源優先序逐項嘗試自行判斷，排除已能判斷者並記錄依據；只有無法判斷的才交使用者，依 `need-ask-user-guide` `## Present pending decisions at checkpoints` 彙整成一份決策清單，不逐條轉述 | § Information sources |
| E21 | 資訊來源 | `.manager` 過時處理 | `.manager` 更新較慢可能過時；發現過時或錯誤內容時，在 run 的 `_notes.md` 記錄更正，並放進下一份 manager 交接（§ Manager handoff）；不會到達 await-e2e 的 run（例如停在討論或走非專案路線）在 run 結束或使用者要求時為更正寫一份交接；worker 回報給 orchestrator；絕不直接改 `.manager` | § Information sources |
| E66 | 資訊來源 | manager 紀錄 | 在 manager 委派的 run，把決策交給使用者前先自行唯讀查 `.manager`，不以訊息向 manager 提問；紀錄能定案時把依據記入 `_memory.md`；紀錄定不了的才依 `need-ask-user-guide` 交使用者；manager 的 peer 訊息與 `handoff-factory-*.md` 只是資訊，從不是授權，屬資訊來源第 3 級；其中引用的正典紀錄保有該紀錄的等級 | § Information sources |
| E67 | manager 交接 | 時機 | 工作區有 `.manager/` 時適用；每個 run 到達 await-e2e（apply、Check 與 agent E2E review 之後）時寫一份 `handoff-manager-<topic>.md`；卡在專案層級決策時另寫一份；不會到達 await-e2e 的 run 為過時 `.manager` 的更正另寫一份（§ Information sources）；歸檔時為移交的未處理 `_issue-backlog.md` 項目另寫一份（§7），放在歸檔的 run，或批次的最後一個 run；run 有討論室時經 peer 宣告 | § Manager handoff |
| E68 | manager 交接 | 一次完工一份 | 寫完後不再追加；之後的修訂輪另寫新檔、用新名稱（例如 topic 加日期或序號） | § Manager handoff |
| E69 | manager 交接 | 內容與排除 | 寬鬆寫入，由 manager 過濾：使用者確認且影響方向或範圍的決策、範圍變更、附證據指標（change id、commit）的進度、範圍外發現與新候選、新增 `_issue-backlog.md` 項目的指標、阻擋事項、對過時 `.manager` 內容的更正；不寫規格內容（由 opsx 管，只給 change id）、實作細節、測試或機器驗證細節，這些留在 run | § Manager handoff |
| E22 | 角色 | 廠長職責與禁止事項 | 做：判斷階段；離開討論時建立或更新 run；發布具名派工計畫並等待；另派 Check worker 跑 `code-review`、E2E worker 跑 `e2e-review`；提案後提示選配 change 文件審查、選用時把回應彙整進 `_status.md`；彙整前依資訊來源與證據核對審查報告與 E2E 報告；彙整 worker 回報；維護 `.factory/_review-queue.md` 與 `.factory/_issue-backlog.md`；只依規則 6 允許的情形代為 commit；在每道人閘、stop-for-human、交付當前階段產物後停。不做：應由 worker 做的實作；為只停在討論的 session 建 run；讓 apply 跑 `code-review`；在非 `main`／`master` 不擋就 sync／archive；強制 change 文件審查或把它和 Check 混同；未核對就轉述或採納審查結論或 E2E 狀態；自己操作受測系統；在討論、部署協助、草擬文件時改專案檔；把驗證綠燈或 E2E 報告當成可出貨；未經該授權就 commit、讓 worker commit；因 report-continue 停整個工廠 | § Role |
| E23 | 角色 | 派工深度 | orchestrator → apply／check／E2E worker；不在 apply 內巢狀驗證；Check worker 可依 `code-review` step 5 以平行、合併或依序方式跑兩軸，並回報所用模式；E2E worker 可依 `e2e-review` 的規定再派子 worker，但只有它操作受測系統 | § Role |
| E24 | 路線選擇 | 專案與非專案實作 | 先選路線再建產物或派工。專案實作：產品行為、原始碼、專案設定、資料或 schema、要成為專案一部分的功能或修正，走完整 opsx，除非使用者明確指定其他核可流程。非專案實作：研究、分析、盤點、規劃、純文件、稽核等，不要求 change 套件，只用相關 skill 與 worker。非專案路線仍須寫明產物、允許寫入、派工時的具名 worker、驗證方式、人工檢查點；可沿用 run 控制機制，但不為了像 opsx 而虛設 propose／apply／sync／archive 階段；分類有歧義且實質影響流程時先唯讀討論並詢問 | § Workflow selection |
| E25 | 流程步驟 | opsx 階段表 | 討論（`discuss-first`，不建 run）→ 提案（`openspec-propose`、`opsx-propose-guide`、`test-first` 必用；建 run 並提示選配審查）→ 人閘：change（預設無 skill；選配審查在 § Automation 以外從不自動要求）→ 派工計畫（提案後可立即發布，審查不阻擋寫計畫，等確認）→ apply（`openspec-apply-change`、`opsx-apply-guide`、`test-first`、結尾 `hard-verify`）→ 機器驗證（Check worker 跑 `code-review`，在 agent E2E review 之前，change 為審查對象）→ agent E2E review（E2E worker 跑 `e2e-review`；預設執行，在 Check 之後、人工 E2E 之前，與修正交替迭代，§5b）→ 人閘：E2E（呈現 agent E2E review 後修訂的清單並更新 `.factory/_review-queue.md`，使用者只測剩下的項目）→ 人閘：archive → sync／archive（`openspec-sync-specs`、`openspec-archive-change`，非主幹擋下）→ commit 建議（預設只給建議，只依規則 6 允許的情形代為 commit）→ change log（完全完成時建議） | § Factory stages |
| E26 | 選配 | 選配 skill 僅點名時載入 | 只在使用者於指令中點名時載入（例：`ponytail`、`karpathy-guidelines`、`opsx-health-check`、`code-to-docs`、`thought-palette-extract`、doc 類指引、`change-review-request`、`change-review-response`）；例外：`test-first` 在 propose 永遠啟用，apply 依 `opsx-apply-guide` 使用；不在本 skill 貼這些 skill 的全文 | § Optional skills |
| E27 | 選配 | change 文件審查定位 | 只在使用者點名或選擇提案後的提示時進行，從不自動要求，但 § Automation 一律執行；主要位置在提案後、與人閘 change 並行、apply 前；回應審查者 ≠ apply worker ≠ apply 後的 Check | § Optional skills |
| E28 | 選配 | 多 agent 協作 | `peer-agent-coordination` 供共用 run 目錄的 peer session 使用，成本高；不自行啟用，使用者提及或與使用者的協作討論需要時才啟用（見其 `## 1. When to enable`），不因 run 結構、其他 skill 的引用或 worker 數量而啟用；run 的 `_intake.md` 記載使用者核可 manager 的委派與 peer 討論室時即已啟用，使用該討論室；與指派一個 worker 多項工作、或多個 worker 同一工作的一般 subagent 派工不同 | § Optional skills |
| E29 | 修復政策 | 三層分類（N=3） | 不把所有問題標 `blocked`。self-fix：指派 change 範圍內的單元測試／lint／編譯失敗，apply worker 修實作並重跑，每個 change 最多 3 輪，仍在 change 文件範圍內，測試異動依 `opsx-apply-guide` 防作弊。report-continue：範圍外發現、略過的檢查類別、已記於 `tasks.md` 的小偏離、非阻擋註記，寫入結果或 `_memory.md` 後繼續其餘指派。stop-for-human：需求矛盾、缺秘密或環境、設計無法實作、自修 3 輪仍紅、需開新 change 的語意污染、`needs_input`，設 `blocked`／`needs_input`、寫 run 檔、附選項回報並等待，不得默默擴大範圍 | § Repair policy |
| E77 | 修復政策 | E2E 結果的分流 | E2E 結果由 orchestrator 分類，不套三層：可信的 `product-fail` 進修正輪；`run-error` 與 `needs-human` 由 orchestrator 決定重派或交人工清單（§5b）；agent 操作系統不完全可靠，`run-error` 從不視為產品失敗 | § Repair policy |
| E30 | 修復政策 | self-fix 防作弊 | self-fix 是修實作；哪些測試異動允許，以 `opsx-apply-guide` `## Test changes (anti-cheat)` 為唯一來源；修訂輪中的斷言調整依 `opsx-apply-guide` `## Amendment rounds`（流程與閘見本 skill 修訂輪） | § Self-fix anti-cheat |
| E31 | 修復政策／產物格式 | `needs_input` 處理與四選單 | 轉達前先查任務指定的紀錄（已確認的 run 決策、`.manager`、專案文件），已有答案就依紀錄恢復並揭露依據，不再問使用者（準則依 `need-ask-user-guide`）；否則轉達使用者並寫 `_needs-input.md`：一行原因 + 建議四選單（① 補定義 ② 允許唯讀查 repo／環境後恢復 ③ 佔位樣板 ④ 略過並記為延後、不宣稱完成），可附情境選項；用編號讓使用者回覆選號；③ 未經使用者選定不得執行，在那之前規則 10 仍適用 | § needs_input menu |
| E32 | 覆寫 | 對 `hard-verify` 的工廠覆寫 | 只在工廠模式：(1) apply 期間 `hard-verify` 是 apply worker 的出口閘，失敗時走 self-fix，覆寫原 skill「不自動修」，只限範圍內實作修正；Check worker 唯讀、不得自動修。(2) 覆寫原 skill「只在對話回報」：apply worker 必須把證據寫入 run 的 `hard-verify-<worker>.md`，不得寫入 `openspec/**`、change 套件或產品原始碼樹。(6) 覆寫原 skill「只在使用者明確呼叫時執行」：使用者確認派工即授權每個 apply worker 在每個 change（或其負責的批次）結束前執行；Check worker 不跑 | § Factory overrides of verify skills |
| E33 | 覆寫 | 對 `code-review` 的工廠覆寫 | (3) Spec 依據：change 是審查對象，依資訊來源判斷（使用者決策、已確認的 run 交接項、`.manager`、opsx 主規格、專案文件）；change 與較高來源衝突時標 `change-design-flaw` 交使用者；不問使用者 Spec 路徑，不搜尋資訊來源以外的來源（例如 issue tracker）；change 文件缺漏時 Spec 標為 blocked／無法審查並繼續 Standards，不自行編造 Spec。(4) orchestrator 必須在每個 Check prompt 注入 `fixed_point`，已知時記入 `_memory.md`（通常是 apply 批次前的 SHA／ref 或與 `main`／`master` 的 merge-base）；因 worker 不 commit，它是工作樹基準，diff 涵蓋未提交與未追蹤檔；複查依修正後複查；有提供時 Check 不問使用者。(5) Check 報告寫入 run 的 `check-<change-id>-code-review.md`，不得寫入 change 套件或 `openspec/**`；工廠模式下只有另派的 Check worker 可跑 `code-review`。(7) Check 報告每個 finding 帶 `code-review` 定義的分類：`violates-change`、`conforms-but-flawed`、`change-design-flaw`；`violates-change` 與 `change-design-flaw` 只用於 Spec 軸 | § Factory overrides of verify skills |
| E78 | 覆寫 | 對 `e2e-review` 的工廠覆寫 | (8) 觸發與位置：使用者確認派工（或 run 的自動化授權）即授權其中列出的 E2E worker；報告上層一律為 `run_dir`，由 worker 建立 `run_dir/e2e-review/`。(9) 專案資產：E2E worker 對專案 `.e2e/` 的變更屬於該 run 的變更集，orchestrator 只依規則 6 commit；第一次建立 `.e2e/` 需使用者核可（§5b） | § Factory overrides of verify skills |
| E34 | run 工作區 | 建立時機與初始化 | 離開討論進入 propose、apply、verify 或任何寫入／派工時建立 run；只停在唯讀討論並結束則不建；建立第一個 run 時，若 `.factory/.gitignore` 不存在，建立單行 `_runs/`（run 是討論與編排的工作空間，太雜不追蹤；收斂結果在 opsx change 與規格） | § When to create |
| E35 | run 工作區 | 路徑與根目錄 | `.factory/_runs/<YYYY-MM-DD>-<slug>/`；slug 只用 `[a-z0-9-]+`，不合法字元去除或替換，資料夾名不含空白或中日韓文字；只有 orchestrator 建 run，worker 不得另建同層 run；`.factory/` 根目錄只放 `.gitignore`、`_review-queue.md`、`_issue-backlog.md`、`_runs/`；worker 從不寫這兩份根目錄檔，由 orchestrator 寫，manager 必要時可更新 | § Path |
| E36 | run 工作區 | slug 唯一性 | 一個工廠主題一個 slug；同日不同主題用不同 slug；自動化計畫下一個 factory session 可依序處理多個 run；完整路徑在 `_runs/` 下唯一，由 orchestrator 負責；目錄已存在時：使用者要恢復該 run 就沿用並先讀 `_status.md`，新主題或不明則不覆蓋，改用新 slug（例如加 `-2`）或詢問使用者；slug 以工作內容命名，不用 `work`、`task` 等泛稱 | § Slug uniqueness；frontmatter description |
| E37 | run 工作區 | 內容範圍 | 放編排狀態、派工計畫、worker 結果、驗證報告、跨 worker 記憶；不放產品原始碼；不取代 `openspec/**` 規格或 change 套件；驗證報告只能依工廠覆寫放在 `run_dir`，不得在 repo 其他地方當檢查草稿 | § What belongs here |
| E38 | run 工作區 | 跨 run 驗收彙總 `_review-queue.md` | 取代前版「跨 run 審查待辦 `_review-backlog.md`」。彙總各 run 的 `_review-checklist.md`，寫成比 run 清單更高的抽象層級，給使用者在最終驗收時看。依功能或業務流程分組，同一畫面的檢查放在一起；每項連回來源 run，同一功能再變更時併入既有項目；agent E2E review 已驗證且 orchestrator 覆核過的項目打勾，以報告路徑為來源指標，證據留在 run；最終只留人類才能處理的項目未勾，排除自動測試、hard-verify 或已覆核的 agent E2E 結果已涵蓋者與簡單邏輯檢查（`need-ask-user-guide`）；自動化計畫下批次結束時一次彙整；清理屬歸檔動作（§7）：已勾項移回負責的 run，未完成或需長期觀察的項目只在使用者決定時保留並 commit，否則工作完成時清空 | § Cross-run review queue |
| E79 | run 工作區 | 跨 run 問題待交接區 `_issue-backlog.md` | 放尚未處理的問題：範圍外發現（例如版面跑掉）、agent E2E review 驗出的實作失敗、疑似錯誤；不設進入門檻，使用者據此開下一個 change 或 run；每個問題一項，寫狀態（open、change opened、won't fix）、現象與證據路徑；清理屬歸檔動作（§7）：仍為 open 的項目經 manager 交接移給 manager 後清空；只有使用者要求時才留在 factory 並 commit；沒有 `.manager` 時由使用者決定去處 | § Cross-run issue backlog |
| E80 | run 工作區 | 根目錄檔不入 run commit | `_review-queue.md` 與 `_issue-backlog.md` 不納入 run 的 commit，使用者要求保留時除外 | § Cross-run issue backlog 末段 |
| E39 | 產物格式 | 檔名慣例 | 控制／交接 `_*.md`：orchestrator 寫，prompt 允許時 worker 才可追加，peer 協作檔依 `peer-agent-coordination`，用於控制面與工廠內部暫存交接；worker 產物 `<role>-<id>-*.md`（不以 `_` 開頭）：由該 worker 寫；跨方交接 `handoff-<recipient>-<topic>.md`：放本 run 根目錄，由 orchestrator 寫，或由 manager 交付 `handoff-factory-<topic>.md`。manager 與 factory 之間的交接檔一律放在 factory run 根目錄：factory 的 `handoff-manager-<topic>.md` 在自己的 run，manager 的 `handoff-factory-<topic>.md` 在收件的 factory run；名稱只用小寫英數與連字號，檔頭三行 `Source run:`、`Recipient:`、`Date:`；收件方從不改寫該檔，在自己的 run 記錄處理 | § File conventions |
| E40 | 產物格式 | 必要控制檔 | `_status.md`：run 建立後一律存在，每次階段轉換更新，內容為階段、分支、worker、Blockers／Decisions needed／Reminders、修訂輪、閘事件、最新產物指標；`_dispatch-plan.md`：發布派工計畫時，存放等待或已確認的具名 worker 表；`_memory.md`：有跨 worker 事實需保存時，主摘要加所有後續 worker 該讀的共享事實（決策、路徑、環境），使用者確認的決策放 `## User decisions`，保持簡短；`_intake.md`：由 PM 交接寫入，工廠從不改寫，內容為已確認脈絡、委派紀錄，以及有時的 `## Automation authorization`；`_review-checklist.md`：Check 之後建立（作為 agent E2E review 的輸入），到達 await-e2e 前修訂；內容為本 run 的清單，層級依 `opsx-apply-guide` §4，agent E2E review 後加上每項的結果、報告指標與剩給人的項目，打勾永久保留。此表標題註明「run 存在且該階段適用時」 | § File conventions |
| E41 | 產物格式 | 選用控制檔 | `_handoff-<worker>.md`：給單一 worker 的工廠內部暫存交接（恢復、部分進度），不是跨方交接；`_needs-input.md`：原因加四選單；`_notes.md`：使用者未確認的討論筆記，以及對過時 `.manager` 內容的更正（資訊來源第 3 級） | § File conventions |
| E42 | 產物格式 | 控制檔寫入方式 | `_status.md`、`_memory.md`、`_dispatch-plan.md`、`_review-checklist.md`、`_review-queue.md`、`_issue-backlog.md` 以編輯工具原地更新；確實需要追加時先確認相同內容不存在；不得以 shell 重導盲目追加 | § File conventions |
| E43 | 產物格式 | worker 產物範例 | `apply-w1-result.md`（`FACTORY_APPLY_RESULT_V1`）、`hard-verify-w1.md`、`check-<change-id>-code-review.md`、`e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/`（每輪 agent E2E 一個資料夾，含報告、結果與證據，依 `e2e-review`）、`change-review-request-NN.md`（選配審查簡報）、`change-review-response-NN.md`（選配審查裁決，`NN` 成對） | § File conventions |
| E44 | 產物格式 | worker prompt 共同要求與跨 run 續用 | 每份 prompt 含 `run_dir: .factory/_runs/<…>/`，存在時 worker 必讀 `_memory.md`、`_status.md`；worker 依資訊來源判斷，可唯讀讀 `.manager`；預設只在當前 run 工作；具名 worker 可跨 run 續用，prompt 須重申新 run 的 `run_dir`、限制與要讀的控制檔，並聲明前一個 run 未記錄的脈絡不沿用；對話只放短摘要，細節留在 `run_dir` | § File conventions |
| E45 | 流程步驟 | 進入工廠模式 | 1 宣告工廠模式開啟；2 判斷是使用者意圖、冷啟動交接或恢復，有提供時確認 `run_dir`；3 行動前讀該 run 的 `_status.md` 與相關 intake、memory、dispatch、最新結果，冷啟動先讀 `_intake.md`、`_memory.md`，需要時依資訊來源唯讀查 `.manager`，`.manager` 不存在不阻擋；4 分類專案或非專案實作並選路線；5 解析起訖階段或產物、範圍、選配 skill、模型偏好、驗證需求；6 階段、產物、範圍或分類缺漏或模糊時唯讀討論，說明原因，解決前不建另一個 run、不 propose、不 apply、不派工 | §1 |
| E46 | 流程步驟 | 提案 | 使用者指示 propose 時（討論已定或明確略過討論）：1 確保 run 存在，新建時初始化 `_status.md` 與空的 `_memory.md`；2 依 `openspec-propose`、`opsx-propose-guide`、`test-first`；3 依 `opsx-apply-guide` §4 設定 run 的清單層級（`broad` 或 `focused`）並記入 `_memory.md`；4 有 change 後進 §3，不啟動 worker；5 提示（非閘）選配 change 文件審查是可行的下一步之一，其他下一步仍在（檢視 change、確認派工等）；預設不要求先審查才派工 | §2 |
| E47 | 流程步驟 | change 文件審查流程 | 只在使用者選用時：1 確保 `run_dir/change-review-request-NN.md` 存在（依 `change-review-request`）；2 等另一位審查者寫 `change-review-response-NN.md`；3 讀裁決與建議下一步，依資訊來源逐項標示採納、誤報排除（附依據）或與較高來源衝突，需使用者釐清的項目依 E65 處理，彙整進 `_status.md`；4 下一步是 orchestrator 核對後的建議（`confirm dispatch`／`amend change`／`needs_input`），不照抄回應；回應含 `change-design-flaw` 時裁決至少為 `needs user clarify`；裁決不是 `ready to apply` 時，派工確認不視為綠燈，直到使用者修正、釐清或明確覆寫 | §2 Optional change-doc review |
| E48 | 產物格式 | 審查者 prompt 樣板 | 欄位：`role`（change 文件審查者，非 apply、非 Check）、`run_dir`、`request`、`skills: change-review-response`、`return`（寫 `change-review-response-NN.md`）、`constraint`（審查對象為 change 文件；有疑問時唯讀查 request 列出的決策脈絡來源，不足時可唯讀查其他來源並在 Context consulted 標 "not in brief"；不 apply；不審產品程式碼） | §2 Reviewer prompt |
| E49 | 人閘／流程步驟 | 派工計畫（必停） | change 建立後（或使用者要求 apply 既有 change 時）立即發布具名 worker 指派、寫 `_dispatch-plan.md`、更新 `_status.md` 並停；選配審查不阻擋寫計畫 | §3 |
| E50 | 流程步驟 | 指派規則 | 獨立 change 可建議不同 apply worker（環境允許時平行）；同系列有序或相依的 change 由一個 apply worker 負責整組；worker 命名清楚（如 `W1`、`W2`），列出確切 change id 與順序；依使用者指令與套件內的相依說明，不套固定平行樣板；使用者可指示一個 worker 多項工作或多個 worker 同一工作（規則 1 覆寫規則 4 的預設）；可沿用前一個 run 的具名 worker，在計畫的 `Reused workers` 註明來源 run | §3 Assignment rules |
| E51 | 產物格式 | 派工計畫表樣板 | 標題 `## Dispatch plan (awaiting confirmation)`；表格欄位 Worker、Role、Changes（依序）、Rationale；另列 Parallelism、Optional skills named by user、Check workers（apply 後派，依資訊來源判斷）、E2E workers（Check 後派，`e2e-review`，寫入授權 `<read-only | scope>`）、Reviewers left out by the user（`<none | Check | E2E>` 並附原因）、Reused workers、run_dir、Next（全部確認／部分確認／改派／選配審查）；之後等使用者確認全部、子集或改派；回報計畫不等於許可；略過審查一律允許；選用審查且最新回應不是 `ready to apply` 時，確認不視為綠燈，直到修正、釐清或明確覆寫 | §3 Plan table |
| E52 | 流程步驟 | apply | 只啟動使用者核可的 worker／change；優先使用平行 worker 或 subagent，每個具名 apply worker 一份 prompt；prompt 簡短，以 change 文件與 `run_dir` 檔冷啟動，不貼長對話；apply worker 在每個 change（或其批次）結束前必跑 `hard-verify`、遵守修復政策、結果寫入 `run_dir`、不得跑 `code-review`；開始前或開始時 orchestrator 在 `_memory.md` 記錄 `fixed_point` | §4 |
| E53 | 產物格式 | apply worker prompt 樣板 | 欄位：`worker`、`role: apply`、`changes`（依序）、`run_dir`、`skills`（`openspec-apply-change`、`opsx-apply-guide`、`test-first`、`hard-verify`）、`repair`（self-fix N=3、防作弊、report-continue、stop-for-human／`needs_input` 附建議選單）、`sources`（四級優先序，與較高來源衝突回 `needs_input`，`.manager` 唯讀）、`verification_level`（`broad`／`focused`，取自 `_memory.md`，依 `opsx-apply-guide` §4）、`reuse`（只用於續用 worker，聲明新 `run_dir` 取代舊 run、舊 run 未記錄脈絡不沿用）、`return`（寫 `apply-<worker>-result.md` 與 `hard-verify-<worker>.md`）、`constraint`（依 change 文件；不跑 code-review；不 sync／archive／commit；不發明需求；回報 out_of_scope；完成指派即停）；選用 `notes` | §4 Apply worker prompt |
| E54 | 產物格式 | `FACTORY_APPLY_RESULT_V1` | 欄位：`worker`、`changes`、`status`（ok／partial／blocked／needs_input）、`summary`、`self_fix_rounds_used`；`## per_change` 每個 change 列 `tasks`、`unit_tests`、`hard_verify`、`deviations`、`assumptions_made`、`developer_verification`（依 `verification_level` 與 `opsx-apply-guide` §4 列需人判斷的項目，排除測試或 hard-verify 已涵蓋者，或指向 `tasks.md`）；另有 `## blocked`、`## out_of_scope`；`blocked`／`needs_input` 只用於 stop-for-human，report-continue 用 `partial` 加 out_of_scope 或 deviations | §4 Apply worker return |
| E55 | 流程步驟 | 機器驗證 | apply 批次完成且結果在 `run_dir` 後：1 另派 Check worker，不得沿用 apply worker 的身分或 session；2 每個 Check worker 只跑 `code-review`（唯讀），負責一或多個 change，寫 `check-<change-id>-code-review.md`；3 change 為審查對象，依資訊來源判斷，每個 finding 帶分類，不搜尋 issue tracker；4 orchestrator 從 `_memory.md` 取（或當下解析）`fixed_point` 傳入；5 彙整前逐項核對 finding：採納、誤報排除（附依據）或與較高來源衝突，需使用者釐清的項目依 E65 處理，不得未經核對轉述或採納，之後彙整進 `_status.md` 與簡短對話摘要；6 綠燈 ≠ archive 許可，也不取代人工 E2E，agent E2E 報告亦同；工廠模式不跑 `impl-verify`，由 `code-review` 取代 | §5 |
| E81 | 流程步驟 | 寫完整清單與剔除 reviewer | Check 的 finding 處理完（修正並複查）後，或使用者剔除 Check 時在 apply 後，依各 change 的開發者驗證清單（`opsx-apply-guide` §4）寫出 run 的完整 `_review-checklist.md`，再進 §5b；使用者在確認派工時剔除 agent E2E review（小型 run，例如單一 debug 修正）時改為停在人工 E2E；剔除記入 `_status.md`；使用者同樣可剔除 Check | §5 末段 |
| E56 | 產物格式 | Check worker prompt 樣板 | 欄位：`worker`、`role: check`、`changes`、`run_dir`、`skills: code-review`、`fixed_point`（取自 `_memory.md`，可為工作樹基準，diff 含未提交與未追蹤檔）、`recheck_scope`（選用，只用於複查：修正處理的 finding 與觸及的檔案或 hunk，只審這些）、`review_basis`（四級優先序，不搜尋 issue tracker）、`amendment`（選用，只用於大規模修訂：依 `opsx-apply-guide` `## Amendment rounds` 核對 `tasks.md` 列出的每項改寫或刪除測試）、`return`（Standards 與 Spec 兩段，寫明執行模式）、`constraint`（唯讀；可讀含 `.manager` 的列出來源；finding 標分類；不修改；不擁有 hard-verify；不 sync／archive／commit；不要求 apply worker 自證；不問 Spec 路徑，也不問已提供的 `fixed_point`） | §5 Check worker prompt |
| E57 | 流程步驟 | 修正後複查 | 修正開始前 orchestrator 在 `_memory.md` 記錄複查用 `fixed_point`：修正前工作樹的快照 ref（例如 `git stash create`，工作樹乾淨時用 `HEAD`），無法快照時記錄修正觸及的檔案清單；並記錄修正範圍（處理的 finding、觸及的檔案或 hunk），因為快照不含未追蹤檔、檔案清單會帶入先前未提交內容，範圍才能縮小複查；複查只涵蓋該修正，派 Check worker 並以 `recheck_scope:` 傳入範圍；只改文件、只調測試資料，或使用者說不需要時可省略，省略與原因記入 `_status.md` | §5 Re-check after fixes |
| E82 | 流程步驟 | agent E2E review 派工與覆核 | 人工 E2E 前的最後一道 agent 自檢；apply worker 與 orchestrator 都不操作受測系統。1 另派 E2E worker，交付完整 `_review-checklist.md` 與 `e2e-review` 要求的輸入；寫入授權來自使用者的派工確認或自動化授權，沒有授權時 worker 唯讀；同一環境同時只有一個 E2E worker 操作。2 使用前依報告與證據核對回傳的 `E2E_REVIEW_RESULT_V1`，每項標為可信、不可信或重跑；不因 worker 說通過就移除人工項目 | §5b 1–2 |
| E83 | 流程步驟 | E2E 結果處理 | 3 可信的 `product-fail` 進修正輪，依修正後複查複查，再以 `--prev` 指向上一輪、以該修正為本輪依據派下一輪；4 `run-error` 與 `needs-human` 由 orchestrator 決定讓 worker 回去重新操作或交人工，工具可靠度有限故允許重跑，項目明顯無法由 agent 完成時停止；`verified-with-limits` 只勾已驗證的部分，限制條件保留為人工項；回傳標明依 agent 步驟判定的 `needs-human` 項目不重派（重跑也改變不了）；仍未解決的項目（失敗、重派後仍 `run-error`、`needs-human`）在人工 E2E 關卡統一整理成一份回報給人，不逐項轉達；5 回傳 `needs-input` 時比照修復政策的 `needs_input` 處理；回傳 `blocked`（環境或驅動不可用）時把剩餘項目交人工，run 少了它們無法繼續時停下等使用者 | §5b 3–5 |
| E84 | 流程步驟 | 問題記錄與清單修訂 | 6 範圍外發現與本 run 未修的實作失敗寫入 `.factory/_issue-backlog.md`；7 修訂 `_review-checklist.md`：可信項目打勾並附報告路徑，保留關鍵項目與未測、失敗、無結論或 agent 無法執行的項目；之後更新 `.factory/_review-queue.md`（§ Automation 下改在批次結束時彙整），進人工 E2E 閘 | §5b 6–7 |
| E85 | 邊界條件 | `.e2e/` 資產 | E2E 階段可在 `e2e-review` 的邊界內寫專案的 `.e2e/`，不算產品修改，不需 propose；orchestrator 在 run 中列出 worker 的寫入並與授權範圍核對，超出授權的寫入是阻擋事項；回傳 `init_needed: yes` 時在下一道人閘呈現初始化提案，使用者核可後才在下一次 E2E 派工指示套用 | §5b `.e2e/` assets |
| E86 | 產物格式 | E2E worker prompt 樣板 | 欄位：`worker`、`role: e2e`、`run_dir`、`skills: e2e-review`、`checklist`（取自 `_review-checklist.md` 的項目編號與原文）、`report_parent: run_dir`、`write_permission`（`<read-only | test data the user allowed>`）、`accounts / environment`（只在 `.e2e/PROJECT.md` 未涵蓋時）、`previous_round`（上一輪資料夾或 none）、`round_basis`（本輪驗證的修正：commit 或 change id）、`init_apply`（只在使用者核可初始化提案後：其輪次資料夾與核可者，供 `--approved-by`）、`return: E2E_REVIEW_RESULT_V1`、`constraint`（依 `e2e-review` 邊界；只寫 `.e2e/` 與 `run_dir/e2e-review/`；不改產品；不 commit；問題交 orchestrator） | §5b E2E worker prompt |
| E58 | 人閘 | 四道人閘 | 檢視 change（提案後；提示選配審查，從不自動要求；§ Automation 下整批只做一次）；確認派工（派工計畫後；確認、子集或改派前不派 worker；選用審查且回應非 `ready to apply` 時暫緩綠燈；§ Automation 下由批次檢視 change 代替）；人工 E2E（agent E2E review 後，剔除 E2E 時為 Check 後；寫 manager 交接、呈現 `_review-checklist.md`（agent E2E review 後修訂的版本，剔除 E2E 時為完整清單）、§ Automation 以外更新 `.factory/_review-queue.md` 後等待，使用者只測剩下的項目；使用者回報通過的項目打勾；自動化計畫下改依 § Automation）；sync／archive（明確核可）。另在 stop-for-human 時停；`needs_input` 以四選單轉達並寫 `_needs-input.md`；report-continue 不停整個工廠 | §6 |
| E59 | 流程步驟 | 修訂輪 | 適用 apply 後、archive 前的需求變更或 E2E 發現（agent 或人工）。意圖與範圍不變 → 修訂既有 change；新能力或語意改變 → 開新 change。change 文件標註依 `opsx-propose-guide` `## Amendments`，可改哪些既有斷言依 `opsx-apply-guide` `## Amendment rounds`；輪次記入 `_status.md`，Stage 沿用既有值。使用者直接要求的修訂免回檢視 change 閘，但記入 `_memory.md` `## User decisions`；orchestrator 發起的修訂回到檢視 change 閘。派工確認仍適用（規則 3），使用者要求修訂並指名 worker 即視為確認。大規模修訂由 orchestrator 標記並交給 worker，Check worker 以 `amendment:` 逐項核對 worker 列出的測試變更 | §6 Amendment rounds |
| E70 | 自動化 | 適用與優先 | run 的 `_intake.md` 帶有使用者經 manager 核可的自動化授權時適用；對這種 run，本節與本 skill 其他段落不同處以本節為準；manager 經 peer 在批次的各 run 之間移動本 session；先查 manager 紀錄（§ Information sources） | § Automation |
| E71 | 自動化 | 設計段 | Stage 為 `design`；每個 run 討論、propose 後一律跑 change 文件審查；不為提問停下：紀錄定不了的決策記入該 run `_notes.md` 的 `## Pending decisions`，依 `opsx-propose-guide` 揭露 change 所作的假設後繼續；`needs doc fix` 時修改 change 再審，兩輪後仍需修改就把剩餘項目記為待決事項；`needs user clarify` 的未解項目同樣記錄；後面 run 的 propose 以同批較早的 change 為前提，依 `opsx-propose-guide` §3 以 `Depends on:` 寫明 | § Automation 1 |
| E72 | 自動化／人閘 | 批次檢視 change | Stage 為 `await-batch-review`；每個 run 都有 change 後，在一個檢查點呈現全部 change 與各 run 的待決事項，依 `need-ask-user-guide` 彙整成一份決策清單並等待；這是整批的檢視 change 閘；使用者確認全部或部分 run；此時使用者指示的修訂不需再審 | § Automation 2 |
| E73 | 自動化 | 施工段 | 依相依順序派工各個已確認的 run，批次檢視代替其確認派工閘；Check 後修正採納的 finding 並複查，再跑 agent E2E review（§5b）；到達 await-e2e 時以修訂後的 `_review-checklist.md` 依授權 commit（預設一次），再寫附 commit hash 的 manager 交接並經 peer 回報 | § Automation 3 |
| E74 | 自動化 | 停止條件 | 施工段的 run 遇 `needs_input` 或 stop-for-human、self-fix 用盡、需要使用者的 Check finding、需開新 change 的範圍外發現時停下；回報 manager；只有相依於它的 run 等待 | § Automation 4 |
| E75 | 自動化 | 批次結束 | manager 回報批次完成時，把各 run 的清單彙整進 `_review-queue.md`；之後人工 E2E 與 sync／archive 閘照常適用；未經使用者另外明確要求不 push | § Automation 5 |
| E60 | 邊界條件 | sync／archive 條件 | 只在人工 E2E 後（含使用者指示的修正）且使用者明確核可 sync 與 archive：1 偵測目前分支；2 不是 `main` 也不是 `master` → 擋下、警告在功能分支執行會損害 `main`／`master` 上的主規格檔，並停止；3 在 `main`／`master` 且已核可 → 依 `openspec-sync-specs`、`openspec-archive-change`；4 歸檔時一併清理跨 run 檔：本次工作在 `_review-queue.md` 的已勾項移回負責的 run，`_issue-backlog.md` 的未處理項交給 manager（§ Cross-run issue backlog）；只有使用者要求時才保留並 commit 任一檔的項目。人工驗證項目未勾時，使用者口頭確認即可歸檔，確認內容與時間記入 `_status.md`；不得替使用者把項目勾成人工已驗證或宣稱使用者已驗證；agent 驗證的打勾附其報告路徑 | §7 |
| E61 | 流程步驟 | commit 建議與 change-log | 使用者要求或批次收尾時跑 `commit-message-suggestion` 並把文字交給使用者，只依規則 6 允許的情形代為 commit；整個工廠工作完全完成時建議 `change-log`，再依該 skill 把輸出交給使用者 | §8 |
| E62 | 產物格式 | 狀態摘要樣板 | `## Factory status`：Stage（discuss／await-factory-session／propose／design／await-batch-review／await-dispatch／apply／machine-verify／agent-e2e／await-e2e／await-archive／done）、run_dir（或只討論時為 none）、Branch（是否允許 sync／archive）、Workers、Change-doc review（none 或略過／等待回應／ready to apply／needs doc fix／needs user clarify）、Blockers（最多 3 點；已記錄但仍阻擋的決策一律列出並附紀錄指標，不計入上限）、Decisions needed（尚未記錄的阻擋決策）、Reminders（非阻擋提醒）；送出前查任務指定紀錄（`.manager`、文件、run）；篩選準則依 `need-ask-user-guide` `## Present pending decisions at checkpoints` | §9 |
| E63 | 流程步驟 | 停止與恢復 | 每道人閘、stop-for-human、交付當前階段產物後停止；只依使用者指示恢復，或依 § Automation 下 manager 的 run 指派恢復；恢復時讀 run 的 `_status.md` 與最新產物，不只依賴對話記憶 | §10 |
| E76 | 流程步驟 | 更換 orchestrator session | 例外情形，用於大型工作耗盡 session 時：卸任 session 若還能，把未記錄的進度寫入 `_status.md` 與 `_memory.md`；接手 session 讀控制檔與最新產物，說明恢復的階段後繼續；換手時使用者在場，有 peer 討論室時依使用者指示更新名冊；只有記錄在 `_memory.md` 或 `_intake.md` 的授權會延續 | §10 Replacing the orchestrator session |

## 3. 其他

- **Stage 列舉不涵蓋非專案路線**：E62 的 Stage 已有自動化的 `design`、`await-batch-review` 與新增的 `agent-e2e`，但 E24 的非專案路線仍沒有對應的階段值。修訂輪與修正後複查明寫「Stage 沿用既有值」，屬刻意設計，不算缺口。
- **`_intake.md` 列在必要控制檔表**：E40 把 `_intake.md` 放進必要控制檔，但它只在 PM 交接建立的 run 存在；使用者直接啟用工廠時自行建立的 run 沒有它。表頭的「run 存在且該階段適用時」與「由 PM 交接寫入」可讀出條件，但字面上沒有說使用者意圖啟用的 run 不需要它。README 的檔案樹把它標為選用。
- **沒有 run 的討論如何送出 `.manager` 更正**：E21、E67 讓不會到達 await-e2e 的 run（例子包含「停在討論」）在結束時為更正寫交接；但依規則 2 與 E34，唯讀討論且就此結束的 session 不建 run，也就沒有 `_notes.md` 或 run 根目錄可放交接檔。這種 session 發現的更正要如何處理，本文沒有寫。
- **`_review-checklist.md` 建立時機只寫 Check 之後**：E40 的時機欄寫「After Check」；使用者剔除 Check 時改在 apply 後建立，只寫在 §5 末段（E81），表內沒有反映。
- **§5b 第 7 步「關鍵項目」與打勾的關係**：同一步同時寫「可信項目打勾」與「保留關鍵項目」；一個 agent 已可信驗證的關鍵項目應打勾還是保留給人，本文沒有說明。
- **E2E 寫入授權與 `.e2e/` 寫入**：E86 的 `write_permission` 只有 `read-only` 或「使用者允許的測試資料」，與 `e2e-review` 必要輸入的 Write permission（可建立或修改哪些測試資料）一致；但 E85 要求「列出 worker 的寫入並與授權核對」，而 `E2E_REVIEW_RESULT_V1` 的 `writes` 依 `e2e-review` 只記測試資料寫入（與 `init-apply`），沒有 `.e2e/` 腳本、樣板的升級清單。覆寫 9 要 orchestrator 把 `.e2e/` 變更併入 run 的變更集，實際只能自行查工作樹得知；另外，派工寫 `read-only` 時 worker 仍可依 `e2e-review` 寫 `.e2e/` 與 `run_dir/e2e-review/`，「唯讀」一詞只指測試資料，字面容易誤讀。
- **`e2e-review` 交給上級決定、本文未接的事項**：下一輪 E2E 是否重驗本輪修正不影響的已驗項目（`e2e-review` Iterations：由上級決定），E83 只寫以 `--prev` 派下一輪，沒有說 `checklist:` 要放哪些項目；技能版本與 `.e2e/PROJECT.md` 記載的版本不符時是否更新 `.e2e/` 資產（`e2e-review` `references/project-profile.md`：由上級決定），本文沒有對應。
- **跨 skill 引用與接點目前都存在**：`opsx-apply-guide` §3、§4、`## Test changes (anti-cheat)`、`## Amendment rounds`，`opsx-propose-guide` §3（`Depends on:`）、`## Amendments`，`need-ask-user-guide` `## Present pending decisions at checkpoints`，`code-review` step 1、3、5 與 Finding tags，`commit-message-suggestion` `## Committing on request`，`peer-agent-coordination` `## 1. When to enable`。`e2e-review`（1.2）的 `E2E_REVIEW_RESULT_V1`、五種項目狀態（`verified`、`verified-with-limits`、`needs-human`、`run-error`、`product-fail`）、回傳 `needs-input`／`blocked`、`init_needed`、`init-apply --approved-by`、`--prev`／`--basis`、輪次資料夾 `<yyyyMMdd-HHmmss>-r<NN>-<short>`、必要輸入表、「同一環境同時只有一個 worker 操作」都與本文對得上。其他 skill 已沒有 `_review-backlog` 的殘留引用。
- **README（`orchestrator-factory-readme.md`）與本文仍不一致處**：
  - 流程圖的 commit 節點仍寫「明確要求時代為 commit」，沒有提到自動化授權；開頭段與自動化流程圖已涵蓋。
  - 沒有寫 manager 的 peer 訊息與交接檔屬資訊來源第 3 級，也沒有寫不會到達 await-e2e 的 run 為過時 `.manager` 更正另寫交接。
  - 檔案樹把 `_intake.md` 標為選用，本文列在必要控制檔表（見上）。
  - manager 交接內容的列舉沒有「新增 `_issue-backlog.md` 項目的指標」（E69）。

## 4. 與前版差異

- 1.11（2026-11-04）：E83 補「依 agent 步驟判定的 `needs-human` 項目不重派」與「未解決項目在人工 E2E 關卡統一回報」（來源：run 2026-11-04-e2e-review-surfaces-recipes `changes/08`）。

對照前版對照稿（version 1.9，last_updated 2026-11-02T13:49:21）與 commit 6bccacb 的 diff。元素編號沿用，新元素接續編號並依章節位置插入。

新增：

- E77 E2E 結果的分流（§ Repair policy）。
- E78 對 `e2e-review` 的工廠覆寫（覆寫 8、9）。
- E79 跨 run 問題待交接區 `_issue-backlog.md`。
- E80 兩份根目錄檔不入 run commit。
- E81 Check 後寫完整清單，以及使用者剔除 Check 或 E2E。
- E82–E84 §5b agent E2E review 的派工與覆核、結果處理、問題記錄與清單修訂。
- E85 `.e2e/` 資產（寫入範圍、寫入核對、初始化提案人閘）。
- E86 E2E worker prompt 樣板。

修改：

- E38 由「跨 run 審查待辦 `_review-backlog.md`」改為「跨 run 驗收彙總 `_review-queue.md`」：改為高抽象彙總；agent 已驗且覆核的項目打勾附報告路徑；使用者回報通過不再移除，改在歸檔時把已勾項移回負責的 run；最終只留人類能處理的項目。
- E10 規則 5：使用者剔除 Check 時除外；`e2e-review` 只在另派的 E2E worker 執行，apply worker 與 orchestrator 都不操作受測系統。
- E17 規則 12：Agent E2E review 階段是只限 `.e2e/` 的寫入階段。
- E22 角色、E23 派工深度：加入 E2E worker、核對 E2E 報告與證據、不自行操作受測系統、維護兩份根目錄檔、E2E 報告也不等於可出貨；E2E worker 可再派子 worker。
- E25 階段表：新增 Agent E2E review 列；機器驗證改在 agent E2E review 之前；人工 E2E 改為呈現修訂後清單、更新 `_review-queue.md`、使用者只測剩下的項目。
- E35 根目錄：改放 `_review-queue.md`、`_issue-backlog.md`；由 orchestrator 寫，manager 必要時可更新。
- E40 `_review-checklist.md`：改為 Check 後建立、await-e2e 前修訂，記錄每項結果與報告指標，打勾永久保留。
- E42、E43：控制檔寫入加入 `_review-checklist.md` 與兩份根目錄檔；worker 產物加入 `e2e-review/` 輪次資料夾。
- E51 派工計畫表：新增 E2E workers 與 Reviewers left out by the user 兩行。
- E55 機器驗證：綠燈不取代人工 E2E 的說法擴及 agent E2E 報告；「之後停在人工 E2E」移到 E81。
- E58 人閘：人工 E2E 閘改在 agent E2E review 後（剔除時在 Check 後），使用者回報通過改為打勾。
- E59 修訂輪：E2E 發現包含 agent 與人工。
- E60 sync／archive：新增第 4 步清理兩份跨 run 檔；打勾限制改為「不替使用者勾成人工已驗證」，agent 驗證的打勾附報告路徑。
- E62 狀態摘要：Stage 新增 `agent-e2e`。
- E67、E69 manager 交接：時機加入 agent E2E review 之後，以及歸檔時為移交的 issue 另寫一份；內容加入新增 `_issue-backlog.md` 項目的指標。
- E73、E75 自動化：施工段在 Check 修正後跑 agent E2E review，以修訂後清單 commit；批次結束彙整到 `_review-queue.md`。
- 摘要：加入 agent E2E review 階段、剔除 reviewer、兩份根目錄檔與歸檔清理。

移除：

- 無元素移除（E38 改寫，見上）。

§3 變動：

- 保留「Stage 列舉不涵蓋非專案路線」（註記已有 `agent-e2e`）、「`_intake.md` 列在必要控制檔表」「沒有 run 的討論如何送出 `.manager` 更正」。
- 新增「`_review-checklist.md` 建立時機只寫 Check 之後」「§5b 第 7 步關鍵項目與打勾的關係」「E2E 寫入授權與 `.e2e/` 寫入」「`e2e-review` 交給上級決定、本文未接的事項」。
- 「跨 skill 引用」項加入 `opsx-apply-guide` §3 與 `e2e-review` 的接點。
- README 項保留三項，新增「交接內容沒有 `_issue-backlog.md` 指標」。
