<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  reportData: Object,
  reportType: String,
  tahun: Number,
  tanggalLaporan: String
})

const isLandscape = computed(() => {
  // Wide reports use landscape
  return ['akomodasi', 'dtw', 'kereta'].includes(props.reportType)
})

const orientationClass = computed(() => {
  return isLandscape.value ? 'landscape' : 'portrait'
})

// Auto-print when component mounts
onMounted(() => {
  // Give browser time to render
  setTimeout(() => {
    window.print()
  }, 500)
})
</script>

<template>
  <div :class="['print-container', orientationClass]" v-if="reportData">
    <!-- Report will be rendered by parent component -->
    <slot />
  </div>
</template>

<style scoped>
@page {
  size: A4 portrait;
  margin: 15mm;
}

@page.landscape {
  size: A4 landscape;
}

@media print {
  * {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
  
  .print-container {
    width: 100%;
    font-family: Arial, sans-serif;
    font-size: 10pt;
  }
  
  .landscape .print-container {
    font-size: 7pt;
  }
}

@media screen {
  .print-container {
    max-width: 210mm;
    margin: 20px auto;
    padding: 20px;
    background: white;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
  }
}
</style>
