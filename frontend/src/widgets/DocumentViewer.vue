<template>
  <Card v-if="document" class="border-slate-200 shadow-sm overflow-hidden flex flex-col h-full min-h-[600px] bg-white">
    <!-- Top Header & Actions -->
    <div class="p-4 bg-slate-900 text-white flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <Badge class="bg-blue-600 text-white font-bold text-xs px-2.5 py-1">PDF</Badge>
        <div>
          <h3 class="text-sm font-semibold truncate max-w-xs md:max-w-md">{{ document.title || document.filename }}</h3>
          <div class="flex items-center gap-2 text-[11px] text-slate-300 mt-0.5">
            <span>Kunjungan: #{{ document.kunjungan_id }}</span>
            <span>•</span>
            <Badge v-if="document.tte_status === 'SIGNED_BSRE'" class="bg-emerald-600 text-white text-[10px]">
              ✓ TTE BSrE BSSN Valid
            </Badge>
            <Badge v-else variant="outline" class="text-amber-300 border-amber-400/50 text-[10px]">
              Belum TTE Elektronik
            </Badge>
          </div>
        </div>
      </div>

      <!-- Action Buttons Menggunakan Komponen Modular Button -->
      <div class="flex items-center gap-2">
        <Button
          size="sm"
          :variant="activeTab === 'preview' ? 'default' : 'secondary'"
          class="h-8 text-xs"
          @click="activeTab = 'preview'"
        >
          Preview PDF
        </Button>
        <Button
          size="sm"
          :variant="activeTab === 'audit' ? 'default' : 'secondary'"
          class="h-8 text-xs"
          @click="loadAuditTrail"
        >
          Audit Trail
        </Button>

        <Button
          size="sm"
          variant="secondary"
          class="h-8 text-xs gap-1.5"
          @click="printDocument"
        >
          <Printer class="w-3.5 h-3.5" />
          <span>Cetak</span>
        </Button>

        <Button
          size="sm"
          class="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white gap-1.5"
          @click="downloadDocument"
        >
          <Download class="w-3.5 h-3.5" />
          <span>Unduh</span>
        </Button>

        <Button
          v-if="closable"
          size="sm"
          variant="ghost"
          class="h-8 px-2 text-slate-300 hover:text-white"
          @click="$emit('close')"
        >
          ✕
        </Button>
      </div>
    </div>

    <!-- TTE BSRE Banner Info (Tanpa menampilkan NIK rahasia) -->
    <div v-if="document.tte_status === 'SIGNED_BSRE'" class="bg-emerald-50 border-b border-emerald-100 px-4 py-2 flex items-center justify-between text-xs text-emerald-900">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>Ditandatangani secara Elektronik oleh <strong>{{ document.tte_signer_name }}</strong></span>
      </div>
      <div class="text-[11px] text-emerald-700 font-mono hidden md:block">
        SHA-256: {{ document.pdf_hash ? document.pdf_hash.substring(0, 16) + '...' : '-' }}
      </div>
    </div>

    <!-- Body Content -->
    <CardContent class="flex-1 bg-slate-100 p-2 md:p-4 overflow-hidden relative">
      <div v-show="activeTab === 'preview'" class="w-full h-full min-h-[500px] bg-white rounded-lg shadow-inner overflow-hidden border border-slate-300">
        <iframe
          ref="pdfFrame"
          :src="viewUrl"
          class="w-full h-full min-h-[550px] border-none"
          title="PDF Viewer"
        ></iframe>
      </div>

      <div v-show="activeTab === 'audit'" class="w-full h-full min-h-[500px] bg-white rounded-lg p-5 overflow-y-auto">
        <h4 class="text-sm font-bold text-slate-800 mb-3">
          Jejak Audit & Kepatuhan Rekam Medis (Permenkes 24/2022)
        </h4>

        <div v-if="loadingAudit" class="text-center py-8 text-xs text-slate-400">
          Memuat catatan jejak audit...
        </div>

        <div v-else-if="auditLogs.length === 0" class="text-center py-8 text-xs text-slate-400">
          Belum ada catatan aktivitas untuk dokumen ini.
        </div>

        <div v-else class="relative border-l-2 border-slate-200 ml-3 space-y-6 text-xs">
          <div v-for="log in auditLogs" :key="log.id" class="ml-4 relative">
            <span class="absolute -left-[23px] top-1 w-3 h-3 rounded-full bg-blue-600 border-2 border-white shadow-sm"></span>
            <div class="flex items-center gap-2">
              <span class="font-bold text-slate-800">{{ log.action }}</span>
              <Badge variant="secondary" class="text-[10px]">{{ log.user_role }}</Badge>
              <span class="text-slate-400 text-[11px]">{{ formatTimestamp(log.created_at) }}</span>
            </div>
            <p class="text-slate-600 mt-0.5">
              Oleh: <strong>{{ log.username }}</strong>
            </p>
            <div v-if="log.details" class="mt-1 p-2 bg-slate-50 border rounded text-[11px] font-mono text-slate-500 overflow-x-auto">
              {{ log.details }}
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>

  <Card v-else class="p-8 text-center bg-white border-slate-200 text-slate-400 text-xs">
    Pilih dokumen untuk melihat preview inline.
  </Card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { documentApi } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Printer, Download } from 'lucide-vue-next'

const props = defineProps({
  document: {
    type: Object,
    default: null
  },
  closable: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

const activeTab = ref('preview')
const pdfFrame = ref(null)
const auditLogs = ref([])
const loadingAudit = ref(false)

const viewUrl = computed(() => {
  if (!props.document?.id) return ''
  return `${documentApi.getViewUrl(props.document.id)}?t=${Date.now()}`
})

const downloadUrl = computed(() => {
  if (!props.document?.id) return '#'
  return documentApi.getDownloadUrl(props.document.id)
})

const downloadDocument = () => {
  if (downloadUrl.value && downloadUrl.value !== '#') {
    window.open(downloadUrl.value, '_blank')
  }
}

const printDocument = () => {
  if (pdfFrame.value && pdfFrame.value.contentWindow) {
    try {
      pdfFrame.value.contentWindow.print()
    } catch (e) {
      window.open(viewUrl.value, '_blank')
    }
  } else {
    window.open(viewUrl.value, '_blank')
  }
}

const loadAuditTrail = async () => {
  activeTab.value = 'audit'
  if (!props.document?.id) return
  loadingAudit.value = true
  try {
    const res = await documentApi.getAuditTrail(props.document.id)
    auditLogs.value = res.data
  } catch (err) {
    console.error('Gagal mengambil audit trail:', err)
  } finally {
    loadingAudit.value = false
  }
}

const formatTimestamp = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>
