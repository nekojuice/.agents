# 設計規格提取為擴充 skill，由 factory 驅動

- Status: accepted
- Scope: design-system-extraction、orchestrator-factory
- Date: 2026-11-17
- Authority: 使用者明確指示（2026-11-17，manager run `2026-11-17-design-extraction-skill`）：採擴充 skill，不另做 orchestrator

## Decision

「從既有前端反推品牌設計規格並交付成 design system skill」做成領域擴充 skill，不另做 orchestrator。調度、run 結構與人閘歸 factory；skill 只提供每一步的做法、驗收、範本與腳本。

## How to apply

- factory 在非實作計畫路線上依使用者指令載入，並依指令選段（抽取、重建、框架遷移）。
- 沒有 factory 時，單一 session 依同一順序做，停點相同。
- skill 不自行擴大 factory 的停點或授權；commit 仍依 commit 授權規則。
- 只有將來出現 factory 沒有的調度需求（例：跨多個前端自動批次）才重新評估專用 orchestrator。
