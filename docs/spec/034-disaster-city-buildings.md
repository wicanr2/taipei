# DISA1 首批建物

狀態：CONFORMED，限以下三種正常已見靜態建物的 48 個圖塊及已驗遊玩路徑。對應 [#56](https://github.com/wicanr2/taipei/issues/56)，母項 [#30](https://github.com/wicanr2/taipei/issues/30)。沿用 B、1280×800、Noto、F11／F12 與原版版面，不改遊戲規則或存檔。

本批從 #54 正常災難台北城市收據核對完整可見的三種 4×4 建物來源。各建物只以 ROM 成員／圖像及原始像素定位，不由外觀命名其發展階段或統計規則。初期 DRAFT 研究與下一閘門保留於下方，正式實作依 READY 契約。

## 固定來源與研究入口

- 原版 EXE／ROM、dosgolem 基底、七補丁與 Docker 版本沿用 [029](029-chart-windows.md)；定位使用 `RS201.ROM` 檔案偏移、零基成員／圖像及原版 320×200 像素。
- 原始正常收據為本機 `workspace/runs/chart-locales-r2/gui/city-paused-capture.zip`，來源色號 SHA 與 #54 的 verification.json 核對，不改寫前件。
- [disaster_building_sources.py](../../workspace/tools/disaster_building_sources.py) 重讀原 ROM 與正常收據，逐格核對完整 81 bytes、全部別名、原位與使用色盤，再匯出完整建物供原型使用。
- 本批候選為成員 34、35、36 各一種正常已見的 4×4 完整來源；精確清單、偏移與雜湊由來源工具保存，原版與素材只留本機。

## 下一閘門

核對三個完整複合矩形與來源是否有重複別名。原型沿原構圖重繪，先審查實際 144×144 圖像及原位，再固定整格素材、來源與色盤、部分遮擋／未知相位回退及存讀檔影響。正式接入前補足 READY 契約與遊玩抽驗情境；沒有長時間狀態對拍門檻。

## 2026-10-13 來源及原型審查

已證實：三個正常完整矩形分別為成員 34 的原生 `(221,133,36,36)`、35 的 `(185,43,36,36)`、36 的 `(95,97,36,36)`，世界原點為 `(6,22)`。各圖庫有 96 張 9×9 圖，本批索引皆為 `4 + 24×row + col`，row／col 為 0..3。48 個完整 81-byte 圖塊互不重複，全部別名與 ROM 檔案／像素偏移保存在 `disaster-buildings-v1/sources.json`，SHA-256 `764054313fa809c6ab1e686a325751eb5fade49ada81fd99fabd569f6cac6272`。這些是正常畫面來源證據，不推定建物規則或下一發展相位。

內建 imagegen 依三個正常完整來源重繪，提示詞與生成原件留在本機 `workspace/prototypes/hd-style/disaster-buildings-v1/`。成員 34 保留六個彩色屋頂、步道與綠地；35 保留左右各五列紅／青屋頂及中央通道；36 保留左側灰青矩形、中央彩色形狀、下方通道與右側紫灰區。原型完整縮至 144×144 後才切片，沒有逐格縮放或新增建物。已檢視原位完整城市畫面。

[disaster_building_check.py](../../workspace/tools/disaster_building_check.py) 直接重讀 ROM、正常收據與固定生成原件，獨立核對三張完整 atlas、48 格來源及整張城市原型。原型 manifest SHA-256 `46aa12d3616bfa98fee4aa794f9553d6ce8f4dfd93ad70ad5495f2ba6f28f0be`，`check.json` 通過；原版及本批以外的像素保持固定前件。此核對不匯入產品呈現器。

## READY 契約

| 項目 | 契約 |
|---|---|
| 型別與來源 | 只讀原版 64,000 bytes 色號、256×RGB 色盤、模式、阻塞與已完成地圖原點。固定 ROM 的 34／35／36 成員，48 個完整 81-byte 來源相等才辨識，保留別名 |
| 素材 | `disaster-buildings-ready-v1/manifest.json`，SHA-256 `7dc484798f0d65962d35db56a33ac3153c7f65fb105daef3a28351018d6030e2`；schema 1、stage disaster48、三張不透明 144×144 atlas，各檔及完整 RGBA 雜湊在 manifest 固定 |
| 繪製 | 將每個已辨識原格對應 atlas 的 36×36 區塊原位繪入輸出。完整及部分可見建物沿原格切分，不依相鄰格猜圖；同一來源的不同世界位置使用同一切片 |
| 色盤 | 每個圖塊只檢查其實際使用色的固定 RGB；未使用色變更不拒絕。已用色失配時該格保留本幀原版，不重算顏色或推定相位 |
| 場景 | 沿既有完整城市、模式 0x13、非阻塞、年度視窗排除及已完成原點範圍閘門。選單、圖表、檔案等模態維持各自家族，不疊本批圖像 |
| 資源故障 | ROM／manifest 失配不畫本批。單張 atlas 缺少、損壞或形狀／透明度錯誤只使該成員回退，其他成員仍可繪製。每幀先恢復原版，不留前幀或借相鄰素材 |
| 收據 | `hd.city_buildings` 記 matched／painted／fallback、來源 `member/image` 次數及原因；併入既有總地圖計數，仍為 435 格。原版或模態時本家族為零 |
| 隔離 | 只寫 1280×800 RGBA 呈現，原版資料、RAM、亂數、時間、輸入與 SAV 不改；F12／F11 沿既有前端隔離，不重啟遊戲 |

素材匯出入口為 [disaster_building_assets.py](../../workspace/tools/disaster_building_assets.py)，固定生成 SHA、來源證據及 ImageMagick 6.9.11 Lanczos 1254→144；PNG 沿既有固定 RGBA8 編碼器。所有素材只留本機，不加入 Git。

## 驗收預登記

正常 GUI 入口為 [disaster_building_gui.sh](../../workspace/tools/disaster_building_gui.sh) 與 [disaster_building_gui.py](../../workspace/tools/disaster_building_gui.py)。呈現入口為 [city_buildings.go](../../workspace/app/internal/hd/city_buildings.go)，必要測試為 [city_buildings_test.go](../../workspace/app/internal/hd/city_buildings_test.go)。

- 三個完整 atlas、48 格、部分可見格及全部區外與 READY 前固定原型一致。來源逐像素失配、已用／未用色盤、實際 manifest／atlas 缺失或損壞須有測試。
- 從正常災難台北進 DISA1，以原版 0 暫停；確認建物實際繪製，F12 原版往返與 F11 五語系不改原始城市畫面。正常 F2 存檔與同次讀回，最後由原版退出。
- 六張原版／HD 五語系實際城市畫面作完整呈現核對，使用固定前件及本批原型，不由目前呈現器產生期望值；有效負對照重算受影響雜湊後仍須拒絕。
- Linux 與 Windows amd64、macOS amd64／arm64 重新編譯，原版輸入不變、輸出 UID/GID 與容器清理通過。真機、其他建物／相位及正式封包另記；驗收依正常遊玩抽驗，不作長時間 RAM／CPU／RNG 對拍。

## CONFORMED 證據

| 驗證 | 結果 |
|---|---|
| 素材重生 | 三個 atlas 與 READY manifest 共四檔從乾淨目錄重生逐 byte 相同；48 個獨立切片與完整城市原型核對通過 |
| 必要測試 | 三個新測試通過，涵蓋 48 格完整重組／區外、3888 項來源失配、已用／未用色盤、八項真實 manifest／atlas 缺失及損壞、原版／阻塞／原點隔離；來源測試首輪漏填固定收據 SHA，補入來源證據的既有值後單獨重跑通過，沒有修改產品 |
| 回歸 | 十一個道路／電線、火力與圖表測試全部通過、無跳過，81.759 秒；鍵盤套件通過。日誌為 `workspace/runs/building-regression-r1.log` |
| 正常遊玩 | `gui-buildings-r1` 從正常 DISA1 入口暫停，實際繪製 116 格本批來源。F12 往返、F11 五語系、原版寫入與同次讀回 BLDG.SAV、原版返回 DOS 均通過，沒有快照或狀態注入 |
| 呈現 | 六張實際原版／HD 五語系城市畫面各 1,024,000 像素核對通過；一個正對照與五個有效破壞重算受影響雜湊後仍正確拒絕。原型、文字與本批以外像素均取開工前固定參考，不匯入目前呈現器 |
| 編譯 | Linux amd64、Windows amd64、macOS amd64／arm64 重新編譯完成。Windows 保留既有 YMFM 編譯警告；不宣稱 Wine／平台真機或正式封包完成 |

正常收據 `workspace/runs/gui-buildings-r1/verification.json` SHA-256 `da0925ab7dd25e6c2e7c51d84e0aa6a7b1ebe2fa76044154828a0fde9504c84a`；完整呈現報告 `pixel-verification.json` SHA-256 `01507a06ce27cb573b23d4f33682a1c9e42b3fe7062316dfe47e1a78b2bfcc78`。BLDG.SAV 為 93567 bytes，SHA-256 `c44e4889acd6aec4b2d1c0088f87d096043685236136095c656d12673cad9100`，讀回不改檔。Linux 已驗 binary SHA-256 `5933a1f2554ee51419eae97493708cb99b2de8da726011e7887c06d5c9c348c3`，保留 `taipei-preview-buildings-r1`。

README 選定畫面由 [export_building_screenshots.py](../../workspace/tools/export_building_screenshots.py) 再核對原子 ZIP 與完整像素後收錄。素材、生成原件、提示詞、字型、binary、SAV 與原始收據只留本機；其餘建物與相位、全新 EXE 冷讀、平台真機及正式封包未驗，不外推本批完成範圍。
