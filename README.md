# 模擬台北：dosgolem 與 HD 呈現

本專案以 dosgolem 執行使用者自備的原版《模擬台北》，接入現代前端與 HD 呈現。
目前已驗證原版冷啟動、電線施工、存檔、退出及全新啟動讀檔，並擷取到實際播放器音訊。
HD 採 B 細緻手繪材質、1280×800 與 Noto 高清黑體，遊戲中以 F12 切換。重繪範圍包含所有圖片與操作介面；目前已接入地景原型、第一批 25 張道路與電線、火力電廠 36 格靜態圖塊、城市框架、六個 Noto 標題與 F1–F6、六功能下拉選單、十四個工具及選取外框、五種工具子選單、新遊戲說明、主選單、城市與難度選擇、存讀檔視窗與離開提示、預算與稅率面板，以及底部費用、年月與資金文字。完整 HD 與三平台封包仍在製作，尚無正式交付包。驗證範圍見 [CONTEXT.md](CONTEXT.md)。

玩家須自備合法取得的原版資料。原版執行檔、資料、美術、音訊與權利未明的 HD 素材
只留本機，不加入此儲存庫或公開封包。

工作區使用 `workspace/`。遊戲專屬探針與可重現工具放在其下；
研究輸出、工具快取、原版資料與 dosgolem 隔離副本排除於 Git。

| 入口 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | 範圍、授權、工作流程與外部知識入口 |
| [CONTEXT.md](CONTEXT.md) | 目前真相、有效決策與限制 |
| [GitHub Issues](https://github.com/wicanr2/taipei/issues) | 唯一工作項目與進度來源 |
| [驗收矩陣](docs/verification-matrix.md) | 玩家路徑、證據與完成邊界 |
| [WORKLOG.md](WORKLOG.md) | 按時間追加的工作歷程 |

探針入口為 [workspace/tools/probe.sh](workspace/tools/probe.sh)，只在 Docker 內建置與執行。
固定版本、原始資料路徑與重播方法見[啟動基線](docs/re/002-dosgolem-startup.md)。
前端建置與正常 GUI 測試入口見[前端契約](docs/spec/005-frontend-preview.md)。

自有程式及文件使用 [RRSAL-1.0](LICENSE)，
不把原版素材或第三方依賴納入自有授權。本專案與原版權利人無隸屬關係。
OPL2 合成使用 [YMFM](https://github.com/aaronsgiles/ymfm) 的 BSD 3-Clause 核心，固定來源與驗證範圍見[音訊契約](docs/spec/009-opl2-audio.md)。
