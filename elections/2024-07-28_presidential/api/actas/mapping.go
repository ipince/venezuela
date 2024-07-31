package actas

import (
	_ "embed"
	"encoding/json"

	"github.com/pkg/errors"
)

//go:embed estructura_completa.json
var structure []byte
var urlmap = map[string]string{}

func init() {
	sitemap := map[string]map[string]map[string]interface{}{}
	err := json.Unmarshal(structure, &sitemap)
	if err != nil {
		panic(err)
	}
	for _, muns := range sitemap {
		for mun, data := range muns {
			urlmap[mun] = data["url"].(string)
			parishes := data["parroquias"].(map[string]interface{})
			for parish, data2 := range parishes {
				urlmap[parish] = data2.(map[string]interface{})["url"].(string)
				centers := data2.(map[string]interface{})["centros"].(map[string]interface{})
				for center, url := range centers {
					urlmap[center] = url.(string)
				}
			}
		}
	}
}

func FindUrl(centerName string) (string, error) {
	if url, ok := urlmap[centerName]; ok {
		return url, nil
	} else {
		return "", errors.Errorf("no url found for %s", centerName)
	}
}
