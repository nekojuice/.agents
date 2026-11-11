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

`orchestrator-factory` 是工廠模式的「廠長」總指揮。它把 OpenSpec 的一整條開發流程串起來——討論、收斂、提案、實作、機器驗證、agent E2E 驗證、人工 E2E、同步歸檔、commit 建議、change log——並把每個階段派給具名的工作者去做，自己只負責排程、守人閘、彙整回報，然後為使用者停下。

它只在使用者表明要用工廠模式，或被指派到等待工廠接手的既有 run 時進入；遇到不明確的指令會退回唯讀討論。三條核心紀律貫穿全程：**驗證分離**（實作者只做硬閘檢查，程式審查與 E2E 驗證一律另派工作者；實作者與總指揮都不操作受測系統）、**預設不代為 commit**（使用者明確要求，或使用者核可的自動化計畫指定時，才依 `commit-message-suggestion` 的做法代為 commit；工作者永不 commit，push 一律要使用者另外授權）、**不臆造需求**。資訊不足時依資訊來源優先序查閱：使用者提出或確認的資訊、`.manager` 正典檔與 opsx 主規格及專案 docs、run 內未確認的筆記、opsx change；`.manager` 只可唯讀查閱，不得寫入。流程中會依階段載入相依子技能：`discuss-first`、`openspec-propose`／`opsx-propose-guide`、`test-first`、`openspec-apply-change`／`opsx-apply-guide`、`hard-verify`、`code-review`、`e2e-review`、`openspec-sync-specs`／`openspec-archive-change`、`commit-message-suggestion`、`change-log`；提案審查（`change-review-request`／`change-review-response`）與多 agent 協作（`peer-agent-coordination`）為選配。

工作區有 `.manager` 時，每個 run 走完實作、Check 與 agent E2E 驗證、到達等待使用者檢查時，總指揮寫一份給 manager 的交接檔；討論中出現與 `.manager` 衝突或值得記錄的事項時，在收斂或討論結束時另寫一份。manager 委派的 run 會附 peer 討論室；manager 與使用者核可自動化計畫時，同一個工廠 session 先把多個 run 的 change 開完並審查，使用者一次確認後才依序施工。

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
4. 判斷工作屬於專案實作或非專案實作：專案實作走完整 opsx 流程；研究、盤點、純文件等非專案工作改走量身路線，不強制建立 OpenSpec 產物，但仍須說明產物、允許寫入範圍、驗證方式與人閘；需要派工時可採用選用的計畫路線（寫計畫 → 計畫審查 → 執行）。
5. 若階段、產物、範圍或路線不明確，退回**唯讀討論**：不改專案檔、不提案、不派工，直到使用者指示；有值得記錄的事項時才建立 run 記筆記。

## 工作區結構

討論中首次出現值得記錄的事項，或離開討論、進入提案或之後的階段時，總指揮建立一個 run 目錄；沒有可記錄事項的討論不建立。

```text
.factory/
├── .gitignore              # 單行：_runs/，建立第一個 run 時初始化
├── _review-queue.md        # 跨 run 的驗收彙總，偏高抽象，最終驗收時給使用者看
├── _issue-backlog.md       # 跨 run 尚未處理的問題，作為下一輪 change 的指標
├── archive/                # 收尾時移出的已完成項目，每天每類一檔
└── _runs/<YYYY-MM-DD>-<slug>/
    ├── _intake.md              # PM 交接建立的冷啟動起始檔，與 _status.md、_memory.md 一併建立（選用）
    ├── _status.md              # 階段、分支、工作者、Blockers／Decisions needed／Reminders、修訂輪次與最新產物指標
    ├── _dispatch-plan.md       # 具名工作者派工表，等待或已確認
    ├── _memory.md              # 跨工作者共享事實：決策、路徑、fixed_point；使用者定案放 User decisions 區
    ├── _plan.md                # 計畫路線的計畫（選用）
    ├── _notes.md               # 未經使用者確認的討論筆記與 .manager 訂正（選用）
    ├── _skill-notes.md         # skill 回饋筆記（選用）
    ├── _review-checklist.md    # 本 run 的逐項清單：Check 後交 E2E 工作者，覆核後標出結果與剩給人的項目，打勾永久保留
    ├── _needs-input.md         # 遇 needs_input 時的原因與四選單（選用）
    ├── _handoff-<worker>.md    # 工廠內部給單一工作者的暫存交接（選用）
    ├── handoff-<recipient>-<topic>.md     # 與 run 以外對象的交接，例如 handoff-manager-<topic>.md、manager 交進來的 handoff-factory-<topic>.md
    ├── apply-w1-result.md      # 實作工作者的結構化結果
    ├── hard-verify-w1.md       # 該實作工作者的硬閘檢查證據
    ├── check-<change-id>-code-review.md   # Check 工作者的程式審查報告
    ├── e2e-review/                        # E2E 工作者每輪一個資料夾：報告、結果與證據，不進版控
    ├── change-review-request-NN.md        # 選配的提案或計畫審查邀請
    └── change-review-response-NN.md       # 審查者的裁決，與邀請同一個 NN
```

