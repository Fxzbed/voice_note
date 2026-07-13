package handler

import (
	"net/http"
	"strconv"

	"voice-note-app/internal/model"
	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type NoteHandler struct {
	DB            *gorm.DB
	UploadService *service.UploadService
}

func NewNoteHandler(db *gorm.DB, uploadService *service.UploadService) *NoteHandler {
	return &NoteHandler{
		DB:            db,
		UploadService: uploadService,
	}
}

func (h *NoteHandler) GetNoteByTaskID(c *gin.Context) {
	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "user not found in token",
		})
		return
	}

	userID, ok := userIDValue.(uint)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "invalid user id",
		})
		return
	}

	taskIDStr := c.Param("task_id")
	taskID64, err := strconv.ParseUint(taskIDStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "invalid task_id",
		})
		return
	}

	taskID := uint(taskID64)

	// 先校验这个 task_id 是否属于当前用户
	_, err = h.UploadService.GetTaskByID(taskID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "task not found",
		})
		return
	}

	// 再查 note_results
	var note model.NoteResult
	if err := h.DB.
		Where("task_id = ?", taskID).
		First(&note).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "note result not found",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"task_id":     note.TaskID,
		"json_result": note.JsonResult,
		"created_at":  note.CreatedAt,
		"updated_at":  note.UpdatedAt,
	})
}
