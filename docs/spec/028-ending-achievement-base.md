# 正常離開的政績靜態底圖

狀態：CONFORMED，限正常退出時已見完整靜態底圖。對應 [#47](https://github.com/wicanr2/taipei/issues/47)，母項 [#32](https://github.com/wicanr2/taipei/issues/32)。取得政績後的圖案、文字變化及動畫仍 DRAFT，不宣稱完整政績畫面已 HD 化。

沿用使用者已確認的 B 細緻手繪材質、1280×800、Noto Sans CJK TC 與 F12。保留原版構圖、內容、十個圖案位置、阻塞輸入及正常退出。此層不重算政績或寫入任何原版狀態。

## 原版來源

來源核對工具 [ending_scene_source_check.py](../../workspace/tools/ending_scene_source_check.py) 直接讀取兩份唯讀 ROM，獨立完成每個壓縮串流，與四份正常 GUI 收據逐 byte 相同。原子收據來自 `gui-infrastructure-cold-r2/` 與 `gui-budget-cold-r4/` 的首次退出及全新 EXE 冷讀後退出；都完成正常存檔、讀檔與兩次原版退出，不使用快照或狀態注入。

| ROM | SHA-256 | 從零起算成員 | ROM 檔案偏移 | 成員長度 |
|---|---|---:|---:|---:|
| RS201.ROM | `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29` | 23 | 193647 | 17587 |
| RS201A.ROM | `5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0` | 1 | 1568 | 17587 |

已證實，限可見底圖：兩份成員 bytes 相同，SHA-256 `cc1e06a9ecaa3032c38f87ba14a1c70ccb5ccdeb5bd12421fdeca151c3ff40ef`。前四 bytes 為小端序寬高 320×200。其後非零 bytes 是單一色號，零值後接色號及非零重複次數。12,444 個單值及 1,713 個重複段完整消耗輸入，產生 64,000 個色號，SHA-256 `0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd`。每個重複段保留 ROM 檔案偏移及輸出偏移，見本機 `workspace/runs/ending-scene-native/source-check.json`。這項結論不推廣至其他候選格式。

已證實，限已抽樣玩家路徑：畫面為模式 0x13、DOS 等待輸入且未退出，後續普通 Space 經原版退出並切至模式 3。四份底圖的 23 個已用色盤項目相同。標題人工辨讀為「您的政績」，原版藍色字墨為色號 148，範圍 (128,3)-(191,17)，座標採右下不含。沒有據此推定 EXE 的繪字函式或內部評分規則。

## 可撤回原型

內建 imagegen 依原版畫面作 B 風格重繪，提示詞與原件保存在 `workspace/prototypes/hd-style/ending-scene-b-candidate-v1.prompt.txt` 及 `ending-scene-b-candidate-v1-generated.png`。保留桃色石紋邊框、紅色面板、頂部凹口及上下各五個暗紅圖案，沒有新增文字或控制項；原版及衍生素材只留本機。

[ending-scene-prototype](../../workspace/app/cmd/ending-scene-prototype/main.go) 以固定 Go／x/image CatmullRom 將原件 1586×992 縮至 1280×800，再由固定 Noto 字型繪製標題。字型 SHA-256 `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4`，SIL OFL 1.1 授權 SHA-256 `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2`。52 點、72 DPI、不使用 hinting，四字皆有 glyph；安全矩形 (512,12)-(768,68)，實際字墨 (537,16)-(742,65)，共 4,459 個非透明像素。字色沿用原版 (0,0,203)。已在實際 1280×800 尺寸目視核對。

| 本機原型輸入／產物 | SHA-256 |
|---|---|
| B 插畫原件 | `2dbdb09f57fe5324542117b2c00bc2b0d4ded4b24781594920f05663f6ad3284` |
| `ending-scene-v1/manifest.json` | `a86c26d3d8731d0d59042d7f461e3cf9468c32f431e127ecae5e1d421d357e41` |
| `ending-scene-v1/presentation.png` | `b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0` |
| 完整呈現 RGBA | `0147c5c7ad6d909d3c01e2084d879b6a32be68cc3167a6a6ae10210986d3a328` |

獨立 [ending_scene_prototype_check.py](../../workspace/tools/ending_scene_prototype_check.py) 使用既有另一套候選解析器重讀兩個 ROM 成員，核對四份正常來源、固定素材及字型。完整 1,024,000 個呈現像素等於 B 背景與原版藍色 Noto 字墨的獨立合成，字墨外全部相同；原版／B 比較圖兩側逐像素相同。結果 `workspace/runs/ending-scene-native/prototype-check-v1.json`。離線原型核對不代替正常玩家或產品驗收。

## 正式契約

- 輸入只讀原版 64,000 色號、色盤、顯示模式、DOS 阻塞及 HD 旗標。完整來源 SHA-256、23 個已用色盤、模式 0x13、阻塞相位均符合才接受，不用部分圖案或局部文字辨識。
- 自動出現的未知政績、文字變化、未確認相位或來源失配，維持完整原版畫面。不同底圖不從此原型猜補。
- 固定正式 manifest、PNG bytes、1280×800、完全不透明及字型／授權來源均符合才覆繪；素材缺失或損壞時維持完整原版，不誤落入其他家族。
- 每次呈現從當前原版重建，F12 不送 DOS 鍵，也不改亂數、時間、記憶體、輸入或 SAV。模式 3 不重用上一張 HD 底圖。
- 回報明確家族及拒絕原因。正常退出的 Space、原版圖案及文字維持原內容，不在正式畫面加入實作或驗證標示。

## 完成閘門

1. DRAFT 來源與原型審查，乾淨重生來源及五個原型檔案逐 byte 相同，再定正式固定輸入及 READY。
2. 完整底圖、來源單點失配、已用／未用色盤、模式、阻塞、F12、真實素材缺失／損壞及其他畫面隔離通過；獨立 Go／Python 核對正常原子收據的完整像素及統計。
3. 有效破壞背景、標題、來源、回退及家族統計，重算相關 PNG／雜湊後仍被兩個核對器拒絕，原件及未用色盤為正對照。
4. 正常冷啟動、施工、存檔、首次退出、全新 EXE 冷讀與第二次退出，兩次經過完整底圖並 F12 來回；原版資料及實際 SAV 不變。唯一正常輸入及步數先回寫 Issue，再核對兩側固定虛擬時間原版狀態。
5. Linux、Windows 及 macOS 兩架構編譯、檔案結構、輸入雜湊、來源權利、擁有權及 Docker 清理完成。正式封包、真機及其餘 HD 仍另驗。

## 2026-10-12 證據審查與 READY

DRAFT 後重新核對完整原版來源、兩個別名、四份正常退出、23 個已用色盤、完整 B 原型及 Noto 實際字墨。獨立 Python 合成核對通過，沒有未知文字或裁切。正常來源三檔及完整原型五檔從乾淨輸入重生逐 byte 相同，收據為 `workspace/runs/ending-scene-native/reproducibility.json`。原件與重生件保留，不覆寫。

以上證據足以將本底圖的靜態呈現升 READY。正式素材由 [ending_scene_ready.py](../../workspace/tools/ending_scene_ready.py) 匯出至 `workspace/prototypes/hd-style/ending-scene-ready-v1/`，僅包含 manifest 及固定完整 PNG；輸入及字型依上述雜湊，原型獨立核對與八檔重生皆為必要前置。正式 manifest 匯出後固定雜湊，再接產品。取得政績後的變化沒有正常證據，不由本批填補。

正式 manifest SHA-256 為 `009fcda9e87d5fcea175ae3112a5a5a610b04833a0d278f2e68b99dd4311ef57`；`screen.png` bytes 與已核對原型完全相同，SHA-256 `b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0`。兩檔亦乾淨重生逐 byte 相同，結果 `ending-scene-native/ready-reproducibility.json`。

[ending_screen.go](../../workspace/app/internal/hd/ending_screen.go) 已依 READY 接入完整來源、色盤、模式、阻塞、固定圖片及字型／授權閘門。只讀來源，整幀覆繪，失配保留原版。實際呈現測試核對 READY 前原型、F12 往返、五處來源失配、23 個已用色盤、未用色盤、模式及相位、九種真實載入故障與城市家族隔離，16.160 秒通過。首次測試的 `image.Image` 參考型別誤用已修正，原失敗紀錄保留。全部 HD／鍵盤回歸 116.613 秒通過。以上為 READY 後實作紀錄，正常驗收見下節。

## 2026-10-12 正常產品驗收

產品與工具固定提交 `70fc29dc91a3422b97554c219c59f8b7fc42fc71`，image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`，Go 1.24.13／Python 3.11.2，dosgolem 基線與七補丁不變。正常 GUI 使用 400000 steps/update，驗收條件及唯一狀態輸入均先回寫 #47，再執行。

| 閘門 | 結果 | `workspace/runs/` 本機證據 |
|---|---|---|
| 正常玩家路徑 | 冷啟動、新城市、電線施工、存檔、兩次原版退出、全新 EXE 冷讀施工格與資金 79980；兩次政績 F12 保留完整來源、讀鍵及非 theme 輸入 | `gui-ending-scene-cold-r1/result.json`、`ending-gui.json` |
| 獨立完整畫面 | Go／Python 全部 50 份原子收據通過，4 份實際覆繪政績；完整像素、家族及回退均核對 | `ending-scene-native/normal-receipts-r1.json`、`normal-go-check-r1.log` |
| 有效破壞 | 背景、標題、來源、相位、模式、色盤及家族 7 項，重算 PNG／雜湊後雙側拒絕；原件與未用色盤 2 個正對照通過 | `ending-scene-hd-negative-r1/result.json` |
| 原版狀態及 SAV | 兩側各 3,000,802,774 步、125 個抽樣點相同，實際覆繪政績 6 點；最終正常 GUI 原畫面、色盤、讀鍵、檔案操作及落地 SAV 相同 | `ending-scene-native/normal-state-r1.json` |
| 平台及輸入 | 四架構編譯與結構通過，Linux 乾淨重建 byte 相同，35 原始檔及 RAR 不變 | `ending-scene-native/build-input-integrity-r1.json`、`final-verification-r1.json` |

狀態採預登記每 24,000,000 步抽樣。唯一正常退出收據 SHA-256 `4ddce3987d53d0636a7d238c825989eaaab085b041bf4cd9a5253db6fa4030d7`，audit SHA-256 `b80f2aa5ff75d0b69a280fc0aa8961c5b2990298abfd1cce9fa0246c7f14168f`。兩側 221.223／213.623 秒，狀態 SHA-256 `d49e1d61592afb3dbf77e7787b5ee9e10c6af9bc8cfb5ccf5f724eb2a7dfd3d6`，結果檔 SHA-256 `ae4c6b201dad45516539f1de345c3b0457600dc6c3c93a83d28bafaf841fb6f9`。實際 `gui-cold-saves.GR4gqL/ROUND4.SAV` 93567 bytes，SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，與完整冷讀及狀態重播相同。

Linux SHA-256 `3df9783e2ca9229666f0f49b5fda9647b5bd94cf4271afc53a723d91acf46654`，另保留相同的 `taipei-preview-ending-clean-r1`。Windows amd64、macOS amd64／arm64 雜湊與標頭見完整性收據。實際畫面 `ending-scene-native/normal-ending-hd-r1.png` 直接取自正常收據，與 READY 前固定 PNG byte 相同，沒有後製，已檢視。輸出 UID/GID 1000，指定 find 為空，本批容器全部退出刪除。

正常 GUI 入口為 [gui_playtest.sh](../../workspace/tools/gui_playtest.sh) 的 `TAIPEI_TEST_ENDING_SCENE=1 TAIPEI_GUI_RUN=gui-ending-scene-cold-r1 TAIPEI_THEME=hd-b`；獨立核對為 [ending_screen_verify.sh](../../workspace/tools/ending_screen_verify.sh) 的 `normal`／`negative`。前件皆保留，工具拒絕覆寫。狀態使用 [presentation-audit](../../workspace/app/cmd/presentation-audit/main.go) 的 `-require-ending-screen -require-file-dialogs -render-interval-steps 24000000`，完整輸入及輸出依 #47 預登記。

本規格僅靜態底圖達 CONFORMED。其他政績、動畫、全部 HD、本批 Windows Wine／macOS 真機及正式封包未完成；母項保持開啟，素材只留本機。
