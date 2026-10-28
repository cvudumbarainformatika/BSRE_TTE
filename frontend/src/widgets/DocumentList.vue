<template>
  <div>
    <!-- Menggunakan Komponen Modular DataTablePremium -->
    <DataTablePremium
      title="Daftar Dokumen Pasien & TTE BSrE"
      :description="`Kunjungan ID: ${kunjunganId || 'Semua'} • Retensi Arsip Resmi 5 Tahun`"
      :items="documents"
      :columns="columns"
      :loading="loading"
      :page-size="meta.per_page"
      :server-side="true"
      :total-items="meta.total"
      :show-add-button="false"
      search-placeholder="Cari judul dokumen, nomor surat, nama pasien..."
      @change="onTableChange"
      @row-click="emitView"
    >
      <!-- Slot Filter Menggunakan Komponen Modular AppSelect & Button -->
      <template #filters>
        <div class="w-48">
          <AppSelect
            id="filter-tte-status"
            label="Filter Status TTE"
            v-model="filterTte"
            :options="tteFilterOptions"
            text-key="label"
            value-key="value"
            option-key="value"
            placeholder="Semua Status TTE"
            @update:model-value="loadDocuments"
          />
        </div>
        <Button
          variant="outline"
          size="sm"
          class="h-10 gap-1.5"
          :disabled="loading"
          @click="loadDocuments"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
          <span>Segarkan</span>
        </Button>
      </template>

      <!-- Custom Cell: Dokumen -->
      <template #cell-title="{ item }">
        <div class="flex items-center gap-2.5">
          <Badge variant="destructive" class="font-bold text-[10px]">PDF</Badge>
          <div>
            <div class="font-semibold text-xs text-slate-800 hover:text-blue-600">
              {{ item.title || item.filename }}
            </div>
            <div class="text-[10px] text-slate-400 font-mono">{{ item.filename }}</div>
          </div>
        </div>
      </template>

      <!-- Custom Cell: Tipe & Pasien -->
      <template #cell-document_type="{ item }">
        <div>
          <Badge variant="secondary" class="text-[10px]">
            {{ formatType(item.document_type) }}
          </Badge>
          <div class="text-[11px] text-slate-500 mt-0.5">
            Kunjungan #{{ item.kunjungan_id }} • RM #{{ item.pasien_id }}
          </div>
        </div>
      </template>

      <!-- Custom Cell: Status TTE -->
      <template #cell-tte_status="{ item }">
        <div>
          <Badge
            v-if="item.tte_status === 'SIGNED_BSRE'"
            class="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-semibold"
          >
            ✓ TTE BSrE Terverifikasi
          </Badge>
          <Badge
            v-else
            variant="outline"
            class="bg-amber-50 text-amber-700 border-amber-200 text-[11px]"
          >
            ⏳ Belum TTE
          </Badge>
          <div v-if="item.tte_signer_name" class="text-[10px] text-slate-400 mt-1">
            Oleh: {{ item.tte_signer_name }}
          </div>
        </div>
      </template>

      <!-- Custom Cell: Waktu Buat -->
      <template #cell-uploaded_at="{ item }">
        <div class="text-xs text-slate-600">
          <div>{{ formatDate(item.uploaded_at) }}</div>
          <div class="text-[10px] text-slate-400">{{ ((item.file_size || 0) / 1024).toFixed(1) }} KB</div>
        </div>
      </template>

      <!-- Custom Cell: Aksi Cepat -->
      <template #cell-aksi="{ item }">
        <div class="flex items-center justify-end gap-1.5" @click.stop>
          <Button
            variant="outline"
            size="sm"
            class="h-7 px-2.5 text-[11px]"
            @click="emitView(item)"
          >
            Preview
          </Button>
          <Button
            v-if="item.tte_status !== 'SIGNED_BSRE' && userRole === 'dokter'"
            size="sm"
            class="h-7 px-2.5 text-[11px] bg-emerald-600 hover:bg-emerald-700 text-white"
            @click="openSignModal(item)"
          >
            Sign BSrE
          </Button>
          <Button
            v-if="item.tte_status === 'SIGNED_BSRE'"
            variant="outline"
            size="sm"
            class="h-7 px-2.5 text-[11px] text-emerald-700 border-emerald-200"
            @click="openVerifyModal(item)"
          >
            Verifikasi
          </Button>
          <Button
            v-if="item.tte_status !== 'SIGNED_BSRE' && (userRole === 'dokter' || userRole === 'admin')"
            variant="ghost"
            size="sm"
            class="h-7 px-2 text-[11px] text-rose-600 hover:bg-rose-50"
            @click="confirmDeleteDoc(item)"
          >
            Hapus
          </Button>
        </div>
      </template>
    </DataTablePremium>

    <!-- Sign BSrE Modal Menggunakan AppDialog Modular -->
    <AppDialog
      v-model="showSignModal"
      title="Tanda Tangan Elektronik (TTE) BSrE BSSN"
      :description="`Anda akan menandatangani dokumen: ${activeDoc?.title || activeDoc?.filename || ''}`"
      :confirm-text="isSigning ? 'Menandatangani...' : 'Tandatangani Sekarang'"
      cancel-text="Batal"
      :confirm-disabled="!passphrase || isSigning"
      @confirm="executeSign"
    >
      <div class="space-y-3 text-xs">
        <AppInput
          id="doclist-passphrase-input"
          label="Passphrase / PIN Pengaman BSrE *"
          v-model="passphrase"
          type="password"
          placeholder="Masukkan Passphrase BSrE Anda..."
          :error="signErrorMsg"
          @keyup.enter="executeSign"
        />
      </div>
    </AppDialog>

    <!-- Verify BSrE Modal Menggunakan AppDialog Modular -->
    <AppDialog
      v-model="showVerifyModal"
      title="Validasi Keaslian TTE BSrE BSSN"
      description="Hasil verifikasi integritas kriptografi SHA-256 dan sertifikat elektronik."
      confirm-text="Tutup"
      cancel-text="Tutup"
      @confirm="showVerifyModal = false"
    >
      <div v-if="verifyData" class="space-y-3 text-xs">
        <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 font-semibold">
          Status: {{ verifyData.integrity?.integrity_status || 'Dokumen Valid dan Sah' }}
        </div>
        <div class="grid grid-cols-2 gap-3 text-slate-700">
          <div>
            <span class="text-slate-400 block text-[10px]">Penandatangan</span>
            <strong>{{ verifyData.signer?.name }}</strong>
          </div>
          <div>
            <span class="text-slate-400 block text-[10px]">Penerbit Sertifikat (CA)</span>
            <strong>{{ verifyData.certificate?.issuer }}</strong>
          </div>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">SHA-256 Dokumen Hash</span>
          <div class="p-2 bg-slate-50 border rounded font-mono text-[10px] break-all text-slate-700">
            {{ verifyData.certificate?.sha256_hash }}
          </div>
        </div>
      </div>
    </AppDialog>

    <!-- Delete Confirmation Modal Menggunakan AppDialog Modular -->
    <AppDialog
      v-model="showDeleteModal"
      title="Konfirmasi Hapus Dokumen"
      :description="`Apakah Anda yakin ingin menghapus dokumen '${docToDelete?.title || docToDelete?.filename || ''}'?`"
      confirm-text="Ya, Hapus"
      cancel-text="Batal"
      @confirm="executeDeleteDoc"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import DataTablePremium from '@/components/DataTablePremium.vue'
