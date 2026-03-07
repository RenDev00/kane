import type { CreateTransactionRequest, Transaction, TransactionFilters, UpdateTransactionRequest } from '@/types/transaction'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { transactionService } from '@/services/transactionService'

export const useTransactionStore = defineStore('transaction', () => {
  // Transaction Table State
  const tableTransactions = ref<Transaction[]>([])
  const recentTransactions = ref<Transaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const getTableTransactions = computed(() => tableTransactions.value)
  const getRecentTransactions = computed(() => recentTransactions.value)

  // Actions
  async function fetchTableTransactions (filters?: TransactionFilters) {
    loading.value = true
    error.value = null
    try {
      const data = await transactionService.getTransactions(filters)
      tableTransactions.value = data
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to fetch table transactions'
      throw error_
    } finally {
      loading.value = false
    }
  }

  async function fetchRecentTransactions (filters?: TransactionFilters) {
    loading.value = true
    error.value = null
    try {
      const data = await transactionService.getTransactions(filters)
      recentTransactions.value = data
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to fetch recent transactions'
      throw error_
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactionById (id: number) {
    loading.value = true
    error.value = null
    try {
      const data = await transactionService.getTransactionById(id)
      return data
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to fetch transaction'
      throw error_
    } finally {
      loading.value = false
    }
  }

  async function createTransaction (data: CreateTransactionRequest) {
    loading.value = true
    error.value = null
    try {
      const newTransaction = await transactionService.createTransaction(data)
      return newTransaction
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to create transaction'
      throw error_
    } finally {
      loading.value = false
    }
  }

  async function updateTransaction (id: number, data: UpdateTransactionRequest) {
    loading.value = true
    error.value = null
    try {
      const updatedTransaction = await transactionService.updateTransaction(id, data)
      return updatedTransaction
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to update transaction'
      throw error_
    } finally {
      loading.value = false
    }
  }

  async function deleteTransaction (id: number) {
    loading.value = true
    error.value = null
    try {
      await transactionService.deleteTransaction(id)
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to delete transaction'
      throw error_
    } finally {
      loading.value = false
    }
  }

  return {
    // Transaction Table State
    tableTransactions,
    recentTransactions,
    loading,
    error,
    // Getters
    getTableTransactions,
    getRecentTransactions,
    // Actions
    fetchTableTransactions,
    fetchRecentTransactions,
    fetchTransactionById,
    createTransaction,
    updateTransaction,
    deleteTransaction,
  }
})
