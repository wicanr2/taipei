# 城市六功能選單

狀態：CONFORMED，限六個完整下拉面板、二十九種選取。對應 [#37](https://github.com/wicanr2/taipei/issues/37)，母項 [#31](https://github.com/wicanr2/taipei/issues/31)。確認後的功能視窗與完整 HD 另驗。

本批處理 F1–F6 城市功能入口的完整下拉面板，保留原版文字、選取、互動及矩形。沿用 B 細緻手繪材質、1280×800、Noto 與 F12。功能確認後開啟的存讀檔、預算、圖表、災害及其他視窗仍各自驗證。

## 原版證據與界線

原始 EXE／ROM、dosgolem 與六補丁沿用 [021](021-tool-submenus.md) 固定輸入。ROM SHA-256 為 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`。定位採 ROM 檔案偏移及從零起算的成員／字模索引，畫面座標為原版 320×200。

- 已證實，限正常可見像素：F1 的「返回」符合 ROM57 索引 389／390，DOS 三字符合 ROM56 的 5×7 ASCII 字模，原位為 (50,41)、(56,41)、(62,41)。F2 四列文字符合 ROM57／58 原字模及字碼，沒有推定 EXE 繪字呼叫來源。
- 已證實，限正常可見操作：六入口全部二十九種選取均符合完整原矩形。上下鍵依選項循環，左右鍵切換相鄰選單並重設選取為 0，兩端亦循環；Escape 關閉並恢復原城市畫面。八十二次動作的原版讀鍵及前端 release 由原子收據逐次核對。
- 已證實，限完整邊框與背景：色號 3 背景、頂底交錯 126／0、左右 126，頂右覆寫為 126，底右保留交錯結果。文字選取為 55，其餘為 15。全部字模及原字碼重新由 ROM56／57／58 讀取，沒有未知字或歧義別名。
- 確認按鍵及存退讀的既有正常路徑已包含 F1／F2。其餘選項開啟後的功能視窗及動態內容不在此面板規格中，不推定其語意或 HD 已完成。

| 面板 ID | 入口 | 原版完整矩形 | 選取數 |
|---|---|---|---:|
| `city-f1` | F1 離開 | (10,35,68,19) | 1 |
| `city-f2` | F2 檔案 | (53,35,68,64) | 4 |
| `city-f3` | F3 市長 | (97,35,68,49) | 3 |
| `city-f4` | F4 圖表 | (141,35,68,94) | 6 |
| `city-f5` | F5 災難 | (185,35,68,154) | 10 |
| `city-f6` | F6 環境 | (228,35,68,79) | 5 |

正常來源工具為 [city_menu_playtest.sh](../../workspace/tools/city_menu_playtest.sh)／[city_menu_playtest.py](../../workspace/tools/city_menu_playtest.py)，每個入口由真實冷啟動進城市，原版速度 0 暫停，逐次等待原版讀鍵與前端 release。收尾採有界停止，只作來源探索；原版退出另以完整正常存退讀路徑驗證。

## 呈現契約

- 由 [city_menu_catalog.py](../../workspace/tools/city_menu_catalog.py) 重建完整交錯邊框、背景及全部原字模；每個選取狀態與正常完整矩形相同才登錄。原字碼、候選 Unicode 與字形對應需審查，不用未知字猜補。
- 沿用固定 `menu-blue-b-v1.png`，SHA-256 `eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9`。Noto 中文採 52 點，DOS 英文採 28 點，72 DPI、無 hinting；保留原位及字距，先掃描實際墨跡再檢查完整畫面。
- 固定字型、授權、manifest、來源完整矩形、使用中色盤及面板 PNG 全部匹配才覆繪。每幀先恢復原版，只改完整面板矩形；矩形外維持原版四倍像素。選取中的頂部標題或模態背景未在此批覆繪時仍列為完整 HD 的未完成項。
- 不改原版 F1–F6、方向、確認或取消操作；F12 不送入 DOS。來源或資產失配完整回退，單張素材故障不影響其他已確認面板。

輸入為原版 64,000 bytes 色號、256×3 色盤、顯示模式與主題。只在模式 0x13、HD 啟用且完整來源及使用中色盤符合固定狀態時接受。面板列入獨立二十九狀態集，於阻塞輸入回退前辨識；既有啟動、說明及工具面板優先順序保留。命中時輸出 `panel=city-fN`、`panel_selection=0..count-1`、`panel_reason=matched-panel`，其他覆繪層計數為零。失配時保留完整原版像素，不以部分文字匹配覆蓋畫面。

資料鏈為原始 ROM／正常畫面 → 固定來源及 layout → 固定 Noto 面板 → 已確認完整 ROI → GUI。此層只讀原版色號及色盤，不寫原版記憶體、輸入、規則或存檔；狀態與存退讀不變仍須在實作後驗證。

| 固定本機輸入 | SHA-256 |
|---|---|
| `city-menu-layout-v1.json` | `91dc1347725734638035f0488233945d46db59a173fce8dec3dcc8a5c62f6c64` |
| `city-menu-sources-v1.json` | `eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870` |
| `city-menus-v1/manifest.json` | `699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5` |
| Noto Sans CJK TC Regular Sans2.004 | `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4` |
| Noto 授權 | `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2` |

字型、原文衍生資料、原版擷取與 B 素材只留本機，不加入 Git。原字模對應只證明可見像素及字碼，不證明原 EXE 的實際繪字呼叫來源。

## READY 與完成閘門

1. 六入口與全部選取、原文、方向循環、左右跨選單、Escape 均有正常證據；確認後的功能視窗另驗。所有完整來源逐 byte 重建，固定 layout／來源／manifest SHA-256。
2. 審查全部 Unicode、最長實際文字、字距、安全矩形及實際 Noto 墨跡，離線面板乾淨重生相同，再升 READY。
3. 正常 HD 遍歷全部狀態、跨選單、取消及六場景 F12；完整來源、固定參考與全部區外獨立核對。
4. 文字、背景、區外、來源、色盤、選取及 ID 竄改，同步重算受影響雜湊及原版 PNG 後仍被拒絕。真實資源另驗缺失／損壞、完整回退與故障範圍。
5. 正常施工、存檔、兩次原版退出及全新 EXE 讀回原施工格；原版資料不變。唯一正常輸入重播兩側完整原版步數，HD 預登記每 24,000,000 步抽樣並要求本批二十九狀態全部涵蓋，外層上限 900 秒，不宣稱逐幀對拍。137 份原子收據步數均與此間距對齊。
6. Linux、Windows、macOS 兩架構編譯與檔案結構；原始檔雜湊、入口、擁有權與 Docker 清理通過。真機與正式封包另驗。

## 2026-10-11 來源與原型審查

`city-menus-native/` 及 `city-menus-native-extra/` 共 137 份正常冷啟動原子收據。完整來源重建通過二十九狀態及 246 個原始單點破壞；Go 單幀核對器分別核對 116／21 份原版 PNG、色號、色盤及四倍呈現。`city_menu_source_check.py` 驗六個完整操作序列、八十二次原版讀鍵及 release、選取循環與兩端跨選單、六次 Escape 恢復原地圖。

離線二十九面板的 599 項實際 Noto 墨跡均在安全矩形內，各墨跡矩形沒有重疊；二十九 PNG、manifest 與墨跡報告共三十一檔，乾淨重生逐 byte 相同。已視覺審查 F1 混合字型、F5 最長十列及 F6 四字選項，未見缺字或裁切。擴充離線工具後，原五工具二十檔仍逐 byte 相同。

原六冷啟動探索碰到既定 900 秒上限，停於 F6 第一個 Up；保留原件，另以相同 image、binary、操作及斷言單獨補跑 F6，退出 0。沒有放寬來源或控制斷言，也沒有把探索末尾停止當成原版退出。正式 HD GUI、竄改負對照、狀態及存退讀仍須實作後驗證。

工具為 Go 1.24.13／Python 3.11.2，image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`，原版唯讀，輸出 UID／GID 1000，無網路、3 GiB／2 CPU／128 PID 上限。工具原始碼、程式、輸入及輸出雜湊保存在 `workspace/runs/city-menu-source/provenance.json`，來源與控制結果在同目錄的 `catalog.json`、`controls-verification.json`、`prototype-verification.json`。

重現正常來源由 [city_menu_playtest.sh](../../workspace/tools/city_menu_playtest.sh) 執行。原型在上述 Docker image 內執行：

```sh
/workspace/runs/tool-panel-prototype -family city -state-count 29 \
  -materials /workspace/prototypes/hd-style \
  -out /workspace/prototypes/hd-style/city-menus-v1 \
  -layout-sha 91dc1347725734638035f0488233945d46db59a173fce8dec3dcc8a5c62f6c64 \
  -sources-sha eb98c1def205eb39e533f9646ad9336fafc7268559998e93e3a1ed1c7157f870
```

本節記錄來源審查時點的 READY 狀態，產品結果見下節。本文件入口由 [CONTEXT](../../CONTEXT.md) 索引。

## 2026-10-11 產品驗證

固定來源已接入 [panels.go](../../workspace/app/internal/hd/panels.go) 及 [render.go](../../workspace/app/internal/hd/render.go)，在阻塞輸入回退前辨識。既有啟動、說明與工具面板保持優先；只有本批完整矩形接受固定 Noto PNG，其他覆繪層計數為零，區外保持原版四倍像素。

| 閘門 | 實際結果 | 本機證據 |
|---|---|---|
| 正常六功能 HD | 一次冷啟動、107 份收據、二十九選取、八十二次讀鍵／release、上下與左右循環、六次 Escape 復原；六場景 F12 不送入 DOS | `workspace/runs/city-menus-hd/controls-verification.json`、`city-panels-verification.json` |
| 原子單幀及區外 | 六功能 107 份及完整存退讀 37 份，原版 PNG／色號／色盤、固定 HD 參考及全部區外均通過 | `workspace/runs/city-panels-verification.log` |
| 有效竄改 | F1 小面板與 F5 十列面板各七項，更新受影響雜湊及原版 PNG，Python／Go 全部拒絕 | `workspace/runs/city-panels-negative/f1/`、`f5/` |
| 實際資源故障 | Go 全套 21.819 秒、無跳過；全二十九來源及區外、來源／色盤／模式／主題、必要檔案缺失／竄改及單張故障隔離通過 | `workspace/runs/city-panels-go-tests.log` |
| 正常存退讀 | 施工、原版存檔、兩次原版退出、全新 EXE 讀回原施工格；存檔及資金保持基準，標題與工具冷讀恢復 | `workspace/runs/gui-cold/result.json`、字型／工具 verification JSON |
| 原版狀態 | 同一正常輸入兩側各 5,184,000,000 步，216 次明示 HD 抽樣涵蓋二十九城市選取共 164 次、說明一次及城市各層 14 次，原版狀態相同 | `workspace/runs/city-panels-state-audit.json`、`city-panels-state-provenance.json` |
| 平台及輸入 | Linux amd64、Windows amd64、macOS amd64／arm64 編譯與架構通過；Linux 由現行來源重建逐 byte 相同，35 原始檔與 RAR 雜湊不變 | `workspace/runs/city-panels-state-provenance.json` |

存檔 SHA-256 維持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，冷讀施工格維持 `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139`。前批完整 GUI 原件保存於 `workspace/runs/gui-cold-before-city-menus/`，沒有覆寫 021 證據。

狀態重播使用 `city-menus-hd/f6/escape-capture.zip` 的唯一正常硬體輸入、固定 dosgolem 初始狀態與虛擬時間，原版 RNG 未改。原版側 398.045 秒、HD 側 351.661 秒；RAM、CPU、色號、色盤、埠、OPL、讀鍵、DOS 狀態與檔案操作相同，狀態 SHA-256 為 `df85c5d5f612ff996d7b671bd81ba1238e41e55bff926dc293c90975ece21174`。HD 間距為預登記的 24,000,000 步，沒有宣稱逐幀或跨 RNG 實作精確對拍。

重現入口為 [city_menu_playtest.sh](../../workspace/tools/city_menu_playtest.sh)，指定 `TAIPEI_THEME=hd-b TAIPEI_CITY_MENU_RUN=city-menus-hd`，以及 [city_panels_verify.sh](../../workspace/tools/city_panels_verify.sh)。完整存退讀另由 [gui_playtest.sh](../../workspace/tools/gui_playtest.sh) 執行。每次重跑前保存既有收據，保留固定 image、程式、輸入與斷言；本批工具及全部收據雜湊由 [city_panels_provenance.py](../../workspace/tools/city_panels_provenance.py) 彙整。

本批達 CONFORMED。選取中的頂部標題、模態背景、確認後的視窗／圖表、其他圖片／場景／動畫、平台真機及正式封包仍未完成，#31 與 HD 母項保持開啟。全部原版及衍生素材只留本機。
