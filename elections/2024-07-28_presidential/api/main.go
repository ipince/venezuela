package main

import (
	"api/actas"
	"net/http"
)

func main() {
	runServer()
}

func runServer() {
	http.HandleFunc("/api/actas", actas.Handler)
	http.ListenAndServe(":8080", nil)
}
