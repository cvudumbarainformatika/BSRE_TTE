<template>
  <div class="relative w-full h-full rounded-lg overflow-hidden border">
    <div ref="mapContainer" class="w-full h-full min-h-[400px] z-0"></div>
    <div v-if="loading" class="absolute inset-0 bg-background/50 backdrop-blur-sm flex items-center justify-center z-10">
      <div class="flex flex-col items-center gap-2">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
        <p class="text-xs font-medium text-muted-foreground">Memuat Peta...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api as axios } from '@/boot/axios'

// Fix generic Leaflet icon issue
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})
L.Marker.prototype.options.icon = DefaultIcon

const mapContainer = ref(null)
const map = ref(null)
const loading = ref(true)

async function initMap() {
  // Koordinat Probolinggo Kota
  const center = [-7.75, 113.21]
  
  map.value = L.map(mapContainer.value).setView(center, 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map.value)

  loading.value = false

  try {
    const response = await axios.get('/api/dashboard/map')
    const geojson = response.data

    geojson.features.forEach((feature) => {
      const { coordinates } = feature.geometry
      const { title, description, location, foto } = feature.properties

      if (coordinates[1] && coordinates[0]) {
        const marker = L.marker([coordinates[1], coordinates[0]]).addTo(map.value)
        
        const popupContent = `
          <div class="p-1 text-center min-w-[150px]">
            <h5 class="font-bold text-sm mb-1">${title}</h5>
            <p class="text-[10px] text-gray-600 mb-1">${description}</p>
            <p class="text-[10px] font-semibold mb-2">${location}</p>
            ${foto ? `<img src="${foto}" class="w-full h-24 object-cover rounded border" />` : ''}
          </div>
        `
        marker.bindPopup(popupContent)
      }
    })
  } catch (err) {
    console.error('Failed to load map data', err)
  }
}

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style>
/* Ensure leaflet controls are below sidebar if necessary, 
   but standard Shadcn sidebar is usually higher z-index */
.leaflet-container {
  font-family: inherit;
}
.leaflet-popup-content-wrapper {
  border-radius: 8px;
  padding: 0;
}
.leaflet-popup-content {
  margin: 12px;
}
</style>
