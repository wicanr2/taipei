# 五工具子選單

狀態：CONFORMED，限五工具完整面板。對應 [#31](https://github.com/wicanr2/taipei/issues/31#issuecomment-6107377718)。

本批只處理工具 2、5、9、10、11 的完整選單矩形及十八個選取狀態。沿用 B 風格、1280×800、Noto、F12 與原版版面。規則、輸入與存檔由原版執行。

| 工具 | 原版完整矩形 | 選項數 | 可見來源 |
|---|---|---|---|
| 2 | (228,29,37,35) | 2 | 公路、捷運 |
| 5 | (212,52,53,35) | 2 | 警察局、消防隊 |
| 9 | (196,124,69,35) | 2 | 垃圾處理、污水處理 |
| 10 | (18,37,235,132) | 10 | 左右各五個文化／休閒設施，保留原文與空白字距 |
| 11 | (196,124,69,35) | 2 | 火力電廠、核能電廠 |

## 來源證據

- 固定 EXE／ROM／dosgolem 與 Noto 雜湊沿用 [020](020-city-footer.md) 及 [009 字模證據](../re/009-chinese-font-sources.md)。
- 大選單底圖為 RS201.ROM 成員 19，檔案偏移 159578、7386 bytes，235×132；小選單完整背景為色號 3。文字取成員 57 的前十四列與成員 58 原始字碼。選取為色號 55，其餘 15。
- `tool_submenu_catalog.py` 必須由完整底圖及全部字模重建每一種狀態，與正常 GUI 逐點相同。整個背景、文字空白及邊界均納入來源雜湊，不能只驗前景。
- 原文資料及素材只留本機。正式接入前須取得十八個正常狀態、方向鍵邊界與 Escape 的實見行為，審查全部 Unicode 候選及 Noto 實際墨跡。

## 已審查呈現契約

2026-10-11 證據審查：`tool-submenus-native/` 及其 `extra/` 共 101 份正常冷啟動收據，十八種完整來源全部重建相同，186 個來源單點破壞不符原狀態。成員 57／58 的字模、原始字碼、檔案偏移與 ROM bytes 重新核對。大型十選項原文及空白、小型八選項均已對照原圖審查。離線十八張面板的 462 項 Noto 實際墨跡位於原矩形及按鈕內，允許依固定契約接入。

所有選單的上下鍵循環選取；大型依索引走完左欄再右欄。左右鍵與 Escape 不改畫面且保持阻塞，Space 確認返回，Tab 返回工具列。這些是已觀察的原版行為，不改寫操作。

| 固定本機輸入 | SHA-256 |
|---|---|
| `tool-menu-layout-v1.json` | `8da4bcab9cdff0e2cb59a208814c7f4589458ad6d9148f6cf6c218cce46fa4ee` |
| `tool-menu-sources-v1.json` | `60d1a8df26a807c53bac6b05317107ea13d2e7cc2227d0e406f21a066a065518` |
| `tool-menus-v1/manifest.json` | `288687aa21460d01aa87dd24060c5bbd3ff50035bf26bab5c821d23688f2543e` |

底板採用 018／019 已審查的 `menu-blue-b-v1.png` 與 `city-chrome-lime-v1.png`，素材雜湊保存在固定 layout。沒有生成新素材或改變已確認美術方向。

- 在既有啟動選單／說明視窗與阻塞輸入判斷間辨識。只接受固定完整矩形、來源雜湊與實際使用中色盤。
- 固定完整 B 面板離線組合，字模採 Noto 52 點、72 DPI、無 hinting，原版座標四倍。保留原文選取紅色、其餘白色及原空白字距。
- 大選單採既有 B 綠色底板及藍色按鈕，小選單採既有 B 藍色底板。每幀先恢復原版，再覆繪已確認的完整矩形，矩形外維持原版。
- 未知來源、色盤、字型、授權、manifest 或單張素材失配即回退原版。單張失配不影響其他已確認狀態。
- 收據沿用完整面板 ID、選取值與原因。F12 只切換呈現，不進 DOS。

## 預登記驗證

1. 真實冷啟動遍歷五工具、十八狀態、方向鍵邊界、Escape、確認返回及五場景 F12。逐次確認原版讀鍵與前端 release。
2. 完整來源、原文字模、Noto 實際墨跡、固定面板及矩形外逐點核對；有意改壞前景、背景、區外、來源、色盤與選取值，更新受影響雜湊後仍須拒絕。
3. 缺失或竄改 manifest、字型、授權與單張素材，已知來源完整回退；來源與色盤失配不得覆繪。
4. 正常施工、存檔、原版退出與全新啟動讀回；相同唯一正常硬體輸入與虛擬時間兩側原版狀態相同。
5. Linux、Windows、macOS 兩架構編譯。完整 HD、正式封包及平台真機另驗。

工具入口由 [CONTEXT](../../CONTEXT.md) 索引。本批未驗的其他文字、圖片與場景仍列為未完成。

## 重現入口與抽樣界線

先以 [build_preview.sh](../../workspace/tools/build_preview.sh) 重建產品，再由下列腳本在固定 Docker image 中執行正常 GUI。原生來源另採 `TAIPEI_THEME=original` 及 `tool-submenus-native`，大型補充集為 `tool-submenus-native/extra`、`TAIPEI_SUBMENU_ONLY=10`。

```sh
TAIPEI_THEME=hd-b TAIPEI_SUBMENU_RUN=tool-submenus-hd bash workspace/tools/tool_submenu_playtest.sh
TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh
```

完整 37 份存退讀另驗 Noto 標題、十四圖示、框架及底部。專用字型／圖示核對器需要冷讀收據，不能用子選單探索集取代。Go 單幀核對沿用 020 的全部固定參考，增加 `-tool-panel-manifest /workspace/prototypes/hd-style/tool-menus-v1/manifest.json`。

[#36](https://github.com/wicanr2/taipei/issues/36) 預登記狀態稽核每 24,000,000 步抽樣，外層 900 秒。兩側完整執行原版步數與唯一正常硬體輸入，原點觀察仍逐步執行；十八工具狀態及既有各層均為必要閘門。這是抽樣呈現不改狀態的證據，不代表逐幀對拍。CLI 原預設 400,000 不變。

以下命令在 image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3` 內執行。容器使用 UID／GID 1000、3 GiB、2 CPU、128 PID、無網路；既存 `workspace/` 可寫，使用者原版 RS201 目錄唯讀掛載 `/orig`。工具建置使用鎖定 Go 1.24.13 與現有依賴快取。

```sh
/workspace/runs/presentation-audit -original /orig \
  -materials /workspace/prototypes/hd-style \
  -receipt /workspace/runs/tool-submenus-hd/tool-11-return-toolbar-capture.zip \
  -out /workspace/runs/tool-panels-state-audit.json \
  -render-interval-steps 24000000 -require-tool-panels \
  -require-dialog -require-font -require-icons -require-chrome -require-footer
```

## 2026-10-11 驗證結果

| 驗證 | 實際結果 | 本機證據 |
|---|---|---|
| 正常原版完整來源 | 101 份收據，十八狀態，186 個來源單點負對照；字模與字碼重新核對 ROM bytes | `workspace/runs/tool-submenus-native/` 及 `extra/`、`workspace/prototypes/hd-style/tool-menu-sources-v1.json` |
| 離線 Noto 面板 | 462 項實際墨跡均在原矩形及按鈕內；二十個檔案乾淨重生逐 byte 相同 | `workspace/prototypes/hd-style/tool-menus-v1/`、`workspace/runs/tool-panels-regenerated/` |
| 正常 HD 操作 | 82 份完整收據，十八種選取、原版循環／無效鍵／返回、五場景 F12 | `workspace/runs/tool-submenus-hd/tool-panels-verification.json` |
| 有效竄改負對照 | 大小面板各七項，Python 及 Go 均拒絕；受影響雜湊與原版 PNG 維持一致 | `workspace/runs/tool-panels-negative-small/result.json`、`tool-panels-negative-large/result.json` |
| 真實資源測試 | HD 全套 Go 測試通過，25.360 秒，沒有跳過 | `workspace/runs/tool-panels-go-test.log` |
| 施工、存退讀與退出 | 37 份收據完整參考及區外通過；兩次原版退出、冷讀原施工格及資金相同 | `workspace/runs/gui-cold/result.json`、字型／圖示／底部 verification JSON |
| 原版狀態不變 | 相同唯一正常輸入，兩側各 4,080,000,000 步；170 次 HD 抽樣含十八工具狀態共 99 次、說明一次及城市各層 33 次 | `workspace/runs/tool-panels-state-audit.json`、`tool-panels-state-provenance.json` |
| 跨平台編譯 | Linux amd64、Windows amd64、macOS amd64／arm64 通過，產品 SHA-256 與架構重新核對 | `workspace/runs/tool-panels-input-hygiene.json` |

原版狀態 SHA-256 為 `53700f59970623a9e83a648b7b4b1eeb080126c6d8b45eccff7e0df4cf9394a1`。比較包含完整 RAM 雜湊、CPU、原版色號、色盤、埠、OPL、讀鍵及檔案操作；原版側 214.806 秒，HD 側 220.093 秒。存檔 SHA-256 維持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`。

本批正常 HD 共 119 份收據。十四負對照及真實資源測試補足來源、回退與像素驗證，抽樣狀態比較不擴張為逐幀或全遊戲規則對拍。模態外仍為原版四倍像素；其他視窗、圖表、圖片、場景、動畫、平台真機及正式封包未完成，#31 與 HD 母項保持開啟。
