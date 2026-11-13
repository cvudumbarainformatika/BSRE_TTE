<template>
  <div class="space-y-4">
    <!-- Header Kartu & Filter Bar Log Audit Trail -->
    <Card class="glass-panel border-border shadow-xs">
      <CardHeader class="p-4 sm:p-5 border-b border-border/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-muted/20">
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-mono px-2.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/30 flex items-center gap-1.5 font-semibold">
              <ShieldCheck class="w-3.5 h-3.5 text-primary" />
              Sesuai Standar Audit Trail Kominfo & BSrE BSSN
            </span>
          </div>
          <CardTitle class="text-base sm:text-lg font-bold text-foreground mt-1.5 flex items-center gap-2">
            <History class="w-5 h-5 text-primary" />
            <span>Rekam Log Audit Trail Tanda Tangan Elektronik</span>
          </CardTitle>
          <CardDescription class="text-xs text-muted-foreground mt-0.5">
            Mencatat riwayat waktu, user penandatangan, status berhasil/gagal, dokumen yang disahkan, dan alasan bila gagal.
          </CardDescription>
        </div>

        <div class="flex items-center gap-2 self-stretch sm:self-auto justify-end">
          <Button
            variant="outline"
            size="sm"
            class="h-9 text-xs rounded-xl gap-1.5 border-border hover:bg-muted/60"
            :disabled="isLoading"
            @click="loadAuditTrail"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
            <span>Segarkan</span>
          </Button>
        </div>
      </CardHeader>

      <CardContent class="p-4 sm:p-5 space-y-4">
        <!-- 3 KPI Card Ringkas Audit Trail -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="p-3.5 rounded-xl bg-card border border-border flex items-center justify-between">
            <div>
              <span class="text-[11px] font-medium text-muted-foreground uppercase">Total Rekam Log</span>
              <div class="text-xl font-bold font-mono text-foreground mt-0.5">{{ logs.length }}</div>
            </div>
            <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
              <ScrollText class="w-4 h-4" />
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-card border border-emerald-500/30 bg-emerald-500/5 flex items-center justify-between">
            <div>
              <span class="text-[11px] font-medium text-emerald-600 dark:text-emerald-400 uppercase">TTE Berhasil</span>
              <div class="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5">
                {{ countSuccess }}
              </div>
            </div>
            <div class="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <CheckCircle2 class="w-4 h-4" />
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-card border border-rose-500/30 bg-rose-500/5 flex items-center justify-between">
            <div>
              <span class="text-[11px] font-medium text-rose-600 dark:text-rose-400 uppercase">Gagal / Ditolak</span>
              <div class="text-xl font-bold font-mono text-rose-600 dark:text-rose-400 mt-0.5">
                {{ countFailed }}
              </div>
            </div>
            <div class="w-9 h-9 rounded-xl bg-rose-500/10 text-rose-500 flex items-center justify-center">
              <AlertTriangle class="w-4 h-4" />
            </div>
          </div>
        </div>

        <!-- Filter & Search Controls -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
          <!-- Filter Kategori Status -->
          <div class="flex flex-wrap items-center gap-1.5">
            <Button
              v-for="f in filterOptions"
              :key="f.id"
              size="sm"
              :variant="activeStatusFilter === f.id ? 'default' : 'outline'"
              class="h-8 text-xs rounded-lg gap-1"
              @click="setStatusFilter(f.id)"
            >
              <component :is="f.icon" class="w-3.5 h-3.5" />
              <span>{{ f.label }}</span>
            </Button>
          </div>

          <!-- Input Pencarian Menggunakan AppInput -->
          <div class="w-full sm:w-72">
            <AppInput
              id="audit-search-input"
              v-model="searchQuery"
              placeholder="Cari user, dokumen, pasien, alasan..."
              class="h-8 text-xs"
              @input="debounceSearch"
            >
              <template #prefix>
                <Search class="w-3.5 h-3.5 text-muted-foreground" />
              </template>
            </AppInput>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Tabel Desktop View -->
    <Card class="glass-panel border-border shadow-xs overflow-hidden">
      <div class="hidden lg:block w-full overflow-x-auto">
        <Table class="table-fixed w-full">
          <TableHeader>
            <TableRow class="bg-muted/40">
              <TableHead class="w-[15%] px-3 text-xs font-bold uppercase">Waktu & Tanggal</TableHead>
              <TableHead class="w-[20%] px-3 text-xs font-bold uppercase">User / Penandatangan</TableHead>
              <TableHead class="w-[12%] px-2 text-xs font-bold uppercase text-center">Status</TableHead>
              <TableHead class="w-[28%] px-3 text-xs font-bold uppercase">Dokumen yang di-TT & Pasien</TableHead>
              <TableHead class="w-[18%] px-3 text-xs font-bold uppercase">Keterangan / Alasan Gagal</TableHead>
              <TableHead class="w-[7%] px-2 text-xs font-bold uppercase text-right">Detail</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            <TableRow v-if="isLoading">
              <TableCell colspan="6" class="py-12 text-center text-muted-foreground text-xs">
                Memuat data log audit trail...
              </TableCell>
            </TableRow>

            <TableRow v-else-if="logs.length === 0">
              <TableCell colspan="6" class="py-12 text-center text-muted-foreground text-xs">
                Tidak ada data log audit yang sesuai dengan kriteria filter saat ini.
              </TableCell>
            </TableRow>

            <TableRow
              v-else
              v-for="log in logs"
              :key="log.id"
              class="hover:bg-muted/30 transition-colors"
            >
              <!-- Kolom 1: Tanggal & Waktu -->
              <TableCell class="px-3 py-3 align-top font-mono text-xs">
                <div class="font-bold text-foreground">
                  {{ formatDateOnly(log.created_at) }}
                </div>
                <div class="text-[11px] text-muted-foreground mt-0.5">
                  {{ formatTimeOnly(log.created_at) }} WIB
                </div>
                <div class="text-[10px] text-muted-foreground/70 mt-1">
                  ID Log: #{{ log.id }}
                </div>
              </TableCell>

              <!-- Kolom 2: Nama User & Role -->
              <TableCell class="px-3 py-3 align-top">
                <div class="flex items-start gap-2">
                  <div class="w-7 h-7 rounded-full bg-primary/15 text-primary border border-primary/30 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    {{ getUserInitial(log.username) }}
                  </div>
                  <div class="min-w-0">
                    <div class="font-bold text-xs text-foreground truncate" :title="log.username">
                      {{ log.username || 'System' }}
                    </div>
                    <div class="text-[11px] text-primary/80 font-medium truncate mt-0.5">
                      {{ formatRole(log.user_role) }}
                    </div>
                    <div v-if="log.ip_address" class="text-[10px] text-muted-foreground font-mono mt-0.5">
                      IP: {{ log.ip_address }}
                    </div>
                  </div>
                </div>
              </TableCell>

              <!-- Kolom 3: Status Berhasil / Gagal -->
              <TableCell class="px-2 py-3 align-top text-center">
                <Badge
                  :variant="getStatusBadgeVariant(log.status)"
                  class="text-[10px] uppercase font-bold px-2 py-0.5 inline-flex items-center gap-1 shadow-2xs"
                  :class="getStatusBadgeClass(log.status)"
                >
                  <component :is="getStatusIcon(log.status)" class="w-3 h-3" />
                  <span>{{ log.status }}</span>
                </Badge>
                <div class="text-[9px] font-mono text-muted-foreground uppercase mt-1">
                  {{ log.action }}
                </div>
              </TableCell>

              <!-- Kolom 4: Dokumen yang di-TT & Pasien -->
              <TableCell class="px-3 py-3 align-top">
                <div class="space-y-1 min-w-0">
                  <div class="flex items-center gap-1.5 text-foreground font-bold text-xs truncate" :title="log.document_title">
                    <FileText class="w-3.5 h-3.5 text-primary shrink-0" />
                    <span class="truncate">{{ log.document_title || `Dokumen #${log.document_id}` }}</span>
                  </div>

                  <!-- Informasi Pasien jika tersedia -->
                  <div v-if="log.nama_pasien" class="flex items-center gap-1.5 flex-wrap">
                    <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                      <User class="w-3 h-3 shrink-0" />
                      <span class="truncate max-w-[180px]">{{ log.nama_pasien }}</span>
                      <span v-if="log.norm" class="font-mono text-[10px] text-emerald-700 dark:text-emerald-300">(RM: {{ log.norm }})</span>
                    </span>
                  </div>

                  <!-- Nomor Dokumen / Surat -->
                  <div v-if="log.nomor_surat" class="text-[11px] text-muted-foreground truncate font-mono">
                    No: {{ log.nomor_surat }}
                  </div>
                </div>
              </TableCell>

              <!-- Kolom 5: Keterangan / Alasan Bila Gagal -->
              <TableCell class="px-3 py-3 align-top">
                <div v-if="log.status === 'GAGAL'" class="p-2 rounded-lg bg-rose-500/10 border border-rose-500/25 text-rose-600 dark:text-rose-400 text-xs space-y-0.5">
                  <div class="font-bold flex items-center gap-1 text-[11px]">
                    <AlertTriangle class="w-3.5 h-3.5 shrink-0" />
                    <span>Alasan Kegagalan:</span>
                  </div>
                  <div class="text-[11px] leading-relaxed break-words line-clamp-3" :title="log.alasan_gagal">
                    {{ log.alasan_gagal || 'Otorisasi atau konektivitas BSrE terganggu' }}
                  </div>
                </div>

                <div v-else-if="log.details?.bsre_id" class="space-y-0.5 text-xs">
                  <div class="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-semibold truncate" :title="log.details.bsre_id">
                    ID: {{ log.details.bsre_id }}
                  </div>
                  <div class="text-[10px] text-muted-foreground truncate" :title="log.details.catatan || 'TTE BSrE Terverifikasi'">
                    {{ log.details.catatan || 'TTE BSrE Terverifikasi' }}
                  </div>
                </div>

                <div v-else class="text-xs text-muted-foreground">
                  {{ log.details?.catatan || log.details?.raw || 'Aktivitas sistem tercatat' }}
                </div>
              </TableCell>

              <!-- Kolom 6: Aksi Modal Detail -->
              <TableCell class="px-2 py-3 align-top text-right">
                <Button
                  variant="outline"
                  size="icon"
                  class="h-7 w-7 text-primary border-primary/30 hover:bg-primary/10 rounded-lg"
                  title="Lihat Detail Payload Audit"
                  @click="openDetailModal(log)"
                >
                  <Eye class="w-3.5 h-3.5" />
                </Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <!-- Mobile & Tablet Card View -->
      <div class="lg:hidden divide-y divide-border">
        <div v-if="isLoading" class="py-10 text-center text-muted-foreground text-xs">
          Memuat data log audit trail...
        </div>
        <div v-else-if="logs.length === 0" class="py-10 text-center text-muted-foreground text-xs px-4">
          Tidak ada data log audit yang sesuai kriteria.
        </div>
        <div
          v-else
          v-for="log in logs"
          :key="`mob-${log.id}`"
          class="p-4 space-y-2.5"
        >
          <div class="flex items-center justify-between gap-2">
            <span class="text-[11px] font-mono font-bold text-foreground">
              {{ formatDateOnly(log.created_at) }} • {{ formatTimeOnly(log.created_at) }} WIB
            </span>
            <Badge
              :variant="getStatusBadgeVariant(log.status)"
              class="text-[10px] uppercase font-bold px-2 py-0.5 inline-flex items-center gap-1"
              :class="getStatusBadgeClass(log.status)"
            >
              <component :is="getStatusIcon(log.status)" class="w-3 h-3" />
              <span>{{ log.status }}</span>
            </Badge>
          </div>

          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-full bg-primary/15 text-primary border border-primary/30 flex items-center justify-center text-[10px] font-bold shrink-0">
              {{ getUserInitial(log.username) }}
            </div>
            <div class="min-w-0 flex-1">
              <span class="text-xs font-bold text-foreground">{{ log.username }}</span>
              <span class="text-[11px] text-muted-foreground ml-1.5">({{ formatRole(log.user_role) }})</span>
            </div>
          </div>

          <div class="space-y-1">
            <div class="flex items-center gap-1.5 text-xs font-bold text-foreground truncate">
              <FileText class="w-3.5 h-3.5 text-primary shrink-0" />
              <span>{{ log.document_title }}</span>
            </div>
            <div v-if="log.nama_pasien" class="flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">
              <User class="w-3 h-3" />
              <span>{{ log.nama_pasien }}</span>
              <span v-if="log.norm" class="font-mono text-[10px] text-muted-foreground">(RM: {{ log.norm }})</span>
            </div>
          </div>

          <!-- Alasan Gagal di Mobile -->
          <div v-if="log.status === 'GAGAL'" class="p-2 rounded-lg bg-rose-500/10 border border-rose-500/25 text-rose-600 dark:text-rose-400 text-xs">
            <div class="font-bold flex items-center gap-1 text-[11px]">
              <AlertTriangle class="w-3 h-3" />
              <span>Alasan:</span>
            </div>
            <div class="text-[11px] mt-0.5">{{ log.alasan_gagal }}</div>
          </div>

          <div class="flex items-center justify-between pt-1 border-t border-border/50">
            <span class="text-[10px] text-muted-foreground font-mono">ID Log: #{{ log.id }}</span>
            <Button
              variant="outline"
              size="sm"
              class="h-7 text-xs rounded-lg gap-1"
              @click="openDetailModal(log)"
            >
              <Eye class="w-3 h-3" />
              <span>Detail Payload</span>
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Modal Dialog Detail Audit Log Menggunakan Komponen Modular AppDialog -->
    <AppDialog
      v-model="showDetailModal"
      title="Detail Bukti Audit Trail Kriptografi"
      :description="`Rekam jejak resmi aktivitas TTE #${selectedLog?.id || ''} pada sistem BSrE BSSN`"
      max-width="sm:max-w-xl"
      cancel-text="Tutup"
    >
      <div v-if="selectedLog" class="space-y-3 text-xs py-1 min-w-0 max-w-full overflow-hidden">
        <!-- Box 1: Metadata Transaksi Kriptografi (Grid 2 Kolom Kokoh Anti-Overflow) -->
        <div class="p-3.5 rounded-xl bg-muted/40 border border-border divide-y divide-border/40">
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">ID Rekam Log:</span>
            <span class="col-span-7 font-mono font-bold text-foreground">#{{ selectedLog.id }}</span>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Waktu Kejadian:</span>
            <span class="col-span-7 font-bold text-foreground">{{ formatFullDateTime(selectedLog.created_at) }} WIB</span>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Nama User / Penandatangan:</span>
            <span class="col-span-7 font-bold text-primary truncate" :title="selectedLog.username">
              {{ selectedLog.username || 'System / Service' }}
              <span class="font-normal text-muted-foreground ml-1">({{ formatRole(selectedLog.user_role) }})</span>
            </span>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Status Transaksi:</span>
            <div class="col-span-7 flex items-center">
              <Badge
                :variant="getStatusBadgeVariant(selectedLog.status)"
                class="text-[10px] uppercase font-bold px-2 py-0.5"
                :class="getStatusBadgeClass(selectedLog.status)"
              >
                {{ selectedLog.status }}
              </Badge>
            </div>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Action Code:</span>
            <span class="col-span-7 font-mono font-semibold text-foreground">{{ selectedLog.action }}</span>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Alamat IP:</span>
            <span class="col-span-7 font-mono text-muted-foreground">{{ selectedLog.ip_address || '-' }}</span>
          </div>
        </div>

        <!-- Alasan Kegagalan (Jika Status Gagal) -->
        <Alert v-if="selectedLog.status === 'GAGAL'" variant="destructive" class="bg-destructive/10 border-destructive/40 p-3">
          <AlertTitle class="text-xs font-bold flex items-center gap-1.5">
            <AlertTriangle class="w-3.5 h-3.5 text-destructive" />
            <span>Alasan Kegagalan TTE</span>
          </AlertTitle>
          <AlertDescription class="text-[11px] mt-1 leading-relaxed break-words whitespace-pre-wrap">
            {{ selectedLog.alasan_gagal }}
          </AlertDescription>
        </Alert>

        <!-- Box 2: Informasi Dokumen Terkait -->
        <div class="p-3.5 rounded-xl bg-muted/40 border border-border divide-y divide-border/40">
          <div class="font-bold text-foreground pb-1 flex items-center gap-1.5">
            <FileText class="w-3.5 h-3.5 text-primary" />
            <span>Informasi Dokumen Terkait:</span>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Judul Dokumen:</span>
            <span class="col-span-7 font-bold text-foreground truncate" :title="selectedLog.document_title">
              {{ selectedLog.document_title || `Dokumen #${selectedLog.document_id}` }}
            </span>
          </div>
          <div v-if="selectedLog.nama_pasien" class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Nama Pasien:</span>
            <span class="col-span-7 font-semibold text-emerald-600 dark:text-emerald-400 truncate">
              {{ selectedLog.nama_pasien }}
            </span>
          </div>
          <div v-if="selectedLog.norm" class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">No. Rekam Medis:</span>
            <span class="col-span-7 font-mono text-foreground">{{ selectedLog.norm }}</span>
          </div>
          <div class="grid grid-cols-12 gap-2 py-1 items-center">
            <span class="col-span-5 text-muted-foreground font-medium">Nomor Surat:</span>
            <span class="col-span-7 font-mono text-foreground">{{ selectedLog.nomor_surat || '-' }}</span>
          </div>
        </div>

        <!-- Box 3: Raw Details JSON Payload -->
        <div class="space-y-1">
          <span class="text-[11px] font-bold text-muted-foreground">Detail Data Mentah (Payload JSON):</span>
          <pre class="p-3 rounded-xl bg-slate-950 text-emerald-400 font-mono text-[10px] overflow-x-auto max-h-48 border border-border whitespace-pre-wrap break-all select-all">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </div>
      </div>
    </AppDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { auditApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
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
import {
  History,
  ShieldCheck,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertTriangle,
  Info,
  ScrollText,
  User,
  FileText,
  Eye
} from 'lucide-vue-next'

const logs = ref([])
const isLoading = ref(false)
const activeStatusFilter = ref('ALL')
const searchQuery = ref('')
const showDetailModal = ref(false)
const selectedLog = ref(null)

const filterOptions = [
  { id: 'ALL', label: 'Semua Status', icon: ScrollText },
  { id: 'SUCCESS', label: 'Berhasil', icon: CheckCircle2 },
  { id: 'FAILED', label: 'Gagal', icon: AlertTriangle },
  { id: 'TTE_ONLY', label: 'Hanya TTE', icon: ShieldCheck }
]

const countSuccess = computed(() => {
  return logs.value.filter((l) => l.status === 'BERHASIL').length
})

const countFailed = computed(() => {
  return logs.value.filter((l) => l.status === 'GAGAL').length
})

const loadAuditTrail = async () => {
  isLoading.value = true
  try {
    const res = await auditApi.getFullAuditTrail({
      limit: 150,
      search: searchQuery.value.trim() || undefined,
      status: activeStatusFilter.value
    })
    logs.value = res.data?.data || []
  } catch (err) {
    console.error('Gagal mengambil audit trail:', err)
  } finally {
    isLoading.value = false
  }
}

const setStatusFilter = (status) => {
  activeStatusFilter.value = status
  loadAuditTrail()
}

let searchTimer = null
const debounceSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadAuditTrail()
  }, 400)
}

