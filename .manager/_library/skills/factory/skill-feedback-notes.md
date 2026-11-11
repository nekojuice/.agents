# skill-feedback-notes 元素對照

- 分支：factory
- 對照版本：`skills/skill-feedback-notes/SKILL.md` version 1.0，last_updated 2026-11-11T10:02:59
- 讀過的檔案：`skills/skill-feedback-notes/SKILL.md`、`skills/skill-feedback-notes/agents/openai.yaml`
- 狀態：已檢查，2026-11-11 移入 manager 正式文件

## 1. 摘要

`skill-feedback-notes` 是 skill 使用後改良的回饋迴圈：工作中使用者對 skill 的指正記成筆記，收尾時交給修訂 skill 的一方，新版落地後在能比較新舊版時記錄差異。適用於 factory、manager、helper 的工作，以及經 orchestrator 授權的 worker。

流程：工作涉及改 skill、製作 skill 或追蹤 skill 品質時開始記 → 收尾必須處理筆記，預設寫 `handoff-skill-<topic>.md` 並告訴使用者路徑 → 使用者帶到 skill repo 的 manager，由其存入 `inputs/` 走非產品路線並做抽象化 → 新版落地後選用驗證，結果再記成筆記。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | factory、manager、helper 的工作（含經授權的 worker）涉及改 skill、製作 skill 或追蹤 skill 品質，明說或隱含皆算；單純使用 skill 不適用 | frontmatter description |
| E2 | 觸發條件 | 隱式呼叫設定 | `disable-model-invocation: false`；`agents/openai.yaml` 為 `allow_implicit_invocation: true` | frontmatter；`agents/openai.yaml` |
| E3 | 觸發條件 | 開始記錄 | 依語意開始；第一筆值得記的事項出現時建立筆記檔；一個 run 或工作區一份 | When to record |
| E4 | 產物格式 | 筆記位置 | factory：`run_dir/_skill-notes.md`；manager：run 根目錄 `skill-notes.md`；helper：自己工作區、與脈絡檔同層的 `skill-notes.md`，寄宿在他人 run 時用宿主的筆記檔，契約另有規定除外 | Where |
| E5 | 邊界條件 | worker 需授權 | worker 只在 orchestrator 派工授權時記錄；記錄放進回傳，由 orchestrator 寫入筆記檔 | Where |
| E6 | 產物格式 | 每筆欄位 | 情境、agent 做了什麼、使用者要的、使用者原話、原因（使用者有說才記）、涉及的 skill 與版本 | What to record |
| E7 | 判斷規則 | 記錄重點 | 優先記人工指正、反覆出現的問題、使用者明說的原則；不記一般進度；盡量記重點，但不因瑣碎而不記，雜訊由修訂方過濾 | What to record |
| E8 | 流程步驟 | 收尾必須處理 | 筆記不為空時，收尾必須處理，與該角色其他收尾項目同時 | At closing |
| E9 | 產物格式 | 交接檔 | 預設寫 `handoff-skill-<topic>.md`（run 或工作區根目錄），帶上各筆記錄；三行標頭 `Source run:`、`Recipient:`（skill repo 的 manager）、`Date:`；多寫無妨；名稱小寫英數與連字號；每次收尾一份、不追加，之後的記錄寫新檔；告訴使用者路徑，由使用者帶給 skill repo 的 manager | At closing |
| E10 | 人閘 | 延後或捨棄 | 只在使用者表示時；記入狀態檔：factory `_status.md`、manager `_run.md`、helper 脈絡檔；延後的筆記在之後的檢查點列為提醒，不當新決策 | At closing |
| E11 | 流程步驟 | 本身在改 skill 的 manager run | 筆記直接當非產品路線需求對照的輸入，不寫交接 | At closing |
| E12 | 流程步驟 | 收件方 | skill repo 的 manager 把交接存入 run 的 `inputs/`，從非產品路線的需求對照開始 | Receiving a handoff |
| E13 | 邊界條件 | 抽象化與專案中立 | 抽象化在 skill repo 進行；專案內容只留在 run，不進 skill 與 manager 正式文件 | Receiving a handoff |
| E14 | 流程步驟 | 高複雜度修訂 | 使用者指示時，持有完整脈絡的 session 可以 manager 模式進入 skill repo，自己走非產品路線 | Receiving a handoff |
| E15 | 流程步驟 | 驗證 | 選用；只在 session 同時持有新舊兩版的記憶或脈絡且正在比較時：1 重讀新版，不依賴先前載入的版本；2 比較新舊版下的工作；3 結果（改善、未改善、副作用）記成一筆 | Verification |
| E16 | 流程步驟 | 使用者回報 | 使用者在工作中回報修訂有無幫助，也記成一筆；驗證記錄走同一條收尾 | Verification |

## 3. 其他

- **引用方**：`orchestrator-factory`（§ Skill feedback notes、§ File conventions、§7）與 `orchestrator-pm`（§ Required references、§ Non-product route、workspace-contract）引用本 skill；`orchestrator-helper` 不修改，由本 skill 的 description 涵蓋，屬使用者定案。
- **跨 repo 交付靠使用者**：交接檔留在產生它的 run，由使用者帶到 skill repo；沒有自動通道。
- **筆記沒有格式範本或品質門檻**：使用者定案寧可多記，由修訂方過濾。

## 4. 與前版差異

- 1.0（2026-11-11）：新增 skill，首次拆解（來源：manager run 2026-11-04-next-skill-evolution `requirements-comparison-skill-feedback-loop.md` §6、`changes/04`；審查分類 `reviews/_triage-skill-feedback-loop.md`）。
