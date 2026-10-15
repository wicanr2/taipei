# 模擬台北：dosgolem 與 HD 呈現

以 dosgolem 執行原版《模擬台北》，保留城市經營玩法，加入 1280×800 的 HD 呈現、Noto 高清黑體與五語系介面。

本機交付版本：`v.1.0.1-20261015`。三平台完整版均含遊戲與 HD 素材，完整解壓後即可遊玩。

本儲存庫保存原創程式與建置工具。本機完整版使用使用者提供的原版資料；原版執行檔、資料、美術、音訊與權利未明的 HD 素材
只留本機，不加入此儲存庫或公開封包。下列選定的文件截圖依使用者指示收錄於私人儲存庫，
不納入自有程式授權。

## 遊戲背景

《模擬台北》是一款以臺灣城市治理為題材的 DOS 城市建設與經營遊戲。
公開典藏資料將它列為 1992 年作品，由聯邦開發、資策科技代理，
見[奧米加典藏條目](https://www.omega.idv.tw/kdb120/viewthread.php?threadid=5296)與[中文模擬類遊戲目錄](https://chiuinan.github.io/game/game/cgame33.htm)。

玩家扮演市長，鋪設道路與電線，建設電廠和公共設施，再透過預算、民意與城市圖表處理交通、住房、治安和污染問題。
除了建設新城市，也能接手「災難台北」等既有城市情境。原版說明設定的目標，是將新城市發展或將災難城市恢復為人口超過五十萬的都會區。
玩法與目標可回查[原版說明來源](docs/spec/017-new-game-dialog.md)及[已核對的介面文字](workspace/app/locales/ui.tsv)。

![HD 繁體中文的台北城市實際畫面](workspace/screenshots/city-map-buildings-zh-Hant.png)

上圖為 Linux 前端正常讀取原版台北城市存檔的實際畫面，尺寸為 1280×800。
九個地圖圖庫的非空原圖已接入 HD，包含其餘建物、道路地景及 Noto 區域標示。
五種代表來源、五語系切換與 C1 原版存讀退出已抽驗；完整來源表與未抽驗分支見[地圖契約](docs/spec/038-map-completion.md)，每張圖片的版本與原始收據見[截圖清單](workspace/screenshots/manifest.json)。

<details>
<summary>目前地圖：原版、HD 建物與五語系區域標示</summary>

區域原字「住、商、工」改用 Noto；韓文為주／상／공，英文為R／C／I。F12仍顯示原版繁中。
以下圖片來自正常遊玩的完整來源前段，原版存讀與退出另由 C1 冷啟流程驗證。高階發展與災害分支沒有逐項試玩。

| 模式／語言 | 建物 | 區域標示 |
|---|---|---|
| 原版繁體中文 | ![原版台北建物](workspace/screenshots/city-map-buildings-original.png) | ![原版區域標示](workspace/screenshots/city-map-zones-original.png) |
| HD 繁體中文 | ![HD 繁中台北建物](workspace/screenshots/city-map-buildings-zh-Hant.png) | ![HD 繁中區域標示](workspace/screenshots/city-map-zones-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡中台北建物](workspace/screenshots/city-map-buildings-zh-Hans.png) | ![HD 簡中區域標示](workspace/screenshots/city-map-zones-zh-Hans.png) |
| HD 日文 | ![HD 日文台北建物](workspace/screenshots/city-map-buildings-ja.png) | ![HD 日文區域標示](workspace/screenshots/city-map-zones-ja.png) |
| HD 韓文 | ![HD 韓文台北建物](workspace/screenshots/city-map-buildings-ko.png) | ![HD 韓文區域標示](workspace/screenshots/city-map-zones-ko.png) |
| HD 英文 | ![HD 英文台北建物](workspace/screenshots/city-map-buildings-en.png) | ![HD 英文區域標示](workspace/screenshots/city-map-zones-en.png) |

</details>

<details>
<summary>開場插畫：原版與 HD 五語系</summary>

門樓、百貨、人物、街景與動畫沿原版來源覆繪，字型使用 Noto。以下皆為正常冷啟動後的實際畫面，見[插畫契約](docs/spec/039-illustration-animation.md)。銀行背景相同，角色仍隨原版時間移動，五張語言照片不宣稱同狀態。

| 模式／語言 | 銀行場景 |
|---|---|
| 原版繁體中文 | ![原版銀行插畫](workspace/screenshots/illustration-bank-original.png) |
| HD 繁體中文 | ![HD 繁中銀行插畫](workspace/screenshots/illustration-bank-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡中銀行插畫](workspace/screenshots/illustration-bank-zh-Hans.png) |
| HD 日文 | ![HD 日文銀行插畫](workspace/screenshots/illustration-bank-ja.png) |
| HD 韓文 | ![HD 韓文銀行插畫](workspace/screenshots/illustration-bank-ko.png) |
| HD 英文 | ![HD 英文銀行插畫](workspace/screenshots/illustration-bank-en.png) |

| HD 開場門樓 | HD 交通插畫 |
|---|---|
| ![HD 開場門樓與標題](workspace/screenshots/illustration-title-zh-Hant.png) | ![HD 交通與車輛插畫](workspace/screenshots/illustration-traffic-zh-Hant.png) |

</details>

<details>
<summary>災難台北建物：原版與 HD 五語系對照</summary>

以下保留首批建物驗收版本的實際畫面，透過 F11／F12 切換後擷取。最新地圖見上方。
首批三種建物共 48 個圖塊，包含完整及部分可見建物；範圍見[建物契約](docs/spec/034-disaster-city-buildings.md)。

| 模式／語言 | 實際畫面 |
|---|---|
| 原版繁體中文 | ![原版災難台北城市畫面](workspace/screenshots/city-disaster-original.png) |
| HD 繁體中文 | ![首批 HD 繁中災難台北建物](workspace/screenshots/city-disaster-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文災難台北建物](workspace/screenshots/city-disaster-zh-Hans.png) |
| HD 日文 | ![HD 日文災難台北建物](workspace/screenshots/city-disaster-ja.png) |
| HD 韓文 | ![HD 韓文災難台北建物](workspace/screenshots/city-disaster-ko.png) |
| HD 英文 | ![HD 英文災難台北建物](workspace/screenshots/city-disaster-en.png) |

</details>

## 目前可玩範圍

原版冷啟動、新遊戲、電線施工、存檔、退出及全新啟動讀檔已通過正常操作驗證，音訊已接入實際播放器。
F4 六圖表已依正常遊玩抽驗通過，包含開啟、F12 切換、返回城市、電力圖五語系切換，以及同次存讀檔與退出，範圍見[圖表契約](docs/spec/029-chart-windows.md)。

| 功能 | 已接入內容 |
|---|---|
| HD 圖像 | B 細緻手繪材質的完整九圖庫非空來源，涵蓋地景、道路電線、城市建物、電廠、港口機場與公共設施；另有城市框架、工具選單、預算與圖表外框、政績底圖，以及開場門樓、插畫、人物／車輛及動畫相位 |
| HD 文字 | Noto 高清黑體，包含啟動選單、城市功能、工具、視窗、預算、狀態列、圖表及住／商／工區域標示 |
| 五語系 | 繁體中文、簡體中文、日文、韓文、英文；已盤點的 146 筆中文來源皆有譯文，涵蓋開場、上任信、介面、圖片可讀文字及逐字訊息 |
| 遊戲中切換 | F11 選語言並保存設定；F12 切原版繁中／HD；Shift+F1 顯示五語系操作說明 |

原版程式繼續負責模擬規則、亂數與存檔，HD 層改變呈現。玩家檔名、原版數值與商標保留原樣。
重繪目標包含所有圖片與操作介面；完整來源已分類並接入，開場與動畫按正常代表抽驗通過；未逐項走過所有事件／結局分支。Windows、Linux、macOS 本機封包已完成；Linux與Windows Wine已驗實際啟動，macOS保留真機未驗限制。
目前證據與限制以 [CONTEXT.md](CONTEXT.md) 及[驗收矩陣](docs/verification-matrix.md)為準；翻譯範圍見[完整來源覆蓋契約](docs/spec/033-localization-source-coverage.md)。

<details>
<summary>警察局與消防局：正常施工與五語系對照</summary>

由新遊戲進入城市，以原版工具子選單建設警察局與消防局，再以 F11／F12 切換擷取。
兩種完整施工圖共 32 格；正常施工、同次存讀檔與原版退出已通過遊玩抽驗，範圍見[警消設施契約](docs/spec/035-civic-facilities.md)。

| 模式／語言 | 實際畫面 |
|---|---|
| 原版繁體中文 | ![原版警察局與消防局施工](workspace/screenshots/city-civic-original.png) |
| HD 繁體中文 | ![HD 繁體中文警察局與消防局](workspace/screenshots/city-civic-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文警察局與消防局](workspace/screenshots/city-civic-zh-Hans.png) |
| HD 日文 | ![HD 日文警察局與消防局](workspace/screenshots/city-civic-ja.png) |
| HD 韓文 | ![HD 韓文警察局與消防局](workspace/screenshots/city-civic-ko.png) |
| HD 英文 | ![HD 英文警察局與消防局](workspace/screenshots/city-civic-en.png) |

</details>

## 操作

| 按鍵 | 功能 |
|---|---|
| Shift+F1 | 開啟或關閉操作說明；原版 F1 仍是離開 |
| Esc | 關閉目前的說明或語言面板 |
| F11 | 遊戲中切換語言並保存選擇；Help 中選完返回說明 |
| F12 | 切換原版繁中／HD 呈現 |

<details>
<summary>垃圾場與污水處理廠：正常施工與五語系對照</summary>

從原版新遊戲與工具子選單施工，各含 16 格 HD 圖。正常施工、F11／F12、同次存讀檔與原版退出已通過遊玩抽驗，範圍見[設施契約](docs/spec/036-public-facilities.md)。同一批另完成十項公共設施，各含 36 格。

| 垃圾場 | 原版繁體中文 | HD 繁體中文 |
|---|---|---|
| 正常施工 | ![原版垃圾場施工](workspace/screenshots/city-waste-original.png) | ![HD 垃圾場施工](workspace/screenshots/city-waste-zh-Hant.png) |

| 污水處理廠模式／語言 | 實際畫面 |
|---|---|
| 原版繁體中文 | ![原版污水處理廠施工](workspace/screenshots/city-sewage-original.png) |
| HD 繁體中文 | ![HD 繁體中文污水處理廠](workspace/screenshots/city-sewage-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文污水處理廠](workspace/screenshots/city-sewage-zh-Hans.png) |
| HD 日文 | ![HD 日文污水處理廠](workspace/screenshots/city-sewage-ja.png) |
| HD 韓文 | ![HD 韓文污水處理廠](workspace/screenshots/city-sewage-ko.png) |
| HD 英文 | ![HD 英文污水處理廠](workspace/screenshots/city-sewage-en.png) |

</details>

<details>
<summary>公共設施：體育場原版與 HD 五語系對照</summary>

十項公共設施已取得完整正常施工來源並重繪，與兩項環境設施合計 392 格。以下從新遊戲建設體育場，再以 F11／F12 切換擷取；完整原圖、同源圖塊辨識、存讀檔及原版退出已通過抽驗，見[十二項設施契約](docs/spec/036-public-facilities.md)。其他動畫相位與正式封包另驗。

| 模式／語言 | 實際畫面 |
|---|---|
| 原版繁體中文 | ![原版體育場施工](workspace/screenshots/city-stadium-original.png) |
| HD 繁體中文 | ![HD 繁體中文體育場](workspace/screenshots/city-stadium-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文體育場](workspace/screenshots/city-stadium-zh-Hans.png) |
| HD 日文 | ![HD 日文體育場](workspace/screenshots/city-stadium-ja.png) |
| HD 韓文 | ![HD 韓文體育場](workspace/screenshots/city-stadium-ko.png) |
| HD 英文 | ![HD 英文體育場](workspace/screenshots/city-stadium-en.png) |

</details>

## 原版與 HD 五語系畫面

<details>
<summary>機場與港口：原版與 HD 五語系對照</summary>

由全新 EXE 正常冷讀 `DISA4.DSA` 的原版城市存檔，經原版鍵盤捲動至完整機場與港口，再切換擷取。兩項合計 72 格，五語系、F12、原版存讀與正常退出已通過遊玩抽驗，見[運輸設施契約](docs/spec/037-transport-facilities.md)。本次 HD 流程採既有設施，新建機場與其他動畫相位未抽測。

| 模式／語言 | 機場 | 港口 |
|---|---|---|
| 原版繁體中文 | ![原版既有機場](workspace/screenshots/city-airport-original.png) | ![原版既有港口](workspace/screenshots/city-port-original.png) |
| HD 繁體中文 | ![HD 繁體中文機場](workspace/screenshots/city-airport-zh-Hant.png) | ![HD 繁體中文港口](workspace/screenshots/city-port-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文機場](workspace/screenshots/city-airport-zh-Hans.png) | ![HD 簡體中文港口](workspace/screenshots/city-port-zh-Hans.png) |
| HD 日文 | ![HD 日文機場](workspace/screenshots/city-airport-ja.png) | ![HD 日文港口](workspace/screenshots/city-port-ja.png) |
| HD 韓文 | ![HD 韓文機場](workspace/screenshots/city-airport-ko.png) | ![HD 韓文港口](workspace/screenshots/city-port-ko.png) |
| HD 英文 | ![HD 英文機場](workspace/screenshots/city-airport-en.png) | ![HD 英文港口](workspace/screenshots/city-port-en.png) |

</details>

<details>
<summary>核能電廠：原版與 HD 五語系對照</summary>

由全新 EXE 冷讀原版台北城市，經正常鍵盤捲動至既有核能電廠，再以 F11／F12 切換擷取。完整 36 格、同源圖塊、五語系、存讀檔與原版退出已通過遊玩抽驗，見[發電廠契約](docs/spec/027-power-facility.md)。新建核電廠與其他動畫相位未抽測。

| 模式／語言 | 實際畫面 |
|---|---|
| 原版繁體中文 | ![原版既有核能電廠](workspace/screenshots/city-nuclear-original.png) |
| HD 繁體中文 | ![HD 繁體中文核能電廠](workspace/screenshots/city-nuclear-zh-Hant.png) |
| HD 簡體中文 | ![HD 簡體中文核能電廠](workspace/screenshots/city-nuclear-zh-Hans.png) |
| HD 日文 | ![HD 日文核能電廠](workspace/screenshots/city-nuclear-ja.png) |
| HD 韓文 | ![HD 韓文核能電廠](workspace/screenshots/city-nuclear-ko.png) |
| HD 英文 | ![HD 英文核能電廠](workspace/screenshots/city-nuclear-en.png) |

</details>

以下為 Linux 前端從正常新遊戲入口擷取的實際畫面。城市以原版 `0` 鍵暫停，再以 F11／F12 切換。
城市與預算各組的原版色號畫面及可見顏色一致；原版為 320×200 的四倍最近鄰放大，HD 為 1280×800。
點圖片可看完整尺寸。以下保留各批驗收版本，圖片來源清單載明實際程式；未逐項試玩所有事件與結局。封包驗證範圍見下方。

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
災難台北建物畫面使用[正常 GUI 入口](workspace/tools/disaster_building_gui.sh)重生，由[匯出工具](workspace/tools/export_building_screenshots.py)核對後收錄，包含原版與 HD 五語系。
警消設施畫面使用[正常施工入口](workspace/tools/civic_facility_playtest.sh)的 `gui` 模式，經[設施像素與語言核對](workspace/tools/civic_facility_check.py)後[匯出](workspace/tools/export_civic_screenshots.py)。
環境與公共設施使用[批次玩家入口](workspace/tools/facility_batch_playtest.sh)的 `hd` 模式；整批以 `--scope public` 執行[獨立像素核對](workspace/tools/public_facility_check.py)與[匯出](workspace/tools/export_public_screenshots.py)。各批原始擷取與工具版本保存在來源清單。
核能電廠使用[既有城市正常入口](workspace/tools/nuclear_existing_playtest.sh)的 `hd` 階段，經[全圖與語言核對](workspace/tools/nuclear_check.py)後[匯出](workspace/tools/export_nuclear_screenshots.py)。
港口與機場使用[正常冷讀入口](workspace/tools/transport_facility_playtest.sh)的 `hd` 階段，像素核對與匯出工具使用 `--scope transport`，逐項保留原版與五語系六張畫面。
原始收據保存在本機工作區，未加入儲存庫。驗證界線見[驗收矩陣](docs/verification-matrix.md)。

## 本機封包與執行

版本 `v.1.0.1-20261015`，位於專案的 `dist-all/v.1.0.1-20261015/full-local/`。
每包含 23 個原版遊戲檔、586 個執行期素材及程式／授權等文件，共 629 檔。包含 `RS201.EXE`、兩份 ROM、DT0–9 與 DSA1–6，不需要另行匯入遊戲。完整包只留本機。

| 平台／架構 | 封包 | 解壓後入口 |
|---|---|---|
| Linux amd64 | `Taipei-v.1.0.1-20261015-linux-amd64-full-local.tar.gz` | `start.sh` |
| Windows amd64 | `Taipei-v.1.0.1-20261015-windows-amd64-full-local.zip` | `Start.cmd` |
| macOS amd64／arm64 | `Taipei-v.1.0.1-20261015-macos-universal-full-local.zip` | `start.command` |

請完整解壓後啟動，預設開啟 HD。`original/`、`materials/`、`locales/`須保留在程式旁。
版本可用啟動器的 `-version` 查詢。Linux需要X11、ALSA及執行期系統函式庫，建置與測試環境為Debian 12。

| 平台 | 存檔與語言設定位置 |
|---|---|
| Linux | `${XDG_DATA_HOME:-$HOME/.local/share}/taipei-dosgolem/saves/` |
| Windows | `%LOCALAPPDATA%\TaipeiDosgolem\saves\` |
| macOS | `$HOME/Library/Application Support/Taipei dosgolem/saves/` |

三包的逐檔內容、必要素材與字型皆已核對。Linux與Windows Wine使用實際封包，驗B開場、F11／F12／Help、設定寫入及缺資料錯誤。Linux原版／HD各20秒錄音沒有新增缺料補零，約58秒遊戲開場錄音與影片音軌通過非靜音、無削波及無半秒以上長靜音檢查。
Windows Wine不等同Windows真機。macOS已驗universal兩個slice、內容、系統依賴及啟動器結構，原生執行與使用者目錄寫入未驗；封包未簽章或公證。
本版正常新遊戲、F11／F12、存讀檔與DOS退出通過，原版存檔與前版相同；範圍見[音訊與呈現修正](docs/spec/042-presentation-audio-continuity.md)。技術錄音不等於人耳確認或完整通關。

各包SHA-256與驗收索引在本機 `dist-all/v.1.0.1-20261015/SHA256SUMS.json`。封裝方式沿[三平台契約](docs/spec/040-local-platform-packages.md)，新版驗證見[042](docs/spec/042-presentation-audio-continuity.md)。

## 本機推廣影片

`dist-all/v.1.0.1-20261015/promo/Taipei-v.1.0.1-20261015-promo.mp4`，76 秒、1280×800、H.264／AAC。

影片包含實際城市操作、F12 原版／HD 切換，以及 F11 繁中、簡中、日文、韓文與英文切換。導航與選單等待經剪輯，配樂取自同一正式封包的開場錄音。影片、預覽圖、原版配樂 WAV、來源與雜湊只留本機，詳細範圍見[影片契約](docs/spec/041-local-promo.md)。

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