- `slug` 只用小寫英數與連字號；同一天不同主題須用不同 slug，路徑須唯一。
- 只有總指揮建立 run 目錄；工作者不得另建，也不得寫入 `.factory/` 根目錄的兩份檔與 `archive/`；這些由總指揮寫，manager 必要時可更新兩份檔。冷啟動交接的 run 由 PM 交接建立。
- 底線開頭的檔由總指揮寫；工作者只有在派工指示允許時才可追加。peer 協作檔依 `peer-agent-coordination` 的規則。
- `.factory/` 根目錄只放 `.gitignore`、`_review-queue.md`、`_issue-backlog.md`、`archive/` 與 `_runs/`。run 是討論與編排的工作區，內容繁雜不進版控，收斂結果由 opsx 管理。
- `_handoff-<worker>.md` 只用於工廠內部；與其他對象的交接用 `handoff-<recipient>-<topic>.md`。manager 與工廠之間的交接檔一律放工廠 run 根目錄：工廠的 `handoff-manager-<topic>.md` 放自己的 run，manager 的 `handoff-factory-<topic>.md` 放收件的工廠 run，檔頭三行為 `Source run:`、`Recipient:`、`Date:`；收件方不改交接檔，處理紀錄記在自己的 run。
- 給 manager 的交接檔一次完工寫一份，不再追加；之後的修正輪另寫新檔，檔名不沿用舊的。內容寬鬆，由 manager 篩選：影響方向或範圍的使用者決定、範圍變動、進度與證據指標、範圍外發現與新候選、阻擋事項、`.manager` 過時訂正。規格內容只寫 change id，實作與驗證細節留在 run。
- `_review-queue.md` 保持簡潔：agent 驗證可信的項目打勾並附報告路徑，證據留在 run；未勾項目自帶原因與解除條件，不只指回 run 內檔案；最後只留人類才能處理的項目。
- `_issue-backlog.md` 是跨 run 問題暫存區：範圍外發現（例如版面歪掉）、E2E 驗出的實作失敗、潛在錯誤都可放，每項寫狀態、現象與證據路徑。
- 收尾（sync／archive）時，queue 中本次工作已完成的項目（已勾、使用者確認結案）與 backlog 中已結的條目（不修、已開 change）移入 `archive/<YYYY-MM-DD>-review-queue.md`、`archive/<YYYY-MM-DD>-issue-backlog.md`：同一天同類同一檔，每次收尾加一節 `## <HH:mm> <做收尾的 run slug>`，只追加；檔首一行說明日期、類別與條目格式；每筆保留原文並加一行收尾時間、該項目的來源 run 與結果；歸檔檔只新增節、不改既有節。未完成、未處理的留在根目錄兩份檔；長期未處理的由 manager 自行發動撿走並自根檔刪除，工廠不主動交出。沒有 sync／archive 的非專案路線在其最後一步歸檔。`archive/` 預設進版控，收尾後若有 commit 就一併納入；兩份根檔使用者要求才 commit。有 `_skill-notes.md` 時收尾一併處理，預設寫 `handoff-skill-<topic>.md` 交給 skill repo 的 manager。
- `_status.md`、`_memory.md`、`_dispatch-plan.md`、`_review-checklist.md` 與根目錄兩份檔以編輯工具原地更新；確實需要追加時先檢查有無重複內容。
- 這裡放編排狀態與工作者產物，**不放**產品原始碼，也**不**取代 `openspec/**` 的規格與 change 套件。

