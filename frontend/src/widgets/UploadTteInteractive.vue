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
                    <span>Stempel Utama:</span>
                  </span>
                  <span class="font-mono font-medium text-foreground">
                    Hal. {{ form.target_page }} • X: {{ stampXPercent.toFixed(1) }}% • Y: {{ stampYPercent.toFixed(1) }}%
                  </span>
                </div>
                <!-- Indikator Multiple QR -->
                <div v-if="extraStamps.length > 0" class="pt-1 border-t border-border/40 text-[11px] text-primary font-medium flex items-center justify-between">
                  <span>+ {{ extraStamps.length }} Stempel Tambahan Aktif</span>
                  <span class="text-muted-foreground font-mono">({{ extraStamps.map(s => `Hal. ${s.page}`).join(', ') }})</span>
                </div>
                <div class="text-[11px] leading-relaxed text-muted-foreground/90 flex items-start gap-1.5 pt-1 border-t border-border/50">
                  <span class="text-primary font-bold">✨</span>
                  <span>
                    <strong>Seret Bebas:</strong> Geser stempel ke posisi manapun di kanvas, dan tarik sudut stempel (handle resize) untuk memperbesar atau memperkecil ukuran QR secara presisi.
                  </span>
                </div>
              </div>

              <!-- Tombol Reset & Preset Cepat Posisi -->
              <div class="flex items-center justify-between pt-1">
                <div class="flex items-center gap-1">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    class="h-7 text-[10px] px-2 border-border"
                    title="Letakkan stempel di kanan bawah (format tanda tangan lazim)"
                    @click="applyPositionPreset('right-bottom')"
                  >
                    Kanan Bawah
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    class="h-7 text-[10px] px-2 border-border"
                    title="Letakkan stempel di kiri bawah (format saksi/mengetahui)"
                    @click="applyPositionPreset('left-bottom')"
                  >
                    Kiri Bawah
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    class="h-7 text-[10px] px-2 border-border"
                    title="Letakkan stempel di tengah bawah"
                    @click="applyPositionPreset('center-bottom')"
                  >
                    Tengah
                  </Button>
                </div>

                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="h-7 text-xs text-muted-foreground hover:text-foreground gap-1 px-2"
                  @click="resetStampToDefault"
                >
                  <RotateCcw class="w-3 h-3" />
                  <span>Reset</span>
                </Button>
              </div>
            </div>

            <!-- Passphrase Input -->
            <div class="space-y-1">
              <AppInput
                id="upload-auth-code"
                type="passphrase"
                label="Passphrase Sertifikat Elektronik BSrE"
                v-model="form.passphrase"
                placeholder="Ketik Passphrase Sertifikat BSrE Anda..."
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
                <span>{{ isSigning ? (isEditMode ? 'Memproses TTE Ulang BSrE...' : 'Memproses Pengesahan BSrE...') : (isEditMode ? 'TTE Ulang Dokumen' : 'Proses & Tanda Tangani Dokumen') }}</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- =================================================================== -->
      <!-- KOLOM KANAN: INTERACTIVE PDF LAYOUT VIEWER & STEMPEL QR MURNI       -->
      <!-- =================================================================== -->
      <div
        class="lg:col-span-7 transition-all duration-300"
        :class="[
          isFullscreen
            ? 'fixed inset-0 z-50 bg-background/95 backdrop-blur-md p-4 sm:p-6 flex flex-col h-screen w-screen'
            : ''
        ]"
      >
        <Card
          class="glass-panel border-border shadow-xs overflow-hidden flex flex-col"
          :class="[isFullscreen ? 'h-full border-primary/40 shadow-2xl' : '']"
        >
          <!-- Card Header: Title, Status, Presets & Fullscreen Toggle -->
          <CardHeader class="p-3.5 sm:p-4 border-b border-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-muted/20 shrink-0">
            <div class="flex items-center gap-2">
              <Eye class="w-4 h-4 text-primary" />
              <CardTitle class="text-xs sm:text-sm font-bold text-foreground">
                PDF Layout Viewer
                <span v-if="uploadSession" class="text-primary font-mono ml-1">
                  (Halaman {{ currentPage }} dari {{ totalPages }})
                </span>
              </CardTitle>
            </div>

            <!-- Header Quick Tools: Panduan Grid & Fullscreen -->
            <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
              <!-- Toggle Grid Bantu Penempatan -->
              <Button
                variant="outline"
                size="sm"
                class="h-8 text-xs gap-1.5 px-2.5 rounded-lg border-border"
                :class="[showGrid ? 'bg-primary/10 text-primary border-primary/50' : 'text-muted-foreground']"
                title="Tampilkan garis kisi-kisi pembantu lurus penempatan stempel"
                @click="showGrid = !showGrid"
              >
                <Grid class="w-3.5 h-3.5" />
                <span class="hidden sm:inline">Garis Kisi</span>
              </Button>

              <!-- Tombol Fullscreen Mode -->
              <Button
                variant="outline"
                size="sm"
                class="h-8 text-xs gap-1.5 px-2.5 rounded-lg border-border"
                :class="[isFullscreen ? 'bg-primary text-primary-foreground font-bold border-primary' : 'text-muted-foreground hover:text-foreground']"
                :title="isFullscreen ? 'Keluar Mode Layar Penuh (Esc)' : 'Buka Layar Penuh untuk tampilan luas'"
                @click="toggleFullscreen"
              >
                <Minimize2 v-if="isFullscreen" class="w-3.5 h-3.5" />
                <Maximize2 v-else class="w-3.5 h-3.5" />
                <span>{{ isFullscreen ? 'Keluar Fullscreen' : 'Layar Penuh' }}</span>
              </Button>
            </div>
          </CardHeader>

          <!-- Card Content / Canvas Viewer Area (Dengan Scroll & Zooming) -->
          <CardContent
            class="p-4 sm:p-6 bg-slate-950/75 flex items-start justify-center relative select-none overflow-auto flex-1 min-h-[580px]"
            :class="[isFullscreen ? 'h-full' : '']"
          >
            <!-- Empty State / Belum Unggah -->
            <div v-if="!uploadSession" class="text-center py-24 px-4 space-y-3 max-w-md my-auto">
              <div class="w-16 h-16 rounded-3xl bg-slate-800/80 text-slate-400 mx-auto flex items-center justify-center border border-slate-700/60 shadow-lg">
                <FileText class="w-8 h-8" />
              </div>
              <h4 class="text-sm font-bold text-slate-200">Pratinjau Lembar Dokumen Kosong</h4>
              <p class="text-xs text-slate-400 leading-relaxed">
                Silakan pilih berkas dokumen PDF, Word, atau EPUB di kolom kiri untuk memuat lembar pratinjau dan menempatkan stempel QR tanda tangan.
              </p>
            </div>

            <!-- Page Container Aktif (Bisa Di-Zoom Bebas) -->
            <div
              v-else
              ref="pageContainerRef"
              class="relative bg-white shadow-2xl rounded-sm border border-slate-700/60 transition-transform origin-top mx-auto"
              :style="{
                width: '100%',
                maxWidth: '580px',
                transform: `scale(${zoomLevel})`,
                transformOrigin: 'top center',
                marginBottom: zoomLevel > 1.0 ? `${(zoomLevel - 1.0) * 820}px` : '0px'
              }"
            >
              <!-- Garis Kisi-Kisi Bantu (Jika Diaktifkan) -->
              <div
                v-if="showGrid"
                class="absolute inset-0 pointer-events-none z-10 opacity-30"
                style="background-image: linear-gradient(to right, #0284c7 1px, transparent 1px), linear-gradient(to bottom, #0284c7 1px, transparent 1px); background-size: 20px 20px;"
              ></div>

              <!-- Gambar Halaman Dokumen yang Dirender PyMuPDF -->
              <img
                :src="currentPagePreviewUrl"
                alt="PDF Page Preview"
                class="w-full h-auto block select-none pointer-events-none rounded-sm"
              />

              <!-- =========================================================== -->
              <!-- 1. STEMPEL QR UTAMA (DRAGGABLE & RESIZABLE)                 -->
              <!-- =========================================================== -->
              <div
                v-if="form.target_page === currentPage"
                class="absolute cursor-move select-none touch-none transition-shadow z-20 group"
                :style="stampStyle"
                @mousedown="startDrag($event, 'primary')"
                @touchstart="startDragTouch($event, 'primary')"
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
                  @mousedown.stop="startResize($event, 'nw', 'primary')"
                  @touchstart.stop="startResizeTouch($event, 'nw', 'primary')"
                >
                  <div class="w-1 h-1 bg-primary rounded-full"></div>
                </div>

                <!-- Sudut Kanan-Atas (NE) -->
                <div
                  class="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 bg-white border-2 border-primary rounded-full cursor-nesw-resize shadow-md hover:scale-125 transition-transform z-30 flex items-center justify-center opacity-80 group-hover:opacity-100"
                  title="Seret untuk mengubah ukuran QR"
                  @mousedown.stop="startResize($event, 'ne', 'primary')"
                  @touchstart.stop="startResizeTouch($event, 'ne', 'primary')"
                >
                  <div class="w-1 h-1 bg-primary rounded-full"></div>
                </div>

                <!-- Sudut Kiri-Bawah (SW) -->
                <div
                  class="absolute -bottom-1.5 -left-1.5 w-3.5 h-3.5 bg-white border-2 border-primary rounded-full cursor-nesw-resize shadow-md hover:scale-125 transition-transform z-30 flex items-center justify-center opacity-80 group-hover:opacity-100"
                  title="Seret untuk mengubah ukuran QR"
                  @mousedown.stop="startResize($event, 'sw', 'primary')"
                  @touchstart.stop="startResizeTouch($event, 'sw', 'primary')"
                >
                  <div class="w-1 h-1 bg-primary rounded-full"></div>
                </div>

                <!-- Sudut Kanan-Bawah (SE) - Handle Utama Beraksen Primary -->
                <div
                  class="absolute -bottom-2 -right-2 w-5 h-5 bg-primary border-2 border-white rounded-full cursor-nwse-resize shadow-lg hover:scale-125 transition-transform z-30 flex items-center justify-center ring-2 ring-primary/30"
                  title="Tarik sudut ini untuk memperbesar atau memperkecil QR"
                  @mousedown.stop="startResize($event, 'se', 'primary')"
                  @touchstart.stop="startResizeTouch($event, 'se', 'primary')"
                >
                  <Maximize2 class="w-2.5 h-2.5 text-white" />
                </div>

                <!-- Floating Coordinates & Dimension Tooltip Real-time -->
                <div class="absolute -top-7 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-slate-900/95 text-cyan-300 text-[10px] font-mono rounded-md shadow-lg pointer-events-none whitespace-nowrap border border-slate-700/80 flex items-center gap-1.5 backdrop-blur-xs">
                  <span class="font-bold text-white">QR #1 (Utama)</span>
                  <span class="text-slate-400">|</span>
                  <span>{{ qrSizeLabel }}</span>
                  <span class="text-slate-400">|</span>
                  <span>X: {{ stampXPercent.toFixed(1) }}%, Y: {{ stampYPercent.toFixed(1) }}%</span>
                </div>
              </div>

              <!-- =========================================================== -->
              <!-- 2. STEMPEL QR TAMBAHAN (JIKA ADA >1 TTD DALAM 1 DOKUMEN)    -->
              <!-- =========================================================== -->
              <template v-for="(exStamp, exIdx) in extraStamps" :key="exStamp.id">
                <div
                  v-if="exStamp.page === currentPage"
                  class="absolute cursor-move select-none touch-none transition-shadow z-20 group"
                  :style="{
                    left: `${exStamp.x}%`,
                    top: `${exStamp.y}%`,
                    width: `${exStamp.widthPercent}%`,
                    aspectRatio: '1 / 1'
                  }"
                  @mousedown="startDrag($event, 'extra', exIdx)"
                  @touchstart="startDragTouch($event, 'extra', exIdx)"
                >
                  <!-- Stempel Tambahan dengan Aksen Amber/Emas -->
                  <div
                    class="w-full h-full border-2 border-dashed border-amber-400 bg-white/95 rounded-md p-1 shadow-2xl flex flex-col items-center justify-center relative overflow-hidden group-hover:border-amber-300 transition-colors"
                  >
                    <!-- Pattern QR Code -->
                    <div class="w-full h-full relative flex items-center justify-center bg-amber-50/40 rounded-xs border border-amber-200/80">
                      <div class="absolute top-1 left-1 w-3.5 h-3.5 border-2 border-slate-900 flex items-center justify-center">
                        <div class="w-1.5 h-1.5 bg-slate-900"></div>
                      </div>
                      <div class="absolute top-1 right-1 w-3.5 h-3.5 border-2 border-slate-900 flex items-center justify-center">
                        <div class="w-1.5 h-1.5 bg-slate-900"></div>
                      </div>
                      <div class="absolute bottom-1 left-1 w-3.5 h-3.5 border-2 border-slate-900 flex items-center justify-center">
                        <div class="w-1.5 h-1.5 bg-slate-900"></div>
                      </div>

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

                      <div class="absolute w-4 h-4 rounded-full bg-gradient-to-tr from-amber-600 to-yellow-500 border border-white shadow-xs flex items-center justify-center text-[7px] text-white font-black">
                        {{ exIdx + 2 }}
                      </div>
                    </div>
                  </div>

                  <!-- Tombol Hapus Stempel Tambahan Ini -->
                  <div
                    class="absolute -top-2 -right-2 w-5 h-5 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center cursor-pointer shadow-md z-30 transition-transform hover:scale-110"
                    title="Hapus stempel QR tambahan ini"
                    @mousedown.stop="removeExtraStamp(exIdx)"
                    @touchstart.stop="removeExtraStamp(exIdx)"
                  >
                    <X class="w-3 h-3" />
                  </div>

                  <!-- Resize Handle Kanan-Bawah -->
                  <div
                    class="absolute -bottom-2 -right-2 w-5 h-5 bg-amber-500 border-2 border-white rounded-full cursor-nwse-resize shadow-lg hover:scale-125 transition-transform z-30 flex items-center justify-center ring-2 ring-amber-500/30"
                    title="Tarik untuk mengubah ukuran QR tambahan ini"
                    @mousedown.stop="startResize($event, 'se', 'extra', exIdx)"
                    @touchstart.stop="startResizeTouch($event, 'se', 'extra', exIdx)"
                  >
                    <Maximize2 class="w-2.5 h-2.5 text-white" />
                  </div>

                  <!-- Floating Tooltip -->
                  <div class="absolute -top-7 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-slate-900/95 text-amber-300 text-[10px] font-mono rounded-md shadow-lg pointer-events-none whitespace-nowrap border border-slate-700/80 flex items-center gap-1 backdrop-blur-xs">
                    <span class="font-bold text-white">QR #{{ exIdx + 2 }}</span>
                    <span>|</span>
                    <span>X: {{ exStamp.x.toFixed(1) }}%, Y: {{ exStamp.y.toFixed(1) }}%</span>
                  </div>
                </div>
              </template>

              <!-- Tombol Pindah Stempel Utama ke Halaman Ini jika Stempel Ada di Halaman Lain -->
              <div
                v-if="form.target_page !== currentPage"
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

          <!-- =============================================================== -->
          <!-- CARD FOOTER: TOOLBAR LENGKAP (PAGINASI, ZOOM, & TAMBAH QR)     -->
          <!-- =============================================================== -->
          <CardFooter class="p-3 sm:p-4 border-t border-border flex flex-wrap items-center justify-between gap-3 bg-muted/20 shrink-0">
            <!-- Sisi Kiri: Pagination Controls (Pindah ke Bawah Sesuai Permintaan) -->
            <div class="flex items-center gap-1.5">
              <span class="text-xs font-semibold text-muted-foreground mr-1 hidden sm:inline">Halaman:</span>

              <!-- Halaman Pertama -->
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 rounded-lg border-border"
                :disabled="!uploadSession || currentPage <= 1"
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
                :disabled="!uploadSession || currentPage <= 1"
                title="Halaman Sebelumnya"
                @click="goToPage(currentPage - 1)"
              >
                <ChevronLeft class="w-4 h-4" />
              </Button>

              <!-- Input Nomor Halaman Langsung -->
              <div class="flex items-center gap-1 px-2 py-0.5 bg-background border border-border rounded-lg shadow-2xs h-8">
                <Input
                  type="number"
                  min="1"
                  :max="totalPages"
                  v-model="pageInputNumber"
                  :disabled="!uploadSession"
                  @keydown.enter="jumpToInputPage"
                  @blur="jumpToInputPage"
                  class="w-10 h-6 text-center text-xs font-mono font-bold px-1 py-0 border-border bg-muted/30 focus-visible:ring-1 focus-visible:ring-primary [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  title="Ketik nomor halaman dan tekan Enter untuk berpindah"
                />
                <span class="text-xs font-mono text-muted-foreground">/ {{ totalPages }}</span>
              </div>

              <!-- Halaman Berikutnya -->
              <Button
                variant="outline"
                size="icon"
                class="h-8 w-8 rounded-lg border-border"
                :disabled="!uploadSession || currentPage >= totalPages"
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
                :disabled="!uploadSession || currentPage >= totalPages"
                :title="`Halaman Terakhir (Hal. ${totalPages})`"
                @click="goToPage(totalPages)"
              >
                <ChevronsRight class="w-4 h-4" />
              </Button>
            </div>

            <!-- Sisi Tengah: Zoom In & Zoom Out Controls -->
            <div class="flex items-center gap-1 bg-background border border-border rounded-lg p-0.5 shadow-2xs">
              <Button
                variant="ghost"
                size="icon"
                class="h-7 w-7 rounded-md text-muted-foreground hover:text-foreground"
                :disabled="!uploadSession || zoomLevel <= 0.6"
                title="Perkecil Dokumen (Zoom Out)"
                @click="zoomOut"
              >
                <ZoomOut class="w-3.5 h-3.5" />
              </Button>

              <button
                type="button"
                class="px-2 text-xs font-mono font-semibold text-foreground hover:text-primary transition-colors cursor-pointer select-none"
                title="Klik untuk reset zoom ke 100%"
                @click="resetZoom"
              >
                {{ Math.round(zoomLevel * 100) }}%
              </button>

              <Button
                variant="ghost"
                size="icon"
                class="h-7 w-7 rounded-md text-muted-foreground hover:text-foreground"
                :disabled="!uploadSession || zoomLevel >= 2.0"
                title="Perbesar Dokumen (Zoom In)"
                @click="zoomIn"
              >
                <ZoomIn class="w-3.5 h-3.5" />
              </Button>
            </div>

            <!-- Sisi Kanan: Tools Tambah Stempel QR TTE -->
            <div class="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                class="h-8 text-xs font-medium gap-1.5 rounded-lg border-primary/30 text-primary hover:bg-primary/10"
                :disabled="!uploadSession"
                title="Tambahkan stempel QR kedua/ketiga pada dokumen ini"
                @click="addExtraStamp"
              >
                <Plus class="w-3.5 h-3.5" />
                <span>Tambah QR Stempel</span>
              </Button>
            </div>
          </CardFooter>
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
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { uploadTteApi } from '@/services/api'
import AppInput from '@/components/AppInput.vue'
import AppSelect from '@/components/AppSelect.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
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
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Grid,
  Plus,
  X
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
const isEditMode = ref(false)
const uploadSession = ref(null)
const currentPage = ref(1)
const pageInputNumber = ref(1)
const isSuccessDialogOpen = ref(false)
const signedResult = ref(null)

