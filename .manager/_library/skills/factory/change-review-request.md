# change-review-request 元素對照

- 分支：factory
- 對照版本：`skills/change-review-request/SKILL.md` version 1.1，last_updated 2026-10-20T15:44:18
- 讀過的檔案：`SKILL.md`、`FORMAT.md`、`agents/openai.yaml`（僅 `allow_implicit_invocation: true`）；交叉引用核對（唯讀）：`change-review-response/SKILL.md`、`code-review/SKILL.md` step 3 與 Finding tags、`orchestrator-factory` 的 change-doc review 段落
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

change-review-request 由 brief 撰寫者（orchestrator／請求方）使用：在 apply 之前，為一個 OpenSpec change package 寫一份審查簡報 `change-review-request-NN.md`，交給另一位 reviewer 判斷 change 文件是否符合已定案的使用者需求。它不是程式碼審查，也不進行 apply。配對 skill 是 `change-review-response`；本目錄的 `FORMAT.md` 是 request 與 response 兩份文件段落格式與配對規則的唯一來源，並定義 verdict 規則（正本，含完整的 verdict 判定對應）、判斷詞彙與 concern 分類。

步驟順序：

1. 確定目標：工廠 `run_dir`（只有使用者已指定該 run 時才建立）、change package 路徑、依層級列出的決策脈絡來源、只在能支撐 checklist 項目時才列的選用路徑。
2. 選 `NN`：列出 `run_dir` 內既有 request，取下一個兩位數編號。
3. 依 `FORMAT.md` 全部段落撰寫：Meta、已定案需求、判斷原則、審查 checklist（保留邀請 reviewer 提出 checklist 外疑慮的固定段落）、參考路徑；Meta 指明預期 response 檔名。

