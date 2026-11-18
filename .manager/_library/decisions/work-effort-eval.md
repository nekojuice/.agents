# 工作時長與工作強度評估

- Status: accepted
- Scope: work-effort-eval、orchestrator-factory、orchestrator-pm
- Date: 2026-11-18
- Authority: 使用者明確指示（manager run `2026-11-18-skill-expression-and-effort` 的 `requirements-comparison-effort-metrics.md` §1、§6–§8）

## Decision

以一份可選的評估 skill 把「任務多難、花多久」量化成參考指標，評估對象是整段工作流程，skill 品質只是其中一項。分兩部分：orch 在工作中隨手記錄，收尾時派 eval worker 評估，orch 覆核。在本框架的 factory 與 manager 中設為自動啟用；日後可調整移除，使用者也可指示不用。

## How to apply

- 以 run 為單位；可隨時獨立發動，直接視為一個獨立 run；中途或事後發動時，缺的訊號標為未記錄，不當成零。
- 不做事前估計難度與時長：初期估計差異大，估錯會給使用者錯誤的信心。
- 三軸分開、不互相換算：量（只作參考，量多不代表難）、agent 負擔、使用者負擔。
- 兩種累計時間：使用者互動時間（只算在線，與決策負擔相關）、agent 自動工作時間（與量相關）。
- 記錄不是稽核日誌：以主線任務為主，盡量當下寫、不勉強；orch 只記自己看得到的訊號，檔案已有的訊號由 eval 自己數，沒記到的由 eval 收尾時找出。觸發 skill 問題反饋時照常記到 skill 回饋筆記，並加一筆不良記錄。
- 收尾評估是啟用後必做的動作，不設人閘；派出前提醒使用者，產出報告時告知路徑。
- eval 由 orch 派新子代理，比照既有 review；orch 可忽略、回絕或修改結果，但大部分尊重 eval。
- 輸出：原始次數加分級，分級有寫死的錨點；記錄 orch 與 eval 的模型、平台與型號。
- 跨 run 累積放 manager 的正典台帳 `_effort-ledger.md`（屬專案管理）；不在本框架內的單次執行不記錄基準。
- 本 skill 本身要多輪校正，如同 LLM-as-a-judge 的提示；校正材料經 skill 回饋筆記交回。
- 歸因、出口、錨點等邏輯主架構由 agent 設計，見 skill 本文。
