# 023：檔案視窗與離開確認

狀態：CONFORMED。核對日期：2026-10-11。Issue：[#38](https://github.com/wicanr2/taipei/issues/38)。限本規格的完整檔案視窗與離開提示。

## 範圍

只處理原版檔案視窗與底部離開確認。沿用 B、Noto Sans CJK TC Regular Sans2.004、1280×800、原位版面及 F12。原版負責檔名輸入、清單、選取、確認、取消、存讀檔與退出。HD 唯讀辨識畫面，不增加輸入分支，也不修正原版留下的文字。

其他功能視窗、外部檔案被刪除／損壞或儲存裝置故障的提示，以及未辨識動畫保持原版，留在 #31 與完整 HD 範圍。已取樣的空白、空清單、長度與覆寫正常操作沒有另外的錯誤視窗；讀檔畫面不接受字母編輯檔名。不能藉回退宣稱完整 HD。

## 固定輸入與定位

| 輸入 | SHA-256／版本 |
|---|---|
| RS201.EXE | `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |
| RS201.ROM | `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29` |
| dosgolem | `a9714ebdab2ad6b529f81225472680f2b11f2842` 與本專案六份補丁 |
| Docker | `c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3` |
| 工具 | Go 1.24.13、Python 3.11.2、Xvfb 與 xdotool |
| Noto | `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4` |
| 字型授權 | `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2` |
| B 面板 | `eeb1aa620c179a7fa0233bdfc9d9ad6abf8719d36f1ad05dc93c84343a164ea9` |

ROM 成員使用檔案偏移與零起算索引。畫面座標是原版 320×200；輸出各軸乘四。讀鍵定位使用 dosgolem 的執行期實模式 CS:IP，不能當成 IDA 位址。

## 來源證據

入口為 [file_dialog_catalog.py](../../workspace/tools/file_dialog_catalog.py)。首批八份來源保留於 `workspace/runs/file-dialog-source/catalog.json`，作固定字碼與原型輸入。完成正常探索後的審查證據為 `workspace/runs/file-dialog-source-ready/catalog.json`，SHA-256 `e319a23224c21cb6798e88abe107c514b6c072174a093ff02e9edbf7c555922b`。243 份完整來源包含 238 個檔案視窗與五個離開提示，729 個單像素負對照全部拒絕。原始 ZIP 含完整索引畫面、色盤、輸入與原版讀鍵；其中有重複畫面，不代表 243 個不同狀態。

| 來源 | 已證實的完整可見模型 |
|---|---|
| 檔案視窗 | ROM3，檔案偏移 22855、4812 bytes；解碼 67×107，索引像素 SHA-256 `697dff15cb595e693f514500531196d2be7f415a2b10e9e99a1182da431657c8`；原位 `(34,41,67,107)` |
| 輸入背景 | ROM3 相對矩形 `[5,4,62,18)` 改為原版索引 31 |
| 清單背景 | 七列相對矩形 `[10,26+11r,58,33+11r)` 改為索引 136，`r=0..6` |
| ASCII | ROM56，標頭 `(5,7,7)`，字碼 32–126；字模在成員內 `6+(code-32)*7`，每列取最高五位。九十五字模含空白均唯一 |
| 文字位置 | 輸入列原位 `(44,49)`；七個清單列 `(44,67+11r)`；每列八字元，字距六像素，實際字模 5×7 |
| 離開提示 | ROM1 完整城市底圖之 `(7,175,224,18)`，加八個中文與六個 ASCII；完整 4032 像素重建 |
| 提示中文字模 | ROM57 索引 `188,301,55,302,51,49,50,167`；字碼由 ROM58 同索引 cp950 復原。來源原文只保留本機 catalog |
| 提示位置 | 中文從 `(19,177)` 起，字距十六，15×14；ASCII 從 `(153,181)` 起，字距六。全部原版墨色索引 32 |

讀鍵已見存檔入口的 CallerCS=5001、CallerIP=2077；讀檔清單入口的 CallerCS=5001、CallerIP=3149。這是正常執行的觀察定位，HD 不依這些位址改寫機器狀態。

## 已證實的正常操作

正常探索入口：[file_dialog_playtest.sh](../../workspace/tools/file_dialog_playtest.sh)。

- 首輪 `file-dialogs-native/` 在字元 `0` 的退格後停下。收據證明原版已讀到 BIOS Word `0x0E08`，畫面仍顯示最後一個字元；原先「退格一定清空」斷言不成立。
- `file-dialogs-native-extra/` 完成其餘字元與邊界。九十四個 ASCII 33–126 輸入中，六十二個英數字接受，小寫顯示大寫；三十二個符號忽略。退格刪最後一字後，該字可見殘留，新英數輸入覆蓋殘留。八字完整顯示，第九字已讀而畫面不變。
- Escape 取消存檔及空清單讀檔確認均恢復完整原畫面。空白存檔確認不產生 SAV。前端私有執行目錄已有兩份 ROM 副本，不能以「整個目錄空白」判斷沒有存檔。
- F2 保留前次選項；首輪重開後固定 Down 的假設被推翻。後續探針依 022 的完整 F2 面板來源確認選項。
- `file-dialogs-native-list/` 使用十份相同合法 SAV 副本，正常上下各十一鍵，取得二十三個清單取樣。七列視窗捲動，上下邊界停止；輸入列墨色 15、未選清單列 31、唯一已選列 32。取消及離開輸入 `n` 恢復整幀原畫面，十份副本不變。
- `file-dialogs-native-edges/` 經原版正常選單覆寫 ALPHA001，沒有第二個確認視窗。原生存檔仍為 93567 bytes，雜湊由 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad` 變為 `59388c3837d65bec89eceb8743cf01e3d5535d06f441e3cd4d3273ecdd8d1044`，其餘九份 SAV 不變。
- `file-dialogs-native-missing/` 在讀檔清單輸入 `MISSING9`，原版逐字讀到，完整畫面不變；正常介面透過清單選檔。這不證明外部刪檔或損壞檔案的錯誤處理。
- 探針都是正常冷啟動與視窗輸入，有界停止只作研究，沒有替代正式原版退出。核對器為 [file_dialog_inputs_check.py](../../workspace/tools/file_dialog_inputs_check.py)，結果 `workspace/runs/file-dialog-inputs-ready.json`。
- 固定 dosgolem 的 AH=40h 寫入記在 `Wrote`，目前前端沒有匯出該欄；`FileOps` 的開／關檔加實際落地雜湊、大小及其他檔不變，作本次覆寫證據。不把缺少 `FileOps.write` 當成沒有寫入。
- 已取樣畫面沒有獨立可見輸入游標相位。未匹配的相位維持原版，不由本批外推沒有動畫。

## 可丟棄原型

[file-dialog-prototype](../../workspace/app/cmd/file-dialog-prototype/main.go) 讀取固定來源 catalog、字型、授權、B 素材及城市框架，輸出 `workspace/prototypes/hd-style/file-dialogs-v1/`。

- ASCII 使用 24 點，白／紅兩組各九十五字形；每字安全矩形 24×28，字距 24。
- 中文使用 52 點，八字各 60×56，字距 64。
- 原型以實際 alpha 墨跡確認無缺字或裁切。空白字形只允許空白字碼。
- 空白檔案面板 268×428；離開提示 896×72。每個輸出都有 SHA-256。
- B 面板紋理縮放後 RGB 除五，提升白字與紅色選取的辨讀；原版位置與文字不變。
- [hd_file_dialogs_check.py](../../workspace/tools/hd_file_dialogs_check.py) 由 PNG 獨立重算 198 個 alpha 墨跡及完整離開提示，結果 `workspace/runs/file-dialog-ink-dim.json` 通過。實際八 W 清單的原位比較為 `workspace/runs/file-dialog-wide-proof.png`，SHA-256 `0fc4db6e204da3f654a401d33517a765148372be6e7bcf4890d3608fe6a3d0f6`，已目視確認沒有裁切。
- 初版亮底原型與來源保留在 `workspace/runs/file-dialog-prototype-first/`。調暗原型經 READY 審查後按下列契約接入產品，正式結果見末節。

## 正式呈現契約

輸入為唯讀 `Indexed[64000]`、`Palette[256][3]`、顯示模式與 HD 開關。輸出為 1280×800 RGBA 與呈現統計。不得存取 DOS 執行器、讀鍵佇列、檔名緩衝、亂數或 SAV，也不寫入原版資料。

- ROM 雜湊、顯示模式 19 及 HD 開關先由既有入口檢查。先重建原版四倍畫面，再嘗試本批來源。
- 檔案視窗完整重建 7169 個索引像素。八列、每列八字元的 5×7 點陣逐格反查 ROM56，包含空白；重建後全矩形逐 byte 相同才接受。輸入列可見墨色只接受 15，清單非空墨色只接受 31／32，最多一列紅字。空白清單列統計以墨色 0 表示沒有可見墨跡，空白輸入列固定記 15，與來源核對器一致。不得從原版邏輯長度清除畫面殘留。
- 離開提示以 ROM1 裁切、上述 ROM57 中文及 ROM56 ASCII 完整重建 4032 像素，來源 SHA-256 `84b33e447ebeea82ba9517eda9c987bf8a9bf5cec759892974cb66401caaf701`。不把同位置其他字串當成離開提示。
- 每次只驗來源矩形實際使用的色盤索引，逐色與固定 `palette.json` 比較。未使用的索引變動不影響匹配。
- 檔案視窗畫固定 B 底板，再按八列可見字元放 Noto atlas；31／15 顯示白字，32 顯示紅字。離開提示畫固定完整 PNG。每次重畫底板，縮短、切換及關閉不保留前幀像素。
- 在既有完整選單辨識後、阻塞輸入回退前嘗試。成功只改本批矩形，其他位置保持當幀原版四倍像素，沿用 018／021 的模態外契約。未知來源整個本批視窗不畫。
- 統計新增 `file_dialog`、`file_text` 八列及 `file_colors` 八列、`file_reason`。成功名稱為 `file-browser` 或 `quit-confirm`，理由 `matched-file-dialog`；離開提示的動態文字欄為空。失敗或原版模式不殘留前幀文字。既有 `dialog` 留給說明視窗。

| 本機固定資源 | SHA-256 |
|---|---|
| `file-dialogs-v1/manifest.json` | `6fc74370c334d77b62f2e0d224a80cb967d158da3e632a79aa1e4017636792b6` |
| `file-dialogs-v1/browser.png` | `222b2939a1f0eae1b7fc15822babd8dc253d5187b5cbb0d07ca5868c1b050754` |
| `file-dialogs-v1/glyphs.png` | `147840d8a0a343361f4c2165ab21c28d7b3ff3813d065ff17d6ea378eedc2618` |
| `file-dialogs-v1/quit-confirm.png` | `b0e62043c86b24a4dbf77dffb7b31dfd1f99430b41131bb9916d6cc4f3151d30` |
| `file-dialogs-v1/palette.json` | `4103f1e8410a2ee91de3074579ce3062de27f48c1d2c415f46bbd195c50b56df` |

原型用首批八份來源重生前三張 PNG 與 manifest。色盤由 `file_dialog_catalog.py` 審查全部正常來源後輸出 `palette.json`，原樣複製到本機素材目錄；該檔另以固定雜湊鎖定。

載入時檢查完整 manifest、字型、授權、色盤與圖片雜湊及尺寸。manifest／字型／授權／色盤資源故障只停本批兩類；底板／atlas 故障只停檔案視窗，離開 PNG 故障只停離開提示。其他既有 HD 家族照常辨識。已知來源發生資源或使用中色盤失配時，保留整幀原版，不再向下套城市覆繪。

## 驗證與完成閘門

1. 正式 Linux GUI 冷啟動，檔名輸入、退格、八字元、清單選取／捲動、取消、空清單／空白確認、覆寫與離開選否。檔案視窗及離開提示各驗 F12 往返，原版畫面及讀鍵不變。
2. Python 依 ROM 獨立重建完整來源、字串、使用中色盤、固定 PNG 與整個區外；Go 核對器亦驗完整呈現。來源、字形、背景、區外、色盤、統計各做有效負對照，同步更新受影響雜湊與原版 PNG，仍須拒絕；另驗未用色盤索引與真實資源缺失／竄改、兄弟資源隔離。
3. 正常施工、原版存檔、兩次原版退出、全新 EXE 讀回原施工格與資金。原件保留後重生正式收據，研究探針不代替此項。
4. 正式實作前預登記：選同一唯一正常 GUI 冷啟動輸入，兩側完整執行原版步數，**每 24,000,000 步抽樣 HD**。要求確實經過 `file-browser` 與 `quit-confirm` 各至少一次；記錄具體抽樣數與範圍。RAM、CPU、原畫面、色盤、埠、OPL、讀鍵、DOS 狀態與檔案操作相同。兩側固定同一 dosgolem 初始狀態、虛擬時間及輸入，不重擲挑樣；這是呈現無副作用抽樣，沒有逐幀或跨亂數實作精確聲明。
5. 真實資源的必要 Go 測試無跳過；Linux、Windows amd64、macOS amd64／arm64 編譯與架構檢查。35 原始檔及 RAR 不變，擁有權與 Docker 清理通過。真機及正式封包另驗。

上述完成前不升 CONFORMED 或關閉 #38。原版圖庫、原文資料、字型、圖片、存檔及收據只留本機；Git 只收原創工具與文件。

## 正式驗證結果

實作入口為 [file_dialogs.go](../../workspace/app/internal/hd/file_dialogs.go)。本批只有呈現層，不引用 DOS 執行器；按當幀完整來源及實際使用色盤畫固定參考。原版處理全部操作與存檔。

- [實際資源測試](../../workspace/app/internal/hd/file_dialogs_test.go) 驗 243 份來源、729 個單像素破壞、雙紅色選取、使用／未使用色盤、十四種必要資源缺失／竄改及兄弟家族隔離。完整 HD、鍵盤、原點測試 67.554 秒通過且無跳過，新增雙選取後本批再驗 13.57 秒通過。
- [正常 HD 操作](../../workspace/tools/file_dialog_hd_playtest.sh) 在 `workspace/runs/file-dialogs-hd/` 取得 64 份收據。空清單、空白存檔、八／九字元、退格、取消、十檔七列捲動與邊界、讀檔輸入忽略、覆寫、其他九檔不變、離開選否及兩家族 F12 均通過。
- `workspace/runs/gui-file-dialogs-cold/` 另有 45 份正常施工存退讀收據，兩次原版退出、全新 EXE 讀回原施工格及資金 79980 通過。存／讀／兩次離開視窗的四次 F12 往返保持原版畫面與鍵盤不變。022 的 `gui-cold/` 原件及 catalog 路徑保留。
- 合計 109 份正常收據的來源及像素由獨立 Python／Go 核對。53 份檔案／提示收據包含原版主題往返，獨立重建字串、墨色、使用中色盤、完整固定面板與全部區外；198 字形墨跡及原位八字、離開提示目視通過。冷讀後標題、十四工具與底部文字另驗恢復。
- [有效負對照](../../workspace/tools/hd_file_dialogs_negative.py) 重算色號、原版 PNG 與呈現雜湊後，十八項來源、字形、背景、區外、色盤及中繼資料破壞均被 Python／Go 拒絕。四個正對照含未使用色盤變動，均通過；證據在 `workspace/runs/file-dialogs-negative/`。

整批命令為 `bash workspace/tools/file_dialogs_verify.sh`。從正常冷啟動至 `quit-file-theme-hd-capture.zip` 的唯一原版硬體輸入，兩側各完整執行 **2,688,000,000 步**，按預登記每 24,000,000 步抽樣，共 112 次。實際包含檔案視窗六次、離開提示三次、說明三次及城市各層六十次。原版側 175.408 秒、HD 側 138.719 秒。

兩側 RAM、CPU、原版色號、色盤、埠、OPL、讀鍵、DOS 狀態、檔案操作、原版寫入紀錄與落地 SAV 雜湊相同，狀態 SHA-256 `f55713cac7d97ff24ed9b8e4b21590a65cd254890efd7d926a23129f0a07bf0e`。稽核各用獨立空白可寫 scratch，並回對正常 GUI 的原版畫面、色盤、讀鍵與檔案操作。`ROUND4.SAV` 維持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`，與正常 GUI 實際存檔一致。這是明示呈現抽樣與正常路徑驗證，不宣稱逐幀或跨亂數實作精確對拍。

狀態收據為 `workspace/runs/file-dialogs-state-audit.json`，命令、來源、程式／工具、固定素材、全部正常收據及四架構雜湊在 `file-dialogs-state-provenance.json`。Linux amd64、Windows amd64、macOS amd64／arm64 編譯與結構核對、35 原始檔與 RAR 不變均通過。平台真機與正式封包、模態外高清化、其他視窗／圖表／圖片／場景／動畫仍未完成。
