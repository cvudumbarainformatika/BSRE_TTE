<template>
  <Card class="border-border shadow-xs overflow-hidden glass-panel text-foreground">
    <!-- Top Alert / Notification Banner -->
    <div class="bg-amber-500/10 border-b border-amber-500/20 p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-start gap-3">
        <div class="p-2.5 bg-amber-500 text-white rounded-xl shadow-xs mt-0.5">
          <Bell class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold text-foreground">
              Signature Inbox — Antrean Dokumen Menunggu TTE BSrE
            </h3>
            <Badge class="bg-amber-500 text-white font-black animate-pulse">
              {{ totalPending }} Dokumen
            </Badge>
          </div>
          <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
            Antrean dokumen Rekam Medis Elektronik (E-RM) yang siap ditandatangani. Anda dapat menandatangani <strong>seluruh dokumen sekaligus (Batch Sign)</strong> dalam 1 kali otorisasi Passphrase BSrE.
          </p>
        </div>
      </div>

      <!-- Quick Action: Batch Sign Button -->
      <div class="flex items-center gap-2 self-end md:self-center">
        <Button
          size="sm"
          :disabled="selectedIds.length === 0 || isBatchSigning"
          @click="openBatchSignModal"
          class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold gap-2 rounded-xl"
        >
          <ShieldCheck class="w-4 h-4" />
          <span>Tanda Tangani Sekaligus ({{ selectedIds.length }} Terpilih)</span>
        </Button>
      </div>
    </div>

    <!-- Category Filter & Select All Bar -->
    <div class="p-4 bg-muted/30 border-b border-border flex flex-wrap items-center justify-between gap-3 text-xs">
      <div class="flex flex-wrap items-center gap-1.5">
        <Button
          size="sm"
          :variant="selectedType === '' ? 'default' : 'outline'"
          class="h-8 text-xs rounded-lg"
          @click="changeCategory('')"
        >
          Semua ({{ totalPending }})
        </Button>
        <Button
          v-for="(count, type) in summaryByType"
          :key="type"
          size="sm"
          :variant="selectedType === type ? 'default' : 'outline'"
          class="h-8 text-xs capitalize rounded-lg"
          @click="changeCategory(type)"
        >
          {{ formatType(type) }} ({{ count }})
        </Button>
      </div>

      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 cursor-pointer" @click="toggleSelectAll">
          <Checkbox :checked="isAllSelected" />
          <Label class="text-xs font-medium text-foreground cursor-pointer">
            Pilih Semua Dokumen ({{ pendingDocs.length }})
          </Label>
        </div>

        <Button
          variant="outline"
          size="sm"
          class="h-8 px-2.5 gap-1.5 text-xs rounded-lg border-border"
          :disabled="isLoading"
          @click="loadPendingDocs"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
          <span>Sinkron E-RM</span>
        </Button>
      </div>
    </div>

    <!-- Feedback Banner Batch Sukses -->
    <div v-if="batchSuccessInfo" class="m-4">
      <Alert class="bg-emerald-500/10 border-emerald-500/30 text-emerald-500">
        <AlertTitle class="text-sm font-bold flex items-center justify-between">
          <span>✓ {{ batchSuccessInfo.message }}</span>
          <Button variant="ghost" size="sm" class="h-6 px-2 text-xs" @click="batchSuccessInfo = null">
            Tutup
          </Button>
        </AlertTitle>
        <AlertDescription class="text-xs text-muted-foreground mt-1">
          Penandatangan: <strong class="text-foreground">{{ batchSuccessInfo.signer?.name }}</strong> •
          Waktu TTE: <strong class="text-foreground">{{ formatDateTime(batchSuccessInfo.signed_at) }}</strong> •
          Sertifikat: <strong class="text-foreground">BSrE BSSN RI</strong>
        </AlertDescription>
      </Alert>
    </div>

    <!-- Table Dokumen Pending Menggunakan Komponen Modular Table -->
    <CardContent class="p-0">
      <Table>
        <TableHeader>
          <TableRow class="bg-muted/40">
            <TableHead class="w-12 text-center">
              <div class="flex justify-center" @click="toggleSelectAll">
                <Checkbox :checked="isAllSelected" />
              </div>
            </TableHead>
            <TableHead class="text-xs font-bold uppercase">Jenis Dokumen</TableHead>
            <TableHead class="text-xs font-bold uppercase">Nama Pasien / Jenazah</TableHead>
            <TableHead class="text-xs font-bold uppercase">No. RM & Kunjungan</TableHead>
            <TableHead class="text-xs font-bold uppercase">Diterbitkan E-RM</TableHead>
            <TableHead class="text-xs font-bold uppercase text-center">Aksi Cepat</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          <TableRow v-if="isLoading">
            <TableCell colspan="6" class="py-12 text-center text-muted-foreground text-xs">
              Menyinkronkan & memeriksa antrean dokumen E-RM...
            </TableCell>
          </TableRow>

          <TableRow v-else-if="pendingDocs.length === 0">
            <TableCell colspan="6" class="py-12 text-center text-muted-foreground text-xs">
              Semua dokumen telah ditandatangani! Tidak ada dokumen pending TTE saat ini.
            </TableCell>
          </TableRow>

          <TableRow
            v-else
            v-for="doc in pendingDocs"
            :key="doc.id"
            :class="selectedIds.includes(doc.id) ? 'bg-primary/10' : ''"
          >
            <TableCell class="text-center">
              <div class="flex justify-center" @click="toggleDocSelection(doc.id)">
                <Checkbox :checked="selectedIds.includes(doc.id)" />
              </div>
            </TableCell>

            <TableCell>
              <div class="flex items-center gap-2">
                <Badge
                  :variant="doc.document_type === 'surat_kematian' ? 'destructive' : 'secondary'"
                  class="text-[10px] uppercase font-bold"
                >
                  {{ formatType(doc.document_type) }}
                </Badge>
                <span class="text-foreground font-semibold text-xs">{{ doc.title }}</span>
              </div>
              <div class="text-[10px] text-muted-foreground font-mono mt-0.5">{{ doc.filename }}</div>
            </TableCell>

            <TableCell>
              <div class="font-bold text-xs text-foreground">{{ getPasienName(doc) }}</div>
              <div class="text-[10px] text-muted-foreground">{{ doc.description }}</div>
            </TableCell>

            <TableCell>
              <div class="font-mono text-xs text-foreground">RM: {{ doc.pasien_id }}</div>
              <div class="text-[10px] text-muted-foreground font-mono">Kunjungan: #{{ doc.kunjungan_id }}</div>
            </TableCell>

            <TableCell class="whitespace-nowrap text-xs text-muted-foreground">
              <div>{{ formatDateTime(doc.uploaded_at) }}</div>
              <Badge variant="outline" class="mt-0.5 text-[10px] text-amber-500 border-amber-500/30 bg-amber-500/10">
                Menunggu TTE Anda
              </Badge>
            </TableCell>

            <TableCell class="text-center whitespace-nowrap">
              <div class="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  class="h-7 px-2.5 text-[11px] text-primary border-primary/30 rounded-lg"
                  @click="$emit('preview-doc', doc)"
                >
                  Preview PDF
                </Button>
                <Button
                  size="sm"
                  class="h-7 px-2.5 text-[11px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg"
                  @click="signSingleDoc(doc)"
                >
                  Sign TTE
                </Button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </CardContent>

    <!-- Modal Batch Sign Menggunakan Komponen Modular AppDialog -->
    <AppDialog
      v-model="showBatchModal"
      title="Otorisasi TTE BSrE Massal (Batch Sign)"
      :description="`Anda akan menandatangani secara elektronik ${selectedIds.length} dokumen sekaligus pada ${currentTodayString}.`"
      :confirm-text="isBatchSigning ? `Menandatangani ${selectedIds.length} Dokumen...` : `Tandatangani ${selectedIds.length} Dokumen Sekarang`"
      cancel-text="Batal"
      :confirm-disabled="!passphrase || isBatchSigning"
      @confirm="executeBatchSign"
    >
      <div class="space-y-4 text-xs">
        <AppInput
          id="batch-passphrase-input"
          label="Passphrase / PIN Pengaman BSrE BSSN *"
          v-model="passphrase"
          type="password"
          placeholder="Masukkan Passphrase BSrE Anda..."
          hint="Sesuai Kriteria Keamanan BSrE BSSN: Passphrase tidak disimpan pada browser maupun database."
          :error="batchErrorMsg"
          @keyup.enter="executeBatchSign"
        />
      </div>
    </AppDialog>
  </Card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { Bell, ShieldCheck, RefreshCw } from 'lucide-vue-next'

