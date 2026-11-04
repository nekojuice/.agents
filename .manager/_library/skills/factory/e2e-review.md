# e2e-review 元素對照

- 分支：factory
- 對照版本：`skills/e2e-review/SKILL.md` version 1.2，last_updated 2026-11-04T10:30:45（工作樹狀態，含審查修正與第二輪修正，未 commit；HEAD 為 1.1。第二輪修正於 10:46–10:47 改動 `SKILL.md`、`scripts/e2e.mjs`、`scripts/core/report.mjs`、`scripts/drivers/http/driver.mjs`，metadata 的 version 與 last_updated 未隨之更新）
- 讀過的檔案：`SKILL.md`、`agents/openai.yaml`（`display_name: "E2E Review"`、`short_description`、`allow_implicit_invocation: true`）、`references/report-spec.md`、`references/script-tiers.md`、`references/recipes.md`、`references/ui-checks.md`、`references/project-profile.md`、`references/tools.md`、`references/drivers/playwright.md`、`references/drivers/http.md`、`assets/recipe.template.md`、`assets/e2e-skeleton/`（`PROJECT.md`、`.gitignore`、`config/env.json`、`config/accounts.local.example.json`、`audit/fetch.mjs`、`surfaces/api/helpers/auth.mjs`、各 `.gitkeep` 目錄）；`scripts/` 中 `e2e.mjs`、`core/*.mjs`、`drivers/playwright/driver.mjs`、`drivers/http/driver.mjs` 唯讀核對行為，driver 附的 probes 與 helpers 只確認用途；交叉核對（唯讀）：`orchestrator-factory/SKILL.md` version 1.11（last_updated 2026-11-04T10:51:56，工作樹，相對 HEAD 的 1.10 只改 § 5b 第 4 步）的 Hard rules 5、Repair policy、Factory overrides 8–9、§ 5b
- 狀態：已檢查（第二輪修正後重新核對），2026-11-04 移入 manager 正式文件

## 1. 摘要

`e2e-review` 是 agent E2E／互動審查的 worker 規則：依上級給的清單實際操作受測系統（透過畫面或 API），以值證據與截圖逐項判斷，記錄清單外的 UI 問題與寫入追溯，交出附證據的報告。它是人工驗收前最後一道 agent 自檢，不取代人工驗收；報告只建議每項狀態，算不算完成由上級決定。上級在自動化流程中是派工的 orchestrator（例如 factory），直接呼叫時是使用者。

skill 本身不含任何專案資訊；專案知識全部放在專案的 `.e2e/`（從 `.e2e/PROJECT.md` 讀起）。受測系統的每個可操作部分是一個 **surface**，登記在 `.e2e/config/env.json` 並指定 driver；skill 附 `playwright`（網頁畫面）與 `http`（API）兩個 driver。腳本依使用累積成三層（即興、碎片、固化 scenario），另有含 agent 手動步驟的 recipe，recipe 現階段不作驗收依據；測試資料透過系統自身的 API 準備，不直接寫 DB。所有會寫入者先以 `--dry` 演練，driver 在演練時另有攔截寫入的防線。

步驟順序：

1. 啟動：讀 `.e2e/PROJECT.md`，跑 `check`；版本不符或版面警告記入 issues 不停工；driver 或環境不可用時回報上級，不安裝、不啟服務；確認必要輸入。
2. `new` 建立回合資料夾 `<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` 並設為目前任務。
3. 有 web surface 時 `open`；執行對應 scenario，或以 `run <surface>:<fragment>` 組合碎片；含 agent 步驟的流程依 recipe 以 `step`／`log` 執行。
4. 以 `peek`、`api`、`scratch/` 腳本或單一瀏覽器指令即興補缺。
5. web surface 上做清單外 UI 檢查；`run web:probes/shot --name=final`。
6. 以 `add` 補記 UI findings、issues、limits、observations、writes、items。
7. 檢視 `scratch/` 決定升級（含 request 範本與 recipe 草稿）。
8. `close <round> --users=<account keys>` 抓稽核紀錄並產生 `report.md`；回傳上級。

專案沒有 `.e2e/` 時：由 orchestrator 在標準化專案派工者走初始化交接（照樣即興審查、產出 `init-proposal`、經上級核准後下次 `init-apply`）；使用者直接呼叫者不初始化，只在執行工作區即興進行。兩種情況下工具都提供隱含的 `web`（`--url`）與 `api`（`--api-url`，不帶登入）surface。

