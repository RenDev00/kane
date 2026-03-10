<template>
  <v-container fluid>
    <!-- Header with Timeframe Selector -->
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center" cols="12">
        <h2 class="text-h4 font-weight-bold">Dashboard</h2>
        <v-select
          v-model="selectedTimeframe"
          density="compact"
          hide-details
          :items="timeframeOptions"
          label="Timeframe"
          max-width="200"
          variant="outlined"
          @update:model-value="handleTimeframeChange"
        />
      </v-col>
    </v-row>

    <!-- Metric Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="4" sm="4">
        <v-card class="metric-card" :color="totals.total_balance >= 0 ? 'info' : 'warning'" variant="tonal">
          <v-card-item>
            <v-card-title class="text-subtitle-2 text-medium-emphasis">
              <v-icon class="mr-2" icon="mdi-cash-fast" size="small" />
              Net Flow
            </v-card-title>
            <v-card-text class="py-2">
              <span class="metric-value" :class="totals.total_balance >= 0 ? 'text-info' : 'text-warning'">
                {{ formatCurrency(totals.total_balance) }}
              </span>
            </v-card-text>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" md="4" sm="4">
        <v-card class="metric-card" color="success" variant="tonal">
          <v-card-item>
            <v-card-title class="text-subtitle-2 text-medium-emphasis">
              <v-icon class="mr-2" icon="mdi-trending-up" size="small" />
              Income
            </v-card-title>
            <v-card-text class="py-2">
              <span class="metric-value text-success">{{ formatCurrency(totals.total_income) }}</span>
            </v-card-text>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" md="4" sm="4">
        <v-card class="metric-card" color="error" variant="tonal">
          <v-card-item>
            <v-card-title class="text-subtitle-2 text-medium-emphasis">
              <v-icon class="mr-2" icon="mdi-trending-down" size="small" />
              Expenses
            </v-card-title>
            <v-card-text class="py-2">
              <span class="metric-value text-error">{{ formatCurrency(totals.total_expense) }}</span>
            </v-card-text>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>

    <!-- Expense Breakdown Cards -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h3 class="text-h6 mb-3 font-weight-medium">Expense Breakdown</h3>
      </v-col>

      <v-col cols="12" md="4" sm="4">
        <v-card class="expense-card" color="teal" variant="tonal">
          <v-card-item class="breakdown-card-item">
            <div>
              <v-card-title class="text-subtitle-2 text-medium-emphasis pa-0 mb-1">
                <v-icon class="mr-2" icon="mdi-piggy-bank" size="small" />
                Savings
              </v-card-title>
              <span class="breakdown-value">{{ formatCurrency(totals.total_saving) }}</span>
            </div>
            <template #append>
              <v-tooltip location="top" text="Percentage of Income">
                <template #activator="{ props }">
                  <v-chip class="breakdown-chip" color="teal" variant="flat" v-bind="props">
                    {{ calculatePercentage(totals.total_saving, totals.total_income) }}%
                  </v-chip>
                </template>
              </v-tooltip>
            </template>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" md="4" sm="4">
        <v-card class="expense-card" color="indigo" variant="tonal">
          <v-card-item class="breakdown-card-item">
            <div>
              <v-card-title class="text-subtitle-2 text-medium-emphasis pa-0 mb-1">
                <v-icon class="mr-2" icon="mdi-home" size="small" />
                Needs
              </v-card-title>
              <span class="breakdown-value">{{ formatCurrency(totals.total_need) }}</span>
            </div>
            <template #append>
              <v-tooltip location="top" text="Percentage of Income">
                <template #activator="{ props }">
                  <v-chip class="breakdown-chip" color="indigo" variant="flat" v-bind="props">
                    {{ calculatePercentage(totals.total_need, totals.total_income) }}%
                  </v-chip>
                </template>
              </v-tooltip>
            </template>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" md="4" sm="4">
        <v-card class="expense-card" color="purple" variant="tonal">
          <v-card-item class="breakdown-card-item">
            <div>
              <v-card-title class="text-subtitle-2 text-medium-emphasis pa-0 mb-1">
                <v-icon class="mr-2" icon="mdi-shopping" size="small" />
                Wants
              </v-card-title>
              <span class="breakdown-value">{{ formatCurrency(totals.total_want) }}</span>
            </div>
            <template #append>
              <v-tooltip location="top" text="Percentage of Income">
                <template #activator="{ props }">
                  <v-chip class="breakdown-chip" color="purple" variant="flat" v-bind="props">
                    {{ calculatePercentage(totals.total_want, totals.total_income) }}%
                  </v-chip>
                </template>
              </v-tooltip>
            </template>
          </v-card-item>
        </v-card>
      </v-col>

    </v-row>

    <!-- Monthly Chart and Recent Transactions Side by Side -->
    <v-row class="mb-6 bottom-row">
      <v-col cols="12" lg="8" md="8">
        <v-card class="chart-card">
          <v-card-title class="text-h6 pa-4 pb-2 d-flex justify-space-between align-center">
            <span>
              <v-icon class="mr-2" icon="mdi-chart-bar" />
              Overview
            </span>
            <v-btn-toggle
              v-model="chartTimeframe"
              class="chart-timeframe-toggle"
              color="primary"
              density="compact"
              mandatory
              variant="outlined"
            >
              <v-btn size="small" value="3m">3M</v-btn>
              <v-btn size="small" value="6m">6M</v-btn>
              <v-btn size="small" value="12m">12M</v-btn>
              <v-btn size="small" value="ytd">YTD</v-btn>
            </v-btn-toggle>
          </v-card-title>
          <v-card-text class="pa-4">
            <div class="chart-container">
              <bar
                v-if="chartData.labels.length > 0"
                :data="chartData"
                :options="chartOptions"
              />
              <v-alert v-else color="info" variant="tonal">
                No data available for the selected timeframe.
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="4" md="4">
        <v-card class="transactions-card">
          <v-card-title class="text-h6 pa-4 pb-2 d-flex justify-space-between align-center">
            <span>
              <v-icon class="mr-2" icon="mdi-history" />
              Recent
            </span>
            <v-btn color="primary" size="small" to="/transactions" variant="text">
              View All
              <v-icon class="ml-1" icon="mdi-arrow-right" />
            </v-btn>
          </v-card-title>
          <v-card-text class="pa-0">
            <v-list lines="two">
              <v-list-item
                v-for="transaction in recentTransactions"
                :key="transaction.id"
                class="transaction-item"
                @click="navigateToTransaction(transaction.id)"
              >
                <template #prepend>
                  <v-avatar :color="getTransactionColor(transaction.type)" size="40">
                    <v-icon :icon="getTransactionIcon(transaction.category)" size="small" />
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-medium">
                  {{ formatCategory(transaction.category) }}
                  <v-chip
                    class="ml-2"
                    :color="transaction.type.toUpperCase() === 'INCOME' ? 'success' : 'error'"
                    density="compact"
                    :prepend-icon="transaction.type.toUpperCase() === 'INCOME' ? 'mdi-arrow-up' : 'mdi-arrow-down'"
                    size="small"
                    variant="tonal"
                  >
                    {{ transaction.type.toUpperCase() === 'INCOME' ? 'In' : 'Out' }}
                  </v-chip>
                </v-list-item-title>

                <v-list-item-subtitle class="text-caption">
                  {{ formatDate(transaction.date) }}
                  <span v-if="transaction.comment" class="ml-2 text-medium-emphasis">
                    • {{ transaction.comment }}
                  </span>
                </v-list-item-subtitle>

                <template #append>
                  <span
                    class="text-h6 font-weight-bold"
                    :class="transaction.type.toUpperCase() === 'INCOME' ? 'text-success' : 'text-error'"
                  >
                    {{ transaction.type.toUpperCase() === 'INCOME' ? '+' : '-' }}{{ formatCurrency(transaction.amount, 2) }}
                  </span>
                </template>
              </v-list-item>

              <v-list-item v-if="recentTransactions.length === 0">
                <v-list-item-title class="text-center text-medium-emphasis">
                  No recent transactions
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
  import type { MonthlyStats, StatTotals } from '@/types/stats'
  import type { Transaction } from '@/types/transaction'
  import {
    ArcElement,
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    Title,
    Tooltip,
  } from 'chart.js'
  import { format } from 'date-fns'
  import { computed, onMounted, ref, watch } from 'vue'
  import { Bar } from 'vue-chartjs'
  import { useRouter } from 'vue-router'
  import { statsService } from '@/services/statsService'
  import { transactionService } from '@/services/transactionService'

  ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

  const router = useRouter()

  // Main timeframe selection (for metrics cards)
  type TimeframeOption = 'current_month' | 'last_month' | 'ytd' | 'last_3_months' | 'last_6_months' | 'last_12_months' | 'all_time'

  const timeframeOptions = [
    { title: 'Current Month', value: 'current_month' },
    { title: 'Last Month', value: 'last_month' },
    { title: 'Last 3 Months', value: 'last_3_months' },
    { title: 'Last 6 Months', value: 'last_6_months' },
    { title: 'Last 12 Months', value: 'last_12_months' },
    { title: 'Year to Date', value: 'ytd' },
    { title: 'All Time', value: 'all_time' },
  ]

  const selectedTimeframe = ref<TimeframeOption>('current_month')
  const loading = ref(false)

  // Chart timeframe selection (separate from main)
  type ChartTimeframeOption = '3m' | '6m' | '12m' | 'ytd'
  const chartTimeframe = ref<ChartTimeframeOption>('6m')

  // Data state
  const totals = ref<StatTotals>({
    total_balance: 0,
    total_income: 0,
    total_expense: 0,
    total_need: 0,
    total_want: 0,
    total_saving: 0,
    total_salary: 0,
    total_other: 0,
  })

  const monthlyStats = ref<MonthlyStats[]>([])
  const recentTransactions = ref<Transaction[]>([])

  const chartData = computed(() => {
    const labels = monthlyStats.value.map(m => formatMonthLabel(m.month))
    const incomeData = monthlyStats.value.map(m => m.total_income)
    const needData = monthlyStats.value.map(m => m.total_need)
    const wantData = monthlyStats.value.map(m => m.total_want)
    const savingData = monthlyStats.value.map(m => m.total_saving)

    return {
      labels,
      datasets: [
        {
          label: 'Income',
          data: incomeData,
          backgroundColor: '#4CAF50',
          borderColor: '#4CAF50',
          borderWidth: 1,
          order: 1,
        },
        {
          label: 'Savings',
          data: savingData,
          backgroundColor: '#26A69A',
          borderColor: '#26A69A',
          borderWidth: 1,
          stack: 'expenses',
          order: 2,
        },
        {
          label: 'Needs',
          data: needData,
          backgroundColor: '#3F51B5',
          borderColor: '#3F51B5',
          borderWidth: 1,
          stack: 'expenses',
          order: 2,
        },
        {
          label: 'Wants',
          data: wantData,
          backgroundColor: '#AB47BC',
          borderColor: '#AB47BC',
          borderWidth: 1,
          stack: 'expenses',
          order: 2,
        },
      ],
    }
  })

  const chartOptions = computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y || 0
            return `${label}: ${formatCurrency(value)}`
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 11,
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          callback: function (this: any, tickValue: string | number) {
            const value = typeof tickValue === 'string' ? Number.parseFloat(tickValue) : tickValue
            return formatCurrency(value)
          },
          font: {
            size: 11,
          },
        },
      },
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
  }))

  // Helper functions for date ranges
  function getDateRangeForTimeframe (timeframe: TimeframeOption): { after?: string, before?: string, months?: number } {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()

    switch (timeframe) {
      case 'current_month': {
        const start = new Date(year, month, 1, 0, 0, 0)
        const end = new Date(year, month + 1, 0, 23, 59, 59)
        return {
          after: start.toISOString(),
          before: end.toISOString(),
          months: 1,
        }
      }
      case 'last_month': {
        const start = new Date(year, month - 1, 1, 0, 0, 0)
        const end = new Date(year, month, 0, 23, 59, 59)
        return {
          after: start.toISOString(),
          before: end.toISOString(),
          months: 1,
        }
      }
      case 'ytd': {
        const start = new Date(year, 0, 1, 0, 0, 0)
        return {
          after: start.toISOString(),
          months: month + 1,
        }
      }
      case 'last_3_months': {
        const start = new Date(year, month - 3, 1, 0, 0, 0)
        const end = new Date(year, month, 0, 23, 59, 59)
        return {
          after: start.toISOString(),
          before: end.toISOString(),
          months: 3,
        }
      }
      case 'last_6_months': {
        const start = new Date(year, month - 6, 1, 0, 0, 0)
        const end = new Date(year, month, 0, 23, 59, 59)
        return {
          after: start.toISOString(),
          before: end.toISOString(),
          months: 6,
        }
      }
      case 'last_12_months': {
        const start = new Date(year, month - 12, 1, 0, 0, 0)
        const end = new Date(year, month, 0, 23, 59, 59)
        return {
          after: start.toISOString(),
          before: end.toISOString(),
          months: 12,
        }
      }
      default: {
        return {}
      }
    }
  }

  function getChartDateRange (timeframe: ChartTimeframeOption): { months: number, before?: string } {
    const now = new Date()

    switch (timeframe) {
      case '3m': {
        return { months: 3 }
      }
      case '6m': {
        return { months: 6 }
      }
      case '12m': {
        return { months: 12 }
      }
      case 'ytd': {
        const year = now.getFullYear()
        const month = now.getMonth()
        return {
          months: month + 1,
          before: new Date(year, month + 1, 0, 23, 59, 59).toISOString(),
        }
      }
      default: {
        return { months: 6 }
      }
    }
  }

  function formatMonthLabel (monthStr: string): string {
    try {
      const [year, month] = monthStr.split('-')
      const date = new Date(Number.parseInt(year!), Number.parseInt(month!) - 1, 1)
      return format(date, 'MMM yyyy')
    } catch {
      return monthStr
    }
  }

  function formatCurrency (value: number | string, decimals?: number): string {
    const num = typeof value === 'string' ? Number.parseFloat(value) : value
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: decimals || 0,
      maximumFractionDigits: decimals || 0,
    }).format(num)
  }

  function formatDate (dateString: string): string {
    const date = new Date(dateString)
    return format(date, 'MMM d, yyyy • HH:mm')
  }

  function formatCategory (category: string): string {
    return category.charAt(0).toUpperCase() + category.slice(1).toLowerCase()
  }

  function calculatePercentage (part: number, total: number): string {
    if (!total || total === 0 || Number.isNaN(total) || Number.isNaN(part)) {
      return '0.0'
    }
    const percentage = (part / total) * 100
    if (Number.isNaN(percentage)) {
      return '0.0'
    }
    return percentage.toFixed(1)
  }

  function getTransactionColor (type: string): string {
    return type.toUpperCase() === 'INCOME' ? 'success' : 'error'
  }

  function getTransactionIcon (category: string): string {
    const icons: Record<string, string> = {
      SALARY: 'mdi-hand-coin',
      OTHER: 'mdi-cash',
      NEED: 'mdi-home',
      WANT: 'mdi-shopping',
      SAVING: 'mdi-piggy-bank',
    }
    return icons[category.toUpperCase()] || 'mdi-cash'
  }

  function navigateToTransaction (id: number) {
    router.push(`/transactions?id=${id}`)
  }

  // Load chart data (independent of main timeframe)
  async function loadChartData () {
    const chartRange = getChartDateRange(chartTimeframe.value)
    const monthlyFilters = {
      months: chartRange.months,
      before: chartRange.before,
    }
    const monthlyResponse = await statsService.getMonthlyStats(monthlyFilters)
    monthlyStats.value = monthlyResponse.months
  }

  // Load only totals (for timeframe changes)
  async function loadTotals () {
    const dateRange = getDateRangeForTimeframe(selectedTimeframe.value)
    const totalsFilters = {
      after: dateRange.after,
      before: dateRange.before,
    }
    totals.value = await statsService.getTotals(totalsFilters)
  }

  // Load all data (initial load)
  async function loadDashboardData () {
    loading.value = true
    try {
      await Promise.all([
        loadTotals(),
        loadChartData(),
        transactionService.getTransactions({ limit: 20 }).then(data => {
          recentTransactions.value = data
        }),
      ])
    } finally {
      loading.value = false
    }
  }

  function handleTimeframeChange () {
    loadTotals()
  }

  // Watch for chart timeframe changes
  watch(chartTimeframe, () => {
    loadChartData()
  })

  onMounted(() => {
    loadDashboardData()
  })
