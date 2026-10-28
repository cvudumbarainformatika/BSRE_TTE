# Cara Install Komponen ShadCN-Vue

Dokumentasi lengkap cara menambahkan komponen shadcn-vue yang belum ada di proyek ini.

## 📋 Daftar Komponen yang Sudah Ada

Komponen yang sudah terinstall di `src/components/ui/`:
- ✅ Button
- ✅ Card (Card, CardHeader, CardTitle, CardDescription, CardContent)
- ✅ Input
- ✅ Label

## 🎨 Cara Mengganti Color Theme

### Lokasi File Theme

Semua color theme didefinisikan di: **`src/css/tailwind.css`**

### ⚠️ PENTING: Format Warna Terbaru

**Proyek ini masih menggunakan format HSL lama.** Shadcn-vue terbaru sudah migrasi ke **OKLCH** untuk color space yang lebih baik.

**Format di Proyek Ini (HSL):**
```css
--primary: 0 0% 9%;  /* H S% L% */
```

**Format Terbaru Shadcn-Vue (OKLCH):**
```css
--primary: oklch(0.205 0 0);  /* oklch(L C H) */
```

**Rekomendasi:** Tetap gunakan HSL untuk sekarang karena sudah berfungsi. Jika ingin migrate ke OKLCH, lihat [dokumentasi Tailwind CSS](https://tailwindcss.com/docs/colors#using-oklch-colors).

---

### Struktur Color Variables

Proyek ini menggunakan **CSS Variables** untuk theming yang support light mode dan dark mode.

```css
@layer base {
  :root {
    /* Light Mode Colors */
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    /* ... dll */
  }

  .dark {
    /* Dark Mode Colors */
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    /* ... dll */
  }
}
```

### Format Color: HSL (Legacy)

Proyek ini menggunakan format **HSL** (Hue, Saturation, Lightness) **tanpa** `hsl()` wrapper.

**Format:** `H S% L%`

**Contoh:**
- `0 0% 9%` = Dark Gray (hampir hitam)
- `0 0% 98%` = Light Gray (hampir putih)
- `0 84.2% 60.2%` = Red
- `142.1 76.2% 36.3%` = Green

**Catatan:** Format ini berbeda dengan shadcn-vue terbaru yang menggunakan OKLCH.

### Cara Mengganti Primary Color

#### 1. Pilih Warna Baru

Gunakan color picker untuk mendapatkan nilai HSL. Tools online:
- https://hslpicker.com/
- https://www.w3schools.com/colors/colors_hsl.asp

**Contoh:** Ingin ganti primary menjadi **Blue**
- HSL: `hsl(221, 83%, 53%)`
- Format untuk CSS Variable: `221 83% 53%`

#### 2. Edit `src/css/tailwind.css`

Cari section `:root` untuk **light mode**:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  
  /* Ganti nilai ini */
  --primary: 221 83% 53%;              /* Blue */
  --primary-foreground: 0 0% 98%;      /* White text */
  
  /* ... colors lainnya ... */
}
```

Cari section `.dark` untuk **dark mode**:

```css
.dark {
  --background: 0 0% 3.9%;
  --foreground: 0 0% 98%;
  
  /* Ganti nilai ini untuk dark mode */
  --primary: 217 91% 60%;              /* Blue lebih terang */
  --primary-foreground: 0 0% 9%;       /* Dark text */
  
  /* ... colors lainnya ... */
}
```

#### 3. Save & Refresh Browser

Setelah save, refresh browser. Semua komponen yang menggunakan `bg-primary`, `text-primary`, dll akan otomatis berubah!

### Daftar Color Variables yang Tersedia

| Variable | Kegunaan | Contoh Penggunaan |
|----------|----------|-------------------|
| `--background` | Background utama halaman | `bg-background` |
| `--foreground` | Text color utama | `text-foreground` |
| `--card` | Background card | `bg-card` |
| `--card-foreground` | Text di card | `text-card-foreground` |
| `--popover` | Background popover/dropdown | `bg-popover` |
| `--popover-foreground` | Text di popover | `text-popover-foreground` |
| `--primary` | Warna utama (buttons, links) | `bg-primary`, `text-primary` |
| `--primary-foreground` | Text di atas primary | `text-primary-foreground` |
| `--secondary` | Warna sekunder | `bg-secondary` |
| `--secondary-foreground` | Text di atas secondary | `text-secondary-foreground` |
| `--muted` | Warna muted/subtle | `bg-muted` |
| `--muted-foreground` | Text muted | `text-muted-foreground` |
| `--accent` | Warna accent (hover, active) | `bg-accent` |
| `--accent-foreground` | Text di atas accent | `text-accent-foreground` |
| `--destructive` | Warna untuk delete/danger | `bg-destructive` |
| `--destructive-foreground` | Text di atas destructive | `text-destructive-foreground` |
| `--border` | Border color | `border-border` |
| `--input` | Input border color | `border-input` |
| `--ring` | Focus ring color | `ring-ring` |
| `--radius` | Border radius default | - |
| `--chart-1` sampai `--chart-5` | Warna untuk charts | `bg-chart-1` |

**Catatan:** Shadcn-vue terbaru juga punya variables untuk sidebar (`--sidebar`, `--sidebar-foreground`, dll) tapi belum ada di proyek ini.

### Contoh Theme Presets (HSL Format)

#### 🔵 Blue Theme
```css
:root {
  --primary: 221 83% 53%;
  --primary-foreground: 0 0% 98%;
}

