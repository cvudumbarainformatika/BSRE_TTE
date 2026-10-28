import { defineStore } from 'pinia'
import { api as axios } from '@/boot/axios'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    loading: false,
    stats: {
      total_survey: 0,
      total_kecamatan: 0,
      total_kelurahan: 0,
      total_intervensi: 0
    },
    rtlhBreakdown: [],
    summary: [],
    recentActivities: [],
    mapData: {
      type: 'FeatureCollection',
      features: []
    }
  }),

  actions: {
    async fetchDashboardData() {
      this.loading = true
      try {
        const response = await axios.get('/api/dashboard')
        if (response.data.success) {
          const d = response.data.data
          this.stats = {
            total_survey: d.total_survey,
            total_kecamatan: d.total_kecamatan,
            total_kelurahan: d.total_kelurahan,
            total_intervensi: d.total_intervensi
          }
          this.rtlhBreakdown = d.rtlh_breakdown || []
          this.summary = d.summary || []
          this.recentActivities = d.recent_activities || []
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchMapData() {
      try {
        const response = await axios.get('/api/dashboard/map')
        this.mapData = response.data
      } catch (error) {
        console.error('Error fetching map data:', error)
      }
    },

    async refreshAll() {
      await Promise.all([
        this.fetchDashboardData(),
        this.fetchMapData()
      ])
    }
  }
})