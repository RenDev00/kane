import type { MonthlyStatsFilters, MonthlyStatsResponse, NumTransactions, NumTransactionsFilters, StatTotals, TotalsFilters } from '@/types/stats'
import { apiClient } from './api'

export const statsService = {
  async getNumTransactions (filters?: NumTransactionsFilters): Promise<NumTransactions> {
    const response = await apiClient.get<NumTransactions>('/stats/num_transactions', {
      params: filters,
    })
    return response.data
  },

  async getTotals (filters?: TotalsFilters): Promise<StatTotals> {
    const response = await apiClient.get<StatTotals>('/stats/totals', {
      params: filters,
    })
    return response.data
  },

  async getMonthlyStats (filters?: MonthlyStatsFilters): Promise<MonthlyStatsResponse> {
    const response = await apiClient.get<MonthlyStatsResponse>('/stats/monthly', {
      params: filters,
    })
    return response.data
  },
}
