<template>
  <ChartContainer 
    :type="'line'"
    :data="processedData"
    :options="mergedOptions"
    :height="height"
    :width="width"
  />
</template>

<script setup>
import { computed } from 'vue'
import ChartContainer from './ChartContainer.vue'

// Props
const props = defineProps({
  labels: {
    type: Array,
    default: () => []
  },
  datasets: {
    type: Array,
    default: () => []
  },
  options: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: Number,
    default: 300
  },
  width: {
    type: Number,
    default: undefined
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showTitle: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Line Chart'
  }
})

// Gunakan computed untuk menggabungkan data
const processedData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map((dataset, index) => ({
    ...dataset,
    borderColor: dataset.borderColor || `hsl(${index * 137.5}, 50%, 50%)`,
    backgroundColor: dataset.backgroundColor || `hsla(${index * 137.5}, 50%, 50%, 0.2)`,
    tension: dataset.tension !== undefined ? dataset.tension : 0.4
  }))
}))

// Gabungkan opsi
const mergedOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: props.showLegend
    },
    title: {
      display: props.showTitle,
      text: props.title
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  },
  ...props.options
}))
</script>