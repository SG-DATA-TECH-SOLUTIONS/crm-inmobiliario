import axios from 'axios'
import type { TokenResponse } from '@/types/auth'

const API_URL = import.meta.env.VITE_API_URL || ''

export const authApi = {
  login: (email: string, password: string) =>
    axios.post<TokenResponse>(`${API_URL}/api/token/`, { email, password }),

  refresh: (refreshToken: string) =>
    axios.post<TokenResponse>(`${API_URL}/api/token/refresh/`, {
      refresh: refreshToken,
    }),
}
