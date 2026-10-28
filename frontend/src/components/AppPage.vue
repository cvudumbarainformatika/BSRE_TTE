<template>
  <div class="flex-1 space-y-4 md:px-8">
    <!-- Header Section -->
    <div class="flex items-center justify-between space-y-2">
      <div class="flex items-center space-x-2">
        <slot name="header-actions" />
      </div>
      <div class="text-right">
        <h2 class="text-3xl font-bold tracking-tight">{{ title }}</h2>
        <p class="text-muted-foreground text-xs">{{ description }}</p>
      </div>
      
    </div>

    <!-- Tabs Section -->
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

    <!-- Content without tabs -->
    <div v-else class="space-y-4">
      <slot />
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

// Props untuk konfigurasi halaman
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: '0000'
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

// Definisikan emit untuk menyampaikan perubahan tab ke parent
const emit = defineEmits(['tab-change'])

// Fungsi untuk menangani perubahan tab
const onTabChange = (value) => {
  emit('tab-change', value)
}
</script>