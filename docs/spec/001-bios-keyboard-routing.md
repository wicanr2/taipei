# 預設 BIOS 鍵盤 IRQ1 路由

狀態：CONFORMED。核對日期：2026-10-11。對應 [#10](https://github.com/wicanr2/taipei/issues/10)。
入口：[CONTEXT.md](../../CONTEXT.md)。

## 證據審查

- dosgolem 基底為 `a9714ebdab2ad6b529f81225472680f2b11f2842`。
- 上游 `docs/spec/202-bios-int09-default-handler.md` 為 READY。其第 2 節明定，向量 9
  指向預設 stub 時，由 `dos` 的 `biosInt9` 讀取 60h 埠並寫入 BDA 鍵盤緩衝。
- `internal/dos/int9.go` 已實作上述契約，但 `internal/machine/keyboard.go:keyTick`
  仍在向量段等於 `StubSeg` 時攔截。這項衝突已證實，不涉及原版遊戲規則。
- `RS201.EXE` SHA-256 為 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。
  冷啟動主選單時，執行期 int09 向量為 `0080:0024`，排入硬體 Enter 後 IRQ1 為 0。
  本機收據：`workspace/runs/intro-enter.log`、`intro-key.png`。

## 實作契約

1. 硬體掃描碼經既有佇列、IF、PIC 遮罩與 `KeyEvery` 節流後送入 int09。
2. 預設向量沿用既有 BIOS 處理，不因其位於 stub 段而阻擋。
3. 自訂 ISR 沿原路執行。通碼、斷碼與修飾鍵翻譯沿用上游規格 202。
4. 不修改原版 EXE、BDA 應用資料或遊戲位址；不加入本作特例。
5. 修改只在 `workspace/dosgolem`；可重現補丁保存於本專案工具目錄，不推送上游。

## 驗證與限制

- 小型 COM 無限迴圈由硬體佇列送 Enter 通碼與斷碼，兩次 IRQ1 應只產生一個 `1C0D` 按鍵。
- 保留自訂 ISR、IF、PIC 遮罩與節流測試；執行 machine、dos 與 oracle 套件測試。
- 以同一份原版檢查點及相同輸入重跑，檢查本作是否實際改變選單。
- 通用路由測試成功只證明 BIOS 路由契約。遊戲操作需另驗，不宣稱整款遊戲相容。
- 上游翻譯表的硬體語意仍是規格近似，沒有實機逐週期驗證。

驗證結果：通用測試與本作原生硬體鍵盤冷啟動通過，見[啟動基線](../re/002-dosgolem-startup.md)。
