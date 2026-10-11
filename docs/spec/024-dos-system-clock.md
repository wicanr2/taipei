# DOS 系統時間與 BIOS 計數

狀態：CONFORMED，限 DOS 時間來源修正。對應 [#40](https://github.com/wicanr2/taipei/issues/40)，已解除 [#39](https://github.com/wicanr2/taipei/issues/39) 的正常預算操作阻塞。

## 問題與證據

預算視窗在正常 F3 選取後讀入 ROM2，下一份定期收據卻已返回地圖。年度入口出現後，Down 原版只讀一次，release 收據也已回到地圖。兩批原件保留在 `workspace/runs/budget-native/`、`budget-native-entry/`，不能由此宣稱原版方向鍵會關閉視窗。

| 定位與位址基準 | 證據及等級 |
|---|---|
| IDA 線性 `sub_2465E`，`2465Eh–247A1h` | 已證實，讀 ROM 畫面、方向選取、Escape、時間輪詢與閒置計數同屬此函式 |
| IDA 線性 `24747h–2478Eh` | 已證實，取得時間後比較秒欄位，變化時累加閒置計數，計數大於 `14h` 後離開；輸入後清閒置計數 |
| IDA 線性 `sub_14203`，`14203h–14210h` | 已證實，INT16 AH=00 傳回完整 AX；預算 Down 收到 `5000h`，沒有重複讀鍵 |
| dosgolem `internal/dos/dos.go` 的 `clock` | 已證實使用 `m.Ticks*5493/1000` 換算百分之一秒；`m.Ticks` 是已送出的 PIT 中斷次數，與 BIOS 時間計數不同 |
| dosgolem `internal/machine/machine.go` 的 BIOS int08 stub | 已證實在 BIOS 路徑推進 BDA `0040:006C`；INT1A AH=00 已回傳這份 BDA 計數 |

IDA 工具 9.4、image `sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab`，輸入 EXE SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。原始名稱、bytes、EXE 檔案偏移與 xrefs 保存在 `workspace/runs/ida-39/budget-owner-r2.json`。原始指令呼叫目標 `_time`／`_gmtime` 是工具名稱；尚未由名稱單獨證實其內部 API 路徑。

## 平台前提

- [Microsoft MS-DOS 3.3 Programmer's Reference，Get Time 2CH](https://www.pcjs.org/documents/books/mspl13/msdos/dosref33/#get-time-function-2ch)：CH／CL／DH／DL 回傳系統時、分、秒、百分之一秒。
- [Microsoft MS-DOS 4.0 TIME.ASM](https://github.com/microsoft/MS-DOS/blob/2d04cacc5322951f187bb17e017c12920ac8ebe2/v4.0/src/DOS/TIME.ASM)：GET_TIME 經 READTIME 讀取時鐘裝置；不以任意硬體 IRQ 次數直接當系統時間。
- [DOSBox Staging 的 DOS 時間實作](https://github.com/dosbox-staging/dosbox-staging/blob/5426d72fa2cdf08cf94598053dcdbab1cbb8ab4d/src/dos/dos.cpp)：AH=2Ch 取得 INT1A AH=00 的 BIOS 時間，再換算回傳值。[BIOS 實作](https://github.com/dosbox-staging/dosbox-staging/blob/5426d72fa2cdf08cf94598053dcdbab1cbb8ab4d/src/ints/bios.cpp) 從 BIOS_TIMER 讀取 INT1A 計數。

三份程式來源逐字保存在 `workspace/runs/dos-clock-source/platform/`；commit、原始網址與 SHA-256 由 `platform-sources.json` 固定，不依賴可變的 branch HEAD。

上述來源支持採用 BIOS 計數。遊戲自訂 PIT、BIOS 鏈接及閒置視窗的動態關係須由最小受控測試及正常 GUI 驗證。硬體 driver、ISR、busy-wait 的逐週期重建不在本項範圍。

## 正式契約

1. DOS AH=2Ch 以現有 BDA `0040:006C` 的 little-endian 32 位元 BIOS 計數換算時間，不讀 `m.Ticks`。保留固定初始 `DOS.Now` 及既有整數換算 `5493/1000`，再取一天的餘數。
2. 此換算是既有的硬體規格近似。它不是實機逐週期 wall-clock，也不宣稱長時間漂移精確一致。此批只修時間來源，避免擴張為整個 PIT／BIOS 或日期服務重寫。
3. 不加入遊戲名稱、EXE 位址、預算特例或主機時間。不改原版等待上限、輸入、規則、亂數函式、音訊及存檔格式。
4. 不加入新的 runtime 狀態或序列化欄位。時間由既有 machine 記憶體與 DOS.Now 還原；快照兩層均保存才構成續跑條件。
5. 原始資料與上游 dosgolem 工作樹唯讀。固定基底與六份既有補丁後，以第七份專案補丁重現修正；本項不推上游。
6. 舊產品、收據與已結案項目的歷史驗證保留。新產品須重跑原版正常入口及本項控制路徑，不能沿用舊收據宣稱新版本通過。

## 證據審查

2026-10-11 已審查公開平台契約、`m.Ticks` 的派送定義、BDA stub、INT1A 讀寫及 DOS 時間資料流。受控測試已在未修實作重現四組失敗，原件為 `workspace/runs/dos-clock-source/before-tests.log`。固定 BIOS=18 時，raw IRQ=7200 卻回傳 00:06:35.49；預期採同一 BIOS 時間應為 00:00:00.98。INT1A 設定也未反映在 DOS 時間。

差異足以確認 DOS 時間來源與平台契約不符，升 READY，允許依上述契約實作。它是否完全解釋預算過早消失，仍須正常 GUI 驗證；沒有把局部紅測試當成玩家路徑通過。修正可能改變以系統時間初始化的原版種子數值，測試須從固定相同初始條件重新生成，不能宣稱新舊原版機器狀態完全不變。

## 審查與驗收閘門

- 修改實作前，受控測試證明同一 BDA、不同 raw IRQ 次數時回傳值錯誤；保存未修版本失敗結果。
- 最小測試涵蓋初始時間、BDA 時間更新／設定、raw IRQ 變化、一天餘數、暫存器回傳及完整快照還原；不以複製實作公式的測試當成唯一證據。
- 審查資料流、公開契約與測試後才改為 READY。正常冷啟動 F3 入口、五列方向選取、數值更新、Escape、重開及閒置離開另驗，不能由局部測試替代。
- 正常施工存檔、原版退出、全新 EXE 讀回與第二次原版退出通過，固定 build／補丁雜湊、35 原始檔／RAR、UID／GID 及 Docker 清理通過，才升 CONFORMED 並關閉 #40。

研究來源與輸出入口由 [CONTEXT.md](../../CONTEXT.md) 維護；歷程追加 [WORKLOG.md](../../WORKLOG.md)。完整預算 HD 仍由 #39 驗收。

## 實作與正常玩家驗證

第七份補丁 [dosgolem-system-clock.patch](../../workspace/tools/dosgolem-system-clock.patch) 的 SHA-256 為 `2a2f84aaed238fa0a82dea8585e1ce2e1157643241b41666a18e8bbc93bccc42`。固定原基底及六補丁後乾淨套用，僅修 `clock()` 的來源並加入四組平台契約測試。四組紅測試轉綠；DOS、狀態、oracle 與 probe 共 236 項頂層測試通過，五項既有無 fixture 測試仍跳過，詳列於收據。HD、鍵盤及原點的十六項實際資源測試通過，無跳過。

| 正常驗證 | 已取得結果 |
|---|---|
| `budget-native-fixed/` | 正常冷啟動 F3 開窗，Down／Up 五列及循環；五列 Right 各減一、Left 還原；Escape 返回，重開及閒置離開通過。Space 保留視窗。41 份收據保留原版行為，沒有改鍵位 |
| 時間與輸入 | 第一份預算收據 PIT divisor=2982，raw IRQ=36452，BIOS tick=1622；閒置返回期間 BIOS 3886→4226，未新增原版讀鍵。原版返回同一暫停地圖 |
| `gui-dos-clock-cold/` | 45 份新產品 HD 正常收據，F12、電線施工、存檔、原版退出、全新 EXE 讀回及第二次原版退出通過。施工格逐 byte 相同，資金均為 79980 |
| 獨立單幀核對 | 45 份 Go 與 Python 來源、固定面板及全部區外通過，專用字型、圖示及底欄核對通過 |
| 四架構 | Linux amd64、Windows amd64、macOS amd64／arm64 編譯及結構通過；沒有新增 Wine 或真機驗收聲明 |
| 輸入與產物 | 35 個原始檔及 RAR 保持基準；存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad` |

本批 Linux 程式 SHA-256 為 `52b65f10bd009c0f94741eaaa1aa36d0349342dbea646453bb9eff7ce9c40b8f`。四架構、七補丁、Go 來源、實際素材、兩批共 86 份正常收據及測試紀錄由 [dos_clock_provenance.py](../../workspace/tools/dos_clock_provenance.py) 核對，結果為 `workspace/runs/dos-clock-source/provenance.json`。

這些結果支持時鐘來源修正，也確認原先過早離開已解除。沒有將舊、新核心機器狀態宣稱相同，沒有新增全遊戲規則、精確硬體時序、完整預算 HD 或正式封包完成聲明。Escape 前所有調整已各自還原，不能由本批推論 Escape 會撤銷未還原的調整。

最終 378 個相對連結、新檔入口及既有入口正對照、Python／shell 語法、Go 格式、1000:1000 擁有權與指定 find 通過。Linux 從現行來源重建逐 byte 相同，probe 七補丁入口重新建置執行通過。本批容器均退出刪除，未新建 image，未清理其他專案。收尾證據為 `workspace/runs/dos-clock-source/final-hygiene.json`；024 限本項升 CONFORMED。
