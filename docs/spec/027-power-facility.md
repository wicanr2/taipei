# 發電廠圖塊

狀態：READY，限火力電廠已見完整來源的 36 格靜態呈現。核能電廠、其他相位維持 DRAFT。對應 [#46](https://github.com/wicanr2/taipei/issues/46)，依 [#30](https://github.com/wicanr2/taipei/issues/30)、[021](021-tool-submenus.md) 及 [026](026-infrastructure-tiles.md)。尚未宣稱正式 GUI／存退讀完成。

沿用 B、1280×800、Noto、F12 及原版構圖。原版 EXE 管理火力／核能電廠選項、費用、建造、供電、發展、動畫與 SAV；本批只重繪已證實來源，不重寫規則。

| 輸入與工具 | 固定內容 |
|---|---|
| RS201.EXE | SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |
| RS201.ROM | SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29` |
| dosgolem | 基底 `a9714ebdab2ad6b529f81225472680f2b11f2842` 與現行七補丁；不改上游工作樹 |
| 正常 GUI | Linux 已驗前端 SHA-256 `3f3953d6b4db3abd9aeededcbcf128706c75ccc1600d5b366e74126db58adf25`；400000 steps/update，原版主題，沒有快照或城市注入 |
| Docker | image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`，UID/GID 1000、3 GiB、2 CPU、128 PID、無網路；原版唯讀 |

已證實的入口是 021 工具 11、完整矩形 (196,124,69,35) 的「火力電廠／核能電廠」兩個選取。正常方向鍵與 Space 操作逐鍵等原版讀取及前端 release；每次由完整已知選單來源核對選項。

研究入口為 [power_facility_playtest.sh](../../workspace/tools/power_facility_playtest.sh) 與 [power_facility_playtest.py](../../workspace/tools/power_facility_playtest.py)。預登記兩種正常施工、游標移開、固定原點，分開已知及未知變更格；完整來源從唯讀 ROM 九圖庫重讀，保留所有別名及原始檔案偏移。`TAIPEI_POWER_FACILITY_CASE=thermal` 或 `nuclear` 各走一次全新 EXE，輸出 `workspace/runs/power-facility-thermal-native/` 或 `power-facility-nuclear-native/`；有界研究停止不代替正常存退讀或原版退出。

首件 `power-facility-native/` 正常火力施工形成可見 6×6 圖塊，24 次 Right 在原版大游標下使原點由 (12,12) 到 (14,12)，因此固定原點斷言停止。原件保留，不列產品缺陷。窄補查改在已見完整陸地 (22..27,3..8) 施工，每次獨立冷啟動，不改遊戲邊界、速度或時間。原件最後施工前及移開游標後兩份原點均為 (14,12)，允許另核對這一部分的原始來源；部分核對明示 prefix，不作完整兩選項或正式 HD 證據。

核能首件 `power-facility-nuclear-native/` 按鍵完成但施工未形成建物。直接依原版 ROM 字形重建底欄，火力成本為 50000 萬、核能 100000 萬，新城市資金 80000 萬；核能資金不足。這是原版正常拒絕，不改產品或注入資金。後續由 [power_funding_playtest.sh](../../workspace/tools/power_funding_playtest.sh) 及 [power_funding_playtest.py](../../workspace/tools/power_funding_playtest.py) 正常運行 DISA1。r2 的 120 次觀察見資金 77413→53221，沒有成功籌資。r3 逐鍵保存過慢而停止；r4 短促按放未完整進入前端，保留原件。r5 以明示按下／放開各 0.2 秒、每八鍵停止並核對原版 Word／讀取與前端放鍵，再重建每列完整預算來源。這次實見稅率限制為 30、四項支出 0，第一年度後 93775；不改遊戲速度、時間或資料。最多 240 次、每次至少 24000000 步觀察，取得至少 120000 萬才正常保存 0001.SAV 及退出，供全新 EXE 冷讀施工。核能維持未完成。

## 火力 36 格 READY 契約

2026-10-12 審查：`workspace/runs/power-facility-native/source-check-thermal-prefix.json` 的同原點施工前後來源已證實 6×6、原位 (203,61,54,54)。完整來源 SHA-256 `791fbfe53259ca39fe6dbd91ba4e2fa36009b7bc43d61e31b3d498b816dca558`。每格均有唯一別名，限 ROM 零基成員 38，索引 `12 + 30×row + col`，row／col 為 0..5。原始 member／image、成員偏移、檔案偏移、像素偏移、81 bytes 雜湊與已用色盤均保留於來源核對及素材 manifest。這是已證實的畫面來源，不用圖庫排列推導未見建物或相位。

B 候選 v3 在實際 216×216 尺寸與原版並列目視核對，保留 15 棵樹、三座斜向廠房、五個紅黃色形狀、淡色直條、路徑及底部綠帶。只細化表面與輪廓，沒有新增附屬建物。v1 構圖偏移候選保留，不採用；幾何材質原型 v1 亦不接正式路徑。

| 審查輸入／結果 | SHA-256 |
|---|---|
| 完整生成候選 `thermal-illustration-b-candidate-v3-generated.png`，1254×1254 | `16642276a2ba54203e2b745525e65ba92106698fc9ac9b1151720f621211aa2c` |
| `power-facility-v2/manifest.json` | `d1d887b33ce64737a4f7939880316317bd2a2547837c5c0b1c10beff48b4ee7a` |
| 216×216 完整高清 RGBA 像素 | `ca1cf32361109c05298ea7f76b81a28c1031e4b2230687a325fbb9fa0807bc4b` |

離線工具 [power_facility_prototype.py](../../workspace/tools/power_facility_prototype.py) 依 ImageMagick 6.9.11-60 Lanczos 將完整候選一次縮至 216×216，再切成 36 個 36×36 格。PNG 由 Python 3.11.2／zlib 1.2.13 固定輸出；不用逐格縮放造成接縫。完整提示詞在候選同目錄 `.prompt.txt`，素材只留本機。獨立 [power_facility_prototype_check.py](../../workspace/tools/power_facility_prototype_check.py) 重讀九圖庫與收據，36 格完整重組等於全圖、原版像素及比較圖相等，2,916 項逐像素失配均拒絕；結果 `power-facility-native/prototype-check-v2.json`。

正式 typed input 僅為原版 64000 色號、色盤、mode、HD 旗標與已驗鏡頭原點。維持既有城市場景、完整選單／預算／檔案視窗與阻塞回退閘門。通過城市閘門後，每格 81 bytes 精確識別，從完整固定 atlas 擷取對應 36×36 格，覆於原版格的四倍矩形；不讀寫 DOS 記憶體、規則、費用、供電、時間、亂數或 SAV。

- 只有 36 個已見完整來源可覆繪，部分視窗以各完整來源格辨識，不依鄰格猜補。游標、未知、損壞來源與未確認動畫相位顯示原版。
- 固定 ROM、atlas／manifest bytes、216×216 形態與不透明 alpha 均須符合。素材或 manifest 失配時，所有已知電廠格維持原版，不落入其他家族。
- 已用色盤逐格符合才呈現；未用色盤變化不誤拒絕。既有城市地形色盤閘門仍在上層生效。
- 每格只寫其 36×36 區域。完整 6×6 重組、部分可見、F12、移開游標及重讀均重新從目前原版來源呈現，不保留覆繪殘影。
- 回報 matched／painted／fallback、image 次數與拒絕原因，統計由獨立核對器對原始資料重算。

正常火力來源窄補查 `power-facility-thermal-native/source-check.json` 已核對 40 個原版讀鍵、固定原點 (12,12) 與完整 36 格，複合來源與部分來源相同。GUI r1 已實際覆繪 36 格、資金 29980。原版大游標 (149,61,54,54) 會隨虛擬時間閃爍；r1 切換期間 212 個變動像素全部位於此矩形，廠區未變且 DOS 鍵盤未新增。因此 r2 先以無輸入觀察原版游標相位，再核對完整游標外及 F12 鍵盤隔離；全機器狀態由固定虛擬時間重播驗證，不要求不同虛擬時間的游標相位相同。未改產品、原版時鐘或遊戲速度。

核能 r5 完整 489 個預算方向鍵與 240 次正常觀察結束，最後年 115 月 8、資金 98212，收入依次實見 16362／4437；未達成本或門檻，沒有保存成功聲明。保留原件，不以此外推財政規則或繼續相同探針。

正式驗收預登記：正常新城市先建一格電線，再經工具 11 的火力選項施工；游標移開，核對原版資金 29980、完整 36 格、F12 不送 DOS 鍵，兩軸各正常捲動兩格及同世界圖塊；正常 F2 存檔、兩次原版退出、全新 EXE 冷讀後恢復電線與火力原始圖塊及資金。另驗 2,916 個來源反例、逐已用色、未用色、真實素材缺失／損壞、完整區外及有效收據負對照。正式狀態重播由這條正常 GUI 的唯一輸入產生後另登記固定步數及 24000000 步抽樣，原版狀態與實際 SAV 須相同。

本節 READY 只授權這一靜態來源呈現，不把核能、完整動畫、其他建物、全部 HD、真機或封包列完成；其未知不由程式猜補。
