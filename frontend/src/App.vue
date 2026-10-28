<template>
  <router-view />
  <Notification />
</template>

<script setup lang="ts">
// Main app component - Quasar handles the routing
import Notification from '@/components/ui/Notification.vue'
</script>