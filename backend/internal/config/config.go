package config

import (
	"log"
	"os"
	"strconv"

	"github.com/joho/godotenv"
	"github.com/spf13/viper"
)

type Config struct {
	AppPort          string
	PythonServiceURL string
	GinMode          string
	JWTSecret        string
	DBHost           string
	DBPort           string
	DBUser           string
	DBPassword       string
	DBName           string

	OSSRegion             string
	OSSBucket             string
	OSSEndpoint           string
	OSSBaseURL            string
	AliyunAccessKeyID     string
	AliyunAccessKeySecret string
	OSSSTSRoleArn         string
	OSSSTSDurationSeconds int64
}

func LoadConfig() *Config {
	_ = godotenv.Load()
	viper.AutomaticEnv()

	cfg := &Config{
		AppPort:               getEnv("APP_PORT", "8080"),
		PythonServiceURL:      getEnv("PYTHON_SERVICE_URL", "http://127.0.0.1:8000"),
		GinMode:               getEnv("GIN_MODE", "debug"),
		JWTSecret:             getEnv("JWT_SECRET", "secret_key"),
		DBHost:                getEnv("DB_HOST", "127.0.0.1"),
		DBPort:                getEnv("DB_PORT", "3306"),
		DBUser:                getEnv("DB_USER", "appuser"),
		DBPassword:            getEnv("DB_PASSWORD", "app123456"),
		DBName:                getEnv("DB_NAME", "voice_note"),
		OSSRegion:             getEnv("OSS_REGION", ""),
		OSSBucket:             getEnv("OSS_BUCKET", ""),
		OSSEndpoint:           getEnv("OSS_ENDPOINT", ""),
		OSSBaseURL:            getEnv("OSS_BASE_URL", ""),
		AliyunAccessKeyID:     getEnv("ALIYUN_ACCESS_KEY_ID", ""),
		AliyunAccessKeySecret: getEnv("ALIYUN_ACCESS_KEY_SECRET", ""),
		OSSSTSRoleArn:         getEnv("OSS_STS_ROLE_ARN", ""),
		OSSSTSDurationSeconds: getEnvAsInt64("OSS_STS_DURATION_SECONDS", 3600),
	}

	log.Println("config loaded")
	return cfg
}

func getEnv(key, defaultValue string) string {
	value := viper.GetString(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func getEnvAsInt64(key string, defaultValue int64) int64 {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}

	value, err := strconv.ParseInt(valueStr, 10, 64)
	if err != nil {
		return defaultValue
	}

	return value
}
