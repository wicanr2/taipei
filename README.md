# 模擬台北：dosgolem 與 HD 呈現

本專案以 dosgolem 執行使用者自備的原版《模擬台北》，接入現代前端與 HD 呈現。
目前已驗證原版冷啟動、主選單與城市選擇。前端、存讀檔及 HD 仍待驗證，尚無可交付遊戲封包。

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

自有程式及文件使用 [RRSAL-1.0](LICENSE)，
不把原版素材或第三方依賴納入自有授權。本專案與原版權利人無隸屬關係。
