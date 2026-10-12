# 031：五語系操作說明

狀態：DRAFT。Issue：[#50](https://github.com/wicanr2/taipei/issues/50)，依賴 [030](030-hd-localization.md)。

使用者要求新增 Help，並提出「maybe use F1」。Help 需求已授權，按鍵候選仍須處理原版衝突。

## 證據與操作前沿

- 已證實：022 正常 GUI 的 F1 開啟離開選單，唯一選項為「返回 DOS」。005 的存退讀路徑也使用此入口。現行前端將 F1 以 scan `3Bh`／`BBh` 送原版；014 保留 F1–F10。
- 已證實：004 的城市方向鍵依焦點移動，Tab／Enter 切換地圖及工具列焦點，Space 在工具列確認、在地圖施工。Help 不把 Enter 誤寫成城市工具確認。
- 新功能提案：Shift+F1 開 Help 並保留原版 F1，或 F1 開 Help 並將原版離開移至 Shift+F1。後者需更新頂部按鍵提示及輸入契約。待使用者選定前，不攔截任何 Help 按鍵。

## 可撤回原型

文字由 [ui.tsv](../../workspace/app/locales/ui.tsv) 提供。工具 [locale-prototype](../../workspace/app/cmd/locale-prototype/main.go) 的 [help.go](../../workspace/app/cmd/locale-prototype/help.go) 在真實 1280×800 HD 收據上繪製兩個按鍵方案、五語系共十張 Help。原始圖、固定 Noto、Docker 與 Go 版本沿 030，不執行 DOS，也不依候選按鍵猜測原版行為。

原型位置 `workspace/prototypes/hd-style/locale-help-draft-r1/`。全部 111 鍵、五語系、733 種字元無缺字；含六標題、面板與 Help 共 223 處實際墨跡落在安全矩形內。此為字墨與操作示意，尚未接入 Help、確認內容或正常 GUI 驗收。

該版實際文字快照為輸出內 `catalog-source.tsv`，SHA-256 `3e8615479950f17da1cb3f33d284f0270449fb3174b75938f18847ce5cc74784`，與原型收據一致。正式 TSV 後續新增四個語言控制／錯誤／視窗標題鍵；重生這版 Help 時以此唯讀快照作輸入。快照與含原版／衍生素材的圖只留本機，不成為第二份正式翻譯來源。

Help 內容目前包含城市選單、焦點、方向、Space、選單確認／取消、F11 及 F12。所有語言的說明文字只在 TSV；不翻譯按鍵送出的 DOS 值。完整遊戲攻略、原版未確認快捷鍵、滑鼠施工與規則說明未納入本批。

## 後續閘門

按鍵選定後整理正式契約，需明確說明開啟／關閉、原版 F1 去向、五語系、F11／F12 互動、VM 暫停與返回，以及輸入放開隔離。正式 Help 前須達 READY，並以正常 GUI 短流程驗收。既有長時間狀態抽樣與圖表驗收不自行恢復。
