<template>
  <Card class="border-slate-200 shadow-sm bg-white">
    <CardHeader class="pb-4 border-b border-slate-100 flex flex-row items-center justify-between">
      <div>
        <CardTitle class="text-base font-semibold text-slate-800">Upload Dokumen Rekam Medis</CardTitle>
        <CardDescription class="text-xs text-slate-500 mt-0.5">
          File akan dipindai virus (ClamAV) dan diindeks semantik sebelum disimpan.
        </CardDescription>
      </div>
      <Badge class="bg-emerald-50 text-emerald-700 border border-emerald-200">
        ✓ ClamAV Protection Active
      </Badge>
    </CardHeader>

    <CardContent class="pt-4 space-y-4">
      <!-- Metadata Form Menggunakan AppInput & AppSelect Modular -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AppInput
          id="upload-kunjungan-id"
          label="ID Kunjungan *"
          v-model="form.kunjunganId"
          type="number"
          placeholder="Contoh: 47615"
        />
        <AppInput
          id="upload-pasien-id"
          label="ID Pasien / No. RM *"
          v-model="form.pasienId"
          type="number"
          placeholder="Contoh: 275315"
        />
        <AppSelect
          id="upload-document-type"
          label="Tipe Dokumen"
          v-model="form.documentType"
          :options="docTypeOptions"
          text-key="label"
          value-key="value"
          option-key="value"
        />
      </div>

      <AppInput
        id="upload-title"
        label="Judul Dokumen"
        v-model="form.title"
        placeholder="Contoh: Hasil Konsultasi Bedah Onkologi Rawat Inap"
      />

      <AppTextarea
        id="upload-description"
        label="Deskripsi / Catatan Tambahan"
        v-model="form.description"
        placeholder="Ringkasan atau keluhan klinis untuk pencarian..."
      />

      <Alert v-if="errorMessage" variant="destructive">
        <AlertTitle class="text-xs font-bold">Gagal Mengunggah</AlertTitle>
        <AlertDescription class="text-xs">{{ errorMessage }}</AlertDescription>
      </Alert>

      <div class="flex justify-end pt-2">
        <Button
          :disabled="isUploading"
          @click="uploadSimulated"
          class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold"
        >
          {{ isUploading ? 'Mengunggah & Memindai...' : 'Simpan Dokumen' }}
        </Button>
      </div>
    </CardContent>
  </Card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import AppInput from '@/components/AppInput.vue'
import AppSelect from '@/components/AppSelect.vue'
import AppTextarea from '@/components/AppTextarea.vue'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'

const props = defineProps({
  kunjunganId: {
    type: [Number, String],
    default: 47615
  },
  pasienId: {
    type: [Number, String],
    default: 275315
  },
  defaultType: {
    type: String,
    default: 'konsul_spesialis'
  }
})

const emit = defineEmits(['uploaded'])

const docTypeOptions = [
  { value: 'surat_kematian', label: 'Surat Keterangan Kematian' },
  { value: 'konsul_spesialis', label: 'Lembar Konsultasi Spesialis' },
  { value: 'resume_medis', label: 'Resume Medis' },
  { value: 'hasil_lab', label: 'Hasil Laboratorium' },
  { value: 'radiologi', label: 'Hasil Radiologi' },
  { value: 'cppt', label: 'Catatan CPPT' },
  { value: 'general', label: 'Dokumen Umum Lainnya' }
]

const form = reactive({
  kunjunganId: props.kunjunganId,
  pasienId: props.pasienId,
  documentType: props.defaultType,
  title: '',
  description: ''
})

const isUploading = ref(false)
const errorMessage = ref('')

const uploadSimulated = () => {
  if (!form.kunjunganId || !form.pasienId) {
    errorMessage.value = 'ID Kunjungan dan ID Pasien wajib diisi.'
    return
  }
  emit('uploaded', { ...form })
}
</script>