</script>

<style scoped>
.metric-value {
  font-size: 2.5rem !important;
  font-weight: 700 !important;
  line-height: 1.2;
}

.breakdown-value {
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  line-height: 1.2;
}

.metric-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: default;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.expense-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.expense-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.breakdown-card-item {
  align-items: center;
}

.breakdown-card-item :deep(.v-card-item__append) {
  align-self: center;
}

.breakdown-chip {
  font-size: 1rem !important;
  font-weight: 600 !important;
  height: 32px !important;
  padding: 0 12px !important;
}

.bottom-row {
  align-items: stretch;
}

.chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-card :deep(.v-card-text) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.transactions-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.transactions-card :deep(.v-card-text) {
  flex: 1;
  overflow: hidden;
}

.transactions-card :deep(.v-list) {
  height: 650px;
  max-height: 650px;
  overflow-y: auto;
}

.chart-container {
  position: relative;
  flex: 1;
  height: 650px;
  max-height: 650px;
  width: 100%;
}

.chart-timeframe-toggle {
  border-radius: 8px;
}

.chart-timeframe-toggle :deep(.v-btn) {
  min-width: 48px;
  font-weight: 600;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.transaction-item {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.transaction-item:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

:deep(.v-list-item__prepend) {
  align-self: center;
}
</style>
