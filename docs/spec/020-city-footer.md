# 城市底部動態文字

狀態：CONFORMED，限本研究前端的費用、年月與資金欄位，右下未知符號仍為原圖。對應 [#31](https://github.com/wicanr2/taipei/issues/31#issuecomment-6107137732)。

## 來源與證據

沿用 [009 字模證據](../re/009-chinese-font-sources.md) 與 [019 城市框架](019-city-chrome.md) 固定的 EXE、ROM、dosgolem、字型及 B 背景。來源唯讀，HD 不讀寫遊戲變數，只辨識實際原版畫面。

| 來源 | 定位與已確認內容 |
|---|---|
| RS201.ROM 成員 1 | 檔案偏移 1888、10774 bytes；320×200 完整底圖像素 SHA-256 `a35e8372b6dbd661444299f3241ad36634291b1c6657e6feacf8189c53e04dd7` |
| 成員 56 | 檔案偏移 935884、1014 bytes；標頭 5／7／7。數字與減號依 ASCII 減 32 取七 bytes，各列高五 bits。數字在正常收據逐點符合；減號僅有原始字庫證據，尚未正常負資金抽樣 |
| 成員 57／58 | 15×14 實際墨跡及原始兩 byte 字碼。索引 107、108、109、110 分別為「每、單、位、萬」，原位紅色色號 32，正常逐點符合 |
| 費用原位 | 中文左上依次為 (19,177)、(35,177)、(51,177)、(103,177)。六個 6×7 數字槽由 (67,181) 開始，右對齊 |
| 日期與資金 | 白色色號 15，5×7 墨跡、六點字距。日期 y=176，資金 y=184；年月萬已烘在底圖，原位分別為 (283,176)、(303,176)、(303,184)，各 7×7 |

原版來源為 `workspace/runs/city-chrome-native/` 的正常十四工具與 `gui-cold-before-footer/` 的施工收據。68 份完整欄位重建通過，408 個單點破壞負對照被拒絕，輸出 `workspace/runs/footer-source/catalog.json`。工具費用已觀察空白、10、20、50、300、500、1000、3000、5000、50000、80000、100000；施工前後資金有變。這些是已觀察的顯示字串，不據此推定規則或上限。右下 (247,184,7,7) 符號未確認語意，保留原版像素，不宣稱本批已將此符號 HD 化。

2026-10-11 證據審查：全部欄位背景與墨跡均由固定 ROM 重建，沒有任意 Unicode 候選；正常字串、前置空白與單位位置可逐點回查。此證據足以辨識呈現，不推定尚未觀察的數值範圍。Noto 十八字形實際 alpha 墨跡檢查通過。允許依以下固定契約接入。

| 固定參考 | SHA-256 |
|---|---|
| `footer-v1/glyphs.png`，384×192 | `df2a49313a51d2076e4880bf88cf4fd8a28d722ea49fb98973c05a094107cd7c` |
| `footer-v1/manifest.json` | `f74c71434954de88e4c9fe6c924091b7f7f64512b651fa60be29087eae5f9650` |
| 左欄完整底圖使用色加 15／32 | `3b4208dbfa57fcac1e09c52c785ec7f0732799de26e6ece81e1a257edd1ce081` |
| 右欄完整底圖使用色加 15 | `e2ca09da088ea18b2846c73ba9fddd03b32c20511ca0f60429d03356a37f0c1f` |

## 正式識別與回退契約

- 只在既有已驗證城市、有效地圖原點、非阻塞、非預算視窗、HD 啟用時辨識。
- 左欄完整矩形 (7,175,224,18)，右欄完整矩形 (244,175,71,18)。從 ROM1 重建背景，再用原始字模重畫實際辨出的每個字。整個矩形 bytes 必須完全相同，不能只驗前景墨跡。
- 左欄只接受完整空白底圖，或完整四個中文字與右對齊六槽數字。右欄日期年槽從 x=253 到 277，月槽為 289、295，資金槽從 x=253 到 295，皆六點字距；只接受前置空白、連續數字，資金可有前置減號。這是保守辨識範圍，不宣稱原版數值上限。
- 各欄獨立確認來源及使用中色盤。來源、色盤、字型、授權、背景或固定字形參考失配時，該欄整欄保持原版。未知字串不補值。
- Noto 字形離線生成固定透明 atlas。數字 28 點、費用中文 52 點、右欄單位 28 點，72 DPI、無 hinting。逐字檢查實際 alpha 墨跡位於原版四倍安全矩形，缺字或越界停止生成。
- 背景取 019 固定 B 框架參考的相同座標。只改兩欄內像素，右下未知符號按原版四倍保留。每幀先恢復原版再覆繪，不保留上幀數值，防止數字縮短殘影。
- 收據加入欄位遮罩、已識別字串及原因。F12 不傳入 DOS，沿用 014。

## 預登記驗證

1. 從 ROM 與正常收據獨立重建全部欄位，加入單點墨跡、空白背景及單位來源破壞，均拒絕原匹配。
2. 十四工具確認、五子選單完整回退、取消返回、F12 往返；推進正常月份與施工資金更新，不注入遊戲狀態。
3. 獨立核對固定 atlas、B 背景、整欄及其他覆繪區外像素。更新受影響雜湊的有效負對照仍須失敗。
4. 正常施工、存檔、原版退出、全新啟動讀回；重播相同唯一鍵盤輸入確認 DOS RAM、CPU、畫面、色盤、埠、OPL、鍵盤及檔案操作不變。
5. 實際資源測試、Linux／Windows／macOS 兩架構編譯，保留未驗的負資金、超出辨識槽與平台真機限制。完整 HD 與正式封包另驗。

本機生成圖、原文資料、畫面與原版字模不入 Git。新原創程式及來源盤點入口由 CONTEXT 索引。

## 驗證結果與重生入口

2026-10-11，固定 GUI image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`、Go 1.24.13。正常工具路徑與存退讀皆執行相同 Linux binary，SHA-256 `9c2f97887f5ea4089447ae25af7acfd09dd3a80a2aa340a1be287e5cc8293977`，與 `footer-gui/program-provenance.txt` 一致。

| 驗證 | 結果與本機證據 |
|---|---|
| 固定十八字形 | 全部實際 alpha 墨跡位於安全矩形，無缺字；重生 PNG 與 manifest 雜湊不變 |
| 正常十四工具及時間 | `workspace/runs/footer-gui/`，66 份收據，42 種工具外框、五子選單回退、取消與 F12；費用包含六位 100000，日期由 80 年 9 月正常推進至 10 月 |
| 施工及存退讀 | `workspace/runs/gui-cold/`，37 份收據，施工資金 80000 → 79980、原版存檔、兩次原版退出、全新啟動讀回原施工格及資金；沒有快照或狀態注入 |
| 獨立像素與來源 | 103 份整欄、固定 atlas、背景、原符號、已驗框架／選單／標題／圖示與其餘區外全部相符。Python 重算 ROM 與字串，Go 單幀核對完整固定參考及區外 |
| 有效負對照 | `workspace/runs/footer-negative/result.json`，字形、背景、原符號、區外、來源、色盤、遮罩、字串八項；受影響雜湊及原版 PNG 保持一致後仍被拒絕。來源／色盤由 Python 底部核對器直接拒絕；Go 不重算這兩項，沒有聲稱兩個核對器各自都驗全部來源 |
| 原版狀態不變 | `footer-state-audit.json`、`footer-state-provenance.json`。相同唯一正常硬體輸入、固定起始狀態與虛擬時間兩側各 2,352,000,000 步，含 3,236 幀兩欄覆繪；RAM、CPU、原版畫面、色盤、埠、OPL、讀鍵與檔案操作相同。狀態 SHA-256 `93808909ec3603a2b2e933e1af782c28178f9f27663ad0842f103be6b2707daa` |
| 存檔及施工格 | 原版存檔 SHA-256 保持 `8c708ef41c56ca6b705de821d69b553f9fbb76c85f391cc599105ea439d6a4ad`；(230,43) 施工格冷讀 SHA-256 `4aa14e7ead003f1071348ea65f64f5d6cb430efe4b2cd51c8bb78bb3ff364139` |
| 真實資源測試及編譯 | Go HD 測試通過，含缺失／竄改五項資源、分欄來源及色盤、縮短數字背景恢復。Linux amd64、Windows amd64、macOS amd64／arm64 編譯通過，未新增平台真機或正式封包聲明 |

主機只呼叫以下 Docker 包裝入口：

```sh
TAIPEI_THEME=hd-b TAIPEI_CHROME_RUN=footer-gui TAIPEI_FOOTER_TIME=1 bash workspace/tools/city_chrome_playtest.sh
TAIPEI_THEME=hd-b bash workspace/tools/gui_playtest.sh
```

以下核對命令在同一固定 GUI image 中執行，`/orig` 唯讀，`/workspace` 為 UID/GID 1000:1000 可寫工作區；掛載與資源限制沿上述包裝入口：

```sh
python3 /workspace/tools/hd_footer_check.py --receipts /workspace/runs/footer-gui --require-time-update
python3 /workspace/tools/hd_footer_check.py --receipts /workspace/runs/gui-cold
python3 /workspace/tools/hd_footer_negative.py --receipt /workspace/runs/footer-gui/confirm-13-capture.zip --out /workspace/runs/footer-negative
/workspace/runs/receipt-check -dir /workspace/runs/gui-cold -font-reference /workspace/prototypes/hd-style/font-comparison/noto-font.png -ui-reference /workspace/prototypes/hd-style/city-icons-b-v1.png -dialog-reference /workspace/prototypes/hd-style/new-game-noto-reference-v1.png -panel-manifest /workspace/prototypes/hd-style/startup-menus-v1/manifest.json -chrome-reference /workspace/prototypes/hd-style/city-chrome-v1 -footer-reference /workspace/prototypes/hd-style
/workspace/runs/presentation-audit -original /orig -materials /workspace/prototypes/hd-style -receipt /workspace/runs/footer-gui/pause-after-time-capture.zip -out /workspace/runs/footer-state-audit.json -require-dialog -require-font -require-icons -require-chrome -require-footer
```

正常連續按鍵的初次腳本少送兩次 Right，施工落在其他格。證據保留 `gui-cold-footer-missed-input/`，修正另見 [#34](https://github.com/wicanr2/taipei/issues/34)；25 次移動改為逐次等原版讀鍵與前端釋放收據，保持原施工位置及全部驗收條件後，以同一 image／命令乾淨重跑通過。這是驗證工具修正，沒有改動遊戲輸入或施工規則。

本批沒有控制不同亂數實作、重擲或挑結果；狀態聲明只限同一 dosgolem 與相同正常輸入下有／無呈現。右下原符號、負資金、超出辨識槽、其他視窗與全遊戲圖片仍保留限制，#31 與完整 HD 母項維持開啟。
