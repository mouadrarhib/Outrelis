import axios from 'axios'

// Kept in module memory only. Never persist passwords or tokens in browser storage.
let accessToken: string | null = null
export function setAccessToken(token: string | null) { accessToken = token }

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 15_000,
})

http.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

http.interceptors.response.use((response) => response, (error: unknown) => {
  if (axios.isAxiosError(error) && error.response?.status === 401 && accessToken) {
    accessToken = null
    window.dispatchEvent(new Event('outrelis:session-expired'))
  }
  return Promise.reject(error)
})
