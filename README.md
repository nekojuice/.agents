# .agents

<details>
<summary>目錄</summary>

- [關於本專案](#關於本專案)
- [技術堆疊](#技術堆疊)
- [快速開始](#快速開始)
- [專案結構](#專案結構)
- [專案邏輯](#專案邏輯)
- [Skill 一覽](#skill-一覽)

</details>

## 關於本專案

本目錄是工作區共用的 Agent 設定與技能庫，把可重用的工作流程、寫作規範與框架實務集中存放，供 Cursor、Claude 等工具以捷徑載入。核心是兩套指揮流程：工廠模式負責從討論、提案、實作、機器檢查到歸檔的開發主線；PM 模式負責專案方向、進度盤點與派工前交接，本身不做實作。另有反向規格指揮者，替未導入 OpenSpec 的既有專案補寫規格。其餘技能採選配，依當下任務手動啟用。

## 技術堆疊

| 類型 | 名稱 | 說明 |
| --- | --- | --- |
| 規格驅動流程 | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | propose / apply / sync / archive 等原生技能與指令 |
| Agent 技能標準 | Agent Skills（`SKILL.md`） | 各技能以目錄＋說明檔形式安裝 |
| 編輯器整合 | Cursor / Claude | 透過初始化腳本建立指向本目錄的捷徑 |

## 快速開始

初始化步驟見 [init-agent-script/readme.md](./init-agent-script/readme.md)。依使用環境執行對應腳本一次即可。

## 專案結構

```text
.agents/
├── skills/              # 全部 Agent 技能
├── commands/            # OpenSpec 相關斜線指令
└── init-agent-script/   # 建立編輯器捷徑的腳本
```

## 專案邏輯

共有三種指揮者，皆僅在使用者明確啟用時進入，預設不自動開跑。

### 工廠模式

由 `orchestrator-factory` 調度，走開發主線。

```mermaid
flowchart TD
  A[討論 discuss-first] --> B[提案 openspec-propose 與擴充規範]
  B --> C[實作 openspec-apply-change 與硬閘檢查]
  C --> D[機器審查 code-review]
  D --> E[同步與歸檔]
  E --> F[commit 建議與 change log]
```

### PM 模式

由 `orchestrator-pm` 調度，管專案方向與狀態，不進行實作。

```mermaid
flowchart TD
  A[進件分類 pm-intake-triage] --> B[調查 pm-investigation-worker]
  B --> C[狀態盤點 pm-status-review]
  C --> D[人閘核可]
  D --> E[交接工廠 pm-factory-handoff]
```

### 反向規格

由 `orchestrator-reverse-spec` 調度，替未導入 OpenSpec 的既有專案反寫主規格，流程止於審查過的規格，不改動產品程式。

## Skill 一覽

欄位：技能名稱、作者、是否自動啟用、簡述。作者若來自公開倉庫，附上 GitHub 連結；自動啟用為「是」表示 agent 可自行判斷載入，「否」表示僅能由使用者手動呼叫。

### Factory workflow 會載入的 skill

依工廠實際流程排序；末兩項為選配的提案審查組合，亦可單獨使用。

| 順序 | Skill | 作者 | 自動啟用 | 簡述 |
| --- | --- | --- | --- | --- |
| 1 | `orchestrator-factory` | 自製 | 是 | 工廠模式總指揮：排程、派工、人閘、彙整執行工作區 |
| 2 | `discuss-first` | 自製 | 是 | 僅討論不改檔的開場；對齊需求與邊界 |
| 3 | `openspec-propose` | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 是 | 一次產出 change 的提案、設計與任務清單 |
| 4 | `opsx-propose-guide` | 自製 | 是 | 提案擴充規範：切分、命名、依賴與冷啟動自足 |
| 5 | `test-first` | 自製 | 是 | 測試優先；提案階段必載，實作階段繼續沿用 |
| 6 | `openspec-apply-change` | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 是 | 依 change 任務逐項實作 |
| 7 | `opsx-apply-guide` | 自製 | 是 | 實作擴充規範：清單進度、測試優先、偏離紀錄 |
| 8 | `hard-verify` | 自製 | 是 | 指揮編譯、建置、靜態檢查與單元測試等硬閘 |
| 9 | `code-review` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 規範與規格雙軸審查；由獨立檢查工作者執行 |
| 10 | `openspec-sync-specs` | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 是 | 將變更規格同步進主規格 |
| 11 | `openspec-archive-change` | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 是 | 完成後歸檔 change |
| 12 | `commit-message-suggestion` | 自製 | 是 | 產生 commit 訊息建議，不代為提交 |
| 13 | `change-log` | 自製 | 是 | 產出改動清單，向使用者與開發者說明變更 |
| 選配 | `change-review-request` | 自製 | 是 | 撰寫任務包審查邀請，供審查者判斷 change 是否正確 |
| 選配 | `change-review-response` | 自製 | 是 | 回覆任務包審查，寫出裁決與下一步 |

### PM workflow 會載入的 skill

| Skill | 作者 | 自動啟用 | 簡述 |
| --- | --- | --- | --- |
| `orchestrator-pm` | 自製 | 否 | PM 模式總指揮：專案方向、進度與交接，不做實作 |
| `pm-intake-triage` | 自製 | 是 | 進件分類與整併：回答、調查、分組或提為工廠候選 |
| `pm-investigation-worker` | 自製 | 是 | 唯讀調查工作者，依派工產出單一發現檔 |
| `pm-status-review` | 自製 | 是 | 證據式狀態盤點，更新專案進度 |
| `pm-factory-handoff` | 自製 | 是 | 人閘核可後產出 `.factory` 交接 |

### 其他選配 skill

| Skill | 作者 | 自動啟用 | 簡述 |
| --- | --- | --- | --- |
| `orchestrator-reverse-spec` | 自製 | 否 | 反寫既有專案為 OpenSpec 主規格的特規指揮者 |
| `explain` | 自製 | 是 | 解釋目標，將目標拆為摘要與元素清單 |
| `decision-support` | 自製 | 是 | 把糾纏的決策因式分解成獨立節點，逐節點權衡與推薦，不綁整包 |
| `peer-agent-coordination` | 自製 | 是 | 多 agent 共用工作空間時的分身協調協定 |
| `openspec-explore` | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 是 | 探索模式：釐清想法，尚未開立 change |
| `impl-verify` | 自製 | 是 | 需求邊界檢查；可獨立使用，非工廠主路徑 |
| `playwright-cli` | [Microsoft](https://github.com/microsoft/playwright-cli) | 是 | 瀏覽器命令列自動化；`impl-verify` 依賴項 |
| `karpathy-guidelines` | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 是 | 實作行為準則：先想清楚、簡化、外科手術式改動 |
| `ponytail` | [DietrichGebert](https://github.com/DietrichGebert/ponytail) | 是 | 懶惰資深工程師模式：選最簡可行解 |
| `i-have-adhd` | [ayghri](https://github.com/ayghri/i-have-adhd) | 否 | ADHD 友善輸出：先給下一步、步驟編號、跨回合重述狀態 |
| `opsx-health-check` | 自製 | 否 | 主規格與程式落差的健康檢查，匯出比對報告 |
| `code-to-docs` | 自製 | 否 | 依程式與主規格產出人類可讀文件 |
| `thought-palette-extract` | 自製 | 是 | 收斂決策為可匯入圖像化工具的結構化資料 |
| `create-skill-guide` | 自製 | 是 | 撰寫或更新技能檔頭 metadata 的規範 |
| `doc-general-guide` | 自製 | 是 | 文件寫作基礎規範層 |
| `doc-readme-guide` | 自製 | 是 | 私有／小團隊 README；依賴 `doc-general-guide` |
| `doc-sop-guide` | 自製 | 是 | 開發者操作與部署說明；依賴 `doc-general-guide` |
| `doc-user-guide` | 自製 | 是 | 使用者畫面操作手冊；依賴 `doc-general-guide` |
| `grill-me` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 以連續拷問對齊計畫與設計 |
| `grill-with-docs` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 拷問並同步產出決策紀錄與詞彙表 |
| `grilling` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | grill 系列底層可複用迴圈 |
| `codebase-design` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 深度模組設計的共用詞彙與紀律 |
| `domain-modeling` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 打磨專案領域模型與共用語言 |
| `diagnosing-bugs` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 難除缺陷與效能回歸的診斷迴圈 |
| `improve-codebase-architecture` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 掃描架構加深機會，再以拷問收斂 |
| `prototype` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 用拋棄式原型回答設計問題 |
| `research` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 依高信任來源調查並寫成 Markdown |
| `resolving-merge-conflicts` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 進行中的合併或變基衝突逐塊解決 |
| `triage` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 議題與外部合併請求的分流狀態機 |
| `wayfinder` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 超長程工作的決策票地圖 |
| `handoff` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 壓縮對話成交接文件給下一代理 |
| `teach` | [Matt Pocock](https://github.com/mattpocock/skills) | 是 | 以工作區為狀態的多回合教學 |
| `writing-great-skills` | [Matt Pocock](https://github.com/mattpocock/skills) | 否 | 編寫與編輯技能的詞彙與原則 |
| `vue-best-practices` | [vuejs-ai](https://github.com/vuejs-ai/skills) | 是 | Vue 3 Composition API 與 TypeScript 實務 |
| `vue-pinia-best-practices` | [vuejs-ai](https://github.com/vuejs-ai/skills) | 是 | Pinia 狀態管理與反應性模式 |
| `vue-router-best-practices` | [vuejs-ai](https://github.com/vuejs-ai/skills) | 是 | Vue Router 導航守衛與生命週期 |
| `vue-testing-best-practices` | [vuejs-ai](https://github.com/vuejs-ai/skills) | 是 | Vitest、元件測試與端對端測試實務 |
| `regle` | [Victor Garcia](https://github.com/victorgarciaesgi/regle) | 是 | Regle 表單驗證核心 |
| `regle-rules` | [Victor Garcia](https://github.com/victorgarciaesgi/regle) | 是 | 內建與自訂驗證規則 |
| `regle-advanced` | [Victor Garcia](https://github.com/victorgarciaesgi/regle) | 是 | 集合、非同步與跨元件等進階模式 |
| `regle-schemas` | [Victor Garcia](https://github.com/victorgarciaesgi/regle) | 是 | 與 Zod、Valibot 等 schema 庫整合 |
| `regle-typescript` | [Victor Garcia](https://github.com/victorgarciaesgi/regle) | 是 | Regle 的 TypeScript 型別整合 |
| `regle-migrate-vuelidate` | [Victor Garcia](https://github.com/victorgarciaesgi/regle) | 是 | 自 Vuelidate 遷移至 Regle |
| `java-coding-style` | 自製 | 是 | UITC Java 後端編碼規範 |
