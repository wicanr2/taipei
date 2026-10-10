# 長時間探針的呼叫紀錄

狀態：CONFORMED。核對日期：2026-10-11。對應 [#13](https://github.com/wicanr2/taipei/issues/13)。
入口：[CONTEXT.md](../../CONTEXT.md)。

## 證據與契約

- 已證實：`cmd/probe` 無條件把 `DOS.CallTrace` 設為非 nil。`internal/dos/int21.go`
  對每次 DOS 呼叫追加紀錄，包含等待輸入的重試。Docker 已記錄冷啟動 OOM，退出碼 137。
- 新增 `-no-call-trace`，預設 false。true 時不啟用逐次 DOS 呼叫軌跡。
- 選項只影響觀測紀錄，不改 CPU、DOS 服務、指令數、計時器、輸入或畫面。
- 按鍵消耗、檔案操作與未支援服務仍沿用原報告。需要逐次軌跡時省略本選項，
  並縮小探針範圍。這項修改不保證其他所有診斷陣列都有界。

## 驗證

執行原有 `cmd/probe` 測試。短程原版探針比較開關前後的原生畫面與終點暫存器；
長程冷啟動用關閉紀錄的同一輸入完成，不提高容器記憶體限制。

驗證結果：測試與觀測開關比較通過，三次冷啟動完成，見[啟動基線](../re/002-dosgolem-startup.md)。
