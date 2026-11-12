<template>
  <div class="relative min-h-screen w-full flex items-center justify-center p-4 overflow-hidden font-sans bg-background text-foreground transition-colors duration-300">

    <!-- CANVAS BACKGROUND PARTICLE EFFECT -->
    <canvas ref="particleCanvasRef" class="absolute inset-0 w-full h-full z-0 pointer-events-none opacity-60"></canvas>
    
    <!-- BACKGROUND GRID LINES OVERLAY -->
    <div class="absolute inset-0 z-0 pointer-events-none bg-grid opacity-30 dark:opacity-60"></div>

    <!-- AMBIENT GLOW ORBS (Futuristik Cyber Glow) -->
    <div class="orb w-[500px] h-[500px] bg-primary/20 -top-20 -left-20 animate-pulse-slow"></div>
    <div class="orb w-[450px] h-[450px] bg-primary/15 -bottom-20 -right-20 animate-pulse-slow"></div>
    <div class="orb w-[350px] h-[350px] bg-emerald-500/10 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>

    <!-- MAIN CONTAINER CARD (12 Cols Responsive) -->
    <div class="relative z-10 w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 rounded-3xl glass-box cyber-border-glow overflow-hidden my-auto transition-all duration-300 bg-card/90 border border-border shadow-2xl">

      <!-- =================================================================== -->
      <!-- SISI KIRI: BRANDING & BSRE SYSTEM INFOGRAPHICS (5 Cols)             -->
      <!-- =================================================================== -->
      <div class="lg:col-span-5 p-8 lg:p-10 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-border bg-gradient-to-b from-primary/10 via-card/50 to-transparent relative overflow-hidden">
        <!-- Top Branding Header -->
        <div>
          <!-- Badge Akreditasi BSrE BSSN -->
          <div class="flex items-center space-x-3 mb-5">
            <span class="text-[10px] font-mono tracking-widest text-primary uppercase font-bold px-3 py-1 rounded-full bg-primary/10 border border-primary/30 flex items-center gap-1.5 shadow-xs">
              <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              BSSN TERAKREDITASI BSrE
            </span>
          </div>

          <!-- Brand Title dengan Ikon Floating Shield -->
          <div class="flex items-center space-x-3.5 mb-4">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-400 via-primary to-emerald-400 p-0.5 shadow-lg shadow-primary/25 shrink-0 flex items-center justify-center">
              <div class="w-full h-full rounded-[14px] flex items-center justify-center bg-card text-primary">
                <ShieldCheck class="w-6 h-6" />
              </div>
            </div>
            <div>
              <h1 class="text-xl font-extrabold tracking-wide flex items-center gap-1.5 text-foreground leading-none">
                E-DOC <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">BSrE</span>
              </h1>
              <p class="text-[11px] text-muted-foreground font-semibold tracking-tight mt-1">UOBK RSUD dr. Mohamad Saleh</p>
            </div>
          </div>

          <h2 class="text-2xl font-extrabold leading-tight text-foreground mt-6">
            Portal Keamanan & Otorisasi <span class="text-primary underline decoration-primary/50 underline-offset-4">Dokumen TTE</span>
          </h2>
          <p class="text-xs mt-3 leading-relaxed text-muted-foreground">
            Sistem Terintegrasi Single Sign-On (SSO) SIMRS & Balai Besar Sertifikasi Elektronik (BSrE - BSSN Republik Indonesia).
          </p>
        </div>

        <!-- Middle Interactive Security Badge Features -->
        <div class="my-8 space-y-3">
          <!-- Feature 1: SSO SIMRS -->
          <div class="p-3.5 rounded-2xl border border-border bg-card/60 hover:border-primary/40 transition-all flex items-center space-x-3.5">
            <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20">
              <QrCode class="w-4 h-4" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-foreground">SSO & QR Authenticator</h3>
              <p class="text-[11px] text-muted-foreground">Login instan via SIMRS Web & SIMRS Mobile Scanner</p>
            </div>
          </div>

          <!-- Feature 2: Cloud HSM BSSN -->
          <div class="p-3.5 rounded-2xl border border-border bg-card/60 hover:border-primary/40 transition-all flex items-center space-x-3.5">
            <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20">
              <ShieldCheck class="w-4 h-4" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-foreground">Sertifikat Elektronik Cloud HSM</h3>
              <p class="text-[11px] text-muted-foreground">Kriptografi Asimetris RSA 2048-bit & BSSN Verified</p>
            </div>
          </div>

          <!-- Feature 3: TSA Time-Stamping -->
          <div class="p-3.5 rounded-2xl border border-border bg-card/60 hover:border-emerald-500/40 transition-all flex items-center space-x-3.5">
            <div class="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0 border border-emerald-500/20">
              <FileCheck class="w-4 h-4" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-foreground">TSA Time-Stamping Valid</h3>
              <p class="text-[11px] text-muted-foreground">Integritas Waktu & Hash SHA-256 Terverifikasi</p>
            </div>
          </div>
        </div>

        <!-- Bottom Live Security Status -->
        <div class="pt-4 border-t border-border flex items-center justify-between text-[11px] font-mono text-muted-foreground">
          <span class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            BSrE Gateway Active
          </span>
          <span class="text-primary font-semibold">TLS 1.3 / SHA256</span>
        </div>
      </div>

      <!-- =================================================================== -->
      <!-- SISI KANAN: LOGIN SCAN QR SIMRS & CONTROLS (7 Cols)                 -->
      <!-- =================================================================== -->
      <div class="lg:col-span-7 p-8 lg:p-12 flex flex-col justify-between relative bg-card/40">
        <div>
          <!-- Header Bar: Logo BSrE, Logo RSUD & Toggle Theme (Mengisi Header Bar Tanpa Menambah Ruang) -->
          <div class="flex items-center justify-between mb-6 pb-3 border-b border-border">
            <!-- Logo Resmi BSrE BSSN & Logo RSUD dr. Mohamad Saleh -->
            <div class="px-3 py-1.5 rounded-xl bg-white dark:bg-white/95 shadow-xs border border-slate-200/80 flex items-center gap-2.5">
              <img src="/images/logo_bsre.png" alt="Balai Besar Sertifikasi Elektronik - BSSN" class="h-7 w-auto object-contain" />
              <div class="h-5 w-[1px] bg-slate-300"></div>
              <img :src="logoRsud" alt="Logo RSUD Mohamad Saleh" class="h-7 w-auto object-contain" />
            </div>

            <!-- Toggle Mode Terang/Gelap -->
            <Button
              type="button"
              variant="outline"
              size="icon"
              class="h-9 w-9 rounded-xl border border-border text-foreground hover:bg-muted shrink-0"
              :title="isDark ? 'Ganti ke Mode Terang (Light)' : 'Ganti ke Mode Gelap (Dark)'"
              @click="toggleTheme"
            >
              <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
              <Moon v-else class="w-4 h-4 text-muted-foreground" />
            </Button>
          </div>

          <!-- LOGIN SCAN QR CODE SIMRS (Seperti WhatsApp Web) -->
          <div class="space-y-5 text-center py-2">
            <div class="max-w-md mx-auto">
              <h3 class="text-sm font-bold text-foreground">Masuk dengan Scan QR SIMRS</h3>
              <p class="text-xs text-muted-foreground mt-1">
                Buka aplikasi SIMRS Mobile / Scanner Dokter di smartphone Anda dan arahkan ke kode QR berikut.
              </p>
            </div>

            <!-- QR Container Card Futuristik (Ukuran Diperbesar & Animasi WOW) -->
            <div
              class="relative w-64 h-64 sm:w-72 sm:h-72 mx-auto p-4 bg-card/95 rounded-3xl border-2 border-primary/40 shadow-2xl overflow-hidden flex items-center justify-center transition-all duration-700 group"
              :class="{
                'border-emerald-500 shadow-emerald-500/25 ring-4 ring-emerald-500/20': qrStatus === 'APPROVED',
                'border-cyan-400 shadow-cyan-400/25 ring-4 ring-cyan-400/20': isQrValidating && qrStatus !== 'APPROVED'
              }"
            >
              <!-- Cybernetic Corner Brackets (Hiasan Sudut Futuristik) -->
              <span class="absolute top-2.5 left-2.5 w-4 h-4 border-t-2 border-l-2 border-primary rounded-tl pointer-events-none transition-colors duration-300" :class="{ '!border-emerald-400': qrStatus === 'APPROVED' }"></span>
              <span class="absolute top-2.5 right-2.5 w-4 h-4 border-t-2 border-r-2 border-primary rounded-tr pointer-events-none transition-colors duration-300" :class="{ '!border-emerald-400': qrStatus === 'APPROVED' }"></span>
              <span class="absolute bottom-2.5 left-2.5 w-4 h-4 border-b-2 border-l-2 border-primary rounded-bl pointer-events-none transition-colors duration-300" :class="{ '!border-emerald-400': qrStatus === 'APPROVED' }"></span>
              <span class="absolute bottom-2.5 right-2.5 w-4 h-4 border-b-2 border-r-2 border-primary rounded-br pointer-events-none transition-colors duration-300" :class="{ '!border-emerald-400': qrStatus === 'APPROVED' }"></span>

              <!-- KONDISI 1: ANIMASI LOGO RSUD BERPUTAR (Saat Scan Berhasil / Validasi / Approved) -->
              <div
                v-if="isQrValidating || qrStatus === 'APPROVED'"
                class="absolute inset-0 flex flex-col items-center justify-center bg-card/95 z-20 transition-all duration-700"
              >
                <!-- Gelombang Ripple Sonar -->
                <div class="absolute w-32 h-32 rounded-full border border-emerald-500/40 animate-ripple pointer-events-none"></div>
                <div class="absolute w-48 h-48 rounded-full border border-cyan-400/30 animate-ripple [animation-delay:0.6s] pointer-events-none"></div>

                <!-- Double Cybernetic Halo Rings -->
                <div class="relative w-36 h-36 flex items-center justify-center">
                  <!-- Ring Luar Berputar Searah Jarum Jam -->
                  <div class="absolute inset-0 rounded-full border-2 border-dashed border-primary/60 animate-spin-slow"></div>
                  <!-- Ring Dalam Berputar Berlawanan Arah -->
                  <div class="absolute inset-2 rounded-full border-2 border-dotted border-emerald-400/70 animate-spin-reverse"></div>

                  <!-- LOGO RSUD BERPUTAR DI TENGAH (WOW EFFECT) -->
                  <div class="relative w-24 h-24 rounded-full bg-white dark:bg-slate-900 p-2.5 shadow-2xl flex items-center justify-center animate-rsud-spin">
                    <img
                      :src="logoRsud"
                      alt="Logo RSUD dr. Mohamad Saleh"
                      class="w-full h-full object-contain filter drop-shadow-md"
                    />
                  </div>
                </div>

                <!-- Badge Keterangan Status Animasi -->
                <div
                  class="mt-4 px-3.5 py-1 rounded-full text-[11px] font-bold tracking-wide flex items-center gap-1.5 shadow-sm transition-all duration-300"
                  :class="qrStatus === 'APPROVED'
                    ? 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/40 animate-pulse'
                    : 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/40'"
                >
                  <CheckCircle2 v-if="qrStatus === 'APPROVED'" class="w-3.5 h-3.5 animate-bounce" />
                  <div v-else class="w-3 h-3 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                  <span>{{ qrStatus === 'APPROVED' ? 'Otentikasi Berhasil!' : 'Sinkronisasi Sesi SIMRS...' }}</span>
                </div>
              </div>

              <!-- KONDISI 2: Loading State Saat Generate QR -->
              <div v-else-if="qrLoading" class="flex flex-col items-center justify-center space-y-3 text-muted-foreground">
                <div class="relative w-12 h-12 flex items-center justify-center">
                  <div class="absolute inset-0 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                  <img :src="logoRsud" alt="RSUD" class="w-6 h-6 object-contain opacity-60" />
                </div>
                <span class="text-xs font-medium font-mono">Membuat Sesi QR...</span>
              </div>

              <!-- KONDISI 3: Active QR Image (Ukuran Lebih Besar & Jelas Dipindai) -->
              <div v-else-if="qrBase64Image" class="relative w-full h-full flex items-center justify-center bg-white rounded-2xl p-2.5 transition-all duration-500">
                <img
                  :src="qrBase64Image"
                  alt="QR Code Login SIMRS"
                  class="w-full h-full object-contain"
                />
                <!-- Scanning Laser Line -->
                <div class="absolute inset-x-2 h-1 bg-gradient-to-r from-cyan-400 via-primary to-emerald-400 shadow-lg shadow-cyan-400 animate-scan pointer-events-none rounded-full"></div>
              </div>

              <!-- KONDISI 4: Fallback State jika QR gagal dimuat -->
              <div v-else class="flex flex-col items-center justify-center space-y-2 p-4 text-center">
                <p class="text-xs text-muted-foreground">QR belum tersedia</p>
                <Button size="sm" variant="outline" class="text-xs rounded-lg" @click="fetchNewQrSession">
                  <RotateCcw class="w-3.5 h-3.5 mr-1" />
                  Muat Ulang
                </Button>
              </div>
            </div>

            <!-- Auto-Refresh Info Badge -->
            <div class="flex items-center justify-center gap-2 text-xs font-mono">
              <span v-if="qrStatus === 'APPROVED'" class="text-emerald-500 font-bold flex items-center gap-1.5 animate-pulse">
                <CheckCircle2 class="w-4 h-4" />
                <span>Otentikasi Berhasil! Mengalihkan ke Ruang Kerja...</span>
              </span>
              <span v-else-if="isQrValidating" class="text-cyan-400 font-bold flex items-center gap-1.5">
                <div class="w-3 h-3 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                <span>Memvalidasi Data Dokter...</span>
              </span>
              <span v-else class="text-muted-foreground flex items-center gap-2 bg-muted/60 px-3.5 py-1.5 rounded-full border border-border shadow-xs">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                <span>QR Aktif • Auto-refresh otomatis</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Footer Compliance Info -->
        <div class="mt-8 pt-4 border-t border-border flex flex-col sm:flex-row items-center justify-between text-[11px] gap-2 text-muted-foreground">
          <div>© 2026 BSSN RI - Balai Sertifikasi Elektronik</div>
          <div class="flex items-center space-x-3">
            <a href="#" class="hover:text-primary transition-colors" @click.prevent="alertHelpdesk">Kebijakan Privasi</a>
            <span>•</span>
            <a href="#" class="hover:text-primary transition-colors" @click.prevent="alertHelpdesk">Panduan TTE</a>
            <span>•</span>
            <a href="#" class="hover:text-primary transition-colors" @click.prevent="alertHelpdesk">Bantuan BSrE</a>
          </div>
        </div>
      </div>
    </div>

    <!-- FULLSCREEN CINEMATIC WARP OVERLAY (TRANSISI HALUS & WOW KE RUANG KERJA ADMIN) -->
    <transition name="warp-fade">
      <div
        v-if="isTransitioningToAdmin"
        class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/90 backdrop-blur-3xl animate-portal-warp transition-all"
      >
        <!-- Ambient Glowing Aura -->
        <div class="absolute w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-cyan-500/25 via-primary/30 to-emerald-500/25 blur-3xl animate-pulse pointer-events-none"></div>

        <div class="relative z-10 flex flex-col items-center text-center p-8 max-w-sm">
          <!-- Logo RSUD Berpendar Memancarkan Gelombang Cahaya -->
          <div class="relative w-28 h-28 mb-6 flex items-center justify-center">
            <div class="absolute inset-0 rounded-full bg-emerald-500/30 blur-xl animate-ping"></div>
            <div class="relative w-full h-full rounded-3xl bg-white dark:bg-card p-4 shadow-2xl border-2 border-emerald-500/50 flex items-center justify-center animate-bounce-subtle">
              <img :src="logoRsud" alt="Logo RSUD" class="w-full h-full object-contain filter drop-shadow-xl" />
            </div>
          </div>

          <h3 class="text-xl font-extrabold tracking-wide text-foreground">
            Selamat Datang, <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">{{ authenticatedUserName || 'Dokter Penandatangan' }}</span>
          </h3>
          <p class="text-xs text-muted-foreground mt-2 font-medium">
            Membuka Ruang Kerja E-DOC BSrE RSUD dr. Mohamad Saleh...
          </p>

          <!-- Futuristik Progress Bar -->
          <div class="w-56 h-1.5 bg-muted rounded-full mt-6 overflow-hidden relative shadow-inner">
            <div class="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-400 via-primary to-emerald-400 rounded-full animate-progress-fill"></div>
          </div>
        </div>
      </div>
    </transition>

    <!-- FLOATING SUCCESS TOAST -->
    <div
      v-if="showSuccessToast"
      class="fixed bottom-6 right-6 z-50 transition-all duration-300"
    >
      <div class="p-4 rounded-2xl border border-emerald-500/40 bg-card/90 flex items-center space-x-3 text-emerald-500 shadow-2xl backdrop-blur-xl">
        <CheckCircle2 class="w-6 h-6 shrink-0" />
        <div>
          <h4 class="text-xs font-bold text-foreground">Otentikasi Berhasil!</h4>
          <p class="text-[11px] text-muted-foreground">Mengarahkan ke Dashboard Dokumen...</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/services/api'
