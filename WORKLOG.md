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

上述 Windows／macOS 預檢及來源盤點提交 `3f5672c` 已推送，#22 附證據結案，主機 gh 回讀為 CLOSED；#9 已回寫實際 Wine 與結構檢查範圍，保持 OPEN。最早未決前沿仍為 #18 字型比較題，尚無使用者選擇；依已載入的 grilling 技能保留正式字型、HD 規格與封包相關分支。沒有把沉默當成同意。本輪結束無殘留 Taipei 容器，Git 僅保存原創程式、文件及保留授權的外部核心補丁。

## 2026-10-11：正常地圖捲動與世界材質相位

先建立 [#23](https://github.com/wicanr2/taipei/issues/23)，登記正常冷啟動、四向捲動、選單與切換，以及圖塊重疊、相異來源數與相符率門檻。路由命中 GUI 還原與文件職責；新增文件及工具皆掛入 `CONTEXT.md`。

24 份收據證實水平與垂直捲動，來源條件及回退像素正確，但六組位移中 2001 個相同世界地景格全部改變 HD 紋理。根因是材質依視窗座標取樣。先保留 `workspace/runs/hd-scroll-before-fix/`，再建立 [#24](https://github.com/wicanr2/taipei/issues/24) 追查原點並修原型。

載入 IDA 9.4 工具鏈入口，沿用已驗證 image 與唯讀 `.i64` 副本。保留原始函式名稱、IDA 線性位址、檔案偏移與 bytes。`sub_1850A` 寫入兩格原點增減，`sub_18594` 以原點及列寬索引原版地圖。EXE MZ 重定位表證實兩個原點段指標，沒有用程式碼位移猜資料位址。重生入口為 `bash workspace/tools/ida_camera_probe.sh`，證據見 `docs/re/006-map-origin.md`。

本作唯讀適配器留在 `workspace/app/internal/original`，不修改 dosgolem 通用層。只有原版完整地圖與游標重繪返回後才記錄原點；段指標失配、超界、未完成事件及捲動未完成均回退原版。HD 繪圖器僅接收分型座標，材質按世界位置取樣，超出既有素材時作鏡像延伸。`011-hd-world-origin-prototype.md` 保持 DRAFT，不把這項修正當成正式字型、操作或素材批次決定。

- `bash workspace/tools/hd_scroll_playtest.sh` 乾淨重跑通過。獨立核對六組原點差與原版圖塊位移相同，2001 個相同世界地景格逐像素相同，改變格數為 0。選單、取消及切換通過，置換圖塊的幾何負對照被拒絕。
- `presentation-audit` 重播同一正常 GUI 鍵盤收據，兩側各 1,608,000,000 步。只跑原版與加上原點觀察及 HD 繪圖，完整 RAM、CPU、色號、色盤、埠值、OPL 暫存器及讀鍵相同。狀態 SHA-256 `451e505444347378857bbaa785a24e7218a263e0d2fa2b806bdda7d244242f92`，1300 次重繪完成、1668 幀 HD 呈現。
- 真實 EXE 原點防護、實際城市素材／來源／色盤／未知原點回退，以及鏡像延伸邊界測試通過。第一次測試收據路徑拼錯，另一次含空白 Docker 掛載路徑漏引號；修正命令後在相同 image 乾淨重跑通過，均屬驗證環境問題。
- 修正後 `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 完成施工、切換、存退讀與兩次原版退出。讀回施工格相同，存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。
- `receipt-check` 通過 24 份捲動及 35 份施工存退讀單幀收據。`build_preview.sh` 離線重建及 Windows／macOS 兩架構重編譯通過。Windows 保留既有 YMFM 編譯警告，沒有新增真機試玩或封包完成聲明。
- 35 個原始檔與 RAR 重新核對 SHA-256 不變。文件相對連結、索引正對照、新輸出 1000:1000 擁有權與 `find workspace -user root -o -type d -name '*.md'` 檢查通過。本批一次性 Docker 工作均已退出並刪除，沒有殘留專案容器，也沒有新建或清理其他專案 image。

#18 字型比較題仍未收到選擇。正式 HD 與封包保留原有確認閘門；本輪只完成已授權、不依賴該決定的 DRAFT 地景修正。

上述捲動修正提交 `e1536d4` 已推送，#23、#24 附證據結案，主機 gh 回讀為 CLOSED。

## 2026-10-11：城市持續運行與年度預算回退

先建立 [#25](https://github.com/wicanr2/taipei/issues/25)，預登記正常冷啟動、原版速度操作、固定步數與人工日期辨識。路由命中 GUI 還原與文件職責，沿用既有工具鏈。核對 IDA 9.4 已有輸入匯出後，從實際視窗送原版鍵 `3`；前端沒有改寫速度、日期或規則。

第一輪 60 次抽樣捕捉兩次年度「預算配置」視窗，兩者 BIOS 非阻塞、頂部城市指紋仍相符。原型因此仍覆繪視窗外的 29 格地景，違反整幀回退契約。先保存 `workspace/runs/hd-runtime-before-guard/`，建立 [#26](https://github.com/wicanr2/taipei/issues/26)，再以實際標題色號修正可撤回原型，契約 `012-budget-window-prototype.md` 維持 DRAFT。

- `bash workspace/tools/hd_runtime_playtest.sh` 修正後乾淨重跑，60 份持續運行樣本皆相隔 24,000,000 虛擬步。日期裁圖人工確認 49 個連續月份，從 80 年 11 月至 84 年 11 月；沒有暫停、快照或狀態注入。
- GUI image 中的 `hd_runtime_check.py` 通過來源、原點、呈現雜湊與回退像素核對。58 份城市畫面均覆繪 433 格；兩次年度視窗整幀等於原版四倍，下一份城市收據恢復 HD。23,815 個來源及原點相同的地景格，HD 像素改變數為 0。
- `receipt-check -dir /workspace/runs/hd-runtime` 通過 65 份單幀封裝。共享核對器新增整幀回退驗證後，既有 24 份捲動收據重新核對通過，六組位移的 2001 個世界地景格仍逐像素相同。
- 兩份實際預算視窗的 Go 測試通過，原版色號未改寫；正常城市、素材撤除、來源與色盤失配、未知原點、鏡像邊界等既有測試通過。Linux 乾淨離線重建及 Windows、macOS 兩架構重編譯通過，Windows 保留既有 YMFM 編譯警告。
- `presentation-audit -require-budget` 重播正常 GUI 鍵盤收據，兩側各 2,400,000,000 步的原版 RAM、CPU、色號、色盤、埠值、OPL 暫存器及讀鍵相同。狀態 SHA-256 `b940de4f9be1b6b322152947e8c3d658c6add061d629368a9c00e3241d32e734`，實際包含 107 次年度視窗回退。
- 日期聯絡圖首次使用 ImageMagick montage，因容器字型快取初始化失敗而 SIGABRT。改用同一 image 的無文字像素拼接後乾淨重跑通過；此為圖表工具環境問題，沒有列為產品缺陷，也沒有因此重跑或挑選原版結果。
- 新證據 `docs/re/007-running-city.md` 與年度回退契約同步掛入 `CONTEXT.md`，驗收矩陣已更新。35 個原始檔與 RAR 的 SHA-256 不變；相對連結、索引正對照、輸出 1000:1000 擁有權及 `find workspace -user root -o -type d -name '*.md'` 檢查通過。一次性容器均已退出並刪除，未留下 Taipei 容器，未新增 image 或清理其他專案資源。

本批提交、推送與結案回讀保存於 #25、#26 的遠端留言。#5 保留完整來源與動畫研究限制。#18 字型比較仍未收到選擇；正式 HD、切換操作、後續素材與三平台封包維持原有閘門。本項未涵蓋發展後建物、所有未擷取相位或平台真機。

## 2026-10-11：使用者確認 Noto 高清黑體

使用者回覆「Noto 高清黑體」，解除先前字型決策阻塞。先核對主機 gh、遠端 #18、#6 與目前工作樹，再同步 `CONTEXT.md`、`AGENTS.md`。採用已展示的 Noto Sans CJK TC Regular Sans2.004，字型與 OFL 授權檔雜湊重新核對相符。

比較圖 `workspace/prototypes/hd-style/font-comparison/comparison-fonts.png` 的 SHA-256 為 `2ec3eea917c9dc173b31e30b5dbd9042f4ff4fca3f0f62a978281a3db5708c28`。因圖中包含原版畫面，保留本機固定參考及可重生腳本，不將其上傳 Git。六個主選單標題的原型已有 glyph、墨跡與安全矩形收據；本次字型定案不宣稱全遊戲文字已接入，也不代替正式切換與素材批次決策。

先建立 [#27](https://github.com/wicanr2/taipei/issues/27)，再接六個已辨識標題的動態繪字。路由命中 GUI 還原、文件職責與規格閘門，新增 `013-noto-menu-prototype.md` 並掛入 `CONTEXT.md`。採固定字型、授權、原版城市 UI 與文字色盤；字型初始化時驗 glyph 與墨跡，覆繪只寫前端 RGBA。模態與年度視窗仍整幀原版，字型失配只回退文字。

- 真實資源 Go 測試通過：六標題與已展示固定參考逐像素相同，字型撤除、字型／授權損壞與文字色盤失配負對照皆回退，既有地景與原點防護維持。
- `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 通過冷啟動、施工、存檔、原版退出、全新 EXE 讀檔與再次原版退出。施工格讀回相同，存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。覆字前 35 份封裝保留於 `gui-cold-before-noto/`。
- GUI image 內 `hd_font_check.py` 通過 35 份原子收據，11 份覆繪六個 Noto 標題、24 份原版回退；實際像素符合已展示樣式，矩形外與原生 F1–F6 保持原版。冷啟動讀檔後文字恢復。
- 舊 `receipt-check` 首次把合法 Noto 矩形視為地圖區外改動，屬於核對契約尚未更新。新增固定參考雜湊及文字矩形逐像素核對後，同一收據乾淨重跑通過。字型區與矩形間各破壞一像素、同步更新呈現雜湊的負對照均拒絕；沒有將整段 UI 列為免驗區。覆字前封裝也維持相容。
- `presentation-audit -require-budget -require-font` 通過兩側各 2,400,000,000 步的原版狀態比對，包含 3610 次 Noto 覆繪與 107 次年度回退，狀態 SHA-256 仍為 `b940de4f9be1b6b322152947e8c3d658c6add061d629368a9c00e3241d32e734`。
- Linux、Windows、macOS 兩架構研究前端重編譯通過；Windows 保留原有 YMFM 警告。正式封包與真機驗收仍未完成。

已提出下一項正式切換操作選擇：沿用原型 F12 即時切換或僅啟動時選主題，尚待使用者回覆。六個標題以外的文字與後續素材批次未定案；本項保持 DRAFT，不以局部覆字取代整體 HD 完成。提交與遠端回讀結果保存於 #18、#27、#6。

本批收尾核對：35 個原始檔與 RAR 的 SHA-256 不變，文件相對連結與索引正對照通過，新程式與輸出均為 1000:1000。`find workspace -user root -o -type d -name '*.md'` 無輸出，一次性容器均已退出並刪除，未留下 Taipei 容器，沒有新建 image 或清理其他專案資源。

## 2026-10-11：確認遊戲中 F12 切換

使用者回覆「允許在遊戲中切換」，採已提出的 F12 即時切換。先回讀主機 gh 與遠端 #6，載入規格閘門、共同決策與文件職責入口，再更新 `AGENTS.md`、`CONTEXT.md`、010、013 與驗收矩陣。新增 `014-live-theme-switch.md` 並同步加入文件索引；其 READY 範圍限前端操作，整體 HD 及正式接入沒有因此結案。

已審查研究前端的新按下事件與 DOS 按鍵表。既有正常 GUI 的 pause、theme-original、theme-hd 三份收據，其原版色號雜湊相同，六筆 DOS 讀鍵紀錄逐項相同。地景覆繪數為 433、0、433，Noto 標題數為 6、0、6。原版正常虛擬步數繼續前進，沒有重開或載入快照。施工存退讀與原版機器狀態證據沿用 #27；本次沒有改程式，也沒有重跑遊戲挑選結果。

F12 決策已回寫 [#6 留言](https://github.com/wicanr2/taipei/issues/6#issuecomment-6105506705)。已展示目前局部原型並提出完整 HD 與先交付局部版的範圍選擇，建議完整地圖建物、工具列與介面、選單及對話框文字、開場與動畫，沿用 B 風格與原版版面。這是待確認的交付範圍，不作已批准規格。

本批文件相對連結、013 索引正對照、014 新入口及檔案 1000:1000 擁有權通過。重新讀取三份既有 F12 收據，確認原版色號、DOS 讀鍵與覆繪數符合上述記錄。擁有權檢查首次跟隨 Wine 既有 `z:` 符號連結，將容器根目錄誤算為輸出；改用不跟隨連結的 `lstat` 與指定 `find` 後通過，未改動任何擁有權。`find workspace -user root -o -type d -name '*.md'` 無輸出，沒有殘留 Taipei 容器或新建 image。提交與推送結果回鏈 #6。

## 2026-10-11：全部圖片與操作介面定案，首批工具圖示接入

使用者明確指定「重繪範圍 所有的圖片 與操作界面」。沿用 B 細緻手繪材質、1280×800、Noto 高清黑體、F12 即時切換及三平台範圍。先回讀主機 gh 與遠端 Issues，更新 #6，再建立 [#28](https://github.com/wicanr2/taipei/issues/28) 至 [#32](https://github.com/wicanr2/taipei/issues/32) 的來源、介面、地圖、文字及場景批次，之後才開始研究與實作。範圍確認留言為 [#6](https://github.com/wicanr2/taipei/issues/6#issuecomment-6105585642)。沒有再等待相同決策。

路由命中復古重製規格閘門、文件職責、字模來源與驗證收尾；按需載入對應入口及技能 reference。建立 `015-full-hd-scope.md` 的 READY 範圍契約。新文件、工具與證據均掛入 `CONTEXT.md`，沒有另建本機 Issue 狀態鏡像或根目錄工作區。

- `full_asset_catalog.py` 完整列入兩份固定 ROM 的 118 個成員，解出 1317 筆圖片來源、1220 個不同尺寸及色號圖像。1287 筆原始圖像與 30 筆游程候選分別標示；25 個初盤待分類成員保留原始 bytes、定位與雜湊。`RS201A.ROM` 成員 10 的偏移表含別名，改以不同偏移的完整區段驗證，不以嚴格單調表排除有效圖片。原版說明視窗、評分底圖及城市工具列均找到完整色號來源；證據見 `docs/re/008-full-asset-inventory.md`。
- 先審查固定成員 1 的 320×200 解碼、工具列矩形及原版選取外框，再建立 `016-city-tool-icons.md` 的 READY 契約。使用內建 imagegen，參考原版十四圖示與已批准 B 比較圖，生成細緻手繪圖示。生成原圖、提示、來源及每格正規化資料保留本機；固定 320×320 atlas SHA-256 `9ad97735f45cab2c968e23d8f1d6924c6b1937854fa4cda1c1c7a5ee90a089ab`。原版及衍生素材未加入 Git。
- `icons.go` 僅寫前端 RGBA，每圖完整來源失配時獨立回退；缺素材、損壞與色盤失配有明確原因。最初全色盤條件擋住正常閃爍，來源審查證明變動的四色都未被圖示使用，故改驗所有圖示實際使用的 88 色。勘誤與固定雜湊寫入規格，沒有用單一收據特例放寬來源。
- 真實資源 Go 測試通過十四圖示、原版外框、單圖失配、素材／色盤回退與 F12 清除恢復；原版色號保持不變，既有地景、文字、模態及年度視窗測試通過。Linux、Windows、macOS 兩架構研究前端重編譯通過；Windows 保留既有 YMFM 警告，沒有新增真機或封包驗收聲明。
- `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 首次在第二次冷啟動觸及 300 秒外層上限，第一個原版程序已正常退出。保留 `workspace/runs/gui-icons-timeout/`，將有界上限改為 480 秒後，用同一 image 及相同輸入乾淨重跑通過。這是驗證器時間上限問題。正常新遊戲、電線施工、檔名退格、存檔、退出、全新 EXE 讀檔與再次原版退出皆通過；施工格冷讀相同，存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。
- `hd_icons_check.py` 從原版來源獨立重算遮罩並核對固定 atlas，35 份收據中有 11 份完整十四圖示、24 份回退；選取外框、冷讀恢復與 Noto 參考像素通過。`receipt-check` 同時核對固定文字與圖示參考，圖示外保持原版。刻意破壞文字、間隙、圖示及外框後同步更新呈現雜湊，四個負對照均被拒絕，結果保存於 `workspace/runs/icons-negative/result.json`。
- `presentation-audit -require-font -require-icons` 重播正常 GUI 輸入，兩側各 1,200,000,000 步的 RAM、CPU、原版畫面、色盤、埠值、OPL 與讀鍵相同；包含 716 幀完整圖示覆繪。狀態 SHA-256 `9a439a04692635051b9967b5e204f18073c87f1d16fe4d7495eba26c22898e68`。016 只在這批研究前端圖示內部達 CONFORMED，#29 及母項仍保持開啟。
- #31 的 `font_catalog.py` 取得成員 57 的 402 個 15×15 字模及成員 58 的原始兩 byte 字碼表。十二個主選單字與正常畫面逐點匹配，十二個單墨跡像素破壞負對照皆被拒絕。在十二類正常畫面找到更多候選，尚未把未審查字形或圖像候選直接接進呈現層。來源、稀有字碼與停止線見 `docs/re/009-chinese-font-sources.md`。
- 工具圖像聯絡圖第一次誤用 ImageMagick montage，再次遇到既有字型快取 SIGABRT；改用同一 image 的無文字像素拼接後通過。沒有因此改動遊戲、挑選原版結果或另建重複 image。

本批重新核對 35 個原始檔與 RAR，SHA-256 全部不變。224 個文件相對連結、新文件索引及 013 正對照通過。輸出與工作目錄均為 1000:1000，容器內 `find workspace -user root -o -type d -name '*.md'` 無輸出。一次性容器已退出並刪除，未殘留 Taipei 容器，沒有新建 image 或清理其他專案資源。

完整 HD 尚須其餘地圖、介面框架、文字、場景及動畫，三平台正式封包亦未建立。下一個文字切片由已取得字模追正常視窗的完整文字欄位、背景及清除條件，再建立 READY 契約。提交、推送與實際遠端進度回鏈 #28、#29、#31 及 #6。

## 2026-10-11：共用繪字呼叫端與已烘製文字的分界

前一批提交 `6aa7416` 已推送，主機 gh 回讀 #29 仍為 OPEN，遠端 repo 為 PRIVATE、Issues 啟用。繼續既有 #31 的文字來源範圍，沒有新增或猜補產品行為。

路由命中 IDA 9.4 與字模來源。載入 `use-ida-pro-9-4` 技能，再經 Codex 工具專案索引讀 `/home/anr2/ida_94_official/README.md`、`knowledge-base/ida-94-tools.md`。沿用本專案已驗證 image，原始 EXE 與正式 `.i64` 均唯讀；所有查詢只對新副本執行。新 `ida_text_probe.py` 與 `text-source-audit` 同次掛入 `CONTEXT.md`。

- 靜態確認 `sub_13274` 的六標題迴圈及 `sub_143DA` 的雙 byte 字碼查表、30-byte 字模步距與中文 16 像素字距。立即數位移候選只作定位線索，完整資料流審查後才標示語意。`sub_15A99` 實際只繪 15×14 墨跡，沒有把字模標頭 15×15 直接當成所有繪製高度。
- `text-source-audit` 重播既有正常輸入，記錄六筆文字與十二個中文字模。原始 ROM 字模、字碼、座標、色號、背景及正常城市畫面逐點相符；十二個單點破壞負對照不符合原版輸出。1,200,000,000 步後完整狀態 SHA-256 仍為 `9a439a04692635051b9967b5e204f18073c87f1d16fe4d7495eba26c22898e68`，與無文字觀察基線相同。
- 初次 IDA 匯出使用 image 預設 ASCII 編碼寫中文 JSON，產生 UnicodeEncodeError。補上明確 UTF-8，從原始唯讀資料庫重建副本，在同一 image 乾淨重跑，schema、版本、固定輸入雜湊及輸出擁有權均通過。分類為證據匯出工具問題。
- 共用函式在本條正常路徑只畫六標題，說明視窗的其他字已烘在成員 22 圖片中，部分字不在 402 字子集。據此保留動態文字與圖片內文字兩種來源證據，沒有將只換字庫當成全遊戲文字完成。原函式名、位址基準與限制追加於 `docs/re/009-chinese-font-sources.md`。

本切片只新增唯讀研究工具，未接入產品文字或改變遊戲。下一批繼續由 #31 的正常視窗來源建立 READY 覆字契約，完整範圍及三平台交付仍在進行。提交與遠端證據回鏈 #31。

最終建置及正常重播乾淨重跑通過，十二字來源、畫面與既有狀態再次相符。35 個原始檔與 RAR 雜湊不變，229 個文件相對連結、索引正對照及新程式與輸出 1000:1000 擁有權通過。容器內指定 `find` 無輸出，所有本批 Taipei 容器已退出並刪除，沒有新增 image 或清理其他專案資源。

## 2026-10-11：完整新遊戲說明視窗接入

依使用者「ok 繼續」接續 [#31](https://github.com/wicanr2/taipei/issues/31)，先回讀主機 gh 與遠端現況，並以[開工留言](https://github.com/wicanr2/taipei/issues/31#issuecomment-6106095044) 登記本批與驗證。路由命中規格閘門、文件職責、README 現況及 imagegen，載入對應契約。沿用已確認 B、1280×800、Noto 與 F12，不重開美術訪談。

- 審查成員 22 的完整 236×132 來源、正常 GUI 位置、使用中色盤、七行文字及字模正對照。先建立 `017-new-game-dialog.md` 的 READY 契約，再寫程式。原文資料保留本機；62 字原位墨跡與共用字模相同，其他字與兩處形狀不同的標點人工核對，不用未審查 OCR 猜補。
- 內建 imagegen 依原版面板與 B 比較圖生成空白銀框藍底，再由實際 Noto 繪原文。完整背景、轉錄、提示、生成原圖、固定參考及來源雜湊都留在 `workspace/prototypes/hd-style/`，未加入 Git。`dialog.go` 用完整來源及六個使用中色盤項目辨識，只改 944×528 面板；不依賴城市地景條件，不改 DOS 輸入或資料。
- 真實資料 Go 測試通過來源、色盤、模式、未使用色盤、F12、關窗，以及素材、文字、字型與授權撤除／損壞的完整回退。實際 Noto 92 字元沒有缺字或裁切，完整參考人工核對後固定雜湊。Linux、Windows、macOS 兩架構研究前端重編譯通過；Windows 保留既有 YMFM 警告。
- 首次 GUI 開場超過單次 120 秒等待上限，最後為 432M 步，尚未進入說明視窗；空讀鍵紀錄使診斷再出 TypeError。先建立 [#33](https://github.com/wicanr2/taipei/issues/33)，只修正空紀錄處理，容器內模擬逾時保留真正 RuntimeError 與步數。證據保留 `workspace/runs/gui-dialog-timeout/`。其他本輪工作結束後，同 image、同命令及原有時間門檻乾淨重跑通過，沒有修改遊戲或放寬門檻。
- 正常 GUI 新遊戲說明的 HD → 原版 → HD 三份收據具有相同原版色號與讀鍵；關窗、難度、城市、電線施工、檔名退格、存檔、原版退出、全新 EXE 冷讀與再次退出通過。37 份收據的完整面板、區外、六標題與十四圖示均通過獨立核對。五個修改字形、邊框、區外、原始來源及色盤的負對照，在同步更新相應雜湊後仍被拒絕。
- 重播覆繪前保存的正常 GUI 輸入，兩側各 1,224,000,000 步的完整 RAM、CPU、原版畫面、色盤、埠值、OPL 與讀鍵相同，包含 55 幀說明覆繪。狀態 SHA-256 `670f2fea2db251b7d694cf1e12d4254110669e09f80179d82865ec786937062e`。結果與輸入收據雜湊保存於 `dialog-state-audit.json`、`dialog-state-provenance.json`。施工格冷讀相同，存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。

本批 017 限該視窗達 CONFORMED。完整 HD 的其餘圖片、介面與三平台正式封包尚未完成，#31 與母項保持開啟。新文件與程式同次掛入 CONTEXT，README 只改穩定現況摘要。35 個原始檔與 RAR 雜湊不變，修改文件連結及索引正對照通過。新程式、素材與四個平台 binary 均為 1000:1000；容器內指定 `find` 無輸出，所有本批容器已退出並刪除，沒有新建 image 或清理其他專案資源。程式與文件明確列檔提交，提交與推送結果回鏈 #31、#33。

## 2026-10-11：三種啟動選單與十三種選取狀態

接續 [#31 的預登記](https://github.com/wicanr2/taipei/issues/31#issuecomment-6106322752)，主機 gh 回讀 OPEN。路由命中復古重製、規格閘門、文件職責及 README 現況，載入對應入口。原版控制、B、Noto、1280×800 與 F12 均沿已確認決策，沒有新增產品取捨。

- 從正常冷啟動走主選單三項、城市七項、難度三項，取得 ROM20／21／17 的完整來源與色盤。43 個操作字的完整 15×14 原版墨跡相符，30 個單點來源負對照被拒絕。城市左右鍵不改選取、上下鍵依左欄後右欄移動；難度 Escape 不改畫面，沒有猜補返回功能。來源收據保留於 `workspace/runs/startup-menus-native/`。
- 內建 imagegen 生成空白木板及兩種按鈕，沿用 017 銀框藍底。初版木紋過於粗糙，改用細緻連續紋理 v2；按鈕空白外緣依記錄裁切正規化。原圖、四份來源參考、提示、原文、幾何、雜湊與十三張面板均只留本機 `workspace/prototypes/hd-style/`。生成紀錄為 `startup-menu-generation.json`。
- 先寫 018 DRAFT，審查十三種正常來源與三張完整離線面板後升 READY，再接入 `panels.go`。固定 manifest、完整原版矩形、使用中色盤、Noto、授權與每張 PNG 全部通過才覆繪。失配完整回退，單張素材缺失不影響其他已驗面板；每幀原版重建後只改該矩形。
- 離線工具逐字掃描 240 個實際墨跡，全部落在安全矩形，與字型邊界共同驗證，沒有依靠裁切掩蓋越界。重生的十三張 PNG 與 manifest 雜湊不變。原版標題四字依原墨跡矩形縮放，操作字為 56 px，原位及反白顏色不變。
- 真實資源 Go 測試驗十三種完整面板、區外、來源／色盤／模式失配、F12、manifest／素材／字型／授權撤除及損壞，全部通過。第一次 Docker mount 參數未引用含空白路徑，在啟動容器前被拒絕；補引用後以同 image 乾淨重跑通過，分類為命令問題。
- `TAIPEI_THEME=hd-b bash workspace/tools/startup_menu_playtest.sh` 正常走完選項、三種選單 F12、無效鍵、難度 Escape 與進入城市。40 份收據由 Python 與獨立 Go 核對器重算來源、選取、固定面板及全部區外。六種字形、邊框、區外、來源、色盤與選取竄改，在更新受影響雜湊後仍被拒絕。探索工具最後採有界停止，不代替退出驗收。
- `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 再走完整施工、存退讀與兩次原版退出。37 份收據包含五份本批選單、兩份說明、十一份城市與十九份原版回退；完整面板、六標題、十四圖示與區外獨立核對通過。施工格冷讀相同，存檔 SHA-256 保持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。前一次證據保留於 `gui-cold-before-startup-panels/`。
- `presentation-audit -require-panels -require-dialog -require-font -require-icons` 重播 `startup-menus/city-scroll-down-capture.zip`，兩側各 1,776,000,000 步的 RAM、CPU、原版色號、色盤、埠值、OPL 與讀鍵完全相同。實際包含十三種選單共 2,165 幀、55 幀說明、176 幀城市；狀態 SHA-256 `2aaad1136e232faa521d778894871e5ae3c31199c582ed12455cb550ade0bacb`。結果、固定輸入及工具來源雜湊見 `panels-state-audit.json`、`panels-state-provenance.txt`。
- `build_preview.sh` 及 `build_preview_cross.sh windows|macos` 完成 Linux amd64、Windows amd64、macOS amd64／arm64 編譯；Windows 保留既有 YMFM 編譯警告。沒有新增平台真機、音訊或正式封包驗收聲明。

018 限上述範圍達 CONFORMED。#31、#7 與完整 HD 母項保持開啟；七座城市各自開局、災難分支、其他圖片及介面仍需後續批次。35 個原始檔與 RAR 雜湊不變，新檔入口、相對連結與 1000:1000 擁有權通過。容器內指定 `find` 無輸出，所有本批容器已退出並刪除，沒有新建 image 或清理其他專案資源。程式與文件依明確清單提交、推送，實際提交回鏈 #31 及 #7。

## 2026-10-11：城市框架、F 鍵與十四工具外框

接續 [#29 的預登記](https://github.com/wicanr2/taipei/issues/29#issuecomment-6106670436)。主機 gh auth 與遠端 Issue 回讀成功，沿用使用者已定 B、1280×800、Noto、F12 及原版版面。路由命中復古重製、規格閘門、正常玩家路徑、文件職責與 imagegen，載入相應入口；沒有新增產品取捨。

- 固定 ROM1 底圖與 66 份正常城市來源比較，確認六部分框架及動態排除範圍。正常 61 份來源走十四工具三種完整外框，共 42 種；工具 2、5、9、10、11 先開原版子選單。底部日期、資金及費用保持原版，後續依 #31 追文字來源。
- 新證據推翻 016 左欄等距公式。實際外框 x=273／296，內部 x=274／297；舊左欄圖示包含一列外框，選取後會失配回退。另確認 Tab 回到已選工具仍為 32，移到其他工具才為 186。先保留 `city-chrome-initial-source/` 與 `city-chrome-submenu-source/`，再訂正來源、規格及定位。工具 5 的第一次 Space 是開子選單，沒有改寫成確認失敗或猜測費用規則。
- 內建 imagegen 依原版與 B 素材生成銀灰板、淺綠板與透明柱飾。依 alpha 包圍盒做柱飾幾何裁切與縮放，提示、原始輸出、全部來源及雜湊保存在本機 `city-chrome-generation.json`。離線 `chrome-prototype` 組合原位框架，六個 F 鍵實際 Noto 墨跡通過安全矩形檢查，中文標題保留 013 固定像素。PNG、字型及生成素材均未加入 Git。
- 019 先 DRAFT，來源與完整離線參考審查後升 READY，再實作 `chrome.go`。六部分來源與使用中色盤各自完整匹配；十四外框驗完整 22×22 來源及 84 個同色邊界點。未知或失配獨立回退，模態及年度視窗整幀回退，每幀從原版重建。快取 RGBA 後直接複製已核對像素，完整參考重生雜湊不變。
- 真實資源 Go 測試通過全部 42 種來源、子選單、來源／色盤／素材／形狀／字型／授權失配及既有功能。既有字型測試人工替換單一 renderer 層，未同步替換框架中的已載入字型；修為單項測試隔離，新框架另驗真正缺檔及失配。獨立核對器第一次把已驗證完整面板再次當成原版框架，補齊責任分派後乾淨重跑。兩者均屬驗證工具問題。
- 最終 binary 再跑 `TAIPEI_THEME=hd-b bash workspace/tools/city_chrome_playtest.sh`。63 份收據包含十四工具三種來源、五個子選單回退、確認、Tab 取消、F2 與 F12；`program-provenance.txt` 固定實際執行檔及工具。`hd_chrome_check.py --require-all-tools` 重算全部來源與固定參考，Go `receipt-check -chrome-reference` 驗逐像素與區外，全部通過。該探索末尾採有界停止，沒有冒充原版退出。
- 最終 binary 另走完整施工、存退讀及兩次原版退出。37 份收據的 Go、框架、Noto、圖示及區外核對通過，冷讀施工格相同，存檔 SHA-256 維持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。前次保留於 `gui-cold-before-chrome/`。本批兩條正常 GUI 共 100 份收據。
- 八個有效負對照包含框架、F 鍵、外框、動態欄位、來源、色盤與兩種偽造遮罩，受影響雜湊與原版 PNG 同步保持一致，仍被來源或像素核對器拒絕。結果逐項區分責任，來源／色盤由 Python、動態欄位由 Go 全區外核對，不將其中一方未驗的項目稱為通過。
- `presentation-audit -require-chrome -require-dialog -require-font -require-icons` 使用保留的唯一正常輸入 `city-chrome-before-cache/theme-hd-capture.zip`。有／無呈現兩側各 2,304,000,000 步，RAM、CPU、原版畫面、色盤、埠、OPL、讀鍵與檔案操作完全相同，包含 3,113 幀完整框架及 65 幀說明。狀態 SHA-256 `60b1cc6b5b29372caebb3a19eec50f96a3c86371908c7781402872e6e0a5f649`，固定輸入、程式及工具鏈見 `chrome-state-provenance.json`。不外推不同亂數實作或逐骰規則對拍。
- Linux amd64、Windows amd64、macOS amd64／arm64 編譯通過，Windows 只有既有 YMFM 警告。沒有新增真機、音訊或正式封包完成聲明。

019 限六部分與十四外框達 CONFORMED。#29、#7 及完整 HD 母項保持開啟；其餘圖片、子選單、動態文字、場景、動畫與正式封包繼續依原範圍處理。35 個原始檔及 RAR 雜湊不變，文件入口與相對連結檢查通過。新檔、素材及四平台 binary 為 1000:1000，容器內指定 `find` 無輸出，本批容器均已退出並刪除。沒有新建 image、改動 dosgolem 上游或清理其他專案資源。程式與文件按明確清單提交並推送，實際提交回鏈 #29 與 #7。

## 2026-10-11：底部費用、年月與資金高清化

接續 [#31 的預登記](https://github.com/wicanr2/taipei/issues/31#issuecomment-6107137732)。本輪先回讀現況與遠端 OPEN Issue，路由命中重製技能、規格閘門、字模索引還原、文件職責；GUI 漏鍵追查另載入正常玩家試玩入口，README 現況修正依專用入口。沿既有 B、Noto、1280×800、F12 及原版版面，不重開決策。

- 以 ROM1 完整底圖、成員 56 數字與成員 57／58 索引 107–110 重建兩個完整原生矩形，68 份來源與 408 個單點負對照通過。「每單位／萬」的 15×14 墨跡及 5×7 數字均有正常像素證據；沒有把舊路徑未呼叫的 ASCII 函式改寫成已追蹤。補充證據回鏈 RE009 與 020，原位、原始定位與推論界線保留。
- 020 先 DRAFT，完成原始來源、完整欄位與字形審查後進 READY，再實作 `footer.go`。固定 B 框架取相同座標作底板，Noto 十八字形生成透明 atlas，數字 28 點、費用中文字 52 點、右欄單位 28 點；所有實際 alpha 墨跡落在安全矩形，重生 PNG 與 manifest 雜湊不變。原圖與 atlas 僅留本機。右下語意未確認的原符號保留原始四倍像素。
- 正式辨識先從 ROM 重建背景及實際原版字模，完整矩形 bytes、使用中色盤、字型／授權、固定參考都符合才逐欄覆繪。來源或素材失配整欄回退，每幀先恢復原版，再畫目前字串。真實資源 Go 測試包含正常來源、分欄色盤及來源破壞、五項素材缺失／竄改、縮短數字背景恢復，全部通過。
- `TAIPEI_THEME=hd-b TAIPEI_CHROME_RUN=footer-gui TAIPEI_FOOTER_TIME=1 bash workspace/tools/city_chrome_playtest.sh` 取得 66 份正常收據，涵蓋十四工具、42 種外框、五個子選單回退、F2／取消／F12 及原版速度鍵 `3`。費用含最長實際六位 100000，80 年 9 月正常推進至 10 月。`program-provenance.txt` 固定實際 Linux binary SHA-256 `9c2f97887f5ea4089447ae25af7acfd09dd3a80a2aa340a1be287e5cc8293977`。
- 完整施工腳本初次固定 wall-clock 連發少送兩次 Right，原版施工與扣款已發生，但落在 (212,43)，未達預定 (230,43)。失敗收據保留 `gui-cold-footer-missed-input/`，先開 [#34](https://github.com/wicanr2/taipei/issues/34) 再修工具。25 次移動改為各自等原版讀鍵及前端 release 的原子收據，沒有注入游標、放寬位置或改遊戲程式。`movement-sync.json` 保存每次 press／release 步數及讀鍵計數；同 image／命令乾淨重跑通過。
- 最終正常施工、原版存檔、兩次原版退出及全新啟動讀檔取得 37 份收據，冷讀施工格與資金 79980 相符。存檔 SHA-256 保持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，施工格保持 `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139`。原來源保留 `gui-cold-before-footer/`。
- 103 份正常收據由 Python 重算來源、字串與色盤，Go 另依固定 atlas／背景核對完整像素與區外。首次獨立核對把已驗主選單覆蓋的底部座標當成原版欄位，修正面板責任分派後乾淨重跑，屬核對工具問題。八個重算雜湊及原版 PNG 的有效負對照被拒絕；來源／色盤由底部核對器直接拒絕，不借其他框架失配代替。Go 不重算這兩種來源，結果明列互補責任。
- `presentation-audit -require-footer -require-chrome -require-dialog -require-font -require-icons` 重播唯一正常輸入 `footer-gui/pause-after-time-capture.zip`。兩側各 2,352,000,000 步，包含 3,236 幀兩欄覆繪，RAM、CPU、原版畫面、色盤、埠、OPL、讀鍵及檔案操作一致。狀態 SHA-256 `93808909ec3603a2b2e933e1af782c28178f9f27663ad0842f103be6b2707daa`，輸入與工具來源保存在 `footer-state-provenance.json`。不外推不同亂數實作或未驗規則。
- Linux amd64、Windows amd64、macOS amd64／arm64 編譯通過，Windows 保留既有 YMFM 警告。沒有新增真機、音訊或正式封包完成聲明。35 個來源檔與 RAR 雜湊不變；156 個文件相對連結、八個新入口的正對照索引及抽查 1000:1000 擁有權通過，容器內指定 `find` 無異常。

020 限費用、年月與資金達 CONFORMED，#31、#7 及完整 HD 母項保持開啟。右下原符號、負資金、超出辨識槽、其他子選單／視窗／圖表、圖片／動畫與正式封包繼續依原範圍處理。本批容器全部退出並刪除，沒有新建 image、改動 dosgolem 上游或清理其他專案資源。程式與文件按明確清單提交推送，結果回鏈 #31、#7、#34。

## 2026-10-11：五工具子選單與十八種選取狀態

接續 [#31 的預登記](https://github.com/wicanr2/taipei/issues/31#issuecomment-6107377718)。主機 gh auth、PRIVATE、Issues 與遠端狀態回讀成功。路由命中復古重製、規格閘門、文件職責與 README 現況；驗證逾時另載入正常玩家試玩及驗證交接入口。沿用 B、Noto、1280×800、F12 與原版版面。

- 正常冷啟動取得五工具的 101 份來源收據。初次探索誤設大型選單為左右欄控制，原版實際上下鍵依左欄後右欄循環，左右鍵及 Escape 保持畫面與阻塞；補跑完整十個選取後，以完整矩形、ROM19 底圖、ROM57／58 字模及字碼重建十八種來源，186 個單點來源破壞均不符原狀態。這是原版控制證據，未改寫遊戲操作。
- 021 先 DRAFT，十八來源、原文與空白字距、離線面板及 462 項 Noto 實際墨跡審查後進 READY，再接入產品。使用既有 B 藍板及綠板，沒有生成新素材。十八張 PNG、manifest 與墨跡報告共二十檔，獨立乾淨重生逐檔相同；來源、原文、字型及素材只留本機。
- `panels.go` 共用固定完整面板載入，但啟動十三狀態與工具十八狀態各自驗 manifest。每幀先恢復原版，只覆繪通過完整來源、色盤、字型、授權及 PNG 雜湊的矩形。模態外保持原版四倍像素，未宣稱底下城市亦 HD；單張素材故障不影響其餘面板。
- 真實資源 HD Go 測試全部通過，25.360 秒，沒有跳過。新測試涵蓋十八狀態、完整面板與區外、來源／色盤／模式／主題、四項資源缺失與損壞。舊框架測試預期五子選單均回退，現改驗五個已接入 ID、保留未知視窗完整回退及 42 種外框斷言。
- 初次原生探索期間修改外層腳本，已完成收據後出現 shell 變數未定義；保留完整探索收據並修正腳本，再以固定版本跑補充原生及 HD 探索，兩者均正常結束。沒有用此錯誤判定產品失敗。後續不修改執行中的腳本。
- `TAIPEI_THEME=hd-b TAIPEI_SUBMENU_RUN=tool-submenus-hd bash workspace/tools/tool_submenu_playtest.sh` 正常走五工具、十八選取、原版循環、左右／Escape、確認返回、Tab 及五場景 F12。82 份收據通過 Python 完整來源／色盤及 Go 固定面板／區外核對。大小兩種面板各七項有效負對照共十四項，同步重算雜湊與原版 PNG 後，Python 與 Go 均拒絕文字、背景、區外、來源、色盤、選取及 ID 竄改。
- 完整存退讀腳本首次到達第二次原版退出確認時碰到外層 480 秒上限，收據保留 `gui-cold-tool-panels-timeout/`。先開 [#35](https://github.com/wicanr2/taipei/issues/35)，只改外層為 600 秒，同 binary、image、步數、操作與斷言乾淨重跑。正常完成兩次原版退出，從 Xvfb log 至結果檔時間約 424.91 秒；此粗估及不同排程不證明產品效能改善。
- 最終 `gui-cold/` 的 37 份收據通過完整面板、框架、底部與區外核對；六標題及十四圖示的專用檢查亦通過，施工格與資金冷讀相同。存檔 SHA-256 維持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。將要求冷讀收據的字型檢查誤用於 82 份子選單探索時曾缺必要輸入，改用完整 37 份存退讀集，沒有放寬斷言。前批 020 完整收據保留於 `gui-cold-before-tools/` 並修正索引。
- 狀態稽核原每 400,000 步重繪，完整 40.8 億步預計 10,200 次，碰到 480 秒上限，未取得比較結果。先開 [#36](https://github.com/wicanr2/taipei/issues/36)，只在驗證 CLI 加明示間距、實際抽樣數與十億步階段進度；舊預設不變。本批預登記每 24,000,000 步抽樣，上限 900 秒，保留兩側全部原版步數、輸入及原點觀察，仍要求全部十八工具狀態及既有呈現層。原來源保存在 `tool-panels-state-provenance-before-sampling.json`。
- Linux amd64、Windows amd64、macOS amd64／arm64 編譯通過；Windows 只有既有 YMFM 警告。調整驗證工具後沒有重建或改變產品 binary，未增加平台真機、音訊或正式封包完成聲明。
- 最終明示抽樣狀態稽核退出 0。相同唯一輸入兩側各 4,080,000,000 步，原版側 214.806 秒、HD 側 220.093 秒，170 次抽樣覆蓋全部十八工具狀態共 99 次、說明一次及城市各層 33 次。RAM、CPU、原版色號、色盤、埠、OPL、讀鍵與檔案操作相同，狀態 SHA-256 `53700f59970623a9e83a648b7b4b1eeb080126c6d8b45eccff7e0df4cf9394a1`。結果、間距、時間、完整命令與來源保存在 `tool-panels-state-audit.json`、`tool-panels-state-provenance.json`；未宣稱逐幀或全部規則對拍。

021 限五工具十八狀態達 CONFORMED，#31、#7 及完整 HD 母項保持開啟。35 個原始檔及 RAR 雜湊不變，四平台產品 SHA-256 與架構一致；178 個相對連結、八個新入口及正對照索引、shell 語法、Go 格式及抽查 1000:1000 擁有權通過。最後檢查初次僅計頂層收據，漏讀 `reload/`；改為遞迴讀取後仍要求原定 37 份，乾淨重跑通過。容器內指定 `find` 無輸出，本批容器全部退出並刪除，沒有新建 image、改動 dosgolem 上游或清理其他專案資源。結果保存 `tool-panels-input-hygiene.json`、`tool-panels-final-hygiene.json`。程式與文件按明確清單提交推送，實際提交回鏈 #31、#7、#35、#36。其他視窗、圖表、圖片、場景、動畫及三平台正式封包仍未完成。

## 2026-10-11：城市六功能選單來源與 Noto 原型

上一輪已推送五工具批次，判定為進展。本輪回讀 Git、主機 gh auth、目前狀態與遠端 Issue，先建立 [#37](https://github.com/wicanr2/taipei/issues/37) 再開工。路由命中復古重製、規格閘門、文件職責及驗證交接，載入現行入口。沿用 B、Noto、1280×800、F12 及原版版面，沒有新增產品取捨。

- 以 `city_menu_playtest.sh` 正常冷啟動六次，逐一進城市，以原版速度 0 暫停後探索 F1–F6。方向鍵及功能鍵逐次等原版讀鍵與 release，不注入狀態、游標、存檔或鍵盤佇列。證實六入口均為下拉選單，選取數為 1／4／3／6／10／5，共二十九種。上下循環，左右切相鄰選單且重設選取為 0，兩端亦循環；Escape 關閉並還原原城市。這些控制與五工具子選單不同，沒有沿用其 Escape 忽略行為。
- 原六次冷啟動批次在 F6 第一個 Up 讀鍵後碰到既定 900 秒上限，以 124 結束；F1–F5 完整結果及 F6 五種 Down 來源保留 `city-menus-native/`。先回寫 #37，再以同 image、binary、操作與斷言，僅補跑 F6 至 `city-menus-native-extra/`，退出 0。沒有提高上限或覆寫前件，來源 catalog 明列兩根及收據路徑；完整控制核對只使用有完整結果的六條路徑。
- 137 份正常原子收據由 Go 單幀核對器驗原版 PNG、色號、色盤與四倍呈現，原批 116、補充 21 全部通過。原始 ROM56／57／58 的字模與字碼重讀，完整交錯邊框、色號 3 背景及全部選取逐 byte 重建相同，246 個來源單點破壞不符。ASCII DOS 原位與 5×7 字模亦相同；沒有用可見字形推定 EXE 繪字呼叫。
- 災難選單有十列，完整矩形為 (185,35,68,154)，會延伸至底部欄位；來源探索涵蓋全 320×200 畫布，沒有按城市 viewport 裁掉底端。所有中文候選均有完整原墨跡及原字碼證據，沒有歧義別名。原文與 layout 只留本機。
- 新增獨立 `city_menu_source_check.py`，固定來源 SHA-256，驗二十九選取、上下循環、左右跨選單及循環邊界、六次 Escape 完整恢復原地圖，並由收據核對八十二次讀鍵與 release。來源重建與控制核對分開，沒有只依腳本完成訊號宣稱通過。
- 022 先 DRAFT。離線工具新增 `-family city -state-count 29`，沿用既有 B 藍板，Noto 中文 52 點、DOS 英文 28 點。599 項實際墨跡位於安全矩形，各墨跡矩形互不重疊。視覺檢查混合字型、十列最長面板及四字選項後，二十九 PNG、manifest 與報告共三十一檔乾淨重生逐 byte 相同。既有五工具二十檔以同工具重生也完全相同，manifest 雜湊不變。
- 原版來源、原文字碼、完整面板與實際墨跡審查後，022 限本批面板升 READY。固定來源、layout、manifest、字型及授權雜湊寫入規格；原文字形定位、工具原始碼、產品及原型 binary、全部收據、輸出及六補丁雜湊保存 `workspace/runs/city-menu-source/provenance.json`。本批沒有改產品 renderer 或核心規則，Linux 產品 SHA-256 仍為 `3da5383d931fccc7e34fa9588ed3e8fe11cc6fc5e132f6a6d7688bd198aec13a`。

正式接入的下一步是以固定 manifest `699c3ed0baed752327667f3d50cc9b0ee45b0124407338eb4f41be94d6239fc5` 建立獨立二十九狀態集，於阻塞輸入回退前辨識，再驗全部正常 HD、F12、有效負對照、存退讀及兩側原版狀態。尚未達 CONFORMED，沒有重跑或宣稱本批跨平台、音訊或正式封包驗收；#37、#31、#7 與完整 HD 母項保持開啟。

35 個原始檔及 RAR 雜湊不變，Git 核對產品呈現與核心原始碼沒有差異。178 個文件相對連結、五個新入口與正對照索引、Python／shell 語法、Go 格式、137 份收據的 24,000,000 步對齊及抽查 1000:1000 擁有權通過，結果為 `workspace/runs/city-menu-source/final-hygiene.json`。容器內指定 `find` 無輸出，所有本批容器已退出並刪除；沒有新建 image、改動 dosgolem 上游或清理其他專案資源。只明列程式、腳本與文件提交推送，原版及衍生資料未上傳，實際提交與階段結果回鏈 #37、#31。

## 2026-10-11：六功能二十九選取接入與正常驗證

依 [#37](https://github.com/wicanr2/taipei/issues/37) 與 READY 022 實作。路由命中規格閘門、文件職責、驗證交接及 README 現況，載入對應入口與必要 reference。沿用使用者已確認的 B、Noto、1280×800、F12、原版版面與六入口操作，沒有改原版 EXE、規則或存檔。

- 呈現層新增固定 `city-menus-v1` 二十九狀態集，保留啟動、說明、五工具及城市的辨識順序。完整來源、使用中色盤、manifest、字型／授權及 PNG 均須匹配；單張故障只回退該面板，模態外維持原版四倍像素。
- Go 實際資源測試共用完整來源與區外斷言，保留五工具十八狀態，加入城市二十九狀態。初跑 21.489 秒僅因既有 `file-menu` 仍要求原版回退而失敗，原 log 保存 `city-panels-go-tests-before-fixture-update.log`；依 022 更新為 F2 面板正對照後，全套 21.819 秒通過且沒有 SKIP。未知存檔／退出確認與年度預算的整幀回退仍驗證，沒有放寬斷言。
- `TAIPEI_THEME=hd-b TAIPEI_CITY_MENU_RUN=city-menus-hd bash workspace/tools/city_menu_playtest.sh` 從一次真實冷啟動進城市，完成六選單二十九選取、八十二次原版讀鍵／release、上下循環、左右跨選單與兩端循環、六次 Escape 復原，以及六場景 F12 往返。沒有狀態注入；探索末尾有界停止仍不當作原版退出。107 份原子收據的完整來源、固定面板及所有區外由 Python／Go 獨立核對通過，實際十列災難面板已視覺確認沒有裁切。
- 保留前批 37 份完整收據於 `gui-cold-before-city-menus/`，修正 021 證據入口，再以 `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh` 重跑。施工、存檔、兩次原版退出及全新 EXE 讀回原施工格通過，最新 37 份原子收據完整像素通過。存檔 SHA-256 維持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，存檔目錄為 `gui-cold-saves.zRF8kg/`，施工格 SHA-256 維持 `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139`。專用標題／圖示核對亦證明冷讀後恢復。
- F1 小面板與 F5 十列面板各驗文字、背景、區外、來源、色盤、選取與 ID，重算受影響雜湊與原版 PNG，十四項有效負對照均被 Python／Go 拒絕。擴充負對照工具的 `--family city` 後，預設五工具入口另以原工具 02 的七項竄改回歸通過。
- Linux、Windows、macOS amd64／arm64 以既有固定 image 與鎖定依賴編譯通過，Windows 保留既有 YMFM 編譯警告，沒有新增平台真機或音訊確認聲明。重播及單幀工具加入城市參考與二十九狀態要求；整批核對入口為 `bash workspace/tools/city_panels_verify.sh`，狀態重播仍在進行。

狀態重播最終退出 0。相同唯一正常輸入兩側各 5,184,000,000 步，原版側 398.045 秒、HD 側 351.661 秒。216 次預登記的 24,000,000 步 HD 抽樣涵蓋全部二十九城市選取共 164 次、說明一次、城市各層 14 次；RAM、CPU、原版色號、色盤、埠、OPL、讀鍵、DOS 狀態與檔案操作相同。狀態 SHA-256 `df85c5d5f612ff996d7b671bd81ba1238e41e55bff926dc293c90975ece21174`，結果在 `city-panels-state-audit.json`，全部命令、來源、工具、素材、四平台架構／雜湊及 144 份正常收據雜湊在 `city-panels-state-provenance.json`。未宣稱逐幀或跨 RNG 實作精確對拍。

Linux 產品從現行來源再次建至獨立暫存檔，與實際 GUI 使用的程式逐 byte 相同，暫存副本已刪除。35 原始檔與 RAR 雜湊保持基準，施工及冷讀資金均為 79980。022 限本批面板達 CONFORMED；其他視窗／圖表／圖片／場景／動畫、模態外、真機與正式封包仍未完成，#31 與完整 HD 母項保持開啟。

最終 338 個相對文件連結、五個新入口及既有入口正對照、Python／shell 語法、Go 格式、變更檔案 1000:1000 擁有權與容器內指定 `find` 通過，結果為 `workspace/runs/city-panels-final-hygiene.json`。本批容器均已退出並刪除，沒有新建 image、改動 dosgolem 上游或清理其他專案資源。只以明確清單提交二十二份原創程式、腳本與文件，原版、擷取、原文衍生資料、字型及美術不入 Git；提交推送及 #37 結案結果回鏈遠端，#31、#7 與完整 HD 母項繼續開啟。

## 2026-10-11：#38 檔案視窗與離開提示來源達 READY

先以主機 gh 回讀遠端並建立 [#38](https://github.com/wicanr2/taipei/issues/38)。沿用原產品 `1f10d0c`、固定 Docker 與唯讀原版，沒有修改前端、HD 正式程式或 dosgolem 上游。路由載入規格閘門、文字反查、正常試玩、GUI 還原與文件職責入口。

- `file_dialog_catalog.py` 重建 ROM3 的 7169 像素檔案視窗、ROM1 加中文／ASCII 的 4032 像素離開提示。首批八份輸入保留 `file-dialog-source/`；後續審查 `file-dialog-source-ready/catalog.json` 共 243 份，其中 238 個檔案視窗、五個離開提示，729 個單像素破壞全部拒絕。來源包含重複狀態，不把份數當成不同狀態。
- 正常探索先後保留 `file-dialogs-native/`、`file-dialogs-native-extra/`、`file-dialogs-native-list/`、`file-dialogs-native-edges/`、`file-dialogs-native-missing/`。首兩次停止分別推翻「最後字元退格後畫面一定空白」與「F2 重開一定選第一項」假設；原版已讀鍵，並非漏鍵或產品缺陷。後續改為保留可見殘留、按完整 F2 來源選項同步，不重掃已完成九十四字元。
- `file_dialog_inputs_check.py` 回讀全量原子收據，驗六十二英數接受、小寫轉大寫、三十二符號忽略、八字元上限、第九字已讀而畫面不變、最後字元殘留由新輸入覆蓋。十檔清單二十三取樣、七列捲動、邊界、取消、空清單／空白確認與離開選否通過。未選清單文字實際墨色為 31，選中為 32；沒有沿用 ROM 範本占位字的墨色猜測。
- 覆寫測試只改私有副本 ALPHA001.SAV。原版開／關檔、93567 bytes、實際輸出 SHA-256 `59388c3837d65bec89eceb8743cf01e3d5535d06f441e3cd4d3273ecdd8d1044` 及其餘九份 SAV 不變通過。讀檔清單收到八字 `MISSING9`，完整畫面仍不變，保留原版選檔操作。
- 核對腳本曾把整個私有執行目錄應空白及 `FileOps` 應有 write 當成斷言。005 已指定獨立 scratch，目錄已有兩份 ROM 副本；固定 dosgolem 的 AH=40h 記在 `Wrote`，前端未匯出，`FileOps` 沒有 write。依來源訂正後核對 SAV、原版開／關檔、落地雜湊、大小與兄弟檔案，乾淨重跑通過，沒有為腳本假失敗修改產品。
- Go 離線原型固定 Noto 與既有 B 材質，198 個字形驗安全矩形；調暗底色後白／紅字可辨讀。獨立 `hd_file_dialogs_check.py` 重算 PNG alpha 與完整提示組合通過，結果 `file-dialog-ink-dim.json`。八 W 原位比較 `file-dialog-wide-proof.png` 已目視無裁切，原版背景與原型清楚分開；這不是產品 HD 收據。初版亮底素材與 Go 來源保留 `file-dialog-prototype-first/`。
- 023 經完整來源、正常操作、獨立墨跡與視覺審查升 READY。正式實作前登記每 24,000,000 步抽樣，要求同一正常 GUI 輸入兩側完整原版步數且兩類視窗實際出現。未知外部刪檔／損壞、裝置錯誤及其他介面留在母項，未宣稱全遊戲 HD 完成。

本批所有探針及原型在既有 Docker 執行，有界停止不代替原版退出驗收。末尾檢查原始 35 檔、RAR、來源與產物雜湊、文件入口、語法、1000:1000 擁有權與指定 find，結果保存 `workspace/runs/file-dialog-research-hygiene.json`；檢查結果完成後回鏈遠端。沒有新建 image。研究容器均退出並刪除，沒有清理其他專案資源。只提交原創工具及 READY 文件；#38 與母項維持開啟，下一步是正式呈現接入及其驗證。

## 2026-10-11：#38 正式呈現接入與驗證

以主機 gh 回讀 #38 的 READY 規格及預登記抽樣條件後實作。`file_dialogs.go` 只讀原版索引畫面與色盤，完整來源接受後接固定 B／Noto。失配回退、檔案視窗／離開提示素材隔離，以及每幀文字清除依 023；不引用 DOS 執行器。規格補清空白輸入列的統計墨色固定為 15，空白清單列為 0，與已審查的來源核對器一致，沒有改動原版可見內容。

- 實際素材測試核對全部 243 份完整來源、729 個單像素負對照、雙紅色選取負對照、使用／未使用色盤及十四項真實資源缺失／竄改。完整 HD、鍵盤及原點測試通過且無跳過；新增雙選取後再跑本批測試通過。
- `file-dialogs-hd/` 由正常冷啟動驗空清單、空白存檔、第八／九字元、退格、取消、十檔七列捲動及邊界、讀檔名稱忽略、覆寫與離開選否。兩家族 F12 往返保持原版畫面及原版鍵盤輸入不變。64 份正常 GUI 收據由獨立 Go 核對器通過，Python 另從 ROM 重建並核對 37 份檔案／提示收據的整框及所有區外，198 字形墨跡通過；八字輸入與離開提示已目視確認。
- `file-dialogs-negative/` 保留重算 PNG 及受影響雜湊的 22 份收據。18 項來源、墨跡、背景、區外、使用中色盤與中繼資料竄改均被 Python／Go 拒絕；四個正對照包含未使用色盤變動，均通過。
- 完整存退讀改用獨立 `gui-file-dialogs-cold/`，保留 022 的 `gui-cold/` 與來源 catalog 路徑。腳本拒絕覆寫既有目錄，另外記錄本輪程式及腳本雜湊，加入存／讀／離開視窗 F12 及從原字模還原的施工／冷讀資金比較。
- 本批須驗實際存檔，`presentation-audit` 使用兩個獨立、空白且可寫的 scratch，保存原版寫入紀錄與落地 SAV 雜湊。新增 `-require-file-dialogs` 同時要求兩家族實際抽樣，並將重播結果的原版畫面、色盤、讀鍵及檔案操作回對正常 GUI 收據。整批驗證入口為 `file_dialogs_verify.sh`，彙整入口為 `file_dialogs_provenance.py`。

本節先記錄已完成的實作與單幀／控制驗證。完整兩次退出、明示 24,000,000 步狀態抽樣、原始輸入與四架構的彙整結果完成後追加；在此之前 023 仍為 READY，#38 維持開啟。

整批驗證最終退出 0。`file-dialogs-hd/` 的 64 份與 `gui-file-dialogs-cold/` 的 45 份正常收據共 109 份，獨立來源、固定參考與全部區外通過；其中 53 份是檔案／離開提示及原版主題往返。完整施工、兩次原版退出、全新 EXE 讀回原施工格與資金 79980 通過，存檔仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，保存在 `gui-cold-saves.EVJvVc/`。

正常 GUI 的唯一硬體輸入重播兩側各完整 2,688,000,000 步，原版側 175.408 秒、HD 側 138.719 秒。112 次預登記的 24,000,000 步抽樣，含檔案視窗六次、離開提示三次、說明三次及城市各層六十次。RAM、CPU、原畫面、色盤、埠、OPL、讀鍵、DOS、檔案操作、原版寫入與實際 SAV 雜湊相同，並回對正常 GUI 收據的原版畫面、色盤、讀鍵與檔案操作。狀態 SHA-256 `f55713cac7d97ff24ed9b8e4b21590a65cd254890efd7d926a23129f0a07bf0e`；完整收據、命令、程式／工具／來源／固定素材及四架構雜湊在 `file-dialogs-state-provenance.json`，過程在 `file-dialogs-verification.log`。

Linux、Windows amd64、macOS amd64／arm64 編譯與架構核對通過；Windows 仍只有既有 YMFM 編譯警告。本輪 Linux 再從現行來源建到容器暫存檔，與實際 GUI 使用程式逐 byte 相同，副本刪除。35 原始檔與 RAR 不變，364 個相對連結、八個新入口及既有入口正對照、Python／shell 語法、Go 格式、1000:1000 及指定 find 通過，結果在 `file-dialogs-final-hygiene.json`。本批容器均退出並刪除，沒有新建 image、修改 dosgolem 上游或清理其他專案資源。

023 限完整檔案視窗與離開提示達 CONFORMED。模態外、外部刪檔／損壞或儲存故障提示、其他視窗／圖表／圖片／場景／動畫、平台真機與正式封包仍未完成。自有程式、腳本與文件以明確清單提交推送，素材、原版、擷取、字型及原文衍生資料留本機；完成證據回寫 #38，母項保持開啟。

## 2026-10-11：#39 預算與稅率來源開工

主機 gh 即時核對遠端沒有重複項後，先建立 [#39](https://github.com/wicanr2/taipei/issues/39)。來源研究命中原版 GUI 還原路由，載入 `local/retro-gui-restoration.md` 的來源重建與生命週期準則；本作仍依專案權威順序，以 dosgolem 收據為準，沒有改用 DOSBox 收據冒充。

`workspace/runs/budget-source/initial-sources.json` 保留 `hd-runtime/running-03-capture.zip` 與 `running-32-capture.zip` 的雜湊、步數、原版索引及四倍圖線索。兩者都是歷史正常年度視窗，`dos_blocked=false`，目前產品整幀回退；不是本批 HD 收據。標題核對矩形 `(18,38,99,22)` 沿既有 `hd_source_audit.budget_window`，SHA-256 `a93af2ea621191dc51663f84eee9ebc40672d149d585a1458b9edf3c60e872bb`。

最初候選腳本誤用標題 y=37，核對失敗後回查既有來源契約，訂正為 y=38；再依 `full_asset_catalog.image` 的 None 返回契約略過不支援形態。修正只涉及研究腳本，沒有改動產品或對未支援資料強解。`initial-candidates.json` 保存原版 ROM 直接圖片候選的完整偏移、形狀與解碼雜湊；候選左上 99×22 均未直接匹配標題，不能由此宣稱 ROM 沒有該來源。

下一個精確閘門是從正常功能選單抵達預算／稅率視窗，確認與年度入口的關係，再重建完整背景、固定文字、動態數值、選取與返回。完整來源模型仍未知，沒有新 READY 規格或正式接入。產物留在 workspace/，原版唯讀、UID／GID 1000，研究容器已退出刪除；#39 與 HD 母項繼續開啟。

## 2026-10-11：#39 完整預算來源與 #40 時鐘缺口修正

本輪回讀主機 gh、Git 與遠端 Issue，再依 #39 研究正常入口。路由命中 GUI 還原、字形反查、平台規格先行、IDA 9.4 與文件職責，載入各任務的單一入口及必要 reference。使用者已定案的 B、1280×800、Noto、F12 及全部圖片／操作介面範圍不變。

- 完整背景為 ROM2，檔案偏移 12662，235×132，原位 `(18,37)`。標題在背景局部 y=1，解釋先前只比左上角候選不符的原因。`budget_catalog.py` 重建五個百分比、四個費用、稅收及淨額共十一個 ASCII 欄位，逐像素核對完整面板，不略過數值區。33 份正常來源符合，132 項單點破壞全拒絕；原字形別名與無精確字碼對應的烘製文字保留未知，沒有直接猜補 Noto 字串。
- `budget-native/` 在 F3 選取後過早返回；`budget-native-entry/` 的年度視窗在一次 Down 後亦已消失。輸入收據證明只讀一次原版按鍵，不能推論方向鍵關窗。兩前件保留，沒有加快擷取或拉長等待來掩蓋差異。先建立 [#40](https://github.com/wicanr2/taipei/issues/40)，再研究時鐘缺口。
- IDA 既有資料庫唯讀掛載，另製可寫副本，窄範圍匯出 `sub_2465E` 與讀鍵函式原始名稱、位址、bytes、檔案偏移及 xrefs。預算 owner 在 IDA 線性 `24747h–2478Eh` 比較秒欄位，閒置計數大於 14h 後離開。第一次查到的 `1EFF4h` 是呼叫後返回位置，依 call 關係追到真正 owner，沒有把 KeyRead caller 當成目前執行函式。IDA 匯出初次 UTF-8 與未知函式斷言失敗均修正查詢工具，再以新副本重跑；不是產品缺陷，未改原資料庫。
- dosgolem 的 DOS `clock()` 誤用 raw PIT IRQ 次數；BDA BIOS 時鐘及 INT1A 已有獨立計數。公開 DOS 契約與固定 commit 的 DOSBox Staging／MS-DOS 原始碼全文存檔後，建立 024 DRAFT 與四組受控紅測試。固定同一 BDA、只變 raw IRQ 即得錯誤時間；INT1A 設定未反映到 DOS 時間。證據審查後升 READY，才新增第七份隔離補丁，改讀既有 BDA。保留原整數近似，不深挖原版 ISR、硬體 driver 或改動閒置上限。
- 四組紅測試轉綠。DOS、狀態、oracle 與 probe 的 236 項頂層測試通過，五項既有無 fixture 測試跳過，名稱完整保存在 `dos-clock-source/provenance.json`。HD、鍵盤及原點十六項實際資源測試通過，無跳過。Linux、Windows amd64、macOS amd64／arm64 均以既有固定 image 編譯及結構核對；Windows 仍有既有 YMFM 編譯警告，沒有新增 Wine 或真機驗收。
- `budget-native-fixed/` 正常冷啟動 F3 的 41 份收據通過。Down／Up 五列循環，Right 各減一、Left 還原，Escape 回同一暫停地圖、重開與閒置返回皆正常。Space 保留視窗。第一份預算的 PIT divisor=2982、raw IRQ=36452、BIOS tick=1622；閒置離開沒有新增原版讀鍵。Escape 前變更已逐項還原，不據此推論 Escape 撤銷尚未還原的調整。
- `gui-dos-clock-cold/` 從 HD 真實冷啟動完成 F12、電線施工、存檔、原版退出、全新 EXE 讀檔與第二次原版退出，45 份新收據由 Go／Python 獨立核對完整來源、固定呈現與全部區外。專用字型、圖示、底欄核對通過。施工格讀回相同，兩次資金均為 79980，實際存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。舊四架構、來源及正常 GUI 原件均保留，沒有宣稱舊、新時鐘核心的全部狀態相同。

本批 Linux SHA-256 為 `52b65f10bd009c0f94741eaaa1aa36d0349342dbea646453bb9eff7ce9c40b8f`。`dos_clock_provenance.py` 核對兩批共 86 份新正常收據、七補丁、四架構、測試、平台全文、35 原始檔與 RAR，輸出 `dos-clock-source/provenance.json`。`probe.sh` 亦從乾淨基底套用七補丁、重新編譯並執行一指令的有界入口測試通過；這只驗工具鏈，不當作新玩家路徑。

預算完整來源已取得，#39 的 Noto 靜態文字、非零金額、未還原調整保存語意及正式 HD 尚未完成。其他視窗、地圖建物、場景、動畫與正式平台封包依母項繼續，沒有改動 dosgolem 上游或公開上傳原版及衍生素材。

收尾 378 個相對連結、七個新工具入口及 024 入口、既有入口正對照、Python／shell 語法、Go 格式、1000:1000 擁有權與容器內指定 find 通過。Linux 再從現行來源建至容器暫存檔，與正常 GUI 使用程式逐 byte 相同，副本刪除。重建初次命令誤寫 `-p1`，改回 Go 的 `-p 1` 後同容器乾淨重跑通過；初次檢查未帶 Docker `-i` 而未接到 stdin，也已補正重跑並取得實際 JSON，不把空輸出視為檢查通過。結果保存 `dos-clock-source/final-hygiene.json`。本批容器均退出刪除，無新建 image，未清理其他專案。024 限時鐘來源升 CONFORMED，#40 的提交與結案回鏈遠端；#39 與完整 HD 母項維持開啟。

## 2026-10-11：#39 預算來源與原型達 READY，#41 修正普通讀鍵同步

時鐘修正 ef3adbd 已推送，主機 gh 回讀 #40 CLOSED、儲存庫 PRIVATE 且 Issues 啟用後，繼續 #39。命中 GUI 還原、字形反查、規格閘門、正常試玩與文件職責入口。沿用已定案 B、Noto、1280×800、F12 及原版版面，沒有新產品取捨。

- `budget-native-ranges/` 實際是未還原調整及 F2 存讀研究，不是規則極值驗收。稅率／公共安全 10／100 調成 9／99，Escape 再開仍保留，Enter 留窗。原版存檔後再改成 8／99，正常 F2 讀回恢復 9／99，讀取沒有改寫 SAV。`BUDGET39.SAV` SHA-256 `442981026373f69080668ad176335949636635c407ba5b14cbf4f2ce7265b430`；未把同一 EXE 的讀取當作全新啟動驗收。
- 固定烘製文字依 ROM2 原框逐字核對，五十個字形各留原位像素 SHA-256；有精確 ROM57 對應者保留，無原始字碼者明記目視轉錄。沒有把 Noto Unicode 視為已抽出的原版字碼。新離線 `budget-prototype` 沿用固定 B 藍板、Noto 與 OFL，產生完整 940×528 面板、白／紅數字、靜態 alpha 及原位比較。數字從 24 點原型調為 32 點，仍在原三／八欄固定字距內；前件留本機。初次原型於 app 目錄找不到 catalog 的相對 receipt 路徑，改在 workspace/ 執行後通過，沒有改原版資料。
- 災難城市來源初次把片頭當成必有 DOS 讀鍵而遇到 NoneType。保留原件，恢復片頭既有入口。另一批啟動仍持續前進卻碰到 120／180 秒上限，收據保留；回查試玩路由與 Docker 資源後，有限 7 億步啟動改驗持續虛擬進展及停滯，整批 900 秒上限不變。沒有加快遊戲、重送鍵或調原版等待。
- `budget-native-scenario-extra/` 逐幀確認災難台北、說明、難度與城市。暫停收據在 1,320,000,000 步，原版 0 卻在 1,320,341,898 步才讀，下一個 F3 只讀一次。兩次讀取被總數斷言混入同一步，先建立 [#41](https://github.com/wicanr2/taipei/issues/41) 再修工具。共用 `action(..., acknowledge=True)` 明示等待普通 Key 與 release，方向鍵仍驗 word；片頭及 F12 不強加 DOS 讀取。單獨的擷取等待曾先到 25 秒上限，原子收據稍後仍正常產生；實際 F3 面板與既有正常 F3 原件逐 byte 相同，未開啟無關的 #37。
- `budget-native-source-ready/` 正常冷啟動重跑成功。原版讀 `Disa1.Dsa` 後進城，暫停、F3、預算與 Escape 全經真實視窗事件；九鍵各只新增一次原版讀取，六個普通鍵與三個方向／功能鍵的 release 通過。四欄費用為 2200／1778／6019／20247，完整 ROM2／十一欄重建相同。這是有界研究停止，未當作原版退出。
- 最終 `ready-model/catalog.json` 含 43 份來源、172 個單像素負對照。來源辨識補恰一個紅色百分比、其餘數字黑色；六原型的無選取／雙選取／費用錯色共十八項有效負對照全拒絕。43 份使用中色盤均符合，初批與中間 catalog 不覆寫。`budget_prototype_check.py` 獨立重讀 ROM 原框、實際 PNG alpha、完整組合及全部區外，74 墨跡及六張原位圖通過。非零五位數、長標籤、單位與快捷鍵已視覺確認沒有裁切，十個原型檔乾淨重生逐 byte 相同。

025 從 DRAFT 經上述證據審查升 READY。固定 manifest `f6a3052430ad3cc1cda5c737fb21ce6c73c13237e191e29cf0c92684553b9933`，完整來源、轉錄、色盤、字型／授權及 B 素材雜湊見規格；彙整在 `budget-source/ready-provenance.json`。正常負淨額、稅率極值與其他城市未全試玩；呈現只讀已重建原字串，逐字墨跡及欄寬已驗，不替原版補規則。正式預算 HD、F12、有效呈現負對照、冷啟動預算重讀、狀態對照及四架構仍須實作後驗收。

本批沒有改產品呈現器或原版核心，四架構程式 SHA-256 與 ef3adbd 的時鐘產品相同。35 原始檔與 RAR 不變，原版、擷取、轉錄、美術及字型留本機；只提交明列的原創工具與文件，未改 dosgolem 上游。

最終 385 個相對文件連結、新增 025／原型工具／獨立核對入口及既有入口正對照、Python／shell 語法、Go 格式、1000:1000、指定 find 通過，結果為 `budget-source/final-hygiene.json`。工具版本、鎖檔、完整 DSA1 讀取及四份存讀收據的獨立解碼已補入 `ready-provenance.json`。本批容器全部退出刪除，沒有新建 image，未清理其他專案。明列十檔提交推送後，#41 結案回讀，#39 保持 OPEN 並登記 READY 與下一個正式接入閘門；完整 HD 母項仍開啟。

## 2026-10-12：#39 完整預算正式接入與驗證中

來源／原型 `254e6a183bb60075065a77ba15d728b508e8aa0e` 已提交推送，#41 結案後回讀 CLOSED。命中 GUI 還原、文件職責及規格閘門入口，依 READY 025 新增完整 ROM2／ASCII 重建、十一欄字串與單一選取，載入固定 B／Noto 底板及數字。正式呈現先於原年度回退及阻塞判斷；原版主題及失配不洩漏 HD 字串。Go 與 Python 收據核對各自從 ROM 及固定參考重建，不引用產品呈現器。

初版 43 份來源、六張固定原型、190 來源破壞、十二實際素材故障、使用／未使用色盤與兄弟家族隔離通過。增加標題內 `(35,45)` 單點後，先取得有效失敗：年度原件的 `Blocked=false`，完整來源與舊標題提示同時拒絕時，城市覆繪可穿過窗口。以第二個不重疊的精確固定文字區只觸發整幀回退，43 原件均確認此區域相同，HD 的完整來源要求不變。修正後 233 來源破壞通過，`hd-title-guard-before.log`、`hd-title-guard-after.log` 與 `secondary-fallback-anchor.json` 保留。全套實際 HD／鍵盤／原點測試無跳過，結果為 `hd-integration-tests-r2.log`；新四架構已編譯。

正常預算段落以真實 F3、五列 Right 減一／Left 還原與 F12、最後保留 9／99、Escape 重開及 Enter 留窗，再接施工存退讀。首批 `gui-budget-cold/` 已於 4,320,002,774 步正常退出一次，第二個 EXE 正常片頭進主選單，但整批 1200 秒逾時回 124。先回查正常試玩路由，建立 #42，再將包含新增工作量的雙冷啟動上限改為 2400 秒；原版速度、虛擬時間、鍵序及容器資源限制保持。部分 r2 流程有界停止並保留，修正版 `gui-budget-cold-r3/` 正在乾淨重跑。尚未把部分玩家路徑當作完成。

`budget-hd-scenario/` 容器內正常非零流程已完成，但主機 wrapper 在長 Docker 命令期間被編輯，恢復讀取時遇到 `pe: command not found` 回 127。這是 wrapper 問題，非產品缺陷。以不可變 Docker 命令與同一修正版重跑 `budget-hd-scenario-r2/`，原版四費用 2200／1778／6019／20247 與 F12 正常完成。獨立腳本第一次誤用不存在的 `tool-submenus-v1`，依既有來源核對後改為 `tool-menus-v1`；已保留部分輸出並乾淨重跑，不將路徑錯誤列產品缺陷。

Linux 現行 SHA-256 `66e8e18ec202cf3cf22a3fe4893947adfb368425c47ba127177b6b8696dcc9c1`，舊時鐘四架構與初版 HD 四架構分別留 `before-hd-build/`、`first-hd-build/`。原版、擷取、轉錄、字型及美術仍留本機；本批未提交、未升 CONFORMED。正式唯一狀態輸入固定為 r3 第一個 EXE 的 `quit-file-theme-hd-capture.zip`，在產生後補登步數／SHA，再重播每 24,000,000 步與逐點原版狀態。#39、#42 與完整 HD 母項維持開啟，容器完成後須核對清理狀態。

r3 第一段 169 次原版狀態抽樣及落地存檔相同，狀態 SHA-256 `8e2712d3be18d590d3f3523e3c41c1e4d563509ac370cd8aa790e2d375b23950`。全新 EXE 正常讀回施工格、資金 79980 與預算 9／99，但讀檔後城市仍持續推進。後續 Escape 已被原版讀一次，80 年 12 月再次出現完整預算，費用 1、淨額 -1；測試要求返回後一直留在城市而失敗。保留原始來源與 `budget-source/reload-return-before.png`，不改原版年度流程。

先建立 #43，再於冷讀核對施工格及資金後加正常 0 鍵暫停，沿用 #41 實際讀鍵及 release。完整 `gui-budget-cold-r4/` 使用同一 Linux binary、image、速度及 2400 秒上限乾淨重跑，r3 與其他部分原件保留。正式唯一狀態輸入改登記 r4 的 `quit-file-theme-hd-capture.zip`，產生後、重播前回寫精確步數與 SHA；r3 第一段只作前件。獨立核對及證據彙整入口同步改為 r4，原正常非零情境仍使用已通過的 `budget-hd-scenario-r2/`。

r4 完整正常流程通過：103 份收據、五列調整／還原與 F12、9／99 存檔及全新 EXE 讀回、同一施工格、資金 79980 與兩次原版退出。第一個 EXE 在 4,322,002,774 步退出，第二個在 2,160,402,774 步退出，未使用快照。實際 SAV 在 `gui-cold-saves.U5Gg8y/ROUND4.SAV`，SHA-256 `7b4470803b77aa311dfb83014db3e14c73981dccfe0b57fdc4aeb6993364efbd`。r3 的淨額 -1 另由兩個核對器驗來源、整框及全部區外通過，原件不改寫。

`budget_hd_verify.sh scenario` 與 `cold` 均退出 0。十三份非零情境加 103 份完整冷啟動，共 116 份正常收據由 Go／Python 獨立核對完整來源、固定高清參考及全部區外，其中 52 份是預算來源及原版主題往返。十三項重算 PNG／雜湊的有效破壞全部被兩個檢查器拒絕，兩個正對照含未用色盤變動通過。十七項頂層實際 HD、鍵盤及原點測試無跳過。

正式 r4 原子輸入 SHA-256 `ad564fb6800171d15dd060cfb8137cdf5c599fbf34dbd712704eb2c154db4170`，先回寫 #39 再重播。第一次預登記誤指舊的 canonical 重播工具，執行前保留 `state-preregister-r4-before-tool.json` 並追加訂正，改用本批 `budget-source/presentation-audit` SHA-256 `2034bd75e4597e70d6290c48b92e7f71456ba0fabf963747754d06f44f6eefbc`；未用錯工具執行正式重播。兩側各 4,056,000,000 步，每 24,000,000 步共 169 點，原版側 265.598 秒、HD 側 240.075 秒。五列預算共 49 次、檔案六次、離開三次及既有呈現層實際抽樣，逐點原版狀態與實際存檔相同，並回對正常 GUI 收據。狀態 SHA-256 `57371f3caa873699e591ce397076453a9ff6ceb111a1a0257825cd8d2510c681`；不是逐幀或全遊戲 HD 對拍。

`budget_hd_verify.sh provenance` 退出 0，彙整 `budget-source/hd-provenance-r4.json`。固定七補丁、35 原始檔、RAR、四架構及 1000:1000 擁有權符合；原型及前件均保留。Linux 再由固定基底與七補丁乾淨重建，與正常 GUI 程式逐 byte 相同。Windows 仍只有既有 YMFM 編譯警告；本批沒有重跑 Wine 或 macOS 真機。實際正常預算畫面 `budget-source/normal-budget-hd.png` 已目視核對選取、中文及數值無裁切。

完成前再回查規格閘門與 README 路由，025 限完整預算呈現升 CONFORMED。CONTEXT、README 及驗收矩陣同步現況；極值規則、模態外、其他圖片／視窗／圖表／場景／動畫、真機與正式封包仍未完成，完整 HD 母項維持開啟。只提交明列的原創程式、腳本與文件，不加入原版、轉錄、字型、美術或擷取，不改 dosgolem 上游。收尾檢查及提交回鏈另追加結果。

收尾 393 個相對連結、九個本批入口與既有入口正對照、全部工具 Python／shell 語法、41 份 Go 格式、變更檔 1000:1000、指定 find 及 Linux 乾淨重建比較通過，記錄 `budget-source/hd-final-hygiene.json`。本批 Docker 容器均退出刪除，主機回讀沒有殘留專案容器，沒有建立新 image 或清理其他專案資源。提交以「完成預算面板高清呈現與正常存退讀驗證 #39 #42 #43」回鏈遠端，提交 SHA、推送及 Issue 結案結果以 #39 的最終回覆為準。

## 2026-10-12：#44 道路電線來源與離線原型

主機 gh 核對 #39／#42／#43 CLOSED 及現行提交 `6b92297e87e53e2e84208b61a7fb2b646395b28d` 後，先建立 [#44](https://github.com/wicanr2/taipei/issues/44)。命中復古重製、GUI 還原、規格閘門與文件職責入口，載入對應技能及必要 reference；新材質使用 imagegen 技能，窄範圍來源查證使用 IDA 9.4 技能。B、1280×800、Noto、F12、完整重繪與四個平台／架構沿既有定案。

- `infrastructure_catalog.py` 嚴格重讀固定 ROM 九組圖庫，1134 筆來源／1049 個不同 81-byte 圖像及所有別名相符。成員 39 全部 75 張有原始偏移、色號及 SHA-256；二十份既有正常城市收據看見其中十四張，75 個首像素破壞全拒絕。技術圖庫最初遇到 image 缺少 rsvg-convert，指定 MSVG 仍無 coder；回查 GUI 還原路由後，改用既有純 PNG 編碼及 ROM56 ASCII 技術標籤，不另建 image。兩前件保留於 `infrastructure-source-before-svg/`、`infrastructure-source-before-msvg/`，正式盤點在 `infrastructure-source/catalog.json`。
- 第一輪 `infrastructure-native/` 完成 97 次正常原版讀鍵，各建九格道路與電線十字並移開游標；中心圖像 25／55、水平 16／46、垂直 15／45，過程另見 21／51。原點取實際 `map_origin=(12,12)`，沒有城市／座標注入或快照。最後 5,112,000,000 步採有界研究停止，未當作原版退出或存退讀。後續探索加入轉角、岸邊及道路電線重疊，另存 `infrastructure-variants-native/`。
- 內建 imagegen 新繪瀝青材質，預設輸出複製至 `workspace/prototypes/hd-style/`，不覆寫原圖。原圖 1586×992，SHA-256 `7b172889bb71eb4a8bb65393e8caaae790afd1eed69529a71a612cffd20b85ae`；固定 ImageMagick 轉 1254×1254 後為 `61057d15840d65801652de6af95b1b27b56706d67774a66f41bec3fb852cd384`。完整提示詞為 `asphalt-b-v1.prompt.txt`，SHA-256 `6a56bd89866d51a10bc56cda39874517f890067c530d7a4d1d8c1827c89b3cfe`。原圖、提示詞及後處理留本機。
- 026 維持 DRAFT。候選成員 39 的 15–29／43–55／60–74 共 43 張，來源各自核對，不以圖庫位置猜用途。v2 將色彩量化改為整數；v3 用三次過渡縮窄薄線混色帶；原位比較發現瀝青顆粒過大，v4 改為四倍世界頻率。各前件保留，沒有改產品呈現器。獨立核對直接解析 ROM，以整數面積及 Fraction 色彩確認 55728 個高清像素、13932 個原像素中心、四向原邊、24 張世界座標測圖、兩張完整 1280×800 及全部區外。五項破壞同步更新自報雜湊後仍拒絕。
- IDA 的 `source-selection.json` 與 `bitmap-drawing.json` 由原始唯讀 `.i64` 的新副本匯出，固定 IDA 9.4 image，沒有改名或回寫原資料庫。`sub_1619A` 的十三指令證實圖偏移索引；`sub_16129` 的三十二指令證實逐列完整 `rep movsb`，色號 0 不能當透明底圖。60–74 與 15–29 的差異包含 240／241 及部分背景像素，不能用換車色或固定 `+45` 推導。240／241 確有原版色盤變動，正常交通來源相位尚未驗收。

第二輪來源另以 `infrastructure_source_check.py` 逐段重讀原子收據、ROM 別名、原版讀鍵與原點；預設部分報告明列缺段，`--require-complete` 才要求全部七段。初步三段 `normal-variants-prefix.json` 有道路十字九格、轉角／鄰格八格及岸邊六格已知變化。岸邊實際來源以原版為準，不另猜橋梁規則。完整版、正式資源／回退契約、正常交通相位、HD 接入、捲動及存退讀仍由 #44 繼續；全部地圖、介面、場景與封包母項未結案。

## 2026-10-12：#45 修正原型 PNG 可重現性

v4 從固定輸入乾淨重建時，`39-015.png` byte 比較失敗。兩圖解碼 RGBA 相同，PNG chunk 證實差異為 `tIME` 及 date:create／date:modify。原型沿用了負對照用的 `hd_chrome_negative.png`，其 ImageMagick 編碼會寫時間戳。先建立 [#45](https://github.com/wicanr2/taipei/issues/45)，才改本批產生器；沒有改其他批次的共用負對照工具。失敗前件保留於 `workspace/runs/infrastructure-repro-v4/`。

v5 採固定 Python 標準庫的 RGBA8 PNG，只有 IHDR／IDAT／IEND、filter 0、zlib level 9；保留 v4 幾何、尺度及像素。獨立完整來源、中心、四邊、24 張世界座標、兩張正常原位及五項有效破壞通過。v5 manifest SHA-256 `c9ea6457c10fc9dec5c755177e940eb0461e26282a74f5a58977456a2c90794c`。乾淨重建、擁有權及 Docker 收尾結果另追加；本缺陷修正不把 026 升 READY，也不將 #44 或完整 HD 結案。

v5 兩次乾淨輸出的 157 份產物及 manifest 逐 byte 相同，70 PNG 全部與 v4 解碼像素相同，且只含 IHDR／IDAT／IEND。Python 3.11.2，zlib 編譯及執行均為 1.2.13；證據在 `infrastructure-source/v5-reproducibility.json`、`png-provenance.json`。成功的重建暫存目錄刪除，v4 失敗前件保留。原版 RAR、EXE／ROM 與 Linux binary 雜湊相符；沒有改產品程式，不重跑無關的跨平台編譯。

第二輪來源在 2400 秒上限回 124，保留完整六段 `normal-variants-final-prefix.json`，只有電線岸邊缺段。另寫窄範圍補查，不延長原整批或重跑已完成內容；同一 binary、image、400000 steps/update 及正常鍵盤，46 次原版讀取及 release 形成五格成員 39／圖像 46。`infrastructure-shore-native/` 在 3,024,000,000 步研究停止，退出 0，獨立 `--case shore --require-complete` 通過。

最終七種情境的已知變更數為 9／8／6／9／8／2／5，游標等未知格另列。道路重疊的五次操作只有兩格畫面改變，其餘來源不變，未依按鍵推論施工成功。`infrastructure-source-r2/catalog.json` 收入 390 份正常城市收據、125 個不同已見圖塊；成員 39 已見 27 張，其中 25 張屬候選，剩餘 18 張正常相位仍未驗。

擴大 `infrastructure-v5-expanded/` 由七份正常原件產生七張離線比較，完整 1280×800、140 個候選格及全部區外通過；五項有效破壞仍拒絕。43 張幾何、13932 個中心、85 種原邊及 24 張世界座標通過，manifest SHA-256 `b59376311fafe2265bc7a2208c4426b20d33c35cafa4dcf989261794354ee32b`。沒有把離線比較當成正式 GUI。技術比較 `infrastructure-v5/power-comparison.png` 左原版、右候選，裁圖及來源雜湊在同目錄 JSON。

最初文件檢查的正對照誤指不存在的工具名稱，改用確定已有入口的 025 後通過。後續新增岸邊補查及最終記錄一併重新核對；最終檔案、連結、語法、入口、1000:1000 及指定 find 結果保存 `infrastructure-source/final-hygiene-r2.json`。本批容器全部退出刪除，沒有新建 image，未清理其他專案資源。只提交明列原創工具與文件，美術、原版、圖庫、字型、擷取及證據產物留本機。提交／推送後回鏈 #44／#45；#45 僅 PNG 修正結案，#44、完整 HD 及跨平台交付母項維持開啟。

## 2026-10-12：#44 第一批道路電線正式接入

回讀主機 gh、#44 與現行提交 `50acd20`，工作樹乾淨。路由命中復古重製、規格閘門、GUI 還原與文件職責；沒有重開 B、1280×800、Noto、F12、全部重繪或平台決策。依已完成的七種正常來源及獨立原型證據，將 026 的已見 25 張獨立審查為 READY；18 張候選維持 DRAFT，完整 #44 範圍不變。開工及驗收條件先回寫遠端。

`infrastructure_assets.py` 從固定 v5 及正常盤點產生 51 份資產，manifest SHA-256 `720e3d40b253c6a505dbfa43f415cb0752e18ea51150d9888c1ea3f4c7bc7aec`。乾淨重生逐 byte 相同，成功暫存目錄刪除。產品 `infrastructure.go` 只匹配完整 81-byte、固定已用色盤與經雜湊核對的四權重幾何；只改 RGBA，素材缺失按來源回退。來源與全部別名、材質及幾何仍留本機。

第一輪 Go 與固定原型不符，根因是沙地色號 204 的 1015 千分比在亮像素超過 255，轉 byte 前漏了契約指定的夾限；並非 PNG 解碼差異。補上夾限後同一容器／命令乾淨重跑，四項新測試無跳過：25 張固定整格與全部區外、2025 項原像素破壞、逐已用／未用色盤、七張正常原位 140 格、162 項實際 loader 撤除／損壞／長度錯及來源隔離、十六張世界材質測圖通過。六項既有城市、年度預算、鍵盤與原點回歸亦通過。結果為 `infrastructure-source/ready25-go-tests-r2.log`、`ready25-regression.log`。

正式 GUI r1 完成電線、四格道路與 F12，水平捲動原點由 (12,12) 到 (14,12)，但腳本誤寫成一格，與 006 既有 `sub_1850A` 的兩格證據矛盾。保留 `gui-infrastructure-cold-r1/`，修驗證斷言，不改產品或遊戲速度。r2 同一 binary、image、400000 steps/update 與 2400 秒上限從冷啟動重跑；新增正常 Up 返回垂直視窗後才存檔，使原電線世界格可直接冷讀核對。正式狀態重播須等唯一輸入產生、回寫 SHA-256 與步數後再執行。

Python 獨立核對器重讀 ROM，以整數幾何與 Fraction shader 核對正式整格。初次負對照啟動發現 prototype checker 頂層匯入負對照工具造成循環，將該匯入限縮到負對照函式後重跑。`infrastructure-hd-negative-r1/` 的五項破壞均重算來源、PNG 及受影響雜湊，完整正對照與未用色盤變動通過，錯整格、錯世界相位、改來源後殘留 HD、回退格與計數破壞均拒絕。

Linux、Windows amd64、macOS amd64／arm64 已重建，Windows 僅有既有 YMFM 警告。Linux 為 `3f3953d6b4db3abd9aeededcbcf128706c75ccc1600d5b366e74126db58adf25`；本輪沒有新增 Wine、macOS 真機或正式封包聲明。r1 真實畫面 `infrastructure-source/normal-road-hd-r1.png` 已檢視，SHA-256 `2983930521bc202e1772eecdc19389ca3f7291e0e509753e4e22f6a824f4f5fe`。

正常災難城市 1 鍵恢復後的三十份來源研究已完成，`infrastructure-traffic-native/` 在 1,752,800,000 步有界停止；已見成員 39 十四張，但沒有 60–74，不能宣稱交通相位已解。依已核對原字碼的 F4 第二列「交通密度」再作窄範圍入口研究，輸出 `infrastructure-density-native/`。只有原始來源與畫面觀察，不新增規則或正式 HD 候選。

中途語法、八個入口與 025 正對照、Go 格式、1000:1000 及指定 find 通過，見 `ready25-intermediate-hygiene.json`。正常 GUI 及密度來源研究容器仍在執行；本批最終驗收、清理、提交與推送結果另追加。026 第一批仍 READY，完整 #44 及 HD 母項保持開啟。

正常 r2 完整通過，兩次原版退出分別為 5,210,002,774 及 1,417,602,774 步。全新 EXE 讀回四格道路、電線世界格 (37,13) 與資金 79780；存檔 `gui-cold-saves.iOsCKm/ROUND4.SAV` 為 93567 bytes，SHA-256 `c2aa48a46f1090262b367bd161d0b8a717374ec8a676170bd50283fcc4791a59`。105 份原子收據全部通過 Python 完整新圖塊及回退格、Go 既有介面及區外核對，60 份實際呈現本批圖塊。水平五格、垂直四格同世界來源與高清像素一致，兩次正常捲動原點均相差兩格。正式存檔前畫面 `infrastructure-source/normal-road-hd-r2.png` 為直接擷取，SHA-256 `4e18570e616c334685face303ee19e068d9ffeb352e839fe670d2efa3d4e2386`，已目視核對。

狀態重播先將唯一輸入、工具 SHA-256、4,944,000,000 步及 24,000,000 步間隔回寫 #44，再執行兩側完整步數。206 個抽樣點原版狀態相同，95 點實際呈現道路／電線；原版側 318.585 秒、HD 側 377.872 秒。最終狀態 SHA-256 `a8a5176dcf971de4376c4818b975dcb01b651825c8e8c728a9a64f6b08255e2f`，正常 GUI 的原畫面、色盤、讀鍵及檔案操作回對相同，實際 SAV 與正常 GUI 相同。`infrastructure_provenance.py` 退出 0，彙整 `infrastructure-source/ready25-provenance.json`，四架構、Linux 乾淨重建、七補丁及 35 原始檔／RAR 不變通過。

交通密度窄探針八份完成，最終 1,320,400,000 步、`dos_blocked=true`，實際是阻塞式圖表，沒有看到候選 60–74。保留原件，不將入口名稱當作動畫語意。完成前回查規格閘門與驗收 reference，026 僅第一批 25 張升 CONFORMED；其餘 18 張及完整 #44 保持 DRAFT／OPEN。同步 CONTEXT、README 與驗收矩陣。正常 GUI 新圖像抽樣為五種，其餘已確認來源另有正常原版與固定全格證據，不宣稱逐幀或全圖像互動窮舉。本批最終衛生、提交及回鏈結果另追加。

收尾 422 個相對連結、九個新增入口與 025 正對照、74 份 Python／27 份 shell 語法、43 份 Go 格式、變更檔 1000:1000 及指定 find 均通過，見 `infrastructure-source/ready25-final-hygiene.json`。本批容器全部退出刪除，主機回讀沒有殘留專案容器，沒有新建 image 或清理其他專案資源。只提交二十份明列的原創程式、工具與文件；原版、幾何、美術、字型、SAV 及收據保持本機。提交以「接入首批道路電線高清與正常存退讀驗證 #44」回鏈遠端，實際 SHA 與推送結果以 #44 回覆為準，完整 Issue 不結案。

實際提交 `e7f854ed03bbd89f7052a012b6130cd04d865f54` 已推送，遠端 main 相同；[#44 驗收回覆](https://github.com/wicanr2/taipei/issues/44#issuecomment-6112700723) 已回讀 OPEN。

## 2026-10-12：#46 發電廠來源研究

先列舉遠端未完成項目，再建立 [#46](https://github.com/wicanr2/taipei/issues/46)，接續 #30 的發電廠圖塊。沿用已載入的規格閘門、文件職責及原版來源入口，未重開使用者定案。核對 021，工具 11 確為火力／核能兩選項；建立 027 DRAFT 與同次文件索引。新增有界正常施工探針，使用 e7f854e 已驗 Linux binary 及同一固定 image，兩次完整選單來源核對、正常方向鍵／Space／Tab 讀取及 release，分列已知與未知變更，不假設複合格大小或圖庫用途。實際結果與容器清理另追加。

首件正常火力施工已形成電廠，但固定原點斷言在移開游標後停止。逐份原子收據顯示第 24 次 Right 使原點 (12,12)→(14,12)；實際大游標及廠區為 6×6，原圖矩形 (203,61,54,54)。保留全部原件及凍結腳本，不列產品缺陷。窄補查將每個選項改為獨立冷啟動，在已見 6×6 陸地 (22..27,3..8) 施工，原版邊界、binary、image、400000 steps/update 及時間不變。`power-facility-nuclear-native/` 已啟動。`power_facility_source_check.py --case thermal --before thermal-target-1-2 --after thermal-uncover-0-19` 直接重讀 ROM 及兩份同為 (14,12) 的原子來源，36 格與來源首像素負對照通過，明列 prefix，未代替完整兩選項或正常存退讀。

另用內建 imagegen 生成工業表面筆觸原型，完整提示詞保存 `workspace/prototypes/hd-style/industrial-paint-b-v1.prompt.txt`。原生成圖實際 1254×1254，SHA-256 `8e1293d89a0725084d77e0eb487f753931e14e94d2855bf8e3f2618d02438af8`；經固定 ImageMagick RGBA8 與已驗標準庫 PNG 編碼為 `industrial-paint-b-v1.png`，SHA-256 `25e851a18d35960f95be339337b706e3b2c433686a6ecd32e9cfc176cdde8094`，擁有權 1000:1000。原圖保留，副本及提示詞均在 workspace，不入 Git，尚未接產品。027 仍 DRAFT。

核能補查完整走位與讀鍵後沒有形成建物，保留 `power-facility-nuclear-native/`。回查 GUI 還原路由，直接依已驗 ROM 字形重建原版費用／資金欄，火力 50000 萬、核能 100000 萬，新城市 80000 萬；核能資金不足，不是產品故障。既有兩份正常 SAV 的唯一共同金額候選為檔案偏移 2，六個 DSA 在此均低於 100000，DISA1 候選 77413 另由正常原版底欄重建相同。偏移用途只作本次候選比對，不建立存檔 writer 或擴大格式逆向。

先記錄正常收入來源條件，再由 `power_funding_playtest.sh` 冷啟動 DISA1，透過原版 3 鍵與年度預算 Escape 返回，最多 120 次明示觀察；達 120000 才由原版正常保存 0001.SAV 及退出。保持原版資料、稅率、亂數與城市不變，不用注入資金解決施工條件。輸出 `power-facility-funding-native/`；實際結果另追加。

完整火力 AI 重繪候選已保存 `thermal-illustration-b-candidate-v1-generated.png`，SHA-256 `455fc25623838a3d1e23b1449d290b03e314ca910e33b1eb8c2acefb232c1f2a`，提示詞在同目錄。候選保留了三座主廠房及煙囪，但位置與附屬結構偏移，未接產品。新增 `power_facility_prototype.py`，由完整原始色號重建複合幾何，細緻葉面、沙地與工業筆觸只改呈現，先作離線實際尺寸比較。027 仍 DRAFT；正常核能成功施工、獨立原型核對及正式 HD 未完成。

離線原型首次呼叫誤用既有 `rgba(path,size)` 介面，輸出目錄尚未建立即停止；依實際介面修正，非產品或素材故障。收入首件保留 35 份正常觀察，第 35 份年度預算完整來源有效但 BIOS 未阻塞，工具假設「預算一定阻塞」而停止。回查 012，既有 `running-03/32` 同樣未阻塞且後續自行返回城市；因此修工具為此相位只觀察，只有完整預算且真正阻塞才送 Escape。原版 binary、image、速度與稅率不變，`power-facility-funding-native-r2/` 乾淨冷啟動重跑，前件保留。

## 2026-10-12：#46 火力 36 格接入與核能資金限制

接續載入規格閘門、GUI 還原及文件職責。r2 原預算正常觀察 120 次，年度後由 77413 降至 53221，未籌得核能資金。r3 改正常 F3 預算調整，但逐鍵兩份完整收據耗時過高，停止研究容器且保留原件。r4 分批 xdotool key 的 89 個命令只形成前端 87 組 make/break，原版恰讀 87；回查 `IsKeyJustPressed/Released` owner，短促按放可落在兩次 Update 之間。r5 改明示按下與放開各 0.2 秒，每八鍵停止並核對原版 Word、總數及 break；489 個方向鍵完整到達，實見稅率 10→30、四列 100→0。原版、400000 steps/update、速度與時鐘不變。

r5 正常觀察 240 次，年 113 月 7 至年 115 月 8，資金 77413→93775→98212；年度收入依次實見 16362、4437。未達成本 100000 或預登記門檻 120000，沒有 SAV 或正常退出完成聲明。結果及原件保留 `power-facility-funding-native-r5/result.json`。核能正常施工來源仍未知；不以改資金、改 SAV、延長相同探針或重擲挑結果填補，後續與其他 HD 批次分開處理。

火力完整來源探針 `power-facility-thermal-native/` 正常完成，40 個原版鍵、固定原點 (12,12)、6×6 原圖 (203,61,54,54) 通過。36 個圖像皆唯一別名 ROM38，索引 `12+30×row+col`，來源 SHA-256 `791fbfe53259ca39fe6dbd91ba4e2fa36009b7bc43d61e31b3d498b816dca558` 與首件部分來源相同。證據保留原始檔案／成員／像素偏移與色盤，不把相鄰未見圖像命名為核能。

完整 B 候選 v2、v3 的原圖與提示詞保存本機。v3 SHA-256 `16642276a2ba54203e2b745525e65ba92106698fc9ac9b1151720f621211aa2c`，在實際 216×216 目視保留 15 棵樹、三座廠房、五個紅黃色形狀、淡色直條與底部綠帶。前件 v1 的煙囪描述只指候選的新增構造，不作原版語意證據；該候選不採用。獨立重讀 ROM、來源收據、原圖、36 格切片與重組，2,916 項逐像素失配均拒絕。原型 78 檔及正式素材 2 檔乾淨重生逐 byte 相同。

027 僅將火力已見靜態 36 格升 READY，再接正式呈現；核能與其他相位仍 DRAFT。固定正式 manifest SHA-256 `bd571fa7a9ca49cbc8de1adde54cf1aa64642db4ff29bf158a567a75ca027c11`、atlas `ceb6c9a9dfe64330c4004c6492b6c0997fc84a2f8881688d506c44e481de8dc2`。完整／部分可見、全部區外、逐來源反例、已用／未用色盤與五種實際資源故障通過；全部 HD／鍵盤測試通過，HD 測試 91.186 秒。Linux 正常 binary SHA-256 `2821c65bfb4daad6e46677bb0c72b199c13f772c8eeae7262dbc17b2e69ee9d1`；Windows、macOS amd64／arm64 編譯通過，正式封包與真機另驗。

`gui-power-facility-cold-r1/` 正常施工達資金 29980、完整火力 36 格，F12 兩次均無 DOS 讀鍵或 DOS 按鍵新增。第二次切換後原版大游標在 (149,61,54,54) 自行閃爍，212 個變動像素全部在此，廠區沒有變動；全畫面跨時間相等的工具斷言停止，原件保留。r2 同程式、image 及遊戲參數乾淨重跑，增加十二次以內的無輸入游標閃爍對照、全部游標外相等與鍵盤隔離。正常捲動、存退讀、兩次退出及固定輸入原版狀態尚在驗收，不宣稱 CONFORMED。

Go 與 Python 各獨立重讀來源及 READY 前完整原型。有效負對照取 r1 真實完整火力收據，重算原版 PNG、呈現 PNG 與所有受影響雜湊；五項像素／切片／來源／回退區／統計破壞兩側皆拒絕，原件及未用色盤兩個正對照通過。前置衛生檢查通過 448 個相對連結、16 個新入口、Python／shell 語法、Go 格式、UID/GID 1000 及指定 find；最終清理與提交另追加。

### 游標原因判斷勘誤

上述「自行閃爍」是過早的原因判斷。r2 十二次無輸入觀察，至少 2.88 億步，原版畫面皆相同，因此停止。r1 三份收據的完整 inputs 差異只有兩個 theme 事件，沒有滑鼠或 DOS 鍵盤輸入；原版大游標矩形內的 212 像素變動仍是事實，原因尚未知。當前規格及現況已撤回自主閃爍的確定敘述，前件及原文保留供回查。

依 GUI 還原路由重新核對輸入 owner，F12 只改前端布林值及記錄 theme，呈現器只讀來源；這項程式檢查不代替執行證據。先在 #46 預登記 r1 的 3,936,000,000 步正常輸入收據及 audit binary 雜湊，再以 24,000,000 步抽樣重播無呈現與有呈現兩側，要求最終原版畫面、色盤、讀鍵及檔案操作符合 GUI 收據。診斷執行中，不宣稱原因已證實或正式玩家路徑完成。提交 d32b35d 已推送；r2 停止後無專案容器殘留，診斷使用一次性容器。

診斷完成：兩側各 3,936,000,000 步、164 個原版狀態抽樣點相同，最終原版畫面、色盤、讀鍵及檔案操作均符合 r1 收據。無呈現器側同樣重現該游標差異，因此 F12／高清呈現器不是必要條件。內部原因維持未知，不追加硬體或游標逆向。原版狀態 SHA-256 `4b9eb6d9e39664dab0257f8fe52d58f58ae87da7b83c702b75a5033704e3aa71`，結果檔 SHA-256 `a6d84f038c55c6bbc06ea0d861a0e439aa0e0a9e9596a2c4edec423d658b1a63`，高清抽到 36 個來源及 15 個火力畫面。無呈現／高清兩側依次 230.1／271.5 秒，診斷容器已自動刪除。

Linux 以 `go build -a` 乾淨重建逐 byte 相同，SHA-256 仍為 `2821c65bfb4daad6e46677bb0c72b199c13f772c8eeae7262dbc17b2e69ee9d1`，建置容器已刪除。r3 正常 GUI 預登記後啟動，使用相同 binary、image 及遊戲時間，只修驗證假設；要求完整游標外、廠區來源與非 theme 輸入相同，捲動逐一核對 36 格世界來源，再正常存退讀。凍結前件及本次腳本，不重用測試目錄。語法與 448 個相對連結通過；正式驗收仍在執行。

## 2026-10-12：#47 正常離開政績底圖的來源與 B 原型

先建立 #47，再從完整素材盤點的已見來源開工。直接重讀 ROM23／ROMA1，檔案偏移 193647／1568、長度 17587，兩個成員 bytes 相同。成員 SHA-256 `cc1e06a9ecaa3032c38f87ba14a1c70ccb5ccdeb5bd12421fdeca151c3ff40ef`，完整解出 320×200 色號 SHA-256 `0040b4374f37464862ae2f89da5bc897ddb7f53d539edd597cf8b2b6ff784ebd`。12,444 個單值及 1,713 個重複段完整消耗輸入，逐段保留原始與輸出偏移。四份正常退出收據來源及 23 個已用色盤相同，均為模式 0x13、等待輸入；後續正常退出轉模式 3。原版內部評分及取得政績後的變化未知，沒有擴大逆向。

使用內建 imagegen 依正常原圖重繪。原件 1586×992，SHA-256 `2dbdb09f57fe5324542117b2c00bc2b0d4ded4b24781594920f05663f6ad3284`，副本及完整提示詞保存 `workspace/prototypes/hd-style/ending-scene-b-candidate-v1-generated.png`／`.prompt.txt`，未覆寫原件。固定 Go CatmullRom 縮至 1280×800，再以 Noto 52 點重繪「您的政績」。四字均有 glyph，實際 4,459 字墨像素位於 (537,16)-(742,65)，完整在原四字安全矩形內，字色沿用原版藍色。已檢視實際完整畫面。

獨立 Python 使用另一套 ROM 解析器，核對兩個來源、四份正常收據、固定插畫、字型及授權；完整 1,024,000 個呈現像素、字墨外、四字實際墨跡及原版／B 比較通過。三個來源檔及五個原型檔乾淨重生逐 byte 相同，保留 `ending-scene-native-repro/` 及 `ending-scene-v1-repro/`。DRAFT 028 建立後完成證據審查，只將已見完整靜態底圖升 READY，其他變化及動畫仍 DRAFT。

正式素材匯出兩檔至 `ending-scene-ready-v1/`，manifest SHA-256 `009fcda9e87d5fcea175ae3112a5a5a610b04833a0d278f2e68b99dd4311ef57`，完整 PNG `b37fddad8ea9cc3bbc505af3a3daad1f5cb59e86c213d98d12bbf279da81cfb0`。這批只完成來源與原型，未接產品，不宣稱 GUI 或 CONFORMED。工具入口同次加入 CONTEXT。來源、原型與重生容器均已刪除，目前只有 #46 的有界正常 GUI 容器；原版及衍生素材未加入 Git。

## 2026-10-12：#46 火力靜態 36 格達 CONFORMED

r3 完整正常 GUI 通過施工、兩次 F12、兩軸捲動、36 格同世界原始來源、返回原點、存檔、兩次原版退出及全新 EXE 冷讀。讀回完整火力 36 格、電線與資金 29980。實際 SAV 在 `gui-cold-saves.zsEQND/ROUND4.SAV`，93567 bytes，SHA-256 `1b7522328f296547dfc1505fd408c04c486c9b23ceed1a8c49a4d2ff66b4972c`，與預登記及權威 result.json 相同。Python／Go 全部 162 份原子收據通過，93 份實際覆繪火力，Go 完整逐像素核對通過。先前五項有效破壞及兩個正對照保留。

正式唯一輸入先在 #46 預登記，再完整執行兩側各 8,064,402,774 步。336 個原版狀態抽樣相同，實際覆繪 164 個火力畫面及 36 個來源，最終原版畫面、色盤、讀鍵、檔案操作符合 GUI，落地 SAV 與實際保存相同。狀態 SHA-256 `df7b442241b71a292822bd4162d7a14a591c870bad80c28ba8e80fe336deda36`，結果檔 SHA-256 `0321c247af7e451f0d26ed6fc38ef276730e72741f509fd4eecb1fa6613a6c90`。兩側 513.8／499.6 秒。此結論以已登記的 binary／audit 版本及正常路徑為界，不宣稱逐幀、核能、其他相位或全部 HD。

收尾總核對 `power-facility-thermal-native/final-verification-r1.json` 通過：原始 35 檔、7919834 bytes 及 RAR 雜湊不變；Linux 乾淨重建相同，Windows amd64 與 macOS amd64／arm64 編譯及結構通過，真機未驗。輸出 UID/GID 1000，指定 find 為空。實際正常畫面原件 `normal-power-hd-r3.png` SHA-256 `2a89a2ccefa5515bf0f062898c7fa3c961e20fc5940f862d354fd4898e45b5b4`，直接取自正常收據，與先前畫面 bytes 相同，沒有後製。Docker 已無專案容器殘留。依規格路由審查後，只將 027 靜態火力升 CONFORMED；核能及其他相位未完成，#46 保持 OPEN。

## 2026-10-12：#47 政績底圖呈現與獨立核對接入

028 READY 後接入完整底圖呈現，完整來源 SHA、模式 0x13、阻塞、23 個已用色盤、固定 manifest／PNG、字型及授權均符合才覆繪，來源失配或素材故障完整回退。F12、模式 3 及其他城市家族隔離有測試。首次測試誤將 `image.Image` 當 RGBA，修正測試參考型別並保留 r1 編譯失敗紀錄；r2 的完整／來源／23 色盤／九種實際載入故障／家族隔離 16.160 秒通過。全部 HD／鍵盤回歸 116.613 秒通過。

Go／Python 獨立核對器直接讀原版與 READY 前完整畫面，已接整張像素、家族及回退檢查。準備七項有效破壞與兩個正對照，等待實際新 GUI 收據，沒有以合成收據冒充正常原件。正常 GUI 工具已加入兩次退出各自 F12、完整非 theme 輸入及讀鍵隔離；原版狀態工具加入 `-require-ending-screen`。新 audit 編至 sibling `presentation-audit-ending-r1`，沒有覆寫 #46 的已登記 audit。正式兩檔素材乾淨重生也逐 byte 相同。

本批尚未重建前端、執行正式 GUI、有效負對照、固定輸入狀態或四平台驗收，因此仍 READY。目前無專案容器殘留；全部新工具及來源已同次加入 CONTEXT，原版及衍生素材不入 Git。

## 2026-10-12：#47 正常驗收啟動與 #48 圖表來源入口

提交 `70fc29dc91a3422b97554c219c59f8b7fc42fc71` 已推送。#46 正式結果已回鏈，完整 Issue 保持 OPEN。#47 新 Linux SHA-256 `3df9783e2ca9229666f0f49b5fda9647b5bd94cf4271afc53a723d91acf46654`，固定 image、400000 steps/update 與兩次政績 F12 先預登記遠端，才啟動 `gui-ending-scene-cold-r1/`。Windows amd64、macOS amd64／arm64 編譯退出 0；Linux 乾淨重建比對中，GUI 結果另追加。

先列舉遠端，再建立 #48。讀既有交通密度正常原子收據，圖為縮小城市與兩側色帶，不將下拉選單或入口名稱當作完整圖表語意。新增 029 DRAFT 與六個正常入口探索工具，同次掛入 CONTEXT。只經原版 DISA1、暫停、F4／Down／Space／Escape 取得來源，原版資料、時序及數值不變；正式 HD 尚未接入。預登記及探索結果另追加。

#47 第一個正常退出完成，政績完整來源與 F12 往返通過。七項重算 PNG／雜湊的有效破壞雙側拒絕，兩個正對照通過。固定第一退出收據 SHA 與 3,000,802,774 步已先回寫遠端，再啟動兩側原版狀態重播；完整 GUI 冷讀仍執行中。Linux 乾淨重建相同，四架構與 35 原始檔／RAR 完整性通過，見 `ending-scene-native/build-input-integrity-r1.json`。實際正常政績 PNG 直接自收據擷取，與 READY 前固定原型逐 byte 相同，沒有後製。

#48 r1 首入口與兩次無輸入觀察通過。Escape 由原版 `int21-AH07` 讀入 ASCII 27、Word 0，且已返回原城市；工具卻等待 BIOS Word 0x011b，120 秒後逾時。回查 GUI 還原路由，分類為驗證讀鍵 owner 假設錯誤，原件與凍結腳本保留；只修本批圖表返回為已證實 DOS 控制台讀取與 release，r2 同一程式／image／參數乾淨重跑。ROM4–10 的中央 105×89 以外 9070 色號完全相同，既有交通密度九份完整框架匹配。MIN／MAX 的原 ASCII 字模掃描沒有匹配，嵌入字形來源仍未知，不猜原字庫或繪字呼叫。

## 2026-10-12：#47 靜態底圖達 CONFORMED

完整 `gui-ending-scene-cold-r1/` 退出 0，兩次正常原版退出及政績 F12 往返通過；全新 EXE 讀回原施工格及資金 79980。50 份正常原子收據全部由 Go／Python 核對，4 份實際政績覆繪；七個有效破壞雙側拒絕，兩個正對照通過。固定原版狀態兩側各 3,000,802,774 步、125 次抽樣相同，六點覆繪政績，最終 GUI 原畫面、色盤、讀鍵及檔案操作一致。原版側 221.223 秒、高清側 213.623 秒，狀態 SHA-256 `d49e1d61592afb3dbf77e7787b5ee9e10c6af9bc8cfb5ccf5f724eb2a7dfd3d6`，結果檔 SHA-256 `ae4c6b201dad45516539f1de345c3b0457600dc6c3c93a83d28bafaf841fb6f9`。

本次 SAV 路徑經完整 result.json 再核對為 `gui-cold-saves.GR4gqL/ROUND4.SAV`，93567 bytes，SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，與預登記及重播落地相同。四架構、Linux 乾淨重建、35 原始檔及 RAR 不變通過。`ending-scene-native/final-verification-r1.json` 彙整完整閘門，實際正常 PNG 與 READY 前固定畫面 byte 相同，已檢視，無後製。

完成前回查規格閘門，028 只升已見靜態底圖 CONFORMED，同步 CONTEXT、README 及矩陣。原版／衍生素材／字型／SAV／收據不入 Git，其他政績及動畫留母項 #32。本批 Docker 全退出刪除，指定 find 為空，輸出 UID/GID 1000；此刻只有 #48 的新來源探索容器。提交、回鏈與 #47 關閉結果另追加。

## 2026-10-12：#48 選取來源勘誤與 r3

r2 六次開圖／返回與 60 份原子收據完整像素通過，Docker die event 為 exitCode 0、355 秒；工具工作階段回報 143，按外層狀態差異記錄，未重跑同一成功流程或列產品缺陷。原型前逐一用 022 固定完整選單來源核對，實際選取為 0、1、3、0、4、3，只有四種入口。F4 重開保留前次選取，原工具錯當每次從 0 開始；r2 result 名稱只代表意圖。撤回六入口完成說法，原件保留，修正 CONTEXT、029、矩陣及遠端 #48。

回查 GUI 還原路由的入口、選取與呈現分離規則，r3 先以固定完整選單 SHA 辨識當前選取，再正常 Down 至指定入口，每一步及確認前皆核對，沒有座標或狀態注入。原版／binary／image／步數／上限不變，預登記後啟動全新 `chart-windows-native-r3/`，尚未正式 HD。兩次假設失敗均先查原始收據，不調參數填補。

直接核對嵌入 bitmap，MIN／MAX 實為 5×5，四組共 138 個色號 14 像素；與 ROM4–10 完整相符。此為可見墨跡證據，未解 ROM56 或 EXE 繪字呼叫。33 份共同框架及四種資料圖像仍有效，完整六選項及資料契約待 r3。

## 2026-10-12：#47 關閉與 #48 READY 原型

提交 `3e2c6c02821f3c3f2b59aff28051bedc73ebbf75` 已推送。#47 的完整靜態底圖結果回鏈 `issuecomment-6114530379`，遠端已回讀 CLOSED；其他政績及動畫仍留 #32。未重新執行已完成的火力、道路或底圖驗收。

#48 r3 完整退出 0。固定完整選單核對實際六選取，12 次無輸入觀察穩定，六次 AH07 Escape 回復完整原城市，56 份正常原子收據由 Go 核對通過。33 份完整框架含六種資料，`source-all-r3.json` SHA-256 `e252c062e832405d3d4a0c65ffbb7a7e694c3c76982b2b366d54b5f12d578f92`，乾淨重生相同；原失敗與選取勘誤保留。進度回鏈 #48 `issuecomment-6114705743`。

首版 Noto 24 點可讀但灰框仍像放大原版，未接產品。使用內建 imagegen 參考原圖及既有 B 筆觸，重繪灰石外框，原件 1341×1173、SHA-256 `109e7da267bed6a0b9dcb9baa0872bb3b5f1b0e1fa0ab1e8b532a82d99f41738`，原件／提示詞／metadata 保存在本機 workspace。v2 僅在完整原版灰框遮罩接受中性灰插畫，共 121432 像素；2120 個生成彩色越界像素回退筆觸。地圖、色帶與文字不採生成內容，四組 Noto 實際墨跡完整在原安全矩形，總 1722 像素。已檢視完整交通圖表原型。

獨立 Python 完整核對六圖各 1,024,000 個 RGBA、原 ROM、實際選取、資料格、遮罩、字墨與全部區外；42 檔乾淨重生逐 byte 相同。首次核對誤要求完整 256 色盤相同，直接重讀確認只有四個未用項 232／233／240／241 有兩種原版值，實際用色完全相同。修正驗證假設，沒有改產品、原版色盤或收據；兩組完整色盤證據 `palette-audit-r1.json` SHA-256 `392dc069f4c39632d14c3991c7f2b0e4f11e5dcf6084b397b744f39caad17473`。

回查規格閘門後，029 只升固定框架與原版資料像素呈現 READY，不重寫統計公式。正式三檔匯出及乾淨重生 byte 相同，manifest SHA-256 `9a0cc44ee54ea2b2681c6e578a00ac532be32b9d88780cc9c90579fe4766226e`。接入原位圖框、透明資料區、固定筆觸及 Noto，完整框架／已用色盤／相位／素材失配完整回退。首輪編譯因檔名 `_windows.go` 被 Go 解讀為 Windows 專用而漏入 Linux，改名 `chart_panel.go`／`chart_panel_test.go` 並同步入口，原失敗 log 保留。r2 六完整原型、資料單格更新、色盤、相位／F12、十一種實際載入故障與家族隔離 13.970 秒通過。

新增 Go／Python 整幀獨立核對及正常存退讀六圖表工具，同次掛入 CONTEXT。Linux 已重建，SHA-256 `a7baf0b205bad28d65b3585e07ad6be30ccf836127d508cd72e3cd4a087ef5e9`；全部 HD／鍵盤回歸及新獨立工具建置正在執行，正式 GUI、有效負對照、固定狀態及四架構驗收尚未完成。本批仍 READY，#48 OPEN，全部遊戲 HD 與正式交付未完成。

## 2026-10-12：依使用者指示先提交與推送

使用者暫停目標並指示「不用抽樣囉，先 commit + push」。停止後續玩家路徑與抽樣工作，只整理目前可 review 的原創程式、工具及文件。尚未啟動正式圖表 GUI、有效負對照、原版狀態或跨平台驗收；029 維持 READY，#48 OPEN，沒有將未驗項視為完成。

先前啟動的完整回歸已結束：HD 套件 155.967 秒，圖表專項仍通過；預算測試指定的 `/workspace/runs/budget-native-source-ready/catalog.json` 不存在而失敗。城市與工具面板因未設定來源環境變數而略過，鍵盤套件 0.009 秒通過。這是本次驗證輸入設定問題，不宣稱產品缺陷或完整回歸通過；原件 `full-render-test-r1.log` 保留，依指示未重跑。兩個新 Go 獨立工具已成功建置，七份相關 Python 語法核對通過。

提交前逐項審查明確檔案清單，原版、字型、衍生素材、binary、SAV 與收據均不加入 Git。`git diff --check` 通過；Docker 指定 find 為空，已無專案容器殘留。提交及 push 結果回鏈遠端 #48。

## 2026-10-12：#49 HD 五語系初稿與操作原型

先前停止點已提交並推送 `c4e6e967a9cc7243c39e3cc4642596e9f9001bee`。使用者另追加繁中、簡中、日文、韓文、英文。先回查知識路由，載入顯示與語意隔離契約、共同決策技能及文件職責。主機 gh auth 成功，回讀全部遠端 Issues 後先建立 #49，才調查現有文字與字型。

使用者已確認「HD 模式提供五語系，原版模式保留繁中」。新增 030 DRAFT、92 鍵 UTF-8 TSV 初稿及獨立離線 locale-prototype，同次更新 AGENTS、CONTEXT、README 與驗收矩陣入口。修正 CONTEXT 頂部仍稱持續整體驗收的舊文字；本次只做多語系分支，沒有重啟 #48 正常 GUI 或長時間原版狀態抽樣。原版資料、產品前端及正式呈現器均未修改。

沿用固定工具 image、Go 1.24.13、Noto TC Sans2.004 及 #47 的真實 HD 收據。92 鍵五個完整欄位、641 種字元、43 處實際墨跡與五張完整原型全部區外像素核對通過。原型保留原安全矩形，以字級縮小容納英文；Environment 為 21 px，閱讀舒適與正式排版尚未定案，未宣稱全遊戲翻譯完成。

八個原型檔乾淨重生逐 byte 相同，八項真正破壞的負對照皆因指定原因拒絕，收據在 `workspace/prototypes/hd-style/locale-validation-r1/validation.json`。首次臨時 metadata 讀取將 scenes list 當成 dict，修正讀取型別後完成；首次 heredoc 檢查漏加 Docker `-i`，沒有執行程式，修正 stdin 轉送後以同一 image、輸入及命令乾淨執行。兩者均屬研究命令問題，沒有修改產品或放寬門檻。

已展示五語系標題與 F11 操作原型，詢問遊戲中切換並記住選擇，或只在啟動時選擇。尚未收到操作決定，不把原型接進正式路徑。圖片含原版／衍生素材，只留本機；TSV、原創工具與文件可提交。所有可寫 Docker 使用 UID/GID 1000，輸出抽查一致；本批一次性容器均退出。提交與遠端回鏈結果另追加。

## 2026-10-12：F11 確認、第一批接入與 Help 原型

先前初稿已提交並推送 `d718dbef17e5bac818de0313b079f6fd988da49e`，遠端 #49 留 OPEN。使用者看過原型後確認「遊戲中切換」，另要求 Help，提出 F1 候選。本輪回查翻譯隔離、規格閘門、文件職責與正常玩家驗證入口，先在 #49 回寫確認，再建立 #50 才研究 Help。原版 F1 已是離開／返回 DOS，022 及正常路徑均有證據；不把 maybe 視為覆蓋原版按鍵的授權。

新增十張五語系 Help 操作原型、111 鍵唯讀文字快照、733 字元與 223 處實際墨跡檢查。向使用者展示 Shift+F1 Help 保留 F1，或 F1 Help 將原版離開移至 Shift+F1；待回答前沒有攔截 Help。031 DRAFT 與 CONTEXT／AGENTS 入口同步。快照 SHA-256 `3e8615479950f17da1cb3f33d284f0270449fb3174b75938f18847ce5cc74784`，與產圖收據一致，僅留本機。

030 限 F11、設定與六標題先審查為 READY，再接入前端。所有新譯文來自唯一 TSV；外部文案可修改而不重編譯，無效來源回退同 TSV 的隨附 catalog。設定存於獨立 `frontend-settings.json`，不以譯文改規則、資源名稱或 SAV。面板內暫停 VM、隔離輸入，開啟時配平已送出的按鍵放開，關閉後等實體按鍵放開。六標題保留來源閘門，繁中原字墨不變；其他語系只在原矩形縮字置中。建置工具同步匯出外部 TSV。

必要測試通過：catalog／設定 0.004 秒、五語系標題完整像素 0.420 秒、實際 Noto 面板／錯誤提示／透明區外／資源故障 0.198 秒；原鍵盤測試通過。正式 TSV 為 115 鍵、761 字元，SHA-256 `afe340850774c2b579b8808e7eac1c89dd24e4332ff978b511157fa258ab59ab`。

正常 GUI 預登記於 #49 `issuecomment-6117951475`。首次工具缺 PIL，尚未啟動遊戲；改用同一 image 已有的 ImageMagick，不安裝主機依賴或改產品，再以同一輸入乾淨執行 r1。兩次全新 EXE、不用 checkpoint，第一個由片頭／主選單走到城市，五語系各驗六標題完整像素、面板內 CPU／步數／原畫面／色盤／原版讀鍵／檔案操作不變、F12 往返、設定落地、原版 F1 及滑鼠選英文。第二個全新 EXE 從設定讀回英文，實際標題及面板為英文，Esc 取消不保存新選擇。`locale-ui-cold-r1/verification.json` 通過；已檢視實際城市英文及全新啟動英文面板。

驗證 binary `taipei-preview-locale-r1` SHA-256 `73820b7ae8d23318e2773cb7387c0c4b71592b4b22f2ac6f54f541a0a8858938`。本次用 stop-file 有界收尾，沒有 SAV 存退讀、原版正常退出、舊圖表 GUI 或長時間原版狀態抽樣。持鍵／IME、真實視窗錯誤與跨平台未驗，030 第一批保持 READY，其他文字家族仍 DRAFT。#49／#50 維持 OPEN；沒有宣稱全遊戲翻譯或 Help 完成。現行 Linux 入口另以正式建置腳本重建；Docker 清理與提交推送結果回鏈遠端。

現行 `workspace/runs/taipei-preview` 由建置腳本重建後，與已驗 binary 逐 byte 相同，外部 `locales/ui.tsv` 也與正式來源相同。文件索引以既有 029 為正對照，所有新增檔案入口與路徑存在通過。指定 find 為空，新增程式、文件及輸出抽查 UID/GID 1000，所有本批容器均退出刪除。提交僅明確列出的原創程式、TSV、測試、建置工具與文件；原版／字型／圖片／收據／binary 不入 Git。

## 2026-10-12：Shift+F1 Help 確認與接入

前一批 `8dcfcaca76132d7bf9265b87d82cb196f94f2313` 已提交並推送。使用者對已展示兩方案回覆「同意」，採建議方案 Shift+F1 開 Help、原版 F1 保留。主機 gh auth 成功，回讀 #50 後先留言 `issuecomment-6118213230`，將 031 審查為 READY，再開始產品實作；同步遠端 Issue 主文，沒有重問已確認決定。

本輪命中並載入本地化顯示隔離、規格閘門及文件職責，完成結論前回查規格閘門。Help 全部文字沿既有唯一 115 鍵 TSV，沒有新增另一份譯文；Noto、OFL、版面與八列操作沿已展示固定原型。新增 localui.Help，與語言面板共用排版及啟動驗證；左右 Shift+F1、Esc、F11 回 Help、F12、前端收據及輸入放開隔離接入。關閉隔離改為檢查所有實體鍵，包含未轉送的鍵與滑鼠中鍵；不改原版模擬。

必要測試通過：五語系 Help 面板逐像素及區外透明、缺鍵／缺字／超長按指定原因拒絕；實際 Noto／OFL、語言面板、catalog／設定、鍵盤及六標題回歸通過。命令為固定 Docker image 內 `go test -mod=readonly -p 1 ./internal/localui ./internal/i18n ./internal/keyboard`，以及 HD 套件限定 `TestFiveLocaleLabelsAgainstDiscardableReference`。最後 Help 測試結果另存 `workspace/runs/help-unit-final.log`。沒有重啟舊完整 HD 回歸或 #48。

`help_ui_playtest.sh` 在預登記後使用同一工具 image、全新 EXE 與正常視窗輸入，沒有 checkpoint。片頭／主選單／城市正常路徑後，先轉送左右 Shift，再開 Help，收據確認配平 AAh／B6h；Help 開啟及關閉沒有穿透 F1。Esc 關閉仍持住 Shift+F1 時 VM 不動，全部放開後 BIOS Shift flags 歸零。Help 內 Tab、方向、Enter、Space、F1、abc 文字及滑鼠不穿透，F11 五語系各回 Help 並保存設定，取消保留原語言。五個面板固定像素、F12 往返及原版模式全部區外同幀原畫面四倍像素通過；同鍵關閉後原版 F1 開離開選單、Esc 返回及原版控制通過。Help 中 CPU、步數、原畫面、palette、BIOS ticks／修飾旗標、原版讀鍵及檔案操作不變。`help-ui-cold-r1/verification.json` 通過，已檢視實際英文 Help。

Linux 已驗 binary SHA-256 `6604e3d0c611f8744c56d0f0f679986680d5cb3a5a6d3e3968550bb22f487ad8`，保留為 `taipei-preview-help-r1`；現行入口及外部 TSV 相同。Windows amd64、macOS amd64／arm64 建置及 PE／Mach-O 架構通過，雜湊見 031 與 `preview-cross-*.txt`。Windows 建置出現未修改 YMFM C++ 的邊界警告，退出 0，未擴張為音訊修正。沒有 Wine、Windows／macOS 真機、SAV 存退讀、原版正常退出、長時間狀態抽樣或正式包；031 只限已驗八列 Help 與前端輸入達 CONFORMED，#49 完整翻譯仍 OPEN。

本批所有新增檔案同次掛入 CONTEXT，README 增加四個穩定按鍵入口。Docker 清理、擁有權、提交及 push 結果在本批收尾後回鏈 Issue。

收尾直接回讀同次原子收據，確認原版已消費 Tab 的 BIOS word `0F09h` 與右方向 `4D00h`，均在 F1 返回之後；驗證工具同步改為等待實際讀鍵，不只檢查轉送紀錄。沒有重跑已通過的 GUI。文件索引以 029 為正對照，所有新檔入口及文件相對連結存在；Linux 現行 binary 與已驗副本、外部 TSV 與正式來源逐 byte 相同。必要 Help 最後專項 0.590 秒通過。

原始 EXE／RS201.ROM／RS201A.ROM 雜湊與基線一致。首次收尾命令誤寫 `RS201.ROMA` 而中止，核對實際檔名後完成，屬檢查命令問題，產品與原始資料未變。新增程式、工具及輸出抽查 UID/GID 1000，指定 find 為空，所有專案容器均已退出刪除。明確提交清單只含原創程式、測試、工具與文件，沒有原版、字型、圖片、收據、binary 或 SAV。

## 2026-10-12：其餘介面五語系翻譯

使用者要求繼續完成其餘介面翻譯。主機 gh auth 成功，回讀 #49 與現行 Issues 後，先建立 #51，再開始 032 規格及產品實作。命中本地化顯示隔離、規格閘門與文件職責，已載入相應契約及復古遊戲研究技能。後續 GUI 同步問題另回查正常玩家路徑路由，載入 `retro-game-playtest.md` 與現有城市選單的原版讀鍵／release 回證工具。未改 dosgolem 上游或恢復 #48、長時間 RAM／亂數抽樣。

032 先限既有來源達 READY，再分離固定 B 底板與 TSV 文案。接入全部 60 種既有選單狀態、三段新遊戲說明、底部單位、離開確認、預算靜態欄、圖表 MAX／MIN 及政績標題。稅收與淨額保留兩欄，原數字、百分比、正負號及玩家檔名保持原樣。功能視窗開啟時，各自核對六標題及底部來源，避免背景仍露出繁中。修正 JSON 選取顏色欄位標籤，並加入原紅字選取的排版檢查。

正常來源追加查證 ROM12／13／14／18。人口六組數字、民意十一組數字及人口等級完整重建，兩個視窗零差異；速度選取與訊息速度也零差異。從正確主選單 Right 入口取得六種災難城市，原字碼、字模、色號與完整面板均零差異。確認後先追加 032 READY，才接入五語系。22 個固定訊息的 EXE 檔案偏移與 bytes 已核對，正式來源碼和可編輯譯文分開。追加家族只核對實際 39 色；正常災難城市的未用色盤會變化，已保留正對照，沒有修改遊戲色盤。

正式 TSV 為 181 鍵、927 種字元，雜湊 `51a713f5499974ea30ff59d5902606b04cede9d4bbb99823c5034f800d73fa88`。實際 Noto／OFL、五語系 Help／F11、catalog／設定／鍵盤通過；五語系各 77 種來源狀態、原版色號不變、預算及人口／民意原數字像素、來源／色盤破壞、未用色盤正對照、F12 原版、缺鍵與超長回退通過。完整結果為 `interface-locale-unit-final.log`，97.762 秒；獨立來源 catalog 雜湊 `c2fcedc4742b6ab55815ca5409942a95cf5023cb42e3f9da8be38661108d95d9`。已檢視英文人口／民意、日文災難城市及主選單排版。

正常 GUI 前件保留。r1 錯把 F11 關閉後已恢復的 VM 步數納入模態凍結檢查，改為比較面板開啟期間。r2 在速度視窗誤用 Escape；r3 與大量 PNG 輸出同時跑，片頭只達 6.5 億步即遇驗證逾時，改成分開執行。r4 誤用主選單 Down 且假定城市 Escape 可返回；以既有正常控制紀錄更正，r5 正確取得災難分支。r6 的人口／民意五語系及 F12 全畫面原版通過，後續環境警告尚未結束便送 F6，原版未消費該鍵。驗證工具改為逐次等待原版讀鍵與 release，沿既有 #34／#41 的方法，用同一 binary／image 乾淨重跑。以上是驗證工具問題，沒有產品修正或加速原版流程。

r7 將普通空白鍵持有至週期收據更新，觸發 X11 文字自動重複。已依現有工具分開普通鍵短按與方向／功能鍵消費確認。r8 在人口視窗等待額外 VM 步數，但原版此時已阻塞讀鍵；已將阻塞狀態視為穩定來源，只等待 release 收據。兩次均屬驗證同步錯誤，未改產品，保留輸出並清理容器。

r9 正常工具子選單、英文 Help、人口／民意五語系與三個場景 F12 通過。環境難度警告逐字顯示後自行返回，測試額外送的 Space 被工具列讀取並開啟道路子選單，後續 F6 因模式不同而無法開環境。已查到實際原版讀鍵與完整訊息來源，移除錯誤的確認操作。r10 使用相同 binary／image 從全新冷啟動驗環境完整提示、預算與存讀檔，不重複已通過的工具／人口／民意；逐字中間畫面依既定來源閘門回退，另記 #49。

r10 五項環境完整英文提示、預算五語系、實際存檔與原版讀回通過；後續仍以定步數斷言尚在逐字顯示的離開提示，驗證失敗。已沿相同完整來源閘門等待 `quit-confirm`。r11 以 `TAIPEI_INTERFACE_PHASE=files` 從全新冷啟動完成新遊戲、英文 F11、LOCALE 檔名保留、93567 bytes 實際 SAV、同次讀回、存檔／離開提示 F12 完整原版、英文政績標題與原版返回 DOS。十四次讀鍵／release 通過；不是全新 EXE 冷讀。r9／r10 只作此前已核對的分段正面收據，不稱整輪 PASS。

`interface-locale-cold-r11/verification.json` SHA-256 為 `0392a2077014272838a569c6c922a74588c714125bebfd18ea985099f6f28949`。SAV SHA-256 `4152f923daa7535fbd49b6d6cabb780c1ef3b6a4cd3f8bd8c91395ca2a123b4c`，讀回後不變。已檢視實際英文民意、檔名及離開確認。正常 GUI 的控制錯誤均留存前件，產品 binary 在 r6 至 r11 之間未變。

Linux 依固定 dosgolem 與七份既有補丁乾淨重建，SHA-256 `c99f17bd03354972ce77346613ba2e1887e361690ac27c5979cf2473a8ab084a`，與已驗副本逐 byte 相同；外部 TSV 與正式來源相同。Windows amd64 雜湊 `3e2a558c994a6ea08091e3785fb15fd12aad852699155cfa2a2bd6b46c143295`，macOS amd64 `e3906562dfc509182c0a3a41d9972d3b384606dd919e6b2e5993dc107b5fc9b5`，arm64 `61338c3fa6d5b877a821b44c036d68cc1c1dc9990a9936c10ffdae262b2bcc37`。PE／Mach-O header 與 Linux Go build metadata 的四架構通過；Windows 仍有未修改 YMFM C++ 邊界警告，建置退出 0。未做 Wine、Windows／macOS 真機或正式封包，不提升 #48 完整 HD 驗收。

收尾回查 README 現況與文件職責路由，更新唯一現況表、032 CONFORMED 的範圍、README 與驗收矩陣。原始 EXE、RS201.ROM、RS201A.ROM 與基線雜湊一致。主工具 image 沒有 `file`，改核對既有 PE／Mach-O 匯出與 Go metadata，屬檢查工具問題。新檔同次掛入 CONTEXT，029 為路由正對照，文件相對連結通過。指定 find 為空，所有專案容器已退出刪除；未建立 image，無需清理其他映像檔。提交只含原創程式、TSV、測試、工具與文件，原版、字型、素材、收據、binary 與 SAV 不入 Git。實際提交／push 與 Issue 狀態以 #51 收尾留言回鏈。

## 2026-10-12：完成 #49 的剩餘五語系來源

使用者明確要求繼續完成 #49。主機 gh auth 成功，回讀遠端後先建立 #52。命中本地化顯示與語意隔離、復古遊戲規格閘門、正常玩家路徑與文件職責路由，載入必要契約。文字來源追查另使用既有 IDA Pro 9.4 image，唯讀資料庫複製至 workspace/runs/ida-52，不修改 dosgolem 上游或原始資料。沒有恢復 #48 或長時間 RAM／RNG 抽樣。

IDA 靜態指令確認清列、逐字進度及發布時機；原版 dosgolem 冷啟動取得開場／上任信 156 個文字階段、城市訊息 36 個階段，獨立 Python 重讀 ROM 字模逐項相同。完整 EXE 字串區的 146 筆可讀中文都已對應譯文，另查出 ROMA 38 的 IV2 小標題。九筆圖片文字涵蓋大小標題、抗議四筆動畫來源、百貨兩筆及銀行。商標與無法辨讀的證書裝飾保留，不猜造原文。

033 先完成來源、原型及字墨審查，升 READY 後才接正式前端。原版觀察器只讀完整來源、原始參數及已完成位元組數；翻譯以整句固定排版再顯示前綴，原版動畫及等待不變。圖片文字逐框比對原始來源與呼叫前後緩衝，失配或裁切保留原版。修正透明小標題重複繪製時背景已含原字形的問題：僅在整個前次合成完全相同時保留乾淨背景。抗議牌另追至 sub_12BDA／sub_16210 的實際裁切契約，完整文字框落在裁切區才覆字。

初步將 EXE 245C4h 視作啟動錯誤的說法撤回。現有資料只證實原始 bytes 與指標表，沒有足夠呼叫端證據，改記未知用途。密碼與版權來源仍保存譯文；正式 /A /D /x 不啟用密碼流程。成功結局兩列及未完成提示已核對 sub_12128／sub_12420 的清列與呼叫參數，五語系合成測例通過。未完成提示有正常退出呼叫，成功結局未走完整玩家流程。

唯一 TSV 為 225 鍵，五語系欄完整；SHA-256 4ae6a237fe96d09411860d4e55156b922acc26f1bccca5431eeef094a1b92ad9，實際 Noto／OFL 檢查 1213 種字元。既有各語系 77 種來源狀態、數字及檔名隔離回歸通過。新增測試驗 156 個開場階段、36 個城市階段、九筆圖片、三個結局合成測例、單像素／裁切破壞、未知來源、ROMA 故障、完整上任信與正式 Render／F12。逐字實際字墨另驗零／半／完整進度、安全矩形、固定位置及超長譯文完整回退；觀察器驗記憶體、暫存器與步數不變。結果在 localization-production-unit-r2.log、localization-source-unit-final.log、localization-reveal-unit-final.log 及 localization-core-unit-r2.log。

GUI 前件保留。r12 的空來源陣列被 JSON 編成 null，驗證程式未處理；r13 只記最後一個已繪文字框，誤判其他招牌未出現。改為記錄全部文字鍵。r14 正常開場、F11 韓文、環境、五語系預算、英文存讀檔與原版退出通過。追加抗議裁切入口後，r15 使用現行 binary 從全新 EXE 完整重跑通過：取得全部三十個開場／上任信鍵及五類圖片文字，途中 F11 改韓文，面板內 CPU、步數、原畫面、色盤、讀鍵與來源進度不變；F12 面板外兩側原版像素相同，檔案與離開視窗另驗完整四倍原版畫面。

r15 亦取得英文城市提示的實際中間相位，驗環境五項、預算五語系、LOCALE 檔名保留、93567 bytes 原版 SAV、同次讀回及正常返回 DOS，共 33 次原版讀鍵／release。SAV SHA-256 d338d3a1418fedb41e13f38efb34ac462d34317430861669a1abafabc7536de8，讀回後不變。主收據 SHA-256 c7f23b6d0c00b58b64cb4d261e91f309cb73abfc1bbbdeaf3cf76369e2d43478，開場收據 573e2073b7b309a8eed7418eca32eafa5168431a44e521ba56ec1cf251324c7d。沒有 checkpoint 或全新 EXE 冷讀。

r16 的缺譯測試以英文啟動，驗證程式仍搜尋中文視窗標題而失敗。改用實際 PID 聚焦，r17 乾淨重跑通過：有效外部 TSV 缺 intro.date 時回退隨附 TSV、開場正常翻譯、F11 顯示英文資源警示，原版輸入不穿透。收據 SHA-256 d41c06c73ae6d4efeda77bc12a73d9f51effe87bbe23850bfaa3df8a9e4481d7。這是驗證工具修正，不改產品。

Linux 已驗 binary SHA-256 1461ac4b4a2fe582f3c937a9f6d84edca34d09562a236a0f1472895f088ec2c8，同來源重建逐 byte 相同。Windows amd64 1506be424369c922a3f7c39a7337252f0388c65eed6b61773a879fbfe775e589；macOS amd64 32fea91049a2911d9e91210393af3dcd7ecd59e1c6dc8930782135cadbcc9b5f；macOS arm64 97d3857bdc3bd152ecda24f54a76c42b76c0785fb54c2e681d8f89dc2f54d344。四架構編譯與 ELF／PE／Mach-O header 通過。Windows 仍出現既有 YMFM C++ 警告，建置退出 0；未修改該第三方元件。未做 Wine、Windows／macOS 真機、IME、母語人工審校或正式封包，不外推全部圖片 HD 完成。

收尾重新核對本地化、正常玩家路徑與文件入口。033 限已核對來源及正式啟動範圍升 CONFORMED，更新 030、唯一現況表、README 與驗收矩陣。029 作文件路由正對照，新文件及新工具皆有入口，相對連結通過。35 個原始檔與 RAR 雜湊保持基線；來源與平台完整雜湊保存於 localization-final-provenance.json。指定 find 為空，專案容器均退出刪除，沒有新 image 或遺留背景程序。明確提交清單只含原創程式、TSV、測試、工具及文件；原版、字型、圖片、收據、SAV 與 binary 不入 Git。提交、push 及 Issue 最終狀態於遠端回鏈。

## 2026-10-12：README 原版與 HD 五語系截圖 #53

使用者要求繼續，並指定 README 必須展示原版與 HD 多語系截圖。先核對主機 gh auth、PRIVATE／Issues 及遠端工作項目，再建立 #53。命中復古 README、正常玩家路徑及文件職責路由，載入 README 標準與復古重製技能的驗證參考。依本次明確指示，僅選定的文件 PNG 可進私人儲存庫；有限例外同步寫入 AGENTS、CONTEXT 與 .gitignore，沒有公開 Release 或上傳原版檔。

沿現行 b6cca7e0cd54f0816c5a9d3b656790f0567350fb 的已驗 Linux 前端擷取，binary SHA-256 1461ac4b4a2fe582f3c937a9f6d84edca34d09562a236a0f1472895f088ec2c8。程式、唯一 TSV、字型與素材沒有修改。新增正常 GUI 擷取及選定 PNG 匯出工具，工作皆在 workspace，原版唯讀，Docker 固定既有 image、UID/GID 1000:1000、無網路與有界資源。

前件保留，只有 r4 整批通過：

| 輪次 | 已查證結果與修正 |
|---|---|
| r1 | 已取得 17 張及正常退出；末段工具誤把原版模式的空 HD 預算欄位與五語系數值比較。改為只核對 HD 數值，不稱整輪 PASS。 |
| r2 | 城市來源與可見 RGB 相同；未使用的 232／233／240／241 色盤項目更新，與 032 既有契約一致。改核對完整色號畫面與解碼 RGB，仍保存完整色盤雜湊。 |
| r3 | 英文預算擷取時已返回城市，沒有新增 DOS 讀鍵或轉送輸入；budget=false 正確擋下。沒有將城市圖誤登為預算，也不推測原版返回的完整原因。 |
| r4 | 各語系從正常 F3 選單重新開預算，擷取後 Esc 返回；省去重選相同語言。17 張、22 次原版讀鍵、F11／F12 隔離與正常退出通過。城市及預算各組原版色號與可見 RGB 一致，預算十一個原始欄位相同。 |

實際執行 `TAIPEI_SCREENSHOTS_RUN=readme-screenshots-r4 bash workspace/tools/readme_screenshots.sh`。原始收據為 `workspace/runs/readme-screenshots-r4/verification.json`，SHA-256 13b3e7f76f7c3fb426c480c263fcea5fd893ebfdac75a9cb7eab6f41c334a35c。沒有 checkpoint、狀態注入或長時間 RAM／RNG 抽樣；原版 0 鍵暫停模擬，CPU 與時鐘仍前進，不稱為相同機器狀態對拍。

匯出在同一 image 的 Docker 內執行 `python3 /workspace/tools/export_readme_screenshots.py --run /workspace/runs/readme-screenshots-r4 --out /workspace/screenshots --source-commit b6cca7e0cd54f0816c5a9d3b656790f0567350fb`。掛載專案 workspace 可寫，runs、tools、app、prototypes/hd-style 與原版 /orig 各自再以唯讀掛載；設定 --rm、--network none、--user 1000:1000、--memory 1g、--cpus 1、--pids-limit 64 及外層 timeout 60s。輸出目錄須尚不存在；重生時使用新的擷取目錄與新輸出目錄，審查後才替換展示圖。

匯出工具重新讀取每份原始 ZIP，核對色號、解碼 RGB、模式、語言、Help 狀態、尺寸、PNG 及原始收據 SHA-256；原版另驗最近鄰四倍像素完全相同。17 張總計 9,785,382 bytes，全部與已逐張目視檢查的 r1 PNG 相同。README 直接展示原版與 HD 五語系城市／預算，Help 五語系可展開。來源、程式、字型、七補丁、工具及完整 PNG 雜湊存入 workspace/screenshots/manifest.json；原始 ZIP、native PNG、binary、SAV、字型與素材包不入 Git。

擷取容器末段 find 的兩筆是容器自建的掛載父目錄，不是主機產物。工具收尾範圍修正為實際掛載的 /workspace/runs，另以完整 workspace 唯讀掛載執行指定 find，結果為空。manifest 的工具欄記錄現行可重生工具雜湊。程式來源及 binary 與上一輪 provenance 一致，35 個原始檔及 RAR 不變；工具語法、README 圖片與連結、來源清單及 UID/GID 核對通過。沒有新增 image，專案容器與背景程序均已清理。只明列提交文件、工具及獲指定的 17 張 PNG／manifest，提交／push 與 #53 最終狀態於遠端回鏈。完整 HD、平台真機與正式封包仍未完成。

## 2026-10-13：六圖表五語系正常操作與 README #54

使用者指示繼續。先核對主機 gh auth、乾淨工作樹及遠端 Issues，再建立 #54 接續 #48 的必要短流程，長時間狀態抽樣仍停止。命中規格閘門、正常玩家路徑與 README 路由，使用既有重製技能、029／032 契約及文件職責。Docker inspect 的首個格式要求不存在的 Entrypoint 欄位而失敗；改讀完整 Config 確認既有 image 以 bash 為預設命令，沿用同一固定 image，沒有另建工具鏈。

產品程式、TSV、dosgolem 與素材都沒有改動。新增正常 GUI 工具、五語系整幀核對器及選定截圖匯出工具，同次掛入 AGENTS／CONTEXT／029。工作及輸出皆在 workspace；固定 image c3d8835a9d39、UID/GID 1000:1000、network none、資源上限與外層逾時，原版唯讀。GUI 上限 1500 秒，使用既有真實讀鍵／release 輔助工具，不注入狀態或圖表選取。

| 項目 | 已查證結果 |
|---|---|
| 正常來源 | 從原版選單進災難台北 DISA1，以原版 0 暫停。完整選單來源確認實際選取 0–5，六個圖表中央資料互不相同 |
| 操作 | 每圖 F12 往返、兩次無輸入及 DOS AH07 Escape 返回，完整原城市與原點一致；電力圖 F11 五語系，選擇期間 VM／畫面／原版讀鍵不變 |
| 整幀核對 | 從原 ROM、READY 前固定灰框／筆觸重算資料。六標題、四組文字與底部單位取本次開工前 032 的五張固定 Noto 圖，只取既定文字矩形；數字由原字模獨立解碼。34 張各 1,024,000 像素相同，沒有跳過字墨或區外 |
| 正反對照 | 14 項中兩個正對照通過，十二個有效破壞被拒絕。涵蓋框架、字墨、資料、標題、底部、區外、原始來源／資料、家族／資料雜湊、錯語言與原版模式；受影響雜湊重算後仍拒絕 |
| 原版存讀檔 | CHARTS.SAV 93567 bytes，正常寫入、同次讀回且雜湊不變，最後原版退出。SAV SHA-256 7fe77eae9edeeb1644e7ba156c651ffbc93427293daa666b3f101fa1fd7beab8 |
| 核心測試 | 六完整原型、資料／色盤／相位／F12 與十一種實際資源故障通過；家族隔離補入固定來源後通過 |
| README | 新增六圖表繁中 HD 與電力圖原版／其他四語系共 11 張，3,572,733 bytes，均與已逐張檢視的前件 PNG 相同。合計 28 張、13,358,115 bytes，來源併入原 manifest |

第一輪 chart-locales-r1 的六圖、34 張呈現與原版存讀檔均有有效收據，但不稱整輪 PASS。原版讀檔視窗已預選 CHARTS，工具又輸入六個字母；畫面條件立即成立，舊收據尚未更新，接著把六字母與 Space 的七個正常讀取誤當作 Space 重複而停止。原始收據明列 CHARTS.SAV 真實讀取。改為沿用預選檔名，沒有修改產品或放寬讀鍵斷言。以相同 image／binary／原版，執行 `TAIPEI_CHART_LOCALE_RUN=chart-locales-r2 bash workspace/tools/chart_locale_gui.sh`，全新目錄完整通過。

正式正常收據 `workspace/runs/chart-locales-r2/verification.json` SHA-256 5625017b4144ccaf186b809cb2a1916404328769807ecd513723c1c723cd7026，含 16 次普通鍵、16 次方向／功能鍵及六次 DOS Escape 同步。呈現核對命令在固定 Docker 內執行 `python3 /workspace/tools/chart_locale_check.py --run /workspace/runs/chart-locales-r2 --out /workspace/runs/chart-locales-r2/pixel-verification.json`，SHA-256 69db95c043b5da0f717d29e36622bde67d00a1a16aaecefdf432ff15186c1623。五個固定 Noto 參考雜湊寫在核對工具，未匯入目前呈現器或以受測畫面生成期望值。

核心測試使用 `go test -mod=readonly -p 1 -v ./internal/hd -run '^TestChartWindows' -count=1`，設定 TAIPEI_HD_ORIGINAL=/orig、TAIPEI_HD_MATERIALS=/workspace/prototypes/hd-style、TAIPEI_CHART_RECEIPTS=/workspace/runs/chart-windows-native-r3。前三項通過，家族隔離因少設 TAIPEI_HD_RECEIPTS 略過。補設為 /workspace/runs/gui-ending-scene-cold-r1，只重跑 `^TestChartWindowsOtherFamilyIsolation$` 通過；日誌為 chart-unit.log 與 chart-isolation.log。這是測試來源設定修正，不是產品缺陷。未為工具與文件變更重建相同產品的四架構 binary。

截圖匯出命令在同一 Docker 內執行 `python3 /workspace/tools/export_chart_screenshots.py --run /workspace/runs/chart-locales-r2 --catalog /workspace/screenshots/manifest.json --source-commit b3cacf3dd13c2fdd1738a5e6f3d496e9353d69d5`。workspace 可寫，runs／tools／app／prototypes 及原版各自再唯讀掛載；--rm、--network none、--user 1000:1000、--memory 1g、--cpus 1、--pids-limit 64、timeout 120s。新 PNG 必須不存在；匯出先重新核對原始 ZIP、整幀與原版／五語系電力圖相同來源，再追加原來源清單。17 張既有 PNG 不變，原始 ZIP、擷取資料與 SAV 不入 Git。

收尾回查規格、正常玩家路徑與 README 路由，更新唯一現況表、029 追加證據與驗收矩陣。README 圖片／連結、28 張雜湊／尺寸與 1000:1000、工具語法、來源入口及 029 正對照通過。產品所有來源及 binary 與既有 provenance 相同，35 個原始檔與 RAR 不變；指定 find 為空，專案容器已清理，沒有新 image 或遺留背景程序。只明列提交文件、工具、來源清單及指定 11 張 PNG；提交／push 及 #54 收尾回鏈遠端 Issue。

本項只完成必要 GUI／呈現分支。沒有恢復長時間 RAM／CPU／RNG 抽樣，沒有全新 EXE 冷讀、施工完整鏈、母語審校、平台真機或正式封包。029 保持 READY、#48 OPEN，不提升完整 HD 或規則 parity。

## 2026-10-13：依遊玩抽驗驗收六圖表，補遊戲背景與截圖 #55

使用者更新完成條件為「抽驗能由遊玩就算驗收通過」，並要求完成後更新 README 的遊戲截圖與背景。先回讀主機 gh auth、遠端 Issues 及目前產品，再建立 [#55](https://github.com/wicanr2/taipei/issues/55)，於 #48 留言登記新標準。命中正常玩家路徑與 README 路由，載入重製技能、驗收參考、README 契約及文件職責。此定案取代六圖表原先以長時間完整狀態對拍作結案門檻的要求，不把未驗項改成通過。

新增 [accept_chart_playtest.py](workspace/tools/accept_chart_playtest.py)，回核 #54 的 `chart-locales-r2/verification.json`、呈現報告、35 份 ZIP／PNG、CHARTS.SAV、現行所有已記錄產品來源與四架構 binary。均符合原來源及雜湊，Linux 為 `1461ac4b4a2fe582f3c937a9f6d84edca34d09562a236a0f1472895f088ec2c8`。六個真實 F4 選項、每圖 F12／觀察／Escape 返回、電力圖 F11 五語系、原版同次存讀檔與 DOS 退出已通過；產品未改，沒有重跑相同遊玩流程。

執行命令為 Docker 內 `python3 /workspace/tools/accept_chart_playtest.py --run /workspace/runs/chart-locales-r2 --manifest /workspace/screenshots/manifest.json --reviewed-commit fa683e208b62b1cac064d74549cefcf19f9f2b56`。沿用既有 image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`，timeout 120s、--network none、--user 1000:1000、--memory 1g、--cpus 1、--pids-limit 64；專案與 workspace 唯讀，僅 `workspace/screenshots/` 可寫。回核通過並從已檢視的正常 `city-paused-capture.zip` 匯出 `city-disaster-zh-Hant.png`，沒有重繪或加工該畫面。新 PNG 1,080,439 bytes、SHA-256 `603fee2fb7ac13e1983a20a0143466cecf09275a5ca9c40a87d482151776bfd5`；全部 29 張合計 14,438,554 bytes，均為 1280×800。

README 新增遊戲背景、城市治理玩法與原版五十萬人口目標，並將正常災難台北城市總覽放在介紹後。發行年代、聯邦開發與資策科技代理引用[奧米加典藏](https://www.omega.idv.tw/kdb120/viewthread.php?threadid=5296)及[中文模擬類遊戲目錄](https://chiuinan.github.io/game/game/cgame33.htm)；玩法及目標回查 017 的原版說明來源及已核對介面文字。公開目錄僅作作品背景出處，不據此宣稱目前原版檔的精確版本或現行權利歸屬。既有原版、HD 五語系、預算、Help 與六圖表截圖全部保留。

029 限六圖表呈現及已驗玩家路徑升 CONFORMED。同步更新 AGENTS 的使用者定案、唯一現況表與文件入口、驗收矩陣及 manifest，舊的研究與停止點依時間保留。現況索引原有三處「正式 HD 未驗」同步改成目前已驗結果，避免舊入口重新開啟已完成工作。

Docker 內完成 Python 語法、五份 Markdown 相對連結、29 個唯一 README 圖片參照與 manifest 集合、全部 PNG SHA-256／尺寸／1000:1000、工具雜湊及文件索引正對照核對。首輪檢查在已通過上述斷言後，列印新圖資訊時錯把舊 manifest 記錄也當作有 batch 欄位；僅修診斷為 `.get()`，同 image 乾淨重跑全部通過，不屬產品缺陷。35 個原始檔及 RAR 與盤點雜湊一致。指定 find 為空，專案容器已清理，沒有新 image 或背景程序；`git diff --check` 通過。

只明列提交文件、回核工具、manifest 與一張指定 PNG，提交及推送後回寫 #48／#55 並核對結案狀態。完整 RAM／CPU／RNG 對拍、本圖表流程施工至全新 EXE 冷讀、未走過分支、平台真機與正式封包仍未執行；依使用者標準不再阻塞本批驗收。全部圖片重繪與三平台交付仍由原母項繼續。

## 2026-10-13：DISA1 三種建物與 48 格 B 高清 #56

依使用者繼續指示，先核對 gh auth、遠端 Issues、乾淨工作樹與既有 Docker image，命中素材／規格閘門、正常玩家路徑及文件職責路由。#44 已先留言登記補查後續正常城市收據；排除重複後 14 種原始畫面仍未取得剩餘 18 張道路候選，回寫結果並停止相同探針，不猜補或縮減範圍。另建立 [#56](https://github.com/wicanr2/taipei/issues/56)，接續 #30 的正常 DISA1 已見建物。

新增 034 DRAFT 及來源工具，同次索引至 AGENTS／CONTEXT。#54 正常原子收據完整核對三個 4×4 複合矩形，成員 34、35、36 各 16 格，索引 `4+24×row+col`；48 個不同來源、全部別名、ROM 檔案偏移與使用色盤保存本機 `disaster-buildings-v1/sources.json`，SHA-256 764054313fa809c6ab1e686a325751eb5fade49ada81fd99fabd569f6cac6272。只確認圖像來源，不從外觀推定建造與發展規則。

使用內建 imagegen 依原版參考製作三張 B 重繪，沒有使用 CLI。三組完整提示詞、來源圖與生成原件保存在 `workspace/prototypes/hd-style/disaster-buildings-v1/34..36-prompt.txt`／`*-generated.png`。預設生成輸出唯讀掛入 Docker，再由 UID/GID 1000 複製至 workspace；沒有覆寫預設原件。完整插畫以 ImageMagick 6.9.11 Lanczos 1254→144 正規化後才按原格切片，保留布局及主要色彩。已檢視完整原位原型與實際繁中、英文及原版 GUI 圖。

來源及原型審查後先固定 034 READY，再接產品。四個正式素材檔在乾淨目錄重生 byte 相同，manifest SHA-256 7dc484798f0d65962d35db56a33ac3153c7f65fb105daef3a28351018d6030e2。新增 city_buildings.go 並接既有城市來源閘門，僅辨識完整原圖與已用色盤，按 36×36 切片繪製；單成員 atlas 故障只讓該來源回退，其餘成員可繪。原版程式、七補丁、規則與存檔格式均未改。新增統計 city_buildings，原版／模態時為零。

三項必要測試通過，包含完整三圖及 48 格／區外、3888 項來源失配、色盤、八項真正素材故障及正常來源／原版／阻塞／原點隔離。首輪測試忘記提供既有來源 helper 必需的收據 SHA，前兩項已通過，隔離項因測試輸入而失敗；補入 sources.json 早已固定的值，只重跑隔離項通過。沒有改產品或放寬核對。十一項火力／道路／圖表回歸無跳過通過，81.759 秒；鍵盤套件通過，日誌為 building-unit-r1.log、building-unit-r2.log、building-regression-r1.log。

`bash workspace/tools/disaster_building_gui.sh` 在既有 image、1500 秒上限、network none、UID/GID 1000、3g／2 CPU／128 pids 與有 trap 的 Xvfb 中執行，原版及工具／素材唯讀。正常 DISA1 入口、原版 0 暫停、116 格本批實際繪製、F12 往返、F11 五語系、BLDG.SAV 原版寫入／同次讀回與 DOS 退出通過。收據 verification.json SHA-256 da0925ab7dd25e6c2e7c51d84e0aa6a7b1ebe2fa76044154828a0fde9504c84a；SAV 93567 bytes、SHA-256 c44e4889acd6aec4b2d1c0088f87d096043685236136095c656d12673cad9100。沒有快照、狀態注入或長時間 RAM／CPU／RNG 對拍。

Docker 內 `python3 /workspace/tools/disaster_building_check.py --run /workspace/runs/gui-buildings-r1 --out /workspace/runs/gui-buildings-r1/pixel-verification.json` 通過六張各 1,024,000 像素整幀及六項正反對照。期望值來自 READY 前固定原型、原 ROM／原版畫面、#54 固定前件與已固定 Noto 文字矩形，不匯入產品呈現器；原版 F12 全畫面核對四倍原色。報告 SHA-256 01507a06ce27cb573b23d4f33682a1c9e42b3fe7062316dfe47e1a78b2bfcc78。

Linux 新 binary 為 taipei-preview-buildings-r1，SHA-256 5933a1f2554ee51419eae97493708cb99b2de8da726011e7887c06d5c9c348c3。先保留舊四架構產品於 runs/buildings-baseline-v1，再由既有 Windows／macOS image 重新編譯；三個外平台架構完成，Windows 留有先前已知 YMFM 警告。跨平台工具加 project=taipei 容器標籤以便清理，沒有新建 image。034 限本批及已驗遊玩路徑 CONFORMED，README 截圖與現況收尾接續下筆紀錄；全部 HD、其他相位、全新 EXE 冷讀、平台真機及正式封包仍未完成。

### #56 截圖與交接收尾

產品與工具已先提交 ad8d6f9cb1450a4c516add1192cafc43c9f0d2ed，使截圖可回查確實包含新呈現程式的來源。正常 GUI 與六張圖已完成後，執行 Docker 內 `python3 /workspace/tools/export_building_screenshots.py --run /workspace/runs/gui-buildings-r1 --manifest /workspace/screenshots/manifest.json --source-commit ad8d6f9cb1450a4c516add1192cafc43c9f0d2ed`。沿用固定 image、90 秒上限、network none、UID/GID 1000、1g／1 CPU／64 pids，只有 screenshots 可寫，其餘 workspace 與原版唯讀。

匯出前再核對正常完成報告、原子 ZIP、PNG 與完整獨立像素。依使用者持續要求更新 README 畫面，更新既有 DISA1 繁中圖並補原版／其他四語系，六張共 6,542,163 bytes；先前繁中圖片來源記錄保留於 manifest 的 replaced_screenshot，不改寫原始收據。README 現有 34 張唯一 PNG，共 19,900,278 bytes，全部 1280×800、1000:1000。來源清單 SHA-256 9e87c93d335487df029faf229a5331ac1d940b5395780d00782d1c0393c88d44。新六張皆已實際檢視，完整畫面與五語系字墨一致。

正常 GUI 通過後才將已驗 Linux 研究產品複製到標準入口 taipei-preview。先核對四個前版保存副本與既有 provenance 相同；新四架構 ELF／PE／Mach-O、所有已記錄程式來源、正常及呈現報告雜湊另存 workspace/runs/buildings-final-provenance.json。35 個原始檔及 RAR 仍與原盤點一致。Windows／macOS 本次只有編譯與架構驗證，沒有真機或正式封包聲明。

收尾回查 README 與文件職責路由，更新唯一現況表、驗收矩陣及 README 功能摘要。34 個唯一圖片參照與 manifest 集合、全部 PNG 雜湊／尺寸／擁有權、五份 Markdown 連結、工具語法與雜湊、034 索引及 029 正對照通過；git diff --check 通過。指定 find 為空，專案相關容器均已清理，沒有新 image、背景程序或全域清理。只明列提交文件、來源清單及指定六張 PNG；兩筆提交推送後回寫 #56 並核對結案，#30 保持 OPEN。其餘建物／動畫、未走過相位、全新 EXE 冷讀與三平台正式封包仍待接續。

## 2026-10-13：警察局與消防局 32 格 B 高清 #57

接續使用者「繼續囉」，主機 gh 核對登入及遠端 Issues，工作樹 main 與 origin/main 均為 576be4d。路由命中素材來源與規格閘門、正常玩家路徑及文件職責，沿用已載入技能與既有工具鏈。先建立 [#57](https://github.com/wicanr2/taipei/issues/57)，035 DRAFT 同次索引；不重開已完成 #56。

兩次正常冷啟動分別從工具 5 警察局／消防局選項施工，再移開游標。完整選單 SHA 對照 021 的 tool-05。各取得 4×4 圖、16 張唯一來源，成員 37 的 `24*r+c` 與 `4+24*r+c`；零起算定位、ROM 檔案偏移、色盤與原子收據保存在 civic-facilities-v1/sources.json，SHA-256 212cb5c2c92fcfc36a254205586a38bb7e668dc8f3595a28e0ed0d770dbadc45。來源探針只有有界停止，未當成原版退出驗收。首次探針使用錯誤的未補零選單 ID，開啟遊戲前即停止；核對既有 manifest 後修正，重新乾淨執行，沒有產品改動。

依原版完整圖使用內建 image_gen 生成兩張 B 素材。提示、來源與原件保存 `workspace/prototypes/hd-style/civic-facilities-v1/`，提示檔 prompts.json，原件 police-generated.png、fire-generated.png。預設生成原件保留，透過唯讀掛載由 UID/GID 1000 複製進 workspace。兩張完整圖各以 ImageMagick 6.9.11 Lanczos 1254→144，再合成 288×144 atlas；逐張檢視比較圖，保留原俯視布局、主色與識別圖。先審查 035 READY，再接入產品。兩個正式素材檔在 civic-facilities-ready-repro-v1 乾淨重生 byte 相同，固定 manifest SHA-256 4c2a707844a6cb00d295ff49afb826b7dddcd7f37f036d3d97ed9d1bb23f5c3c。

新增 civic_facilities.go 與城市呈現統計，沿既有場景／原點／主題閘門。僅覆繪完整來源與已用色盤，必要清單或共用 atlas 失配時本批回退。原版 EXE、規則、七補丁、資料及存檔格式未改。12 項警消／DISA1 建物／道路／電廠測試全部通過，50.734 秒，無跳過。追加兩份正常原圖中的全部區外隔離檢查後，只重跑修改項通過，6.813 秒。記錄 civic-tests-r1.log、civic-scene-isolation-r1.log；包含 2592 個來源單點破壞、已用色盤、四項真正素材缺失／損壞與原版資料隔離。

`bash workspace/tools/civic_facility_playtest.sh gui` 在固定 GUI image、1500 秒上限、network none、UID/GID 1000、3g／2 CPU／128 pids 與有 trap 的 Xvfb 中執行。正常新城市、原版 0 暫停、警察局 22,3 與消防局 22,7 施工、F12、F11 五語系、CIVIC.SAV 寫入／同次讀回及 DOS 退出通過；原點維持 12,12、32 格覆繪、資金由原版扣至 79400。SAV 93567 bytes，SHA-256 8bf5e72fa4282f1b069276722d19ac03b84d219634f2ba03e1ee345773346b47，讀回後不變。verification.json SHA-256 4eb94f6863916cabac7b2d4e4c8985a1f8a836b93e40523bfcdb3cec03eb5d30。

Docker 內 civic_facility_check.py 從原 ROM 與生成原件獨立重算 32 格及 atlas，驗六張 GUI 的設施實際像素、五語系標籤與原版整張像素；一個正對照及四項同步更新雜湊的破壞通過。初次 glob 誤收冷啟動 city-choice 診斷圖，修正成明列六張輸出後，以同一 image、命令與未修改的原始收據重跑通過，沒有放寬像素斷言。報告 SHA-256 295b1fc95d9ba8a0f34f87b76309afee458d673aaeb689ecd4019a2a3c7576d3。六張圖均已人工檢視。

Linux 已驗產品 bb8aa4271a403b0e1602c5a82faacda4554de48972b212bf00daef83fa589a5d 保留於 taipei-preview-civic-r1，抽驗完成後才提升為標準入口 taipei-preview。前版 Linux 及外平台保存副本均保留。沿原 Windows／macOS image 重編，ELF／PE／Mach-O 四架構核對通過，Windows 留有既有 YMFM 警告；僅編譯／結構，不宣稱真機或封包驗收。35 原始檔及 RAR 與盤點一致。來源、七補丁、image 與產物雜湊保存 civic-final-provenance.json，SHA-256 eaedd8f49cc91a2c72f0558e36f09bfe542f381c13654f4d65ce21788e6cbf6d。

035 限本批呈現及已驗正常路徑 CONFORMED，README 六張截圖接續匯出。未走過動畫、長時間機器狀態對拍、全新 EXE 冷讀、真機與正式封包保留限制。指定 find 為空，本批容器均已自動刪除；未新增 image 或留下背景程序。

### #57 README 截圖與收尾

程式與驗證工具先提交 6c4a5efe28ec3911bc473cd533d51e83b7231832。Docker 內 `python3 /workspace/tools/export_civic_screenshots.py --source-commit 6c4a5efe28ec3911bc473cd533d51e83b7231832` 再核對原子收據、正常遊玩完成報告、實際設施像素及語言標籤後匯出六張 PNG，只有 screenshots 掛載可寫。原版與 HD 五語系使用相同原始畫面，沿用 Linux 真實遊玩擷取，不修改舊 34 張來源。

README 現有 40 張唯一 1280×800 PNG，共 26,894,292 bytes；新增六張 6,994,014 bytes。manifest 的 civic_capture 保存本批 binary、來源提交、工具及報告 SHA，清單 SHA-256 9534063d7ef4e90047b1feea280a9bf235624367edfb42b7e6365818345d8d1e。README 功能表與對照圖、唯一現況表及驗收矩陣同步更新。新增 PNG 僅明列六檔開放版控，素材、字型、SAV、EXE 與原始收據仍排除。

收尾回查文件職責與現況路由，40 個唯一 README 圖片參照與 manifest 完全一致；所有 PNG 雜湊／尺寸／1000:1000、工具語法及固定雜湊、五份文件連結、034 正對照與 035 索引、現行程式及四架構產物雜湊通過。git diff --check 通過，指定 find 為空，專案相關容器均已清理。遠端仍為 PRIVATE。明列檔案提交及推送，回寫 #57 與 #30；#30 其餘建物／相位及正式交付維持未完成。

## 2026-10-14：環境設施與公共設施批次 #58–#60

接續使用者加速完成指示，先核對主機 gh auth、遠端 Issue、現況、路由與專用 image，建立 #58 與 036 DRAFT。以原版 F2 的 BASE.SAV 重用城市，減少冷啟動。#59 讓收據間隔可指定，預設仍為 60，本批使用 6；#60 另查公共設施正常施工後的輸入問題。沒有修改原版程式、規則或 dosgolem 七補丁。

垃圾場與污水處理廠各正常扣款 3000，取得完整 4×4 圖。來源證明、所有別名／偏移及色盤保存本機 public-facilities-v1。正確 ROM37 索引為 12+24*r+c、16+24*r+c。初版沿交接摘要誤寫 8／12，固定來源測試拒絕後回查 source.json，訂正規格與程式，未修改來源或放寬斷言。

使用內建 imagegen 按完整原版參考生成兩張 B 素材，保留預設原件，唯讀掛入 Docker 複製至 workspace。提示、原件與雜湊均保存。完整圖縮放為 144×144，檢視 DRAFT 比較圖後才固定 READY。正式三檔在 public-facilities-ready-repro-v1 乾淨重生相同，manifest SHA-256 07319733ab01743a8e2e30cec7e6e042554b35982bf342ba556f21d84c2892e1。其餘十項 DRAFT，#58 保持 OPEN。

共用 public_facilities.go 僅辨識這 32 個完整來源與已用色盤，各設施 atlas 故障獨立回退。核心兩測試通過，7.307 秒，含完整圖、區外、2592 項來源破壞、六項實際資源故障及正常原版來源。十二項既有回歸中十一項先通過；唯一失敗為 DISA1 收據環境誤指不存在的目錄。按固定 SHA 找回 chart-locales-r2/gui，只重跑該項通過，1.778 秒。keyboard 通過。日誌 public-tests-r1/r2.log、public-regression-r1/r2.log。

TAIPEI_CITY_MENU_RUN=gui-environment-r1 bash workspace/tools/facility_batch_playtest.sh hd，在固定 c3d8835a9d39 image、network none、UID/GID 1000、3g／2 CPU／128 pids、外層逾時與有 trap 的 Xvfb 中完成正常冷啟動、新遊戲、兩項施工、F12、F11 五語系、PUBLIC.SAV 同次存讀檔及 DOS 退出。原版及素材唯讀，無快照、注入或長時間抽樣。93567-byte SAV SHA-256 660bfc71f309b96fe0bce6dcb743b8ca3635f2ebbd299060275ba86821097746，讀回不變。收據 SHA-256 82e4945f80375699d6da21174097a3cf3825ff086d7aa011c792b96bc5439fba。

public_facility_check.py 由固定 DRAFT 原型、原 ROM 與生成原件重算來源，驗八張實際畫面的設施像素、五語系標籤及原版整張。一項正對照與四項同步重算雜湊的破壞通過，報告 SHA-256 f6d728f45cba4c5b387b7772bf2bfc4c84d48fce653926fc7c3a43a957a6cf4c。已檢視垃圾場 HD、污水英文 HD 與原版。036 限兩項及已驗路徑 CONFORMED。Linux 已驗 binary 21705e3c9521d247b86220bcaecb295db39958b6ba485d5501df42059063abf4 通過後才提升標準入口；Windows／macOS 延至後續合併重建，保留前版來源，不稱本批外平台已驗。程式先提交，再匯出 README 八張 PNG 以便回查來源。

### 前件與 #60 診斷歷程

以下由原 036 DRAFT 移入唯一 WORKLOG，保留歷史；正式契約只寫現況。

探針修正：原版讀檔由多個 DOS read 組成，核對完整 93567 bytes，不以單次 read 作假設。r2 的工具列差異只有工具 9 的 84 個外框像素，色號由 186 變為 32；依 [004](docs/re/004-native-controls.md) 與 [019](docs/spec/019-city-chrome.md)，讀檔後以 Tab 回到工具列焦點，再核對原先保存的完整工具列來源。r1／r2 失敗屬驗證腳本，原版讀檔成功，前件保留；r3 用同一 image 與收據參數乾淨重跑。

追加修正：r3 證實 Tab 後所選工具與游標重合時仍為紅框，不能要求回復紫框。改依 019 的十四個完整 22×22 圖示來源與白／紅／紫外框，辨識當前工具，四份既有正常來源離線核對通過。新城市原版存檔關窗後十四框均白，初始工具游標 0 依 004 已證實；此狀態獨立處理。r4 啟動後因離線初始狀態檢查未通過而提前停止，避免沿用舊版探針。垃圾設施來源保留 r1，r5 完成污水來源。

r5 公共設施施工成功並扣除費用，但下一個 Left 持續按住直到原版讀取，120 秒內沒有被讀取。原版仍在執行且無缺指令；原生放鍵閘門為強推論，不把腳本等待當成產品缺陷。r6 改為先確認前端按下、立即放開並確認 break，再等待原版恰讀一鍵。仍保留完整原版讀鍵確認，不採盲目定時送鍵；既有來源不重做。

r6 同樣未取得施工後 Left 讀取，單純持鍵假說不足。另開 [#60](https://github.com/wicanr2/taipei/issues/60)，以 [IDA 窄查詢](workspace/tools/ida_facility_probe.py) 核對取樣位置及呼叫端，輸出 `workspace/runs/ida-60/stall.json`。其餘已完成來源與素材沿用。

[#60 診斷重播](workspace/tools/facility_diagnostic.go) 使用 r8 真實 GUI 的原始輸入與步數，從原版 EXE 冷啟動追蹤 BDA 頭尾改變及取樣 PC。用途限找出丟棄按鍵的原始指令，不能代替正常 GUI 驗收。

IDA 9.4 核對固定 EXE 及資料庫輸入雜湊相同。兩次取樣落在原始 sub_24D96，IDA 0x24FB9／0x24FC2，呼叫端 sub_248E2／sub_27796／sub_289AE。原始函式遍歷 89×105 格並更新分類計數，語意為城市格統計的強推論，並非等待鍵盤放開的證據。暫存器陣列依 x86 編碼為 AX/CX/DX/BX/SP/BP/SI/DI，不把 SP 誤當 SI。r7 只恢復既有 60-update 正常探針在施工確認後的 24,000,000 步觀察窗，其他逐鍵仍用短收據；驗證較早送入的鍵是否在原版施工收尾被丟棄，不修改原版規則或時鐘。

### #58 README 截圖與來源收尾

程式及工具先提交 1559288e7e8baf18ec6d91982cf0e34fc2c8b896。以同 GUI image、network none、UID/GID 1000、2g／2 CPU／64 pids、120 秒上限執行 export_public_screenshots.py；原版、workspace 與專案唯讀，只有 screenshots 可寫。匯出前再次核對正常完成收據、原子 ZIP、PNG 與獨立像素報告，加入垃圾場原版／繁中 HD，以及污水處理廠原版／HD 五語系八張 PNG。未替換舊 40 張；各批來源仍保留原始程式提交及雜湊。

README 現有 48 張唯一 1280×800 PNG，共 35,393,627 bytes；本批新增 8,499,335 bytes。manifest SHA-256 b74fe56ad8323b8ade3f4221a4d8d8d139fd2f8337c3eba3ca2dffd650ed5489。README 更新設施對照與功能摘要，CONTEXT 及驗收矩陣同步記錄兩項完成、十項公共設施 DRAFT 與外平台前版。僅明列八張 PNG 開放版控，原素材、SAV、字型與原版資料仍排除。

收尾回查正常玩家路徑與文件職責入口。48 張圖片參照與 manifest 集合、所有 PNG 雜湊／尺寸／1000:1000、Markdown 連結、產品來源與七補丁一致，35 原始檔及 RAR 未變；記錄 public-final-hygiene.json。指定 find 未發現 root-owned 輸出或 .md 目錄。產品抽驗與匯出容器均已 --rm；#60 的新診斷仍在有界容器執行，不提前宣稱全部研究已清理。

### #60 原版清鍵證據

r8 追加 BIOS 鍵盤頭尾、佇列、IRQ 向量、CPU flags 與 KeyPolls，只增觀測。從真實 GUI 輸入冷啟動的 headless 診斷重播到 1,300,000,000 步，原始圖雜湊與 r8 最後畫面相同，記錄 public-diagnostic-r1/diagnostic.json、memory.bin 及 provenance.json。此為診斷，不當成正常 GUI 驗收。

BDA 頭尾追蹤證實，Left 入緩衝後在第 1,191,033,529 步由原版 CS 052D:0012 清掉。IDA 9.4 核對其原始位置 0x141E2 為 INT21 AH=0Ch，原函式 sub_141DC 保留原名及位址。早先單純持鍵假說不足；固定 24,000,000 步也早於施工收尾。新的 r9 改以完整已知 ROM 施工矩形作觀測條件後才送方向鍵，仍要求原版恰讀一鍵及原版退出，尚待本輪結果。不改原版規則或時鐘。

### #60 施工完成閘門與游標前件

r9 正常新遊戲、國父紀念館施工、移開游標與原版退出通過，verification.json SHA-256 be6b80ffd9602529776d333540ba50e5fc054c8655d19058bb2ac5a985f65477。完整 6×6 圖共 36 格，來源 ROM40，證明檔 public-facilities-v1/sun-yat-sen/source.json SHA-256 b6d7fda1fbb69433c6f5c370a3122433d7feee29cc80a9d87a23e925d4d95bb7。完整施工圖出現後才送方向鍵，避免原版 AH=0Ch 清掉過早輸入；全部按鍵仍核對 BIOS word，不增加固定等待、時鐘特例或修改原版。

r10 中正紀念堂完成繪圖，但其游標覆蓋四邊，純完整 ROM 格的就緒條件一直不成立。36 格的未遮擋像素各自唯一匹配 ROM40，索引 6+30*r+c；外框差異只在一像素四邊，左右為 15、上下為交錯 15／0，右上及右下按實際繪製次序核對。這是探針假失敗，尚未送出下一個方向鍵，不列產品阻塞。

新增 facility_cursor.py，只接受完整 ROM 格或上述已見完整外框變體，限制用途為下一個測試按鍵的就緒判斷。r8 無游標及 r10 有游標兩個完整複合圖均通過，逐格內部破壞及游標外框破壞共 74 項均拒絕；正式來源匯出仍要求移開游標後的全 81 bytes，不從遮罩猜補圖片。r11 使用同一 image／binary／原版乾淨重跑九項剩餘公共設施，另加入最終 PUBLIC.SAV 正常存讀與原圖核對，等待完成。

國父紀念館依正常參考使用內建 imagegen 製作 B 原件，預設原件保留並唯讀複製至 workspace。generated.png SHA-256 ee049c6243f1f98aa7e2ce38010da3262b780f3c6977b42219f0a21b3739046e；提示與 generation.json 保存在同來源目錄。這張仍為 DRAFT，未接入產品或宣稱全部公共設施完成。

## 2026-10-14：十二項設施整批完成 #58，施工探針修正 #60

r11 正常建設剩餘九項，各費用 5000、完整 6×6 圖；移開游標後核對全部原始 81 bytes。最後 PUBLIC.SAV 原版存讀、施工格讀回及 DOS 退出均有收據，SHA-256 72d9f359193fc9cd9080f938c81d2aa1c4f611b96aee020133b47a0646867175；SAV d6601a5009ce1af565d41e6592a4a4690fe19db49644bd47b3425c53fc3ef91a。外層清理回傳 143，完整前件保留，不把 wrapper 稱為 PASS。後續 trap 只等待自己的 Xvfb，詳細日誌改寫 workspace/runs；信號原因未證實，不列原版缺陷。新產品整輪 wrapper 為 0。

十項公共設施按完整原版參考使用內建 imagegen 製作 B 圖。二二八前兩個版本在下方綠地新增迴環路，未採用；最終版回復下方綠地及中間直路。預設生成原件保留，只唯讀複製選定版本；提示及雜湊保存在 generation.json。已檢視十二張完整圖與 144／216 像素對照。首次 montage 未指定可用字型而失敗，補明列既有 Noto 後同 image 重生 overview；屬檢視環境，不是產品缺陷。v1 保留，v2 DRAFT manifest 8a90556b3065244377ae9cfbc414389b76fb71150c618623a06a05116caf5428，READY manifest cbbb76d9a14f71f540e310a073492c5b43f58b6a13ff3f99c081d55064ed1f32。

共 392 格、391 種原圖。體育場同源兩格依同設施全部可見唯一原圖定位，至少一個錨點、只准唯一解，否則回退。共用載入器按實際 ROM 表驗全部別名、雜湊、尺寸、偏移與使用色盤；成員數讀 header 69，末圖終點取成員長度，未把兩 ROM 合計 118 或不存在的 sentinel 套入單一 archive。未改原版程式、規則、時鐘或七補丁。

| 驗證 | 結果與證據 |
|---|---|
| 核心四項 | public-v2-tests-r1.log，55.163 秒。十二圖／區外、391 項來源失配、色盤、26 項實際素材故障與隔離、十二正常來源、archive 首末／越界、同源格原位／裁切／缺鄰格／錯鄰格通過 |
| 既有回歸 | public-v2-regression-r1.log，12.231 秒。警消、DISA1、道路、火力四項及 keyboard 通過；工具語法通過，無跳過 |
| 素材重生 | public-facilities-ready-repro-v2 十三檔與正式輸入逐 byte 相同 |
| 正常 GUI | TAIPEI_CITY_MENU_RUN=gui-public-r2 bash workspace/tools/facility_batch_playtest.sh hd，wrapper 0。真實新遊戲、垃圾場／體育場、F12、F11 五語系、PUBLIC.SAV 同次存讀及 DOS 退出；無快照、注入或長時間抽樣 |
| 獨立像素 | public_facility_check.py --run /workspace/runs/gui-public-r2 --scope public。八圖完整設施／五語系標籤／原版整張與六項正反對照通過；交換同源兩格再重算雜湊仍拒絕 |
| 四架構 | Linux amd64 54d04177；Windows amd64 0a9ac278；macOS amd64 3666e91c、arm64 0b2873ee。沿既有三 image 重編；原始 ELF／PE／Mach-O header 及 compiler objdump／otool 輸出核對，前版保留 |

正常報告 a163522a7e18d0c40811acb898d4b64e4e453fb2990a255b5dcadc29793a1e56，像素報告 caa694687de1c71ec711516faacfdc3dddcb0bcca6625f5ae12826df11cd6a18。PUBLIC.SAV 93567 bytes、SHA-256 02ff88bf23cdd719b3c8e1c2b935257a729e6d0f430b0ee1a101fe550ad8a6bc，讀回不變。已檢視體育場原版、繁中及英文實際畫面，其他語言標籤按固定參考逐像素核對。Linux 通過後提升標準入口；來源、七補丁、素材與四架構記錄 public-v2-final-provenance.json。首次彙整發現 GUI image 沒有 file 指令，改用既有 Python 解析原始 header，不新增 image 或退回主機。

036 v2 限十二項靜態圖及已驗路徑 CONFORMED，#60 以正常產品輸入／存讀／退出補驗。README 接續匯出體育場原版與五語系六張 PNG。其他相位、全新 EXE 冷讀、完整 RAM／CPU／RNG 對拍、外平台真機及正式封包未驗；完整 HD 與母項繼續。

### #58 十二項整批截圖與收尾

程式與驗證先提交 6ff4e57134c6bdb3d406419f6aec551ae5a1cbf8。export_public_screenshots.py --run /workspace/runs/gui-public-r2 --scope public --source-commit 6ff4e57134c6bdb3d406419f6aec551ae5a1cbf8，在既有 GUI image、network none、UID/GID 1000、2g／2 CPU／64 pids 與 120 秒上限核對正常收據及八張實際像素，再匯出體育場原版／HD 五語系六張 PNG。只有 screenshots 可寫；既有 48 張不改，各批來源提交仍保留。

README 現有 54 張唯一 1280×800 圖，共 42,344,222 bytes，本批新增 6,950,595 bytes，manifest SHA-256 314b1edc9af196d06a149dcf654940a21663194a02f556e3370170c42b375530。已回查有 local_capture 的十二份既有來源，其中正常城市均無新增設施來源，不需要重生未受影響的 DISA1／警消畫面。移到 WORKLOG 的四個規格目錄相對連結已依實際原路徑重設到專案根，所有連結乾淨重查通過。

README 功能表及體育場對照同步更新，來源清單只新增本批六張；CONTEXT 保持唯一現況。選定 PNG 明列加入 .gitignore 例外，素材、SAV、字型及原版檔仍排除。原版 35 檔、RAR、產品來源與七補丁、四架構雜湊、圖片尺寸／雜湊／擁有權及 Docker 清理另由最終收尾核對。其他相位、冷讀、外平台真機與正式封包仍未完成。

## 2026-10-14 十二項設施結案與核能來源接續

十二項設施的程式／驗收提交 `6ff4e57`、體育場六張截圖及文件提交 `9911f45` 已推送。README 共 54 張。#58、#60 已關閉並由主機 gh 回讀 CLOSED，#30 已回寫批次完成，其他母項保留 OPEN。最終衛生報告 `public-v2-final-hygiene.json` 通過；當時無遺留容器。

#46 接續前回查復古重製／規格閘門路由，載入 027 與遠端 Issue。六座正常城市探針 r1 誤用視覺網格推定 Right 切欄，第二次仍載入 DISA1；兩次正常保存／退出原件保留，未宣稱兩城。查回 033 的既有正常選取收據，改用 Down 依欄序遞增並逐步等待完整 disaster-city-N 來源。r2 其餘五座全部完成保存及原版退出。獨立原版底欄、DSA 讀取、實際 SAV 與退出核對通過，check.json SHA-256 `830675c58177f173520a91580e893c3473629dca2db6354caec4c1902af98c40`。六城資金均不足核能成本，數值記入 027。

不同財政條件 r6 使用原版預算將稅率調為 20、四項支出 0，逐批核對全部原版讀鍵與前端放鍵。480 次正常觀察完成，最後年 117 月 8、98428；117 年 1 月的 98528 不能取代最後值。年度收入為 11326／3089／3715／3085。原版步進批量改為 2000000 指令／Update、每六次 Update 收據，只用於研究效率，不改產品預設、原版速度 3、時鐘或資料。該次外層 exit 0，但未籌足、未保存或正常退出，不宣稱核能來源完成。

新增 DRAFT 的 power-funding-continuation 命令，從 EXE 重播 r6 真實 GUI 輸入，末端須與原版畫面／色盤／讀鍵／檔案操作相同，才以同一城市續跑並經原版鍵盤保存進度。第一件因未支援 GUI 的文字 metadata 與初始滑鼠移動而在啟動即拒絕；已依前端 queue 契約修正，文字 metadata 只核對同一步有實際掃描碼，實際掃描碼與滑鼠事件照錄重播。r2 已編譯並在有界、無網路、UID/GID 1000 的 Docker 執行中。只作來源研究，不代替 GUI 抽驗；未注入快照、城市、財政或 SAV bytes。

核能冷讀／整地／施工／存退讀探針已列於 027，仍為未執行 DRAFT。Python AST、shell 語法及 Go 命令編譯通過。研究工具都在 workspace/，成功來源與 READY 前不接產品。六城與 r6 容器已刪除，目前僅有界的 dosgolem 續跑容器。

續跑 r2 的固定末端比對通過，之後監測列印 funds=0 是沒有辨識值，不是原版資金。原因為 DRAFT 命令漏了現行前端的 SetLanguage 初始化，且誤要求左右兩欄 mask=3。回查 020 與實際 constructor／defer 契約後停止 r2；沒有將此件列為遊戲或模擬器缺陷。r3 先以固定原始收據的 inspect 模式確認合法右欄 mask=2、98428，exit 0，才重新執行。r3 末端比對後先用原版鍵盤 F2 保存 0000.SAV 保留進度，再按原版 3 續跑，最後另存 0001.SAV；不使用快照或自行改寫財政資料。

`power-nuclear-preflight-r1` 正常 GUI 前置抽驗外層 exit 0。原版冷讀 FUND.SAV、焦點切換、整地工具與單格游標、陸地候選及原版退出通過，種子 SAV 雜湊不變。實見原點 (6,22)、游標 (9,8)、整地費用 10、6×6 候選 (11,7)。沒有整地或施工，因此不宣稱核能來源完成。此容器已刪除，目前僅 dosgolem r3 有界續跑容器。新增來源目錄維持 workspace/，DRAFT 工具入口已掛入 027。

### 核能來源研究停止線與既有電廠

r3 續跑保存 0001.SAV，93567 bytes、SHA-256 `93918cfa7491b3538645abf77f2ee7615b9f519bd4b35b87c9da4263cd8bf391`，原版資金 104415。末端前綴四項比對通過，但退出前 120000000 步上限不足而回傳 2，不稱整輪通過。後續 r4 只延長退出觀察並保留 before-quit.json；未重跑財政流程。施工 r1 整地後仍有區域／碎石，r2 的顏色選址無候選，兩件未成功建設核電廠，保留原件。

IDA 9.4 窄查詢保留原始名稱、bytes 與位址。sub_19102 的工具 case 12 調用 sub_1A64C，檢查完整 6×6 的 dword_322BE=0 且 dword_322D8 非零；核能選項的返回值 3 在 sub_17BF8 形成索引 `18+30*row+col`。sub_17B52 確認寬度 dword_322F0、高度 dword_3233C。先前把 dword_322F2 當高度的假說撤回，正確資料及 bytes 保留於 ida-46/nuclear-dimensions.json。IDA 線性 0x322BE 對應 EXE 檔案偏移 0x242BE，MZ header 0x2000，載入空間偏移 0x222BE；各位址空間分開記錄。site-audit 從 EXE 重播正常 GUI 前綴並匹配四項末端，再唯讀匯出兩個原始陣列，實際城市為 105×89，沒有注入。

原版地圖已在 (60,44) 含 type 0x85、variant 18 的核電廠，因此停止籌資及空地探針。依使用者正常遊玩抽驗，改從原版既有電廠取得完整來源，核能新建施工另外列未驗。#46 已預登記冷啟動、原版冷讀、捲動、五語系、F12、存讀與退出。gui-nuclear-baseline-r1 的多餘 Space 在 Tab 啟用工具後整地並扣款 10，腳本資金斷言拒絕，沒有列 PASS；r2 移除該 Space，同一 image／binary／種子重新執行。沒有修改產品、原版規則或資料。研究工具與輸出保持 1000:1000，已結束容器皆 --rm。

### 核能來源與 READY 素材

gui-nuclear-baseline-r2 wrapper 0，正常冷讀 DISA1 既有核電廠、原版捲動至 (52,40)、完整來源、F11／F12、同次存讀與原版退出通過。verification.json SHA-256 `359a09e4dc68d30053cc6a6162b92392c776031e8d8d095131dee34aff823565`，NUCLEAR.SAV `10ae70c129292142430417bfa7328c1a1546d152039e59fb6c3ec61ba31b1d9a`。nuclear_sources.py 逐格核對 36 格／35 種來源，完整複合圖與原版 ROM38 相符，沒有用完整退出替代施工分支。

內建 imagegen 依完整正常參考生成一張 B 圖，保留原件，唯讀複製至 workspace/prototypes/hd-style/nuclear-v1/nuclear/。已檢視 216×216 與原版對照；原件、提示、來源與 READY seal 見 027。public_facility_assets.py 增加核能 stage 與 issue 參數，舊公共設施輸出不變。READY 兩檔在 nuclear-ready-repro-v1 乾淨重生，逐 byte 相同。獨立 nuclear_check.reference 重讀原版與生成原件，36 格、完整 186624 bytes RGBA 及色盤通過。

核能載入器使用泛化的封存 atlas 載入函式，原公共設施仍用原 seal；呈現器新增 nuclear_facility 統計與同源格唯一鄰圖定位。沒有改 dosgolem、原版 EXE、時間、規則或 SAV。核能三項及公共設施四項測試通過，nuclear-tests-r2.log 86.055 秒，無跳過。初次測試 image.Image 型別的編譯失敗已修正並乾淨重跑。Linux binary `9e4fa21247dd36ef6879fd89440ca473708fae22786b9c7a664d7f681735f1ec` 保存在 taipei-preview-nuclear-r1，舊標準入口保留，正式 HD GUI 執行中。

### 核能 HD 遊玩抽驗與 README 收尾

實作與工具提交 `c44b1abfef5cab176a15d924aed7d59ea28c8a02` 已推送。gui-nuclear-hd-r1 正常冷啟動、FUND.SAV 冷讀、原版鍵盤捲動至既有核電廠、完整 36 格覆繪、五語系及 F12、原版 F2 保存／讀回與 DOS 退出通過，wrapper 0。主收據 SHA-256 `f306c270e07e8936d010c304cb2ff3485f56d6bcab9f59a53e4293233311c8d0`。獨立核對八張全圖與六項正反對照，報告 `5d3c576791e4aff6c7efe0fee615b100d187dd9337ff9a4a9603ca416c861ae6`；同源兩格交換並重算雜湊仍拒絕。已檢視實際 HD 繁中遊戲畫面。

NUCLEAR.SAV 為 93567 bytes、SHA-256 `10ae70c129292142430417bfa7328c1a1546d152039e59fb6c3ec61ba31b1d9a`，與沒有核能 HD 的正常基線存檔逐 byte 相同，讀回不變。既有城市／警消／道路／火力四項回歸 28.077 秒；鍵盤與研究命令編譯通過，無跳過。這是正常遊玩與存檔證據，不冒稱完整 RAM／CPU／RNG 對拍，也不把既有電廠當作成功新建核能施工。

沿用既有 Linux／Windows／macOS 三個 image 完成四架構重編。Windows 編譯保留既有 YMFM 警告，回傳 0，沒有新增模擬器修改。Linux 標準 build_preview.sh 從固定 dosgolem 與七補丁乾淨重建，與已驗核能 binary 完全相同，提升標準入口。四個 binary 完整 SHA-256 見 027 與 nuclear-final-verification.json；外平台只有編譯／格式，真機未驗。

export_nuclear_screenshots.py 先重核正常收據與像素，再以來源提交 c44b1ab 匯出原版／HD 五語系六張實際 PNG。README 保留遊戲背景並增加核能對照，總計 60 張 1280×800、48,858,728 bytes。manifest SHA-256 `3f607a4d2b7de6250873fe2efd3142b488ee08ccb7e923765d0e06d57cd1be00`。僅這六張 PNG 加入明列例外，原版、HD 素材、字型、SAV、原始收據與 binary 均留本機。

回查正常玩家路徑、規格閘門與文件職責入口後，027 限火力／核能靜態圖與已驗路徑 CONFORMED，CONTEXT 及驗收矩陣同步更新。nuclear_final_check.py 核對 35 原始檔／RAR 未變、所有 Go 來源及七補丁符合 c44b1ab、四架構 header、實際存檔、60 張 PNG 雜湊／尺寸／擁有權與文件連結通過，結果 SHA-256 `c65dbd65203385c33242244e0f4920dc828fa8441678d31dd69a775e901f745e`。指定 find 無 root-owned 輸出或 .md 目錄，本批相關容器全數 --rm，主機 docker ps -a 的 project=taipei 清單為空。

新建核能施工、其他相位、完整機器狀態對拍、外平台真機與正式封包仍未驗。其他圖片與動畫繼續由 #30／#32 維護，完整 HD 母項保持 OPEN；失敗籌資與整地前件不再重新開啟相同研究。

## 2026-10-14：港口與機場 #61 接續

核能文件與六張截圖提交 f2e177353c9dfb910e624f08470eeb412e0e09f6 已推送，#46 更新本次抽驗範圍及限制後關閉，主機 gh 回讀 CLOSED。#30 已收到完成回鏈，相關容器清單為空。完整 HD 未完成，接續前先查遠端沒有重複的港口／機場 Issue，再建立 #61。

新批次命中規格閘門與 GUI 路由，沿用已載入入口，新增 037 前再讀文件職責；工作目錄沿使用者指定 workspace/，不新增 workplace/。既有 IDA 9.4 的 nuclear-check.json 保留原始 issue 46 與工具版本，不換名冒充新原件。窄查 sub_19102 的 case13／14 與 sub_17BF8 的對應 case，兩項使用同一六格陸地檢查，沒有新的財政或硬體逆向需求。正式來源語意仍待正常 GUI。

transport_facility_playtest.py／.sh 在 #61 預登記後執行，正常新遊戲、暫停、BASE 保存，工具12／13分別施工，原版重載 BASE 分隔兩件，最後 TRANSP 原版存讀及退出。沿用完整 ROM 格／已見游標變體的完成閘門，來源匯出不遮罩。Python AST 與 shell 語法通過；目前來源探針有界執行中，產品仍為已驗核能版本 9e4fa212，本批 HD 未接入。原版唯讀、UID/GID 1000、3 GiB／2 CPU／128 PID、無網路、外層1800秒，Xvfb由同一容器trap擁有。沒有改原版財政、時間、規則或 SAV。

r1 港口正常施工完整 36 格已取得，費用 80000，資金 80000→0，來源 ROM38 基底6。原版重載 BASE 後機場顯示成本100000，腳本在施工前因資金不足而停止，wrapper1；不列產品缺陷或兩項完成。執行原件為 transport-source-r1/executed-driver.py，沒有覆寫成新探針。

唯讀核對先前原版 FUND.SAV 與 nuclear-site-audit-r1 匯出的兩個9345-byte陣列，完整相等的 SAV 偏移分別為115、9460。只用於定位既有城市候選，不作正式資料格式或新規則。六座已正常保存的城市中，DISA4 在 (25,5) 有 type0x85／variant6、(47,29) 有 type0x85／variant0；圖像語意仍由正常 GUI 逐格確認。改用 DISA4 的正常存檔來源，資金73455，不再進入籌資或整地迴圈。新探針及唯讀種子／鏡頭／世界位置已寫037並於#61追加預登記，來源及正式HD分階段執行。

### 港口／機場來源修正與 READY

r2 候選完整性補查發現 DISA4 (25,5) 的港口缺一格，(26,5) 已為 type6／variant7 碎石。主動停止、保留 partial-scope 與執行原件，不用根節點代替完整6×6。原版唯讀資料確認同城機場(47,29)與港口(43,73)全部36格完整；r3 改先機場視窗(36,24)，再港口視窗(32,68)。這是候選修正，不改遊戲或猜補缺格。

r3 到達機場原點後，游標定位立即拒絕。原件對比證明2064000000步鏡頭已完成、(1,1)仍是完整ROM59地景；2066000000步沒有新輸入，才出現完整32像素游標邊框。真因為原點觀測早於游標重畫。沿既有GUI／#60契約，r4只改等完整已知游標，再移開並等完整36格來源，不加固定延遲、遮罩、原版補丁或時鐘特例。transport_source_prefix.py 保留r3實際capture.zip原名，只匯出完整機場來源，明示未完成退出。

r4 正常EXE冷讀DISA4、兩項原版捲動、完整來源、TRANSP存讀與原版退出通過，wrapper0，verification SHA-256 `bd859c75ccfb7c86a766be1008162608b470ba038a52c1478cc22fc83d55330b`。實際SAV `8dfab3da2107cfb0d701d7aef796d25d5f5c5a2de473f7e418fa5c61ef123e27`，資金73455保持不變。全部前件保留，不再重跑財政探針。

兩項各36格，合計72種唯一來源，無其他圖庫或地景重疊。內建imagegen依完整來源生成港口及機場。港口原件 `37d6b8476aaa52425b3c548d94066fc4ea1d28fca5c536137274222c7e53504b`；機場v1右側建物越過青色外緣，v2只修復該邊界，原件 `9515116c6decb1876cf9f2f26d5c165b73d875f733a6e77614ad5fafb8458c77`。原版圈H經白色像素逐點確認，保留而非新造標示。提示與前件保存在transport-v1各素材目錄，預設生成原件保持原位。

已檢視兩張216×216原版／B對照。DRAFT manifest `3ad256026ebfa478fbe0da48e1053131079c5d4b10787b5320f8f388546094cd`，READY `78a955c44ab2078eb5d4b71bff534101fc0dc110cc6f4aa3edde27fe5b6dc191`，獨立重讀72格／50種已用色盤及完整生成原件縮放通過。037先達READY，再接入兩個atlas與transport_facilities統計，不改原版規則與SAV。

核心運輸兩項、核能三項與公共同源一項測試通過，transport-tests-r1.log 10.123秒，無跳過；驗完整圖／全部區外、場景、來源與色盤、家族衝突及六項實際素材故障隔離。Linux候選 `d2c326607d0b111501371c6cc7db55d68bd1954d3f8e40f5bba1e076bed6f644`，正式HD GUI執行中，標準入口仍保留9e4fa212。

共用來源／素材／像素／匯出工具增加issue61與transport分支，舊公共設施原始像素報告相同。環境舊報告使用不同scope文案，不能以整份JSON相等判斷產品退化；其八份原件及五項有效對照均與新核對結果相同，歷史文案保留。首次回核誤用gui-public-r1路徑，改從截圖manifest讀取gui-environment-r1，不列產品缺陷。收尾工具新增--batch transport，舊核能預設保持原契約。所有分析／建置／GUI在既有image、原版唯讀、1000:1000執行；來源容器已刪除，現在僅有界HD GUI容器。

### 港口與機場 HD 驗收及 README

實作提交 `487953922bc0dec7e45b28155fdfa3ec438a33c0` 已推送。`gui-transport-r1` 正常冷啟動、冷讀 DISA4、兩項捲動、各六張原版／五語系、F12、原版存讀及正常退出通過，wrapper 0。已檢視實際機場與港口 HD 繁中遊戲畫面。

| 驗證 | 結果 |
|---|---|
| 正常 GUI | 主收據 SHA-256 `17fa9dc60428642b3ba11ee9a2cc50e449a40d2bd7cd649290417cb0f34994a4`，兩項各36格實際覆繪，資金73455保持不變 |
| 獨立像素 | 十二張全圖、原版整張及五項有效正反對照通過，報告 `07eb2a90eb4e9c51e9490c576ccf43ca8b8c6a37789128d9ae3f7209850d8793` |
| 原版 SAV | 93567 bytes，`8dfab3da2107cfb0d701d7aef796d25d5f5c5a2de473f7e418fa5c61ef123e27`，與無運輸 HD 的 r4 基線逐 byte 相同，讀回不變 |
| 素材重生 | `transport-ready-repro-v1` 的 manifest／airport.png／port.png 三檔與正式素材逐 byte 相同 |
| 四架構 | Windows／macOS 兩架構編譯通過，保留既有 YMFM 編譯警告。Linux標準入口從固定 dosgolem 與七補丁乾淨重建，與已驗 d2c32660 相同；完整雜湊見037 |
| README | 匯出兩項各六張實際PNG，共72張、61,351,056 bytes；manifest `bfb77f62ce56110cb4be8b45898c2269b47cda8253948e775c133f63eb61353e` |

README 保留遊戲背景，新增機場／港口原版與五語系並列表。只有明列十二張文件 PNG 加入私人儲存庫，原版、素材、字型、SAV、原始收據與 binary 仍留本機。CONTEXT、037 及驗收矩陣同步更新，037 限本批靜態圖與正常既有城市路徑 CONFORMED。

收尾重新核對正常遊玩、規格與文件職責契約。`nuclear_final_check.py --batch transport --source-commit 487953922bc0dec7e45b28155fdfa3ec438a33c0` 通過，輸出 `transport-final-verification.json`，SHA-256 `35e8631187eaeb690aaa2f179d7a91d86c523adbf5950a954464775f8642e314`。35個原始檔與RAR未變，全部Go來源及七補丁符合指定提交，四架構header、原版SAV、72張PNG尺寸／雜湊／1000:1000與文件連結通過。指定find無root-owned輸出或.md目錄，相關容器清單為空，沒有新增image。

新建機場、其他動畫相位、完整機器狀態對拍、外平台真機與正式封包未驗。完整圖片與動畫由#30／#32接續，這批結案不宣稱全部HD完成。

## 2026-10-14：剩餘地圖圖庫 #62

#61文件提交aed180b已推送，主機gh回讀CLOSED。接續先建立#62，命中規格閘門及正常GUI路由，沿既有034–037與026來源契約。038建立時再查文件職責並掛入CONTEXT；不重新開啟已完成批次。遠端Issue初稿的教育／醫療用途未證實，已修正為ROM37 base8編號。

唯讀九圖庫共1134位置／1049種原圖。map-coverage-audit只替換呈現副本的一格，不跑VM、不改SAV，明示合成診斷。原先760種辨識、745種單格可繪製，空白來源57個位置；原核能／體育場同源缺鄰格不重開。301種非空待補為十三複合圖208位置／207種、三區域48位置／36種、小格58種。第一版資產腳本的207／36分類假設寫反成208／35，被完整bytes計數攔下；修正後乾淨重跑同命令，總數301不變。

沿既有IDA9.4原件sub_17BF8 loader linear 0x17FD1–0x17FE6的24*row+4*arg6+col，不推定建物成長規則。六份正常SAV只唯讀找候選，313筆完整4×4候選仍標強推論，直到正常GUI逐byte確認。原版字樣住／商／工已檢視，新增唯一TSV三鍵，韓文주／상／공與英文R／C／I；原版仍維持原字。

內建imagegen依十三張完整原圖逐張重繪B圖，提示、原始生成圖／預設路徑、來源與權利保存在本機map-completion-v1。整張縮至144×144後切格，原版／HD並排已檢視構圖、輪廓、色塊與邊框。首次聯絡圖montage因fontconfig不可寫cache崩潰，明確指定已有Noto與/tmp cache後同image重跑成功，不列產品缺陷。

038先達READY，才接map_completion.go與呈現器。原有批次優先序保留，新家族在城市建物後接入；來源81bytes、全部別名、已用色盤、封存素材與opaque形態同時檢查。共享圖只有裁切完全相同才可免定位，否則依完整可見唯一鄰格。全黑填充辨識為空白，不冒稱重繪。Noto未就緒使區域原版回退，不影響其餘介面。

READY根manifest be04e87136b05e09c3eb92402eea6173280687c9323fdf97cef77c2c8dd10a10，complex／zones／detail子manifest依次559fb204、e2af961d、b115c099，完整值見038。重建與DRAFT子manifest相同。核心兩項10.616秒無跳過，十三整圖／全部區外、十五區域字墨與整圖、24381來源變異、301色盤失配、十二項實際素材故障及隔離、共享負對照與場景閘門通過。合成單格1049種全部辨識、1045種繪製；三個共享來源需鄰格及一個空白明列，不冒稱正常GUI。

正常GUI候選gui-map-r1與無新增HD的map-baseline-r1皆由真實EXE冷啟，依038預登記的七代表走原版讀取兩城市副本、方向鍵捲動、移開完整游標、F11／F12、Help、存退讀及原版退出。僅診斷工具免複製每次路由鍵的整份zip，原版按放／逐次讀取與最終原件仍完整保留。標準入口尚未提升，相關有界GUI容器仍執行中；沒有修改原版、dosgolem上游或七補丁。

### #62 抽驗路由修正

r1兩側在第一個目標Y9往返，主動保留route-boundary-capture.zip／partial-scope並停止容器，不當玩家驗收。最初暫判是Y10邊界，回查路由入口與既有transport-source-r4原件後否定：airport-route-X-15原點38，下一次為36，原版每次捲動兩格。Y9與偶數原點不相容，實際在8／10往返，並非原版不能向上捲動。partial-scope另加勘誤，保留最初暫判原因。

修正七個鏡頭為同一世界圖像的可達偶數原點，增加奇偶拒絕檢查；不改正式程式、虛擬時間、相位或原版輸入。gui-map-r2／map-baseline-r2用同一容器與命令乾淨冷啟重跑。使用者看到的邊界進度說明由本勘誤及新進度修正；r1只作腳本診斷，不列產品缺陷。兩個舊容器已刪除。

r2路由已按預期進展，但每鍵須等六次完整收據而增加閒置步數。沿已完成#59的可設定收據頻率，r3兩側改每更新一份，不減少按放／原版讀鍵、完整ROM來源或存讀退出判準。r2原件保留route-prefix與partial-scope後停止刪除容器；不是產品失敗，不要求長時間狀態重播。r3執行同一腳本與容器，第一至第三代表已取得正常完整圖與五語系。

## 2026-10-14：開場與動畫 #32 來源原型

主機gh先在既有#32回報接續範圍。建立039 DRAFT前再查文件職責並掛入CONTEXT，沿033原版IV2／raw／RLE及唯讀呼叫契約，不新增玩法或時序推測。illustration_sources.py匯出209筆／197種非9×9完整圖，inventory SHA-256 d67d234268f912cfc049ebad59ecf706d967ee2e6ce6d5d95a9c21678d356f5a。數量包含既有介面原圖，不當197張未完成素材數。

ROM52–55每個八筆offset表，32個IV2相位完整消耗並以加法進位結束，所有literal位於64000色號範圍。保留相位原左上空白與別名，不剪掉後錯位。七份105×89世界資料、字型／色盤／音訊分別記錄，不把能解出長方形都當獨立插畫。原初盤1317候選扣七份世界資料加33筆IV2後為1343圖像來源／1246種原圖，其中9×9仍1134／1049；細分用途、正式色盤與呼叫時序尚待39審查。

來源總覽使用正常城市色盤，只作導覽，不宣稱開場正式色盤。兩張開場門樓以內建imagegen製作DRAFT。a04 v1誤造匾額文字，已拒絕；v2由imagegen移除該文字，空白圖板仍待原字墨復原與完整契約，不能進產品。a05亦只為DRAFT。三份生成原件、提示、sha與預設來源路徑在本機illustrations-v1保存，原件保留預設位置。沒有把生成圖當真實GUI截圖，沒有改本輪已編譯程式。

### #62 正常來源與完整退出的範圍分開

r3兩側已取得C1五種完整4×4原圖，HD側有各原版／五語系30張真實PNG。C2候選m35-b12／m36-b16路由在舊d2c與新874版皆未達目標；128鍵上限停止，wrapper1，原件與執行driver保留。不能只由失敗判定HD退化。暫猜多送Tab改變焦點，但原件activate-saved-tool及先前完整C1都呈現tool0外框32、其餘15，無法證實該猜測；不寫成真因。原版C2路由保持未知，兩高階候選未正常抽驗。

依使用者正常遊玩代表抽驗與停止線，不再重跑已有五組圖像，也不深挖C2控制內部。r4兩側正常冷啟C1，以商業區(38,24)／鏡頭(14,22)及另一同源ROM37-b08(54,24)／鏡頭(30,22)兩重複代表完成存退讀與退出。之前五組來源前段不補造native_exit，獨立核對逐份保留source_run與normal_path_complete。合計七組視圖、五種不同正常來源、42張真實PNG；三組新圖案仍只由前段確認，原版SAV垂直路徑由完整C1流程驗證。高階圖片整張及所有來源故障診斷已通過，正常出現分支列未驗。

### #62 驗收、標準入口與 README

r4兩側wrapper0，HD另驗Help。正常主收據8d1c8772，舊版ea697316，獨立42圖e56bd100；完整雜湊見038。93567-byte MAPHD.SAV為7ca351e35aa6ed8c3f5da525d88af43eab1f00add2989c0fd4b13bfe20efd55b，兩版及讀回後逐byte相同。42張原版整張／B整圖／Noto字墨與背景及42個有效像素反例通過，沒有把r3補成退出完成。

Linux標準入口從固定dosgolem與七補丁乾淨重建，與已驗87439f2f候選相同。Windows amd64／macOS兩架構已重建，header核對通過。136檔READY素材乾淨重生全部相同。十二張明列文件PNG已匯出，README合計84張／75,683,303 bytes，manifest 78e5b0f1873d3e51ba345102c42ca6ccdce24d8bf58d252f4361e8087f807621。首頁顯示最新完整地圖，新增建物／區域原版與五語系，舊批照片保留各自程式版本。

收尾前回核路由與同一規格閘門。map_completion_final.py --source-commit 42639adb07abdf5f6134bdc8fb40263e1a882191通過，map-completion-final.json SHA-256 77ac8656256286affdbbc340146823f95228ff39dcda272b6643a003a75805e1。35個原始檔與RAR不變、全部Go／TSV與七補丁符合提交、四架構／136素材／84PNG／文件入口／1000:1000通過。指定find無root-owned或.md目錄，主機project=taipei容器清單為空，未新增image。

038限完整來源呈現與五種正常代表CONFORMED。C2兩高階路由未取得、成長／災害分支未逐項試玩、外平台真機、人耳與正式封包未驗。所有原版／美術／字型／SAV／原始收據留本機；提交僅原創程式、工具、文件與十二張已授權截圖。開場與動畫039仍DRAFT，接續#32，完整HD與封包不稱完成。

e5d97ac90c830725ad4f9d898ba14e9d7adf031a含文件／十二PNG／匯出核對工具已推送。#62附完整證據、命令及前段／完整流程限制後結案，主機gh回讀CLOSED。再即時回讀#29／#30／#31／#44最新留言，確認舊OPEN只留下已由後續批次解決的範圍；分別回鏈現行來源與限制後關閉，五項均回讀CLOSED。九圖庫範圍不包含#32非9×9插畫／移動物件與動畫，完整HD與三平台封包仍未完成。

唯讀比對aed180b的唯一TSV：原225鍵五欄全部相同，只新增038三個區域鍵。現行228鍵／1214種字元，SHA-256 b68456b42325baa572b614f85a2d285a98a61049f189d6ce03b59887b78d901b；新字墨已經實際固定Noto/OFL五語系檢查。033改明示歷史驗收版本並追加038入口，不重寫舊收據。#31結案只外推已核對文字來源，成功結局／停用密碼／未知用途與裝飾原標誌限制保留。

### #32 原版呼叫與完整相位原型

沿已載入規格／GUI路由與033既有IDA9.4原件，確認透明RLE、raw整張覆蓋、IV2、raw裁切兩種契約，原始名稱、bytes、位址與輸入SHA保留；未重新啟動IDA或硬體driver逆向。三十三筆IV2沒有literal255，未寫背景可安全以255標記。ROM0與ROMA3量化後相差七色，正常城市另有四個運行改色。a05第一次呼叫尚是前一色盤，不能據此宣稱最終發布色盤。

illustration-source-audit正常EXE無輸入前段8億步，28種圖像／30種來源呼叫組合／1362次返回全部與完整後緩衝合成相同。r1 f22294d8原件保留；r2補before／after與最大可見矩形，48份保存例中27份全圖。獨立Python重讀原ROM而非信任Matched，46個實際來源像素變異有效，兩個首次極窄裁切無非透明像素明列。r2 audit c0db0977、核對3b37b5d2，完整SHA見039。沒有將後緩衝證據稱GUI、HD或發布畫面，沒有RNG比較／重擲。

illustration_groups.py生成53組／170相位來源參考，manifest 13c5aac1；其中游標只作來源對照，52組可作美術批次。原始同源別名、每格原生矩形與參考SHA保存，已完成UI／Noto標題及七張城市預覽另分類。所有提示與生成原件只留workspace，預設原件保持原位。

先以r25六相位、r42雙相位驗證組圖。r42-v1多出白邊與未證實的手持細節，拒絕進產品。proto-v1直接回覆整塊原圖小形狀區，產生背景色塊接縫，亦未READY；執行原腳本保存在該目錄。v2由imagegen只保留背景板、去除猜造前景，原人物及紅色小形狀按原始色號輪廓與B材質覆回，保留相位。白邊逐列實測RGB差3，原參考邊緣非單色；程式採每通道差5的近單色與參考閘門，不裁真正純色背景。已檢視640×384兩相位及r25完整原型，沒有把原始小形狀猜成新道具。v2八圖manifest 99c3de63，完整SHA見039。r43–51批次先保留DRAFT，逐張核對同類前景後再用同機制。

本批皆Docker、原版唯讀、1000:1000、無網路與有界資源；兩個唯讀探針容器已--rm，沒有GUI背景程序或新增image。現行產品仍為87439f2f，尚未接入039，完整圖片／動畫與三平台封包持續未完成。

## 2026-10-15：#32 完整插畫原型與發布色盤

52組169相位，加兩門樓、七預覽與用途未定的A35，共179個完整四倍DRAFT；18種既有UI／Noto另列。54份選用生成metadata保留提示、來源與修訂雜湊。v10 manifest ebe1576e、獨立核對9b62f6e5，完整SHA與入口見039。重讀209筆／197種，驗尺寸、外背景、黑場、跨圖共通區及四個有效破壞反例。

逐像素複製共通色號造成角色鋸齒，已改用完整B背景板；R42–51的小人物保留原輪廓與全部相位差異。灰色間隙實際有漸層，先核對色域與參考邊緣才裁除。A33弧線包含14及195兩色，舊只取14的假說已由原始bytes推翻；A15／16的57像素差異含眼鏡與嘴形。前件及原執行腳本保留，結構PASS沒有外推整體美術或正常GUI。

沿033正常r15標題、百貨、交通及獎章四份原件，獨立重算原生PNG與色號／色盤相同，256項均為ROMA3 VGA6-bit展開；城市色盤差11項。新收據c8a44941只確認原版發布配色，未驗新HD。現行87439f2f產品、84張README照片與228鍵TSV本批未變。

全部後處理在固定GUI image、原版唯讀、1000:1000、有界資源且無網路。project=taipei容器清單空，未新增image。原型、字型與原始收據留本機；提交只含工具與文件。完整HD與正式三平台封包仍未完成。

### #32 READY 接入、實際素材與正常GUI

依六原生ABI、209原始別名／197種、原版完整合成與發布色盤，039限來源及保守覆繪升READY。正式素材由固定179張原型另建，260個PNG及manifest共261檔；乾淨重生逐byte相同，manifest 545b4f94，完整SHA見039。原型標記不變，素材仍僅本機。

新增嚴格raw／RLE／IV2解析、唯讀原版觀察、有界順序及遮擋、未知呼叫屏障、已知色盤變體與逐圖故障回退。Noto欄位先清原字墨，覆繪後沿HD底圖畫字；普通逐字文字保護矩形。原版資料、時序與存檔不寫入。七個圖表原圖的兩個顯示鍵新增為230鍵，原228鍵不變，字元集合仍1214種；中央動態圖表沿029已完成契約。

實際ROM／537個色盤變體、五語系新字墨、缺圖／竄改PNG／manifest隔離及來源／色盤／透明色／重疊／未知屏障測試通過。五語系各156開場階段及36城市訊息階段回歸通過，觀察器記憶體／CPU／步數唯讀檢查通過。

r18正常冷啟、F11／F12、93567-byte原版存讀檔及DOS退出通過，2,902,002,774步。交通曾回退，原因為161C3守衛錯將寬度大於255一概拒絕。既有IDA原bytes確認初始偏移AL×CL但列距仍完整BX，sy=0寬294／296圖成立；修為比較實際乘積，非零不等乘積仍回退，新增反例通過。r16／r17名稱已存在造成wrapper啟動退出，未跑產品，改用先查明空白的r18，保留既有資料。

候選r2 fa212691已建立；r19正常重驗已顯示交通B圖、銀行五語系與Help，完整存退讀、獨立像素核對及README匯出尚在進行。標準程式仍87439f2f，未宣稱039 CONFORMED或封包完成。所有輸出1000:1000，未新增image；r19為有900秒上限及Xvfb trap的作用中容器，結束時再核對清理。

### #32 正常抽驗閉合與92張README

r19新候選已確認十圖、銀行五語系／F12及Help，但420秒驗證上限在letter.easy後截止。這是GUI驗證預算，沒有遊戲崩潰證據；不調原版速度，也不重播已取得插畫。改由同候選r20真實冷啟、原版Space略過片頭、進城、F11／F12、14原版讀鍵／release及存退讀，1,797,602,774步原版退出通過。r19原件保留為前段，r20完整verification e628e40f，沒有偽造r19成功標記。

獨立工具直接重解ROM及封存PNG，十張照片165591個原生位置的四倍格全部相同。r2核對更改實際呈現緩衝再重跑同一完整核對，十個有效像素反例拒絕；收據9e8b94ee，完整SHA及命令入口見039。r20的93567-byte SAV為4152f923，讀回後不變；沒有比較未受控亂數的不同局。

標準Linux入口乾淨重建為fa212691，與已驗候選相同。八張明列PNG已匯出，README合計92張／79,734,099 bytes，manifest cc5847f6；新增五語系銀行、原版銀行、門樓及交通。圖片保留各自來源版本，沒有把角色自然移動的五語系照片稱同狀態。原版資料、字型、素材、SAV及原始ZIP仍不入Git。

回查規格／README路由，039限完整來源與正常代表升CONFORMED；全部圖像1343筆／1246種已分類，未知用途保留原編號、不推定每一事件都已玩過。正式封包及外平台新版本由#9接續，避免為同一素材重編兩次。指定find沒有root-owned檔或.md目錄；Python stat曾跟隨Wine的z:連到根目錄，這不是symlink本身的擁有權問題，沒有chown。project=taipei容器清單空，未新增image。
