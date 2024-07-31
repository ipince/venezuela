package actas

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ResponseErr struct {
	Error string
}

func Handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	cedula := r.URL.Query().Get("cedula")
	if cedula == "" {
		writeErr(w, "missing required param 'cedula'", http.StatusBadRequest)
		return
	}

	info, err := Handle(cedula)
	if err != nil {
		writeErr(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse, err := json.Marshal(info)
	if err != nil {
		writeErr(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write(jsonResponse)
}

func writeErr(w http.ResponseWriter, msg string, code int) {
	resp, _ := json.Marshal(ResponseErr{Error: msg})
	w.WriteHeader(code)
	w.Write(resp)
}

func Handle(cedula string) (*CedulaInfo, error) {
	info, err := Resolve(cedula)
	if err != nil {
		return nil, err
	}

	fmt.Printf("%v\n", info)
	url, err := FindUrl(info.CenterName)
	if err != nil {
		return nil, err
	}
	info.ResultsURL = url

	fmt.Printf("%s -> %s -> %s\n", cedula, info.CenterName, url)

	return info, nil
}
