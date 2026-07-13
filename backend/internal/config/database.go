package config

import (
	"fmt"
	"log"

	"voice-note-app/internal/model"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

func InitDB(cfg *Config) *gorm.DB {
	dsn := fmt.Sprintf(
		"%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True&loc=Local",
		cfg.DBUser,
		cfg.DBPassword,
		cfg.DBHost,
		cfg.DBPort,
		cfg.DBName,
	)

	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("database connect failed: ", err)
	}

	log.Println("database connected")

	if err := db.AutoMigrate(
		&model.User{},
		&model.UploadTask{},
		&model.NoteResult{},
	); err != nil {
		log.Fatal("database migrate failed: ", err)
	}

	log.Println("database migrated")

	return db
}
