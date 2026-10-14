# 033：開場、逐字訊息與剩餘文字覆蓋

狀態：CONFORMED，限下列已核對來源及正式啟動範圍。Issue：[#52](https://github.com/wicanr2/taipei/issues/52)，母項 [#49](https://github.com/wicanr2/taipei/issues/49)。

本批沿用 [030](030-hd-localization.md)、[031](031-help.md)、[032](032-interface-localization.md) 的五語系與操作決定。只增加呈現，不改原版規則、輸入或存檔。

## 來源研究

固定輸入 EXE、兩個 ROM 與 Noto 雜湊沿 [032](032-interface-localization.md)。IDA Pro 9.4 使用既有 image `sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab`，唯讀資料庫副本，輸出在 `workspace/runs/ida-52/`。

- 已證實，限靜態指令：`sub_12CA2` 先清除文字列，再呼叫 `sub_149B8`。`sub_12CDA` 呼叫 `sub_14A92`，有額外背景參數。定位是 IDA loader linear，原始名稱、bytes 與 operand 保存在 `typing.json`、`message.json`。
- 已證實，限靜態指令：`sub_14ED2` 在完整零結尾字串上逐字繪製。IDA `14FCEh–14FE3h` 更新可見矩形，`14FE6h–14FEFh` 等待下一字；`14FF2h–14FFBh` 檢查下一字。不能從不完整像素前綴猜完整句子。
- `14320h–143D9h` 尚無 IDA 函式邊界。保留原定位與未定界標記，不建立推測性函式名。
- 已證實，限靜態指令與實際畫面：`sub_14D74` 使用背景色號 21，於 `14E7Fh–14E94h` 發布底部訊息矩形，在 `14E97h` 等待下一字。`notice.json` 保留完整指令。正常執行觀察取得四句訊息的 36 個可見階段，獨立重建字模全部相同。
- 已證實，限靜態指令與來源解碼：`sub_16164` 讀取 IV2 的位移、長度及 literal bytes，以位移加法進位結束。`sub_12D30` 載入 `tp0.iv2` 並在 `(1,1)` 繪製。來源是 ROMA 成員 38；小標題及大型標題分別由此格式與 `sub_160C5` 的透明 RLE 繪圖。

上述位址均為 IDA loader linear。執行觀察使用 `PC - ImageBase + 10000h`；EXE 檔案偏移另列，不混用位址基準。

已證實，限靜態指令：抗議動畫經 `sub_12BDA` 裁至原版插畫區，再呼叫 `sub_16210`。後者接受原始圖片 far pointer、來源 x/y、寬高、目的 x/y 與透明色。`clipped.json`、`clippedraw.json` 保存原名、bytes 與全部指令。只在完整文字框落於實際發布的裁切區且像素相同時覆字；圖片其他部分出界不授權畫出界文字。

已證實，限靜態指令：`endings.json` 的 `sub_12128` 清底後，以 `sub_12CA2` 在 `(0,164)`、`(0,180)` 畫兩列成功文字，色號 15。`sub_12420` 以同一清列函式在 `(32,32)` 畫未完成提示。正常 r15 原版退出實際觀察到後一個呼叫；成功文字以 IDA 參數合成測例核對，不稱正常遊戲勝利收據。

研究入口為 [ida_text_probe.py](../../workspace/tools/ida_text_probe.py) 的 `remaining` 查詢，以及 [text-source-audit](../../workspace/app/cmd/text-source-audit/remaining.go) 的 `-remaining-steps` 唯讀正常執行觀察。後者記錄完整來源 bytes、原始參數、實際畫面與相位，不注入狀態或改寫 DOS。

## 完成閘門

## 呈現契約

- 只觀察已核對呼叫的完整原始字串、座標、顏色與原版已完成的位元組數，不寫入 VM，不用畫面前綴猜整句。
- 以原版 ROM 字模重建整列來源。字墨、背景、位置或可見相位不符時，保留原版。底部訊息另核對完整原版訊息框及使用的色盤。
- 逐字翻譯依已完成原文字數的比例顯示目標語言字元。整句先量測、固定字型大小與位置，再顯示前綴；保留原版等待、動畫與按鍵，F11 不重設相位。開頭全形空白的原版等待期間不提前顯示文字。
- 圖片文字限九筆來源：ROMA 6 大標題、ROMA 38 小標題、ROMA 10 四筆抗議動畫，以及 ROMA 15、16、17 的百貨與銀行。只改已量測文字框；透明像素以呼叫前的原版後緩衝還原。完整文字框與來源合成不同、被遮擋或裁切時保留原版。
- 保留 SOGO 等標誌及無法辨讀的裝飾筆畫。原版建築插畫 ROM 42–51 與地圖 60–66 已檢視，沒有新增可辨讀的句子。政績證書筆畫無法辨讀，不猜造文字。
- 五語系都由唯一 TSV 取得文字；原版顯示模式跳過整個覆繪層。缺字型、缺鍵、來源雜湊失配均沿既有回退契約。

## READY 審查與驗證範圍

`localization-source-intro-r2/` 的 156 個非空開場／上任信階段及 `localization-source-city-r2/` 的 36 個訊息階段，均由獨立 Python 重讀原版字模核對。`localization-prototype-unit-r3.log` 驗五語系逐階段、來源單像素失配、九個圖片來源、實際字墨與十列完整上任信，全部通過。圖片原型是來源合成，尚不當正常 GUI 證據。原型保存在 `localization-text-prototypes-r3/`，已檢視英文百貨／銀行、繁中抗議與完整上任信。

EXE `245C4h–259A0h` 的 146 筆可讀中文字串與圖片來源另由覆蓋工具列出。密碼與版權文字保留譯文，但正式 `/A /D /x` 不啟用密碼流程；`245C4h` 的用途仍未知，不稱為啟動錯誤。資料有譯文不等於該分支已走過。

正式接入後的必要短流程：正常冷啟動開場、圖中文字、上任信逐字、F11 中途切換、F12 原版、城市底部逐字提示，以及既有正常存讀檔與原版退出。各語言字墨與失配回退另驗。完成聲明限已核對來源與正式啟動參數；封包與平台真機另驗。

本批不恢復 #48 圖表的完整 HD 驗收或長時間原版 RAM／RNG 抽樣。

## 來源覆蓋與完成結果

本批驗收時唯一 [ui.tsv](../../workspace/app/locales/ui.tsv) 為225鍵、五個完整語系欄，SHA-256 `4ae6a237fe96d09411860d4e55156b922acc26f1bccca5431eeef094a1b92ad9`。當時實際Noto／OFL檢查涵蓋1213種字元。覆蓋工具 [localization_source_inventory.py](../../workspace/tools/localization_source_inventory.py) 直接讀固定 EXE 與兩個 ROM，輸出 `workspace/runs/localization-source-coverage.json`，SHA-256 `7db6132a25dc4b0f582bb1936dfc207d99b73bf2c585ffd3c69a6dda1377ff04`。

後續[038](038-map-completion.md)增加三個區域字樣鍵，原225鍵全部五欄逐項不變。現行228鍵、1214種字元，TSV SHA-256 `b68456b42325baa572b614f85a2d285a98a61049f189d6ce03b59887b78d901b`；三字樣的實際Noto與五語系墨跡已驗。歷史225鍵收據保持原件，不重寫成新數量。

| 來源家族 | 已完成 | 證據限制 |
|---|---|---|
| EXE 字串區 `245C4h–259A0h` | 146 筆可讀中文全部對應譯文，沒有漏譯 | 來源對應不等於每個分支已執行 |
| 既有介面 | 五語系各 77 種來源狀態、數字及檔名隔離 | 沿 032 的來源與正常 GUI 範圍 |
| 開場與上任信 | 二十句開場、十列上任信及原版逐字進度 | 156 個原版文字階段；正常 r15 顯示全部三十鍵 |
| 城市提示 | 完整來源與逐字前綴，F11 不重設進度 | 36 個原版階段，r15 實際取得英文中間相位 |
| 圖片文字 | 九筆來源的大小標題、抗議、百貨及銀行 | 所有來源相位離線驗字墨，r15 正常動畫取得五類文字 |
| 三句結局文字 | 清列參數及五語系合成來源測例通過 | 未完成提示有正常呼叫；未實際玩至成功結局 |
| 密碼、版權及未知用途字串 | 八筆原始來源、七個穩定鍵均有譯文 | `/x` 的密碼分支未執行；`245C4h` 用途未知 |
| 商標及裝飾 | 保留原版標誌與無法辨讀的證書筆畫 | 不猜造原文；圖片全面重繪仍屬 HD 母項 |

正式呈現入口為 [text_sources.go](../../workspace/app/internal/hd/text_sources.go)、[text_images.go](../../workspace/app/internal/hd/text_images.go)，原始呼叫由 [original/text.go](../../workspace/app/internal/original/text.go) 唯讀觀察。只在已核對的完整來源通過時覆字，來源未知、字墨失配、裁切或資源故障保留原版。

`localization-production-unit-r2.log` 的既有五語系各 77 種來源回歸通過。`localization-source-unit-final.log` 驗五語系的 156 個開場階段、36 個城市階段、三個結局合成測例、九筆圖片、單像素與裁切破壞、完整上任信、正式 Render 與 F12、未知來源及 ROMA 故障，全部通過。`localization-reveal-unit-final.log` 以實際字墨檢查零／半／完整進度、安全矩形、固定位置及超長外部譯文完整回退。原版觀察器另驗記憶體、暫存器及步數不變，以及重複透明標題保留乾淨背景。

## 正常 GUI 與交付邊界

`TAIPEI_INTERFACE_OPENING=1 TAIPEI_INTERFACE_QUICK=1 TAIPEI_INTERFACE_PHASE=settings TAIPEI_INTERFACE_RUN=interface-locale-cold-r15 bash workspace/tools/interface_locale_playtest.sh` 通過。全新 EXE 不用 checkpoint，正常播放開場及插畫，在逐字上任信中 F11 改為韓文，面板內原版步數、CPU、原畫面、色盤、讀鍵及來源進度不變。F12 原版在面板外兩側逐像素相同；存檔與離開視窗另驗完整原版四倍畫面。接著進新城市，驗環境五項、五語系預算、英文 LOCALE 檔名、93567 bytes 原版 SAV、同次讀回、政績畫面及原版返回 DOS。沒有全新 EXE 冷讀或長時間狀態抽樣。

主收據 `interface-locale-cold-r15/verification.json` SHA-256 `c7f23b6d0c00b58b64cb4d261e91f309cb73abfc1bbbdeaf3cf76369e2d43478`；開場收據 SHA-256 `573e2073b7b309a8eed7418eca32eafa5168431a44e521ba56ec1cf251324c7d`。本批正常字墨與切換證據補足 030／032 的剩餘範圍；既有 Help、人口／民意與設定冷讀證據仍沿 030–032。

`TAIPEI_INTERFACE_FALLBACK=1 TAIPEI_INTERFACE_RUN=interface-locale-cold-r17 bash workspace/tools/interface_locale_playtest.sh` 以有效但缺 `intro.date` 的外部 TSV 冷啟動，實際回退隨附 TSV，開場正常翻譯，F11 顯示英文資源警示，面板輸入不穿透。收據 SHA-256 `d41c06c73ae6d4efeda77bc12a73d9f51effe87bbe23850bfaa3df8a9e4481d7`。字型／授權／缺字與其他 catalog 故障由實際資源測試核對。

已驗 Linux binary SHA-256 `1461ac4b4a2fe582f3c937a9f6d84edca34d09562a236a0f1472895f088ec2c8`，同來源重建逐 byte 相同。跨平台編譯結果另記 CONTEXT；本批沒有 Windows／macOS 真機、Wine、正式封包、IME 或成功結局的完整玩家流程，不將來源覆蓋外推這些結果。五語系尚未經母語人工審校。

四架構編譯及 ELF／PE／Mach-O header 核對通過。`workspace/runs/localization-final-provenance.json` 記錄原創 Go 來源、TSV、四個 binary 雜湊、35 個原始檔與 RAR 不變、正常收據及 SAV 雜湊。Windows amd64 SHA-256 `1506be424369c922a3f7c39a7337252f0388c65eed6b61773a879fbfe775e589`；macOS amd64 `32fea91049a2911d9e91210393af3dcd7ecd59e1c6dc8930782135cadbcc9b5f`；macOS arm64 `97d3857bdc3bd152ecda24f54a76c42b76c0785fb54c2e681d8f89dc2f54d344`。含原版的圖片、收據、字型、SAV 與 binary 均只留本機。
