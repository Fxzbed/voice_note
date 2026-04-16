package service

import (
	"encoding/json"
	"fmt"
	"net/http"

	"voice-note-app/internal/dto"
)

type PythonService struct {
	BaseURL string
	Client  *http.Client
}

func NewPythonService(baseURL string, client *http.Client) *PythonService {
	return &PythonService{
		BaseURL: baseURL,
		Client:  client,
	}
}

func (s *PythonService) HealthCheck() (*dto.PythonHealthResponse, error) {
	url := fmt.Sprintf("%s/health", s.BaseURL)

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}

	resp, err := s.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("python service returned status: %d", resp.StatusCode)
	}

	var result dto.PythonHealthResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}
