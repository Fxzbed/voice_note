package service

import (
	"encoding/json"
	"fmt"
	"path/filepath"
	"strings"
	"time"

	openapi "github.com/alibabacloud-go/darabonba-openapi/v2/client"
	sts "github.com/alibabacloud-go/sts-20150401/v2/client"
	"github.com/alibabacloud-go/tea/tea"
	"github.com/google/uuid"

	"voice-note-app/internal/dto"
)

type OSSService struct {
	Region             string
	Bucket             string
	Endpoint           string
	BaseURL            string
	AccessKeyID        string
	AccessKeySecret    string
	STSRoleArn         string
	STSDurationSeconds int64
}

func NewOSSService(
	region string,
	bucket string,
	endpoint string,
	baseURL string,
	accessKeyID string,
	accessKeySecret string,
	roleArn string,
	durationSeconds int64,
) *OSSService {
	return &OSSService{
		Region:             region,
		Bucket:             bucket,
		Endpoint:           endpoint,
		BaseURL:            strings.TrimRight(baseURL, "/"),
		AccessKeyID:        accessKeyID,
		AccessKeySecret:    accessKeySecret,
		STSRoleArn:         roleArn,
		STSDurationSeconds: durationSeconds,
	}
}

func (s *OSSService) BuildObjectKey(userID uint, originalName string) string {
	ext := filepath.Ext(originalName)
	return fmt.Sprintf(
		"audio/%d/%d/%02d/%02d/%s%s",
		userID,
		time.Now().Year(),
		time.Now().Month(),
		time.Now().Day(),
		uuid.NewString(),
		ext,
	)
}

func (s *OSSService) BuildObjectURL(objectKey string) string {
	return fmt.Sprintf("%s/%s", s.BaseURL, objectKey)
}

func (s *OSSService) createSTSClient() (*sts.Client, error) {
	// STS 是全局服务，通常走杭州端点
	// 阿里云官方文档和示例里 STS 常用 cn-hangzhou 端点。
	config := &openapi.Config{
		AccessKeyId:     tea.String(s.AccessKeyID),
		AccessKeySecret: tea.String(s.AccessKeySecret),
		Endpoint:        tea.String("sts.cn-hangzhou.aliyuncs.com"),
	}

	return sts.NewClient(config)
}

func (s *OSSService) GetSTSForUpload(userID uint, originalName string) (*dto.GetOSSSTSResponse, error) {
	objectKey := s.BuildObjectKey(userID, originalName)

	client, err := s.createSTSClient()
	if err != nil {
		return nil, err
	}

	// 只允许上传到当前 objectKey
	// 这样前端拿到临时凭证后不能随便写其他路径
	policyMap := map[string]any{
		"Version": "1",
		"Statement": []map[string]any{
			{
				"Effect":   "Allow",
				"Action":   []string{"oss:PutObject"},
				"Resource": []string{fmt.Sprintf("acs:oss:*:*:%s/%s", s.Bucket, objectKey)},
			},
		},
	}

	policyBytes, err := json.Marshal(policyMap)
	if err != nil {
		return nil, err
	}

	roleSessionName := fmt.Sprintf("upload-user-%d-%d", userID, time.Now().Unix())

	req := &sts.AssumeRoleRequest{
		RoleArn:         tea.String(s.STSRoleArn),
		RoleSessionName: tea.String(roleSessionName),
		DurationSeconds: tea.Int64(s.STSDurationSeconds),
		Policy:          tea.String(string(policyBytes)),
	}

	resp, err := client.AssumeRole(req)
	if err != nil {
		return nil, err
	}

	if resp == nil || resp.Body == nil || resp.Body.Credentials == nil {
		return nil, fmt.Errorf("sts assume role returned empty credentials")
	}

	creds := resp.Body.Credentials

	return &dto.GetOSSSTSResponse{
		AccessKeyID:     tea.StringValue(creds.AccessKeyId),
		AccessKeySecret: tea.StringValue(creds.AccessKeySecret),
		SecurityToken:   tea.StringValue(creds.SecurityToken),
		Expiration:      tea.StringValue(creds.Expiration),

		Region:    s.Region,
		Bucket:    s.Bucket,
		Endpoint:  s.Endpoint,
		BaseURL:   s.BaseURL,
		ObjectKey: objectKey,
	}, nil
}

func (s *OSSService) DeleteObject(objectKey string) error {
	// 当前先给出占位逻辑
	// 如果你后面已经接入了 OSS Go SDK 的真实客户端，
	// 可以在这里调用 DeleteObject API
	// 例如：client.DeleteObject(bucket, objectKey)

	// 暂时不删除 OSS 也可以直接 return nil
	return nil
}
