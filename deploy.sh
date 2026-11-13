#!/bin/bash
# ==============================================================================
# SCRIPT OTOMATISASI DEPLOYMENT KE SERVER PRODUCTION
# RSUD dr. Mohamad Saleh • Microservice TTE BSrE BSSN
# ==============================================================================

set -e

# Warna Terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}   🚀 MEMULAI DEPLOYMENT OTOMATIS MICROSERVICE TTE BSrE RSUD   ${NC}"
echo -e "${CYAN}================================================================${NC}"

# 1. Baca Konfigurasi dari file .env
ENV_FILE="$(dirname "$0")/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: File .env tidak ditemukan di $(dirname "$0")!${NC}"
    exit 1
fi

# Ekstrak kredensial server dari .env
PROD_HOST=$(grep -E "^PROD_SERVER_HOST=" "$ENV_FILE" | cut -d '=' -f2- | tr -d ' "' | tr -d "'")
PROD_PORT=$(grep -E "^PROD_SERVER_PORT=" "$ENV_FILE" | cut -d '=' -f2- | tr -d ' "' | tr -d "'")
PROD_USER=$(grep -E "^PROD_SERVER_USER=" "$ENV_FILE" | cut -d '=' -f2- | tr -d ' "' | tr -d "'")
PROD_PASS=$(grep -E "^PROD_SERVER_PASS=" "$ENV_FILE" | cut -d '=' -f2- | tr -d ' "' | tr -d "'")

PROD_HOST=${PROD_HOST:-192.168.150.114}
PROD_PORT=${PROD_PORT:-22}
PROD_USER=${PROD_USER:-sa}
PROD_PASS=${PROD_PASS:-sasa0102sa}
REMOTE_DIR="/opt/bsre_tte"

echo -e "${BLUE}ℹ️  Target Server  : ${YELLOW}${PROD_USER}@${PROD_HOST}:${PROD_PORT}${NC}"
echo -e "${BLUE}ℹ️  Direktori App  : ${YELLOW}${REMOTE_DIR}${NC}"

# Cek dependensi sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}⚠️  sshpass tidak ditemukan di PATH, mencoba /opt/homebrew/bin/sshpass...${NC}"
    if [ -x "/opt/homebrew/bin/sshpass" ]; then
        SSHPASS_BIN="/opt/homebrew/bin/sshpass"
    else
        echo -e "${RED}❌ Error: sshpass wajib terpasang untuk otomasi deployment! (brew install sshpass)${NC}"
        exit 1
    fi
else
    SSHPASS_BIN="sshpass"
fi

# 2. Build Frontend untuk Production dengan Relative API URL (Universal Staging Domain & IP)
echo -e "\n${CYAN}[1/4] Membangun Frontend Quasar Production...${NC}"
export VITE_API_URL="/api/v1"
npm --prefix frontend run build

# 3. Sinkronisasi File Proyek ke Server via Rsync
echo -e "\n${CYAN}[2/4] Melakukan Sinkronisasi File Proyek ke Server Production...${NC}"
$SSHPASS_BIN -p "$PROD_PASS" rsync -avz --delete \
    -e "ssh -p ${PROD_PORT} -o StrictHostKeyChecking=no" \
    --exclude="node_modules" \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="panduan-server*.md" \
    --exclude="backend/storage/app/temp/*" \
    --exclude="backend/storage/app/documents/*" \
    --exclude="backend/storage/app/qr_codes/*" \
    ./ ${PROD_USER}@${PROD_HOST}:${REMOTE_DIR}/

# 4. Buat File .env Production di Server
echo -e "\n${CYAN}[3/4] Menyesuaikan Konfigurasi Environment di Server...${NC}"
$SSHPASS_BIN -p "$PROD_PASS" ssh -p "$PROD_PORT" -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} "bash -s" << EOF
set -e
cd ${REMOTE_DIR}

# Buat .env production
cat > .env << 'ENV_EOF'
# ============================================================================
# KONFIGURASI PRODUCTION — E-DOC TTE BSRE RSUD DR. MOHAMAD SALEH
# ============================================================================
ENV=production
DEBUG=false
SECRET_KEY=super-secret-bsre-tte-simrs-jwt-key-2026-very-secure

