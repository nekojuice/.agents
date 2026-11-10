# orchestrator-helper 元素對照

- 分支：factory
- 對照版本：`skills/orchestrator-helper/SKILL.md` version 1.0，last_updated 2026-11-05T11:49:00
- 讀過的檔案：`skills/orchestrator-helper/SKILL.md`、`skills/orchestrator-helper/agents/openai.yaml`
- 狀態：已檢查，2026-11-10 移入 manager 正式文件

## 1. 摘要

`orchestrator-helper` 是獨立的輔助指揮者：一個可以接上任何工作的彈性幫手。本身規範很輕，每次做什麼由當下那份工作建立的契約決定。

通常由使用者建立；平台能建立 session 時，其他角色也可以建立。指揮者是使用者，以及經使用者授權的 manager 或 factory；常見做法是使用者先與上級 agent 談好授權，再由該 agent 與 Helper 溝通。可以直接呼叫，也可以由授權角色以文字發動。

契約是工作的核心，在工作開始時建立：使用者直接呼叫時由使用者指定範圍與用法，授權角色呼叫時由該角色指定；工作在契約內進行，契約沒涵蓋的事回到建立契約的一方。Helper 持有一份自己的簡單脈絡（預設是工作區根目錄的 `helper-context.md`，可依工作調整），記錄當下的契約；其他脈絡文件只在授權共用時使用。

Helper 仍是指揮者：朝契約組織工作、在交出前判斷結果；可以自建工作區或寄宿在既有工作區；工作需要時派 worker，並與 manager 或 factory 溝通。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | 使用者呼叫 `orchestrator-helper`，或經使用者授權的 manager 或 factory 以文字發動 | frontmatter description |
| E2 | 觸發條件 | 隱式呼叫設定 | `disable-model-invocation: false`；`agents/openai.yaml` 為 `allow_implicit_invocation: true` | frontmatter；`agents/openai.yaml` |
| E3 | 角色 | 輔助指揮者 | 可以接上任何工作的彈性幫手；規範很輕，每次做什麼由該工作的契約決定 | 開頭段 |
| E4 | 角色 | 誰建立 | 通常由使用者建立；平台能建立 session 時，其他角色也可以建立 | Who starts and directs you |
| E5 | 角色 | 誰指揮 | 使用者，以及經使用者授權的 manager 或 factory；常見做法是使用者先與上級 agent 談好，再由該 agent 與 Helper 協作 | Who starts and directs you |
| E6 | 觸發條件 | 發動方式 | 可直接呼叫，或由授權角色以文字發動 | Who starts and directs you |
| E7 | 契約 | 契約是核心 | 在工作開始的當下建立契約 | The contract |
| E8 | 契約 | 由誰指定 | 使用者直接呼叫時由使用者指定範圍與用法；授權角色呼叫時由該角色指定 | The contract |
| E9 | 契約 | 契約範圍 | 在契約內工作；工作需要契約沒涵蓋的事時，回到建立契約的一方 | The contract |
| E10 | 脈絡 | 自己的脈絡 | 持有一份自己的脈絡，依工作盡量簡單；預設是工作所在工作區根目錄的固定檔 `helper-context.md`，可依工作調整 | Your context |
| E11 | 脈絡 | 記錄契約 | 把當下的契約記在自己的脈絡裡 | Your context |
| E12 | 脈絡 | 共用其他脈絡 | 其他脈絡文件只在獲授權共用時使用 | Your context |
| E13 | 角色 | 仍是指揮者 | 朝契約組織工作，交出前先判斷結果 | How you work |
| E14 | 工作區 | 自建或寄宿 | 依契約與工作需要，自建工作區或寄宿在既有工作區 | How you work |
| E15 | 派工 | 派遣 worker | 工作需要時派 worker | How you work |
| E16 | 溝通 | 與 manager、factory 溝通 | 依工作需要與 manager 或 factory 溝通 | How you work |

## 3. 其他

- **其他角色的 skill 沒有提到 Helper**：使用者定案不修改其他角色的 skill；manager 與 factory 以文字發動 Helper（E1、E6），`orchestrator-pm`、`orchestrator-factory` 本文沒有對應條文，屬刻意設計。
- **契約與脈絡沒有固定格式**：E7–E11 只要求建立並記錄契約，沒有欄位或範本；使用者要求規範保持彈性，屬刻意設計。
- **預設脈絡檔名與「記錄契約」由 agent 自定**：`helper-context.md` 與 E11 是建立 skill 時 agent 自行決定並已揭露的兩項（manager run `2026-11-04-next-skill-evolution`），使用者未另行指示。
- **沒有專屬 README**：本 skill 沒有對應的說明文件；根目錄 `README.md` 的 skill 一覽已列入（協作與判斷）。

## 4. 與前版差異

- 1.0（2026-11-05）：新增 skill，首次拆解（來源：manager run 2026-11-04-next-skill-evolution `orchestrator-helper-draft.md`）。
