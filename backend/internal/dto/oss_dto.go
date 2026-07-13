package dto

type GetOSSSTSResponse struct {
	AccessKeyID     string `json:"accessKeyId"`
	AccessKeySecret string `json:"accessKeySecret"`
	SecurityToken   string `json:"securityToken"`
	Expiration      string `json:"expiration"`

	Region    string `json:"region"`
	Bucket    string `json:"bucket"`
	Endpoint  string `json:"endpoint"`
	BaseURL   string `json:"baseUrl"`
	ObjectKey string `json:"objectKey"`
}

type CompleteUploadRequest struct {
	OriginalName string `json:"original_name"`
	ObjectKey    string `json:"object_key"`
	OSSURL       string `json:"oss_url"`
	FileSize     int64  `json:"file_size"`
}

type CompleteUploadResponse struct {
	Message   string `json:"message"`
	TaskID    uint   `json:"task_id"`
	Status    string `json:"status"`
	FileName  string `json:"file_name"`
	ObjectKey string `json:"object_key"`
	OSSURL    string `json:"oss_url"`
}