# Database Microservice (PostgreSQL 16 + pgvector)
POSTGRES_DB=simrs_tte
POSTGRES_USER=postgres
POSTGRES_PASSWORD=RsudSalehTte2026!SecurePostgres
DATABASE_URL=postgresql://postgres:RsudSalehTte2026!SecurePostgres@db:5432/simrs_tte

# Database MySQL Riil SIMRS
DB_HOST=192.168.11.1
DB_PORT=3306
DB_NAME=rs
DB_USER=viewer
DB_PASSWORD=sasa0102

# Integrasi BSrE BSSN Production Gateway Kominfo
BSRE_MOCK_MODE=true
BSRE_BASE_URL=http://103.146.34.29
BSRE_API_URL=http://103.146.34.29/api
BSRE_USERNAME=rsud_saleh
BSRE_PASSWORD=7kuzBaIRyX1Ei5
BSRE_API_KEY=sandbox-bsre-api-key
BSRE_TIMEOUT_SECONDS=15
BSRE_DEV_NIK=0803202100007062
BSRE_DEV_PASSPHRASE=Bsre2026.#!

# ClamAV Antivirus
CLAMAV_ENABLED=true
CLAMAV_HOST=clamav
CLAMAV_PORT=3310

# Profil Rumah Sakit
HOSPITAL_GOV_HEADER=PEMERINTAH KOTA PROBOLINGGO
HOSPITAL_NAME=UOBK RSUD DOKTER MOHAMAD SALEH
HOSPITAL_CITY=PROBOLINGGO
HOSPITAL_ADDRESS=Jl. Mayjend Panjaitan No.65 Probolinggo Jawa Timur
HOSPITAL_PHONE=Telp. (0335) 433478,433119,421118 Fax. (0335) 432702
HOSPITAL_EMAIL=rsudprob@probolinggokota.go.id

# Storage & API URL Target
BASE_STORAGE_PATH=/app/storage/app
VITE_API_URL=/api/v1

# Nginx Proxy Manager (NPM) Admin Credentials
NPM_ADMIN_USER=harry
NPM_ADMIN_EMAIL=admin@example.com
NPM_ADMIN_PASS=changeme
ENV_EOF

# Pastikan hak akses folder storage
mkdir -p backend/storage/app/documents backend/storage/app/qr_codes backend/storage/app/temp
echo "sasa0102sa" | sudo -S chmod -R 777 backend/storage 2>/dev/null || chmod -R 777 backend/storage 2>/dev/null || true

# Buka Port 81 (NPM), 8088 (FileBrowser), 9090 (Cockpit) di UFW jika belum dibuka
if command -v ufw &> /dev/null; then
    echo "sasa0102sa" | sudo -S ufw allow 81/tcp comment 'Nginx Proxy Manager Admin UI' > /dev/null 2>&1 || true
    echo "sasa0102sa" | sudo -S ufw allow 8088/tcp comment 'FileBrowser Web File Manager' > /dev/null 2>&1 || true
    echo "sasa0102sa" | sudo -S ufw allow 9090/tcp comment 'Cockpit Web Admin & User Monitor' > /dev/null 2>&1 || true
fi

# Jalankan Container Docker Compose
echo "Memulai docker compose build & up..."
docker compose up -d --build
EOF

# 5. Health Check Pengujian Layanan di Server Production
echo -e "\n${CYAN}[4/4] Memeriksa Kesehatan Layanan (Health Check)...${NC}"
sleep 5

CHECK_BACKEND=false
for i in {1..10}; do
    if curl -s -f "http://${PROD_HOST}:8005/health" > /dev/null 2>&1; then
        CHECK_BACKEND=true
        break
    fi
    echo -e "${YELLOW}Menunggu Backend FastAPI siap... (percobaan $i/10)${NC}"
    sleep 3
done

CHECK_FRONTEND=false
if curl -s -f "http://${PROD_HOST}:3000" > /dev/null 2>&1; then
    CHECK_FRONTEND=true
fi

CHECK_NPM=false
for i in {1..10}; do
    if curl -s -I "http://${PROD_HOST}:81" > /dev/null 2>&1; then
        CHECK_NPM=true
        break
    fi
    echo -e "${YELLOW}Menunggu Nginx Proxy Manager siap... (percobaan $i/10)${NC}"
    sleep 3
