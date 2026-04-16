package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
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

func (s *PythonService) CreateTask(reqBody *dto.CreatePythonTaskRequest) (*dto.CreatePythonTaskResponse, error) {
	url := fmt.Sprintf("%s/tasks", s.BaseURL)

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest(http.MethodPost, url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		raw, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("python create task failed: status=%d body=%s", resp.StatusCode, string(raw))
	}

	var result dto.CreatePythonTaskResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func (s *PythonService) GetTask(taskID uint) (*dto.PythonTaskResponse, error) {
	url := fmt.Sprintf("%s/tasks/%d", s.BaseURL, taskID)

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
		raw, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("python get task failed: status=%d body=%s", resp.StatusCode, string(raw))
	}

	var result dto.PythonTaskResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}
