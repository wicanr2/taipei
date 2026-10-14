// 040: offline audit of the exact unpacked package through production loaders.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/taipei/preview/internal/hd"
	"github.com/wicanr2/taipei/preview/internal/i18n"
)

func main() {
	root := flag.String("root", "", "解包根目錄")
	flag.Parse()
	read := func(name string) []byte {
		b, e := os.ReadFile(filepath.Join(*root, "original", name))
		if e != nil {
			panic(e)
		}
		return b
	}
	catalog, err := i18n.Load(filepath.Join(*root, "locales/ui.tsv"))
	if err != nil {
		panic(err)
	}
	counts, err := hd.AuditPackageResources(read("RS201.EXE"), read("RS201.ROM"), read("RS201A.ROM"), filepath.Join(*root, "materials"), catalog)
	if err != nil {
		panic(err)
	}
	data, _ := json.Marshal(counts)
	fmt.Println(string(data))
}
