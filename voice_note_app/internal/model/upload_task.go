package model

import "time"

const (
	TaskStatusUploaded       = "uploaded"        // 上传成功，未开始 ASR
	TaskStatusASRProcessing  = "asr_processing"  // ASR 中
	TaskStatusASRDone        = "asr_done"        // ASR 完成，未生成笔记
	TaskStatusASRFailed      = "asr_failed"      // ASR 失败
	TaskStatusNoteGenerating = "note_generating" // 笔记生成中
	TaskStatusNoteDone       = "note_done"       // 笔记生成完成
	TaskStatusNoteFailed     = "note_failed"     // 笔记生成失败
	TaskStatusUploadFailed   = "upload_failed"   // 文件上传失败
)

type UploadTask struct {
	ID           uint   `gorm:"primaryKey"`
	UserID       uint   `gorm:"not null;index"`
	OriginalName string `gorm:"type:varchar(255);not null"`
	StoredName   string `gorm:"type:varchar(255);not null"`
	FilePath     string `gorm:"type:varchar(500);not null"`
	FileSize     int64  `gorm:"not null"`
	Status       string `gorm:"type:varchar(50);not null;default:'uploaded';index"`
	ErrorMessage string `gorm:"type:text"`
	CreatedAt    time.Time
	UpdatedAt    time.Time
}

func GetTaskStatusText(status string) string {
	switch status {
	case TaskStatusUploaded:
		return "上传成功，未开始 ASR"
	case TaskStatusASRProcessing:
		return "ASR 中"
	case TaskStatusASRDone:
		return "ASR 完成，未生成笔记"
	case TaskStatusASRFailed:
		return "ASR 失败"
	case TaskStatusNoteGenerating:
		return "笔记生成中"
	case TaskStatusNoteDone:
		return "笔记生成完成"
	case TaskStatusNoteFailed:
		return "笔记生成失败"
	case TaskStatusUploadFailed:
		return "文件上传失败"
	default:
		return "未知状态"
	}
}
