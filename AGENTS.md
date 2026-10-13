# 模擬台北：dosgolem 重打包與 HD 版本

本檔是本專案的協作入口。面向使用者的回覆、文件與提交訊息使用繁體中文。
所有研究與實作先建立 GitHub Issue，再開工。遠端 Issue 是工作狀態的唯一權威。

## 1. 使用者授權與專案範圍

依使用者 2026-10-10 的指示，本次工作已授權：

- 參考 `/home/anr2/cht/psychic-war` 與 `/home/anr2/cht/simcity` 的經驗，
  用 dosgolem 重新打包《模擬台北》，並提供 HD 版本。
- 建立新的 **private** GitHub 儲存庫，啟用 Issues。儲存庫名稱預設為 `taipei`，
  owner 以主機 `gh` 確認的登入帳號為準。建立前檢查同名儲存庫；不得接管既有專案。
- 初始化本目錄的 Git，設定專案身分，提交並推送本範圍內的文件、原創程式與建置腳本。
  推送前必須檢查明確的檔案清單，不使用 `git add .` 收入原版資料。
- 建立、更新、留言及關閉本專案範圍內的 Issue，記錄依賴、證據、驗證與完成結果。
- 使用者已在本對話追加明確授權使用主機 `/home/anr2/.local/bin/gh`，並指示開始。
  此授權持續有效；工具環境限制與使用者授權分開記錄，不因工具拒絕而重複索取授權。
