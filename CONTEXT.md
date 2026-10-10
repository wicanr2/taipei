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

## 目前狀態表

| 項目 | 現況 | 證據或限制 |
|---|---|---|
| 私人儲存庫 | 已由主機 gh 回讀 PRIVATE，Issues 啟用 | 遠端原為空儲存庫 |
| 工作項目 | 初始 9 張 Issues 已建立 | 狀態只以 [遠端 Issues](https://github.com/wicanr2/taipei/issues) 為準 |
| 本機 Git | 沿用使用者建立的空 clone，管理資料移至專案根目錄 | 原 clone 只有 `.git`，沒有提交或其他檔案 |
| 原版輸入 | 35 個檔案、7,919,834 bytes；RAR 與逐檔 SHA-256 已保存 | [輸入基線](docs/re/001-input-baseline.md)；原版精確版本與權利人仍未知 |
| 啟動入口 | `模擬台北/RS201/RS201.EXE /A /D /x` | 兩個 EXE 同雜湊；批次檔與兩個 config 一致 |
| dosgolem 啟動 | 冷啟動到主選單與城市選擇通過，兩次主選單畫面及暫存器一致；新增 Caps Lock 補丁通過核心與硬體讀鍵測試 | [啟動基線](docs/re/002-dosgolem-startup.md)、[Caps Lock](docs/spec/007-bios-caps-lock.md)；補丁只在隔離副本與本專案保存 |
| 原版前端與存讀檔 | 正常 GUI 冷啟動、新遊戲、游標、檔名退格、原版存檔、離開、全新啟動讀檔通過 | [#4](https://github.com/wicanr2/taipei/issues/4)；建設操作與音訊尚未完成 |
| HD | B 材質離線原型已輸出 1280×800，435 格中 433 格覆繪、2 格回退；素材撤除及來源失配負對照通過 | [原型契約](docs/spec/008-hd-material-prototype.md)；只涵蓋水面、沙地與樹冠，動態遮擋與正式接入待驗 |
| 封包 | 尚未建立 | 不宣稱可玩、HD 完成或跨平台驗收 |

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
