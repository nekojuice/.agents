# opsx-propose-guide 元素對照

- 分支：factory
- 對照版本：`skills/opsx-propose-guide/SKILL.md` version 1.3，last_updated 2026-10-20T15:43:47
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`（僅 `allow_implicit_invocation: true`）；交叉引用核對（唯讀）：`orchestrator-factory` 的 `### Amendment rounds` 與 Propose 階段、`opsx-apply-guide` 的 `## Amendment rounds` 與 §4
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

給「指揮型 agent」的 propose 撰寫紀律。指揮型 agent 是與使用者討論並定案的中樞，決定走 opsx 流程後，產出要交給其他模型或 session 實作的 change 任務包。機械步驟（跑 CLI、產生 `proposal.md`／`design.md`／`tasks.md`）仍交給 `openspec-propose`（frontmatter 最外層 `extends: openspec-propose`）；本 skill 只規範怎麼切範圍、命名、排序與揭露，讓沒有這段對話脈絡的實作者也能正確執行。

在工廠流程中，它屬於 Propose 階段，與 `openspec-propose`、`test-first` 一起載入（`orchestrator-factory` 階段表）。

使用順序：與使用者對齊並決定走 opsx → 建包時依序處理：§1 切範圍 → §2 命名編號 → §3 以文字寫明相依順序，涉及跨 repo 共用值時在 `design.md` 指定唯一來源 → §4 雙軌揭露假設並逐 change 分配 → §5 在 `tasks.md` 鋪驗證骨架 → 若任務包要求文件或範例，規定識別資訊用虛構名稱 → 交出前依 §6 檢查清單逐項自檢。撰寫修訂（apply 後、archive 前修改既有 change）時另依 Amendments 一節標註。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 角色 | 指揮型 agent | 與使用者討論定案的中樞；產出的任務包通常委派給其他模型或 session，以便平行協作 | 開頭段 |
| E2 | 角色 | 與 `openspec-propose` 分工 | 機械步驟交給 `openspec-propose`；本 skill 只約束範圍、命名、排序、揭露，目標讀者是零脈絡的實作者 | 開頭段、frontmatter |
| E3 | 觸發條件 | 使用時機 | 已與使用者對齊且決定走 opsx；即將建立要交給另一 session 實作的任務包；建包全程與交出前都適用；允許隱含啟用 | When to use、`agents/openai.yaml` |
| E4 | 範圍 | 一個內聚工作單位 | 每個 change 是能整體審查、整體回退的內聚單位；task 是其中的小步驟。混雜無關關注點、跨層宜分開審、太大難以整體推理時拆分；太小無法獨立或離開兄弟工作就無意義時合併 | §1 |
| E5 | 硬規則 | 不寫 commit | change 文件不得寫任何 commit 相關內容，產包過程也不做 commit；「工作單位」只是撰寫者的尺寸參考，不得以指示或動作形式出現在 change 中 | §1 |
| E6 | 產物格式 | 命名與編號 | 系列或有順序的 change 用 `<series>-<NN>-<subtitle>`，`NN` 固定兩位數；無後續的獨立 change 不編號，用一般 kebab-case | §2 |
| E7 | 產物格式 | 相依與順序以文字表達 | change 內有鏈狀順序時在 `tasks.md` 寫明先後與原因；跨 change 相依寫在 `proposal.md` 固定位置（例如 `Depends on:` 行，寫明須先合併），以文字而非工具 metadata 表達 | §3 |
| E8 | 產物格式 | 跨 repo 契約 | change 觸及跨 repo 共用的契約值（介面形狀、常數、訊息格式）時，在 `design.md` 寫明唯一來源（哪一側、哪個定義為準）與一致性驗證方式，並把該驗證加入驗證骨架；另一側的 change 引用該來源，不自行寫死副本 | §3 Cross-repo contracts |
| E9 | 硬規則 | 假設雙軌揭露 | 代使用者決定的邊界與假設屬可變決定；須同時寫進 `proposal.md` 固定段落（例如 `## Assumptions & Decisions Made`），並在建包後於對話中以條列回報給使用者；兩軌都不可省 | §4 |
| E10 | 邊界條件 | 系列逐 change 分配 | 討論工作表是分配用輸入而非貼上內容：只寫已定案的；每包只列本 change 實作的項目；每項只有一個擁有者，後續 change 以引用代替重複；屬於未來兄弟 change 的項目寫明延後到哪個 change 並省略細節，範例為 `alert-03-retention-policy`，符合 `<series>-<NN>-<subtitle>` | §4 Per-change allocation |
| E11 | 流程步驟 | 修訂的定義與分工 | 修訂指 apply 之後、archive 之前修改 change；何時修訂既有 change、何時開新 change、適用哪些人閘，以 `orchestrator-factory` 的 `### Amendment rounds` 為準，本 skill 不重新定義 | Amendments |
| E12 | 產物格式 | 修訂標註 | 在 change 文件標明修訂輪次、原因、日期；追加的 tasks 放在 `tasks.md` 的獨立小節，讓實作者分辨修訂工作與原始工作 | Amendments |
| E13 | 硬規則 | 指明被取代的行為 | 修訂改變既有行為時，寫明取代了哪一項行為；這是實作者可改寫或刪除既有斷言的唯一邊界（`opsx-apply-guide` 的 `## Amendment rounds`） | Amendments |
| E14 | 邊界條件 | 修訂沿用紀律 | 追加的 tasks 同樣要有驗證骨架（§5）與雙軌假設揭露（§4） | Amendments |
| E15 | 邊界條件 | 大規模修訂 | 修訂取代某功能大部分行為，或舊測試已無法一對一對應到新行為時，標為大規模（工廠模式由 orchestrator 標記，否則由撰寫修訂的指揮型 agent 標記），並要求實作者在 `tasks.md` 列出每個被改寫或刪除的測試及其原涵蓋行為 | Amendments |
| E16 | 產物格式 | 驗證骨架 | 在 `tasks.md` 鋪驗證骨架：需要測試的寫單元測試意圖（test-first）；只需檢查的寫檢查什麼；端對端／瀏覽器驗證標為 human-only，由開發者手動執行，實作 session 不自行驅動 | §5 |
| E17 | 邊界條件 | 人工項目抽象層級 | human-only 項目寫在功能或業務流程層級、依畫面分組、只列需要人判斷的；不列個別控制項、訊息文字、內部實作，也不列單元測試或硬檢查已涵蓋者（`need-ask-user-guide`）；正本規則在 `opsx-apply-guide` §4；附一組佔位對照（過細 vs 適當層級），聲明只示層級、不是範本 | §5 |
| E18 | 硬規則 | 驗證安全邊界 | 任何步驟不得執行會印出秘密值的指令，確認秘密存在時只列檔名；不得呼叫付費外部服務；確實需要真實付費服務時標為 human-only 並註明成本與副作用 | §5 |
| E19 | 邊界條件 | 骨架不是腳本 | 骨架只是雛形；最終具體驗證清單由實作 session 產出（可與骨架不同）並當時與使用者確認；不得寫成僵硬腳本 | §5 末段 |
| E20 | 硬規則 | 範例識別資訊 | 任務包要求文件、README 或範例時，要求範例中的識別資訊（帳號、主機、組織、產品等）使用匿名虛構名稱或佔位；工具本身與專案本身的名稱除外；tasks 不得指示實作者使用真實外部名稱 | Example identifiers in requested docs |
| E21 | 人閘／自檢 | 交出前檢查清單 | 十項：Scope（含不得有 commit 指示）、Naming、Ordering、Assumptions（本 change 限定、不貼整份工作表、不把未定 TBD 當指示、跨 change 以引用重用）、Self-containment、Acceptance（成功條件具體到實作者能判定完成）、Verification skeleton（含人工項目層級、不印秘密、不呼叫付費服務）、Cross-repo contracts、Example identifiers、Amendments（寫明被取代行為並依 Amendments 標註） | §6 |
| E22 | 硬規則 | 不提供填空範本 | 不給交接填空模板，避免下游「抄作業」而失焦；只說明任務包必須包含什麼，讓每包依自身工作撰寫 | §6 末段 |

