package handler

import (
	"net/http"
	"strconv"

	"voice-note-app/internal/model"
	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
)

type UploadHandler struct {
	UploadService *service.UploadService
}

func NewUploadHandler(uploadService *service.UploadService) *UploadHandler {
	return &UploadHandler{
		UploadService: uploadService,
	}
}

func (h *UploadHandler) UploadAudio(c *gin.Context) {
	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in token"})
		return
	}
	userID := userIDValue.(uint)

	fileHeader, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "file is required"})
		return
	}

	if fileHeader.Size == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "empty file"})
		return
	}

	task, err := h.UploadService.SaveUploadedFile(userID, fileHeader, func(dst string) error {
		return c.SaveUploadedFile(fileHeader, dst)
	})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "save file failed"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":     "upload success",
		"task_id":     task.ID,
		"status":      task.Status,
		"file_name":   task.OriginalName,
		"file_path":   task.FilePath,
		"stored_name": task.StoredName,
	})
}

func (h *UploadHandler) GetTaskStatus(c *gin.Context) {
	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in token"})
		return
	}
	userID := userIDValue.(uint)

	idStr := c.Param("id")
	taskID64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid task id"})
		return
	}

	task, err := h.UploadService.GetTaskByID(uint(taskID64), userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "task not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"id":            task.ID,
		"original_name": task.OriginalName,
		"file_size":     task.FileSize,
		"status":        task.Status,
		"status_text":   model.GetTaskStatusText(task.Status),
		"error_message": task.ErrorMessage,
		"created_at":    task.CreatedAt,
	})
}

func (h *UploadHandler) ListMyTasks(c *gin.Context) {
	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in token"})
		return
	}
	userID := userIDValue.(uint)

	tasks, err := h.UploadService.GetTasksByUserID(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "query tasks failed"})
		return
	}

	result := make([]gin.H, 0, len(tasks))
	for _, task := range tasks {
		result = append(result, gin.H{
			"id":            task.ID,
			"original_name": task.OriginalName,
			"file_size":     task.FileSize,
			"status":        task.Status,
			"status_text":   model.GetTaskStatusText(task.Status),
			"error_message": task.ErrorMessage,
			"created_at":    task.CreatedAt,
			"updated_at":    task.UpdatedAt,
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"tasks": result,
	})
}
