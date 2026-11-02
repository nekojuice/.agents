# opsx-apply-guide 元素對照

- 分支：factory
- 對照版本：`skills/opsx-apply-guide/SKILL.md` version 1.3，last_updated 2026-11-02T11:47:29
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`（僅 `allow_implicit_invocation: true`）；交叉引用核對（唯讀）：`orchestrator-factory` 的 `### Amendment rounds`、self-fix 段落、§2 清單層級與 apply prompt 的 `verification_level`，`opsx-propose-guide` 的 Amendments、§5 與 §6，`need-ask-user-guide` 的 `## Present pending decisions at checkpoints` 標題
- 狀態：已檢查，2026-11-02 移入 manager 正式文件

## 1. 摘要

給「套用（apply）opsx change 的 session」的實作紀律。這個 session 通常沒有 propose 對話的脈絡，必須依賴 change 文件並忠實執行。機械步驟交給 `openspec-apply-change`，測試流程交給 `test-first`（frontmatter 最外層 `extends: openspec-apply-change, test-first`）；本 skill 只補上那兩者沒涵蓋的工作紀律。

在工廠流程中，它屬於 Apply 階段，由 apply worker 與 `openspec-apply-change`、`test-first`、`hard-verify` 一起載入；工廠的 self-fix 引用本 skill 的 anti-cheat 作為測試變更的唯一來源，工廠在 propose 時依本 skill §4 設定 run 的清單層級，經 `verification_level` 傳給 apply worker。

工作順序：逐 task 實作，每個 task 完成即勾選，每節完成時回頭對帳 → 以 test-first 實作，單元測試全綠為完成標準 → 全程遵守測試變更紀律（anti-cheat），想改測試但任務包未要求時停下回報 → 不自行跑 E2E，改寫成給人執行的步驟 → 收尾時產出開發者驗證清單，層級分兩級：broad（預設，大型或連鎖實作的端到端功能或業務流程）與 focused（使用者發起的小修改或 debug，寫必看事項，debug 時寫 bug 原因），寫入 `tasks.md` 尾段，並在對話或回傳結果中呈現 → 誠實回報完成狀態；過程中遇到範圍外發現就回報，不自行更新 change 任務以外的文件，實作與任務包不同就記錄偏離。若處理的是修訂輪，另依 Amendment rounds：以被取代行為為測試改寫邊界，並在 `tasks.md` 記錄測試對應。

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
| E19 | 邊界條件 | 清單抽象層級（正本） | 本節是正本，`opsx-propose-guide` 與協調流程引用它。分兩級，採用協調者指定的層級（例如 `verification_level`），否則依工作判斷：broad（預設；大型或連鎖實作）每項是端到端的功能或業務流程，有 UI 時以 UI 操作描述，不列個別控制項、訊息文字、內部實作；focused（使用者發起的小修改或 debug）寫明修改後必須觀察的事項，debug 時寫 bug 原因，修改對象是控制項或訊息時點名它。兩級共通：同一畫面的檢查歸在同一項或同一處；只列需要人判斷的，排除單元測試或硬檢查已涵蓋者與簡單邏輯檢查（`need-ask-user-guide` 的 `## Present pending decisions at checkpoints`）；附三則佔位對照（對 broad 過細、broad、focused），聲明只示層級、不是範本 | §4 |
| E27 | 邊界條件 | self-fix 修好的問題不列 | 在 self-fix 輪次中修好的問題不列入清單，也不會讓工作變成 focused | §4 |
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
- **引用本節的 `opsx-propose-guide` §6 仍是單一層級**：該 skill §5 已改為「依本 skill §4 設定的層級」，但 §6 交出前檢查清單的 Verification skeleton 項仍寫「human-only 項目在功能或流程層級」，沒有反映 focused 級可點名控制項與訊息。
- 章節編號：Test changes (anti-cheat) 與 Amendment rounds 是未編號的二級標題，插在 §2 與 §3 之間；交叉引用以標題名稱進行，可對上。

## 4. 與前版差異

對照前版對照稿（version 1.2，last_updated 2026-10-20T15:52:52）與 `git diff HEAD`。元素編號沿用，新元素接續編號並依章節位置插入。

新增：

- E27 self-fix 修好的問題不列入清單，也不使工作變成 focused。

修改：

- E19 清單抽象層級：由單一層級（每項是功能或業務流程，不列個別控制項、訊息文字、內部實作）改為 broad 與 focused 兩級，採用協調者指定的層級（例如 `verification_level`），否則依工作判斷；broad 加入端到端與「有 UI 時以 UI 操作描述」；focused 寫必看事項、debug 時寫 bug 原因、可點名修改對象的控制項或訊息；佔位對照由兩則（過細、適當層級）改為三則（對 broad 過細、broad、focused）。
- 摘要：加入兩級清單，以及工廠經 `verification_level` 傳遞層級。

移除：

- 無。

§3 變動：

- 新增「引用本節的 `opsx-propose-guide` §6 仍是單一層級」。
