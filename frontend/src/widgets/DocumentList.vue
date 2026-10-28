<template>
  <div>
    <!-- Menggunakan Komponen Modular DataTablePremium -->
    <DataTablePremium
      title="Dokumen Resmi Terverifikasi TTE BSrE"
      description="Seluruh dokumen rekam medis yang telah memiliki PDF resmi dan telah sah ditandatangani secara elektronik (TTE BSrE BSSN) • Retensi Arsip 5 Tahun"
      :items="documents"
      :columns="columns"
      :loading="loading"
      :page-size="meta.per_page"
      :server-side="true"
      :total-items="meta.total"
      :show-add-button="false"
      search-placeholder="Cari judul dokumen, nomor surat, nama pasien, No. RM..."
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

      <!-- Custom Cell: Dokumen & Versioning -->
      <template #cell-title="{ item }">
        <div class="flex items-center gap-2.5">
          <Badge variant="destructive" class="font-bold text-[10px]">PDF</Badge>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-semibold text-xs text-foreground hover:text-primary transition-colors">
                {{ item.title || item.filename }}
              </span>
              <Badge variant="outline" class="text-[10px] font-mono bg-primary/10 text-primary border-primary/30">
                v1.0 • Final TTE
              </Badge>
            </div>
            <div class="text-[10px] text-muted-foreground font-mono mt-0.5">{{ item.filename }}</div>
          </div>
        </div>
      </template>

      <!-- Custom Cell: Tipe & Pasien -->
      <template #cell-document_type="{ item }">
        <div>
          <Badge variant="secondary" class="text-[10px]">
            {{ formatType(item.document_type) }}
          </Badge>
          <div class="text-[11px] text-muted-foreground mt-0.5">
            Kunjungan #{{ item.kunjungan_id }} • RM #{{ item.pasien_id }}
          </div>
        </div>
      </template>

      <!-- Custom Cell: Status TTE -->
      <template #cell-tte_status="{ item }">
        <div>
          <Badge
            variant="outline"
            class="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 text-[11px] font-semibold"
          >
            ✓ Sah TTE BSrE
          </Badge>
          <div v-if="item.tte_signer_name" class="text-[10px] text-muted-foreground mt-1">
            Oleh: {{ item.tte_signer_name }}
          </div>
        </div>
      </template>

      <!-- Custom Cell: Waktu TTE & Ukuran -->
      <template #cell-uploaded_at="{ item }">
        <div class="text-xs text-muted-foreground">
          <div>{{ formatDate(item.tte_signed_at || item.uploaded_at) }}</div>
          <div class="text-[10px] text-muted-foreground/80">{{ ((item.file_size || 0) / 1024).toFixed(1) }} KB</div>
        </div>
      </template>

      <!-- Custom Cell: Aksi Cepat -->
      <template #cell-aksi="{ item }">
        <div class="flex items-center justify-end gap-1.5" @click.stop>
          <Button
            variant="outline"
            size="sm"
            class="h-7 px-2.5 text-[11px] rounded-lg text-primary border-primary/30"
            @click="emitView(item)"
          >
            Preview PDF & Versioning
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="h-7 px-2.5 text-[11px] text-emerald-500 border-emerald-500/30 rounded-lg"
            @click="openVerifyModal(item)"
          >
            Verifikasi BSrE
          </Button>
        </div>
      </template>
    </DataTablePremium>

    <!-- Verify BSrE Modal Menggunakan AppDialog Modular -->
    <AppDialog
      v-model="showVerifyModal"
      title="Validasi Keaslian & Versioning TTE BSrE BSSN"
      description="Hasil verifikasi integritas kriptografi SHA-256, sertifikat elektronik, dan riwayat versi dokumen."
      confirm-text="Tutup"
      cancel-text="Tutup"
      @confirm="showVerifyModal = false"
    >
      <div v-if="verifyData" class="space-y-3 text-xs">
        <div class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-500 font-semibold flex items-center justify-between">
          <span>Status: {{ verifyData.integrity?.integrity_status || 'Dokumen Valid dan Sah' }}</span>
          <Badge class="bg-emerald-600 text-white text-[10px]">v1.0 Signed</Badge>
        </div>
        <div class="grid grid-cols-2 gap-3 text-foreground">
          <div>
            <span class="text-muted-foreground block text-[10px]">Penandatangan</span>
            <strong>{{ verifyData.signer?.name }}</strong>
          </div>
          <div>
            <span class="text-muted-foreground block text-[10px]">Penerbit Sertifikat (CA)</span>
            <strong>{{ verifyData.certificate?.issuer }}</strong>
          </div>
        </div>
        <div>
          <span class="text-muted-foreground block text-[10px]">SHA-256 Dokumen Hash (Final Signed Version)</span>
          <div class="p-2 bg-muted/40 border border-border rounded font-mono text-[10px] break-all text-foreground">
            {{ verifyData.certificate?.sha256_hash }}
          </div>
        </div>
      </div>
    </AppDialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import DataTablePremium from '@/components/DataTablePremium.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { RefreshCw } from 'lucide-vue-next'

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
  { key: 'title', label: 'Dokumen & Versi' },
  { key: 'document_type', label: 'Tipe & Pasien' },
  { key: 'tte_status', label: 'Status TTE BSrE' },
  { key: 'uploaded_at', label: 'Waktu TTE' },
  { key: 'aksi', label: 'Aksi', align: 'right' }
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
    hasil_lab: 'Laboratorium',
    radiologi: 'Radiologi',
    cppt: 'CPPT',
    general: 'Umum'
  }
  return map[type] || type
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
