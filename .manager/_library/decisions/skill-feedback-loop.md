# skill 使用後改良的回饋迴圈

- Status: accepted
- Scope: skill-feedback-notes、orchestrator-factory、orchestrator-pm；涵蓋 orchestrator-helper 的工作
- Date: 2026-11-11
- Authority: 使用者明確指示（manager run `2026-11-04-next-skill-evolution` 的 `requirements-comparison-skill-feedback-loop.md` §1、§6）

## Decision

skill 使用中得到的指正以一份參考用 skill 記成筆記，收尾時交給修訂 skill 的一方，新版落地後在能比較新舊版時回饋，形成改良迴圈。factory 與 manager 引用它；它可自動調用。

## How to apply

- 觸發：工作涉及改 skill、製作 skill 或追蹤 skill 品質的語意。
- 記錄：盡量記重點、壓制低品質內容，但不能什麼都不記；雜訊由修訂 skill 的 agent 過濾。
- 範圍：factory、manager、helper；orchestrator 底下的 worker 需 orchestrator 授權。
- 收尾：筆記是收尾待處理項目，與 opsx、issue backlog、review queue 同一階段處理。一般修訂比照 factory 交接 manager：交接 → skill repo 的 manager 走非產品路線 → 修改 skill；抽象化在 skill repo 進行。
- 高複雜度修訂：產品 session 可在使用者指示下直接以 manager 模式修改 skill，不禁止。
- 驗證：不一定要跑；只在 session 持有新舊兩版脈絡且正在比較時觸發，避免干擾日常作業；使用者在交互中發現有改善也算。
