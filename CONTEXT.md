# 模擬台北：目前現況

核對日期：2026-10-12。目標是完成原版與 dosgolem 整合，並提供 HD 呈現。

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
| HD 接入 | 已接入 B 地景、六 Noto 標題、六功能下拉選單、十四工具、五工具子選單、說明與啟動選單、城市框架／F1–F6、底部費用／年月／資金、存讀檔與離開提示，以及完整預算面板。025 的 116 份正常收據、十三項有效呈現破壞、施工存退讀與兩次退出通過；兩側各 40.56 億步、169 次明示抽樣原版狀態及實際存檔相同 | [預算契約](docs/spec/025-budget-panel.md)、[檔案視窗](docs/spec/023-file-dialogs.md)；模態外、右下原符號、其他圖片、文字／圖表／視窗、場景及正式封包未完成 |
| 城市六功能選單 | 限六個完整下拉面板、二十九選取達 CONFORMED；完整來源、固定面板及區外、實際資源、正常 GUI、存退讀與原版狀態通過，四平台編譯通過 | [022](docs/spec/022-city-function-menus.md)、[#37](https://github.com/wicanr2/taipei/issues/37)；確認後的功能視窗及完整 HD 另驗 |
| 存讀檔與離開提示 HD | 023 限完整兩家族達 CONFORMED；243 份來源、729 項單像素、雙選取、十四項實際資源故障、109 份正常 GUI、十八項有效破壞與四個正對照通過。F12、正常施工存退讀、原版狀態與四架構通過 | [023](docs/spec/023-file-dialogs.md)、[#38](https://github.com/wicanr2/taipei/issues/38)；外部刪檔／損壞、儲存故障、模態外、其他視窗及正式封包未完成 |
| 預算與稅率視窗 | 025 限完整預算呈現達 CONFORMED。43 份來源、六張固定原型、233 項來源破壞、十二項真實資源故障及隔離通過。十七項 HD／鍵盤／原點測試無跳過；116 份正常收據、五列 F12、9／99 全新 EXE 讀回、十三項有效呈現破壞及 169 次原版狀態抽樣通過 | [025](docs/spec/025-budget-panel.md)；正常非零費用及淨額 -1 已抽樣，規則極值、其他介面與正式封包未完成 |
| 道路與電線 | 026 限第一批 25 張達 CONFORMED。固定整格、2025 項來源破壞、七張正常原位 140 格、162 項資源故障及十六張世界材質測圖通過；105 份正常 GUI、施工／F12／雙向捲動、兩次原版退出及全新 EXE 讀回通過。兩側各 49.44 億步、206 點原版狀態及實際 SAV 相同 | [026](docs/spec/026-infrastructure-tiles.md)、[#44](https://github.com/wicanr2/taipei/issues/44)；其餘 18 張候選仍 DRAFT。正常交通及密度入口未取得這些來源，不推導其用途；完整來源研究、全部 HD 與正式封包繼續 |
| 預算驗收工具 | #42 的 2400 秒整批上限與 #43 的正常冷讀後 0 鍵暫停，已由 `gui-budget-cold-r4/` 完整通過。施工格、資金 79980、預算 9／99、兩次原版退出及實際存檔通過；前件保留 | [#42](https://github.com/wicanr2/taipei/issues/42)、[#43](https://github.com/wicanr2/taipei/issues/43)；同一 binary、image 與遊戲時間，只修驗證條件 |
| 普通按鍵研究同步 | #41 的明示 ASCII 讀取與 release 確認已由正常災難台北開預算驗證；九鍵各讀一次，六個普通鍵及三個方向／功能鍵通過，保留片頭特殊入口 | [#41](https://github.com/wicanr2/taipei/issues/41)；`budget-native-source-ready/`；只改驗證工具，不改產品或遊戲速度 |
| 預算操作的時間缺口 | 024 限時間來源修正達 CONFORMED。#40 修正 DOS 時間從 raw PIT IRQ 改讀 BIOS 計數；四組受控反例轉綠，正常預算操作 41 份及完整 HD 施工存退讀 45 份通過，兩次原版退出。四架構編譯通過 | [024](docs/spec/024-dos-system-clock.md)；時間採既有整數近似，沒有新增真機或逐週期一致聲明 |
| 跨平台編譯 | 本批 Linux amd64、Windows amd64、macOS amd64／arm64 研究前端編譯與架構通過；Windows Wine 冷啟動至城市為先前產品的預檢結果 | 本批未重跑 Wine，macOS 未真機執行；編譯及結構檢查不等於封包或真機驗收 |
| 封包 | 尚未建立 | 不宣稱正式 HD 完成或跨平台封包已驗 |

## 文件入口

- 道路電線第一批資產：[infrastructure_assets.py](workspace/tools/infrastructure_assets.py) 從固定 v5 與正常來源盤點，產生 25 張本機呈現資產；完整 #44 範圍及其他 18 張候選仍繼續研究。輸出位於既有 `workspace/prototypes/hd-style/`，不加入 Git。
- 道路電線第一批呈現：[infrastructure.go](workspace/app/internal/hd/infrastructure.go) 依 026 只匹配 25 張完整來源、已用色盤與固定資產；限第一批達 CONFORMED。
- 道路電線第一批測試：[infrastructure_test.go](workspace/app/internal/hd/infrastructure_test.go) 核對固定 v5 像素、七種正常原位、2025 項來源破壞、實際資產故障及世界材質相位；正常 GUI 與狀態已另通過，正式封包未完成。
- 道路電線正常呈現核對：[hd_infrastructure_check.py](workspace/tools/hd_infrastructure_check.py) 直接解析唯讀 ROM，獨立重算整數幾何與 Fraction 色彩，核對正式 GUI 整格及收據；[hd_scroll_check.py](workspace/tools/hd_scroll_check.py) 同時核對所有回退格。
- 道路電線有效破壞：[hd_infrastructure_negative.py](workspace/tools/hd_infrastructure_negative.py) 重算來源、PNG 與所有受影響雜湊，驗正式整格、錯世界相位、改來源、回退格及計數；保留原件及兩個正對照。
- 道路電線正常生命周期：[infrastructure_gui.py](workspace/tools/infrastructure_gui.py) 透過既有 [gui_playtest.sh](workspace/tools/gui_playtest.sh) 的 `TAIPEI_TEST_INFRASTRUCTURE=1` 分支，追加道路、F12、水平／垂直捲動，沿原版流程存檔、退出、全新 EXE 冷讀；世界格轉換使用實際完成原點。
- 道路電線狀態驗證：[presentation-audit](workspace/app/cmd/presentation-audit/main.go) 的 `-require-infrastructure` 要求真正抽到道路與電線 HD，同步每個呈現抽樣點的原版狀態、最終正常 GUI 色號／色盤／讀鍵／檔案操作及實際 SAV。輸入產生後先回寫 #44 的 SHA-256 與步數，再執行正式重播。
- 道路電線第一批彙整：[infrastructure_provenance.py](workspace/tools/infrastructure_provenance.py) 核對固定素材、有效破壞、正常 GUI、四格道路及電線冷讀、兩次原版退出、雙向捲動、逐點原版狀態、落地 SAV、四架構與原始輸入雜湊；只涵蓋第一批 25 張。
- 道路電線正式證據：`workspace/runs/infrastructure-source/ready25-provenance.json` 彙整 105 份正常收據、水平五格及垂直四格同世界像素、五項有效呈現破壞與兩個正對照。唯一預登記輸入為 `gui-infrastructure-cold-r2/quit-file-theme-hd-capture.zip`，SHA-256 `f2fa0f50b268607eb9635bd631c007406d3f2282fbba356d10628ef698a97030`；兩側各 4,944,000,000 步，每 24,000,000 步共 206 點，95 點實際呈現道路／電線。狀態 SHA-256 `a8a5176dcf971de4376c4818b975dcb01b651825c8e8c728a9a64f6b08255e2f`；SAV 為 `c2aa48a46f1090262b367bd161d0b8a717374ec8a676170bd50283fcc4791a59`。這是明示抽樣，沒有外推其餘來源或全遊戲。
- 道路電線現行程式：Linux SHA-256 `3f3953d6b4db3abd9aeededcbcf128706c75ccc1600d5b366e74126db58adf25`，乾淨重建逐 byte 相同；四架構雜湊及 ELF／PE／Mach-O 檢查見同份彙整。正常存檔前實際畫面為 `workspace/runs/infrastructure-source/normal-road-hd-r2.png`，SHA-256 `4e18570e616c334685face303ee19e068d9ffeb352e839fe670d2efa3d4e2386`。本批沒有重跑 Wine、真機或正式封包。
- 交通候選的正常來源研究：[infrastructure_traffic_playtest.py](workspace/tools/infrastructure_traffic_playtest.py)、[infrastructure_traffic_playtest.sh](workspace/tools/infrastructure_traffic_playtest.sh) 從正常災難城市冷啟動，預設原版 0 暫停後以 1 恢復、觀察三十份色號；`TAIPEI_TRAFFIC_MODE=density` 則走 022 已查證的 F4 第二列「交通密度」入口，另觀察八份。只辨識實際原來源，不推導交通或模擬規則。

- 道路與電線批次：[#44](https://github.com/wicanr2/taipei/issues/44)，依 #30 研究完整來源、連接及 B 原型；第一批正常已見 25 張達 CONFORMED，其他候選維持 DRAFT。來源工具 [infrastructure_catalog.py](workspace/tools/infrastructure_catalog.py) 嚴格解析九組 9×9 圖庫與所有別名，回對既有正常 GUI 原子收據，輸出限本機 `workspace/runs/infrastructure-source/`。先查成員 39，不把來源圖庫索引當成建築語意。
- 道路／電線正常來源探針：[infrastructure_playtest.py](workspace/tools/infrastructure_playtest.py)、[infrastructure_playtest.sh](workspace/tools/infrastructure_playtest.sh)，以正常工具、方向鍵及 Space 建十字連接並移開游標；不注入城市／座標，有界研究停止不代替原版退出驗收。初批輸出 `workspace/runs/infrastructure-native/`，97 次原版讀鍵與兩個九格十字已通過。追加轉角、岸邊及電線道路重疊模式輸出 `workspace/runs/infrastructure-variants-native/`，另驗結果。
- 正常建造逐段核對：[infrastructure_source_check.py](workspace/tools/infrastructure_source_check.py)，直接重讀 ROM、原子畫面與原版讀鍵，分開已知來源變化及游標等未知格。預設 `--require-complete` 要求全部七段；`--case shore` 只核對獨立電線岸邊補查，結果分列本次要求及全部七段狀態。前綴報告明列缺段，不能代替整批完成。
- 電線岸邊缺段補查：[infrastructure_shore_playtest.py](workspace/tools/infrastructure_shore_playtest.py)、[infrastructure_shore_playtest.sh](workspace/tools/infrastructure_shore_playtest.sh)。第二輪 2400 秒上限保留六段完整收據，最後岸邊另由獨立補查通過：46 次原版讀鍵，陸地 (23,10) 向左至 (19,10) 五格均為成員 39／圖像 46。沿用同一 binary、image 及遊戲速度，輸出 `workspace/runs/infrastructure-shore-native/`；有界研究停止不代替原版退出。
- 追加來源盤點 `workspace/runs/infrastructure-source-r2/` 收入既有來源、第一輪十字、第二輪六段及獨立岸邊補查，沿用來源工具；不覆寫 v5 所固定的初盤。擴大正常來源的 v5 原位比較另存 `workspace/prototypes/hd-style/infrastructure-v5-expanded/`，不改 v5 素材或既有 SHA-256。
- 道路與電線呈現契約：[026](docs/spec/026-infrastructure-tiles.md)，第一批 25 張達 CONFORMED。候選四權重幾何及材質組合由 [infrastructure_prototype.py](workspace/tools/infrastructure_prototype.py) 產生，輸出 `workspace/prototypes/hd-style/infrastructure-v1/` 至 v5；其中其餘 18 張仍只供離線研究。
- 道路電線原型獨立核對：[infrastructure_prototype_check.py](workspace/tools/infrastructure_prototype_check.py)，直接解析固定 ROM 全部別名，以整數面積與 Fraction 色彩核對每張來源、四向邊緣、完整 1280×800 及全部區外。`infrastructure-v2/` 的 43 張候選、二十四張世界座標圖及五項有效破壞已通過；三次過渡修訂另存 `workspace/prototypes/hd-style/infrastructure-v3/`，v1／v2 保留作前件。原型均在 `workspace/prototypes/hd-style/`，正式 GUI 另驗。
- 瀝青材質原型：內建 imagegen 生成，檔案 `workspace/prototypes/hd-style/asphalt-b-v1-generated.png` 與 `asphalt-b-v1.png`，完整提示詞為同目錄 `asphalt-b-v1.prompt.txt`。1254×1254 版本 SHA-256 `61057d15840d65801652de6af95b1b27b56706d67774a66f41bec3fb852cd384`；原生成圖、提示詞及後處理均留本機，不把材質存在當作道路 HD 完成。
- 原位材質尺度修訂：v3 的實際 36×36 道路對比顯示瀝青顆粒過大。`workspace/prototypes/hd-style/infrastructure-v4/` 改以四倍世界頻率取樣同一固定瀝青，只調新材質尺度，保留原來源幾何及其他地景相位；正式接入前另核對此版本。
- 道路電線來源選取：[infrastructure_ida.sh](workspace/tools/infrastructure_ida.sh) 沿用既有固定 IDA 9.4 image 與唯讀 `ida-19/event-keys.i64`，在 `workspace/runs/ida-44/` 的一次性副本匯出 `sub_1619A` 原始定位與 bytes。參數 `bitmap-drawing` 另查原圖繪製 `sub_16129`，不覆寫前件；只追本批來源與相位，不改原始資料庫或覆蓋函式名稱。
- 道路電線 PNG 可重現修正：[#45](https://github.com/wicanr2/taipei/issues/45)，v4 乾淨重建發現像素相同但時間戳不同，前件保留 `workspace/runs/infrastructure-repro-v4/`。產生器改用固定標準庫 RGBA PNG，v5 輸出在 `workspace/prototypes/hd-style/infrastructure-v5/`，幾何與像素契約不變；157 檔乾淨重建通過，#45 已結案。026 狀態依上列第一批與其餘候選分開記錄。
- v5 驗證結果：兩次乾淨輸出全部 157 檔相同，70 PNG 均與 v4 解碼像素相同且只含 IHDR／IDAT／IEND。證據 `workspace/runs/infrastructure-source/v5-reproducibility.json`、`png-provenance.json`；Python 3.11.2／zlib 1.2.13，固定 GUI image。原位技術比較為 `workspace/prototypes/hd-style/infrastructure-v5/power-comparison.png`，左原版、右離線候選，非正式 GUI HD 收據。
- 預算完整面板契約：[025](docs/spec/025-budget-panel.md)，限完整預算呈現達 CONFORMED；已驗完整來源、動態文字、選取、F12、施工存退讀、有效負對照與原版狀態。
- 預算正式呈現：[budget.go](workspace/app/internal/hd/budget.go)，依 025 重建完整來源、辨識十一欄與單一選取，載入固定 B／Noto 面板及數字。只讀原畫面，不修改遊戲狀態。
- 預算實際素材測試：[budget_test.go](workspace/app/internal/hd/budget_test.go)，以固定 43 份來源及六張審查原型核對完整呈現、全部區外、失配回退與家族隔離；正常玩家驗收另驗。
- 預算 Go 獨立收據核對：[receipt-check/budget.go](workspace/app/cmd/receipt-check/budget.go)，`receipt-check -budget-reference <素材根> -original <原版目錄>` 另讀 ROM、固定參考、十一欄及選取；不引用產品呈現器。
- 預算有效負對照：[hd_budget_negative.py](workspace/tools/hd_budget_negative.py)，從正常收據破壞來源、色盤、底板、實際墨跡、區外及中繼資料；重算原版 PNG、呈現 PNG 與受影響雜湊後，要求兩個獨立核對器拒絕。
- 預算正式證據彙整：[budget_hd_provenance.py](workspace/tools/budget_hd_provenance.py)，已核對 116 份正常收據、五列 F12、非零費用、全新 EXE 預算設定讀回、逐點原版狀態、實際存檔、有效負對照、四架構及原始輸入，結果為 `workspace/runs/budget-source/hd-provenance-r4.json`。
- 預算整批獨立核對：[budget_hd_verify.sh](workspace/tools/budget_hd_verify.sh)，依序以 `scenario`、`cold`、`provenance` 核對已保存的修正版來源；每階段拒絕覆寫完成結果。狀態重播在正常第一段產生後另預登記並執行。
- 預算驗收程式：當時 Linux SHA-256 `66e8e18ec202cf3cf22a3fe4893947adfb368425c47ba127177b6b8696dcc9c1`；`budget-hd-scenario-r2/` 十三份與 `gui-budget-cold-r4/` 103 份正常收據均通過。正式唯一狀態輸入為後者 `quit-file-theme-hd-capture.zip`，SHA-256 `ad564fb6800171d15dd060cfb8137cdf5c599fbf34dbd712704eb2c154db4170`；兩側各 4,056,000,000 步，每 24,000,000 步共 169 點，五列預算實際呈現及原版狀態相同。結果 `budget-source/state-audit-r4.json`，狀態 SHA-256 `57371f3caa873699e591ce397076453a9ff6ceb111a1a0257825cd8d2510c681`。r3 僅作前件，其正常淨額 -1 另核對；目前程式雜湊以上列道路電線批次為準。
- 預算收尾：`workspace/runs/budget-source/hd-final-hygiene.json` 保存文件入口、相對連結、語法、Go 格式、擁有權、指定 find 與 Linux 乾淨重建比較。正式本機預算畫面在 `budget-source/normal-budget-hd.png`；素材與擷取不入 Git。存檔在 `gui-cold-saves.U5Gg8y/ROUND4.SAV`，SHA-256 `7b4470803b77aa311dfb83014db3e14c73981dccfe0b57fdc4aeb6993364efbd`。
- 預算負淨額抽樣：`workspace/runs/budget-source/negative-net-source.json`，r3 正常冷讀後的淨額 -1 已由獨立 Go／Python 核對完整來源、高清呈現及全部區外；原子收據 SHA-256 `f88c3831a3e787b620d956e39848750c68ec1a7868dacaf07ea8fc3ef488f85a`。僅驗該呈現，不宣稱稅率或規則極值已驗。
- 預算 Python 獨立核對：[hd_budget_check.py](workspace/tools/hd_budget_check.py)，重建完整來源、固定合成及全部區外，由既有逐幀核對共用。正常冷啟動的預算段落為 [budget_gui.py](workspace/tools/budget_gui.py)，本批以 `TAIPEI_TEST_BUDGET=1 TAIPEI_GUI_RUN=gui-budget-cold-r4 TAIPEI_THEME=hd-b` 交由既有 `gui_playtest.sh` 執行，五列 F12、調整、存退讀與新 EXE 設定重開已通過；拒絕覆寫原件。
- 預算離線原型：[budget-prototype](workspace/app/cmd/budget-prototype/main.go)，只讀本機來源與轉錄，沿用固定 B／Noto 產生完整底板、數字字形及原位比較；輸出 `workspace/prototypes/hd-style/budget-v1/`。固定輸出已由正式呈現載入，原型程式不進產品路徑。
- 預算原型獨立核對：[budget_prototype_check.py](workspace/tools/budget_prototype_check.py)，重讀 ROM、轉錄原框與 PNG alpha，核對靜態／數字墨跡、安全矩形、完整原位組合及全部區外；輸出 `workspace/runs/budget-source/prototype-check.json`。不當作正式 HD 收據。
- 預算讀鍵同步：[city_menu_playtest.py](workspace/tools/city_menu_playtest.py) 的 `action(..., acknowledge=True)` 只對已查證普通鍵等待實際 Key 與 release；預設片頭流程不強加 DOS 讀鍵。有限步數啟動使用 `wait_for(..., progress=True)`，仍由各 shell 的外層逾時擁有。#41 的正常入口與逐鍵收據已通過。
- 預算 READY 證據：`workspace/runs/budget-source/ready-model/catalog.json`、`ready-provenance.json`、`prototype-check.json`；43 份來源、172 項單點、十八項選取負對照、74 墨跡、六張原位圖及十檔重生通過。正式 manifest SHA-256 `f6a3052430ad3cc1cda5c737fb21ce6c73c13237e191e29cf0c92684553b9933`。研究收尾記錄 `final-hygiene.json`；正式 HD 驗證另見本批 r4 彙整。
- 預算研究審查來源：`workspace/runs/budget-source/review-model/catalog.json` 含 42 份完整來源、168 項單像素，初批 33 份原件不覆寫。`budget-native-ranges/result.json` 是未還原調整及實際 F2 存讀研究，名稱不代表完成規則極值測試。存檔 `budget-saves.rnp1jg5l/BUDGET39.SAV` SHA-256 `442981026373f69080668ad176335949636635c407ba5b14cbf4f2ce7265b430`。
- DOS 時間收尾：`workspace/runs/dos-clock-source/final-hygiene.json` 保存本批文件入口、相對連結、語法、格式、擁有權、容器內指定 find 與 Linux 重建比較；Docker 生命週期另由主機回讀。本批不建立正式交付目錄。
- DOS 時間證據彙整：[dos_clock_provenance.py](workspace/tools/dos_clock_provenance.py)，已核對該批原始輸入、固定七補丁、四架構、86 份正常收據、施工存退讀、兩次退出及獨立畫面檢查；輸出 `workspace/runs/dos-clock-source/provenance.json`。該時鐘批 Linux SHA-256 `52b65f10bd009c0f94741eaaa1aa36d0349342dbea646453bb9eff7ce9c40b8f`；舊四架構與來源收據保留 `before-build/`。
- DOS 時間測試：[dos_clock_verify.sh](workspace/tools/dos_clock_verify.sh)，先由現行建置入口重生七補丁，再執行 DOS、狀態、oracle、probe 與實際 HD 素材測試；輸出 `workspace/runs/dos-clock-source/`，正式正常 GUI 與封包不由此代替。
- DOS 時間修正補丁：[dosgolem-system-clock.patch](workspace/tools/dosgolem-system-clock.patch)，固定基底及原六補丁後套用的第七份補丁；沿用既有 Go image 與 [build_preview.sh](workspace/tools/build_preview.sh)。正常 GUI 由 `TAIPEI_THEME=hd-b TAIPEI_GUI_RUN=gui-dos-clock-cold bash workspace/tools/gui_playtest.sh` 驗證，拒絕覆寫既有收據。
- DOS 時間契約：[024](docs/spec/024-dos-system-clock.md)，#40 的公開平台前提、時間來源及驗證閘門。研究輸出 `workspace/runs/dos-clock-source/`，保留未修版本四組紅測試及固定 commit 的平台全文；新產品正常操作及存退讀已通過。
- 預算字形來源候選：`workspace/runs/budget-source/static-glyph-candidates.json`、`rom2-x4.png`，保留 ROM2 背景與原字模的精確匹配及別名；沒有 ROM57 精確對應的烘製文字已固定原框目視轉錄，不宣稱取得原版字碼。
- 預算輸入定位：[ida_budget_probe.py](workspace/tools/ida_budget_probe.py)，以 IDA Pro 9.4 及唯讀既有資料庫的複本匯出窄範圍函式；輸出 `workspace/runs/ida-39/`，保留原始名稱、bytes、IDA 線性位址與 EXE 檔案偏移。
- 預算正常入口研究：[budget_playtest.sh](workspace/tools/budget_playtest.sh)、[budget_playtest.py](workspace/tools/budget_playtest.py)，從正常冷啟動經 F3 預算選項探索數值、選取及返回；有界停止不取代原版退出。
- 預算完整來源研究：[budget_catalog.py](workspace/tools/budget_catalog.py)，ROM2 在 `(18,37)` 的 235×132 背景及十一個 ASCII 動態欄位。來源及轉錄經 025 READY 審查，正式完整面板與正常驗證均已完成。
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
