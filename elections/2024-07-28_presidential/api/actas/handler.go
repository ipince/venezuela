package actas

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type Response struct {
	Cedula     string
	CenterName string
	ResultsUrl string
}

func Handler(w http.ResponseWriter, r *http.Request) {
	cedula := r.URL.Query().Get("c")
	if cedula == "" {
		http.Error(w, "missing required param 'c'", http.StatusBadRequest)
		return
	}

	resp, err := Handle(cedula)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse, err := json.Marshal(resp)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(jsonResponse)
}

func Handle(cedula string) (*Response, error) {
	info, err := Resolve(cedula)
	if err != nil {
		return nil, err
	}

	fmt.Printf("%v\n", info)
	url, err := FindUrl(info.CenterName)
	if err != nil {
		return nil, err
	}

	fmt.Printf("%s -> %s -> %s\n", cedula, info.CenterName, url)

	return &Response{
		Cedula:     cedula,
		CenterName: info.CenterName,
		ResultsUrl: url,
	}, nil
}
