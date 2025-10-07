import { apiService } from './api'
import type {
  User,
  LoginRequest,
  RegisterRequest,
  ApiResponse,
  ApiRequestBody
} from '@/types/api-types'

interface LoginResponse {
  access: string
  refresh: string
  user: User
}

interface RegisterData extends RegisterRequest {}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    return apiService.post<LoginResponse>('/api/auth/login/', {
      email,
      password,
    })
  },

  async register(userData: RegisterData): Promise<LoginResponse> {
    return apiService.post<LoginResponse>('/api/auth/register/', userData)
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refreshToken')
    if (refreshToken) {
      await apiService.post('/api/auth/logout/', {
        refresh: refreshToken,
      })
    }
  },

  async getCurrentUser() {
    return apiService.get('/api/users/profile/')
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    return apiService.post<{ access: string }>('/api/auth/token/refresh/', {
      refresh: refreshToken,
    })
  },
}