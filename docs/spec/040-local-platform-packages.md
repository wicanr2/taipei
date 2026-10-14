# 三平台本機封包

狀態：CONFORMED，限三平台內容／結構、Linux及Windows Wine實際啟動；macOS原生執行仍未驗。對應 [#9](https://github.com/wicanr2/taipei/issues/9)。入口 [CONTEXT.md](../../CONTEXT.md)。前置038／039及正常玩家驗收已完成；本項只改啟動、版本與封裝，不改遊戲規則、素材或呈現演算法。

## 輸入與版本

- 使用乾淨提交的不可變tag建置。完整版號為 `v.1.0.0-20261015`，日期採Asia/Taipei；CLI `-version`、收據、VERSION、tag、封包及manifest一致。CLI版本查詢不開GUI。
- 原版35檔與RAR逐項回核001原始inventory；只包遊戲RS201目錄，排除舊DOSBox整合器。EXE／ROM／ROMA固定SHA沿039，資料唯讀，存檔另寫。
- dosgolem固定a9714ebdab2ad6b529f81225472680f2b11f2842及現有七補丁，Go1.24.13、既有Linux／MinGW／osxcross image。從tag匯出原創app及工具，固定module與依賴；不使用工作樹的未提交程式。
- 材料僅收現行載入器所需的固定檔案及READY家族。記錄逐檔SHA；原版、Noto、原版衍生HD分類，不能因private或生成工具就稱可公開。原版及HD完整包留本機。
- 自有程式RRSAL-1.0，隨附dosgolem RRSAL、實際連結Go modules、YMFM與Noto原授權。依二進位`go version -m`列實際元件，不下載未連結的範例／測試依賴。

## 封包與啟動

正式根 `dist-all/v.1.0.0-20261015/`，只建本項使用的 `full-local/`、`smoke/`及`SHA256SUMS.json`，不建第二交付根或公開Release。

| 平台 | 封包及入口 | 可寫位置 |
|---|---|---|
| Linux amd64 | tar.gz；`start.sh`自動解析封包位置，執行同目錄ELF | `${XDG_DATA_HOME:-$HOME/.local/share}/taipei-dosgolem/` |
| Windows amd64 | zip；ASCII CRLF `Start.cmd`，執行同目錄PE | `%LOCALAPPDATA%\TaipeiDosgolem\` |
| macOS amd64／arm64 | zip；兩個已驗架構以lipo合成universal Mach-O，`start.command` | `$HOME/Library/Application Support/Taipei dosgolem/` |

每個使用者目錄下分`saves/`及`receipts/`。啟動器指定原版／materials／230鍵TSV絕對路徑，預設HD，F12可回原版；讀現有語言設定。正常預設使用名義時鐘與音訊，研究抽驗可明示`-mute`及既有診斷參數。必要資料缺少時顯示可見錯誤；Windows保留錯誤console，macOS可用系統alert，Linux寫stderr。不得把原版或封包目錄當可寫存檔目錄。

每包內含完整版號、來源commit、平台／架構、原版／HD／字型權利分類、全部內容SHA及使用說明。Windows README.txt為UTF-8 BOM及CRLF；ZIP含非ASCII項目時驗UTF-8 bit11。打包從乾淨輸入建立，來源封包不覆寫。

## 驗收與停止線

1. 四個架構程式及macOS universal逐項核對header、依賴、版本及來源；Linux查實際`-version`，Windows用既有Wine，macOS結構／CLI字串及launcher契約另列，真機未知不冒稱通過。
2. 解開實際三包至乾淨目錄，核對每檔SHA、版本、權利、必要材料、字型、完整圖像及原版檔；從套件位置啟動。材料由實際HD載入器驗全部家族與五語系，缺件不可靜默當完整HD成功。
3. Linux正常GUI冷啟看見B開場，原版／HD／F11／Help及存退讀沿039正常證據；另驗封包入口、預設音訊及使用者可寫存檔路由。Windows Wine驗實際包正常冷啟與B畫面、含空白／中文路徑；Wine不稱Windows真機。macOS無真機時明列未驗，驗Mach-O兩slice、依賴與啟動參數，不以stub稱實際遊玩。
4. 逐包建立manifest、SHA-256與大小，原始輸入不變，1000:1000、指定find及Docker清空。README只放穩定下載路徑、執行方法及限制；命令與雜湊歷程寫WORKLOG。

原版精確版本／權利人、未逐項試玩的事件／成功結局、硬體逐週期音訊、人耳及外平台真機仍是證據限制，不為封包重開已完成HD批次。此版本不公開Release、不上傳原版或衍生素材。

實作入口將由本節索引：`workspace/tools/release_build.sh`、`release_inputs.py`、`package_local.py`、`package_check.py`與`package_smoke.sh`。這些工具均經Docker入口執行；本機僅做Docker／Git／gh管理。

實際材料載入核對入口為[package-resources](../../workspace/app/cmd/package-resources/main.go)及[AuditPackageResources](../../workspace/app/internal/hd/package_resources.go)，不建立DOS機器；用正式載入器的固定manifest／PNG／字型印記驗全部家族及五語系。Ebitengine在main前初始化X11，所以Linux程式`-version`在Xvfb內驗證，沒有建立遊戲視窗；封包啟動器另可直接讀VERSION供無顯示器查詢。不為版本查詢改動GUI架構。

材料選取包含三份已封存layout的`art_sha256`相依表，不能只看Go的直接檔名。最小材料預檢首次抓到缺少工具背景`city-chrome-lime-v1.png`，已改追完整相依表；586個runtime檔由實際載入器驗全部家族及五語系通過。原始inventory SHA `b9f1a573e3656d800354740edfe3707c80ce520abc9a140b12e5ce54e4e37084`，35檔及RAR回核，封包只收RS201內23檔，排除DOSBox整合器。

工具入口：[乾淨建置](../../workspace/tools/release_build.sh)、[輸入與授權鎖定](../../workspace/tools/release_inputs.py)、[封裝](../../workspace/tools/package_local.py)、[解包與材料核對](../../workspace/tools/package_check.py)、[GUI／音訊與Wine入口](../../workspace/tools/package_smoke.sh)、[正常前端及路徑抽驗](../../workspace/tools/package_smoke.py)。音訊另沿用既有D831 image、Wine沿用C047 image；無網路、1000:1000、trap及有界執行，不重建重複image或覆寫HOME。

收尾入口：[release_accept.py](../../workspace/tools/release_accept.py)。只有三包內容／材料與Linux／Wine實際GUI全部通過才產生`smoke/acceptance.json`並更新既有SHA256SUMS的驗收索引，不改封包內容或tag。另驗macOS兩slice、11.0欄位與系統依賴、35原始檔／RAR、92張README及指定find；平台未驗限制寫入收據。GUI抽驗使用唯讀掛載的`/封包 測試`，實際經過中文及空白路徑，不只將解包目錄命名為中文。

## v.1.0.0-20261015 本機驗收

來源tag固定於 `57c559695fa73ad610ed4fdbce38b0803e6c4b3b`，已推送私人repo，不移動、不公開Release。四架構與macOS universal由同一tag、固定dosgolem／七補丁及三個既有工具鏈重建。程式只有版本及路徑收據metadata改動，遊戲呈現／規則沿039。

| 封包 | 大小 bytes | SHA-256 |
|---|---:|---|
| Linux amd64 tar.gz | 131770851 | `4099d3c802531b5305cd2eccafb545bf4afe6f12f6b44f13f38bba9a7dfaf6d0` |
| Windows amd64 zip | 131547342 | `e298680fb956327026ff6b62e24b1756fe79734dda628078f1151c6270458a19` |
| macOS universal zip | 138670270 | `1d84611455636487adc83ff3a31f2a58a3b2eb3df10ac8de23199dc33a647369` |

三包各629檔，含23原版、586 runtime材料及實際10個連結module的授權，共13份第三方通知。逐檔SHA、manifest、版本、架構、解包安全、Windows BOM／CRLF及UTF-8旗標、實際HD載入器與五語系通過。撤除實際封存插畫後，原生載入核對器拒絕，還原後不改封包。`smoke/unpacked/package-verification.json` SHA `3ff6e824ae9a9c2f3e41900cb200b585279ace7d5920b69135685f4bda450670`。

| 執行驗收 | 已驗及限制 |
|---|---|
| Linux實際包 | 唯讀中文空白目錄啟動，B開場、正式版號、F11英文、預設使用者目錄設定寫入、Shift+F1 Help、F12完整原生最近鄰與返回、缺資料可見錯誤、正常前端停止通過；不是本次完整DOS退出。smoke SHA `65a686d2a318424b98279b5520d97f43c1a5156695ba718bb42c6e92b56ebeb4` |
| Linux預設音訊 | 未指定mute或研究步速，隔離Pulse monitor五秒，峰值5584、459794個非零16-bit samples；技術非靜音，人耳未驗。WAV SHA `f05c22aa237515c56db5ea407699ce43a6511da076194e475c783d71148ca177` |
| Windows實際包 | Wine內實際Start.cmd與中文空白目錄、正式版號、B開場、F11設定、Help／F12及缺資料錯誤通過；本次靜音，不稱Windows真機或Windows音訊驗收。smoke SHA `63f0f4457a0698d1f7a1f6f5f56d8ec9205da9717edf9ccb4dfd4952e6421047` |
| macOS | universal含amd64／arm64，兩slice與個別建置逐byte相同；minimum deployment target 11.0及全部系統依賴、內容／材料與launcher語法／版本核對。原生執行、音訊及使用者目錄寫入未知；不以Linux代跑或stub稱真機驗收 |

X11實窗照片已檢視，Linux／Wine Help八列可見、無缺字或裁切。039的正常存讀與DOS退出沿用；本次停止旗標僅作有界啟動抽驗，不補造原版退出。

原始35檔與RAR不變、92張README的雜湊／1280×800、全部輸出1000:1000及指定find通過；專案容器清空，未新增image。最終 `smoke/acceptance.json` SHA `2d9e2201b4f38aa5160edd2c526d6085111dcb255c19d2266141c0d042e26c99`；`SHA256SUMS.json` SHA `49d2f0b9bf21a938322867cdb90de86b7adad54443e0bb5f2f92031deb96577d`。輸入鎖定 `workspace/runs/release-v.1.0.0-20261015/inputs.json` SHA `21f06194289f37e7ed4bccd158c6cbce25bcbbd596bc363e75b277d23fb2edf6`。全部封包與原始收據留本機。

重建入口為 `bash workspace/tools/release_build.sh <新版本tag>`，其後在固定Docker內依序執行release_inputs、package_local、package_check、兩平台package_smoke及release_accept。既有版本輸出不覆寫；同版本重生請使用另一個乾淨工作區，修正版依版號契約提高修訂號，不移動本tag。
