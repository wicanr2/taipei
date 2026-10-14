# 驗收矩陣

本檔定義證據與完成條件。工作狀態只看 [GitHub Issues](https://github.com/wicanr2/taipei/issues)，
目前真相由 [CONTEXT.md](../CONTEXT.md) 保存。

依使用者 2026-10-13 的定案，已實作功能可由正常遊玩抽驗驗收。與現行產品一致的已通過收據可沿用，長時間相同步數 RAM／CPU／RNG 對拍不列必要結案門檻。結論限實際走過的功能與路徑，未製作圖片、未驗平台及正式封包仍各自處理；本次回核見 [#55](https://github.com/wicanr2/taipei/issues/55)。

| 範圍 | Issue | 必要證據 | 完成限制 |
|---|---|---|---|
| 開場、插畫與動畫 | [#32](https://github.com/wicanr2/taipei/issues/32) | 209別名／197種、179完整正式圖、261檔重生、六ABI唯讀、來源／色盤／素材／遮擋／未知屏障正反例、正常十圖與五語系、F12／Help及同程式存退讀 | [039](spec/039-illustration-animation.md) 限完整來源與正常代表CONFORMED。十圖165591格及十像素反例；r19正常前段、r20完整存退讀退出分列，不能把前段補為完整退出。92張README；全部出現分支、外平台及正式封包另驗 |
| 完整地圖圖庫 | [#62](https://github.com/wicanr2/taipei/issues/62)、[#30](https://github.com/wicanr2/taipei/issues/30) | 九圖庫實際1134項／1049種、301種新增非空來源、十三整圖、十五區域Noto字墨、來源／色盤／真實資源故障、正常五種代表與C1存讀退出 | [038](spec/038-map-completion.md) 限來源呈現與實際抽樣CONFORMED；24381來源反例、12資源故障、136檔重生、42張真實GUI與42像素反例、93567-byte SAV與舊版相同。r3照片為正常來源前段，r4完成C1存讀退出；C2兩高階路由未知、成長／災害分支、外平台真機及正式封包未驗 |
| 十二項環境與公共設施 | [#58](https://github.com/wicanr2/taipei/issues/58)、[#60](https://github.com/wicanr2/taipei/issues/60) | 十二份正常完整施工圖、392 格 B；同源鄰格辨識、來源／色盤／素材回退；正常跨組 F11／F12／存讀檔／DOS 退出 | [036](spec/036-public-facilities.md) v2 限靜態圖與已驗路徑 CONFORMED。391 種來源、26 項素材故障與隔離、全部區外、同源格原位／裁切／失配通過；八張 GUI 與六項正反對照含同源格交換。十三素材檔重生相同，四架構重編。其他相位、冷讀、外平台真機與正式封包未驗 |
| 治理 | [#1](https://github.com/wicanr2/taipei/issues/1) | private／Issues 回讀、文件入口、排除規則、提交與推送 | 不證明遊戲可執行 |
| 原版輸入 | [#2](https://github.com/wicanr2/taipei/issues/2) | 檔案清單、SHA-256、啟動方式與版本證據 | 來源未知不猜填 |
| dosgolem 啟動 | [#3](https://github.com/wicanr2/taipei/issues/3) | 固定 commit、真實入口、可操作畫面、重播與缺口 | 未實際走到的路徑不算支援 |
| 原版前端與存檔 | [#4](https://github.com/wicanr2/taipei/issues/4) | 正常 GUI、核心操作、存退讀與來源雜湊 | direct-entry 不替代 GUI |
| HD 原型 | [#5](https://github.com/wicanr2/taipei/issues/5) | 已證實繪圖來源與同狀態比較原型 | 不自動進正式路徑 |
| HD 契約 | [#6](https://github.com/wicanr2/taipei/issues/6) | 使用者批准樣式、平台與 READY 規格 | 重大取捨不得推定同意 |
| HD 接入 | [#7](https://github.com/wicanr2/taipei/issues/7) | 來源／動畫／遮擋／清除／切換，正常遊玩及存讀檔抽驗 | 圖片存在不代表正確播放；不以遊玩抽驗宣稱完整機器狀態對拍 |
| 玩家抽樣 | [#8](https://github.com/wicanr2/taipei/issues/8) | 先登記情境，正常冷啟動至核心操作及存退讀；有效負對照 | 限實際驗證範圍，不宣稱全程試玩 |
| 交付 | [#9](https://github.com/wicanr2/taipei/issues/9) | 實際封包啟動、權利、manifest、SHA-256 與平台結果 | Wine、結構及真機驗證分開記錄 |
| 全部來源盤點 | [#28](https://github.com/wicanr2/taipei/issues/28) | 所有成員、圖像與別名、正常可見狀態、未知來源及覆蓋清單 | 可解碼不等於繪製語意已證實 |
| 城市介面 | [#29](https://github.com/wicanr2/taipei/issues/29) | 工具圖示、外框與選取狀態逐像素核對，原版命中範圍不變 | 十四個圖示內部不代表完整介面 |
| 全部地圖 | [#30](https://github.com/wicanr2/taipei/issues/30) | 地景、道路、電線、建物、設施與災害的來源、遮擋及相位 | 未接入或未知回退仍列未完成 |
| 道路與電線 | [#44](https://github.com/wicanr2/taipei/issues/44) | 完整來源、別名、固定整格、資源故障、有效負對照；正常施工／F12／雙向捲動／存退讀及原版狀態 | [026](spec/026-infrastructure-tiles.md) 限第一批 25 張 CONFORMED；105 正常收據、九格同世界像素、五項有效呈現破壞及 206 點原版狀態通過。其餘 18 張 DRAFT，完整批次及交付仍未完成 |
| 火力電廠 | [#46](https://github.com/wicanr2/taipei/issues/46) | 完整 36 格來源／重組、回退、實際素材故障、有效負對照；正常施工／F12／雙向捲動／存退讀及兩次退出 | [027](spec/027-power-facility.md) 限已見靜態來源 CONFORMED；162 正常收據、36 格同世界來源、五項有效破壞及 336 點原版狀態與實際 SAV 相同。其他相位、全部 HD／封包未完成 |
| 核能電廠 | [#46](https://github.com/wicanr2/taipei/issues/46) | 既有城市正常冷讀與捲動、36 格完整來源／同源格、F11／F12、存讀檔與原版退出；全圖、區外、裁切、資源故障及有效負對照 | [027](spec/027-power-facility.md) 限 36 格／35 種來源與已驗路徑 CONFORMED；八份整圖、六項正反對照及既有回歸通過。原版 SAV 與無核能 HD 基線完全相同。新建核電廠、其他相位、完整狀態對拍、外平台真機及封包未驗 |
| 港口與機場 | [#61](https://github.com/wicanr2/taipei/issues/61) | 既有DISA4正常冷讀／捲動、完整72格、逐項F11五語系／F12、原版存讀與退出、完整圖與區外、來源／色盤／素材故障及有效負對照 | [037](spec/037-transport-facilities.md) 限72種來源與已驗路徑CONFORMED。十二張全圖與五項對照通過，SAV與無運輸HD基線相同；四架構編譯／格式完成。新建機場、其他相位、完整狀態對拍、外平台真機及正式封包未驗 |
| 警察局與消防局 | [#57](https://github.com/wicanr2/taipei/issues/57) | 工具 5 正常施工兩種設施、32 格 B、來源／色盤／素材回退、F11／F12／存讀檔／DOS 退出 | [035](spec/035-civic-facilities.md) 限本批及已驗路徑 CONFORMED；六張設施像素與語言標籤、原版整張、五項正反對照；2592 項來源失配、四項真實素材故障、正常來源與全部區外隔離、12 項測試與四架構通過。二素材檔乾淨重生相同；其餘相位、全新 EXE 冷讀、長時間狀態對拍、真機與正式封包未驗 |
| DISA1 首批建物 | [#56](https://github.com/wicanr2/taipei/issues/56) | 三種完整正常來源、48 格 B 重繪、色盤與資源回退、正常入口／F11／F12／存讀檔／退出 | [034](spec/034-disaster-city-buildings.md) 限本批及已驗路徑 CONFORMED；116 格正常繪製、六張完整畫面、六項正反對照、3888 項來源失配、八項真實資源故障、十一項既有回歸與四架構通過。三圖及 manifest 四檔乾淨重生相同；其他建物／相位、全新 EXE 冷讀、真機及正式封包未驗 |
| 全部文字與視窗 | [#31](https://github.com/wicanr2/taipei/issues/31) | 原始文字來源、完整字串、實際 Noto 墨跡、安全矩形與正常 GUI | 字模候選不直接作正式覆字規則 |
| 介面五語系 | [#51](https://github.com/wicanr2/taipei/issues/51)、[#52](https://github.com/wicanr2/taipei/issues/52)、[#49](https://github.com/wicanr2/taipei/issues/49) | 五語系完整文字鍵、實際字形與安全矩形、來源覆蓋、數值／檔名隔離、正常 F11／F12、缺譯警示與存讀檔／退出 | [032](spec/032-interface-localization.md)、[033](spec/033-localization-source-coverage.md) 限已盤點來源及必要短流程 CONFORMED；225 鍵、1213 字元、146 筆中文對應、各語系 77 種介面狀態及 192 個原版文字階段、九筆圖片通過。成功結局完整流程、密碼分支、未知用途、平台真機與正式包的限制見 033 |
| README 原版與五語系截圖 | [#53](https://github.com/wicanr2/taipei/issues/53) | 現行前端正常冷啟動，原版城市／預算及 HD 五語系、Help 五語系；PNG／原始收據雜湊、尺寸、字形、連結、來源色號與可見 RGB、原始預算數值及正常退出 | [17 張截圖來源](../workspace/screenshots/manifest.json)與 `readme-screenshots-r4/verification.json` 通過。每語系從正常選單重開預算；各組完整原版畫面及可見顏色一致。CPU／時鐘及未使用色盤不要求相同，無長時間抽樣、完整 HD、平台真機或封包驗收聲明 |
| 遊玩驗收與遊戲介紹 | [#55](https://github.com/wicanr2/taipei/issues/55) | 現行產品與正常收據一致；README 遊戲背景有來源、實際截圖有標示與 manifest | 六圖表依新標準通過，追加災難台北城市畫面後共 29 張截圖；不重跑相同產品的已通過流程 |
| 城市六功能選單 | [#37](https://github.com/wicanr2/taipei/issues/37) | 六入口、二十九選取、完整來源、原文及墨跡；正常 F12、取消、存退讀與狀態對照 | 022 限六面板二十九選取 CONFORMED；確認後視窗另驗 |
| 存讀檔與離開提示 | [#38](https://github.com/wicanr2/taipei/issues/38) | 完整來源、正常輸入邊界與選取、F12、施工存退讀、有效負對照及原版狀態 | 023 限兩家族 CONFORMED；外部檔案錯誤與模態外另驗 |
| 預算與稅率視窗 | [#39](https://github.com/wicanr2/taipei/issues/39) | 完整 ROM2、十一動態欄位、五列選取、Noto 墨跡、正常調整／返回、全新 EXE 設定重讀及 HD 狀態對照 | 025 限完整面板 CONFORMED；116 正常收據、十三有效呈現破壞與 169 點原版狀態通過；極值規則及其他介面另驗 |
| 預算完整 GUI 工具 | [#42](https://github.com/wicanr2/taipei/issues/42)、[#43](https://github.com/wicanr2/taipei/issues/43) | 有界雙冷啟動、冷讀後正常暫停、實際鍵及 release、施工與兩次原版退出 | 同產品及 image 的 `gui-budget-cold-r4/` 通過；部分前件保留，不改原版速度或年度流程 |
| 普通按鍵驗證同步 | [#41](https://github.com/wicanr2/taipei/issues/41) | 正常入口、原版 Key／word 與 release，片頭特殊入口保留，整批有界 | 九鍵及六個普通讀取已正常通過；只驗工具，不代表新的產品 HD |
| DOS 系統時間 | [#40](https://github.com/wicanr2/taipei/issues/40) | BIOS／raw IRQ 受控反例、INT1A 設定、快照、正常預算、施工存退讀與四架構 | 024 限時間來源 CONFORMED；保留既有整數近似，不宣稱精確硬體時序 |
| 場景與動畫 | [#32](https://github.com/wicanr2/taipei/issues/32) | 開場、選城、難度、插畫、事件、評分與動畫相位 | 單張素材不證明完整播放 |
| 政績靜態底圖 | [#47](https://github.com/wicanr2/taipei/issues/47) | 兩個完整 ROM 來源、B／Noto 原型、F12／失配回退／真實資源故障；正常施工存退讀、兩次原版退出、獨立完整像素及固定輸入狀態 | [028](spec/028-ending-achievement-base.md) 限已見底圖 CONFORMED；50 正常收據、七項有效破壞及 125 點原版狀態與實際 SAV 相同。其他結果及動畫 DRAFT，全部 HD／封包未完成 |
| F4 圖表視窗 | [#48](https://github.com/wicanr2/taipei/issues/48)、[#54](https://github.com/wicanr2/taipei/issues/54)、[#55](https://github.com/wicanr2/taipei/issues/55) | 六個真實入口及返回、B／Noto、F11／F12、正常遊玩與存讀檔抽驗 | [029](spec/029-chart-windows.md) 限六圖表呈現及已驗正常路徑 CONFORMED。六入口及返回、電力圖五語系、34 張完整圖表、14 項正反對照、同次存讀檔與正常退出通過；既有四項核心測試含十一種資源故障與家族隔離通過。#55 回核與現行產品一致，依使用者指定的遊玩標準驗收。完整相同步數狀態、本圖表流程施工至全新 EXE 冷讀及平台真機未驗，保留證據限制 |

032 的現行文字驗證為 `interface-locale-unit-final.log` 與 `interface-source/catalog.json`。正常 GUI 分段來源為 r9 的工具／Help／人口／民意、r10 的五項環境完整提示與五語系預算，以及 r11 的完整冷啟動英文存讀檔、兩場景 F12、政績標題與原版退出；前兩輪後續驗證錯誤保留，不能稱整輪 PASS。`interface-locale-cold-r11/verification.json` 通過，LOCALE.SAV 93567 bytes，讀回後雜湊相同。Linux 重建與已驗 binary 相同，Windows amd64／macOS amd64／arm64 編譯與架構通過；不提升 029 完整 HD 或平台真機驗收，也未恢復長時間抽樣。下方 030 的 115 鍵為第一批歷史範圍，現行 181 鍵以 032 為準。

目前已驗證正常 GUI 冷啟動、新遊戲、電線施工、檔名輸入及退格、原版實際存檔、
原版離開、全新 EXE 啟動與實際讀檔，兩次均由原版返回 DOS。沒有使用機器快照。
收據為 `workspace/runs/gui-cold/result.json`，來源 35 個檔案雜湊不變。
施工格在全新啟動讀檔後逐 byte 相同。原版音訊已經實際播放器輸出，隔離 monitor 非靜音；合成分段連續、原版狀態不變及平台限制另見[音訊契約](spec/009-opl2-audio.md)。技術擷取不當作人耳試聽。

HD 離線及動態比較原型的地景涵蓋水面、沙地與樹冠。素材撤除、來源／色盤失配、原版視窗回退、切換與區外像素檢查通過；冷啟動施工存退讀通過，存檔與原版模式相同。詳見[離線契約](spec/008-hd-material-prototype.md)與[動態契約](spec/010-hd-live-prototype.md)。字型方向已定 Noto，正式切換已定 F12，全部圖片與介面範圍見 [015](spec/015-full-hd-scope.md)。各批來源與實作繼續驗證，不把局部原型當成 #7 或 #8 的正式完成證據。三平台封包仍未建立。

Windows 研究 binary 已在 Wine 從真實冷啟動到城市畫面，正常鍵盤輸入及原版城市色號與 Linux 相同。收據為 `workspace/runs/wine-preview/result.json`；這項預檢沒有驗 Windows 音訊裝置、存退讀、正式封包或真機。macOS 兩架構只完成編譯及載入命令檢查，最低系統版本欄位為 11.0，未真機執行。

[#23](https://github.com/wicanr2/taipei/issues/23)、[#24](https://github.com/wicanr2/taipei/issues/24) 另抽樣正常 GUI 四向捲動。24 份單幀收據的來源及回退像素通過，六組原版圖塊位移與已證實的世界原點差一致，2001 個相同世界地景格的 HD 像素保持相同。有／無原點觀察及 HD 呈現的原版 RAM、CPU、色號、色盤與讀鍵紀錄相同。證據見[地圖原點研究](re/006-map-origin.md)，契約見[世界座標原型](spec/011-hd-world-origin-prototype.md)。範圍仍為 DRAFT 地景原型，沒有替代正式 #7、#8 或全遊戲動畫驗收。

[#25](https://github.com/wicanr2/taipei/issues/25)、[#26](https://github.com/wicanr2/taipei/issues/26) 從真實冷啟動使用原版速度鍵 `3`，固定間隔抽樣 60 次。人工確認 49 個連續月份，從 80 年 11 月至 84 年 11 月。兩次年度預算視窗已整幀回退，後續城市恢復 HD；23,815 個相同原點與來源的地景格保持相同像素。重播相同正常輸入，兩側各 2,400,000,000 步的原版狀態相同。證據見[持續運行研究](re/007-running-city.md)，契約見[年度視窗原型](spec/012-budget-window-prototype.md)。本項不涵蓋發展後建物、未擷取相位、正式字型、原版退出或平台封包。

[#18](https://github.com/wicanr2/taipei/issues/18) 已取得使用者 Noto 高清黑體定案。[#27](https://github.com/wicanr2/taipei/issues/27) 的六個主選單標題已接入動態比較原型：35 份正常冷啟動施工存退讀收據、固定參考逐像素比對、字型／授權／色盤失配回退與原版機器狀態比對通過，存檔雜湊相同。收據核對器對文字與矩形間像素破壞的有效負對照均拒絕。範圍與命令見 [Noto 動態原型](spec/013-noto-menu-prototype.md)，其他文字尚未完成。

使用者已確認遊戲中切換。[F12 操作契約](spec/014-live-theme-switch.md) 為 READY；既有正常 GUI 的 HD → 原版 → HD 三份收據，其原版色號雜湊與 DOS 讀鍵紀錄相同。此為研究前端操作證據；#7、#8 仍須驗正式接入及實際封包，不能以本次文件定案結案。

HD 五語系控制沿 [030](spec/030-hd-localization.md)，後續介面與完整可讀來源沿 [032](spec/032-interface-localization.md)、[033](spec/033-localization-source-coverage.md)。第一批 `locale-ui-cold-r1/verification.json` 驗兩次冷啟動、F11 五語系、設定冷讀、輸入隔離及 F12。後續 r15 正常播放開場與插畫，在上任信逐字中切換韓文，取得全部三十個開場／上任信鍵及五類圖片文字，再驗城市逐字提示、環境、預算五語系、英文原版 SAV 存讀檔與 DOS 退出。r17 真實缺譯回退與 F11 可見警示通過。三句結局文字另有 IDA 參數合成測例；成功結局未走完整玩家流程，密碼未啟用，`245C4h` 保留未知用途標記。沒有 checkpoint、長時間 RAM／RNG 抽樣、平台真機或正式封包。

[Help 031](spec/031-help.md)／[#50](https://github.com/wicanr2/taipei/issues/50) 已確認 Shift+F1 開啟、保留原版 F1，限八列操作與前端輸入達 CONFORMED。五語系完整面板與確認前固定原型逐像素相同，區外透明，缺鍵／缺字／超長及固定字型／授權故障通過。`help-ui-cold-r1/verification.json` 的正常冷啟動驗左右 Shift、已轉送持鍵配平、Esc／同鍵關閉、關閉持鍵隔離、鍵盤／文字／滑鼠不穿透、F11 五語系與取消返回 Help、F12 原版區外同幀像素、原版 F1 選單及返回後原版輸入。Help 期間 CPU／步數／原畫面／palette／BIOS ticks 與修飾旗標／讀鍵／檔案操作不變。Linux amd64、Windows amd64、macOS amd64／arm64 編譯與架構通過；未重跑 Wine、真機、SAV 存退讀、原版退出或長時間狀態抽樣，不外推完整 HD／翻譯或正式交付。

[#29](https://github.com/wicanr2/taipei/issues/29) 首批十四個工具圖示內部已接入。[016](spec/016-city-tool-icons.md) 限本批範圍達 CONFORMED：35 份正常 GUI 收據中，11 份完整覆繪十四個圖示、24 份回退；固定 atlas、獨立重算來源遮罩、選取外框及冷讀恢復皆通過。破壞文字、矩形間隙、圖示及選取外框後同步更新呈現雜湊，四個負對照均被拒絕。兩側各 1,200,000,000 步的原版狀態相同，實際包含 716 幀圖示覆繪；存檔雜湊保持相同。#29 仍須其餘框架、狀態與操作提示，母項保持開啟。

[#28](https://github.com/wicanr2/taipei/issues/28) 的[完整初盤](re/008-full-asset-inventory.md)保留 118 個成員、1317 筆圖片來源、1220 個不同圖像及未知項。依 [#31](https://github.com/wicanr2/taipei/issues/31) 另取得 402 個字模與原始字碼，十二字正常畫面正對照及十二個單點破壞負對照通過，詳見[字模研究](re/009-chinese-font-sources.md)。候選搜尋尚未接入正式覆字，不能據此宣稱其餘文字已完成。

[#31](https://github.com/wicanr2/taipei/issues/31) 的[新遊戲說明視窗](spec/017-new-game-dialog.md) 已接入完整 B 底板與 Noto 原文，本批達 CONFORMED。正常 GUI 開窗、F12 往返與關窗通過，37 份收據的完整面板、區外像素、既有標題與圖示均通過獨立核對；五個同步更新雜湊的竄改負對照均被拒絕。相同正常輸入的兩側各 1,224,000,000 步原版狀態相同，實際包含 55 幀說明覆繪。施工、存退讀與原版退出通過，存檔雜湊保持相同。#31 的其他選單、動態文字、圖表與視窗仍未完成。

[#31](https://github.com/wicanr2/taipei/issues/31) 的[三種啟動選單](spec/018-startup-menus.md) 限十三個選取狀態達 CONFORMED。40 份正常冷啟動收據包含全部選取、三場景 F12、無效鍵、難度 Escape 及進入城市；獨立核對完整面板、選取與區外像素。六種同步更新受影響雜湊的竄改均被拒絕。另重跑 37 份施工、存退讀與原版退出收據，原版存檔雜湊相同。兩側相同輸入各 1,776,000,000 步的完整原版狀態一致，涵蓋 2,165 幀及全部十三種選單。沒有逐一驗七座城市開局或災難分支，其他介面及正式封包仍未完成。

[#29](https://github.com/wicanr2/taipei/issues/29) 的[城市框架](spec/019-city-chrome.md) 限六部分及十四工具外框達 CONFORMED。正常 GUI 的 63 份收據驗完整 42 種外框、五個子選單回退、確認、Tab 取消、F2 與 F12；37 份正常施工存退讀及原版退出收據亦通過，共 100 份。來源重算、固定參考與區外由互補核對器驗證，八種重算雜湊且原版 PNG 一致的竄改均被拒絕。相同輸入兩側各 2,304,000,000 步的完整原版狀態與檔案操作一致，實際包含 3,113 幀完整框架。存檔與冷讀施工格相同。左欄定位依新證據訂正，舊推論與收據保留勘誤。底部文字後續進展見 020；子選單高清化、其他圖片與正式封包仍未完成。

[#31](https://github.com/wicanr2/taipei/issues/31) 的[底部動態文字](spec/020-city-footer.md) 限費用、年月與資金達 CONFORMED。68 份原始來源整欄重建、408 個來源負對照及十八字形實際墨跡通過。最新正常 GUI 共 103 份收據，涵蓋十四工具、五子選單回退、F12、80 年 9 → 10 月、施工資金 80000 → 79980、存檔與兩次原版退出、冷讀原施工格及資金。整欄固定參考、原符號與其他區外通過，八種重算雜湊的有效竄改被拒絕。相同唯一正常輸入兩側各 2,352,000,000 步，包含 3,236 幀底部覆繪，原版狀態及檔案操作相同；存檔雜湊保持基準。正常連續方向鍵改為逐次等原版讀鍵及 release，修正 [#34](https://github.com/wicanr2/taipei/issues/34) 的自動化漏鍵。右下原符號、負資金、其他視窗／圖表／圖片與正式封包仍保留限制。

[#31](https://github.com/wicanr2/taipei/issues/31) 的[五工具子選單](spec/021-tool-submenus.md) 限十八選取狀態達 CONFORMED。101 份原版來源、186 個來源單點破壞、462 項 Noto 實際墨跡及二十檔乾淨重生通過。82 份正常 HD 收據驗完整面板、原版循環／無效鍵／確認返回及五場景 F12；另 37 份施工存退讀與兩次原版退出通過，共 119 份。大小面板各七項同步更新雜湊與原版 PNG 的竄改，Python 與 Go 均拒絕；真實資源 Go 全套無跳過，存檔及冷讀施工格維持基準。

本批相同唯一正常輸入兩側各 4,080,000,000 步，依 [#36](https://github.com/wicanr2/taipei/issues/36) 預登記每 24,000,000 步抽樣 HD，共 170 次，含十八工具狀態共 99 次、說明一次及城市各層 33 次。原版 RAM、CPU、原畫面、色盤、埠、OPL、讀鍵及檔案操作相同；這是明示抽樣，不代表逐幀對拍。完整存退讀外層預算依 [#35](https://github.com/wicanr2/taipei/issues/35) 改為 600 秒，同 binary／image 乾淨重跑通過，逾時前件保留。Linux、Windows、macOS 兩架構編譯與結構通過；模態外仍保持原版四倍像素，其他視窗／圖表／圖片／場景／動畫、真機及正式封包未完成。#31 與 HD 母項保持開啟。

[#37](https://github.com/wicanr2/taipei/issues/37) 的[城市六功能選單](spec/022-city-function-menus.md) 限六個完整下拉面板、二十九選取達 CONFORMED。137 份原版來源、246 個來源破壞、599 項 Noto 實際墨跡及三十一檔重生先完成 READY 審查。正式產品再以一次正常冷啟動取得 107 份收據，驗全部二十九選取、八十二次讀鍵／release、上下循環、左右跨選單及邊界、六次 Escape 與六場景 F12。完整來源、固定面板與全部區外均由 Python／Go 獨立核對，大小面板十四項重算雜湊及原版 PNG 的有效竄改被拒絕；實際資源 Go 全套 21.819 秒無跳過。

另 37 份正常施工存退讀收據通過，兩次原版退出及全新 EXE 讀回原施工格，存檔雜湊與資金 79980 維持基準，冷讀標題／圖示恢復。相同唯一正常輸入兩側各 5,184,000,000 步，預登記每 24,000,000 步抽樣，共 216 次，含二十九城市選取共 164 次、說明一次與城市各層 14 次；原版狀態相同，非逐幀對拍。Linux、Windows、macOS 兩架構編譯與架構檢查通過，Linux 由現行來源重建逐 byte 相同，35 原始檔及 RAR 不變。證據為 `city-panels-state-audit.json`、`city-panels-state-provenance.json` 及最新 `gui-cold/`；021 原件保留 `gui-cold-before-city-menus/`。模態外、確認後的視窗／圖表、其他圖片／場景／動畫、平台真機與正式封包仍未完成，母項保持開啟。

[#38](https://github.com/wicanr2/taipei/issues/38) 的[檔案視窗與離開確認](spec/023-file-dialogs.md) 限完整兩家族達 CONFORMED。243 份原版完整來源、729 項單像素破壞、九十四字元與輸入邊界、十檔七列捲動、取消、空白、覆寫及離開選否先完成 READY 審查。正式產品取得 64 份正常 HD 操作及 45 份完整施工存退讀收據，共 109 份。Python／Go 驗完整來源、動態字串、使用中色盤、固定參考及全部區外，198 字形墨跡通過；兩家族 F12 均不送入 DOS。十八項重算 PNG／雜湊的有效破壞均被兩核對器拒絕，四個正對照含未用色盤變動通過。243 份實際資源測試、雙選取、十四種資源故障及隔離通過，完整 HD、鍵盤、原點測試無跳過。

正常施工、存檔、兩次原版退出及全新 EXE 讀回原施工格與資金 79980 通過，存檔維持基準。唯一正常輸入的兩側各完整 2,688,000,000 步，預登記每 24,000,000 步 HD 抽樣，共 112 次，含檔案六次、離開三次、說明三次與城市各層六十次。RAM、CPU、原畫面、色盤、埠、OPL、讀鍵、DOS、檔案操作、原版寫入與落地存檔相同，並回對正常 GUI 的畫面、色盤、讀鍵與檔案操作。四架構編譯／結構及原始輸入不變通過。證據在 `file-dialogs-state-audit.json`、`file-dialogs-state-provenance.json`、`file-dialogs-hd/` 與 `gui-file-dialogs-cold/`；022 原件保留。外部刪檔／損壞及儲存故障、其他介面、模態外、圖片／動畫、真機及正式封包仍未完成，母項保持開啟。
