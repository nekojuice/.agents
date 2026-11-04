# orchestrator-factory

<details>
<summary>目錄</summary>

- [關於本技能](#關於本技能)
- [如何啟用](#如何啟用)
- [工作區結構](#工作區結構)
- [技能邏輯](#技能邏輯)
- [關鍵參數](#關鍵參數)

</details>

## 關於本技能

`orchestrator-factory` 是工廠模式的「廠長」總指揮。它把 OpenSpec 的一整條開發流程串起來——討論、提案、實作、機器驗證、agent E2E 驗證、人工 E2E、同步歸檔、commit 建議、change log——並把每個階段派給具名的工作者去做，自己只負責排程、守人閘、彙整回報，然後為使用者停下。

它只在使用者表明要用工廠模式，或被指派到等待工廠接手的既有 run 時進入；遇到不明確的指令會退回唯讀討論。三條核心紀律貫穿全程：**驗證分離**（實作者只做硬閘檢查，程式審查與 E2E 驗證一律另派工作者；實作者與總指揮都不操作受測系統）、**預設不代為 commit**（使用者明確要求，或使用者核可的自動化計畫指定時，才依 `commit-message-suggestion` 的做法代為 commit；工作者永不 commit，push 一律要使用者另外授權）、**不臆造需求**。資訊不足時依資訊來源優先序查閱：使用者提出或確認的資訊、`.manager` 正典檔與 opsx 主規格及專案 docs、run 內未確認的筆記、opsx change；`.manager` 只可唯讀查閱，不得寫入。流程中會依階段載入相依子技能：`discuss-first`、`openspec-propose`／`opsx-propose-guide`、`test-first`、`openspec-apply-change`／`opsx-apply-guide`、`hard-verify`、`code-review`、`e2e-review`、`openspec-sync-specs`／`openspec-archive-change`、`commit-message-suggestion`、`change-log`；提案審查（`change-review-request`／`change-review-response`）與多 agent 協作（`peer-agent-coordination`）為選配。

工作區有 `.manager` 時，每個 run 走完實作、Check 與 agent E2E 驗證、到達等待使用者檢查時，總指揮寫一份給 manager 的交接檔。manager 委派的 run 會附 peer 討論室；manager 與使用者核可自動化計畫時，同一個工廠 session 先把多個 run 的 change 開完並審查，使用者一次確認後才依序施工。

## 如何啟用

有兩條啟用路徑：

- 使用者以斜線指令、「工廠模式」或同義說法表明要用工廠模式。
- 冷啟動交接：新 session 被指派到某個既有 `.factory/_runs/<run>/`，且其 `_status.md` 為 `Stage: await-factory-session`、`Factory started: no`。此時直接沿用該 run，先讀 `_status.md`、`_intake.md`、`_memory.md`，不需使用者再下啟用指令。自動化時，已在運作的工廠 session 由 manager 經 peer 指派到另一個 run，不論該 run 在哪個階段都以同樣方式進入，前一個 run 未記錄的脈絡不帶過去。

```text
/orchestrator-factory
```

只因 `.factory/` 存在、有舊 run、說明中提到工廠或 PM，或使用者提出一般實作要求但沒有工廠意圖，不會啟用。啟用本身不代表核可派工、實作、E2E 驗收或同步歸檔，各人閘照常適用；帶有自動化授權的 run 依下方「自動化」一節調整。

啟用後的動作：

1. 宣告工廠模式已開啟。
2. 判斷是使用者啟用、冷啟動交接或恢復既有 run，並確認 `run_dir`。
3. 讀該 run 的 `_status.md` 與相關控制檔、最新產物再行動；需要時可依資訊來源優先序唯讀查閱 `.manager`，`.manager` 不存在也不影響啟用。
4. 判斷工作屬於專案實作或非專案實作：專案實作走完整 opsx 流程；研究、盤點、純文件等非專案工作改走量身路線，不強制建立 OpenSpec 產物，但仍須說明產物、允許寫入範圍、驗證方式與人閘。
5. 若階段、產物、範圍或路線不明確，退回**唯讀討論**：不建立 `.factory/`、不提案、不派工，直到使用者指示。

## 工作區結構

離開討論、進入提案或之後的階段時，總指揮才建立一個 run 目錄；純唯讀討論不建立。

```text
.factory/
├── .gitignore              # 單行：_runs/，建立第一個 run 時初始化
├── _review-queue.md        # 跨 run 的驗收彙總，偏高抽象，最終驗收時給使用者看
├── _issue-backlog.md       # 跨 run 尚未處理的問題，作為下一輪 change 的指標
└── _runs/<YYYY-MM-DD>-<slug>/
    ├── _intake.md              # PM 交接建立的冷啟動起始檔，與 _status.md、_memory.md 一併建立（選用）
    ├── _status.md              # 階段、分支、工作者、Blockers／Decisions needed／Reminders、修訂輪次與最新產物指標
    ├── _dispatch-plan.md       # 具名工作者派工表，等待或已確認
    ├── _memory.md              # 跨工作者共享事實：決策、路徑、fixed_point；使用者定案放 User decisions 區
    ├── _notes.md               # 未經使用者確認的討論筆記與 .manager 訂正（選用）
    ├── _review-checklist.md    # 本 run 的逐項清單：Check 後交 E2E 工作者，覆核後標出結果與剩給人的項目，打勾永久保留
    ├── _needs-input.md         # 遇 needs_input 時的原因與四選單（選用）
    ├── _handoff-<worker>.md    # 工廠內部給單一工作者的暫存交接（選用）
    ├── handoff-<recipient>-<topic>.md     # 與 run 以外對象的交接，例如 handoff-manager-<topic>.md、manager 交進來的 handoff-factory-<topic>.md
    ├── apply-w1-result.md      # 實作工作者的結構化結果
    ├── hard-verify-w1.md       # 該實作工作者的硬閘檢查證據
    ├── check-<change-id>-code-review.md   # Check 工作者的程式審查報告
    ├── e2e-review/                        # E2E 工作者每輪一個資料夾：報告、結果與證據，不進版控
    ├── change-review-request-NN.md        # 選配的提案審查邀請
    └── change-review-response-NN.md       # 審查者的裁決，與邀請同一個 NN
```

- `slug` 只用小寫英數與連字號；同一天不同主題須用不同 slug，路徑須唯一。
- 只有總指揮建立 run 目錄；工作者不得另建，也不得寫入 `.factory/` 根目錄的兩份檔；兩份檔由總指揮寫，manager 必要時可更新。冷啟動交接的 run 由 PM 交接建立。
- 底線開頭的檔由總指揮寫；工作者只有在派工指示允許時才可追加。peer 協作檔依 `peer-agent-coordination` 的規則。
- `.factory/` 根目錄只放 `.gitignore`、`_review-queue.md`、`_issue-backlog.md` 與 `_runs/`。run 是討論與編排的工作區，內容繁雜不進版控，收斂結果由 opsx 管理。
- `_handoff-<worker>.md` 只用於工廠內部；與其他對象的交接用 `handoff-<recipient>-<topic>.md`。manager 與工廠之間的交接檔一律放工廠 run 根目錄：工廠的 `handoff-manager-<topic>.md` 放自己的 run，manager 的 `handoff-factory-<topic>.md` 放收件的工廠 run，檔頭三行為 `Source run:`、`Recipient:`、`Date:`；收件方不改交接檔，處理紀錄記在自己的 run。
- 給 manager 的交接檔一次完工寫一份，不再追加；之後的修正輪另寫新檔，檔名不沿用舊的。內容寬鬆，由 manager 篩選：影響方向或範圍的使用者決定、範圍變動、進度與證據指標、範圍外發現與新候選、阻擋事項、`.manager` 過時訂正。規格內容只寫 change id，實作與驗證細節留在 run。
- `_review-queue.md` 保持簡潔：agent 驗證可信的項目打勾並附報告路徑，證據留在 run；最後只留人類才能處理的項目。
- `_issue-backlog.md` 是待交接區：範圍外發現（例如版面歪掉）、E2E 驗出的實作失敗、潛在錯誤都可放，每項寫狀態、現象與證據路徑。
- 兩份檔的清理屬於歸檔動作：queue 已勾項移回負責的 run；issue 未處理項經交接移給 manager。使用者要求保留時才留下並 commit。
- `_status.md`、`_memory.md`、`_dispatch-plan.md`、`_review-checklist.md` 與根目錄兩份檔以編輯工具原地更新；確實需要追加時先檢查有無重複內容。
- 這裡放編排狀態與工作者產物，**不放**產品原始碼，也**不**取代 `openspec/**` 的規格與 change 套件。

## 技能邏輯

### 完整流程

每個人閘都必須停下等待使用者，綠燈的檢查不等於可以出貨。自動化時人閘的位置依下方「自動化」一節調整。

```mermaid
flowchart TD
  A[啟用工廠模式或冷啟動交接] --> B{階段或範圍明確?}
  B -- 否 --> D[唯讀討論 discuss-first<br/>不建 .factory/]
  B -- 是 --> P[提案 openspec-propose + opsx-propose-guide + test-first]
  P --> G1[人閘：檢視 change<br/>選配提案審查，回報先經總指揮核對]
  G1 --> DP[發布派工計畫 _dispatch-plan.md]
  DP --> G2[人閘：確認派工]
  G2 --> AP[實作 apply 工作者<br/>openspec-apply-change + opsx-apply-guide + test-first + hard-verify]
  AP --> CK[機器驗證 Check 工作者<br/>code-review 唯讀，finding 帶分類標記]
  CK --> VC[總指揮依資訊來源核對 finding<br/>能自行判斷的需釐清項先排除，其餘彙整成一份決策清單]
  VC --> EE[agent E2E 驗證 E2E 工作者<br/>依 _review-checklist.md 實際操作、取證、交報告]
  EE --> EV{總指揮覆核報告}
  EV -- 可信的產品失敗 --> FX[修正並複查<br/>下一輪 E2E 指向上一輪]
  FX --> EE
  EV -- 執行失敗或無法判定 --> EE
  EV -- 完成 --> HO[精簡 _review-checklist.md，問題寫入 _issue-backlog.md<br/>寫給 manager 的交接檔]
  HO --> G3[人閘：人工 E2E<br/>呈現剩下事項，更新 _review-queue.md]
  G3 -- 修正 --> RC[修正後複查<br/>修正前記錄快照 ref 或檔案清單，只查該修正]
  RC --> G3
  G3 -- 需求變更或 E2E 發現 --> AR{修訂由誰發起?}
  AR -- 使用者直接要求 --> AU[修訂輪<br/>記入 User decisions，免回檢視 change 人閘]
  AU -- 仍需確認派工，使用者指名工作者即視為確認 --> G2
  AR -- 總指揮發起 --> G1
  G3 --> G4[人閘：核可同步歸檔]
  G4 --> SY[同步歸檔 openspec-sync-specs + openspec-archive-change<br/>僅限 main/master]
  SY --> CM[commit 建議 commit-message-suggestion<br/>明確要求時代為 commit]
  CM --> CL[change log]
```

### 其他規則

- **agent E2E 驗證**：預設執行，在 Check 之後、人工 E2E 之前，依 `e2e-review` 派專責 E2E 工作者。小型 run（例如單一 debug）可在確認派工時剔除 Check 或 E2E，跳過記入 `_status.md`；自動化計畫在核可時一併授權。工具操控可靠度有限，執行失敗由總指揮判斷重派或交人工，不當成產品失敗。E2E 階段可寫專案的 `.e2e/`，不算改產品；寫入範圍依派工時的授權，`.e2e/` 由總指揮依規則 6 一併 commit。專案還沒有 `.e2e/` 時，初始化提案要經使用者核可。
- **討論期間不改專案檔**：討論、協助部署或撰寫文件時，總指揮不修改專案檔、設定檔或進入點程式；需要改程式時說明原因並詢問是否開 propose。使用者口頭授權的修改例外，有 run 時記入 `_memory.md` 的 User decisions 區。
- **文件同步**：預設只同步受這次工作影響的 README。使用者提到其他文件，例如 docs 資料夾、`.manager` 檔、巢狀 README、說明文件、交接檔時，先列出會同步的文件清單等使用者確認，不得擅自更新；`.manager` 仍只透過交接檔處理。各類文件依對應的 doc 系列技能撰寫。
- **需使用者釐清的項目**：提案審查或 Check 回報需釐清的項目時，總指揮先依資訊來源優先序自行判斷並排除，真的無法判斷的才交給使用者，並彙整成一份決策清單，不逐條轉述。
- **工作者模型與執行環境**：工作者預設與總指揮同模型，換模型須先徵得使用者同意；優先使用平行工作者或 subagent，環境無法隔離時改為產出可貼上的各工作者指令並等待。
- **不自動載入 grill 類技能**：`grill-me`、`grill-with-docs` 不會被載入一般工廠流程。
- **狀態值**：`_status.md` 的 Stage 除 opsx 各階段外，另有 agent E2E 驗證中的 `agent-e2e`，自動化另有 `design`（設計段）與 `await-batch-review`（等待批次檢視）。
- **多 agent 協作**：`peer-agent-coordination` 成本高，不主動啟用，使用者提及或協作討論需要時才用；不因 run 結構、其他技能的引用或工作者數量而啟用。`_intake.md` 記載使用者核可 manager 委派與討論室時已啟用，直接使用該討論室。
- **查 manager 紀錄**：manager 委派的 run，決策問題先自行唯讀查閱 `.manager`，不發訊息向 manager 提問；紀錄無法解決的才依 `need-ask-user-guide` 彙整給使用者。manager 的 peer 訊息與交進來的交接檔是資訊，不是授權。
- **檢查清單層級**：提案時依 `opsx-apply-guide` §4 決定 broad 或 focused 並記在 `_memory.md`。大規模或連鎖實作用 broad，寫端到端業務流程；使用者發起的小修改或 debug 用 focused，寫修改後一定要觀察的事項，debug 另寫 bug 原因。
- **換手**：大規模實作耗盡 session 時才換手，屬例外。接手者先讀控制檔與最新產物，說明恢復到哪個階段再繼續；換手時使用者在場，peer 名冊依使用者指示更新；只沿用已記錄的授權。

### 自動化

run 的 `_intake.md` 帶有使用者經 manager 核可的自動化授權時適用；與本技能其他段落不同處，以本節為準。

```mermaid
flowchart TD
  P[設計段：每個 run 討論與提案<br/>不為提問停下，待決事項記入 _notes.md] --> R[一定執行提案審查]
  R -- 需修文件 --> FX[修改 change]
  FX -- 重審 --> R
  FX -- 兩輪仍不過 --> L
  R -- 需使用者釐清 --> L[先依資訊來源排除<br/>其餘記為該 run 的待決事項]
  R -- ready to apply --> N1{全部 run 都有 change?}
  L --> N1
  N1 -- 否，manager 指派下一個 run --> P
  N1 -- 是 --> G[人閘：一次檢視全部 change<br/>各 run 待決事項彙整成一份決策清單一次問]
  G --> AP[施工段：依相依順序派工 apply<br/>不再逐 run 確認派工]
  AP --> CK[Check，採納的 finding 修正並複查]
  CK --> AE[agent E2E 驗證與覆核]
  AE --> E[到達等待檢查：<br/>寫檢查清單 → 依授權 commit → manager 交接檔附 hash]
  E -- 經 peer 回報，manager 指派下一個 run --> AP
  E -. 整批完成 .-> B[彙整 _review-queue.md<br/>之後照常走人工 E2E 與同步歸檔人閘]
```

- 設計段不逐題提問：無法依紀錄解決的決策記入該 run 的 `_notes.md`，依 `opsx-propose-guide` 揭露假設後照常提案，到批次檢視時一次問。批次檢視時使用者指示的修改不需再審。
- 停下條件（施工段）：`needs_input` 或需要使用者介入、self-fix 三輪仍紅、Check 有需要使用者決定的 finding、範圍外發現需開新 change。只有依賴它的 run 會等。
- 後面 run 的提案把同批較早的 change 當前置，依 `opsx-propose-guide` §3 寫 `Depends on:`。
- push 一律要使用者另外明確授權。

### 修復政策

工作者遇到問題時先分類，不是一律標記阻塞。

```mermaid
flowchart TD
  X[工作者遇到問題] --> C{分類}
  C -- 指派範圍內的測試/lint/編譯失敗 --> S[self-fix<br/>修實作並重跑，每個 change 最多 3 輪<br/>測試異動依 opsx-apply-guide 防作弊規則]
  C -- 範圍外發現/略過項/小偏離 --> R[report-continue<br/>記錄後繼續其餘工作]
  C -- 需求矛盾/缺密鑰/需開新 change --> H[stop-for-human<br/>寫 run 檔並等待]
  S -- 三輪仍紅 --> H
```

## 關鍵參數

### 修復層級

| 層級 | 觸發 | 行為 |
| --- | --- | --- |
| self-fix | 指派範圍內的單元測試／lint／編譯失敗 | 修復實作並重跑檢查，每個 change 最多 3 輪；測試異動依 `opsx-apply-guide` 的防作弊規則 |
| report-continue | 範圍外發現、略過的檢查類別、已記於 `tasks.md` 的小偏離 | 寫入結果或 `_memory.md`，繼續該工作者其餘指派 |
| stop-for-human | 需求矛盾、缺密鑰或環境、設計無法實作、self-fix 三輪仍紅、需開新 change、`needs_input` | 標記 `blocked`／`needs_input`，寫 run 檔並等待 |

使用者確認派工即視為授權實作工作者在每個 change 結束前執行 `hard-verify`，覆寫該技能「只在使用者明確呼叫時執行」的預設；Check 工作者不執行 `hard-verify`。

### `needs_input` 四選單

工作者回報 `needs_input` 時，總指揮先查 run 內定案、`.manager`、docs 等紀錄；已有答案就依紀錄恢復並說明依據。沒有答案才寫入 `_needs-input.md` 並提供編號選項，讓使用者可直接回覆選號。

| 選項 | 意義 |
| --- | --- |
| 1 補定義 | 由人在討論或 change 文件補上缺漏的邊界 |
| 2 由 repo／env 解 | 允許唯讀查找後恢復 |
| 3 佔位樣板 | 僅在使用者明確選此項後才建臨時 stub |
| 4 略過此項 | 延後處理，不宣稱已完成 |

### 工作區檔案慣例

| 類型 | 命名 | 誰寫 | 用途 |
| --- | --- | --- | --- |
| 控制／交接 | `_*.md` | 總指揮；工作者僅在派工指示允許時追加 | 控制面與工廠內部暫時交接 |
| 工作者產物 | `<role>-<id>-*.md` | 該工作者 | 結構化結果 |
| 跨對象交接 | `handoff-<recipient>-<topic>.md` | 總指揮；manager 交進來的 `handoff-factory-<topic>.md` 由 manager 寫 | 與 run 以外的對象交接 |

同步歸檔僅能在 `main`／`master` 分支執行；在功能分支上會被擋下並警告，以免破壞主規格檔。人工驗證項目未勾選時，使用者口頭確認即可歸檔，總指揮記入 run，但不代為勾選。
