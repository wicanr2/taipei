# 正常離開的政績靜態底圖

狀態：READY，限正常退出時已見完整靜態底圖。對應 [#47](https://github.com/wicanr2/taipei/issues/47)，母項 [#32](https://github.com/wicanr2/taipei/issues/32)。取得政績後的圖案、文字變化及動畫仍 DRAFT，不宣稱完整政績畫面已 HD 化。呈現已實作並通過回歸，正常 GUI 與正式驗收尚未完成。

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

[ending_screen.go](../../workspace/app/internal/hd/ending_screen.go) 已依 READY 接入完整來源、色盤、模式、阻塞、固定圖片及字型／授權閘門。只讀來源，整幀覆繪，失配保留原版。實際呈現測試核對 READY 前原型、F12 往返、五處來源失配、23 個已用色盤、未用色盤、模式及相位、九種真實載入故障與城市家族隔離，16.160 秒通過。首次測試的 `image.Image` 參考型別誤用已修正，原失敗紀錄保留。全部 HD／鍵盤回歸 116.613 秒通過；正常 GUI、有效收據破壞、原版狀態及跨平台仍待驗，不宣稱 CONFORMED。
