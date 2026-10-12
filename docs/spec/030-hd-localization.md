# 030：HD 五語系

狀態：DRAFT。Issue：[#49](https://github.com/wicanr2/taipei/issues/49)。

## 已確認範圍

使用者指定繁體中文、簡體中文、日文、韓文、英文，並確認「HD 模式提供五語系，原版模式保留繁中」。原版 EXE、規則、亂數、資源識別與存檔格式不變。F12 維持既有原版／HD 切換。

遊戲中語言切換、設定保存及正式排版尚待確認。F11 面板只是可撤回操作原型，沒有接入產品，也未攔截任何遊戲按鍵。

## 顯示與語意邊界

依外部契約 `/home/anr2/.codex/knowledge-base/local/localization-display-semantic-isolation.md`，語言文字以 UTF-8 TSV 為唯一來源。初稿為 [ui.tsv](../../workspace/app/locales/ui.tsv)，欄位是 `key`、`zh-Hant`、`zh-Hans`、`ja`、`ko`、`en`。正式程式與版面只引用穩定文字鍵。修改譯文不應要求重新編譯。

原版讀鍵、比較常數、資源名稱、DOS 路徑、玩家檔名、城市資料、數值與 SAV 序列化不使用譯文。原版回退仍顯示原生繁中；HD 缺字、缺鍵或版面失配的處理需另列明確契約，不能默默裁掉文字。

現有 `萬` 表示原版的 10,000 單位。翻譯單位不換算遊戲內金額，也不改人口目標。新遊戲說明的目標保留「超過五十萬」。

## 現有來源與需要分離的文字

下表是已讀取的實作及來源事實，並非全遊戲翻譯覆蓋清單。

| 呈現家族 | 現有來源 | 多語系工作 |
|---|---|---|
| 六個功能標題 | `internal/hd/menu.go` 的原文及六個固定安全矩形 | 改以文字鍵及語系排版；保留 F1–F6 與原版按鍵 |
| 主選單、城市、難度 | `startup-menu-layout-v1.json`，十三個既有選取狀態 | 拆出烘焙文字；保留原版選取、按鈕與命中來源 |
| 五工具子選單 | `tool-menu-layout-v1.json`，十八個既有選取狀態 | 以選項為整句翻譯單位，避免逐中文字替換 |
| 城市六功能選單 | `city-menu-layout-v1.json`，二十九個既有選取狀態 | 同上；保留實際原版選項索引 |
| 新遊戲說明 | `new-game-text-v1.json` 的九十個文字格 | 重組三段原文再翻譯；長段落需換行與實際墨跡驗證 |
| 預算 | `budget-layout-v1.json`、固定底板與十一個原數值欄 | 靜態標籤與單位分離，數值來源及操作保持原版 |
| 底部資訊 | `footer.go` 的來源重建與字形圖集 | 翻譯標籤與日期／單位格式；保留原數值及未知角落符號 |
| 存讀檔與離開確認 | `file_dialogs.go` 的底板及字形圖集 | 靜態提示另盤點；檔名與列表保持玩家原值 |
| 圖表與政績 | `chart_panel.go`、`ending_screen.go` 的固定素材 | 分離烘焙標題；原圖表資料像素及來源閘門保持原樣 |
| 其他事件與文字 | 完整 HD 母項及原版來源 | 未完成辨識前保留未知，不以初稿宣稱全遊戲翻譯完成 |

上述 JSON 與素材都在本機 `workspace/prototypes/hd-style/`。來源識別沿各既有規格，不把顯示譯文當成識別原版畫面的依據。

## 可撤回原型

工具：[locale-prototype](../../workspace/app/cmd/locale-prototype/main.go)。只讀正常 HD 收據與固定字型，輸出五語系的六標題及 F11 面板示意，不 import 產品呈現器，也不執行 DOS。

| 輸入 | SHA-256 |
|---|---|
| `workspace/runs/gui-ending-scene-cold-r1/uncover-power-presentation.png` | `39d288d8fada337c82fa09de84a8d73d6142d54d3b57cdd365d138e5f21b9c8f` |
| `NotoSansCJKtc-Regular.otf`，Sans2.004 | `dce08bd4fd91aa8aa76ed8fea4b694c2dfb8550f67871e326843212ddbeb88b4` |
| 初稿 `ui.tsv` | `a3a57e48ec174ed33caca6d3619f4cf23997caed71b05ecce9a150eed8ec0bf3` |

工具鏈沿用 image `sha256:c3d8835a9d39ec7229078a6f49c0036af2aaf1cee0f15e1a8b2cbb7f6d232ff3`、Go 1.24.13、`golang.org/x/image v0.31.0`，Docker 內 `--network none`、UID/GID 1000、2 CPU、2 GiB、有界逾時。從 `/workspace/app` 執行：

```sh
go run -p 1 ./cmd/locale-prototype \
  -input /workspace/runs/gui-ending-scene-cold-r1/uncover-power-presentation.png \
  -font /workspace/prototypes/hd-style/fonts/NotoSansCJKtc-Regular.otf \
  -catalog /workspace/app/locales/ui.tsv \
  -out /workspace/prototypes/hd-style/locale-draft-r1
```

初稿有 92 鍵、五個完整語系欄，共 641 種字元。UTF-8、欄數、鍵唯一、空值、控制字元、佔位符一致與固定字型 glyph index 檢查通過。43 處實際墨跡皆落在安全矩形；五張完整城市原型只改六個標題區，其餘像素逐一相同。

六標題字級為 21–56 px，英文 `Environment` 為 21 px。此結果只證明未缺字或裁切，未證明小字閱讀舒適、日韓區域字形偏好、長段落排版或完整玩家路徑。初稿譯文也尚未完成語言審閱。

輸出只留本機 `workspace/prototypes/hd-style/locale-draft-r1/`，包含 `receipt.json`、`five-languages.png`、`language-picker-draft.png` 及五張完整畫面。收據保留來源、字型、TSV 與輸出雜湊、實際墨跡及字級。含原版／衍生素材的圖片不入 Git。

另以同一來源乾淨重生至 `locale-draft-rebuild-r1/`，八檔逐 byte 相同。八項有效負對照包含重複鍵、缺譯、無效 UTF-8、錯欄數、佔位符不一致、缺字、缺呈現鍵及覆寫既有輸出，皆因預期原因拒絕。結果保存於 `locale-validation-r1/validation.json`。這是離線工具驗證，不是正常玩家路徑驗收。

## 待定與正式驗收

- 目前前沿：啟動時選語言，或 F11 遊戲中切換並保存選擇。待使用者回答後，整理共同理解，再依共同決策入口確認正式契約。
- 正式驗收需涵蓋全部可切換文字鍵、實際來源覆蓋、最長字串、原數值與玩家檔名、未知來源回退，以及 F12 原版繁中不變。完整覆蓋未達成前，不關閉 #49。
- 目前只進行離線文字／操作原型。先前「不用抽樣囉，先 commit + push」的停止點保持有效，沒有重啟 #48 圖表正常 GUI 或長時間原版狀態抽樣。
