# 模擬台北：dosgolem 與 HD 呈現

以 dosgolem 執行原版《模擬台北》，保留城市經營玩法，加入 1280×800 的 HD 呈現、Noto 高清黑體與五語系介面。

玩家須自備合法取得的原版資料。原版執行檔、資料、美術、音訊與權利未明的 HD 素材
只留本機，不加入此儲存庫或公開封包。下列選定的文件截圖依使用者指示收錄於私人儲存庫，
不納入自有程式授權。

## 遊戲背景

《模擬台北》是一款以臺灣城市治理為題材的 DOS 城市建設與經營遊戲。
公開典藏資料將它列為 1992 年作品，由聯邦開發、資策科技代理，
見[奧米加典藏條目](https://www.omega.idv.tw/kdb120/viewthread.php?threadid=5296)與[中文模擬類遊戲目錄](https://chiuinan.github.io/game/game/cgame33.htm)。

玩家扮演市長，鋪設道路與電線，建設電廠和公共設施，再透過預算、民意與城市圖表處理交通、住房、治安和污染問題。
除了建設新城市，也能接手「災難台北」等既有城市情境。原版說明設定的目標，是將新城市發展或將災難城市恢復為人口超過五十萬的都會區。
玩法與目標可回查[原版說明來源](docs/spec/017-new-game-dialog.md)及[已核對的介面文字](workspace/app/locales/ui.tsv)。

![HD 繁體中文的災難台北城市實際畫面](workspace/screenshots/city-disaster-zh-Hant.png)

上圖為 Linux 前端從正常「災難台北」選單進入 `DISA1.DSA` 的實際畫面，以原版 `0` 鍵暫停。
顯示目前已接入的 HD 地景、道路與介面，尺寸為 1280×800；來源見[截圖清單](workspace/screenshots/manifest.json)。

## 目前可玩範圍

原版冷啟動、新遊戲、電線施工、存檔、退出及全新啟動讀檔已通過正常操作驗證，音訊已接入實際播放器。
F4 六圖表已依正常遊玩抽驗通過，包含開啟、F12 切換、返回城市、電力圖五語系切換，以及同次存讀檔與退出，範圍見[圖表契約](docs/spec/029-chart-windows.md)。

| 功能 | 已接入內容 |
|---|---|
| HD 圖像 | B 細緻手繪材質地景、首批 25 張道路與電線、火力電廠 36 格靜態圖塊、城市框架、工具與選單、預算和圖表外框、政績靜態底圖 |
| HD 文字 | Noto 高清黑體，包含啟動選單、城市功能、工具、視窗、預算、狀態列與圖表文字 |
| 五語系 | 繁體中文、簡體中文、日文、韓文、英文；已盤點的 146 筆中文來源皆有譯文，涵蓋開場、上任信、介面、圖片可讀文字及逐字訊息 |
| 遊戲中切換 | F11 選語言並保存設定；F12 切原版繁中／HD；Shift+F1 顯示五語系操作說明 |

原版程式繼續負責模擬規則、亂數與存檔，HD 層改變呈現。玩家檔名、原版數值與商標保留原樣。
重繪目標包含所有圖片與操作介面；其餘圖片、動畫與 Windows、Linux、macOS 正式封包仍在製作，尚無正式交付包。
目前證據與限制以 [CONTEXT.md](CONTEXT.md) 及[驗收矩陣](docs/verification-matrix.md)為準；翻譯範圍見[完整來源覆蓋契約](docs/spec/033-localization-source-coverage.md)。

## 操作

| 按鍵 | 功能 |
|---|---|
| Shift+F1 | 開啟或關閉操作說明；原版 F1 仍是離開 |
| Esc | 關閉目前的說明或語言面板 |
| F11 | 遊戲中切換語言並保存選擇；Help 中選完返回說明 |
| F12 | 切換原版繁中／HD 呈現 |

## 原版與 HD 五語系畫面

以下為 Linux 前端從正常新遊戲入口擷取的實際畫面。城市以原版 `0` 鍵暫停，再以 F11／F12 切換。
城市與預算各組的原版色號畫面及可見顏色一致；原版為 320×200 的四倍最近鄰放大，HD 為 1280×800。
點圖片可看完整尺寸。截圖展示目前已接入的呈現，不代表全部圖片已重繪或三平台封包已驗收。

| 模式／語言 | 城市 | 預算 |
|---|---|---|
| 原版繁體中文 | ![原版繁體中文城市畫面](workspace/screenshots/city-original.png) | ![原版繁體中文預算畫面](workspace/screenshots/budget-original.png) |
| HD 繁體中文 | ![HD 繁體中文城市畫面](workspace/screenshots/city-zh-Hant.png) | ![HD 繁體中文預算畫面](workspace/screenshots/budget-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文城市畫面](workspace/screenshots/city-zh-Hans.png) | ![HD 簡體中文預算畫面](workspace/screenshots/budget-zh-Hans.png) |
| HD 日文 | ![HD 日文城市畫面](workspace/screenshots/city-ja.png) | ![HD 日文預算畫面](workspace/screenshots/budget-ja.png) |
| HD 韓文 | ![HD 韓文城市畫面](workspace/screenshots/city-ko.png) | ![HD 韓文預算畫面](workspace/screenshots/budget-ko.png) |
| HD 英文 | ![HD 英文城市畫面](workspace/screenshots/city-en.png) | ![HD 英文預算畫面](workspace/screenshots/budget-en.png) |

<details>
<summary>Help 五語系畫面</summary>

以 Shift+F1 開啟，沿用同一城市。F11 可切換說明語言，Esc 返回遊戲。

| 語言 | 操作說明 |
|---|---|
| 繁體中文 | ![繁體中文操作說明](workspace/screenshots/help-zh-Hant.png) |
| 簡體中文 | ![簡體中文操作說明](workspace/screenshots/help-zh-Hans.png) |
| 日文 | ![日文操作說明](workspace/screenshots/help-ja.png) |
| 韓文 | ![韓文操作說明](workspace/screenshots/help-ko.png) |
| 英文 | ![英文操作說明](workspace/screenshots/help-en.png) |

</details>

<details>
<summary>F4 六圖表與五語系對照</summary>

情境為 DISA1.DSA，由正常「災難台北」選單進入。六個選項分別確認後擷取，保留原版已計算的資料格，HD 更新外框與文字。電力圖另展示原版及五語系，切換前後的原始資料畫面相同。

| 圖表 | HD 繁體中文 |
|---|---|
| 電力供應 | ![HD 電力供應圖](workspace/screenshots/chart-power-zh-Hant.png) |
| 交通密度 | ![HD 交通密度圖](workspace/screenshots/chart-traffic-zh-Hant.png) |
| 人口密度 | ![HD 人口密度圖](workspace/screenshots/chart-population-zh-Hant.png) |
| 犯罪率 | ![HD 犯罪率圖](workspace/screenshots/chart-crime-zh-Hant.png) |
| 房價 | ![HD 房價圖](workspace/screenshots/chart-land-value-zh-Hant.png) |
| 污染 | ![HD 污染圖](workspace/screenshots/chart-pollution-zh-Hant.png) |

| 電力圖模式／語言 | 畫面 |
|---|---|
| 原版繁體中文 | ![原版電力供應圖](workspace/screenshots/chart-power-original.png) |
| HD 簡體中文 | ![HD 簡體中文電力圖](workspace/screenshots/chart-power-zh-Hans.png) |
| HD 日文 | ![HD 日文電力圖](workspace/screenshots/chart-power-ja.png) |
| HD 韓文 | ![HD 韓文電力圖](workspace/screenshots/chart-power-ko.png) |
| HD 英文 | ![HD 英文電力圖](workspace/screenshots/chart-power-en.png) |

六個正常入口、F11／F12、返回城市、同次存讀檔與退出已通過遊玩抽驗。
此結論限已驗路徑；完整機器狀態對拍、圖表流程全新 EXE 冷讀及平台真機未執行，見[圖表契約](docs/spec/029-chart-windows.md)。

</details>

來源、程式與圖片雜湊見[截圖清單](workspace/screenshots/manifest.json)。
重生入口為 [readme_screenshots.sh](workspace/tools/readme_screenshots.sh)，以[匯出工具](workspace/tools/export_readme_screenshots.py)核對後收錄，只在 Docker 內執行；
圖表使用 [chart_locale_gui.sh](workspace/tools/chart_locale_gui.sh) 擷取，經[整張畫面核對](workspace/tools/chart_locale_check.py)後[匯出](workspace/tools/export_chart_screenshots.py)。
災難台北城市畫面由[收據回核工具](workspace/tools/accept_chart_playtest.py)從同一批正常遊玩收據匯出。
原始收據保存在本機工作區，未加入儲存庫。驗證界線見[驗收矩陣](docs/verification-matrix.md)。

## 開發與文件

工作區使用 `workspace/`。遊戲專屬探針與可重現工具放在其下；
研究輸出、工具快取、原版資料與 dosgolem 隔離副本排除於 Git。

| 入口 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | 範圍、授權、工作流程與外部知識入口 |
| [CONTEXT.md](CONTEXT.md) | 目前真相、有效決策與限制 |
| [GitHub Issues](https://github.com/wicanr2/taipei/issues) | 唯一工作項目與進度來源 |
| [驗收矩陣](docs/verification-matrix.md) | 玩家路徑、證據與完成邊界 |
| [WORKLOG.md](WORKLOG.md) | 按時間追加的工作歷程 |

探針入口為 [workspace/tools/probe.sh](workspace/tools/probe.sh)，只在 Docker 內建置與執行。
固定版本、原始資料路徑與重播方法見[啟動基線](docs/re/002-dosgolem-startup.md)。
前端建置與正常 GUI 測試入口見[前端契約](docs/spec/005-frontend-preview.md)。

自有程式及文件使用 [RRSAL-1.0](LICENSE)，
不把原版素材或第三方依賴納入自有授權。本專案與原版權利人無隸屬關係。
OPL2 合成使用 [YMFM](https://github.com/aaronsgiles/ymfm) 的 BSD 3-Clause 核心，固定來源與驗證範圍見[音訊契約](docs/spec/009-opl2-audio.md)。
