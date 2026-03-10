import type { TransactionCategory, TransactionType } from './transaction'

export interface NumTransactions {
  num_transactions: number
}

export interface StatTotals {
  total_balance: number
  total_income: number
  total_expense: number
  total_need: number
  total_want: number
  total_saving: number
  total_salary: number
  total_other: number
}

export interface MonthlyStats {
  month: string
  total_income: number
  total_expense: number
  total_need: number
  total_want: number
  total_saving: number
}

export interface MonthlyStatsResponse {
  months: MonthlyStats[]
}

export interface NumTransactionsFilters {
  before?: string
  after?: string
  type?: TransactionType
  category?: TransactionCategory
  comment?: string
}

export interface TotalsFilters {
  before?: string
  after?: string
}

export interface MonthlyStatsFilters {
  months?: number
  before?: string
}
