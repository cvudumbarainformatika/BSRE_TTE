<template>
  <div class="relative min-h-screen w-full flex items-center justify-center p-4 overflow-hidden font-sans bg-background text-foreground transition-colors duration-300">
    <!-- CANVAS BACKGROUND PARTICLE EFFECT -->
    <canvas ref="particleCanvasRef" class="absolute inset-0 w-full h-full z-0 pointer-events-none opacity-60"></canvas>
    
    <!-- BACKGROUND GRID LINES OVERLAY -->
    <div class="absolute inset-0 z-0 pointer-events-none bg-grid opacity-30 dark:opacity-60"></div>

    <!-- AMBIENT GLOW ORBS -->
    <div class="orb w-[500px] h-[500px] bg-primary/20 -top-20 -left-20 animate-pulse-slow"></div>
    <div class="orb w-[450px] h-[450px] bg-primary/15 -bottom-20 -right-20 animate-pulse-slow"></div>

    <!-- MAIN CONTAINER CARD -->
    <div class="relative z-10 w-full max-w-lg rounded-3xl glass-box cyber-border-glow overflow-hidden p-8 sm:p-10 bg-card/90 border border-border shadow-2xl">
      <!-- Top Branding -->
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-border">
        <div class="flex items-center space-x-3">
          <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-cyan-400 via-primary to-emerald-400 p-0.5 shadow-lg shadow-primary/25">
            <div class="w-full h-full rounded-[14px] flex items-center justify-center bg-card text-primary">
              <Terminal class="w-6 h-6" />
            </div>
          </div>
          <div>
            <span class="text-[10px] font-mono tracking-widest text-primary uppercase font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/30">
              INTERNAL IT ONLY
            </span>
            <h1 class="text-lg font-extrabold tracking-wide text-foreground">
              PORTAL LOGIN <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">KHUSUS IT</span>
            </h1>
            <p class="text-[10px] text-muted-foreground font-medium">UOBK RSUD dr. Mohamad Saleh</p>
          </div>
        </div>

        <Button
          type="button"
          variant="outline"
          size="icon"
          class="h-9 w-9 rounded-xl border border-border text-foreground hover:bg-muted"
          :title="isDark ? 'Mode Terang' : 'Mode Gelap'"
          @click="toggleTheme"
        >
          <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
          <Moon v-else class="w-4 h-4 text-muted-foreground" />
        </Button>
      </div>

      <div class="mb-6">
        <h2 class="text-base font-bold text-foreground">Login Akun SIMRS / IT</h2>
        <p class="text-xs text-muted-foreground mt-1">
          Halaman autentikasi khusus Administrator & Teknisi IT SIMRS menggunakan kredensial master SIMRS.
        </p>
      </div>

      <!-- FORM LOGIN USERNAME & PASSWORD -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- Input Username / NIP / Email -->
        <AppInput
          id="it-username"
          label="USERNAME / NIP / EMAIL"
          v-model="form.username"
          placeholder="Contoh: admin, sa, atau NIP IT"
          :error="errors.username"
          autofocus
        >
          <template #prefix>
            <UserCheck class="w-4 h-4 text-muted-foreground" />
          </template>
        </AppInput>

        <!-- Input Password -->
        <AppInput
          id="it-password"
          label="PASSWORD SIMRS"
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="Masukkan Password Akun Anda"
          :error="errors.password"
        >
          <template #prefix>
            <Lock class="w-4 h-4 text-muted-foreground" />
          </template>
          <template #suffix>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              class="h-7 w-7 text-muted-foreground hover:text-primary"
              @click="showPassword = !showPassword"
            >
              <EyeOff v-if="showPassword" class="w-4 h-4" />
              <Eye v-else class="w-4 h-4" />
            </Button>
          </template>
        </AppInput>

        <!-- Captcha Security Box -->
        <div>
          <label class="block text-xs font-bold text-foreground mb-1.5 font-mono">
            KODE VERIFIKASI KEAMANAN (CAPTCHA)
          </label>
          <div class="grid grid-cols-12 gap-3 items-center">
            <div class="col-span-7 sm:col-span-8">
              <AppInput
                id="it-captcha"
                v-model="form.captcha"
                placeholder="Ketik 5 Digit Kode"
                maxlength="5"
                class="font-mono uppercase tracking-widest"
                :error="errors.captcha"
              >
                <template #prefix>
                  <Fingerprint class="w-4 h-4 text-muted-foreground" />
                </template>
              </AppInput>
            </div>

            <div class="col-span-5 sm:col-span-4 flex items-center space-x-2">
              <div class="h-10 px-3 flex-1 flex items-center justify-center font-mono font-black text-sm tracking-[0.25em] rounded-xl border border-border bg-muted text-primary select-none shadow-inner">
                {{ captchaCode }}
              </div>
              <Button
                type="button"
                variant="outline"
                size="icon"
                class="h-10 w-10 shrink-0 rounded-xl border-border hover:bg-muted"
                title="Ganti Kode Captcha"
                @click="generateCaptcha"
              >
                <RotateCcw class="w-4 h-4 text-muted-foreground" />
              </Button>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-2">
          <Button
            type="submit"
            :disabled="isLoading"
            class="w-full h-11 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl cursor-pointer"
          >
            <div v-if="isLoading" class="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
            <ShieldCheck v-else class="w-4 h-4" />
            <span>{{ isLoading ? 'Memverifikasi Akses IT...' : 'Masuk ke Sistem E-DOC' }}</span>
          </Button>
        </div>
      </form>

      <!-- Bottom Info -->
      <div class="mt-6 pt-4 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground">
        <span>Sub-Divisi SIMRS & Teknologi Informasi</span>
        <router-link to="/login" class="text-primary hover:underline font-semibold flex items-center gap-1">
          ← Kembali ke Login QR
        </router-link>
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
          <h4 class="text-xs font-bold text-foreground">Login IT Berhasil!</h4>
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
import AppInput from '@/components/AppInput.vue'
import { Button } from '@/components/ui/button'
import {
  ShieldCheck,
  Terminal,
  UserCheck,
  Lock,
  Eye,
  EyeOff,
  Fingerprint,
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

const showPassword = ref(false)
const showSuccessToast = ref(false)
const isLoading = ref(false)

const form = reactive({
  username: '',
  password: '',
  captcha: ''
})

const errors = reactive({
  username: '',
  password: '',
  captcha: ''
})

// Captcha Generator
const captchaCode = ref('87B9X')
const generateCaptcha = () => {
  const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
  let res = ''
  for (let i = 0; i < 5; i++) {
    res += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaCode.value = res
  form.captcha = res // kenyamanan akses
}

const handleLogin = async () => {
  errors.username = ''
  errors.password = ''
  errors.captcha = ''

  if (!form.username.trim()) {
    errors.username = 'Username / NIP wajib diisi'
    return
  }
  if (!form.password.trim()) {
    errors.password = 'Password wajib diisi'
    return
  }
  if (form.captcha.trim().toUpperCase() !== captchaCode.value.toUpperCase()) {
    errors.captcha = 'Kode Captcha tidak sesuai'
    return
  }

  isLoading.value = true
  try {
    const res = await authApi.login({
      username: form.username.trim(),
      password: form.password.trim()
    })

    if (res.data && res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      showSuccessToast.value = true
      setTimeout(() => {
        router.push('/')
      }, 1000)
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Autentikasi gagal. Periksa kembali Username dan Password Anda.')
  } finally {
    isLoading.value = false
  }
}

// Canvas Particles
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
  const count = Math.min(Math.floor((width * height) / 16000), 50)

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.7,
      vy: (Math.random() - 0.5) * 0.7,
      radius: Math.random() * 2 + 1,
      color: 'rgba(0, 240, 255, 0.35)'
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
    }
    animId = requestAnimationFrame(render)
  }
  render()
}

onMounted(() => {
  generateCaptcha()
  initParticles()
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
})
</script>

<style scoped>
.glass-box {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.cyber-border-glow {
  box-shadow: 0 0 35px -5px rgba(0, 240, 255, 0.15), 0 0 15px -3px rgba(0, 255, 157, 0.1);
}
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
.bg-grid {
  background-size: 36px 36px;
  background-image: 
    linear-gradient(to right, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
}
</style>
