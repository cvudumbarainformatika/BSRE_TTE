<template>
  <div>
    <!-- Menggunakan Komponen Modular DataTablePremium -->
    <DataTablePremium
      title="Arsip Dokumen Resmi Terverifikasi TTE BSrE"
      description="Daftar global seluruh dokumen elektronik yang telah memiliki PDF resmi dan telah sah ditandatangani secara elektronik (TTE BSrE BSSN) • Retensi Arsip 5 Tahun"
      :items="documents"
      :columns="columns"
      :loading="loading"
      :page-size="meta.per_page"
      :server-side="true"
      :total-items="meta.total"
      :show-add-button="false"
      search-placeholder="Cari judul/perihal dokumen, nomor surat, atau nama penandatangan..."
      @change="onTableChange"
      @row-click="emitView"
    >
      <!-- Slot Filter Menggunakan Komponen Modular Button -->
      <template #filters>
        <Button
          variant="outline"
          size="sm"
          class="h-10 gap-1.5"
          :disabled="loading"
          @click="loadDocuments"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
          <span>Segarkan Dokumen</span>
        </Button>
      </template>

      <!-- Custom Cell: Jenis Dokumen + Waktu Diterbitkan di bawahnya -->
      <template #cell-document_type="{ item }">
        <div class="min-w-0">
          <div class="flex flex-nowrap items-center gap-1.5">
            <Badge variant="secondary" class="text-[10px] uppercase font-bold shrink-0 whitespace-nowrap" :title="formatType(item.document_type)">
              {{ formatType(item.document_type) }}
            </Badge>
            <Badge variant="outline" class="text-[10px] px-1.5 font-mono bg-primary/10 text-primary border-primary/30 shrink-0 whitespace-nowrap">
              v{{ getDocVersion(item) }}.0
            </Badge>
          </div>
          <div
            class="text-[10px] text-muted-foreground mt-1.5 whitespace-nowrap"
            :title="`Diterbitkan: ${formatDate(item.uploaded_at)}`"
          >
            {{ formatDate(item.uploaded_at) }}
          </div>
        </div>
      </template>

      <!-- Custom Cell: Perihal & No. Dokumen (Global + Ellipsis) -->
      <template #cell-title="{ item }">
        <div class="flex flex-nowrap items-start gap-2 min-w-0 max-w-full">
          <Badge variant="destructive" class="font-bold text-[10px] mt-0.5 shrink-0 whitespace-nowrap">PDF</Badge>
          <div class="min-w-0 flex-1 overflow-hidden">
            <div
              class="font-bold text-xs text-foreground hover:text-primary transition-colors truncate"
              :title="item.title || item.filename"
            >
              {{ item.title || item.filename }}
            </div>
            <div
              class="text-[11px] text-muted-foreground mt-0.5 truncate"
              :title="getDocReferenceSummary(item)"
            >
              {{ getDocReferenceSummary(item) }}
            </div>
            <div
              class="text-[10px] text-muted-foreground/80 font-mono mt-0.5 truncate"
              :title="item.filename"
            >
              {{ item.filename }}
            </div>
          </div>
        </div>
      </template>

      <!-- Custom Cell: Penandatangan TTE (Avatar & Nama Inline + Ellipsis) -->
      <template #cell-tte_signer_name="{ item }">
        <div class="flex flex-nowrap items-center gap-2 min-w-0 max-w-full">
          <div class="w-7 h-7 rounded-full bg-primary/15 text-primary border border-primary/30 flex items-center justify-center text-[10px] font-bold shrink-0">
            {{ getSignerInitial(item.tte_signer_name || item.target_signer_name) }}
          </div>
          <div class="min-w-0 flex-1 overflow-hidden">
            <div
              class="font-bold text-xs text-foreground truncate"
              :title="item.tte_signer_name || item.target_signer_name || '-'"
            >
              {{ item.tte_signer_name || item.target_signer_name || '-' }}
            </div>
            <div
              class="text-[10px] text-muted-foreground truncate mt-0.5"
              :title="`Di-TTE: ${formatDate(item.tte_signed_at || item.uploaded_at)}`"
            >
              Di-TTE: {{ formatDate(item.tte_signed_at || item.uploaded_at) }}
            </div>
          </div>
        </div>
      </template>

      <!-- Custom Cell: Status BSrE -->
      <template #cell-tte_status="{ item }">
        <div class="min-w-0">
          <Badge
            variant="outline"
            class="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 text-[10px] px-2 py-0.5 font-semibold shrink-0 whitespace-nowrap inline-flex items-center gap-1"
          >
            ✓ Sah BSrE
          </Badge>
          <div class="text-[10px] text-muted-foreground/80 mt-1 whitespace-nowrap">
            {{ ((item.file_size || 0) / 1024).toFixed(1) }} KB
          </div>
        </div>
      </template>

      <!-- Custom Cell: Aksi Cepat (Hanya Icon dengan Tooltip) -->
      <template #cell-aksi="{ item }">
        <div class="flex flex-nowrap items-center justify-end gap-1.5 shrink-0" @click.stop>
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8 rounded-lg text-primary border-primary/30 hover:bg-primary/10 shrink-0 transition-transform active:scale-95"
            title="Preview PDF & Riwayat Versi"
            @click="emitView(item)"
          >
            <Eye class="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10 rounded-lg shrink-0 transition-transform active:scale-95"
            title="Verifikasi Keaslian Sertifikat BSrE BSSN"
            @click="openVerifyModal(item)"
          >
            <ShieldCheck class="w-4 h-4" />
          </Button>
        </div>
      </template>
    </DataTablePremium>

    <!-- Verify BSrE Modal Menggunakan AppDialog Modular -->
    <AppDialog
      v-model="showVerifyModal"
      title="Validasi Keaslian & Versioning TTE BSrE BSSN"
      description="Hasil verifikasi integritas kriptografi SHA-256, sertifikat elektronik, dan riwayat versi dokumen."
      @confirm="showVerifyModal = false"
    >
      <div v-if="verifyData" class="space-y-3.5 text-xs">
        <!-- Status Box & Sleek Version Badge -->
        <div class="p-3 bg-emerald-500/10 border border-emerald-500/25 rounded-xl flex items-center justify-between gap-3">
          <div class="flex items-center gap-2.5 min-w-0">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0"></span>
            <div class="flex flex-col">
              <span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 leading-tight">
                {{ verifyData.integrity?.integrity_status || 'Dokumen Valid dan Sah' }}
              </span>
              <span class="text-[10px] text-emerald-600/80 dark:text-emerald-400/80 leading-tight">
                Integritas data terverifikasi belum pernah diubah sejak ditandatangani
              </span>
            </div>
          </div>
          <Badge
            variant="outline"
            class="h-7 px-3 font-mono text-xs font-semibold bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30 rounded-lg shrink-0 whitespace-nowrap flex items-center gap-1.5 shadow-xs"
          >
            <ShieldCheck class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>v{{ getDocVersion(selectedVerifyDoc) }}.0 • Sah BSrE</span>
          </Badge>
        </div>

        <div class="grid grid-cols-2 gap-3 text-foreground p-3 bg-muted/40 border border-border rounded-xl">
          <div>
            <span class="text-muted-foreground block text-[10px]">Penandatangan TTE</span>
            <strong class="text-xs text-foreground">{{ verifyData.signer?.name || selectedVerifyDoc?.tte_signer_name || '-' }}</strong>
          </div>
          <div>
            <span class="text-muted-foreground block text-[10px]">Penerbit Sertifikat (CA)</span>
            <strong class="text-xs text-foreground">{{ verifyData.certificate?.issuer || 'Balai Besar Sertifikasi Elektronik (BSrE) - BSSN' }}</strong>
          </div>
        </div>

        <div>
          <span class="text-muted-foreground block text-[10px] mb-1">SHA-256 Dokumen Hash (Final Signed Version)</span>
          <div class="p-2.5 bg-muted/50 border border-border rounded-lg font-mono text-[10px] break-all text-foreground select-all">
            {{ verifyData.certificate?.sha256_hash || selectedVerifyDoc?.pdf_hash }}
          </div>
        </div>

        <!-- Riwayat Versi Dokumen (Jika Ada Revisi) -->
        <div v-if="verifyRevisionHistory.length > 0" class="pt-1">
          <span class="text-muted-foreground block text-[10px] mb-1 font-semibold uppercase tracking-wider">
            Riwayat Revisi Dokumen Sebelumnya (Arsip)
          </span>
          <div class="space-y-1.5">
            <div
              v-for="rev in verifyRevisionHistory"
              :key="rev.version"
              class="p-2 bg-muted/30 border border-border rounded-lg flex items-center justify-between text-[11px]"
            >
              <div class="flex items-center gap-2">
                <Badge variant="outline" class="text-[10px] font-mono px-1.5 py-0 bg-primary/10 text-primary border-primary/30">
                  {{ rev.version_label || `v${rev.version}.0` }}
                </Badge>
                <span class="text-foreground font-medium">{{ rev.summary || 'Versi Arsip' }}</span>
              </div>
              <span class="text-muted-foreground text-[10px] font-mono">{{ formatDate(rev.signed_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Single Tutup Button (Tanpa tombol Tutup ganda) -->
      <template #footer>
        <Button size="sm" class="px-5 font-semibold rounded-lg" @click="showVerifyModal = false">
          Tutup
        </Button>
      </template>
    </AppDialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import DataTablePremium from '@/components/DataTablePremium.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, ShieldCheck, Eye } from 'lucide-vue-next'

const props = defineProps({
  kunjunganId: {
    type: [Number, String],
    default: null
  },
  pasienId: {
    type: [Number, String],
    default: null
  },
  userRole: {
    type: String,
    default: 'dokter'
  }
})

const emit = defineEmits(['view-document'])

const columns = [
  { key: 'document_type', label: 'Jenis Dokumen', class: 'w-[18%]' },
  { key: 'title', label: 'Perihal & No. Dokumen', class: 'w-[37%]' },
  { key: 'tte_signer_name', label: 'Penandatangan TTE', class: 'w-[25%]' },
  { key: 'tte_status', label: 'Status', class: 'w-[11%]' },
  { key: 'aksi', label: 'Aksi', align: 'right', class: 'w-[9%]' }
]

const documents = ref([])
const loading = ref(false)
const searchQuery = ref('')
const meta = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  total_pages: 1
})

const showVerifyModal = ref(false)
const verifyData = ref(null)
const selectedVerifyDoc = ref(null)

const verifyRevisionHistory = computed(() => {
  if (!selectedVerifyDoc.value?.metadata_json) return []
  try {
    const metaObj = typeof selectedVerifyDoc.value.metadata_json === 'string'
      ? JSON.parse(selectedVerifyDoc.value.metadata_json)
      : selectedVerifyDoc.value.metadata_json
    return Array.isArray(metaObj.revision_history) ? metaObj.revision_history : []
  } catch (e) {
    return []
  }
})

const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: meta.page,
      per_page: meta.per_page,
      search: searchQuery.value || undefined,
      tte_status: 'SIGNED_BSRE',
      kunjungan_id: props.kunjunganId || undefined,
      pasien_id: props.pasienId || undefined
    }
    const res = await documentApi.list(params)
    documents.value = res.data.data
    meta.page = res.data.meta.page
    meta.per_page = res.data.meta.per_page
    meta.total = res.data.meta.total
    meta.total_pages = res.data.meta.total_pages
  } catch (err) {
    console.error('Gagal memuat dokumen:', err)
  } finally {
    loading.value = false
  }
}

