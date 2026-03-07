import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const drawer = ref(true)

  const toggleDrawer = () => {
    drawer.value = !drawer.value
  }

  return { drawer, toggleDrawer }
})
