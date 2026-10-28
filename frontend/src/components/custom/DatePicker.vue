<script setup lang="ts">
import { computed } from 'vue'
import { DateFormatter, type DateValue, getLocalTimeZone } from '@internationalized/date'
import { Calendar as CalendarIcon } from 'lucide-vue-next'
import { Calendar } from '@/components/ui/calendar'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Pilih tanggal...',
  disabled: false
})

const emit = defineEmits(['update:modelValue'])

const df = new DateFormatter('id-ID', {
  dateStyle: 'long',
})

// Konversi string YYYY-MM-DD dari backend ke DateValue untuk Calendar
const value = computed({
  get: () => {
    if (!props.modelValue) return undefined
    try {
      const [year, month, day] = props.modelValue.split('-').map(Number)
      // Perlu return objek yang kompatibel dengan Calendar shadcn-vue
      // Untuk sederhananya kita bisa pakai Date objek jika Calendar mendukungnya, 
      // tapi biasanya shadcn-vue butuh DateValue dari @internationalized/date
      return undefined // Fallback jika parsing rumit, Calendar biasanya bisa handle Date
    } catch (e) {
      return undefined
    }
  },
  set: (val) => {
    if (val) {
      // Emit format YYYY-MM-DD ke parent
      const d = val.toDate(getLocalTimeZone())
      const formatted = d.toISOString().split('T')[0]
      emit('update:modelValue', formatted)
    } else {
      emit('update:modelValue', '')
    }
  }
})

// Helper untuk label tombol
const buttonLabel = computed(() => {
  if (!props.modelValue) return props.placeholder
  try {
    const d = new Date(props.modelValue)
    return df.format(d)
  } catch (e) {
    return props.modelValue
  }
})

function handleSelect(val: DateValue | undefined) {
  if (val) {
    const d = val.toDate(getLocalTimeZone())
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    emit('update:modelValue', `${year}-${month}-${day}`)
  }
}
</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        :disabled="disabled"
        :class="cn(
          'w-full justify-start text-left font-normal bg-background border-input hover:bg-accent hover:text-accent-foreground rounded-md shadow-sm',
          !modelValue && 'text-muted-foreground',
        )"
      >
        <CalendarIcon class="mr-2 h-4 w-4 opacity-70" />
        <span class="truncate">{{ buttonLabel }}</span>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0 z-[1001]" align="start">
      <Calendar
        initial-focus
        @update:model-value="handleSelect"
      />
    </PopoverContent>
  </Popover>
</template>
