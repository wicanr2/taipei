# BIOS Caps Lock

狀態：CONFORMED。日期：2026-10-11。對應 [#15](https://github.com/wicanr2/taipei/issues/15)。
入口：[CONTEXT.md](../../CONTEXT.md)。適用通用 BIOS 預設 IRQ1 handler。

固定 dosgolem 基底的 `internal/dos/int9.go` 沒有 Caps Lock 狀態與字母翻譯。
前端硬體測試可重現 `round2A!` 在 Caps Lock 案例讀回 `ROUND2a!`。

公開契約：[SeaBIOS rel-1.16.3 的 kbd.c](https://raw.githubusercontent.com/coreboot/seabios/rel-1.16.3/src/kbd.c)，
Caps Lock 的狀態切換及字母 Shift 翻譯，參見 `__process_key`。
BDA 的 bit6 定義另見 [DJGPP 鍵盤狀態文件](https://www.delorie.com/djgpp/doc/libc/libc_144.html)。

- BDA `0040:0017` bit6 表示 Caps Lock 已啟用；`0040:0018` bit6 表示實體鍵按住。
- 首次 make 切換已啟用狀態，同次按住的重複 make 不切換；break 清除按住位元。
- 字母使用 Shift XOR Caps Lock；數字與標點只依 Shift。Ctrl 字母維持控制字元。
- 鎖定鍵本身不產生可讀字元。不擴充 Num Lock、延伸 E0 鍵或遊戲 IRQ driver。
- 狀態保存在原有 BDA 記憶體，沿用既有狀態保存契約，不新增檔案格式。

驗證：直接 handler 的鎖定切換及大小寫／數字／標點；前端經硬體 IRQ1 到 BIOS 的
完整字元序列與修飾狀態恢復；原有 DOS、machine 與公開介面測試。

結果：固定隔離副本提交 `fcf43b1`，`go test -p 1 ./internal/dos ./internal/machine .`
與前端硬體測試通過。重複 make、break、Shift XOR Caps、數字標點與 Ctrl 字母均有抽測。
補丁為 `workspace/tools/dosgolem-bios-caps-lock.patch`，SHA-256
`7413a0938078afefb69284c2a538f1443e5b58049786d11e91260231270a2d76`。
它是第五份通用補丁，只在本專案保存，不修改上游工作樹。