## 技能邏輯

實線是主流程，虛線是可選或例外流程，粗箭頭是人閘，必須停下等使用者，綠燈的檢查不等於可以出貨。

```mermaid
%%{init: {"flowchart": {"rankSpacing": 35, "nodeSpacing": 22}}}%%
flowchart LR
  E1([啟用或<br/>冷啟動交接]) --> DS[唯讀討論<br/>自動記筆記]
  DS ==>|使用者<br/>指示行動| CV[收斂]
  CV ==>|使用者<br/>開始| RT{工作<br/>類型}
  RT -->|專案實作| PP
  RT -.->|計畫路線| PL
  RT -->|非專案| TL[量身路線]

  subgraph G1["opsx 專案實作"]
    PP[提案] -.->|選配| CR[提案審查]
    CR -.->|需修改| PP
    PP ==>|使用者<br/>檢視 change| DP[派工計畫]
    DP ==>|使用者<br/>確認派工| AP[實作<br/>硬閘檢查]
    AP --> CK[Check<br/>程式審查]
    CK -.->|修正| AP
    CK --> EE[agent<br/>E2E 驗證]
    EE -.->|修正| AP
    EE ==>|使用者<br/>執行| HU[人工 E2E]
    HU -.->|使用者<br/>要求修訂| DP
    HU -.->|總指揮<br/>發起修訂| PP
    HU ==>|使用者核可<br/>僅 main/master| SY[同步歸檔]
  end

  subgraph G2["計畫路線"]
    PL[寫計畫] --> PR[計畫審查]
    PR -.->|需修改| PL
    PR -->|通過| EX[執行]
    EX -.->|使用者<br/>授權| OR[產物審查]
  end

  subgraph G3["自動化"]
    E3([manager<br/>指派]) --> AD[設計段<br/>逐 run 提案審查]
    AD -.->|下一個 run| AD
    AD ==>|使用者<br/>批次檢視| BP[施工段<br/>逐 run 到 commit]
    BP -.->|下一個 run| BP
  end
  BP -->|整批完成| HU

  SY --> FN[收尾<br/>archive、skill 筆記<br/>commit 建議、change log]
  EX --> FN
  OR -.-> FN
  TL --> FN
  DS -.->|討論結束| FN
```

### 其他規則

