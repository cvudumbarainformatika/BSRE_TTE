<template>
  <div :class="cn(badgeVariants({ variant }), $attrs.class ?? '')">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => {
      return ['default', 'secondary', 'outline', 'destructive', 'success', 'warning', 'info'].includes(value)
    }
  }
})

const badgeVariants = computed(() => {
  return ({
    variant = 'default'
  }) => {
    const variantClasses = {
      default: 'bg-primary text-primary-foreground hover:bg-primary/80 border-transparent',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border-transparent',
      destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/80 border-transparent',
      success: 'bg-emerald-500 text-white hover:bg-emerald-600 border-transparent',
      warning: 'bg-amber-500 text-white hover:bg-amber-600 border-transparent',
      info: 'bg-sky-500 text-white hover:bg-sky-600 border-transparent',
      outline: 'text-foreground border'
    }

    return [
      'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
      variantClasses[variant] || variantClasses.default
    ].filter(Boolean).join(' ')
  }
})
</script>