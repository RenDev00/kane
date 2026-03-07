<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-nav-icon @click="appStore.toggleDrawer()" />
      <v-toolbar-title>Kane</v-toolbar-title>
      <v-chip class="mr-4" color="red" variant="flat">Demo</v-chip>
    </v-app-bar>

    <v-navigation-drawer v-model="appStore.drawer">
      <v-list>
        <v-list-item to="/dashboard">
          <template #prepend>
            <v-icon>mdi-view-dashboard</v-icon>
          </template>
          <v-list-item-title>Dashboard</v-list-item-title>
        </v-list-item>

        <v-list-item to="/transactions">
          <template #prepend>
            <v-icon>mdi-swap-horizontal</v-icon>
          </template>
          <v-list-item-title>Transactions</v-list-item-title>
        </v-list-item>
      </v-list>

      <template #append>
        <v-list>
          <v-list-item to="/settings">
            <template #prepend>
              <v-icon>mdi-cog</v-icon>
            </template>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
        </v-list>
      </template>

    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
  import { useAppStore } from '@/stores/app'

  const appStore = useAppStore()
</script>
