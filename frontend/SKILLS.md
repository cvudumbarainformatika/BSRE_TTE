---
name: Frontend Development with Shadcn-Vue & Tailwind
description: Pedoman pengembangan frontend modular menggunakan Quasar, Shadcn-vue, dan Tailwind CSS.
---

# Pedoman Pengembangan Frontend e-RTLH

Selalu gunakan standar ini dalam pengembangan frontend agar kode tetap bersih, modular, dan konsisten.

## 1. UI Stack
- **Framework**: Quasar (Vite)
- **Styling**: Tailwind CSS (Utility-first)
- **UI Components**: Shadcn-vue (Radix Vue)
- **Icons**: Lucide Vue Next

## 2. Prinsip Modularitas
Pisahkan fitur berdasarkan modul di dalam `src/modules` (jika proyek bertumbuh besar) atau gunakan struktur direktori yang konsisten:
- `src/components/ui`: Komponen dasar Shadcn.
- `src/components/shared`: Komponen yang digunakan di banyak fitur (Header, Sidebar).
- `src/modules/[feature]`: Berisi komponen, store, dan utilitas khusus fitur tersebut.

## 3. Aturan Shadcn-vue & Tailwind
- **Prioritas Pertama**: Selalu gunakan komponen dari `src/components/ui`.
- **Customization**: Gunakan class Tailwind untuk styling tambahan. Hindari class Quasar (`q-pa-md`, `q-mb-sm`, dll) kecuali untuk komponen layout Quasar yang memang diperlukan.
- **Dark Mode**: Gunakan class `dark:` dari Tailwind. Pastikan sinkron dengan state `$q.dark.isActive`.

## 4. Komunikasi API
- Gunakan `src/boot/axios.js` untuk instance global.
- Semua request ke backend dikelompokkan dalam file service/api di setiap modul.

## 5. State Management
- Gunakan **Pinia** untuk manajemen state global.
- Pisahkan store per modul fitur.

---
> [!IMPORTANT]
> Jangan campur aduk class Quasar UI dengan Tailwind di dalam komponen murni Shadcn. Jaga agar elemen UI tetap menggunakan standar Tailwind.