.dark {
  --primary: 217 91% 60%;
  --primary-foreground: 0 0% 9%;
}
```

#### 🟣 Purple Theme
```css
:root {
  --primary: 270 70% 50%;
  --primary-foreground: 0 0% 98%;
}

.dark {
  --primary: 275 75% 60%;
  --primary-foreground: 0 0% 9%;
}
```

#### 🟢 Green Theme
```css
:root {
  --primary: 142 76% 36%;
  --primary-foreground: 0 0% 98%;
}

.dark {
  --primary: 142 71% 45%;
  --primary-foreground: 0 0% 9%;
}
```

#### 🔴 Red Theme
```css
:root {
  --primary: 0 84% 60%;
  --primary-foreground: 0 0% 98%;
}

.dark {
  --primary: 0 73% 51%;
  --primary-foreground: 0 0% 98%;
}
```

#### 🟠 Orange Theme
```css
:root {
  --primary: 25 95% 53%;
  --primary-foreground: 0 0% 98%;
}

.dark {
  --primary: 21 90% 48%;
  --primary-foreground: 0 0% 98%;
}
```

### Menggunakan Theme Generator Official

Shadcn-vue menyediakan theme generator di: **https://www.shadcn-vue.com/themes**

**Cara pakai:**
1. Kunjungi https://www.shadcn-vue.com/themes
2. Pilih theme yang diinginkan
3. Copy CSS variables yang digenerate
4. **PENTING:** Theme generator menghasilkan format OKLCH, Anda perlu convert ke HSL atau migrate proyek ke OKLCH

**Contoh convert OKLCH ke HSL:**
- OKLCH: `oklch(0.646 0.222 41.116)` 
- Gunakan tool: https://oklch.com/ untuk convert ke HSL

### Tips Memilih Warna

1. **Contrast Ratio** - Pastikan contrast antara `primary` dan `primary-foreground` cukup tinggi (minimal 4.5:1) untuk accessibility
2. **Dark Mode** - Warna di dark mode biasanya lebih terang (Lightness lebih tinggi) dari light mode
3. **Consistency** - Gunakan hue yang sama untuk primary, tapi variasikan saturation dan lightness
4. **Test** - Selalu test di light dan dark mode
5. **Accessibility** - Gunakan tools seperti https://webaim.org/resources/contrastchecker/

### Tools untuk Generate Color Palette

- **Shadcn-vue Themes:** https://www.shadcn-vue.com/themes (OKLCH format)
- **Realtime Colors:** https://realtimecolors.com/
- **UI Colors:** https://uicolors.app/create
- **Coolors:** https://coolors.co/
- **Adobe Color:** https://color.adobe.com/create/color-wheel
- **OKLCH Color Picker:** https://oklch.com/ (untuk convert OKLCH ↔ HSL)

### Cara Menggunakan Custom Colors di Tailwind

Setelah define di CSS variables, gunakan di class Tailwind:

```vue
<template>
  <!-- Background -->
  <div class="bg-primary text-primary-foreground">
    Primary Background
  </div>

  <!-- Border -->
  <div class="border-2 border-primary">
    Primary Border
  </div>

  <!-- Text -->
  <p class="text-primary">
    Primary Text
  </p>

  <!-- Hover -->
  <button class="hover:bg-primary hover:text-primary-foreground">
    Hover Primary
  </button>

  <!-- Chart Colors -->
  <div class="bg-chart-1">Chart Color 1</div>
  <div class="bg-chart-2">Chart Color 2</div>
