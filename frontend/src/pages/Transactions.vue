<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center" cols="12">
        <h1>Transactions</h1>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          New
        </v-btn>
      </v-col>
    </v-row>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      hover
      item-value="id"
      :items="transactionStore.getTableTransactions"
      :items-length="statsStore.getCurrentNumTransactions"
      :items-per-page-options="[10]"
      :loading="transactionStore.loading"
      @click:row="(_event: Event, row: any) => openEditDialog(row.item)"
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

    <crud-dialog
      v-model="dialog"
      :deleting="deleting"
      :editing="!!editingId"
      entity-name="Transaction"
      :save-disabled="!formValid"
      :saving="saving"
      @delete="deleteTransaction"
      @save="saveTransaction"
    >
      <v-form ref="formRef" v-model="formValid" @submit.prevent="saveTransaction">
        <v-row>
          <v-col cols="12">
            <v-select
              v-model="form.type"
              :items="typeOptions"
              label="Type"
              required
              :rules="[v => !!v || 'Type is required']"
              @update:model-value="form.category = categoryOptions[0]!"
            />
          </v-col>
          <v-col cols="12">
            <v-select
              v-model="form.category"
              :disabled="!form.type"
              :items="categoryOptions"
              label="Category"
              required
              :rules="[v => !!v || 'Category is required']"
            />
          </v-col>
          <v-col cols="12">
            <v-number-input
              v-model="form.amount"
              inset
              label="Amount"
              :min="0"
              :precision="2"
              required
              :rules="[
                v => v != null || 'Amount is required',
                v => v >= 0 || 'Invalid amount'
              ]"
            />
          </v-col>
          <v-col cols="12">
            <v-text-field
              label="Date & Time"
              :model-value="dialogDateTimeString"
              readonly
              required
              :rules="[v => !!v || 'Date is required']"
            >
              <template #append-inner>
                <v-menu v-model="dateMenu" :close-on-content-click="false">
                  <template #activator="{ props }">
                    <v-btn v-bind="props" icon="mdi-calendar" size="small" variant="text" />
                  </template>
                  <v-date-picker v-model="selectedDate" @update:model-value="dateMenu = false" />
                </v-menu>
                <v-menu v-model="timeMenu" :close-on-content-click="false">
                  <template #activator="{ props }">
                    <v-btn v-bind="props" icon="mdi-clock" size="small" variant="text" />
                  </template>
                  <v-time-picker v-model="selectedTime" format="24hr" @update:minute="timeMenu = false" />
                </v-menu>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field v-model="form.comment" label="Comment (Optional)" />
          </v-col>
        </v-row>
      </v-form>
    </crud-dialog>
  </v-container>
</template>

