package config

import (
	"log"

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
}

func LoadConfig() *Config {
	_ = godotenv.Load()
	viper.AutomaticEnv()

	cfg := &Config{
		AppPort:          getEnv("APP_PORT", "8080"),
		PythonServiceURL: getEnv("PYTHON_SERVICE_URL", "http://127.0.0.1:8000"),
		GinMode:          getEnv("GIN_MODE", "debug"),
		JWTSecret:        getEnv("JWT_SECRET", "secret_key"),
		DBHost:           getEnv("DB_HOST", "127.0.0.1"),
		DBPort:           getEnv("DB_PORT", "3306"),
		DBUser:           getEnv("DB_USER", "appuser"),
		DBPassword:       getEnv("DB_PASSWORD", "app123456"),
		DBName:           getEnv("DB_NAME", "voice_note"),
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
