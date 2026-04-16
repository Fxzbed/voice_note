package dto

type PythonHealthResponse struct {
	Status string `json:"status"`
}

type PythonTranscribeResponse struct {
	Text     string `json:"text"`
	Markdown string `json:"markdown"`
}
