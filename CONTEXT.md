# 模擬台北：目前現況

核對日期：2026-10-11。目標是完成原版與 dosgolem 整合，並提供 HD 呈現。

使用者已指示恢復工作，繼續整合與驗收。

## 有效決策

- 私人儲存庫：[wicanr2/taipei](https://github.com/wicanr2/taipei)。Issues 已啟用。
- 使用者已授權主機 gh、專案提交與推送，以及本範圍的 Issue 管理。
- 使用者指定所有工作區放在本專案的 `workspace/`。原始輸入保留原位並唯讀使用。
- 原版規則、EXE 與存檔格式保持原樣。
- HD 美術採 B「細緻手繪材質」，以使用者最新改選取代先前的 A。HD 解析度為 1280×800，對應原版 320×200 的四倍。
- 使用者選定 Windows、Linux、macOS 三平台封包。字型待比較原型確認；平台實機驗收另記限制。原版確有 F1–F6 標示，按鍵語意依原版驗證。

目前最早的待確認決策是 [#18](https://github.com/wicanr2/taipei/issues/18) 字型比較：Noto 高清黑體或保留原版點陣。比較題已提出，尚未收到使用者選擇。正式字型、切換操作與後續素材範圍依共同決策逐項確認；目前原型不自動轉成正式 HD 或封包。

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
| HD | B 材質動態比較原型輸出 1280×800，435 格中 433 格覆繪、2 格回退；正常施工、切換、存退讀與模態回退通過 | [動態原型](docs/spec/010-hd-live-prototype.md)；只涵蓋水面、沙地與樹冠，字型、正式切換及後續批次待確認 |
| 跨平台編譯 | Linux amd64、Windows amd64、macOS amd64／arm64 完整研究前端編譯通過；Windows binary 經 Wine 冷啟動至城市，原版畫面與 Linux 相同 | macOS 未真機執行；Wine 及結構檢查不等於封包或真機驗收 |
| 封包 | 尚未建立 | 不宣稱正式 HD 完成或跨平台封包已驗 |

## 文件入口

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
- 動態 HD 比較原型：[docs/spec/010-hd-live-prototype.md](docs/spec/010-hd-live-prototype.md)，限研究前端；正式字型與切換操作待定。
- 原版音訊播放器驗證：[audio_playtest.sh](workspace/tools/audio_playtest.sh)、[audio_playtest_check.py](workspace/tools/audio_playtest_check.py)，使用隔離 PulseAudio monitor 擷取，技術確認與人耳確認分開。
- 原版音訊前端：[sound/session.go](workspace/app/internal/sound/session.go)，對應 `009-opl2-audio.md` 的技術驗證範圍；通用後端保存在 [dosgolem-audio.patch](workspace/tools/dosgolem-audio.patch)。
- 研究前端跨平台編譯：[build_preview_cross.sh](workspace/tools/build_preview_cross.sh)，先執行原型建置，再指定 `windows` 或 `macos`；編譯結果不等於封包驗收。
- 原版音訊狀態對照：[audio_state_audit.go](workspace/tools/audio_state_audit.go)，固定原始 EXE、步數與鍵盤輸入，核對消費音訊前後的 RAM、CPU、色盤、畫面與晶片暫存器。
- Windows 前端預檢：[wine_preview_playtest.sh](workspace/tools/wine_preview_playtest.sh)、[wine_preview_playtest.py](workspace/tools/wine_preview_playtest.py)，限 Wine 冷啟動至城市；非正式封包或真機驗收。
- 正常施工 HD 來源盤點：[hd_source_audit.py](workspace/tools/hd_source_audit.py)，依 [#22](https://github.com/wicanr2/taipei/issues/22) 保留全部相同圖塊來源別名及 ROM 檔案偏移，不猜建物語意。
- 正常施工 HD 來源證據：[docs/re/005-native-hd-sources.md](docs/re/005-native-hd-sources.md)，指出電線位於成員 39、圖像 45，與現行成員 59 地景批次分開。
