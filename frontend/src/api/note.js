import request from './request.js'

export function getNoteByTaskIdApi(taskId) {
  return request.get(`/notes/${taskId}`)
}
