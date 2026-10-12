# 031：五語系操作說明

狀態：CONFORMED，2026-10-12，限本檔八列 Help 呈現與前端操作。Issue：[#50](https://github.com/wicanr2/taipei/issues/50)，依賴 [030](030-hd-localization.md)。

使用者看過兩個按鍵方案後回覆「同意」，採建議方案：Shift+F1 開 Help，保留原版 F1 離開。

## 證據與操作前沿

- 已證實：022 正常 GUI 的 F1 開啟離開選單，唯一選項為「返回 DOS」。005 的存退讀路徑也使用此入口。現行前端將 F1 以 scan `3Bh`／`BBh` 送原版；014 保留 F1–F10。
- 已證實：004 的城市方向鍵依焦點移動，Tab／Enter 切換地圖及工具列焦點，Space 在工具列確認、在地圖施工。Help 不把 Enter 誤寫成城市工具確認。
- 已確認的新增功能：左、右 Shift 均可配合 F1 開 Help，原版 F1 不重映射。Help 是前端功能，沒有原版 Help 的對拍主張。

## 可撤回原型

文字由 [ui.tsv](../../workspace/app/locales/ui.tsv) 提供。工具 [locale-prototype](../../workspace/app/cmd/locale-prototype/main.go) 的 [help.go](../../workspace/app/cmd/locale-prototype/help.go) 在真實 1280×800 HD 收據上繪製兩個按鍵方案、五語系共十張 Help。原始圖、固定 Noto、Docker 與 Go 版本沿 030，不執行 DOS，也不依候選按鍵猜測原版行為。

原型位置 `workspace/prototypes/hd-style/locale-help-draft-r1/`。全部 111 鍵、五語系、733 種字元無缺字；含六標題、面板與 Help 共 223 處實際墨跡落在安全矩形內。原型階段只驗字墨與操作示意；正式接入及正常 GUI 結果見下節。

該版實際文字快照為輸出內 `catalog-source.tsv`，SHA-256 `3e8615479950f17da1cb3f33d284f0270449fb3174b75938f18847ce5cc74784`，與原型收據一致。正式 TSV 後續新增四個語言控制／錯誤／視窗標題鍵；重生這版 Help 時以此唯讀快照作輸入。快照與含原版／衍生素材的圖只留本機，不成為第二份正式翻譯來源。

Help 內容目前包含城市選單、焦點、方向、Space、選單確認／取消、F11 及 F12。所有語言的說明文字只在 TSV；不翻譯按鍵送出的 DOS 值。完整遊戲攻略、原版未確認快捷鍵、滑鼠施工與規則說明未納入本批。

## 正式契約

- 呈現：沿已展示的 `help-shift-f1-<語言>.png`，面板為 `(40,40)–(1240,760)`，八列操作與底部 Esc 提示均取 TSV 穩定文字鍵。區外透明，不改地圖或原版畫面緩衝。
- 語言：沿當前 F11 選擇。Help 中 F11 開語言面板，選定或取消後回 Help；選定時立即更新 Help 與六標題，語言仍寫入獨立 `frontend-settings.json`，不寫 SAV。
- 開關：Shift 按住時新按 F1 開啟或關閉 Help，Esc 關閉。單按 F1 仍送 `3Bh/BBh`。Help 在原版／HD 兩種呈現皆可開啟，F12 可切換底層呈現。
- 輸入：開啟前補送已轉送按鍵及滑鼠的放開事件。Help／語言面板與關閉後持鍵隔離期間，停止 VM 推進，不送鍵盤、文字及滑鼠操作。關閉後等待所有實體鍵與滑鼠按鈕放開，丟棄放開當幀文字；Shift+F1 的 F1 不得穿透，Caps Lock 鎖定狀態不重設。
- 狀態與輸出：只新增前端 Help 開關、影像及收據欄位。原版 CPU、記憶體、虛擬時間、原畫面、讀鍵、規則、亂數與資料不由 Help 修改；開啟前必要的放開事件另記錄，不冒稱沒有事件。
- 故障：啟動時驗五語系 Help 必要鍵、Noto 字形與文字安全矩形。外部 TSV 不合格沿 030 回退隨附 TSV。固定字型或授權不合格時停用前端面板並保留原版輸入，不用錯誤字型覆蓋。無法排版不得顯示殘缺面板。

固定輸入為 RS201.EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`；Noto Sans CJK TC Regular Sans2.004 字型雜湊 `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4`、OFL 雜湊 `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2`。正式 TSV 115 鍵雜湊 `afe340850774c2b579b8808e7eac1c89dd24e4332ff978b511157fa258ab59ab`。dosgolem 固定 `a9714ebdab2ad6b529f81225472680f2b11f2842` 加既有七個本地修補；Go 1.24.13、Docker image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`。本項沒有新增反組譯位址，原版操作證據回鏈 004／005／022。

## 驗收與停止線

先登錄再執行：實際 Noto 五語系 Help 面板與確認前固定原型逐像素相同，區外透明；缺鍵、缺字、過長文字須拒絕。既有設定故障測試沿 030，不複製另一份設定機制。

正常 GUI 從冷啟動進城市，驗左右 Shift+F1、五語系 Help、F11 返回 Help、F12、Esc 與同鍵關閉、按住關閉鍵時隔離、鍵盤／文字／滑鼠不穿透及原版 F1 返回 DOS 選單仍可用。面板內比較 CPU、步數、原畫面、palette、讀鍵及檔案操作，擷取本次程式自行產生的收據。固定原型比較證明呈現契約，正常視窗證明輸入契約，均不外推整款原版 parity。

不自行恢復既有長時間狀態抽樣、#48 圖表驗收或正式封包。完整攻略、未確認操作、其他介面翻譯、SAV 存退讀與 Windows／macOS 真機不在本項完成聲明內。圖像及原版／衍生資料僅留本機；原創程式、TSV、規格及重現腳本可提交私人 repo。

## 已完成的驗證

- [help_test.go](../../workspace/app/internal/localui/help_test.go)：實際固定 Noto，五語系完整面板逐像素與確認前原型相同，全部區外透明；缺鍵、缺字及超長字串按指定原因拒絕。原語言面板、catalog／設定、鍵盤及六標題專項回歸通過。
- [正常 GUI 工具](../../workspace/tools/help_ui_playtest.sh) 的 `workspace/runs/help-ui-cold-r1/verification.json`：全新 EXE 經片頭／主選單至城市，左右 Shift 先送入原版後開 Help，確認配平 `AAh/B6h`；Shift+F1 沒有送 `3Bh/BBh`。Esc 關閉時保持開啟鍵不放，VM 仍不推進；全部放開後恢復，BIOS Shift flags 歸零。
- Help 內鍵盤、文字及滑鼠隔離，F11 五語系各回 Help 並保存設定，取消仍留原語言，面板固定像素全部相同。F12 往返，原版模式全部面板區外與同幀原畫面四倍像素相同；同鍵關閉後原版 F1 開離開選單，Esc 返回城市，Tab／方向鍵重新送原版。已檢視實際英文 Help。
- Help 期間 CPU、步數、原畫面、palette、BIOS ticks／修飾旗標、原版讀鍵與檔案操作不變。此為前端暫停契約，沒有執行長時間 RAM／亂數抽樣，沒有將原版 F1 選單測試稱為原版正常退出。
- Linux amd64、Windows amd64、macOS amd64／arm64 編譯與架構檢查通過。Windows 編譯出現未修改 YMFM C++ 的邊界警告，建置退出 0；沒有因此修改音訊或擴張本項。Wine、Windows／macOS 真機與正式封包未驗。

已驗 Linux binary SHA-256 `6604e3d0c611f8744c56d0f0f679986680d5cb3a5a6d3e3968550bb22f487ad8`，現行 `workspace/runs/taipei-preview` 與保留的 `taipei-preview-help-r1` 相同。Windows 雜湊 `8bbca95e4494937482bc3a56342cae6c4453f88bd160af563eac241d848df658`；macOS amd64 `4bde30e6662673e3f1557aad11ef296b15e19723b675b8ca1d96e58bdb172ff7`、arm64 `7212d1bac602dbb319cc351267d8885bf7fa6c296ea64c80583ebd3914c35802`。輸出與 `preview-cross-*.txt` 僅留 workspace，不作正式發行包。
