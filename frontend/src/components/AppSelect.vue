<template>
  <div class="space-y-1">
    <Label v-if="label" :for="id" class="text-xs font-bold text-slate-700">{{ label }}</Label>

    <Select
      :disabled="disabled"
      :model-value="modelValue"
      @update:model-value="emit('update:modelValue', $event)"
    >
      <SelectTrigger
        :id="id"
        :class="['w-full bg-background', { 'border-destructive': !!error }]"
        :disabled="disabled"
      >
        <SelectValue :placeholder="placeholder || 'Pilih...'" />
      </SelectTrigger>

      <SelectContent>
        <SelectItem v-if="isNoData" :value="noDataValue">
          {{ noDataText }}
        </SelectItem>

        <SelectItem
          v-for="item in options"
          :key="optionKey ? item[optionKey] : getValue(item)"
          :value="getValue(item)"
          :disabled="isDisabled(item)"
        >
          {{ getItemText(item) }}
        </SelectItem>
      </SelectContent>
    </Select>

    <p v-if="error" class="text-xs text-destructive">{{ error }}</p>
  </div>
</template>

<script setup>
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'

const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, default: '' },
  modelValue: { type: [String, Number, Object, Array], default: null },
  placeholder: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  textKey: { type: String, default: 'text' },
  valueKey: { type: String, default: 'value' },
  optionKey: { type: String, default: null },
  isNoData: { type: Boolean, default: false },
  noDataValue: { type: [String, Number], default: 0 },
  noDataText: { type: [String, Number], default: 'Tidak Ada Data' },
  disabled: { type: Boolean, default: false },
  disableOption: { type: [String, Number], default: null },
  disableOptions: { type: Array, default: () => [] },
  error: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const getValue = (item) => {
  if (item === null || item === undefined) return ''
  if (typeof item !== 'object') return item
  return props.valueKey && item[props.valueKey] !== undefined
    ? item[props.valueKey]
    : item
}

const getItemText = (item) => {
  if (item === null || item === undefined) return 'Tidak Ada'
  if (typeof item !== 'object') return String(item)
  return props.textKey && item[props.textKey] !== undefined
    ? item[props.textKey]
    : String(item)
}

const isDisabled = (item) => {
  const value = getValue(item)
  return value === props.disableOption || props.disableOptions.includes(value)
}
</script>
