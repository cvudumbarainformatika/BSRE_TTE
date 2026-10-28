<script setup>
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Konfirmasi' },
  description: { type: String, default: '' },
  item: { type: Object, default: null },
  maxWidth: { type: String, default: 'sm:max-w-lg' },
  confirmText: { type: String, default: 'Lanjutkan' },
  cancelText: { type: String, default: 'Batal' },
  confirmDisabled: { type: Boolean, default: false },
  hideFooter: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

function close() {
  emit('update:modelValue', false)
}
function onConfirm() {
  emit('confirm', props.item)
}
function onCancel() {
  emit('cancel')
  close()
}
</script>

<template>
  <Dialog
    :open="modelValue"
    @update:open="emit('update:modelValue', $event)"
  >
    <DialogContent :class="['bg-white text-slate-800', maxWidth]">
      <DialogHeader>
        <DialogTitle class="text-base font-bold text-slate-900">
          <slot name="title">{{ title }}</slot>
        </DialogTitle>
        <DialogDescription v-if="description || $slots.description" class="text-xs text-slate-500">
          <slot name="description">{{ description }}</slot>
        </DialogDescription>
      </DialogHeader>

      <div v-if="$slots.default" class="py-2">
        <slot />
      </div>

      <DialogFooter v-if="!hideFooter" class="gap-2">
        <slot name="footer" :close="close" :onCancel="onCancel" :onConfirm="onConfirm">
          <Button variant="outline" size="sm" @click="onCancel">
            {{ cancelText }}
          </Button>
          <Button size="sm" :disabled="confirmDisabled" @click="onConfirm">
            {{ confirmText }}
          </Button>
        </slot>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
