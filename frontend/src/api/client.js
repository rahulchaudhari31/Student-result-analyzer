import axios from 'axios'
import { API_URL } from '../config'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.dispatchEvent(new CustomEvent('auth:logout'))
    }
    return Promise.reject(error)
  },
)

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (email, password, name, role) =>
    api.post('/auth/register', { email, password, name, role }),
}

export const resultsAPI = {
  analyze: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/results/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  save: (payload) => api.post('/results/save', payload),
  list: () => api.get('/results/'),
  get: (id) => api.get(`/results/${id}`),
}

export const studentsAPI = {
  identifiers: () => api.get('/students/identifiers'),
  history: (prn) => api.get('/students/history', { params: { prn } }),
}

export const overviewAPI = {
  get: () => api.get('/overview/'),
}

function formatValidationDetail(detail) {
  if (!Array.isArray(detail)) return detail

  return detail
    .map((item) => {
      if (item == null) return null
      const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : undefined
      const rawMsg = item?.msg
      const msg = Array.isArray(rawMsg) ? rawMsg.join(', ') : typeof rawMsg === 'string' ? rawMsg : ''
      if (msg) return field ? `${field}: ${msg}` : msg
      return field ? String(field) : JSON.stringify(item)
    })
    .filter((line) => line != null && line !== '')
    .join('\n')
}

export function getErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  try {
    const detail = error?.response?.data?.detail
    if (detail != null) {
      const formatted = formatValidationDetail(detail)
      if (typeof formatted === 'string' && formatted.trim()) return formatted
    }
    if (error instanceof Error && error.message) return error.message
    if (typeof error === 'string' && error.trim()) return error
  } catch {
    // fall through to fallback
  }
  return fallback
}

export default api
