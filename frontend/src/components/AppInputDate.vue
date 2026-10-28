<script setup lang="ts">
import {  getLocalTimeZone, today, parseDate, DateValue } from '@internationalized/date'
import { CalendarIcon } from 'lucide-vue-next'
import { computed, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { cn } from '@/lib/utils'

// Define the model for v-model support
const model = defineModel<Date | string | null>({ default: null })

// Define props for custom formatting
const props = defineProps({
  labelFormat: {
    type: String,
    default: 'dd MMM yyyy' // Default to day month year format
  },
  valueFormat: {
    type: String,
    default: 'yyyy-MM-dd' // Default to ISO format
  },
  useFormattedValue: {
    type: Boolean,
    default: true // When true, v-model will use the formatted value
  },
  // error message, optional
  error: { type: String, default: '' },
})

// Convert the model value to a DateValue for the calendar component
const dateValue = computed<DateValue | undefined>({
  get() {
    if (!model.value) return undefined

    let date: Date;
    if (props.useFormattedValue && typeof model.value === 'string') {
      // If using formatted value and model is a string, parse it back to a date
      const [year, month, day] = model.value.split('-').map(Number);
      date = new Date(year, month - 1, day);
    } else if (model.value instanceof Date) {
      date = model.value;
    } else {
      return undefined;
    }

    // Use local date string instead of ISO string to avoid timezone issues
    const localDateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
    return parseDate(localDateStr)
  },
  set(value) {
    if (value) {
      // Convert DateValue to JavaScript Date
      const date = new Date(value.year, value.month - 1, value.day)

      if (props.useFormattedValue) {
        // If using formatted value, set the model to the formatted string
        const formatted = formatValue(date);
        model.value = formatted;
      } else {
        // Otherwise, set the model to the Date object
        model.value = date;
      }
    } else {
      model.value = null
    }
  }
})

// Helper function to format date according to valueFormat
const formatValue = (date: Date | null) => {
  if (!date) return null;

  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Month is 0-indexed
  const year = date.getFullYear();

  return props.valueFormat
    .replace('dd', day)
    .replace('MM', month)
    .replace('yyyy', year.toString());
}

// Format the date for display in the button
const formattedDate = computed(() => {
  if (!model.value) return 'Pilih Tanggal'

  let date: Date;
  if (typeof model.value === 'string') {
    // If model is a string (when useFormattedValue is true), parse it back to a date for display formatting
    const [year, month, day] = model.value.split('-').map(Number);
    date = new Date(year, month - 1, day);
  } else if (model.value instanceof Date) {
    date = model.value;
  } else {
    return 'Pilih Tanggal';
  }

  // Format based on labelFormat prop
  const day = date.getDate().toString().padStart(2, '0')
  const month = date.toLocaleDateString('id-ID', { month: 'short' }) // Indonesian short month
  const year = date.getFullYear()

  // Simple replacement for now - in a real app you might want a more robust date formatting library
  return props.labelFormat
    .replace('dd', day)
    .replace('MMM', month)
    .replace('yyyy', year.toString())
})

// Format the date for value output
const formattedValue = computed(() => {
  if (!model.value) return null

  if (model.value instanceof Date) {
    return formatValue(model.value);
  } else if (typeof model.value === 'string') {
    // If model is already a string (when useFormattedValue is true), return it
    return model.value;
  }
  return null;
})

// Define an emit for the formatted value
const emit = defineEmits(['formatted-value-change'])

// Watch for changes in the formatted value and emit when it changes
watch(formattedValue, (newVal) => {
  emit('formatted-value-change', newVal)
})

const defaultPlaceholder = today(getLocalTimeZone())
</script>

<template>
  <div class="relative">
    <Popover>
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        :class="cn(
          'w-full justify-start text-left font-normal',
          !model && 'text-muted-foreground',
        )"
      >
        <CalendarIcon class="mr-2 h-4 w-4" />
        {{ formattedDate }}
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0">
      <Calendar
        v-model="dateValue"
        :initial-focus="true"
        :default-placeholder="defaultPlaceholder"
        layout="month-and-year"
      />
    </PopoverContent>
  </Popover>
      <!-- Error text -->
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>