const onTableChange = ({ page, search }) => {
  meta.page = page
  searchQuery.value = search || ''
  loadDocuments()
}

const emitView = (doc) => {
  emit('view-document', doc)
}

const openVerifyModal = async (doc) => {
  selectedVerifyDoc.value = doc
  try {
    const res = await documentApi.verifyTte(doc.id)
    verifyData.value = res.data
    showVerifyModal.value = true
  } catch (err) {
    console.error('Gagal mengambil data verifikasi BSrE:', err)
  }
}

const formatType = (type) => {
  const map = {
    surat_kematian: 'Surat Kematian',
    konsul_spesialis: 'Konsul Spesialis',
    resume_medis: 'Resume Medis',
    laporan_operasi: 'Laporan Operasi',
    hasil_lab: 'Laboratorium',
    radiologi: 'Radiologi',
    cppt: 'CPPT',
    general: 'Dokumen Umum'
  }
  return map[type] || type
}

const getSignerInitial = (name) => {
  if (!name) return 'P'
  const cleaned = name
    .replace(/^(drg?\.|prof\.|h\.|hj\.|ir\.|drs\.|ns\.)\s*/gi, '')
    .trim()
  const words = cleaned.split(/\s+/).filter(Boolean)
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return (cleaned.charAt(0) || 'P').toUpperCase()
}

const getDocVersion = (doc) => {
  if (doc?.metadata_json) {
    try {
      const meta = JSON.parse(doc.metadata_json)
      return Number(meta.version || 1)
    } catch (e) {}
  }
  return 1
}

const getDocReferenceSummary = (doc) => {
  if (doc.metadata_json) {
    try {
      const meta = JSON.parse(doc.metadata_json)
      const parts = []
      if (meta.nomor_surat || meta.nosrtmeninggal) {
        parts.push(`No. Dokumen: ${meta.nomor_surat || meta.nosrtmeninggal}`)
      }
      if (meta.noreg) {
        parts.push(`Ref: ${meta.noreg}`)
      }
      if (parts.length > 0) return parts.join(' • ')
    } catch (e) {}
  }
  if (doc.description) {
    return doc.description.split('•').slice(0, 2).join('•').trim()
  }
  return `ID Dokumen: #${doc.id}`
}

const formatDate = (isoString) => {
  if (!isoString) return '-'
  const d = new Date(isoString)
  return d.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadDocuments()
})

defineExpose({
  loadDocuments
})
</script>
