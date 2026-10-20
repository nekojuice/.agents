# doc-sop-guide 元素對照

- 分支：doc
- 對照版本：`skills/doc-sop-guide/SKILL.md` version 1.2，last_updated 2026-10-20T13:33:25
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`；父層 `skills/doc-general-guide/SKILL.md`（version 1.2，用於核對引用章節）
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

doc-sop-guide 規範 SOP／runbook／cheat-sheet：給已熟悉環境的操作者（setup、deploy、restart、recover）走最短指令路徑。它擴充 doc-general-guide，衝突時以本 guide 為準。定位是「SOP 是程序，不是說明」：只寫依序執行的指令、要做的動作、如何確認成功；「不寫理由」是 SOP 類型的規則，架構理由歸 README，需要逐步理由的第一次操作者改用教學。

結構：範圍與界線（SOP 對教學、盤點清單）→ Inherited 表 12 列與 Overrides 表 6 列 → 硬規則 8 條 → 結構規則 4 條 → 動筆前流程 → 正反範例 → 完成檢查清單。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 適用範圍 | 建立或修改 SOP、runbook、cheat-sheet；讀者是已熟悉環境的操作者；不適用：給第一次操作者的教學（`doc-tutorial-guide`）、終端使用者的應用程式手冊（`doc-user-guide`）、獨立盤點／稽核清單（依 doc-general-guide）；`disable-model-invocation: false`，openai 允許隱式呼叫 | frontmatter；`agents/openai.yaml` |
| E2 | 角色 | 程序而非說明 | 讀者要知道依序執行什麼指令、做什麼動作、怎麼確認成功；判準：一句話若不是叫操作者做某事或檢查結果，可能不屬於 SOP；不寫理由是 SOP 類型規則，不是所有操作文件的規則；架構理由歸 README，需要逐步理由的第一次操作者用教學，不在 SOP 開「為什麼」例外 | 開頭兩段 |
| E3 | 繼承與覆寫 | 擴充宣告 | `extends: doc-general-guide`；先讀父層的共通基礎；衝突時本 guide 為準 | frontmatter；開頭第三段 |
| E4 | 邊界條件 | SOP 與教學分工 | SOP／runbook／cheat-sheet：熟悉環境的操作者、最短路徑、指令導向、每個指令配一個預期結果、不寫理由，歸本 guide；教學：第一次操作者、多為 UI 步驟、允許簡短理由與結果對照表，歸 `doc-tutorial-guide`；兩者依文件類型區分，不混寫在同一份，需要時互相連結 | Scope and boundaries |
| E5 | 邊界條件 | 盤點清單界線 | 獨立的盤點／稽核清單不是 SOP，依 doc-general-guide §0.1；SOP 內的服務、埠、端點表只服務本 SOP 的步驟 | Scope and boundaries |
| E6 | 繼承與覆寫 | Inherited §1 素材與驗證 | 父層 §1 由淺入深蒐集素材（有 openspec 時必讀）與驗證規則 1–5 全部套用；Process 只補 SOP 情境；只寫已定案狀態 | Inherited from doc-general-guide |
| E7 | 繼承與覆寫 | Inherited §2.5 清單用表格 | 服務、埠、端點、網址 | Inherited from doc-general-guide |
| E8 | 繼承與覆寫 | Inherited §2.6 範圍聲明 | 作為 SOP 開頭，可接服務／端點表 | Inherited from doc-general-guide |
| E9 | 繼承與覆寫 | Inherited §2.7 可命名物件 | 指令、旗標、路徑、設定鍵、容器名、log 字串 | Inherited from doc-general-guide |
| E10 | 繼承與覆寫 | Inherited §3 標題 | 名稱優先、標題不放狀態，套用到每個步驟標題 | Inherited from doc-general-guide |
| E11 | 繼承與覆寫 | Inherited §4 括號規則 | 原樣套用到散文與註記 | Inherited from doc-general-guide |
| E12 | 繼承與覆寫 | Inherited §2.13 不造詞 | 步驟文字與註記用平實、廣泛使用的用語 | Inherited from doc-general-guide |
| E13 | 繼承與覆寫 | Inherited §2.14 單一語言 | 一份 SOP 一種語言；指令與識別字原樣保留 | Inherited from doc-general-guide |
| E14 | 繼承與覆寫 | Inherited §2.15 範例值一次 | 寫了「以 `<env>` 為例」之後不再重寫；寫「改成實際值」 | Inherited from doc-general-guide |
| E15 | 繼承與覆寫 | Inherited §2.16 識別資訊佔位 | 帳號、主機、內部網址、人、組織寫成 `<placeholder>`；不寫秘密 | Inherited from doc-general-guide |
| E16 | 繼承與覆寫 | Inherited §2.17 職責範圍 | 職責外步驟只寫一行「請 `<owning role>` 處理」 | Inherited from doc-general-guide |
| E17 | 繼承與覆寫 | Inherited §2.18 與既定決策一致 | 不寫與主 spec 或決策紀錄相違的做法，替代方案或反例也不寫 | Inherited from doc-general-guide |
| E18 | 繼承與覆寫 | Overrides §2.11 設計理由 | SOP 永不包含理由 | Overrides |
| E19 | 繼承與覆寫 | Overrides §2.12 `>` 註記上限 | 由最多 2 行改為最多 1 行（硬規則 4） | Overrides |
| E20 | 繼承與覆寫 | Overrides §5 指令上方步驟註解 | 註解只標預期輸出或目標（硬規則 3） | Overrides |
| E21 | 繼承與覆寫 | Overrides §2.8 參數意義表 | SOP 不帶參數解釋 | Overrides |
| E22 | 繼承與覆寫 | Overrides §2.8 分節不拆檔 | SOP 依環境或受眾拆成各自完整的檔案，見 Structure | Overrides |
| E23 | 繼承與覆寫 | Overrides §7 檢查清單 | 由本 guide 的完成檢查清單取代 | Overrides |
| E24 | 硬規則：指令 | 指令放 code block | 同父層 §2.1；附反例（條列中內嵌指令）與正例（標題、code block、一行結果） | Hard rules 1 |
| E25 | 硬規則：指令 | 多步驟編號 | 同父層 §2.2；也不把「先 X → 再 Y」流程寫進 code block 註解；附反例與正例 | Hard rules 2 |
| E26 | 硬規則：註解 | 註解只標指令 | 允許預期輸出（`# PONG`）、目標（`# → <data-dir>`）；不允許結果／行為描述、多動作指示、解釋；行為說明移到 block 後單行 `>` | Hard rules 3 |
| E27 | 硬規則：註記 | 註記一行且精確 | 每個註記最多一行 `>`；刪除模糊用語，改成具體陳述；附模糊與具體的對照 | Hard rules 4 |
| E28 | 硬規則：指令 | 手動編輯寫成散文 | 同父層 §2.3；手動編輯是 `cp` 指令後的一句散文，不是假裝成步驟的註解 | Hard rules 5 |
| E29 | 硬規則：指令 | 給真實設定指令 | 同父層 §2.4 | Hard rules 6 |
| E30 | 硬規則：範圍 | 不重述範圍 | 同父層 §3.4；已限定環境的 SOP 不再加範圍修飾 | Hard rules 7 |
| E31 | 硬規則：範圍 | 標題寫實際範圍 | 同父層 §3.3；Staging、Prod 等環境或受眾有意義，放在標題或分檔 | Hard rules 8 |
| E32 | 結構 | 依環境／受眾分檔 | 流程差異大時拆成各自完整的檔案，不寫滿條件分支；共用步驟重複可接受，每檔須能獨立使用 | Structure |
| E33 | 結構 | 執行順序 | 依操作者實際執行順序；開發機上的部署前動作（測試、發布）排在目標機設定之前；必要時用 `0a`、`0b` 子步驟 | Structure |
| E34 | 結構 | 指令配預期結果 | 每段為「指令 → 預期結果／驗證」，給操作者可目視確認的檢查；附範例 | Structure |
| E35 | 結構 | 清單用精簡表格 | 啟動的服務、端點、UI／網址、埠用精簡表格 | Structure |
| E36 | 流程步驟 | 動筆前驗證 | 先套用父層 §1 驗證規則 1–5；SOP 常見情境：讀步驟用到的實際 compose、env、設定、腳本檔；引用的腳本在另一個專案、白名單漏掉需要的目錄，都會讓 SOP 錯誤；會發布壞掉內容的發布步驟要標出並提修正，不照寫 | Process (before writing) |
| E37 | 產物格式 | 正反範例 | 兩組：內嵌指令＋模糊結果 → 標題、code block、精確註記；註解內的流程 → 編號步驟 | Examples |
| E38 | 完成條件 | 完成檢查清單 | 11 項：文件是 SOP 而非教學或盤點清單、指令 code block、編號步驟、註解與註記、範圍修飾與標題、設定指令與手動編輯、執行順序、以現有檔案驗證、分檔、缺陷已標出、繼承規則（括號、識別資訊、範例值、職責範圍、不造詞、單一語言） | Completion checklist |