- 使用者於 2026-10-12 要求 README 展示原版與 HD 五語系截圖。依 [#53](https://github.com/wicanr2/taipei/issues/53)，
  選定的文件用 PNG 可加入目前私人儲存庫的 `workspace/screenshots/`，來源與雜湊保存於該處 `manifest.json`。
  此例外限 README 展示，不授權原版執行檔、資料、素材包、存檔、原始收據或公開發布。
  後續修改已展示的畫面或譯文時，同次沿第 3 節的擷取與匯出工具更新截圖及來源清單。

上述管理操作不需要重複徵求授權。儲存庫改為公開、公開 Release、上傳原版素材、
加入協作者、改動其他專案、推送 dosgolem 上游及破壞性操作，另行取得授權。

啟動順序固定為：**本 AGENTS.md → 私人儲存庫 → 初始工作項目的 Issues → 研究與實作**。
第一張治理 Issue 補登本次啟動文件與環境阻塞。建立 Issues 前，不解壓原版、不跑遊戲、
不寫產品程式；讀取協作規則與參考專案入口屬於撰寫本檔的準備工作。

## 2. 定位與已確認邊界

- 主要路線是 dosgolem 執行原版 DOS 程式，由本專案提供前端與 HD 呈現。
  不自行重寫模擬規則，也不把 simcity 的 Micropolis 規則套入《模擬台北》。
- 原版 EXE、遊戲資料、規則、亂數與存檔格式保持原樣。存檔寫入獨立可寫目錄，
  原始輸入唯讀。匯入既有存檔時保留原檔並驗證副本。
- HD 層只改變呈現。素材來源、繪製時機、遮擋、清除及動畫依本作證據辨識。
  未辨識或失配時顯示原版，不用推測圖像覆蓋畫面。
- 美術風格已定 B 細緻手繪材質，解析度為 1280×800，交付 Windows、Linux、macOS，字型採 Noto 高清黑體。
  遊戲中以 F12 即時切換原版／HD，保留目前遊戲狀態；操作契約見 [014](docs/spec/014-live-theme-switch.md)。
  使用者指定重繪所有圖片與操作介面，包含各場景及動畫。固定字型與已展示比較圖見 `CONTEXT.md`。
  一般素材批次沿已確認的 B 風格與原版版面自主執行；實質變更構圖、內容、操作或忠實度時依第 8 節確認。
- 使用者已指定所有工作區使用本專案的 `workspace/`，覆蓋共用方法的 `workplace/` 預設。
  原版資料保留使用者提供的位置並唯讀掛載；探針、工具副本、快取與中間產物都在 `workspace/`。
- 使用者追加 HD 五語系：繁體中文、簡體中文、日文、韓文、英文。F12 原版模式保留繁中。
  已確認 F11 遊戲中切換並保存選擇，依 [030](docs/spec/030-hd-localization.md) 與 [#49](https://github.com/wicanr2/taipei/issues/49) 執行，不改 DOS 語意或存檔。
  另確認 Shift+F1 開五語系 Help，保留原版 F1 離開，依 [031](docs/spec/031-help.md) 與 [#50](https://github.com/wicanr2/taipei/issues/50) 執行。
- 不因其他遊戲能在 dosgolem 執行，就宣稱本作已受支援。先跑本作的正常啟動探針。

## 3. 入口與按需載入

剩餘五語系的開場、圖片文字與逐字相位入口為 [033](docs/spec/033-localization-source-coverage.md) 與 [#52](https://github.com/wicanr2/taipei/issues/52)。研究工具使用 `text-source-audit -remaining-steps`，只觀察正常原版呼叫，不改寫 DOS。

每個工作階段先讀本檔，再讀已建立的 `CONTEXT.md`、本次遠端 Issue 與直接相關規格。
新增文件時，同次更新本節或專案索引。表中的「規劃」路徑須由對應 Issue 建立，
尚未存在時不得當成已完成證據。

| 觸發／用途 | 入口 | 使用限制 |
|---|---|---|
| 專案規則與啟動 | `AGENTS.md` | 本檔為專案入口 |
| 目前真相與決策 | [CONTEXT.md](CONTEXT.md) | 唯一現況表；不保存完整歷史 |
| 工作項目與進度 | [GitHub Issues](https://github.com/wicanr2/taipei/issues) | 主機 gh 即時回讀；不另建本機待辦鏡像 |
| 歷程與交接 | [WORKLOG.md](WORKLOG.md) | 按時間追加，包含驗證與 Docker 清理狀態 |
| 原版研究 | [docs/re/001-input-baseline.md](docs/re/001-input-baseline.md) | 固定輸入雜湊、工具版本、定位與證據等級 |
| 原版盤點工具 | [workspace/tools/inventory.py](workspace/tools/inventory.py) | Docker 內唯讀盤點使用者提供的解壓來源 |
| 原版啟動與缺口 | [docs/re/002-dosgolem-startup.md](docs/re/002-dosgolem-startup.md) | 固定工具、四份補丁、冷啟動收據與重播 |
| 原版探針 | [workspace/tools/probe.sh](workspace/tools/probe.sh) | Docker 內從固定基底與補丁重建，支援範圍見啟動基線 |
| 正式行為與 HD 契約 | [CONTEXT.md 的文件入口](CONTEXT.md#文件入口) | DRAFT／READY／CONFORMED；規格回鏈 Issue |
| 自有程式授權 | [LICENSE](LICENSE) | RRSAL-1.0，不授權原版或第三方元件 |
| 驗收範圍 | [docs/verification-matrix.md](docs/verification-matrix.md) | 串起 Issue、玩家路徑、證據與未驗限制 |
| 執行與交付摘要 | [README.md](README.md) | 穩定入口；不寫逐輪流水帳 |
| README 原版與五語系畫面 | [擷取工具](workspace/tools/readme_screenshots.sh)、[匯出工具](workspace/tools/export_readme_screenshots.py)、`workspace/screenshots/manifest.json` | #53；正常冷啟動擷取，選定 PNG 限目前私人儲存庫展示 |
| 六圖表五語系正常操作 | [GUI 入口](workspace/tools/chart_locale_gui.sh)、[完整呈現核對](workspace/tools/chart_locale_check.py)、[截圖匯出](workspace/tools/export_chart_screenshots.py) | #54 接續 #48；沿 029／032，長時間狀態抽樣不列結案門檻 |
| 遊玩抽驗收尾與城市截圖 | [收據回核及匯出工具](workspace/tools/accept_chart_playtest.py)、[029](docs/spec/029-chart-windows.md) | #55；Docker 內核對現行產品與既有正常遊玩收據，匯出災難台北城市畫面 |
| 外部知識路由 | `/home/anr2/.codex/knowledge-base/knowledge-router.md` | 只讀命中入口及必要 reference |
| 復古遊戲證據與實作 | `/home/anr2/.codex/skills/reverse-engineer-retro-game-remake/SKILL.md` | 用於最小充分研究、規格與驗收 |
| 共同決策 | `/home/anr2/.codex/skills/grilling/SKILL.md` | 重大取捨逐題確認；一般執行不重開訪談 |
| HD 多語系 | [030](docs/spec/030-hd-localization.md) | 已確認 HD 五語系、原版繁中與 F11；控制／設定／六標題 READY，其他家族 DRAFT |
| 五語系 Help | [031](docs/spec/031-help.md) | Shift+F1 開 Help、原版 F1 不變；限八列操作、五語系與輸入隔離 CONFORMED |
| 其餘介面翻譯 | [032](docs/spec/032-interface-localization.md) | #51；既有來源家族五語系 READY，未辨識視窗另查證 |
| 翻譯與顯示隔離 | `/home/anr2/.codex/knowledge-base/local/localization-display-semantic-isolation.md` | 翻譯、語系切換、文字來源及字型檢查時載入；TSV 只供顯示，不改識別值與 SAV |
| 文件與新目錄 | `/home/anr2/.codex/knowledge-base/local/project-document-responsibilities.md` | 建立文件或目錄前讀取 |
| 交付目錄 | `/home/anr2/.codex/knowledge-base/local/retro-remake-dist-all-output.md` | `dist-all/` 子目錄的唯一契約；不照抄舊專案 |
| 正式版號 | `/home/anr2/.codex/knowledge-base/local/retro-remake-release-versioning.md` | 定版、打 tag 或重發前讀取 |
| 專案程式授權 | `/home/anr2/.codex/knowledge-base/local/rrsal-1.0.md` | 使用指定 RRSAL-1.0 範本；不授權原版素材 |
| dosgolem 能力與用法 | `/home/anr2/cht/dosgolem/README.md`、`CLAUDE.md` | 先查能力，再用 `cmd/probe`；Docker 入口 `tools/go.sh` |

### 參考專案的經驗

| 來源 | 本專案採用的經驗 | 不直接移植的內容 |
|---|---|---|
| `/home/anr2/cht/psychic-war/AGENTS.md`、`CONTEXT.md`、`docs/spec/024-hd-theme.md`、`tools/package.sh` | 原版執行加呈現覆繪；來源失配回復原版；原版與 HD 比較機器狀態及存檔；驗實際封包 | 遊戲位址、PBL 格式、8×8 遮罩、熱鍵、美術定案與完成數字 |
| `/home/anr2/cht/simcity/AGENTS.md`、`CONTEXT.md`、`tools/verify_package_all.sh` | 正常玩家路徑、存退讀、滑鼠座標、畫面差分、乾淨目錄封包驗收與平台限制 | Micropolis 模擬規則、城市格式、圖形集、舊交付目錄及本作未驗證的功能 |

參考專案的使用者定案只適用於各該專案。本專案採共用規則的現行契約；
參考文件裡的舊版交付結構、授權或 oracle 限制不能覆蓋現行規則。

## 4. GitHub 與 Issue 先行

- GitHub 管理使用主機 `/home/anr2/.local/bin/gh`。第一次存取先執行 `gh auth status`。
  有 sandbox 或網路隔離時使用 host／unsandboxed 權限，在 Codex 為 `require_escalated`。
  不在受限環境呼叫後推斷主機登入狀態，不把憑證搬入 Docker。
- 建立後回讀儲存庫網址、owner、private 狀態與 Issues 是否啟用，再記入 `CONTEXT.md`。
  本機 Git 身分先查專案設定，電子郵件沿參考專案使用 `wicanr2@gmail.com`；不改全域設定。
- 先列舉遠端 Issues，避免重複。初始工作項目須全部登錄，再依依賴順序開工。
  後續新增研究、缺陷、規格、素材批次或打包工作，也先建立 Issue。
- 每張 Issue 寫明目標、範圍、依賴、輸入、規格狀態、完成條件與驗證方法。
  開工回報實際 Issue URL；提交訊息與規格引用實際編號，不預填不存在的 `#1` 等編號。
- 執行中回寫已查證事實、證據入口與阻塞。超出原範圍時先拆 Issue，不「順便」加功能。
- 完成後附提交、驗證命令、結果、證據路徑及剩餘限制，再關閉並回讀狀態。
  不因已有圖片、測試全綠或檔案存在就關閉整項 HD／交付 Issue。
- 主機 gh 權限或遠端存取受阻時，記錄確切環境原因並停止依賴 Issue 的工作。
  本機草稿不是遠端 Issue，也不能作為開工依據。尚未成功執行主機 auth 檢查時，
  不宣稱憑證失效。

### 初始 Issue 範圍

初始工作已登錄為 [#1–#9](https://github.com/wicanr2/taipei/issues)。
下表只定義範圍與依賴，狀態只在遠端維護。

| 階段與 Issue 標題 | 依賴 | 完成條件 |
|---|---|---|
| [G0／#1](https://github.com/wicanr2/taipei/issues/1)：協作治理 | 本檔 | 回讀 private 與 Issues；設好排除規則；建立現況、歷程與文件索引；提交本檔並回鏈啟動紀錄 |
| [G1／#2](https://github.com/wicanr2/taipei/issues/2)：原始輸入 | G0 | RAR 與成員 SHA-256、檔案清單、版本證據、EXE／啟動參數、資料及存檔需求；來源唯讀且無越界解壓 |
| [G2／#3](https://github.com/wicanr2/taipei/issues/3)：dosgolem 基線 | G1 | 固定 dosgolem commit；從真實入口到第一個可操作畫面；保存輸入重播、畫面與缺服務紀錄；缺口逐項開 Issue |
| [G3／#4](https://github.com/wicanr2/taipei/issues/4)：前端與存讀檔 | G2 及必要缺口 | READY 規格；正常輸入、座標與音訊；新遊戲、核心操作、存退讀；資料目錄可寫且來源雜湊不變 |
| [G4／#5](https://github.com/wicanr2/taipei/issues/5)：HD 來源與原型 | G2 | 本作繪圖來源及遮擋證據；原版／HD 同狀態比較；重繪清單與覆蓋計數；美術及解析度待使用者定案 |
| [G5／#6](https://github.com/wicanr2/taipei/issues/6)：HD 與平台契約 | G3、G4 | 記錄使用者定案、批准原型、素材權利、目標平台、抽樣範圍與 READY 契約；未知項明列是否阻塞 |
| [G6／#7](https://github.com/wicanr2/taipei/issues/7)：HD 接入 | G5 | 每批可追溯來源、原位／動作／遮擋驗證、未知來源回退、切換與重載；原版機器狀態及存檔不受 HD 影響 |
| [G7／#8](https://github.com/wicanr2/taipei/issues/8)：正常玩家路徑 | G3、G6 | 實際 GUI 冷啟動、核心操作、轉場、切換、存檔、退出及重載；dosgolem 自生收據、有效負對照與預登記抽樣 |
| [G8／#9](https://github.com/wicanr2/taipei/issues/9)：封包驗收 | G5、G7 | 乾淨輸入、固定版本與依賴；逐包啟動／內容／存檔位置／權利／manifest／SHA-256；明列真機未驗項，交付僅留本機 |

## 5. dosgolem 分層與原版證據

- 本作位址、資料識別、畫面狀態與 HD 素材對應留在本專案。通用 CPU、DOS、BIOS、
  顯示、輸入與音訊能力屬 dosgolem，不把《模擬台北》名稱或位址寫入通用層。
- `/home/anr2/cht/dosgolem` 作為唯讀參考。需要補能力時先開本專案缺口 Issue，
  再在隔離 clone／worktree 工作，遵守該專案規則；不直接改動它的目前工作樹。
- 固定使用的 dosgolem commit、Go 版本、Docker image ID 與依賴鎖檔。
  參考專案的 `latest` 標籤或本機 `replace` 路徑不足以重現交付。
- dosgolem 是原版行為、畫面、輸入與虛擬時間的主要執行器；正式收據由它重生。
  DOSBox／DOSBox-X 只補足診斷與交叉驗證，擷取明標輔助基準，不改名冒充 dosgolem 收據。
- 每項研究保留輸入檔名與 SHA-256、工具版本、原始 bytes／位址空間、資料流與可重播步驟。
  證據等級使用「已證實、強推論、假說、未知」。反組譯名稱只供導覽，不取代原始定位。
- 逆向只追正常玩家功能或交付所需的最小充分證據。硬體時序依公開規格及成熟模擬器契約，
  不為 DAC／PIT／DMA 逐週期一致深挖原版 driver。

## 6. 規格與驗證閘門

正式行為採：`原版證據 → DRAFT → 證據審查 → READY → 實作 → 同狀態驗證 → CONFORMED`。
沒有 READY 的探針及原型不進產品路徑。實作發現未知時回到研究與規格，不猜補。

- 使用者於 2026-10-13 指定「抽驗能由遊玩就算驗收通過」。已實作功能以正常玩家路徑抽驗判定，
  長時間相同步數 RAM／CPU／RNG 對拍不列必要結案門檻。可沿用與現行產品一致的已通過收據，
  不為結案重跑同一流程。六圖表的具體範圍見 [029](docs/spec/029-chart-windows.md)，
  回核入口為 [accept_chart_playtest.py](workspace/tools/accept_chart_playtest.py)，只在固定 Docker image 執行。
  此標準不將未製作的圖片、未走過的分支或未驗平台算成完成；未執行的狀態對拍仍列證據限制。
- 基線與 HD 使用相同原始資料、dosgolem 版本、初始狀態、虛擬時間及等價輸入。
  涉及亂數時在執行前固定 seed 或明示受控亂數條件，不重擲挑結果。
- 驗證 HD 不改變原版記憶體、暫存器、原版畫面緩衝、遊戲資料與存檔結果。
  主題切換不得重開遊戲、重設亂數或遺失當前狀態。
- 視覺驗收另驗來源辨識、動作相位、遮擋、消失、背景恢復、切換與讀檔後的殘影。
  用失配來源、撤除素材及區外像素檢查建立負對照。
- 中文文字驗字型實際墨跡、文字安全矩形、最長實際字串與縮放後畫面。
  不因字串表完整就宣稱沒有缺字或裁切。
- 正常 GUI 走一條實際核心操作至存退讀的垂直路徑。快照、direct-entry、座標或狀態注入
  只供診斷，不能取代正常玩家路徑。
- 驗實際交付封包，在乾淨目錄啟動，素材與存檔分開，包含缺必要資料時的可見錯誤。
  平台結構檢查、Wine 執行與真機試玩分別標示；未驗項保留原狀。
- 抽樣情境與完成條件先寫入 Issue／驗收矩陣，再執行。將「重打包已驗證」、
  「原版 oracle 未知」與「可選改善」分開，不用新發現重新開啟無關的已完成工作。

## 7. Docker、檔案與交付衛生

- 分析、搜尋、解壓、建置、測試、執行遊戲、音訊與 GUI 自動化只在 Docker 內進行。
  主機僅做必要 Docker／Git 管理、工作樹檢查與檔案編輯；GitHub 依第 4 節的主機例外。
- 沿用現有合適 image，先查 entrypoint 與工具版本；確有缺件才修正可重現建置來源。
  不掛主機 Python 或虛擬環境進工具容器。
- 一次性工作使用 `--rm`、相稱的 `--memory`、`--cpus`、`--pids-limit` 與外層逾時。
  預設 `--network none`；明確需要下載時才開網路。背景程序須有 trap 與有界擁有程序。
- 原版輸入唯讀掛載，可寫容器指定使用者 UID/GID。掛載前確認 host 路徑存在與類型；
  寫入前後核對目錄與檔案擁有權，不對整個專案遞迴 chown。
- 原始壓縮檔保留原位且不覆寫。研究中間產物使用專案根目錄 `workspace/`；
  新目錄先依第 3 節文件職責契約確認。不要為每輪研究另造根目錄。
- 每批工作用 `find <工作根> -user root -o -type d -name '*.md'` 檢查輸出，
  此檢查也在容器內執行。檢查並移除本次不再需要的容器；不清理其他專案資源。
- 原版 EXE、資料、壓縮檔、掃描、存檔、擷取資產及權利未明的 HD 素材不入 Git。
  private 不代表已取得素材散布權。先設定 `.gitignore`，再檢查 staged 內容與素材清單。
  第 1 節已獲使用者指定的 README 截圖為有限例外；原始收據仍只留本機。
- 自有程式與文件依指定 RRSAL-1.0 範本建立 `LICENSE`，保留第三方元件授權。
  未確認的原版權利人與素材來源不得猜填。
- 正式交付根為 `dist-all/<版本>/`；子目錄依第 3 節唯一契約建立。
  完整版僅留本機；可散布包排除未授權素材。本次未授權公開發布。
- 正式版號為 `v.<主版>.<次版>.<修訂版>-YYYYMMDD`，發行日期採 Asia/Taipei。
  先完成提交再打 tag、打包；tag、程式、封包與 manifest 同版。已發布 tag 不移動或覆寫。

## 8. 共同決策

- 使用者已決定 dosgolem 重打包、HD 版本、私人儲存庫與 Issue 先行，不重複詢問。
- HD 美術與操作取捨先展示本作可並列原型。依第 3 節 `grilling` 入口，
  每次只提出目前最早會阻塞的決定，取得確認後再寫 READY 規格。
- 實質改變規則、存檔格式、原版忠實度、版面、平台範圍或散布方式時先確認。
  可由 bytes、現行程式、規格或測試查出的事實自行查證。
- 已授權範圍內的讀取、測試、明確實作與可逆修正自主執行，不為普通「繼續」重開訪談。

## 9. 現況入口

目前狀態只保存於 [CONTEXT.md](CONTEXT.md)，工作歷程見 [WORKLOG.md](WORKLOG.md)。
