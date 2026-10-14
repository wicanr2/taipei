# 環境與公共設施批次

狀態：垃圾場／污水處理廠呈現及已驗路徑 CONFORMED；十項公共設施 DRAFT。Issue：[58](https://github.com/wicanr2/taipei/issues/58)，父項 [30](https://github.com/wicanr2/taipei/issues/30)。

## 已審查來源與呈現契約

垃圾場與污水處理廠均已正常施工、扣款 3000 並移開游標。各為 4×4 個 9×9 原格，ROM 成員 37 的零起算索引分別為 `12+24*r+c`、`16+24*r+c`，以固定來源證明的實際索引為準。32 個來源互不重複。來源證明保存於 `public-facilities-v1/waste/source.json` 與 `sewage/source.json`，SHA-256 分別為 `01354b5add558197a435aa3caee567214f6013687c785bee5dd40866bb444e74`、`49bf897e4550f953425c8c8f7ad24324cdf0f1f25c1ab71ac211562d2a4b0677`。

兩張 B 原件及完整縮放比較圖已檢視。正式素材為 `public-facilities-ready-v1/` 的 manifest、waste.png、sewage.png，每張 144×144。固定 manifest SHA-256 `07319733ab01743a8e2e30cec7e6e042554b35982bf342ba556f21d84c2892e1`，包含原 ROM、全部別名／偏移、已用色盤、來源證明、提示與生成原件雜湊。原件以整張 Lanczos 縮放，再依 36×36 原格切片。

呈現器先驗固定 ROM／manifest，再逐格驗來源與已用色盤，沿現行城市／原點／主題閘門覆繪。清單失配整批回退；單設施 atlas 缺失或損壞只讓該設施回退。未知及有歧義來源不覆蓋。統計列出 matched、painted、fallback、設施與原因，不改原版資料或規則。

本次產品抽驗垃圾場及污水處理廠、F12、F11 五語系、正常存讀檔與 DOS 退出。公共設施因 [#60](https://github.com/wicanr2/taipei/issues/60) 的正常施工阻塞維持 DRAFT；原先跨組抽樣留待其來源完整後執行，#58 不因兩項完成而結案。

產品：[public_facilities.go](../../workspace/app/internal/hd/public_facilities.go)。[單元測試](../../workspace/app/internal/hd/public_facilities_test.go) 核對完整圖、區外、來源／色盤失配、真實資源故障及正常原版收據；[GUI 像素核對](../../workspace/tools/public_facility_check.py) 從 READY 前的固定原型及生成原件驗實際八張畫面與五語系標籤，不匯入產品呈現器。[README 匯出工具](../../workspace/tools/export_public_screenshots.py) 再核對收據、PNG 與像素報告後追加來源清單。

沿 [021](021-tool-submenus.md) 工具 9 的垃圾／污水處理與工具 10 的十項公共設施，正常新遊戲建立 BASE.SAV，再以原版 F2 讀回同一座城市，逐項施工、移開游標並核對完整 ROM 圖像。只讀畫面推定游標矩形，不注入城市、資金或座標。圖像索引、大小及費用待實見確認，無完整來源的設施維持 DRAFT。

輸入、dosgolem 七補丁、B 風格、1280×800、Noto 與五語系沿 [035](035-civic-facilities.md)。正式呈現前固定來源、別名、偏移、使用色盤、完整生成圖與 SHA-256，審查轉 READY。只改呈現，原版負責全部規則與 SAV。

預登記抽驗：全部已確認設施的正常原版來源加產品離線像素驗證；產品 GUI 抽驗環境與公共設施各一種、F12、F11 五語系、正常存讀檔與 DOS 退出。素材故障按設施隔離、來源與色盤失配回退，驗完整複合圖、原版資料及區外。依使用者遊玩抽驗標準，不增加長時間狀態重播門檻。

入口：[批次玩家探針](../../workspace/tools/facility_batch_playtest.py)、[Docker 入口](../../workspace/tools/facility_batch_playtest.sh)。研究收據在 `workspace/runs/public-native-r1/`；素材與來源在 `workspace/prototypes/hd-style/public-facilities-v1/`。產品及素材工具確認後同次補入本入口。既有工作區與原版資料路徑不變。

來源匯出工具為 [public_facility_sources.py](../../workspace/tools/public_facility_sources.py)，每項保存完整圖、所有來源別名、偏移與原版收據。素材工具為 [public_facility_assets.py](../../workspace/tools/public_facility_assets.py)，以 `--count` 明列本次已審查來源數，不將其他 DRAFT 項自動納入；完整圖縮放後才切片。離線比較在 `public-facilities-prototype-v1/`，正式固定素材在 `public-facilities-ready-v1/`，均位於既有 `workspace/prototypes/hd-style/`。

## 正常抽驗結果與限制

`workspace/runs/gui-environment-r1/verification.json` SHA-256 `82e4945f80375699d6da21174097a3cf3825ff086d7aa011c792b96bc5439fba`。從原版新遊戲施工兩項設施，以原版 BASE.SAV 讀回重用城市，完成 F12、F11 五語系、PUBLIC.SAV 同次存讀檔與 DOS 退出。無快照、狀態注入或長時間機器狀態抽樣。PUBLIC.SAV 為 93567 bytes，SHA-256 `660bfc71f309b96fe0bce6dcb743b8ca3635f2ebbd299060275ba86821097746`。

八張實際 GUI 的設施像素、五語系標籤、原版整張及五項正反對照通過，像素報告 SHA-256 `f6d728f45cba4c5b387b7772bf2bfc4c84d48fce653926fc7c3a43a957a6cf4c`。單元測試通過完整圖、區外、2592 項來源失配、已用色盤、六項實際素材故障及設施隔離；十二項既有警消／建物／道路／電廠回歸通過。正式三個素材檔乾淨重生相同。

十項公共設施因 #60 維持 DRAFT。[IDA 窄查詢](../../workspace/tools/ida_facility_probe.py) 與[診斷重播](../../workspace/tools/facility_diagnostic.go) 保存原始指令、BDA 變化及取樣 PC。診斷不能代替正常 GUI；公共設施尚未通過施工後輸入與存讀檔。

本批 Linux binary SHA-256 `21705e3c9521d247b86220bcaecb295db39958b6ba485d5501df42059063abf4`。Windows／macOS 延至後續合併重建；其他相位、全新 EXE 冷讀、平台真機及正式封包未驗。
