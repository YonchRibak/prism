import { apiService } from './api'
import type {
  Category,
  PaginatedResponse
} from '@/types/api-types'

export const categoryService = {
  async getCategories(): Promise<PaginatedResponse<Category>> {
    return apiService.get<PaginatedResponse<Category>>('/api/v1/categories/')
  },

  async getCategory(id: number): Promise<Category> {
    return apiService.get<Category>(`/api/v1/categories/${id}/`)
  },

  async createCategory(data: Omit<Category, 'id' | 'user' | 'createdAt' | 'updatedAt'>): Promise<Category> {
    return apiService.post<Category>('/api/v1/categories/', data)
  },

  async updateCategory(id: number, data: Partial<Category>): Promise<Category> {
    return apiService.put<Category>(`/api/v1/categories/${id}/`, data)
  },

  async deleteCategory(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v1/categories/${id}/`)
  }
}