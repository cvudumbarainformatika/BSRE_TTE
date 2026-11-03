<template>
  <div class="space-y-6">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl sm:text-2xl font-bold text-foreground flex items-center gap-2">
          <UploadCloud class="w-6 h-6 text-primary" />
          <span>Upload & Penandatanganan TTE PDF</span>
        </h2>
        <p class="text-xs sm:text-sm text-muted-foreground mt-1">
          Unggah berkas PDF, Word (.docx/.doc), atau EPUB (.epub), tentukan ukuran dan posisi QR Stempel BSrE secara presisi.
        </p>
      </div>
    </div>

    <!-- Main Grid: Form di Kiri, Interactive Viewer di Kanan -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- =================================================================== -->
      <!-- KOLOM KIRI: DROPZONE UPLOAD, METADATA & PENGATUR UKURAN QR          -->
      <!-- =================================================================== -->
      <div class="lg:col-span-5 space-y-5">
        <!-- 1. Dropzone Card -->
        <Card
          class="glass-panel border-2 border-dashed transition-all duration-200"
          :class="[
            isDraggingFile
              ? 'border-primary bg-primary/10 scale-[1.01]'
              : uploadSession
                ? 'border-emerald-500/40 bg-card'
                : 'border-border hover:border-primary/50 bg-card'
          ]"
          @dragover.prevent="isDraggingFile = true"
          @dragleave.prevent="isDraggingFile = false"
          @drop.prevent="onFileDrop"
        >
          <CardContent class="p-6 text-center">
            <!-- Hidden Input File -->
            <input
              ref="fileInputRef"
              type="file"
              accept=".pdf,.docx,.doc,.epub"
              class="hidden"
              @change="onFileInputChange"
            />

            <!-- Kondisi Belum Ada File -->
            <div v-if="!uploadSession && !isConverting" class="space-y-3">
              <div class="w-14 h-14 rounded-2xl bg-primary/15 text-primary mx-auto flex items-center justify-center shadow-md">
                <UploadCloud class="w-7 h-7" />
              </div>
              <div>
                <h3 class="text-sm font-bold text-foreground">Drag & Drop file PDF / Word / EPUB di sini</h3>
                <p class="text-xs text-muted-foreground mt-1">
                  Maksimal ukuran file: 25 MB (.pdf, .docx, .doc, .epub)
                </p>
              </div>
              <Button
                variant="outline"
                class="rounded-xl border-border text-foreground hover:bg-muted text-xs h-9 px-4 gap-2 font-medium"
                @click="triggerFileInput"
              >
                <FileUp class="w-4 h-4 text-primary" />
                <span>Pilih File Dokumen</span>
              </Button>
            </div>

            <!-- Kondisi Sedang Konversi / Uploading -->
            <div v-else-if="isConverting" class="py-6 space-y-3">
              <div class="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
              <div class="text-xs font-semibold text-foreground">Memproses & Mengonversi Dokumen...</div>
              <p class="text-[11px] text-muted-foreground">Menyiapkan halaman interaktif untuk stempel QR BSrE</p>
            </div>

            <!-- Kondisi Berkas Sudah Diunggah & Siap -->
            <div v-else class="space-y-3 text-left">
              <div class="flex items-center justify-between pb-3 border-b border-border">
                <div class="flex items-center gap-2.5 min-w-0">
                  <div class="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center shrink-0">
                    <FileCheck class="w-5 h-5" />
                  </div>
                  <div class="min-w-0">
                    <div class="text-xs font-bold text-foreground truncate" :title="uploadSession.original_filename">
                      {{ uploadSession.original_filename }}
                    </div>
                    <div class="text-[11px] text-muted-foreground">
                      {{ uploadSession.total_pages }} Halaman • PDF Standard
                    </div>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  class="text-xs text-muted-foreground hover:text-foreground h-8 px-2"
                  @click="triggerFileInput"
                >
                  <RotateCcw class="w-3.5 h-3.5 mr-1" /> Ganti
                </Button>
              </div>
              <div class="flex items-center gap-2 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                <CheckCircle2 class="w-4 h-4 shrink-0" />
                <span>Dokumen siap. Geser posisi stempel QR di kanvas halaman ke lokasi tanda tangan.</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 2. Form Metadata & Passphrase Card -->
        <Card class="glass-panel border-border shadow-xs">
          <CardHeader class="pb-3 border-b border-border">
            <div class="flex items-center gap-2">
              <SlidersHorizontal class="w-4 h-4 text-primary" />
              <CardTitle class="text-sm font-bold text-foreground">
                Metadata & Pengaturan TTE
              </CardTitle>
            </div>
            <CardDescription class="text-xs text-muted-foreground">
              Nomor surat bersifat opsional jika berkas tidak memiliki nomor.
            </CardDescription>
          </CardHeader>

          <CardContent class="p-5 space-y-4">
            <!-- Nomor Surat (Opsional) -->
            <div class="space-y-1">
              <AppInput
                id="upload-nomor-surat"
                label="Nomor Surat / Dokumen (Opsional)"
                v-model="form.nomor_surat"
                placeholder="Contoh: 800/1249/BKPSDM/2026 (Kosongkan jika tidak ada)"
                hint="Boleh dikosongkan jika surat/dokumen tidak mempunyai nomor."
              />
            </div>

            <!-- Perihal Dokumen -->
            <div class="space-y-1">
              <AppInput
                id="upload-perihal"
                label="Perihal / Judul Dokumen"
                v-model="form.perihal"
                placeholder="Contoh: Surat Keputusan (Otomatis nama berkas jika kosong)"
                hint="Digunakan sebagai judul arsip dokumen di sistem database."
              />
            </div>

            <!-- Kategori Dokumen -->
            <AppSelect
              id="upload-kategori"
              label="Kategori Dokumen"
              v-model="form.kategori"
              :options="kategoriOptions"
              placeholder="Pilih Kategori..."
            />

            <!-- PENGATUR UKURAN & POSISI STEMPEL QR DINAMIS (LIVE DRAG & RESIZE) -->
            <div class="p-3.5 rounded-xl bg-muted/40 border border-border space-y-2.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-bold text-foreground flex items-center gap-1.5">
                  <Maximize2 class="w-3.5 h-3.5 text-primary" />
                  <span>Ukuran Stempel QR:</span>
                </span>
                <Badge variant="outline" class="font-mono text-xs px-2.5 py-0.5 text-primary border-primary/30 font-bold bg-primary/5">
                  {{ qrSizeLabel }}
                </Badge>
              </div>

              <!-- Info Live & Petunjuk Seret Bebas -->
              <div class="rounded-lg bg-background/80 border border-border/80 p-2.5 space-y-1.5 text-xs text-muted-foreground">
                <div class="flex items-center justify-between text-[11px]">
                  <span class="flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span>Status Penempatan:</span>
                  </span>
                  <span class="font-mono font-medium text-foreground">
                    Hal. {{ form.target_page }} • X: {{ stampXPercent.toFixed(1) }}% • Y: {{ stampYPercent.toFixed(1) }}%
                  </span>
                </div>
                <div class="text-[11px] leading-relaxed text-muted-foreground/90 flex items-start gap-1.5 pt-1 border-t border-border/50">
                  <span class="text-primary font-bold">✨</span>
                  <span>
                    <strong>Seret Bebas:</strong> Geser stempel ke posisi manapun di kanvas, dan tarik sudut stempel (handle resize) untuk memperbesar atau memperkecil ukuran QR secara bebas dan presisi.
                  </span>
                </div>
              </div>

              <!-- Tombol Reset Cepat Posisi & Ukuran -->
              <div class="flex items-center justify-end">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="h-7 text-xs text-muted-foreground hover:text-foreground gap-1 px-2"
                  @click="resetStampToDefault"
                >
                  <RotateCcw class="w-3 h-3" />
                  <span>Reset Ukuran & Posisi</span>
                </Button>
              </div>
            </div>

            <!-- Passphrase Input -->
            <div class="space-y-1">
              <AppInput
                id="upload-passphrase"
                type="password"
                label="Passphrase Sertifikat BSrE (P12)"
                v-model="form.passphrase"
                placeholder="Ketik Passphrase Anda (contoh: Bsre2026.#!)"
                hint="Wajib diisi untuk otorisasi kriptografi penandatanganan resmi BSrE."
                :error="formErrors.passphrase"
              />
            </div>

            <!-- Tombol Submit Tanda Tangani -->
            <div class="pt-2">
              <Button
                class="w-full h-11 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-bold text-xs sm:text-sm shadow-md hover:shadow-emerald-500/25 transition-all gap-2"
                :disabled="isSigning || !uploadSession"
                @click="submitProcessSign"
              >
                <div v-if="isSigning" class="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                <FileSignature v-else class="w-4 h-4" />
                <span>{{ isSigning ? 'Memproses Pengesahan BSrE...' : 'Proses & Tanda Tangani Dokumen' }}</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- =================================================================== -->
      <!-- KOLOM KANAN: INTERACTIVE PDF LAYOUT VIEWER & STEMPEL QR MURNI       -->
      <!-- =================================================================== -->
      <div class="lg:col-span-7">
        <Card class="glass-panel border-border shadow-xs overflow-hidden">
          <!-- Card Header & Navigation Bar -->
          <CardHeader class="p-3.5 sm:p-4 border-b border-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-muted/20">
            <div class="flex items-center gap-2">
              <Eye class="w-4 h-4 text-primary" />
              <CardTitle class="text-xs sm:text-sm font-bold text-foreground">
                PDF Layout Viewer
                <span v-if="uploadSession" class="text-primary font-mono ml-1">
                  (Halaman {{ currentPage }} dari {{ totalPages }})
                </span>
              </CardTitle>
            </div>

            <!-- Pagination Controls (Awal, Prev, Input Halaman, Next, Akhir) -->
            <div v-if="uploadSession && totalPages > 1" class="flex items-center gap-1.5 w-full sm:w-auto justify-end">
              <!-- Halaman Pertama -->
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 rounded-lg border-border"
                :disabled="currentPage <= 1"
                title="Halaman Pertama (Hal. 1)"
                @click="goToPage(1)"
              >
                <ChevronsLeft class="w-4 h-4" />
              </Button>

              <!-- Halaman Sebelumnya -->
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 rounded-lg border-border"
                :disabled="currentPage <= 1"
                title="Halaman Sebelumnya"
                @click="goToPage(currentPage - 1)"
              >
                <ChevronLeft class="w-4 h-4" />
              </Button>

              <!-- Input Nomor Halaman Langsung -->
              <div class="flex items-center gap-1 px-2 py-0.5 bg-background border border-border rounded-lg shadow-2xs h-8">
                <span class="text-[11px] text-muted-foreground font-medium">Hal.</span>
                <Input
                  type="number"
                  min="1"
                  :max="totalPages"
                  v-model="pageInputNumber"
                  @keydown.enter="jumpToInputPage"
                  @blur="jumpToInputPage"
                  class="w-12 h-6 text-center text-xs font-mono font-bold px-1 py-0 border-border bg-muted/30 focus-visible:ring-1 focus-visible:ring-primary [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  title="Ketik nomor halaman dan tekan Enter untuk berpindah langsung"
                />
                <span class="text-xs font-mono text-muted-foreground">/ {{ totalPages }}</span>
              </div>

              <!-- Halaman Berikutnya -->
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 rounded-lg border-border"
                :disabled="currentPage >= totalPages"
                title="Halaman Berikutnya"
                @click="goToPage(currentPage + 1)"
              >
                <ChevronRight class="w-4 h-4" />
              </Button>

              <!-- Halaman Terakhir -->
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 rounded-lg border-border"
                :disabled="currentPage >= totalPages"
                :title="`Halaman Terakhir (Hal. ${totalPages})`"
                @click="goToPage(totalPages)"
              >
                <ChevronsRight class="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>

          <!-- Card Content / Canvas Viewer Area -->
          <CardContent class="p-4 sm:p-6 bg-slate-950/70 flex items-center justify-center min-h-[580px] relative select-none overflow-x-auto">
            <!-- Empty State / Belum Unggah -->
            <div v-if="!uploadSession" class="text-center py-20 px-4 space-y-3 max-w-md">
              <div class="w-16 h-16 rounded-3xl bg-slate-800/80 text-slate-400 mx-auto flex items-center justify-center border border-slate-700/60 shadow-lg">
                <FileText class="w-8 h-8" />
              </div>
              <h4 class="text-sm font-bold text-slate-200">Pratinjau Lembar Dokumen Kosong</h4>
              <p class="text-xs text-slate-400 leading-relaxed">
                Silakan pilih berkas dokumen PDF, Word, atau EPUB di kolom kiri untuk memuat lembar pratinjau dan menempatkan stempel QR tanda tangan.
              </p>
            </div>

            <!-- Page Container Aktif -->
            <div
              v-else
              ref="pageContainerRef"
              class="relative bg-white shadow-2xl rounded-sm border border-slate-700/60 transition-all mx-auto"
              style="width: 100%; max-width: 580px;"
            >
              <!-- Gambar Halaman Dokumen yang Dirender PyMuPDF -->
              <img
                :src="currentPagePreviewUrl"
                alt="PDF Page Preview"
                class="w-full h-auto block select-none pointer-events-none rounded-sm"
              />

              <!-- Draggable QR Stamp Overlay (HANYA QR SAJA, TANPA LABEL SAMPING, ASPECT RATIO 1:1) -->
              <div
                v-if="form.target_page === currentPage"
                class="absolute cursor-move select-none touch-none transition-shadow z-20 group"
                :style="stampStyle"
                @mousedown="startDrag"
                @touchstart="startDragTouch"
              >
                <!-- Stempel QR Murni Berbingkai Putus-putus Cyan -->
                <div
                  class="w-full h-full border-2 border-dashed border-cyan-400 bg-white/95 rounded-md p-1 shadow-2xl flex flex-col items-center justify-center relative overflow-hidden group-hover:border-cyan-300 transition-colors"
                >
                  <!-- Pattern QR Code Realistis -->
                  <div class="w-full h-full relative flex items-center justify-center bg-slate-50 rounded-xs border border-slate-200/80">
                    <!-- QR Finder Patterns di 3 Sudut -->
                    <div class="absolute top-1 left-1 w-3.5 h-3.5 border-2 border-slate-900 flex items-center justify-center">
                      <div class="w-1.5 h-1.5 bg-slate-900"></div>
                    </div>
                    <div class="absolute top-1 right-1 w-3.5 h-3.5 border-2 border-slate-900 flex items-center justify-center">
                      <div class="w-1.5 h-1.5 bg-slate-900"></div>
                    </div>
                    <div class="absolute bottom-1 left-1 w-3.5 h-3.5 border-2 border-slate-900 flex items-center justify-center">
                      <div class="w-1.5 h-1.5 bg-slate-900"></div>
                    </div>

                    <!-- Mock QR Matrix Dots -->
                    <div class="w-3/5 h-3/5 grid grid-cols-4 grid-rows-4 gap-0.5 opacity-80">
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-transparent"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-transparent"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-transparent"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-transparent"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-transparent"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                      <div class="bg-transparent"></div>
                      <div class="bg-slate-900 rounded-[0.5px]"></div>
                    </div>

                    <!-- Logo RSUD di Tengah QR -->
                    <div class="absolute w-4 h-4 rounded-full bg-gradient-to-tr from-cyan-600 to-emerald-500 border border-white shadow-xs flex items-center justify-center text-[7px] text-white font-black">
                      S
                    </div>
                  </div>
                </div>

                <!-- 4 Interactive Resize Handles di Setiap Sudut Stempel (Aspect Ratio 1:1) -->
                <!-- Sudut Kiri-Atas (NW) -->
                <div
                  class="absolute -top-1.5 -left-1.5 w-3.5 h-3.5 bg-white border-2 border-primary rounded-full cursor-nwse-resize shadow-md hover:scale-125 transition-transform z-30 flex items-center justify-center opacity-80 group-hover:opacity-100"
                  title="Seret untuk mengubah ukuran QR"
                  @mousedown.stop="startResize($event, 'nw')"
                  @touchstart.stop="startResizeTouch($event, 'nw')"
                >
                  <div class="w-1 h-1 bg-primary rounded-full"></div>
                </div>

                <!-- Sudut Kanan-Atas (NE) -->
                <div
                  class="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 bg-white border-2 border-primary rounded-full cursor-nesw-resize shadow-md hover:scale-125 transition-transform z-30 flex items-center justify-center opacity-80 group-hover:opacity-100"
                  title="Seret untuk mengubah ukuran QR"
                  @mousedown.stop="startResize($event, 'ne')"
                  @touchstart.stop="startResizeTouch($event, 'ne')"
                >
                  <div class="w-1 h-1 bg-primary rounded-full"></div>
                </div>

                <!-- Sudut Kiri-Bawah (SW) -->
                <div
                  class="absolute -bottom-1.5 -left-1.5 w-3.5 h-3.5 bg-white border-2 border-primary rounded-full cursor-nesw-resize shadow-md hover:scale-125 transition-transform z-30 flex items-center justify-center opacity-80 group-hover:opacity-100"
                  title="Seret untuk mengubah ukuran QR"
                  @mousedown.stop="startResize($event, 'sw')"
                  @touchstart.stop="startResizeTouch($event, 'sw')"
                >
                  <div class="w-1 h-1 bg-primary rounded-full"></div>
                </div>

                <!-- Sudut Kanan-Bawah (SE) - Handle Utama Beraksen Primary -->
                <div
                  class="absolute -bottom-2 -right-2 w-5 h-5 bg-primary border-2 border-white rounded-full cursor-nwse-resize shadow-lg hover:scale-125 transition-transform z-30 flex items-center justify-center ring-2 ring-primary/30"
                  title="Tarik sudut ini untuk memperbesar atau memperkecil QR"
                  @mousedown.stop="startResize($event, 'se')"
                  @touchstart.stop="startResizeTouch($event, 'se')"
                >
                  <Maximize2 class="w-2.5 h-2.5 text-white" />
                </div>

                <!-- Floating Coordinates & Dimension Tooltip Real-time -->
                <div class="absolute -top-7 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-slate-900/95 text-cyan-300 text-[10px] font-mono rounded-md shadow-lg pointer-events-none whitespace-nowrap border border-slate-700/80 flex items-center gap-1.5 backdrop-blur-xs">
                  <span class="font-bold text-white">{{ qrSizeLabel }}</span>
                  <span class="text-slate-400">|</span>
                  <span>X: {{ stampXPercent.toFixed(1) }}%, Y: {{ stampYPercent.toFixed(1) }}%</span>
                </div>
              </div>

              <!-- Tombol Pindah Stempel ke Halaman Ini jika Stempel Ada di Halaman Lain -->
              <div
                v-else
                class="absolute bottom-4 left-1/2 -translate-x-1/2 z-20"
              >
                <Button
                  size="sm"
                  variant="secondary"
                  class="rounded-xl shadow-lg border border-primary/40 text-xs font-semibold gap-1.5"
                  @click="form.target_page = currentPage"
                >
                  <FileSignature class="w-3.5 h-3.5 text-primary" />
                  <span>Pindahkan Stempel TTE ke Halaman {{ currentPage }}</span>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Dialog Hasil Sukses Pengesahan TTE BSrE -->
    <AppDialog
      v-model="isSuccessDialogOpen"
      title="Pengesahan Dokumen Elektronik Berhasil"
      max-width="sm:max-w-md"
      :hide-footer="true"
    >
      <div class="p-6 text-center space-y-4">
        <div class="w-16 h-16 rounded-full bg-emerald-500/15 text-emerald-500 mx-auto flex items-center justify-center">
          <CheckCircle2 class="w-8 h-8" />
        </div>

        <div>
          <h3 class="text-base font-bold text-foreground">Dokumen Resmi Ditandatangani</h3>
          <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
            Dokumen <strong class="text-foreground">{{ form.perihal || 'Dokumen' }}</strong> telah diverifikasi dan dibubuhi Tanda Tangan Elektronik resmi BSrE BSSN.
          </p>
        </div>

        <div class="p-3.5 rounded-xl bg-muted/60 border border-border text-left text-xs space-y-1.5">
          <div class="flex justify-between">
            <span class="text-muted-foreground">Nomor Surat:</span>
            <span class="font-bold text-foreground">{{ form.nomor_surat || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Status Integritas:</span>
            <span class="font-bold text-emerald-500">TERVERIFIKASI (SHA-256)</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Otoritas Sertifikat:</span>
            <span class="font-mono text-[11px] text-foreground">BSrE - BSSN RI</span>
          </div>
        </div>

        <div class="flex items-center gap-3 pt-2">
          <Button
            variant="outline"
            class="flex-1 rounded-xl text-xs h-10 border-border"
            @click="closeSuccessDialog"
          >
            Tutup
          </Button>
          <Button
            class="flex-1 rounded-xl text-xs h-10 bg-primary text-primary-foreground font-bold gap-1.5"
            @click="goToDocumentList"
          >
            <FileText class="w-4 h-4" />
            <span>Buka Arsip Dokumen</span>
          </Button>
        </div>
      </div>
    </AppDialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onUnmounted } from 'vue'
import { uploadTteApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppSelect from '@/components/AppSelect.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  UploadCloud,
  FileUp,
  FileCheck,
  FileText,
  SlidersHorizontal,
  FileSignature,
  Eye,
  ChevronsLeft,
  ChevronLeft,
  ChevronRight,
  ChevronsRight,
  RotateCcw,
  CheckCircle2,
  Maximize2
} from 'lucide-vue-next'

const emit = defineEmits(['document-signed', 'navigate-to'])

// Form State (Default Kosong agar tidak dikira placeholder)
const form = reactive({
  nomor_surat: '',
  perihal: '',
  kategori: 'general',
  tipe_stempel: 'qr_only',
  passphrase: '',
  target_page: 1
})

const formErrors = reactive({
  passphrase: ''
})

const kategoriOptions = [
  { value: 'general', text: 'Dokumen Umum / Mandiri' },
  { value: 'sk', text: 'Surat Keputusan (SK)' },
  { value: 'surat_keterangan', text: 'Surat Keterangan' },
  { value: 'surat_tugas', text: 'Surat Tugas' },
  { value: 'sertifikat', text: 'Sertifikat / Piagam' },
  { value: 'berita_acara', text: 'Berita Acara' },
  { value: 'rekam_medis', text: 'Rekam Medis / Klinis' }
]

// Upload & Preview State
const fileInputRef = ref(null)
const pageContainerRef = ref(null)
const isDraggingFile = ref(false)
const isConverting = ref(false)
const isSigning = ref(false)
const uploadSession = ref(null)
const currentPage = ref(1)
const pageInputNumber = ref(1)
const isSuccessDialogOpen = ref(false)
const signedResult = ref(null)

// =========================================================================
// PENGATUR UKURAN QR CODE (1:1 Aspect Ratio)
// =========================================================================
const qrWidthPercent = ref(12.5) // Default ~2.6 cm pada halaman A4 standar (595pt)

// Ukuran fisik riil terhitung (berdasarkan standar lebar kertas A4 = 21.0 cm / 595.28 pt)
const qrSizeCm = computed(() => {
  return ((qrWidthPercent.value / 100) * 21.0).toFixed(1)
})

const qrSizePt = computed(() => {
  return Math.round((qrWidthPercent.value / 100) * 595.28)
})

const qrSizeLabel = computed(() => {
  return `${qrSizeCm.value} x ${qrSizeCm.value} cm (${qrSizePt.value} pt)`
})

const resetStampToDefault = () => {
  stampXPercent.value = 70.0
  stampYPercent.value = 80.0
  qrWidthPercent.value = 12.5
}

// Draggable Coordinate State (Persentase 0 - 100%)
const stampXPercent = ref(70.0)
const stampYPercent = ref(80.0)

const stampStyle = computed(() => {
  return {
    left: `${stampXPercent.value}%`,
    top: `${stampYPercent.value}%`,
    width: `${qrWidthPercent.value}%`,
    aspectRatio: '1 / 1'
  }
})

const totalPages = computed(() => uploadSession.value?.total_pages || 1)

const currentPagePreviewUrl = computed(() => {
  if (!uploadSession.value) return ''
  return uploadTteApi.getPagePreviewUrl(uploadSession.value.upload_id, currentPage.value)
})

// Trigger File Picker
const triggerFileInput = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const onFileInputChange = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    handleFileUpload(file)
  }
}