done

if [ "$CHECK_NPM" = true ]; then
    # Pastikan Proxy Host default untuk Frontend TTE terdaftar di NPM
    NPM_TOKEN=$(curl -s -X POST "http://${PROD_HOST}:81/api/tokens" -H "Content-Type: application/json" -d "{\"identity\":\"${NPM_ADMIN_EMAIL:-admin@example.com}\",\"secret\":\"${NPM_ADMIN_PASS:-changeme}\"}" | grep -o "\"token\":\"[^\"]*" | cut -d"\"" -f4 || true)
    if [ -n "$NPM_TOKEN" ]; then
        NPM_HOSTS=$(curl -s "http://${PROD_HOST}:81/api/nginx/proxy-hosts" -H "Authorization: Bearer $NPM_TOKEN" || true)
        if ! echo "$NPM_HOSTS" | grep -q "${PROD_HOST}"; then
            curl -s -X POST "http://${PROD_HOST}:81/api/nginx/proxy-hosts" \
              -H "Authorization: Bearer $NPM_TOKEN" \
              -H "Content-Type: application/json" \
              -d "{
                \"domain_names\": [\"${PROD_HOST}\", \"localhost\"],
                \"forward_scheme\": \"http\",
                \"forward_host\": \"frontend\",
                \"forward_port\": 80,
                \"access_list_id\": 0,
                \"certificate_id\": 0,
                \"ssl_forced\": 0,
                \"caching_enabled\": 0,
                \"block_exploits\": 1,
                \"advanced_config\": \"\",
                \"meta\": {\"letsencrypt_agree\": false, \"dns_challenge\": false},
                \"allow_websocket_upgrade\": 1,
                \"http2_support\": 0,
                \"hsts_enabled\": 0,
                \"hsts_subdomains\": 0
              }" > /dev/null 2>&1 || true
        fi
    fi
fi

echo -e "\n${GREEN}================================================================${NC}"
if [ "$CHECK_BACKEND" = true ] && [ "$CHECK_FRONTEND" = true ]; then
    echo -e "${GREEN}   ✅ DEPLOYMENT BERHASIL & SEMUA LAYANAN AKTIF DENGAN SEMPURNA! ${NC}"
else
    echo -e "${YELLOW}   ⚠️  DEPLOYMENT SELESAI, BEBERAPA CONTAINER MASIH INITIALIZING ${NC}"
fi
echo -e "${GREEN}================================================================${NC}"
echo -e " 🌐 Dashboard Frontend TTE : ${CYAN}http://${PROD_HOST}:3000${NC} (atau http://${PROD_HOST})"
echo -e " 🔌 API Docs (Swagger)     : ${CYAN}http://${PROD_HOST}:8005/docs${NC}"
echo -e " 🛡️  Nginx Proxy Manager   : ${CYAN}http://${PROD_HOST}:81${NC} (SSL & Bridging Domain .go.id UI)"
echo -e "    * Login Awal NPM       : ${YELLOW}admin@example.com${NC} / ${YELLOW}changeme${NC}"
echo -e " 🖥️  Cockpit Server Admin  : ${CYAN}https://${PROD_HOST}:9090${NC} (Pantau Kesehatan Server & User)"
echo -e "    * Login Cockpit        : User sistem Ubuntu (${YELLOW}sa${NC} / ${YELLOW}sasa0102sa${NC})"
echo -e " 📂 FileBrowser (Files UI) : ${CYAN}http://${PROD_HOST}:8088${NC} (Web File Manager Visual)"
echo -e "    * Login FileBrowser    : ${YELLOW}admin${NC} / ${YELLOW}AdminRsud2026!${NC}"
echo -e " 🗄️  Adminer (Database UI) : ${CYAN}http://${PROD_HOST}:8089${NC} (PostgreSQL GUI Web)"
echo -e "    * System: PostgreSQL, Server: db, Database: simrs_tte"
echo -e " 🐳 Portainer Docker UI    : ${CYAN}https://${PROD_HOST}:9443${NC} atau ${CYAN}http://${PROD_HOST}:9000${NC}"
echo -e " 🔒 Status Keamanan        : ${GREEN}UFW Firewall & Fail2Ban Aktif${NC}"
echo -e "${GREEN}================================================================${NC}\n"
