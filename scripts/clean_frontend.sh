#!/usr/bin/env bash
set -e

echo "=== Membersihkan Halaman Starter-Kit yang Tidak Digunakan ==="
cd "$(dirname "$0")/../frontend"
rm -rf src/pages/dokter src/pages/entry src/pages/layanan src/pages/spesialis src/components/public src/components/charts
echo "✓ Frontend cleaned. Modular widgets and SIMRS pages preserved."
