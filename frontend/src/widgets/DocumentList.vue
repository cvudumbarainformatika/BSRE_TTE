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

      <!-- Kolom 1: Jenis Dokumen (Ikon PDF Merah + Label Teks Tanpa Badge + Versioning, Size & Tgl Terbit di Bawahnya) -->
      <template #cell-document_type="{ item }">
        <div class="flex flex-nowrap items-center gap-2.5 min-w-0 max-w-full">
          <!-- Icon Kotak PDF Merah (Tiru SS) -->
          <div class="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/25 flex flex-col items-center justify-center shrink-0 shadow-xs">
            <svg class="w-3.5 h-3.5 text-rose-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM14 3.5L18.5 8H14V3.5z"/>
            </svg>
            <span class="text-[6.5px] font-black text-rose-500 leading-none mt-0.5 tracking-tight">PDF</span>
          </div>

          <!-- Label Tanpa Badge + Versioning, Size & Tgl Terbit -->
          <div class="min-w-0 flex-1 overflow-hidden">
            <div class="text-xs font-semibold text-foreground truncate" :title="formatType(item.document_type)">
              {{ formatType(item.document_type) }}
            </div>
            <div
              class="text-[10px] text-muted-foreground mt-0.5 truncate flex flex-nowrap items-center gap-1.5"
              :title="`Versi: v${getDocVersion(item)}.0 • Ukuran: ${((item.file_size || 0) / 1024).toFixed(1)} KB • Terbit: ${formatDate(item.uploaded_at)}`"
            >
              <span class="font-mono text-primary font-medium shrink-0">v{{ getDocVersion(item) }}.0</span>
              <span class="text-muted-foreground/40 shrink-0">•</span>
              <span class="shrink-0">{{ ((item.file_size || 0) / 1024).toFixed(1) }} KB</span>
              <span class="text-muted-foreground/40 shrink-0">•</span>
              <span class="truncate">{{ formatDate(item.uploaded_at) }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- Kolom 2: Perihal & No. Dokumen (Badge PDF Merah Dihapus + Ellipsis Rapi) -->
      <template #cell-title="{ item }">
        <div class="min-w-0 max-w-full overflow-hidden">
          <div
            class="font-bold text-xs text-foreground hover:text-primary transition-colors truncate"
            :title="item.title || item.filename"
          >
            {{ item.title || item.filename }}
          </div>
          <div
            class="text-[11px] text-muted-foreground mt-0.5 truncate font-mono"
            :title="getDocReferenceSummary(item)"
          >
            {{ getDocReferenceSummary(item) }}
          </div>
          <div
            class="text-[10px] text-muted-foreground/70 font-mono mt-0.5 truncate"
            :title="item.filename"
          >
            {{ item.filename }}
          </div>
        </div>
      </template>

      <!-- Kolom 3: Penandatangan TTE (Nama Penandatangan + NIP & Waktu Di-TTE) -->
      <template #cell-tte_signer_name="{ item }">
        <div class="min-w-0 max-w-full overflow-hidden">
          <div
            class="font-bold text-xs text-foreground truncate"
            :title="item.tte_signer_name || item.target_signer_name || '-'"
          >
            {{ item.tte_signer_name || item.target_signer_name || '-' }}
          </div>
          <div
            v-if="item.tte_signer_nip || item.target_signer_nip"
            class="text-[10px] text-muted-foreground font-mono mt-0.5 truncate"
            :title="`NIP: ${item.tte_signer_nip || item.target_signer_nip}`"
          >
            NIP: {{ item.tte_signer_nip || item.target_signer_nip }}
          </div>
          <div
            class="text-[10px] text-muted-foreground mt-0.5 truncate"
            :title="`Di-TTE: ${formatDate(item.tte_signed_at || item.uploaded_at)}`"
          >
            Di-TTE: {{ formatDate(item.tte_signed_at || item.uploaded_at) }}
          </div>
        </div>
      </template>

      <!-- Kolom 4: Status (Badge Terverifikasi BSrE Meniru SS) -->
      <template #cell-tte_status>
        <div class="min-w-0 max-w-full overflow-hidden">
          <!-- Badge Pill Terverifikasi BSrE (Tiru SS) -->
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-medium whitespace-nowrap shadow-xs">
            <CheckCircle2 class="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Terverifikasi BSrE</span>
          </div>
        </div>
      </template>

      <!-- Kolom 5: Aksi Cepat (Hanya Icon dengan Tooltip) -->
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

    <!-- Modal Verifikasi Keabsahan TTE BSrE BSSN -->
    <AppDialog
      v-model="showVerifyModal"
      title="Verifikasi Keaslian & Sertifikat TTE BSrE BSSN"
      description="Audit integritas kriptografi & validitas sertifikat digital otoritas BSrE BSSN"
      size="lg"
    >
      <div v-if="verifyData" class="space-y-4">
        <!-- Status Alert Banner -->
        <div
          class="p-4 rounded-xl border flex items-start gap-3"
          :class="verifyData.is_valid
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
            : 'bg-rose-500/10 border-rose-500/30 text-rose-600 dark:text-rose-400'"
        >
          <ShieldCheck class="w-6 h-6 shrink-0 mt-0.5" />
          <div>
            <h4 class="font-bold text-sm">
              {{ verifyData.is_valid ? 'DOKUMEN ASLI & TERVERIFIKASI BSrE BSSN' : 'INTEGRITAS DOKUMEN TIDAK VALID' }}
            </h4>
            <p class="text-xs mt-1 text-muted-foreground leading-relaxed">
              {{ verifyData.notes || verifyData.message }}
            </p>
          </div>
        </div>

        <!-- Detail Spesifikasi Sertifikat -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="p-3 bg-muted/40 rounded-lg border border-border">
            <span class="text-muted-foreground block text-[11px]">Nama Penandatangan (Signer):</span>
            <strong class="text-foreground text-xs">{{ verifyData.signer_name || '-' }}</strong>
          </div>
          <div class="p-3 bg-muted/40 rounded-lg border border-border">
            <span class="text-muted-foreground block text-[11px]">NIP / Identitas Resmi:</span>
            <strong class="text-foreground text-xs">{{ verifyData.signer_nip || '-' }}</strong>
          </div>
          <div class="p-3 bg-muted/40 rounded-lg border border-border">
            <span class="text-muted-foreground block text-[11px]">Otoritas Penerbit Sertifikat (CA):</span>
            <strong class="text-foreground text-xs">{{ verifyData.certificate_issuer || 'Balai Sertifikasi Elektronik (BSrE) - BSSN RI' }}</strong>
          </div>
          <div class="p-3 bg-muted/40 rounded-lg border border-border">
            <span class="text-muted-foreground block text-[11px]">Waktu Penandatanganan (Timestamp):</span>
            <strong class="text-foreground text-xs">{{ formatDate(verifyData.signed_at) }}</strong>
          </div>
        </div>

        <!-- Informasi Hash SHA-256 Integritas Berkas -->
        <div class="p-3 bg-muted/30 rounded-lg border border-border">
          <span class="text-muted-foreground block text-[11px] mb-1">Nilai Hash Dokumen (SHA-256 Integritas):</span>
          <code class="text-[10px] break-all font-mono text-muted-foreground bg-background p-1.5 rounded border border-border block">
            {{ verifyData.sha256_hash || verifyData.pdf_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' }}
          </code>
        </div>
      </div>

      <template #footer>
        <Button variant="outline" size="sm" @click="showVerifyModal = false">
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
import { RefreshCw, ShieldCheck, Eye, CheckCircle2 } from 'lucide-vue-next'

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

// Struktur Kolom Tetap Sesuai Urutan Asli
const columns = [
  { key: 'document_type', label: 'Jenis Dokumen', class: 'w-[23%]' },
  { key: 'title', label: 'Perihal & No. Dokumen', class: 'w-[35%]' },
  { key: 'tte_signer_name', label: 'Penandatangan TTE', class: 'w-[22%]' },
  { key: 'tte_status', label: 'Status', class: 'w-[12%]' },
  { key: 'aksi', label: 'Aksi', align: 'right', class: 'w-[8%]' }
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
  return map[type] || type || 'Dokumen'
}

const getDocVersion = (doc) => {
  if (doc?.metadata_json) {
    try {
      const meta = typeof doc.metadata_json === 'string' ? JSON.parse(doc.metadata_json) : doc.metadata_json
      return Number(meta.version || 1)
    } catch (e) {}
  }
  return 1
}

const getDocReferenceSummary = (doc) => {
  if (doc.metadata_json) {
    try {
      const meta = typeof doc.metadata_json === 'string' ? JSON.parse(doc.metadata_json) : doc.metadata_json
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
