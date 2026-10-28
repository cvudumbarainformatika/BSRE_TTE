<template>
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
</template>

<script setup>
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  tabs: {
    type: Array,
    default: () => []
  },
  defaultTab: {
    type: String,
    default: () => 'master'
  },
  isHideTabs: {
    type: Boolean,
    default: () => false
  }
})

const emit = defineEmits(['update:modelValue', 'tab-change'])

const onTabChange = (value) => {
  emit('update:modelValue', value)
  emit('tab-change', value)
}
</script>