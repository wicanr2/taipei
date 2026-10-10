# BIOS 讀鍵等待模式

狀態：CONFORMED。核對日期：2026-10-11。對應 [#11](https://github.com/wicanr2/taipei/issues/11)。
入口：[CONTEXT.md](../../CONTEXT.md)。

## 平台前提與證據審查

BIOS `int16 AH=00/10` 是等待式讀鍵；空佇列不得被當作一次 `AX=0` 的按鍵回傳。
來源：Ralf Brown Interrupt List Release 61，[作者入口](https://www.cs.cmu.edu/~ralf/files.html)、
[INTERRUP.D 原文鏡像](https://github.com/cirosantilli/ralf-brown-interrupt-list/blob/master/inter61a/INTERRUP.D)。
此實作依平台契約近似等待，不宣稱 BIOS 逐週期一致。

上游固定基底 `a9714ebdab2ad6b529f81225472680f2b11f2842` 的
`docs/spec/008-blocking-console-input.md` 第 3 節已記錄相同限制，為既有使用者保留空佇列回零。
`internal/dos/bios.go:int16` 確實如此，屬已證實的實作限制。

本作 `RS201.EXE` 雜湊見[輸入基線](../re/001-input-baseline.md)。主選單接受空白鍵，
Stdin 路徑已進入城市選擇；BIOS 空白鍵尚未被讀取。修正後須重跑原生路徑，不外推原因已全解。

## 契約

- 增加通用設定 `DOS.BlockingBIOSKeys`，預設 false，保留其他使用者的既有行為。
- 啟用後，AH=00/10 依原有順序讀 BDA、DOS.Keys、Stdin。空時用 `CPU.Rewind()` 重試
  同一道 INT，保持暫存器，設定 `Blocked` 並累加 `KeyWaits`。
- 計時器與硬體 IRQ1 照常前進。有鍵時清除 `Blocked`，一次只取一個鍵。
- AH=01/11 查詢保持不阻塞、不消耗；預設 BIOS 與自訂 ISR 路由依規格 001。
- 探針新增 `-blocking-bios-keys`。設定在載入檢查點之後套用，屬執行器政策，
  與既有 `NonBlockingKeys` 一樣不改原版存檔格式。
- 不修改遊戲 bytes、規則或選單狀態，不在通用層加入遊戲名稱或位址。

## 驗證

最小 COM 驗證空讀不前進、不修改 AX、計時器前進；硬體空白鍵解除等待，只產生一個
`3920`；AH=00/10 均抽測，舊模式與查詢不變。執行 dos、machine、oracle、state 測試。
然後從主選單檢查點用原生空白鍵進入城市選擇，再從冷啟動重跑。
若仍無反應，只將通用等待契約記為通過，繼續保留遊戲操作缺口。
