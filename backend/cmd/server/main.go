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
	// 1. 加载配置
	cfg := config.LoadConfig()

	// 2. 设置 Gin 模式
	gin.SetMode(cfg.GinMode)

	// 3. 初始化数据库
	db := config.InitDB(cfg)

	// 4. 自动迁移表结构
	if err := db.AutoMigrate(
		&model.User{},
		&model.UploadTask{},
	); err != nil {
		log.Fatalf("auto migrate failed: %v", err)
	}

	// 5. 初始化 HTTP 客户端
	client := httpclient.NewClient()

	// 6. 初始化 Python 服务
	pythonService := service.NewPythonService(cfg.PythonServiceURL, client)

	// 7. 初始化健康检查 Handler
	healthHandler := handler.NewHealthHandler(pythonService)

	// 8. 初始化用户认证模块
	userRepo := repository.NewUserRepository(db)
	authService := service.NewAuthService(userRepo, cfg.JWTSecret)
	authHandler := handler.NewAuthHandler(authService)

	// 9. 初始化上传任务模块
	uploadTaskRepo := repository.NewUploadTaskRepository(db)
	uploadService := service.NewUploadService(uploadTaskRepo, "./uploads")
	if err := uploadService.EnsureUploadDir(); err != nil {
		log.Fatalf("create upload dir failed: %v", err)
	}
	uploadHandler := handler.NewUploadHandler(uploadService)

	// 10. 初始化 Python 任务 Handler
	pythonTaskHandler := handler.NewPythonTaskHandler(
		pythonService,
		uploadService,
	)

	// 11. 注册路由
	r := router.SetupRouter(
		authHandler,
		healthHandler,
		uploadHandler,
		pythonTaskHandler,
		cfg.JWTSecret,
	)

	// 12. 启动服务
	log.Printf("server running on :%s", cfg.AppPort)
	if err := r.Run(":" + cfg.AppPort); err != nil {
		log.Fatalf("server start failed: %v", err)
	}
}
