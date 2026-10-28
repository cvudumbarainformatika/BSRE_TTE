<template>
  <ChartContainer 
    :type="'bar'"
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
    default: 'Bar Chart'
  },
  stacked: {
    type: Boolean,
    default: false
  }
})

// Gunakan computed untuk menggabungkan data
const processedData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map((dataset, index) => ({
    ...dataset,
    borderColor: dataset.borderColor || `hsl(${index * 137.5}, 50%, 50%)`,
    backgroundColor: dataset.backgroundColor || `hsl(${index * 137.5}, 50%, 75%)`,
    borderWidth: dataset.borderWidth || 1
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
    x: {
      stacked: props.stacked
    },
    y: {
      stacked: props.stacked,
      beginAtZero: true
    }
  },
  ...props.options
}))
</script>