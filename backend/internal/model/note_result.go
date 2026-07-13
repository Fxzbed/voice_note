package model

import "time"

type NoteResult struct {
	TaskID uint `gorm:"primaryKey;column:task_id"`

	JsonResult string `gorm:"type:longtext"`

	CreatedAt time.Time
	UpdatedAt time.Time
}

func (NoteResult) TableName() string {
	return "note_results"
}
