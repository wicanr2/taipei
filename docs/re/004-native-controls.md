# 原版工具列與建設操作

對應 [#19](https://github.com/wicanr2/taipei/issues/19) 與 [#4](https://github.com/wicanr2/taipei/issues/4)。核對日期：2026-10-11。

## 輸入與工具

- 輸入 `RS201.EXE`，SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`。
- IDA Pro 9.4，image `sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab`。資料庫與匯出保留於 `workspace/runs/ida-19/`，不入 Git。
- IDA 線性映像從 `0x10000` 起；dosgolem MZ 載入段為 `0x0110`。本次已核對的程式碼位址換算差為 `0xEF00`。資料定位採原始段指標與偏移，不套用程式碼差值猜測資料位址。
- 原始 bytes、獨立檔案偏移及函式名由 [ida_input_sites.py](../../workspace/tools/ida_input_sites.py) 匯出。未改名或改寫 EXE。

## 已證實的控制流程

| 原始定位 | 語意與證據 |
|---|---|
| IDA `sub_163AC`，`0x16447`–`0x16458` | 呼叫原始 BIOS 讀鍵包裝，再把完整 AX 交給 `sub_16C1C` |
| IDA `sub_14203`，INT 16h 位於 `0x14209` | 實際 dosgolem 讀鍵位置為 `052D:003B`；唯讀堆疊紀錄的遠返回位址 `0744:010C` 對應 IDA `0x1644C` |
| IDA `sub_16C1C` | Tab `0F09h`／Enter `1C0Dh` 呼叫 `sub_18DDC`；Space `3920h` 呼叫 `sub_16FF4`；方向鍵依焦點移動地圖游標或工具游標 |
| IDA `sub_18DDC` | 將工具游標恢復為已選工具，再切換焦點 1／2。Tab 與 Enter 本身不確認新工具 |
| IDA `sub_16FF4` | 工具列焦點下確認工具；地圖焦點下經檢查、套用與重畫呼叫施工 |

資料定位保留原始操作數：`es:[004Ah]` 為本次已驗焦點，`es:[004Fh]`、`es:[0051h]` 為原生地圖游標，`ds:[0E3Ch]`、`ds:[0E3Eh]` 為工具游標及已選工具。`es` 的來源是原版 `ds:[20F2h]` 段指標。語意由直接控制流與 GUI 觀察共同證實，只適用於固定輸入版本。

## 正常玩家路徑

新城市初始焦點為工具列，值為 2。先按 Tab 會回到地圖，這是先前探索未選到工具的原因。

本次抽樣依序：冷啟動 → 新城市 → `0` 暫停 → Right 選第 2 項電線 → Space 確認 → 25 次 Right、1 次 Down 移至原生 `(230,43)` → Space 施工 → Right 移開游標 → 原版存檔 → 原版退出 → 全新 EXE 冷啟動 → 原版讀檔 → 原版退出。

結果：工具費用顯示 20 萬，資金由 80000 萬降為 79980 萬；施工格由樹木變為電線，冷啟動讀檔後同一格逐 byte 相同。這條路徑沒有注入座標、城市狀態或機器快照。

| 收據 | 結果 |
|---|---|
| `workspace/runs/gui-cold/result.json` | 冷啟動、施工、存檔、原版退出與冷讀檔通過 |
| 施工前 9×9 圖塊 SHA-256 | `c67851a91f6085bffcd608e04137ea468c7109874709307d1a88ca37fa632a69` |
| 施工後及讀檔後同格 SHA-256 | `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139` |
| 原版 `ROUND4.SAV` | 93,567 bytes；`8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`；讀檔未改寫 |

重跑：`bash workspace/tools/build_preview.sh`，再執行 `bash workspace/tools/gui_playtest.sh`。診斷快照探索另用 `gui_explore.sh`，不能取代上述冷啟動收據。

## 限制

本次原版正常路徑沒有呼叫 INT 33h，IDA 本輪已辨識指令也未找到 INT 33h。這只能確認目前可重播的鍵盤操作路徑；不據此宣稱所有版本或所有流程都沒有滑鼠功能。未追完整遊戲規則或硬體 driver。
