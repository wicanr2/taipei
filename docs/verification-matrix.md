# 驗收矩陣

本檔定義證據與完成條件。工作狀態只看 [GitHub Issues](https://github.com/wicanr2/taipei/issues)，
目前真相由 [CONTEXT.md](../CONTEXT.md) 保存。

| 範圍 | Issue | 必要證據 | 完成限制 |
|---|---|---|---|
| 治理 | [#1](https://github.com/wicanr2/taipei/issues/1) | private／Issues 回讀、文件入口、排除規則、提交與推送 | 不證明遊戲可執行 |
| 原版輸入 | [#2](https://github.com/wicanr2/taipei/issues/2) | 檔案清單、SHA-256、啟動方式與版本證據 | 來源未知不猜填 |
| dosgolem 啟動 | [#3](https://github.com/wicanr2/taipei/issues/3) | 固定 commit、真實入口、可操作畫面、重播與缺口 | 未實際走到的路徑不算支援 |
| 原版前端與存檔 | [#4](https://github.com/wicanr2/taipei/issues/4) | 正常 GUI、核心操作、存退讀與來源雜湊 | direct-entry 不替代 GUI |
| HD 原型 | [#5](https://github.com/wicanr2/taipei/issues/5) | 已證實繪圖來源與同狀態比較原型 | 不自動進正式路徑 |
| HD 契約 | [#6](https://github.com/wicanr2/taipei/issues/6) | 使用者批准樣式、平台與 READY 規格 | 重大取捨不得推定同意 |
| HD 接入 | [#7](https://github.com/wicanr2/taipei/issues/7) | 來源／動畫／遮擋／清除／切換，機器狀態與存檔比較 | 圖片存在不代表正確播放 |
| 玩家抽樣 | [#8](https://github.com/wicanr2/taipei/issues/8) | 先登記情境，正常冷啟動至核心操作及存退讀；有效負對照 | 限實際驗證範圍，不宣稱全程試玩 |
| 交付 | [#9](https://github.com/wicanr2/taipei/issues/9) | 實際封包啟動、權利、manifest、SHA-256 與平台結果 | Wine、結構及真機驗證分開記錄 |
| 全部來源盤點 | [#28](https://github.com/wicanr2/taipei/issues/28) | 所有成員、圖像與別名、正常可見狀態、未知來源及覆蓋清單 | 可解碼不等於繪製語意已證實 |
| 城市介面 | [#29](https://github.com/wicanr2/taipei/issues/29) | 工具圖示、外框與選取狀態逐像素核對，原版命中範圍不變 | 十四個圖示內部不代表完整介面 |
| 全部地圖 | [#30](https://github.com/wicanr2/taipei/issues/30) | 地景、道路、電線、建物、設施與災害的來源、遮擋及相位 | 未接入或未知回退仍列未完成 |
| 全部文字與視窗 | [#31](https://github.com/wicanr2/taipei/issues/31) | 原始文字來源、完整字串、實際 Noto 墨跡、安全矩形與正常 GUI | 字模候選不直接作正式覆字規則 |
| 場景與動畫 | [#32](https://github.com/wicanr2/taipei/issues/32) | 開場、選城、難度、插畫、事件、評分與動畫相位 | 單張素材不證明完整播放 |

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

[#29](https://github.com/wicanr2/taipei/issues/29) 首批十四個工具圖示內部已接入。[016](spec/016-city-tool-icons.md) 限本批範圍達 CONFORMED：35 份正常 GUI 收據中，11 份完整覆繪十四個圖示、24 份回退；固定 atlas、獨立重算來源遮罩、選取外框及冷讀恢復皆通過。破壞文字、矩形間隙、圖示及選取外框後同步更新呈現雜湊，四個負對照均被拒絕。兩側各 1,200,000,000 步的原版狀態相同，實際包含 716 幀圖示覆繪；存檔雜湊保持相同。#29 仍須其餘框架、狀態與操作提示，母項保持開啟。

[#28](https://github.com/wicanr2/taipei/issues/28) 的[完整初盤](re/008-full-asset-inventory.md)保留 118 個成員、1317 筆圖片來源、1220 個不同圖像及未知項。依 [#31](https://github.com/wicanr2/taipei/issues/31) 另取得 402 個字模與原始字碼，十二字正常畫面正對照及十二個單點破壞負對照通過，詳見[字模研究](re/009-chinese-font-sources.md)。候選搜尋尚未接入正式覆字，不能據此宣稱其餘文字已完成。
