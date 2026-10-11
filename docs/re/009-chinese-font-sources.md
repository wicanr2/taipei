# 中文字模、字碼表與正常畫面來源

日期：2026-10-11。對應 [#31](https://github.com/wicanr2/taipei/issues/31)，入口：[CONTEXT.md](../../CONTEXT.md)。本份保存文字來源研究，尚未把候選辨識接進 HD。

## 固定來源與定位

`RS201.ROM` SHA-256 沿用 [008](008-full-asset-inventory.md)。以下全部為 ROM 檔案偏移，不是 IDA 或執行期位址。

| 成員 | 檔案偏移 | 長度 | SHA-256 | 已查證內容 |
|---|---:|---:|---|---|
| 56 | 935884 | 1014 | `50f4718a24c1c0e4bd27955c8753c16970fbabeef1a667ea6b7f0ddf10b33998` | 標頭為 5、7、7；ASCII 對應尚未逐字驗證 |
| 57 | 936898 | 12066 | `6b7bd36caf8dc22fa968a10542e10b49463a23014e58155c687510b61a0ef1eb` | 15×15 字模，stride 30，402 筆 |
| 58 | 948964 | 806 | `3a86b2284023f19a6a59b41cf138ade536f31c0e49d693f4664bc7d596d5af46` | 16 位元數量 402，後接 402 組兩 byte 字碼 |

工具：[font_catalog.py](../../workspace/tools/font_catalog.py)，Python 3.13.16，image `sha256:bf44cdfcb76cd3b41e879bc058fc37ec5872002ccfde7fcb765e218cde0cd79c`。字模聯絡圖與完整字碼 JSON 留在 `workspace/runs/font-catalog/`，不入 Git。

容器內重生：`python /workspace/tools/font_catalog.py --original /orig --receipts /workspace/runs/gui-cold-before-icons --out /workspace/runs/font-catalog`。原版唯讀，輸出限上述目錄。

## 已證實及候選

- 已證實：成員 57 的六 byte 標頭為三個 16 位元小端序數 `15,15,30`，餘下恰為 `402×30` bytes。每字十五列，每列兩 byte、最高位在左，保留十五個可見位元。
- 已證實：十二個主選單字「離開、檔案、市長、圖表、災難、環境」的完整 15×15 前景遮罩，與正常城市 `(x,11)` 的白色號 15 逐點相同。x 依序為 `10,26,53,69,98,114,141,157,185,201,229,245`，原始字模索引逐項保留於 JSON。
- 已證實：402 份完整原始字模的 SHA-256 互不重複。空白字模不作畫面搜尋，不能靠空白推定字串。
- 已證實：上述十二字各移除一個實際墨跡像素，皆不再符合任何完整字模；原始畫面保持不變。十二筆負對照及座標保留於 JSON，不只檢查搜尋工具能找到正樣本。
- 強推論：成員 58 的相同序號提供各字模的 Big5／CP950 字碼。Python `cp950` 能解出全部 402 組，但編碼可解不代表全部字形語意已確認；原始兩 byte 與字模索引均保留。
- 候選：十二個已走過的正常場景抽樣，在固定六種前景色找到完整字模遮罩。說明視窗 74 筆、檔案選單 26 筆、存檔視窗 16 筆。這是圖像候選，不是完整文字、字串順序或背景恢復契約。

中文字模來源已直接取得，無須先掃描整個 executable 或猜字串編碼。後續只追玩家可見文字的繪製、字距、背景、陰影與清除；不同大小的開場題字仍依圖片批次處理。

## 語意與停止線

完整聯絡圖已人工檢視。字碼表中有稀有或異體字，例如索引 101 的 `F5 A4` 解為「鶪」、索引 104 的 `C9 F3` 解為「机」；未完成字形語意審查前不自動校正，也不直接拿解碼字取代原版字模。其餘尚未審查的字同樣保留原始證據。

一般圖片可能偶然包含相同二值遮罩，文字覆繪還需要原版文字欄位、完整字串／繪製呼叫、背景與安全矩形等證據。不能只靠字模搜尋就覆蓋所有畫面。#31 仍需各類視窗與動態數值的 READY 契約、實際 Noto 墨跡及正常 GUI 驗收。

## 共用文字呼叫端與正常重播

工具為 IDA Pro 9.4，沿用既有 image `sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab`、UID/GID 1000:1000 及唯讀 `workspace/runs/ida-19/event-keys.i64` 副本。固定 EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。查詢工具為 [ida_text_probe.py](../../workspace/tools/ida_text_probe.py)，輸出在 `workspace/runs/ida-31/`；保留原函式名、bytes、原始運算元及各自定位，不改正式資料庫。

| 原始定位 | 附加語意與等級 | 證據 |
|---|---|---|
| IDA 線性 `sub_13274`，`132C5h–132F6h` | 已證實，六個頂部標題的呼叫迴圈 | DS 相對 `8D4h+5*i` 取零結尾字串，迴圈六次，push 色號、字串遠指標、y、x，再 call `sub_143DA` |
| IDA 線性 `sub_143DA`，`143DAh–144B3h`；EXE 檔案偏移 `25562–25779` | 已證實，限此函式，按原始雙 byte 字碼查表後繪字 | `1444Fh–14471h` 比較字碼表；`14476h–1448Fh` 用索引乘 30、加標頭 6，送字模遠指標；中文 x 增 16 |
| IDA 線性 `sub_15A99`，`15A99h–15AE4h` | 已證實，限此函式，透明墨跡寫入 15×14 | 列迴圈 14、行內位元 15，只有設定位元寫入色號；第十五列字模資料未被此函式繪製 |
| IDA 線性 `sub_15BCE`，`15BCEh–15C18h` | 強推論，5×7 ASCII 透明墨跡；本次沒有實際呼叫 | 原始指令列迴圈 7、行內位元 5；`sub_143DA` 的 ASCII 路徑字距 6、y 加 4，指標公式相當於 `header6+7*(code-32)` |

立即數等於 DS 相對字串位移只作假說線索，經完整函式資料流才附上表語意。沒有直接 xref 的文字不被判定為未使用。容器內查詢入口為 `idat -A -S"/tools/ida_text_probe.py text-render 0x143da 0x15a99 0x15bce" <一次性資料庫>.i64`，工作目錄須為明確可寫輸出，來源與工具唯讀。

[text-source-audit](../../workspace/app/cmd/text-source-audit/main.go) 以 Go 1.24.13 及本專案固定 dosgolem 補丁版本，重播 `gui-cold-before-icons/uncover-power-capture.zip` 的正常輸入。沒有快照或直接進入函式；在原版真正呼叫時唯讀記錄字串、參數、字模及前後繪製緩衝。

- 已證實：兩個 byte 字碼、字模索引與 ROM 的 30-byte 原始字模逐筆相符。六筆文字呼叫共十二字，座標、色號與 `sub_13274` 的原始資料一致。
- 已證實：十二字繪製前的 15×14 區域全為色號 21；繪製後恰為原背景加原版字模的色號 15 墨跡，與正常城市原版畫面逐點相同。移除一個墨跡像素的十二個負對照均不符合原版輸出。
- 原版同狀態驗證：1,200,000,000 步後的完整狀態 SHA-256 `9a439a04692635051b9967b5e204f18073c87f1d16fe4d7495eba26c22898e68`，與既有無文字觀察基線相同。重播與核對輸出分別為 `text-runtime.json`、`text-runtime-verification.json`。
- 範圍限制：這條正常路徑只呼叫上述函式六次，不是全部遊戲文字。成員 22 的完整說明視窗含已烘製文字，見 [008](008-full-asset-inventory.md)；「說、明、目、標」等字不在 402 字子集。不能只替換共用字庫就宣稱所有介面已用 Noto。

在固定 GUI image 內建置 `go build -mod=readonly -p 1 -trimpath -o /out/text-source-audit ./cmd/text-source-audit` 後，執行 `text-source-audit -original /orig -receipt /runs/gui-cold-before-icons/uncover-power-capture.zip -out /out/text-runtime.json -expected-state 9a439a04692635051b9967b5e204f18073c87f1d16fe4d7495eba26c22898e68`。原版與收據唯讀，輸出只寫 `/out`。實際函式證據與像素比對已足以限定這條路徑，停止擴挖其他不相干 helper；後續依可見視窗逐批重繪與覆字。

## 底部動態欄位的後續證據

2026-10-11，依 [#31](https://github.com/wicanr2/taipei/issues/31#issuecomment-6107137732) 以 [footer_catalog.py](../../workspace/tools/footer_catalog.py) 重建正常十四工具與施工收據的完整兩欄。使用相同固定 EXE、ROM 與 GUI image，Python 3.13.16 在盤點 image `sha256:bf44cdfcb76cd3b41e879bc058fc37ec5872002ccfde7fcb765e218cde0cd79c` 執行。定位基準為 ROM 檔案偏移、零起算字模索引及 320×200 原生畫面座標；沒有新增函式呼叫追蹤。

- 已證實：成員 57 的索引 107–110 與成員 58 字碼，分別為「每、單、位、萬」。在 (19,177)、(35,177)、(51,177)、(103,177) 的 15×14 紅色墨跡逐點符合。
- 已證實：正常費用、年月與資金的數字墨跡符合成員 56 的七列高五 bits，字距六點；保留完整欄位前置空白與背景。
- 已證實：ROM1 底圖加原始字模，完整重建 68 份收據的兩欄。408 個背景、墨跡或單位單點破壞均被拒絕，不能只比前景或挑相近字。
- 範圍：這補足數字的正常像素來源證據；上節 `sub_15BCE` 在先前 1.2B 步路徑未被呼叫的紀錄仍有效，不將這次畫面匹配改寫成該函式已執行。

完整來源、色盤、前置空白、固定字型參考與呈現閘門見 [020](../spec/020-city-footer.md)。本機來源保留於 `city-chrome-native/`、`gui-cold-before-footer/`，重建與負對照位於 `workspace/runs/footer-source/catalog.json`。右下未確認語意的符號仍為原版，負資金尚未走正常玩家路徑，不因 ASCII 字模能解碼就宣稱已驗全範圍。
