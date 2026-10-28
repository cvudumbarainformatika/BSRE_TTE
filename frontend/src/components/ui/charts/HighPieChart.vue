<template>
  <HighChart :options="chartOptions" :width="width" :height="height" />
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import HighChart from './HighChart.vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Grafik Lingkaran'
  },
  data: {
    type: Array,
    default: () => []
  },
  width: {
    type: [Number, String],
    default: '100%'
  },
  height: {
    type: [Number, String],
    default: '400px'
  }
})

// Dark mode detection
const isDark = ref(false)

onMounted(() => {
  // Check if dark mode is active
  isDark.value = document.documentElement.classList.contains('dark')
  
  // Watch for theme changes
  const observer = new MutationObserver(() => {
    isDark.value = document.documentElement.classList.contains('dark')
  })
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  })
})

// Options grafik lingkaran
const chartOptions = computed(() => {
  const textColor = isDark.value ? '#e5e7eb' : '#374151'
  
  return {
    chart: {
      type: 'pie',
      backgroundColor: 'transparent'
    },
    title: {
      text: props.title,
      style: {
        color: textColor
      }
    },
    tooltip: {
      pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>',
      backgroundColor: isDark.value ? 'rgba(31, 41, 55, 0.95)' : 'rgba(255, 255, 255, 0.95)',
      style: {
        color: textColor
      }
    },
    plotOptions: {
      pie: {
        allowPointSelect: true,
        cursor: 'pointer',
        dataLabels: {
          enabled: true,
          format: '<b>{point.name}</b>: {point.percentage:.1f} %',
          style: {
            color: textColor,
            textOutline: 'none'
          }
        }
      }
    },
    series: [{
      name: 'Nilai',
      colorByPoint: true,
      data: props.data
    }],
    credits: {
      enabled: false
    }
  }
})
</script>