import { getEchoInstance } from '@/services/sockets'
import AppInput from '@/components/AppInput.vue'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import logoRsud from '@/assets/images/logo-rsud.png'
import {
  ShieldCheck,
  Key,
  FileCheck,
  UserCheck,
  QrCode,
  RotateCcw,
  Sun,
  Moon,
  CheckCircle2
} from 'lucide-vue-next'

const router = useRouter()

// Mode Gelap / Terang
const isDark = ref(localStorage.getItem('theme') !== 'light')

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const showSuccessToast = ref(false)
const isLoading = ref(false)

// QR Code Session State & Animasi Transisi WOW
const qrSessionId = ref('')
const qrCodeString = ref('')
const qrBase64Image = ref('')
const qrCountdown = ref(180)
const qrStatus = ref('PENDING')
const qrLoading = ref(false)
const isQrValidating = ref(false)
const isTransitioningToAdmin = ref(false)
const authenticatedUserName = ref('')
let qrPollingTimer = null
let echoChannel = null

// Audio Chime Futuristik Berbasis Web Audio API (Multi-Tone Synth WOW Chime)
const playSuccessSound = () => {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return
    const ctx = new AudioCtx()
    const now = ctx.currentTime

    // Chord 1 (C5 - 523.25 Hz)
    const osc1 = ctx.createOscillator()
    const gain1 = ctx.createGain()
    osc1.type = 'sine'
    osc1.frequency.setValueAtTime(523.25, now)
    gain1.gain.setValueAtTime(0.12, now)
    gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.5)
    osc1.connect(gain1)
    gain1.connect(ctx.destination)
    osc1.start(now)
    osc1.stop(now + 0.5)

    // Chord 2 (E5 - 659.25 Hz)
    const osc2 = ctx.createOscillator()
    const gain2 = ctx.createGain()
    osc2.type = 'sine'
    osc2.frequency.setValueAtTime(659.25, now + 0.12)
    gain2.gain.setValueAtTime(0.15, now + 0.12)
    gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.7)
    osc2.connect(gain2)
    gain2.connect(ctx.destination)
    osc2.start(now + 0.12)
    osc2.stop(now + 0.7)

    // Chord 3 (G5 - 783.99 Hz - Climax Chime)
    const osc3 = ctx.createOscillator()
    const gain3 = ctx.createGain()
    osc3.type = 'triangle'
    osc3.frequency.setValueAtTime(783.99, now + 0.24)
    gain3.gain.setValueAtTime(0.18, now + 0.24)
    gain3.gain.exponentialRampToValueAtTime(0.0001, now + 1.2)
    osc3.connect(gain3)
    gain3.connect(ctx.destination)
    osc3.start(now + 0.24)
    osc3.stop(now + 1.2)
  } catch (e) {
    console.debug('Audio not supported or blocked:', e)
  }
}

