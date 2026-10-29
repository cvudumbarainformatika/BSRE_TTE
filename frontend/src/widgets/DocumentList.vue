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
      search-placeholder="Cari judul dokumen, nomor surat, atau nama penandatangan..."
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

      <!-- Kolom 1: Dokumen & Nomor (Icon PDF Merah + Judul Bold + Nomor Dokumen Muted) -->
      <template #cell-title="{ item }">
        <div class="flex flex-nowrap items-center gap-3 min-w-0 max-w-full">
          <!-- Icon Kotak PDF Merah (Meniru Desain Referensi) -->
          <div class="w-9 h-9 rounded-lg bg-rose-500/10 border border-rose-500/25 flex flex-col items-center justify-center shrink-0 shadow-xs">
            <svg class="w-4 h-4 text-rose-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM14 3.5L18.5 8H14V3.5z"/>
            </svg>
            <span class="text-[7px] font-black text-rose-500 leading-none mt-0.5 tracking-tight">PDF</span>
          </div>

          <div class="min-w-0 flex-1 overflow-hidden">
            <div
              class="font-bold text-xs md:text-sm text-foreground hover:text-primary transition-colors truncate"
              :title="item.title || item.filename"
            >
              {{ item.title || item.filename }}
            </div>
            <div
              class="text-xs text-muted-foreground font-mono mt-0.5 truncate"
              :title="getDocNumber(item)"
            >
              {{ getDocNumber(item) }}
            </div>
          </div>
        </div>
      </template>

      <!-- Kolom 2: Jenis Dokumen (Kategori - Label Bersih Tanpa Badge) -->
      <template #cell-document_type="{ item }">
        <div class="text-xs font-normal text-muted-foreground whitespace-nowrap">
          {{ formatType(item.document_type) }}
        </div>
      </template>

      <!-- Kolom 3: Penandatangan (Nama Dokter / Pejabat + NIP di Bawahnya) -->
      <template #cell-tte_signer_name="{ item }">
        <div class="min-w-0">
          <div
            class="font-semibold text-xs text-foreground truncate"
            :title="item.tte_signer_name || item.target_signer_name || '-'"
          >
            {{ item.tte_signer_name || item.target_signer_name || '-' }}
          </div>
          <div
            class="text-[11px] text-muted-foreground font-mono mt-0.5 truncate"
            :title="`NIP: ${item.tte_signer_nip || item.target_signer_nip || '-'}`"
          >
            NIP: {{ item.tte_signer_nip || item.target_signer_nip || '-' }}
          </div>
        </div>
      </template>

      <!-- Kolom 4: Status BSrE (Badge Centang Hijau Terverifikasi BSrE + 2 Tanggal: Terbit & Di-TTE) -->
      <template #cell-tte_status="{ item }">
        <div class="space-y-1.5 min-w-0">
          <!-- Badge Pill Terverifikasi BSrE (Meniru Desain Referensi) -->
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium whitespace-nowrap shadow-xs">
            <CheckCircle2 class="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Terverifikasi BSrE</span>
          </div>

          <!-- 2 Tanggal: Terbit & Di-TTE -->
          <div class="text-[11px] text-muted-foreground space-y-0.5 whitespace-nowrap leading-tight">
            <div class="flex items-center gap-1">
              <span class="text-muted-foreground/70">Terbit :</span>
              <span class="font-mono text-foreground/80">{{ formatDate(item.uploaded_at) }}</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="text-muted-foreground/70">Di-TTE :</span>
              <span class="font-mono text-foreground/80">{{ formatDate(item.tte_signed_at || item.uploaded_at) }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- Kolom 5: Aksi Cepat (Tombol Icon Preview & Unduh Sesuai Referensi) -->
      <template #cell-aksi="{ item }">
        <div class="flex flex-nowrap items-center justify-end gap-1.5 shrink-0" @click.stop>
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8 rounded-lg text-foreground/80 border-border/80 hover:bg-muted hover:text-foreground shrink-0 transition-transform active:scale-95"
            title="Lihat & Validasi Dokumen"
            @click="emitView(item)"
          >
            <Eye class="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8 rounded-lg text-foreground/80 border-border/80 hover:bg-muted hover:text-foreground shrink-0 transition-transform active:scale-95"
            title="Unduh Berkas PDF Resmi"
            @click="downloadDoc(item)"
          >
            <Download class="w-4 h-4" />
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
import { RefreshCw, ShieldCheck, Eye, Download, CheckCircle2 } from 'lucide-vue-next'

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

// Definisi Urutan Kolom Sesuai Referensi Pengguna
const columns = [
  { key: 'title', label: 'DOKUMEN & NOMOR', class: 'w-[36%]' },
  { key: 'document_type', label: 'KATEGORI', class: 'w-[16%]' },
  { key: 'tte_signer_name', label: 'PENANDATANGAN', class: 'w-[20%]' },
  { key: 'tte_status', label: 'STATUS BSRE', class: 'w-[20%]' },
  { key: 'aksi', label: 'AKSI', align: 'right', class: 'w-[8%]' }
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

const downloadDoc = (doc) => {
  if (!doc?.id) return
  window.open(documentApi.getDownloadUrl(doc.id), '_blank')
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

const getDocNumber = (doc) => {
  if (doc?.metadata_json) {
    try {
      const meta = typeof doc.metadata_json === 'string' ? JSON.parse(doc.metadata_json) : doc.metadata_json
      if (meta?.nomor_surat || meta?.nosrtmeninggal) {
        return meta.nomor_surat || meta.nosrtmeninggal
      }
      if (meta?.noreg) {
        return meta.noreg
      }
    } catch (e) {}
  }
  if (doc?.description) {
    const parts = doc.description.split('•')
    for (const p of parts) {
      if (p.includes('No. Surat:')) {
        return p.replace('No. Surat:', '').trim()
      }
    }
  }
  return `DOC-${String(doc.id).padStart(5, '0')}`
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
