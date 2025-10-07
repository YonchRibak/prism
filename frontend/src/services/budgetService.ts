import { apiService } from './api'
import type {
  Budget,
  PaginatedResponse
} from '@/types/api-types'

export const budgetService = {
  async getBudgets(): Promise<PaginatedResponse<Budget>> {
    return apiService.get<PaginatedResponse<Budget>>('/api/v1/budgets/')
  },

  async getBudget(id: number): Promise<Budget> {
    return apiService.get<Budget>(`/api/v1/budgets/${id}/`)
  },

  async createBudget(data: Omit<Budget, 'id' | 'user' | 'spent' | 'remaining' | 'createdAt' | 'updatedAt'>): Promise<Budget> {
    return apiService.post<Budget>('/api/v1/budgets/', data)
  },

  async updateBudget(id: number, data: Partial<Budget>): Promise<Budget> {
    return apiService.put<Budget>(`/api/v1/budgets/${id}/`, data)
  },

  async deleteBudget(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v1/budgets/${id}/`)
  },

  async getBudgetSummary(): Promise<any> {
    return apiService.get('/api/v1/budgets/summary/')
  }
}