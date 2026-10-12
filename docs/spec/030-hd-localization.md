# 030：HD 五語系

狀態：F11 語言面板、設定與六標題 READY；其他文字家族 DRAFT。Issue：[#49](https://github.com/wicanr2/taipei/issues/49)。

## 已確認範圍

使用者指定繁體中文、簡體中文、日文、韓文、英文，並確認「HD 模式提供五語系，原版模式保留繁中」。原版 EXE、規則、亂數、資源識別與存檔格式不變。F12 維持既有原版／HD 切換。

使用者看過 F11 原型後回覆「遊戲中切換」，採 F11 面板並記住選擇。Help 已確認 Shift+F1 開啟、保留原版 F1 離開，契約見 [031](031-help.md) 與 [#50](https://github.com/wicanr2/taipei/issues/50)。

## 第一批 READY 契約

本批限語言面板、前端設定與城市六標題。完整五語系仍需其餘文字家族逐批接入，不因選了語言就宣稱所有文字已翻譯。

| 項目 | 契約 |
|---|---|
| 輸入與操作 | F11 新按下開啟面板；↑／↓ 移動選擇，Enter 或滑鼠點擊選項套用，Esc 或 F11 取消。持續按住不重複切換 |
| 原版輸入隔離 | 面板使用的按鍵、文字與滑鼠不送 DOS；開啟時補齊前端已送出的按鍵放開，關閉後等待實體鍵與滑鼠放開才恢復。F12 仍只切換呈現 |
| 面板生命週期 | 開啟時保留原版目前狀態，暫停 VM 推進，關閉後續跑；不建立遊戲快照、不重開 EXE、不改 seed 或遊戲速度 |
| 語言值 | `zh-Hant`、`zh-Hans`、`ja`、`ko`、`en`。初始預設繁中，之後讀使用者前端設定；`-language` 可明確覆蓋本次初值 |
| 保存 | 獨立存檔目錄下 `frontend-settings.json`，schema 1、language 字段，原子寫入；不經 DOS、不改 SAV。保存失敗保留當前語言並在面板顯示 TSV 錯誤提示 |
| 文字來源 | 外部 `-catalog` 或執行檔旁 `locales/ui.tsv` 優先；缺失／無效時回退由同一 TSV 產生的隨附 catalog，收據記錄原因。缺鍵回退同 catalog 繁中，再顯示 key。無程式譯文 literal |
| 字型與來源 | 固定 Noto／OFL 雜湊；只有既有完整城市來源與六標題閘門符合才翻譯。繁中保留 013 的字墨位置，其他語系只在原六個安全矩形內縮字置中；不能容納時回退原版標題 |
| F12 原版 | 關閉面板時直接顯示原版繁中，翻譯不覆蓋 DOS 色號或原畫面。前端面板屬新增控制介面，取消後恢復原版畫面 |
| 收據 | 記錄語言、catalog 來源／雜湊、面板狀態、保存錯誤及明示的前端輸入事件；不可把語言字串當成原版畫面識別或 SAV 名稱 |

已證實來源：六標題及原版完整頂列沿 013，F1–F6 及二十九選取沿 022；Noto 與原子 HD 輸入雜湊見下表。F11 與設定為使用者授權的新前端功能，沒有原版對應位址，不宣稱原版 parity。前端 typed 值與顯示文字鍵分開。

實作前審查已確認語系、來源、範圍與輸入隔離；剩餘未知文字不進本批規則。驗證採實際五語系字墨、缺鍵／缺字／壞 TSV／保存故障、原版 F12 像素、輸入隔離及正常 GUI 短流程。不重啟先前長時間狀態抽樣；通過前本批不升 CONFORMED。

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

## 第一批實作與驗證

本輪以 115 鍵 TSV 接入前端控制及六標題，SHA-256 `afe340850774c2b579b8808e7eac1c89dd24e4332ff978b511157fa258ab59ab`。實際字型驗證涵蓋 761 種字元。`i18n` 不匯入 DOS；`Catalog.Get` 的三類使用者僅為 HD 標題、前端面板、視窗標題。保存使用固定語言代碼，不使用譯文作比較、路徑、資源或 SAV 識別。

必要測試通過：外部文案修改不重編譯、無效 UTF-8／欄數／重複鍵／缺譯／控制字元／佔位符、設定五語系讀寫、錯格式與保存失敗、SAV 不變；五語系六標題與固定原型全部像素相同，繁中維持 013 字墨。實際 Noto／OFL 的五語系面板及兩種錯誤提示、透明區外、缺字／缺字型與授權故障均通過。

`workspace/runs/locale-ui-cold-r1/verification.json` 記錄兩次正常冷啟動。第一個 EXE 從片頭／主選單走到新城市，原版 0 暫停後以 F11 依序切換簡中、日文、韓文、英文、繁中，六標題各與固定參考完整矩形相同。面板內 CPU／步數／原畫面／色盤／原版讀鍵及檔案操作相同；五次 F12 往返、設定落地、原版 F1、滑鼠選英文通過。第二個全新 EXE 讀回英文，實際視窗標題及面板為英文，Esc 取消不寫新選擇。沒有使用 checkpoint。

本次 binary `taipei-preview-locale-r1` SHA-256 `73820b7ae8d23318e2773cb7387c0c4b71592b4b22f2ac6f54f541a0a8858938`。短流程以 stop-file 收尾，沒有原版正常退出、SAV 存退讀或長時間原版狀態抽樣。長時間持鍵／IME、錯誤提示的真實視窗流程與跨平台實機尚未驗，第一批保持 READY，不外推 CONFORMED 或完整五語系。

## 剩餘範圍

其餘已辨識功能介面改由 [032](032-interface-localization.md)／[#51](https://github.com/wicanr2/taipei/issues/51) 接續，涵蓋既有選單、說明、動態欄位，以及追加的人口、民意、速度、災難城市和固定訊息。032 的 READY 與驗證範圍優先於以下第一批歷史限制；開場敘事、插畫內文字及未知事件仍須個別來源契約。

- F11 遊戲中切換已確認；Help 的按鍵衝突另見 031。其他文字家族仍需來源及排版契約，不能由第一批 READY 外推全部翻譯完成。
- 正式驗收需涵蓋全部可切換文字鍵、實際來源覆蓋、最長字串、原數值與玩家檔名、未知來源回退，以及 F12 原版繁中不變。完整覆蓋未達成前，不關閉 #49。
- 使用者已授權語言第一批正式接入。先前「不用抽樣囉，先 commit + push」的停止點保持有效，沒有重啟 #48 圖表正常 GUI 或長時間原版狀態抽樣。
