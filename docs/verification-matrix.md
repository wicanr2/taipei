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

目前已驗證正常 GUI 冷啟動、新遊戲、電線施工、檔名輸入及退格、原版實際存檔、
原版離開、全新 EXE 啟動與實際讀檔，兩次均由原版返回 DOS。沒有使用機器快照。
收據為 `workspace/runs/gui-cold/result.json`，來源 35 個檔案雜湊不變。
施工格在全新啟動讀檔後逐 byte 相同。原版音訊已經實際播放器輸出，隔離 monitor 非靜音；合成分段連續、原版狀態不變及平台限制另見[音訊契約](spec/009-opl2-audio.md)。技術擷取不當作人耳試聽。

HD 離線及動態比較原型只涵蓋水面、沙地與樹冠。素材撤除、來源／色盤失配、原版視窗回退、切換與區外像素檢查通過；冷啟動施工存退讀通過，存檔與原版模式相同。詳見[離線契約](spec/008-hd-material-prototype.md)與[動態契約](spec/010-hd-live-prototype.md)。字型、正式切換與其他 HD 批次尚未定案，不當成 #7 或 #8 的正式完成證據。三平台封包仍未建立。
