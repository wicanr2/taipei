# 原版前端、輸入與存檔

狀態：CONFORMED，限下列原版模式抽樣。核對日期：2026-10-11。對應 [#4](https://github.com/wicanr2/taipei/issues/4)。
入口：[CONTEXT.md](../../CONTEXT.md)。原型已提供下列證據；本規格准許原版模式接入。HD 比較仍受 [010](010-hd-live-prototype.md) 的 DRAFT 範圍限制，正式封包另依 #9 驗收。

## 原版證據與版本

- 已證實：固定 `RS201.EXE` SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3`，啟動參數 `/A /D /x`。來源、檔案與工具版本見 [001](../re/001-input-baseline.md)、[002](../re/002-dosgolem-startup.md)。
- 已證實：原生鍵盤經 BIOS／DOS 讀鍵；新城市初始焦點在工具列，方向鍵選工具、空白鍵確認，再由原版施工。位址、原始 bytes、堆疊、檔案偏移與證據等級見 [004](../re/004-native-controls.md)。不把圖塊或規則重寫在前端。
- 已證實：原版由檔案選單寫入 93,567 bytes 的 `ROUND4.SAV`，正常退出後全新 EXE 冷啟動可讀回施工格。最小玩家路徑為冷啟動、新城市、暫停、電線施工、存檔、退出、重啟、讀檔、再次退出。
- 已證實：原版產生 OPL2 旋律及節奏事件；硬體合成採 [009](009-opl2-audio.md) 的 `hardware-spec approximation`。音訊觀測紀錄不參與原版邏輯。
- 固定 dosgolem 基底 `a9714ebdab2ad6b529f81225472680f2b11f2842` 及六份受版控補丁，由 [build_preview.sh](../../workspace/tools/build_preview.sh) 重建。Go 1.24.13、Ebitengine 2.9.9 與模組雜湊固定；image ID 由建置入口指定。

## 前端契約

- 原版資料唯讀，`DOS.Scratch` 指向獨立可寫目錄，原版自行讀寫原生存檔格式。檔名保留原版大小寫與 BIOS 修飾鍵行為。載入診斷機器快照只供研究，不能替代正常存退讀。
- 原生畫面 320×200，由色號及同幀 DAC 色盤產生；輸出 1280×800。原版模式使用四倍最近鄰，不重繪文字、UI 或建設圖塊。
- 鍵盤有序文字事件按 `006` 轉原生通斷碼，實體修飾鍵及 Caps Lock 依 `007`；其他鍵按下／放開送 set 1 通斷碼。滑鼠只在輸出矩形內換算，除以 4 回原生座標，經現有 DOS 驅動介面送入。已抽樣玩家路徑沒有 INT 33h 呼叫，故不宣稱本作全部功能已驗滑鼠操作。
- 原版 EXE 雜湊失配、必要資料無法讀取、模擬器或播放器錯誤須退出非零狀態。資料不足不猜補。原版退出或正常視窗關閉時，清理 DOS handle、合成器與播放器。
- 實際播放器每次執行名義時鐘的 1/60 秒步數。裝置尚未就緒或緩衝不足時保留已收輸入，暫停 VM 步進。`-mute` 停用主機裝置而保留相同 AdLib 偵測及合成；研究加速僅可與 `-mute` 合用。
- 收據以單一原子 `capture.zip` 保存原版 PNG、色號、色盤、呈現 PNG、CPU／鍵盤／檔案紀錄。獨立 [receipt-check](../../workspace/app/cmd/receipt-check/main.go) 解碼核對同幀一致；分開的導覽檔不能作正式比較輸入。

## 驗證與限制

先以既有原版原型完成證據審查，再依本 READY 契約重跑 [gui_playtest.sh](../../workspace/tools/gui_playtest.sh) 的正常玩家路徑，以及 [audio_playtest.sh](../../workspace/tools/audio_playtest.sh) 的實際播放器擷取。來源 35 個檔案 SHA-256 必須不變。音訊消費的原版狀態比較由 [audio_state_audit.go](../../workspace/tools/audio_state_audit.go) 補足；測試不取代正常 GUI。

Windows、Linux、macOS 已是使用者指定範圍；編譯、Wine、真機分別記錄。未抽樣的城市、災難、全部選單與長時間模擬不外推為已驗。原版素材只留本機，權利邊界見 AGENTS.md。

READY 後已重跑原版模式冷啟動施工存退讀，兩次由原版正常返回 DOS，`workspace/runs/gui-cold/result.json` 通過。存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，施工格 SHA-256 `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139`，讀回相同。實際音訊播放器的延後聚焦擷取與關閉通過，音訊消費的相同原版狀態比較通過。正式封包與未抽樣功能維持原限制。
