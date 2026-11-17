# design-system-extraction 元素對照

- 分支：factory
- 對照版本：`skills/design-system-extraction/SKILL.md` version 1.0，last_updated 2026-11-17T17:59:56
- 讀過的檔案：`skills/design-system-extraction/SKILL.md`、`agents/openai.yaml`、`references/` 全部（`phase-1-extract.md`、`phase-2-rebuild.md`、`phase-3-migrate.md`、`authoring.md`、`verification.md`、`run-operations.md`、`tailwind-notation.md`）、`assets/` 全部（`plan-phase-1.md`、`plan-phase-2.md`、`plan-phase-3.md`、`worker-briefs.md`、`forbid-list.template.txt`、`residue-ledger.template.md`、`deliverable-skeleton/` 的 `SKELETON.md` 與 `SKILL.md`）、`scripts/README.md`；腳本本體未逐支細讀
- 狀態：已檢查，2026-11-17 移入 manager 正式文件

## 1. 摘要

`design-system-extraction` 是領域 skill：從既有前端的程式碼逆向整理品牌設計規格，交付成給人與 agent 使用的設計系統 skill。它只說每一步做什麼、怎麼檢查，不負責編排；在 `orchestrator-factory` 下於計畫路線載入，run、派工與人閘由工廠負責；沒有工廠時由單一 session 依同樣順序執行、在同樣的閘停下。交付物是美術與設計規格，CSS 分析只是取值手段，不成為交付內容。

三個階段可從任一階段進入，只要該階段的輸入存在：

1. P1 擷取：忠實、可追溯的現況快照，每個值都能回到來源行或渲染量測；打包成分層 schema 的原始品牌 skill，每筆 `origin: source`。
2. P2 重建：凍結 P1 後，整理成 primitive → semantic → component 三層 token、依功能合併的元件（variant／size／state）、pattern 登錄與 lineage；以 H1–H5 證明沒有漂移。
3. P3 遷移（選用）：凍結 P2 後，把 web 層改寫成 utility-first（Tailwind v4）記法，token 值不變；殘留清冊逐列處理。

每個階段走同一個迴圈：寫計畫 → 獨立審查 → 計畫停點 → 凍結前版（P2、P3）→ 單一 worker 在 `staging/` 建構 → 另派驗證與冷啟動試用 → 固定順序修正 → 換入（rollback 先備妥）→ 使用者驗收。

## 2. 元素