在工廠流程中，本 skill 由獨立 E2E worker 執行（Check 之後、人工 E2E 之前），`orchestrator-factory` § 5b 以固定的 prompt 形狀派工，並以覆寫 8–9 規定報告父資料夾與 `.e2e/` 的歸屬。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 啟用時機 | 被派為人工驗收前的 E2E／互動審查者，或使用者要求對畫面與流程做 agent E2E 或 API 整合檢查；透過系統自身的 API 準備測試資料而非直接寫 DB；允許隱含啟用；不用於單元測試、code review、正式環境 | frontmatter description、`agents/openai.yaml` |
| E2 | 定位 | 延伸與預設 prompt | `extends: playwright-cli`；`default_prompt` 為驗證指派的清單項目並把報告寫到指定父資料夾 | frontmatter、`agents/openai.yaml` |
| E3 | 定位 | 最後一道 agent 自檢 | 實際操作受測系統（畫面或 API），回報驗了什麼、沒驗什麼與證據；不取代人工驗收 | 開頭段 |
| E4 | 定位 | skill 不含專案資訊 | 專案特有內容全部在專案的 `.e2e/`，從 `.e2e/PROJECT.md` 讀起 | 開頭段、`project-profile.md` |
| E5 | 介面 | surface 與 driver | 受測系統每個被操作的部分是一個 surface，登記於 `.e2e/config/env.json` 的 `surfaces` 並指定 driver；skill 附 `playwright`（網頁）與 `http`（API）；專案只登記實際存在的 surface | 開頭段、`project-profile.md` Surfaces |
| E6 | 角色 | worker 與上級 | worker 負責操作、判斷、取證、回報；不代任何人驗收，不修改上級的清單或控制檔 | Role and superior |
| E7 | 角色 | 上級對照表 | orchestrator 派工：上級為派工的 orchestrator，報告放派工指定的父資料夾（例如 factory run），回傳 "Return" 區塊；使用者直接呼叫：上級為使用者，報告放使用者指定路徑否則依 `tools.md` 預設，回報報告連結、整體判定、需決定或需人工確認的項目 | Role and superior |
| E8 | 角色 | 問題交給上級 | 缺輸入、寫入權限、缺帳號、環境掛掉都問上級；不自行決定，不繞過 orchestrator 直接問使用者 | Role and superior |
| E9 | 必要輸入 | 必要輸入表 | 清單項目（編號與原文，必填）；報告父資料夾（派工時必填，worker 在其下建立固定名稱 `e2e-review/`）；寫入權限（必填，預設唯讀）；帳號（PROJECT.md 未涵蓋時）；環境（PROJECT.md 未涵蓋時：站台、版本、資料範圍）；前一回合（迭代時）；回合依據（選填，例如 commit 或 change 名稱）；缺必填項回傳 `needs-input` | Required input |
| E10 | 邊界 | 環境與外部服務 | 絕不碰正式環境，只在 PROJECT.md 指名的測試環境工作；未經使用者核可範圍不呼叫付費外部服務或外部網站 | Boundaries |
| E11 | 邊界 | 寫入範圍 | 不改產品程式碼、設定、規格；只寫專案 `.e2e/` 與執行工作區 `e2e-review/`；不 commit、不 push，`.e2e/` 的 commit 由上級決定 | Boundaries、`project-profile.md` |
| E12 | 邊界 | 測試資料寫入 | 只在授與的權限內寫測試資料；登入、登出、開頁產生的稽核紀錄屬預期副作用，列入報告 | Boundaries |
| E13 | 邊界 | 密碼與憑證 | 密碼只在 `.e2e/config/accounts.local.json`，除使用者明確允許（例如封閉內部測試環境）外不 commit；所有產物（報告、`result.json`、`steps.jsonl`、`exchanges/`、values、截圖、scratch 腳本、init proposal、回傳內容）只記帳號鍵名；token 與 session cookie 比照密碼 | Boundaries |
| E14 | 邊界 | API 呼叫來源 | API 只打 PROJECT.md 為測試環境登記的 surface；request 依從真實畫面請求錄下的範本，或專案公開的 API 契約（controllers、OpenAPI 或 PROJECT.md 指名的 API 文件）組成；不打兩者以外的端點，例如未公開的內部或管理端點；沒有畫面的專案只依契約；測試資料經 API 準備而非直接寫 DB，讓後端寫齊相關資料表 | Boundaries、`drivers/http.md` Request templates |
| E15 | 邊界 | 先演練再寫入 | 所有會寫入者（碎片、scenario、recipe 步驟、即興 API 呼叫）支援 `--dry`，只組 request 或填表不送出；web surface 上 driver 另於演練時攔下寫入請求（E68）；先演練，再真正寫入一次 | Boundaries、`script-tiers.md` Writing fragments |
| E16 | 邊界 | 單一操作者 | 每個環境同時只有一個 worker 操作受測系統（跨所有 surface）；派出的 sub-worker 不操作 | Boundaries、Internal delegation |
| E17 | 流程步驟 | 啟動檢查 | 每次呼叫都跑，缺的才建立：讀 PROJECT.md → `check`（資產、skill 版本對 PROJECT.md、已登記 surface 與 driver 可用性和碎片宣告、1.1 版面警告、稽核 adapter、帳號鍵）→ 版本不符或版面警告記入 issues 不停工 → driver 或環境不可用則回報上級，不安裝工具、不啟服務 → 確認必要輸入後 `new` | Startup、`tools.md` Commands |
| E18 | 初始化 | 無 `.e2e/` 時的分流 | 標準化專案（有固定 agent 工作流程與 `.factory/` 等資料夾）由 orchestrator 派工：走初始化交接；使用者直接呼叫：不初始化，只在執行工作區即興進行 | Startup／When the project has no `.e2e/`、`project-profile.md` Initialization |
| E19 | 初始化 | 初始化交接 | 一律經上級核准：1 照樣即興完成審查（初始化不阻擋審查）；2 `init-proposal <round>` 複製骨架到 `<round>/init-proposal/.e2e/`（自動填入目前 skill 版本），依唯讀調查填寫，只保留專案實有的 surface，可寫資料、帳號、稽核來源等不確定處標待確認，不放密碼；列出值得升級的即興腳本；3 在報告結論與 issues 註明未初始化與 proposal 路徑，並設定回傳的 `init_needed`；4 上級核准（必要時由上級問使用者，worker 不直接問）後，於下次派工或明確指示時 `init-apply <round> --approved-by=<who>`，移入核准的升級項並記入 writes；`init-apply` 不覆寫 | Startup、`project-profile.md` Initialization |
| E20 | 流程步驟 | 建立回合 | `new <short> --parent=<report parent> [--prev] [--basis] [--kind=review\|prep\|init]` 建立 `<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` 並設為目前任務；只準備資料的回合用 `prep` | Workflow 1 |
| E21 | 流程步驟 | 執行 | 涉及 web surface 時 `open --surface=web`，API surface 不需 open；跑對應 `scenario`，或以 `run <surface>:<fragment> --account=<key> --save=<name>` 組合碎片；含 agent 步驟的流程依 recipe（`step`、`log start\|end`） | Workflow 2–3 |
| E22 | 流程步驟 | 即興補缺 | `peek --from=<text>` 探索畫面、`api <METHOD> <path>` 單次有紀錄的 API 呼叫、`scratch/` 腳本經 `run` 執行，或單一瀏覽器指令（不記錄，寫入任務中避免使用） | Workflow 4、`tools.md` Sessions |
| E23 | 流程步驟 | 收尾 | web surface 做清單外 UI 檢查（截圖多時用 `sheet`）→ 用過 web surface 時 `run web:probes/shot --name=final` → `add` 補記 → 檢視 `scratch/` 升級 → `close <round> --users=<account keys>` → 回傳上級 | Workflow 5–10 |
| E24 | 判斷規則 | 證據要求 | 每個 pass 或 fail 都要證據，值證據優於截圖；沒有證據即 inconclusive | Judgment、`report-spec.md` Evidence |
| E25 | 判斷規則 | check 來源 | `script`（比較寫在腳本中，高）、`value`（腳本讀值、agent 比較或待上級決定，中）、`visual`（只看截圖，低）、`not-run`（條件不具備或屬人工項，無）、`run-error`（工具或腳本錯誤，無）；後三者一律 `inconclusive`，`note` 寫明缺的條件或錯誤；因前一步失敗而未達的 check 是 `inconclusive` 不是 `fail`；來源是工具內部分類，不是上級的驗收規則 | Judgment、`report-spec.md` Check source |
| E26 | 判斷規則 | 驗證途徑 | `checks[].via` 記 `web`／`api`／`db`；畫面行為項只經 `api` 或 `db` 驗證屬 limit，不算完整通過；畫面先擋下的拒絕不代表伺服器會拒絕，項目涉及伺服器行為時也要經 `api` 驗；依賴 agent 步驟的判斷另以 `checks[].agent` 標記（E72） | Judgment、`report-spec.md` Verification route |
| E27 | 判斷規則 | 失敗如實與工具失敗 | 失敗照實回報，不為了通過放寬 check；分清產品失敗與工具失敗：修工具後在同一回合資料夾重跑並保留兩次紀錄，修不了則以 `run-error` 判 inconclusive | Judgment |
| E28 | 判斷規則 | issues 與 limits | 自身假設、替代方法、覆蓋缺口記入 issues；在受限條件下通過的 check 記入 limits（含何時如何重驗） | Judgment、`report-spec.md` result.json |
| E29 | 判斷規則 | 判定彙整 | check 判定 `pass`／`fail`／`inconclusive`；整體：全 pass 為 `pass`，任一 fail 為 `fail`，無 fail 但有 inconclusive 為 `inconclusive`；整體判定不論 check 如何記入（scenario、`add`、recipe）都由 `report`／`close` 產生報告時依現有 check 重算，連同 `stats` 寫回 `result.json`，scenario 的 `ctx.finish` 也會計算；無 check 時不重算，維持存著的值；`prep` 與 `init` 回合沒有驗收 check、不給 pass 判定：無 check 時 `result.verdict` 維持 `inconclusive`，回傳不帶 items、在 `notes` 註明回合種類，上級看種類不看判定；若仍記了 check 則比照 `review` | Judgment、`report-spec.md` Verdicts、Round kinds |
| E30 | 判斷規則 | 清單項目建議狀態 | 依序推導：任一 check fail → `product-fail`；任一 inconclusive 且來源 `run-error` → `run-error`；其他 inconclusive、任一 check 依賴 agent 步驟（即使 pass）或無 check → `needs-human`；全 pass 且有 limit → `verified-with-limits`；全 pass 無 limit → `verified`；剩餘人工工作合併 `humanWork`、未通過 check 的 note、依 agent 步驟判定需人工確認者與 limit 重驗；上級決定什麼算完成 | Judgment、`report-spec.md` Checklist item status |
| E31 | 迭代 | 回合規則 | 每回合新資料夾並以 `--prev` 指向前一回合，報告比較各項狀態（改善、退步、新增、不變）；工具問題造成的重跑留在同一回合；本回合修正可能影響的已驗項目要重驗，未受影響者由上級決定 | Iterations、`report-spec.md` Comparison |
| E32 | 回傳 | `E2E_REVIEW_RESULT_V1` | 回給 orchestrator 的區塊：`status: done \| needs-input \| blocked`、`round_folder`（絕對路徑）、`report`、`verdict: pass \| fail \| inconclusive`、`items`（每項 `<id>: <verified \| verified-with-limits \| needs-human \| run-error \| product-fail> — <一行>`）、`init_needed: no \| yes (<proposal path>)`、`writes`（完整紀錄在 `data/manifest.json`）、`notes`（阻擋、版本不符、給上級的問題）；依 agent 步驟判定的 `needs-human` 項目在其行內註明（例如「agent step: …」），重跑回合不會改變它，由上級交給人；對使用者以文字給同樣事實 | Return |
| E33 | 內部委派 | sub-worker | 可派 sub-worker 平行準備；只有自己操作受測系統、跑腳本、寫測試資料；sub-worker 可推導期望值、跑唯讀 DB 查詢、依給定快照或錄下的 request 起草碎片／scenario／recipe／request 範本、審截圖與值找 UI finding 候選、起草 issue 與 observation 文字；其程式碼進 `.e2e/` 前自己試跑，其發現進報告前自己核對證據 | Internal delegation |
| E34 | 專案資產 | `.e2e/` 版面 | `PROJECT.md`、`config/`（`env.json`、其他 JSON 注入為 `P.config.<name>`、`accounts.local.json`、`accounts.local.example.json`）、`surfaces/<surface>/{actions,probes,helpers}/`、`data/{templates,builders,sets}/`、`scenarios/`（含 `lib/`）、`recipes/`、`audit/fetch.mjs`、`tools/`、`state/`、`out/`、`.gitignore` | `project-profile.md` Layout |
| E35 | 專案資產 | 版本控制歸屬 | PROJECT.md、config（`accounts.local.json` 除外）、surfaces、data、scenarios、recipes、audit、tools 由上級 commit，worker 不 commit；`accounts.local.json` 原則不 commit；`state/`（含 `data-<env>.json`）、`out/` 不 commit；`e2e-review/` 執行工作區不 commit（自帶 `*` 的 `.gitignore`）；執行產物從不進 `.e2e/`，只有升級的腳本、範本、資料設計與專案事實進入 | `project-profile.md` Layout |
| E36 | 專案資產 | surface 登記規則 | `env.json` 的 `surfaces.<name>` 寫 `driver` 與欄位（`playwright`：`baseUrl`、`browser`、`session`（`E2E_SESSION` 可覆寫）、`dryAllow`（演練時允許寫入的 URL 片段，例如登入）；`http`：`baseUrl`，登入由 `surfaces/<surface>/helpers/auth.mjs`）；選填頂層 `name` 為環境名，用於 `state/data-<env>.json`，否則用 `dataScope`；名稱對專案有意義，兩套網頁系統登記兩個 surface；新增 surface 時加登記、建資料夾、以 `check` 確認 skill 附有該 driver，skill 未附的 driver 是給 skill 擁有者的提案；`env.defaultSurface` 為無前綴時的預設，否則 `web`，再否則第一個 | `project-profile.md` Surfaces |
| E37 | 專案資產 | PROJECT.md 章節 | Verified skill version、System under test（含 API 端點定義處）、Surfaces、Operating limits、Accounts（不含密碼）、Audit trail、Test data（範本來源與日期、`state/data-<env>.json` 讀法、測試前綴）、Scripts（各 surface 的 actions／probes 表、scenarios、recipes 與剩餘 agent 步驟數）、Known pitfalls；任務中學到的專案知識寫回 PROJECT.md，通用心得交給 skill 擁有者 | `project-profile.md` PROJECT.md、`assets/e2e-skeleton/PROJECT.md` |
| E38 | 專案資產 | 稽核 adapter | `.e2e/audit/fetch.mjs` 為常駐腳本、唯讀存取；簽章 `({ from, to, users, env, config }) => rows`，`from`／`to` 為第一步開始與最後一步結束的本地時間，`users` 由帳號鍵解析出的 user id（字面 id 原樣傳入）；每列 `time`（本地 `yyyy-MM-ddTHH:mm:ss[.fff]`）、`user`、`action`（代碼加可讀標籤）、`target`、`detail`、`source`；無稽核紀錄的專案刪除 adapter，報告只顯示步驟時間線 | `project-profile.md` Audit adapter、`assets/e2e-skeleton/audit/fetch.mjs` |
| E39 | 專案資產 | 版本相容 | skill 的 `metadata.version` 是相容標記；PROJECT.md 記驗證過的版本，每份 `result.json` 記產出它的 skill 版本；不符時照常工作並記入 issues，是否更新資產由上級決定，核對後更新 PROJECT.md 該行 | `project-profile.md` Versioning |
| E40 | 專案資產 | 1.1 遷移 | 1.2 只從 `surfaces/<surface>/` 讀碎片，`check` 發現 1.1 版面會警告；一次遷移：移 `actions/`、`probes/`、`helpers/` 到 `surfaces/web/` → `actions/`、`probes/` 的碎片第一行加 `// @driver playwright`，helper 不需宣告 → `env.json` 網頁欄位移入 `surfaces.web` → scenario 引用改 `web:` 前綴 → 建 `data/`、`recipes/` 與（需要時）api surface 資料夾和 `auth.mjs` → 更新 PROJECT.md → `check` 無警告、無不符碎片，再以 `--dry` 演練一個既有 scenario：先把 `dryAllow` 設為登入端點；1.1 碎片不讀 `P.dry`，其他寫入會被 driver 攔下，存檔被攔後的失敗在演練中屬預期 | `project-profile.md` Migrating from 1.1 |
| E41 | 腳本分層 | 三層加 recipe | 即興（回合 `scratch/<surface>/`、`peek`、`api`、單一瀏覽器指令）；碎片（單一 surface 上一個穩定動作或觀察，`.e2e/surfaces/<surface>/actions/` 改狀態、`probes/` 唯讀）；scenario（清單區塊或完整業務流程，每步皆腳本、比較寫在程式中，`.e2e/scenarios/`，共用片段在 `lib/`）；recipe（仍含 agent 手動步驟的固化流程，尚不作驗收依據，`.e2e/recipes/`）；各 driver 附通用 probe（playwright：`shot`、`ui-lint`、`contact-sheet`） | `script-tiers.md` |
| E42 | 腳本分層 | 碎片引用與 driver 宣告 | 以 `<surface>:<path>` 引用，無前綴用預設 surface；查找順序：明確檔案路徑 → `.e2e/surfaces/<surface>/<path>` → skill 的 `scripts/drivers/<driver>/<path>`；每個碎片在前五行內以註解宣告 `// @driver playwright` 或 `// @driver http`，與 surface 的 driver 不符則拒絕執行，`check` 統計未宣告（不計 `helpers/`）與不符者；scenario 與 recipe 可跨 surface | `script-tiers.md` Surfaces、`scripts/core/drivers.mjs` |
| E43 | 腳本分層 | 升級規則 | 即興 → 碎片（第二次需要、每次都需要的步驟、每回合重複的手動檢查）；即興 request → 範本；即興 → recipe（會重複但尚不能腳本化）；recipe → scenario（全為腳本步驟時改寫並刪 recipe）；碎片 → scenario（需端到端重跑）；scenario 間重複 → `lib/`；與專案無關者提案給 skill 擁有者，任務中不改 skill；每次升級、變更、刪除都更新 PROJECT.md 腳本表（唯一清冊） | `script-tiers.md` Promotion |
| E44 | 腳本分層 | 降級與修復、收尾盤點 | scenario 失敗時修壞掉的碎片，不在 scenario 裡繞過；UI 或 API 變更使碎片不穩時回到即興重新學習再修；已移除功能的腳本連同表列刪除；關回合前檢視 `scratch/`，合格者當下升級，其餘留在回合資料夾，下次先翻前幾回合 | `script-tiers.md` Demotion and repair、End-of-task inventory |
| E45 | 腳本分層 | 碎片撰寫通則 | 回傳可 JSON 序列化；寫入型碎片可重跑（先查目標狀態、已完成就略過、回傳是否有寫入）並遵守 `P.dry`；http driver 演練不送任何請求、playwright driver 攔寫入請求只是安全網，碎片不得只靠它；期望值取自規格或資料，取自現有程式碼時在 check note 寫出來源檔；每個 surface 的登入集中一處；`.js`／`.mjs`／`.py` 用編輯工具改；密碼與 token 不當參數傳，從 `P.account` 取 | `script-tiers.md` Writing fragments |
| E46 | 腳本分層 | web 碎片 | 單一函式運算式 `async (page, P, H) => {}`，不得 `import`、`require`、`URL`；以 role 與文字定位元素；以 URL 進頁面（除非選單本身受測）；點持續性控制項前先關殘留對話框；截圖或版面檢查前 `H.settle(page)`；等待給明確 timeout | `script-tiers.md` Web fragments、`drivers/playwright.md` |
| E47 | 腳本分層 | API 碎片 | Node 內執行的 ES module `export default async (api, P, H) => {}`，可 import（例如 `data/builders/`）；以 `api.record` 把 id 記入 manifest；`scratch/api/` 的即興腳本要加 `api:` 前綴執行，否則套用預設 surface（通常 web）而宣告不符 | `script-tiers.md` API fragments、`drivers/http.md` Fragments |
| E48 | 腳本分層 | 注入值 | `P.env`、`P.surface`、`P.surfaceConfig`、`P.config`、`P.account`／`P.accountKey`（密碼只留在呼叫內）、`P.out`（回合或 `<round>/dry/`）、`P.args`、`P.dry`；`H.<name>` 為 driver 自帶與 `surfaces/<surface>/helpers/` 下的 helper（web 在瀏覽器端，api 為 Node module） | `script-tiers.md` Injected values |
| E49 | 腳本分層 | scenario 與 `ctx` | scenario 匯出單一 async 函式、不 import skill；`ctx` 提供 `run`、`check`（`pass = null` 自動歸 `run-error`；`opts.via`／`opts.by`／`opts.agent`）、`manual`、`addWrite`、`finding`、`lint`、`ownerStep` 與時間 helper、`valueFile`／`writeValue`、`dry`、`result`、`finish`（計算整體判定與 `stats`；報告產生時會再依 check 重算，E29）；以 `ownerStep` 或步驟時間窗比對紀錄，不用「最新一筆」；須設定 `result.items`；寫入型 scenario 先 `--dry` 一次再實跑一次 | `script-tiers.md` Writing scenarios |
| E50 | 測試資料 | 資料設計 | 經 API（或畫面）建立的測試資料是設計出來的：`data/templates/`（由真實畫面請求錄下或取自公開 API 契約，遮蔽後存，註明來源畫面或文件與日期）、`data/builders/`（範本加參數組成 request 的純函式，不連網）、`data/sets/`（具名資料組，一檔一用途）；後端改變 request 形狀時重錄範本，不憑猜測修補 | `script-tiers.md` Test data、`drivers/http.md` Request templates |
| E51 | 測試資料 | 實際寫入與重用 | 回合實際建立或變更的資料記在 `data/manifest.json`（API 寫入呼叫自動記錄，登入除外；碎片以 `api.record`、scenario 以 `ctx.addWrite` 補 id）；後續回合要重用的紀錄登記於 `.e2e/state/data-<env>.json`（`<env>` 為 `env.json` 的 `name`，否則 `dataScope`；不 commit；工具不讀寫，由 worker 依約維護），建立前先讀、能重用就不重建；以 PROJECT.md 指定的測試前綴命名 | `script-tiers.md` Test data |
| E52 | recipe | 定義與格式 | 固化但仍含 agent 手動步驟（例如透過腳本無法呼叫的 MCP 工具）的流程，由 agent 依檔重播；`.e2e/recipes/<name>.md`，YAML front matter（`purpose`、`preconditions`、`surfaces`、`writes`）加每步一個 `yaml` 區塊；欄位 `id`（不得重複）、`surface`（必填）、`kind`（`script`／`agent`）、`run`（可省 surface 前綴，有前綴須與 `surface` 相同）、`args`（map，flow map 或 JSON）、`save`（script，預設 `<recipe>-<id>`）、`do`（agent，可用 `\|` 區塊）、`evidence`（agent）、`expect`（全部）；只讀 YAML 子集（純量、頂層 `\|`／`>` 區塊、一層巢狀 map 或清單、單行 flow map／list 或 JSON），其他報錯並指出該行；範本為 `assets/recipe.template.md` | `recipes.md`、`assets/recipe.template.md`、`scripts/core/recipe.mjs` |
| E53 | recipe | 執行與成長 | script 步驟 `step <recipe>#<id> [--dry]`；agent 步驟 `log start <recipe>#<id>` → 操作 → `log end … [--evidence] [--note] [--fail]`；兩者都進 `steps.jsonl`，agent 步驟依開始時間排入時間線，agent 步驟的寫入以 `add <round> writes` 記；依賴 agent 步驟的判斷要標記（E72）；成長：從即興 → 多為 agent 步驟的 recipe → 穩定段落逐步腳本化 → 全為腳本時改寫成 scenario 並刪 recipe；PROJECT.md recipes 表含剩餘 agent 步驟數 | `recipes.md` Running、Growing a recipe |
| E54 | UI 檢查 | 範圍與分類 | 清單外判斷 UI 不合理之處，記入 UI findings、不影響判定；只適用 web surface，純 API 回合略過，清單外明顯錯誤的 API 行為（錯誤狀態碼、洩漏欄位）記入 observations；分類 `operation`、`layout`、`wording`、`display`、`error` | `ui-checks.md` |
| E55 | UI 檢查 | 方法與自動規則 | 先跑自動 lint（`ctx.lint` 或 `run web:probes/ui-lint`）→ 目視檢查 lint 抓不到的（viewport 截圖、`sheet` 聯絡表、必要時開原圖）→ 每回合重複的目視檢查改成 lint 規則；通用規則 `iso-datetime`、`clipped-text`、`stacked-header`、`readonly-counter`、`overflow-x`；專案規則放 `surfaces/<web surface>/helpers/uiLintExtra.js`；新增規則先在已知有問題與無問題的頁面各驗一次 | `ui-checks.md` Method、Automatic rules、Adding or changing a rule |
| E56 | UI 檢查 | finding 寫法 | 附證據（先截圖，用詞問題附讀到的值；當時沒留證據就標人工複看）；只寫現象與位置，不寫原因與修法；不評論測試資料內容；PROJECT.md 列為設計如此者略過 | `ui-checks.md` Writing findings、`report-spec.md` UI findings |
| E57 | 產物格式 | 回合資料夾內容 | `result.json`、`report.md`（必有）；`shots/`（有 web surface，含 `final.png`）；`values/`；`exchanges/`（有 api surface，每次呼叫一檔、遮蔽後再截斷，主體超過 20,000 字截斷）；`data/manifest.json`（有寫入）；`dry/`（演練的步驟含被攔下的寫入、values、exchanges、result，不進報告）；`review/`（視覺輔助，非證據）；`scratch/`（依 surface 分）；`steps.jsonl`（自動）；`init-proposal/`（需要時）；時間戳讓上級分辨修正前後，`r<NN>` 為回合 | `report-spec.md` Round folder |
| E58 | 產物格式 | 回合種類 | `review`（預設，依 check 判定）、`prep`（只準備資料）、`init`（初始化資產）；後兩者無 check 時結論寫回合種類與「no acceptance checks」，回傳方式見 E29 | `report-spec.md` Round kinds |
| E59 | 產物格式 | 報告章節 | 結論（含依 agent 步驟判定的 check）、清單項目對照、與前一回合比較、任務、環境（含 surface 與 driver、skill 版本與 PROJECT.md 驗證版本）、checks、截圖、UI findings（空則寫無）、writes（唯讀任務寫「none, login entries only」）、步驟與稽核軌跡、issues、observations、重現指令；標題目前以繁體中文產出，存值維持英文 | `report-spec.md` Report sections、Conclusion wording |
| E60 | 產物格式 | `result.json` 結構 | `task`（含 `kind`）、`round`、`previousReport`、`basis`、`verdict`、`summary`、`stats`（由 `ctx.finish` 或有 check 時的報告產生寫入）、`env`（含 `surfaces`、`skillVersion`、`projectVerifiedSkillVersion`）、`items`、`checks`（含 `by`、`via`、`agent`、`evidence`）、`uiFindings`、`writes`（本地時間）、`limits`、`issues`、`observations`、`reproduce` | `report-spec.md` result.json |
| E61 | 遮蔽 | 值遮蔽 | 工具寫出的每個產物都經值遮蔽：`accounts.local.json` 的密碼與登入取得的 token、cookie 出現處換成 `<redacted>`；鍵名為 `password`、`pass`、`pwd`、`jwt` 或以 password、secret、token、credential、cookie、authorization、api key、session id 結尾者整值遮蔽，`passed`、`passDate` 等一般欄位不遮；登入 exchange 省略本文（程式另省略回應 header，E69）；引用含密碼的清單原文時自行遮蔽 | `report-spec.md` Redaction、`scripts/core/secrets.mjs` |
| E62 | 寫入追溯 | 稽核歸屬 | 回合資料夾即任務身分；同回合重跑附加到 `steps.jsonl`，失敗步驟保留，演練記在 `dry/` 不混入；`close --users` 或 `audit --users` 經 adapter 抓任務時間窗的稽核紀錄到 `values/audit.json`；步驟依開始時間排序後，每列歸給在它之前最後開始的步驟，超過該步驟結束 1.5 秒者列為未歸屬並附說明 | `report-spec.md` Write traceability |
| E63 | 工具 | 資料夾與預設父資料夾 | 從專案根目錄執行（或 `--project`），往上找 `.e2e/`；執行工作區 `<parent>/e2e-review/` 固定名稱、自我忽略；演練輸出在 `<round>/dry/`；driver 輸出（例如 `.playwright-cli/`）留在執行工作區；未給 parent 時有資產用 `.e2e/out/`，否則目前目錄；派工一律依 orchestrator 指示傳 `--parent` | `tools.md` Folders |
| E64 | 工具 | 指令集 | `check`、`new`、`open`、`run`、`scenario`、`api`、`step`、`log`、`peek`、`sheet`、`add`、`audit`、`report`、`close`、`init-proposal`、`init-apply`；`open`、`peek`、`sheet` 以 `--surface` 指定 surface（預設 `web`），依該 surface 的 driver 是否提供決定可否使用；`api` 以 `--surface` 指定 http surface（預設 `api`），`--dry` 的步驟記為成功；`report`、`close` 產生報告時重算整體判定（E29）；省略 `<round>` 時用目前任務；`run` 保留參數名 `account`、`save`、`out`、`dry` | `tools.md` Commands、`scripts/e2e.mjs` |
| E65 | 工具 | session 與目前任務 | 瀏覽器 session 名取 `E2E_SESSION`，否則 surface 的 `session`，否則 `e2e`，`open`、`run`、`peek` 與目前任務指標一律依此；`new` 把目前回合記在 `.e2e/state/current-<session>`（無資產時在執行工作區）；直接執行的單一瀏覽器指令不記錄；API 呼叫一律經 `e2e.mjs` 以確保記錄；http driver 的登入 session 只存在單一指令的記憶體中，scenario 內跨步驟共用 | `tools.md` Sessions and the current task |
| E66 | 工具 | 長時間與 Windows | 超過 shell 工具時限的指令在背景跑，以 `result.json` 或 `steps.jsonl` 最後一行判斷完成，不前景 sleep；Git Bash 會改寫 `/` 開頭參數，`e2e.mjs` 依 `EXEPATH`（否則預設安裝位置）找 Git 安裝並還原自身參數，其他工具可能需 `MSYS_NO_PATHCONV=1`；skill 路徑寫 `C:/Users/...`；編輯時保留原行尾 | `tools.md` Long runs、Windows |
| E67 | 工具 | 分層與 driver 契約 | core（`scripts/core/`：專案查找、surface 與 driver 載入、回合資料夾與步驟紀錄、值遮蔽、data manifest、recipe、scenario context、audit、report）與 drivers（`scripts/drivers/<driver>/`）分層；driver 匯出 `name`、`extensions`、`available()`（版本字串或 null，供 `check`）、`runFragment({ file, P, ctx })`，可加 `open`、`peek`、`buildSheets`，對應指令對任何提供它們的 driver 可用；新增 driver 只加資料夾與 reference，core 不變；core 只用 Node.js 無第三方套件，playwright 需 `playwright-cli` 在 `PATH`，http 用 Node 內建 `fetch` | `tools.md` Layers |
| E68 | driver | playwright | `run` 把碎片與注入的 `P`、`H` 組成一個函式寫入執行工作區暫存檔，以 `playwright-cli run-code` 執行後刪除（暫存檔是密碼唯一在 `accounts.local.json` 以外出現處，僅限呼叫期間；被中斷留下的暫存檔於下次呼叫前刪除）；演練時先以 route 攔下 `POST`／`PUT`／`PATCH`／`DELETE`（URL 含 `dryAllow` 項目者放行），被攔請求記在 `dry/steps.jsonl` 的 `blockedWrites`，碎片回傳值不變；呼叫本身無 timeout，每個等待都要給 timeout；browser 端 helper `H.settle`、`H.uiLint`；已知陷阱（首次啟動偶發失敗 `open` 重試一次、全頁截圖重複固定版面、動畫期間截圖看似被裁、讀不存在元素的文字會等滿 timeout、瀏覽器保留上次登入帳號、稽核約延遲一秒、dev server 服務工作樹故未 commit 變更屬受測版本、以攔截畫面請求錄範本） | `drivers/playwright.md` |
| E69 | driver | http | `api` client：`get`／`post`／`put`／`patch`／`del`、`request`、`as(accountKey)`、`record`、`dry`；以 `--account` 登入，無帳號則不帶憑證；演練不送任何請求、也不登入，每次呼叫回傳 `{ status: 0, dry: true, request }` 並寫 `dry/exchanges/`；失敗不重試、寫入失敗只回報不重送；登入由 `auth.mjs` 每個帳號鍵每個指令一次，cookie 與回傳 header 只在記憶體、登記遮蔽；登入 exchange 省略請求本文、回應 header 與回應本文，保留方法、網址、狀態與依鍵名遮蔽的請求 header（回應中的 token 寫入時尚未被認得是秘密）；紀錄寫入 `steps.jsonl`、`exchanges/NNN-<label>-<METHOD>.json`（先遮蔽再截斷）、`data/manifest.json`（登入呼叫除外）；陷阱：日期時間照畫面格式送、中途 401 多為 session 過期需以新指令重跑、即興 `api` 的 body 取自 JSON 檔 | `drivers/http.md` |
| E70 | 範本 | `.e2e/` 骨架 | `assets/e2e-skeleton/`：`PROJECT.md`（`{{SKILL_VERSION}}` 由 `init-proposal` 填入）、`.gitignore`（`config/accounts.local.json`、`state/`、`out/`）、`config/env.json`（web 與 api 兩個 surface 的 placeholder，web 含空的 `dryAllow`）、`config/accounts.local.example.json`、`audit/fetch.mjs`（未實作即丟錯）、`surfaces/api/helpers/auth.mjs`（登入範例）、`surfaces/{web,api}/{actions,probes,helpers}/`、`data/{templates,builders,sets}/`、`scenarios/lib/`、`recipes/` 空目錄 | `assets/e2e-skeleton/` |
| E71 | 工具 | 無資產時的隱含 surface | 專案沒有 `.e2e/`（直接即興呼叫或初始化前）時，`web`（`--url=<base>`）與 `api`（`--api-url=<base>`）兩個內建 surface 皆隱含存在；隱含 api surface 沒有 `auth.mjs`，呼叫不帶登入 | `tools.md` Folders、`scripts/e2e.mjs` |
| E72 | 判斷規則 | recipe 尚不作驗收依據 | recipe 用於準備資料或狀態與培養腳本；判斷依賴 agent 操作的 recipe 步驟的 check 以 `agent` 標記（`ctx.check` 的 `opts.agent`），即使 pass 其清單項目仍為 `needs-human`，報告在結論下列出這些 check，並於人工工作註明需人工確認；回傳時該項目行內註明依 agent 步驟、重跑不會改變（E32） | Judgment、Return、`recipes.md`、`report-spec.md` Verification route、`script-tiers.md` |