## 3. 其他

- **父層章節存在性**：Inherited 與 Overrides 表及硬規則引用的 §1、§2.1–§2.8、§2.11–§2.18、§3、§3.3、§3.4、§4、§5、§7、§0.1 皆存在於 doc-general-guide 1.2，內容與引用描述相符。
- **部分 Overrides 列是重述而非覆寫**：E18（§2.11）與 E21（§2.8 參數意義表）在父層原本就適用於 SOP（父層 §2.11 預設不寫理由，§2.8 已寫「SOP 禁止這類解釋」）；E22 覆寫的 §2.8「不拆檔」在父層只針對工程參考手冊。三列的作用是明示，與父層不衝突。
- **硬規則 4 的對照**：E19 與 E27 一致（`>` 註記一行）；檢查清單「notes are single `>` lines」與之相符。
- 其餘無衝突或缺口。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/doc/doc-sop-guide.md`（前版 version 1.1，E1–E16）。

- 修改 E1 適用範圍（前 E1）：由「任何如何操作／部署／設定文件」縮小為熟悉環境的操作者，加入 cheat-sheet，並列出不適用的三類與對應 skill。
- 修改 E2 程序而非說明（前 E2）：明寫「不寫理由」是 SOP 類型規則，理由歸 README，第一次操作者改用教學。
- 新增 E3 擴充宣告（`extends: doc-general-guide`，前版不提父層）。
- 新增 E4 SOP 與教學分工、E5 盤點清單界線。
- 新增 E6–E17 Inherited 12 列、E18–E23 Overrides 6 列。
- 修改 E24、E25、E28（前 E3、E4、E7）：改為引用父層 §2.1、§2.2、§2.3，範例換成通用虛構名稱。
- 修改 E29 給真實設定指令（前 E8）：改為只引用父層 §2.4，本 skill 不再自帶範例。
- 修改 E30、E31（前 E9 合併一列）：拆成兩條並分別引用父層 §3.4、§3.3。
- 修改 E26、E27（前 E5、E6）：規則不變，範例換成佔位符與通用虛構內容。
- 修改 E32（前 E10）：規則不變，環境範例換成 staging／prod。
- 修改 E34（前 E12）：規則不變，範例容器名換成通用虛構名稱。
- 修改 E35（前 E13）：開頭範圍聲明自 Structure 移除，改由 E8（Inherited §2.6）承接；清單表格維持。
- 修改 E36 動筆前驗證（前 E14）：四條自有規則改為引用父層 §1 驗證規則 1–5，另列三個 SOP 情境。
- 修改 E37 正反範例（前 E15）：兩組結構不變，內容換成通用虛構名稱。
- 修改 E38 完成檢查清單（前 E16）：9 項增為 11 項，新增「是 SOP 而非教學或盤點清單」與「繼承規則」兩項。
- 不變：E33（前 E11）。
