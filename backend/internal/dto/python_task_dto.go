package dto

type CreatePythonTaskRequest struct {
	TaskID   uint    `json:"task_id"`
	FilePath string  `json:"file_path"`
	Language *string `json:"language,omitempty"`
}

type CreatePythonTaskResponse struct {
	TaskID   uint    `json:"task_id"`
	Status   string  `json:"status"`
	FilePath string  `json:"file_path"`
	Language *string `json:"language,omitempty"`
}

type PythonTaskResponse struct {
	TaskID         uint    `json:"task_id"`
	FilePath       string  `json:"file_path"`
	Language       *string `json:"language,omitempty"`
	Status         string  `json:"status"`
	ErrorMessage   *string `json:"error_message,omitempty"`
	SegmentDir     *string `json:"segment_dir,omitempty"`
	SegmentCount   int     `json:"segment_count"`
	ResultText     *string `json:"result_text,omitempty"`
	ResultTextFile *string `json:"result_text_file,omitempty"`
	CreatedAt      float64 `json:"created_at"`
	UpdatedAt      float64 `json:"updated_at"`
}
