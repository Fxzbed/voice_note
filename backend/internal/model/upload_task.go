package model

import "time"

const (
	TaskStatusUploaded  = "uploaded"
	TaskStatusSubmitted = "submitted"

	TaskStatusDownloadProcessing = "download_processing"
	TaskStatusDownloadDone       = "download_done"
	TaskStatusDownloadFailed     = "download_failed"

	TaskStatusVADProcessing = "vad_processing"
	TaskStatusVADDone       = "vad_done"
	TaskStatusVADFailed     = "vad_failed"

	TaskStatusASRProcessing = "asr_processing"
	TaskStatusASRDone       = "asr_done"
	TaskStatusASRFailed     = "asr_failed"

	TaskStatusNoteGenerating = "note_generating"
	TaskStatusNoteDone       = "note_done"
	TaskStatusNoteFailed     = "note_failed"
)

type UploadTask struct {
	ID           uint   `gorm:"primaryKey"`
	UserID       uint   `gorm:"not null;index"`
	OriginalName string `gorm:"size:255;not null"`
	StoredName   string `gorm:"size:255"`
	FilePath     string `gorm:"size:500"`
	FileSize     int64  `gorm:"not null"`

	OSSObjectKey string `gorm:"size:500"`
	OSSURL       string `gorm:"size:1000"`

	Status    string `gorm:"size:50;not null"`
	CreatedAt time.Time
	UpdatedAt time.Time
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
	case TaskStatusDownloadFailed:
		return "文件上传失败"
	default:
		return "未知状态"
	}
}
