<template>
  <v-dialog :max-width="maxWidth" :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)">
    <v-card>
      <v-card-title class="pt-3">
        <span class="text-h5">{{ dialogTitle }}</span>
      </v-card-title>

      <v-card-text>
        <slot />
      </v-card-text>

      <v-card-actions>
        <template v-if="editing">
          <v-btn
            v-if="!confirmingDelete"
            color="error"
            variant="text"
            @click="confirmingDelete = true"
          >
            Delete
          </v-btn>
          <template v-else>
            <v-btn color="grey" variant="text" @click="confirmingDelete = false">Cancel</v-btn>
            <v-btn color="error" :loading="deleting" variant="text" @click="$emit('delete')">Confirm Delete</v-btn>
          </template>
        </template>
        <v-spacer />
        <v-btn color="grey" @click="close">Cancel</v-btn>
        <v-btn color="primary" :disabled="saveDisabled" :loading="saving" @click="$emit('save')">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue'

  const props = withDefaults(defineProps<{
    modelValue: boolean
    editing: boolean
    entityName: string
    saveDisabled?: boolean
    saving?: boolean
    deleting?: boolean
    maxWidth?: string
  }>(), {
    saveDisabled: false,
    saving: false,
    deleting: false,
    maxWidth: '500px',
  })

  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
    'save': []
    'delete': []
  }>()

  const confirmingDelete = ref(false)

  const dialogTitle = computed(() =>
    props.editing ? `Edit ${props.entityName}` : `New ${props.entityName}`,
  )

  function close () {
    confirmingDelete.value = false
    emit('update:modelValue', false)
  }

  watch(() => props.modelValue, open => {
    if (open) {
      confirmingDelete.value = false
    }
  })
</script>
