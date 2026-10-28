<template>
  <div class="space-y-1">
    <Label v-if="label" :for="id" class="text-xs font-bold text-slate-700">{{ label }}</Label>
    <Textarea
      :id="id"
      v-bind="$attrs"
      :placeholder="placeholder"
      v-model="localValue"
      :class="[$attrs.class, { 'border-destructive': !!error }]"
    />
    <p v-if="error" class="text-xs text-destructive">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const localValue = computed({
  get() {
    return props.modelValue ?? ''
  },
  set(val) {
    emit('update:modelValue', val)
  }
})
</script>