// Viewer Features State (Zoom, Fullscreen, Grid, Multiple QR)
const zoomLevel = ref(1.0)
const isFullscreen = ref(false)
const showGrid = ref(false)
const extraStamps = ref([])

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

// Preset Cepat Penempatan Stempel
const applyPositionPreset = (preset) => {
  if (preset === 'right-bottom') {
    stampXPercent.value = 70.0
    stampYPercent.value = 80.0
  } else if (preset === 'left-bottom') {
    stampXPercent.value = 12.0
    stampYPercent.value = 80.0
  } else if (preset === 'center-bottom') {
    stampXPercent.value = 42.0
    stampYPercent.value = 80.0
  }
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

// =========================================================================
// ZOOM & FULLSCREEN CONTROLS
// =========================================================================
const zoomIn = () => {
  if (zoomLevel.value < 2.0) {
    zoomLevel.value = +(zoomLevel.value + 0.15).toFixed(2)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.6) {
    zoomLevel.value = +(zoomLevel.value - 0.15).toFixed(2)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1.0
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handleKeydown = (e) => {
  if (e.key === 'Escape' && isFullscreen.value) {
    isFullscreen.value = false
  }
}

// =========================================================================
// MULTIPLE QR STAMPS MANAGEMENT
// =========================================================================
const addExtraStamp = () => {
  if (!uploadSession.value) return
  const newX = stampXPercent.value > 45 ? 15.0 : 70.0
  const newY = stampYPercent.value
  extraStamps.value.push({
    id: Date.now() + Math.random(),
    page: currentPage.value,
    x: newX,
    y: newY,
    widthPercent: qrWidthPercent.value
  })
}

const removeExtraStamp = (index) => {
  extraStamps.value.splice(index, 1)
}

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
  isEditMode.value = false
  isConverting.value = true
  extraStamps.value = []
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
// LOGIKA DRAGGABLE STEMPEL (POINTER / MOUSE / TOUCH - MENDUKUNG EXTRA STAMP)
// =========================================================================
let isDragging = false
let activeDragTarget = 'primary' // 'primary' atau 'extra'
let activeDragIndex = 0
let startX = 0
let startY = 0
let initialStampX = 0
let initialStampY = 0

const startDrag = (e, target = 'primary', index = 0) => {
  if (!pageContainerRef.value) return
  isDragging = true
  activeDragTarget = target
  activeDragIndex = index
  startX = e.clientX
  startY = e.clientY

  if (target === 'primary') {
    initialStampX = stampXPercent.value
    initialStampY = stampYPercent.value
  } else {
    initialStampX = extraStamps.value[index].x
    initialStampY = extraStamps.value[index].y
  }

  window.addEventListener('mousemove', onDragging)
  window.addEventListener('mouseup', stopDrag)
}

const startDragTouch = (e, target = 'primary', index = 0) => {
  if (!pageContainerRef.value || !e.touches[0]) return
  isDragging = true
  activeDragTarget = target
  activeDragIndex = index
  startX = e.touches[0].clientX
  startY = e.touches[0].clientY

  if (target === 'primary') {
    initialStampX = stampXPercent.value
    initialStampY = stampYPercent.value
  } else {
    initialStampX = extraStamps.value[index].x
    initialStampY = extraStamps.value[index].y
  }

  window.addEventListener('touchmove', onDraggingTouch, { passive: false })
  window.addEventListener('touchend', stopDragTouch)
}

const handleDragMath = (clientX, clientY) => {
  if (!isDragging || !pageContainerRef.value) return
  const rect = pageContainerRef.value.getBoundingClientRect()
  const deltaXPixels = clientX - startX
  const deltaYPixels = clientY - startY

  const deltaXPercent = (deltaXPixels / rect.width) * 100
  const deltaYPercent = (deltaYPixels / rect.height) * 100

  const containerRatio = rect.width / (rect.height || 1)
  const currentWidthPercent = activeDragTarget === 'primary' 
    ? qrWidthPercent.value 
    : extraStamps.value[activeDragIndex]?.widthPercent || qrWidthPercent.value
  const stampHeightPercent = currentWidthPercent * containerRatio

  let newX = initialStampX + deltaXPercent
  let newY = initialStampY + deltaYPercent

  newX = Math.max(0.5, Math.min(newX, 99.5 - currentWidthPercent))
  newY = Math.max(0.5, Math.min(newY, 99.5 - stampHeightPercent))

  if (activeDragTarget === 'primary') {
    stampXPercent.value = newX
    stampYPercent.value = newY
  } else if (extraStamps.value[activeDragIndex]) {
    extraStamps.value[activeDragIndex].x = newX
    extraStamps.value[activeDragIndex].y = newY
  }
}

const onDragging = (e) => {
  handleDragMath(e.clientX, e.clientY)
}

const onDraggingTouch = (e) => {
  if (!e.touches[0]) return
  e.preventDefault()
  handleDragMath(e.touches[0].clientX, e.touches[0].clientY)
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
let activeResizeTarget = 'primary'
let activeResizeIndex = 0
let resizeCorner = 'se'
let resizeStartX = 0
let resizeStartY = 0
let initialResizeWidth = 0
let initialResizeX = 0
let initialResizeY = 0

const startResize = (e, corner = 'se', target = 'primary', index = 0) => {
  if (!pageContainerRef.value) return
  isResizing = true
  activeResizeTarget = target
  activeResizeIndex = index
  resizeCorner = corner
  resizeStartX = e.clientX
  resizeStartY = e.clientY

  if (target === 'primary') {
    initialResizeWidth = qrWidthPercent.value
    initialResizeX = stampXPercent.value
    initialResizeY = stampYPercent.value
  } else {
    const s = extraStamps.value[index]
    initialResizeWidth = s.widthPercent
    initialResizeX = s.x
    initialResizeY = s.y
  }

  window.addEventListener('mousemove', onResizing)
  window.addEventListener('mouseup', stopResize)
}

const startResizeTouch = (e, corner = 'se', target = 'primary', index = 0) => {
  if (!pageContainerRef.value || !e.touches[0]) return
  isResizing = true
  activeResizeTarget = target
  activeResizeIndex = index
  resizeCorner = corner
  resizeStartX = e.touches[0].clientX
  resizeStartY = e.touches[0].clientY

  if (target === 'primary') {
    initialResizeWidth = qrWidthPercent.value
    initialResizeX = stampXPercent.value
    initialResizeY = stampYPercent.value
  } else {
    const s = extraStamps.value[index]
    initialResizeWidth = s.widthPercent
    initialResizeX = s.x
    initialResizeY = s.y
  }

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
    let targetWidth = initialResizeWidth + deltaXPercent
    targetWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))
    targetWidth = Math.min(targetWidth, 99.5 - initialResizeX)

    const targetHeightPercent = targetWidth * containerRatio
    if (initialResizeY + targetHeightPercent > 99.5) {
      targetWidth = (99.5 - initialResizeY) / containerRatio
    }
    const finalWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))
    if (activeResizeTarget === 'primary') {
      qrWidthPercent.value = finalWidth
    } else if (extraStamps.value[activeResizeIndex]) {
      extraStamps.value[activeResizeIndex].widthPercent = finalWidth
    }
  } else if (resizeCorner === 'nw') {
    let targetWidth = initialResizeWidth - deltaXPercent
    targetWidth = Math.max(MIN_WIDTH, Math.min(targetWidth, MAX_WIDTH))

    const widthDiff = targetWidth - initialResizeWidth
    let newX = initialResizeX - widthDiff
    let newY = initialResizeY - (widthDiff * containerRatio)

    if (newX >= 0.5 && newY >= 0.5) {
      if (activeResizeTarget === 'primary') {
        qrWidthPercent.value = targetWidth
        stampXPercent.value = newX
        stampYPercent.value = newY
      } else if (extraStamps.value[activeResizeIndex]) {
        extraStamps.value[activeResizeIndex].widthPercent = targetWidth
        extraStamps.value[activeResizeIndex].x = newX
        extraStamps.value[activeResizeIndex].y = newY
      }
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

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  stopDrag()
  stopDragTouch()
  stopResize()
  stopResizeTouch()
})