const onFileDrop = (e) => {
  isDraggingFile.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) {
    handleFileUpload(file)
  }
}

// Upload & Convert
const handleFileUpload = async (file) => {
  isConverting.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await uploadTteApi.convertAndPreview(formData)
    uploadSession.value = res.data
    currentPage.value = 1
    pageInputNumber.value = 1
    form.target_page = 1

    // Otomatis isi perihal dari nama file jika belum diisi oleh pengguna
    if (!form.perihal.trim()) {
      const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' ')
      form.perihal = cleanName
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal memproses dan mengonversi berkas.')
  } finally {
    isConverting.value = false
  }
}

const goToPage = (p) => {
  if (p >= 1 && p <= totalPages.value) {
    currentPage.value = p
    pageInputNumber.value = p
  }
}

const jumpToInputPage = () => {
  let target = Number(pageInputNumber.value)
  if (isNaN(target) || target < 1) target = 1
  if (target > totalPages.value) target = totalPages.value
  goToPage(target)
}

// =========================================================================
// LOGIKA DRAGGABLE STEMPEL (POINTER / MOUSE / TOUCH)
// =========================================================================
let isDragging = false
let startX = 0
let startY = 0
let initialStampX = 0
let initialStampY = 0

const startDrag = (e) => {
  if (!pageContainerRef.value) return
  isDragging = true
  startX = e.clientX
  startY = e.clientY
  initialStampX = stampXPercent.value
  initialStampY = stampYPercent.value

  window.addEventListener('mousemove', onDragging)
  window.addEventListener('mouseup', stopDrag)
}

