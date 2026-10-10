# 原始輸入與啟動基線

日期：2026-10-10。對應 [#2](https://github.com/wicanr2/taipei/issues/2)。
索引：[CONTEXT.md](../../CONTEXT.md)、[驗收矩陣](../verification-matrix.md)。

## 已證實

| 項目 | 原始定位與結果 |
|---|---|
| RAR | `rs201 模擬台北.rar`，2,551,142 bytes；SHA-256 `01051d219ada15f079b18d89320e6911a0d5f9f0c9eab55dc8cdf395e8744510` |
| 使用者解壓來源 | `rs201 模擬台北/`，35 個檔案、7,919,834 bytes；未由本專案重新解壓 |
| 遊戲資料根 | `rs201 模擬台北/模擬台北/RS201/` |
| 執行檔 | `RS201.EXE`，157,756 bytes；SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |
| 別名 EXE | `RS201a.EXE` 與 `RS201.EXE` 完全相同，沒有第二種遊戲版本的證據 |
| 檔案型態 | MZ，header 8,192 bytes，2,018 relocation；entry `1A3D:001A`，SS:SP `24F0:0800`。這些是 MZ header 相對段位址，不是執行期或 IDA 位址 |
| 整合包啟動 | 兩個 DOSBox config 的 `[autoexec]` 均進入 `RS201` 後呼叫 `RS201X.BAT`；該批次檔為 `rs201 /A /D /x` |
| 原安裝說明 | `INSTALL1.BAT` 將 `RS201` 標為 With AdLib Card，`RS201X` 標為 Without AdLib Card |
| 必要資料候選 | `RS201.ROM`、`RS201A.ROM`、`RS201.DT0` 至 `.DT9`、`DISA1.DSA` 至 `DISA6.DSA`；用途需由實際讀寫確認 |

工具：Python 3.13.15，`python:3.13-slim`；盤點程式
[workspace/tools/inventory.py](../../workspace/tools/inventory.py)。本機收據為
`workspace/runs/inventory.json`，包含 35 個檔案的大小與 SHA-256。
第二次獨立讀取逐檔重算雜湊，確認來源未變。

## 限制與下一閘門

- Microsoft runtime 字串存在於 EXE；精確 compiler 家族與版本仍未知，不用版權年份猜填。
- 正式發行版本、年份、原版權利人及存檔語意尚未確認，不能以下載整合包名稱作證。
- `.ROM` 的容器格式未知，不把它當作主機遊戲 ROM，也不沿用其他遊戲的格式。
- 7-Zip 26.01 在既有工具 image 無法列舉這份 RAR，屬工具限制。來源已由使用者提供，
  不改用主機解壓，也不把尚未做的 archive-member 校驗寫成通過。
- 下一步用固定版本 dosgolem，唯讀掛載資料根，從 `RS201.EXE /A /D /x` 冷啟動。