// Transisi Halus dan Efek Modern Menuju Ruang Kerja Admin
const triggerLoginSuccessTransition = (user) => {
  authenticatedUserName.value = user?.nama || user?.name || user?.username || 'Dokter Penandatangan'
  qrStatus.value = 'APPROVED'
  isQrValidating.value = true

  // Bunyikan Audio Chime WOW
  playSuccessSound()

  // Berikan jeda agar user menikmati logo RSUD berputar & memancarkan aura
  setTimeout(() => {
    isTransitioningToAdmin.value = true
  }, 900)

  // Masuk secara smooth ke Dashboard
  setTimeout(() => {
    router.push('/').catch(() => {
      window.location.href = '/'
    })
  }, 1600)
}

const makeRandomId = (length) => {
  let result = ''
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
  }
  return result
}

const generateSimrsQrString = () => {
  const uid = Date.now().toString(36) + Math.random().toString(36)
  return `${uid}/${makeRandomId(3)}`
}

const fetchNewQrSession = async () => {
  qrLoading.value = true
  qrStatus.value = 'PENDING'
  qrCountdown.value = 180
  stopQrPolling()

  try {
    // 1. Buat kode QR yang formatnya 100% identik dengan SIMRS-V3
    const simrsQrCode = generateSimrsQrString()
    qrCodeString.value = simrsQrCode

    // 2. Minta backend merender gambar QR Code berlogo RSUD
    const res = await authApi.generateQr(simrsQrCode)
    qrSessionId.value = res.data.session_id
    qrBase64Image.value = res.data.qr_image_base64
    qrCountdown.value = res.data.expires_in_seconds || 180

    // 3. Hubungkan ke WebSocket Pusher SIMRS (channel: public.login.qr, event: .login-qr)
    setupPusherListener()
    startQrPolling()
  } catch (err) {
    console.error('Gagal generate QR login session:', err)
  } finally {
    qrLoading.value = false
  }
}

