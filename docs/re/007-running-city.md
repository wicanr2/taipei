# 城市持續運行與年度預算視窗

對應 [#25](https://github.com/wicanr2/taipei/issues/25)、[#26](https://github.com/wicanr2/taipei/issues/26)。範圍限 B 地景 DRAFT 原型，補足先前暫停城市與捲動抽樣之外的正常時間推進。

## 固定輸入與工具

| 項目 | 輸入與版本 |
|---|---|
| EXE | `RS201.EXE /A /D /x`；SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |
| ROM | `RS201.ROM`；SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29` |
| dosgolem | 基底 `a9714ebdab2ad6b529f81225472680f2b11f2842`，加本專案六份補丁；[建置入口](../../workspace/tools/build_preview.sh)與本機 `workspace/runs/preview-provenance.txt` 保存依賴及補丁雜湊 |
| GUI image | `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`；Go 1.24.13、Python 3.11.2、ImageMagick 6.9.11-60 Q16 |
| 原版輸入證據 | IDA 9.4，`workspace/runs/ida-19/event-keys.json`、`input-sites.json`；沿用 [工具列研究](004-native-controls.md)的固定 EXE 與唯讀資料庫，沒有追加硬體時序逆向 |
| HD 材質 | [008 原型](../spec/008-hd-material-prototype.md)的三份固定素材；只涵蓋成員 59 的水面、沙地與樹冠 |

## 原版速度操作

正常冷啟動經主選單、新城市與難度選擇至城市，從實際視窗送入原版鍵 `3`。沒有送暫停鍵 `0`、使用快照、注入日期或由前端改寫速度欄位。原版讀鍵紀錄包含 `Key=51`、`Word=0433h`。速度操作的原始定位如下，IDA 線性位址與檔案偏移分欄。

| IDA 原始定位 | 檔案偏移 | 原始 bytes／運算元 | 證據等級與用途 |
|---|---|---|---|
| `sub_16C1C`，`16CA4h` | `8CA4h` | `b004`，`mov al, 4` | 已證實：原版數字鍵分派的鍵 `3` 分支，接共同呼叫 `sub_274F6` |
| `16C91h` | `8C91h` | `9a861b9725`，`call sub_274F6` | 已證實：上述原版控制入口 |
| `sub_274F6`，`276F4h` | `196F4h` | `26c6069a0700`，`mov es:byte_3241A, 0` | 已證實：參數 4 分支的原版欄位寫入；保留原始名稱，不推定精確時間倍率 |
| `27708h` | `19708h` | `9a54223416`，`call sub_18594` | 已證實：原版控制分支返回前呼叫重繪 |

## 正常 GUI 抽樣

重生入口為 `bash workspace/tools/hd_runtime_playtest.sh`。腳本使用上述 Docker image、唯讀 `/orig` 與可寫 `/workspace`，以有界 Xvfb 和實際視窗按鍵執行；不在主機啟動遊戲。每次更新 400,000 虛擬步，每隔 24,000,000 步擷取，預登記 60 份持續運行收據。

獨立核對命令須在同一 GUI Docker image 中執行：

```sh
python3 /workspace/tools/hd_runtime_check.py --original /orig --receipts /workspace/runs/hd-runtime
/workspace/runs/receipt-check -dir /workspace/runs/hd-runtime
```

核對器從固定 ROM 重解 135 個 9×9 圖塊，核對來源合格數、實際呈現像素、原版回退、原點、色盤及同一地景的 HD 穩定性。日期矩形為原生 `(270,174,50,11)`；裁圖去重後另由人工辨識，雜湊變化本身不作月份證據。

| 證據 | 結果 |
|---|---|
| 原子收據 | 65 份同幀封裝通過，包含 60 份持續運行樣本 |
| 虛擬步數 | `running-01` 為 984,000,000，`running-60` 為 2,400,000,000；60 份皆相隔 24,000,000 |
| 原版日期 | 人工檢視 `dates-contact.png`，49 個連續月份從 80 年 11 月至 84 年 11 月 |
| 正常城市 | 58 份，均有 433 格合格來源及實際覆繪，原點皆為 `(12,12)` |
| 年度預算視窗 | `running-03`、`running-32`；修正後覆繪數均為 0，全幀 RGBA 等於原版四倍 |
| 返回城市 | `running-04`、`running-33` 恢復 433 格覆繪 |
| 地景穩定性 | 相鄰合格畫面中 23,815 個原版來源及原點相同的地景格，36×36 HD 像素全部相同 |
| 色盤 | 材質使用的 RGB 只有一種雜湊；完整色盤有兩種，不推測未追查差異的原因 |

收據、完整核對與日期裁圖保存在本機 `workspace/runs/hd-runtime/`。擷取結束由研究停止請求退出前端，不宣稱本項驗了原版離開或存檔；正常存退讀由 [前端驗收](../spec/005-frontend-preview.md)另行保存。

## 預算視窗缺陷與修正

修正前兩份真實年度視窗的 BIOS 阻塞狀態均為 false，頂部城市 UI 指紋仍相符，原型因此覆繪視窗外的 29 格地景。這違反 [010](../spec/010-hd-live-prototype.md) 的整幀回退契約。修正前收據保留於 `workspace/runs/hd-runtime-before-guard/`，沒有重寫歷史結果。

先建立 #26，再以實際標題色號辨識年度視窗；完整特徵、雜湊與範圍見 [012](../spec/012-budget-window-prototype.md)。兩份實際收據的全幀回退測試通過，重新冷啟動也捕捉相同預算視窗及返回城市。既有城市、來源失配、素材撤除、色盤與未知原點回退測試通過。共享核對器新增整幀回退檢查後，既有 24 份捲動收據與六組位移重新核對通過，2001 個世界地景格仍保持相同像素。

## 原版機器狀態

[presentation-audit](../../workspace/app/cmd/presentation-audit/main.go) 加 `-require-budget`，重播修正前 `running-60-capture.zip` 的完整正常 GUI 鍵盤序列。固定原始輸入、dosgolem 初始狀態與虛擬時間，兩側各 2,400,000,000 步，分別只執行原版及加入唯讀原點觀察和 HD 繪圖。沒有重擲或挑選亂數結果。

完整 RAM、CPU、原版色號、色盤、埠值、OPL 暫存器及讀鍵紀錄相同。狀態 SHA-256 為 `b940de4f9be1b6b322152947e8c3d658c6add061d629368a9c00e3241d32e734`；有 1776 次地圖重繪完成、3610 次 HD 呈現、107 次年度視窗回退。完整收據為 `workspace/runs/hd-runtime/budget-state-audit.json`。這證明本次呈現處理未改變所比較的原版狀態，不證明全遊戲規則或亂數實作對拍完成。

## 限制

以上推論等級為已證實，限固定 EXE、空城市、原版速度鍵與列出的實際抽樣。固定步數擷取不能證明所有未擷取的開關相位沒有閃爍。尚未涵蓋發展後建物、全遊戲動畫、所有原版視窗、正式字型或平台真機。#7、#8、#9 的正式驗收閘門維持；本項未產生封包。
