<script setup>
import { ref, computed } from 'vue'
import { Check, ChevronsUpDown } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: null
  },
  options: {
    type: Array,
    default: () => []
  },
  optionKey: {
    type: String,
    required: true
  },
  valueKey: {
    type: String,
    required: true
  },
  textKey: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Pilih...'
  },
  searchPlaceholder: {
    type: String,
    default: 'Cari...'
  }
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)

const selectedLabel = computed(() => {
  if (!props.modelValue) return props.placeholder
  const selected = props.options.find(item => item[props.valueKey] === props.modelValue)
  return selected ? selected[props.textKey] : props.placeholder
})

const onSelect = (item) => {
  emit('update:modelValue', item[props.valueKey])
  open.value = false
}
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        role="combobox"
        :aria-expanded="open"
        class="w-full justify-between font-normal px-3"
        :class="[!modelValue && 'text-muted-foreground']"
      >
        <span class="truncate flex-1 text-left">{{ selectedLabel }}</span>
        <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="p-0" align="start" :style="{ width: 'var(--radix-popper-anchor-width)' }">
      <Command>
        <CommandInput 
          :placeholder="searchPlaceholder" 
          class="h-9 border-none focus:ring-0" 
        />
        <CommandEmpty>Tidak ditemukan.</CommandEmpty>
        <CommandList>
          <CommandGroup>
            <CommandItem
              v-for="item in options"
              :key="item[optionKey]"
              :value="item[textKey]"
              @select="onSelect(item)"
              class="cursor-pointer"
            >
              {{ item[textKey] }}
              <Check
                :class="cn(
                  'ml-auto h-4 w-4',
                  modelValue === item[valueKey] ? 'opacity-100' : 'opacity-0'
                )"
              />
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>

<style scoped>
/* Force flex layout on CommandInput wrapper to fix broken icon alignment */
:deep([cmdk-input-wrapper]) {
  display: flex !important;
  align-items: center !important;
}

/* Hide Search Icon inside CommandInput */
:deep([cmdk-input-wrapper] svg) {
  display: none !important;
}

/* Add hover highlight effect for dropdown items */
:deep([role="option"]:hover) {
  background-color: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}

/* Ensure proper cursor on items */
:deep([role="option"]) {
  cursor: pointer;
}
</style>
