import { apiService } from './api'
import type {
  Goal,
  PaginatedResponse
} from '@/types/api-types'

export const goalService = {
  async getGoals(): Promise<PaginatedResponse<Goal>> {
    return apiService.get<PaginatedResponse<Goal>>('/api/v1/goals/')
  },

  async getGoal(id: number): Promise<Goal> {
    return apiService.get<Goal>(`/api/v1/goals/${id}/`)
  },

  async createGoal(data: Omit<Goal, 'id' | 'user' | 'progress' | 'createdAt' | 'updatedAt'>): Promise<Goal> {
    return apiService.post<Goal>('/api/v1/goals/', data)
  },

  async updateGoal(id: number, data: Partial<Goal>): Promise<Goal> {
    return apiService.put<Goal>(`/api/v1/goals/${id}/`, data)
  },

  async deleteGoal(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v1/goals/${id}/`)
  }
}