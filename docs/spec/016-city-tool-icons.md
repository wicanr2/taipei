# 十四個城市工具圖示

狀態：**CONFORMED，限研究前端十四個圖示內部**。對應 [#29](https://github.com/wicanr2/taipei/issues/29)，屬於 [完整 HD 範圍](015-full-hd-scope.md) 的第一批；介面框架、文字、其他場景與正式前端另驗。本批先完成來源審查與 READY 契約，再實作及驗證。

## 原版來源與證據

固定 `RS201.ROM` SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`。成員 1 位於 ROM 檔案偏移 `1888`，長度 `10774`，前四 bytes 為 `40 01 C8 00`，寬 320、高 200。後續非零 byte 為單點色號；零 byte 後接色號與重複次數，次數直接使用，不加一。完整輸入消耗後恰產生 64,000 色號，SHA-256 `a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7`。

證據來源：[完整盤點工具](../../workspace/tools/full_asset_catalog.py)，Python 3.13.16，image `sha256:bf44cdfcb76cd3b41e879bc058fc37ec5872002ccfde7fcb765e218cde0cd79c`。上述數值均為 ROM 檔案偏移，不是 IDA 或執行期位址。解碼其餘壓縮成員的語意仍逐項標示；本批只使用這份固定成員及下列已證實矩形。

- 已證實：原版正常 `city-map-capture.zip` 的工具列 `(270,0)-(320,171)` 與成員 1 解碼結果逐色號相同。
- 已證實：電線工具的選取與確認只改 `(296,4)-(318,26)` 的 84 個外框色號，內部 20×20 不變。證據是既有正常 `power-tool`、`power-confirm`、施工與存讀檔收據。
- 已證實：十四個圖示內部位置為 `(273+24*(i%2),5+24*(i/2),20,20)`，`i=0..13`。前端對應矩形四倍為 80×80，原版外框與命中範圍保留。

## HD 資產與繪製

本機 `workspace/prototypes/hd-style/city-icons-b-v1.png` 為 320×320、4×4 atlas，依原版由左至右、由上至下的十四個圖示排列，最後兩格不使用。SHA-256 `9ad97735f45cab2c968e23d8f1d6924c6b1937854fa4cda1c1c7a5ee90a089ab`。使用內建 imagegen，原版圖示 atlas 為內容參考，已批准 B 比較圖為風格參考。完整提示、生成原圖及正規化資料見同目錄的 `city-icons-b-v1.prompt.txt` 與 `city-icons-b-v1.source.json`，只留本機。

沿用城市模式、頂部指紋、年度視窗、原版阻塞及已完成原點條件。十四個完整來源圖示的色號聯集共 88 色，依色號遞增串接實際 RGB，SHA-256 須為 `39592c7fa30a9605b79cc18217f320484e16e3d301c6c8a2a4e992951b32a759`。每個圖示須完整 400 個來源色號相同才覆繪；失配只回退該圖示。素材缺失、損壞、尺寸或雜湊失配時全部圖示回退，不換猜測素材。

色盤審查勘誤：最初要求完整 256 色相同，實際正常 `pause`、工具選取及施工收據顯示色號 232、233、240、241 會交換 RGB。這四色都不在上述來源聯集，沒有改變任何圖示內部色彩。改依完整來源使用的 88 色核對，保留正常閃爍外框與原版畫面；不是針對單一收據放寬來源條件。

每幀先重建原版，再覆繪目前符合條件的圖示。不得修改原版色號、選取外框、鍵盤、滑鼠座標或存檔。F12 關閉後清除圖示，重新開啟時由當前原版來源恢復。收據記錄覆繪數、14 位元圖示遮罩與回退原因。

## 預登記驗收

- 真實城市十四個圖示的 RGBA 與固定 atlas 逐像素相同。正常電線選取及確認的外框保持原版，圖示內部仍可覆繪。
- 破壞一個圖示來源時該圖示回退，其餘十三個保留；色盤失配、缺素材、損壞素材、模態與年度視窗回退。來源、色盤及原版色號不改寫。
- 原版／HD 往返沒有殘影；圖示外只允許既有地景與 Noto 矩形改動，其他像素逐點核對原版。
- 正常 GUI 冷啟動、新遊戲、工具選取、施工、存檔、原版退出與全新 EXE 讀檔；施工格與存檔雜湊仍與原版一致。
- 獨立核對器從原版來源重算圖示遮罩，逐像素比對資產。破壞圖示或外框像素、同步更新呈現雜湊的負對照仍應拒絕。
- 固定正常 GUI 輸入及初始狀態，比較有／無此覆繪的 RAM、CPU、原版畫面、色盤、埠值、OPL 與讀鍵，要求相同且實際經過圖示覆繪。

本批無遊戲資料或存檔格式變更。原版與衍生圖示只留本機，不入 Git／Release；完整介面與所有圖片尚未完成時，#29 及母項保持開啟。

## 已執行驗證

實作為 [icons.go](../../workspace/app/internal/hd/icons.go)，獨立核對器為 [hd_icons_check.py](../../workspace/tools/hd_icons_check.py)。建置與 GUI image 沿用 [007](../re/007-running-city.md)，Go 1.24.13。容器內實際資源測試使用 `TAIPEI_HD_ORIGINAL=/orig`、`TAIPEI_HD_MATERIALS=/workspace/prototypes/hd-style`、既有正常收據及 `go test -mod=readonly -p 1 ./internal/hd ./internal/original`。

- Go 測試通過完整十四圖示、選取外框、單圖來源失配只回退一個、圖示色盤失配、素材撤除與損壞、F12 清除及恢復；原版色號未改寫，既有地景、字型、模態與年度視窗測試通過。
- `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 通過冷啟動、新遊戲、切換、電線施工、檔名退格、原版存檔與退出、全新 EXE 讀檔及再次原版退出。施工格冷讀相同，存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。收據為 `workspace/runs/gui-cold/result.json`。
- `hd_icons_check.py --original /orig --materials /workspace/prototypes/hd-style --receipts /workspace/runs/gui-cold` 通過 35 份收據；11 份完整十四圖示、24 份回退。原版來源重算遮罩、固定 atlas 像素、選取外框與冷讀恢復皆相符。結果為 `icons-verification.json`，同目錄 Noto 獨立核對亦通過。
- `receipt-check -dir /workspace/runs/gui-cold -font-reference /workspace/prototypes/hd-style/font-comparison/noto-font.png -ui-reference /workspace/prototypes/hd-style/city-icons-b-v1.png` 通過全部封裝。文字、矩形間隙、圖示與外框各破壞一像素，再同步更新呈現雜湊，四個負對照仍被拒絕；結果為 `workspace/runs/icons-negative/result.json`。
- `presentation-audit -receipt /workspace/runs/gui-cold-before-icons/uncover-power-capture.zip -require-font -require-icons` 重播相同正常輸入，兩側各 1,200,000,000 步；完整 RAM、CPU、原版畫面、色盤、埠值、OPL 與讀鍵相同，實際經過 716 幀完整圖示覆繪。狀態 SHA-256 `9a439a04692635051b9967b5e204f18073c87f1d16fe4d7495eba26c22898e68`，結果為 `workspace/runs/icons-state-audit.json`。
- Linux amd64、Windows amd64、macOS amd64／arm64 研究前端重編譯通過。Windows 保留既有 YMFM 編譯警告；未新增真機或封包驗收聲明。

覆繪前收據保留於 `workspace/runs/gui-cold-before-icons/`。首次 GUI 外層 300 秒逾時的證據保留於 `gui-icons-timeout/`；第一個原版程序已正常退出，逾時發生在第二次冷啟動。將驗證器有界逾時改為 480 秒後，在同一 image、相同輸入乾淨重跑通過，分類為驗證器時間上限問題。