## 3. 其他

### 與 `orchestrator-factory` § 5b 的介面核對

核對 `orchestrator-factory` version 1.11 的 § 5b、E2E worker prompt（shape）、Hard rules 5、Repair policy 的 E2E 段與 Factory overrides 8–9；1.11 相對 1.10 只改 § 5b 第 4 步，以對應 e2e-review 第二輪修正對依 agent 步驟判定項目的處理。**主要介面相符**，未發現互相矛盾的規定；差異多屬單邊未寫，列在下方「落差」。

相符處：

- **必要輸入**：prompt 的 `checklist`（編號與原文）、`report_parent: run_dir`、`write_permission`（`read-only` 或使用者允許的測試資料）、`accounts / environment`（僅在 PROJECT.md 未涵蓋時）、`previous_round`、`round_basis`（commit 或 change id）逐一對應 E9 的七項；報告父資料夾固定為 `run_dir`，worker 建立 `run_dir/e2e-review/`（覆寫 8）與 E9、E63 一致。
- **surface**：§ 5b 不指定 surface，交由 `.e2e/PROJECT.md` 與 `env.json` 決定；「同一環境同時只有一個 E2E worker」與 E16 的「跨所有 surface 單一操作者」一致。
- **回傳區塊**：prompt 指定 `return: E2E_REVIEW_RESULT_V1`，即 E32；兩輪修正都未改回傳契約的欄位，第二輪只在 Return 段補充依 agent 步驟項目的行內標示。
- **狀態**：§ 5b 處理 `product-fail`（修正回合 → 重新 Check → 以 `--prev` 與修正為 basis 再派下一回合，對應 E31）、`run-error` 與 `needs-human`（重派或交人工；Repair policy 明言 `run-error` 不當產品失敗）、`verified-with-limits`（只勾已驗部分、limit 留為人工項）；`needs-input` 明確對應工廠的 `needs_input`，`blocked` 對應環境或 driver 不可用。項目狀態五值與回傳狀態三值都有落點。
- **依 agent 步驟判定的 `needs-human`**：e2e-review 讓這類項目即使 check pass 仍為 `needs-human`（E72），Return 段要求在該項目行內註明並說明重跑不會改變、由上級交人工（E32）；§ 5b 第 4 步對應為「回傳標示依 agent 步驟的 `needs-human` 項目一律不重派」，並規定所有未解決項目（失敗、重派後仍 `run-error`、`needs-human`）在人工 E2E 關卡以一份統一報告交給人，不逐項交辦。兩邊一致。標示方式在 e2e-review 只是範例措辭（「agent step: …」），不是固定標記，orchestrator 需從行文判讀；報告的人工工作欄另寫「依 agent 步驟判定，需人工確認」可供核對。
- **寫入範圍**：prompt 的 constraint「只寫 `.e2e/` 與 `run_dir/e2e-review/`、不改產品、不 commit、問題交 orchestrator」與 E8、E11 相同；`.e2e/` 變更歸入 run 的 change set、由 orchestrator 依規則 commit（覆寫 9）對應 E11、E35。
- **初始化**：`init_needed: yes` → orchestrator 在下一個人工關卡呈現 proposal → 使用者核准後在下次派工以 `init_apply`（proposal 所在回合資料夾與核准者）指示，對應 E19 的 `init-apply <round> --approved-by=<who>`。工廠要求一律經使用者核准，比 E19「必要時由上級問使用者」嚴格，兩者相容。
- **內部委派**：Role 段「E2E worker 可依 `e2e-review` 允許派 sub-worker，只有它操作受測系統」與 E33 一致。

