# 三平台本機封包

狀態：READY。對應 [#9](https://github.com/wicanr2/taipei/issues/9)。入口 [CONTEXT.md](../../CONTEXT.md)。前置038／039及正常玩家驗收已完成；本項只改啟動、版本與封裝，不改遊戲規則、素材或呈現演算法。

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
