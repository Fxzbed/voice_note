package repository

import (
	"errors"

	"voice-note-app/internal/model"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

type NoteResultRepository struct {
	DB *gorm.DB
}

func NewNoteResultRepository(db *gorm.DB) *NoteResultRepository {
	return &NoteResultRepository{
		DB: db,
	}
}

func (r *NoteResultRepository) FindByTaskID(taskID uint) (*model.NoteResult, error) {
	var result model.NoteResult
	err := r.DB.Where("task_id = ?", taskID).First(&result).Error
	if err != nil {
		return nil, err
	}
	return &result, nil
}

func (r *NoteResultRepository) Upsert(result *model.NoteResult) error {
	return r.DB.Clauses(clause.OnConflict{
		Columns:   []clause.Column{{Name: "task_id"}},
		DoUpdates: clause.AssignmentColumns([]string{"json_result", "updated_at"}),
	}).Create(result).Error
}

func (r *NoteResultRepository) DeleteByTaskID(taskID uint) error {
	return r.DB.Where("task_id = ?", taskID).Delete(&model.NoteResult{}).Error
}

func (r *NoteResultRepository) Exists(taskID uint) (bool, error) {
	var count int64
	err := r.DB.Model(&model.NoteResult{}).Where("task_id = ?", taskID).Count(&count).Error
	return count > 0, err
}

func (r *NoteResultRepository) IsNotFound(err error) bool {
	return errors.Is(err, gorm.ErrRecordNotFound)
}
