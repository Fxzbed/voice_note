import request from './request'

export function uploadApi(file) {
  const formData = new FormData()

  // 你的 Gin 后端是 c.FormFile("file")，所以这里必须是 file
  formData.append('file', file)

  return request.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getTasksApi() {
  return request.get('/tasks')
}

export function getTaskDetailApi(taskId) {
  return request.get(`/tasks/${taskId}`)
}

export function createPythonTaskApi(taskId) {
  return request.post('/python/tasks', {
    task_id: taskId
  })
}

export function getPythonTaskApi(taskId) {
  return request.get(`/python/tasks/${taskId}`)
}

export function getOssStsApi(originalName) {
  return request.post('/oss/sts', {
    original_name: originalName
  })
}

export function completeUploadApi(data) {
  return request.post('/upload/complete', data)
}

export function deleteTaskApi(taskId) {
  return request.delete(`/tasks/${taskId}`)
}
