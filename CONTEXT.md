# 模擬台北：目前現況

核對日期：2026-10-11。目標是完成原版與 dosgolem 整合，並提供 HD 呈現。

使用者已指示恢復工作，繼續整合與驗收。

## 有效決策

- 私人儲存庫：[wicanr2/taipei](https://github.com/wicanr2/taipei)。Issues 已啟用。
- 使用者已授權主機 gh、專案提交與推送，以及本範圍的 Issue 管理。
- 使用者指定所有工作區放在本專案的 `workspace/`。原始輸入保留原位並唯讀使用。
- 原版規則、EXE 與存檔格式保持原樣。
- HD 美術採 B「細緻手繪材質」，以使用者最新改選取代先前的 A。HD 解析度為 1280×800，對應原版 320×200 的四倍。
- 使用者選定 Windows、Linux、macOS 三平台封包，字型採 Noto 高清黑體。固定使用已展示的 Noto Sans CJK TC Regular Sans2.004；平台實機驗收另記限制。原版確有 F1–F6 標示，按鍵語意依原版驗證。
- 使用者確認「允許在遊戲中切換」，採已提出的 F12 即時切換原版／HD。切換只改呈現，保留目前遊戲狀態，不將 F12 送入 DOS。操作契約見 [014](docs/spec/014-live-theme-switch.md)。
- 使用者明確指定「重繪範圍 所有的圖片 與操作界面」。完整範圍涵蓋地圖／建物／設施、工具列／按鈕／框架、全部選單與視窗文字、圖表、開場／插畫／事件及動畫相位，沿用已定案風格與原版版面。

使用者已回覆「Noto 高清黑體」，[#18](https://github.com/wicanr2/taipei/issues/18) 的字型方向已定。已展示比較圖保存在本機 `workspace/prototypes/hd-style/font-comparison/comparison-fonts.png`，SHA-256 `2ec3eea917c9dc173b31e30b5dbd9042f4ff4fca3f0f62a978281a3db5708c28`；含原版畫面，依素材邊界不入 Git。固定字型 SHA-256 `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4`，授權為 SIL OFL 1.1。後續全部文字依已確認方向接入，不以六個標題原型宣稱全遊戲文字已 HD 化。

正式切換操作與完整重繪範圍已定案，不再等待相同決策。現有研究前端的 F12 已有正常 GUI 收據；正式接入依 #7 驗收。全部素材先盤點來源，再逐批建立 READY 規格及接入；未知來源回退仍列未完成，不能把局部地景與六個標題當成完整交付。

## 目前狀態表

| 項目 | 現況 | 證據或限制 |
|---|---|---|
| 私人儲存庫 | 已由主機 gh 回讀 PRIVATE，Issues 啟用 | 遠端原為空儲存庫 |
| 工作項目 | 初始 9 張 Issues 已建立 | 狀態只以 [遠端 Issues](https://github.com/wicanr2/taipei/issues) 為準 |
| 本機 Git | 沿用使用者建立的空 clone，管理資料移至專案根目錄 | 原 clone 只有 `.git`，沒有提交或其他檔案 |
| 原版輸入 | 35 個檔案、7,919,834 bytes；RAR 與逐檔 SHA-256 已保存 | [輸入基線](docs/re/001-input-baseline.md)；原版精確版本與權利人仍未知 |
| 啟動入口 | `模擬台北/RS201/RS201.EXE /A /D /x` | 兩個 EXE 同雜湊；批次檔與兩個 config 一致 |
| dosgolem 啟動 | 冷啟動到主選單與城市選擇通過，兩次主選單畫面及暫存器一致；新增 Caps Lock 補丁通過核心與硬體讀鍵測試 | [啟動基線](docs/re/002-dosgolem-startup.md)、[Caps Lock](docs/spec/007-bios-caps-lock.md)；補丁只在隔離副本與本專案保存 |
| 原版前端與存讀檔 | 正常 GUI 冷啟動、新遊戲、電線施工、檔名退格、原版存檔、離開與全新啟動讀檔通過；施工格讀回相同 | [#4](https://github.com/wicanr2/taipei/issues/4)、[前端契約](docs/spec/005-frontend-preview.md)；限已抽樣玩家路徑 |
| 即時音訊 | OPL2 節奏與旋律串流已接實際播放器；冷啟動 monitor 非靜音，延後聚焦及有界緩衝通過 | [音訊契約](docs/spec/009-opl2-audio.md)；硬體規格近似，尚未做人耳與平台真機確認 |
| HD 範圍 | 所有圖片與操作介面已定案；完整來源初盤為 118 個 ROM 成員、1317 筆圖片來源，保留別名與未知項；另取得 402 個中文字模及原始字碼 | [完整範圍](docs/spec/015-full-hd-scope.md)、[來源盤點](docs/re/008-full-asset-inventory.md)、[字模證據](docs/re/009-chinese-font-sources.md)；數量不代表全部重繪完成 |
| HD 接入 | B 地景原型、六個 Noto 標題、十四個工具圖示、新遊戲說明及三種啟動選單已接入研究前端；十三種選取與三場景 F12 通過。40 份選單與 37 份存退讀收據均通過，存檔雜湊相同 | [動態原型](docs/spec/010-hd-live-prototype.md)、[Noto 原型](docs/spec/013-noto-menu-prototype.md)、[工具圖示](docs/spec/016-city-tool-icons.md)、[說明視窗](docs/spec/017-new-game-dialog.md)、[啟動選單](docs/spec/018-startup-menus.md)；其他圖像、框架、文字與場景仍未完成，正式封包另驗 |
| 跨平台編譯 | Linux amd64、Windows amd64、macOS amd64／arm64 完整研究前端編譯通過；Windows binary 經 Wine 冷啟動至城市，原版畫面與 Linux 相同 | macOS 未真機執行；Wine 及結構檢查不等於封包或真機驗收 |
| 封包 | 尚未建立 | 不宣稱正式 HD 完成或跨平台封包已驗 |

## 文件入口

- 啟動選單完整面板載入：[panels.go](workspace/app/internal/hd/panels.go)，契約見 [018](docs/spec/018-startup-menus.md)。本機生成提示為 `workspace/prototypes/hd-style/startup-menu-generation.json`。
- 啟動面板獨立核對：[hd_panels_check.py](workspace/tools/hd_panels_check.py)，驗完整來源、固定參考及區外，不免驗面板區域；負對照見 [hd_panels_negative.py](workspace/tools/hd_panels_negative.py)。
- 啟動面板實際資源測試：[panels_test.go](workspace/app/internal/hd/panels_test.go)，使用正常 GUI 的十三種來源及失配條件。
- 啟動面板同狀態結果：`workspace/runs/panels-state-audit.json`，相同正常輸入兩側各 1,776,000,000 步，十三種選單及完整原版狀態相同；來源與執行檔雜湊見 `panels-state-provenance.txt`。本批未驗其他分支或正式封包。
- 啟動選單正常 GUI：[startup_menu_playtest.sh](workspace/tools/startup_menu_playtest.sh)、[startup_menu_playtest.py](workspace/tools/startup_menu_playtest.py)，對應 #31，驗十三種選取、三場景 F12、無效鍵與原版取消語意。
- 啟動選單契約：[docs/spec/018-startup-menus.md](docs/spec/018-startup-menus.md)，對應 #31，完整三選單與十三個選取狀態。
- 啟動選單來源審查：[startup_menu_catalog.py](workspace/tools/startup_menu_catalog.py)，從固定底圖逐點核對正常選取畫面與原文字模。
- 啟動選單離線工具：[startup-panel-prototype](workspace/app/cmd/startup-panel-prototype/main.go)，依固定 Noto、來源及素材輸出完整面板，掃描 240 個實際墨跡；執行時只接受 018 審查的固定面板。
- 新遊戲說明視窗：[docs/spec/017-new-game-dialog.md](docs/spec/017-new-game-dialog.md)，對應 #31，完整來源辨識、B 底板、Noto 原文與回退契約。
- 說明視窗呈現與失配測試：[dialog.go](workspace/app/internal/hd/dialog.go)、[dialog_test.go](workspace/app/internal/hd/dialog_test.go)。
- 說明視窗獨立核對：[hd_dialog_check.py](workspace/tools/hd_dialog_check.py)，重算完整來源並核對固定面板與區外像素。
- 說明視窗負對照：[hd_dialog_negative.py](workspace/tools/hd_dialog_negative.py)，檢查改寫像素與同步更新雜湊仍被拒絕。
- 規則：[AGENTS.md](AGENTS.md)。
- 唯一工作狀態：[GitHub Issues](https://github.com/wicanr2/taipei/issues)。
- 驗收：[docs/verification-matrix.md](docs/verification-matrix.md)。
- 歷程：[WORKLOG.md](WORKLOG.md)。
- 原始輸入：[docs/re/001-input-baseline.md](docs/re/001-input-baseline.md)。
- 啟動與鍵盤：[docs/re/002-dosgolem-startup.md](docs/re/002-dosgolem-startup.md)。
- 可重現探針：[workspace/tools/probe.sh](workspace/tools/probe.sh)。
- BIOS 鍵盤路由：[docs/spec/001-bios-keyboard-routing.md](docs/spec/001-bios-keyboard-routing.md)。
- BIOS 等待模式：[docs/spec/002-blocking-bios-input.md](docs/spec/002-blocking-bios-input.md)。
- DOS 原生輸入：[docs/spec/003-console-keyboard-input.md](docs/spec/003-console-keyboard-input.md)。
- 探針紀錄：[docs/spec/004-probe-trace-memory.md](docs/spec/004-probe-trace-memory.md)。
- GUI 研究原型：[docs/spec/005-frontend-preview.md](docs/spec/005-frontend-preview.md)。
- 有序文字輸入：[docs/spec/006-ordered-text-input.md](docs/spec/006-ordered-text-input.md)，對應 [#14](https://github.com/wicanr2/taipei/issues/14)。
- BIOS Caps Lock：[docs/spec/007-bios-caps-lock.md](docs/spec/007-bios-caps-lock.md)，對應 [#15](https://github.com/wicanr2/taipei/issues/15)。
- 原型程式：[workspace/app/cmd/taipei-preview/main.go](workspace/app/cmd/taipei-preview/main.go)。
- 原型建置：[workspace/tools/build_preview.sh](workspace/tools/build_preview.sh)，第一次可用 `--download` 下載鎖定依賴。
- GUI 冷啟動驗證：[workspace/tools/gui_playtest.sh](workspace/tools/gui_playtest.sh)。
- GUI 操作診斷：[workspace/tools/gui_explore.sh](workspace/tools/gui_explore.sh)，只供快照探索。
- ROM 來源盤點：[workspace/tools/rom_catalog.py](workspace/tools/rom_catalog.py)。
- HD 圖塊證據：[docs/re/003-rom-graphics.md](docs/re/003-rom-graphics.md)。
- B 風格材質原型：[docs/spec/008-hd-material-prototype.md](docs/spec/008-hd-material-prototype.md)，離線程式為 [hd-prototype](workspace/app/cmd/hd-prototype/main.go)。
- 原型重生與負對照：[workspace/tools/hd_prototype.sh](workspace/tools/hd_prototype.sh)，驗證程式為 [hd_prototype_check.py](workspace/tools/hd_prototype_check.py)。
- 中文字型比較：[workspace/app/cmd/font-prototype/main.go](workspace/app/cmd/font-prototype/main.go)，限 [#18](https://github.com/wicanr2/taipei/issues/18) 離線原型。
- 字型原型重生：[workspace/tools/font_prototype.sh](workspace/tools/font_prototype.sh)，固定版本來源檢查為 [font_source.py](workspace/tools/font_source.py)。
- 工具列輸入研究：[GitHub #19](https://github.com/wicanr2/taipei/issues/19)，IDA 工具探針為 [ida_input_probe.py](workspace/tools/ida_input_probe.py)。
- 原始輸入定位匯出：[ida_input_sites.py](workspace/tools/ida_input_sites.py)，保留 IDA 位址與獨立檔案偏移，不附猜測性名稱。
- 原版即時音訊事件盤點：[workspace/tools/audio_audit.go](workspace/tools/audio_audit.go)，限 [#17](https://github.com/wicanr2/taipei/issues/17) 的有界研究。
- OPL2 節奏模式原型：[workspace/tools/ymfm_render.cpp](workspace/tools/ymfm_render.cpp)，依 [#20](https://github.com/wicanr2/taipei/issues/20) 使用固定外部 YMFM 核心，只供研究。
- 原版工具列與施工證據：[docs/re/004-native-controls.md](docs/re/004-native-controls.md)，冷啟動施工圖塊已驗存退讀。
- 音訊契約：[docs/spec/009-opl2-audio.md](docs/spec/009-opl2-audio.md)，Windows 工具鏈擴充來源：[Dockerfile.windows-audio](workspace/tools/Dockerfile.windows-audio)。
- 原版音訊分段驗證：[audio_stream_audit.go](workspace/tools/audio_stream_audit.go)，使用受版控補丁重建的 dosgolem 音訊套件，兩種批次 PCM 必須相同。
- GUI 單幀收據：[receipt-check](workspace/app/cmd/receipt-check/main.go)，依 [#21](https://github.com/wicanr2/taipei/issues/21) 核對原子封裝內的 PNG、色號與色盤。
- HD 遮擋與色盤條件研究：[hd_gate_audit.py](workspace/tools/hd_gate_audit.py)，限 [#5](https://github.com/wicanr2/taipei/issues/5) 的實際收據與離線負對照。
- 動態 HD 比較原型：[docs/spec/010-hd-live-prototype.md](docs/spec/010-hd-live-prototype.md)，限研究前端；字型、F12 與完整重繪範圍已定，各素材批次另驗。
- 原版音訊播放器驗證：[audio_playtest.sh](workspace/tools/audio_playtest.sh)、[audio_playtest_check.py](workspace/tools/audio_playtest_check.py)，使用隔離 PulseAudio monitor 擷取，技術確認與人耳確認分開。
- 原版音訊前端：[sound/session.go](workspace/app/internal/sound/session.go)，對應 `009-opl2-audio.md` 的技術驗證範圍；通用後端保存在 [dosgolem-audio.patch](workspace/tools/dosgolem-audio.patch)。
- 研究前端跨平台編譯：[build_preview_cross.sh](workspace/tools/build_preview_cross.sh)，先執行原型建置，再指定 `windows` 或 `macos`；編譯結果不等於封包驗收。
- 原版音訊狀態對照：[audio_state_audit.go](workspace/tools/audio_state_audit.go)，固定原始 EXE、步數與鍵盤輸入，核對消費音訊前後的 RAM、CPU、色盤、畫面與晶片暫存器。
- Windows 前端預檢：[wine_preview_playtest.sh](workspace/tools/wine_preview_playtest.sh)、[wine_preview_playtest.py](workspace/tools/wine_preview_playtest.py)，限 Wine 冷啟動至城市；非正式封包或真機驗收。
- 正常施工 HD 來源盤點：[hd_source_audit.py](workspace/tools/hd_source_audit.py)，依 [#22](https://github.com/wicanr2/taipei/issues/22) 保留全部相同圖塊來源別名及 ROM 檔案偏移，不猜建物語意。
- 正常施工 HD 來源證據：[docs/re/005-native-hd-sources.md](docs/re/005-native-hd-sources.md)，指出電線位於成員 39、圖像 45，與現行成員 59 地景批次分開。
- HD 捲動研究：[hd_scroll_playtest.sh](workspace/tools/hd_scroll_playtest.sh)、[hd_scroll_playtest.py](workspace/tools/hd_scroll_playtest.py)，依 [#23](https://github.com/wicanr2/taipei/issues/23) 走真實冷啟動及視窗按鍵；原型結果不作正式 HD 驗收。
- HD 捲動獨立核對：[hd_scroll_check.py](workspace/tools/hd_scroll_check.py)，比較完整原版圖塊位移、來源合格數與回退格實際像素，判定門檻先登記於 #23。
- 原版地圖原點：[docs/re/006-map-origin.md](docs/re/006-map-origin.md)，IDA 唯讀查詢入口為 [ida_camera_probe.sh](workspace/tools/ida_camera_probe.sh)、[ida_camera_probe.py](workspace/tools/ida_camera_probe.py)。
- 世界座標材質原型：[docs/spec/011-hd-world-origin-prototype.md](docs/spec/011-hd-world-origin-prototype.md)，限 [#24](https://github.com/wicanr2/taipei/issues/24) 的 DRAFT 修正。
- 呈現層狀態對照：[presentation-audit](workspace/app/cmd/presentation-audit/main.go)，重播正常 GUI 收據，比較有／無原點觀察及 HD 繪圖的原版狀態。
- 城市持續運行抽樣：[hd_runtime_playtest.sh](workspace/tools/hd_runtime_playtest.sh)、[hd_runtime_playtest.py](workspace/tools/hd_runtime_playtest.py)，對應 [#25](https://github.com/wicanr2/taipei/issues/25)，使用原版速度按鍵與固定虛擬步數擷取。
- 持續運行核對：[hd_runtime_check.py](workspace/tools/hd_runtime_check.py)，核對來源、原點、回退與相同地景像素；日期裁圖另作人工辨識，不以單純雜湊變化宣稱月份已推進。
- 城市持續運行證據：[docs/re/007-running-city.md](docs/re/007-running-city.md)，記錄正常月份推進、年度視窗修正與原版機器狀態比對。
- 年度預算視窗回退原型：[docs/spec/012-budget-window-prototype.md](docs/spec/012-budget-window-prototype.md)，依 [#26](https://github.com/wicanr2/taipei/issues/26) 的正常年度畫面證據修正整幀回退。
- Noto 主選單動態原型：[docs/spec/013-noto-menu-prototype.md](docs/spec/013-noto-menu-prototype.md)，依 [#27](https://github.com/wicanr2/taipei/issues/27) 接入使用者已選字型，限六個已辨識標題。
- Noto 實際像素核對：[hd_font_check.py](workspace/tools/hd_font_check.py)，對已展示字型參考逐像素比較，另驗文字回退及矩形外不變。
- Noto 收據負對照：[hd_font_negative.py](workspace/tools/hd_font_negative.py)，破壞文字或矩形間像素並同步更新呈現雜湊，要求核對器仍拒絕。
- 遊戲中主題切換：[docs/spec/014-live-theme-switch.md](docs/spec/014-live-theme-switch.md)，依 #6 使用者定案，READY 範圍只涵蓋 F12 呈現切換；正式前端與封包另驗。
- 完整圖片來源盤點：[workspace/tools/full_asset_catalog.py](workspace/tools/full_asset_catalog.py)，對應 [#28](https://github.com/wicanr2/taipei/issues/28)；全部 ROM 成員與候選圖片保留原始定位、來源別名與未知項。
- 完整 HD 範圍：[docs/spec/015-full-hd-scope.md](docs/spec/015-full-hd-scope.md)，使用者已確認所有圖片與操作介面，列出 #28–#32 批次及完整交付判準。
- 城市工具圖示：[docs/spec/016-city-tool-icons.md](docs/spec/016-city-tool-icons.md)，對應 #29，限十四個已證實來源的圖示內部；選取外框與互動範圍沿用原版。
- 工具圖示獨立核對：[hd_icons_check.py](workspace/tools/hd_icons_check.py)，從原版成員重算逐圖來源遮罩，核對固定 atlas 與選取外框。
- 完整素材盤點證據：[docs/re/008-full-asset-inventory.md](docs/re/008-full-asset-inventory.md)，記錄 118 成員、1317 圖片來源與 25 待分類成員，數量不當成全部重繪完成。
- 全中文字模盤點：[font_catalog.py](workspace/tools/font_catalog.py)，對應 #31，匯出固定 ROM 的字模、原始字碼與正常畫面候選；未審查字形語意不直接覆字。
- 中文字模證據：[docs/re/009-chinese-font-sources.md](docs/re/009-chinese-font-sources.md)，記錄字模定位、十二字正常畫面正對照、CP950 候選與尚未確認的語意。
- 原版文字呼叫端：[ida_text_probe.py](workspace/tools/ida_text_probe.py)，依 #31 在既有唯讀 IDA 9.4 資料庫的副本查原始字串、交叉參照與窄範圍函式，輸出留在 `workspace/runs/ida-31/`。
- 正常文字重播：[text-source-audit](workspace/app/cmd/text-source-audit/main.go)，依 #31 唯讀觀察正常輸入中的原版字串與字模呼叫，逐點核對原版繪製緩衝；不接入產品路徑。
