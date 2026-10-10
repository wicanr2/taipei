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

目前已驗證冷啟動到城市選擇，主選單雙重播一致。四項通用缺口的測試與原版收據見
[啟動基線](re/002-dosgolem-startup.md)。GUI、核心操作、存退讀與 HD 尚未通過。
