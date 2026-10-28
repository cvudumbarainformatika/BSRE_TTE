<template>
  <div class="space-y-3 w-full">
    <Label class="text-base font-semibold">{{ label }} <span v-if="required" class="text-destructive">*</span></Label>
    
    <div 
      class="relative flex flex-col items-center justify-center w-full h-56 border-2 border-dashed rounded-xl transition-all cursor-pointer overflow-hidden group"
      :class="{
        'border-muted-foreground/30 bg-muted/20 hover:bg-primary/5 hover:border-primary/50': !modelValue && !isUploading,
        'border-primary/20 bg-background pointer-events-none': isUploading || modelValue
      }"
      @click="!modelValue && !isUploading ? $refs.fileInput.click() : null"
    >
      <input 
        type="file" 
        ref="fileInput"
        class="hidden" 
        @change="handleFileUpload" 
        accept="image/*" 
      />
      
      <!-- State: Uploading -->
      <div v-if="isUploading" class="flex flex-col items-center justify-center px-4 text-center">
        <div class="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mb-4 shadow-sm"></div>
        <p class="text-sm font-semibold text-primary">Mengunggah Foto...</p>
        <p class="text-xs text-muted-foreground mt-1 animate-pulse">Mohon tunggu sebentar</p>
      </div>
      
      <!-- State: Uploaded (Preview) -->
      <div v-else-if="modelValue" class="relative w-full h-full group bg-black">
        <img :src="backendUrl(modelValue)" alt="Preview Foto" class="w-full h-full object-contain transition-transform duration-500 group-hover:scale-105" />
        
        <!-- Hover Overlay with Action Button -->
        <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center pointer-events-auto backdrop-blur-sm">
          <Button type="button" variant="destructive" class="gap-2 shadow-xl hover:scale-105 transition-transform" @click.stop="removeImage">
            <Trash2 class="h-4 w-4" /> Ganti Foto
          </Button>
        </div>
        
        <!-- Success Badge overlay -->
        <div class="absolute top-4 right-4 bg-green-500 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1.5">
          <Check class="h-3 w-3" /> Berhasil Diunggah
        </div>
      </div>
      
      <!-- State: Default Empty -->
      <div v-else class="flex flex-col items-center justify-center px-4 text-center">
        <div class="h-16 w-16 mb-4 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 group-hover:bg-primary/20 transition-all duration-300 ring-4 ring-primary/5">
          <UploadCloud class="h-8 w-8" />
        </div>
        <p class="text-base font-medium text-foreground mb-1">
          <span class="text-primary font-semibold">Klik untuk unggah</span> atau seret dan lepas
        </p>
        <p class="text-xs text-muted-foreground max-w-xs mt-2">
          Mendukung format gambar standar PNG, JPG atau JPEG. Resolusi otomatis disesuaikan.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api as axios } from '@/boot/axios'
import { UploadCloud, Trash2, Check } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { useQuasar } from 'quasar'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Sematkan Gambar'
  },
  required: {
    type: Boolean,
    default: false
  },
  uploadSubstorage: {
    type: String,
    required: true
  },
  uploadStorage: {
    type: String,
    default: 'antrian'
  }
})

const emit = defineEmits(['update:modelValue', 'update:uploading'])

const $q = useQuasar()
const isUploading = ref(false)

function backendUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  
  // Ambil base URL dari axios config (SOP Konsistensi URL)
  let base = axios.defaults.baseURL || ''
  if (base === '/') base = ''
  
  // Hapus suffix /api jika ada, karena storage ada di root (SOP Fix Image Path)
  base = base.replace(/\/api\/?$/, '')
  
  // Jika development dan base masih kosong, arahkan ke localhost
  if (import.meta.env.DEV && !base) {
    base = 'http://localhost:8082'
  }
  
  // Bersihkan trailing slash pada base dan leading slash pada path
  const cleanBase = base.replace(/\/$/, '')
  const cleanPath = path.replace(/^\//, '')
  
  return `${cleanBase}/${cleanPath}`
}

async function handleFileUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  
  isUploading.value = true
  emit('update:uploading', true)
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('storage', props.uploadStorage)
  formData.append('substorage', props.uploadSubstorage)
  
  try {
    const res = await axios.post('/api/front/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
    emit('update:modelValue', data.path)
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Gagal upload foto ' + props.label })
  } finally {
    isUploading.value = false
    emit('update:uploading', false)
  }
}

function removeImage() {
  emit('update:modelValue', null)
}
</script>
