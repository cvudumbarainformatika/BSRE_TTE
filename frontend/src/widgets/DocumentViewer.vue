<template>
  <Card v-if="document" class="border-border shadow-xs overflow-hidden flex flex-col h-full min-h-[600px] glass-panel text-foreground">
    <!-- Top Header & Actions -->
    <div class="p-4 bg-muted/60 border-b border-border text-foreground flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0">
        <Badge variant="destructive" class="font-bold text-xs px-2.5 py-1 shrink-0">PDF</Badge>
        <div class="min-w-0">
          <h3 class="text-sm font-semibold truncate max-w-xs md:max-w-md text-foreground" :title="document.title || document.filename">
            {{ document.title || document.filename }}
          </h3>
          <div class="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
            <span class="truncate max-w-[260px]" :title="document.description || `ID: #${document.id}`">
              {{ document.description || `ID Dokumen: #${document.id}` }}
            </span>
            <span>•</span>
            <Badge v-if="document.tte_status === 'SIGNED_BSRE'" variant="outline" class="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 text-[10px] shrink-0">
              ✓ TTE BSrE BSSN Valid
            </Badge>
            <Badge v-else variant="outline" class="text-amber-500 border-amber-500/30 text-[10px] shrink-0">
              Menunggu TTE
            </Badge>
          </div>
        </div>
      </div>

      <!-- Action Buttons Menggunakan Komponen Modular Button -->
      <div class="flex items-center gap-2">
        <Button
          size="sm"
          :variant="activeTab === 'preview' ? 'default' : 'outline'"
          class="h-8 text-xs rounded-lg"
          @click="activeTab = 'preview'"
        >
          Preview PDF
        </Button>
        <Button
          size="sm"
          :variant="activeTab === 'audit' ? 'default' : 'outline'"
          class="h-8 text-xs rounded-lg"
          @click="loadAuditTrail"
        >
          Audit Trail
        </Button>

        <Button
          size="sm"
          variant="outline"
          class="h-8 text-xs gap-1.5 rounded-lg border-border"
          @click="printDocument"
        >
          <Printer class="w-3.5 h-3.5" />
          <span>Cetak</span>
        </Button>

        <Button
          size="sm"
          class="h-8 text-xs bg-primary text-primary-foreground font-semibold gap-1.5 rounded-lg"
          @click="downloadDocument"
        >
          <Download class="w-3.5 h-3.5" />
          <span>Unduh</span>
        </Button>

        <Button
          v-if="closable"
          size="sm"
          variant="ghost"
          class="h-8 px-2 text-muted-foreground hover:text-foreground rounded-lg"
          @click="$emit('close')"
        >
          ✕
        </Button>
      </div>
    </div>

    <!-- TTE BSRE Banner Info & Selector Versioning -->
    <div v-if="document.tte_status === 'SIGNED_BSRE' || versionList.length > 1" class="bg-emerald-500/10 border-b border-emerald-500/20 px-4 py-2 flex flex-wrap items-center justify-between gap-2 text-xs text-emerald-500">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
        <span v-if="document.tte_status === 'SIGNED_BSRE'">
          Ditandatangani secara Elektronik oleh <strong>{{ document.tte_signer_name }}</strong>
        </span>
        <span v-else class="text-amber-500 font-semibold">
          Revisi v{{ currentVersion }}.0 Menunggu TTE Ulang (Versi sebelumnya telah di-TTE)
        </span>
      </div>

      <!-- Tombol Pilih Versi Dokumen (v1.0, v2.0, dst.) -->
      <div class="flex items-center gap-1.5">
        <span class="text-[11px] text-muted-foreground mr-1">Versi PDF:</span>
        <Button
          v-for="v in versionList"
          :key="v.version"
          size="sm"
          :variant="selectedVersion === v.version ? 'default' : 'outline'"
          class="h-6 px-2 text-[10px] font-mono rounded-md"
          :title="v.summary || v.label"
          @click="selectedVersion = v.version"
        >
          {{ v.label }}
        </Button>
      </div>
    </div>

    <!-- Body Content -->
    <CardContent class="flex-1 bg-muted/20 p-2 md:p-4 overflow-hidden relative">
      <div v-show="activeTab === 'preview'" class="w-full h-full min-h-[500px] bg-card rounded-lg shadow-inner overflow-hidden border border-border">
        <iframe
          ref="pdfFrame"
          :src="viewUrl"
          class="w-full h-full min-h-[550px] border-none"
          title="PDF Viewer"
        ></iframe>
      </div>

      <div v-show="activeTab === 'audit'" class="w-full h-full min-h-[500px] bg-card rounded-lg p-5 overflow-y-auto border border-border">
        <h4 class="text-sm font-bold text-foreground mb-3">
          Jejak Audit & Kepatuhan Rekam Medis (Permenkes 24/2022)
        </h4>

        <div v-if="loadingAudit" class="text-center py-8 text-xs text-muted-foreground">
          Memuat catatan jejak audit...
        </div>

        <div v-else-if="auditLogs.length === 0" class="text-center py-8 text-xs text-muted-foreground">
          Belum ada catatan aktivitas untuk dokumen ini.
        </div>

        <div v-else class="relative border-l-2 border-border ml-3 space-y-6 text-xs">
          <div v-for="log in auditLogs" :key="log.id" class="ml-4 relative">
            <span class="absolute -left-[23px] top-1 w-3 h-3 rounded-full bg-primary border-2 border-background shadow-sm"></span>
            <div class="flex items-center gap-2">
              <span class="font-bold text-foreground">{{ log.action }}</span>
              <Badge variant="secondary" class="text-[10px]">{{ log.user_role }}</Badge>
              <span class="text-muted-foreground text-[11px]">{{ formatTimestamp(log.created_at) }}</span>
            </div>
            <p class="text-muted-foreground mt-0.5">
              Oleh: <strong class="text-foreground">{{ log.username }}</strong>
            </p>
            <div v-if="log.details" class="mt-1 p-2 bg-muted/40 border border-border rounded text-[11px] font-mono text-muted-foreground overflow-x-auto">
              {{ log.details }}
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>

  <Card v-else class="p-8 text-center glass-panel border-border text-muted-foreground text-xs">
    Pilih dokumen untuk melihat preview inline.
  </Card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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
