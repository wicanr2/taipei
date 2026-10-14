# 開場、插畫與動畫完整圖像

狀態：DRAFT。對應 [#32](https://github.com/wicanr2/taipei/issues/32) 與來源母項 [#28](https://github.com/wicanr2/taipei/issues/28)。入口 [CONTEXT.md](../../CONTEXT.md)。沿用所有圖片與介面、B、1280×800、Noto、五語系及F12，原版構圖、透明、裁切、相位與時序保持原樣。

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

[copy_illustration_generations.py](../../workspace/tools/copy_illustration_generations.py) 只複製內建imagegen的明列輸出及提示，保留原預設檔案；metadata記錄來源／版面／提示／生成圖sha與權利。目前53組來源參考包含170相位，小游標組只作原型對照，52組可作美術批次。新生成的r25六相位與r42雙相位仍DRAFT；r42新增外側白邊與小人物手持細節尚未符合來源，不能接產品或算完成。細小不可辨識細節須保留原始形狀，不由生成模型猜武器、文字或用途。

相位原型 [illustration_prototype.py](../../workspace/tools/illustration_prototype.py) 只輸出DRAFT。`illustrations-v1/prototype-v1/` 保留首次比較與原執行腳本；`prototype-v2/` 使用r42-v2背景板，人物／細小道具以原始形狀及B材質覆回，保留原位與相位，不猜用途。只去除原參考外緣沒有的新增近單色邊框，原件白邊每通道差3，容差5且參考原邊非單色才可去除。原版各相位相同的靜態區沿同一B底圖；小形狀區的四權重邊緣可隨鄰近相位變化。r42的(48,52,72,22)只覆前景色號形狀，原圖背景不整塊覆回，避免色塊接縫。類似圖庫逐張核對後才套用，仍未READY。

## 已取得的 DRAFT 原版證據

`illustration-observer-r1/audit.json` SHA-256 `f22294d861e191b516b1aacc46205c8937742264a8c736ed1bd4cf5cf603f262`，從EXE無輸入正常入口觀察8億步，28種原始圖像、30種來源／呼叫組合、1362次完整返回後緩衝比對通過。沒有HD、GUI或退出聲明。

r2增加before／after原件及最大可見矩形，保留首次裁切。48份原件中27份完整顯示來源，46個有畫像素的來源變異反例有效，兩份首次狹窄裁切無非透明像素明列。audit SHA-256 `c0db09774e394c14c2a4dc3bc08113a318b15edf6bdeafce9d16e1a8a97b1dd1`；獨立重讀兩ROM核對為 `3b37b5d2cc4f6dbfc4167d7c039b517c24959a6e5c4ab4fe54b5124c982a9b65`。全部1362次返回均核對，48份只是保存例，不代表只核對48次。

色盤另保存8種與7個觀察事件。a05第一次繪圖時仍是前一色盤，不能把呼叫瞬間色盤當成最終發布畫面。正式配色／淡入仍需依實際發布狀態，不能只看PNG或ROMA3就宣稱完成。

相位參考manifest `13c5aac1a68913b2562e2cfc86032be925d21f02aa7712388b482b400e0f2f0c`。目前只生成r25六相位與r42雙相位，加先前兩門樓；r42-v1被拒絕，v2作背景板與原形狀覆回。八張DRAFT原型v2 manifest為 `99c3de63409f85af4149cb032af3d050713c8031da0ead5bad851468b495022d`。完整批次、資源回退、正常GUI、README與封包均未完成，不把原型數當已交付。