| # | 群組 | 元素 | 內容 | 出處章節 |
| --- | --- | --- | --- | --- |
| E1 | 觸發條件 | 適用範圍 | 使用者要從既有前端程式碼擷取、逆向、重建或遷移品牌設計系統，通常在工廠計畫路線下；不用於從零設計新品牌、實作產品功能或只改單一元件樣式 | frontmatter description |
| E2 | 觸發條件 | 只能明確呼叫 | `disable-model-invocation: true`；`agents/openai.yaml` 為 `allow_implicit_invocation: false` | frontmatter；`agents/openai.yaml` |
| E3 | 流程步驟 | 角色定位 | 領域 skill，不編排；工廠下於計畫路線載入，工廠負責 run、派工與人閘；無工廠時單一 session 依同順序、停在同樣的閘 | 開頭 |
| E4 | 判斷規則 | 交付物本質 | 交付物是美術與設計規格；CSS 分析只是取值手段，永不成為交付內容 | 開頭；`phase-1-extract.md` 開頭 |
| E5 | 流程步驟 | 階段進入與組合 | 任一階段皆可進入，只要輸入存在（前一階段交付物或等價物）；新專案走 P1 → P2，P2 交付即用 Tailwind 記法；P3 只用於網頁層尚未是 utility 記法的既有套件 | Phases |
| E6 | 流程步驟 | P1 擷取 | 輸入 `<target frontend>` 原始碼（唯讀），可選本機執行實例；產出留在 run 的研究筆記（逐值附來源）與分層 schema 的原始品牌 skill（每筆 `origin: source`）；驗收：產出檔等於重新產生（`--check`）、package check `data` 加 `--allow-orphans`、獨立驗證、冷啟動試用 | Phases；`phase-1-extract.md` |
| E7 | 流程步驟 | P2 重建 | 輸入凍結的 P1 交付物；產出三層 token、依功能合併的元件、pattern 登錄、lineage、專案中立範例；驗收：對 P1 驗 H1–H5、package check `data` 再 `full`、獨立驗證、冷啟動試用 | Phases；`phase-2-rebuild.md` |
| E8 | 流程步驟 | P3 遷移 | 輸入尚未是 utility 記法的凍結套件；產出由 token 產生的 theme、utility 記法的元件規格、離線編譯的 preview、全部處理完的殘留清冊；驗收：H1–H5 與對 P2 的 box 尺寸比對、殘留掃描乾淨、冷啟動試用 | Phases；`phase-3-migrate.md` |
| E9 | 邊界條件 | 鐵律 1 專案中立 | 交付物可重用部分與為改良本 skill 寫的筆記，不含來源的公司、品牌、產品或專案內容；用 placeholder；專案資料留在 run | Iron rules 1 |
| E10 | 判斷規則 | 鐵律 2 值維持原樣 | 不「改良」值；對比不足以中性措辭記為事實，不自行改色或補上來源沒有的狀態 | Iron rules 2；`phase-2-rebuild.md` Fidelity criterion |
| E11 | 判斷規則 | 鐵律 3 不沿用劣化結構 | 形式明顯是後補或設計退化的元素與互動機制不算規格；結構改用既定 pattern（互動元件用 WAI-ARIA APG），值保留，替換記入版本紀錄 | Iron rules 3；`phase-2-rebuild.md` Fidelity criterion |
| E12 | 邊界條件 | 鐵律 4 只在本機 | 不發布設計資料；腳本不連網；需下載的工具先經使用者核可，裝在 run 內 | Iron rules 4；`run-operations.md` Tool downloads |
| E13 | 判斷規則 | 鐵律 5 範例不是目標 | 使用者舉例說明的（「例如 X」）不是目標，只有使用者指名的才在範圍內；分不清時放待議清單，不升格（`discuss-first`） | Iron rules 5；`phase-1-extract.md` Before starting |
| E14 | 判斷規則 | 鐵律 6 token 是唯一值來源 | Tailwind 記法是表達樣式的共通語言，含非 CSS 媒體（簡報、印刷）；換算依 `tailwind-notation.md` | Iron rules 6 |
| E15 | 判斷規則 | 鐵律 7 先忠實再重建 | P1 不為美觀合併或改名；P2 不發明值；每個 P2 值經 lineage 回溯到 P1 | Iron rules 7 |
| E16 | 驗證 | 硬規則 H1–H5 | P1 之後每個階段對凍結的前版重驗，失敗即停：H1 記錄過的文字／背景對比不退步；H2 可區分的 surface 保持可區分；H3 各 role 內、各 variant 在每個檢查寬度依部位、屬性、狀態實際生效的字級順序不變（覆寫只取代所在部位）；H4 控制項 box 高度差 < 4px；H5 沒有孤兒 primitive | Hard rules；`phase-2-rebuild.md` Hard rules |
| E17 | 驗證 | 產出新鮮度與數值子集 | 每個產生的檔案等於重新產生；手冊中每個數字都是資料檔的子集 | Hard rules 末段；`authoring.md` Self-checks |
| E18 | 流程步驟 | 階段迴圈 1–2 | 由 `assets/plan-phase-<n>.md` 寫階段計畫進 run；獨立計畫審查，修訂後再審 | Gates 1–2 |
| E19 | 人閘 | 計畫停點 | 工廠下依工廠計畫路線的停點規則，並在 Converge 建議使用者先要求看計畫（本領域需要計畫、獨立審查與使用者確認）；無工廠時停下等使用者確認計畫 | Gates 3 |
| E20 | 流程步驟 | 凍結前版 | P2、P3 在計畫確認後、建構前，凍結前版並匯出唯讀 baseline：有 tag 用 tag 匯出，沒有 tag 用 hashed copy；commit 與 tag 只在使用者要求時（`orchestrator-factory` hard rule 6、`commit-message-suggestion` `## Committing on request`） | Gates 4；`run-operations.md` Frozen baseline |
| E21 | 流程步驟 | 建構、驗證、修正 | 一個 worker 在 run 的 `staging/` 建構相依系列；另一 worker 驗證，再另一個做冷啟動試用；修正依固定順序：對應檔與 token → 規格與 preview → 手冊 → 完整檢查 → 重驗 | Gates 5–7；`verification.md` Fix loop |
| E22 | 人閘 | 換入與驗收 | 前提通過且 rollback 備妥（換入前目標資料夾的已驗證雜湊副本；首次 P1 為空）後換入；停下讓使用者看 preview 與 diff 驗收，或以 rollback 還原；只在使用者要求時 commit | Gates 8–9；`run-operations.md` Staging and swap |
| E23 | 產物格式 | 續作點 | 每次停下都把續作點寫進 run 狀態檔的 Stage 行（工廠下為 `_status.md`）：階段、步驟、最後完成的產出、下一步；續作不需重讀對話 | Gates 末段；`run-operations.md` Pause and resume |
| E24 | 流程步驟 | 與工廠搭配 | 計畫骨架填入工廠的 `_plan.md`；worker 簡報取自 `assets/worker-briefs.md`；相依系列留給同一 worker，驗證與冷啟動用不同 worker；forbid list 由 orchestrator 在建構前產生並留在 run | Working with a factory |
| E25 | 判斷規則 | 驗證結果分類 | `product-fail`（套件錯誤，進修正輪）、`run-error`（檢查本身失敗，修檢查後重跑，不計入套件）、`needs-human`（run 無法判斷，帶證據停在閘）；只有確認的 `product-fail` 進修正輪 | Working with a factory；`verification.md` Report classes |
| E26 | 流程步驟 | 閱讀順序 | 只讀當前步驟需要的；依步驟對應 reference、腳本與 asset（範圍與計畫 → P1 各步 → 撰寫 → 重建 → 遷移 → 驗證 → 凍結／換入／工具／環境）；`scripts/README.md` 列全部參數 | Reading order |
| E27 | 人閘 | P1 開工前定案 | worker 讀碼前與使用者定：品牌前端與排除者、目標、交付物與位置（asset 複製不連結）、參考格式（只取結構）、保真、在地；記入階段計畫 | `phase-1-extract.md` Before starting |
| E28 | 流程步驟 | P1 八步 | 1 樣式來源與 stack profile；2 元件與 asset 盤點；3 視覺語言與版面；4 規則索引與對比工具；5 元件層級的值；6 渲染檢查；7 token 綜合；8 打包；步驟 5 留下大量 `runtime-dependent` 時，步驟 6 提前到 7 之前 | `phase-1-extract.md` Step map |
| E29 | 產物格式 | 證據三欄 | 步驟 5 起每個值帶 `source`（`measured: <path:line>`、`measured: render <page> @<width>`、`estimated: <basis>`）、`resolved`、`confidence`（`static-certain`／`runtime-dependent`／`unresolved`）；使用前重開引用行一次；後兩級進 Known Gaps | `phase-1-extract.md` Evidence fields |
| E30 | 判斷規則 | P1 防護 | 依元件解析值，不看全域頻率；屬性含版面對齊與欄寬；同頁載入同一框架的多個版本時，以渲染判定實際生效者，無法渲染則標 `runtime-dependent`；需輸入資料、登入的頁面列 Known Gaps，不繞過；自創的驗證路線無結果時標 `estimated`、記 gap 後繼續，不轉成使用者問題；若該證據屬必要驗證，worker 交回 orchestrator 當阻擋項；因頁而異的文字與欄寬標「varies by page」並列出觀察案例 | `phase-1-extract.md` Guards |
| E31 | 邊界條件 | 渲染檢查授權與清理 | 先確認可啟動的服務、可否寫 build 產出、允許的互動；啟動會安裝套件時停下回報；不送出表單、不觸發寄信或寫資料；結束時刪暫存 key、重設 emulation、停服務、確認埠已釋放、確認產品 repo 無新變更 | `phase-1-extract.md` 6 Render check；`run-operations.md` Browsers |
| E32 | 產物格式 | P1 打包 tier 指派 | 角色推薦值 → `semantic`；元件專用的並存原值 → `component`；未品牌化殘留 → `semantic` 命名 `residue-<role>`；尺度階 → `primitive`；不合併、不刪除原值；研究欄位留在 run；usage 只寫數字，不寫「fails」「must fix」 | `phase-1-extract.md` 8 Packaging |
| E33 | 判斷規則 | P2 決策檔 | 人的判斷放在 run 的 `data/decisions.json`，腳本只放演算法；含色彩 role 草稿、type 格位、size 分類、元件目錄與每個原 variant 的去向、必填 `note_syntax`；lineage 另存 `data/lineage.json`；`rationalize.py` 失敗時以最小偏差解決並記為待決，不發明新規則 | `phase-2-rebuild.md` Decisions file |
| E34 | 判斷規則 | P2 token 分層與合併 | primitive 不引用任何東西；semantic 引用 primitive（複合值可引用 semantic 色）；component 引用 semantic 或 primitive，同元件可互引；其餘跨層引用 package check 失敗；色彩以 CIELAB／ΔE2000 合併，極淺 surface 只經決策檔合併；type、spacing、radius、shadow、size、breakpoint 各有合併規則 | `phase-2-rebuild.md` Token tiers、Color、Type、Spacing |
| E35 | 判斷規則 | P2 元件 | 依功能不依頁面合併，三軸 variant／size／state；中性 id 並對照 forbid list；pattern 進登錄；每個原 variant 對到目標或「removed」；寫 parts 前對每個互動元件套保真準則；新增狀態標 `origin: added`，只檢查實際新增的狀態（無新增則略過；各 surface 依實際套用的焦點環量測，新增項無可驗證 surface 時失敗），focus ring 對每個可放焦點元素的 surface ≥ 3:1 | `phase-2-rebuild.md` Components、Hard rules |
| E36 | 判斷規則 | P3 目標記法 | 預設 utility CSS（規格與 preview 無舊機制 class，theme 名只來自 token，preview 狀態用標記屬性）；非 utility 為選項（每個 class 帶品牌前綴，用強制狀態 class）；只有使用者指名的框架才是目標 | `phase-3-migrate.md` Choose the target notation |
| E37 | 判斷規則 | P3 殘留分類 | 先盤點再改寫，殘留藏在值、token 與資料結構；四類：`brand-value` 保留、`mechanism-bound-value` 隨元素保留或刪除、`motion` 保留為 duration／easing token、`mechanism` 移除改為 anatomy + variant + ARIA；「等於框架預設」不等於機制，看得見的值保留 | `phase-3-migrate.md` Residue inventory |
| E38 | 判斷規則 | P3 theme 與白名單 | `theme.css` 由 token 產生、不手改；先把 stock namespace 重設為 `initial`；值一律 `var(--<prefix>-...)`；舊變數別名放在消費產品、不進套件；同名不同值清單公布於 DESIGN.md usage；arbitrary 值不含色彩與未登錄長度；forbid list 與 utility 名衝突時用等價 arbitrary property 並回報 | `phase-3-migrate.md` Tokens to theme、Whitelist |
| E39 | 產物格式 | DESIGN.md 章節 | 依骨架 0–10 章；必留區塊：container、並排間距、群組間距、其他專案的 reset、字型 fallback、整頁骨架；以點名 token 的祈使規則開頭；值 ⊂ JSON；計數指向資料檔；不放研究敘事；核心加 web 層 500 行內 | `authoring.md` DESIGN.md |
| E40 | 判斷規則 | 格式與「標準」的說法 | DESIGN.md 格式以實際讀者為準，平台格式只作參考；關於「標準」的結論依 `research` skill 標注依據（primary source、verbatim 親自讀原文不經摘要、partially supported、own design），不把自己的設計說成標準 | `authoring.md` Format choice |
| E41 | 產物格式 | 交付 skill 與元件規格 | 交付 SKILL.md 預設明確呼叫、兩宿主政策相反、`last_updated` 由 OS 時鐘取到秒；元件規格錨點統一 `<component>--<variant>` 並加顯式 `<a id>`；機械段落由 map 產生；範例文字取自記錄的來源文案，沒有就用標記的中性 placeholder，不自創文案；map 看來有誤時回報擁有者，不自改 | `authoring.md` Deliverable SKILL.md、Component specs |
| E42 | 產物格式 | 離線 preview | 單向總覽頁，無腳本、無外部資源；fragment 是唯一 HTML 來源；每個主品牌 variant 一張卡；未品牌化狀態照原樣畫並標示；缺的 map 值不在 preview 補 | `authoring.md` Offline preview |
| E43 | 驗證 | 獨立驗證 | 驗證者不改套件、自寫腳本、不信建構者自報；證據依階段：P1 用 data 加 `--allow-orphans` 並記錄後續基準，P2／P3 以 full 檢查並自資料重算 H1–H5；回溯來源抽樣 ≥ 30 token、每族 ≥ 3，不足時全查；重算全部對比；依計畫的元件與寬度並排截圖，看群組對齊；無 live site 時用計畫指定的凍結證據，皆無則停下；工廠下驗證與冷啟動試用在 Converge 列為待授權工作 | `verification.md` Independent verification |
| E44 | 驗證 | 冷啟動試用 | 只拿套件的新 worker 從空白 HTML 做整頁 mock，回報閱讀順序、每區依據、每個猜測；每個猜測都是套件缺口，進修正輪；不同頁型只比外框與元件 | `verification.md` Cold-start trial |
| E45 | 驗證 | box 尺寸比對 | P3 與任何不應移動像素的變更：同 DOM 的新舊 preview 逐元素比 `getBoundingClientRect`（`boxdiff.py`），先排除 reset 影響，其餘逐一說明或修正；瀏覽器中再驗 H4 | `verification.md` Box-size comparison |
| E46 | 邊界條件 | forbid list | 機械產生、只留在 run、不進任何交付物，也不把其內容抄進筆記或報告；區段 `[allow]`（區分大小寫遮蔽）、`[substring]`、`[class]`、`[regex]`、`[section-allow]`；worker 只讀不改，衝突由 orchestrator 決定是否移入 `[allow]`；給可重用 skill 的筆記也要掃 | `run-operations.md` Forbid list；`forbid-list.template.txt` |
| E47 | 邊界條件 | 工具下載 | 先向使用者說明套件、版本、來源、大小；裝在 run 內固定路徑，不裝系統暫存或全域；釘選至少兩週前發布的確切版本；cache 指到 run、跳過 install script；裝完刪 cache 並記入 run 狀態 | `run-operations.md` Tool downloads |
| E48 | 邊界條件 | rollback 方式 | 換入前把目標資料夾複製到 run 並寫雜湊清單、驗證；回復時只清空目標資料夾內容、複製回去，以路徑集合與雜湊驗證；不用會改 index、HEAD 或其他工作樹路徑的 git 指令；不在換入目標外遞迴刪除 | `run-operations.md` Staging and swap |
| E49 | 產物格式 | assets 範本 | `plan-phase-1/2/3.md`（工廠計畫路線必填項：目標、範圍與排除、交付物與路徑、允許寫入、worker 指派、驗證方式、人閘、交接；另有決策與修訂紀錄表）；`worker-briefs.md`（Research、Packaging、Construction、V1、V2 五種角色，共通規則含不用 git、不問使用者、只經回傳格式回報）；`residue-ledger.template.md`（`## Ledger` 六欄表）；`deliverable-skeleton/`（交付 skill 骨架，預設明確呼叫、version `"1.0"`、相對路徑） | `assets/`；`deliverable-skeleton/SKELETON.md` |
| E50 | 產物格式 | 腳本群組 | 只用 Python 標準庫、不連網、所有路徑皆為參數，以 `python -I` 執行並附 self-test；`extract/`（P1 掃描、索引、比對、對比）、`rebuild/`（色彩量測、`rationalize.py`）、`package/`（產生 token、theme、對比、preview 與 `check_package.py`）、`migrate/`（殘留掃描、清冊檢查、同名比對）、`verify/`（`boxdiff.py`）；`package/` 複製進交付套件 `scripts/`，run 內不改副本，需改時改本 skill 再複製 | `scripts/README.md`；`phase-2-rebuild.md` Layered packaging |

