package service

import (
	"errors"
	"time"

	"voice-note-app/internal/model"
	"voice-note-app/internal/repository"

	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

type AuthService struct {
	UserRepo *repository.UserRepository
	JwtKey   []byte
}

func NewAuthService(userRepo *repository.UserRepository, jwtKey string) *AuthService {
	return &AuthService{
		UserRepo: userRepo,
		JwtKey:   []byte(jwtKey),
	}
}

// 注册
func (s *AuthService) Register(username, password string) error {
	_, err := s.UserRepo.FindByUsername(username)
	if err == nil {
		return errors.New("user already exists")
	}

	hash, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)

	user := &model.User{
		Username: username,
		Password: string(hash),
	}

	return s.UserRepo.Create(user)
}

// 登录
func (s *AuthService) Login(username, password string) (string, error) {
	user, err := s.UserRepo.FindByUsername(username)
	if err != nil {
		return "", errors.New("user not found")
	}

	err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(password))
	if err != nil {
		return "", errors.New("wrong password")
	}

	// 生成 JWT
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id":  user.ID,
		"username": user.Username,
		"exp":      time.Now().Add(24 * time.Hour).Unix(),
	})

	return token.SignedString(s.JwtKey)
}
