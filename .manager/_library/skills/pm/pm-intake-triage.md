# pm-intake-triage 元素對照

- 分支：pm
- 對照版本：`skills/pm-intake-triage/SKILL.md` version 1.1，last_updated 2026-10-20T11:49:52
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/case-classification.md`、`references/grouping-and-deduplication.md`、`references/triage-outcomes.md`
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`pm-intake-triage` 是 PM 模式下的進件分流流程。它把混雜的進件（問題、回饋、疑似 bug、設計疑慮、風險、構想）轉成直接回答、有界調查，或以共同成果或根因為核心的候選；過程保留原始語意、減少重複與不必要的工廠工作。只在明確的 orchestrator-pm 模式內使用，不建立也不啟動工廠工作。每個候選標記路線：`factory` 的候選等人明確建立後交 `pm-factory-handoff`；`non-product` 的候選改交 orchestrator-pm 的非產品路線。

流程九步：

1. 每筆輸入各自記錄為來源項。
2. 正規化問題、觀察行為、預期行為、影響、環境、現有證據。
3. 可靠的專案證據足夠時直接回答。
4. 只有證據支持共同原因、相依或共同期望成果時才分組，保留每個原始來源項的連結。
5. 需要有界的程式、文件或舊系統比對時，派 `pm-investigation-worker`。
6. 為每一項分類。
7. 以一致的成果或根因組成候選，而不是以進件數量；受管對象屬非產品路線時，候選的執行路徑是該路線。
8. 呈現候選的理由、範圍邊界、證據、信心、相依、未知。
9. 等人明確建立後才呼叫 `pm-factory-handoff`；`non-product` 候選不呼叫它，改交非產品路線，仍等該路線要求的人工指示。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 使用範圍 | 只在明確的 orchestrator-pm 模式內，有一筆或多筆進件需要回答、調查、依根因分組、延後、拒絕或提為候選時使用；`disable-model-invocation: false`，openai 允許隱式呼叫；`extends: orchestrator-pm, pm-investigation-worker, pm-factory-handoff` | frontmatter；`agents/openai.yaml` |
| E2 | 硬規則 | 一份進件不等於一個候選 | 不把單一進件直接對應成一個工廠候選 | § Hard rules |
| E3 | 硬規則 | 不建立工廠工作 | 不建立也不啟動工廠工作 | § Hard rules |
| E4 | 硬規則 | 分流與調查期間不改 | 分流或調查期間不改產品檔、受管對象、正典狀態；非產品路線的受管對象只經該路線、在人指示後才改 | § Hard rules |
| E5 | 硬規則 | 保留原件 | 保留原始進件、來源、陳述的嚴重度 | § Hard rules |
| E6 | 硬規則 | 區分三種陳述 | 區分觀察事實、回報者假設、PM 推論 | § Hard rules |
| E7 | 人閘 | 需要人的決定 | 預期行為未定義且答案會改變分類時問人；預期行為、優先序、專案方向或建立權限無法推得時，一次問一個具體決定 | § Hard rules；triage-outcomes § Human decision needed |
| E8 | 產物格式 | 六種型別 | question（有支持的答案即可不經工廠結案）、suspected-bug（預期或行為未充分驗證）、confirmed-bug（預期與違反行為或實作路徑皆有證據）、design-concern（照實作運作但設計造成可用性、正確性、維護、安全或營運傷害）、initiative（不以修正缺陷為主的能力或成果）、risk（可能傷害交付或營運，但尚未成為缺陷或核可方向）；分類不明時保持 investigating，說明需要什麼證據 | case-classification |
| E9 | 邊界條件 | 分組條件 | 至少要有一種關係：同一個已確認或強烈懷疑的根因、同一個期望專案成果、一方是另一方的症狀或相依、一個工廠變更可一起解決且不帶入無關範圍。只因同一畫面、repo、客戶或日期，不得分組 | grouping-and-deduplication |
| E10 | 產物格式 | 分組保留欄位 | 原始來源編號與措辭、各自環境與影響、關係的證據、剩餘差異、分組信心；不確定時保持各自獨立，以 `possibly-related` 連結，直到調查釐清 | grouping-and-deduplication |
| E11 | 產物格式 | 處置定義 | answered（答案與證據，不需候選）；investigating（有界問題、缺漏證據、指派的 worker 產物、下一檢查點）；duplicate or related（保留每筆並指向主群組或案件，不刪除原件）；factory candidate（一個一致成果、來源項、理由、邊界、相依、證據、信心、未解問題，不等於核可工作）；deferred（理由與客觀的重審條件）；rejected（無效、無支持、無附加價值的重複或不符方向的理由）；human decision needed（見 E7） | triage-outcomes |
| E12 | 產物格式 | 候選路線標記 | 每個候選標 `factory` 或 `non-product`；在非產品路線下，同一處置代表執行路徑為該路線的變更候選（run 內異動決策、直接修改、git diff 審查），不是工廠交接，仍不等於核可工作 | triage-outcomes § Factory candidate；§ Workflow 7 |
| E13 | 流程步驟 | 分類步驟的值域 | Workflow 6 的值域混合處置與型別：answered、investigating、duplicate-or-related、suspected-bug、confirmed-bug、design-concern、initiative、risk、deferred、rejected | § Workflow 6 |
| E14 | 流程步驟 | 候選的後續交付 | `factory` 候選等人明確建立後才呼叫 `pm-factory-handoff`；`non-product` 候選不呼叫 `pm-factory-handoff`，交給 orchestrator-pm 的非產品路線，仍等該路線要求的人工指示 | § Workflow 9 |
| E15 | 產物格式 | 輸出 | `PM_TRIAGE_RESULT_V1`：source_count、answered（來源編號、答案、證據）、investigating（來源編號、問題、指派產物）、duplicate_or_related（群組、來源編號、分組證據）、factory_candidates（候選編號、route factory／non-product、成果、來源、理由、信心、未知）、deferred（來源編號、理由、重審條件）、rejected（來源編號、理由）、human_decisions_needed | § Output |
| E16 | 產物格式 | 細節位置 | 耐久細節寫進目前的 manager run；聊天只放精簡彙整 | § Output 末段 |

## 3. 其他

- **分類值域與輸出欄位不對應**：Workflow 6 的值域混合型別與處置（E13），沒有 candidate；輸出沒有型別欄位，分類為 suspected-bug、design-concern 等的項目在輸出中放在哪個欄位，要靠它同時是 investigating 或候選來推斷。
- **欄位名稱與路線**：輸出欄位仍叫 `factory_candidates`，但內容包含 `non-product` 路線的候選；分組條件第四項也以「一個工廠變更」為準，沒有非產品路線的對應說法。
- **與 backlog 的銜接**：本 skill 不改正典狀態，只把細節寫在 run；分流結果如何進入 `_backlog.md` 依 `orchestrator-pm` 的 run 收斂升級規則，本 skill 沒有直接提到。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/pm/pm-intake-triage.md`（前版 version 1.0）：

- 修改 E3 不建立工廠工作（前版 E3）：「等人明確建立後才呼叫交接」移到 E14。
- 修改 E4（前版 E4「調查期間不改」）：範圍擴為分流與調查期間，對象加入受管對象，並規定非產品路線受管對象只經該路線、人指示後才改。
- 修改 E7 需要人的決定（前版 E7）：併入 triage-outcomes 的 human decision needed 條件（前版列在 E11）。
- 修改 E11 處置定義（前版 E11「七種處置定義」）：human decision needed 移到 E7。
- 新增 E12 候選路線標記（`factory`／`non-product`）。
- 新增 E14 候選的後續交付（`non-product` 候選不呼叫 `pm-factory-handoff`）。
- 修改 E15 輸出（前版 E13）：`factory_candidates` 加入 route 欄位。
- 移除：無。
