<template>
  <div class="space-y-1">
    <div v-if="label || $slots['label-right']" class="flex items-center justify-between">
      <Label v-if="label" :for="computedId" class="text-xs font-bold text-slate-700 dark:text-slate-200">{{ label }}</Label>
      <slot name="label-right" />
    </div>

    <div class="relative">
      <div v-if="$slots.prefix" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
        <slot name="prefix" />
      </div>

      <Input
        :id="computedId"
        :name="computedName"
        v-bind="computedAttrs"
        :type="computedType"
        :placeholder="placeholder"
        :style="computedStyle"
        v-model="localValue"
        :class="[
          'bg-background text-foreground font-medium placeholder:font-normal placeholder:text-muted-foreground/50',
          $attrs.class,
          { 
            'pl-9': !!$slots.prefix, 
            'pr-10': !!$slots.suffix || isSecret, 
            'border-destructive': !!error 
          }
        ]"
      />

      <div v-if="$slots.suffix" class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400">
        <slot name="suffix" />
      </div>

      <!-- Built-in Toggle Show/Hide untuk Passphrase (Anti-Password-Manager Browser) -->
      <button
        v-else-if="isSecret"
        type="button"
        class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors focus:outline-none"
        @click="isMasked = !isMasked"
        tabindex="-1"
        :title="isMasked ? 'Lihat Passphrase' : 'Sembunyikan Passphrase'"
      >
        <EyeOff v-if="isMasked" class="w-4 h-4" />
        <Eye v-else class="w-4 h-4" />
      </button>
    </div>

    <p v-if="hint && !error" class="text-[11px] text-slate-500">{{ hint }}</p>
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, useAttrs } from 'vue'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Eye, EyeOff } from 'lucide-vue-next'

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

const isSecret = computed(() => {
  return props.type === 'passphrase' || props.type === 'password'
})

const isMasked = ref(true)

// Sanitasi id & name agar tidak mengandung kata kunci 'password' / 'pass'
// Ini mencegah heuristik browser password manager untuk mendeteksi field ini
const computedId = computed(() => {
  if (isSecret.value) {
    return props.id.replace(/password|passphrase/gi, 'auth_pin')
  }
  return props.id
})

const computedName = computed(() => {
  if (isSecret.value) {
    return `sec_${computedId.value}`
  }
  return props.id
})

// Mencegah deteksi browser password manager:
// Kita gunakan type='text' dan masking visual dengan -webkit-text-security: disc
// sehingga Chrome / Edge / Safari TIDAK PERNAH memunculkan dialog "Simpan Password" / autofill
const computedType = computed(() => {
  if (isSecret.value) {
    return 'text'
  }
  return props.type
})

const computedStyle = computed(() => {
  if (isSecret.value && isMasked.value) {
    return {
      WebkitTextSecurity: 'disc',
      textSecurity: 'disc'
    }
  }
  return {}
})

const computedAttrs = computed(() => {
  if (isSecret.value) {
    return {
      autocomplete: 'off',
      autocorrect: 'off',
      autocapitalize: 'off',
      spellcheck: 'false',
      'data-lpignore': 'true',
      'data-1p-ignore': 'true',
      'data-bwignore': 'true',
      'data-form-type': 'other',
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
