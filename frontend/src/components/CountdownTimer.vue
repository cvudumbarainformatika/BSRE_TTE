<template>
  <div 
    :class="[
      'rounded-lg border transition-all duration-300',
      variant === 'sidebar' ? 'p-4' : 'px-3 py-1.5',
      statusClass
    ]"
  >
    <!-- Sidebar Version (Large) -->
    <div v-if="variant === 'sidebar'" class="space-y-2">
      <!-- Clock -->
      <div class="flex items-center gap-2 text-sm">
        <Clock class="h-4 w-4" />
        <span>{{ currentTime }}</span>
      </div>
      
      <!-- Status Badge -->
      <div class="flex items-center gap-2">
        <component :is="statusIcon" :class="['h-5 w-5', iconClass]" />
        <div class="flex-1">
          <div class="text-sm font-semibold">{{ statusText }}</div>
          <!-- Always show countdown during days 1-10, even if operational -->
          <div v-if="isOpen" class="text-xs text-muted-foreground mt-0.5">
            {{ daysLeft }} hari tersisa | Deadline: {{ deadlineDate }}
          </div>
        </div>
      </div>
    </div>

    <!-- Header Version (Compact) -->
    <div v-else class="flex items-center gap-2 text-xs">
      <Clock class="h-3.5 w-3.5" />
      <span class="hidden sm:inline">{{ compactDate }}</span>
      <span class="text-muted-foreground hidden sm:inline">|</span>
      <component :is="statusIcon" :class="['h-3.5 w-3.5', iconClass]" />
      <span>{{ compactStatus }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Clock, CheckCircle2, AlertTriangle, Circle } from 'lucide-vue-next'
import { useMasterStore } from '@/stores/master'

const masterStore = useMasterStore()

const props = defineProps({
  variant: {
    type: String,
    default: 'sidebar', // 'sidebar' | 'header'
    validator: (value) => ['sidebar', 'header'].includes(value)
  }
})

const now = ref(new Date())
let timer = null

// Update clock every second
const updateClock = () => {
  now.value = new Date()
}

onMounted(() => {
  timer = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// Current date/time formatting
const currentTime = computed(() => {
  return now.value.toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
})

const compactDate = computed(() => {
  return now.value.toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short'
  })
})

// Countdown logic
const currentDay = computed(() => now.value.getDate())
const deadline = 10
const daysLeft = computed(() => Math.max(0, deadline - currentDay.value))
const isOpen = computed(() => currentDay.value <= deadline)

const deadlineDate = computed(() => {
  const year = now.value.getFullYear()
  const month = now.value.getMonth()
  const deadlineDate = new Date(year, month, deadline)
  return deadlineDate.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
})

// Check if bulan or tahun is active
const hasActiveMonth = computed(() => {
  return masterStore.bulans?.some(bulan => bulan.active) || false
})

const hasActiveYear = computed(() => {
  return masterStore.tahuns?.some(tahun => tahun.active) || false
})

const isSystemOperational = computed(() => {
  return hasActiveMonth.value && hasActiveYear.value
})

// Status computed properties
const statusText = computed(() => {
  // Priority 1: If both month AND year are active → Always Operasional
  if (isSystemOperational.value) {
    return 'Operasional'
  }
  
  // Priority 2: If either month or year is NOT active → Follow countdown
  // Within deadline (1-10)
  if (isOpen.value) {
    if (daysLeft.value === 0) return 'Deadline Hari Ini'
    if (daysLeft.value <= 2) return 'Operasional (Segera Ditutup)'
    return 'Operasional'
  }
  
  // After deadline (11+) and no active month/year
  return 'Lewat Tenggat Input'
})

const compactStatus = computed(() => {
  // If system operational (both active) → Always Operasional
  if (isSystemOperational.value) {
    return 'Operasional'
  }
  
  // Follow countdown
  if (isOpen.value) {
    if (daysLeft.value <= 2) return `${daysLeft.value}h lagi`
    return 'Operasional'
  }
  
  // Not operational
  return 'Lewat Tenggat'
})

const statusIcon = computed(() => {
  // If system operational → green check
  if (isSystemOperational.value) {
    return CheckCircle2
  }
  
  // After deadline and not operational → red dot
  if (!isOpen.value) return Circle
  
  // Within deadline warning → orange triangle
  if (daysLeft.value <= 2) return AlertTriangle
  
  // Within deadline normal → green check
  return CheckCircle2
})

// Theme-based styling
const statusClass = computed(() => {
  // System operational (both active) → green
  if (isSystemOperational.value) {
    return 'bg-primary/10 border-primary/50'
  }
  
  // After deadline and not operational → red
  if (!isOpen.value) {
    return 'bg-destructive/10 border-destructive/50'
  }
  
  // Within deadline warning → orange
  if (daysLeft.value <= 2) {
    return 'bg-orange-500/10 border-orange-500/50'
  }
  
  // Within deadline normal → green
  return 'bg-primary/10 border-primary/50'
})

const iconClass = computed(() => {
  // System operational → green
  if (isSystemOperational.value) {
    return 'text-primary'
  }
  
  // After deadline not operational → red
  if (!isOpen.value) return 'text-destructive'
  
  // Warning → orange
  if (daysLeft.value <= 2) return 'text-orange-500'
  
  // Normal → green
  return 'text-primary'
})
</script>