- **agent E2E 驗證**：預設執行，在 Check 之後、人工 E2E 之前，依 `e2e-review` 派專責 E2E 工作者。小型 run（例如單一 debug）可在確認派工時剔除 Check 或 E2E，跳過記入 `_status.md`；自動化計畫在核可時一併授權。工具操控可靠度有限，執行失敗由總指揮判斷重派或交人工，不當成產品失敗。E2E 階段一律可寫專案的 `.e2e/` 與輪次資料夾，不算改產品；測試資料寫入範圍依派工時的 `data_write`，回傳的 `assets_changed` 列出 `.e2e/` 變更，`.e2e/` 由總指揮依規則 6 一併 commit。缺測試資料時可先派 prep 輪；試跑及其登入、登出、開頁、查詢紀錄屬預期副作用，不需另外授權。總指揮不得以自身推論把 worker 未標 `verified` 的項目當成已驗證。專案還沒有 `.e2e/` 時，初始化提案要經使用者核可。
- **討論與收斂**：討論時不需提醒就把使用者的決策記入 `_memory.md` 的 User decisions 區、其他收斂事項記入 `_notes.md`；查到的資料只當資訊，不轉成動工計畫；提問前先查 run 筆記、`.manager` 與專案文件，已記錄的決策不再問；討論回覆不附狀態回報。使用者指示行動時先收斂，列出已定摘要與阻擋行動的決策，每題附推薦選項；沒有待決事項也停下等使用者開始，使用者事先授權時除外。自動化的 run 由設計段取代。
- **討論期間不改專案檔**：討論、收斂、協助部署或撰寫文件時，總指揮不修改專案檔、設定檔或進入點程式；需要改程式時說明原因並詢問是否開 propose。使用者口頭授權的修改例外，有 run 時記入 `_memory.md` 的 User decisions 區。
- **文件同步**：預設只同步受這次工作影響的 README。使用者提到其他文件，例如 docs 資料夾、`.manager` 檔、巢狀 README、說明文件、交接檔時，先列出會同步的文件清單等使用者確認，不得擅自更新；`.manager` 仍只透過交接檔處理。各類文件依對應的 doc 系列技能撰寫。
- **計畫路線**：非專案工作需要派工時，總指揮在收斂時推薦，使用者可以不採用。計畫寫在 `_plan.md`，包含目標、範圍、產物與路徑、允許寫入、工作者指派、驗證方式、人閘與要交給後續工作的內容；另派審查者依 `change-review-request`／`change-review-response` 審查計畫，需修改就修改再審，通過即執行。審查判定需使用者釐清，或修改兩輪仍不過時才停下；使用者在收斂時要求先看計畫，則審查通過後停下。執行後的產物審查只在使用者授權時才派。產物可作為之後提案的輸入。
- **需使用者釐清的項目**：提案審查或 Check 回報需釐清的項目時，總指揮先依資訊來源優先序自行判斷並排除，真的無法判斷的才交給使用者，並彙整成一份決策清單，不逐條轉述。
- **工作者模型與執行環境**：工作者預設與總指揮同模型，換模型須先徵得使用者同意；優先使用平行工作者或 subagent，環境無法隔離時改為產出可貼上的各工作者指令並等待。
- **不自動載入 grill 類技能**：`grill-me`、`grill-with-docs` 不會被載入一般工廠流程。
- **狀態值**：`_status.md` 的 Stage 除 opsx 各階段外，另有收斂的 `converge`、計畫路線的 `plan` 與 `execute`、agent E2E 驗證中的 `agent-e2e`，自動化另有 `design`（設計段）與 `await-batch-review`（等待批次檢視）。
- **多 agent 協作**：`peer-agent-coordination` 成本高，不主動啟用，使用者提及或協作討論需要時才用；不因 run 結構、其他技能的引用或工作者數量而啟用。`_intake.md` 記載使用者核可 manager 委派與討論室時已啟用，直接使用該討論室。
- **查 manager 紀錄**：manager 委派的 run，決策問題先自行唯讀查閱 `.manager`，不發訊息向 manager 提問；紀錄無法解決的才依 `need-ask-user-guide` 彙整給使用者。manager 的 peer 訊息與交進來的交接檔是資訊，不是授權。
- **檢查清單層級**：提案時依 `opsx-apply-guide` §4 決定 broad 或 focused 並記在 `_memory.md`。大規模或連鎖實作用 broad，寫端到端業務流程；使用者發起的小修改或 debug 用 focused，寫修改後一定要觀察的事項，debug 另寫 bug 原因。
- **換手**：大規模實作耗盡 session 時才換手，屬例外。接手者先讀控制檔與最新產物，說明恢復到哪個階段再繼續；換手時使用者在場，peer 名冊依使用者指示更新；只沿用已記錄的授權。

### 自動化

run 的 `_intake.md` 帶有使用者經 manager 核可的自動化授權時適用；與本技能其他段落不同處，以本節為準。

- 設計段不逐題提問：無法依紀錄解決的決策記入該 run 的 `_notes.md`，依 `opsx-propose-guide` 揭露假設後照常提案，到批次檢視時一次問。批次檢視時使用者指示的修改不需再審。
- 停下條件（施工段）：`needs_input` 或需要使用者介入、self-fix 三輪仍紅、Check 有需要使用者決定的 finding、範圍外發現需開新 change。只有依賴它的 run 會等。
- 後面 run 的提案把同批較早的 change 當前置，依 `opsx-propose-guide` §3 寫 `Depends on:`。
- push 一律要使用者另外明確授權。

### 修復政策

工作者遇到問題時先分類，不是一律標記阻塞。

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