</template>
```

### Menambahkan Custom Color Variables

Jika ingin menambahkan warna custom (contoh: `warning`):

**1. Tambahkan di `src/css/tailwind.css`:**
```css
:root {
  --warning: 38 92% 50%;
  --warning-foreground: 0 0% 98%;
}

.dark {
  --warning: 32 95% 44%;
  --warning-foreground: 0 0% 98%;
}
```

**2. Tambahkan di `tailwind.config.js`:**
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        warning: 'hsl(var(--warning))',
        'warning-foreground': 'hsl(var(--warning-foreground))',
      }
    }
  }
}
```

**3. Gunakan di template:**
```vue
<div class="bg-warning text-warning-foreground">
  Warning message!
</div>
```

---

## 🚀 Cara Install Komponen Baru

### ✅ Metode Recommended: Menggunakan CLI

**Cara tercepat dan termudah!** CLI shadcn-vue **BISA DIGUNAKAN** di proyek ini.

#### Langkah 1: Install Komponen dengan CLI

```bash
npx shadcn-vue@latest add button
```

atau untuk komponen lain:

```bash
npx shadcn-vue@latest add card
npx shadcn-vue@latest add dialog
npx shadcn-vue@latest add dropdown-menu
npx shadcn-vue@latest add select
npx shadcn-vue@latest add avatar
npx shadcn-vue@latest add badge
```

#### Langkah 2: Cek Hasil

CLI akan otomatis:
- ✅ Menambahkan komponen ke `src/components/ui/[component]/`
- ✅ Install dependencies yang diperlukan (Radix Vue, dll)
- ✅ Setup dengan konfigurasi yang benar

#### Langkah 3: Import dan Gunakan

Import komponen dari folder yang dibuat CLI:

```vue
<script setup>
// Import dari folder component
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Hello World</CardTitle>
    </CardHeader>
    <CardContent>
      <Button>Click Me</Button>
    </CardContent>
  </Card>
</template>
```

**Catatan:** CLI membuat folder untuk setiap komponen (contoh: `button/`, `card/`, `avatar/`), bukan file tunggal.

---

### Metode 2: Manual Installation (Alternatif)

Jika CLI tidak bekerja atau Anda ingin kontrol penuh, install secara manual.


#### Langkah 1: Cek Komponen di Dokumentasi

Kunjungi: https://www.shadcn-vue.com/docs/components/

Pilih komponen yang ingin diinstall, misalnya: **Dialog**, **Dropdown Menu**, **Select**, dll.

#### Langkah 2: Install Dependencies (Jika Diperlukan)

Beberapa komponen memerlukan dependencies tambahan. Cek di dokumentasi komponen tersebut.

Contoh untuk **Dialog**:
```bash
npm install @radix-vue/dialog
```

Contoh untuk **Dropdown Menu**:
```bash
npm install @radix-vue/dropdown-menu
```

Contoh untuk **Select**:
```bash
npm install @radix-vue/select
```

#### Langkah 3: Copy Kode Komponen

Buka halaman komponen di dokumentasi shadcn-vue, lalu:

1. Klik tab **"Code"** atau **"Installation"**
2. Copy kode komponen Vue
3. Buat file baru di `src/components/ui/[NamaKomponen].vue`
4. Paste kode tersebut

**Contoh untuk Dialog:**

Buat file: `src/components/ui/Dialog.vue`
```vue
<script setup lang="ts">
import { DialogRoot, DialogTrigger, DialogPortal, DialogOverlay, DialogContent, DialogTitle, DialogDescription, DialogClose } from 'radix-vue'

// Props dan logic dari dokumentasi
</script>

<template>
  <!-- Template dari dokumentasi -->
</template>
```

#### Langkah 4: Sesuaikan Import Path

Pastikan import path menggunakan alias `@/`:

```javascript
// ✅ Benar
import Button from '@/components/ui/Button.vue'

// ❌ Salah
import Button from '~/components/ui/Button.vue'
```

#### Langkah 5: Test Komponen

Buat test sederhana di halaman untuk memastikan komponen berfungsi:

```vue
<script setup>
import Dialog from '@/components/ui/Dialog.vue'
</script>

<template>
  <Dialog>
    <!-- Test content -->
  </Dialog>
</template>
```

---

## 📦 Contoh Install Komponen Populer

### 1. Dialog / Modal

