# code-review 元素對照

- 分支：factory
- 對照版本：`skills/code-review/SKILL.md` version 1.1，last_updated 2026-10-20T15:44:18
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`（`display_name: "Code Review"`、`short_description`、`allow_implicit_invocation: true`）；交叉引用核對（唯讀）：`change-review-request/FORMAT.md`、`change-review-request/SKILL.md`、`change-review-response/SKILL.md`、`orchestrator-factory` 的 Factory overrides of verify skills
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

code-review 對「工作樹（含已 commit、未 commit、未追蹤的變更）與固定點之間的差異」做雙軸審查：**Standards**（是否符合 repo 文件化的編碼規範，外加一組固定的程式碼異味基準）與 **Spec**（是否忠實實作審查中的 spec：issue、PRD 或 change）。審查中的 spec 是審查對象之一，不是唯一真相；Spec 軸依四層依據來源的優先序判斷程式碼與 spec 本身。每個 finding 帶一個標記（`violates-change`／`conforms-but-flawed`／`change-design-flaw`），標記名稱與定義和 change-review 共用；Standards 軸只用 `conforms-but-flawed`，另兩個標記只屬 Spec 軸。

步驟順序：

1. 釘住固定點：取得追蹤變更 diff、未追蹤檔清單、commit 清單；複查時可改用快照 ref 或檔案清單；先驗證 ref 可解析、變更集非空。
2. 決定審查中的 spec：呼叫端已指名就直接用；否則依 commit 中 issue 參照 → 使用者路徑 → `docs/`／`specs/`／`.scratch/` → `openspec/changes/<id>/` → 問使用者；確認沒有就讓 Spec 審查跳過。
3. 決定依據來源：呼叫端給清單就用；否則唯讀探查；依四層優先序使用。
4. 決定 Standards 來源：repo 內的規範文件，外加 12 項 Fowler 異味基準。
5. 執行兩軸：預設平行兩個 sub-agent；變更小時可合併；宿主不支援 sub-agent 時依序自行執行。
6. 彙整：兩軸分節並列、保留標記；結尾一行摘要與查閱過的依據來源清單。

在工廠流程中，本 skill 由獨立 Check worker 執行（apply 之後、人工 E2E 之前），`orchestrator-factory` 以覆寫條款注入固定點、規定 Spec 依據與報告位置。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | 使用者要審查分支、PR、進行中的變更，或說「review since X」；允許隱含啟用 | frontmatter description、`agents/openai.yaml` |
| E2 | 審查對象 | 差異範圍 | 工作樹（已 commit、未 commit、未追蹤的變更）與使用者給的固定點之間的差異 | 開頭段、§1 |
| E3 | 審查軸 | Standards 軸 | 檢查程式碼是否符合 repo 文件化的編碼規範 | 開頭段 |
| E4 | 審查軸 | Spec 軸 | 檢查程式碼是否忠實實作審查中的 spec（issue／PRD／change）；該 spec 是審查對象之一而非唯一真相，依 step 3 的依據來源優先序判斷 | 開頭段 |
| E5 | 前置條件 | issue tracker 取用 | 只在 step 2 從 commit 中的 issue 參照解出 spec 時才需要；呼叫端已指名 spec 時略過；依 repo 文件描述的取得方式，沒有描述就向使用者要 issue 內容或路徑 | 開頭段 |
| E6 | 判斷規則 | 每個 finding 一個標記 | 每個 finding 恰帶一個標記；標記名中的「change」指審查中的 spec，在 OpenSpec 流程中即 change package | Finding tags |
| E7 | 判斷規則 | 三個標記定義 | `violates-change`：程式碼偏離審查中的 spec，違反或遺漏其明文要求（僅 Spec）；`conforms-but-flawed`：程式碼依循 spec，但有不需改變 spec 意圖即可修正的問題，含規範違反、異味、邏輯缺陷、風險、spec 未提及處，以及可直接修正的 spec 措辭（不清或自相矛盾，註記 "amend change"）（Standards、Spec）；`change-design-flaw`：spec 與更高優先的依據來源衝突，或解決問題需要使用者決定（僅 Spec） | Finding tags |
| E8 | 共用定義 | 標記與 change-review 共用 | 標記名稱與定義和 `change-review-request/FORMAT.md` 的 concern 分類、`change-review-response` 共用；本表是正本，那些副本與本表保持語意一致 | Finding tags |
| E9 | 前置條件 | 固定點 | 使用者說的就是固定點（commit SHA、分支、tag、`main`、`HEAD~5` 等）；未給就問 | §1 |
| E10 | 前置條件 | 複查用固定點 | 呼叫端可改給修正前的快照 ref（例如 `git stash create` 產生）或修正的檔案清單，作為複查的固定點；給檔案清單時從原固定點 diff 但限於這些路徑；快照 ref 不含未追蹤檔，檔案清單仍包含這些檔案中先前的未 commit 工作；呼叫端另給複查範圍（已修的 findings 與觸及的檔案或 hunk）時只審該範圍 | §1 |
| E11 | 流程步驟 | 擷取差異指令 | 追蹤變更：`git diff <base>` 對工作樹，branch 類固定點的 `<base>` 為 `git merge-base <fixed-point> HEAD`，快照 ref 則用 ref 本身，有檔案清單時加 `-- <paths>`；未追蹤檔：`git ls-files --others --exclude-standard`（有檔案清單時過濾），sub-agent 以新檔完整讀取；commit：`git log <fixed-point>..HEAD --oneline`，全部未 commit 時可為空 | §1 |
| E12 | 前置條件 | 早期失敗 | 進入審查前先以 `git rev-parse` 驗證固定點可解析，且追蹤 diff 或未追蹤清單至少一者非空；壞 ref 或空變更集在此失敗 | §1 |
| E13 | 來源搜尋 | 決定審查中的 spec | 呼叫端已指名就直接用，不搜尋、不問使用者；否則依序：commit 訊息中的 issue 參照 → 使用者傳入的路徑 → `docs/`、`specs/`、`.scratch/` 下與分支名或功能相符的 PRD／spec → 與分支名或 change id 相符的 `openspec/changes/<id>/` → 問使用者；使用者確認沒有則 Spec 審查跳過並回報 "no spec available" | §2 |
| E14 | 判斷規則 | 依據來源四層（正本） | 優先序由高到低：1 使用者陳述或確認的資訊（本對話中的陳述，以及使用者確認後寫下的交接項或決策紀錄）；2 正本與其他有效參考（存在時的 `.manager/` 管理正本、`openspec/specs/`、專案文件）；3 使用者未確認的討論筆記（例如 run 筆記）；4 審查中的 spec 本身（可能含生成或自行決定的內容，可能有錯或不清）。此清單是正本，其他 skill 重述時，副本與正本保持語意一致 | §3 |
| E15 | 來源搜尋 | 依據來源的取得 | 呼叫端提供清單就用該清單；單獨使用且無清單時，唯讀探查本對話的使用者陳述、`openspec/specs/`、專案文件與 README、存在時的 `.manager/` 正本；`.manager/_runs/` 只是線索、不是依據；都找不到就只對 spec 審查並在報告註明 "basis: spec only"；不為了找依據來源而詢問使用者 | §3 Getting them |
| E16 | 判斷規則 | 依據來源的使用 | 全部唯讀；有疑問時先查再判斷；脈絡只用來校準判斷（排除已在他處決定或修正的誤報、確認真正違反），不得用來要求 spec 與更高優先來源都沒要求的事；spec 與更高優先來源衝突時標 `change-design-flaw`、引用兩側、交使用者決定，不選邊、不改寫需求；依據來源本身看似過時或錯誤時在報告註明，不修改 | §3 Using them |
| E17 | 來源搜尋 | Standards 來源 | repo 內任何描述程式碼寫法的文件（例如 `CODING_STANDARDS.md`、`CONTRIBUTING.md`） | §4 |
| E18 | 判斷規則 | 異味基準 | 12 項 Fowler 異味（Mysterious Name、Duplicated Code、Feature Envy、Data Clumps、Primitive Obsession、Repeated Switches、Shotgun Surgery、Divergent Change、Speculative Generality、Message Chains、Middle Man、Refused Bequest），每項寫「是什麼 → 怎麼修」；repo 沒有任何規範時仍適用 | §4 |
| E19 | 判斷規則 | repo 優先 | 文件化的 repo 規範永遠優先；repo 認可而基準會標出的寫法要壓下 | §4 |
| E20 | 判斷規則 | 異味只是判斷 | 異味一律標為「possible …」的啟發式判斷，不得當硬性違規；工具已強制的項目略過 | §4 |
| E21 | 執行方式 | 三種執行模式 | parallel（預設）：同一則訊息兩個 `Agent` 呼叫，皆用 `general-purpose`；merged：變更小時由一個 agent 跑兩軸；sequential：宿主不支援 sub-agent 時自行執行，先完成 Standards 再做 Spec。merged 與 sequential 時每軸仍各自成節，不合併、不重排；報告開頭寫明執行模式與理由 | 開頭段、§5 Execution mode |
| E22 | sub-agent 輸入 | Standards prompt | step 1 的完整差異指令（追蹤 diff 與未追蹤清單）與 commit 清單；step 4 找到的規範檔清單，並完整貼上異味基準（sub-agent 沒有其他取得管道）；step 3 的依據來源清單與優先層級 | §5 |
| E23 | sub-agent 輸入 | Standards brief | 回報 (a) 違反文件化規範處並引用規範出處、(b) 發現的異味並引用 hunk；區分硬性違規與判斷，異味一律是判斷，repo 規範優先於基準；略過工具強制項；每個規範違反或異味一律標 `conforms-but-flawed`，從不使用 `violates-change`，對審查中 spec 的判斷屬 Spec 軸；400 字內 | §5 |
| E24 | sub-agent 輸入 | Spec prompt | step 1 的差異指令（追蹤 diff 與未追蹤清單）與 commit 清單；審查中 spec 的路徑或取得內容；step 3 的依據來源清單與優先層級，並完整貼上 step 3 的使用規則 | §5 |
| E25 | sub-agent 輸入 | Spec brief | 回報 (a) spec 要求但缺漏或不完整、(b) diff 中未被要求的行為（scope creep）、(c) 看似實作但實作疑似錯誤，(a)–(c) 標 `violates-change`；(d) 符合 spec 但有邏輯缺陷或風險，標 `conforms-but-flawed`；(e) spec 本身與更高優先依據來源衝突或需要使用者決定，標 `change-design-flaw` 並引用兩側；spec 措辭不清或不一致但可不改意圖修正者標 `conforms-but-flawed` 並註 'amend change'。每項引用 spec 原文；引用依據來源時寫出名稱與層級；列出實際查閱的依據來源；400 字內，查閱來源清單不計入 | §5 |
| E26 | 邊界條件 | 無 spec 時 | 跳過 Spec 審查，並在最終報告註明 | §5 |
| E27 | 產物格式 | 兩軸並列 | `## Standards` 與 `## Spec` 兩節，原文或輕度整理，保留每個 finding 的標記；不得合併或重新排序 findings | §6 |
| E28 | 產物格式 | 結尾摘要 | 一行：每軸 finding 總數、每軸各標記的數量、各軸內最嚴重的問題；不跨軸選出單一最嚴重，標記也不構成跨軸排序 | §6 |
| E29 | 產物格式 | 查閱依據來源清單 | 結尾附 Basis sources consulted：每個來源及其優先層級，或 `none`；此清單與執行模式說明不計入每軸字數上限 | §6 |
| E30 | 設計理由 | 為何雙軸 | 一軸通過不代表另一軸通過（守規範但做錯事；做對事但破壞慣例）；分開回報避免一軸遮蔽另一軸；標記是軸內屬性，不改變兩軸分離；`violates-change` 與 `change-design-flaw` 屬 Spec 軸，因為兩者都以審查中的 spec 為判斷對象，而非程式碼寫法 | Why two axes |