const startDragTouch = (e) => {
  if (!pageContainerRef.value || !e.touches[0]) return
  isDragging = true
  startX = e.touches[0].clientX
  startY = e.touches[0].clientY
  initialStampX = stampXPercent.value
  initialStampY = stampYPercent.value

  window.addEventListener('touchmove', onDraggingTouch, { passive: false })
  window.addEventListener('touchend', stopDragTouch)
}

const onDragging = (e) => {
  if (!isDragging || !pageContainerRef.value) return
  const rect = pageContainerRef.value.getBoundingClientRect()
  const deltaXPixels = e.clientX - startX
  const deltaYPixels = e.clientY - startY

  const deltaXPercent = (deltaXPixels / rect.width) * 100
  const deltaYPercent = (deltaYPixels / rect.height) * 100

  const containerRatio = rect.width / (rect.height || 1)
  const stampHeightPercent = qrWidthPercent.value * containerRatio

  let newX = initialStampX + deltaXPercent
  let newY = initialStampY + deltaYPercent

  newX = Math.max(0.5, Math.min(newX, 99.5 - qrWidthPercent.value))
  newY = Math.max(0.5, Math.min(newY, 99.5 - stampHeightPercent))

  stampXPercent.value = newX
  stampYPercent.value = newY
}

const onDraggingTouch = (e) => {
  if (!isDragging || !pageContainerRef.value || !e.touches[0]) return
  e.preventDefault()
  const rect = pageContainerRef.value.getBoundingClientRect()
  const deltaXPixels = e.touches[0].clientX - startX
  const deltaYPixels = e.touches[0].clientY - startY

  const deltaXPercent = (deltaXPixels / rect.width) * 100
  const deltaYPercent = (deltaYPixels / rect.height) * 100

  const containerRatio = rect.width / (rect.height || 1)
  const stampHeightPercent = qrWidthPercent.value * containerRatio

  let newX = initialStampX + deltaXPercent
  let newY = initialStampY + deltaYPercent

  newX = Math.max(0.5, Math.min(newX, 99.5 - qrWidthPercent.value))
  newY = Math.max(0.5, Math.min(newY, 99.5 - stampHeightPercent))

  stampXPercent.value = newX
  stampYPercent.value = newY
}

