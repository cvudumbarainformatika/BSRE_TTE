<template>
  <div class="space-y-1">
    <div v-if="label || $slots['label-right']" class="flex items-center justify-between">
      <Label v-if="label" :for="id" class="text-xs font-bold text-slate-700 dark:text-slate-200">{{ label }}</Label>
      <slot name="label-right" />
    </div>

    <div class="relative">
      <div v-if="$slots.prefix" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
        <slot name="prefix" />
      </div>

      <Input
        :id="id"
        v-bind="computedAttrs"
        :type="type"
        :placeholder="placeholder"
        v-model="localValue"
        :class="[
          'bg-background text-foreground font-medium placeholder:font-normal placeholder:text-muted-foreground/50',
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
import { computed, useAttrs } from 'vue'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const attrs = useAttrs()

const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' }
})

// Ketentuan Poin 4 Audit BSrE BSSN: Passphrase / password wajib bebas dari web cache browser
const computedAttrs = computed(() => {
  if (props.type === 'password') {
    return {
      autocomplete: 'new-password',
      autocorrect: 'off',
      autocapitalize: 'off',
      spellcheck: 'false',
      ...attrs
    }
  }
  return attrs
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