完成後停止，除非使用者明確要求，否則不寫 response。在工廠流程中，這是 propose 之後的 opt-in 選項，永不自動強制（`orchestrator-factory`）。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | 使用者呼叫本 skill 或要求撰寫該審查簡報；允許隱含啟用 | frontmatter description、`agents/openai.yaml` |
| E2 | 角色 | brief 撰寫者 | orchestrator／請求方；產出交給同儕的簡報，內含 change package 與 checklist | 開頭段 |
| E3 | 邊界條件 | 非程式碼審查、非 apply | 簡報只針對 change package 文件 | 開頭段 |
| E4 | 共用格式 | FORMAT 為唯一來源 | 撰寫前先讀 `FORMAT.md`；它是 request 與 response 段落標題與配對規則的唯一來源；concern 分類名稱與正本 `code-review` 標記保持語意一致 | 開頭段、FORMAT 開頭 |
| E5 | 配對規則 | 同 run_dir、同 `NN` | request `change-review-request-NN.md` ↔ response `change-review-response-NN.md`；位置為同一工廠 `run_dir`（`.factory/_runs/<date>-<slug>/`）；`NN` 為該 `run_dir` 內的兩位數序號，request 與 response 共用 | §Handoff rules、FORMAT §Pairing |
| E6 | 配對規則 | 先寫 request | response 留給 reviewer；只有使用者明確要求時才在本輪建立 | §Handoff rules |
| E7 | 邊界條件 | reviewer 修改 change 的條件 | reviewer 只在使用者另行下令時才編輯 change package | §Handoff rules |
| E8 | 流程步驟 | 確定目標 | 工廠 `run_dir`（當前 run；只有使用者已指定工廠 run 在此時才建立）、change package `openspec/changes/<id>/`（proposal、design、tasks、相關 specs）；完成條件：`run_dir` 與 change id／路徑已知，且決策脈絡來源已列出或確認不存在 | §1 Resolve targets |
| E9 | 判斷規則 | 決策脈絡來源層級 | 依來源優先序（高到低）列出：1 使用者陳述或確認的資訊，含使用者確認後寫入 run 的交接項與決策；2 管理正本（存在時的 `.manager/`，唯讀）、主 OpenSpec specs、專案文件；3 run 中使用者未確認的討論筆記；change package 本身是第 4 層（審查對象）。與 `code-review` step 3 的正本保持語意一致；`.manager/_runs/` 只是線索；不論是否支撐 checklist 項目都要列出 | §1 Resolve targets |
| E10 | 流程步驟 | 選用路徑 | 範例文件、`AGENTS.md`、歸檔／schema 等，只在能支撐 checklist 項目時才列；FORMAT 的選用清單另含 db_schema 與 `_dispatch-plan.md` | §1、FORMAT §5 Optional |
| E11 | 流程步驟 | 選編號 | 列出 `run_dir` 內既有 `change-review-request-*.md`，取下一個未用的兩位數 `NN`（無則 `01`） | §2 Choose NN |
| E12 | 流程步驟 | 撰寫簡報 | 依 FORMAT 全部段落建立 `run_dir/change-review-request-NN.md`；Meta 的 Expected response 設為同 `NN` 的 response 檔名；完成條件：檔案存在、引用 change package、寫明預期 response 檔名 | §3 Write the brief |
| E13 | 判斷規則 | checklist 可判定性 | 每列必須能只憑 change 文件判為 pass／gap／unclear，有疑問時查閱所列決策脈絡來源 | §3 |
| E14 | 硬規則 | 保留固定邀請段 | FORMAT 請求文件 §4 邀請 reviewer 提出 checklist 以外疑慮的段落是固定文字，每份 brief 都保留、不得刪除 | §3、FORMAT（請求文件說明） |
| E15 | 產物格式 | Meta | run_dir、Change id、Change path、Purpose（apply 前判斷 change package 文件是否符合已定案需求）、Expected response（同 run_dir、由 reviewer 撰寫） | FORMAT 請求 §1 |
| E16 | 產物格式 | 已定案需求 | 編號列出 change 文件必須表達的已定案需求；只引用或轉述使用者定案者；本節是第 1 層來源，判斷時優先於所有其他來源 | FORMAT 請求 §2 |
| E17 | 產物格式 | 判斷原則 | 表格：原則／審查時如何使用 | FORMAT 請求 §3 |
| E18 | 產物格式 | 審查 checklist 與整體 verdict | 表格：#／Focus／Judgment／Evidence；要求 reviewer 每列判 pass／gap／unclear 並附檔案與章節證據；另要求整體 verdict（`ready to apply`／`needs doc fix`／`needs user clarify`）；固定邀請段：reviewer 可提出自己的疑慮，在 response 的 Reviewer concerns 依分類記錄，任一 `change-design-flaw` 使 verdict 至少為 `needs user clarify` | FORMAT 請求 §4 |
| E19 | 產物格式 | 參考路徑 | change package（必讀，審查對象）：proposal、design、tasks、相關 specs；決策脈絡來源（唯讀，有疑問時查）：依層級分組、高層在前、每項標層級，空層寫 `none`，change package 為第 4 層，第 1 層舉例為 run 中使用者確認的交接項（例如工廠 `_memory.md`）；選用路徑（E10）；層級清單（change package 為第 4 層）與 `code-review` step 3 的正本保持語意一致 | FORMAT 請求 §5 |
| E20 | 產物格式 | response 文件段落 | Overall verdict（三選一加一段理由）；Checklist results（鏡像 request 每列，附 change 文件路徑章節或決策脈絡來源並標層級）；Gaps and unclear items（全部 pass 時省略）；Reviewer concerns（一列一項，無則 `none`；`change-design-flaw` 列須寫出衝突的高層來源或說明為何判為設計缺陷；欄位為 Category／Concern／Evidence／Reasoning）；Context consulted（實際查閱的來源、層級與它校準了哪個判斷，brief 未列者標 "not in brief"，無則 `none`）；Recommended next action | FORMAT Response document |
| E21 | 產物格式 | next action 三值 | 恰一個：`confirm dispatch`（文件相符，使用者準備好就可往 apply 走）／`amend change`（指明要改的 change 檔與最小修正）／`needs_input`（只列使用者才能回答的問題） | FORMAT Response document |
| E22 | 判斷規則 | verdict 規則（正本） | checklist 全部 pass 且無疑慮 → `ready to apply`；有任一 gap 或 `conforms-but-flawed` 疑慮，且沒有 unclear 列與 `change-design-flaw` → `needs doc fix`；有任一 unclear 列或 `change-design-flaw` 疑慮 → `needs user clarify`；verdict 為 `needs user clarify` → next action 為 `needs_input` 並列出給使用者的問題；本清單是正本，其他重述 verdict 底線的 skill 與其保持語意一致 | FORMAT Verdict rules |
| E29 | 判斷規則 | 需使用者釐清項目的去向 | `needs user clarify` 的項目交給協調的 orchestrator，由其依資訊來源自行排除能判斷者，只把其餘彙整成一份清單交使用者；reviewer 不逐條直接對使用者提出 | FORMAT Verdict rules 後段 |
| E23 | 判斷詞彙 | pass／gap／unclear | pass＝change 文件清楚一致地表達已定案需求；gap＝已定案需求在 change 文件中缺漏、矛盾或不足，且只修 change 即可解決；unclear＝查過 change 文件與所列決策脈絡來源後仍無法判斷 | FORMAT Judgment vocabulary |
| E24 | 判斷詞彙 | concern 分類 | `conforms-but-flawed`：change 文件依循已定案需求，但在設計、task 切分、驗證步驟、內部一致性或可直接修正的措辭上有不改意圖即可修的問題；`change-design-flaw`：change 與更高層來源衝突，或解決問題需要使用者決定（例如不改意圖就無法修正的整體做法或底層原則）；定義與 `code-review` 標記、`change-review-response` 共用，與正本 `code-review` 標記保持語意一致 | FORMAT Concern categories |
| E25 | 判斷詞彙 | `violates-change` 的對應 | `code-review` 的第三個標記（偏離 change）在 change-review 中由 checklist 的 gap 承載，不出現在 concerns | FORMAT Concern categories |
| E26 | 判斷規則 | gap 與 `change-design-flaw` 的分界 | 已定案需求清楚、只修 change 即可解決 → gap（→ `needs doc fix`／`amend change`）；只修 change 即可解決的疑慮 → `conforms-but-flawed`；需要使用者決定（已定案需求本身看似不健全、brief 以外的更高層來源與 change 衝突、更高層來源彼此衝突）→ `change-design-flaw`（→ `needs user clarify`／`needs_input`） | FORMAT Concern categories 末段 |
| E27 | 完成條件 | 停止點 | 簡報存在於 `run_dir/change-review-request-NN.md`，指向 change package 與預期 response 後停止；除非使用者要求，不寫 response | §Completion |
| E28 | metadata | extends | frontmatter 最外層 `extends: change-review-response`（response 端反向 `extends: change-review-request`） | frontmatter |

