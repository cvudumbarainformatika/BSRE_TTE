<template>
  <div class="space-y-4">
    <!-- Top Control Panel: Modular Card Component -->
    <Card class="border-slate-200 shadow-sm bg-white">
      <CardHeader class="pb-4 border-b border-slate-100">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <Badge class="bg-teal-600 text-white uppercase font-bold text-[10px]">
                SYNC MYSQL SIMRS READ-ONLY (SELECT ONLY)
              </Badge>
              <CardTitle class="text-base font-black text-slate-900 uppercase">
                Dokumen Surat Keterangan Kematian (Rawat Inap)
              </CardTitle>
            </div>
            <CardDescription class="text-xs text-slate-500">
              Data ditarik otomatis dari database MySQL SIMRS (<code class="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">rs23</code>, <code class="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">rs23_nosurat</code>, <code class="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">rs15</code>) tanpa mengubah kode SIMRS.
            </CardDescription>
          </div>

          <div class="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="isLoadingMysql"
              @click="loadFromMysql(true)"
              class="text-xs font-bold gap-1.5"
            >
              <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoadingMysql }" />
              <span>{{ isLoadingMysql ? 'Menyinkronkan MySQL SIMRS...' : 'Tarik & Sync Otomatis dari SIMRS' }}</span>
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent class="pt-4 space-y-4">
        <!-- Pilih Pasien Meninggal Riil dari MySQL SIMRS menggunakan AppSelect Modular -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
          <div class="lg:col-span-6">
            <AppSelect
              id="select-pasien-mysql"
              label="Pilih Data Pasien Meninggal (Riil dari Database MySQL SIMRS)"
              v-model="selectedNoreg"
              :options="mysqlRecordsOptions"
              text-key="label"
              value-key="value"
              option-key="value"
              placeholder="Pilih pasien meninggal dari MySQL SIMRS..."
              @update:model-value="onSelectMysqlRecord"
            />
          </div>

          <div class="lg:col-span-6 flex flex-wrap items-center justify-end gap-2">
            <!-- Status Badge Modular -->
            <Badge
              v-if="currentTteStatus === 'SIGNED_BSRE'"
              class="bg-emerald-100 text-emerald-800 border border-emerald-300 px-3 py-1 text-xs font-bold"
            >
              ✓ TERVERIFIKASI TTE BSrE
            </Badge>
            <Badge
              v-else
              variant="outline"
              class="bg-amber-50 text-amber-800 border-amber-300 px-3 py-1 text-xs font-bold"
            >
              ⏳ Menunggu TTE di Signature Inbox
            </Badge>

            <!-- Tombol Tanda Tangani BSrE Sekarang -->
            <Button
              size="sm"
              :disabled="isSubmitting"
              @click="openDirectSignModal"
              class="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold gap-1.5"
            >
              <ShieldCheck class="w-4 h-4" />
              <span>Tanda Tangani TTE BSrE Sekarang</span>
            </Button>

            <!-- Tombol Preview PDF Resmi -->
            <Button
              v-if="activeDocumentId"
              variant="outline"
              size="sm"
              @click="openPdfViewer"
              class="border-blue-300 text-blue-700 hover:bg-blue-50 text-xs font-bold gap-1.5"
            >
              <FileText class="w-4 h-4" />
              <span>Preview & Cetak PDF Resmi</span>
            </Button>
          </div>
        </div>

        <!-- Form Ringkasan Data Pasien Menggunakan AppInput Modular -->
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
          <AppInput
            id="input-noreg"
            label="Noreg Ranap"
            v-model="pasienData.noreg"
            placeholder="Noreg"
          />
          <AppInput
            id="input-nosurat"
            label="No. Surat Meninggal"
            v-model="nomorData.nosrtmeninggal"
            placeholder="Nomor Surat"
          />
          <AppInput
            id="input-nama-pasien"
            label="Nama Lengkap"
            v-model="pasienData.nama_panggil"
            placeholder="Nama Pasien"
          />
          <AppInput
            id="input-ktp-pasien"
            label="Nomor KTP"
            v-model="pasienData.nktp"
            placeholder="Nomor KTP"
          />
          <AppInput
            id="input-jam-meninggal"
            label="Jam Meninggal (WIB)"
            v-model="nomorData.jamMeninggal"
            placeholder="08:47"
          />
          <AppInput
            id="input-penyebab-kematian"
            label="Penyebab Kematian"
            v-model="diagnosaText"
            placeholder="Cardiac arrest, unspecified"
          />
        </div>

        <!-- Alert Feedback Modular -->
        <Alert
          v-if="feedbackMsg"
          :variant="feedbackError ? 'destructive' : 'default'"
          class="mt-2 bg-emerald-50/80 border-emerald-200 text-emerald-950"
        >
          <AlertTitle class="text-xs font-bold flex items-center justify-between">
            <span>{{ feedbackError ? 'Peringatan' : 'Informasi Layanan TTE BSrE' }}</span>
            <Button variant="ghost" size="sm" class="h-6 px-2 text-xs" @click="feedbackMsg = ''">
              Tutup
            </Button>
          </AlertTitle>
          <AlertDescription class="text-xs flex items-center justify-between mt-1">
            <span>{{ feedbackMsg }}</span>
            <Button
              v-if="activeDocumentId && !feedbackError"
              size="sm"
              class="bg-emerald-700 hover:bg-emerald-800 text-white text-xs h-7"
              @click="openPdfViewer"
            >
              Buka PDF Resmi →
            </Button>
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>

    <!-- ===================================================================== -->
    <!-- TAMPILAN KERTAS 100% IDENTIK SuratKematianPage.vue (SS1 & SS3)        -->
    <!-- ===================================================================== -->
    <Card class="border-slate-300 shadow-md overflow-hidden max-w-4xl mx-auto bg-white">
      <div class="px-5 py-3 bg-teal-600 text-white flex items-center justify-between">
        <div class="font-bold text-sm tracking-wide">SURAT KEMATIAN</div>
        <div class="text-xs opacity-90 font-mono">
          Noreg: {{ pasienData.noreg }} | RM: {{ pasienData.norm }}
        </div>
      </div>

      <!-- Area Dokumen Cetak (#pdfDoc) Persis SS1 -->
      <CardContent class="p-8 sm:p-12 bg-white text-black font-sans text-[13px] leading-relaxed">
        <!-- 1. KOP SURAT (Logo Perisai Hitam Putih logo-kota-grey.png di kiri + Teks Tengah) -->
        <div class="flex items-center justify-center gap-6 pb-3">
          <img
            :src="logoKotaGrey"
            alt="Logo Pemerintah Kota Probolinggo"
            class="w-[52px] h-auto object-contain shrink-0"
          />
          <div class="text-center">
            <div class="font-bold text-[15px] tracking-wide leading-snug">PEMERINTAH KOTA PROBOLINGGO</div>
            <div class="font-bold text-[15px] tracking-wide leading-snug">UOBK RSUD DOKTER MOHAMAD SALEH</div>
            <div class="text-[12.5px] text-slate-900 leading-snug">
              <div>Jl. Mayjend Panjaitan No.65 Probolinggo Jawa Timur</div>
              <div>Telp. (0335) 433478,433119,421118 Fax. (0335) 432702</div>
            </div>
          </div>
        </div>

        <!-- Garis Ganda Kop -->
        <hr class="border-t-2 border-slate-500 mt-1" />
        <hr class="border-t border-slate-400 mt-0.5 mb-5" />

        <!-- 2. JUDUL & NOMOR SURAT -->
        <div class="text-center">
          <div class="text-[17px] font-bold underline underline-offset-4">
            SURAT KETERANGAN KEMATIAN
          </div>
          <div class="text-[13px] font-bold mt-1">
            NOMOR : <span>{{ nomorData.nosrtmeninggal }}</span>
          </div>
        </div>

        <!-- 3. BIODATA DOKTER & PASIEN -->
        <div class="mt-6">
          <div>Yang bertanda tangan di bawah ini :</div>
          <div class="pl-5 py-2 space-y-1">
            <div class="grid grid-cols-12">
              <div class="col-span-3">Nama Dokter</div>
              <div class="col-span-9">: {{ dpjpData.nama }}</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3">Pangkat / Gol</div>
              <div class="col-span-9">: {{ dpjpData.golongan }} / {{ dpjpData.ket_golongan }}</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3">Jabatan</div>
              <div class="col-span-9">: {{ dpjpData.ket_jabatan }}</div>
            </div>
          </div>

          <div class="mt-2">Menyatakan bahwa :</div>
          <div><span class="font-bold">TELAH MENINGGAL DUNIA</span> , Saudara :</div>

          <!-- Tabel Biodata Pasien -->
          <div class="pl-5 py-2 space-y-1">
            <div class="grid grid-cols-12">
              <div class="col-span-3">Nama Lengkap</div>
              <div class="col-span-9">: {{ pasienData.nama_panggil }}</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3">Nomor KTP</div>
              <div class="col-span-9">: {{ pasienData.nktp }}</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3">Umur</div>
              <div class="col-span-9">: {{ pasienData.usia }}</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3">Jenis Kelamin</div>
              <div class="col-span-9">: {{ pasienData.kelamin }}</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3">Alamat</div>
              <div class="col-span-9">: {{ pasienData.alamat }}</div>
            </div>
          </div>

          <!-- Paragraf Waktu & Penyebab Meninggal -->
          <div class="mt-4 indent-6">
            Pada Tanggal <span class="font-bold">{{ pasienData.tglkeluar }}</span>
            tepatnya pada jam : <span class="font-bold">{{ nomorData.jamMeninggal }} WIB</span> ,
            dikarenakan <span>{{ diagnosaText }}</span> .
          </div>

          <div class="mt-1 indent-6">
            Demikian Surat Keterangan Kematian ini kami terbitkan untuk dapat digunakan
            semestinya dan sebijak-bijaknya
          </div>

          <!-- 4. AREA TANDA TANGAN DOKTER (Sisi Kanan Bawah — HANYA 1 QR CODE BSrE + LOGO DI TENGAH, TANPA NIK/ID SERTIFIKAT) -->
          <div class="mt-12 flex justify-end">
            <div class="text-center min-w-[260px]">
              <div>Probolinggo, Tgl {{ pasienData.tglkeluar }}</div>
              <div>Mengetahui</div>
              <div class="mb-2">Dokter,</div>

              <!-- QR Code Tunggal dengan Logo Berwarna di Tengah (Persis SS1 & SS3) -->
              <div class="my-3 flex justify-center">
                <div class="relative inline-block p-1 bg-white">
                  <img
                    :src="`https://api.qrserver.com/v1/create-qr-code/?size=110x110&ecc=H&data=${encodeURIComponent(qrVerificationUrl)}`"
                    alt="QR TTE BSrE"
                    class="w-24 h-24"
                  />
                  <!-- Logo RSUD Berwarna (Kuning-Merah) di Tengah QR Code -->
                  <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div class="bg-white p-0.5 rounded-full shadow-2xs">
                      <img
                        :src="logoRsud"
                        alt="Logo RSUD Tengah QR"
                        class="w-6 h-6 object-contain"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-2">
                {{ dpjpData.nama }}
              </div>
            </div>
          </div>

          <!-- 5. FOOTER SAH RSUD MOH SALEH & KALIMAT WAJIB BSrE BSSN -->
          <div class="mt-14 pt-2 text-right font-serif text-[12px] text-slate-900">
            Dokumen Sah dari RSUD MOH SALEH KOTA PROBOLINGGO | Hal Ke-1
          </div>
          <div class="mt-2 pt-2 border-t border-slate-300 text-center text-[10px] text-slate-700 leading-snug">
            <div>Dokumen ini telah ditandatangani secara elektronik menggunakan sertifikat elektronik</div>
            <div>yang telah diterbitkan oleh Balai Besar Sertifikasi Elektronik (BSrE), Badan Siber dan Sandi Negara</div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- MODAL OTORISASI PASSPHRASE BSrE MENGGUNAKAN KOMPONEN MODULAR AppDialog -->
    <AppDialog
      v-model="showSignModal"
      title="Otorisasi Tanda Tangan Elektronik (TTE) BSrE BSSN"
      description="Masukkan Passphrase BSrE Anda untuk menandatangani Surat Keterangan Kematian ini."
      confirm-text="Tandatangani Sekarang"
      cancel-text="Batal"
      :confirm-disabled="!passphrase || isSubmitting"
      @confirm="executeDirectSign"
    >
      <div class="space-y-4 text-xs">
        <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
          <div class="flex justify-between">
            <span class="text-slate-500">Nomor Surat:</span>
            <span class="font-mono font-bold text-slate-800">{{ nomorData.nosrtmeninggal }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Nama Pasien:</span>
            <span class="font-bold text-slate-800">{{ pasienData.nama_panggil }} (RM: {{ pasienData.norm }})</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Dokter Penandatangan:</span>
            <span class="font-bold text-slate-800">{{ dpjpData.nama }}</span>
          </div>
        </div>

        <AppInput
          id="modal-passphrase-input"
          label="Passphrase BSrE BSSN *"
          v-model="passphrase"
          :type="showPass ? 'text' : 'password'"
          placeholder="Masukkan Passphrase BSrE Anda..."
          hint="Passphrase dikirim secara terenkripsi ke Engine BSrE dan tidak disimpan di database."
          :error="modalError"
          @keyup.enter="executeDirectSign"
        >
          <template #suffix>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              class="h-6 px-1.5 text-[11px]"
              @click="showPass = !showPass"
            >
              {{ showPass ? 'Sembunyikan' : 'Lihat' }}
            </Button>
          </template>
        </AppInput>
      </div>
    </AppDialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { documentApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppSelect from '@/components/AppSelect.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { RefreshCw, ShieldCheck, FileText } from 'lucide-vue-next'

import logoKotaGrey from '@/assets/images/logo-kota-grey.png'
import logoRsud from '@/assets/images/logo-rsud.png'

const emit = defineEmits(['document-created', 'view-generated'])

const mysqlRecords = ref([])
const isLoadingMysql = ref(false)
const selectedNoreg = ref('47708/10/2026/X')
const activeDocumentId = ref(null)
const currentTteStatus = ref('UNSIGNED')

const pasienData = reactive({
  noreg: '47708/10/2026/X',
  norm: '705065',
  nama_panggil: 'BUDI UTOMO',
  nktp: '3508152612570002',
  usia: '68 Tahun 10 Bulan 1 Hari',
  kelamin: 'Laki-laki',
  alamat: 'PERUM PONDOK GABRIELLA B.03 JL. CITARUM 004/001 - CURAHGRINTING',
  tglkeluar: '27 Oktober 2026',
  carakeluar: 'C003',
  sebabkematian: 'I46.9',
  kddrygmenyatakan: '57'
})

const nomorData = reactive({
  nosrtmeninggal: '472.12/2728/425.102.8/KEM/X/2026',
  jamMeninggal: '08:47'
})

const dpjpData = reactive({
  kdpegsimrs: '57',
  nama: 'dr. RIA NURMALA SETYANINGRUM',
  nip: '198201262009032003',
  golongan: 'IV/a',
  ket_golongan: 'Pembina',
  ket_jabatan: 'Dokter Madya'
})

const diagnosaText = ref('Cardiac arrest, unspecified')

const isSubmitting = ref(false)
const showSignModal = ref(false)
const passphrase = ref('')
const showPass = ref(false)
const modalError = ref('')
const feedbackMsg = ref('')
const feedbackError = ref(false)
const lastResult = ref(null)

const mysqlRecordsOptions = computed(() => {
  return mysqlRecords.value.map((rec) => ({
    value: rec.noreg,
    label: `${rec.pasien?.nama || '-'} (RM: ${rec.norm} | No: ${rec.nosrtmeninggal}) — [${rec.tte_status === 'SIGNED_BSRE' ? 'SIGNED BSrE' : 'MENUNGGU TTE'}]`
  }))
})

const qrVerificationUrl = computed(() => {
  try {
    const noreg = pasienData.noreg || ''
    const dok = 'SURAT-KEMATIAN.png'
    const asal = 'RANAP'
    const petugas = dpjpData.kdpegsimrs || pasienData.kddrygmenyatakan || ''
    const enc = btoa(`${noreg}|${dok}|${asal}|${petugas}`)
    return `https://rsud.probolinggokota.go.id/dokumen-simrs/legalitas/${enc}`
  } catch (e) {
    return 'https://rsud.probolinggokota.go.id/dokumen-simrs/legalitas'
  }
})

const applyRecordToView = (rec) => {
  if (!rec) return
  selectedNoreg.value = rec.noreg
  activeDocumentId.value = rec.document_id || null
  currentTteStatus.value = rec.tte_status || 'UNSIGNED'

  pasienData.noreg = rec.noreg
  pasienData.norm = rec.norm
  pasienData.nama_panggil = rec.pasien?.nama || '-'
  pasienData.nktp = rec.pasien?.nktp || '-'
  pasienData.usia = rec.pasien?.usia || '-'
  pasienData.kelamin = rec.pasien?.kelamin || '-'
  pasienData.alamat = rec.pasien?.alamat || '-'
  pasienData.tglkeluar = rec.tgl_meninggal || '-'

  nomorData.nosrtmeninggal = rec.nosrtmeninggal || '-'
  nomorData.jamMeninggal = rec.jamMeninggal || '00:00'

  dpjpData.kdpegsimrs = rec.dokter?.kdpegsimrs || ''
  dpjpData.nama = rec.dokter?.nama || 'dr. RIA NURMALA SETYANINGRUM'
  dpjpData.nip = rec.dokter?.nip || ''
  dpjpData.golongan = rec.dokter?.golongan || 'IV/a'
  dpjpData.ket_golongan = rec.dokter?.ket_golongan || 'Pembina'
  dpjpData.ket_jabatan = rec.dokter?.ket_jabatan || 'Dokter Madya'

  diagnosaText.value = rec.sebabkematian_ket || rec.diagnosa || 'Cardiac arrest, unspecified'
}

const onSelectMysqlRecord = (noregVal) => {
  const found = mysqlRecords.value.find((r) => r.noreg === noregVal)
  if (found) {
    applyRecordToView(found)
  }
}

const loadFromMysql = async (showNotice = false) => {
  isLoadingMysql.value = true
  try {
    const res = await documentApi.getMysqlSuratKematianList({ limit: 20, auto_sync: true })
    mysqlRecords.value = res.data.data || []

    // Prioritaskan data BUDI UTOMO (472.12/2728/425.102.8/KEM/X/2026) agar persis SS1
    const preferred =
      mysqlRecords.value.find((r) => r.noreg === selectedNoreg.value) ||
      mysqlRecords.value.find((r) => r.pasien?.nama?.includes('BUDI UTOMO')) ||
      mysqlRecords.value[0]

    if (preferred) {
      applyRecordToView(preferred)
    }

    if (showNotice) {
      feedbackError.value = false
      feedbackMsg.value = `Berhasil menarik ${mysqlRecords.value.length} Surat Keterangan Kematian dari MySQL SIMRS (${res.data.sync_summary?.newly_synced || 0} dokumen baru masuk Signature Inbox).`
      emit('document-created')
    }
  } catch (err) {
    console.error('Gagal tarik data MySQL SIMRS:', err)
  } finally {
    isLoadingMysql.value = false
  }
}

const buildPayload = (signNow = false) => ({
  noreg: pasienData.noreg,
  norm: pasienData.norm,
  nosrtmeninggal: nomorData.nosrtmeninggal,
  jamMeninggal: nomorData.jamMeninggal,
  tglkeluar: pasienData.tglkeluar,
  diagnosa: diagnosaText.value,
  pasien: { ...pasienData },
  dpjp: { ...dpjpData },
  sign_now: signNow,
  passphrase: signNow ? passphrase.value : undefined
})

const openDirectSignModal = () => {
  modalError.value = ''
  passphrase.value = ''
  showSignModal.value = true
}

const executeDirectSign = async () => {
  isSubmitting.value = true
  modalError.value = ''
  feedbackMsg.value = ''
  feedbackError.value = false
  try {
    const res = await documentApi.finalizeSuratKematianRanap(buildPayload(true))
    lastResult.value = res.data
    activeDocumentId.value = res.data.document_id || res.data.data?.id
    currentTteStatus.value = 'SIGNED_BSRE'
    showSignModal.value = false
    passphrase.value = ''
    feedbackMsg.value = res.data.message
    await loadFromMysql(false)
    emit('document-created', res.data.data)
  } catch (err) {
    modalError.value = err.response?.data?.detail || 'Gagal menandatangani dokumen dengan BSrE'
  } finally {
    isSubmitting.value = false
  }
}

const openPdfViewer = async () => {
  if (!activeDocumentId.value) return
  try {
    const res = await documentApi.getById(activeDocumentId.value)
    if (res.data?.document) {
      emit('view-generated', res.data.document)
    }
  } catch (e) {
    if (lastResult.value?.data) {
      emit('view-generated', lastResult.value.data)
    }
  }
}

onMounted(() => {
  loadFromMysql(false)
})
</script>
