import { apiService } from './api'
import type {
  Account,
  PaginatedResponse,
  ApiRequestBody,
  ApiResponse
} from '@/types/api-types'

export const accountService = {
  async getAccounts(): Promise<PaginatedResponse<Account>> {
    return apiService.get<PaginatedResponse<Account>>('/api/v1/accounts/')
  },

  async getAccount(id: number): Promise<Account> {
    return apiService.get<Account>(`/api/v1/accounts/${id}/`)
  },

  async createAccount(data: Omit<Account, 'id' | 'user' | 'balance' | 'createdAt' | 'updatedAt'>): Promise<Account> {
    return apiService.post<Account>('/api/v1/accounts/', data)
  },

  async updateAccount(id: number, data: Partial<Account>): Promise<Account> {
    return apiService.put<Account>(`/api/v1/accounts/${id}/`, data)
  },

  async deleteAccount(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v1/accounts/${id}/`)
  },

  async getAccountSummary(): Promise<any> {
    return apiService.get('/api/v1/accounts/summary/')
  }
}