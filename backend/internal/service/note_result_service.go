package service

import (
	"encoding/json"

	"voice-note-app/internal/model"
	"voice-note-app/internal/repository"
)

type NoteResultService struct {
	Repo *repository.NoteResultRepository
}

func NewNoteResultService(repo *repository.NoteResultRepository) *NoteResultService {
	return &NoteResultService{
		Repo: repo,
	}
}

func (s *NoteResultService) SaveTaskResult(taskID uint, data map[string]any) error {
	raw, err := json.Marshal(data)
	if err != nil {
		return err
	}

	result := &model.NoteResult{
		TaskID:     taskID,
		JsonResult: string(raw),
	}

	return s.Repo.Upsert(result)
}

func (s *NoteResultService) GetByTaskID(taskID uint) (*model.NoteResult, error) {
	return s.Repo.FindByTaskID(taskID)
}

func (s *NoteResultService) DeleteByTaskID(taskID uint) error {
	return s.Repo.DeleteByTaskID(taskID)
}
