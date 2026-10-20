# opsx-apply-guide 元素對照

- 分支：factory
- 對照版本：`skills/opsx-apply-guide/SKILL.md` version 1.2，last_updated 2026-10-20T15:52:52
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`（僅 `allow_implicit_invocation: true`）；交叉引用核對（唯讀）：`orchestrator-factory` 的 `### Amendment rounds` 與 self-fix 段落、`opsx-propose-guide` 的 Amendments 與 §5、`need-ask-user-guide` 的 `## Present pending decisions at checkpoints` 標題
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

給「套用（apply）opsx change 的 session」的實作紀律。這個 session 通常沒有 propose 對話的脈絡，必須依賴 change 文件並忠實執行。機械步驟交給 `openspec-apply-change`，測試流程交給 `test-first`（frontmatter 最外層 `extends: openspec-apply-change, test-first`）；本 skill 只補上那兩者沒涵蓋的工作紀律。

在工廠流程中，它屬於 Apply 階段，由 apply worker 與 `openspec-apply-change`、`test-first`、`hard-verify` 一起載入；工廠的 self-fix 引用本 skill 的 anti-cheat 作為測試變更的唯一來源。

工作順序：逐 task 實作，每個 task 完成即勾選，每節完成時回頭對帳 → 以 test-first 實作，單元測試全綠為完成標準 → 全程遵守測試變更紀律（anti-cheat），想改測試但任務包未要求時停下回報 → 不自行跑 E2E，改寫成給人執行的步驟 → 收尾時產出開發者驗證清單（寫入 `tasks.md` 尾段，並在對話或回傳結果中呈現）→ 誠實回報完成狀態；過程中遇到範圍外發現就回報，不自行更新 change 任務以外的文件，實作與任務包不同就記錄偏離。若處理的是修訂輪，另依 Amendment rounds：以被取代行為為測試改寫邊界，並在 `tasks.md` 記錄測試對應。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 角色 | 套用 session | 處理指揮型 agent 打包交出的 tasks；通常沒有 propose 對話脈絡，只依 change 文件忠實執行 | 開頭段 |
| E2 | 角色 | 與其他 skill 分工 | 機械步驟用 `openspec-apply-change`，測試流程用 `test-first`；本 skill 只補工作紀律 | 開頭段、frontmatter |
| E3 | 觸發條件 | 使用時機 | 實作 opsx change 的 tasks 時；實作全程與收尾時都適用；允許隱含啟用 | When to use、`agents/openai.yaml` |
| E4 | 流程步驟 | 即時勾選 | `tasks.md` 中每個標題群組是一節；每個 task 完成時立即把 `- [ ]` 改成 `- [x]`，與 `openspec-apply-change` 一致 | §1 |
| E5 | 流程步驟 | 逐節對帳 | 每節完成時回頭確認每個勾選都對應已完成的工作、該節沒有默默略過；不可把整個 change 的勾選留到最後，結束時勾選必須反映實況 | §1 |
| E6 | 硬規則 | test-first 與完成標準 | 依 `test-first` 先寫失敗的單元測試再寫程式；單元測試全綠即為「完成」的標準，不需要更高層級的自動化測試；測試聚焦真實行為與邏輯，不以瑣碎或框架提供的行為灌水 | §2 |
| E7 | 硬規則 | anti-cheat 適用範圍 | 適用於每個 apply session，不論單獨或被委派，也包括修復建置、測試、lint 等硬檢查失敗時 | Test changes (anti-cheat) |
| E8 | 硬規則 | 修實作、不弱化測試 | 修的是實作；可依 `test-first` 新增表達 change 所需行為的測試；不得以弱化、刪除或改寫斷言或測試讓檢查變綠。明列禁止：為過閘刪除或放寬失敗測試、註解掉斷言、放寬 matcher 到任何結果都通過 | Test changes (anti-cheat) |
| E9 | 邊界條件 | 測試刪改的例外 | 只有任務包明文要求時（例如 `tasks.md`／`design.md` 說明行為已改、舊測試須移除）才可移除或改寫測試；修訂輪中以被取代行為為邊界 | Test changes (anti-cheat) |
| E10 | 人閘 | 無授權改測試時停下回報 | 想改測試但任務包沒有要求時，停下並回報：被委派時回報委派者（工廠模式為 `needs_input`／stop-for-human），否則回報使用者；不當一般修正處理 | Test changes (anti-cheat) |
| E11 | 流程步驟 | 修訂輪的定義與分工 | 修訂輪指 apply 之後、archive 之前修改 change；何時修訂或開新 change、適用哪些人閘以 `orchestrator-factory` 的 `### Amendment rounds` 為準；change 文件如何標註以 `opsx-propose-guide` 的 Amendments 為準；本節只管實作端 | Amendment rounds |
| E12 | 流程步驟 | 修訂 tasks 的勾選 | 追加的 tasks 依 §1 勾選與對帳；保留修訂標註不動 | Amendment rounds |
| E13 | 硬規則 | 被取代行為為改寫邊界 | 只有直接斷言「修訂指明為被取代之行為」的測試可改寫或刪除；其他測試仍受 anti-cheat 約束；需要改測試但修訂沒有指明被取代行為時，停下回報 | Amendment rounds |
| E14 | 硬規則 | 改寫測試仍走 test-first | 改寫後的測試須先因正確的理由失敗，再改程式 | Amendment rounds |
| E15 | 產物格式 | 修訂測試對應紀錄 | 在 `tasks.md` 記錄每個被改寫或刪除的測試、它原本涵蓋的行為、所屬的修訂項目；此紀錄與偏離紀錄（§7）分開，不在偏離中重複 | Amendment rounds、§7 |
| E16 | 邊界條件 | 大規模修訂 | 判定標準：修訂取代某功能大部分行為，或舊測試已無法一對一對應到新行為。修訂被標為大規模時（工廠模式由 orchestrator 標記，否則由撰寫修訂的指揮型 agent 標記），逐一列出每個被改寫或刪除的測試與原行為，供審查者（工廠模式為 Check worker）逐項核對；未被標記但符合判定標準時同樣逐一列出，寧多勿少 | Amendment rounds |
| E17 | 硬規則 | E2E 僅限人工 | apply 流程中不得操作瀏覽器或 UI 自動化工具做端對端驗證，改把 E2E 步驟寫給開發者；此限制只適用 apply 驗證，不管使用者在流程外自行使用瀏覽器工具 | §3 |
| E18 | 產物格式 | 開發者驗證清單的內容與擁有者 | 收尾時由套用 session 擁有最終清單（實作可能與 proposal 預想不同），由使用者確認；有測試的列出應測項目，含手動 E2E 步驟；只需檢查的列出檢查項目 | §4 |
| E19 | 邊界條件 | 清單抽象層級（正本） | 本節是正本，`opsx-propose-guide` 與協調流程引用它：每項是功能或業務流程；同一畫面的檢查歸在同一項或同一處；不列個別控制項、訊息文字、內部實作；只列需要人判斷的，排除單元測試或硬檢查已涵蓋者與簡單邏輯檢查（`need-ask-user-guide` 的 `## Present pending decisions at checkpoints`）；附一組佔位對照，聲明只示層級、不是範本 | §4 |
| E25 | 硬規則 | 驗證清單安全邊界 | 與 `opsx-propose-guide` §5 相同：任何步驟不得執行會印出秘密值的指令，確認秘密存在時只列檔名；不得呼叫付費外部服務；確實需要真實付費服務時標為 human-only 並註明成本與副作用 | §4 |
| E20 | 產物格式 | 清單雙軌交付 | 寫入 `tasks.md` 尾端固定段落（例如 `## Developer verification`），並在回覆中直接告知使用者以便當場確認或調整；由協調者委派時改放在回傳結果中，由委派者呈現給使用者；兩軌都不可省 | §4 |
| E21 | 邊界條件 | 每個 change 各自一份 | 每個 change 保有自己的清單；跨 change 或跨 run 的彙整屬協調流程，不屬本 skill | §4 |
| E22 | 硬規則 | 誠實回報完成 | 單元測試失敗或有 task 未完成時，不得勾選 task／節或宣稱完成；測試失敗或略過步驟要直說並附實際失敗輸出；勾選代表「已驗證」 | §5 |
| E23 | 邊界條件 | 範圍外發現 | 發現任務包未涵蓋的事（相關 bug、需要的重構、缺少的決策）要回報使用者並由使用者決定，不得默默擴大範圍 | §6 |
| E26 | 邊界條件 | 不更新任務以外的文件 | 範圍外發現包含文件：不更新 change 任務以外的任何文件；README 與其他文件的同步依協調流程的文件同步規則，例如 `orchestrator-factory` 規則 14：預設只同步 README，其他文件須使用者確認列出的清單後才更新 | §6 |
| E24 | 產物格式 | 記錄偏離 | 實作與任務包描述不同時，在 `tasks.md` 記下實際做法與原因，讓文件與成品一致；修訂輪的測試對應不算偏離 | §7 |

