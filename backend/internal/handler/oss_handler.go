package handler

import (
	"net/http"

	"voice-note-app/internal/dto"
	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
)

type OSSHandler struct {
	OSSService    *service.OSSService
	UploadService *service.UploadService
}

func NewOSSHandler(ossService *service.OSSService, uploadService *service.UploadService) *OSSHandler {
	return &OSSHandler{
		OSSService:    ossService,
		UploadService: uploadService,
	}
}

type GetSTSRequest struct {
	OriginalName string `json:"original_name"`
}

func (h *OSSHandler) GetSTS(c *gin.Context) {
	var req GetSTSRequest
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

	resp, err := h.OSSService.GetSTSForUpload(userID, req.OriginalName)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, resp)
}

func (h *OSSHandler) CompleteUpload(c *gin.Context) {
	var req dto.CompleteUploadRequest
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

	task, err := h.UploadService.CreateTaskFromOSS(
		userID,
		req.OriginalName,
		req.ObjectKey,
		req.OSSURL,
		req.FileSize,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, dto.CompleteUploadResponse{
		Message:   "upload success",
		TaskID:    task.ID,
		Status:    task.Status,
		FileName:  task.OriginalName,
		ObjectKey: task.OSSObjectKey,
		OSSURL:    task.OSSURL,
	})
}