<script lang="ts" setup>
  import type { NumTransactionsFilters } from '@/types/stats'
  import type { CreateTransactionRequest, Transaction, TransactionCategory, TransactionType, UpdateTransactionRequest } from '@/types/transaction'
  import { TZDate } from '@date-fns/tz'
  import { format } from 'date-fns'
  import { computed, onMounted, ref } from 'vue'
  import CrudDialog from '@/components/CrudDialog.vue'
  import { useStatsStore } from '@/stores/stats'
  import { useTransactionStore } from '@/stores/transaction'

  const transactionStore = useTransactionStore()
  const statsStore = useStatsStore()
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone

  const currentPage = ref(1)
  const itemsPerPage = ref(10)

  const headers = [
    { title: 'No.', key: 'no', sortable: false },
    { title: 'Date', key: 'date', cellProps: { class: 'd-none d-sm-table-cell' }, headerProps: { class: 'd-none d-sm-table-cell' }, sortable: false },
    { title: 'Type', key: 'type', sortable: false },
    { title: 'Category', key: 'category', sortable: false },
    { title: 'Amount', key: 'amount', sortable: false },
    { title: 'Comment', key: 'comment', cellProps: { class: 'd-none d-sm-table-cell' }, headerProps: { class: 'd-none d-sm-table-cell' }, sortable: false },
  ]

  const typeOptions: TransactionType[] = ['INCOME', 'EXPENSE']
  const incomeCategories: TransactionCategory[] = ['SALARY', 'OTHER']
  const expenseCategories: TransactionCategory[] = ['NEED', 'WANT', 'SAVING']

  const categoryOptions = computed<TransactionCategory[]>(() => {
    if (form.value.type === 'INCOME') return incomeCategories
    if (form.value.type === 'EXPENSE') return expenseCategories
    return []
  })

  const dialog = ref(false)
  const dateMenu = ref(false)
  const timeMenu = ref(false)
  const formRef = ref()
  const formValid = ref(false)
  const saving = ref(false)
  const deleting = ref(false)
  const editingId = ref<number | null>(null)

  const form = ref<CreateTransactionRequest>({
    amount: 0,
    date: '',
    type: 'EXPENSE',
    category: 'NEED',
    comment: '',
  })

  const selectedDate = ref<Date>(new Date())
  const selectedTime = ref<string>('12:00')

  const dialogDateTimeString = computed(() => {
    const dateStr = format(selectedDate.value, 'yyyy-MM-dd')
    return `${dateStr} ${selectedTime.value}`
  })

  function getApiDateString (): string {
    const dateStr = format(selectedDate.value, 'yyyy-MM-dd')
    const tzDate = new TZDate(`${dateStr}T${selectedTime.value}:00`, timeZone)
    return tzDate.toISOString()
  }

  function setLocalDateTimeFromUtc (utcStr: string) {
    const tzDate = new TZDate(utcStr, timeZone)
    selectedDate.value = new Date(format(tzDate, 'yyyy-MM-dd'))
    selectedTime.value = format(tzDate, 'HH:mm')
  }

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

  function openCreateDialog () {
    editingId.value = null
    const now = new Date()
    selectedDate.value = now
    selectedTime.value = format(now, 'HH:mm')
    form.value = {
      amount: 0,
      date: '',
      type: 'EXPENSE',
      category: 'NEED',
      comment: '',
    }
    dialog.value = true
  }

  function openEditDialog (transaction: Transaction) {
    editingId.value = transaction.id
    setLocalDateTimeFromUtc(transaction.date)
    form.value = {
      amount: Number.parseFloat(transaction.amount),
      date: '',
      type: transaction.type.toUpperCase() as TransactionType,
      category: transaction.category.toUpperCase() as TransactionCategory,
      comment: transaction.comment || '',
    }
    dialog.value = true
  }

  function closeDialog () {
    dialog.value = false
    dateMenu.value = false
    timeMenu.value = false
    formRef.value?.reset()
  }

  async function saveTransaction () {
    if (!formValid.value) return

    saving.value = true
    try {
      const apiDate = getApiDateString()
      if (editingId.value) {
        const updateData: UpdateTransactionRequest = {
          amount: form.value.amount,
          date: apiDate,
          type: form.value.type,
          category: form.value.category,
          comment: form.value.comment,
        }
        await transactionStore.updateTransaction(editingId.value, updateData)
      } else {
        const createData: CreateTransactionRequest = {
          amount: form.value.amount,
          date: apiDate,
          type: form.value.type,
          category: form.value.category,
          comment: form.value.comment,
        }
        await transactionStore.createTransaction(createData)
      }
      closeDialog()
      await refreshTable()
    } finally {
      saving.value = false
    }
  }

  async function deleteTransaction () {
    if (!editingId.value) return

    deleting.value = true
    try {
      await transactionStore.deleteTransaction(editingId.value)
      closeDialog()
      await refreshTable()
    } finally {
      deleting.value = false
    }
  }

  async function refreshTable () {
    await transactionStore.fetchTableTransactions({ page: currentPage.value, limit: itemsPerPage.value })
    await updateNumTransactions()
  }

  onMounted(() => {
    updateNumTransactions()
  })
</script>
