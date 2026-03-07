import type { CreateTransactionRequest, Transaction, TransactionFilters, UpdateTransactionRequest } from '@/types/transaction'
import { apiClient } from './api'

export const transactionService = {
  async createTransaction (data: CreateTransactionRequest): Promise<Transaction> {
    const response = await apiClient.post<Transaction>('/transactions/', data)
    return response.data
  },

  async getTransactions (filters?: TransactionFilters): Promise<Transaction[]> {
    const response = await apiClient.get<Transaction[]>('/transactions/', {
      params: filters,
    })
    return response.data
  },

  async getTransactionById (id: number): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/transactions/${id}`)
    return response.data
  },

  async updateTransaction (id: number, data: UpdateTransactionRequest): Promise<Transaction> {
    const response = await apiClient.patch<Transaction>(`/transactions/${id}`, data)
    return response.data
  },

  async deleteTransaction (id: number): Promise<void> {
    await apiClient.delete(`/transactions/${id}`)
  },
}
