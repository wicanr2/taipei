# 原版 OPL2 與 PC 喇叭串流

狀態：CONFORMED，限通用串流與 Linux 前端技術驗證。核對日期：2026-10-11。對應 [#17](https://github.com/wicanr2/taipei/issues/17)、[#20](https://github.com/wicanr2/taipei/issues/20)。

## 證據與外部契約

原版冷啟動至主選單實際產生 7214 筆 OPL2 寫入、840 次旋律 Key-On、900 次節奏模式啟用。`/A /D /x` 與 `/A /D` 在本輪抽樣的事件總數與主選單畫面相同；不推定 `/x` 單獨語意，不改正式啟動參數。研究工具為 [audio_audit.go](../../workspace/tools/audio_audit.go)。載入機器快照會清空觀測紀錄，快照後的零事件不能證明原版無聲。

採用 [YMFM 官方核心](https://github.com/aaronsgiles/ymfm)，固定 commit `81aec25ccbb98f4873a255f7551ac4dadac59b4a`，BSD 3-Clause。來源封存 SHA-256 `9bcf001b30f53754c49cf2fb864792a64702b8aeebb105baa908ad5dd33f443f`。原始 LICENSE 與檔頭原樣保留。使用 YM3812 的暫存器、旋律與節奏實作，不逆向原版 driver。

離線 [ymfm_render.cpp](../../workspace/tools/ymfm_render.cpp) 已處理全部 7214 筆事件，49715 Hz、3648923 frames、73.3968 秒，非零樣本 3097515，峰值 6240，削波 0。WAV 為本機研究產物，未做人耳確認，不作正式音樂素材。

串流原型已在 Linux、Windows amd64、macOS x86_64／arm64 編譯。Windows 測試在 Wine 通過，尚非 Windows 真機；macOS 尚非真機驗收。Linux AddressSanitizer 的單元測試與實際標題事件驗證通過。48 kHz stereo 的 3523047 frames 分別以兩種批次合成，PCM 逐 byte 相同，峰值 5584、削波 0，SHA-256 `f5dd002f7f1d95360ac5b85c9e2ad5ae8264047a42ba8c2cee065c8b59df6626`。研究收據為 `workspace/runs/audio-stream-audit.json`、`audio-stream-asan.json`。

MinGW GCC 12 對上游晶片模板報越界最佳化警告。適配器僅呼叫 YM3812，以 uint8 暫存器位址傳入，保留上游邊界 assert；不啟用其他晶片或外部 timer callback。沒有修改或隱藏上游警告，實際使用範圍另經上述 AddressSanitizer 與 Wine 驗證。

dosgolem 指令時鐘依固定版本 `StepsPerSecond()`。OPL 晶片時鐘 3579545 Hz 與 PC 喇叭 PIT 基準依既有平台契約。換算結果標示 `hardware-spec approximation`，不稱原版硬體逐週期或逐波形一致。

## 分層與串流

- 通用解碼、步數換算、PC 喇叭方波與 OPL2 合成留在隔離 dosgolem，專案只負責接播放器及音量。
- OPL 核心放在可選的 `audio/ymfm` 套件。基礎 CPU／DOS 套件不依賴 C++ 或圖形介面。
- 每筆原版暫存器寫入依原有 Step、Bank、Reg、Val 消費，保留相同步數下的原始順序。只接受 Bank 0，其他 bank 明示不支援。
- 48 kHz、16-bit stereo；分段合成保留晶片、方波相位與取樣餘數。相同事件拆成不同批次必須產生相同 PCM。
- 每次最多合成兩秒，播放器環形緩衝有固定容量。缺資料輸出靜音，關閉時停止播放器；過量資料須記錄，不持續累積。
- 實際播放器以名義時鐘執行。裝置尚未就緒或環形緩衝不足一個完整更新時，暫停原版執行步進並保留已收輸入；不丟棄原版事件。自訂加速步數只供 `-mute` 診斷使用。
- 原版即時硬體合成是本專案既定 dosgolem 執行路線的一部分，不建立猜測性的預錄替代曲。OGG 規則適用於另行製作的正式音樂素材，本項沒有新增這類素材。
- 只清理已消費的觀測 log，不改 CPU、記憶體、暫存器、原版畫面、晶片暫存器檔、亂數、遊戲資料或存檔。

## 驗證閘門

1. 三平台 C++14 編譯；固定來源與第三方授權可回查。
2. 合成核心節奏模式會發聲，停止後衰減，旋律及節奏均消費實際標題事件。
3. 全段與分段 PCM 相同；時間單調與越界檢查；環形緩衝有界，靜音及關閉行為可驗證。
4. 音訊開／關的相同原版初始狀態、Step 與輸入產生相同機器狀態與存檔。
5. 正常 GUI 冷啟動與建設存退讀保留通過。技術非靜音、人耳確認與各平台真機分別記錄。

Windows 編譯器擴充來源為 [Dockerfile.windows-audio](../../workspace/tools/Dockerfile.windows-audio)，沿用既有 GUI image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3` 的本機別名 `taipei-gui-base:c3d8835a9d39`，只補 [Debian MinGW C++](https://packages.debian.org/bookworm/amd64/g%2B%2B-mingw-w64-x86-64-posix) `12.2.0-14+deb12u1+25.2+b1`。建置前核對 base image ID；不取代 Linux 或 macOS 工具鏈。

已建 image ID 為 `sha256:80cda80f47353188794d030f468c37821d8e77a3a078e5b306f12cb0a0953c7d`。Windows 原型只引用 KERNEL32.dll、msvcrt.dll，C++ runtime 已靜態連結。編譯通過與人耳／真機驗收分開記錄。

## 前端技術驗證

完整研究前端在 Linux amd64、Windows amd64、macOS amd64／arm64 編譯通過，重建入口為 [build_preview_cross.sh](../../workspace/tools/build_preview_cross.sh)。這些是研究 binary，尚非正式封包。上述僅有兩項 DLL 的描述限純音訊原型；完整 GUI 的匯入表另保存於 `workspace/runs/preview-windows-pe.txt`。

Linux 實際播放器由 [audio_playtest.sh](../../workspace/tools/audio_playtest.sh) 冷啟動原版，經隔離 PulseAudio monitor 擷取 688984 frames，1236348 個非零聲道樣本，峰值 5584，RMS 811.70。刻意延後聚焦三秒，緩衝沒有拒收資料，播放器及環形緩衝正常關閉。收據為 `workspace/runs/audio-device/result.json`，WAV SHA-256 `922454c93122645a20c822d529eb9fc8be1007fa7cb8b64093c50b04a1190296`。擷取 wall-clock 由主機播放器控制，重跑不要求 WAV hash 相同。

[audio_state_audit.go](../../workspace/tools/audio_state_audit.go) 以同一原始 EXE、AdLib 存在、850000001 步及相同原生鍵盤輸入，分別保留與消費音訊觀測事件。完整 RAM、CPU、原版畫面、色盤、埠值、OPL 暫存器與讀鍵紀錄相同；比較狀態 SHA-256 `1dfdcc515013b62b02122dde8b00047752183a7526e6742efc9a95782a13ab57`。收據為 `workspace/runs/audio-state-audit.json`。

正常原版模式與動態 HD 比較原型均通過電線施工存退讀，存檔 SHA-256 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad` 相同。正常玩家路徑使用 `-mute` 加速，仍保留 AdLib 偵測與完整音訊合成；實際裝置另由上述冷啟動擷取驗證。未做人耳確認，不把 Linux 技術擷取或 Wine 核心測試當成 Windows／macOS 真機音效驗收。
