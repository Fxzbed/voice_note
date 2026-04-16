package repository

import (
	"voice-note-app/internal/model"

	"gorm.io/gorm"
)

type UploadTaskRepository struct {
	DB *gorm.DB
}

func NewUploadTaskRepository(db *gorm.DB) *UploadTaskRepository {
	return &UploadTaskRepository{DB: db}
}

func (r *UploadTaskRepository) Create(task *model.UploadTask) error {
	return r.DB.Create(task).Error
}

func (r *UploadTaskRepository) FindByID(id uint) (*model.UploadTask, error) {
	var task model.UploadTask
	err := r.DB.First(&task, id).Error
	return &task, err
}

func (r *UploadTaskRepository) FindByIDAndUserID(id uint, userID uint) (*model.UploadTask, error) {
	var task model.UploadTask
	err := r.DB.Where("id = ? AND user_id = ?", id, userID).First(&task).Error
	return &task, err
}

func (r *UploadTaskRepository) FindByUserID(userID uint) ([]model.UploadTask, error) {
	var tasks []model.UploadTask
	err := r.DB.
		Where("user_id = ?", userID).
		Order("created_at DESC").
		Find(&tasks).Error
	return tasks, err
}

func (r *UploadTaskRepository) UpdateStatus(id uint, status string, errMsg string) error {
	return r.DB.Model(&model.UploadTask{}).
		Where("id = ?", id).
		Updates(map[string]interface{}{
			"status":        status,
			"error_message": errMsg,
		}).Error
}
