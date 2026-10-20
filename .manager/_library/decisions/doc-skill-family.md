# 文件 skill 繼承架構與類型路由

- Status: accepted
- Scope: 本 repo 的 skill
- Date: 2026-10-20
- Authority: 使用者明確指示

## Decision

doc-general-guide 是文件 skill 的父層與唯一類型路由。子 skill 繼承父層規則，衝突時以子 skill 為準，衝突須在子 skill 的覆寫表宣告。

## How to apply

- 子 skill：README、SOP、使用者手冊、教學、OpenAPI 文件；父層直接負責工程參考手冊與盤點清單。
- 教學類英文類型名稱為 `tutorial`。
- 產出文件的識別資訊用佔位符或匿名虛構名稱；盤點清單本體可記實際識別值，秘密值永不記錄。
- 使用者手冊與教學的畫面路徑寫法統一：起點不加引號、選單用『』、按鈕用「」；條件提示標籤統一。
