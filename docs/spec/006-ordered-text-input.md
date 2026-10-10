# 前端有序文字輸入

狀態：CONFORMED。日期：2026-10-11。對應 [#14](https://github.com/wicanr2/taipei/issues/14)。
入口：[CONTEXT.md](../../CONTEXT.md)。限於 #4 的研究前端，不代表正式前端全部完成。

## 證據與原因

`workspace/runs/gui-cold/status.json` 記錄使用者輸入 `round2`，同一更新內的 D、N
被前端依鍵位表順序送出，原版實際建立 `ROUDN2.SAV`。這是前端排序缺陷。

固定 Ebitengine v2.9.9 的 `input.go` 明定：`AppendInputChars` 提供更新時收到的
可列印字元；`Key` 代表實體鍵位，控制鍵與修飾鍵另用 `IsKeyPressed` 處理。
來源為鎖定模組內的原始碼，不假設目前最新版行為。

## 契約

- 可列印 ASCII 依 `AppendInputChars` 的順序轉為 set 1 通斷碼，只送一次。
- 一般文字不再同時由實體可列印鍵送出。Ctrl／Alt 組合仍送實體鍵通斷碼。
- Shift 與 Caps Lock 狀態納入字元轉換；暫時調整 Shift 後恢復使用者按住的狀態。
- 修飾狀態依實際排入 IRQ1 的通斷碼更新。同次更新收到 Shift 按放與大寫文字時，仍送出正確大寫字元。
- 方向鍵、功能鍵、退格與 Esc 保留原生通斷碼。不寫 BDA、不注入 Stdin 或遊戲狀態。
- 不支援的 Unicode 記錄為研究限制，不猜測 Big5 或原版輸入法。
- 控制鍵與文字同時落在同一更新時，API 未提供合併後的事件時間順序。
  本規格不宣稱該情境精確重播；GUI 驗證使用分開的實際按鍵動作。

驗證：硬體 IRQ1 到 BIOS 讀回的文字順序、Shift／Caps Lock 組合及無重複字元；
再以真實 GUI 存入含跨鍵位順序的檔名，抽測退格，驗原版實際檔名與存檔內容。

結果：硬體 BIOS 測試通過；真實 GUI 輸入 `round3`、退格及 `4` 後，
原版建立 `ROUND4.SAV`，93,567 bytes。全新 EXE 實際讀回該檔，雜湊不變。
快速 Shift 按放後的 `Y` 由原版 DOS AH=07h 讀為 89，正常離開通過。
收據在 `workspace/runs/gui-cold/`，重生入口為 `bash workspace/tools/gui_playtest.sh`。
