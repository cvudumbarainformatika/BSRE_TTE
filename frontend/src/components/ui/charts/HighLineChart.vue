<template>
  <HighChart :options="chartOptions" :width="width" :height="height" />
</template>

<script setup>
import { computed } from 'vue'
import HighChart from './HighChart.vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Grafik Garis'
  },
  data: {
    type: Array,
    default: () => []
  },
  categories: {
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

// Options grafik garis
const chartOptions = computed(() => {
  return {
    chart: {
      type: 'line'
    },
    title: {
      text: props.title
    },
    xAxis: {
      categories: props.categories
    },
    yAxis: {
      title: {
        text: 'Nilai'
      }
    },
    series: props.data,
    credits: {
      enabled: false
    }
  }
})
</script>