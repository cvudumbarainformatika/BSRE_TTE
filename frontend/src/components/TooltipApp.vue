<template>
  <TooltipProvider variant="custom" :delay-duration="delayDuration" 
    style="--popover: 0 0% 10%; --popover-foreground: 0 0% 100%;"
  >
    <Tooltip>
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipContent class="relative text-foreground bg-primary/50 px-3 py-1">
        <p>{{ label }}</p>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
</template>

<script setup>
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '@/components/ui/tooltip'
const props = defineProps({
  delayDuration: {
    type: Number,
    default: 200
  },
  label: {
    type: String,
    default: ''
  }
  
})
</script>

<style scoped>

</style>