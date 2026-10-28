<template>
  <Card class="border-border shadow-md p-6 max-w-4xl mx-auto glass-panel text-foreground font-sans">
    <!-- Top Action Bar -->
    <div class="flex flex-wrap items-center justify-between pb-4 mb-4 border-b border-border gap-3">
      <div class="flex items-center gap-2">
        <Badge class="bg-primary/20 text-primary font-bold text-xs">SIMRS-V3</Badge>
        <h2 class="text-sm md:text-base font-bold text-foreground uppercase tracking-wide">
          Lembar Konsultasi Dokter Spesialis
        </h2>
        <Badge variant="secondary" class="text-xs">2 Konsultasi Tercatat</Badge>
      </div>

      <div class="flex items-center gap-2">
        <Button
          size="sm"
          :disabled="isGenerating"
          @click="generateAndSignPdf"
          class="bg-primary text-primary-foreground text-xs font-bold gap-2 rounded-xl"
        >
          <Printer class="w-4 h-4" />
          <span>{{ isGenerating ? 'Memproses PDF & TTE...' : 'Cetak Dokumen' }}</span>
        </Button>
      </div>
    </div>

    <!-- Notification generated -->
    <Alert v-if="successDoc" class="mb-4 bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
      <AlertTitle class="text-xs font-bold flex items-center justify-between">
        <span>✓ PDF Berhasil dibuat: {{ successDoc.filename }}</span>
        <Button variant="link" size="sm" class="h-6 text-xs text-primary font-bold" @click="$emit('view-generated', successDoc)">
          Lihat Viewer
        </Button>
      </AlertTitle>
    </Alert>

    <!-- KERTAS DOKUMEN CETAK -->
    <div class="border border-black p-4 bg-white text-[11px] leading-tight select-text">
      <div class="grid grid-cols-12 border border-black divide-x divide-black text-center mb-2">
        <div class="col-span-8 p-2 flex items-center justify-center gap-3">
          <img :src="logoKotaGrey" alt="Logo Pemkot" class="w-10 h-auto object-contain" />
          <div>
            <div class="font-bold text-xs tracking-wider">PEMERINTAH KOTA PROBOLINGGO</div>
            <div class="font-black text-sm tracking-wide">UOBK RSUD DOKTER MOHAMAD SALEH</div>
            <div class="text-[9px] text-slate-700">Jl. Mayjend Panjaitan No.65 Probolinggo Jawa Timur</div>
            <div class="text-[9px] text-slate-700">Telp. (0335) 433478,433119,421118 Fax. (0335) 432702</div>
          </div>
        </div>
        <div class="col-span-4 p-2 flex flex-col justify-center items-center bg-slate-50/50">
          <span class="font-bold text-xs leading-snug">LEMBAR KONSULTASI<br/>DOKTER SPESIALIS<br/>RAWAT INAP</span>
        </div>
      </div>

      <!-- IDENTITAS PASIEN (Grid Modular) -->
      <div class="border border-black divide-y divide-black text-[10px] mb-2">
        <div class="grid grid-cols-12 divide-x divide-black">
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">Nama Pasien</div>
          <div class="col-span-4 p-1.5 font-bold">: {{ dataPasien.nama }}</div>
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">No. RM / Noreg</div>
          <div class="col-span-4 p-1.5 font-bold">: {{ dataPasien.norm }} / {{ dataPasien.noreg }}</div>
        </div>
        <div class="grid grid-cols-12 divide-x divide-black">
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">Tgl Lahir / Usia</div>
          <div class="col-span-4 p-1.5">: {{ dataPasien.tgllahir }} ({{ dataPasien.usia }})</div>
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">Jenis Kelamin</div>
          <div class="col-span-4 p-1.5">: {{ dataPasien.kelamin }}</div>
        </div>
        <div class="grid grid-cols-12 divide-x divide-black">
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">Ruangan / Kelas</div>
          <div class="col-span-4 p-1.5">: {{ dataPasien.ruangan }} / {{ dataPasien.kelas }}</div>
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">Sistem Bayar</div>
          <div class="col-span-4 p-1.5">: {{ dataPasien.sistembayar }}</div>
        </div>
        <div class="grid grid-cols-12 divide-x divide-black">
          <div class="col-span-2 p-1.5 font-bold bg-slate-100">DPJP Utama</div>
          <div class="col-span-10 p-1.5 font-bold">: {{ dataPasien.dokter_dpjp }}</div>
        </div>
      </div>

      <div class="border border-black">
        <div class="bg-slate-200 p-1.5 font-bold flex justify-between border-b border-black text-[10px] uppercase">
          <span>I. PERMINTAAN KONSULTASI (ID: #{{ dataKonsul.id }})</span>
          <span class="text-blue-900 font-semibold">{{ dataKonsul.tgl_konsul }}</span>
        </div>

        <div class="p-2 space-y-1 text-[10px] border-b border-black">
          <div class="grid grid-cols-12 gap-1">
            <div class="col-span-3 font-bold">Kepada Yth. Teman Sejawat</div>
            <div class="col-span-9 font-bold">: {{ dataKonsul.dokter_konsulan }}</div>
          </div>
          <div class="grid grid-cols-12 gap-1">
            <div class="col-span-3 font-bold">Keperluan Konsultasi</div>
            <div class="col-span-9">: {{ dataKonsul.keperluan }}</div>
          </div>
          <div class="pt-1.5">
            <div class="font-bold underline mb-1">Ikhtisar Klinik / Masalah Medik & Permintaan Konsul:</div>
            <div class="p-2 bg-slate-50 border border-slate-200 rounded whitespace-pre-line text-slate-800">
              {{ dataKonsul.ikhtisar_klinik }}
            </div>
          </div>
        </div>

        <div class="bg-slate-200 p-1.5 font-bold flex justify-between border-b border-black text-[10px] uppercase">
          <span>II. JAWABAN KONSULTASI</span>
          <span class="text-emerald-800 font-semibold">{{ dataJawaban.tgl_jawab }}</span>
        </div>

        <div class="p-2 space-y-1 text-[10px] border-b border-black">
          <div class="pt-1">
            <div class="font-bold underline mb-1">Pendapat / Saran Tindakan Medik & Pengobatan:</div>
            <div class="p-2 bg-slate-50 border border-slate-200 rounded whitespace-pre-line text-slate-800 min-h-[60px]">
              {{ dataJawaban.pendapat_saran }}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 divide-x divide-black p-3 text-center text-[10px]">
          <div class="flex flex-col items-center justify-between p-2">
            <div>
              <p>Probolinggo, 25 Oktober 2026</p>
              <p class="font-bold">Dokter / Nakes Yang Mengonsulkan,</p>
            </div>
            <div class="my-2 relative inline-block p-1 bg-white">
              <img
                src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&ecc=H&data=TTE-BSRE-PENGIRIM"
                alt="QR TTE Pengirim"
                class="w-16 h-16"
              />
              <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <img :src="logoRsud" alt="Logo RSUD" class="w-4 h-4 bg-white p-0.5 rounded-full" />
              </div>
            </div>
            <div>
              <p class="font-bold">EFI DINDA MELASIH PRIHATINI, A.Md.Kep.</p>
            </div>
          </div>

          <div class="flex flex-col items-center justify-between p-2">
            <div>
              <p>Probolinggo, 25 Oktober 2026</p>
              <p class="font-bold">Dokter Spesialis Konsulan,</p>
            </div>
            <div class="my-2 relative inline-block p-1 bg-white">
              <img
                src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&ecc=H&data=TTE-BSRE-KONSULAN"
                alt="QR TTE Konsulan"
                class="w-16 h-16"
              />
              <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <img :src="logoRsud" alt="Logo RSUD" class="w-4 h-4 bg-white p-0.5 rounded-full" />
              </div>
            </div>
            <div>
              <p class="font-bold">dr. RIZKI HABIBIE, Sp.PD.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-3 pt-2 border-t border-slate-300 text-center text-[9px] text-slate-700 leading-snug">
        <div>Dokumen ini telah ditandatangani secara elektronik menggunakan sertifikat elektronik</div>
        <div>yang telah diterbitkan oleh Balai Besar Sertifikasi Elektronik (BSrE), Badan Siber dan Sandi Negara</div>
      </div>
    </div>
  </Card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { documentApi } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertTitle } from '@/components/ui/alert'