落差（不構成矛盾，但兩邊都沒寫清楚）：

- **回合種類**：E2E prompt 沒有 `round_kind` 欄位，工廠也未描述 `prep` 回合（只準備資料）何時使用；目前等於永遠以預設 `review` 派工。e2e-review 現已定義 `prep`／`init` 無 check 時回傳 `verdict: inconclusive`、無 items、`notes` 帶回合種類（E29），但 § 5b 未說明 orchestrator 如何讀這種回傳。
- **`blocked` 與 `needs-input` 的界線**：e2e-review 只在「缺必要輸入」時明定回 `needs-input`；Role 段又把「環境掛掉」列為要問上級的問題，Startup 第 4 點只說「回報上級」。工廠把 `blocked` 解讀為環境或 driver 不可用。e2e-review 本身沒有定義何時回 `blocked`。
- **版本不符與 1.1 遷移**：e2e-review 把「是否更新資產」交給上級（E39、E40），回傳 `notes` 會帶版本不符；工廠 § 5b 沒有說 orchestrator 如何處理版本不符，也沒說遷移 `.e2e/`（含設定 `dryAllow` 與演練）是否需要另行授權。
- **`init-apply` 的寫入紀錄位置**：依 `scripts/e2e.mjs`，`init-apply <round>` 把寫入紀錄加到參數指定的回合（即先前產出 proposal 的回合）的 `result.json`，而非本次派工的新回合；SKILL 只寫「記入 writes」。工廠要求「列出 worker 的寫入並對照授權」，若 worker 未在新回合另以 `add` 補記，新回合報告不會列出 `.e2e/` 的建立。
- **未初始化專案下派工的目前任務指標**（讀程式碼所見，未實際執行）：無 `.e2e/` 時，`new --parent=<run_dir>` 把目前任務指標寫在 `<run_dir>/e2e-review/current-<session>`，但讀取時只找 `<目前目錄>/e2e-review/`；從專案根目錄執行且 `run_dir` 在 `.factory/_runs/` 下時，後續省略回合的指令會找不到目前任務，需一律帶 `--out`（或回合參數）。審查修正只統一了 session 名稱來源，未改變這一點。另外隱含 surface 的 base URL 取自每次指令的 `--url`／`--api-url`，後續每個指令都要再帶。這正是工廠初始化交接會走到的情境。
- **未初始化專案的 API 審查只能不帶登入**：審查修正後無 `.e2e/` 時已有隱含的 `api` surface（E71），只有 API 的專案初始化前可以即興呼叫 API；但隱含 api surface 沒有 `auth.mjs`，需要登入的 API 在初始化前仍無法審查，E18、E19 的「照樣即興審查」對這類專案只部分成立。

