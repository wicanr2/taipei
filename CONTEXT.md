# 模擬台北：目前現況

核對日期：2026-10-11。目標是完成原版與 dosgolem 整合，並提供 HD 呈現。

## 有效決策

- 私人儲存庫：[wicanr2/taipei](https://github.com/wicanr2/taipei)。Issues 已啟用。
- 使用者已授權主機 gh、專案提交與推送，以及本範圍的 Issue 管理。
- 使用者指定所有工作區放在本專案的 `workspace/`。原始輸入保留原位並唯讀使用。
- 原版規則、EXE 與存檔格式保持原樣。HD 美術、解析度與平台矩陣尚未定案。

## 目前狀態表

| 項目 | 現況 | 證據或限制 |
|---|---|---|
| 私人儲存庫 | 已由主機 gh 回讀 PRIVATE，Issues 啟用 | 遠端原為空儲存庫 |
| 工作項目 | 初始 9 張 Issues 已建立 | 狀態只以 [遠端 Issues](https://github.com/wicanr2/taipei/issues) 為準 |
| 本機 Git | 沿用使用者建立的空 clone，管理資料移至專案根目錄 | 原 clone 只有 `.git`，沒有提交或其他檔案 |
| 原版輸入 | 35 個檔案、7,919,834 bytes；RAR 與逐檔 SHA-256 已保存 | [輸入基線](docs/re/001-input-baseline.md)；原版精確版本與權利人仍未知 |
| 啟動入口 | `模擬台北/RS201/RS201.EXE /A /D /x` | 兩個 EXE 同雜湊；批次檔與兩個 config 一致 |
| dosgolem 啟動 | 冷啟動到主選單與城市選擇通過，兩次主選單畫面及暫存器一致 | [啟動基線](docs/re/002-dosgolem-startup.md)；四份補丁只在隔離副本與本專案保存 |
| 原版前端與存讀檔 | 尚未驗證 | [#4](https://github.com/wicanr2/taipei/issues/4)；啟動基線不代表整款遊戲可玩 |
| HD | 尚未製作原型 | 由 [#5](https://github.com/wicanr2/taipei/issues/5) 查證來源；尚未批准樣式 |
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
