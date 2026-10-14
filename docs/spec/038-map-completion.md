# 剩餘地圖圖庫補齊

狀態：READY。對應 [#62](https://github.com/wicanr2/taipei/issues/62)，依 [#30](https://github.com/wicanr2/taipei/issues/30) 與 [026](026-infrastructure-tiles.md)、[034](034-disaster-city-buildings.md) 至 [037](037-transport-facilities.md)。沿用已確認的 B、1280×800、Noto、五語系與 F12，不重寫規則。

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

READY資產根manifest為 `be04e87136b05e09c3eb92402eea6173280687c9323fdf97cef77c2c8dd10a10`，三子manifest與候選相同。核心兩項測試10.616秒無跳過；24381種來源變異、301個已用色盤失配、十二個真實刪除／損壞及隔離、十三完整圖與全部區外、十五區域字墨與整圖通過。單格合成診斷1049種全部辨識、1045種可直接繪製；剩餘是空白與三種需要原版鄰格定位的同源來源，整圖正對照已補驗新增同源格，舊兩種沿既有正常收據保持完成。