// =========================================================================
// SUBMIT PROSES TTE BSrE (TETAP MENJAGA ALUR ASLI YANG SUDAH PAS)
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

  // Sertakan stempel tambahan jika ada
  if (extraStamps.value.length > 0) {
    formData.append('additional_stamps', JSON.stringify(extraStamps.value))
  }

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

const loadExistingDocument = async (doc) => {
  if (!doc) return
  isEditMode.value = true
  isConverting.value = true
  extraStamps.value = []
  form.perihal = doc.title || doc.filename || ''
  form.nomor_surat = doc.document_number || doc.nomor_surat || ''
  if (doc.category || doc.document_type) {
    const matched = kategoriOptions.find(k => k.value === (doc.category || doc.document_type))
    if (matched) {
      form.kategori = matched.value
    }
  }

  try {
    const res = await uploadTteApi.loadDocumentForEdit(doc.id)
    uploadSession.value = res.data
    currentPage.value = 1
    pageInputNumber.value = 1
    form.target_page = 1
    if (res.data?.document) {
      if (res.data.document.title) form.perihal = res.data.document.title
      const extractedNomor = res.data.document.nomor_surat || res.data.document.document_number
      if (extractedNomor) form.nomor_surat = extractedNomor
      if (res.data.document.category) {
        const m = kategoriOptions.find(k => k.value === res.data.document.category)
        if (m) form.kategori = m.value
      }
    }
  } catch (err) {
    console.error('Gagal memuat pratinjau dokumen:', err)
    alert(err.response?.data?.detail || 'Gagal memuat pratinjau dokumen.')
  } finally {
    isConverting.value = false
  }
}

defineExpose({
  loadExistingDocument
})
</script>
