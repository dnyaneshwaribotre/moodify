import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
const api = axios.create({ baseURL, headers: { 'Content-Type': 'application/json' } })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('moodify_access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use((response) => response, async (error) => {
  const original = error.config
  if (error.response?.status === 401 && !original?._retried && localStorage.getItem('moodify_refresh') && !original.url?.includes('/auth/login/')) {
    original._retried = true
    try {
      const { data } = await axios.post(`${baseURL}/auth/refresh/`, { refresh: localStorage.getItem('moodify_refresh') })
      localStorage.setItem('moodify_access', data.access)
      if (data.refresh) localStorage.setItem('moodify_refresh', data.refresh)
      original.headers.Authorization = `Bearer ${data.access}`
      return api(original)
    } catch { localStorage.removeItem('moodify_access'); localStorage.removeItem('moodify_refresh') }
  }
  const payload = error.response?.data
  const message = payload?.detail || payload?.error || (payload && Object.values(payload).flat().join(' ')) || error.message || 'Request failed'
  return Promise.reject(new Error(String(message)))
})
export default api