import AppSelect from '@/components/AppSelect.vue'
import AppInput from '@/components/AppInput.vue'
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
  { key: 'title', label: 'Dokumen' },
  { key: 'document_type', label: 'Tipe & Pasien' },
  { key: 'tte_status', label: 'Status TTE BSrE' },
  { key: 'uploaded_at', label: 'Waktu Buat' },
  { key: 'aksi', label: 'Aksi', align: 'right' }
]

const tteFilterOptions = [
  { value: 'ALL', label: 'Semua Status TTE' },
  { value: 'SIGNED_BSRE', label: 'Sudah TTE BSrE' },
  { value: 'UNSIGNED', label: 'Belum TTE' }
]

const documents = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterTte = ref('ALL')
const meta = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  total_pages: 1
})

const showSignModal = ref(false)
const showVerifyModal = ref(false)
const showDeleteModal = ref(false)
const activeDoc = ref(null)
const docToDelete = ref(null)
const passphrase = ref('')
const signErrorMsg = ref('')
const isSigning = ref(false)
const verifyData = ref(null)

const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: meta.page,
      per_page: meta.per_page,
      search: searchQuery.value || undefined,
      tte_status: filterTte.value && filterTte.value !== 'ALL' ? filterTte.value : undefined,
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

const openSignModal = (doc) => {
  activeDoc.value = doc
  passphrase.value = ''
  signErrorMsg.value = ''
  showSignModal.value = true
}

const executeSign = async () => {
  if (!activeDoc.value) return
  isSigning.value = true
  signErrorMsg.value = ''
  try {
    await documentApi.signTte(activeDoc.value.id, { passphrase: passphrase.value })
    showSignModal.value = false
    passphrase.value = ''
    await loadDocuments()
  } catch (err) {
    signErrorMsg.value = err.response?.data?.detail || 'Gagal menandatangani TTE BSrE'
  } finally {
    isSigning.value = false
  }
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

const confirmDeleteDoc = (doc) => {
  docToDelete.value = doc
  showDeleteModal.value = true
}

const executeDeleteDoc = async () => {
  if (!docToDelete.value) return
  try {
    await documentApi.delete(docToDelete.value.id)
    showDeleteModal.value = false
    await loadDocuments()
  } catch (err) {
    console.error('Gagal menghapus dokumen:', err)
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
