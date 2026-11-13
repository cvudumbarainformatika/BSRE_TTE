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
              Inbox Antrean TTE — Otorisasi Dokumen Elektronik
            </h3>
            <Badge class="bg-amber-500 text-white font-black">
              {{ totalPending }} Dokumen
            </Badge>
          </div>
          <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
            Daftar seluruh dokumen elektronik yang menunggu verifikasi dan tanda tangan elektronik (TTE BSrE BSSN) berdasarkan pejabat/dokter penandatangan tujuan.
          </p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2 self-end md:self-center">
        <!-- Tombol Batch TTE Utama -->
        <Button
          v-if="totalPending > 0"
          class="h-8 px-3.5 gap-2 text-xs font-bold rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 shadow-md hover:shadow-cyan-500/20 active:scale-95 transition-all cursor-pointer"
          :disabled="isLoading || isSigningBatch"
          @click="openBatchSignModal()"
        >
          <ShieldCheck class="w-4 h-4" />
          <span>
            {{ selectedDocIds.length > 0 ? `TTE Terpilih (${selectedDocIds.length})` : `TTE Sekaligus (${totalPending})` }}
          </span>
        </Button>

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

    <!-- Floating / Sticky Selection Bar saat ada dokumen dipilih -->
    <div
      v-if="selectedDocIds.length > 0"
      class="px-4 py-2.5 bg-primary/10 border-b border-primary/30 flex items-center justify-between gap-3 text-xs flex-wrap transition-all"
    >
      <div class="flex items-center gap-2">
        <Badge class="bg-primary text-primary-foreground font-bold text-xs">
          {{ selectedDocIds.length }} Terpilih
        </Badge>
        <span class="text-foreground font-medium text-xs">
          dokumen antrean siap ditandatangani sekaligus
        </span>
      </div>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          class="h-7 text-xs text-muted-foreground hover:text-foreground"
          @click="deselectAll"
        >
          Batalkan Pilihan
        </Button>
        <Button
          size="sm"
          class="h-7 px-3 bg-primary text-primary-foreground text-xs font-bold gap-1.5 shadow-sm hover:bg-primary/90"
          @click="openBatchSignModal()"
        >
          <ShieldCheck class="w-3.5 h-3.5" />
          <span>Lanjutkan Batch TTE ({{ selectedDocIds.length }}) →</span>
        </Button>
      </div>
    </div>

    <!-- Global Filter Bar: Jenis Dokumen & Tujuan Penandatangan (User TTE) -->
    <div class="p-4 bg-muted/30 border-b border-border flex flex-col lg:flex-row lg:items-center justify-between gap-3 text-xs">
      <!-- Filter Jenis Dokumen -->
      <div class="flex flex-wrap items-center gap-1.5">
        <span class="text-[11px] font-semibold text-muted-foreground mr-1">Jenis Dokumen:</span>
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

      <!-- Filter Penandatangan Tujuan (Dokumen Ini Untuk Siapa) -->
      <div v-if="Object.keys(summaryBySigner).length > 0" class="flex flex-wrap items-center gap-1.5 min-w-0">
        <span class="text-[11px] font-semibold text-muted-foreground mr-1 flex items-center gap-1 shrink-0">
          <UserCheck class="w-3.5 h-3.5 text-primary shrink-0" />
          <span>Tujuan TTE:</span>
        </span>
        <Button
          size="sm"
          :variant="selectedSigner === '' ? 'default' : 'outline'"
          class="h-8 text-xs rounded-lg shrink-0"
          @click="changeSigner('')"
        >
          Semua Penandatangan
        </Button>
        <Button
          v-for="(count, signerName) in summaryBySigner"
          :key="signerName"
          size="sm"
          :variant="selectedSigner === signerName ? 'default' : 'outline'"
          class="h-8 text-xs rounded-lg max-w-[220px]"
          :title="`${signerName} (${count} Dokumen)`"
          @click="changeSigner(signerName)"
        >
          <span class="truncate">{{ signerName }}</span>
          <span class="ml-1 shrink-0">({{ count }})</span>
        </Button>
      </div>
    </div>

    <!-- Feedback Banner Sukses -->
    <div v-if="successInfo" class="m-4">
      <Alert class="bg-emerald-500/10 border-emerald-500/30 text-emerald-500">
        <AlertTitle class="text-sm font-bold flex items-center justify-between gap-2">
          <span class="truncate" :title="successInfo.message">✓ {{ successInfo.message }}</span>
          <Button variant="ghost" size="sm" class="h-6 px-2 text-xs shrink-0" @click="successInfo = null">
            Tutup
          </Button>
        </AlertTitle>
        <AlertDescription class="text-xs text-muted-foreground mt-1 truncate">
          Penandatangan: <strong class="text-foreground">{{ successInfo.signer?.name || '-' }}</strong> •
          Waktu TTE: <strong class="text-foreground">{{ formatDateTime(successInfo.signed_at) }}</strong> •
          Sertifikat: <strong class="text-foreground">BSrE BSSN RI</strong>
        </AlertDescription>
      </Alert>
    </div>

    <!-- Table Dokumen Pending Global (Responsive Desktop & Mobile) -->
    <CardContent class="p-0">
      <!-- Desktop View (Layar Lapang: xl ke atas) -->
      <div class="hidden xl:block w-full overflow-hidden">
        <Table class="table-fixed w-full">
          <TableHeader>
            <TableRow class="bg-muted/40">
              <TableHead class="w-[5%] px-3 text-center">
                <Checkbox
                  :checked="isAllSelected"
                  :disabled="pendingDocs.length === 0"
                  title="Pilih Semua Dokumen"
                  @update:checked="toggleSelectAll"
                />
              </TableHead>
              <TableHead class="w-[18%] px-3 text-xs font-bold uppercase">Jenis Dokumen</TableHead>
              <TableHead class="w-[34%] px-3 text-xs font-bold uppercase">Perihal & No. Dokumen</TableHead>
              <TableHead class="w-[23%] px-3 text-xs font-bold uppercase">Tujuan TTE (Penandatangan)</TableHead>
              <TableHead class="w-[10%] px-2 text-xs font-bold uppercase">Status</TableHead>
              <TableHead class="w-[10%] px-3 text-xs font-bold uppercase text-right">Aksi</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            <TableRow v-if="isLoading">
              <TableCell colspan="6" class="py-12 text-center text-muted-foreground text-xs">
                Memuat daftar antrean dokumen TTE...
              </TableCell>
            </TableRow>

            <TableRow v-else-if="pendingDocs.length === 0">
              <TableCell colspan="6" class="py-12 text-center text-muted-foreground text-xs">
                Semua dokumen telah ditandatangani! Tidak ada dokumen menunggu TTE di Inbox saat ini.
              </TableCell>
            </TableRow>

            <TableRow
              v-else
              v-for="doc in pendingDocs"
              :key="doc.id"
              :class="{ 'bg-primary/5 border-l-2 border-l-primary': selectedDocIds.includes(doc.id) }"
            >
              <!-- Kolom 0: Checkbox Seleksi Batch -->
              <TableCell class="px-3 py-3 align-middle text-center" @click.stop>
                <Checkbox
                  :checked="selectedDocIds.includes(doc.id)"
                  @update:checked="(val) => toggleSelectDoc(doc.id, val)"
                />
              </TableCell>

              <!-- Kolom 1: Jenis Dokumen + Versi + Waktu Diterbitkan di bawahnya -->
              <TableCell class="px-3 py-3 align-middle">
                <div class="flex flex-nowrap items-center gap-1.5">
                  <Badge
                    :variant="doc.document_type === 'surat_kematian' ? 'destructive' : 'secondary'"
                    class="text-[10px] uppercase font-bold shrink-0 whitespace-nowrap"
                    :title="formatType(doc.document_type)"
                  >
                    {{ formatType(doc.document_type) }}
                  </Badge>
                  <Badge
                    variant="outline"
                    class="text-[10px] px-1.5 font-mono shrink-0 whitespace-nowrap"
                    :class="getDocVersion(doc) > 1 ? 'bg-amber-500/15 text-amber-500 border-amber-500/40 font-bold' : 'bg-primary/10 text-primary border-primary/30'"
                  >
                    {{ getDocVersion(doc) > 1 ? `Revisi v${getDocVersion(doc)}.0` : 'v1.0' }}
                  </Badge>
                </div>
                <div
                  class="text-[10px] text-muted-foreground mt-1.5 whitespace-nowrap"
                  :title="`Diterbitkan: ${formatDateTime(doc.uploaded_at)}`"
                >
                  {{ formatDateTime(doc.uploaded_at) }}
                </div>
              </TableCell>

              <!-- Kolom 2: Perihal & No. Dokumen (Global + Ellipsis) -->
              <TableCell class="px-3 py-3 align-middle">
                <div class="min-w-0 max-w-[340px] xl:max-w-none">
                  <div
                    class="text-foreground font-bold text-xs truncate"
                    :title="doc.title"
                  >
                    {{ doc.title }}
                  </div>
                  <div
                    class="text-[11px] text-muted-foreground mt-0.5 truncate"
                    :title="getDocReferenceSummary(doc)"
                  >
                    {{ getDocReferenceSummary(doc) }}
                  </div>
                  <div
                    class="text-[10px] text-muted-foreground/80 font-mono mt-0.5 truncate"
                    :title="doc.filename"
                  >
                    {{ doc.filename }}
                  </div>
                </div>
              </TableCell>

              <!-- Kolom 3: Tujuan TTE (Avatar & Nama Inline + Ellipsis) -->
              <TableCell class="px-3 py-3 align-middle">
                <div class="flex flex-nowrap items-center gap-2 min-w-0">
                  <div class="w-7 h-7 rounded-full bg-primary/15 text-primary border border-primary/30 flex items-center justify-center text-[10px] font-bold shrink-0">
                    {{ getSignerInitial(doc.target_signer_name) }}
                  </div>
                  <div class="min-w-0 flex-1 overflow-hidden">
                    <div
                      class="font-bold text-xs text-foreground truncate"
                      :title="doc.target_signer_name || 'Pejabat / Dokter Penandatangan'"
                    >
                      {{ doc.target_signer_name || 'Pejabat / Dokter Penandatangan' }}
                    </div>
                    <div
                      class="text-[10px] text-muted-foreground font-mono truncate mt-0.5"
                      :title="getSignerSubInfo(doc)"
                    >
                      {{ getSignerSubInfo(doc) }}
                    </div>
                  </div>
                </div>
              </TableCell>

              <!-- Kolom 4: Status Otorisasi (Ringkas: wait) -->
              <TableCell class="px-2 py-3 align-middle">
                <div class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[11px] font-medium whitespace-nowrap shadow-xs">
                  <Clock class="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <span>wait</span>
                </div>
              </TableCell>

              <!-- Kolom 5: Aksi (Hanya Icon dengan Tooltip) -->
              <TableCell class="px-3 py-3 align-middle text-right">
                <div class="flex flex-nowrap items-center justify-end gap-1.5 shrink-0">
                  <Button
                    variant="outline"
                    size="icon"
                    class="h-8 w-8 text-primary border-primary/30 hover:bg-primary/10 rounded-lg shrink-0 transition-transform active:scale-95"
                    title="Preview Dokumen PDF"
                    @click="$emit('preview-doc', doc)"
                  >
                    <Eye class="w-4 h-4" />
                  </Button>
                  <Button
                    size="icon"
                    class="h-8 w-8 bg-primary text-primary-foreground font-bold rounded-lg shadow-xs shrink-0 transition-transform active:scale-95 hover:bg-primary/90"
                    title="Tanda Tangani Dokumen secara Elektronik (TTE BSrE)"
                    @click="openSignModal(doc)"
                  >
                    <ShieldCheck class="w-4 h-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <!-- Mobile & Tablet Responsive Card View (Layar Lebih Kecil) -->
      <div class="xl:hidden divide-y divide-border">
        <div v-if="isLoading" class="py-10 text-center text-muted-foreground text-xs">
          Memuat daftar antrean dokumen TTE...
        </div>
        <div v-else-if="pendingDocs.length === 0" class="py-10 text-center text-muted-foreground text-xs px-4">
          Semua dokumen telah ditandatangani! Tidak ada dokumen menunggu TTE di Inbox saat ini.
        </div>
        <div
          v-else
          v-for="doc in pendingDocs"
          :key="`mob-${doc.id}`"
          class="p-4 space-y-3 transition-colors"
          :class="{ 'bg-primary/5 border-l-4 border-l-primary': selectedDocIds.includes(doc.id) }"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <Checkbox
                :checked="selectedDocIds.includes(doc.id)"
                @update:checked="(val) => toggleSelectDoc(doc.id, val)"
              />
              <Badge
                :variant="doc.document_type === 'surat_kematian' ? 'destructive' : 'secondary'"
                class="text-[10px] uppercase font-bold"
              >
                {{ formatType(doc.document_type) }}
              </Badge>
            </div>
            <span class="text-[10px] text-muted-foreground">{{ formatDateTime(doc.uploaded_at) }}</span>
          </div>
          <div class="min-w-0">
            <div class="font-bold text-xs text-foreground truncate">{{ doc.title }}</div>
            <div class="text-[11px] text-muted-foreground truncate mt-0.5">{{ getDocReferenceSummary(doc) }}</div>
          </div>
          <div class="flex flex-nowrap items-center justify-between gap-2 pt-2 border-t border-border/50">
            <div class="flex flex-nowrap items-center gap-2 min-w-0 flex-1">
              <div class="w-6 h-6 rounded-full bg-primary/15 text-primary border border-primary/30 flex items-center justify-center text-[10px] font-bold shrink-0">
                {{ getSignerInitial(doc.target_signer_name) }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="font-bold text-[11px] text-foreground truncate">{{ doc.target_signer_name }}</div>
                <div class="text-[10px] text-muted-foreground font-mono truncate">{{ getSignerSubInfo(doc) }}</div>
              </div>
            </div>
            <div class="flex flex-nowrap items-center gap-1.5 shrink-0">
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 text-primary border-primary/30 hover:bg-primary/10 rounded-lg shrink-0"
                title="Preview Dokumen PDF"
                @click="$emit('preview-doc', doc)"
              >
                <Eye class="w-4 h-4" />
              </Button>
              <Button
                size="icon"
                class="h-8 w-8 bg-primary text-primary-foreground font-bold rounded-lg shadow-xs shrink-0"
                title="Tanda Tangani Dokumen secara Elektronik (TTE BSrE)"
                @click="openSignModal(doc)"
              >
                <ShieldCheck class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </CardContent>

    <!-- Modal Sign Dokumen Tunggal Menggunakan Komponen Modular AppDialog -->
    <AppDialog
      v-model="showSignModal"
      title="Otorisasi Tanda Tangan Elektronik (TTE) BSrE BSSN"
      :description="`Masukkan Passphrase BSrE untuk menandatangani dokumen: ${selectedDoc?.title || ''}`"
      :confirm-text="isSigning ? 'Menandatangani...' : 'Tandatangani Sekarang'"
      cancel-text="Batal"
      :confirm-disabled="!passphrase || isSigning"
      @confirm="executeSign"
    >
      <div class="space-y-4 text-xs">
        <div v-if="selectedDoc" class="p-3 bg-muted/40 border border-border rounded-xl space-y-1.5">
          <div class="flex justify-between gap-2">
            <span class="text-muted-foreground">Jenis Dokumen:</span>
            <span class="font-bold text-foreground uppercase">{{ formatType(selectedDoc.document_type) }}</span>
          </div>
          <div class="flex justify-between gap-2">
            <span class="text-muted-foreground">Perihal Dokumen:</span>
            <span class="font-bold text-foreground text-right">{{ selectedDoc.title }}</span>
          </div>
          <div class="flex justify-between gap-2">
            <span class="text-muted-foreground">Nomor / Referensi:</span>
            <span class="font-mono text-foreground text-right">{{ getDocReferenceSummary(selectedDoc) }}</span>
          </div>
          <div class="flex justify-between gap-2 pt-1 border-t border-border">
            <span class="text-muted-foreground">Penandatangan (Tujuan TTE):</span>
            <span class="font-bold text-primary text-right">{{ selectedDoc.target_signer_name || '-' }}</span>
          </div>
        </div>

        <!-- Notifikasi Alert Error TTE BSrE -->
        <Alert v-if="errorMsg" variant="destructive" class="bg-destructive/10 border-destructive/40 text-destructive p-3">
          <AlertTitle class="text-xs font-bold">✕ Gagal Menandatangani Dokumen (BSrE)</AlertTitle>
          <AlertDescription class="text-[11px] mt-1 leading-relaxed">
            {{ errorMsg }}
          </AlertDescription>
        </Alert>

        <AppInput
          id="inbox-auth-code"
          label="Passphrase / PIN Pengaman BSrE BSSN *"
          v-model="passphrase"
          type="passphrase"
          placeholder="Masukkan Passphrase BSrE Anda..."
          hint="Passphrase dikirim secara terenkripsi ke Engine BSrE dan tidak disimpan di database."
          :error="errorMsg"
          @keyup.enter="executeSign"
        />
      </div>
    </AppDialog>

    <!-- MODAL DIALOG BATCH TTE (TTE SEKALIGUS SELURUH DOKUMEN TERPILIH) -->
    <AppDialog
      v-model="showBatchSignModal"
      title="Otorisasi Batch TTE BSrE (TTE Sekaligus)"
      description="Tanda tangan elektronik masal untuk seluruh dokumen terpilih dalam 1 kali otorisasi passphrase resmi BSrE BSSN."
      max-width="sm:max-w-md"
      confirm-text="Tanda Tangani Sekaligus"
      cancel-text="Batal"
      :confirm-disabled="!batchPassphrase || isSigningBatch"
      :loading="isSigningBatch"
      @confirm="executeBatchSign"
    >
      <div class="space-y-4 py-1 text-xs">
        <!-- Banner Info Ringkasan Batch -->
        <div class="p-3.5 bg-gradient-to-tr from-cyan-500/10 to-emerald-500/10 border border-cyan-500/30 rounded-xl space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-foreground flex items-center gap-1.5 text-xs">
              <ShieldCheck class="w-4 h-4 text-primary" />
              <span>Ringkasan Batch Dokumen</span>
            </span>
            <Badge class="bg-primary text-primary-foreground font-black text-xs">
              {{ targetBatchDocIds.length }} Dokumen
            </Badge>
          </div>
          <p class="text-muted-foreground leading-relaxed text-[11px]">
            Seluruh <strong>{{ targetBatchDocIds.length }} berkas dokumen</strong> yang Anda pilih akan dibubuhi stempel QR Code resmi dan tanda tangan digital terenkripsi RSA 2048-bit BSrE BSSN dalam satu kali proses.
          </p>
        </div>

        <!-- Notifikasi Error jika Batch Gagal -->
        <Alert v-if="batchErrorMsg" variant="destructive" class="bg-destructive/10 border-destructive/40 text-destructive p-3">
          <AlertTitle class="text-xs font-bold">✕ Otorisasi Batch TTE Gagal</AlertTitle>
          <AlertDescription class="text-[11px] mt-1 leading-relaxed">
            {{ batchErrorMsg }}
          </AlertDescription>
        </Alert>

        <!-- Input Passphrase BSrE -->
        <div class="space-y-1">
          <AppInput
            id="batch-auth-code"
            label="Passphrase / PIN Pengaman BSrE BSSN *"
            v-model="batchPassphrase"
            type="passphrase"
            placeholder="Ketik Passphrase BSrE Anda..."
            hint="Otorisasi 1 kali untuk seluruh dokumen yang dipilih."
            :error="batchErrorMsg"
            @keyup.enter="executeBatchSign"
          />
        </div>

        <!-- Input Catatan Pengesahan (Opsional) -->
        <div class="space-y-1">
          <AppInput
            id="batch-catatan-input"
            label="Catatan Pengesahan (Opsional)"
            v-model="batchCatatan"
            placeholder="Contoh: Disahkan secara masal melalui Inbox SIMRS"
          />
        </div>
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
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { Bell, ShieldCheck, RefreshCw, UserCheck, Eye, Clock } from 'lucide-vue-next'

const emit = defineEmits(['preview-doc', 'document-signed'])

const pendingDocs = ref([])
const totalPending = ref(0)
const summaryByType = ref({})
const summaryBySigner = ref({})
const selectedType = ref('')
const selectedSigner = ref('')
const isLoading = ref(false)

// State Seleksi & Batch Sign TTE Masal
const selectedDocIds = ref([])
const showBatchSignModal = ref(false)
const batchPassphrase = ref('')
const batchCatatan = ref('Ditandatangani secara masal via Inbox Antrean SIMRS')
const isSigningBatch = ref(false)
const batchErrorMsg = ref('')

const isAllSelected = computed(() => {
  return pendingDocs.value.length > 0 && selectedDocIds.value.length === pendingDocs.value.length
})

const toggleSelectAll = (checked) => {
  if (checked) {
    selectedDocIds.value = pendingDocs.value.map((d) => d.id)
  } else {
    selectedDocIds.value = []
  }
}

const toggleSelectDoc = (id, checked) => {
  if (checked) {
    if (!selectedDocIds.value.includes(id)) {
      selectedDocIds.value.push(id)
    }
  } else {
    selectedDocIds.value = selectedDocIds.value.filter((item) => item !== id)
  }
}

const deselectAll = () => {
  selectedDocIds.value = []
}

const targetBatchDocIds = computed(() => {
  if (selectedDocIds.value.length > 0) {
    return selectedDocIds.value
  }
  return pendingDocs.value.map((d) => d.id)
})

const openBatchSignModal = (presetIds = null) => {
  if (presetIds && Array.isArray(presetIds)) {
    selectedDocIds.value = presetIds
  } else if (selectedDocIds.value.length === 0) {
    // Jika tidak ada yang diceklis, otomatis targetkan seluruh dokumen pending
    selectedDocIds.value = pendingDocs.value.map((d) => d.id)
  }
  batchErrorMsg.value = ''
  batchPassphrase.value = ''
  batchCatatan.value = 'Ditandatangani secara masal via Inbox Antrean SIMRS'
  showBatchSignModal.value = true
}

const executeBatchSign = async () => {
  if (!batchPassphrase.value.trim()) {
    batchErrorMsg.value = 'Passphrase BSrE wajib diisi untuk otorisasi Batch TTE'
    return
  }

  const idsToSign = targetBatchDocIds.value
  if (!idsToSign || idsToSign.length === 0) {
    batchErrorMsg.value = 'Tidak ada dokumen yang dipilih untuk ditandatangani'
    return
  }

  isSigningBatch.value = true
  batchErrorMsg.value = ''

  try {
    const res = await documentApi.batchSignTte({
      document_ids: idsToSign,
      passphrase: batchPassphrase.value.trim(),
      catatan: batchCatatan.value.trim() || 'Ditandatangani secara masal via Inbox Antrean SIMRS'
    })

    const signedCount = res.data?.signed_count || idsToSign.length
    successInfo.value = {
      message: `Sukses! Sebanyak ${signedCount} dokumen berhasil ditandatangani sekaligus via BSrE BSSN.`,
      signer: res.data?.signer || { name: 'Pejabat Penandatangan' },
      signed_at: new Date().toISOString()
    }

    showBatchSignModal.value = false
    batchPassphrase.value = ''
    selectedDocIds.value = []

    await loadPendingDocs()
    emit('document-signed', res.data)
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      batchErrorMsg.value = detail.map((d) => d.msg).join(', ')
    } else {
      batchErrorMsg.value = detail || 'Gagal memproses Batch TTE BSrE'
    }
  } finally {
    isSigningBatch.value = false
  }
}

