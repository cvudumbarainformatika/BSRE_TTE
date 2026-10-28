<template>
  <!-- <div class="flex-1 space-y-4 "> -->
     <Tabs
      v-if="tabs && tabs.length > 0"
      :default-value="defaultTab"
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
  <!-- </div> -->
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

const props = defineProps({
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

const emit = defineEmits(['tab-change'])

const onTabChange = (value) => {
  emit('tab-change', value)
}
</script>