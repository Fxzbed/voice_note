package httpclient

import (
	"net/http"
	"time"
)

func NewClient() *http.Client {
	return &http.Client{
		Timeout: 60 * time.Second,
	}
}
