<template>
  <div class="chart-container w-full">
    <canvas :id="chartId" ref="chartCanvasRef"></canvas>
  </div>
</template>

<script setup>
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'
import { ref, onMounted, onUnmounted, watch } from 'vue'

// Registrasi komponen Chart.js
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

// Props
const props = defineProps({
  labels: {
    type: Array,
    required: true
  },
  datasets: {
    type: Array,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  },
  width: {
    type: Number,
    default: undefined
  },
  height: {
    type: Number,
    default: 300
  }
})

// Refs
const chartCanvasRef = ref(null)
let chartInstance = null

// ID unik untuk chart
const chartId = `pie-chart-${Math.random().toString(36).substr(2, 9)}`

// Fungsi untuk membuat chart
const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  const canvas = chartCanvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')

  // Gabungkan opsi default dengan opsi yang diberikan
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
            const percentage = Math.round((value / total) * 100);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
    ...props.options
  }

  chartInstance = new ChartJS(ctx, {
    type: 'pie',
    data: {
      labels: props.labels,
      datasets: props.datasets
    },
    options: chartOptions
  })
}

// Lifecycle hooks
onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

// Watch for data or options changes
watch(() => [props.labels, props.datasets, props.options], () => {
  createChart()
}, { deep: true })
</script>