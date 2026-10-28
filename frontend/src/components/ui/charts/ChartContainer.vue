<template>
  <div class="chart-container w-full">
    <canvas :id="chartId" ref="chartCanvasRef" class="w-full"></canvas>
  </div>
</template>

<script setup>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
  RadialLinearScale,
  LineController,
  BarController,
  PieController,
  DoughnutController,
  PolarAreaController,
  RadarController,
  BubbleController,
  ScatterController
} from 'chart.js'
import { ref, onMounted, onUnmounted, watch } from 'vue'

// Registrasi komponen Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  LineController,
  BarController,
  PieController,
  DoughnutController,
  PolarAreaController,
  RadarController,
  BubbleController,
  ScatterController,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
  RadialLinearScale
)

// Props
const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => [
      'line', 'bar', 'pie', 'doughnut', 'radar', 'polarArea', 'bubble', 'scatter'
    ].includes(value)
  },
  data: {
    type: Object,
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
const chartId = `chart-${Math.random().toString(36).substr(2, 9)}`

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
    ...props.options
  }

  chartInstance = new ChartJS(ctx, {
    type: props.type,
    data: props.data,
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

// Watch for data or type changes
watch(() => [props.data, props.type, props.options], () => {
  createChart()
}, { deep: true })
</script>