# 模擬台北：目前現況

核對日期：2026-10-10。目標是完成原版與 dosgolem 整合，並提供 HD 呈現。

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
| 原版輸入 | 使用者已解壓至 `rs201 模擬台北/` | 尚未完成雜湊與版本盤點 |
| 啟動候選 | `模擬台北/RS201/RS201.EXE`、`RS201a.EXE` | 尚未確認差異與實際啟動路徑 |
| dosgolem 整合 | 尚未驗證 | 由 [#3](https://github.com/wicanr2/taipei/issues/3) 保存基線與缺口 |
| HD | 尚未製作原型 | 由 [#5](https://github.com/wicanr2/taipei/issues/5) 查證來源；尚未批准樣式 |
| 封包 | 尚未建立 | 不宣稱可玩、HD 完成或跨平台驗收 |

## 文件入口

- 規則：[AGENTS.md](AGENTS.md)。
- 唯一工作狀態：[GitHub Issues](https://github.com/wicanr2/taipei/issues)。
- 驗收：[docs/verification-matrix.md](docs/verification-matrix.md)。
- 歷程：[WORKLOG.md](WORKLOG.md)。
