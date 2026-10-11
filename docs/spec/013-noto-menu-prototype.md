# Noto 主選單文字動態原型

狀態：**DRAFT**。對應 [#27](https://github.com/wicanr2/taipei/issues/27)，以使用者在 [#18](https://github.com/wicanr2/taipei/issues/18) 選定的 Noto 高清黑體接入 [010](010-hd-live-prototype.md) 比較原型。正式 F12 切換見 [014](014-live-theme-switch.md)；使用者已確認全部圖片與操作介面，後續文字依 [015](015-full-hd-scope.md) 與 #31 執行。

## 固定字型與已展示樣式

- Noto Sans CJK TC Regular Sans2.004，SHA-256 `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4`。
- SIL OFL 1.1 授權檔 SHA-256 `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2`；取得入口 [font_source.py](../../workspace/tools/font_source.py)，離線參考重生入口 [font_prototype.sh](../../workspace/tools/font_prototype.sh)。
- 已展示 `comparison-fonts.png` SHA-256 `2ec3eea917c9dc173b31e30b5dbd9042f4ff4fca3f0f62a978281a3db5708c28`；其中 `noto-font.png` SHA-256 `feefbf252a77ab01322c72654a2c6d8b7cb42118494949604f194c20d4f331da`。兩者保存在本機 `workspace/prototypes/hd-style/font-comparison/`，含原版畫面而不入 Git。
- 字級 56 px、72 DPI、不 hinting；六個標題為「離開、檔案、市長、圖表、災難、環境」，沿用已展示的文字、位置與配色。

## 證據與呈現邊界

固定 EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`，ROM 及 dosgolem 依 [持續運行研究](../re/007-running-city.md)。字型只寫入前端 1280×800 呈現緩衝，不讀寫 DOS 文字或遊戲語意資料。

既有城市模式、原版阻塞、色盤、頂部 UI、年度視窗及已完成地圖原點條件都通過後，才替換六個完整標題矩形。原生矩形為 `(7+44*i,10,34,17)`，輸出矩形為 `(28+176*i,40,136,68)`，`i=0..5`。字型墨跡原點相對矩形為 `(12,54)`。原生 F1–F6、邊框與點擊位置保持原版。矩形外的地景及後續工具圖示，分別依 [010](010-hd-live-prototype.md) 與 [016](016-city-tool-icons.md) 核對。

原版正常收據的矩形色號使用 15、21、27，其 RGB 串接 SHA-256 為 `1acb802a98b9fb298f4d68b1f4e5a74b0d3bfca88cba6d347795dbafbab63a1e`。這三色失配時，只回退文字矩形；地景仍依自己的色盤與來源條件判定。字型或授權缺失、雜湊失配、缺 glyph 或墨跡越界，也只回退文字，不猜換另一套字型。後續 [016](016-city-tool-icons.md) 的圖示獨立驗來源及像素，不將文字矩形外的圖示區直接免驗。

證據等級：已證實，限正常城市完整頂部指紋、已展示的六個標題、安全矩形與實際色盤。這不是全遊戲文字來源或動態字串解碼契約。開場、視窗、建物與未辨識文字保留原版；整幀回退狀態不另外覆字。

## 預登記驗證

- 六個標題的實際 RGBA 與已展示 `noto-font.png` 的相同矩形逐像素相同；glyph 與實際墨跡皆在安全矩形內。
- 文字矩形外不新增差異；原生 F1–F6 與原版色號不變。
- 字型撤除、字型損壞、授權損壞及文字色盤失配有有效負對照，回退後沒有前幀殘影。
- 原版／HD 切換、模態、年度視窗、取消返回、正常施工、存退讀及冷啟動讀檔後恢復文字。
- 同一正常鍵盤輸入的原版機器狀態與存檔不因 Noto 覆字而改變。
- Linux、Windows、macOS 兩架構研究前端重編譯；真機與正式封包另驗。

含 Noto 的單幀封裝以 `receipt-check -dir /workspace/runs/gui-cold -font-reference /workspace/prototypes/hd-style/font-comparison/noto-font.png` 核對。若另含 [016](016-city-tool-icons.md) 的圖示，須追加 `-ui-reference /workspace/prototypes/hd-style/city-icons-b-v1.png`。參考圖須固定雜湊，各矩形逐像素比較，其他區域仍依原版或既有地景規則驗證；不把新增區域直接列為免驗區。沒有 Noto 或圖示的歷史封裝仍可使用原有命令。

## 已執行驗證

使用 [menu.go](../../workspace/app/internal/hd/menu.go) 在初始化時核對字型、授權、glyph 與墨跡，預先繪製六個標題；每幀只在上述完整來源條件成立時覆繪。原版色號、DOS 字串、輸入與點擊區域不變。

- `internal/hd`、`internal/original` 的實際資源測試通過。六個標題像素與固定參考相同；字型撤除、字型或授權損壞、文字色盤失配皆回退，且正常地景保持覆繪。原有模態、年度視窗、來源、材質與原點防護維持。
- `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 通過正常冷啟動、原版施工、檔名退格、存檔、原版退出、全新 EXE 讀檔與再次原版退出。存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，與覆字前相同；施工格冷讀相同。
- [hd_font_check.py](../../workspace/tools/hd_font_check.py) 獨立核對 35 份原子收據，11 份有六個 Noto 標題、24 份保留原版文字。實際字型像素與已展示參考相同，原生 F1–F6 及文字與地圖外像素保持原版，冷讀後恢復 Noto。結果 `workspace/runs/gui-cold/font-verification.json`。
- 更新後 `receipt-check` 通過上述 35 份收據與覆字前的 35 份封裝。[hd_font_negative.py](../../workspace/tools/hd_font_negative.py) 分別破壞 `(28,40)` 的字型像素與 `(200,40)` 的矩形間原版像素，並同步更新呈現雜湊，兩者仍被拒絕。結果 `workspace/runs/noto-negative/result.json`。
- `presentation-audit -require-budget -require-font` 重播固定正常 GUI 收據，兩側各 2,400,000,000 步的原版 RAM、CPU、原生畫面、色盤、埠值、OPL 暫存器及讀鍵相同。包含 3610 次 Noto 覆繪與 107 次年度視窗回退；狀態 SHA-256 `b940de4f9be1b6b322152947e8c3d658c6add061d629368a9c00e3241d32e734`，結果 `workspace/runs/noto-state-audit.json`。
- Linux amd64、Windows amd64、macOS amd64／arm64 研究前端重新編譯通過。工具版本與固定 image 沿用 [持續運行研究](../re/007-running-city.md)，Windows 保留原有 YMFM 編譯警告；沒有新增真機或封包驗收聲明。

覆字前的正常 GUI 收據保留於 `workspace/runs/gui-cold-before-noto/`。本次只完成已辨識的六個標題動態原型；其他文字與場景仍回退原版，不將 DRAFT 升為正式 HD 完成。
