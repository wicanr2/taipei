# 剩餘地圖圖庫補齊

狀態：CONFORMED，限完整來源呈現與下列正常抽樣。對應 [#62](https://github.com/wicanr2/taipei/issues/62)，依 [#30](https://github.com/wicanr2/taipei/issues/30) 與 [026](026-infrastructure-tiles.md)、[034](034-disaster-city-buildings.md) 至 [037](037-transport-facilities.md)。沿用已確認的 B、1280×800、Noto、五語系與 F12，不重寫規則。

## 來源與覆蓋

固定原版 ROM SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`。九圖庫的實際 count 為成員34／35／36／37各96、38為180、39為75、40／41各180、59為135，共1134項。每項仍從實際offset表重讀9×9與81 bytes，末項以成員長度為終點，不能假定多一個sentinel。

已完成圖片不重做。其餘圖片按完整原始來源處理，保留所有別名與用途未知的標記；用途未知不授權猜造圖像或遊戲規則。全黑空白填充另列，不用原始筆數假充重繪進度。來源影像覆蓋、正常遊玩抽樣與未走過分支分開記錄。

## 唯讀覆蓋診斷

[map-coverage-audit](../../workspace/app/cmd/map-coverage-audit/main.go) 使用真實正常GUI城市收據作固定底圖，僅在呈現器輸入副本的一格依次放入每個完整原版來源，記錄現行來源是否辨識與實際像素是否改變。沒有執行DOS VM、注入城市或改SAV，明示 synthetic_renderer_input，不作正常玩家路徑完成證據。

命令僅在既有GUI Docker image內執行，參數 `-rom <唯讀ROM> -materials <本機素材> -receipt <正常GUI原件> -out <新的本機JSON>`。原始輸入唯讀、輸出1000:1000、有界資源及無網路。正式來源與重繪規格須達READY後才接產品；正常GUI另走代表建物／地景、F11／F12、原版存讀與退出。

## 覆蓋結果與來源匯出

`map-coverage-baseline-r1.json` SHA-256 `b2abcdad3b2810232ba5f2ae98a0db7f5c4caf9e8851b884a1c094b578448ab9`，6.913秒。1049種原始像素中，760種現行辨識，745種在單格合成條件可繪製。一種全黑來源出現於57個填充位置。核能／體育場兩種同源圖只缺合成鄰格，既有正常驗證保持完成；其餘301種非空原圖待補，包含城市複合圖、區域字樣、尚未接入的4×4圖與小格。

[map_completion_sources.py](../../workspace/tools/map_completion_sources.py) 按實際ROM與覆蓋結果匯出來源。4×4排列由既有IDA9.4原件 `ida-46/nuclear-check.json` 的 `sub_17BF8` 證實，IDA loader linear 0x17FD1–0x17FE6 原始shift／add形成 `24×row+4×arg6+col`，不以圖庫數量猜用途。新複合圖用原始編號命名，不推定成長或統計規則。

本機根為 `workspace/prototypes/hd-style/map-completion-v1/`，`complex/` 放十三張待補複合圖，`zones/` 放三張區域原圖，`misc/` 放58種小格原始bytes；`inventory.json` 保存全部別名、色盤及來源雜湊。已完成的base4三張沿034保留。六座正常保存城市的唯讀候選只用於選擇抽驗位置，不改SAV、不當GUI證據；空白填充與舊同源回退不重開為新圖片工作。

## 固定素材與審查

[map_completion_assets.py](../../workspace/tools/map_completion_assets.py) 將十三張 imagegen 整張重繪一次縮至144×144，再切4×4圖格。原圖／HD整張並排已檢查構圖、輪廓、色塊與邊框；不生成每格獨立接縫。實際208個位置有207種來源，m34-b08的下排兩格同源，沿既有唯一鄰格定位。三張區域圖48個位置有36種來源，加58種小格，共301種新來源。最初208／35的分類計數假設已由完整bytes核對修正，總數不變。

區域原字為住／商／工。只擦除原版白字，保留原邊框與沙地，執行時使用固定Noto與唯一TSV三鍵 `map.zone.residential`、`map.zone.commercial`、`map.zone.industrial`。繁／簡／日用住／商／工，韓文用주／상／공，英文用R／C／I。文字安全矩形為整張圖(44,44)到(108,100)，最大52、最小24，須驗實際墨跡。原版F12維持原DOS像素。語言或字型故障使該區域回退，不沿用上一次語言。

小格沿026的四權重平滑輪廓、原色身份與B材質，權重總和255、來源中心顏色身份保持。水面接既有water，其他未命名色保留原色明暗加細微材質；不推定道路連接、災害相位或用途。同源區域格只有所有候選HD裁切完全相同時可直接繪製，否則仍需精確可見唯一鄰格；無法定位則原版回退。

候選根 `map-completion-prototype-v1/`，正式本機根 `map-completion-ready-v1/`。三子目錄complex／zones／detail各有獨立封存manifest，sha256依次為 `559fb204323da6838a5167b93f3d711cf4f46d962d03a4c111668367b5618489`、`e2af961d4d73ea89304faf105edbbea6cb6066de326e8705997d3e62520e8fd4`、`b115c09937401d34bcd1ab65b717fef4a73e9031b7c6da68a4c0983d2b9f5cb7`。DRAFT根manifest為 `ff23fbc32902ddd0c4f1108950014ccf6c3376b1815682a046405bab9fc2d606`。正式重建須得到相同圖像／幾何／子manifest。原圖、生成圖、素材與收據留本機，禁止加入Git。

## 接入與預登記抽驗

已完成家族優先序及像素不變。新增家族接在既有城市建物之後、舊地景之前；來源須完整81 bytes、固定ROM全部別名、已用色盤、素材sha與opaque形態同時符合。單張圖損壞只影響該圖；合成輸入與覆蓋工具標記保持原樣。全黑57個填充位置辨識為同一空白來源，不宣稱重繪、不填假圖。

診斷：1049種來源完整盤點、十六張整圖裁切／所有區外、每種來源變異與已用色盤失配、共享鄰格負對照、實際manifest／圖檔／幾何刪除及損壞、五語系Noto墨跡與切換、原版畫面副本不變。合成單格缺鄰格不構成正常玩家缺陷；整圖正對照補驗共享位置。

正常GUI：從真實EXE冷啟、原版F2讀取唯讀城市副本，代表三種區域與m34-b08、m35-b12、m36-b16、m37-b08，透過正常方向鍵捲動與移開原版游標，逐byte核對完整4×4來源。驗F11五語系、F12、Shift+F1、F2存退讀與原版退出。較高階圖無現成正常城市者列未抽驗，不籌資、不注入SAV或RAM。小格隨同場景記錄實際出現者，完整表格身份不等於每種連接／災害分支已玩過。四架構編譯；Windows／macOS真機仍未驗。README於最終整合更新原版與五語系真實截圖。

實作入口 [map_completion.go](../../workspace/app/internal/hd/map_completion.go)，沿[render.go](../../workspace/app/internal/hd/render.go)既有場景閘門後呈現。區域字型未就緒保留原版，單一素材故障不阻斷其餘介面語言。測試 [map_completion_test.go](../../workspace/app/internal/hd/map_completion_test.go)；正常路徑 [map_completion_gui.sh](../../workspace/tools/map_completion_gui.sh)／[map_completion_gui.py](../../workspace/tools/map_completion_gui.py)。上述工具都在既有GUI image內執行，原版與兩份種子唯讀、輸出1000:1000、無網路、有界資源與Xvfb trap。

抽驗鏡頭依既有正常原件確認每次捲動兩格，必須與目前原點同奇偶。r2七個原點依序(32,10)、(28,20)、(44,40)、(44,44)、(12,34)、(72,60)、(60,72)，世界位置保持相同。r1奇數目標往返是腳本錯誤，原件與勘誤留WORKLOG，不算產品失敗或完整玩家驗收。

READY資產根manifest為 `be04e87136b05e09c3eb92402eea6173280687c9323fdf97cef77c2c8dd10a10`，三子manifest與候選相同。核心兩項測試10.616秒無跳過；24381種來源變異、301個已用色盤失配、十二個真實刪除／損壞及隔離、十三完整圖與全部區外、十五區域字墨與整圖通過。單格合成診斷1049種全部辨識、1045種可直接繪製；剩餘是空白與三種需要原版鄰格定位的同源來源，整圖正對照已補驗新增同源格，舊兩種沿既有正常收據保持完成。

正常獨立核對入口 [map_completion_check.py](../../workspace/tools/map_completion_check.py)，直接重讀ROM與別名、真實PNG及封存圖，不信任呈現器自報完成數。文件匯出 [export_map_screenshots.py](../../workspace/tools/export_map_screenshots.py) 只選m34-b08／m34-b00各原版與五語系，共十二張。通過原版存退讀與退出後才匯出，原始收據留本機；其他批次截圖保留各自來源版本。

收尾入口 [map_completion_final.py](../../workspace/tools/map_completion_final.py) 以 `--source-commit <實際已驗程式提交>` 核對原始35檔與RAR、四架構header、已驗與標準入口相同、136檔素材乾淨重生、84張文件PNG、來源及七補丁、文件入口與擁有權。容器清理另由主機 `docker ps -a --filter label=project=taipei` 回讀；此工具不代替正式封包驗收。

正常抽樣修訂：r3取得C1五種來源與30張PNG，但C2兩高階路由在舊／HD兩版都未達目標，原因未定，不當HD退化。依使用者代表抽驗，r4兩側正常冷啟C1，以商業區(38,24)／鏡頭(14,22)、ROM37-b08(54,24)／鏡頭(30,22)兩重複代表補完整存退讀退出。獨立工具以 `--prefix <r3原件> --run <r4完整流程> --baseline <r4原版基線>` 核對42張圖。完成範圍是五種不同正常來源與兩重複完整流程，不稱七種正常來源，也不將r3補成完成退出。高階圖的原圖身份／完整圖已驗，正常出現分支保留未抽驗。

## 完成結果

程式提交 `42639adb07abdf5f6134bdc8fb40263e1a882191` 已推送。`gui-map-r4`／`map-baseline-r4`皆正常冷啟、C1原版讀取、方向鍵、F11／F12、原版存讀與退出，wrapper0；HD另驗Help。r3五種來源與r4兩重複視圖共42張真實GUI，原版整張／B整圖／Noto字墨與背景及42項有效像素反例通過。原版、HD及讀回後MAPHD.SAV均為93567 bytes，SHA-256 `7ca351e35aa6ed8c3f5da525d88af43eab1f00add2989c0fd4b13bfe20efd55b`。

| 證據 | SHA-256 |
|---|---|
| HD完整流程主收據 | `8d1c87725053437947e2935ae3f86932f73d1bd054da4b4406302147ac3f6aab` |
| 舊版完整流程主收據 | `ea6973160c095555fa62caacdd54f9e8319803e150bef43f042b8b03a02808c7` |
| 獨立42圖核對 | `e56bd100dc050efc7df1ef3b365d8d291114173517c1d5a5c1b15f93ac1d88b4` |
| Linux amd64，標準與已驗候選相同 | `87439f2fb2b9758f3b5afb85cda7c51dd152355b9f0eae12c599688dfa7652f4` |
| Windows amd64 | `fb5f40b87b34615e75350c502568537cdb3cd0874a0f36e98d9ea1e18b88bcc5` |
| macOS amd64 | `f655423a97f0ef86be9a4bfaa04096af8540f3689623382552b2798aeb13099f` |
| macOS arm64 | `28b636471bae365b630ad5f9c1cca202dd55e5b6aaebff2d20eafe699d3bfba9` |
| README 84張manifest | `78e5b0f1873d3e51ba345102c42ca6ccdce24d8bf58d252f4361e8087f807621` |

136檔READY素材乾淨重生逐byte相同。README新增十二張真正遊玩PNG，合計84張／75,683,303 bytes；首頁更新完整地圖，舊批次保持其來源版本。只收錄明列文件截圖，原版、素材、字型、SAV與原始收據留本機。039開場／插畫／動畫仍DRAFT，完整HD母項與正式封包未完成。

收尾報告 `workspace/runs/map-completion-final.json` SHA-256 `77ac8656256286affdbbc340146823f95228ff39dcda272b6643a003a75805e1` 通過，原始35檔與RAR不變、程式及七補丁、四架構、136素材、84PNG與文件入口／擁有權均核對。指定find無root-owned或.md目錄，專案容器清單為空。C2高階路由、人耳、Windows／macOS真機、039圖片與正式封包仍未驗或未完成。
