<template>
  <v-container fluid>
    <h1>Transactions</h1>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      item-value="id"
      :items="transactionStore.getTableTransactions"
      :items-length="statsStore.getCurrentNumTransactions"
      :items-per-page-options="[10]"
      :loading="transactionStore.loading"
      @update:options="handleOptionsUpdate"
    >
      <template #item.no="{ index }">
        {{ (currentPage - 1) * itemsPerPage + index + 1 }}
      </template>
      <template #item.date="{ item }">
        {{ formatDate(item.date) }}
      </template>
      <template #item.type="{ item }">
        {{ capitalize(item.type) }}
      </template>
      <template #item.category="{ item }">
        {{ capitalize(item.category) }}
      </template>
      <template #item.amount="{ item }">
        {{ formatAmount(item.amount) }}
      </template>
    </v-data-table-server>
  </v-container>
</template>

<script lang="ts" setup>
  import type { NumTransactionsFilters } from '@/types/stats'
  import { onMounted, ref } from 'vue'
  import { useStatsStore } from '@/stores/stats'
  import { useTransactionStore } from '@/stores/transaction'

  const transactionStore = useTransactionStore()
  const statsStore = useStatsStore()

  const currentPage = ref(1)
  const itemsPerPage = ref(10)

  const headers = [
    { title: 'No.', key: 'no', sortable: false },
    { title: 'Date', key: 'date' },
    { title: 'Type', key: 'type' },
    { title: 'Category', key: 'category' },
    { title: 'Amount', key: 'amount' },
    { title: 'Comment', key: 'comment' },
  ]

  async function updateNumTransactions (filters?: NumTransactionsFilters) {
    await statsStore.fetchNumTransactions(filters)
  }

  async function handleOptionsUpdate (options: { page: number, itemsPerPage: number }) {
    const { page, itemsPerPage: limit } = options
    currentPage.value = page
    await transactionStore.fetchTableTransactions({ page, limit })
  }

  function formatDate (dateString: string): string {
    const date = new Date(dateString)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  }

  function capitalize (text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
  }

  function formatAmount (amount: string | number): string {
    const num = typeof amount === 'string' ? Number.parseFloat(amount) : amount
    return num.toFixed(2)
  }

  onMounted(() => {
    updateNumTransactions()
  })
</script>
