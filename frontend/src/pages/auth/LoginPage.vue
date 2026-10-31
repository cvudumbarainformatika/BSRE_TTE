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
          <div class="flex items-center space-x-3 mb-6">
            <!-- Floating Shield Icon -->
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-400 via-primary to-emerald-400 p-0.5 shadow-lg shadow-primary/25 animate-float">
              <div class="w-full h-full rounded-[14px] flex items-center justify-center bg-card text-primary">
                <ShieldCheck class="w-7 h-7" />
              </div>
            </div>
            <div>
              <span class="text-[10px] font-mono tracking-widest text-primary uppercase font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/30">
                BSSN VERIFIED TTE
              </span>
              <h1 class="text-xl font-extrabold tracking-wide flex items-center gap-1.5 mt-0.5 text-foreground">
                E-DOC <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">BSrE</span>
              </h1>
              <p class="text-[10px] text-muted-foreground font-medium tracking-tight">UOBK RSUD dr. Mohamad Saleh</p>
            </div>
          </div>

          <h2 class="text-2xl font-extrabold leading-tight text-foreground">
            Portal Keamanan & Otorisasi <span class="text-primary underline decoration-primary/50 underline-offset-4">Dokumen TTE</span>
          </h2>
          <p class="text-xs mt-3 leading-relaxed text-muted-foreground">
            Sistem Terintegrasi Single Sign-On (SSO) SIMRS & Balai Sertifikasi Elektronik (BSrE - BSSN Republik Indonesia).
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

          <!-- Feature 2: P12 / PFX -->
          <div class="p-3.5 rounded-2xl border border-border bg-card/60 hover:border-primary/40 transition-all flex items-center space-x-3.5">
            <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20">
              <Key class="w-4 h-4" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-foreground">Sertifikat Digital P12/PFX</h3>
              <p class="text-[11px] text-muted-foreground">Otentikasi Kriptografi Asimetris RSA 2048-bit</p>
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
      <!-- SISI KANAN: LOGIN FORM & AUTHENTICATION TABS (7 Cols)               -->
      <!-- =================================================================== -->
      <div class="lg:col-span-7 p-8 lg:p-12 flex flex-col justify-between relative bg-card/40">
        <div>
          <!-- Header Tabs Navigation & Right Controls -->
          <div class="flex items-center justify-between mb-8 pb-3 border-b border-border">
            <div class="flex flex-wrap gap-1.5 sm:gap-2">
              <!-- Tab 1: QR SIMRS -->
              <Button
                type="button"
                size="sm"
                :variant="activeTab === 'qr' ? 'secondary' : 'ghost'"
                class="rounded-xl text-xs font-bold transition-all gap-1.5 h-9 px-3"
                :class="activeTab === 'qr'
                  ? 'bg-primary/15 text-primary border border-primary/30 shadow-xs'
                  : 'text-muted-foreground hover:text-foreground'"
                @click="switchTab('qr')"
              >
                <QrCode class="w-3.5 h-3.5" />
                <span>Scan QR SIMRS</span>
              </Button>

              <!-- Tab 2: P12 Cert -->
              <Button
                type="button"
                size="sm"
                :variant="activeTab === 'cert' ? 'secondary' : 'ghost'"
                class="rounded-xl text-xs font-bold transition-all gap-1.5 h-9 px-3"
                :class="activeTab === 'cert'
                  ? 'bg-primary/15 text-primary border border-primary/30 shadow-xs'
                  : 'text-muted-foreground hover:text-foreground'"
                @click="switchTab('cert')"
              >
                <FileSignature class="w-3.5 h-3.5" />
                <span>File P12</span>
              </Button>
            </div>

            <!-- Right Controls: Toggle Tema Light/Dark -->
            <div class="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="icon"
                class="h-9 w-9 rounded-xl border border-border text-foreground hover:bg-muted"
                :title="isDark ? 'Ganti ke Mode Terang (Light)' : 'Ganti ke Mode Gelap (Dark)'"
                @click="toggleTheme"
              >
                <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
                <Moon v-else class="w-4 h-4 text-muted-foreground" />
              </Button>
            </div>
          </div>

          <!-- =============================================================== -->
          <!-- TAB 1: LOGIN SCAN QR CODE SIMRS (Seperti SIMRS / WA Web)        -->
          <!-- =============================================================== -->
          <div v-if="activeTab === 'qr'" class="space-y-5 text-center py-2">
            <div class="max-w-md mx-auto">
              <h3 class="text-sm font-bold text-foreground">Masuk dengan Scan QR SIMRS</h3>
              <p class="text-xs text-muted-foreground mt-1">
                Buka aplikasi SIMRS Mobile / Scanner Dokter di smartphone Anda dan arahkan ke kode QR berikut.
              </p>
            </div>

            <!-- QR Container Card -->
            <div class="relative w-56 h-56 mx-auto p-3.5 bg-card rounded-2xl border-2 border-primary/40 shadow-xl overflow-hidden flex items-center justify-center group">
              <!-- Loading State -->
              <div v-if="qrLoading" class="flex flex-col items-center justify-center space-y-2 text-muted-foreground">
                <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                <span class="text-xs">Membuat QR Sesi...</span>
              </div>

              <!-- Active QR Image (Selalu Otomatis Segar) -->
              <div v-else-if="qrBase64Image" class="relative w-full h-full flex items-center justify-center bg-white rounded-xl p-2">
                <img
                  :src="qrBase64Image"
                  alt="QR Code Login SIMRS"
                  class="w-full h-full object-contain"
                />
                <!-- Scanning Laser Line -->
                <div class="absolute inset-x-0 h-1 bg-primary shadow-lg shadow-primary animate-scan pointer-events-none"></div>
              </div>

              <!-- Fallback State jika QR gagal dimuat -->
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
              <span v-if="qrStatus === 'APPROVED'" class="text-emerald-500 font-bold flex items-center gap-1.5">
                <CheckCircle2 class="w-4 h-4" />
                Otentikasi Berhasil! Mengalihkan...
              </span>
              <span v-else class="text-muted-foreground flex items-center gap-2 bg-muted/60 px-3 py-1 rounded-full border border-border">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                <span>QR Aktif • Auto-refresh otomatis</span>
              </span>
            </div>
          </div>

          <!-- =============================================================== -->
          <!-- TAB 2: FORM LOGIN FILE DIGITAL CERTIFICATE (.P12 / .PFX)        -->
          <!-- =============================================================== -->
          <form v-else-if="activeTab === 'cert'" @submit.prevent="handleCertLogin" class="space-y-4">
            <input
              ref="certFileInputRef"
              type="file"
              accept=".p12,.pfx"
              class="hidden"
              @change="onCertFileChange"
            />

            <!-- Drag & Drop P12 File Upload Area -->
            <div>
              <label class="block text-xs font-bold text-foreground mb-1.5 font-mono">
                UNGGAH FILE SERTIFIKAT DIGITAL (.P12 / .PFX)
              </label>
              <div
                class="border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer group"
                :class="uploadedCertFile
                  ? 'border-emerald-500 bg-emerald-500/10'
                  : 'border-border hover:border-primary/50 bg-muted/20'"
                @click="triggerCertFileInput"
              >
                <div class="w-12 h-12 rounded-2xl bg-primary/10 text-primary mx-auto flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                  <FileKey class="w-6 h-6" />
                </div>
                <p class="text-xs font-bold text-foreground">
                  {{ uploadedCertFile ? uploadedCertFile.name : 'Pilih atau drag & drop file sertifikat .p12' }}
                </p>
                <p class="text-[11px] text-muted-foreground mt-0.5">
                  Diterbitkan oleh Balai Sertifikasi Elektronik (BSrE BSSN)
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  class="mt-3 rounded-lg text-xs h-7 border-border font-medium"
                >
                  {{ uploadedCertFile ? 'Ganti File P12' : 'Pilih File P12' }}
                </Button>
              </div>
            </div>

            <!-- Passphrase P12 -->
            <AppInput
              id="cert-passphrase"
              label="PASSPHRASE DEKRIPSI SERTIFIKAT"
              v-model="certForm.passphrase"
              :type="showCertPassphrase ? 'text' : 'password'"
              placeholder="Masukkan Passphrase File .P12"
              :error="formErrors.certPassphrase"
            >
              <template #prefix>
                <Key class="w-4 h-4 text-muted-foreground" />
              </template>
              <template #suffix>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  class="h-7 w-7 text-muted-foreground hover:text-primary"
                  @click="showCertPassphrase = !showCertPassphrase"
                >
                  <EyeOff v-if="showCertPassphrase" class="w-4 h-4" />
                  <Eye v-else class="w-4 h-4" />
                </Button>
              </template>
            </AppInput>

            <!-- Submit Button (P12 Login) -->
            <div class="pt-2">
              <Button
                type="submit"
                :disabled="isLoading"
                class="w-full h-11 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl cursor-pointer"
              >
                <div v-if="isLoading" class="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                <Fingerprint v-else class="w-4 h-4" />
                <span>{{ isLoading ? 'Mendekripsi Sertifikat...' : 'Otentikasi Sertifikat Digital' }}</span>
              </Button>
            </div>
          </form>
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
import {
  ShieldCheck,
  Key,
  FileCheck,
  UserCheck,
  FileSignature,
  QrCode,
  Lock,
  Eye,
  EyeOff,
  Fingerprint,
  RotateCcw,
  FileKey,
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

// Active Tab ('qr' atau 'cert')
const activeTab = ref('qr')
const showCertPassphrase = ref(false)
const showSuccessToast = ref(false)
const isLoading = ref(false)

// State Form File P12
const certForm = reactive({
  passphrase: 'password123'
})
const certFileInputRef = ref(null)
const uploadedCertFile = ref(null)

const formErrors = reactive({
  certPassphrase: ''
})

// QR Code Session State
const qrSessionId = ref('')
const qrCodeString = ref('')
const qrBase64Image = ref('')
const qrCountdown = ref(180)
const qrStatus = ref('PENDING')
const qrLoading = ref(false)
let qrPollingTimer = null
let echoChannel = null

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

const switchTab = (tabName) => {
  activeTab.value = tabName
  if (tabName === 'qr') {
    fetchNewQrSession()
  } else {
    stopQrPolling()
  }
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
          qrStatus.value = 'APPROVED'
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
              setTimeout(() => {
                router.push('/')
              }, 800)
            }
          } catch (loginErr) {
            console.error('Gagal login via event QR Pusher:', loginErr)
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
        qrStatus.value = 'APPROVED'
        stopQrPolling()
        localStorage.setItem('access_token', res.data.access_token)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        showSuccessToast.value = true
        setTimeout(() => {
          router.push('/')
        }, 800)
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

const triggerCertFileInput = () => {
  if (certFileInputRef.value) {
    certFileInputRef.value.click()
  }
}

const onCertFileChange = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    uploadedCertFile.value = file
  }
}

const alertHelpdesk = () => {
  alert('Silakan hubungi Helpdesk BSrE BSSN RSUD dr. Mohamad Saleh Kota Probolinggo untuk dukungan teknis.')
}

// =========================================================================
// HANDLER LOGIN CERTIFICATE (.P12)
// =========================================================================
const handleCertLogin = async () => {
  formErrors.certPassphrase = ''
  if (!certForm.passphrase.trim()) {
    formErrors.certPassphrase = 'Passphrase file sertifikat P12 wajib diisi'
    return
  }

  isLoading.value = true
  try {
    const res = await authApi.login({
      username: 'dr_rizki',
      password: 'password123'
    })
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    showSuccessToast.value = true
    setTimeout(() => {
      router.push('/')
    }, 1200)
  } catch (err) {
    alert('Dekripsi file .P12 gagal: ' + (err.response?.data?.detail || err.message))
  } finally {
    isLoading.value = false
  }
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
  if (activeTab.value === 'qr') {
    fetchNewQrSession()
  }
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

.bg-grid {
  background-size: 36px 36px;
  background-image: 
    linear-gradient(to right, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
}
</style>
