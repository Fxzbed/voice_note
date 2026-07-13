package handler

import (
	"encoding/json"
	"net/http"
	"strconv"

	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
)

type NoteResultHandler struct {
	NoteResultService *service.NoteResultService
	UploadService     *service.UploadService
}

func NewNoteResultHandler(
	noteResultService *service.NoteResultService,
	uploadService *service.UploadService,
) *NoteResultHandler {
	return &NoteResultHandler{
		NoteResultService: noteResultService,
		UploadService:     uploadService,
	}
}

func (h *NoteResultHandler) GetByTaskID(c *gin.Context) {
	idStr := c.Param("task_id")
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

	result, err := h.NoteResultService.GetByTaskID(taskID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "note result not found"})
		return
	}

	var parsed map[string]any
	if err := json.Unmarshal([]byte(result.JsonResult), &parsed); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to parse note result"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"task_id": taskID,
		"note":    parsed,
	})
}
