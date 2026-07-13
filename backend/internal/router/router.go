package router

import (
	"voice-note-app/internal/handler"
	"voice-note-app/internal/middleware"

	"github.com/gin-gonic/gin"
)

func SetupRouter(
	authHandler *handler.AuthHandler,
	healthHandler *handler.HealthHandler,
	uploadHandler *handler.UploadHandler,
	pythonTaskHandler *handler.PythonTaskHandler,
	ossHandler *handler.OSSHandler,
	noteResultHandler *handler.NoteResultHandler,
	jwtSecret string,
) *gin.Engine {
	r := gin.Default()

	api := r.Group("/api")
	{
		api.POST("/register", authHandler.Register)
		api.POST("/login", authHandler.Login)

		api.GET("/health", healthHandler.AppHealth)
		api.GET("/python/health", healthHandler.PythonHealth)

		protected := api.Group("/")
		protected.Use(middleware.JWTAuth(jwtSecret))
		{
			protected.GET("/me", func(c *gin.Context) {
				c.JSON(200, gin.H{"message": "you are logged in"})
			})

			// protected.POST("/upload", uploadHandler.UploadAudio)
			protected.GET("/tasks", uploadHandler.ListMyTasks)
			protected.GET("/tasks/:id", uploadHandler.GetTaskStatus)

			protected.GET("/notes/:task_id", noteResultHandler.GetByTaskID)
			protected.POST("/oss/sts", ossHandler.GetSTS)
			protected.POST("/upload/complete", ossHandler.CompleteUpload)
			protected.DELETE("/tasks/:id", uploadHandler.DeleteTask)

			protected.POST("/python/tasks", pythonTaskHandler.CreateTask)
			protected.GET("/python/tasks/:id", pythonTaskHandler.GetTask)
		}
	}

	return r
}
