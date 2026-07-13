import request from './request'

export function loginApi(data) {
  return request.post('/login', data)
}

export function registerApi(data) {
  return request.post('/register', data)
}