## 3. 其他

- E6 以單元測試全綠為完成標準；E7 已提到建置、lint 等硬檢查的修復，但完成標準本身未納入這些硬檢查。工廠模式下 apply worker 須通過 `hard-verify`（含建置、lint）作為出口閘，實際標準更高；本 skill 未說明兩者關係。
- 修訂輪的觸發、修訂與開新 change 的分界、人閘（E11）只定義在 `orchestrator-factory`；非工廠情境單獨使用本 skill 時，須讀工廠 skill 才能取得這些規則。
- E26 的 README 與其他文件同步交給「協調流程的文件同步規則」；單獨使用、沒有協調流程時，只有「不更新 change 任務以外的文件」一句適用，README 是否同步沒有另外說明。
- 章節編號：Test changes (anti-cheat) 與 Amendment rounds 是未編號的二級標題，插在 §2 與 §3 之間；交叉引用以標題名稱進行，可對上。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/opsx-apply-guide.md`（前版 E1–E10，version 1.1）：

- 未變：前版 E1–E3 → 本版 E1–E3；E3 補記允許隱含啟用。
- 修改：前版 E4 逐節對帳勾選拆為 E4 即時勾選與 E5 逐節對帳；勾選時點由「小 task 不必完成當下立刻勾」改為「每個 task 完成即勾」。
- 編號變動、內容未變：前版 E5 → E6、E6 → E17、E8 → E22、E9 → E23。
- 修改：前版 E7 開發者驗證清單（雙軌）拆為 E18、E19、E20、E21；被委派時第二軌改放回傳結果、由委派者呈現（E20）。
- 修改：前版 E10 記錄偏離 → 本版 E24，加註修訂輪測試對應不算偏離。
- 新增：E7 anti-cheat 適用範圍。
- 新增：E8 修實作、不弱化測試。
- 新增：E9 測試刪改的例外。
- 新增：E10 無授權改測試時停下回報。
- 新增：E11 修訂輪的定義與分工。
- 新增：E12 修訂 tasks 的勾選。
- 新增：E13 被取代行為為改寫邊界。
- 新增：E14 改寫測試仍走 test-first。
- 新增：E15 修訂測試對應紀錄。
- 新增：E16 大規模修訂。
- 新增：E19 清單抽象層級（正本）。
- 新增：E21 每個 change 各自一份。
- 移除：無。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.2，last_updated 2026-10-20T11:50:09）。元素編號沿用，新元素接續編號並依章節位置插入。

新增：

- E25 驗證清單安全邊界：引用 `opsx-propose-guide` §5，不印秘密值、不呼叫付費外部服務（F20）。
- E26 不更新任務以外的文件：README 與其他文件同步依協調流程規則，例如 `orchestrator-factory` 規則 14（F6、複查修正）。

修改：

- E16 大規模修訂：加入判定標準「取代某功能大部分行為，或舊測試已無法一對一對應到新行為」；未標記時的條件由「發現大量測試須改」改為「符合判定標準」（F22）。
- 摘要中的 frontmatter 描述：`extends` 由 `metadata` 底下移到最外層（U2）；E2 內容不變。

移除：

- 無。

§3 變動：

- 移除「最終驗證清單沒有安全條件」：已新增 E25。
- 移除「大量測試與大規模沒有判定門檻」：已有判定標準。
- 新增「單獨使用時 README 同步沒有另外說明」。
