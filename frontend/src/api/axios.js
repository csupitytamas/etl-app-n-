import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
})

// 🔐 Interceptor – Token automatikus hozzáadása minden kéréshez
instance.interceptors.request.use((config) => {
  let token
  if (window.electronStore?.getToken) {
    token = window.electronStore.getToken()
  } else {
    token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  }

  if (token) {
    config.headers['Authorization'] = token
  }

  return config
}, (error) => {
  return Promise.reject(error)
})

export default instance