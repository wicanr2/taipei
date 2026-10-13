# 警察局與消防局建物

狀態：CONFORMED，限兩種施工圖的呈現及已驗正常玩家路徑。Issue：[57](https://github.com/wicanr2/taipei/issues/57)，父項 [30](https://github.com/wicanr2/taipei/issues/30)。

沿用 [021](021-tool-submenus.md) 工具 5 的已證實警察局、消防局子選單。兩次獨立正常冷啟動、新遊戲、暫停、選擇子項、施工及移開游標，均取得完整 4×4 圖像。來源已證實，限本次可見施工圖，不推定其他發展相位。

| 設施 | ROM 成員／圖像索引 | 原版畫面與世界位置 |
|---|---|---|
| 警察局 | 37，`24*r+c`，r、c 各 0..3 | 原點 12,12；畫面格 22,3；原版矩形 203,61,36,36 |
| 消防局 | 37，`4+24*r+c`，r、c 各 0..3 | 同上，各用獨立新遊戲施工 |

成員 37 有 96 張圖、8354 bytes。32 張原始 9×9 圖像均有唯一來源。定位保留零起算成員、圖像索引、成員偏移與 ROM 檔案偏移，不改寫原始名稱。輸入 ROM SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`；EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。

來源清單 `civic-facilities-v1/sources.json` SHA-256 `212cb5c2c92fcfc36a254205586a38bb7e668dc8f3595a28e0ed0d770dbadc45`，保存兩份正常收據及逐格來源；工具版本為 Python 3.11.2、ImageMagick 6.9.11，dosgolem 基底與七補丁沿用現行前端。

本批只改呈現。原版程式負責費用、施工、規則與存檔。圖像採已確認 B 風格、四倍尺寸，完整圖縮放後切片。逐格比對原始 81 bytes 及使用中色盤；必要素材或來源失配回退，不覆繪未知相位。

素材已以內建 image_gen 依完整原版圖生成並檢視。警察局保留藍底金色徽章；消防局保留灰色看板、紅筒與暗色管線。B 材質屬呈現近似，不宣稱原版像素相同。提示存於 `civic-facilities-v1/prompts.json`；生成紀錄為同目錄 `generation.json`，生成圖警察局 SHA-256 `bffc16d81a92676ea6b6514294e7fa84284195f937eddfc8fef6d895711e1427`、消防局 `5547e9ba27afc93d5a0db8479a90dd37da2c0195368b5201d66c7f585608bf19`。

完整圖各縮至 144×144，再橫向合為 288×144 的 `37.png`，左警政、右消防。atlas 格為 8×4，索引 `24*r+c`。固定清單 `civic-facilities-ready-v1/manifest.json` SHA-256 `4c2a707844a6cb00d295ff49afb826b7dddcd7f37f036d3d97ed9d1bb23f5c3c`，stage `civic32`。缺失、竄改清單或 atlas 時本批整組回退；只核對圖塊實際使用的色盤。僅在已確認城市畫面、有效原點、HD 開啟及無阻塞面板時繪製，未知圖像沿用原版。

正常 GUI 已在同一座新城市施工兩種設施，警察局畫面格 22,3、消防局 22,7；原點保持 12,12。逐格重新核對 32 張完整來源；F12 原版／HD、F11 五語系、同次 CIVIC.SAV 存讀檔及原版 DOS 退出通過。五語系切換保持原始畫面不變，語言面板開啟期間原版狀態不前進。CIVIC.SAV 為 93567 bytes，讀回後雜湊與 32 格覆繪均保持。

驗證記錄 `workspace/runs/gui-civic-r1/verification.json` SHA-256 `4eb94f6863916cabac7b2d4e4c8985a1f8a836b93e40523bfcdb3cec03eb5d30`。獨立核對原始 ROM、兩張生成圖與實際縮放 atlas；六張 GUI 的 HD 設施像素、語言標籤及原版整張像素通過，包含一項正對照及四項有效破壞。`pixel-verification.json` SHA-256 `295b1fc95d9ba8a0f34f87b76309afee458d673aaeb689ecd4019a2a3c7576d3`。

Go 測試確認兩完整圖重組、2592 項來源單點失配、使用中色盤、四項實際素材缺失／損壞、正常來源與原版資料不變、兩份正常畫面中的建物區外隔離。原道路、電廠與 DISA1 建物共 12 項測試通過，追加區外檢查後單項乾淨重跑通過。記錄 `workspace/runs/civic-tests-r1.log` 與 `civic-scene-isolation-r1.log`。

Linux 已驗執行檔 `workspace/runs/taipei-preview-civic-r1` SHA-256 `bb8aa4271a403b0e1602c5a82faacda4554de48972b212bf00daef83fa589a5d`。Windows amd64、macOS amd64／arm64 另完成重新編譯及架構核對，詳見本機 `workspace/runs/civic-final-provenance.json`；尚未進行 Windows／macOS 真機試玩或正式封包驗收。未走過的動畫、長時間機器狀態對拍及全新 EXE 冷讀保留限制。

工具：[Docker 入口](../../workspace/tools/civic_facility_playtest.sh)、[正常來源探針](../../workspace/tools/civic_facility_playtest.py)、[來源核對](../../workspace/tools/civic_facility_sources.py)、[素材重生](../../workspace/tools/civic_facility_assets.py)、[正常遊玩](../../workspace/tools/civic_facility_gui.py)、[像素核對](../../workspace/tools/civic_facility_check.py)、[截圖匯出](../../workspace/tools/export_civic_screenshots.py)、[載入與覆繪](../../workspace/app/internal/hd/civic_facilities.go)、[測試](../../workspace/app/internal/hd/civic_facilities_test.go)。來源及生成素材留在 `workspace/prototypes/hd-style/civic-facilities-v1/`，正常收據留在 `workspace/runs/civic-police-native-r1/` 與 `civic-fire-native-r1/`。

乾淨工作區可用 `bash workspace/tools/civic_facility_playtest.sh source` 重生兩份來源；`gui` 走正式抽驗。已有收據時停止，不覆寫。GUI 可用 `TAIPEI_CITY_MENU_RUN` 指定新收據名稱。素材重生在同一 pinned image 內執行 `python3 /workspace/tools/civic_facility_assets.py --stage civic32 --out <尚不存在的輸出目錄>`，原始輸入掛 `/orig` 唯讀。
