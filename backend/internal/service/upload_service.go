// package service

// import (
// 	"fmt"
// 	"mime/multipart"
// 	"os"
// 	"path/filepath"
// 	"time"

// 	"voice-note-app/internal/model"
// 	"voice-note-app/internal/repository"

// 	"github.com/google/uuid"
// )

// type UploadService struct {
// 	Repo      *repository.UploadTaskRepository
// 	UploadDir string
// }

// func NewUploadService(repo *repository.UploadTaskRepository, uploadDir string) *UploadService {
// 	return &UploadService{
// 		Repo:      repo,
// 		UploadDir: uploadDir,
// 	}
// }

// func (s *UploadService) EnsureUploadDir() error {
// 	return os.MkdirAll(s.UploadDir, 0755)
// }

// func (s *UploadService) CreateTaskFromOSS(
// 	userID uint,
// 	originalName string,
// 	objectKey string,
// 	ossURL string,
// 	fileSize int64,
// ) (*model.UploadTask, error) {
// 	task := &model.UploadTask{
// 		UserID:       userID,
// 		OriginalName: originalName,
// 		FileSize:     fileSize,
// 		OSSObjectKey: objectKey,
// 		OSSURL:       ossURL,
// 		Status:       model.TaskStatusUploaded,
// 	}

// 	if err := s.Repo.Create(task); err != nil {
// 		return nil, err
// 	}

// 	return task, nil
// }

// func (s *UploadService) SaveUploadedFile(
// 	userID uint,
// 	fileHeader *multipart.FileHeader,
// 	saveFunc func(dst string) error,
// ) (*model.UploadTask, error) {
// 	ext := filepath.Ext(fileHeader.Filename)
// 	storedName := fmt.Sprintf("%d_%s%s", time.Now().Unix(), uuid.NewString(), ext)

// 	relativePath := filepath.Join(s.UploadDir, storedName)
// 	absolutePath, err := filepath.Abs(relativePath)
// 	if err != nil {
// 		return nil, err
// 	}

// 	if err := saveFunc(absolutePath); err != nil {
// 		return nil, err
// 	}

// 	task := &model.UploadTask{
// 		UserID:       userID,
// 		OriginalName: fileHeader.Filename,
// 		StoredName:   storedName,
// 		FilePath:     absolutePath,
// 		FileSize:     fileHeader.Size,
// 		Status:       model.TaskStatusUploaded,
// 	}

// 	if err := s.Repo.Create(task); err != nil {
// 		return nil, err
// 	}

// 	return task, nil
// }

// func (s *UploadService) GetTaskByID(taskID uint, userID uint) (*model.UploadTask, error) {
// 	return s.Repo.FindByIDAndUserID(taskID, userID)
// }

//	func (s *UploadService) GetTasksByUserID(userID uint) ([]model.UploadTask, error) {
//		return s.Repo.FindByUserID(userID)
//	}
package service

import (
	"errors"

	"voice-note-app/internal/model"
	"voice-note-app/internal/repository"

	"gorm.io/gorm"
)

type UploadService struct {
	Repo       *repository.UploadTaskRepository
	UploadDir  string
	OSSService *OSSService
}

func NewUploadService(
	repo *repository.UploadTaskRepository,
	uploadDir string,
	ossService *OSSService,
) *UploadService {
	return &UploadService{
		Repo:       repo,
		UploadDir:  uploadDir,
		OSSService: ossService,
	}
}

func (s *UploadService) EnsureUploadDir() error {
	return nil
}

func (s *UploadService) CreateTaskFromOSS(
	userID uint,
	originalName string,
	objectKey string,
	ossURL string,
	fileSize int64,
) (*model.UploadTask, error) {
	task := &model.UploadTask{
		UserID:       userID,
		OriginalName: originalName,
		FileSize:     fileSize,
		OSSObjectKey: objectKey,
		OSSURL:       ossURL,
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

func (s *UploadService) DeleteTask(taskID uint, userID uint) error {
	task, err := s.Repo.FindByIDAndUserID(taskID, userID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("task not found")
		}
		return err
	}

	// 可选：如果有 OSS 文件，就删除 OSS 对象
	if s.OSSService != nil && task.OSSObjectKey != "" {
		if err := s.OSSService.DeleteObject(task.OSSObjectKey); err != nil {
			return err
		}
	}

	// 删除数据库记录
	if err := s.Repo.DeleteByID(task.ID); err != nil {
		return err
	}

	return nil
}

func (s *UploadService) UpdateTaskStatus(taskID uint, status string) error {
	return s.Repo.UpdateStatus(taskID, status)
}