const openDetailModal = (log) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const getStatusBadgeVariant = (status) => {
  if (status === 'BERHASIL') return 'default'
  if (status === 'GAGAL') return 'destructive'
  return 'secondary'
}

const getStatusBadgeClass = (status) => {
  if (status === 'BERHASIL') {
    return 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
  }
  if (status === 'GAGAL') {
    return 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30'
  }
  return 'bg-blue-500/15 text-blue-600 dark:text-blue-400 border border-blue-500/30'
}

const getStatusIcon = (status) => {
  if (status === 'BERHASIL') return CheckCircle2
  if (status === 'GAGAL') return AlertTriangle
  return Info
}

const getUserInitial = (name) => {
  if (!name) return 'U'
  const clean = name.replace(/^(dr\.|drg\.|prof\.|ns\.)\s*/i, '').trim()
  const words = clean.split(/\s+/).filter(Boolean)
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return clean.substring(0, 2).toUpperCase()
}

const formatRole = (role) => {
  if (!role) return 'Petugas'
  const r = role.toLowerCase()
  if (r.includes('dokter')) return 'Dokter DPJP'
  if (r.includes('admin') || r.includes('it') || r.includes('programmer')) return 'IT Administrator'
  if (r.includes('penandatangan')) return 'Penandatangan TTE'
  return role
}

const formatDateOnly = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

const formatTimeOnly = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleTimeString('id-ID', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatFullDateTime = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('id-ID', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadAuditTrail()
})

defineExpose({
  loadAuditTrail
})
</script>
