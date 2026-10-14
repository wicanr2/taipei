package hd

// 037: two complete static facilities, verified through normal original GUI.
const transportFacilitiesManifestSHA = "78a955c44ab2078eb5d4b71bff534101fc0dc110cc6f4aa3edde27fe5b6dc191"

func loadTransportFacilities(rom []byte, dir string) *publicFacilitySet {
	return loadFacilityAtlases(rom, dir, "transport-ready-v1", transportFacilitiesManifestSHA, "transport", 72, 72, map[string][2]int{"airport": {6, 6}, "port": {6, 6}})
}