## 3. 其他

- 固定點（E9）只寫「使用者說的就是固定點，未給就問」；呼叫端可提供的只寫到複查用的快照 ref 或檔案清單（E10）。一般審查由呼叫端注入固定點的情形，本 skill 未寫，由 `orchestrator-factory` 的覆寫條款補上。
- merged 模式的「變更小」沒有判定門檻。
- 本 skill 未規定報告寫入位置；單獨使用時彙整結果呈現於對話。工廠模式的寫檔位置由 `orchestrator-factory` 覆寫條款規定。
- 標記定義（E7）以「程式碼 vs 審查中的 spec」為對象；change-review 的同名分類以「change 文件 vs 已定案需求」為對象。名稱相同、對象平行，E8 的「語意一致」指對應關係，並非同一段文字。
- `orchestrator-factory` 覆寫 (7) 列出三個標記時只在 `change-design-flaw` 後註明「只用於 Spec 軸」，沒有同時標出 `violates-change` 也只屬 Spec 軸（E7）；兩處不矛盾，但工廠端的註記較少。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/code-review.md`（前版 E1–E27，version 1.0）：

- 未變：前版 E1 → E1、E3 → E3、E5 → E9、E9 → E17、E10 → E18、E11 → E19、E12 → E20、E18 → E26。
- 修改：前版 E2 差異範圍由「`HEAD` 對固定點的三點式 diff」改為工作樹含未 commit 與未追蹤變更 → 本版 E2、E11。
- 修改：前版 E4 Spec 軸，spec 由「判斷基準」改為「審查對象之一，依依據來源優先序判斷」 → 本版 E4。
- 修改：前版 E6 早期失敗，條件改為追蹤 diff 或未追蹤清單至少一者非空 → 本版 E12。
- 移除：前版 E7 issue tracker 設定依賴（缺設定檔時執行外部 setup 指令）；改為本版 E5 按需取用。
- 修改：前版 E8 spec 來源順序，新增「呼叫端已指名就直接用」與 `openspec/changes/<id>/` 一項 → 本版 E13。
- 修改：前版 E13 平行雙 sub-agent 改為三種執行模式 → 本版 E21。
- 修改：前版 E14 Standards prompt 加入未追蹤清單與依據來源清單 → 本版 E22。
- 修改：前版 E15 Standards brief 加入標記規則 → 本版 E23。
- 修改：前版 E16 Spec prompt 加入依據來源清單與使用規則 → 本版 E24。
- 修改：前版 E17 Spec brief 加入 (d)(e) 與標記、依據來源引用與查閱清單 → 本版 E25。
- 移除：前版 E19 sub-agent 可見資訊（「prompt 未提及其他脈絡來源」）；本版 prompt 已帶入依據來源（E22、E24），該描述不再成立。
- 修改：前版 E20 兩軸並列，加入保留標記 → 本版 E27。
- 修改：前版 E21 結尾摘要，加入各標記數量 → 本版 E28。
- 修改：前版 E22 為何雙軸，加入標記與兩軸的關係 → 本版 E30。
- 移除：前版 E23 輸出位置（「未規定」屬缺項描述，改記於 §3）。
- 移除：前版 E24–E27 工廠覆寫與 Check worker 邊界；這些內容在 `orchestrator-factory`，不屬本 skill 檔案，本對照不列為元素。
- 新增：E6 每個 finding 一個標記。
- 新增：E7 三個標記定義。
- 新增：E8 標記與 change-review 共用。
- 新增：E10 複查用固定點。
- 新增：E14 依據來源四層（正本）。
- 新增：E15 依據來源的取得。
- 新增：E16 依據來源的使用。
- 新增：E29 查閱依據來源清單。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.1，last_updated 2026-10-20T13:40:41）。元素編號沿用。

新增：

- 無。

修改：

- E7 三個標記定義：`violates-change` 的適用軸由「Standards、Spec」改為「僅 Spec」（F23）。
- E8 標記與 change-review 共用：改為本表是正本，副本保持語意一致（F5）。
- E14 依據來源四層（正本）：副本要求改為與正本語意一致（F5）。
- E23 Standards brief：規範違反與異味一律標 `conforms-but-flawed`，不使用 `violates-change`；刪除 'prescribed by change' 註記（F23）。
- E30 為何雙軸：`violates-change` 與 `change-design-flaw` 都屬 Spec 軸（F23）。

移除：

- 無元素移除。

§3 變動：

- 移除「Standards brief 依 spec 明文決定標記，但 Standards prompt 沒有帶 spec」：Standards 軸已不使用 `violates-change`，不再需要 spec。
- 移除「四層依據副本措辭不同、一致性只是語意上的」：正本已明定副本保持語意一致。
- 新增「`orchestrator-factory` 覆寫 (7) 的軸別註記較少」。
