# dosgolem 啟動與原生鍵盤基線

對應 [#3](https://github.com/wicanr2/taipei/issues/3)。輸入雜湊見[輸入基線](001-input-baseline.md)。
本研究不修改原版 EXE 或資料。

## 固定工具

| 項目 | 版本 |
|---|---|
| dosgolem 基底 | `a9714ebdab2ad6b529f81225472680f2b11f2842` |
| Go | `go1.24.13 linux/amd64` |
| Docker image | `sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac` |
| 原版入口 | `RS201.EXE /A /D /x` |
| 原版 EXE SHA-256 | `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |

隔離副本的本機提交依序為 `0cbcc4d`、`af3fbfa`、`4c56da4`、`e5e2a12`，未推送上游。
可重現的實際輸入是四份受版控補丁，依序由 [probe.sh](../../workspace/tools/probe.sh)
套用到基底的 `git archive`。它不使用上游或隔離副本的未提交檔案。

| 補丁 | SHA-256 | 規格 |
|---|---|---|
| `dosgolem-bios-irq1.patch` | `20b92b39ce74c6872408be6d7cc59e291327f055a73febee6b51ea2d66b11252` | [001](../spec/001-bios-keyboard-routing.md) |
| `dosgolem-bios-blocking.patch` | `80825cf9c15067302d82caee8d7b85f988315b67c8dcce92effc241905b8bf14` | [002](../spec/002-blocking-bios-input.md) |
| `dosgolem-console-keyboard.patch` | `545c82fe2f4da69a2cc3e3a4f6324fa1af89425d0f19d337f801fe763b3640e6` | [003](../spec/003-console-keyboard-input.md) |
| `dosgolem-probe-trace.patch` | `708ecef0ee1e9825328446561bd72059bd41973323280b6fb1575a3f767117a6` | [004](../spec/004-probe-trace-memory.md) |

建置後探針 SHA-256：`ccabd2047cbdd1744e6053a17b4cb367d026ddbe931b6b3c9e700fc020e4cc9e`。
重生時另存 `workspace/runs/probe-provenance.txt`。

## 已證實的基線

- 原生顯示模式為 13h，320×200，256 色。中文由原版繪製。
- 從 EXE 入口冷啟動，以硬體掃描碼送兩次空白鍵，到達主選單。
  兩次獨立重跑的原生畫面、終點暫存器與計時器計數相同。
- 原生畫面色號 SHA-256：`5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4`。
- 終點為 dosgolem 執行期 `CS:IP=0080:0026`，`AX=0000 BX=325C CX=0000 DX=43DD`。
  此為原生 BIOS 等待路徑，不是 IDA 線性位址或 EXE 檔案偏移。
- 計時器中斷 31,398 次，鍵盤中斷 4 次。空白鍵在第 800,000,003 道由 DOS AH=07 取走。
- 35 個原始檔案重算 SHA-256，全部與盤點相同。
- 第三次冷啟動送三次空白鍵，到第 960,000,001 道已進入城市選擇畫面。
  第 900,000,003 道由 BIOS AH=00 取到空白鍵，硬體 IRQ1 共 6 次。
  收據：`workspace/runs/baseline-city.log`、`baseline-city.png`、`baseline-city.state`。

## 重播

在專案根目錄執行。主機腳本只管理 Docker，建置與探針在容器內。
先以 Git 建立 `workspace/dosgolem` 隔離 clone，確保含上述基底提交。

```bash
bash workspace/tools/probe.sh -no-call-trace \
  -steps 850000001 -block-after 0 \
  -press space,space -press-at 700000000 -press-every 50000000 \
  -save-state 850000000:/out/baseline-a.state \
  -dump-vram /out/baseline-a.bin
```

第二次改用 `baseline-b` 輸出名稱。`-press-every` 的單位是相鄰掃描碼間隔，
每個按鍵包含通碼與斷碼。上述空白鍵在 700M、800M 送通碼，在 750M、850M 送斷碼。
沒有餵入 Stdin、沒有改記憶體、沒有載入快照。BIOS 等待模式在執行前啟用。
虛擬時鐘、初始 BDA 與輸入時點固定，沒有更改遊戲亂數內部狀態或重擲挑結果。

城市選擇重播改為 `-press space,space,space -steps 960000001`，快照步數為 960000000，
輸出名稱改為 `baseline-city`。其餘設定相同。

快照、畫面與完整報告只保存在本機 `workspace/runs/`，不進 Git。
`-dump-vram` 同時輸出色號與 PNG。`-shots` 只輸出色號與色盤。
`-save-state` 的步數須小於最終 `-steps`，才能執行該迴圈起點的保存動作。

## 能力修正與驗證

| Issue | 已證實問題 | 最小驗證 |
|---|---|---|
| [#10](https://github.com/wicanr2/taipei/issues/10) | 預設 BIOS 已有 int09 handler，硬體鍵盤派送卻擋住 stub 向量 | 真實硬體佇列至 BDA，另保留 IF、PIC、自訂 ISR 負對照 |
| [#11](https://github.com/wicanr2/taipei/issues/11) | 空 BIOS 讀鍵返回 0，原版選單缺少等待 | AH=00/10 等待、通斷碼只消耗一次、計時器繼續前進；預設保持舊 API |
| [#12](https://github.com/wicanr2/taipei/issues/12) | DOS 主控台只讀 Stdin，忽略原生鍵盤 | AH=01/07/08、06、0B，延伸鍵分段讀取與狀態往返 |
| [#13](https://github.com/wicanr2/taipei/issues/13) | 等待重試累積逐次 DOS 呼叫紀錄，長程探針 OOM | 明示停用紀錄，同程短重播畫面與暫存器相同；冷啟動在原限制內完成 |

`go test -p 1 ./...` 通過。第四份補丁加入後，重跑 `cmd/probe`、`internal/machine`、
`internal/dos`、`oracle`、`internal/state`，全部通過。缺外部測資的既有測試仍依其原條件跳過，
不宣稱涵蓋全部 DOS 硬體或原版玩法。

觀測開關比較使用 `city-native.state` 的同一短程續跑，至第 990,100,000 道。
色號相同，SHA-256 為 `a886e1a96e04f1fe7d7621a9d119c563f64a911e2d3fe7b19d6f272ad37f9d3c`。
終點暫存器相同。此比較只驗證觀測選項，不取代冷啟動或玩家路徑。

## 限制

- 尚未完成正常 GUI、新遊戲、核心操作與存退讀。主選單基線不代表整款遊戲支援完成。
- 先前以 BIOS 佇列及快照續跑到地圖，僅為診斷證據，不列為正式冷啟動收據。
- 啟動時未見缺檔或未實作服務報告。滑鼠在主選單未被輪詢，不推定整款遊戲的控制方式。
- 使用 `/x` 路線，尚未驗證音樂與人耳聽感。音訊交由前端 Issue 接續。
- 沒有完成美術、HD 素材辨識、解析度或平台定案。