const selectedVersion = ref(null)

const parsedMeta = computed(() => {
  if (!props.document?.metadata_json) return {}
  try {
    return JSON.parse(props.document.metadata_json)
  } catch (e) {
    return {}
  }
})

const currentVersion = computed(() => Number(parsedMeta.value.version || 1))

const versionList = computed(() => {
  const history = Array.isArray(parsedMeta.value.revision_history) ? parsedMeta.value.revision_history : []
  const items = history.map((h) => ({
    version: Number(h.version),
    label: `v${h.version}.0 (Arsip)`,
    summary: h.summary || `Versi v${h.version}.0`
  }))
  items.push({
    version: currentVersion.value,
    label: `v${currentVersion.value}.0 (Terbaru)`,
    summary: `Versi Terbaru v${currentVersion.value}.0`
  })
  return items.sort((a, b) => b.version - a.version)
})

watch(
  () => props.document,
  () => {
    selectedVersion.value = currentVersion.value
  },
  { immediate: true }
)

const viewUrl = computed(() => {
  if (!props.document?.id) return ''
  const ver = selectedVersion.value || currentVersion.value
  const rawTitle = props.document.title || props.document.filename || 'dokumen'
  const safeFilename = encodeURIComponent(rawTitle.replace(/[/\\?%*:|"<>]/g, '_')) + '.pdf'
  return `${documentApi.getViewUrl(props.document.id)}/${safeFilename}?version=${ver}&t=${Date.now()}`
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