## 3. 其他

- next action 的明文對應只有一條：verdict `needs user clarify` → `needs_input`（E22）。`ready to apply` 對應 `confirm dispatch`、`needs doc fix` 對應 `amend change`，只能從 E21 三值的說明與 E26 分界段落的箭頭推得，verdict 規則本身沒有列出。
- E13「只憑 change 文件即可判定」與同句「有疑問時查閱決策脈絡來源」並列；可讀為「以 change 文件為判斷對象、以脈絡來源校準」，但字面上「只憑」與「查閱其他來源」同時出現。
- 選用路徑清單在 SKILL §1（範例文件、`AGENTS.md`、歸檔／schema）與 FORMAT §5（另含 db_schema、`_dispatch-plan.md`）不完全相同。
- 雙向 extends：request 與 response 互相 `extends`（兩者都在 frontmatter 最外層）。僅記錄，不判定是否構成循環依賴。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/change-review-request.md`（前版 E1–E20，version 1.0）：

- 未變：前版 E1 → E1、E2 → E2、E3 → E3、E5 → E6、E6 → E7、E8 → E11、E11 → E15、E13 → E17、E18 → E27、E19 → E28。
- 修改：前版 E4 配對規則，`run_dir` 路徑由 `.factory/<date>-<slug>/` 改為 `.factory/_runs/<date>-<slug>/` → 本版 E5。
- 修改：前版 E7 確定目標拆為 E8（加入決策脈絡來源的完成條件，路徑同上更新）、E9（新增決策脈絡來源層級）、E10（選用路徑）。
- 修改：前版 E9 撰寫簡報，FORMAT 參考路徑段落分為 change package、決策脈絡來源、選用路徑 → 本版 E12。
- 修改：前版 E10 checklist 可判定性，加入「有疑問時查閱決策脈絡來源」 → 本版 E13。
- 修改：前版 E12 已定案需求，加入「本節為第 1 層來源、優先於所有其他來源」 → 本版 E16。
- 修改：前版 E14 審查 checklist，加入 reviewer 疑慮固定邀請段與 `change-design-flaw` 的 verdict 底線 → 本版 E18。
- 修改：前版 E15 參考路徑，改為 change package 必讀、決策脈絡來源依層級分組，工廠 `_memory.md` 由選用路徑移為第 1 層舉例 → 本版 E19。
- 修改：前版 E16 判斷詞彙，gap 加入「只修 change 即可解決」，unclear 改為「查過 change 文件與所列決策脈絡來源後仍無法判斷」 → 本版 E23。
- 修改：前版 E17 FORMAT 為兩 skill 共用，加入 concern 分類須與 `code-review` 標記一致 → 本版 E4。
- 移除：前版 E20 工廠銜接（opt-in 位置）；內容在 `orchestrator-factory`，不屬本 skill 檔案，本對照只在摘要提及。
- 新增：E14 保留固定邀請段。
- 新增：E20 response 文件段落（含 Reviewer concerns、Context consulted）。
- 新增：E21 next action 三值。
- 新增：E22 verdict 規則（正本）。
- 新增：E24 concern 分類。
- 新增：E25 `violates-change` 的對應。
- 新增：E26 gap 與 `change-design-flaw` 的分界。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.1，last_updated 2026-10-20T14:08:54）。元素編號沿用，新元素接續編號並依章節位置插入。

新增：

- E29 需使用者釐清項目的去向：交給協調的 orchestrator 自行排除後彙整成一份清單，reviewer 不逐條對使用者提出（F24）。

修改：

- E4 FORMAT 為唯一來源：concern 分類改為與正本 `code-review` 標記保持語意一致（F5）。
- E9 決策脈絡來源層級：副本要求改為與 `code-review` step 3 正本語意一致（F5）。
- E19 參考路徑：層級清單改為與正本語意一致（F5）。
- E22 verdict 規則：由「`change-design-flaw` 底線與 `needs user clarify` → `needs_input`」擴充為三種 verdict 的完整判定對應（F24）；副本要求改為語意一致（F5）。
- E24 concern 分類：一致性要求改為與正本語意一致（F5）。
- E28 extends：由 `metadata` 底下移到 frontmatter 最外層（U2）。

移除：

- 無元素移除。

§3 變動：

- 「verdict 與 next action 的對應不完整」改寫：verdict 判定已完整，只剩 `ready to apply`、`needs doc fix` 對應的 next action 未在規則中明列。
- 移除「四層來源與 concern 定義副本措辭不同」：各處已統一為與正本語意一致。
- 雙向 extends 項更新位置為 frontmatter 最外層。
