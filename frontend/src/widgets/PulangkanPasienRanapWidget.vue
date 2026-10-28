<template>
  <div class="space-y-4">
    <!-- Card Utama: Pulangkan Pasien Ranap (Modular Card) -->
    <Card class="border-border shadow-xs glass-panel text-foreground">
      <CardHeader class="pb-4 border-b border-border">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <Badge class="bg-primary/10 text-primary border border-primary/30 uppercase font-bold text-[10px]">
                RANAP • TRANSAKSI KEPULANGAN
              </Badge>
              <CardTitle class="text-base font-black text-foreground uppercase">
                Alur Pemulangan Pasien Rawat Inap (Discharge)
              </CardTitle>
            </div>
            <CardDescription class="text-xs text-muted-foreground">
              Sistem otomatis mendeteksi kondisi kepulangan. Jika pasien meninggal dan belum di-TTE di menu dokumen, surat kematian otomatis dikirim ke Inbox TTE DPJP.
            </CardDescription>
          </div>

          <Button
            variant="outline"
            size="sm"
            :disabled="isLoading"
            @click="loadPatients"
            class="text-xs font-bold gap-1.5 rounded-lg border-border"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" />
            <span>Segarkan Data Pasien</span>
          </Button>
        </div>
      </CardHeader>

      <CardContent class="pt-5 space-y-5">
        <!-- 1. Pilih Pasien Ranap Menggunakan AppSelect Modular -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
          <div class="lg:col-span-8">
            <AppSelect
              id="select-pasien-pulang"
              label="Pilih Pasien Rawat Inap Yang Akan Dipulangkan"
              v-model="selectedNoreg"
              :options="patientOptions"
              text-key="label"
              value-key="value"
              option-key="value"
              placeholder="Pilih pasien ranap..."
              @update:model-value="onSelectPatient"
            />
          </div>

          <div class="lg:col-span-4">
            <AppSelect
              id="select-kondisi-pulang"
              label="Keadaan / Cara Keluar Pasien *"
              v-model="caraKeluar"
              :options="caraKeluarOptions"
              text-key="label"
              value-key="value"
              option-key="value"
            />
          </div>
        </div>

        <!-- 2. Ringkasan Data Pasien Menggunakan AppInput Modular -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 p-4 bg-muted/30 border border-border rounded-xl">
          <AppInput
            id="pulang-nama"
            label="Nama Lengkap Pasien"
            v-model="activePatient.nama"
            readonly
          />
          <AppInput
            id="pulang-noreg"
            label="No. Registrasi Ranap"
            v-model="activePatient.noreg"
            readonly
          />
          <AppInput
            id="pulang-norm"
            label="No. Rekam Medis (RM)"
            v-model="activePatient.norm"
            readonly
          />
          <AppInput
            id="pulang-dpjp"
            label="Dokter DPJP Penanggung Jawab"
            v-model="activePatient.dpjp_nama"
            readonly
          />
        </div>

        <!-- 3. Deteksi Status Dokumen Surat Kematian Terkini -->
        <div class="p-4 rounded-xl border transition-all" :class="statusCardClass">
          <div class="flex items-start gap-3">
            <div class="p-2 rounded-lg" :class="statusIconBgClass">
              <ShieldCheck v-if="activePatientTteStatus === 'SIGNED_BSRE'" class="w-5 h-5 text-emerald-400" />
              <Clock v-else class="w-5 h-5 text-amber-500" />
            </div>
            <div class="flex-1 space-y-1">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold uppercase tracking-wide">Status Dokumen Surat Kematian Pasien Ini:</span>
                <Badge
                  v-if="activePatientTteStatus === 'SIGNED_BSRE'"
                  class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold"
                >
                  ✓ SUDAH DI-TTE SAH BSrE
                </Badge>
                <Badge
                  v-else
                  variant="outline"
                  class="bg-amber-500/10 text-amber-500 border border-amber-500/30 text-[10px] font-bold"
                >
                  ⏳ BELUM DI-TTE
                </Badge>
              </div>
              <p class="text-xs leading-relaxed opacity-90">
                <template v-if="activePatientTteStatus === 'SIGNED_BSRE'">
                  Surat Keterangan Kematian telah ditandatangani sah melalui menu Dokumen. Ketika pasien dipulangkan, <strong>sistem tidak perlu mengirimkan berkas lagi ke Inbox TTE</strong>.
                </template>
                <template v-else>
                  Surat Keterangan Kematian belum ditandatangani di menu Dokumen. Sesuai alur, ketika tombol di bawah ditekan, <strong>sistem akan otomatis mengirimkan berkas ke Inbox TTE Dokter DPJP</strong> ({{ activePatient.dpjp_nama }}).
                </template>
              </p>
            </div>
          </div>
        </div>

        <!-- 4. Tombol Aksi: Proses Pulangkan Pasien -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div class="text-xs text-muted-foreground">
            Pastikan data kepulangan pasien sudah sesuai dengan rekam medis sebelum memproses.
          </div>

          <Button
            size="default"
            :disabled="isProcessing || !activePatient.noreg"
            @click="prosesPulangkanPasien"
            class="bg-primary text-primary-foreground font-bold text-xs gap-2 rounded-xl shadow-xs px-5"
          >
            <LogOut class="w-4 h-4" :class="{ 'animate-pulse': isProcessing }" />
            <span>{{ isProcessing ? 'Memproses Kepulangan...' : 'Proses Pulangkan Pasien Ranap' }}</span>
          </Button>
        </div>

        <!-- 5. Feedback Alert Modular Setelah Proses -->
        <Alert
          v-if="resultAlert"
          :variant="resultAlert.variant"
          class="mt-4"
          :class="resultAlert.variant === 'destructive' ? 'bg-destructive/10 border-destructive/30' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'"
        >
          <AlertTitle class="text-xs font-bold flex items-center justify-between">
            <span>{{ resultAlert.title }}</span>
            <Button variant="ghost" size="sm" class="h-6 px-2 text-xs" @click="resultAlert = null">
              Tutup
            </Button>
          </AlertTitle>
          <AlertDescription class="text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-2">
            <span>{{ resultAlert.message }}</span>
            <div class="flex items-center gap-2 shrink-0">
              <Button
                v-if="resultAlert.action === 'GO_INBOX'"
                size="sm"
                class="bg-primary text-primary-foreground text-xs h-7 rounded-lg font-bold"
                @click="$emit('navigate', 'inbox')"
              >
                Lihat di Inbox Dokter →
              </Button>
              <Button
                v-if="resultAlert.action === 'GO_DOC'"
                size="sm"
                variant="outline"
                class="border-primary/40 text-primary text-xs h-7 rounded-lg font-bold"
                @click="$emit('navigate-doc')"
              >
                Buka Menu Surat Kematian →
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppSelect from '@/components/AppSelect.vue'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { RefreshCw, ShieldCheck, Clock, LogOut } from 'lucide-vue-next'