### 其他不一致與缺口

- **web surface 名稱寫死（部分修正）**：審查修正後 `open`、`peek`、`sheet` 都接受 `--surface`，`sheet` 也改用指定 surface 的 `contact-sheet`。仍有殘留：Workflow 第 6 步寫 `run web:probes/shot`（`drivers/playwright.md` 另說名稱不同時以專案名稱取代），`ctx.lint` 預設 `surface = 'web'` 而 `script-tiers.md` 的 `ctx` 表只寫 `lint(where, { scope, shot })`，沒寫 `surface` 選項；`result.env.url`、`browser` 與目前任務指標的 session 只讀 `surfaces.web`，web surface 不叫 `web` 時報告環境的網址與瀏覽器為空。
- **登入 exchange 的文件與程式（殘留，影響小）**：第二輪修正後程式連回應 header 一併省略，token 經非典型回應 header 外漏的疑慮已解決。仍有措辭落差：`drivers/http.md` 說登入 exchange「只留方法、網址、狀態」，程式另保留請求 header（依鍵名遮蔽；登入時尚無 token，但 `auth.mjs` 自帶的 header 也會寫入）；`report-spec.md` Redaction 仍只寫「登入 exchange 省略本文」，未提回應 header 也省略。
- **骨架與 PROJECT.md 範本不完全對應**：PROJECT.md 範本的登入欄指向 `surfaces/web/actions/login`，骨架沒有此檔（只有空目錄）；Layout 列出 `tools/`，骨架沒有此資料夾。前者是 placeholder，後者為選用，影響小。
- **骨架稽核 adapter 預設丟錯**：`audit/fetch.mjs` 未實作即丟錯，初始化後在 adapter 實作或刪除前，`close --users` 會失敗；`check` 只確認檔案存在，會回報 adapter 存在。文件只說「無稽核紀錄的專案刪除 adapter」。
- **整體判定與 `stats` 的寫入未寫入文件**（影響小）：第二輪修正後 `report`／`close` 產生報告時依現有 check 重算 `verdict` 與 `stats` 並覆寫 `result.json`（無 check 時不動），`ctx.finish` 也會寫入；文件仍只寫 `finish` 計算整體判定（`script-tiers.md`）與「check 數由報告產出，不存在 summary」（`report-spec.md`），未提報告產生會覆寫 `result.json` 的 `verdict` 與 `stats`；沒有 check 的回合沒有 `stats`。

