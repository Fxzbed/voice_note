package handler

import (
	"net/http"
	"strconv"

	"voice-note-app/internal/dto"
	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
)

type PythonTaskHandler struct {
	PythonService *service.PythonService
	UploadService *service.UploadService
}

func NewPythonTaskHandler(
	pythonService *service.PythonService,
	uploadService *service.UploadService,
) *PythonTaskHandler {
	return &PythonTaskHandler{
		PythonService: pythonService,
		UploadService: uploadService,
	}
}

type CreatePythonTaskRequest struct {
	TaskID uint `json:"task_id"`
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

	resp, err := h.PythonService.CreateTask(&dto.CreatePythonTaskRequest{
		TaskID:   uploadTask.ID,
		FilePath: uploadTask.FilePath,
		Language: nil,
	})
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, resp)
}

func (h *PythonTaskHandler) GetTask(c *gin.Context) {
	idStr := c.Param("id")
	taskID64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid task id"})
		return
	}

	resp, err := h.PythonService.GetTask(uint(taskID64))
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, resp)
}
