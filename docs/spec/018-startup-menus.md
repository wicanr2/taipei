# 主選單、城市選擇與難度選擇

狀態：**CONFORMED**，限研究前端的三種啟動選單與十三個選取狀態。對應 [#31](https://github.com/wicanr2/taipei/issues/31)，沿用 [015](015-full-hd-scope.md) 的完整 HD 範圍。2026-10-11 完成來源及離線審查，先升 READY 再接入；目前已通過下列正常操作及同狀態驗證。

## 已取得來源

固定 ROM、dosgolem 與工具鏈沿用 [008](../re/008-full-asset-inventory.md)、[017](017-new-game-dialog.md)。位址均為 ROM 檔案偏移，成員索引從零開始。

| 畫面 | ROM 成員與偏移 | 原版矩形 | 目前證據 |
|---|---|---|---|
| 主選單 | 20，166964 | `(16,15,288,175)` | 三個選項的正常 GUI 畫面；底圖差異僅是按鈕文字 |
| 城市選擇 | 21，173282 | `(18,37,236,132)` | 七個選項的正常 GUI 畫面；選取字為白色，其他字為紅色 |
| 難度選擇 | 17，141866 | `(18,37,236,132)` | 三個選項的正常 GUI 畫面；標題在底圖，選項文字另繪 |

已證實：城市選擇的左右鍵不改選取，上下鍵依原版順序移動；難度選擇的 Escape 不改畫面。保留原版控制，不自行新增返回語意。正常收據由 [startup_menu_playtest.sh](../../workspace/tools/startup_menu_playtest.sh) 冷啟動取得，不載入快照。

## 呈現契約

- 完整原版矩形色號、實際使用中色盤及固定素材相符，才覆繪該選取狀態。三種選單共十三個完整狀態，未知或失配時整個選單保留原版。
- B 木紋底板、紅色及藍色按鈕由內建 imagegen 生成，素材保留本機。按鈕矩形從原版底圖量出，按鈕位置與操作範圍維持原樣。
- 藍底銀框沿用已審查的 017 素材，分割邊角以維持固定框線厚度。背景與按鈕先依精確矩形組合，再以固定 Noto 繪原文。
- 操作字逐字沿原版位置繪製，56 px；每字與實際墨跡都須落在按鈕內縮安全矩形。主選單原版圖像標題的四字，Noto 先以大字級繪製再映射至原版每字墨跡矩形，保留各字原來的大小與構圖。
- 原文與來源資料僅存本機。離線工具輸出固定面板與 manifest，執行時須驗 manifest、每張面板、固定字型及授權雜湊，不接受只驗路徑的圖片。
- 每幀先重建原版。此批只覆繪匹配選單矩形，區外保持原版；不改原始畫面、規則、輸入或存檔。F12 往返與關閉清除均須驗證。

## 證據審查與固定輸入

已證實：正常 GUI 取得三種主選單、七種城市、三種難度狀態。底圖外加原版選項字模的完整墨跡全部相符，43 個操作字均逐點核對；30 個單點來源負對照被拒絕。主選單選取字為紅色，城市及難度選取字為白色。

離線工具 [startup-panel-prototype](../../workspace/app/cmd/startup-panel-prototype/main.go) 依原版矩形生成十三張面板，逐字檢查 Noto 缺字、實際墨跡、64×64 字格及按鈕內縮 8 px 安全範圍。人工審查三張完整面板的原文、選取色、框線與木紋，未變更構圖與操作。主標題四字依原版墨跡矩形縮放，與其他操作字固定 56 px 分開記錄。

| 本機輸入 | SHA-256 |
|---|---|
| `startup-menu-layout-v1.json` | `55d977d8da010783bb5a1e0836e6597458dba33a069f83163f0693ff6de264ee` |
| `startup-menu-sources-v1.json` | `cbe20400432e71d7ed21bba29d2fb2ae8c5d118d24842b8f2ed98d9c867f3ab6` |
| `startup-menus-v1/manifest.json` | `daeb0a0b440bce18b792cae3b89bcacc98b78e19ae05ab5a7e19f86c6cc3384d` |
| `menu-wood-b-v2.png` | `7622ec92b2b8d3dc2f56c7d0bdca489f61aca788617d92ecccceeb41de3ff8f7` |
| `menu-red-b-v1.png` | `e01cc0cfc4f5dc064ba0fadd7b7eff7ee35967451bcc1d38313b961e986c432e` |
| `menu-blue-b-v1.png` | `eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9` |

以上都位於 `workspace/prototypes/hd-style/`。生成提示與正規化紀錄為 `startup-menu-generation.json`；原圖、原文、manifest 與面板不入 Git。工具鏈與字型雜湊沿用 017。

執行時載入完整 manifest，型別包含場景、選取值、原版矩形、來源雜湊、使用中色盤索引及雜湊、面板檔名與雜湊。只有上述固定 manifest、字型及授權通過才能識別。每張面板另驗完整 PNG 與四倍尺寸；該張缺失時整個原版矩形回退，不影響其他已驗面板。未知來源不匹配，色盤失配不覆繪。此層不匯入 DOS 執行器，也不寫入原始資料或存檔。

## 預登記驗證

- 從固定 ROM 重算底圖與正常畫面差異，逐選項核對原文、來源、反白與選取順序。完整十三狀態及有效單像素負對照。
- 離線實際 Noto 墨跡、最長五字選項、字型缺字與安全矩形，人工核對全部標題、城市及難度文字。
- 正常 GUI 冷啟動，主選單三狀態、城市七狀態、難度三狀態、無效方向鍵、Escape 及 F12。原版不支援的取消保持原樣，不以工具注入返回。
- 固定參考逐像素比對完整面板與區外；來源、色盤、manifest、素材、文字、字型或授權失配完整回退。
- 同輸入與虛擬步數的完整原版狀態比較；接續施工、存退讀及退出，實際封裝收據不得把面板區域列為免驗。
- 三平台重編譯，真機與正式封包另驗。此批完成不關閉 #31 或完整 HD 母項。

## 已驗證結果與重跑入口

- [正常 GUI 工具](../../workspace/tools/startup_menu_playtest.sh) 以 `TAIPEI_THEME=hd-b` 執行，真實冷啟動並走完十三種選取、三種選單的 F12 往返、無效方向鍵、難度 Escape 與進入城市。40 份原子收據位於 `workspace/runs/startup-menus/`；開工前原版來源保存在 `workspace/runs/startup-menus-native/`。此探索工具最後採有界停止，不冒稱原版退出。
- [面板核對器](../../workspace/tools/hd_panels_check.py) 重算完整來源、使用中色盤及選取值，核對固定面板與全部區外像素。`receipt-check -panel-manifest` 獨立解碼與核對同一批收據。字形、框線、區外、來源、色盤及選取資料六種竄改，在更新受影響雜湊後仍被拒絕，輸出為 `workspace/runs/panels-negative/result.json`。
- [實際資源測試](../../workspace/app/internal/hd/panels_test.go) 驗全部十三種來源、完整區外、來源／色盤／模式失配、切換清除、manifest／面板／字型／授權缺失及損壞，單張素材失配不影響其他已驗面板。離線工具另掃描 240 個實際字形墨跡，全部落在已核對安全矩形；再次生成的全部 PNG 與 manifest 雜湊不變。
- [原版玩家路徑](../../workspace/tools/gui_playtest.sh) 再走施工、存檔、原版退出、全新 EXE 讀檔及再次退出。37 份收據的完整面板、六標題、十四圖示及區外核對通過。施工格冷讀相同，存檔 SHA-256 保持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。
- `presentation-audit -require-panels -require-dialog -require-font -require-icons` 重播正常 GUI 最後的 `city-scroll-down-capture.zip`，兩側各 1,776,000,000 步。完整原版狀態相同，包含全部十三種選單、2,165 幀選單、55 幀說明與 176 幀城市覆繪；狀態 SHA-256 `2aaad1136e232faa521d778894871e5ae3c31199c582ed12455cb550ade0bacb`。收據雜湊及執行檔、來源雜湊保存於 `workspace/runs/panels-state-provenance.txt`，結果為 `panels-state-audit.json`。
- Linux amd64、Windows amd64、macOS amd64／arm64 研究前端重編譯完成。原始 35 檔及 RAR 雜湊不變，素材仍只留本機。

本批只驗證選單呈現與已列正常路徑，未逐一驗七座城市開局、災難分支、其他選單、動態數值、圖表或平台真機。完整 HD 與正式封包尚未完成。
