# 模擬台北：dosgolem 與 HD 呈現

本專案以 dosgolem 執行使用者自備的原版《模擬台北》，接入現代前端與 HD 呈現。
目前已驗證原版冷啟動、電線施工、存檔、退出及全新啟動讀檔，並擷取到實際播放器音訊。
HD 採 B 細緻手繪材質、1280×800 與 Noto 高清黑體，遊戲中以 F12 切換。重繪範圍包含所有圖片與操作介面；目前已接入地景原型、第一批 25 張道路與電線、火力電廠 36 格靜態圖塊、正常退出的政績靜態底圖、城市框架、六個 Noto 標題與 F1–F6、六功能下拉選單、十四個工具及選取外框、五種工具子選單、新遊戲說明、主選單、城市與難度選擇、存讀檔視窗與離開提示、預算與稅率面板，以及底部費用、年月與資金文字。完整 HD 與三平台封包仍在製作，尚無正式交付包。驗證範圍見 [CONTEXT.md](CONTEXT.md)。

玩家須自備合法取得的原版資料。原版執行檔、資料、美術、音訊與權利未明的 HD 素材
只留本機，不加入此儲存庫或公開封包。下列選定的文件截圖依使用者指示收錄於私人儲存庫，
不納入自有程式授權。

HD 五語系已確定支援繁體中文、簡體中文、日文、韓文與英文；F12 原版模式保留繁中。
目前已接入 F11 遊戲中語言切換、設定保存、啟動與功能選單、新遊戲說明、預算、人口、民意、速度、固定狀態訊息及離開確認。玩家檔名與原版數值保持原樣。
開場、上任信、圖片中的可讀招牌及逐字訊息已接入五語系，已盤點的 146 筆中文來源全部有譯文。正常語言切換、原版／HD 切換、缺譯警示、英文存讀檔與退出已驗證；商標、不可辨讀的裝飾及玩家檔名保留原樣。
範圍與未驗分支見[完整來源覆蓋契約](docs/spec/033-localization-source-coverage.md)、[多語系契約](docs/spec/030-hd-localization.md)、[介面翻譯契約](docs/spec/032-interface-localization.md)與[操作說明契約](docs/spec/031-help.md)。

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

正常六入口、F11／F12、返回城市及同次存讀檔已核對；完整機器狀態、全新 EXE 冷讀與平台真機仍依[圖表契約](docs/spec/029-chart-windows.md)另驗。

</details>

來源、程式與圖片雜湊見[截圖清單](workspace/screenshots/manifest.json)。
重生入口為 [readme_screenshots.sh](workspace/tools/readme_screenshots.sh)，以[匯出工具](workspace/tools/export_readme_screenshots.py)核對後收錄，只在 Docker 內執行；
圖表使用 [chart_locale_gui.sh](workspace/tools/chart_locale_gui.sh) 擷取，經[整張畫面核對](workspace/tools/chart_locale_check.py)後[匯出](workspace/tools/export_chart_screenshots.py)。
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
