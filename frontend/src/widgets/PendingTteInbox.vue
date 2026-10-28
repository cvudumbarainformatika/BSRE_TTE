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
              Inbox TTE Dokter — Otorisasi Dokumen Medis
            </h3>
            <Badge class="bg-amber-500 text-white font-black">
              {{ totalPending }} Dokumen
            </Badge>
          </div>
          <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
            Daftar dokumen Rekam Medis Elektronik (E-RM) yang masuk ke Inbox Anda untuk diverifikasi dan ditandatangani secara elektronik (TTE BSrE BSSN).
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2 self-end md:self-center">
        <Button
          variant="outline"
          size="sm"
          class="h-8 px-3 gap-1.5 text-xs rounded-lg border-border"
          :disabled="isLoading"
          @click="loadPendingDocs"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
          <span>Segarkan Inbox</span>
        </Button>
      </div>
    </div>

    <!-- Category Filter Bar -->
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
    </div>

    <!-- Feedback Banner Sukses -->
    <div v-if="successInfo" class="m-4">
      <Alert class="bg-emerald-500/10 border-emerald-500/30 text-emerald-500">
        <AlertTitle class="text-sm font-bold flex items-center justify-between">
          <span>✓ {{ successInfo.message }}</span>
          <Button variant="ghost" size="sm" class="h-6 px-2 text-xs" @click="successInfo = null">
            Tutup
          </Button>
        </AlertTitle>
        <AlertDescription class="text-xs text-muted-foreground mt-1">
          Penandatangan: <strong class="text-foreground">{{ successInfo.signer?.name || 'dr. RIA NURMALA SETYANINGRUM' }}</strong> •
          Waktu TTE: <strong class="text-foreground">{{ formatDateTime(successInfo.signed_at) }}</strong> •
          Sertifikat: <strong class="text-foreground">BSrE BSSN RI</strong>
        </AlertDescription>
      </Alert>
    </div>

    <!-- Table Dokumen Pending Menggunakan Komponen Modular Table -->
    <CardContent class="p-0">
      <Table>
        <TableHeader>
          <TableRow class="bg-muted/40">
            <TableHead class="text-xs font-bold uppercase">Jenis Dokumen</TableHead>
            <TableHead class="text-xs font-bold uppercase">Nama Pasien / Jenazah</TableHead>
            <TableHead class="text-xs font-bold uppercase">No. RM & Kunjungan</TableHead>
            <TableHead class="text-xs font-bold uppercase">Diterbitkan E-RM</TableHead>
            <TableHead class="text-xs font-bold uppercase text-center">Aksi</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          <TableRow v-if="isLoading">
            <TableCell colspan="5" class="py-12 text-center text-muted-foreground text-xs">
              Menyinkronkan & memeriksa antrean dokumen E-RM...
            </TableCell>
          </TableRow>

          <TableRow v-else-if="pendingDocs.length === 0">
            <TableCell colspan="5" class="py-12 text-center text-muted-foreground text-xs">
              Semua dokumen telah ditandatangani! Tidak ada dokumen menunggu TTE di Inbox saat ini.
            </TableCell>
          </TableRow>

          <TableRow
            v-else
            v-for="doc in pendingDocs"
            :key="doc.id"
          >
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
                  class="h-7 px-2.5 text-[11px] bg-primary text-primary-foreground font-bold rounded-lg shadow-xs"
                  @click="openSignModal(doc)"
                >
                  <ShieldCheck class="w-3.5 h-3.5 mr-1" />
                  Tanda Tangani TTE
                </Button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </CardContent>

    <!-- Modal Sign Dokumen Tunggal Menggunakan Komponen Modular AppDialog -->
    <AppDialog
      v-model="showSignModal"
      title="Otorisasi Tanda Tangan Elektronik (TTE) BSrE BSSN"
      :description="`Masukkan Passphrase BSrE Anda untuk menandatangani dokumen: ${selectedDoc?.title || ''}`"
      :confirm-text="isSigning ? 'Menandatangani...' : 'Tandatangani Sekarang'"
      cancel-text="Batal"
      :confirm-disabled="!passphrase || isSigning"
      @confirm="executeSign"
    >
      <div class="space-y-4 text-xs">
        <div v-if="selectedDoc" class="p-3 bg-muted/40 border border-border rounded-xl space-y-1">
          <div class="flex justify-between">
            <span class="text-muted-foreground">Dokumen:</span>
            <span class="font-bold text-foreground">{{ selectedDoc.title }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Pasien:</span>
            <span class="font-bold text-foreground">{{ getPasienName(selectedDoc) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Tujuan TTE:</span>
            <span class="font-mono text-foreground">{{ selectedDoc.target_signer_name || 'dr. RIA NURMALA SETYANINGRUM' }}</span>
          </div>
        </div>

        <AppInput
          id="inbox-passphrase-input"
          label="Passphrase / PIN Pengaman BSrE BSSN *"
          v-model="passphrase"
          type="password"
          placeholder="Masukkan Passphrase BSrE Anda..."
          hint="Passphrase dikirim secara terenkripsi ke Engine BSrE dan tidak disimpan di database."
          :error="errorMsg"
          @keyup.enter="executeSign"
        />
      </div>
    </AppDialog>
  </Card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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

const emit = defineEmits(['preview-doc', 'document-signed'])

const pendingDocs = ref([])
const totalPending = ref(0)
const summaryByType = ref({})
const selectedType = ref('')
const isLoading = ref(false)

const showSignModal = ref(false)
const selectedDoc = ref(null)
const passphrase = ref('')
const isSigning = ref(false)
const errorMsg = ref('')
const successInfo = ref(null)

const loadPendingDocs = async () => {
  isLoading.value = true
  try {
    const res = await documentApi.getPendingMyDocuments({
      document_type: selectedType.value || undefined
    })
    pendingDocs.value = res.data.data
    totalPending.value = res.data.total_pending
    summaryByType.value = res.data.summary_by_type
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

const openSignModal = (doc) => {
  selectedDoc.value = doc
  errorMsg.value = ''
  passphrase.value = ''
  showSignModal.value = true
}

const executeSign = async () => {
  if (!selectedDoc.value) return
  isSigning.value = true
  errorMsg.value = ''
  try {
    const res = await documentApi.signTte(selectedDoc.value.id, {
      passphrase: passphrase.value,
      catatan: 'Ditandatangani melalui Inbox TTE Dokter E-RM'
    })
    successInfo.value = {
      message: res.data.message || `Dokumen ${selectedDoc.value.title} berhasil ditandatangani!`,
      signer: res.data.signer,
      signed_at: res.data.signed_at || new Date().toISOString()
    }
    showSignModal.value = false
    passphrase.value = ''
    await loadPendingDocs()
    emit('document-signed', res.data)
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Gagal menandatangani dokumen dengan BSrE'
  } finally {
    isSigning.value = false
  }
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
      return meta.pasien?.nama || meta.pasien?.nama_panggil || doc.title
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