## 3. 其他

- 「Acceptance（成功條件具體）」只出現在 §6 檢查清單，正文各節沒有對應說明。
- 修訂的觸發條件、修訂與開新 change 的分界、人閘（E11）只定義在 `orchestrator-factory`；非工廠情境單獨使用本 skill 時，這些規則仍須讀工廠 skill 才能取得。
- §5 提到 test-first 的單元測試意圖，但沒有提到 `test-first` 要先鎖定 seam；骨架是否應寫出 seam 未說明。
- 章節編號：Amendments 與 Example identifiers in requested docs 是未編號的二級標題，分別插在 §4 與 §5、§5 與 §6 之間；正文與檢查清單以「section N」或標題名稱引用，引用本身可對上。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/opsx-propose-guide.md`（前版 E1–E13，version 1.2）：

- 未變：前版 E1–E7 → 本版 E1–E7；E3 補記允許隱含啟用（前版寫在來源欄）。
- 編號變動、內容未變：前版 E8 → E9、E9 → E10、E10 → E16、E11 → E19、E13 → E22。
- 修改：前版 E12 交出前檢查清單由七項增為十項，新增 Cross-repo contracts、Example identifiers、Amendments，Verification skeleton 項加入人工項目層級與安全條件 → 本版 E21。
- 新增：E8 跨 repo 契約。
- 新增：E11 修訂的定義與分工。
- 新增：E12 修訂標註。
- 新增：E13 指明被取代的行為。
- 新增：E14 修訂沿用紀律。
- 新增：E15 大規模修訂。
- 新增：E17 人工項目抽象層級。
- 新增：E18 驗證安全邊界。
- 新增：E20 範例識別資訊。
- 移除：無。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.3，last_updated 2026-10-20T11:50:09）。元素編號沿用。

新增：

- 無。

修改：

- E10 系列逐 change 分配：延後範例由 `alert-03` 補上副標為 `alert-03-retention-policy`（F19）。
- E15 大規模修訂：判定標準由「重塑大範圍」改為「取代某功能大部分行為，或舊測試已無法一對一對應到新行為」（F22）。
- 摘要中的 frontmatter 描述：`extends` 由 `metadata` 底下移到最外層（U2）；E2 內容不變。

移除：

- 無。

§3 變動：

- 移除「延後範例缺 subtitle」：範例已補副標。
- 移除「重塑大範圍沒有判定門檻」：已有判定標準。
- 移除「`extends` 放在 `metadata` 底下」：已移到最外層。