## 3. 其他

- **引用方**：目前沒有其他 skill 引用本 skill；本 skill 單向引用 `orchestrator-factory`（計畫路線、hard rule 6）、`commit-message-suggestion`（`## Committing on request`）、`discuss-first`（待議清單）與 `research`（結論依據標注）；計畫範本的審查欄位指向 `change-review-request`／`change-review-response` 的檔名格式。
- **research 標注規則只在本 skill 的撰寫步驟生效**：E40 借用 `research` skill 的依據分類，但 `research` 本身只在被呼叫時生效，本 skill 的其他步驟或其他 skill 不會自動套用；擺放位置已定案，記為已知限制。
- **腳本間重複的 helper 延後處理**：多支腳本中 hex 正規化與前綴邏輯重複；抽成共用模組屬重構，超出本版「不重寫腳本」的範圍，審查分類駁回並記為後續。
- **H1–H5 在 P1 不設閘**：P1 尚未合併任何值，只記錄 P2 檢查所需的資料；H5 的孤兒 primitive 在 P1 以 `--allow-orphans` 報告而不失敗。
- **工廠計畫路線的停點以工廠為準**：本 skill 只建議使用者在 Converge 先要求看計畫，實際是否停下由工廠計畫路線的規則決定；無工廠時才由本 skill 直接要求停下確認計畫。
