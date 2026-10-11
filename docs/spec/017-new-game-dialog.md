# 新遊戲說明視窗

狀態：**CONFORMED，限研究前端的新遊戲說明視窗**。對應 [#31](https://github.com/wicanr2/taipei/issues/31) 的單一視窗批次，沿用 [完整 HD 範圍](015-full-hd-scope.md)。本批先完成來源審查與 READY 契約，再接入整個底板、框架與原文；其他視窗與正式封包另驗。

## 來源審查

固定 ROM 與來源盤點見 [008](../re/008-full-asset-inventory.md)。`RS201.ROM` 成員 22 位於 ROM 檔案偏移 `180507`，圖片為 236×132。依零 byte、色號、直接重複次數解碼，完整色號 SHA-256 為 `a6299b68e4e28c3309bcbf10f2e562c4a9be7fb7d2a43f8a4bc79e69a77ccc8b`。

已證實：正常冷啟動主選單、城市選擇後，`new-game-capture.zip` 中 `(18,37)-(254,169)` 完整逐色號匹配該來源，畫面 SHA-256 `c58155921b30dd1a7a95d1da63e032dc49f0ad0d29fa78661af62efb676bcab7`。視窗等待原版按鍵。這是 dosgolem 正常玩家路徑收據，不是直接注入狀態。

已人工對照放大原圖與 [字模候選](../re/009-chinese-font-sources.md)，保留原文、標點、七行分行與縮排。轉錄資料僅存本機 `workspace/prototypes/hd-style/new-game-text-v1.json`，不把原版整段文字加入 Git。來源字模可匹配的字維持原位置；原圖「章」的起點為原生 x=200。其他全形字每格 16 原生像素，ASCII 附註使用較小字級。

轉錄資料 SHA-256 `2fbe3ae36cccf679965f33ac1a8d8d49ea866e913baaeb7dda119b3fa1794a71`，90 個定位欄位、92 個字元。實際 Noto 墨跡及原文人工核對後固定完整參考 `new-game-noto-reference-v1.png`，SHA-256 `6bfa6faeffd0950d31af1a5bb9da84aa71af4a34dc36dae374d3d387b1e6c7e9`。該參考由已審查的素材及字型匯出，收據核對另以固定雜湊檢查，不由待驗收據重生。

62 字的原位置與完整 15×15 墨跡同共用字模完全相符。兩處標點在原圖中的形狀與共用字模不同，連同其餘 26 個欄位依放大原圖人工核對；不因 Unicode 候選存在就宣稱字模相同，也不把候選搜尋接入產品覆字。

## 呈現契約

- 模式 19、HD 開啟、固定 ROM、完整矩形色號與使用中的六個色盤項目全部相符，才顯示此視窗。使用色號依序為 `15,16,20,23,27,134`，RGB 串接 SHA-256 `701e28d343effaf04f5e2b535626a87a3b18e4a1c2fcdc10cbb2a6939714e4de`。此獨立條件容許原版等待輸入，不套城市地圖條件。
- 只改輸出矩形 `(72,148)-(1016,676)`，共 944×528。每幀先重建原版；關閉、失配或切換後沒有殘影。其他像素保持原版，此幀不畫地景或城市工具。
- 底板為 imagegen 依原圖與已確認 B 風格重繪的空白銀框藍底，固定資產 `new-game-panel-b-v1.png`，SHA-256 `87a25f1552c42d5f4cc77c1d49c07f69d02d103c6f154feb43d57bc1445558e5`。原圖、提示與正規化紀錄只存本機。
- 字型與授權雜湊沿用 [013](013-noto-menu-prototype.md)。全形字 Noto 56 px，ASCII 附註 28 px，無 hinting。全形字逐格定位，不使用自動換行。每字實際墨跡須完整落在原格與面板內緣安全矩形 `(16,16)-(928,512)`。
- 素材、文字資料、字型、授權或版面失配均保留原版完整視窗，不顯示空白面板或部分文字。收據新增視窗識別與回退原因，不併入六個城市標題數量。
- 不改原版資料、輸入、規則或存檔。F12 只切呈現，不送 DOS。

## 預登記驗證

- 逐字核對原文、分行、實際墨跡與完整固定參考圖；完整面板逐像素比對，區外像素逐點核對原版。
- 原始矩形改一像素、使用中色盤失配、撤除或損壞素材、文字資料失配、字型失配及原版模式，各自必須完整回退。未使用色盤變動不影響識別。
- 真實 GUI 冷啟動進入說明，F12 關閉及恢復，再按原版空白鍵進入難度與城市；保留來源幀、DOS 讀鍵與切換收據。之後施工、存退讀正常，視窗不殘留。
- 收據核對器拒絕被竄改的面板字形、邊框與區外像素，即使重新計算呈現雜湊。獨立來源核對不得只相信收據的覆繪旗標。
- 固定正常玩家輸入與虛擬步數，實際經過此視窗覆繪，比較有／無呈現的完整 RAM、CPU、原版畫面、色盤、埠值、OPL 與讀鍵。
- Linux、Windows、macOS 研究前端編譯；不據此宣稱封包或真機已驗。#31 與整體 HD 母項保持開啟。

## 已執行驗證

實作為 [dialog.go](../../workspace/app/internal/hd/dialog.go)，實際資料測試為 [dialog_test.go](../../workspace/app/internal/hd/dialog_test.go)。工具鏈沿用 [007](../re/007-running-city.md) 的固定 GUI image，Go 1.24.13、Python 3.11.2；完整來源解碼與字模資料由 Python 3.13.16 盤點。位址均為 ROM 檔案偏移。使用的 dosgolem commit 及六個補丁沿用前端建置來源，未改上游。

- 容器內 `go test -mod=readonly -p 1 ./internal/hd ./internal/original` 通過，環境指定原版 `/orig`、素材 `/workspace/prototypes/hd-style` 及當時的正常收據 `/workspace/runs/gui-cold`，該份收據現保留於 `gui-cold-before-panel/`。來源、色盤、模式、未使用色盤、F12、關窗殘影、素材／文字／字型／授權的撤除與損壞均通過；原始色號不改寫。
- `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 通過。正常開窗、HD → 原版 → HD 的三份收據，其原版畫面 SHA-256 都為 `c58155921b30dd1a7a95d1da63e032dc49f0ad0d29fa78661af62efb676bcab7`，讀鍵紀錄完全相同。之後進入難度、城市、施工、存檔、原版退出、全新 EXE 讀檔與再次退出。存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，施工格冷讀相同。結果為 `workspace/runs/gui-cold/result.json`。
- `hd_dialog_check.py --receipts /workspace/runs/gui-cold` 重算完整來源及色盤條件，兩份 HD 說明面板與固定參考逐像素相符，區外保持原版；關閉與切回原版沒有殘影。全部 37 份收據通過既有 Noto 標題與圖示獨立核對，11 份完整城市覆繪、26 份城市回退。結果為同目錄 `dialog-verification.json`、`font-verification.json`、`icons-verification.json`。
- `receipt-check -dir /workspace/runs/gui-cold -font-reference /workspace/prototypes/hd-style/font-comparison/noto-font.png -ui-reference /workspace/prototypes/hd-style/city-icons-b-v1.png -dialog-reference /workspace/prototypes/hd-style/new-game-noto-reference-v1.png` 通過 37 份封裝。`hd_dialog_negative.py` 破壞實際白色字形 `(110,180)`、邊框、區外、原始色號與色盤，更新相應雜湊後五項仍被拒絕；結果為 `workspace/runs/dialog-negative/result.json`。
- `presentation-audit -receipt /workspace/runs/gui-cold-before-panel/uncover-power-capture.zip -require-font -require-icons -require-dialog` 使用相同正常輸入，兩側各 1,224,000,000 步。原版完整 RAM、CPU、畫面、色盤、埠值、OPL 與讀鍵相同，包含 55 幀完整說明覆繪。狀態 SHA-256 `670f2fea2db251b7d694cf1e12d4254110669e09f80179d82865ec786937062e`。結果與輸入收據雜湊保存在 `workspace/runs/dialog-state-audit.json`、`dialog-state-provenance.json`。
- Linux amd64、Windows amd64、macOS amd64／arm64 重編譯通過；Windows 保留既有 YMFM 編譯警告。35 個原版檔案與 RAR 雜湊不變。沒有新增真機或正式封包聲明。

首次 GUI 在開場只走到 432M 步即超過單次等待 120 秒，空讀鍵紀錄又引發診斷例外。證據保留 `workspace/runs/gui-dialog-timeout/`，診斷修正依 [#33](https://github.com/wicanr2/taipei/issues/33)。其他工作結束後，以同一 image、同一命令及原有時間門檻乾淨重跑通過；沒有為通過而修改遊戲或放寬門檻。覆繪前收據保留 `gui-cold-before-panel/`。