// State Sign Tunggal
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
      document_type: selectedType.value || undefined,
      target_signer: selectedSigner.value || undefined
    })
    pendingDocs.value = res.data.data
    totalPending.value = res.data.total_pending
    summaryByType.value = res.data.summary_by_type || {}
    summaryBySigner.value = res.data.summary_by_signer || {}
    // Bersihkan id yang sudah tidak ada
    selectedDocIds.value = selectedDocIds.value.filter((id) =>
      pendingDocs.value.some((d) => d.id === id)
    )
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

const changeSigner = (signer) => {
  selectedSigner.value = signer
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
      document_id: selectedDoc.value.id,
      passphrase: passphrase.value,
      catatan: 'Ditandatangani melalui Inbox Antrean TTE'
    })
    const signedData = res.data?.data || res.data
    successInfo.value = {
      message: res.data.message || `Dokumen ${selectedDoc.value.title} berhasil ditandatangani!`,
      signer: signedData?.signer || { name: selectedDoc.value.target_signer_name },
      signed_at: signedData?.signed_at || new Date().toISOString()
    }
    showSignModal.value = false
    passphrase.value = ''
    await loadPendingDocs()
    emit('document-signed', res.data)
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      errorMsg.value = detail.map((d) => d.msg).join(', ')
    } else {
      errorMsg.value = detail || 'Gagal menandatangani dokumen dengan BSrE'
    }
  } finally {
    isSigning.value = false
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
    general: 'Dokumen Umum'
  }
  return map[type] || type
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

const getSignerSubInfo = (doc) => {
  if (doc.metadata_json) {
    try {
      const meta = JSON.parse(doc.metadata_json)
      const nip = meta.dokter?.nip || meta.dpjp?.nip || doc.target_signer_nip
      const jabatan = meta.dokter?.ket_jabatan || meta.dpjp?.ket_jabatan
      if (nip && jabatan) return `NIP: ${nip} • ${jabatan}`
      if (nip) return `NIP/ID: ${nip}`
      if (jabatan) return jabatan
    } catch (e) {}
  }
  if (doc.target_signer_nip) return `ID Penandatangan: ${doc.target_signer_nip}`
  return 'Otorisasi TTE BSrE'
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