const stopDrag = () => {
  isDragging = false
  window.removeEventListener('mousemove', onDragging)
  window.removeEventListener('mouseup', stopDrag)
}

const stopDragTouch = () => {
  isDragging = false
  window.removeEventListener('touchmove', onDraggingTouch)
  window.removeEventListener('touchend', stopDragTouch)
}

// =========================================================================
// LOGIKA RESIZE SUDUT STEMPEL (1:1 ASPECT RATIO, 4 SUDUT INTERAKTIF)
// =========================================================================
let isResizing = false
let resizeCorner = 'se'
let resizeStartX = 0
let resizeStartY = 0
let initialResizeWidth = 0
let initialResizeX = 0
let initialResizeY = 0

const startResize = (e, corner = 'se') => {
  if (!pageContainerRef.value) return
  isResizing = true
  resizeCorner = corner
  resizeStartX = e.clientX
  resizeStartY = e.clientY
  initialResizeWidth = qrWidthPercent.value
  initialResizeX = stampXPercent.value
  initialResizeY = stampYPercent.value

  window.addEventListener('mousemove', onResizing)
  window.addEventListener('mouseup', stopResize)
}

const startResizeTouch = (e, corner = 'se') => {
  if (!pageContainerRef.value || !e.touches[0]) return
  isResizing = true
  resizeCorner = corner
  resizeStartX = e.touches[0].clientX
  resizeStartY = e.touches[0].clientY
  initialResizeWidth = qrWidthPercent.value
  initialResizeX = stampXPercent.value
  initialResizeY = stampYPercent.value

  window.addEventListener('touchmove', onResizingTouch, { passive: false })
  window.addEventListener('touchend', stopResizeTouch)
}

