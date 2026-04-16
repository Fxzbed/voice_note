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
}

func NewPythonTaskHandler(pythonService *service.PythonService) *PythonTaskHandler {
	return &PythonTaskHandler{
		PythonService: pythonService,
	}
}

type CreateTaskRequest struct {
	TaskID   uint    `json:"task_id"`
	FilePath string  `json:"file_path"`
	Language *string `json:"language"`
}

func (h *PythonTaskHandler) CreateTask(c *gin.Context) {
	var req CreateTaskRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := h.PythonService.CreateTask(&dto.CreatePythonTaskRequest{
		TaskID:   req.TaskID,
		FilePath: req.FilePath,
		Language: req.Language,
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
