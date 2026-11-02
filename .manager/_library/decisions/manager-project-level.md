# manager 停在專案層級

- Status: accepted
- Scope: orchestrator-pm 系列
- Date: 2026-11-02
- Authority: 使用者明確指示

## Decision

manager 只管專案的方向、範圍、排程與狀態。factory 粒度的研究、設計與實作問題交給 factory，manager 不深挖、不代為決定，也不改 factory 的工作檔。

## How to apply

- 建立 factory run（交接）、在委派中發 peer 訊息、交付 `handoff-factory-<topic>.md` 到 factory run 根目錄，都屬允許的動作；peer 是溝通管道，不算寫入文件。
- factory 自行唯讀查閱 `.manager`，不以訊息向 manager 提問；manager 也不回答 factory 粒度的問題。
- manager 發動的委派，manager 在討論室保持可被喚醒直到使用者結束討論室；預設同平台，不需自製站台的背景接聽。factory 換手時使用者在場，名冊依使用者指示更新。
- 非自動化時，補交給 factory 的事項先與使用者討論後才發出。
- factory 的交接可以多寫，manager 收件時篩選，不全盤接收；所有正式檔更新先擬稿到 run 的 `staging/`，使用者檢查後才沖入。
