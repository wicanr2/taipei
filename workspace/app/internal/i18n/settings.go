package i18n

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type settings struct {
	Schema   int    `json:"schema"`
	Language string `json:"language"`
}

func ReadSettings(path string) (string, error) {
	raw, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return Default, nil
	}
	if err != nil {
		return Default, err
	}
	var s settings
	if err = json.Unmarshal(raw, &s); err != nil {
		return Default, err
	}
	if s.Schema != 1 || Index(s.Language) < 0 {
		return Default, fmt.Errorf("settings-format")
	}
	return s.Language, nil
}

func SaveSettings(path, language string) error {
	if Index(language) < 0 {
		return fmt.Errorf("settings-language")
	}
	raw, err := json.MarshalIndent(settings{1, language}, "", "  ")
	if err != nil {
		return err
	}
	f, err := os.CreateTemp(filepath.Dir(path), ".frontend-settings-*")
	if err != nil {
		return err
	}
	defer os.Remove(f.Name())
	if _, err = f.Write(append(raw, '\n')); err != nil {
		f.Close()
		return err
	}
	if err = f.Close(); err != nil {
		return err
	}
	return os.Rename(f.Name(), path)
}
