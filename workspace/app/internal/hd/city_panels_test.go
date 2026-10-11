package hd

import "testing"

func TestActualCityPanels(t *testing.T) {
	testActualFixedPanels(t, "TAIPEI_CITY_PANEL_RECEIPTS", "city-menus-v1", 29, "city-f1", "city-f5", loadCityPanels, func(r *Renderer) **panelSet { return &r.cityPanels })
}