const handleResizeMath = (clientX, clientY) => {
  if (!isResizing || !pageContainerRef.value) return
  const rect = pageContainerRef.value.getBoundingClientRect()
  const deltaXPixels = clientX - resizeStartX
  const deltaXPercent = (deltaXPixels / rect.width) * 100
  const containerRatio = rect.width / (rect.height || 1)

  const MIN_WIDTH = 7.0  // ~1.5 cm
  const MAX_WIDTH = 35.0 // ~7.4 cm

  if (resizeCorner === 'se') {
    // Kanan-Bawah: memperbesar ke kanan dan bawah
    let targetWidth = initialResizeWidth + deltaXPercent
    targetWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))
    targetWidth = Math.min(targetWidth, 99.5 - initialResizeX)

    const targetHeightPercent = targetWidth * containerRatio
    if (initialResizeY + targetHeightPercent > 99.5) {
      targetWidth = (99.5 - initialResizeY) / containerRatio
    }
    qrWidthPercent.value = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))
  } else if (resizeCorner === 'nw') {
    // Kiri-Atas: memperbesar ke kiri dan atas (anchor di pojok kanan-bawah)
    let targetWidth = initialResizeWidth - deltaXPercent
    targetWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))

    const widthDiff = targetWidth - initialResizeWidth
    let newX = initialResizeX - widthDiff
    let newY = initialResizeY - (widthDiff * containerRatio)

    if (newX >= 0.5 && newY >= 0.5) {
      qrWidthPercent.value = targetWidth
      stampXPercent.value = newX
      stampYPercent.value = newY
    }
  } else if (resizeCorner === 'ne') {
    // Kanan-Atas: memperbesar ke kanan dan atas (anchor di pojok kiri-bawah)
    let targetWidth = initialResizeWidth + deltaXPercent
    targetWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))

    const widthDiff = targetWidth - initialResizeWidth
    let newY = initialResizeY - (widthDiff * containerRatio)

    if (initialResizeX + targetWidth <= 99.5 && newY >= 0.5) {
      qrWidthPercent.value = targetWidth
      stampYPercent.value = newY
    }
  } else if (resizeCorner === 'sw') {
    // Kiri-Bawah: memperbesar ke kiri dan bawah (anchor di pojok kanan-atas)
    let targetWidth = initialResizeWidth - deltaXPercent
    targetWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))

    const widthDiff = targetWidth - initialResizeWidth
    let newX = initialResizeX - widthDiff
    const targetHeightPercent = targetWidth * containerRatio

    if (newX >= 0.5 && initialResizeY + targetHeightPercent <= 99.5) {
      qrWidthPercent.value = targetWidth
      stampXPercent.value = newX
    }
  }
}

