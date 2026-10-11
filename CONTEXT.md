# 模擬台北：目前現況

核對日期：2026-10-11。目標是完成原版與 dosgolem 整合，並提供 HD 呈現。

使用者已指示恢復工作，繼續整合與驗收。

## 有效決策

- 私人儲存庫：[wicanr2/taipei](https://github.com/wicanr2/taipei)。Issues 已啟用。
- 使用者已授權主機 gh、專案提交與推送，以及本範圍的 Issue 管理。
- 使用者指定所有工作區放在本專案的 `workspace/`。原始輸入保留原位並唯讀使用。
- 原版規則、EXE 與存檔格式保持原樣。
- HD 美術採 B「細緻手繪材質」，以使用者最新改選取代先前的 A。HD 解析度為 1280×800，對應原版 320×200 的四倍。
- 使用者選定 Windows、Linux、macOS 三平台封包，字型採 Noto 高清黑體。固定使用已展示的 Noto Sans CJK TC Regular Sans2.004；平台實機驗收另記限制。原版確有 F1–F6 標示，按鍵語意依原版驗證。
- 使用者確認「允許在遊戲中切換」，採已提出的 F12 即時切換原版／HD。切換只改呈現，保留目前遊戲狀態，不將 F12 送入 DOS。操作契約見 [014](docs/spec/014-live-theme-switch.md)。
- 使用者明確指定「重繪範圍 所有的圖片 與操作界面」。完整範圍涵蓋地圖／建物／設施、工具列／按鈕／框架、全部選單與視窗文字、圖表、開場／插畫／事件及動畫相位，沿用已定案風格與原版版面。

使用者已回覆「Noto 高清黑體」，[#18](https://github.com/wicanr2/taipei/issues/18) 的字型方向已定。已展示比較圖保存在本機 `workspace/prototypes/hd-style/font-comparison/comparison-fonts.png`，SHA-256 `2ec3eea917c9dc173b31e30b5dbd9042f4ff4fca3f0f62a978281a3db5708c28`；含原版畫面，依素材邊界不入 Git。固定字型 SHA-256 `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4`，授權為 SIL OFL 1.1。後續全部文字依已確認方向接入，不以六個標題原型宣稱全遊戲文字已 HD 化。

正式切換操作與完整重繪範圍已定案，不再等待相同決策。現有研究前端的 F12 已有正常 GUI 收據；正式接入依 #7 驗收。全部素材先盤點來源，再逐批建立 READY 規格及接入；未知來源回退仍列未完成，不能把局部地景與六個標題當成完整交付。

## 目前狀態表

| 項目 | 現況 | 證據或限制 |
|---|---|---|
| 私人儲存庫 | 已由主機 gh 回讀 PRIVATE，Issues 啟用 | 遠端原為空儲存庫 |
| 工作項目 | 初始 9 張 Issues 已建立 | 狀態只以 [遠端 Issues](https://github.com/wicanr2/taipei/issues) 為準 |
| 本機 Git | 沿用使用者建立的空 clone，管理資料移至專案根目錄 | 原 clone 只有 `.git`，沒有提交或其他檔案 |
| 原版輸入 | 35 個檔案、7,919,834 bytes；RAR 與逐檔 SHA-256 已保存 | [輸入基線](docs/re/001-input-baseline.md)；原版精確版本與權利人仍未知 |
| 啟動入口 | `模擬台北/RS201/RS201.EXE /A /D /x` | 兩個 EXE 同雜湊；批次檔與兩個 config 一致 |
| dosgolem 啟動 | 冷啟動到主選單與城市選擇通過，兩次主選單畫面及暫存器一致；新增 Caps Lock 補丁通過核心與硬體讀鍵測試 | [啟動基線](docs/re/002-dosgolem-startup.md)、[Caps Lock](docs/spec/007-bios-caps-lock.md)；補丁只在隔離副本與本專案保存 |
| 原版前端與存讀檔 | 正常 GUI 冷啟動、新遊戲、電線施工、檔名退格、原版存檔、離開與全新啟動讀檔通過；施工格讀回相同 | [#4](https://github.com/wicanr2/taipei/issues/4)、[前端契約](docs/spec/005-frontend-preview.md)；限已抽樣玩家路徑 |
| 即時音訊 | OPL2 節奏與旋律串流已接實際播放器；冷啟動 monitor 非靜音，延後聚焦及有界緩衝通過 | [音訊契約](docs/spec/009-opl2-audio.md)；硬體規格近似，尚未做人耳與平台真機確認 |
| HD 範圍 | 所有圖片與操作介面已定案；完整來源初盤為 118 個 ROM 成員、1317 筆圖片來源，保留別名與未知項；另取得 402 個中文字模及原始字碼 | [完整範圍](docs/spec/015-full-hd-scope.md)、[來源盤點](docs/re/008-full-asset-inventory.md)、[字模證據](docs/re/009-chinese-font-sources.md)；數量不代表全部重繪完成 |
| HD 接入 | 已接入 B 地景、六 Noto 標題、六功能下拉選單、十四工具、五工具子選單、說明與啟動選單、城市框架／F1–F6、底部費用／年月／資金，以及存讀檔視窗與離開提示。023 的 109 份正常收據、十八項有效負對照、施工存退讀與兩次退出通過；兩側各 26.88 億步、112 次明示 HD 抽樣原版狀態及實際存檔相同 | [檔案視窗契約](docs/spec/023-file-dialogs.md)、[城市選單](docs/spec/022-city-function-menus.md)；模態外、右下原符號、其他圖片、文字／圖表／視窗、場景及正式封包未完成 |
| 城市六功能選單 | 限六個完整下拉面板、二十九選取達 CONFORMED；完整來源、固定面板及區外、實際資源、正常 GUI、存退讀與原版狀態通過，四平台編譯通過 | [022](docs/spec/022-city-function-menus.md)、[#37](https://github.com/wicanr2/taipei/issues/37)；確認後的功能視窗及完整 HD 另驗 |
| 存讀檔與離開提示 HD | 023 限完整兩家族達 CONFORMED；243 份來源、729 項單像素、雙選取、十四項實際資源故障、109 份正常 GUI、十八項有效破壞與四個正對照通過。F12、正常施工存退讀、原版狀態與四架構通過 | [023](docs/spec/023-file-dialogs.md)、[#38](https://github.com/wicanr2/taipei/issues/38)；外部刪檔／損壞、儲存故障、模態外、其他視窗及正式封包未完成 |
| 預算與稅率視窗 | 025 經證據審查達 READY。43 份完整來源、172 項單像素、十八項選取負對照及 74 項實際 Noto 墨跡通過；Escape 保留調整，正常 F2 存讀恢復。災難台北正常取得四欄非零費用，六張原位原型完整核對，十檔乾淨重生逐 byte 相同 | [025](docs/spec/025-budget-panel.md)；尚未接入產品 HD，未達 CONFORMED；負淨額／規則極值未作正常玩家驗收 |
| 普通按鍵研究同步 | #41 的明示 ASCII 讀取與 release 確認已由正常災難台北開預算驗證；九鍵各讀一次，六個普通鍵及三個方向／功能鍵通過，保留片頭特殊入口 | [#41](https://github.com/wicanr2/taipei/issues/41)；`budget-native-source-ready/`；只改驗證工具，不改產品或遊戲速度 |
| 預算操作的時間缺口 | 024 限時間來源修正達 CONFORMED。#40 修正 DOS 時間從 raw PIT IRQ 改讀 BIOS 計數；四組受控反例轉綠，正常預算操作 41 份及完整 HD 施工存退讀 45 份通過，兩次原版退出。四架構編譯通過 | [024](docs/spec/024-dos-system-clock.md)；時間採既有整數近似，沒有新增真機或逐週期一致聲明 |
| 跨平台編譯 | 本批 Linux amd64、Windows amd64、macOS amd64／arm64 研究前端編譯與架構通過；Windows Wine 冷啟動至城市為先前產品的預檢結果 | 本批未重跑 Wine，macOS 未真機執行；編譯及結構檢查不等於封包或真機驗收 |
| 封包 | 尚未建立 | 不宣稱正式 HD 完成或跨平台封包已驗 |

## 文件入口

- 預算完整面板契約：[025](docs/spec/025-budget-panel.md)，已審查完整來源、動態數值、轉錄、非零費用及正常控制，達 READY；正式呈現尚未接入。
- 預算離線原型：[budget-prototype](workspace/app/cmd/budget-prototype/main.go)，只讀本機來源與轉錄，沿用固定 B／Noto 產生完整底板、數字字形及原位比較；輸出 `workspace/prototypes/hd-style/budget-v1/`。正式呈現仍未接入。
- 預算原型獨立核對：[budget_prototype_check.py](workspace/tools/budget_prototype_check.py)，重讀 ROM、轉錄原框與 PNG alpha，核對靜態／數字墨跡、安全矩形、完整原位組合及全部區外；輸出 `workspace/runs/budget-source/prototype-check.json`。不當作正式 HD 收據。
- 預算讀鍵同步：[city_menu_playtest.py](workspace/tools/city_menu_playtest.py) 的 `action(..., acknowledge=True)` 只對已查證普通鍵等待實際 Key 與 release；預設片頭流程不強加 DOS 讀鍵。有限步數啟動使用 `wait_for(..., progress=True)`，仍由各 shell 的外層逾時擁有。#41 的正常入口與逐鍵收據已通過。
- 預算 READY 證據：`workspace/runs/budget-source/ready-model/catalog.json`、`ready-provenance.json`、`prototype-check.json`；43 份來源、172 項單點、十八項選取負對照、74 墨跡、六張原位圖及十檔重生通過。正式 manifest SHA-256 `f6a3052430ad3cc1cda5c737fb21ce6c73c13237e191e29cf0c92684553b9933`。研究收尾記錄 `final-hygiene.json`，完整正式 HD 另驗。
- 預算研究審查來源：`workspace/runs/budget-source/review-model/catalog.json` 含 42 份完整來源、168 項單像素，初批 33 份原件不覆寫。`budget-native-ranges/result.json` 是未還原調整及實際 F2 存讀研究，名稱不代表完成規則極值測試。存檔 `budget-saves.rnp1jg5l/BUDGET39.SAV` SHA-256 `442981026373f69080668ad176335949636635c407ba5b14cbf4f2ce7265b430`。
- DOS 時間收尾：`workspace/runs/dos-clock-source/final-hygiene.json` 保存本批文件入口、相對連結、語法、格式、擁有權、容器內指定 find 與 Linux 重建比較；Docker 生命週期另由主機回讀。本批不建立正式交付目錄。
- DOS 時間證據彙整：[dos_clock_provenance.py](workspace/tools/dos_clock_provenance.py)，已核對本批原始輸入、固定七補丁、四架構、86 份正常收據、施工存退讀、兩次退出及獨立畫面檢查；輸出 `workspace/runs/dos-clock-source/provenance.json`。現行 Linux SHA-256 `52b65f10bd009c0f94741eaaa1aa36d0349342dbea646453bb9eff7ce9c40b8f`；舊四架構與來源收據保留 `before-build/`。
- DOS 時間測試：[dos_clock_verify.sh](workspace/tools/dos_clock_verify.sh)，先由現行建置入口重生七補丁，再執行 DOS、狀態、oracle、probe 與實際 HD 素材測試；輸出 `workspace/runs/dos-clock-source/`，正式正常 GUI 與封包不由此代替。
- DOS 時間修正補丁：[dosgolem-system-clock.patch](workspace/tools/dosgolem-system-clock.patch)，固定基底及原六補丁後套用的第七份補丁；沿用既有 Go image 與 [build_preview.sh](workspace/tools/build_preview.sh)。正常 GUI 由 `TAIPEI_THEME=hd-b TAIPEI_GUI_RUN=gui-dos-clock-cold bash workspace/tools/gui_playtest.sh` 驗證，拒絕覆寫既有收據。
- DOS 時間契約：[024](docs/spec/024-dos-system-clock.md)，#40 的公開平台前提、時間來源及驗證閘門。研究輸出 `workspace/runs/dos-clock-source/`，保留未修版本四組紅測試及固定 commit 的平台全文；新產品正常操作及存退讀已通過。
- 預算字形來源候選：`workspace/runs/budget-source/static-glyph-candidates.json`、`rom2-x4.png`，保留 ROM2 背景與原字模的精確匹配及別名；沒有 ROM57 精確對應的烘製文字已固定原框目視轉錄，不宣稱取得原版字碼。
- 預算輸入定位：[ida_budget_probe.py](workspace/tools/ida_budget_probe.py)，以 IDA Pro 9.4 及唯讀既有資料庫的複本匯出窄範圍函式；輸出 `workspace/runs/ida-39/`，保留原始名稱、bytes、IDA 線性位址與 EXE 檔案偏移。
- 預算正常入口研究：[budget_playtest.sh](workspace/tools/budget_playtest.sh)、[budget_playtest.py](workspace/tools/budget_playtest.py)，從正常冷啟動經 F3 預算選項探索數值、選取及返回；有界停止不取代原版退出。
- 預算完整來源研究：[budget_catalog.py](workspace/tools/budget_catalog.py)，ROM2 在 `(18,37)` 的 235×132 背景及十一個 ASCII 動態欄位。來源及轉錄經 025 READY 審查，正式呈現尚未接入產品。
- 預算與稅率來源：[#39](https://github.com/wicanr2/taipei/issues/39)，本機 `workspace/runs/budget-source/full-model/catalog.json` 保存 33 份完整來源與 132 項單像素負對照；ROM2 檔案偏移 12662，解碼 SHA-256 `db92d35996a6c8fc112d129ab0a92d1018384495cd38b31d637df468b52c7967`，原位 `(18,37,235,132)`，標題位於局部 y=1。正常操作 `budget-native-fixed/result.json` 含五列選取與原版 Right 減一／Left 還原；兩個未修時鐘前件保留。初始線索仍在 `initial-sources.json` 與 `initial-candidates.json`。原版素材不入 Git，來源符合不等於 HD 已接入。
- 檔案視窗正式呈現：[file_dialogs.go](workspace/app/internal/hd/file_dialogs.go)，依 023 完整來源與使用中色盤辨識，接入固定 B／Noto；限本批達 CONFORMED。
- 檔案視窗實際素材測試：[file_dialogs_test.go](workspace/app/internal/hd/file_dialogs_test.go)，核對 243 筆完整來源、整框與區外、色盤及真實素材故障。
- 檔案視窗獨立 Go 收據核對：[files.go](workspace/app/cmd/receipt-check/files.go)，`receipt-check -file-reference <素材根> -original <原版目錄>`；重建完整來源與動態文字，不引用產品呈現器。
- 檔案視窗 HD 正常操作：[file_dialog_hd_playtest.sh](workspace/tools/file_dialog_hd_playtest.sh)、[file_dialog_hd_playtest.py](workspace/tools/file_dialog_hd_playtest.py)，固定 Docker 冷啟動、編輯、清單捲動、空白、覆寫、取消與兩家族 F12；有界停止，原版退出另驗。
- 檔案視窗有效負對照：[hd_file_dialogs_negative.py](workspace/tools/hd_file_dialogs_negative.py)，重算 PNG 與雜湊後測試來源、色盤、墨跡、背景、區外及中繼資料；包含未使用色盤正對照。
- 檔案視窗整批驗證：[file_dialogs_verify.sh](workspace/tools/file_dialogs_verify.sh)、[file_dialogs_provenance.py](workspace/tools/file_dialogs_provenance.py) 通過 109 份正常收據、施工存退讀、兩次退出、四架構與原始輸入核對。`presentation-audit -require-file-dialogs` 使用真實獨立 scratch，另回對正常 GUI 畫面、色盤、讀鍵、檔案操作及落地存檔；兩側各 2,688,000,000 步、112 次預登記抽樣，含檔案六次、離開三次，狀態相同，SHA-256 `f55713cac7d97ff24ed9b8e4b21590a65cd254890efd7d926a23129f0a07bf0e`。證據為 `workspace/runs/file-dialogs-state-audit.json`、`file-dialogs-state-provenance.json` 及 `file-dialogs-verification.log`。
- 檔案視窗離線原型：[file-dialog-prototype](workspace/app/cmd/file-dialog-prototype/main.go)，固定 Noto、既有 B 面板與來源字碼，產生 95 ASCII 雙色及八個中文墨跡、原位空白面板與離開提示。用於本機素材重生；正式呈現由 `file_dialogs.go` 載入固定結果。
- 檔案視窗契約：[023](docs/spec/023-file-dialogs.md)，限本批達 CONFORMED；完整來源、正常操作、素材、失配隔離及正式驗證通過。
- 檔案視窗獨立檢查：[hd_file_dialogs_check.py](workspace/tools/hd_file_dialogs_check.py)，從 ROM 重建完整來源與使用中色盤，核對固定 PNG、動態字形、整框、全部區外及 198 個字形墨跡。由 `hd_scroll_check.py` 共用，53 份檔案／提示收據含原版主題往返均通過。
- 檔案視窗收尾證據：`workspace/runs/file-dialogs-final-hygiene.json`，364 個相對連結、八個新入口與既有入口正對照、語法、格式、1000:1000 及指定 find 通過。Linux 從現行來源重建逐 byte 相同；本批容器均退出刪除，無新 image。正式 GUI 存檔在 `gui-cold-saves.EVJvVc/`，原始 35 檔與 RAR 保持基準。
- 檔名正常輸入核對：[file_dialog_inputs_check.py](workspace/tools/file_dialog_inputs_check.py)，回讀九十四字元、原版讀鍵、退格、八／九字元、取消與空清單確認；完整收據和色盤參考留本機。
- 存讀檔與離開確認來源：[#38](https://github.com/wicanr2/taipei/issues/38)，[file_dialog_catalog.py](workspace/tools/file_dialog_catalog.py) 重建 ROM3 完整檔案視窗、八列 ASCII 字模及 ROM1 底部離開提示，審查結果 `workspace/runs/file-dialog-source-ready/catalog.json`。首批八份原型輸入另留 `file-dialog-source/catalog.json`，未覆寫前批正常 GUI。
- 檔案視窗正常探索：[file_dialog_playtest.sh](workspace/tools/file_dialog_playtest.sh)、[file_dialog_playtest.py](workspace/tools/file_dialog_playtest.py)，從正常冷啟動查實際檔名字集、長度、退格、空清單、分頁、取消與離開選否；輸出 `workspace/runs/file-dialogs-native/`。只作來源探索，有界停止不代替原版退出驗收。
- 城市六功能正式驗證：[city_menu_hd_playtest.py](workspace/tools/city_menu_hd_playtest.py)，由既有 shell 入口指定 `TAIPEI_THEME=hd-b TAIPEI_CITY_MENU_RUN=city-menus-hd`，一次正常冷啟動遍歷二十九選取及六場景 F12，107 份收據通過。實際資源測試為 [city_panels_test.go](workspace/app/internal/hd/city_panels_test.go)，共用五工具的完整來源、區外及故障隔離斷言，全套 21.819 秒無跳過。
- 城市面板獨立核對：[hd_city_panels_check.py](workspace/tools/hd_city_panels_check.py)，驗二十九選取、六場景 F12、來源、固定 PNG 與所有區外像素；有效負對照沿用 [hd_tool_panels_negative.py](workspace/tools/hd_tool_panels_negative.py) 的 `--family city`，逐項更新受影響雜湊與原版 PNG。
- 城市面板整批核對：[city_panels_verify.sh](workspace/tools/city_panels_verify.sh)，144 份正常收據、大小面板十四項有效負對照、標題／工具冷讀通過；兩側完整 5,184,000,000 步，216 次明示 24,000,000 步抽樣含二十九城市選取共 164 次、說明一次及城市各層 14 次。狀態相同，SHA-256 `df85c5d5f612ff996d7b671bd81ba1238e41e55bff926dc293c90975ece21174`；結果為 `workspace/runs/city-panels-state-audit.json`，過程在 `city-panels-verification.log`，非逐幀對拍。
- 城市面板證據彙整：[city_panels_provenance.py](workspace/tools/city_panels_provenance.py)，以唯讀 `/project` 核對原始 35 檔及 RAR，記錄四平台架構、程式／工具／來源／素材雜湊、全部正常收據與明示抽樣結果至 `workspace/runs/city-panels-state-provenance.json`。只彙整實際通過結果，不改原始收據。
- 本批 GUI 保留來源：五工具 021 的完整 37 份存退讀收據移存 `workspace/runs/gui-cold-before-city-menus/`，原件保留；現行 `workspace/runs/gui-cold/` 已由 022 產品重新冷啟動，37 份收據及兩次原版退出通過，存檔基準不變。六功能獨立正常 HD 收據為 `workspace/runs/city-menus-hd/`。本批入口、格式、連結及擁有權見 `workspace/runs/city-panels-final-hygiene.json`。
- 城市六功能入口研究：[#37](https://github.com/wicanr2/taipei/issues/37)，[city_menu_playtest.sh](workspace/tools/city_menu_playtest.sh)、[city_menu_playtest.py](workspace/tools/city_menu_playtest.py)。正常冷啟動 F1–F6、全部二十九選取、邊界與取消通過，原版來源在 `workspace/runs/city-menus-native/` 及 `city-menus-native-extra/`；此探索有界停止不當作原版退出，產品另以完整存退讀驗證。
- 城市功能完整來源：[city_menu_catalog.py](workspace/tools/city_menu_catalog.py)，重建完整交錯邊框、背景及 ROM56／57／58 原字模；只接受正常完整矩形，原文與衍生 layout 留在本機，不由未知字形猜補。
- 城市功能原版控制核對：[city_menu_source_check.py](workspace/tools/city_menu_source_check.py)，固定完整來源 SHA-256，驗二十九種選取、上下循環、左右跨選單及循環邊界、六入口 Escape 復原與八十二次讀鍵／release。
- 城市功能離線組合沿用 [tool-panel-prototype](workspace/app/cmd/tool-panel-prototype/main.go)，`-family city -state-count <已審查數量>` 指定城市來源；既有預設仍為五工具十八狀態。僅生成本機比較原型，來源與實際墨跡審查前不接入產品。
- 城市六功能選單契約：[022-city-function-menus.md](docs/spec/022-city-function-menus.md)，限二十九選取達 CONFORMED。137 份來源、246 個來源破壞、599 項實際墨跡、三十一檔重生及原版控制核對通過；原文及固定素材在本機 `workspace/prototypes/hd-style/city-menus-v1/`，來源階段雜湊在 `workspace/runs/city-menu-source/`。產品及完整正常驗證見上述本批證據，其他功能視窗未完成。

- 呈現狀態稽核抽樣：[#36](https://github.com/wicanr2/taipei/issues/36)，[presentation-audit](workspace/app/cmd/presentation-audit/main.go) 的 `-render-interval-steps` 預設仍為 400,000；本批預登記 24,000,000，完整執行兩側原版步數並要求十八工具狀態，輸出抽樣數與階段時間。來源保存在 `workspace/runs/tool-panels-state-provenance.json`，先前逾時來源另存 `tool-panels-state-provenance-before-sampling.json`。
- 五工具同狀態結果：`workspace/runs/tool-panels-state-audit.json`，兩側各 4,080,000,000 步、170 次抽樣，十八工具狀態共 99 次及既有呈現層全部涵蓋，原版狀態相同；SHA-256 `53700f59970623a9e83a648b7b4b1eeb080126c6d8b45eccff7e0df4cf9394a1`。執行命令、輸入、來源與工具雜湊見 provenance。原始檔、RAR、四平台產品雜湊與架構核對見 `workspace/runs/tool-panels-input-hygiene.json`；入口、連結、格式、擁有權與容器內檔案檢查見 `tool-panels-final-hygiene.json`。

- 完整 GUI 執行預算：[#35](https://github.com/wicanr2/taipei/issues/35)，外層上限改為 600 秒，同產品與 image 乾淨重跑，保留全部原版操作及斷言，37 份收據與兩次原版退出通過；逾時收據保留 `workspace/runs/gui-cold-tool-panels-timeout/`，正常腳本仍為 [gui_playtest.sh](workspace/tools/gui_playtest.sh)。

- 五工具有效負對照：[hd_tool_panels_negative.py](workspace/tools/hd_tool_panels_negative.py)，修改文字、背景、區外、來源、色盤、選取與 ID，重算受影響雜湊及原版 PNG，分別要求 Python 來源與 Go 固定參考核對器拒絕。

- 五工具實際資源測試：[tool_panels_test.go](workspace/app/internal/hd/tool_panels_test.go)，十八個完整正常來源、實際面板及區外，來源／色盤／模式／主題、必要檔案缺失或竄改與故障範圍。
- 五工具正常驗證：[hd_tool_panels_check.py](workspace/tools/hd_tool_panels_check.py)，共用完整來源、固定參考及區外核對，另驗十八狀態、原版循環、左右／Escape、確認返回及五場景 F12。

- 五工具離線面板：[tool-panel-prototype](workspace/app/cmd/tool-panel-prototype/main.go)，依已審查完整來源、Noto 與既有 B 素材組合，逐字驗實際墨跡；完整來源及固定面板接入 [panels.go](workspace/app/internal/hd/panels.go)。
- 工具面板獨立驗證沿用 [hd_panels_check.py](workspace/tools/hd_panels_check.py) 完整來源／色盤與區外核對；[receipt-check](workspace/app/cmd/receipt-check/main.go) 新增 `-tool-panel-manifest`；[presentation-audit](workspace/app/cmd/presentation-audit/main.go) 新增 `-require-tool-panels`，十八狀態與啟動十三狀態分開計數。

- 五工具子選單批次：[021-tool-submenus.md](docs/spec/021-tool-submenus.md)，對應 #31，限十八個完整選取狀態達 CONFORMED；原始來源、462 項 Noto 墨跡、119 份正常 HD 收據與明示抽樣狀態對照通過。
- 五工具完整來源：[tool_submenu_catalog.py](workspace/tools/tool_submenu_catalog.py)，以固定 ROM19、57／58 與完整小選單背景重建，輸出本機 layout、來源及負對照；原文衍生資料不入 Git。

- 五工具子選單正常來源：[tool_submenu_playtest.sh](workspace/tools/tool_submenu_playtest.sh)、[tool_submenu_playtest.py](workspace/tools/tool_submenu_playtest.py)，對應 #31，逐次確認原版讀鍵，遍歷全部選取、邊界、Escape 與 F12；輸出 `workspace/runs/tool-submenus-native/` 或 `tool-submenus-hd/`。

- 底部動態文字批次：[020-city-footer.md](docs/spec/020-city-footer.md)，對應 #31，限費用、年月與資金達 CONFORMED；103 份正常收據、八項有效負對照與 3,236 幀同狀態覆繪通過，右下原符號及其他介面仍未完成。
- 底部欄位來源：[footer_catalog.py](workspace/tools/footer_catalog.py)，由 ROM1／56／57／58 重建整個矩形，保存正常字串及單點破壞負對照；輸出 `workspace/runs/footer-source/catalog.json`。
- 底部固定字形：[footer-prototype](workspace/app/cmd/footer-prototype/main.go)，離線繪製十八個 Noto 字形並檢查實際墨跡；輸出本機 `workspace/prototypes/hd-style/footer-v1/`，不入 Git。
- 底部欄位接入：[footer.go](workspace/app/internal/hd/footer.go)，依 020 重建完整欄位、分欄核對色盤、固定字形與背景，失配整欄回退；正常工具、時間、施工及冷讀已抽樣。
- 底部獨立核對：[hd_footer_check.py](workspace/tools/hd_footer_check.py)，從固定 ROM 重新辨字及完整回建，核對 Noto 字形、背景、原符號與回退；由共同正常收據核對入口呼叫。
- 底部單幀參考：[receipt-check/footer.go](workspace/app/cmd/receipt-check/footer.go)，`-footer-reference` 指向本機素材根，按收據字串與固定 atlas 核對整欄及原版區外；來源與字串由 Python 另行重算。
- 底部來源與失配測試：[footer_test.go](workspace/app/internal/hd/footer_test.go)，正常字模、整欄負對照、獨立色盤回退、缺失／竄改素材及縮短數字背景恢復。
- 底部有效負對照：[hd_footer_negative.py](workspace/tools/hd_footer_negative.py)，重算受影響雜湊及原版 PNG，分別驗字形、背景、原符號、區外、來源、色盤、遮罩及字串。
- 底部同狀態收據：`workspace/runs/footer-state-audit.json`、`footer-state-provenance.json`；相同唯一正常輸入兩側各 2,352,000,000 步，3,236 幀底部覆繪，原版狀態相同。020 正常 GUI 為 `footer-gui/` 與 `gui-cold-before-tools/`，來源前件保留 `gui-cold-before-footer/`。
- 連續方向鍵驗證修正：[gui_playtest.py](workspace/tools/gui_playtest.py)，依 [#34](https://github.com/wicanr2/taipei/issues/34) 逐次確認 25 次原版讀鍵及前端 release；不注入狀態。初次漏鍵證據 `gui-cold-footer-missed-input/`、修正後 `gui-cold/movement-sync.json`。

- 城市框架批次：[019-city-chrome.md](docs/spec/019-city-chrome.md)，對應 #29，限六部分與十四外框達 CONFORMED；63 份十四工具與 37 份存退讀收據通過，其餘介面與封包仍未完成。
- 城市框架載入與遮罩：[chrome.go](workspace/app/internal/hd/chrome.go)，依 019 已審查的六部分及十四外框逐項辨識、失配回退；正式封包另驗。
- 框架獨立核對：[hd_chrome_check.py](workspace/tools/hd_chrome_check.py)，重算六部分、42 種工具外框來源與使用中色盤，核對固定參考及失配回退。
- 單幀框架參考核對：[receipt-check/chrome.go](workspace/app/cmd/receipt-check/chrome.go)，`-chrome-reference` 指向本機 `city-chrome-v1/`，逐像素檢查固定參考及原版區外。
- 框架實際來源測試：[chrome_test.go](workspace/app/internal/hd/chrome_test.go)，驗十四工具 42 狀態、子選單及缺素材／字型、來源與色盤失配。
- 框架有效負對照：[hd_chrome_negative.py](workspace/tools/hd_chrome_negative.py)，重算雜湊與原版 PNG 後，驗框架、F 鍵、外框、動態欄位、來源、色盤與偽造遮罩。
- 框架同狀態收據：`workspace/runs/chrome-state-audit.json` 與 `chrome-state-provenance.json`。正常 GUI 唯一鍵盤輸入、固定 EXE／dosgolem／虛擬時間兩側各 2,304,000,000 步，包含 3,113 幀完整框架；原版 RAM、CPU、畫面、色盤、埠、OPL、讀鍵與檔案操作相同。唯讀輸入為 `city-chrome-before-cache/theme-hd-capture.zip`，不以不同 GUI 即時時序猜測精確對拍。
- 城市框架離線組合：[chrome-prototype](workspace/app/cmd/chrome-prototype/main.go)，固定生成素材及 Noto；本機提示與來源記錄為 `workspace/prototypes/hd-style/city-chrome-generation.json`，完整參考輸出為 `city-chrome-v1/`，正式辨識範圍依 019。
- 框架及外框來源盤點：[city_chrome_catalog.py](workspace/tools/city_chrome_catalog.py)，本機輸出 `workspace/runs/city-chrome/catalog.json`，未審查候選不接入產品。
- 框架正常 GUI：[city_chrome_playtest.sh](workspace/tools/city_chrome_playtest.sh)、[city_chrome_playtest.py](workspace/tools/city_chrome_playtest.py)，十四工具依原版方向選取、確認及 Tab 取消。

- 啟動選單完整面板載入：[panels.go](workspace/app/internal/hd/panels.go)，契約見 [018](docs/spec/018-startup-menus.md)。本機生成提示為 `workspace/prototypes/hd-style/startup-menu-generation.json`。
- 啟動面板獨立核對：[hd_panels_check.py](workspace/tools/hd_panels_check.py)，驗完整來源、固定參考及區外，不免驗面板區域；負對照見 [hd_panels_negative.py](workspace/tools/hd_panels_negative.py)。
- 啟動面板實際資源測試：[panels_test.go](workspace/app/internal/hd/panels_test.go)，使用正常 GUI 的十三種來源及失配條件。
- 啟動面板同狀態結果：`workspace/runs/panels-state-audit.json`，相同正常輸入兩側各 1,776,000,000 步，十三種選單及完整原版狀態相同；來源與執行檔雜湊見 `panels-state-provenance.txt`。本批未驗其他分支或正式封包。
- 啟動選單正常 GUI：[startup_menu_playtest.sh](workspace/tools/startup_menu_playtest.sh)、[startup_menu_playtest.py](workspace/tools/startup_menu_playtest.py)，對應 #31，驗十三種選取、三場景 F12、無效鍵與原版取消語意。
- 啟動選單契約：[docs/spec/018-startup-menus.md](docs/spec/018-startup-menus.md)，對應 #31，完整三選單與十三個選取狀態。
- 啟動選單來源審查：[startup_menu_catalog.py](workspace/tools/startup_menu_catalog.py)，從固定底圖逐點核對正常選取畫面與原文字模。
- 啟動選單離線工具：[startup-panel-prototype](workspace/app/cmd/startup-panel-prototype/main.go)，依固定 Noto、來源及素材輸出完整面板，掃描 240 個實際墨跡；執行時只接受 018 審查的固定面板。
- 新遊戲說明視窗：[docs/spec/017-new-game-dialog.md](docs/spec/017-new-game-dialog.md)，對應 #31，完整來源辨識、B 底板、Noto 原文與回退契約。
- 說明視窗呈現與失配測試：[dialog.go](workspace/app/internal/hd/dialog.go)、[dialog_test.go](workspace/app/internal/hd/dialog_test.go)。
- 說明視窗獨立核對：[hd_dialog_check.py](workspace/tools/hd_dialog_check.py)，重算完整來源並核對固定面板與區外像素。
- 說明視窗負對照：[hd_dialog_negative.py](workspace/tools/hd_dialog_negative.py)，檢查改寫像素與同步更新雜湊仍被拒絕。
- 規則：[AGENTS.md](AGENTS.md)。
- 唯一工作狀態：[GitHub Issues](https://github.com/wicanr2/taipei/issues)。
- 驗收：[docs/verification-matrix.md](docs/verification-matrix.md)。
- 歷程：[WORKLOG.md](WORKLOG.md)。
- 原始輸入：[docs/re/001-input-baseline.md](docs/re/001-input-baseline.md)。
- 啟動與鍵盤：[docs/re/002-dosgolem-startup.md](docs/re/002-dosgolem-startup.md)。
- 可重現探針：[workspace/tools/probe.sh](workspace/tools/probe.sh)。
- BIOS 鍵盤路由：[docs/spec/001-bios-keyboard-routing.md](docs/spec/001-bios-keyboard-routing.md)。
- BIOS 等待模式：[docs/spec/002-blocking-bios-input.md](docs/spec/002-blocking-bios-input.md)。
- DOS 原生輸入：[docs/spec/003-console-keyboard-input.md](docs/spec/003-console-keyboard-input.md)。
- 探針紀錄：[docs/spec/004-probe-trace-memory.md](docs/spec/004-probe-trace-memory.md)。
- GUI 研究原型：[docs/spec/005-frontend-preview.md](docs/spec/005-frontend-preview.md)。
- 有序文字輸入：[docs/spec/006-ordered-text-input.md](docs/spec/006-ordered-text-input.md)，對應 [#14](https://github.com/wicanr2/taipei/issues/14)。
- BIOS Caps Lock：[docs/spec/007-bios-caps-lock.md](docs/spec/007-bios-caps-lock.md)，對應 [#15](https://github.com/wicanr2/taipei/issues/15)。
- 原型程式：[workspace/app/cmd/taipei-preview/main.go](workspace/app/cmd/taipei-preview/main.go)。
- 原型建置：[workspace/tools/build_preview.sh](workspace/tools/build_preview.sh)，第一次可用 `--download` 下載鎖定依賴。
- GUI 冷啟動驗證：[workspace/tools/gui_playtest.sh](workspace/tools/gui_playtest.sh)。
- GUI 操作診斷：[workspace/tools/gui_explore.sh](workspace/tools/gui_explore.sh)，只供快照探索。
- ROM 來源盤點：[workspace/tools/rom_catalog.py](workspace/tools/rom_catalog.py)。
- HD 圖塊證據：[docs/re/003-rom-graphics.md](docs/re/003-rom-graphics.md)。
- B 風格材質原型：[docs/spec/008-hd-material-prototype.md](docs/spec/008-hd-material-prototype.md)，離線程式為 [hd-prototype](workspace/app/cmd/hd-prototype/main.go)。
- 原型重生與負對照：[workspace/tools/hd_prototype.sh](workspace/tools/hd_prototype.sh)，驗證程式為 [hd_prototype_check.py](workspace/tools/hd_prototype_check.py)。
- 中文字型比較：[workspace/app/cmd/font-prototype/main.go](workspace/app/cmd/font-prototype/main.go)，限 [#18](https://github.com/wicanr2/taipei/issues/18) 離線原型。
- 字型原型重生：[workspace/tools/font_prototype.sh](workspace/tools/font_prototype.sh)，固定版本來源檢查為 [font_source.py](workspace/tools/font_source.py)。
- 工具列輸入研究：[GitHub #19](https://github.com/wicanr2/taipei/issues/19)，IDA 工具探針為 [ida_input_probe.py](workspace/tools/ida_input_probe.py)。
- 原始輸入定位匯出：[ida_input_sites.py](workspace/tools/ida_input_sites.py)，保留 IDA 位址與獨立檔案偏移，不附猜測性名稱。
- 原版即時音訊事件盤點：[workspace/tools/audio_audit.go](workspace/tools/audio_audit.go)，限 [#17](https://github.com/wicanr2/taipei/issues/17) 的有界研究。
- OPL2 節奏模式原型：[workspace/tools/ymfm_render.cpp](workspace/tools/ymfm_render.cpp)，依 [#20](https://github.com/wicanr2/taipei/issues/20) 使用固定外部 YMFM 核心，只供研究。
- 原版工具列與施工證據：[docs/re/004-native-controls.md](docs/re/004-native-controls.md)，冷啟動施工圖塊已驗存退讀。
- 音訊契約：[docs/spec/009-opl2-audio.md](docs/spec/009-opl2-audio.md)，Windows 工具鏈擴充來源：[Dockerfile.windows-audio](workspace/tools/Dockerfile.windows-audio)。
- 原版音訊分段驗證：[audio_stream_audit.go](workspace/tools/audio_stream_audit.go)，使用受版控補丁重建的 dosgolem 音訊套件，兩種批次 PCM 必須相同。
- GUI 單幀收據：[receipt-check](workspace/app/cmd/receipt-check/main.go)，依 [#21](https://github.com/wicanr2/taipei/issues/21) 核對原子封裝內的 PNG、色號與色盤。
- HD 遮擋與色盤條件研究：[hd_gate_audit.py](workspace/tools/hd_gate_audit.py)，限 [#5](https://github.com/wicanr2/taipei/issues/5) 的實際收據與離線負對照。
- 動態 HD 比較原型：[docs/spec/010-hd-live-prototype.md](docs/spec/010-hd-live-prototype.md)，限研究前端；字型、F12 與完整重繪範圍已定，各素材批次另驗。
- 原版音訊播放器驗證：[audio_playtest.sh](workspace/tools/audio_playtest.sh)、[audio_playtest_check.py](workspace/tools/audio_playtest_check.py)，使用隔離 PulseAudio monitor 擷取，技術確認與人耳確認分開。
- 原版音訊前端：[sound/session.go](workspace/app/internal/sound/session.go)，對應 `009-opl2-audio.md` 的技術驗證範圍；通用後端保存在 [dosgolem-audio.patch](workspace/tools/dosgolem-audio.patch)。
- 研究前端跨平台編譯：[build_preview_cross.sh](workspace/tools/build_preview_cross.sh)，先執行原型建置，再指定 `windows` 或 `macos`；編譯結果不等於封包驗收。
- 原版音訊狀態對照：[audio_state_audit.go](workspace/tools/audio_state_audit.go)，固定原始 EXE、步數與鍵盤輸入，核對消費音訊前後的 RAM、CPU、色盤、畫面與晶片暫存器。
- Windows 前端預檢：[wine_preview_playtest.sh](workspace/tools/wine_preview_playtest.sh)、[wine_preview_playtest.py](workspace/tools/wine_preview_playtest.py)，限 Wine 冷啟動至城市；非正式封包或真機驗收。
- 正常施工 HD 來源盤點：[hd_source_audit.py](workspace/tools/hd_source_audit.py)，依 [#22](https://github.com/wicanr2/taipei/issues/22) 保留全部相同圖塊來源別名及 ROM 檔案偏移，不猜建物語意。
- 正常施工 HD 來源證據：[docs/re/005-native-hd-sources.md](docs/re/005-native-hd-sources.md)，指出電線位於成員 39、圖像 45，與現行成員 59 地景批次分開。
- HD 捲動研究：[hd_scroll_playtest.sh](workspace/tools/hd_scroll_playtest.sh)、[hd_scroll_playtest.py](workspace/tools/hd_scroll_playtest.py)，依 [#23](https://github.com/wicanr2/taipei/issues/23) 走真實冷啟動及視窗按鍵；原型結果不作正式 HD 驗收。
- HD 捲動獨立核對：[hd_scroll_check.py](workspace/tools/hd_scroll_check.py)，比較完整原版圖塊位移、來源合格數與回退格實際像素，判定門檻先登記於 #23。
- 原版地圖原點：[docs/re/006-map-origin.md](docs/re/006-map-origin.md)，IDA 唯讀查詢入口為 [ida_camera_probe.sh](workspace/tools/ida_camera_probe.sh)、[ida_camera_probe.py](workspace/tools/ida_camera_probe.py)。
- 世界座標材質原型：[docs/spec/011-hd-world-origin-prototype.md](docs/spec/011-hd-world-origin-prototype.md)，限 [#24](https://github.com/wicanr2/taipei/issues/24) 的 DRAFT 修正。
- 呈現層狀態對照：[presentation-audit](workspace/app/cmd/presentation-audit/main.go)，重播正常 GUI 收據，比較有／無原點觀察及 HD 繪圖的原版狀態。
- 城市持續運行抽樣：[hd_runtime_playtest.sh](workspace/tools/hd_runtime_playtest.sh)、[hd_runtime_playtest.py](workspace/tools/hd_runtime_playtest.py)，對應 [#25](https://github.com/wicanr2/taipei/issues/25)，使用原版速度按鍵與固定虛擬步數擷取。
- 持續運行核對：[hd_runtime_check.py](workspace/tools/hd_runtime_check.py)，核對來源、原點、回退與相同地景像素；日期裁圖另作人工辨識，不以單純雜湊變化宣稱月份已推進。
- 城市持續運行證據：[docs/re/007-running-city.md](docs/re/007-running-city.md)，記錄正常月份推進、年度視窗修正與原版機器狀態比對。
- 年度預算視窗回退原型：[docs/spec/012-budget-window-prototype.md](docs/spec/012-budget-window-prototype.md)，依 [#26](https://github.com/wicanr2/taipei/issues/26) 的正常年度畫面證據修正整幀回退。
- Noto 主選單動態原型：[docs/spec/013-noto-menu-prototype.md](docs/spec/013-noto-menu-prototype.md)，依 [#27](https://github.com/wicanr2/taipei/issues/27) 接入使用者已選字型，限六個已辨識標題。
- Noto 實際像素核對：[hd_font_check.py](workspace/tools/hd_font_check.py)，對已展示字型參考逐像素比較，另驗文字回退及矩形外不變。
- Noto 收據負對照：[hd_font_negative.py](workspace/tools/hd_font_negative.py)，破壞文字或矩形間像素並同步更新呈現雜湊，要求核對器仍拒絕。
- 遊戲中主題切換：[docs/spec/014-live-theme-switch.md](docs/spec/014-live-theme-switch.md)，依 #6 使用者定案，READY 範圍只涵蓋 F12 呈現切換；正式前端與封包另驗。
- 完整圖片來源盤點：[workspace/tools/full_asset_catalog.py](workspace/tools/full_asset_catalog.py)，對應 [#28](https://github.com/wicanr2/taipei/issues/28)；全部 ROM 成員與候選圖片保留原始定位、來源別名與未知項。
- 完整 HD 範圍：[docs/spec/015-full-hd-scope.md](docs/spec/015-full-hd-scope.md)，使用者已確認所有圖片與操作介面，列出 #28–#32 批次及完整交付判準。
- 城市工具圖示：[docs/spec/016-city-tool-icons.md](docs/spec/016-city-tool-icons.md)，對應 #29，限十四個已證實來源的圖示內部；選取外框與互動範圍沿用原版。
- 工具圖示獨立核對：[hd_icons_check.py](workspace/tools/hd_icons_check.py)，從原版成員重算逐圖來源遮罩，核對固定 atlas 與選取外框。
- 完整素材盤點證據：[docs/re/008-full-asset-inventory.md](docs/re/008-full-asset-inventory.md)，記錄 118 成員、1317 圖片來源與 25 待分類成員，數量不當成全部重繪完成。
- 全中文字模盤點：[font_catalog.py](workspace/tools/font_catalog.py)，對應 #31，匯出固定 ROM 的字模、原始字碼與正常畫面候選；未審查字形語意不直接覆字。
- 中文字模證據：[docs/re/009-chinese-font-sources.md](docs/re/009-chinese-font-sources.md)，記錄字模定位、十二字正常畫面正對照、CP950 候選與尚未確認的語意。
- 原版文字呼叫端：[ida_text_probe.py](workspace/tools/ida_text_probe.py)，依 #31 在既有唯讀 IDA 9.4 資料庫的副本查原始字串、交叉參照與窄範圍函式，輸出留在 `workspace/runs/ida-31/`。
- 正常文字重播：[text-source-audit](workspace/app/cmd/text-source-audit/main.go)，依 #31 唯讀觀察正常輸入中的原版字串與字模呼叫，逐點核對原版繪製緩衝；不接入產品路徑。
