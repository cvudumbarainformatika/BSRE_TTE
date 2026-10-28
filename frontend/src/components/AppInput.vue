<template>
  <div class="space-y-1">
    <div v-if="label || $slots['label-right']" class="flex items-center justify-between">
      <Label v-if="label" :for="id" class="text-xs font-bold text-slate-700">{{ label }}</Label>
      <slot name="label-right" />
    </div>

    <div class="relative">
      <div v-if="$slots.prefix" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
        <slot name="prefix" />
      </div>

      <Input
        :id="id"
        v-bind="$attrs"
        :type="type"
        :placeholder="placeholder"
        v-model="localValue"
        :class="[
          $attrs.class,
          { 'pl-9': !!$slots.prefix, 'pr-10': !!$slots.suffix, 'border-destructive': !!error }
        ]"
      />

      <div v-if="$slots.suffix" class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400">
        <slot name="suffix" />
      </div>
    </div>

    <p v-if="hint && !error" class="text-[11px] text-slate-500">{{ hint }}</p>
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' }
})

const modelValue = defineModel({
  type: [String, Number, null],
  default: null
})

const localValue = computed({
  get() {
    if (props.type === 'number') {
      return props.modelValue != null ? String(props.modelValue) : ''
    }
    return props.modelValue ?? ''
  },
  set(val) {
    if (props.type === 'number') {
      const trimmedVal = String(val ?? '').trim()
      if (!trimmedVal) {
        modelValue.value = null
        return
      }
      const num = Number(trimmedVal)
      modelValue.value = isNaN(num) ? null : num
    } else {
      modelValue.value = val
    }
  }
})
</script>