## 4. 與前版差異

首次建立。

- git 歷史：`git log -- skills/e2e-review` 只有一筆 `aecd92e`（2026-11-04，「新增 e2e-review」），commit 時即為 version 1.1（last_updated 2026-11-03T17:29:41）；1.0 未進入 git，僅能從 HEAD 版 `report-spec.md` 範例中的 `"skillVersion": "1.0"` 看出曾存在，1.0 → 1.1 的內容差異無法從 git 追溯。
- 1.1（HEAD）的範圍：只操作畫面（單一 playwright driver，`scripts/playwright/`）、`.e2e/` 根目錄下的 `actions/`、`probes/`、`helpers/`，description 明列「不用於純 API 檢查」。
- 1.1 → 1.2（工作樹，未 commit）：引入 surface 概念與 `http` driver（`references/drivers/http.md`、`scripts/drivers/http/`），playwright 移到 `scripts/drivers/playwright/`，新增 `core/drivers.mjs`；碎片改放 `.e2e/surfaces/<surface>/` 並要求 `// @driver` 宣告，附 1.1 遷移步驟與 `check` 版面警告；description 移除「不用於純 API 檢查」，改為可做 API 整合檢查。
- 1.2 新增：recipe（`references/recipes.md`、`assets/recipe.template.md`、`core/recipe.mjs`、`step`／`log` 指令、`checks[].agent`）；測試資料設計（`data/{templates,builders,sets}/`、`data/manifest.json`、`core/manifest.mjs`、`state/data-<env>.json`）；`--dry` 演練與 `dry/` 輸出；值遮蔽（`core/secrets.mjs`、token 與 cookie 比照密碼、`exchanges/` 納入遮蔽範圍）；回合種類 `review`／`prep`／`init`；驗證途徑 `checks[].via` 與「畫面項只經 API 驗屬 limit」規則。
- 1.2 修改：單一操作者由「瀏覽器」擴大為「受測系統、跨所有 surface」；回傳 `writes` 指向 `data/manifest.json`；`shots/` 與 `final.png` 改為只在有 web surface 時必備；UI 檢查限定 web surface，API 的明顯錯誤改記 observations；sub-worker 可起草 recipe 與 request 範本。
- 審查修正（同為 1.2，last_updated 2026-11-04T09:51:50 → 10:30:45，未 commit；依一份 20 項的設計審查全數修正）：登入 exchange 省略本文；playwright 演練時攔下寫入請求（新增 `dryAllow`、`blockedWrites`），http 演練不登入也不送請求；依 agent 步驟判定的項目一律 `needs-human`，並寫明 recipe 尚不作驗收依據；無 `.e2e/` 時另有隱含的 `api` surface；API 端點規則改為「畫面實際使用或公開 API 契約定義者」，description 改寫為透過系統 API 準備資料；`E2E_SESSION` 一律優先；範例改為中性名稱；秘密鍵名規則收窄、先遮蔽再截斷；recipe 的 YAML 子集擴充（單行 flow、頂層區塊），`surface` 必填並核對 `run` 前綴；`prep`／`init` 的回傳方式寫明；步驟依開始時間排序；暫存檔殘留清除；`<env>` 定義；driver 匯出 `available()`，`peek`、`sheet` 支援 `--surface`；driver 宣告統一為「前五行」，helper 不需宣告。
- 本對照因審查修正的調整：E1、E14、E15、E17、E26、E29、E30、E35–E37、E40–E42、E45、E47、E49–E53、E57、E58、E61、E62、E64–E70 依現行內容改寫；新增 E71（無資產時的隱含 surface）、E72（recipe 尚不作驗收依據）；無刪除元素。§ 3 移除已解決的「API 端點限制與無畫面專案」「driver 宣告位置措辭」「helper 是否需要宣告」「範例名稱的專案中立性」；「未初始化專案只有隱含 web surface」縮為「只能不帶登入」，「web surface 名稱寫死」縮為殘留部分；新增「整體判定只由 `ctx.finish` 計算」「依 agent 步驟判定的 `needs-human`」「登入 exchange 的文件與程式」「演練中的即興 `api` 呼叫記為失敗」。
- 第二輪修正（同為 1.2，10:46–10:47，SKILL.md 的 last_updated 未更新，未 commit；依前一版對照提出的四項補充）：`report`／`close` 產生報告時依 check 重算整體判定與 `stats` 並寫回 `result.json`；登入 exchange 連回應 header 一併省略；即興 `api` 的演練步驟記為成功；Return 段寫明依 agent 步驟的 `needs-human` 項目在回傳行內標示、重跑不會改變。`orchestrator-factory` 隨之升為 1.11，§ 5b 第 4 步改為此類項目不重派、未解決項目在人工 E2E 關卡統一回報人類。本對照因第二輪調整：E29、E32、E49、E60、E61、E64、E69、E72 改寫，無新增或刪除元素；§ 3 移除已解決的「整體判定只由 `ctx.finish` 計算」「依 agent 步驟判定的 `needs-human`」落差（改列為相符處）「演練中的即興 `api` 呼叫記為失敗」；「登入 exchange 的文件與程式」縮為措辭殘留；「`result.json` 的 `stats`」改寫為「整體判定與 `stats` 的寫入未寫入文件」。