**Install dependency:**
```bash
npm install @radix-vue/dialog
```

**Buat file:** `src/components/ui/Dialog.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/dialog

---

### 2. Dropdown Menu

**Install dependency:**
```bash
npm install @radix-vue/dropdown-menu
```

**Buat file:** `src/components/ui/DropdownMenu.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/dropdown-menu

---

### 3. Select

**Install dependency:**
```bash
npm install @radix-vue/select
```

**Buat file:** `src/components/ui/Select.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/select

---

### 4. Tabs

**Install dependency:**
```bash
npm install @radix-vue/tabs
```

**Buat file:** `src/components/ui/Tabs.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/tabs

---

### 5. Toast / Notification

**Install dependency:**
```bash
npm install @radix-vue/toast
```

**Buat file:** `src/components/ui/Toast.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/toast

---

### 6. Popover

**Install dependency:**
```bash
npm install @radix-vue/popover
```

**Buat file:** `src/components/ui/Popover.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/popover

---

### 7. Table

**Tidak perlu dependency tambahan** (pure Tailwind)

**Buat file:** `src/components/ui/Table.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/table

---

### 8. Badge

**Tidak perlu dependency tambahan** (pure Tailwind)

**Buat file:** `src/components/ui/Badge.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/badge

---

### 9. Avatar

**Install dependency:**
```bash
npm install @radix-vue/avatar
```

**Buat file:** `src/components/ui/Avatar.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/avatar

---

### 10. Checkbox

**Install dependency:**
```bash
npm install @radix-vue/checkbox
```

**Buat file:** `src/components/ui/Checkbox.vue`

**Copy dari:** https://www.shadcn-vue.com/docs/components/checkbox

---

## 🎨 Komponen yang Sudah Dikustomisasi

Beberapa komponen di proyek ini sudah dikustomisasi untuk kompatibilitas dengan Quasar:

### Button.vue

Sudah ditambahkan `/* @vue-ignore */` untuk mengatasi TypeScript error:

```vue
interface ButtonProps extends /* @vue-ignore */ VariantProps<typeof buttonVariants> {
  tag?: string
}
```

### Card Components

Sudah dibuat modular dengan file terpisah:
- `Card.vue` - Container utama
- `CardHeader.vue` - Header section
- `CardTitle.vue` - Title text
- `CardDescription.vue` - Description text
- `CardContent.vue` - Content section

---

## 🔧 Troubleshooting

### Error: "Cannot find module '@radix-vue/...'"

**Solusi:** Install dependency yang diperlukan:
```bash
npm install @radix-vue/[nama-komponen]
```

### Error: "Unknown at rule @apply"

**Solusi:** Ini adalah warning dari CSS linter, bisa diabaikan. Tailwind `@apply` berfungsi normal.

### Error: TypeScript interface extends error

**Solusi:** Tambahkan `/* @vue-ignore */` sebelum extends:
```typescript
interface Props extends /* @vue-ignore */ VariantProps<typeof variants> {
  // props
}
```

### Komponen tidak ter-style dengan benar

**Solusi:** 
1. Pastikan `tailwind.css` sudah di-import di `quasar.config.js`
2. Cek apakah CSS variables sudah didefinisikan di `src/css/tailwind.css`
3. Pastikan Tailwind config sudah benar di `tailwind.config.js`

---

## 📚 Resources

- **ShadCN-Vue Docs:** https://www.shadcn-vue.com/
- **Radix Vue Docs:** https://www.radix-vue.com/
- **Tailwind CSS Docs:** https://tailwindcss.com/
- **Lucide Icons:** https://lucide.dev/

---

## 💡 Tips

1. **Selalu cek dependencies** - Beberapa komponen memerlukan Radix Vue packages
2. **Test di browser** - Pastikan komponen berfungsi sebelum digunakan di production
3. **Gunakan TypeScript** - Untuk autocomplete dan type safety yang lebih baik
4. **Customize sesuai kebutuhan** - Jangan ragu untuk memodifikasi komponen sesuai design system Anda
5. **Konsisten dengan naming** - Gunakan PascalCase untuk nama file komponen (contoh: `DropdownMenu.vue`)

---

## 🎯 Next Steps

Setelah install komponen baru:

1. ✅ Test komponen di halaman `/full-shadcn`
2. ✅ Tambahkan ke showcase jika perlu
3. ✅ Update dokumentasi jika ada customization
4. ✅ Commit changes ke Git

---

**Happy Coding! 🚀**