const emit = defineEmits(['navigate', 'navigate-doc', 'patient-discharged'])

const patientList = ref([])
const isLoading = ref(false)
const isProcessing = ref(false)
const selectedNoreg = ref('47708/10/2026/X')
const caraKeluar = ref('C003')
const resultAlert = ref(null)

const activePatient = reactive({
  noreg: '47708/10/2026/X',
  norm: '705065',
  nama: 'BUDI UTOMO',
  tglkeluar: '27 Oktober 2026',
  nosrtmeninggal: '472.12/2728/425.102.8/KEM/X/2026',
  jamMeninggal: '08:47',
  diagnosa: 'Cardiac arrest, unspecified',
  dpjp_nama: 'dr. RIA NURMALA SETYANINGRUM',
  dpjp_nip: '198201262009032003',
  dpjp_kdpegsimrs: '57'
})

const activePatientTteStatus = ref('UNSIGNED')

const caraKeluarOptions = [
  { value: 'C003', label: 'Meninggal Dunia (C003)' },
  { value: 'C001', label: 'Sembuh / Izin Keluar Dokter' },
  { value: 'C002', label: 'Rujuk Ke Faskes / RS Lain' },
  { value: 'C004', label: 'Pulang Atas Permintaan Sendiri (APS)' }
]

const patientOptions = computed(() => {
  return patientList.value.map((p) => {
    let statusLabel = 'BELUM DI-TTE'
    if (p.tte_status === 'SIGNED_BSRE') {
      statusLabel = 'SUDAH TTE BSrE'
    } else if (p.document_id) {
      statusLabel = 'ADA DI INBOX'
    }
    return {
      value: p.noreg,
      label: `${p.pasien?.nama || '-'} (RM: ${p.norm} | No: ${p.nosrtmeninggal}) — [${statusLabel}]`
    }
  })
})

