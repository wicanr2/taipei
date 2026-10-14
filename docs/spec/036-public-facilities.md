# 環境與公共設施批次

狀態：v1 兩項與 v2 十二項靜態施工圖及已驗路徑 CONFORMED。Issue：[58](https://github.com/wicanr2/taipei/issues/58)，父項 [30](https://github.com/wicanr2/taipei/issues/30)。

## 已審查來源與呈現契約

垃圾場與污水處理廠均已正常施工、扣款 3000 並移開游標。各為 4×4 個 9×9 原格，ROM 成員 37 的零起算索引分別為 `12+24*r+c`、`16+24*r+c`，以固定來源證明的實際索引為準。32 個來源互不重複。來源證明保存於 `public-facilities-v1/waste/source.json` 與 `sewage/source.json`，SHA-256 分別為 `01354b5add558197a435aa3caee567214f6013687c785bee5dd40866bb444e74`、`49bf897e4550f953425c8c8f7ad24324cdf0f1f25c1ab71ac211562d2a4b0677`。

兩張 B 原件及完整縮放比較圖已檢視。正式素材為 `public-facilities-ready-v1/` 的 manifest、waste.png、sewage.png，每張 144×144。固定 manifest SHA-256 `07319733ab01743a8e2e30cec7e6e042554b35982bf342ba556f21d84c2892e1`，包含原 ROM、全部別名／偏移、已用色盤、來源證明、提示與生成原件雜湊。原件以整張 Lanczos 縮放，再依 36×36 原格切片。

呈現器先驗固定 ROM／manifest，再逐格驗來源與已用色盤，沿現行城市／原點／主題閘門覆繪。清單失配整批回退；單設施 atlas 缺失或損壞只讓該設施回退。未知及有歧義來源不覆蓋。統計列出 matched、painted、fallback、設施與原因，不改原版資料或規則。

v1 已驗垃圾場及污水處理廠、F12、F11 五語系、正常存讀檔與 DOS 退出。後續十項及跨組抽驗見 v2；兩批固定來源及收據均保留。

產品：[public_facilities.go](../../workspace/app/internal/hd/public_facilities.go)。[單元測試](../../workspace/app/internal/hd/public_facilities_test.go) 核對完整圖、區外、來源／色盤失配、真實資源故障及正常原版收據；[GUI 像素核對](../../workspace/tools/public_facility_check.py) 從 READY 前的固定原型及生成原件驗實際八張畫面與五語系標籤，不匯入產品呈現器。[README 匯出工具](../../workspace/tools/export_public_screenshots.py) 再核對收據、PNG 與像素報告後追加來源清單。

沿 [021](021-tool-submenus.md) 工具 9 的垃圾／污水處理與工具 10 的十項公共設施，正常新遊戲建立 BASE.SAV，再以原版 F2 讀回同一座城市，逐項施工、移開游標並核對完整 ROM 圖像。只讀畫面推定游標矩形，不注入城市、資金或座標。圖像索引、大小及費用待實見確認，無完整來源的設施維持 DRAFT。

輸入、dosgolem 七補丁、B 風格、1280×800、Noto 與五語系沿 [035](035-civic-facilities.md)。正式呈現前固定來源、別名、偏移、使用色盤、完整生成圖與 SHA-256，審查轉 READY。只改呈現，原版負責全部規則與 SAV。

預登記抽驗：全部已確認設施的正常原版來源加產品離線像素驗證；產品 GUI 抽驗環境與公共設施各一種、F12、F11 五語系、正常存讀檔與 DOS 退出。素材故障按設施隔離、來源與色盤失配回退，驗完整複合圖、原版資料及區外。依使用者遊玩抽驗標準，不增加長時間狀態重播門檻。

入口：[批次玩家探針](../../workspace/tools/facility_batch_playtest.py)、[Docker 入口](../../workspace/tools/facility_batch_playtest.sh)。研究收據在 `workspace/runs/public-native-r1/`；素材與來源在 `workspace/prototypes/hd-style/public-facilities-v1/`。產品及素材工具確認後同次補入本入口。既有工作區與原版資料路徑不變。

來源匯出工具為 [public_facility_sources.py](../../workspace/tools/public_facility_sources.py)，每項保存完整圖、所有來源別名、偏移與原版收據。素材工具為 [public_facility_assets.py](../../workspace/tools/public_facility_assets.py)，以 `--count` 明列本次已審查來源數，不將其他 DRAFT 項自動納入；完整圖縮放後才切片。離線比較在 `public-facilities-prototype-v1/`，正式固定素材在 `public-facilities-ready-v1/`，均位於既有 `workspace/prototypes/hd-style/`。

## 正常抽驗結果與限制

`workspace/runs/gui-environment-r1/verification.json` SHA-256 `82e4945f80375699d6da21174097a3cf3825ff086d7aa011c792b96bc5439fba`。從原版新遊戲施工兩項設施，以原版 BASE.SAV 讀回重用城市，完成 F12、F11 五語系、PUBLIC.SAV 同次存讀檔與 DOS 退出。無快照、狀態注入或長時間機器狀態抽樣。PUBLIC.SAV 為 93567 bytes，SHA-256 `660bfc71f309b96fe0bce6dcb743b8ca3635f2ebbd299060275ba86821097746`。

八張實際 GUI 的設施像素、五語系標籤、原版整張及五項正反對照通過，像素報告 SHA-256 `f6d728f45cba4c5b387b7772bf2bfc4c84d48fce653926fc7c3a43a957a6cf4c`。單元測試通過完整圖、區外、2592 項來源失配、已用色盤、六項實際素材故障及設施隔離；十二項既有警消／建物／道路／電廠回歸通過。正式三個素材檔乾淨重生相同。

施工探針的原版清鍵及游標問題見 #60。[IDA 窄查詢](../../workspace/tools/ida_facility_probe.py) 與[診斷重播](../../workspace/tools/facility_diagnostic.go) 保存原始指令、BDA 變化及取樣 PC；正常後續由 r9／r11 及 v2 產品 GUI 補驗，診斷不取代正常 GUI。

施工探針的[就緒辨識](../../workspace/tools/facility_cursor.py) 只接受完整 ROM 格或 r10 已逐像素核對的原版游標外框。此閘門只控制下一個測試按鍵；來源匯出仍須移開游標並完整核對每格 81 bytes，不以游標遮罩生成正式來源或 HD 素材。

v1 Linux binary SHA-256 `21705e3c9521d247b86220bcaecb295db39958b6ba485d5501df42059063abf4`；現行四架構見 v2。其他相位、全新 EXE 冷讀、平台真機及正式封包未驗。

## 十二項整批 CONFORMED

v1 的兩項及其收據保持不變。整批 v2 使用既有 `public-facilities-v1/` 的十二份來源證明與生成原件，在同一素材根下建立 `public-facilities-prototype-v2/`，審查後才建立 `public-facilities-ready-v2/`。兩項環境設施為 144×144，十項公共設施各為 216×216。新素材不覆寫 v1。

國父紀念館來源為 r9，其餘九項為 r11，全部正常施工與移開游標，各 6×6 格、費用 5000。r11 完成原版 PUBLIC.SAV 存讀、全部最後施工格讀回及 DOS 退出，報告 SHA-256 `72d9f359193fc9cd9080f938c81d2aa1c4f611b96aee020133b47a0646867175`，SAV SHA-256 `d6601a5009ce1af565d41e6592a4a4690fe19db49644bd47b3425c53fc3ef91a`。外層清理回傳 143，來源與完成收據保留，不能把整個 wrapper 稱為 PASS；後續產品 GUI 另做乾淨完成。

共 392 格、391 個不同來源。唯一同源出現在體育場 `[3,0]`／`[4,0]`，ROM41 圖 9／10，SHA-256 `c7d8532244e8a14fdac66ea1fe533c46c6b474c66dce4ba20873aafab738c5be`。兩格 HD 片段不同，須依同一設施仍可見的全部唯一相鄰原圖核對位置，至少一個可見錨點，且只能唯一選出一個位置；不足、失配或多解均回退。此辨識只改呈現，不靠推測位置或改原版資料。

v2 驗收沿原先跨組抽驗：環境設施與公共設施各一項、F12、公共設施五語系、原版存讀與 DOS 退出。十二份來源均做產品離線像素及區外核對，共用格另驗完整／裁切／歧義／錯鄰格回退。

十二張完整重繪及 144／216 像素比較圖已檢視。固定 DRAFT 原型 manifest SHA-256 `8a90556b3065244377ae9cfbc414389b76fb71150c618623a06a05116caf5428`；READY manifest SHA-256 `cbbb76d9a14f71f540e310a073492c5b43f58b6a13ff3f99c081d55064ed1f32`。十二個 atlas 各自固定 SHA、來源證明、完整提示與生成原件。清單保持既有 schema；共用載入器逐一經實際 ROM 成員／圖片表驗全部別名、大小、偏移、81 bytes、使用色盤與完整 atlas。RS201.ROM 的成員數讀實際 header，不把兩個 ROM 合計 118 成員當作單一 archive 的大小。

四項必要測試通過，55.163 秒。包含十二張完整 atlas／全部區外、391 項來源失配、使用色盤、二十六項真實素材故障與設施隔離、實際 archive 首末格與越界，以及十二份正常來源的產品呈現／原版資料隔離。共用格正常原位、裁切、缺鄰格及錯鄰格通過。四項既有家族回歸與鍵盤通過；十三個正式素材檔在 `public-facilities-ready-repro-v2/` 乾淨重生相同。

`TAIPEI_CITY_MENU_RUN=gui-public-r2 bash workspace/tools/facility_batch_playtest.sh hd` 以真實新遊戲施工垃圾場及體育場，完成 F12、F11 五語系、PUBLIC.SAV 同次存讀與原版退出；wrapper 為 0。無快照、注入或長時間狀態抽樣。正常報告 SHA-256 `a163522a7e18d0c40811acb898d4b64e4e453fb2990a255b5dcadc29793a1e56`，SAV 93567 bytes、SHA-256 `02ff88bf23cdd719b3c8e1c2b935257a729e6d0f430b0ee1a101fe550ad8a6bc`。

`public_facility_check.py --run /workspace/runs/gui-public-r2 --scope public` 從固定 DRAFT 原型、原 ROM 及完整生成原件，核對八張實際畫面中的整座設施、五語系標籤及原版整張。六項正反對照通過，包含交換體育場兩個同源 HD 片段再重算雜湊，仍被拒絕。報告 SHA-256 `caa694687de1c71ec711516faacfdc3dddcb0bcca6625f5ae12826df11cd6a18`。

現行 Linux binary SHA-256 `54d04177a5ed420f95cf7592e7907f9d8e750661fa0ace086409b169d960655c`。Windows amd64、macOS amd64／arm64 本次合併重建；來源、四架構、工具與素材雜湊保存 `workspace/runs/public-v2-final-provenance.json`。其他相位、全新 EXE 冷讀、長時間完整機器狀態對拍、外平台真機及正式封包未驗。
