package service

import (
	"fmt"
	"mime/multipart"
	"os"
	"path/filepath"
	"time"

	"voice-note-app/internal/model"
	"voice-note-app/internal/repository"

	"github.com/google/uuid"
)

type UploadService struct {
	Repo      *repository.UploadTaskRepository
	UploadDir string
}

func NewUploadService(repo *repository.UploadTaskRepository, uploadDir string) *UploadService {
	return &UploadService{
		Repo:      repo,
		UploadDir: uploadDir,
	}
}

func (s *UploadService) EnsureUploadDir() error {
	return os.MkdirAll(s.UploadDir, 0755)
}

func (s *UploadService) SaveUploadedFile(
	userID uint,
	fileHeader *multipart.FileHeader,
	saveFunc func(dst string) error,
) (*model.UploadTask, error) {
	ext := filepath.Ext(fileHeader.Filename)
	storedName := fmt.Sprintf("%d_%s%s", time.Now().Unix(), uuid.NewString(), ext)

	relativePath := filepath.Join(s.UploadDir, storedName)
	absolutePath, err := filepath.Abs(relativePath)
	if err != nil {
		return nil, err
	}

	if err := saveFunc(absolutePath); err != nil {
		return nil, err
	}

	task := &model.UploadTask{
		UserID:       userID,
		OriginalName: fileHeader.Filename,
		StoredName:   storedName,
		FilePath:     absolutePath,
		FileSize:     fileHeader.Size,
		Status:       model.TaskStatusUploaded,
	}

	if err := s.Repo.Create(task); err != nil {
		return nil, err
	}

	return task, nil
}

func (s *UploadService) GetTaskByID(taskID uint, userID uint) (*model.UploadTask, error) {
	return s.Repo.FindByIDAndUserID(taskID, userID)
}

func (s *UploadService) GetTasksByUserID(userID uint) ([]model.UploadTask, error) {
	return s.Repo.FindByUserID(userID)
}