const emit = defineEmits(['preview-doc', 'batch-signed'])

const pendingDocs = ref([])
const totalPending = ref(0)
const summaryByType = ref({})
const selectedType = ref('')
const selectedIds = ref([])
const isLoading = ref(false)
const isBatchSigning = ref(false)

const showBatchModal = ref(false)
const passphrase = ref('')
const batchErrorMsg = ref('')
const batchSuccessInfo = ref(null)

const currentTodayString = computed(() => {
  return new Date().toLocaleDateString('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
})

const isAllSelected = computed(() => {
  if (pendingDocs.value.length === 0) return false
  return pendingDocs.value.every((d) => selectedIds.value.includes(d.id))
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = pendingDocs.value.map((d) => d.id)
  }
}

const toggleDocSelection = (docId) => {
  const idx = selectedIds.value.indexOf(docId)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(docId)
  }
}

const loadPendingDocs = async () => {
  isLoading.value = true
  try {
    const res = await documentApi.getPendingMyDocuments({
      document_type: selectedType.value || undefined
    })
    pendingDocs.value = res.data.data
    totalPending.value = res.data.total_pending
    summaryByType.value = res.data.summary_by_type
    selectedIds.value = pendingDocs.value.map((d) => d.id)
  } catch (err) {
    console.error('Gagal mengambil antrean pending:', err)
  } finally {
    isLoading.value = false
  }
}

