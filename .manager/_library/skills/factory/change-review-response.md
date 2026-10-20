# change-review-response 元素對照

- 分支：factory
- 對照版本：`skills/change-review-response/SKILL.md` version 1.1，last_updated 2026-10-20T15:44:18
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`（僅 `allow_implicit_invocation: true`）、`../change-review-request/FORMAT.md`（本 skill 的格式來源）；交叉引用核對（唯讀）：`change-review-request/SKILL.md`、`code-review/SKILL.md` step 3 與 Finding tags、`orchestrator-factory` 的 change-doc review 段落
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

change-review-response 由 reviewer 使用：讀取 `change-review-request-NN.md` 與其引用的 change package，寫出配對的 `change-review-response-NN.md`。change package 是審查對象，brief 的已定案需求是第 1 層依據；reviewer 對每列 checklist 給判斷與證據，並保有自身判斷，可在 checklist 以外依分類提出疑慮；最後給整體 verdict 與唯一的下一步。不進行 apply、不修改 change。

步驟順序：

1. 讀 brief：使用者指定的 request，或當前 `run_dir` 中最新且尚未配對的 request；以 Meta、已定案需求、原則、checklist、參考路徑（含決策脈絡來源）為審查範圍。
2. 讀 change package：讀 brief 列出的路徑；有疑問時依層級由高到低唯讀查閱決策脈絡來源，不夠時可再查 brief 以外的來源，並記錄查閱了什麼。
3. 寫 verdict：依 FORMAT 的 response 段落撰寫整體 verdict、checklist 結果、gap／unclear 說明、reviewer 疑慮、查閱過的脈絡、建議下一步；verdict 依 FORMAT 的 verdict 規則選擇，需使用者釐清的項目交給協調的 orchestrator。

在工廠流程中，orchestrator 讀取 verdict 與 next action 後自行給出經檢查的建議；verdict 不是 `ready to apply` 時，在使用者修正、釐清或明確覆寫前，不把 dispatch 確認視為放行（`orchestrator-factory`）。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | 使用者呼叫本 skill 或要求回覆該審查簡報；允許隱含啟用 | frontmatter description、`agents/openai.yaml` |
| E2 | 角色 | verdict 撰寫者 | reviewer；讀 brief 與 change package，寫配對的 response | 開頭段 |
| E3 | 判斷規則 | 審查對象與第 1 層依據 | change package 是審查對象；brief 的已定案需求是第 1 層依據 | 開頭段 |
| E4 | 硬規則 | 保有自身判斷 | 除 checklist 外，可依分類提出自己的疑慮 | 開頭段 |
| E5 | 硬規則 | 不 apply | apply 留給之後另行下達的指令；完成後停止，不開始 apply | 開頭段、§Completion |
| E6 | 共用格式 | 格式來源在兄弟目錄 | 撰寫前讀 `../change-review-request/FORMAT.md`；配對 skill 為 `change-review-request`；frontmatter 最外層 `extends: change-review-request` | 開頭段、frontmatter |
| E7 | 配對規則 | 同 run_dir、同 `NN` | 與 request 一對一配對；request 先寫，本 skill 只產出 response | §Handoff rules |
| E8 | 邊界條件 | 不改 change package | 除非使用者另行下令修改，否則 change package 保持不變 | §Handoff rules、§Completion |
| E9 | 判斷規則 | 依據來源四層 | 優先序由高到低：1 使用者陳述或確認的資訊（brief 的已定案需求、使用者確認的交接項）；2 管理正本、主 OpenSpec specs、專案文件；3 使用者未確認的討論筆記；4 change package 本身（可能有錯或不清的設計藍圖）。與 `code-review` step 3 的正本保持語意一致 | Basis and context |
| E10 | 判斷規則 | 脈絡只用於校準 | 用脈絡排除誤報（已在他處決定或修正）或確認真正的不一致；不得加入 brief 與更高層來源都沒要求的需求；提出疑慮，不改寫需求 | Basis and context |
| E11 | 判斷規則 | `change-design-flaw` 與 verdict 底線 | change 與更高層來源衝突、或解決問題需要使用者決定時，記為 `change-design-flaw`；verdict 至少為 `needs user clarify`，next action 為 `needs_input`；不選邊；更高層來源彼此衝突時也交給使用者；此底線與正本（FORMAT 的 verdict 規則）保持語意一致 | Basis and context |
| E12 | 硬規則 | 來源唯讀 | 所有來源唯讀、不得寫入；來源看似過時或錯誤時，在對應疑慮或 Context consulted 中註明，不修改來源 | Basis and context |
| E13 | 流程步驟 | 讀 brief | 開啟指定的 request（使用者路徑，或當前 `run_dir` 中最新且未配對者）；以 Meta、已定案需求、原則、checklist、參考路徑（含決策脈絡來源）為審查範圍；完成條件：預期 response 檔名、change 路徑、每列 checklist 都已知 | §1 Read the brief |
| E14 | 流程步驟 | 讀 change package | 讀 brief 列出的 change package 路徑（proposal、design、tasks、指名的 specs，選用路徑只讀某列 checklist 需要者）；以這些檔案的證據為優先，不自創需求 | §2 Read the change package |
| E15 | 流程步驟 | 補查脈絡 | 有疑問時依層級由高到低，唯讀查閱 brief 列出的決策脈絡來源；仍不足以判斷時，可再唯讀查閱其他 run 紀錄、主 OpenSpec specs、專案文件、`.manager/` 正本；`.manager/_runs/` 只是線索；記錄每個查閱的來源、brief 是否列出、它校準了哪個判斷 | §2 |
| E16 | 完成條件 | unclear 的成立時點 | 每列 checklist 都有足以判 pass 或 gap 的材料；只有在查過脈絡後仍不足時才維持 unclear | §2 Done when |
| E17 | 流程步驟 | 寫 verdict | 在 `run_dir/change-review-response-NN.md`（與 request 同 `NN`、同 `run_dir`）依 FORMAT 全部段落撰寫：Overall verdict、Checklist results、Gaps and unclear items、Reviewer concerns、Context consulted、Recommended next action | §3 Write the verdict |
| E18 | 產物格式 | verdict 與 checklist 結果 | verdict 為 `ready to apply`／`needs doc fix`／`needs user clarify` 之一（FORMAT 要求附一段理由）；request 的每列都給判斷與證據（change 檔案與章節，或脈絡來源及其層級）；gap／unclear 逐項說明缺什麼或哪裡模糊並附證據，全部 pass 時省略該段（FORMAT） | §3、FORMAT Response document |
| E19 | 判斷規則 | concern 分類 | 每個疑慮依 FORMAT 的 Concern categories 歸類：`conforms-but-flawed`（依循 change；不改意圖即可修正，含可直接修正的 change 措辭）或 `change-design-flaw`（與更高層來源衝突或需要使用者決定），附證據與理由；無疑慮時寫 `none`；定義與 FORMAT、`code-review` 標記共用，與正本 `code-review` 標記保持語意一致 | §3、FORMAT Response document |
| E23 | 判斷規則 | verdict 選擇 | 依 FORMAT 的 verdict 規則：每列 pass 且無疑慮 → `ready to apply`；任一 gap 或 `conforms-but-flawed` 疑慮 → `needs doc fix`；任一 unclear 列或 `change-design-flaw` 疑慮 → `needs user clarify`，next action 為 `needs_input` | §3 |
| E24 | 邊界條件 | 需使用者釐清項目的去向 | `needs user clarify` 的項目交給協調的 orchestrator，由其依資訊來源自行排除能判斷者，只把其餘彙整成一份清單交使用者；reviewer 不逐條對使用者提出 | §3 |
| E20 | 產物格式 | Context consulted | 列出每個實際查閱的決策脈絡來源、其層級、它校準了哪個判斷；brief 未列者標 "not in brief"；沒查任何來源時寫 `none` | §2、FORMAT Response document |
| E21 | 產物格式 | 建議下一步 | 恰一個：`confirm dispatch`／`amend change`（指明要改的 change 檔與最小修正）／`needs_input`（只列使用者才能回答的問題）；verdict 底線與 `needs user clarify` → `needs_input` 依 FORMAT 的 verdict 規則 | §3、FORMAT Response document、FORMAT Verdict rules |
| E22 | 完成條件 | 停止點 | response 存在於 request 指定的路徑；checklist 全覆蓋；Reviewer concerns 與 Context consulted 已寫；next action 已寫明；停止，不開始 apply、不修改 change | §Completion |

## 3. 其他

- E19 的簡短定義寫 `conforms-but-flawed` 為「依循 change」；FORMAT 的完整定義是「change 文件依循已定案需求」。在 change-review 中 change 是審查對象、依循的對象應為已定案需求；兩處措辭不同，且本 skill 同時要求與 FORMAT 保持語意一致。
- E23 的 verdict 選擇摘要省略了 FORMAT 的排除條件：FORMAT 寫「任一 gap 或 `conforms-but-flawed` 疑慮，且沒有 unclear 列與 `change-design-flaw`」才是 `needs doc fix`；本 skill 只寫「任一 gap 或 `conforms-but-flawed` 疑慮 → `needs doc fix`」。gap 與 unclear 並存時，字面上兩條都成立，須回到 FORMAT 才知道取 `needs user clarify`。
- `ready to apply`、`needs doc fix` 對應的 next action 沒有明文（同 `change-review-request` 對照 §3）；只有 `needs user clarify` → `needs_input` 明列。
- E13 未指定路徑時取「最新且未配對」的 request；多個未配對 request 並存時如何處理未說明。
- E15 允許查閱 brief 以外的來源，並要求在 Context consulted 標層級；brief 以外來源的層級歸屬只能依 E9 的四層類別自行判斷，沒有另外的指引。
- 雙向 extends：與 `change-review-request` 互相 `extends`（兩者都在 frontmatter 最外層）。僅記錄，不判定。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/factory/change-review-response.md`（前版 E1–E20，version 1.0）：