import { Printer } from 'lucide-vue-next'

import logoKotaGrey from '@/assets/images/logo-kota-grey.png'
import logoRsud from '@/assets/images/logo-rsud.png'

const props = defineProps({
  pasien: {
    type: Object,
    default: () => ({
      nama: 'Ny. ISTIANATULLAH',
      norm: '275315',
      noreg: '47615/10/2026/X',
      tgllahir: '1983-03-24',
      usia: '43 Tahun 7 Bulan 2 Hari',
      kelamin: 'Perempuan',
      ruangan: 'Ruang Flamboyan Kelas 3 / 3',
      kelas: 'BED : 3',
      sistembayar: 'BPJS JAMKESMAS',
      dokter_dpjp: 'dr. RIZKI HABIBIE, Sp.PD.'
    })
  },
  konsultasi: {
    type: Object,
    default: () => ({
      id: '109248',
      tgl_konsul: 'Minggu, 25 Oktober 2026 pukul 13:41 WIB',
      dokter_konsulan: 'dr. RIZKI HABIBIE, Sp.PD.',
      keperluan: 'Konsultasikan tindakan masalah medik saat ini',
      ikhtisar_klinik: 'Pasien dengan anemia HB 5.9, keadaan umum baik, kesadaran composmentis GCS 4-5-6.'
    })
  },
  jawaban: {
    type: Object,
    default: () => ({
      tgl_jawab: 'Minggu, 25 Oktober 2026 pukul 14:10 WIB',
      status_verifikasi: 'TERVERIFIKASI',
      pendapat_saran: 'Acc KRS. Lanjutkan pengobatan oral dan kontrol poli 1 minggu lagi.'
    })
  }
})

const emit = defineEmits(['document-created', 'view-generated'])

const dataPasien = reactive({ ...props.pasien })
const dataKonsul = reactive({ ...props.konsultasi })
const dataJawaban = reactive({ ...props.jawaban })

const isGenerating = ref(false)
const successDoc = ref(null)

const generateAndSignPdf = async () => {
  isGenerating.value = true
  successDoc.value = null
  try {
    const payload = {
      kunjungan_id: 47615,
      pasien_id: 275315,
      document_type: 'konsul_spesialis',
      title: 'Lembar Konsultasi Dokter Spesialis Rawat Inap - Ny. Istianatullah',
      pasien: dataPasien,
      konsultasi: dataKonsul,
      jawaban: dataJawaban
    }
    const res = await documentApi.generateSimrs(payload)
    successDoc.value = res.data.data
    emit('document-created', res.data.data)
  } catch (err) {
    console.error('Gagal membuat dokumen PDF dari data SIMRS:', err)
  } finally {
    isGenerating.value = false
  }
}
</script>
