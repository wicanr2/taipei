# 發電廠圖塊

狀態：CONFORMED，限火力電廠已見完整來源的 36 格靜態呈現。核能電廠、其他相位維持 DRAFT。對應 [#46](https://github.com/wicanr2/taipei/issues/46)，依 [#30](https://github.com/wicanr2/taipei/issues/30)、[021](021-tool-submenus.md) 及 [026](026-infrastructure-tiles.md)。不宣稱完整發電廠、全部 HD、真機或正式封包完成。

沿用 B、1280×800、Noto、F12 及原版構圖。原版 EXE 管理火力／核能電廠選項、費用、建造、供電、發展、動畫與 SAV；本批只重繪已證實來源，不重寫規則。

| 輸入與工具 | 固定內容 |
|---|---|
| RS201.EXE | SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |
| RS201.ROM | SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29` |
| dosgolem | 基底 `a9714ebdab2ad6b529f81225472680f2b11f2842` 與現行七補丁；不改上游工作樹 |
| 正常 GUI | Linux 已驗前端 SHA-256 `3f3953d6b4db3abd9aeededcbcf128706c75ccc1600d5b366e74126db58adf25`；400000 steps/update，原版主題，沒有快照或城市注入 |
| Docker | image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`，UID/GID 1000、3 GiB、2 CPU、128 PID、無網路；原版唯讀 |

已證實的入口是 021 工具 11、完整矩形 (196,124,69,35) 的「火力電廠／核能電廠」兩個選取。正常方向鍵與 Space 操作逐鍵等原版讀取及前端 release；每次由完整已知選單來源核對選項。

研究入口為 [power_facility_playtest.sh](../../workspace/tools/power_facility_playtest.sh) 與 [power_facility_playtest.py](../../workspace/tools/power_facility_playtest.py)。預登記兩種正常施工、游標移開、固定原點，分開已知及未知變更格；完整來源從唯讀 ROM 九圖庫重讀，保留所有別名及原始檔案偏移。`TAIPEI_POWER_FACILITY_CASE=thermal` 或 `nuclear` 各走一次全新 EXE，輸出 `workspace/runs/power-facility-thermal-native/` 或 `power-facility-nuclear-native/`；有界研究停止不代替正常存退讀或原版退出。

首件 `power-facility-native/` 正常火力施工形成可見 6×6 圖塊，24 次 Right 在原版大游標下使原點由 (12,12) 到 (14,12)，因此固定原點斷言停止。原件保留，不列產品缺陷。窄補查改在已見完整陸地 (22..27,3..8) 施工，每次獨立冷啟動，不改遊戲邊界、速度或時間。原件最後施工前及移開游標後兩份原點均為 (14,12)，允許另核對這一部分的原始來源；部分核對明示 prefix，不作完整兩選項或正式 HD 證據。

核能首件 `power-facility-nuclear-native/` 按鍵完成但施工未形成建物。直接依原版 ROM 字形重建底欄，火力成本為 50000 萬、核能 100000 萬，新城市資金 80000 萬；核能資金不足。這是原版正常拒絕，不改產品或注入資金。後續由 [power_funding_playtest.sh](../../workspace/tools/power_funding_playtest.sh) 及 [power_funding_playtest.py](../../workspace/tools/power_funding_playtest.py) 正常運行 DISA1。r2 的 120 次觀察見資金 77413→53221，沒有成功籌資。r3 逐鍵保存過慢而停止；r4 短促按放未完整進入前端，保留原件。r5 以明示按下／放開各 0.2 秒、每八鍵停止並核對原版 Word／讀取與前端放鍵，再重建每列完整預算來源。這次實見稅率限制為 30、四項支出 0，第一年度後 93775；不改遊戲速度、時間或資料。最多 240 次、每次至少 24000000 步觀察，取得至少 120000 萬才正常保存 0001.SAV 及退出，供全新 EXE 冷讀施工。核能維持未完成。

## 火力 36 格 READY 契約

2026-10-12 審查：`workspace/runs/power-facility-native/source-check-thermal-prefix.json` 的同原點施工前後來源已證實 6×6、原位 (203,61,54,54)。完整來源 SHA-256 `791fbfe53259ca39fe6dbd91ba4e2fa36009b7bc43d61e31b3d498b816dca558`。每格均有唯一別名，限 ROM 零基成員 38，索引 `12 + 30×row + col`，row／col 為 0..5。原始 member／image、成員偏移、檔案偏移、像素偏移、81 bytes 雜湊與已用色盤均保留於來源核對及素材 manifest。這是已證實的畫面來源，不用圖庫排列推導未見建物或相位。

B 候選 v3 在實際 216×216 尺寸與原版並列目視核對，保留 15 棵樹、三座斜向廠房、五個紅黃色形狀、淡色直條、路徑及底部綠帶。只細化表面與輪廓，沒有新增附屬建物。v1 構圖偏移候選保留，不採用；幾何材質原型 v1 亦不接正式路徑。

| 審查輸入／結果 | SHA-256 |
|---|---|
| 完整生成候選 `thermal-illustration-b-candidate-v3-generated.png`，1254×1254 | `16642276a2ba54203e2b745525e65ba92106698fc9ac9b1151720f621211aa2c` |
| `power-facility-v2/manifest.json` | `d1d887b33ce64737a4f7939880316317bd2a2547837c5c0b1c10beff48b4ee7a` |
| 216×216 完整高清 RGBA 像素 | `ca1cf32361109c05298ea7f76b81a28c1031e4b2230687a325fbb9fa0807bc4b` |

離線工具 [power_facility_prototype.py](../../workspace/tools/power_facility_prototype.py) 依 ImageMagick 6.9.11-60 Lanczos 將完整候選一次縮至 216×216，再切成 36 個 36×36 格。PNG 由 Python 3.11.2／zlib 1.2.13 固定輸出；不用逐格縮放造成接縫。完整提示詞在候選同目錄 `.prompt.txt`，素材只留本機。獨立 [power_facility_prototype_check.py](../../workspace/tools/power_facility_prototype_check.py) 重讀九圖庫與收據，36 格完整重組等於全圖、原版像素及比較圖相等，2,916 項逐像素失配均拒絕；結果 `power-facility-native/prototype-check-v2.json`。

正式 typed input 僅為原版 64000 色號、色盤、mode、HD 旗標與已驗鏡頭原點。維持既有城市場景、完整選單／預算／檔案視窗與阻塞回退閘門。通過城市閘門後，每格 81 bytes 精確識別，從完整固定 atlas 擷取對應 36×36 格，覆於原版格的四倍矩形；不讀寫 DOS 記憶體、規則、費用、供電、時間、亂數或 SAV。

- 只有 36 個已見完整來源可覆繪，部分視窗以各完整來源格辨識，不依鄰格猜補。游標、未知、損壞來源與未確認動畫相位顯示原版。
- 固定 ROM、atlas／manifest bytes、216×216 形態與不透明 alpha 均須符合。素材或 manifest 失配時，所有已知電廠格維持原版，不落入其他家族。
- 已用色盤逐格符合才呈現；未用色盤變化不誤拒絕。既有城市地形色盤閘門仍在上層生效。
- 每格只寫其 36×36 區域。完整 6×6 重組、部分可見、F12、移開游標及重讀均重新從目前原版來源呈現，不保留覆繪殘影。
- 回報 matched／painted／fallback、image 次數與拒絕原因，統計由獨立核對器對原始資料重算。

正常火力來源窄補查 `power-facility-thermal-native/source-check.json` 已核對 40 個原版讀鍵、固定原點 (12,12) 與完整 36 格，複合來源與部分來源相同。GUI r1 已實際覆繪 36 格、資金 29980。r1 切換期間 212 個原版變動像素全部位於大游標矩形 (149,61,54,54)，廠區未變，收據只新增 theme 事件，沒有 DOS 鍵盤或滑鼠事件。r2 的十二次無輸入對照未觀察到改變，因此撤回「自主閃爍」的確定解釋。固定步數診斷兩側各完整執行 3,936,000,000 步，164 個抽樣點的原版狀態相同，兩側最終原版畫面、色盤、讀鍵及檔案操作符合 r1 真實 GUI 收據。無呈現器側沒有執行 theme 事件，證明該游標差異不需要 F12／高清呈現器；內部控制原因維持未知。高清側實際抽到 36 格、15 個火力畫面，結果為 `power-facility-thermal-native/cursor-state-diagnostic-r1.json`，原版狀態 SHA-256 `4b9eb6d9e39664dab0257f8fe52d58f58ae87da7b83c702b75a5033704e3aa71`。此診斷不代替正常存退讀與退出。原件保留，未改產品、原版時鐘或遊戲速度。

r3 正常 GUI 依 [預登記](https://github.com/wicanr2/taipei/issues/46#issuecomment-6113688837) 重跑。不要求跨不同虛擬時間的游標像素相等，也不要求游標改變；要求完整游標外及完整廠區來源相等，F12 只新增 theme 事件。全原版狀態依相同輸入、相同步數的完整重播驗證。捲動及返回原點逐一核對 36 格世界座標／來源，正常存退讀及兩次退出仍為必需完成條件。

核能 r5 完整 489 個預算方向鍵與 240 次正常觀察結束，最後年 115 月 8、資金 98212，收入依次實見 16362／4437；未達成本或門檻，沒有保存成功聲明。保留原件，不以此外推財政規則或繼續相同探針。

正式驗收預登記：正常新城市先建一格電線，再經工具 11 的火力選項施工；游標移開，核對原版資金 29980、完整 36 格、F12 不送 DOS 鍵，兩軸各正常捲動兩格及同世界圖塊；正常 F2 存檔、兩次原版退出、全新 EXE 冷讀後恢復電線與火力原始圖塊及資金。另驗 2,916 個來源反例、逐已用色、未用色、真實素材缺失／損壞、完整區外及有效收據負對照。正式狀態重播由這條正常 GUI 的唯一輸入產生後另登記固定步數及 24000000 步抽樣，原版狀態與實際 SAV 須相同。

本規格 CONFORMED 只適用於這一已見靜態來源、以下版本及正常抽樣路徑；其餘未知不由程式猜補。

## 2026-10-12 正常 GUI 與原版狀態驗收

`gui-power-facility-cold-r3/` 從全新 EXE 正常新城市、暫停、電線及火力施工，資金 29980、完整 36 格通過。兩次 F12 只新增 theme 事件，原版讀鍵、其餘全部輸入、完整游標外與廠區來源相同。一次無輸入對照未見游標變化，不要求特定閃爍週期。水平 13 次 Right 使原點 (12,12)→(14,12)，垂直 12 次 Down 到 (14,14)，正常返回 (12,12)；各階段逐一核對 36 格的世界座標及原始來源。

正常 F2 保存、兩次原版退出與全新 EXE 冷讀通過，原電線格及火力 36 格來源相同，讀回資金 29980。實際 `gui-cold-saves.zsEQND/ROUND4.SAV` 為 93567 bytes，SHA-256 `1b7522328f296547dfc1505fd408c04c486c9b23ceed1a8c49a4d2ff66b4972c`。Go／Python 獨立核對 162 份原子收據，其中 93 份實際覆繪火力；完整像素、來源、色盤、回退及統計通過。五項重算 PNG／雜湊的有效破壞兩側均拒絕，原件及未用色盤兩個正對照通過。

依 [正式重播預登記](https://github.com/wicanr2/taipei/issues/46#issuecomment-6113948686)，唯一 GUI 收據 SHA-256 `30b4949f89d34f38e16fb0935d31e8086c2b08030149ac5d63e0abd4ba7004e9`。兩側各完整執行 8,064,402,774 步，每 24,000,000 步抽樣，共 336 個原版狀態相同，實際抽到 36 個火力來源及 164 個火力畫面、檔案六次及離開確認三次。最終原版畫面、色盤、讀鍵及檔案操作符合實際 GUI；落地 SAV 同為上述實際雜湊。原版狀態 SHA-256 `df7b442241b71a292822bd4162d7a14a591c870bad80c28ba8e80fe336deda36`，結果檔 `power-facility-thermal-native/normal-state-r1.json` SHA-256 `0321c247af7e451f0d26ed6fc38ef276730e72741f509fd4eecb1fa6613a6c90`。兩側依次 513.8／499.6 秒，沒有以不同時間的游標像素作相同狀態判準。

本批 GUI binary SHA-256 `2821c65bfb4daad6e46677bb0c72b199c13f772c8eeae7262dbc17b2e69ee9d1`，原創呈現實作提交 `d32b35d`，正常驗證工具提交 `f5e21ff`；dosgolem 與七補丁未變。Linux 乾淨重建逐 byte 相同，保留 `workspace/runs/taipei-preview-power-clean-r1`。Windows amd64 及 macOS amd64／arm64 編譯與結構通過，真機仍未驗。全部 HD 及鍵盤回歸通過；本批原始 35 檔與 RAR 雜湊不變，輸出 UID/GID 1000，指定 root-owned／`.md` 目錄檢查為空，相關容器均已刪除。

總核對在 `power-facility-thermal-native/final-verification-r1.json`，正式正常畫面原件為同目錄 `normal-power-hd-r3.png`，SHA-256 `2a89a2ccefa5515bf0f062898c7fa3c961e20fc5940f862d354fd4898e45b5b4`，直接取自真實正常收據，沒有後製。核能正常成功施工與其他相位尚無充分來源，#46 保持 OPEN。

## 核能接續研究入口

[power_scenario_scan.sh](../../workspace/tools/power_scenario_scan.sh) 與 [power_scenario_scan.py](../../workspace/tools/power_scenario_scan.py) 從全新 EXE 的正常災難城市選單依顯示順序檢查六座城市。逐座暫停、解碼原版資金、正常 F2 保存與原版退出；遇到第一座至少 120000 的城市即停止。檔案讀取紀錄確認實際 DSA，SAV 保留原始 bytes 與 SHA-256。此研究不改寫城市、財政、時間或亂數，不重複已結束的 DISA1 極端預算探針，也不作核能施工完成證據。

[power-funding-continuation](../../workspace/app/cmd/power-funding-continuation/main.go) 是 DRAFT 研究命令，僅在 Docker 內執行，參數為 `GUI-capture.zip new-output-dir`。從 EXE 重播 r6 實際輸入，必須先匹配末端原版畫面、色盤、讀鍵及檔案操作，才續跑最多 250 次、每次 24000000 步。資金達 102000 就暫停，未達上限也保存進度；存檔及退出均用原版鍵盤／DOS owner，不寫財政記憶體或 SAV bytes。這是原版來源研究，不代替正常 GUI 抽驗。

[power_nuclear_playtest.sh](../../workspace/tools/power_nuclear_playtest.sh) 與 [power_nuclear_playtest.py](../../workspace/tools/power_nuclear_playtest.py) 為尚未執行的 DRAFT 探針。接受唯讀的原版籌資 SAV 與固定 SHA-256，預定由正常 GUI 冷讀、確認陸地、原版整地及核能施工，再正常存讀退出。成功來源與 READY 前不接核能 HD。執行前須在 #46 登記實際輸入及完整情境。

六座城市已正常載入、原版 F2 保存與退出。`power-scenario-scan-r2/check.json` 以獨立原版底欄字形、DSA 讀取總長 93567、實際 SAV 雜湊／長度與最終 DOS 退出逐項核對，SHA-256 `830675c58177f173520a91580e893c3473629dca2db6354caec4c1902af98c40`。來源為 r1 第一座及 r2 其餘五座；r1 的第二次重複台北不計入六城。原版 Down 依欄序遞增選項，Right 不切欄。

| 原版城市檔 | 正常畫面起始資金 |
|---|---:|
| DISA1.DSA | 77413 |
| DISA2.DSA | 69679 |
| DISA3.DSA | 52673 |
| DISA4.DSA | 73455 |
| DISA5.DSA | 78475 |
| DISA6.DSA | 80000 |

r6 完整預算按鍵與 480 次正常觀察已完成，稅率實際為 20、四項支出 0。最後年 117 月 8、資金 98428，仍未達核能成本。117 年 1 月曾見 98528，不當作末端資金。年度收入實見 11326／3089／3715／3085。後續由同一實際輸入的原版續跑保留進度，不重擲或修改財政條件。

`power-nuclear-preflight-r1/preflight.json` 已完成正常 GUI 冷讀、工具列／地圖焦點、單格游標、陸地候選及原版退出。原版 FUND.SAV 保持 `fdd4e3a9c0da6320bb0a2a4357f948589ebc34d0061d54ae624951b190bbc96f`；原點 (6,22)、游標 (9,8)、整地費用 10，候選矩形為視窗格 (11,7,6,6)。這一件沒有整地或核能施工，只驗證探針的前置操作。

續跑 r2 已從 EXE 完整重播到 15780000000 步，原版末端畫面、色盤、讀鍵與檔案操作符合 GUI；監測漏了現行 Renderer 的 SetLanguage 初始化而讀不到資金，已停止並保留原件。r3 執行前以固定原始收據的 `inspect` 模式確認右欄 mask=2、98428，才重播。右欄獨立有效即可讀資金，不要求左欄費用一起匹配。r3 先用原版鍵盤保存 0000.SAV，再續跑，最後保存不同名稱 0001.SAV，避免驗證工具錯誤時再次遺失原版可保存進度；仍不是核能施工完成證據。
