import { defineStore } from 'pinia'
import { api } from '@/boot/axios' // Import axios instance

export const useMasterStore = defineStore('master', {
  state: () => ({
    loading: false,
    wisatas: [],
    hotels: [],
    pips: [],
    tahuns: [],
    bulans: [],
    negaras: [],
    provinsis: [],
    kabupatens: [],
    negarasOther: [],
    tahun: null,
    bulan: null,
    roles: [
      'Administrator',
      'User',
      'Hotel',
      'Wisata',
      'Pip',
      'Kapal Pesiar',
      'Kereta Api',
      'Kepala Dinas'
    ],
  }),

  actions: {
    async getMasterWisata() {
      this.loading = true
      try {
        const response = await api.get('/api/master/wisata')
        // console.log('getMasterWisata', response);

        this.wisatas = response?.data?.data || []
        // this.wisatas.unshift({ idWisata: 0, name: 'Admin' })
        
        return response
      } catch (error) {
        console.error('Error fetching getMasterWisata:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterHotel() {
      this.loading = true
      try {
        const response = await api.get('/api/master/hotels')
        // console.log('getMasterHotel', response);

        this.hotels = response?.data?.data || []
        


        
        return response
      } catch (error) {
        console.error('Error fetching getMasterHotel:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterPip() {
      this.loading = true
      try {
        const response = await api.get('/api/master/pips')
        // console.log('getMasterHotel', response);

        this.pips = response?.data?.data || []
        


        
        return response
      } catch (error) {
        console.error('Error fetching getMasterPip:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterTahun() {
      this.loading = true
      try {
        // Auto-activate previous month AND year on 1st of each month
        await api.post('/api/master/bulan/auto-activate')
        
        // Ensure current year exists in database
        await api.post('/api/master/tahun/ensure-current')
        
        const response = await api.get('/api/master/tahun')
        // console.log('getMasterTahun', response);

        this.tahuns = response?.data?.data || []
        const active = this.tahuns.find(item => item.active)
        if (active) {
          this.tahun = active?.id
        }
        // console.log('activeTahun:', this.tahun);
        
        return response
      } catch (error) {
        console.error('Error fetching getMasterTahun:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterBulan() {
      this.loading = true
      try {
        // Auto-activate previous month on 1st of each month
        await api.post('/api/master/bulan/auto-activate')
        
        const response = await api.get('/api/master/bulan')
        // console.log('getMasterBulan', response);

        this.bulans = response?.data?.data || []
       const active = this.bulans.find(item => item.active)
        if (active) {
          this.bulan = active?.id || null
        }
        // console.log('activeBulan:', this.bulan);
        

        return response
      } catch (error) {
        console.error('Error fetching getMasterBulan:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterNegara() {
      this.loading = true
      try {
        const response = await api.get('/api/master/negara')
        // console.log('getMasterNegara', response);

        this.negaras = response?.data?.data || []
        
        return response
      } catch (error) {
        console.error('Error fetching getMasterNegara:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterProvinsi() {
      this.loading = true
      try {
        const response = await api.get('/api/master/provinsi')
        // console.log('getMasterProvinsi', response);

        this.provinsis = response?.data?.data || []
        
        return response
      } catch (error) {
        console.error('Error fetching getMasterProvinsi:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterKabupaten() {
      this.loading = true
      try {
        const response = await api.get('/api/master/kabupaten')
        // console.log('getMasterKabupaten', response);

        this.kabupatens = response?.data?.data || []
        
        return response
      } catch (error) {
        console.error('Error fetching getMasterKabupaten:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async getMasterNegaraOther() {
      this.loading = true
      try {
        const response = await api.get('/api/master/negara/other')
        // console.log('getMasterNegaraOther', response);

        this.negarasOther = response?.data?.data || []
        
        return response
      } catch (error) {
        console.error('Error fetching getMasterNegaraOther:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
  }
})