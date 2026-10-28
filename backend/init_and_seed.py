import sys
import os

# Tambahkan direktori backend ke sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import init_db
from database.seeders.db_seeder import seed_database

if __name__ == "__main__":
    print("Memulai inisialisasi tabel dan extension pgvector...")
    init_db()
    print("Memulai seeding data pengguna dan sample Lembar Konsultasi SIMRS...")
    seed_database()
    print("Selesai! Database siap digunakan.")
