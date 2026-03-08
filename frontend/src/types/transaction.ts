export type TransactionType = 'INCOME' | 'EXPENSE'

export type TransactionCategory = 'SALARY' | 'OTHER' | 'NEED' | 'WANT' | 'SAVING'

export interface Transaction {
  id: number
  amount: string
  date: string
  type: TransactionType
  category: TransactionCategory
  comment?: string
}

export interface CreateTransactionRequest {
  amount: number
  date: string
  type: TransactionType
  category: TransactionCategory
  comment?: string
}

export interface UpdateTransactionRequest {
  amount?: number
  date?: string
  type: TransactionType
  category: TransactionCategory
  comment?: string
}

export interface TransactionFilters {
  amount?: number
  before?: string
  after?: string
  type?: TransactionType
  category?: TransactionCategory
  comment?: string
  page?: number
  limit?: number
}

export const INCOME_CATEGORIES: TransactionCategory[] = ['SALARY', 'OTHER']
export const EXPENSE_CATEGORIES: TransactionCategory[] = ['NEED', 'WANT', 'SAVING']
