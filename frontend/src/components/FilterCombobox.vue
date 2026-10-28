<template>
  <Popover v-model:open="open">
    <PopoverTrigger asChild>
      <Button
        variant="outline"
        role="combobox"
        :aria-expanded="open"
        class="w-full justify-between font-normal bg-background !bg-background px-3 py-2 text-sm border-input h-10 shadow-sm transition-colors"
        :disabled="disabled"
      >
        <span class="truncate">{{ selectedLabel }}</span>
        <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>
    <PopoverContent 
      class="combobox-popover p-0 overflow-hidden" 
      align="start" 
      :style="{ width: 'var(--reka-popover-trigger-width)' }"
    >
      <!-- Search bar: hanya tampil jika opsi > threshold -->
      <div v-if="showSearch" class="combobox-search-wrapper">
        <Search class="combobox-search-icon" />
        <input 
          ref="searchInput"
          v-model="searchQuery" 
          :placeholder="searchPlaceholder"
          type="text"
          class="combobox-search-input"
          @keydown.up.prevent="moveActive(-1)"
          @keydown.down.prevent="moveActive(1)"
          @keydown.enter.prevent="selectActive"
          @keydown.esc="open = false"
        />
      </div>

      <!-- Options list -->
      <div class="combobox-list">
        <!-- Default "Semua" option -->
        <div 
          v-if="showAll"
          class="combobox-item"
          :class="{ 
            'combobox-item--selected': modelValue === '',
            'combobox-item--active': activeIndex === -1
          }"
          @click="handleSelect('')"
          @mouseenter="activeIndex = -1"
        >
          <span>{{ defaultOptionText }}</span>
          <Check v-if="modelValue === ''" class="combobox-check-icon" />
        </div>

        <!-- Filtered options -->
        <template v-if="filteredOptions.length > 0">
          <div 
            v-for="(opt, i) in filteredOptions"
            :key="getOptionValue(opt)"
            class="combobox-item"
            :class="{ 
              'combobox-item--selected': modelValue === getOptionValue(opt),
              'combobox-item--active': activeIndex === i
            }"
            @click="handleSelect(getOptionValue(opt))"
            @mouseenter="activeIndex = i"
          >
            <span>{{ getOptionLabel(opt) }}</span>
            <Check v-if="modelValue === getOptionValue(opt)" class="combobox-check-icon" />
          </div>
        </template>

        <!-- Empty state -->
        <div v-else class="combobox-empty">
          {{ emptyText }}
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Check, ChevronsUpDown, Search } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Pilih...' },
  searchPlaceholder: { type: String, default: 'Cari...' },
  defaultOptionText: { type: String, default: 'Semua' },
  emptyText: { type: String, default: 'Tidak ditemukan.' },
  disabled: { type: Boolean, default: false },
  searchThreshold: { type: Number, default: 6 },
  showAll: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'change'])

const open = ref(false)
const searchQuery = ref('')
const activeIndex = ref(-1) // -1 = default "Semua" option
const searchInput = ref(null)

// Tampilkan search bar hanya jika opsi > searchThreshold
const showSearch = computed(() => props.options.length > props.searchThreshold)

function getOptionValue(opt) { return typeof opt === 'object' ? opt.value : opt }
function getOptionLabel(opt) { return typeof opt === 'object' ? opt.label : opt }

// Deduplicated & filtered options
const filteredOptions = computed(() => {
  const seen = new Set()
  return (props.options || []).filter(opt => {
    const label = getOptionLabel(opt)
    const value = String(getOptionValue(opt))
    if (seen.has(value)) return false
    seen.add(value)
    if (!searchQuery.value) return true
    return label.toLowerCase().includes(searchQuery.value.toLowerCase())
  })
})

const selectedLabel = computed(() => {
  if (!props.modelValue) {
    return props.showAll ? props.defaultOptionText : props.placeholder
  }
  
  // Pencarian yang lebih fleksibel (case-insensitive)
  const valStr = String(props.modelValue).toLowerCase()
  const option = props.options.find(opt => {
    const optVal = String(getOptionValue(opt)).toLowerCase()
    return optVal === valStr
  })
  
  return option ? getOptionLabel(option) : (props.modelValue || props.placeholder)
})

// Move highlight up/down with keyboard
function moveActive(dir) {
  const max = filteredOptions.value.length - 1
  if (dir === -1) {
    activeIndex.value = activeIndex.value <= -1 ? max : activeIndex.value - 1
  } else {
    activeIndex.value = activeIndex.value >= max ? -1 : activeIndex.value + 1
  }
}

// Select the currently highlighted item
function selectActive() {
  if (activeIndex.value === -1) {
    handleSelect('')
  } else if (filteredOptions.value[activeIndex.value]) {
    handleSelect(getOptionValue(filteredOptions.value[activeIndex.value]))
  }
}

function handleSelect(val) {
  emit('update:modelValue', val)
  emit('change', val)
  searchQuery.value = ''
  activeIndex.value = -1
  open.value = false
}

// Focus search input when opened, reset state when closed
watch(open, (val) => {
  if (val) {
    activeIndex.value = -1
    searchQuery.value = ''
    nextTick(() => searchInput.value?.focus())
  }
})

// Reset active when search changes
watch(searchQuery, () => { activeIndex.value = -1 })
</script>

<style scoped>
.combobox-search-wrapper {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  border-bottom: 1px solid hsl(var(--border, 214.3 31.8% 91.4%));
  padding: 8px 12px;
  gap: 8px;
}

.combobox-search-icon {
  width: 14px !important;
  height: 14px !important;
  flex-shrink: 0 !important;
  opacity: 0.5;
  display: block !important;
}

.combobox-search-input {
  flex: 1 !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  background: transparent !important;
  font-size: 0.875rem !important;
  line-height: 1.25rem !important;
  padding: 0 !important;
  margin: 0 !important;
  color: inherit !important;
  min-width: 0 !important;
  -webkit-appearance: none !important;
  appearance: none !important;
}

.combobox-list {
  max-height: 240px;
  overflow-y: auto;
}

.combobox-item {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 7px 12px !important;
  font-size: 0.875rem !important;
  cursor: pointer !important;
  transition: background-color 0.1s ease !important;
  background-color: transparent !important;
  border-radius: 0 !important;
}

.combobox-item:hover,
.combobox-item--active {
  background-color: hsl(var(--accent, 210 40% 96.1%)) !important;
  color: hsl(var(--accent-foreground, 222.2 47.4% 11.2%)) !important;
}

.combobox-item--selected {
  font-weight: 500;
}

.combobox-check-icon {
  width: 14px !important;
  height: 14px !important;
  flex-shrink: 0;
  opacity: 0.7;
}

.combobox-empty {
  padding: 16px 12px;
  font-size: 0.875rem;
  text-align: center;
  color: hsl(var(--muted-foreground, 215.4 16.3% 46.9%));
}
</style>
