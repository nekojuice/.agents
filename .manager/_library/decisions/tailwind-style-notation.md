# Tailwind 語法為通用樣式表達語言

- Status: accepted
- Scope: design-system-extraction 及其產出的品牌 skill
- Date: 2026-11-17
- Authority: 使用者明確指示（2026-11-17，manager run `2026-11-17-design-extraction-skill`）：樣式一律以 Tailwind 語法表達，含非 CSS 媒介

## Decision

樣式規格一律以 Tailwind 語法表達，涵蓋所有類 CSS 框架，也用於非 CSS 媒介（例：簡報、列印）的等效寫法。數值的唯一來源仍是 token。

## How to apply

- 跨框架可搬移靠共用的 CSS 變數，不做元件庫專屬對應。
- 非 CSS 媒介的單位換算：1in = 96px、1pt = 1/72in 依 W3C CSS Values and Units Level 4 § 6.2；914400 EMU = 1in 依 Microsoft Office Open XML 文件；「token 的 px 視為 CSS px」是 skill 的約定，不是標準。