const statusCardClass = computed(() => {
  if (activePatientTteStatus.value === 'SIGNED_BSRE') {
    return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
  }
  return 'bg-amber-500/10 border-amber-500/30 text-amber-500'
})

const statusIconBgClass = computed(() => {
  if (activePatientTteStatus.value === 'SIGNED_BSRE') {
    return 'bg-emerald-500/20'
  }
  return 'bg-amber-500/20'
})

const applySelectedPatient = (rec) => {
  if (!rec) return
  selectedNoreg.value = rec.noreg
  activePatient.noreg = rec.noreg
  activePatient.norm = rec.norm
  activePatient.nama = rec.pasien?.nama || '-'
  activePatient.tglkeluar = rec.tgl_meninggal || '-'
  activePatient.nosrtmeninggal = rec.nosrtmeninggal || '-'
  activePatient.jamMeninggal = rec.jamMeninggal || '08:47'
  activePatient.diagnosa = rec.sebabkematian_ket || rec.diagnosa || 'Cardiac arrest, unspecified'
  activePatient.dpjp_nama = rec.dokter?.nama || 'dr. RIA NURMALA SETYANINGRUM'
  activePatient.dpjp_nip = rec.dokter?.nip || '198201262009032003'
  activePatient.dpjp_kdpegsimrs = rec.dokter?.kdpegsimrs || '57'
  activePatientTteStatus.value = rec.tte_status || 'UNSIGNED'
}

const onSelectPatient = (noregVal) => {
  const found = patientList.value.find((p) => p.noreg === noregVal)
  if (found) {
    applySelectedPatient(found)
  }
}

const loadPatients = async () => {
  isLoading.value = true
  try {
    const res = await documentApi.getMysqlSuratKematianList({ limit: 20, auto_sync: false })
    patientList.value = res.data.data || []

    const preferred =
      patientList.value.find((p) => p.noreg === selectedNoreg.value) ||
      patientList.value.find((p) => p.pasien?.nama?.includes('BUDI UTOMO')) ||
      patientList.value[0]

    if (preferred) {
      applySelectedPatient(preferred)
    }
  } catch (err) {
    console.error('Gagal memuat daftar pasien:', err)
  } finally {
    isLoading.value = false
  }
}

const prosesPulangkanPasien = async () => {
  isProcessing.value = true
  resultAlert.value = null
  try {
    const payload = {
      noreg: activePatient.noreg,
      norm: activePatient.norm,
      nama_pasien: activePatient.nama,
      tglkeluar: activePatient.tglkeluar,
      carakeluar: caraKeluar.value,
      keadaan_keluar: caraKeluar.value === 'C003' ? 'Meninggal' : 'Biasa',
      nosrtmeninggal: activePatient.nosrtmeninggal,
      jamMeninggal: activePatient.jamMeninggal,
      diagnosa: activePatient.diagnosa,
      dpjp_nama: activePatient.dpjp_nama,
      dpjp_nip: activePatient.dpjp_nip,
      dpjp_kdpegsimrs: activePatient.dpjp_kdpegsimrs
    }

    const res = await documentApi.pulangkanPasienRanap(payload)
    const data = res.data

    if (data.status === 'SENT_TO_INBOX') {
      resultAlert.value = {
        title: 'Pasien Berhasil Dipulangkan (Meninggal Dunia)',
        message: data.message,
        variant: 'default',
        action: 'GO_INBOX'
      }
      activePatientTteStatus.value = 'UNSIGNED'
    } else if (data.status === 'ALREADY_SIGNED') {
      resultAlert.value = {
        title: 'Pasien Berhasil Dipulangkan (Surat Kematian Telah Sah)',
        message: data.message,
        variant: 'default',
        action: 'GO_DOC'
      }
      activePatientTteStatus.value = 'SIGNED_BSRE'
    } else {
      resultAlert.value = {
        title: 'Pasien Berhasil Dipulangkan',
        message: data.message,
        variant: 'default',
        action: null
      }
    }

    await loadPatients()
    emit('patient-discharged', data)
  } catch (err) {
    resultAlert.value = {
      title: 'Gagal Memproses Kepulangan Pasien',
      message: err.response?.data?.detail || 'Terjadi kesalahan sistem saat memproses kepulangan pasien.',
      variant: 'destructive',
      action: null
    }
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  loadPatients()
})
</script>