const setupPusherListener = () => {
  try {
    const echo = getEchoInstance()
    if (!echo) return

    if (!echoChannel) {
      echoChannel = echo.channel('public.login.qr')
      echoChannel.listen('.login-qr', async (e) => {
        // e.message: { menu: 'login-qr', data: qrCode, email: userEmail, token: userToken }
        const msg = e.message || e
        const scannedCode = msg.data || msg.qr
        // Cocokkan apakah kode yang discan oleh aplikasi mobile adalah QR yang ada di layar
        if (scannedCode === qrCodeString.value) {
          isQrValidating.value = true
          stopQrPolling()
          try {
            const loginRes = await authApi.loginQrSimrs({
              email: msg.email,
              token: msg.token
            })
            if (loginRes.data && loginRes.data.access_token) {
              localStorage.setItem('access_token', loginRes.data.access_token)
              localStorage.setItem('user', JSON.stringify(loginRes.data.user))
              showSuccessToast.value = true
              triggerLoginSuccessTransition(loginRes.data.user)
            }
          } catch (loginErr) {
            console.error('Gagal login via event QR Pusher:', loginErr)
            isQrValidating.value = false
          }
        }
      })
    }
  } catch (err) {
    console.warn('Gagal konek WebSocket Pusher SIMRS:', err)
  }
}

