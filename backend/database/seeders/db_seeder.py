import os
import json
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from config.database import engine, init_db
from config.settings import settings
from app.Models.User import User, UserRole
from app.Models.Document import Document
from app.Models.DocumentAuditLog import TteSignature, DocumentTemplate
from app.Models.Notification import UserNotification
from app.Http.Middleware.AuthMiddleware import get_password_hash
from app.Services.PdfGeneratorService import pdf_service
from app.Services.BsreTteService import bsre_service
from app.Services.VectorSearchService import vector_service

def seed_database():
    init_db()
    
    with Session(engine) as db:
        # 1. Seed Users (dr_rizki sebagai User A, dr_elieza sebagai User B, perawat, ppa, admin)
        users_data = [
            {
                "username": "dr_rizki",
                "nama": "dr. RIZKI HABIBIE, Sp.PD.",
                "nip": "198304152011011003",
                "nik": "0803202100007062",
                "email": "dr.rizki@rsudmohammadsaleh.id",
                "role": UserRole.DOKTER,
                "password": "password123"
            },
            {
                "username": "dr_elieza",
                "nama": "dr. ELIEZA, Sp.A.",
                "nip": "198506122014022001",
                "nik": "3574011206850003",
                "email": "dr.elieza@rsudmohammadsaleh.id",
                "role": UserRole.DOKTER,
                "password": "password123"
            },
            {
                "username": "perawat_dinda",
                "nama": "EFI DINDA MELASIH PRIHATINI, A.Md.Kep.",
                "nip": "199405122020122008",
                "nik": "3574021205940001",
                "email": "dinda.perawat@rsudmohammadsaleh.id",
                "role": UserRole.PERAWAT,
                "password": "password123"
            },
            {
                "username": "ppa_budi",
                "nama": "Budi Santoso, S.Tr.Kes.",
                "nip": "199008202018031005",
                "nik": "3574032008900004",
                "email": "budi.ppa@rsudmohammadsaleh.id",
                "role": UserRole.PPA,
                "password": "password123"
            },
            {
                "username": "admin",
                "nama": "Administrator Sistem RSUD",
                "nip": "198801012015011001",
                "nik": "3574010101880001",
                "email": "admin.simrs@rsudmohammadsaleh.id",
                "role": UserRole.ADMIN,
                "password": "password123"
            }
        ]

        created_users = {}
        for u in users_data:
            exist = db.exec(select(User).where(User.username == u["username"])).first()
            if not exist:
                user = User(
                    username=u["username"],
                    nama=u["nama"],
                    nip=u["nip"],
                    nik=u["nik"],
                    email=u["email"],
                    role=u["role"],
                    hashed_password=get_password_hash(u["password"])
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                created_users[u["username"]] = user
            else:
                if exist.nik != u["nik"]:
                    exist.nik = u["nik"]
                    db.add(exist)
                    db.commit()
                    db.refresh(exist)
                created_users[u["username"]] = exist

        print("✓ Users seeded successfully.")

        # 2. Seed Templates
        templates = [
            {"code": "surat_kematian", "name": "Surat Keterangan Kematian", "category": "administrasi"},
            {"code": "konsul_spesialis", "name": "Lembar Konsultasi Dokter Spesialis", "category": "medis"},
            {"code": "resume_medis", "name": "Ringkasan Pulang (Resume Medis)", "category": "medis"}
        ]
        for t in templates:
            exist = db.exec(select(DocumentTemplate).where(DocumentTemplate.code == t["code"])).first()
            if not exist:
                tmpl = DocumentTemplate(**t)
                db.add(tmpl)
        db.commit()

        # 3. Skenario Nyata User:
        # Total 80 Dokumen Surat Kematian di RS, 30 Dokumen milik User A (dr_rizki), 30 milik User B (dr_elieza)
        # Serta 20 Lembar Konsultasi Spesialis milik dr_rizki.
        # Dokumen otomatis di-generate tanpa upload manual!
        
        dr_a = created_users.get("dr_rizki")
        dr_b = created_users.get("dr_elieza")
        uploader_id = created_users.get("perawat_dinda").id

        existing_kematian = db.exec(select(Document).where(Document.document_type == "surat_kematian")).all()
        if len(existing_kematian) < 60:
            print("⏳ Menghasilkan 80 dokumen otomatis dari SIMRS (30 Surat Kematian dr_rizki, 30 dr_elieza, 20 Konsul)...")
            doc_base_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", "batch_simrs")
            os.makedirs(doc_base_dir, exist_ok=True)

            # Buat 30 Surat Kematian untuk User A (dr_rizki)
            for i in range(1, 31):
                norm = 280000 + i
                noreg = 50000 + i
                nama_pasien = f"Jenazah Pasien Kasus #{i} (Ranap Flamboyan)"
                pdf_filename = f"KEMATIAN_{noreg}_{norm}_AUTO.pdf"
                pdf_path = os.path.join(doc_base_dir, pdf_filename)

                simrs_payload = {
                    "kunjungan_id": noreg,
                    "nomor_surat": f"474.3/{noreg}/425.208/2026",
                    "tgl_meninggal": (datetime.now() - timedelta(days=i % 5)).strftime("%A, %d %B %Y"),
                    "jam_meninggal": f"{8 + (i % 12):02d}:{15 + (i % 40):02d} WIB",
                    "tempat_meninggal": "Ruang Rawat Inap Flamboyan, RSUD dr. Moh. Saleh",
                    "pasien": {
                        "nama": nama_pasien,
                        "norm": str(norm),
                        "tgllahir": "1965-05-12",
                        "usia": f"{55 + (i % 25)} Tahun",
                        "kelamin": "Laki-laki" if i % 2 == 0 else "Perempuan",
                        "alamat": f"Kel. Kebonsari Kulon No. {i}, Kota Probolinggo"
                    },
                    "penyebab_langsung": "Cardiorespiratory Failure" if i % 2 == 0 else "Septic Shock",
                    "penyebab_antara": "Pneumonia Akut + Severe Sepsis",
                    "penyebab_dasar": "Chronic Kidney Disease Stage V" if i % 3 == 0 else "Cardiovascular Disease",
                    "dokter": {
                        "nama": dr_a.nama,
                        "nip": dr_a.nip
                    }
                }

                pdf_service.generate_surat_kematian_pdf(simrs_payload, pdf_path)
                fsize = os.path.getsize(pdf_path)
                fhash = bsre_service.calculate_file_hash(pdf_path)
                embed = vector_service.generate_embedding(f"{nama_pasien} Surat Kematian {simrs_payload['penyebab_langsung']}")

                doc = Document(
                    kunjungan_id=noreg,
                    pasien_id=norm,
                    document_type="surat_kematian",
                    title=f"Surat Keterangan Kematian - {nama_pasien}",
                    filename=pdf_filename,
                    storage_path=pdf_path,
                    original_path="SIMRS_AUTO_INGEST",
                    uploaded_by=uploader_id,
                    uploaded_at=datetime.now(timezone.utc) - timedelta(hours=i),
                    status="pending",
                    description=f"Surat Kematian diterbitkan SIMRS untuk ditandatangani oleh {dr_a.nama}",
                    file_size=fsize,
                    target_signer_nip=dr_a.nip,
                    target_signer_name=dr_a.nama,
                    tte_status="UNSIGNED",
                    pdf_hash=fhash,
                    metadata_json=json.dumps(simrs_payload),
                    embedding=embed
                )
                db.add(doc)

            # Buat 30 Surat Kematian untuk User B (dr_elieza)
            for j in range(31, 61):
                norm = 280000 + j
                noreg = 50000 + j
                nama_pasien = f"Jenazah Pasien Kasus #{j} (Pediatrik)"
                pdf_filename = f"KEMATIAN_{noreg}_{norm}_AUTO.pdf"
                pdf_path = os.path.join(doc_base_dir, pdf_filename)

                simrs_payload = {
                    "kunjungan_id": noreg,
                    "nomor_surat": f"474.3/{noreg}/425.208/2026",
                    "tgl_meninggal": (datetime.now() - timedelta(days=j % 4)).strftime("%A, %d %B %Y"),
                    "jam_meninggal": f"{10 + (j % 10):02d}:{20 + (j % 30):02d} WIB",
                    "tempat_meninggal": "Ruang Rawat Inap Melati (Anak), RSUD dr. Moh. Saleh",
                    "pasien": {
                        "nama": nama_pasien,
                        "norm": str(norm),
                        "tgllahir": "2018-02-14",
                        "usia": "8 Tahun",
                        "kelamin": "Perempuan",
                        "alamat": "Jl. Basuki Rahmat, Kota Probolinggo"
                    },
                    "penyebab_langsung": "Encephalopathy Sepsis",
                    "penyebab_antara": "Severe Dengue Shock Syndrome",
                    "penyebab_dasar": "Dengue Hemorrhagic Fever",
                    "dokter": {
                        "nama": dr_b.nama,
                        "nip": dr_b.nip
                    }
                }

                pdf_service.generate_surat_kematian_pdf(simrs_payload, pdf_path)
                fsize = os.path.getsize(pdf_path)
                fhash = bsre_service.calculate_file_hash(pdf_path)
                embed = vector_service.generate_embedding(f"{nama_pasien} Surat Kematian Pediatrik dr Elieza")

                doc = Document(
                    kunjungan_id=noreg,
                    pasien_id=norm,
                    document_type="surat_kematian",
                    title=f"Surat Keterangan Kematian - {nama_pasien}",
                    filename=pdf_filename,
                    storage_path=pdf_path,
                    original_path="SIMRS_AUTO_INGEST",
                    uploaded_by=uploader_id,
                    uploaded_at=datetime.now(timezone.utc) - timedelta(hours=j),
                    status="pending",
                    description=f"Surat Kematian diterbitkan SIMRS untuk ditandatangani oleh {dr_b.nama}",
                    file_size=fsize,
                    target_signer_nip=dr_b.nip,
                    target_signer_name=dr_b.nama,
                    tte_status="UNSIGNED",
                    pdf_hash=fhash,
                    metadata_json=json.dumps(simrs_payload),
                    embedding=embed
                )
                db.add(doc)

            # Buat Notifikasi Khusus ke User A (dr_rizki)
            notif_dr_a = UserNotification(
                user_id=dr_a.id,
                user_nip=dr_a.nip,
                title="30 Surat Kematian Belum Di-TTE",
                message="Perhatian dr. RIZKI HABIBIE, Sp.PD.: Terdapat 30 dokumen Surat Kematian dan Lembar Konsul baru yang diterbitkan SIMRS dan menunggu tanda tangan elektronik (TTE BSRE) Anda.",
                document_type="surat_kematian",
                pending_count=30,
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            db.add(notif_dr_a)

            # Notifikasi ke User B (dr_elieza)
            notif_dr_b = UserNotification(
                user_id=dr_b.id,
                user_nip=dr_b.nip,
                title="30 Surat Kematian Belum Di-TTE",
                message="Perhatian dr. ELIEZA, Sp.A.: Terdapat 30 dokumen Surat Kematian Ruang Melati menunggu TTE BSRE Anda.",
                document_type="surat_kematian",
                pending_count=30,
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            db.add(notif_dr_b)

            db.commit()
            print("✓ 60 Dokumen Surat Kematian & notifikasi berhasil di-generate secara otomatis!")

if __name__ == "__main__":
    seed_database()
