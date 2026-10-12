# 032：其餘介面的五語系呈現

狀態：CONFORMED，2026-10-12，限本批來源文字與下述實際驗證。Issue：[#51](https://github.com/wicanr2/taipei/issues/51)，母項 [#49](https://github.com/wicanr2/taipei/issues/49)。沿 [030](030-hd-localization.md) 與 [031](031-help.md) 的已確認語言、字型、操作及設定。逐字動畫、未知事件與 029 完整 HD 驗收不在此完成聲明內。

## 來源審查與邊界

已證實的完整來源、選取與動態欄位，分別沿 [017](017-new-game-dialog.md)、[018](018-startup-menus.md)、[020](020-city-footer.md)、[021](021-tool-submenus.md)、[022](022-city-function-menus.md)、[023](023-file-dialogs.md)、[025](025-budget-panel.md)、[028](028-ending-achievement-base.md) 及 [029](029-chart-windows.md)。不重新推定按鍵、規則、統計或原版數值。

| 家族 | 已確認來源與文字單位 | 呈現範圍 |
|---|---|---|
| 啟動 | main／city／difficulty，十三狀態 | 原按鈕與標題安全矩形，原選取色 |
| 工具 | tool-02／05／09／10／11，十八狀態 | 各選項整句，原按鈕或原行內縮 |
| 城市 | city-f1–f6，二十九狀態 | 各選項整句，原完整矩形及選取色 |
| 新遊戲說明 | 完整 ROM22 與三段已審查原文 | 原底板內緣三段安全矩形；目標仍超過 500000 |
| 底部 | 020 完整重建兩區 | 每單位、萬、年、月；原數字及未知角落符號保留 |
| 檔案 | 023 完整 browser／quit-confirm | browser 的玩家檔名不翻譯；離開提示為「您確定離開遊戲嗎?(Y/N)」，不改成存檔詢問 |
| 預算 | 025 完整重建、十一原數字欄 | 標題、操作提示、五列、稅收／淨額、%／萬分離；不跨過數字合併文字 |
| 圖表 | 029 完整固定框架 | 四組 MAX／MIN；中央原資料及色帶保留，不為翻譯恢復 #48 完整驗收 |
| 政績 | 028 已見完整靜態底圖 | 只翻標題，未見動態政績不猜補 |

固定 ROM SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`，EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。位址沿引用規格的 ROM 檔案偏移，幾何採原生 320×200 四倍。工具鏈與固定 Noto／OFL 沿 031，不新增反組譯結論。

版面只讀固定本機資料：startup layout 雜湊 `55d977d8da010783bb5a1e0836e6597458dba33a069f83163f0693ff6de264ee`、tool layout `8da4bcab9cdff0e2cb59a208814c7f4589458ad6d9148f6cf6c218cce46fa4ee`、city layout `91dc1347725734638035f0488233945d46db59a173fce8dec3dcc8a5c62f6c64`、budget layout `f505cd1ca1e70a798d26d4e1caa9f3a3170ca4cb93b88dd0c81e40a8eb5891f0`。原文欄只作既有證據，正式繪字只用 TSV 文字鍵。B 底板／按鈕重用上述 layout 中固定素材雜湊；政績無字背景 `ending-scene-v1/art-scaled.png` 雜湊 `ac77b0cc8fc8f085d6c09d6e3c9ea3107afbe57494d3ef6417c0cc8ce9250c2c`。

## 正式契約

- 五個語言均由唯一 `workspace/app/locales/ui.tsv` 取字，含繁中原文。選項以 scene ID 及原選取索引對應穩定鍵，不以譯文辨識來源、資源、規則或存檔。
- 原按鈕、面板、命中範圍、選項順序、選取顏色保持原樣。整句在既有安全矩形置中，單行逐整數字級縮小至 14 px；原生僅 5–7 px 高的圖表／單位欄容許 12 px 與 1 px 內縮。仍不容納即拒絕，不裁切。新遊戲三段在原底板內緣換行，字級 44 至 24 px，行距及總高同時受限。
- 所有原版來源／色盤／素材／字型／授權閘門先通過，才套語系。既有中文字從空白 B 底板重組，避免用翻譯覆在舊字上。切語言時完整預驗並交換語系快取，每幀由原版重新繪，返回或 F12 不留殘影。
- 功能視窗開啟時，仍可顯示六標題及底部資訊。六標題以既有 013 的完整頂部 `uiSHA` 與色盤辨識；底部逐區沿 020 完整重建。各區獨立核對，不因中間視窗未辨識而遮住它，也不把未辨識視窗判成已翻譯。
- 預算與底部的原數字字串、顏色、位置、正負號及欄數不變。萬仍等於 10000；窄欄英文以 `10k` 表示此單位，無金額換算。年與月只換單位文字，原曆年數值不轉換。
- 檔案 browser 內八欄 ASCII 檔名及列表保持原值，Y/N 仍送原版原鍵。翻譯不進 DOS、記憶體、亂數、檔案或 SAV。前端設定沿 030。
- 任一語系鍵、字形、安全矩形或空白資源失配，不顯示半套面板；保留原版並記錄呈現原因。F12 原版始終顯示未覆繪繁中。
- 未在上述來源的其他功能視窗、事件及圖片內文字仍須查證，歸 #49／#31，不由本批完成外推全遊戲完成。

## 預登記驗證

### 人口、民意、速度與狀態訊息的來源審查

2026-10-12 追加 READY。正常冷啟動收據為 `workspace/runs/interface-locale-cold-r2/gui/mayor-1-capture.zip`、`mayor-2-capture.zip`、`environment-0-capture.zip`、`environment-1-capture.zip`。此批來源研究歸 #51。工具為固定 GUI image 內 Python 3.11.2、既有 dosgolem 與原版 ROM，雜湊及位址基準沿上文。

- 人口與民意視窗分別為 ROM 成員 13／14，均位於原生 `(18,37,235,132)`。解碼色號 SHA-256 分別為 `9e700aade5641d18fe5e21215a88e621c1a3a955d47d6bc5930d8eb18c9fab19` 與 `a1be5c63d2cb40a50027866805e0f7c3b80a611f16aed1abc3f2346c02f5b8c6`。
- 人口六組數字欄相對座標為 `(46,15,3)`、`(143,15,8)`、`(46,40,3)`、`(143,40,8)`、`(144,65,8)`、`(180,88,3)`，第三值為六像素寬字欄數。民意十一組為 y=28／47／66／85／104、x=81／196 的三字欄，及 `(130,123,3)`。均使用 ROM56 的 5×7 字模，前景／背景色號分別為人口 14／9、民意 11／1。人口等級在 `(144,108)` 使用 ROM57 的既有字模與色號 13。將正常收據的各欄解碼並重建後，兩個完整視窗均為零像素差異。這只確認欄位呈現，不新增統計公式或等級規則。
- 翻譯人口的固定名稱、三個「人」單位及五種原版等級，民意的標題、十項名稱及總成績。每次必須完整重建來源，數字、符號或等級無法重建即整個視窗回退。文字在原位 B 底板內繪製，原數字及百分比區保留原像素與色盤。
- 速度視窗為 ROM12，原生 `(54,87,165,41)`，解碼 SHA-256 `ebc0873bab68422d2bae28af7e1fa2734a8cb04aaa4aecf7c71e4a7676f4ed78`。四個選項字模位於相對 `(7,14)`、`(47,14)`、`(87,14)`、`(127,14)`，原白字 15、選取紅字 12；選取字模由 ROM57 重建。只換選項文字，不改速度或確認操作。
- 底部狀態訊息由固定 EXE 的原始字串位元組與 ROM56／57／58 字模重建。漢字從 `(19,177)` 每字前進 16 像素，ASCII 從同一水平位置、y=181 每字前進 6 像素，色號 32；完整左區 `(7,175,224,18)` 必須等於原底圖加字模。訊息速度提示已在正常收據零差異重建，其餘固定警告只在來源完整匹配時顯示。記錄靜態來源已確認與實際觸發範圍，不宣稱每個災難均已正常觸發。

來源重建、座標與 EXE 字串定位由 `workspace/tools/interface_source_catalog.py` 重生至 `workspace/runs/interface-source/catalog.json`。正式呈現為 `workspace/app/internal/hd/interface_extra.go`；來源碼與文字鍵分開，翻譯仍只從 TSV 取值。

### 災難城市分支

追加 READY。從正常主選單用 Right 選擇災難城市，再以 Space 開啟，六個 Down 循環來源保存於 `workspace/runs/interface-locale-cold-r5/gui/disaster-city-0–5-capture.zip`。主選單是左右選取，城市選擇不以 Escape 返回；探索工具前件誤用按鍵的紀錄保留，不列為產品缺陷或驗收。

原底板為 ROM18，236×132，原生 `(18,37)`，解碼 SHA-256 `bb31340f9990e90edba6eaa575966b8dd29ed72ba014357cd1dd1825ace5667a`。六個字串原始 EXE 檔案偏移為 `0x25591`、`0x2559e`、`0x255ab`、`0x255b8`、`0x255c5`、`0x255d2`。左三項字模起點 `(13,43)`、`(13,74)`、`(13,105)`，右三項 x=127；皆為底板相對座標。以 ROM57／58 字模及字碼重建，選取色號 15、其他 55，六個完整面板皆零像素差異。HD 沿已定 B 木紋／紅按鈕與相同幾何，選取白字、其他紅字；翻譯標題及六項城市，不更改城市檔案、入口或順序。

上述追加家族只核對實際使用的 39 個色號，RGB 串列雜湊為 `bb592feaa8a51c36b22b702efa4fbed5a793e43a8029526cd6912d915d8a7919`，清單由來源工具重生。人口與災難城市兩個正常入口得到相同串列；未用的 232／233／240／241 實際會不同，不把它們當作來源失配。

五語系遍歷十三／十八／二十九狀態、三段說明及動態家族，檢查實際字墨、安全矩形、整個區外、原數值與檔名。缺鍵、缺字、超長、來源或資源失配須有效拒絕。正常 GUI 短流程涵蓋啟動、城市與工具選單、預算、存讀檔、F11／F12 與 Help；不恢復舊長時間 RAM／亂數抽樣。Linux／Windows／macOS 編譯與真機、正式封包分開。

正常 GUI 入口為 `bash workspace/tools/interface_locale_playtest.sh`，由 `workspace/tools/interface_locale_playtest.py` 冷啟動原版，檢查翻譯並擷取尚未辨識的人口、民意及環境視窗。原版單幀來源驗證為 `internal/hd/interface_locale_test.go` 的 `TestInterfaceLocalesWithOriginalReceipts`，需要固定本機素材及唯讀 ROM。

實作、測試與正常收據從 CONTEXT 索引。來源覆蓋未確認或正常路徑尚缺時，保持對應 Issue OPEN。

## 已完成的來源與排版驗證

正式 TSV 已擴充為 181 鍵、927 種字元，五個語系欄均完整。SHA-256 為 `51a713f5499974ea30ff59d5902606b04cede9d4bbb99823c5034f800d73fa88`。固定 Noto 實際字形檢查、Help／F11／鍵盤回歸通過。五語系各 77 種已匹配狀態通過，包含全部 60 種既有選單選取及六種災難城市選取。預算與人口／民意數字區逐像素保持原樣，原版色號輸入未改寫。

追加家族的來源單像素破壞、使用中色盤失配、未用色盤變動正對照、F12 完整原版、缺必要鍵及過長翻譯整幀回退通過。結果為 `workspace/runs/interface-locale-unit-final.log`，固定參考圖保存在 `workspace/runs/interface-locale-gallery-r3/`。已檢視實際英文人口／民意與日文災難城市排版。這些圖是正常原版單幀的呈現驗證，不取代整條正常操作路徑。

獨立來源證據為 `workspace/runs/interface-source/catalog.json`，SHA-256 `c2fcedc4742b6ab55815ca5409942a95cf5023cb42e3f9da8be38661108d95d9`。人口、民意、速度、訊息速度與六種災難城市均由原版正常來源完整重建，零像素差異。22 個固定訊息的 EXE bytes 與字模構成已核對；各個自然災難與所有警告的正常觸發未逐項驗證。

正常環境警告會逐字繪出並自行結束。來源閘門只接受完整訊息，中間字串保留原版；逐字動畫翻譯仍屬 #49，不能將完整訊息已匹配外推為每個動畫相位完成。警告結束後多送 Space 會操作目前工具，驗證工具須等待完整訊息後直接開下一個原版選單。

## 正常路徑與現行程式

同一產品 binary／TSV 的分段收據保存如下，均從全新冷啟動取得，沒有 checkpoint。

| 收據 | 已驗範圍 | 邊界 |
|---|---|---|
| `interface-locale-cold-r9/gui/` | 英文道路子選單與 Help，人口／民意各五語系；工具／人口／民意三場景 F12 完整原版往返 | 後續測試多送 Space 開啟工具，整輪未通過；只使用此前已核對收據 |
| `interface-locale-cold-r10/gui/` | 五項環境設定的完整英文提示、預算五語系、LOCALE 存檔與同次原版讀回 | 後續測試未等待離開提示完整顯示，整輪未通過；不以此聲稱退出 |
| `interface-locale-cold-r11/verification.json` | 正常新遊戲、英文 F11、檔名保留、實際 SAV 寫入與讀回、存檔／離開提示 F12、英文政績標題與原版返回 DOS | `phase=files`，不重複前兩段；不是全新 EXE 冷讀或完整 HD 驗收 |

r11 以 `TAIPEI_INTERFACE_RUN=interface-locale-cold-r11 TAIPEI_INTERFACE_QUICK=1 TAIPEI_INTERFACE_PHASE=files bash workspace/tools/interface_locale_playtest.sh` 重生；保留已用 run 名稱，重跑必須另選新編號。完整流程用 `TAIPEI_INTERFACE_PHASE=all`，環境／預算／檔案流程用 `settings`。所有模式仍正常冷啟動，沒有狀態注入。

r11 的十四次原版讀鍵／release、實際 93567 bytes 的 `LOCALE.SAV`、讀回後存檔不變及原版退出通過。SAV SHA-256 為 `4152f923daa7535fbd49b6d6cabb780c1ef3b6a4cd3f8bd8c91395ca2a123b4c`；驗證 JSON SHA-256 為 `0392a2077014272838a569c6c922a74588c714125bebfd18ea985099f6f28949`。已檢視實際英文民意、檔名與離開提示。

已驗 Linux binary SHA-256 為 `c99f17bd03354972ce77346613ba2e1887e361690ac27c5979cf2473a8ab084a`；`build_preview.sh` 從固定依賴重建後與已驗副本逐 byte 相同，外部 TSV 與唯一來源逐 byte 相同。沒有恢復長時間 RAM／亂數抽樣、#48 完整驗收或正式封包。平台編譯與清理結果另見本批 WORKLOG、CONTEXT 及 #51 收尾留言。
