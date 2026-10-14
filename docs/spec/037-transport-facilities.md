# 港口與機場靜態圖

狀態：CONFORMED，限兩項完整靜態圖與已驗既有城市正常路徑。對應 [#61](https://github.com/wicanr2/taipei/issues/61)，母項 [#30](https://github.com/wicanr2/taipei/issues/30)。沿用 B、1280×800、Noto、F11 五語系及 F12。原版 EXE 繼續負責規則、施工、費用、時間、亂數及 SAV。其他相位、新建機場、外平台真機與正式封包未驗。

固定 EXE／ROM／dosgolem 與七補丁沿 [027](027-power-facility.md)。Docker 使用既有 GUI image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`，原版唯讀、UID/GID 1000、有界資源及無網路。

## 最小來源證據

已證實，限 IDA Pro 9.4 靜態指令：正常施工 `sub_19102` 的 case 13 於 IDA loader linear 0x1A4F8 調用 `sub_1A64C`，通過後返回 1；case 14 於 0x1A512 調用相同六格區域檢查。`sub_17BF8` 的 case 13／14 分別從 0x17DE4／0x17E24 設定 type 5、六格複合圖。原始名稱、bytes、各項檔案偏移保留於既有 `workspace/runs/ida-46/nuclear-check.json`；跨批引用原件，不改其中 issue 或工具版本。

原版工具與來源用途尚待正常 GUI 完整核對。不把未見 ROM 排列當作成功施工或 READY。本批不再重跑財政與核能選址研究。

## 正常來源探針

[transport_facility_playtest.sh](../../workspace/tools/transport_facility_playtest.sh) 與 [transport_facility_playtest.py](../../workspace/tools/transport_facility_playtest.py) 從全新 EXE 正常冷讀 DISA4 既有城市。唯讀種子是先前正常保存的 `power-scenario-scan-r2/city-4/saves/FUND.SAV`，93567 bytes、SHA-256 `47f73cbe590a26bc8b9b792d8de4eea4f2d9efb6723ca664c931075f1d4d52b1`。原版資金 73455。經原版方向鍵先到機場視窗 (36,24)、世界 (47,29)，再到港口視窗 (32,68)、世界 (43,73)，移開原版小游標後核對完整 81 bytes。最後原版保存 TRANSP、讀回及正常退出，沒有新建、狀態注入或財政修改。`TAIPEI_TRANSPORT_PHASE=hd` 為後續 READY 接入後的正式五語系／F12 抽驗階段，現在只執行 source。

首件 `transport-source-r1` 已在正常新城市取得港口完整 36 格，ROM38 索引 `6+30×row+col`，原版費用 80000、資金 0；原件保留。原版機場費用 100000，新城市資金 80000，尚未施工就被腳本拒絕。本輪不重新籌資，改用已正常保存的既有城市抽驗。首件只作港口來源前綴，不作兩項存讀／退出或正式 HD 完成證據。

正式 HD 前須取得完整來源、全部別名、色盤、複合矩形與 B 圖，審查 READY 後再接入。預定核對全圖與區外、來源／色盤／實際素材故障、F11／F12、存讀及原版退出；其他相位、外平台真機與正式封包另列限制。

來源成功後使用 [public_facility_sources.py](../../workspace/tools/public_facility_sources.py) 的 `--issue 61 --run <正常來源目錄> --out <本批素材目錄>` 匯出完整原圖、全部別名與定位。舊公共設施預設 issue 58 與輸出欄位維持原樣，不覆寫既有來源證明。

本機素材根為 `workspace/prototypes/hd-style/transport-v1/`，下分 `port/`、`airport/` 保存來源、參考、生成原件與提示。完整港口來源可先由 r1 前綴製作可撤回原型；正常存讀／退出由 r4 補足，正式 HD 另由後續產品抽驗驗證。

r2 在完整候選補查後主動停止：世界 (25,5) 港口的 (26,5) 已是 type6／variant7 碎石。保留 `transport-source-r2/partial-scope.json` 與執行原件，不以根節點 type0x85 代替完整矩形。r3 已先核對同城機場 (47,29) 及另一港口 (43,73) 的全部 36 個 type／variant，再走上述正常 GUI。最終圖像仍須與 ROM 逐 byte 相同，唯讀 SAV 定位不代替畫面證據。

來源及生成原件由 [public_facility_assets.py](../../workspace/tools/public_facility_assets.py) 使用 `--count 2 --issue 61` 製作完整 DRAFT，READY 後再用 `--stage transport` 匯出。獨立核對與截圖工具沿 [public_facility_check.py](../../workspace/tools/public_facility_check.py)、[export_public_screenshots.py](../../workspace/tools/export_public_screenshots.py) 的 `--scope transport`，固定原型 seal 前不可執行正式驗收。

[transport_source_prefix.py](../../workspace/tools/transport_source_prefix.py) 只從 r3 停止前的實際 `capture.zip` 匯出機場完整 36 格來源，逐 byte 符合 ROM38 基底0才接受，保留 prefix／normal_path_complete=false，不更名原收據，也不冒稱正常存讀或退出。r3 的原點已完成但游標未重畫造成探針早讀，r4 改等完整已知游標及設施來源再送鍵。機場候選可先用此完整原圖製作，正式產品仍另驗正常 GUI。

## 72 格 READY 契約

2026-10-14：r4 已經正常冷讀、捲動、移開游標取得兩項完整 36 格，與 r1 港口／r3 機場來源相同。ROM38 港口索引 `6+30×row+col`、機場 `30×row+col`，全部 72 種來源唯一，沒有其他圖庫別名或地景來源重疊。兩份完整來源證明 SHA-256：港口 `0c0616fe918189c68e35846fd916f786090806c49fc882dab87c561f46c6d70d`，機場 `61aeb6803546ef6edb48c81e38a109d41aece97e078247c7aa901aca04434327`。來源前綴的限制保留，正式遊玩結論另記。

內建 imagegen 依完整原圖重繪，港口保留藍色建物、黃色船錨與灰色外框；機場保留四架白色飛機、灰色跑道、黃色中心線、青色建物與圈 H。圈 H 已由原版白色像素逐點確認，沒有新造標示。機場 v1 右側建物超出青色外緣，v2 只修復外緣，v1 保留未採用。已檢視兩張實際 216×216 原版／B 對照。

| 固定輸入 | SHA-256 |
|---|---|
| 港口生成原件 | `37d6b8476aaa52425b3c548d94066fc4ea1d28fca5c536137274222c7e53504b` |
| 機場生成原件 v2 | `9515116c6decb1876cf9f2f26d5c165b73d875f733a6e77614ad5fafb8458c77` |
| DRAFT `transport-prototype-v1/manifest.json` | `3ad256026ebfa478fbe0da48e1053131079c5d4b10787b5320f8f388546094cd` |
| READY `transport-ready-v1/manifest.json` | `78a955c44ab2078eb5d4b71bff534101fc0dc110cc6f4aa3edde27fe5b6dc191` |

正式載入沿 027 的封存 atlas 函式。只接受固定 ROM、manifest、兩張不透明 216×216 atlas、完整 81 bytes 原始圖與已用色盤。每格只寫對應 36×36 矩形，不改原版畫面、輸入、財政、時間、亂數與 SAV；未知、受損、游標遮擋、素材故障、模態、未驗原點及 F12 原版一律維持原版。全圖只縮放一次，按原圖格擷取，不逐格縮放。

獨立核對已重讀生成原件、ROM 與全部 72 格／50 種已用色盤，完整 atlas 與 ImageMagick 6.9.11 Lanczos 輸出相同。正式 HD 沿用 r4 正常既有城市路徑，每項原版與五語系各擷取六張，另驗同次存讀及退出。新建機場、其他相位、外平台真機與正式封包未驗，不從圖片完整性推導這些分支。

呈現入口：[transport_facilities.go](../../workspace/app/internal/hd/transport_facilities.go)。正常來源、完整 atlas、區外、家族衝突、場景、來源／色盤與實際素材故障測試：[transport_facilities_test.go](../../workspace/app/internal/hd/transport_facilities_test.go)。

收尾沿 [nuclear_final_check.py](../../workspace/tools/nuclear_final_check.py) 的 `--batch transport --source-commit <實作提交>`，核對本批正常 GUI、原版 SAV、四架構、72 張 README 圖、來源及原版輸入／擁有權，輸出 `workspace/runs/transport-final-verification.json`。舊核能預設分支保持不變，歷史結論依其固定提交與收據。

## 正常 HD 遊玩驗收

`TAIPEI_CITY_MENU_RUN=gui-transport-r1 TAIPEI_TRANSPORT_PHASE=hd TAIPEI_TRANSPORT_BINARY=taipei-preview-transport-r1 bash workspace/tools/transport_facility_playtest.sh` 通過，wrapper0。全新EXE冷讀DISA4，兩項正常捲動、完整36格、各六張原版／五語系、F12不送DOS鍵、原版TRANSP保存／讀回及正常退出。資金73455保持不變，沒有狀態注入、新建或長時間重播。

主收據 SHA-256 `17fa9dc60428642b3ba11ee9a2cc50e449a40d2bd7cd649290417cb0f34994a4`。獨立核對72格固定來源／生成原件、十二張全圖與五項有效正反對照通過，像素報告 `07eb2a90eb4e9c51e9490c576ccf43ca8b8c6a37789128d9ae3f7209850d8793`。區外、5832項來源失配、已用／未用色盤、六項實際素材故障及家族隔離由正常來源Go測試核對；連同核能及公共同源回歸10.123秒，無跳過。

原版TRANSP.SAV 93567 bytes，SHA-256 `8dfab3da2107cfb0d701d7aef796d25d5f5c5a2de473f7e418fa5c61ef123e27`，與沒有運輸HD的r4來源基線逐byte相同，讀回不變。READY三個素材檔在transport-ready-repro-v1乾淨重生，逐byte相同。沒有將此結果外推為完整RAM／CPU／RNG對拍。

實作提交 `487953922bc0dec7e45b28155fdfa3ec438a33c0` 已推送。Linux已驗binary `d2c326607d0b111501371c6cc7db55d68bd1954d3f8e40f5bba1e076bed6f644`，標準build_preview.sh從固定dosgolem與七補丁乾淨重建相同。Windows amd64 `d52d0954888a9cf7c1bc4a166b02d56a669d65cf70d3f3545dde7504a3d28496`、macOS amd64 `e8ea6202509b0a84ab31e79739a5144cf4596fde20380a8c6943dd45e30402b6`、macOS arm64 `df4236850565647fca63e8430e1ca0db67da84cac3d089715cf8f6e10ed13761` 編譯與結構完成，外平台真機仍未驗。

README新增兩項各六張實際畫面，合計72張；原始收據、生成原件、SAV與binary留本機。其他相位與全部圖片繼續由#30／#32維護，正式封包由#9驗收。
