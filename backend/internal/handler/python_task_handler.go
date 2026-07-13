// package handler

// import (
// 	"net/http"
// 	"strconv"

// 	"voice-note-app/internal/dto"
// 	"voice-note-app/internal/model"
// 	"voice-note-app/internal/service"

// 	"github.com/gin-gonic/gin"
// )

// type PythonTaskHandler struct {
// 	PythonService *service.PythonService
// 	UploadService *service.UploadService
// }

// func NewPythonTaskHandler(
// 	pythonService *service.PythonService,
// 	uploadService *service.UploadService,
// ) *PythonTaskHandler {
// 	return &PythonTaskHandler{
// 		PythonService: pythonService,
// 		UploadService: uploadService,
// 	}
// }

// type CreatePythonTaskRequest struct {
// 	TaskID   uint    `json:"task_id"`
// 	Language *string `json:"language,omitempty"`
// }

// func (h *PythonTaskHandler) CreateTask(c *gin.Context) {
// 	var req CreatePythonTaskRequest

// 	if err := c.ShouldBindJSON(&req); err != nil {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
// 		return
// 	}

// 	userIDValue, exists := c.Get("user_id")
// 	if !exists {
// 		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in token"})
// 		return
// 	}
// 	userID := userIDValue.(uint)

// 	uploadTask, err := h.UploadService.GetTaskByID(req.TaskID, userID)
// 	if err != nil {
// 		c.JSON(http.StatusNotFound, gin.H{"error": "task not found"})
// 		return
// 	}

// 	if uploadTask.OSSObjectKey == "" {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": "task has no oss object key"})
// 		return
// 	}

// 	resp, err := h.PythonService.CreateTask(&dto.CreatePythonTaskRequest{
// 		TaskID:       uploadTask.ID,
// 		OriginalName: uploadTask.OriginalName,
// 		OSSObjectKey: uploadTask.OSSObjectKey,
// 		Language:     req.Language,
// 	})
// 	if err != nil {
// 		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
// 		return
// 	}

// 	// Python 接收任务成功后，立即更新数据库状态
// 	if err := h.UploadService.UpdateTaskStatus(uploadTask.ID, model.TaskStatusASRProcessing); err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{
// 			"error": "python task created, but failed to update db status: " + err.Error(),
// 		})
// 		return
// 	}

// 	c.JSON(http.StatusOK, gin.H{
// 		"message": "python task created successfully",
// 		"python":  resp,
// 		"task_id": uploadTask.ID,
// 		"status":  model.TaskStatusASRProcessing,
// 	})
// }

// func (h *PythonTaskHandler) GetTask(c *gin.Context) {
// 	idStr := c.Param("id")
// 	taskID64, err := strconv.ParseUint(idStr, 10, 64)
// 	if err != nil {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid task id"})
// 		return
// 	}

// 	resp, err := h.PythonService.GetTask(uint(taskID64))
// 	if err != nil {
// 		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
// 		return
// 	}

//		c.JSON(http.StatusOK, resp)
//	}
package handler

import (
	"net/http"
	"strconv"

	"voice-note-app/internal/dto"
	"voice-note-app/internal/model"
	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
)

type PythonTaskHandler struct {
	PythonService     *service.PythonService
	UploadService     *service.UploadService
	NoteResultService *service.NoteResultService
}

func NewPythonTaskHandler(
	pythonService *service.PythonService,
	uploadService *service.UploadService,
	noteResultService *service.NoteResultService,
) *PythonTaskHandler {
	return &PythonTaskHandler{
		PythonService:     pythonService,
		UploadService:     uploadService,
		NoteResultService: noteResultService,
	}
}

type CreatePythonTaskRequest struct {
	TaskID   uint    `json:"task_id"`
	Language *string `json:"language,omitempty"`
}

func (h *PythonTaskHandler) CreateTask(c *gin.Context) {
	var req CreatePythonTaskRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in token"})
		return
	}
	userID := userIDValue.(uint)

	uploadTask, err := h.UploadService.GetTaskByID(req.TaskID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "task not found"})
		return
	}

	if uploadTask.OSSObjectKey == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "task has no oss object key"})
		return
	}

	resp, err := h.PythonService.CreateTask(&dto.CreatePythonTaskRequest{
		TaskID:       uploadTask.ID,
		OriginalName: uploadTask.OriginalName,
		OSSObjectKey: uploadTask.OSSObjectKey,
		Language:     req.Language,
	})
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}

	// 提交成功后，先更新数据库状态
	if err := h.UploadService.UpdateTaskStatus(uploadTask.ID, model.TaskStatusSubmitted); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "python task created, but failed to update db status: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "python task created successfully",
		"python":  resp,
		"task_id": uploadTask.ID,
		"status":  model.TaskStatusSubmitted,
	})
}

func (h *PythonTaskHandler) GetTask(c *gin.Context) {
	idStr := c.Param("id")
	taskID64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid task id"})
		return
	}
	taskID := uint(taskID64)

	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in token"})
		return
	}
	userID := userIDValue.(uint)

	_, err = h.UploadService.GetTaskByID(taskID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "task not found"})
		return
	}

	resp, err := h.PythonService.GetTask(taskID)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}

	// 同步 Python 当前状态到 MySQL
	if err := h.UploadService.UpdateTaskStatus(taskID, resp.Status); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "python task fetched, but failed to sync db status: " + err.Error(),
		})
		return
	}

	// 如果任务已经完成，并且拿到了结构化结果，则保存到结果表
	if resp.Status == model.TaskStatusNoteDone &&
		h.NoteResultService != nil &&
		resp.StructuredNoteJSON != nil {
		if err := h.NoteResultService.SaveTaskResult(taskID, resp.StructuredNoteJSON); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "python task fetched, but failed to save note result: " + err.Error(),
			})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "python task fetched successfully",
		"task_id": taskID,
		"status":  resp.Status,
		"data":    resp,
	})
}
