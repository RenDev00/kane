import type { NumTransactionsFilters, StatTotals, TotalsFilters } from '@/types/stats'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { statsService } from '@/services/statsService'

export const useStatsStore = defineStore('stats', () => {
  // Stats State
  const currentNumTransactions = ref<number>(0)
  const totals = ref<StatTotals>({
    total_balance: 0,
    total_expense: 0,
    total_income: 0,
    total_need: 0,
    total_want: 0,
    total_saving: 0,
    total_salary: 0,
    total_other: 0,
  })
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const getCurrentNumTransactions = computed(() => currentNumTransactions.value)
  const getTotals = computed(() => totals.value)

  // Actions
  async function fetchNumTransactions (filters?: NumTransactionsFilters) {
    loading.value = true
    error.value = null
    try {
      const data = await statsService.getNumTransactions(filters)
      currentNumTransactions.value = data.num_transactions
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to fetch number of transactions'
      throw error_
    } finally {
      loading.value = false
    }
  }

  async function fetchTotals (filters?: TotalsFilters) {
    loading.value = true
    error.value = null
    try {
      const data = await statsService.getTotals(filters)
      totals.value = data
    } catch (error_) {
      error.value = error_ instanceof Error ? error_.message : 'Failed to fetch number of transactions'
      throw error_
    } finally {
      loading.value = false
    }
  }

  return {
    // Stats State
    loading,
    error,
    // Getters
    getCurrentNumTransactions,
    getTotals,
    // Actions
    fetchNumTransactions,
    fetchTotals,
  }
})
