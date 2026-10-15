# 本機完整版回核與遊玩推廣影片

狀態：READY。對應 [#63](https://github.com/wicanr2/taipei/issues/63)。

## 範圍

初次回核 `v.1.0.0-20261015` 三平台封包完整遊戲內容。依 [042](042-presentation-audio-continuity.md) 的音訊修正另建 `v.1.0.1-20261015`，正式影片由新實包錄製；既有 tag 與封包不覆寫。影片只留本機。

| 項目 | 契約 |
|---|---|
| 完整版 | 從三份實際壓縮檔讀取 `original/`，23 個檔案及雜湊均須符合固定原始盤點，包含 EXE、ROM、DT0–9、DSA1–6 |
| 擷取 | 正式 Linux 實包唯讀掛載，以正常啟動器冷啟動；不載入機器快照、不注入狀態 |
| 遊玩 | 正常選單進入 DISA1，城市移動或施工；保留原生讀鍵與攝影時間事件 |
| 切換 | 同一場遊戲 F12 原版／HD，F11 繁中、簡中、日文、韓文、英文；不重新啟動遊戲 |
| 聲音 | 隔離 PulseAudio 擷取實際封包播放；使用 009 固定 YMFM 核心與原版 OPL 事件，不另製替代曲 |
| 剪輯 | 1280×800、30 fps、H.264／AAC；全畫面保留，不裁切遊戲介面；說明文字放獨立字卡 |
| 音樂 | 可將本次實際開場錄音剪成配樂，記錄來源區段與循環；不暗示剪輯配樂與所有操作同步 |
| 成片 | 實際遊玩為主，展示原版／HD 與五語系；檢查音視長度、全片解碼、黑幀、凍結與字幕安全矩形 |
| 音訊 | 檢查取樣率、聲道、時長、非靜音、削波、DC、長靜音；故意開選單暫停與原版停曲另記 |
| 限制 | 技術檢查不等於人耳確認；本輪 Linux 錄音不擴張為 Windows／macOS 真機音效驗收 |

## 入口與交付

- 擷取與回核：[promo_capture.sh](../../workspace/tools/promo_capture.sh)、[promo_capture.py](../../workspace/tools/promo_capture.py)。
- 合成與檢測：[promo_render.py](../../workspace/tools/promo_render.py)。
- 工作資料：`workspace/runs/promo-v.1.0.1-20261015/`，重跑使用明確的新 run 名稱，不覆寫證據。
- 正式影片、抽樣圖、FFprobe、音訊檢測、來源與權利清單：`dist-all/v.1.0.1-20261015/promo/`。
- 本檔由 [CONTEXT.md](../../CONTEXT.md) 索引；歷程只追加於 [WORKLOG.md](../../WORKLOG.md)。

外部流程為 `~/.codex/knowledge-base/sources/claude/retro-cht/game-promo-video-ffmpeg.md`；原版音源邊界為同知識庫 `sources/claude/rulebook/93-promo-video-original-assets.md`。本片使用本作城市綠色介面、Noto 黑體及實機混剪，不沿用奇幻遊戲紫金模板。
