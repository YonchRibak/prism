import { apiService } from './api'
import type {
  Transaction,
  PaginatedResponse
} from '@/types/api-types'

export interface TransactionFilters {
  account?: number
  category?: number
  type?: 'income' | 'expense'
  startDate?: string
  endDate?: string
  search?: string
}

export const transactionService = {
  async getTransactions(filters?: TransactionFilters): Promise<PaginatedResponse<Transaction>> {
    const params = new URLSearchParams()

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString())
        }
      })
    }

    const queryString = params.toString()
    const url = `/api/v1/transactions/${queryString ? `?${queryString}` : ''}`

    return apiService.get<PaginatedResponse<Transaction>>(url)
  },

  async getTransaction(id: number): Promise<Transaction> {
    return apiService.get<Transaction>(`/api/v1/transactions/${id}/`)
  },

  async createTransaction(data: Omit<Transaction, 'id' | 'user' | 'createdAt' | 'updatedAt'>): Promise<Transaction> {
    return apiService.post<Transaction>('/api/v1/transactions/', data)
  },

  async updateTransaction(id: number, data: Partial<Transaction>): Promise<Transaction> {
    return apiService.put<Transaction>(`/api/v1/transactions/${id}/`, data)
  },

  async deleteTransaction(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v1/transactions/${id}/`)
  },

  async getTransactionSummary(): Promise<any> {
    return apiService.get('/api/v1/transactions/summary/')
  }
}