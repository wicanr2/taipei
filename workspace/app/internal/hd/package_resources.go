package hd

import (
	"fmt"

	"github.com/wicanr2/taipei/preview/internal/i18n"
)

// AuditPackageResources uses the real loaders, including their fixed seals.
// It is an offline packaging check and never creates a DOS machine.
func AuditPackageResources(exe, rom, romA []byte, dir string, catalog *i18n.Catalog) (map[string]int, error) {
	r := New(rom, dir)
	if r.reason != "" {
		return nil, fmt.Errorf("base: %s", r.reason)
	}
	if r.menu.reason != "matched-menu" || r.icons.reason != "matched-icons" || r.dialog.reason != "matched-dialog" || len(r.shades) != 13 || !r.chrome.fontOK || r.chrome.frame == nil || r.chrome.rings == nil || !r.footer.ready {
		return nil, fmt.Errorf("base resources: menu=%s icons=%s dialog=%s shades=%d chrome=%t footer=%t", r.menu.reason, r.icons.reason, r.dialog.reason, len(r.shades), r.chrome.fontOK, r.footer.ready)
	}
	counts := map[string]int{"material_shades": len(r.shades)}
	for name, set := range map[string]*panelSet{"startup": r.panels, "tools": r.toolPanels, "city_menus": r.cityPanels} {
		if set.reason != "scene-fallback" {
			return nil, fmt.Errorf("%s: %s", name, set.reason)
		}
		for _, state := range set.states {
			if state.reason != "matched-panel" || state.image == nil {
				return nil, fmt.Errorf("%s: %s", name, state.reason)
			}
		}
		counts[name] = len(set.states)
	}
	if r.files.reason != "scene-fallback" || r.budget.reason != "scene-fallback" || r.ending.reason != "" || r.charts.reason != "" || r.powerFacility.reason != "" || r.powerFacility.atlas == nil || r.civicFacilities.reason != "" || r.cityBuildings.reason != "" {
		return nil, fmt.Errorf("panels: files=%s budget=%s ending=%s charts=%s power=%s civic=%s buildings=%s", r.files.reason, r.budget.reason, r.ending.reason, r.charts.reason, r.powerFacility.reason, r.civicFacilities.reason, r.cityBuildings.reason)
	}
	for name, set := range map[string]*publicFacilitySet{"nuclear": r.nuclearFacility, "transport": r.transportFacilities, "public": r.publicFacilities, "map_complex": r.mapComplex, "map_zones_base": r.mapZonesBase} {
		if set.reason != "" || len(set.atlases) == 0 || len(set.tiles) == 0 {
			return nil, fmt.Errorf("%s: %s", name, set.reason)
		}
		for _, atlas := range set.atlases {
			if atlas == nil {
				return nil, fmt.Errorf("%s: missing atlas", name)
			}
		}
		counts[name] = len(set.tiles)
	}
	for name, set := range map[string]*infrastructureSet{"infrastructure": r.infrastructure, "map_detail": r.mapDetail} {
		if len(set.tiles) == 0 || len(set.textures) == 0 {
			return nil, fmt.Errorf("%s: missing data", name)
		}
		for _, tile := range set.tiles {
			if tile.reason != "" || len(tile.indices) == 0 || len(tile.weights) == 0 {
				return nil, fmt.Errorf("%s: %s", name, tile.reason)
			}
		}
		counts[name] = len(set.tiles)
	}
	if len(r.InitTextSources(exe, rom, romA)) != 9 || len(r.InitIllustrations(exe, rom, romA, dir)) != 209 || r.illustrations.reason != "" {
		return nil, fmt.Errorf("illustration or text sources")
	}
	for id, asset := range r.illustrations.assets {
		for _, variant := range asset.variants {
			if variant.art == nil {
				return nil, fmt.Errorf("illustration %s/%s", id, variant.Palette)
			}
		}
	}
	counts["illustrations"] = len(r.illustrations.assets)
	if err := ValidateInterfaceCatalog(catalog); err != nil {
		return nil, err
	}
	for _, lang := range i18n.Languages {
		r.SetLanguage(catalog, lang)
		if r.locale.reason != "" || r.mapZones.reason != "" {
			return nil, fmt.Errorf("locale %s: %s / %s", lang, r.locale.reason, r.mapZones.reason)
		}
	}
	counts["languages"] = len(i18n.Languages)
	return counts, nil
}
