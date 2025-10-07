import { apiService } from './api'
import type { User } from '@/types/api-types'

export interface PasswordChangeData {
  oldPassword: string
  newPassword: string
}

export const userService = {
  async getProfile(): Promise<User> {
    return apiService.get<User>('/api/users/profile/')
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    return apiService.put<User>('/api/users/profile/', data)
  },

  async changePassword(data: PasswordChangeData): Promise<void> {
    return apiService.post<void>('/api/users/change-password/', data)
  }
}