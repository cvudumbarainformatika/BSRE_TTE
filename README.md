# SIMRS TTE BSRE Microservice 🏥🔏

Microservice modern untuk pengelolaan dokumen medis rumah sakit dengan dukungan penuh **Tanda Tangan Elektronik (TTE) BSRE BSSN**, **Otomatisasi Dokumen SIMRS (Tanpa Upload Manual)**, **TTE Banyak Dokumen Sekaligus (Batch Sign)**, pemindaian antivirus **ClamAV**, pencarian kemiripan semantik **pgvector**, jejak audit (*audit trail*), serta retensi 5 tahun sesuai regulasi rekam medis Indonesia (**Permenkes No. 24 Tahun 2022**).

---

## 📑 Daftar Isi
1. [Prinsip Kerja Dokumen SIMRS: Otomatis Tanpa Upload Manual](#prinsip-kerja-dokumen-simrs-otomatis-tanpa-upload-manual)
2. [Fitur Batch Sign (TTE Puluhan Dokumen Sekaligus)](#fitur-batch-sign-tte-puluhan-dokumen-sekaligus)
3. [Arsitektur & Tech Stack](#arsitektur--tech-stack)
4. [Struktur Folder (Laravel-Style Backend)](#struktur-folder-laravel-style-backend)
5. [Komponen Widget Frontend (`src/widgets/`)](#komponen-widget-frontend-srcwidgets)
6. [Integrasi dengan SIMRS-V3](#integrasi-dengan-simrs-v3)
7. [Cara Menjalankan dengan Docker](#cara-menjalankan-dengan-docker)
8. [Akun Bawaan & Skenario Pengujian](#akun-bawaan--skenario-pengujian)

---

## ⚡ Prinsip Kerja Dokumen SIMRS: Otomatis Tanpa Upload Manual

Sesuai alur operasional nyata di rumah sakit:
> **Dokter dan tenaga medis TIDAK PERLU mengunggah file PDF secara manual.**

Ketika dokumen medis diterbitkan di SIMRS (seperti **Surat Keterangan Kematian**, **Lembar Konsultasi Spesialis**, **Resume Medis**, atau **Informed Consent**):
1. **Otomatis Dibuat**: Sistem SIMRS memanggil endpoint `/api/v1/simrs/auto-ingest` mengirimkan data rekam medis.
2. **Otomatis Di-generate ke PDF Resmi**: Microservice mengubah data menjadi PDF berformat resmi RSUD Dokter Mohammad Saleh lengkap dengan Nomor Surat, Identitas Jenazah/Pasien, dan area tanda tangan elektronik.
3. **Target Penandatangan Ditentukan**: Dokumen otomatis diarahkan ke NIP/NIK dokter yang berwenang (misal: 30 dokumen Surat Kematian ditujukan untuk User A / dr. Rizki Habibie).
4. **Notifikasi Otomatis Terkirim**: Dokter yang dituju menerima notifikasi in-app dan counter merah di lonceng navbar: *"Terdapat 30 dokumen Surat Kematian baru yang belum Anda tandatangani"*.

---

## 🚀 Fitur Batch Sign (TTE Puluhan Dokumen Sekaligus)

Dokter yang memiliki antrean puluhan atau ratusan dokumen tidak perlu menandatangani dokumen satu per satu:

1. **Buka Tab "Inbox TTE Saya"**:
   Dokter melihat daftar dokumen miliknya yang menunggu TTE (misal 30 Surat Kematian).
2. **Pilih Semua (Select All)**:
   Cukup klik checkbox *"Pilih Semua Dokumen di Tampilan Ini (30)"*.
3. **Klik "Tanda Tangani Sekaligus (Batch Sign)"**:
   Muncul modal otorisasi PIN / Passphrase BSRE.
4. **Masukkan PIN 1 Kali**:
   Dokter memasukkan PIN BSRE 1 kali saja.
5. **Semua Dokumen Sah Ber-TTE Sekaligus**:
   - Sistem secara serempak menyematkan visual stamp & QR Code verifikasi resmi BSRE BSSN pada seluruh 30 dokumen.
   - Seluruh dokumen memiliki **tanggal dan jam penandatanganan yang seragam pada saat itu**.
   - Integritas hash SHA-256 dan jejak audit (*audit trail*) tercatat otomatis untuk setiap dokumen.
   - Notifikasi antrean otomatis berkurang / ditandai selesai.

---

## 🏛️ Arsitektur & Tech Stack

```
+-----------------------------------------------------------------------------------+
|                            SIMRS-V3 Frontend (Quasar)                             |
|  +-----------------------------------------------------------------------------+  |
|  |   Widgets: PendingTteInbox (Batch Sign), SimrsDocWidget, List, Viewer       |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST (JWT Auth)
                                           v
+-----------------------------------------------------------------------------------+
|                        FastAPI Microservice (Python 3.11)                         |
|  - Laravel-Style MVC/Service Architecture                                         |
|  - Batch Signing Engine (Penandatanganan Massal TTE BSRE)                         |
|  - Notification Engine (Tracking Dokumen Belum Di-TTE per NIP Dokter)             |
|  - Automated PDF Engine (Surat Kematian, Lembar Konsultasi, Resume Medis)         |
|  - SlowAPI Rate Limiter & Helmet Security Headers                                 |
+---------------------+-------------------------------+-----------------------------+
                      |                               |
                      v                               v
       +-------------------------------+   +--------------------+
       | PostgreSQL 16 + pgvector      |   | ClamAV Daemon      |
       | - SQL-Standard Tables         |   | - Antivirus Stream |
       | - Vector(1536) Embeddings     |   +--------------------+
       | - Audit Trails & Retensi 5 Th |
       +-------------------------------+
```

---

## 📂 Struktur Folder (Laravel-Style Backend)

```
backend/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── AuthController.py         # Login, register, profile
│   │   │   ├── DocumentController.py     # Upload, list, view, approve
│   │   │   ├── TteBsreController.py      # Batch Sign massal & single sign TTE BSRE
│   │   │   ├── NotificationController.py # Notifikasi dokumen pending TTE per dokter
│   │   │   ├── SimrsIngestController.py  # Automated Ingest dokumen dari SIMRS
│   │   │   └── AuditController.py        # Jejak audit trail dokumen
│   │   ├── Middleware/
│   │   │   ├── AuthMiddleware.py         # JWT Token decoder & RBAC dependency
│   │   │   ├── RateLimitMiddleware.py    # SlowAPI configuration
│   │   │   └── SecurityHeadersMiddleware.py # Helmet security headers
│   │   └── Requests/
│   │       ├── AuthRequest.py            # DTO validasi login
│   │       └── DocumentRequests.py       # DTO validasi Batch Sign & SIMRS Ingest
│   ├── Models/
│   │   ├── User.py                       # Model user & NIP dokter
│   │   ├── Document.py                   # Model dokumen (target_signer_nip, pgvector 1536)
│   │   ├── Notification.py               # Model notifikasi dokumen pending TTE
│   │   └── DocumentAuditLog.py           # Model audit log & riwayat sertifikat BSRE
│   ├── Repositories/
│   │   ├── DocumentRepository.py         # SQL query, pagination, filter, vector cosine search
│   │   └── AuditRepository.py            # Query jejak audit
│   └── Services/
│       ├── PdfGeneratorService.py        # Generator PDF Surat Kematian & Konsul RSUD
│       ├── BsreTteService.py             # Integrasi TTE BSRE BSSN, QR code & stamping
│       ├── VirusScanService.py           # Scanner antivirus ClamAV
│       ├── VectorSearchService.py        # Generator vektor embedding 1536-dimensi
│       └── AuditService.py               # Dispatcher audit log terpusat
├── config/
│   ├── settings.py                       # Environment variable & app configuration
│   └── database.py                       # SQLModel engine & pgvector initialization
├── database/
│   └── seeders/
│       └── db_seeder.py                  # Seeder 80 dokumen otomatis (30 surat kematian dr_rizki)
├── routes/
│   └── api.py                            # Aggregator routing /api/v1/...
├── storage/
│   └── app/
│       ├── documents/                    # File PDF permanen
│       └── qr_codes/                     # File gambar QR Code verifikasi
├── main.py                               # Entrypoint ASGI application
├── requirements.txt
└── Dockerfile
```

---

## 🧩 Komponen Widget Frontend (`src/widgets/`)

Widget dirancang modular, independen, dan siap ditanamkan ke dalam project SIMRS:

### 1. `PendingTteInbox.vue` (Batch Sign Widget)
- Menampilkan antrean dokumen yang otomatis terbit dari SIMRS milik dokter yang sedang login.
- Tabs kategori: *"Semua (50)"*, *"Surat Kematian (30)"*, *"Konsul Spesialis (20)"*.
- Checkbox **"Pilih Semua Dokumen"**.
- Tombol **"Tanda Tangani Sekaligus (Batch Sign)"**: meminta PIN BSRE 1 kali dan men-sign seluruh dokumen terpilih serentak pada tanggal/jam tersebut.
- Contoh penggunaan:
  ```vue
  <template>
    <PendingTteInbox
      @preview-doc="openPreviewModal"
      @batch-signed="onBatchSuccess"
    />
  </template>

  <script setup>
  import { PendingTteInbox } from '@/widgets'
  </script>
  ```

### 2. `SimrsDocWidget.vue`
- Menampilkan tampilan visual lembar konsultasi rawat inap persis seperti pada screenshot antarmuka RSUD Dokter Mohammad Saleh.
- Tombol **"Cetak Dokumen"** langsung mengirimkan data rekam medis ke backend untuk membuat PDF resmi dan ber-TTE BSRE.

### 3. `DocumentList.vue`
- Tabel data seluruh dokumen dengan filter status TTE BSRE, pencarian instan, dan pagination.
- Tombol aksi: *View PDF*, *Unduh*, *Sign BSRE*, *Cek Sertifikat BSRE*, *Approve*.

### 4. `DocumentViewer.vue`
- Viewer inline PDF dengan tombol cetak langsung (`window.print()`), badge verifikasi sertifikat BSRE, dan tab jejak audit (*audit trail*).

---

## 🔄 Integrasi dengan SIMRS-V3

### Contoh Memanggil Otomatisasi Saat SIMRS Menerbitkan Surat Kematian:
Saat petugas atau dokter selesai menginput data kematian di SIMRS, backend SIMRS cukup menembakkan payload ke microservice ini:
```javascript
import api from '@/services/api'

// Dipanggil otomatis saat form kematian disimpan di SIMRS
await api.post('/simrs/auto-ingest', {
  kunjungan_id: 50001,
  pasien_id: 280001,
  document_type: 'surat_kematian',
  title: 'Surat Keterangan Kematian - Tn. Ahmad',
  target_signer_nip: '198304152011011003', // NIP Dokter Penandatangan (User A)
  target_signer_name: 'dr. RIZKI HABIBIE, Sp.PD.',
  content_data: {
    nomor_surat: '474.3/50001/425.208/2026',
    tgl_meninggal: 'Senin, 26 Oktober 2026',
    jam_meninggal: '04:15 WIB',
    tempat_meninggal: 'Ruang Flamboyan',
    pasien: {
      nama: 'Tn. Ahmad',
      norm: '280001',
      usia: '62 Tahun',
      kelamin: 'Laki-laki',
      alamat: 'Kota Probolinggo'
    },
    penyebab_langsung: 'Cardiorespiratory Failure',
    penyebab_antara: 'Septic Shock',
    penyebab_dasar: 'Pneumonia Akut'
  },
  notify_user: true
})
```
Dokumen langsung otomatis tercipta, berformat PDF resmi RSUD, dan masuk ke antrean Batch TTE dokter yang bersangkutan!

---

## 🐳 Cara Menjalankan dengan Docker

```bash
cd /Users/it/Developer/www/BSRE_TTE

# 1. Jalankan seluruh container stack
docker compose up -d --build

# 2. Jalankan seeder 80 dokumen otomatis & akun pengujian
docker compose exec backend python init_and_seed.py
```
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👤 Akun Bawaan & Skenario Pengujian

Sesuai skenario yang Anda minta:
- Total ada **80 Dokumen di SIMRS**:
  - **User A (`dr_rizki`)**: memiliki **30 dokumen Surat Kematian** + **20 Lembar Konsultasi** yang belum ditandatangani. Muncul notifikasi counter **30** di lonceng header.
  - **User B (`dr_elieza`)**: memiliki **30 dokumen Surat Kematian Ruang Melati** miliknya.
- Begitu User A login dan membuka tab **"Inbox TTE Saya"**, User A dapat mencentang ke-30 dokumennya dan menekan **"Tanda Tangani Sekaligus"**. Seluruh 30 dokumen langsung berstatus `SIGNED_BSRE` pada tanggal dan jam tersebut!

| Role | Username | Password | Skenario Antrean TTE |
| :--- | :--- | :--- | :--- |
| **User A (Dokter)** | `dr_rizki` | `password123` | NIP: 198304152011011003. Memiliki **30 Surat Kematian & 20 Konsul** siap Batch Sign. |
| **User B (Dokter)** | `dr_elieza` | `password123` | NIP: 198506122014022001. Memiliki **30 Surat Kematian Pediatrik** miliknya. |
| **Petugas Ruangan** | `perawat_dinda` | `password123` | NIP: 199405122020122008. Input pelayanan SIMRS. |
| **Admin** | `admin` | `password123` | Administrator sistem & audit trail. |
