# F4 圖表視窗

狀態：DRAFT。對應 [#48](https://github.com/wicanr2/taipei/issues/48)，母項 [#31](https://github.com/wicanr2/taipei/issues/31)。本批尚未接入正式呈現。

使用者已確認全部圖片與操作介面、B 細緻手繪材質、1280×800、Noto 與遊戲中 F12。沿用原版圖表內容、位置、數值及操作，不重寫統計規則。

## 正常來源與未知

固定原版、dosgolem 及七補丁沿用 [028](028-ending-achievement-base.md)。原版 ROM SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`，EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。定位使用 ROM 檔案偏移、從零起算的成員／字模索引及原版 320×200 像素。

- 已證實，限 [022](022-city-function-menus.md) 的下拉面板：F4 六列依序為「電力供應」「交通密度」「人口密度」「犯罪率」「房價」「污染」。確認後的畫面不屬於 022 完成範圍。
- 已證實，限既有正常收據：`workspace/runs/infrastructure-density-native/traffic-density-open-capture.zip` 在 1,128,000,000 步，模式 0x13、等待輸入，完整色號 SHA-256 `c79af4a8d00a06c2e48783ed5707be8b65ee484c165d21df14c22c5021956ac2`。畫面實際包含縮小城市地圖、兩側色帶、MIN／MAX 與框架。原圖副本在 `workspace/runs/chart-windows-native/traffic-density-native.png`。
- 未知：完整視窗矩形、各圖表資料與色盤契約、動態數值／文字、原始圖庫／字模對應、返回與刷新條件。不能因有一張交通畫面就將六圖表升 READY。

首件補充證據：ROM4–10 的 145×127 圖像在中央局部 (20,20,105,89) 以外，9,070 個色號完全相同。既有交通密度九份原子收據均符合原位 (66,35,145,127) 的完整固定框架，中央資料區只有一種實見來源。工具 [chart_window_source_check.py](../../workspace/tools/chart_window_source_check.py) 保存成員原始偏移、雜湊、完整來源與已用色盤；中央區只列原始像素，不命名統計內部規則。

正常 r1 首個電力入口的 Escape 已由 `int21-AH07` 讀到 ASCII 27、`Word=0`，並恢復原城市畫面。原工具錯等 BIOS 的 `Word=0x011b` 而逾時，收據保留 `workspace/runs/chart-windows-native-r1/`。r2 對圖表返回只核對已見 DOS 控制台讀取及 release，不改產品、操作、時間或六入口條件。六入口全部返回仍待 r2 完成。

r2 勘誤：六次開圖及返回完成，但以 022 的完整選單來源核對，實際選取為 0、1、3、0、4、3，僅涵蓋四個入口。F4 重開保留上次選取，工具錯把每次入口當作 0。r2 原件與原本記錄的意圖名稱保留，不能作六選項來源證據。r3 先以固定完整選單 SHA 辨識當前選取，再正常 Down 至目標，每一步與確認前皆核對完整選取來源；產品與原版參數不變。

嵌入框架的 MAX／MIN 為 5×5 字墨，四字串原位局部 (1,22,17,5)、(127,22,17,5)、(1,101,17,5)、(127,101,17,5)，色號 14，共 138 像素。直接重讀 ROM4–10 的完整嵌入墨跡相符，未據此宣稱來自 ROM56 或某個 EXE 繪字呼叫。

正常探索入口為 [chart_window_playtest.sh](../../workspace/tools/chart_window_playtest.sh) 與 [chart_window_playtest.py](../../workspace/tools/chart_window_playtest.py)。從真實冷啟動進入 DISA1，以原版 0 暫停，再逐一正常 F4／Down／Space 開啟六選項、兩次無輸入觀察與 Escape 返回；原版讀鍵、前端 release 及原點皆核對。原始資料唯讀，來源研究有界停止，不當作正常退出驗收。

## 升 READY 前的條件

1. 六個正常入口、完整畫面與返回有收據；每個來源保留雜湊、工具版本、定位與證據等級。
2. 固定框架、全部文字、資料區、色盤與動態範圍可完整重建；未知來源及相位仍完整回退。
3. 以已定 B／Noto 製作可撤回原型，獨立核對完整原版來源、實際字墨、字型授權與乾淨重生，再逐已確認批次升 READY。
4. 實作後另外驗 F12、有效負對照、真正資源故障、正常存退讀與相同步數原版狀態、四架構及清理；靜態原型不代替玩家路徑。

原版、字型、衍生圖像與收據只留本機，不能因 private 儲存庫而散布。文件入口由 [CONTEXT](../../CONTEXT.md) 索引。