- 未變：前版 E1 → E1、E2 → E2、E5 → E5、E6 → E7、E7 → E8、E10 → E14（併入）、E12 → E18（verdict 部分）、E14 → E18（gap／unclear 說明部分）、E18 → E6。
- 移除：前版 E3 只審 change 文件（「預設只看 change 文件，除非 request 另有說明」）；改為本版 E3 change package 是審查對象。
- 移除：前版 E4 停留在已定案需求；改為本版 E3（已定案需求為第 1 層依據）、E4（保有自身判斷）、E9（依據來源四層）。
- 修改：前版 E8 讀 brief，範圍加入決策脈絡來源 → 本版 E13。
- 修改：前版 E9 只讀 brief 列出的參考路徑，改為可依層級補查 brief 以外的來源 → 本版 E14、E15。
- 修改：前版 E11 寫 verdict，FORMAT 段落加入 Reviewer concerns 與 Context consulted → 本版 E17。
- 修改：前版 E13 checklist 結果，證據可為脈絡來源並標層級 → 本版 E18。
- 修改：前版 E15 建議下一步，加入依 FORMAT verdict 規則的對應 → 本版 E21。
- 修改：前版 E16 unclear 定義，改為查過所列決策脈絡來源後仍無法判斷 → 本版 E16。
- 修改：前版 E17 停止點，加入 Reviewer concerns、Context consulted 已寫與不修改 change → 本版 E22。
- 移除：前版 E19、E20 工廠銜接（角色區隔、verdict 效力）；內容在 `orchestrator-factory`，不屬本 skill 檔案，本對照只在摘要提及。
- 新增：E4 保有自身判斷。
- 新增：E9 依據來源四層。
- 新增：E10 脈絡只用於校準。
- 新增：E11 `change-design-flaw` 與 verdict 底線。
- 新增：E12 來源唯讀。
- 新增：E15 補查脈絡。
- 新增：E19 concern 分類。
- 新增：E20 Context consulted。

### 第二輪修改（`changes/25-round2-fixes.md`）

對照本對照稿前一版（version 1.1，last_updated 2026-10-20T13:32:15）。元素編號沿用，新元素接續編號並依章節位置插入。

新增：

- E23 verdict 選擇：本 skill §3 列出三種 verdict 的判定對應（F24）。
- E24 需使用者釐清項目的去向：交給協調的 orchestrator 彙整，reviewer 不逐條對使用者提出（F24）。

修改：

- E6 格式來源：`extends` 由 `metadata` 底下移到 frontmatter 最外層（U2）。
- E9 依據來源四層：副本要求改為與 `code-review` step 3 正本語意一致（F5）。
- E11 verdict 底線：改為與正本（FORMAT verdict 規則）語意一致（F5）。
- E19 concern 分類：一致性要求改為與正本 `code-review` 標記語意一致（F5）。

移除：

- 無元素移除。

§3 變動：

- 「verdict 與 next action 的對應不完整」改寫：verdict 判定已補齊，只剩兩種 verdict 的 next action 未明列。
- 新增「E23 的 verdict 選擇摘要省略 FORMAT 的排除條件」。
- 雙向 extends 項更新位置為 frontmatter 最外層。
