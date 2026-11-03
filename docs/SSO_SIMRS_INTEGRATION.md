# Panduan Integrasi Single Sign-On (SSO) SIMRS & E-DOC TTE BSrE
**UOBK RSUD dr. Mohamad Saleh • Microservice TTE BSrE**

Dokumen ini menjelaskan cara mengkoneksikan dan membuka aplikasi **Tanda Tangan Elektronik (TTE) BSrE** langsung dari portal / menu **SIMRS** tanpa mengharuskan dokter, perawat, atau staf rumah sakit melakukan login berulang kali.

---

## 🌟 Ringkasan Alur & Perilaku SSO

1. **Akses dari SIMRS**: Ketika user membuka aplikasi TTE dari SIMRS (baik melalui Tab Baru, Deep-Link, maupun iFrame tersemat), identitas user (`nip`, `username`, atau `ticket`) otomatis diverifikasi dan langsung dialihkan ke **Dashboard Utama** dalam status terotentikasi.
2. **Akses Langsung (Tanpa SIMRS)**: Jika pengguna membuka URL `http://localhost:3000` langsung di browser tanpa parameter SSO dan belum memiliki sesi login aktif, sistem akan mengarahkan pengguna ke halaman **Login**.
3. **Sinkronisasi Otomatis Master Pegawai (JIT Provisioning)**: Jika dokter atau staf baru pertama kali masuk via SSO, microservice TTE secara otomatis membaca profil kepegawaian dari database MySQL riil SIMRS (`kepegx.pegawai` / `users`), mengimpor nama, NIP, NIK, dan menetapkan peran (`dokter`, `perawat`, `ppa`, `admin`), lalu membuatkan akun lokal PostgreSQL secara transparan.

---

## 🚀 4 Pilihan Metode Integrasi di SIMRS

Anda dapat memilih salah satu metode di bawah ini yang paling sesuai dengan arsitektur menu SIMRS Anda:

### 1. Metode 1: Tombol 1-Klik Redirect (Paling Cepat & Praktis)
Metode ini adalah cara paling sederhana. Di halaman portal atau menu SIMRS, cukup buat tautan / tombol yang mengarah ke endpoint redirect backend TTE:

#### Contoh HTML / Blade / PHP:
```html
<!-- Tombol Menu di SIMRS -->
<a 
  href="http://192.168.150.114:8005/api/v1/auth/sso/redirect?nip={{ $user->nip }}" 
  target="_blank" 
  class="btn btn-primary"
>
  <i class="fa fa-file-signature"></i> Buka Aplikasi TTE BSrE
</a>
```

#### Contoh JavaScript di Frontend SIMRS:
```javascript
function bukaAplikasiTTE(nipDokter) {
  const url = `http://192.168.150.114:8005/api/v1/auth/sso/redirect?nip=${encodeURIComponent(nipDokter)}`
  window.open(url, '_blank')
}
```

> **Cara Kerja:** Browser dokter akan memanggil backend TTE, token JWT instan digenerate, dan browser langsung di-redirect (HTTP 302) ke dashboard frontend TTE `http://192.168.150.114/#/?token=...`.

---

### 2. Metode 2: Direct URL Deep-Link (Frontend Hash)
SIMRS dapat langsung membuka frontend TTE dengan parameter query `nip`:

```javascript
// Membuka tab baru langsung ke frontend TTE
const nipDokter = '197804202014061001'
window.open(`http://192.168.150.114/#/?nip=${nipDokter}`, '_blank')
```

> **Cara Kerja:** Router guard frontend TTE otomatis mendeteksi parameter `?nip=...` atau `?sso_token=...`, melakukan pertukaran token dengan backend secara background, menyimpan token JWT ke `localStorage`, membersihkan URL dari query param, dan membuka Dashboard.

---

### 3. Metode 3: iFrame / Modal Dialog Tersemat (Seamless In-App)
Jika Anda ingin aplikasi TTE tampil di dalam pop-up modal atau halaman iframe di dalam SIMRS:

```html
<!-- Container iFrame di SIMRS -->
<div class="tte-modal-container">
  <iframe 
    id="iframeTte" 
    src="http://192.168.150.114/#/" 
    style="width: 100%; height: 85vh; border: none; border-radius: 8px;"
  ></iframe>
</div>

<script>
  const iframe = document.getElementById('iframeTte')
  iframe.onload = function() {
    // Kirim pesan postMessage otorisasi SSO ke dalam iFrame
    iframe.contentWindow.postMessage({
      type: 'SIMRS_SSO_AUTH',
      nip: '197804202014061001' // NIP Dokter yang sedang login di SIMRS
    }, '*')
  }
</script>
```

---

### 4. Metode 4: Enterprise Secure One-Time Ticket (Sangat Aman)
Untuk keamanan tingkat enterprise di mana NIP tidak ingin diekspos di URL publik:

1. **Backend SIMRS (Laravel / PHP / NodeJS)** meminta tiket SSO sekali pakai ke backend TTE:
```php
// Di Controller SIMRS (PHP/Laravel)
use Illuminate\Support\Facades\Http;

public function openTteSso(Request $request)
{
    $nip = auth()->user()->nip;
    
    // Request One-Time Ticket ke Microservice TTE (berlaku 5 menit)
    $response = Http::post('http://192.168.150.114:8005/api/v1/auth/sso/ticket', [
        'nip' => $nip,
        'expires_in_seconds' => 300
    ]);

    if ($response->successful()) {
        $ssoUrl = $response->json()['sso_url']; // contoh: http://192.168.150.114/#/?sso_ticket=tick_xxxx
        return redirect($ssoUrl);
    }
    
    return back()->with('error', 'Gagal membuat tiket SSO TTE');
}
```

2. Tiket `tick_xxxx` hanya dapat digunakan **1 kali**. Begitu frontend TTE menukarkannya dengan token JWT, tiket tersebut langsung dimusnahkan sehingga tidak bisa disalahgunakan oleh pihak lain.

---

## 🧪 Uji Coba SSO yang Sudah Berjalan

Daftar endpoint yang telah terpasang dan siap digunakan:

| Endpoint | Method | Deskripsi |
| :--- | :--- | :--- |
| `/api/v1/auth/sso/redirect?nip={nip}` | `GET` | 1-Klik redirect dari SIMRS langsung ke dashboard frontend TTE |
| `/api/v1/auth/sso/ticket` | `POST` | Menghasilkan one-time secure ticket untuk backend SIMRS |
| `/api/v1/auth/sso-login` | `POST` | Endpoint pertukaran identitas SSO (`sso_ticket`, `sso_token`, atau `nip`) |
| `http://192.168.150.114/#/?nip={nip}` | `GET` | Direct deep-link frontend dengan auto-login transparan |
