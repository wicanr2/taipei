# DOS 主控台的原生鍵盤輸入

狀態：CONFORMED。核對日期：2026-10-11。對應 [#12](https://github.com/wicanr2/taipei/issues/12)。
入口：[CONTEXT.md](../../CONTEXT.md)。

## 平台前提與證據

- RBIL Release 61：[AH=06 輸入](https://www.delorie.com/djgpp/doc/rbinter/id/70/25.html)、
  [AH=0B 狀態](https://www.delorie.com/djgpp/doc/rbinter/id/76/25.html)。主控台來源包含鍵盤；
  延伸鍵先回 00，下一次回其碼。AH=06 無鍵時 ZF=1、AL=0，有鍵時 ZF=0。
- 固定 dosgolem 基底的 `conIn` 只讀 Stdin，AH=0B 也只看 Stdin；AH=06 輸入恆回無鍵。
  這些是已證實的實作限制。修改依公開契約，不聲稱 BIOS／DOS 逐週期一致。
- 本作城市選擇後的說明頁停在 `int21 AH=07`，執行期 `052D:002C`。
  收據 `workspace/runs/city.log`；原版雜湊見[輸入基線](../re/001-input-baseline.md)。

## 契約與邊界

1. 主控台依待讀延伸碼、BDA、DOS.Keys、Stdin 順序取字元，成功只消耗一次。
2. BIOS 按鍵 ASCII 非零時回其字元；ASCII 為零時先回 00，再回掃描碼。
3. AH=01/07/08 沿用既有等待與回顯規則；AH=0B 只查詢、不消耗。
4. AH=06 輸入不阻塞，依有無字元設定 ZF 與 AL；輸出行為保持原樣。
5. AH=0C 同步清除待讀延伸碼，沿用已確認的回放 Stdin 保留契約。
6. DOS 執行器狀態檔保存待讀延伸碼，舊檔缺欄位時視為沒有待讀碼。
7. 不處理本次未依賴的 Ctrl-Break、檔案重導向與完整 DOS 裝置驅動。
8. 不改原版遊戲檔、規則、存檔或選單狀態。

## 驗證

由真實硬體佇列送字母，確認 AH=0B 看得到、AH=07 取到、取完後 BIOS 與 DOS 都看不到。
另驗延伸鍵兩次讀出、等待解除、回顯、AH=06 空讀與單次消耗、清緩衝、待讀碼狀態往返。
跑既有套件測試後，重跑本作說明頁及完整冷啟動。通用測試不取代原版玩家路徑。

驗證結果：通用測試、原版說明頁續跑及原生硬體冷啟動通過，見[啟動基線](../re/002-dosgolem-startup.md)。
