# 開場、插畫與動畫完整圖像

狀態：CONFORMED，限完整來源、保守覆繪與下列正常代表抽驗；不外推所有事件／結局分支。對應 [#32](https://github.com/wicanr2/taipei/issues/32) 與來源母項 [#28](https://github.com/wicanr2/taipei/issues/28)。入口 [CONTEXT.md](../../CONTEXT.md)。沿用所有圖片與介面、B、1280×800、Noto、五語系及F12，原版構圖、透明、裁切、相位與時序保持原樣。

來源先沿 [008盤點](../re/008-full-asset-inventory.md) 及 [033](033-localization-source-coverage.md) 已核對的raw、RLE、IV2與五個繪圖呼叫。不將原初盤每筆可解資料直接算插畫，105×89世界資料、字型、色盤與音樂另分類並附證據等級。未知用途保留數字編號；資料未知不猜補正式行為。

新增研究／原型根為 `workspace/prototypes/hd-style/illustrations-v1/`，放每個完整原圖、全部相位別名、原始ROM定位、解碼與來源雜湊、生成圖及提示。可重生來源清單由 [illustration_sources.py](../../workspace/tools/illustration_sources.py) 建立。所有原圖與衍生素材留本機，不入Git；此DRAFT不進產品。

ROM52–55每個實際八筆offset表都能由033已證實的IV2位移／literal／加法進位結束契約完整消耗；合計32個來源相位，全部寫入64000色號範圍。這確認來源形態，尚不推定用途、繪製位置或正常出現時序。每筆保留透明空白與原始左上偏移，不把裁切後相位誤放同一位置。

後續以唯讀原版呼叫與完整合成來源確認位置、透明色、裁切和發布時機，再固定完整重繪與READY契約。重繪先以完整相位組保持一致；五語系文字沿033後繪，避免生成圖造字。正常開場、城市事件及原版退出的代表抽驗另登記，合成圖表不當正常玩家收據。

初次匯出209筆／197種非9×9圖像，包含既有介面圖片，不能當197張待重繪數。inventory SHA-256 `d67d234268f912cfc049ebad59ecf706d967ee2e6ce6d5d95a9c21678d356f5a`。原初盤加減分類後為1343筆／1246種圖像，透明、正式色盤與場景時序仍分開驗。兩張門樓生成原型只留本機：a04-v1錯造文字已拒絕，v2空白匾額須復原原字墨；a05待原版繪製契約。兩者均未READY，未接入呈現器。

## 原版繪製證據

沿033的既有IDA9.4原件，無新增反組譯、改名或規則研究。以下位址皆IDA loader linear，輸入EXE SHA-256沿033；運行觀察另標原始實體位址。

| 原始函式 | 已證實契約 | 原件與SHA-256 |
|---|---|---|
| sub_1605E／sub_160C5 | 寬高後0,color,count游程；255跳過背景，非255寫入 | ida-52/blit.json `4b695cf830d789486b8345252f7457a5c33b17c37f146fb7d493d0de219fdb4a`；image.json `c6e51205924341c5ae15f5247acbcbe62fae4cebc028e0d7cedf83317f623519` |
| sub_16129 | 寬高後逐列rep movsb，包含255，無透明判斷 | 同blit.json |
| sub_16164 | IV2位移／literal；16-bit目的位址加法進位結束 | ida-52/iv2.json `13129191246cd6f111e960ea7b2fb501b4cb7861f4a47dc53d954838eed189cd` |
| sub_161C3 | 原圖來源矩形裁切，逐列rep movsb，無透明判斷 | ida-52/clipped.json `b772671cbf462ccc834494e0cb96534e30277fbfa3d3453d8b5bc447be681acd`，保留原始mul cl，未擴張至未驗寬度 |
| sub_16210 | 原圖來源矩形裁切，arg_10低byte為透明色，相等時跳過 | ida-52/clippedraw.json `12b3263c6e54f56df4bcda0082167af9f67e0e9cddeda0d71e62ccec79ce0859` |

三十三筆IV2逐literal重讀均無255，因此本批以255標記未寫背景不會混淆真正白色literal。不能把raw圖片一律當透明，須保留實際呼叫契約。

ROM0與ROMA3色盤經原始8-bit通道右移2位、VGA6-bit展開後相差七個色號；ROM0對正常城市色盤252／256項相同，四個運行中改色仍須記錄。ROMA3的31號為黑色，原初城市預覽為灰色。因此a05的灰背景只是DRAFT導覽色，不當正式黑背景；正式素材與色盤契約須以原版實際呼叫／發布畫面回核。

唯讀診斷入口 [illustration-source-audit](../../workspace/app/cmd/illustration-source-audit/main.go) 從真實EXE入口觀察上述六函式，以原版返回後完整後緩衝比對來源與透明／裁切合成，保留實際色盤。沒有HD、checkpoint或城市注入；無輸入前段不當正常GUI或完整退出。參數 `-original <唯讀原版> -inputs <本機DRAFT來源> -out <新的本機目錄> -steps <有界上限>`，僅在既有Go／GUI Docker image、1000:1000、有界資源與無網路執行。

獨立核對入口 [illustration_source_check.py](../../workspace/tools/illustration_source_check.py)，參數 `--inputs <完整來源> --audit <唯讀觀察目錄> --out <新JSON>`。直接重讀兩個ROM的原始bytes，重解圖片，再用實際before／after核對透明與裁切；已畫像素的來源變異必須被拒絕，不信任工具自報Matched。

相位組原型入口 [illustration_groups.py](../../workspace/tools/illustration_groups.py)，在既有 `illustrations-v1/groups/` 內按原始圖庫分組，保存每格來源／原生矩形、灰色間隙、原始別名與固定reference sha。原生寬高與相位數不由生成模型改動；生成後整張縮放再按已存矩形切格，不把灰色間隙放入遊戲。兩門樓已另有DRAFT，既有UI／Noto標題與七張城市預覽／游標分別核對，不將所有197種都當新生成需求。

[copy_illustration_generations.py](../../workspace/tools/copy_illustration_generations.py) 只複製內建imagegen的明列輸出及提示，保留原預設檔案；metadata記錄來源／版面／提示／生成圖sha與權利。53組來源參考包含170相位，細小圖A35只作來源對照，52組作美術批次。初次r25六相位與r42雙相位仍DRAFT；r42-v1新增外側白邊與未證實手持細節，已拒絕。細小不可辨識細節保留原始形狀，不由生成模型猜武器、文字或用途。

相位原型 [illustration_prototype.py](../../workspace/tools/illustration_prototype.py) 只輸出DRAFT。`illustrations-v1/prototype-v1/` 保留首次比較與原執行腳本；`prototype-v2/` 使用r42-v2背景板，人物／細小道具以原始形狀及B材質覆回，保留原位與相位，不猜用途。只去除原參考外緣沒有的新增近單色邊框，原件白邊每通道差3，容差5且參考原邊非單色才可去除。原版各相位相同的靜態區沿同一B底圖；小形狀區的四權重邊緣可隨鄰近相位變化。r42的(48,52,72,22)只覆前景色號形狀，原圖背景不整塊覆回，避免色塊接縫。類似圖庫逐張核對後才套用，仍未READY。

## 已取得的 DRAFT 原版證據

`illustration-observer-r1/audit.json` SHA-256 `f22294d861e191b516b1aacc46205c8937742264a8c736ed1bd4cf5cf603f262`，從EXE無輸入正常入口觀察8億步，28種原始圖像、30種來源／呼叫組合、1362次完整返回後緩衝比對通過。沒有HD、GUI或退出聲明。

r2增加before／after原件及最大可見矩形，保留首次裁切。48份原件中27份完整顯示來源，46個有畫像素的來源變異反例有效，兩份首次狹窄裁切無非透明像素明列。audit SHA-256 `c0db09774e394c14c2a4dc3bc08113a318b15edf6bdeafce9d16e1a8a97b1dd1`；獨立重讀兩ROM核對為 `3b37b5d2cc4f6dbfc4167d7c039b517c24959a6e5c4ab4fe54b5124c982a9b65`。全部1362次返回均核對，48份只是保存例，不代表只核對48次。

色盤另保存8種與7個觀察事件。a05第一次繪圖時仍是前一色盤，不能把呼叫瞬間色盤當成最終發布畫面。正式配色／淡入仍需依實際發布狀態，不能只看PNG或ROMA3就宣稱完成。

相位參考manifest `13c5aac1a68913b2562e2cfc86032be925d21f02aa7712388b482b400e0f2f0c`。初次生成r25六相位與r42雙相位，加先前兩門樓；r42-v1被拒絕，v2作背景板與原形狀覆回。八張DRAFT原型v2 manifest為 `99c3de63409f85af4149cb032af3d050713c8031da0ead5bad851468b495022d`，原件保留。

## 完整 DRAFT 批次與發布色盤

2026-10-15完成52組169相位，加兩門樓、七預覽及細小圖A35，共179張完整四倍圖。其餘18種由既有UI／Noto處理，197種來源全部有分類。A35用途仍未知，不推定輸入游標行為。`prototype-v10/manifest.json` SHA-256 `ebe1576eeb2899058aff4ef8a3bba4b64a1e24f56f9cbb4ed17b15fd54dc519b`；54份選用生成metadata含來源、提示與修訂雜湊。A16沿用A15同一背景板，57個原生差異包含眼鏡與嘴形，不能只稱嘴形動畫。

[illustration_prototype_check.py](../../workspace/tools/illustration_prototype_check.py) 直接重讀ROM，核對209筆／197種來源、179個PNG及18個既有UI分類、54份生成metadata、尺寸與不透明性。驗108269個原255外背景格、3539個黑場格、63560個跨來源靜態格及1876個同角色格。四個有效反例為黑場亮點、外背景新墨、八方向缺相位、同街景背景改色。收據 `workspace/runs/illustration-prototype-v10-check.json` SHA-256 `9b62f6e54995669823ae2c192fb7237ec365d0d104abf53725c759977a04862d`。這證明明列結構條件，不替代正常GUI與整體美術驗收。

R42–51共用背景板，人物與小道具由原形狀及相位差異覆回。前次逐像素複製共通色號造成角色鋸齒，已改成完整背景板及有證據的局部形狀；灰色間隙的漸層則依參考邊緣與已測色域排除。保留舊版本與執行腳本，沒有將結構檢查通過稱為美術通過。A33弧線差異包含14與195兩色，不把角色自身195號膚色覆成弧線。生成字、旗面及細小標誌改回原輪廓，不猜Unicode內容。

[illustration_published_palette.py](../../workspace/tools/illustration_published_palette.py) 沿033正常冷啟動r15的標題、百貨、交通與獎章四份原版收據，重算原生PNG與64000色號／當時色盤逐像素相同；四者256項均為ROMA3的VGA6-bit展開。正常城市與ROMA3相差11項，包含四個城市運行改色；繪圖瞬間a05的31號綠色不能當最終黑背景。收據 `workspace/runs/illustration-published-palette-r1.json` SHA-256 `c8a44941e1290044db13de03ec28f6f0b2c523690d30cb05bcddd7214b77d50d`。這是既有正常原版證據，沒有驗新HD或新增平台聲明。

產品仍使用038已驗版本。資源回退、新HD正常GUI、更新README照片與封包尚未完成；DRAFT圖片不得直接載入正式呈現器。

## READY 呈現契約

2026-10-15證據審查：六種繪圖ABI、三種完整解碼、原版1362次合成、正常發布色盤與179張原型的結構條件足以實作保守來源覆繪。用途與未抽驗的出現分支仍未知，不阻塞按原始來源辨識的呈現。原型保持DRAFT，正式素材須由下列工具重建為封存的READY manifest，不能直接改標籤載入。

| 項目 | 輸入、邊界與失敗處理 |
|---|---|
| 固定輸入 | EXE `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`、ROM `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29`、ROMA `5d66f238dce650b8a407986100392ee4b8ac2aa23a033e80a7ca18ed91b3d9b0`。工具Go1.24.13／Python3.11.2，固定GUI image沿038 |
| 來源解析 | ROM檔案偏移、零起算member／image。209筆／197種；raw寬高後恰好w×h，RLE完整輸入／輸出消耗且禁止零長游程，IV2 stride320、carry結束、未寫255、禁止literal255及越界。18種既有UI／Noto不重新蓋原圖 |
| 唯讀觀察 | 六個已列IDA loader linear入口。far參數SP+4 x、+6 y、+8 off、+10 seg；裁切入口+4 off、+6 seg、+8 sx、+10 sy、+12 w、+14 h、+16 dx、+18 dy、+20透明色低byte。原始bytes及encoding必須完全吻合；161C3只接受已驗mul cl可表達的寬度範圍。保留位置、裁切、實際透明與透明色，不把raw255一律跳過 |
| 順序與遮擋 | 最多8192個有界繪製紀錄，同來源／位置／裁切／呼叫移到最後。由新至舊驗原生色號，已確認較新遮擋及已完整核對的文字欄位可略過；其餘每個可見來源像素必須相同，至少兩種可見色號才覆繪。完全遮擋、單色碎片或失配回退。未知呼叫用可安全取得的目的矩形阻擋舊圖，無安全幾何時作全畫面屏障。只有新於屏障的已確認圖可覆繪 |
| 色盤 | 接受ROM0、ROMA3或正常城市三個已知色盤家族，逐圖只核對實際會畫出的色號。原型R使用城市參考，A使用ROMA3；必要變體各子像素RGB加上該原生色號的目標／參考通道差並截在0–255。這是HD配色近似，原版色盤不變。未知淡入或改色回退原版 |
| 正式素材 | `workspace/prototypes/hd-style/illustrations-ready-v1/`，179張來源及按內容去重的已知色盤變體。manifest必須READY、整檔SHA固定、每PNG SHA／四倍尺寸／不透明性核對；每圖故障只回退受影響圖。原始來源仍從兩ROM重解，不能信任素材自報像素 |
| 文字疊合 | 沿033完整來源核對與固定Noto。先移除已驗圖片欄位的原點陣文字，再畫HD背景，最後在該HD底圖上畫Noto；普通逐字文字的已驗矩形保護不被圖片覆蓋。A6／A38標題可讓底圖穿過原字形；無字型、缺譯文或欄位失配時，相關圖片保持原版，避免蓋掉原文 |
| 七張預覽 | R4–10同源MAX／MIN字墨已逐byte核對：左／右上矩形(1,22)–(18,27)、(127,22)–(144,27)，下方y101–106；只含原14號字墨及129號底色。正式圖清成129號，依同一完整原圖核對畫Noto五語系「最大／最小、최대／최소、MAX／MIN」，目標68×20、字級12–20。TSV新鍵僅顯示，不進DOS |

垂直鏈為兩原版ROM → 嚴格來源解碼 → 唯讀呼叫紀錄 → 完整可見來源／已知色盤 → B圖片與Noto → 原版存檔。HD不持有可寫VM指標，不改原圖緩衝、時序、輸入、亂數或SAV。F12停用覆繪時全畫面回到原版；F11與Help沿既有前端契約。

實作入口將使用 [illustration_assets.py](../../workspace/tools/illustration_assets.py)、[hd/illustrations.go](../../workspace/app/internal/hd/illustrations.go)、[original/illustrations.go](../../workspace/app/internal/original/illustrations.go)。新增檔案同次由本節索引；其內容必須遵循本READY契約。

161C3邊界補證：既有IDA原bytes `AD 8B D8`先令AX／BX為完整寬度，`8B 4E 0C F6 E1`是AL×CL計算初始列偏移，`2B D9`及`03 F3`仍用完整BX作列距。不能以「寬度大於255」全部拒絕；sy=0的294／296寬開場圖列偏移正確。READY條件為 `(width & 255) * (sy & 255) == width * sy`，再驗來源矩形邊界。不滿足時保守回退，不擅自修正原版運算。來源為上列clipped.json、IDA loader linear 161D2／161D8／161DB／161F5／16201，推論等級已證實指令語意；正常新GUI另驗。前次過窄guard造成r18交通回退，列為呈現缺口，不能把該輪算交通HD通過。

實際來源／素材故障及遮擋測試入口：[hd/illustrations_test.go](../../workspace/app/internal/hd/illustrations_test.go)、[original/illustrations_test.go](../../workspace/app/internal/original/illustrations_test.go)。七張預覽共用的兩個新顯示鍵使TSV為230鍵，字元集合仍1214種；不改原有228鍵或DOS語意。

正常插畫五語系擷取入口：[illustration_gallery.py](../../workspace/tools/illustration_gallery.py)，由既有介面GUI工具設定 `TAIPEI_INTERFACE_OPENING=1 TAIPEI_ILLUSTRATION_GALLERY=1` 呼叫。銀行背景上使用真實F11／F12／Shift+F1，驗modal期間原版狀態不變；閉合選單後原版角色繼續運行，因此五張照片不宣稱同狀態。R4–10在正常圖表被中央動態資料覆寫，正式圖表仍沿029的完整來源／資料格及五語系契約，不以原圖沒全匹配認定029回歸。

驗收先做實際ROM解析、裁切／raw255／透明色、重疊順序、未知屏障、來源單點失配、未知色盤、缺圖／竄改PNG／manifest及文字字型故障。再從正常冷啟動走開場門樓、百貨、透明角色／交通與獎章代表、F11五語系／F12／Help、城市原版存退讀及退出；不以合成或direct-entry取代正常GUI。依使用者正常遊玩抽驗，不重跑長RAM／CPU／RNG對拍。README使用新程式實際擷取照片；所有素材與原始收據只留本機，正式封包另驗。

獨立正常插畫像素核對入口：[illustration_gui_check.py](../../workspace/tools/illustration_gui_check.py)。從兩ROM重解來源，讀封存READY PNG與正常冷啟動收據，驗十張照片明列可見插畫的完整四倍格及單像素破壞反例；字墨僅排除已列欄位，沿033另驗。未提供`--normal-run`時只核對插畫前段，`normal_path_complete=false`；完整存退讀由獨立主收據閉合後才可匯出README及結案。不將呈現器自報Painted當像素證據。

README匯出入口：[export_illustration_screenshots.py](../../workspace/tools/export_illustration_screenshots.py)。正常主流程、銀行五語系／F12／Help與十圖像素核對全部通過後，只複製八張明列原版及HD PNG並追加既有來源清單。原始收據與完整素材不入Git。

正常抽驗可由同一候選程式的兩次冷啟組成，明列插畫來源前段與完整存退讀流程。r19已取得十份插畫／五語系照片與Help，420秒驗證上限在上任信`letter.easy`後截止，沒有完整退出聲明。保留該原件，以r20真實冷啟按Space略過片頭後完成核心存退讀；兩工具以 `--normal-run` 指定完整流程，不把r19寫成成功完整退出，不重跑已驗插畫。

正式READY manifest為 `545b4f94b6454debc0de5110bab646d5e68ae19dfa126f700361cd12d9d276af`，179種／260 PNG／261檔。由同一固定輸入乾淨重生至 `workspace/runs/illustration-assets-repro-r1/`，261檔逐byte相同。候選Linux r2 SHA-256 `fa21269163c22123f0c7d1ad28da420150b3bc731f990aace951215a9396ea3e`；尚未提升標準入口，正常GUI驗收與跨平台另記。

## 正常代表抽驗與交付入口

2026-10-15完成039本範圍。179種正式圖、260個PNG與manifest共261檔乾淨重生相同；18種既有UI／Noto另列。完整原始圖像1343筆／1246種，包含地圖1134／1049及非地圖209／197。這是來源與呈現覆蓋，不宣稱每種原版出現分支均已走過。

| 證據 | 已驗結果與SHA-256 |
|---|---|
| 正常插畫前段r19 | EXE冷啟無checkpoint，取得門樓／百貨／透明角色／交通／獎章插畫代表；銀行原版／五語系、F11 modal狀態、F12原生最近鄰及Help輸入隔離通過。gallery `47c38e086b639efc10af6d1c7cfe9d7acd379fbefc2c8f49616e46d4ab08be2a`；上任信末段420秒驗證上限截止，沒有完整退出聲明 |
| 獨立插畫像素 | `interface-locale-cold-r19/illustration-pixel-check-r2.json`：十圖165591個原生位置的完整四倍格相同；改動實際解碼呈現緩衝後重跑同一全圖核對，十個單像素反例均拒絕。SHA `9e8b94eea81e11851772a3dc2d94ec35200ce48486e924e37a237863905db7c1`；只確認插畫前段，不補造完整流程 |
| 完整正常r20 | 同一r2程式冷啟，以原版Space略過片頭，再進城、F11、兩場景F12、14次原版讀鍵／release、93567-byte LOCALE.SAV實際存讀及DOS退出。1,797,602,774步；verification `e628e40f21941f91c36c3fe6cf1b85d65811d3a6ce10ba090030582d21af357e` |
| 原版SAV | `4152f923daa7535fbd49b6d6cabb780c1ef3b6a4cd3f8bd8c91395ca2a123b4c`，讀回後不變；未與未受控亂數的另一局宣稱逐byte parity |
| 程式 | 來源提交 `12ed901d17c55417fdd6aaae80b45ed68c79ab4f`。Linux r2及標準入口由固定dosgolem／七補丁乾淨重建相同，SHA `fa21269163c22123f0c7d1ad28da420150b3bc731f990aace951215a9396ea3e`；新外平台版本由#9正式封包重建 |
| README | 八張新真實PNG，合計92張／79,734,099 bytes；manifest `cc5847f66da27c44ab16df0465cd1afc20bc34273923f17b0108196833edff9c`。每張保留程式版本、來源、語系與原生畫面雜湊 |

五語系各156開場階段／36城市訊息階段回歸、209別名／197來源／179素材／537色盤變體、五語系新增MAX／MIN字墨、實際缺圖／竄改PNG／manifest隔離、來源／色盤／raw255／透明色／遮擋／未知屏障及六ABI唯讀測試通過。原型、正式素材、原版、字型、SAV與原始收據只留本機。沒有長RAM／CPU／RNG對拍、人耳確認、逐事件／成功結局流程、外平台真機或正式封包完成聲明。

指定find無root-owned檔或.md目錄；project=taipei容器已清空，未新增image。後續封包沿#9，不重新開啟已通過的來源／插畫與介面批次。