const changeCategory = (type) => {
  selectedType.value = type
  loadPendingDocs()
}

const openBatchSignModal = () => {
  if (selectedIds.value.length === 0) return
  batchErrorMsg.value = ''
  passphrase.value = ''
  showBatchModal.value = true
}

const executeBatchSign = async () => {
  if (selectedIds.value.length === 0) return
  isBatchSigning.value = true
  batchErrorMsg.value = ''
  try {
    const res = await documentApi.batchSignTte({
      document_ids: selectedIds.value,
      passphrase: passphrase.value
    })
    batchSuccessInfo.value = res.data
    showBatchModal.value = false
    selectedIds.value = []
    passphrase.value = ''
    await loadPendingDocs()
    emit('batch-signed', res.data)
  } catch (err) {
    batchErrorMsg.value = err.response?.data?.detail || 'Gagal menandatangani batch dokumen'
  } finally {
    isBatchSigning.value = false
  }
}

const signSingleDoc = (doc) => {
  selectedIds.value = [doc.id]
  batchErrorMsg.value = ''
  passphrase.value = ''
  showBatchModal.value = true
}

const formatType = (type) => {
  const map = {
    surat_kematian: 'Surat Kematian',
    konsul_spesialis: 'Konsul Spesialis',
    resume_medis: 'Resume Medis',
    hasil_lab: 'Laboratorium',
    general: 'Umum'
  }
  return map[type] || type
}

const getPasienName = (doc) => {
  if (doc.metadata_json) {
    try {
      const meta = JSON.parse(doc.metadata_json)
      return meta.pasien?.nama || doc.title
    } catch (e) {}
  }
  return doc.title
}

const formatDateTime = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadPendingDocs()
})

defineExpose({
  loadPendingDocs
})
</script>