const onResizing = (e) => {
  handleResizeMath(e.clientX, e.clientY)
}

const onResizingTouch = (e) => {
  if (!e.touches[0]) return
  e.preventDefault()
  handleResizeMath(e.touches[0].clientX, e.touches[0].clientY)
}

const stopResize = () => {
  isResizing = false
  window.removeEventListener('mousemove', onResizing)
  window.removeEventListener('mouseup', stopResize)
}

const stopResizeTouch = () => {
  isResizing = false
  window.removeEventListener('touchmove', onResizingTouch)
  window.removeEventListener('touchend', stopResizeTouch)
}

onUnmounted(() => {
  stopDrag()
  stopDragTouch()
  stopResize()
  stopResizeTouch()
})

// =========================================================================
// SUBMIT PROSES TTE BSrE
// =========================================================================
const submitProcessSign = async () => {
  formErrors.passphrase = ''

  if (!form.passphrase.trim()) {
    formErrors.passphrase = 'Passphrase BSrE wajib diisi untuk otorisasi tanda tangan'
    return
  }

  isSigning.value = true
  const formData = new FormData()
  formData.append('upload_id', uploadSession.value.upload_id)
  formData.append('nomor_surat', form.nomor_surat.trim() || '-')
  formData.append('perihal', form.perihal.trim() || (uploadSession.value?.original_filename || 'Dokumen'))
  formData.append('kategori', form.kategori)
  formData.append('tipe_stempel', 'qr_only')
  formData.append('passphrase', form.passphrase.trim())
  formData.append('target_page', form.target_page)
  formData.append('x_percent', stampXPercent.value.toFixed(2))
  formData.append('y_percent', stampYPercent.value.toFixed(2))
  formData.append('width_percent', qrWidthPercent.value.toFixed(2))
  formData.append('height_percent', qrWidthPercent.value.toFixed(2))

  try {
    const res = await uploadTteApi.processSign(formData)
    signedResult.value = res.data
    isSuccessDialogOpen.value = true
    emit('document-signed', res.data)
  } catch (err) {
    const errMsg = err.response?.data?.detail || err.message || 'Gagal menandatangani dokumen.'
    alert(`Otorisasi BSrE Gagal: ${errMsg}`)
  } finally {
    isSigning.value = false
  }
}

const closeSuccessDialog = () => {
  isSuccessDialogOpen.value = false
}

const goToDocumentList = () => {
  isSuccessDialogOpen.value = false
  emit('navigate-to', 'dokumen')
  window.dispatchEvent(new CustomEvent('nav-tab-change', { detail: 'dokumen' }))
}
</script>