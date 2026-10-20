# pm-factory-handoff 元素對照

- 分支：pm
- 對照版本：`skills/pm-factory-handoff/SKILL.md` version 1.1，last_updated 2026-10-20T14:08:54
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`、`references/handoff-contract.md`、`references/context-sanitization.md`、`assets/factory-intake.template.md`、`assets/factory-status.template.md`、`assets/factory-memory.template.md`
- 狀態：已檢查，2026-10-20 移入 manager 正式文件

## 1. 摘要

`pm-factory-handoff` 是 PM 通往工廠的出口。人明確核可把某個已識別的候選交給工廠之後，它在 `.factory/_runs/<YYYY-MM-DD>-<slug>/` 建立一份自足的冷啟動包（`_intake.md`、`_status.md`、`_memory.md`），供人另起的工廠 session 的指揮者讀取；然後在 manager run 記錄交接並停止。它不載入 `orchestrator-factory`、不啟動任何 worker。PM 在權威上位於工廠上游，但兩邊的工作區在操作上隔離。交接檔可以把 `.manager` 標為選擇性的背景參考，但每個必要事實都要以值寫入交接。

流程九步：

1. 驗證人的核可，並在 manager run 的 outcome 引述。
2. 呈現委派摘要（候選、目標、範圍邊界、擬定的工廠 run 標題／slug）並取得確認；人明確要求直接建立、不確認時可跳過。
3. 決定唯一的 `.factory/_runs/<YYYY-MM-DD>-<slug>/` 路徑；`.factory/.gitignore` 不存在時建立，內容為單行 `_runs/`。
4. 把候選蒸餾成已確認的目標、脈絡、範圍、排除、限制、證據、開放問題、預期人工檢查點。
5. 由本 skill 的範本產生三個檔案。
6. 確認沒有必要內容只存在於 `.manager`（以值重述），移除工廠不讀 `.manager` 就看不懂的 PM 專用術語，把剩下的 manager 參照全部標為選擇性。
7. 驗證這份交接在沒有 PM 對話紀錄的新 session 中仍然可用。
8. 在 manager run 的 `outcome.md` 記錄工廠 run 路徑；除非人另外要求盤點，否則不更新正典狀態。
9. 向人回報工廠 run 路徑，說明可另起工廠 session，然後停止。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 呼叫政策 | `disable-model-invocation: false`，openai `allow_implicit_invocation: true`；`extends: orchestrator-pm`；description 寫明只在人明確核可建立特定候選後使用 | frontmatter；`agents/openai.yaml` |
| E2 | 觸發條件 | 前提條件 | 四項全部滿足：人明確指示把一個已識別候選交接／派工／委派給工廠（實作者），中文同義詞或任何不含糊的等義說法都算；目前 manager run 已記錄候選成果；已確認的範圍足以說明為何要開工廠；沒有會讓交接誤導的未解矛盾。PM 建議、候選標籤、試探性討論都不算核可 | § Preconditions |
| E3 | 角色 | 冷啟動包作者 | 寫出的每個檔案都是工廠指揮者開始新 session 的冷啟動包，不是 PM 工作記憶；PM 權威在上游，兩邊工作區在操作上隔離 | 開頭段 |
| E4 | 硬規則 | 不越界到工廠 | 不載入或呼叫 `orchestrator-factory`；不啟動 worker、不提出實作、不改產品檔、不跨越任何工廠閘 | § Hard rules |
| E5 | 硬規則 | 不依賴 manager、只可選擇性提及 | 不要求未來的工廠 session 讀 `.manager`；factory-facing 檔可以把 `.manager` 列為選擇性的唯讀背景，但每個必要事實都要以值寫入交接；不得指示工廠寫入 `.manager`。Workflow 6 落實為三件事：必要內容不只存在於 `.manager`、移除工廠看不懂的 PM 專用術語、剩下的 manager 參照標為選擇性 | § Hard rules；§ Workflow 6 |
| E6 | 硬規則 | 不整批轉移 | 不複製 scratch 筆記、worker 逐字紀錄、未確認假設，也不整批複製 PM library | § Hard rules |
| E7 | 硬規則 | 不覆寫 | 不覆寫既有工廠 run；只有人明確恢復同一份交接時才重用；不覆寫無關的 run | § Hard rules；handoff-contract § Directory |
| E8 | 人閘 | 核可引述與委派摘要確認 | 先驗證並在 manager run 的 outcome 引述人的核可；建立任何工廠檔案前，呈現候選、目標、範圍邊界、擬定標題／slug 並取得確認；只有人明確要求直接建立、不確認時才跳過 | § Workflow 1、2 |
| E9 | 產物格式 | 路徑與 `.gitignore` | `.factory/_runs/<YYYY-MM-DD>-<slug>/`，須唯一，slug 限小寫英數與連字號；`.factory/.gitignore` 不存在時建立，內容為單行 `_runs/` | § Workflow 3；handoff-contract § Directory |
| E10 | 邊界條件 | 冷啟動包不是跨方交接檔 | 冷啟動包是新工廠 run 自己的控制檔，不使用跨方交接檔的 `handoff-<recipient>-<topic>.md` 命名（該命名只用於留在寄件方 run 根目錄的交接檔） | handoff-contract § Directory |
| E11 | 產物格式 | `_intake.md` | 九項：目標與業務或專案理由、已確認脈絡、範圍內成果、明確排除、限制與已接受決策、證據與相關專案路徑、交由工廠討論的開放問題、預期驗證與人工檢查點、選擇性來源（manager run 與候選編號，標為工廠永遠不需要讀的線索） | handoff-contract § `_intake.md` |
| E12 | 產物格式 | intake 範本 | 段落：Goal、Why now、Confirmed context、In scope、Explicit exclusions、Constraints、Evidence and project paths、Open questions for factory discussion、Verification intent、Source (optional)、Human checkpoints；Human checkpoints 預設兩項：派工前審閱工廠討論與提案、最終驗收前做人工 E2E | `assets/factory-intake.template.md` |
| E13 | 產物格式 | `_status.md` | 狀態設為 `await-factory-session`，註明工廠未啟動、須由人另起工廠 session。範本欄位：Stage、Factory started: no、Intake、Shared memory、Next（人另起工廠 session 並提供本 run 目錄）、Blockers（intake 未解問題只是討論輸入） | handoff-contract § `_status.md`；`assets/factory-status.template.md` |
| E14 | 產物格式 | `_memory.md` | 只放每個後續工廠 worker 都可能需要的簡短共享事實；範本段落 Confirmed facts、Accepted constraints、Important paths；不複製整份 intake 或 PM 歷史 | handoff-contract § `_memory.md`；`assets/factory-memory.template.md` |
| E15 | 邊界條件 | 獨立性測試 | 只認識專案工作區與這個工廠 run 的新 session，必須能理解：為何可能需要這項工作、什麼已確認、什麼被排除、還要討論什麼、人核可與未核可什麼。若必須讀 `.manager` 或 PM 對話，交接就不完整 | handoff-contract § Independence test；§ Workflow 7 |
| E16 | 邊界條件 | 可追溯性在 manager 側 | 與 manager 案件的正式追溯記在 manager 端 outcome；factory-facing 檔內的任何 manager 參照都只是線索；交接後不更新正典狀態，除非人另外要求盤點 | handoff-contract § Independence test 末段；§ Workflow 8 |
| E17 | 去脈絡 | Include 清單 | 人核可的成果；與成果相關的已確認行為、限制、事實、決策；工廠可檢視的精確來源或專案路徑；已知相依與排除；標為開放的問題；驗收意圖（不捏造實作細節） | context-sanitization § Include |
| E18 | 去脈絡 | Exclude 清單 | 任何讓 `.manager` 參照變成必讀的措辭（必要內容以值轉移，PM 來源 metadata 只在工廠用得上時保留）；PM scratch 與內部討論；worker 逐字紀錄或無支持的結論；無關 library 條目；實作不需要的客戶識別或敏感資料；應由工廠討論決定的過早技術設計；PM 專用術語；要求工廠向 PM 回報或回呼的指示（回流路徑由工廠自己的規則決定） | context-sanitization § Exclude |
| E19 | 去脈絡 | 以值轉移 | 需要 manager 的事實或決策時，在 intake 重述已確認內容，有權威專案來源時引用該來源；不得只以指向 `.manager` 的連結轉移 | context-sanitization § Convert by value |
| E20 | 產物格式 | 輸出 | `PM_FACTORY_HANDOFF_V1`：candidate、factory_run、approval（人的陳述與日期）、files（三個檔案）、manager_outcome、`factory_started: false` | § Output |
| E21 | 邊界條件 | 停止 | 回報工廠 run 路徑、說明可另起工廠 session 後停止 | § Workflow 9；§ Hard rules |

## 3. 其他

- **`.factory/.gitignore` 的寫入授權**：E9 會在 `.factory/` 根目錄建立 `.gitignore`；`orchestrator-pm` 的 PM 可寫清單只列 `.factory/_runs/<run>`，擁有權表寫「只建已核可的交接」，沒有列出這個檔案。
- **委派摘要欄位**：E8 的摘要含「目標」；`orchestrator-pm` authority-and-gates 的委派摘要只列候選、範圍、擬定標題。
- **核可引述與摘要確認的順序**：Workflow 1 先在 outcome 引述核可，Workflow 2 才確認委派摘要；若人在摘要階段修改範圍或取消，已寫入的核可引述如何處理沒有規定。
- **PM 來源資訊的界線**：Exclude 清單排除 PM 專用術語，但允許「工廠用得上時」保留 PM 來源 metadata，intake 範本也有選擇性的候選編號欄位；兩者的界線依「工廠用得上」判斷，沒有更具體的標準。
- **不處理非產品路線**：本 skill 只建立工廠交接；`pm-intake-triage` 明定非產品路線的候選不呼叫本 skill。

## 4. 與前版差異

對照 run `2026-10-19-skill-improvement` 的 `staging/_baseline-2026-10-19/pm/pm-factory-handoff.md`（前版 version 1.0）：

- 修改 E5（前版 E5「不依賴、不提及 manager」）：由「factory-facing 檔不得提及 `.manager`、manager run 路徑或 PM 來源 metadata」改為「可選擇性提及，必要事實以值寫入，不得指示工廠寫入 `.manager`」；併入 Workflow 6 的三件事。
- 修改 E8（前版 E8 委派摘要確認）：併入 Workflow 1 的核可引述（前版放在 E15）。
- 修改 E9 路徑（前版 E9）：`.factory/<YYYY-MM-DD>-<slug>/` 改為 `.factory/_runs/<YYYY-MM-DD>-<slug>/`，加入建立 `.factory/.gitignore`。
- 新增 E10 冷啟動包不是跨方交接檔。
- 修改 E11 `_intake.md`（前版 E10）：八項變九項，加入選擇性來源欄。
- 修改 E12 intake 範本（前版 E11）：加入 Source (optional) 段，並列出完整段落。
- 修改 E13 `_status.md`（前版 E12）：移除「不得指出上游產生者」；列出範本全部欄位。
- 修改 E16 可追溯性（前版 E15）：由「追溯只放在 manager 端」改為「正式追溯在 manager 端，工廠檔內的 manager 參照只是線索」。
- 修改 E18 Exclude 清單（前版 E17）：「`.manager` 路徑與 PM 來源 metadata」改為「讓 `.manager` 參照變必讀的措辭」；「要求向上回報」改為「要求向 PM 回報或回呼，回流路徑由工廠規則決定」。
- 移除：無。
