# 工作歷程

## 2026-10-10：啟動與協作治理

對應 [#1](https://github.com/wicanr2/taipei/issues/1)。先前已依使用者要求撰寫 AGENTS.md。
當時工具政策拒絕主機提權，受限環境也無法連線 GitHub，未把其 token 錯誤當成主機憑證失效。
本次工具環境已開放，主機 gh auth status 成功。使用者已手動建立私人儲存庫，
回讀確認 PRIVATE、Issues 啟用、儲存庫為空；接著登錄初始 9 張 Issues。

使用者追加指定 `workspace/`，覆蓋共用方法的 `workplace/` 預設。
所有研究、工具副本、快取、探針與中間產物都放入該目錄。根目錄保存 Git 管理與文件入口。
使用者另已解壓原始資料至 `rs201 模擬台北/`，保留原位並唯讀使用，不重複解壓。

原有 `taipei/` 是空 clone，只含 `.git`，無提交或其他檔案。將其 Git 管理資料移至
本專案根目錄，移除已空的子目錄，沿用原遠端，未建立第二份 clone。
新增排除規則、CONTEXT、README 與驗收矩陣，避免原版資料與研究輸出進入 Git。

目錄理由：`docs/` 保存受版控的驗收與研究文件；`workspace/` 承載使用者指定的工作區。
未建立第二份本機待辦清單。G0 驗證與提交結果在本節追加。

G0 驗證：文件相對連結、1000:1000 擁有權、根目錄衛生與 `git diff --check` 通過。
Git 狀態確認原版 RAR 及解壓目錄被排除；沒有啟動原版或修改來源。
本批 Docker 均為一次性 `--rm`，未留下執行中或停止的專案容器。

G0 提交 `b685b0c` 已推送 main，回寫並關閉 #1，主機 gh 回讀為 CLOSED。

## 2026-10-10：原版盤點

對應 [#2](https://github.com/wicanr2/taipei/issues/2)。唯讀使用使用者已解壓來源，
新增 `workspace/tools/inventory.py`，輸出 35 個檔案及 RAR 的 SHA-256。
兩個 EXE 完全相同，真實整合包入口為 `RS201.EXE /A /D /x`。
第二次逐檔重算雜湊通過，原版未修改。研究與限制見輸入基線。

既有工具的 7-Zip 無法列舉 RAR，列為工具限制，不重複解壓或退回主機執行。
Go 工具探查首次使用登入 shell，PATH 被重設而找不到 Go；同一 image 改用非登入 shell
確認 Go 1.24.13 可用。此失敗屬工具腳本環境，不是遊戲或產品缺陷。
dosgolem 主工作樹有既有修改；後續只 clone 固定提交，不搬入未提交的改動。

## 2026-10-11：原版啟動與原生鍵盤

對應 #3、#10、#11、#12、#13。知識路由命中復古整合、平台規格優先與文件職責入口。
修正預設 BIOS IRQ1 路由、加入明示的 BIOS 讀鍵等待、接通 DOS 原生主控台鍵盤。
全部修改在 `workspace/dosgolem`，匯出四份補丁與 Docker 探針，沒有改動或推送上游。

長程探針被 Docker OOM 中止，事件確認退出 137。原因是每次 DOS 等待重試累積呼叫紀錄。
新增明示關閉選項，保留預設行為。相同短程重播的畫面與暫存器不變。
未增加 3 GiB 容器限制。原先登入 shell、PNG 輸出旗標與快照步數邊界的失敗，
屬工具使用問題，已按同一工具契約修正，不列為遊戲缺陷。

兩次冷啟動主選單畫面與終點暫存器相同；第三次由原生空白鍵進入城市選擇。
dosgolem 全套測試通過，第四份補丁後核心五套件重跑通過。35 個原始輸入雜湊不變。
新增研究證據與規格索引，建立指定 RRSAL-1.0 LICENSE。限制與命令見啟動基線。
城市地圖的舊快照續跑只作診斷，不替代正式玩家路徑。

## 2026-10-11：暫停與美術方向改選

對應 [#5](https://github.com/wicanr2/taipei/issues/5)。使用者先選 A「原味像素精修」，
其後明確改選 B「細緻手繪材質」，現行方向以 B 為準。這次只定美術方向；字型、
生成圖上的快捷鍵標示、解析度與平台仍待確認。比較圖路徑與雜湊見圖塊來源研究。

目標狀態已核對為 paused。本輪只保存決策與暫停狀態，沒有恢復實作或執行驗收。
GUI 與 HD 研究的未提交修改保留，最近已推送提交仍為 994ca04。
Docker 列舉確認沒有本專案執行中的容器，其他專案容器維持原狀。

使用者隨後指定 HD 解析度為 1280×800，並明確指示恢復工作。採 B 美術方向，
以原版 320×200 的四倍作為 HD 基準，恢復 #4 與 #5 的原版操作及繪圖來源驗證。

使用者再確認 Windows、Linux、macOS 三平台封包；平台真機試玩仍需各自驗證。

## 2026-10-11：原版 GUI 存退讀與 HD 材質原型

對應 #4、#5、#14、#15、#16、#18。修正前端同次更新的文字排序，以及快速 Shift
按放後的大寫轉換。原版曾收到 `ROUDN2`，原因是前端按實體鍵表順序送出同幀字元。
現以有序文字事件轉原生通斷碼，仍經 IRQ1 與 BIOS。隔離 dosgolem 補齊 Caps Lock，
匯出第五份補丁。硬體讀鍵、Caps Lock 與核心測試通過。

完整正常 GUI 流程已通過：冷啟動、新遊戲、游標右移、存檔對話輸入 round3、退格改為
round4、實際存檔、原版離開、全新 EXE 冷啟動、原版讀回及再離開。原版離開有動畫及
最後讀鍵，腳本先前漏掉最後空白鍵，已依原版阻塞狀態補齊並乾淨重跑。
本輪存檔 `ROUND4.SAV` 為 93,567 bytes，SHA-256
`d338d3a1418fedb41e13f38efb34ac462d34317430861669a1abafabc7536de8`，讀檔後不變。
重生命令為 `bash workspace/tools/build_preview.sh` 及 `bash workspace/tools/gui_playtest.sh`。
收據在 `workspace/runs/gui-cold/`，沒有使用機器快照。建設操作及音訊仍未完成。

B 風格離線原型生成水面、沙地與樹冠材質，完整提示詞與原圖留本機。
正常冷啟動地圖 435 格中，434 格完整匹配來源，433 格覆繪、2 格回退。
撤除全部材質後輸出與原版四倍完全相同；破壞一格來源後，該格回退且覆繪格數減一。
三項區域外差異均為 0。重生命令為 `bash workspace/tools/hd_prototype.sh`。
此為 DRAFT 離線原型，不宣稱動態 HD 已完成。

字型比較原型只替換六個實際主選單文字，保留原生 F1–F6 標示與位置。
使用 Noto Sans CJK TC Sans2.004，字型 SHA-256
`dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4`，授權為 SIL OFL 1.1。
已核對十二個中文字皆有 glyph，實際墨跡在安全矩形內。完整文字及動態繪字仍待驗。
命令為 `bash workspace/tools/font_prototype.sh --download`，後續離線重跑可省略 `--download`。
本機比較圖在 `workspace/prototypes/hd-style/font-comparison/`。已展示並詢問使用者字型方向，
尚未收到選擇，不接正式字型覆繪。首次授權檔 URL 指向錯誤子目錄而返回 404，
已改為同一固定 tag 的根目錄 LICENSE，驗證雜湊後才採用。

新增字型工具後，首次離線建置缺少鎖定 Go 模組的下載 metadata。
以既有建置入口 `--download` 補齊後，同一 image 乾淨離線重跑成功。
此為依賴快取問題，沒有更換工具鏈或放寬離線驗證。

本批重新核對 35 個原始輸入雜湊不變，沒有 root-owned 檔案或誤建 `.md` 目錄。
GUI 容器皆使用有界程序、trap 與 `--rm`，本批完成後無殘留專案容器。
# 2026-10-11：原版建設垂直路徑與音訊核心原型

- 工作依 [#19](https://github.com/wicanr2/taipei/issues/19)、[#17](https://github.com/wicanr2/taipei/issues/17)、[#20](https://github.com/wicanr2/taipei/issues/20) 執行。新增研究文件及音訊契約均掛入 `CONTEXT.md`。
- 沿用既有 IDA 9.4 py312 image，最小探針、原始 bytes／位址／獨立檔案偏移與實際 INT 16h 堆疊共同核對輸入 owner。新城市初始焦點在工具列，先按 Tab 會切回地圖；撤回把 Tab 當成必需第一步的探索假設。
- `bash workspace/tools/build_preview.sh` 通過。`bash workspace/tools/gui_playtest.sh` 於全新 EXE 冷啟動經真實 GUI 完成電線施工、存檔、原版退出、全新啟動讀檔與再次退出。施工格逐 byte 相同，存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，讀檔未改寫。細節與定位見 `docs/re/004-native-controls.md`。
- 即時冷啟動盤點確認原版有 OPL2 音訊及節奏模式。快照載入後觀測紀錄為空不代表無音訊。固定官方 YMFM commit 完成離線標題音訊原型：7214 事件全部消費，73.3968 秒，非靜音、削波 0。Linux、macOS x86_64 與 arm64 編譯通過；Windows 編譯器擴充另在本次可重現 Dockerfile 處理。尚未接正式音訊，未做人耳確認。
- 字型比較原型已提出，使用者尚未定案。未默認改用新字型。
- 本批 GUI／IDA／原型容器均為有界 `--rm` 工作。GUI 輸出 UID/GID 為 1000:1000，`workspace/runs/` 無 root-owned 輸出。Windows Docker 建置仍進行中，完成後另核對清理。

## 2026-10-11：單幀收據、動態 HD 原型與原版音訊

對應 #4、#5、#17、#20、#21。知識路由命中 GUI、平台規格優先、規格閘門與文件職責；更新 README 前另讀首頁契約。所有新增文件與工具已掛入 `CONTEXT.md`。

- #21 修正收據驗證問題。先前 PNG、色號與 JSON 分別 rename，可能跨更新代擷取。現以單一原子 `capture.zip` 保存原版、色盤、狀態及 1280×800 呈現。獨立 `receipt-check` 驗證原版模式 33 份、HD 比較原型 35 份收據；逐像素核對原版 PNG、呈現雜湊、回退幀及地圖區外像素。只改 JSON 色盤的負對照在 `(0,0)` 被拒絕。GUI 腳本清理前次命名收據，避免主題不同的歷史產物混入新一輪。
- #5 動態 B 地景比較原型接入研究前端。435 格中 433 格覆繪、2 格回退，實際模態畫面、色盤失配、素材撤除及切回原版測試通過。F12 只作比較原型切換，沒有傳入 DOS。完整正常 GUI 經施工、切換、存退讀通過。HD 分支同幀封裝保存在 `workspace/runs/gui-hd-comparison/`，供後續原版模式重跑後仍能核對。只涵蓋水面、沙地與樹冠，不宣稱正式 HD 或全部建設素材完成。
- #20 固定官方 YMFM、BSD 授權及來源清單，通用串流保存於第六份 `dosgolem-audio.patch`，SHA-256 `089e143cf811636262ea902d868cd867c01f3ed83a85812443583f8cdaccd8ed`。隔離 dosgolem 提交 `2144a2a`，沒有改動或推送上游。節奏、PC 喇叭、批次連續、有界緩衝及狀態不變測試通過。實際 7214 筆事件兩種批次 PCM 相同；Linux AddressSanitizer、Windows Wine 純核心測試通過。
- Windows image 沿用既有 GUI base，補固定 MinGW C++ 版本。第一次使用字面 `FROM sha256` 被當成遠端名稱，改為核對 ID 的本機別名；建置器不接受 `--cpus`，改用其支援的建置入口。首次下載超過短逾時，加入 apt cache 並以有界建置完成。均屬工具鏈建置問題。image ID `sha256:80cda80f47353188794d030f468c37821d8e77a3a078e5b306f12cb0a0953c7d`，來源為受版控 Dockerfile。保留上游 MinGW 最佳化警告及實際適用範圍，不把編譯警告隱藏。沒有新增重複用途的 Linux 或 macOS image。
- #17 原版前端明示 AdLib 存在，`-mute` 只停主機裝置，仍合成並消費原版事件。實際播放器初次在未設定焦點時未持續取樣，環形緩衝溢位；聚焦後的同命令擷取通過。加入裝置就緒與完整批次容量檢查，保留已收輸入，暫停 VM 步進而不丟事件。刻意延後聚焦三秒的乾淨重跑通過，monitor 688984 frames、1236348 個非零聲道樣本、峰值 5584，拒收 0，正常關閉。技術擷取未當成人耳確認。
- 原版 EXE 相同初始狀態、850000001 步與原生鍵盤輸入，有／無消費音訊的完整 RAM、CPU、畫面、色盤、埠值、OPL 暫存器與讀鍵紀錄相同。狀態 SHA-256 `1dfdcc515013b62b02122dde8b00047752183a7526e6742efc9a95782a13ab57`，重生工具 `audio_state_audit.go`。
- 原版前端規格由研究證據審查升 READY，再重跑 `TAIPEI_THEME=original bash workspace/tools/gui_playtest.sh`。施工格讀回相同，存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，與 HD 分支相同。前端及音訊規格標 CONFORMED，限明列的原版玩家路徑與 Linux 音訊技術驗證；HD 原型仍 DRAFT，字型與正式切換待定。
- `build_preview.sh` 乾淨離線建置、鍵盤／HD 真實資源測試、dosgolem DOS／machine／audio／公開 API 測試通過。完整前端 Linux amd64、Windows amd64、macOS amd64／arm64 編譯通過，入口 `build_preview_cross.sh`。編譯不當作平台真機或正式封包驗收。
- 35 個原始輸入重新逐檔核對 SHA-256 不變。精確 `find workspace -user root -o -type d -name '*.md'` 無輸出，抽查新原始碼、補丁與 binary 均為 1000:1000。Wine `dosdevices/z:` 是同使用者建立、指向容器根的符號連結；不依跟隨連結的 stat 誤判，更未對其目標改權限。所有本批有界容器已退出並刪除，沒有殘留 Taipei 容器，其他專案未清理。

本批提交 `8137a65` 已推送。#4、#17、#20、#21 附提交、命令、證據與限制結案，主機 gh 回讀均為 CLOSED。#5 保留未完成的完整重繪清單與動畫限制，沒有以局部地景原型關閉整個來源研究。

## 2026-10-11：Windows 前端與 macOS 結構預檢

對應 #9 的隔離預檢，先回寫 Issue；正式封包仍須等待 #6、#7、#8。路由命中跨平台試玩，載入 `retro-game-playtest.md`。只使用既有 Wine image，沒有在主機執行 Windows 程式。

`bash workspace/tools/wine_preview_playtest.sh` 通過。由完整 Windows amd64 binary 冷啟動原版，真實按鍵經主選單、新城市與難度選擇至城市畫面，沒有機器快照。城市原版色號 SHA-256 `a838e6e26f6af4f62a2fc9a6c945e2671c2b5fa8194d80f01b028791a20fe000`，與 Linux 相同；再由研究停止請求正常關閉播放器與程式。這項只驗 Wine 冷啟動及輸入，不宣稱 Windows 真機、音訊裝置、存退讀或封包完成。

macOS 兩種架構以固定 otool 匯出系統函式庫與載入命令，入口收錄於 `build_preview_cross.sh`；未真機執行。Windows 靜態匯入表只見 KERNEL32.dll、msvcrt.dll，前端仍可能動態載入 Windows 系統 API，不以這張表宣稱完整裝置相容。

Wine 初始化出現缺少 syswow64 rundll32 的訊息，但 64-bit 前端與正常輸入實際通過，列為 Wine prefix 初始化噪音。工作容器已清理，輸出留在 `workspace/runs/wine-preview/`，原版資料仍唯讀。

## 2026-10-11：正常施工 HD 來源清單

先建立 [#22](https://github.com/wicanr2/taipei/issues/22)，再寫唯讀盤點工具及研究證據，均掛入 `CONTEXT.md`。九個已證實 9×9 圖庫共有 1134 筆來源、1049 個不同圖像；保留全部相同圖像別名及 ROM 檔案偏移，不依外觀猜建物語意。

原版 33 份與 HD 原型 35 份正常 GUI 單幀收據完成來源盤點，HD 的 35 份收據皆在原版抽樣找到相同畫面雜湊，來源映射一致，來源破壞負對照被拒絕。電線施工格唯一匹配成員 39、圖像 45，標頭檔案偏移 `0x8EA07`、色號 `0x8EA0B`；冷啟動讀檔後相同。目前 B 地景只接受成員 59，電線回退有可回查原因，不把沙地材質套到未知電線色號。

新研究文件 `docs/re/005-native-hd-sources.md` 說明目前覆繪分母、游標未知格及後續批次界線。原始畫面、逐格完整清單及圖塊仍只留本機。本項不擴張成全遊戲圖庫語意逆向，也不宣稱未抽樣的動畫、捲動或正式 HD 完成。
