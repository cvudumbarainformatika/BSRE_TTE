<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-[#f0f4f8] relative overflow-hidden p-4 font-sans">
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] animate-blob"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-400/20 rounded-full blur-[120px] animate-blob animation-delay-2000"></div>

    <div class="w-full max-w-md z-10 animate-fade-in-up">
      <Card class="relative bg-white/85 backdrop-blur-3xl border border-white/40 shadow-2xl rounded-[36px] overflow-hidden">
        <CardContent class="p-10 md:p-12 relative z-20">
          <!-- Logo & Header -->
          <div class="flex flex-col items-center mb-8 text-center">
            <div class="h-20 w-20 bg-white shadow-xl rounded-[24px] flex items-center justify-center mb-5 ring-1 ring-black/5">
              <img :src="logoRsud" alt="Logo RSUD" class="h-12 w-12 object-contain" />
            </div>
            <h1 class="text-2xl font-black tracking-tight text-slate-800 mb-2">SIMRS TTE BSrE</h1>
            <Badge variant="secondary" class="px-4 py-1 text-[10px] uppercase tracking-widest font-black">
              RSUD dr. Mohamad Saleh
            </Badge>
          </div>

          <!-- Form Menggunakan Komponen Modular AppInput & Button -->
          <form @submit.prevent="handleLogin" class="space-y-5">
            <AppInput
              id="login-username"
              label="USERNAME"
              v-model="form.username"
              placeholder="Username Anda"
            >
              <template #prefix>
                <User class="h-4 w-4" />
              </template>
            </AppInput>

            <AppInput
              id="login-password"
              label="PASSWORD"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
            >
              <template #prefix>
                <Lock class="h-4 w-4" />
              </template>
              <template #suffix>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  class="h-7 w-7 text-slate-400 hover:text-primary"
                  @click="showPassword = !showPassword"
                >
                  <Eye v-if="!showPassword" class="h-4 w-4" />
                  <EyeOff v-else class="h-4 w-4" />
                </Button>
              </template>
            </AppInput>

            <div class="pt-3">
              <Button
                type="submit"
                :disabled="loading"
                class="w-full h-12 bg-slate-900 hover:bg-black text-white font-bold rounded-xl shadow-lg gap-2"
              >
                <span>{{ loading ? 'Memverifikasi...' : 'Masuk Ke Sistem' }}</span>
                <ArrowRight v-if="!loading" class="h-4 w-4" />
              </Button>
            </div>
          </form>
        </CardContent>

        <div class="bg-slate-50/80 border-t border-slate-100 p-5 text-center">
          <p class="text-[9px] text-slate-400 uppercase font-black tracking-[0.3em]">
            &copy; RSUD dr. Mohamad Saleh &bull; Kota Probolinggo
          </p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useQuasar } from 'quasar'
import AppInput from '@/components/AppInput.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { User, Lock, Eye, EyeOff, ArrowRight } from 'lucide-vue-next'
import logoRsud from '@/assets/images/logo-rsud.png'

const router = useRouter()
const auth = useAuthStore()
const $q = useQuasar()

const loading = ref(false)
const showPassword = ref(false)

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  loading.value = true
  try {
    const success = await auth.login(form.username, form.password)
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'Akses Diterima! Selamat datang di sistem.',
        icon: 'verified',
        position: 'top-right'
      })
      router.push('/')
    } else {
      $q.notify({
        type: 'negative',
        message: auth.error || 'Autentikasi gagal. Periksa kembali akun Anda.',
        icon: 'error_outline',
        position: 'top-right'
      })
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
