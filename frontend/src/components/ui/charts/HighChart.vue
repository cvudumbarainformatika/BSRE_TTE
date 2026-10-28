<template>
  <div :id="chartId" ref="chartRef" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Highcharts from 'highcharts'
import HighchartsMore from 'highcharts/highcharts-more'
import Highcharts3D from 'highcharts/highcharts-3d'
import Exporting from 'highcharts/modules/exporting'
import ExportData from 'highcharts/modules/export-data'
import OfflineExporting from 'highcharts/modules/offline-exporting'
import Accessibility from 'highcharts/modules/accessibility'

// Inisialisasi modul Highcharts
if (typeof Highcharts === 'object') {
  // Pastikan fungsi modul tersedia sebelum dijalankan
  if (typeof HighchartsMore === 'function') {
    HighchartsMore(Highcharts)
  }
  if (typeof Highcharts3D === 'function') {
    Highcharts3D(Highcharts)
  }
  if (typeof Exporting === 'function') {
    Exporting(Highcharts)
  }
  if (typeof ExportData === 'function') {
    ExportData(Highcharts)
  }
  if (typeof OfflineExporting === 'function') {
    OfflineExporting(Highcharts)
  }
  if (typeof Accessibility === 'function') {
    Accessibility(Highcharts)
  }
}

// Props untuk komponen
const props = defineProps({
  options: {
    type: Object,
    required: true
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

// Refs
const chartRef = ref(null)
let chartInstance = null

// ID unik untuk chart
const chartId = `highchart-${Math.random().toString(36).substring(2, 10)}`

// Fungsi untuk membuat chart
const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  if (chartRef.value) {
    // Gabungkan opsi default dengan opsi dari props
    const chartOptions = {
      chart: {
        type: 'line',
        ...props.options.chart
      },
      title: {
        text: props.options.title?.text || '',
        ...props.options.title
      },
      xAxis: {
        ...(Array.isArray(props.options.xAxis) ? props.options.xAxis[0] : props.options.xAxis)
      },
      yAxis: {
        ...(Array.isArray(props.options.yAxis) ? props.options.yAxis[0] : props.options.yAxis)
      },
      series: props.options.series || [],
      legend: {
        enabled: true,
        ...props.options.legend
      },
      plotOptions: props.options.plotOptions || {},
      tooltip: props.options.tooltip || {},
      credits: {
        enabled: false // Nonaktifkan credit Highcharts
      },
      exporting: {
        enabled: true // Aktifkan fitur export
      },
      responsive: {
        rules: [{
          condition: {
            maxWidth: 500
          },
          chartOptions: {
            legend: {
              align: 'center',
              verticalAlign: 'bottom',
              layout: 'horizontal'
            },
            yAxis: {
              labels: {
                align: 'left',
                x: 0,
                y: 0
              },
              title: {
                rotation: 0
              }
            },
            subtitle: {
              text: null
            },
            credits: {
              enabled: false
            }
          }
        }]
      },
      ...props.options
    }

    chartInstance = Highcharts.chart(chartRef.value, chartOptions)
  }
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

// Watch untuk perubahan opsional
watch(() => props.options, () => {
  createChart()
}, { deep: true })
</script>