const startQrPolling = () => {
  stopQrPolling()

  // Polling fallback tiap 3 detik
  qrPollingTimer = setInterval(async () => {
    if (!qrSessionId.value) return
    try {
      const res = await authApi.checkQrStatus(qrSessionId.value)
      if (res.data.status === 'APPROVED' && res.data.access_token) {
        stopQrPolling()
        localStorage.setItem('access_token', res.data.access_token)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        showSuccessToast.value = true
        triggerLoginSuccessTransition(res.data.user)
      } else if (res.data.status === 'EXPIRED') {
        await fetchNewQrSession()
      }
    } catch (err) {
      console.warn('Gagal cek status QR session:', err)
    }
  }, 3000)
}

const stopQrPolling = () => {
  if (qrPollingTimer) clearInterval(qrPollingTimer)
  qrPollingTimer = null
}

const alertHelpdesk = () => {
  alert('Silakan hubungi Helpdesk BSrE BSSN RSUD dr. Mohamad Saleh Kota Probolinggo untuk dukungan teknis.')
}

// =========================================================================
// CANVAS PARTICLES & CYBER NETWORKS
// =========================================================================
const particleCanvasRef = ref(null)
let animId = null

const initParticles = () => {
  const canvas = particleCanvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  let width = (canvas.width = window.innerWidth)
  let height = (canvas.height = window.innerHeight)

  const handleResize = () => {
    if (!canvas) return
    width = canvas.width = window.innerWidth
    height = canvas.height = window.innerHeight
  }
  window.addEventListener('resize', handleResize)

  const particles = []
  const count = Math.min(Math.floor((width * height) / 16000), 75)

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.7,
      vy: (Math.random() - 0.5) * 0.7,
      radius: Math.random() * 2 + 1,
      color: Math.random() > 0.4 ? 'rgba(0, 240, 255, 0.4)' : 'rgba(0, 255, 157, 0.3)'
    })
  }

  const render = () => {
    ctx.clearRect(0, 0, width, height)

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]
      p.x += p.vx
      p.y += p.vy

      if (p.x < 0 || p.x > width) p.vx *= -1
      if (p.y < 0 || p.y > height) p.vy *= -1

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fillStyle = p.color
      ctx.fill()

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j]
        const dx = p.x - p2.x
        const dy = p.y - p2.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < 110) {
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = `rgba(0, 240, 255, ${0.15 * (1 - dist / 110)})`
          ctx.lineWidth = 0.75
          ctx.stroke()
        }
      }
    }
    animId = requestAnimationFrame(render)
  }

  render()
}

