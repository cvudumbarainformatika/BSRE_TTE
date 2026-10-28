# Standar Operasional Prosedur (SOP) Desain Premium Sistem Antrian

Dokumen ini adalah **KONTRAK WAJIB** bagi AI (Antigravity) dalam membangun UI. Setiap perubahan kode frontend HARUS mematuhi aturan berikut tanpa pengecualian.

## 1. Warna & Tema (Semantic First)
- **DILARANG KERAS** menggunakan warna hardcoded (seperti `bg-slate-950`, `text-white`, `bg-black`) langsung pada elemen.
- **WAJIB** menggunakan variabel semantik agar responsif terhadap Light & Dark Mode:
  - Gunakan `bg-card` untuk kartu/modal.
  - Gunakan `bg-background` untuk latar belakang utama.
  - Gunakan `text-foreground` untuk teks utama.
  - Gunakan `border-border` untuk garis pembatas.
- Pastikan kontras warna tetap nyaman di mata (harmonious) sesuai standar aksesibilitas.

## 2. Estetika Modal & Komponen
- **Backdrop**: Gunakan `backdrop-filter: blur(8px)` untuk semua modal agar terlihat premium.
- **Radius**: Gunakan radius yang lembut dan konsisten (minimal `16px` atau `20px` untuk komponen besar).
- **Shadow**: Gunakan bayangan yang lembut (`shadow-sm` atau `shadow-md` untuk elemen kecil, `shadow-2xl` untuk modal utama).
- **Spacing**: Pastikan padding dan margin konsisten menggunakan skala standard (e.g., `p-4`, `p-6`).

## 3. Micro-Animations & Interaction
- Tambahkan transisi halus (`transition-all`, `duration-300`) pada efek hover tombol dan kartu.
- Gunakan ikon yang konsisten (seperti Lucide) dengan ukuran yang proporsional.

## 4. Standarisasi Struktur Fitur
- Setiap fitur baru (misal: Master Dokter, Layanan, dll) **WAJIB** mengikuti pola folder dan penamaan file pada `pages/entry`:
  - `*ListPage.vue`: Untuk tampilan tabel/daftar data.
  - `*FormPage.vue`: Untuk tampilan form tambah/edit data.
  - `*ShowPage.vue`: Untuk tampilan detail data.
- Struktur kode di dalam file tersebut harus mengacu pada komponen dan logic yang sudah ada di folder `entry` sebagai standar kualitas.

## 5. Checklist Sebelum Penyerahan (Self-Audit)
- [ ] Apakah saya memakai warna hardcoded yang merusak tema?
- [ ] Apakah komponen ini sudah terlihat bagus baik di Light Mode MAUPUN Dark Mode?
- [ ] Apakah desain ini sudah terasa "Premium" dan "Wow", atau hanya sekadar fungsi saja?
- [ ] Apakah saya sudah mengikuti hierarki tipografi yang benar?

---
*Dibuat oleh Antigravity sebagai jaminan kualitas visual untuk Bapak.*
