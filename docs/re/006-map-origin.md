# 地圖原點與 HD 捲動證據

對應 [#23](https://github.com/wicanr2/taipei/issues/23)、[#24](https://github.com/wicanr2/taipei/issues/24)。研究範圍限現行地景比較原型的材質定位。

## 輸入與工具

| 項目 | 固定輸入 |
|---|---|
| EXE | `RS201.EXE`，SHA-256 `798db7f69e287690814f4e7b588be733fc0ad28a6ad943eb397d1f82528db3b3` |
| ROM | `RS201.ROM`，SHA-256 `0cfa01ab22c24de391b6bfc42b1d5786a16c8feecab8e004f87cfb7a759afc29` |
| IDA | 9.4；image `sha256:4ac62de83339c215bab10e455cee3a22d9c6efed9fd0d8ed0f068327b83a06ab` |
| 資料庫 | 唯讀來源 `workspace/runs/ida-19/event-keys.i64`；查詢使用一次性副本 `workspace/runs/ida-24/camera.i64` |
| 匯出 | `bash workspace/tools/ida_camera_probe.sh`；[查詢腳本](../../workspace/tools/ida_camera_probe.py)，本機 `ida-24/camera.json`、`draw.json` |
| dosgolem | 基底 `a9714ebdab2ad6b529f81225472680f2b11f2842` 加本專案六份補丁；MZ 載入段 `0110h` |

IDA 線性位址、檔案偏移與 dosgolem 段位址分欄記錄。下列語意不改原始資料庫名稱。

## 已證實的讀寫鏈

| IDA 原始定位 | 原始 bytes 或運算元 | 語意與證據等級 |
|---|---|---|
| `sub_16C1C`，`16D13h` | 呼叫 `sub_1850A` | 已證實：地圖焦點下方向鍵抵達邊界後，傳方向 1 至 4 進入捲動處理 |
| `sub_1850A`，`18536h`／`18552h` | `sub/add es:word_32420, 2` | 已證實：垂直原點每次減／加兩格；下移前比較 `originY+10h` 與 `59h` |
| `sub_1850A`，`18566h`／`1857Eh` | `sub/add es:word_3241C, 2` | 已證實：水平原點每次減／加兩格；右移前比較 `originX+1Eh` 與 `69h` |
| `185B8h`，檔案 `A5B8h` | `8e063e21`，`mov es, seg_3456E` | 已證實：由 DS:`213Eh` 取得水平原點的段 |
| `185BCh`，檔案 `A5BCh` | `26a19c07`，`mov ax, es:word_3241C` | 已證實：水平原點位於上述段的 `079Ch` |
| `185C0h`，檔案 `A5C0h` | `8e064021`，`mov es, seg_34570` | 已證實：由 DS:`2140h` 取得垂直原點的段 |
| `185C6h`，檔案 `A5C6h` | `26a1a007`，`mov ax, es:word_32420` | 已證實：垂直原點位於上述段的 `07A0h` |
| `185CAh` 至 `185EBh` | `(originY+row)*word_322F0 + originX + col` | 已證實：上述兩值用於地圖資料索引，單位為圖塊 |
| `185FBh` 至 `1861Ah` | 畫面 `x=5+col*9`，`y=34+row*9` | 已證實：圖塊 9×9；兩個迴圈各取 29 欄與 15 列 |
| `18B4Dh`，檔案 `AB4Dh` | `5e`，`pop si` | 已證實：地圖迴圈、附加覆繪、矩形處理及游標函式都已返回，接著為函式尾聲 |

## 重定位核對

EXE 檔頭長 `2000h`，有 2018 筆重定位。`seg_3456E`、`seg_34570` 分別對應檔案 `2656Eh`、`26570h`，原始值都為 `21C8h`，且兩者都列於 MZ 重定位表。dosgolem 加載入段 `0110h` 後為 `22D8h`，因此原點讀取位置為 `22D8:079C`、`22D8:07A0`。

DS 表的 IDA 基址為 `32430h`。原型依已核對的 MZ 映像位置取得執行期表位置，並驗證兩個段指標等於 `22D8h`。不依賴擷取瞬間的 CPU DS／ES。

重繪完成定位的 IDA 段基址為 `16340h`，對應相對載入段 `0634h`。dosgolem 使用 `0744:280D` 觀察 `18B4Dh`。觀察只讀，不寫入原版 CPU、記憶體或畫面。

## 原型缺陷與驗證範圍

修正前，24 份正常冷啟動 GUI 收據通過來源條件、覆繪數及回退像素檢查。六組充分可辨識的原版圖塊位移證明水平與垂直捲動。相同世界位置的 2001 個合格地景格全部改變 HD 紋理，原因是原型以視窗座標索引材質。

修正前證據保存在 `workspace/runs/hd-scroll-before-fix/verification.json`。幾何門檻先登記於 #23：至少 100 格重疊、至少 8 種圖塊、至少 98% 相符；置換圖塊的負對照必須被拒絕。

## 修正後正常 GUI 核對

重跑 `bash workspace/tools/hd_scroll_playtest.sh`，從原版冷啟動、新城市、地圖焦點，實際按方向鍵經四向捲動、檔案選單取消及主題切換。沒有快照或座標注入。Python 3.11.2 與 ImageMagick 6.9.11-60 Q16 在固定 GUI image 中獨立核對：

```sh
python3 /workspace/tools/hd_scroll_check.py --original /orig --receipts /workspace/runs/hd-scroll --require-world-origin
```

上述命令須在本專案 GUI Docker image 中使用 `/orig` 唯讀掛載與 `/workspace` 工作區掛載，不在主機執行。24 份單幀收據通過來源數量、呈現雜湊與回退格逐像素核對。六組充分辨識位移如下，推論等級均為已證實，限本次抽樣。

| 正常輸入擷取 | 原點變化 | 原版圖塊位移 | 相同世界材質格 | HD 改變格數 |
|---|---|---|---|---|
| right-20 → right-30 | `(12,12)` → `(14,12)` | `(2,0)` | 403 | 0 |
| right-30 → right-40 | `(14,12)` → `(24,12)` | `(10,0)` | 283 | 0 |
| down-12 → down-18 | `(24,12)` → `(24,16)` | `(0,4)` | 316 | 0 |
| left-20 → left-30 | `(24,16)` → `(22,16)` | `(-2,0)` | 400 | 0 |
| left-30 → left-40 | `(22,16)` → `(12,16)` | `(-10,0)` | 282 | 0 |
| up-12 → up-18 | `(12,16)` → `(12,12)` | `(0,-4)` | 317 | 0 |

原點差與畫面位移完全一致。2001 個合格世界地景格的 36×36 實際 HD 像素逐一相同。置換圖塊的幾何負對照被拒絕。檔案選單整幀回退、取消恢復、F12 切換不增加原版讀鍵。擷取、幾何及逐像素證據保存在 `workspace/runs/hd-scroll/verification.json`。

`presentation-audit` 從同一正常 GUI 收據重播鍵盤輸入。兩側使用相同 EXE、dosgolem 初始狀態、虛擬時鐘與 1,608,000,000 步，不重新挑選亂數結果。一側只跑原版，另一側加上唯讀原點觀察及 HD 繪圖。完整 RAM、CPU、原版色號、色盤、埠值、OPL 暫存器與讀鍵紀錄相同，狀態 SHA-256 為 `451e505444347378857bbaa785a24e7218a263e0d2fa2b806bdda7d244242f92`。實際觀察 1300 次地圖完成、1668 幀 HD 呈現。收據為 `workspace/runs/hd-scroll/presentation-state-audit.json`。

錯誤段指標、超界原點、首次完成事件前、捲動未完成時，以及 HD 繪圖器收到未知原點的負對照通過。鏡像延伸邊界與整張可見地圖範圍的索引檢查通過。這些小型測試只驗防護條件，正常捲動結論來自上述 GUI 收據。

本次沒有逐週期動畫驗收，也沒有驗證全地圖、全部字型或正式封包。本規格及修正仍為可撤回的 DRAFT 原型。

修正後另外執行 `TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh`，正常施工、檔名退格、原版存檔、原版退出、全新 EXE 冷啟動讀回及再次退出通過。施工格仍為 `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139`，存檔 SHA-256 仍為 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。35 份施工存退讀單幀收據與 24 份捲動收據通過獨立 `receipt-check`，包含原版 PNG 與地圖區外像素。Linux、Windows、macOS 兩架構重新編譯通過，沒有新增平台真機驗收聲明。
