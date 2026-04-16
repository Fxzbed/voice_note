package handler

import (
	"net/http"

	"voice-note-app/internal/service"

	"github.com/gin-gonic/gin"
)

type HealthHandler struct {
	PythonService *service.PythonService
}

func NewHealthHandler(pythonService *service.PythonService) *HealthHandler {
	return &HealthHandler{
		PythonService: pythonService,
	}
}

func (h *HealthHandler) AppHealth(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "go service is running",
	})
}

func (h *HealthHandler) PythonHealth(c *gin.Context) {
	resp, err := h.PythonService.HealthCheck()
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{
			"error": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"python_status": resp.Status,
	})
}
