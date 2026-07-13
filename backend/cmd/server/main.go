package main

import (
	"log"

	"github.com/gin-gonic/gin"

	"voice-note-app/internal/config"
	"voice-note-app/internal/handler"
	"voice-note-app/internal/model"
	"voice-note-app/internal/repository"
	"voice-note-app/internal/router"
	"voice-note-app/internal/service"
	"voice-note-app/pkg/httpclient"
)

func main() {
	cfg := config.LoadConfig()

	gin.SetMode(cfg.GinMode)

	db := config.InitDB(cfg)

	if err := db.AutoMigrate(
		&model.User{},
		&model.UploadTask{},
		&model.NoteResult{},
	); err != nil {
		log.Fatalf("auto migrate failed: %v", err)
	}

	client := httpclient.NewClient()

	pythonService := service.NewPythonService(cfg.PythonServiceURL, client)

	healthHandler := handler.NewHealthHandler(pythonService)

	userRepo := repository.NewUserRepository(db)
	authService := service.NewAuthService(userRepo, cfg.JWTSecret)
	authHandler := handler.NewAuthHandler(authService)

	uploadTaskRepo := repository.NewUploadTaskRepository(db)

	ossService := service.NewOSSService(
		cfg.OSSRegion,
		cfg.OSSBucket,
		cfg.OSSEndpoint,
		cfg.OSSBaseURL,
		cfg.AliyunAccessKeyID,
		cfg.AliyunAccessKeySecret,
		cfg.OSSSTSRoleArn,
		cfg.OSSSTSDurationSeconds,
	)
	uploadService := service.NewUploadService(uploadTaskRepo, "./uploads", ossService)
	if err := uploadService.EnsureUploadDir(); err != nil {
		log.Fatalf("create upload dir failed: %v", err)
	}

	uploadHandler := handler.NewUploadHandler(uploadService)
	// noteHandler := handler.NewNoteHandler(db, uploadService)
	noteResultRepo := repository.NewNoteResultRepository(db)
	noteResultService := service.NewNoteResultService(noteResultRepo)

	pythonTaskHandler := handler.NewPythonTaskHandler(
		pythonService,
		uploadService,
		noteResultService,
	)

	ossHandler := handler.NewOSSHandler(ossService, uploadService)

	noteResultHandler := handler.NewNoteResultHandler(noteResultService, uploadService)

	r := router.SetupRouter(
		authHandler,
		healthHandler,
		uploadHandler,
		pythonTaskHandler,
		ossHandler,
		noteResultHandler,
		cfg.JWTSecret,
	)

	log.Printf("server running on :%s", cfg.AppPort)
	if err := r.Run(":" + cfg.AppPort); err != nil {
		log.Fatalf("server start failed: %v", err)
	}
}