onMounted(() => {
  initParticles()
  fetchNewQrSession()
})

onUnmounted(() => {
  stopQrPolling()
  if (animId) cancelAnimationFrame(animId)
})
</script>

<style scoped>
/* Futuristik Glassmorphism & Cyber Shimmer Border */
.glass-box {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.cyber-border-glow {
  box-shadow: 0 0 35px -5px rgba(0, 240, 255, 0.15), 0 0 15px -3px rgba(0, 255, 157, 0.1);
}

/* Ambient Pulsing Orbs */
.orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(90px);
  pointer-events: none;
  z-index: 0;
}

@keyframes pulseSlow {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.9;
  }
}

.animate-pulse-slow {
  animation: pulseSlow 7s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

.animate-float {
  animation: float 4s ease-in-out infinite;
}

/* Scanning Laser Animation pada Box QR Code */
@keyframes laserScan {
  0% {
    top: 0%;
    opacity: 0.2;
  }
  50% {
    opacity: 0.9;
  }
  100% {
    top: 98%;
    opacity: 0.2;
  }
}

.animate-scan {
  animation: laserScan 2.2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* ========================================================================= */
/* EFEK MODERN & ANIMASI WOW QR LOGIN RSUD MOHAMAD SALEH                     */
/* ========================================================================= */

/* Rotasi Halus 3D Logo RSUD saat Validasi/Approved */
@keyframes rsudSpinPulse {
  0% {
    transform: rotate(0deg) scale(0.92);
    filter: drop-shadow(0 0 10px rgba(6, 182, 212, 0.45));
  }
  50% {
    transform: rotate(180deg) scale(1.08);
    filter: drop-shadow(0 0 25px rgba(16, 185, 129, 0.75));
  }
  100% {
    transform: rotate(360deg) scale(0.92);
    filter: drop-shadow(0 0 10px rgba(6, 182, 212, 0.45));
  }
}

.animate-rsud-spin {
  animation: rsudSpinPulse 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes spinSlow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spinSlow 6s linear infinite;
}

@keyframes spinReverse {
  from {
    transform: rotate(360deg);
  }
  to {
    transform: rotate(0deg);
  }
}

.animate-spin-reverse {
  animation: spinReverse 4s linear infinite;
}

@keyframes rippleWave {
  0% {
    transform: scale(0.85);
    opacity: 0.9;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

.animate-ripple {
  animation: rippleWave 1.9s cubic-bezier(0, 0.2, 0.8, 1) infinite;
}

/* Transisi Warp Sinematik Menuju Admin (Smooth WOW Effect) */
@keyframes portalWarp {
  0% {
    opacity: 0;
    transform: scale(0.97);
    backdrop-filter: blur(0px);
  }
  50% {
    opacity: 1;
    transform: scale(1);
    backdrop-filter: blur(18px);
  }
  100% {
    opacity: 1;
    transform: scale(1.01);
    backdrop-filter: blur(28px);
  }
}

.animate-portal-warp {
  animation: portalWarp 0.85s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes progressFill {
  0% {
    width: 0%;
  }
  100% {
    width: 100%;
  }
}

.animate-progress-fill {
  animation: progressFill 1.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes bounceSubtle {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-6px) scale(1.03);
  }
}

.animate-bounce-subtle {
  animation: bounceSubtle 1.8s ease-in-out infinite;
}

.warp-fade-enter-active,
.warp-fade-leave-active {
  transition: opacity 0.5s ease;
}
.warp-fade-enter-from,
.warp-fade-leave-to {
  opacity: 0;
}

.bg-grid {
  background-size: 36px 36px;
  background-image: 
    linear-gradient(to right, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
}
</style>
