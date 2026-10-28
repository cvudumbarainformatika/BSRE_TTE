<template>
  <div class="flex-1 space-y-6 w-full text-foreground relative">
    <!-- Overlay Loading Global Ketika props :loading = true -->
    <div
      v-if="loading"
      class="rounded-2xl glass-panel p-12 flex flex-col items-center justify-center space-y-4 my-6 border border-border"
    >
      <div class="relative w-12 h-12">
        <div class="absolute inset-0 rounded-full border-2 border-primary/20 animate-ping"></div>
        <div class="w-12 h-12 rounded-full border-2 border-t-primary border-r-transparent border-b-primary border-l-transparent animate-spin"></div>
      </div>
      <div class="text-sm font-medium text-foreground tracking-wide">
        {{ loadingText || 'Memuat data sistem...' }}
      </div>
      <div class="text-xs text-muted-foreground font-mono">
        BSrE Microservice Sync & Encryption
      </div>
    </div>

    <!-- Konten Utama Halaman -->
    <div v-show="!loading" class="space-y-6">
      <!-- Header Section Opsional -->
      <div
        v-if="title || $slots['header-actions']"
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border"
      >
        <div>
          <h2 v-if="title" class="text-2xl font-bold tracking-tight text-foreground">{{ title }}</h2>
          <p v-if="description" class="text-xs text-muted-foreground mt-0.5">{{ description }}</p>
        </div>
        <div v-if="$slots['header-actions']" class="flex items-center gap-2">
          <slot name="header-actions" />
        </div>
      </div>

      <!-- Tabs Section (Jika disediakan prop tabs) -->
      <Tabs
        v-if="tabs && tabs.length > 0"
        :model-value="modelValue || defaultTab"
        class="space-y-4"
        @update:model-value="onTabChange"
      >
        <TabsList :class="isHideTabs ? 'hidden' : ''">
          <TabsTrigger
            v-for="tab in tabs"
            :key="tab.value"
            :value="tab.value"
            :disabled="tab.disabled"
          >
            {{ tab.label }}
          </TabsTrigger>
        </TabsList>

        <TabsContent
          v-for="tab in tabs"
          :key="tab.value"
          :value="tab.value"
          class="space-y-4"
        >
          <slot :name="tab.value" :tab-data="tab.data" />
        </TabsContent>
      </Tabs>

      <!-- Slot Default Tanpa Tabs (Macro Layout Konten Penuh) -->
      <div v-else class="space-y-6">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Memproses data...'
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  tabs: {
    type: Array,
    default: () => []
  },
  defaultTab: {
    type: String,
    default: ''
  },
  modelValue: {
    type: String,
    default: ''
  },
  isHideTabs: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['tab-change'])

const onTabChange = (value) => {
  emit('tab-change', value)
}
</script>