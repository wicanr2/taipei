package hd

// 027: complete static nuclear plant observed through the normal DISA1 route.
const nuclearFacilityManifestSHA = "05b13ecfc0979b8b4f26e004b195d6068c8202c67cb3ef9ae2836ab9f5cda73a"

func loadNuclearFacility(rom []byte, dir string) *publicFacilitySet {
	return loadFacilityAtlases(rom, dir, "nuclear-ready-v1", nuclearFacilityManifestSHA, "nuclear", 36, 35, map[string][2]int{"nuclear": {6, 6}})
}
