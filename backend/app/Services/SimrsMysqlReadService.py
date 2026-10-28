import os
import re
import json
import logging
import pymysql
import pymysql.cursors
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select

from config.settings import settings
from app.Models.Document import Document
from app.Models.User import User
from app.Models.Notification import UserNotification
from app.Services.PdfGeneratorService import pdf_service
from app.Services.BsreTteService import bsre_service
from app.Services.VectorSearchService import vector_service

logger = logging.getLogger(__name__)

BULAN_INDO = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}


class SimrsMysqlReadService:
    """
    Layanan Koneksi Read-Only (SELECT-Only) ke Database MySQL Riil SIMRS
    menggunakan kredensial khusus viewer dari file .env.
    Menggunakan query yang 100% identik dengan RanapController.php & pegawai-by-kdpegsimrs
    pada SIMRS-V3 (kepegx.pegawai, kepegx.m_jabatan, kepegx.m_golruang, rs23, rs23_nosurat, rs15, rs99x).
    """

    @staticmethod
    def _get_connection():
        if not settings.DB_HOST or not settings.DB_USER:
            raise RuntimeError("Konfigurasi DB_HOST / DB_USER belum diatur di .env")
        return pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=8,
            read_timeout=15
        )

    @staticmethod
    def _extract_numeric_id(raw_str: str, fallback: int = 50001) -> int:
        digits = re.sub(r"\D", "", str(raw_str or ""))
        if not digits:
            return fallback
        return int(digits[:12])

    @staticmethod
    def _format_tanggal_indo(dt_val: Any) -> str:
        if not dt_val:
            now = datetime.now()
            return f"{now.day:02d} {BULAN_INDO[now.month]} {now.year}"
        if isinstance(dt_val, (datetime, date)):
            return f"{dt_val.day:02d} {BULAN_INDO[dt_val.month]} {dt_val.year}"
        s = str(dt_val).strip()
        try:
            parsed = datetime.fromisoformat(s.replace("Z", ""))
            return f"{parsed.day:02d} {BULAN_INDO[parsed.month]} {parsed.year}"
        except Exception:
            return s

    @classmethod
    def fetch_surat_kematian_ranap(cls, limit: int = 25, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Mengambil daftar Surat Keterangan Kematian Rawat Inap langsung dari MySQL SIMRS:
        - rs23 & rs23_nosurat (kunjungan ranap meninggal & nomor surat)
        - rs15 (master pasien dengan format alamat dan usia persis RanapController.php)
        - kepegx.pegawai + kepegx.m_jabatan + kepegx.m_golruang (persis route /v1/pegawai/master/pegawai-by-kdpegsimrs)
        - rs99x (master ICD-10 penyebab kematian)
        """
        conn = cls._get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT
                        r.rs1 AS noreg,
                        r.rs2 AS norm,
                        r.rs4 AS tglkeluar,
                        r.rs22 AS statuspulang,
                        r.rs23 AS carakeluar,
                        r.rs25 AS sebabkematian_kode,
                        r.rs26 AS diagakhir_kode,
                        n.nosrtmeninggal,
                        n.jamMeninggal,
                        n.kddrygmenyatakan,
                        p.rs2 AS nama_panggil,
                        CONCAT(p.rs3, ' ', p.gelardepan, ' ', p.rs2, ' ', p.gelarbelakang) AS nama_lengkap,
                        CONCAT(
                            p.rs4, ' KEL ', p.rs5, ' RT ', p.rs7, ' RW ', p.rs8, ' ',
                            p.rs6, ' ', p.rs11, ' ', p.rs10
                        ) AS alamat_lengkap,
                        CONCAT(
                            TIMESTAMPDIFF(YEAR, p.rs16, CURDATE()), ' Tahun ',
                            MOD(TIMESTAMPDIFF(MONTH, p.rs16, CURDATE()), 12), ' Bulan ',
                            TIMESTAMPDIFF(DAY, TIMESTAMPADD(MONTH, TIMESTAMPDIFF(MONTH, p.rs16, CURDATE()), p.rs16), CURDATE()), ' Hari'
                        ) AS usia_lengkap,
                        p.rs49 AS nktp,
                        p.rs16 AS tgllahir,
                        p.rs17 AS kelamin,
                        peg.nama AS nama_dokter_kepegx,
                        peg.nip AS nip_dokter_kepegx,
                        peg.nik AS nik_dokter_kepegx,
                        jab.jabatan AS ket_jabatan_kepegx,
                        gol.golruang AS golongan_kepegx,
                        gol.keterangan AS ket_golongan_kepegx,
                        d.rs2 AS nama_dokter_rs21,
                        d.nip AS nip_dokter_rs21,
                        icd.rs4 AS sebabkematian_ket,
                        icd.rs3 AS sebabkematian_indo
                    FROM rs23 r
                    INNER JOIN rs23_nosurat n ON r.rs1 = n.noreg
                    LEFT JOIN rs15 p ON r.rs2 = p.rs1
                    LEFT JOIN kepegx.pegawai peg ON n.kddrygmenyatakan = peg.kdpegsimrs AND peg.aktif = 'AKTIF'
                    LEFT JOIN kepegx.m_jabatan jab ON peg.jabatan = jab.kode_jabatan
                    LEFT JOIN kepegx.m_golruang gol ON peg.golruang = gol.kode_gol
                    LEFT JOIN rs21 d ON n.kddrygmenyatakan = d.rs1
                    LEFT JOIN rs99x icd ON r.rs25 = icd.rs1
                    WHERE (r.rs23 = 'C003' OR (n.nosrtmeninggal IS NOT NULL AND n.nosrtmeninggal != ''))
                """
                params = []
                if search:
                    sql += " AND (r.rs1 LIKE %s OR r.rs2 LIKE %s OR p.rs2 LIKE %s OR n.nosrtmeninggal LIKE %s)"
                    q = f"%{search}%"
                    params.extend([q, q, q, q])

                sql += " ORDER BY r.rs4 DESC LIMIT %s"
                params.append(limit)

                cur.execute(sql, tuple(params))
                rows = cur.fetchall()

                results = []
                for row in rows:
                    noreg = row.get("noreg") or ""
                    norm = row.get("norm") or ""
                    kunjungan_id = cls._extract_numeric_id(noreg, 50001)
                    pasien_id = cls._extract_numeric_id(norm, 20001)

                    tgl_meninggal_str = cls._format_tanggal_indo(row.get("tglkeluar"))
                    umur_str = (row.get("usia_lengkap") or "-").strip()

                    sebab_kode = (row.get("sebabkematian_kode") or "").strip()
                    sebab_ket = (row.get("sebabkematian_ket") or row.get("sebabkematian_indo") or "").strip()
                    diagnosa_str = sebab_ket or sebab_kode or "-"

                    # Ambil dari kepegx.pegawai (persis SIMRS-V3), fallback ke rs21 jika kosong
                    nama_dokter = (row.get("nama_dokter_kepegx") or row.get("nama_dokter_rs21") or "dr. Dokter Pemeriksa").strip()
                    nip_dokter = (row.get("nip_dokter_kepegx") or row.get("nip_dokter_rs21") or "").strip()
                    golongan = (row.get("golongan_kepegx") or "-").strip()
                    ket_golongan = (row.get("ket_golongan_kepegx") or "-").strip()
                    ket_jabatan = (row.get("ket_jabatan_kepegx") or "Dokter Fungsional").strip()

                    alamat_lengkap = re.sub(r"\s+", " ", (row.get("alamat_lengkap") or "PROBOLINGGO")).strip()
                    nama_panggil = (row.get("nama_panggil") or "-").strip()

                    nosurat = (row.get("nosrtmeninggal") or "").strip()
                    if not nosurat:
                        nosurat = f"472.12/{str(kunjungan_id)[-4:]}/425.102.8/KEM/X/2026"

                    jam_meninggal = (row.get("jamMeninggal") or "00:00").strip()

                    payload = {
                        "kunjungan_id": kunjungan_id,
                        "pasien_id": pasien_id,
                        "noreg": noreg,
                        "norm": norm,
                        "judul": "SURAT KETERANGAN KEMATIAN",
                        "nosrtmeninggal": nosurat,
                        "nomor_surat": nosurat,
                        "tgl_meninggal": tgl_meninggal_str,
                        "tglkeluar_raw": str(row.get("tglkeluar") or ""),
                        "jamMeninggal": jam_meninggal,
                        "jam_meninggal": jam_meninggal,
                        "diagnosa": diagnosa_str,
                        "sebabkematian_kode": sebab_kode,
                        "sebabkematian_ket": diagnosa_str,
                        "pasien": {
                            "noreg": noreg,
                            "norm": norm,
                            "nama": nama_panggil,
                            "nama_panggil": nama_panggil,
                            "nktp": (row.get("nktp") or "-").strip(),
                            "tgllahir": str(row.get("tgllahir") or "-"),
                            "usia": umur_str,
                            "kelamin": (row.get("kelamin") or "-").strip(),
                            "alamat": alamat_lengkap,
                            "tglkeluar": tgl_meninggal_str,
                            "sebabkematian": diagnosa_str
                        },
                        "dokter": {
                            "kdpegsimrs": row.get("kddrygmenyatakan") or "",
                            "nama": nama_dokter,
                            "nip": nip_dokter,
                            "nik": settings.BSRE_DEV_NIK,
                            "golongan": golongan,
                            "ket_golongan": ket_golongan,
                            "ket_jabatan": ket_jabatan
                        },
                        "dpjp": {
                            "kdpegsimrs": row.get("kddrygmenyatakan") or "",
                            "nama": nama_dokter,
                            "nip": nip_dokter,
                            "nik": settings.BSRE_DEV_NIK,
                            "golongan": golongan,
                            "ket_golongan": ket_golongan,
                            "ket_jabatan": ket_jabatan
                        }
                    }
                    results.append(payload)

                return results
        finally:
            conn.close()

    @classmethod
    def sync_surat_kematian_to_postgres(cls, db: Session, limit: int = 15) -> Dict[str, Any]:
        """
        Sinkronisasi otomatis data Surat Keterangan Kematian Ranap dari MySQL SIMRS (Read-Only)
        ke PostgreSQL Microservice & Signature Inbox.
        """
        records = cls.fetch_surat_kematian_ranap(limit=limit)
        synced_docs = []
        skipped_count = 0

        default_user = db.exec(select(User).where(User.role == "dokter")).first()
        uploader_id = default_user.id if default_user else 1

        for item in records:
            kunjungan_id = item["kunjungan_id"]
            nosurat = item["nosrtmeninggal"]
            nama_dokter = item["dokter"]["nama"]

            existing = db.exec(
                select(Document).where(
                    Document.document_type == "surat_kematian",
                    Document.kunjungan_id == kunjungan_id
                )
            ).first()

            if existing:
                try:
                    existing.target_signer_name = nama_dokter
                    existing.metadata_json = json.dumps(item)
                    if existing.tte_status == "SIGNED_BSRE":
                        existing.tte_signer_name = nama_dokter
                        verify_url = bsre_service.build_simrs_legalitas_url(metadata_payload=item, doc_id=existing.id)
                        pdf_service.generate_surat_kematian_pdf(item, existing.storage_path, is_signed=True, verify_url=verify_url)
                    else:
                        pdf_service.generate_surat_kematian_pdf(item, existing.storage_path, is_signed=False)
                    existing.file_size = os.path.getsize(existing.storage_path)
                    existing.pdf_hash = bsre_service.calculate_file_hash(existing.storage_path)
                    db.add(existing)
                except Exception as e:
                    logger.warning(f"Gagal update PDF doc {existing.id}: {e}")
                skipped_count += 1
                continue

            doc_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", "ranap_kematian", str(kunjungan_id))
            os.makedirs(doc_dir, exist_ok=True)

            filename = f"SURAT_KEMATIAN_RANAP_{kunjungan_id}_{item['pasien_id']}.pdf"
            file_path = os.path.join(doc_dir, filename)

            pdf_service.generate_surat_kematian_pdf(item, file_path, is_signed=False)
            file_size = os.path.getsize(file_path)
            doc_hash = bsre_service.calculate_file_hash(file_path)

            nama_pasien = item["pasien"]["nama"]
            signer_nik = settings.BSRE_DEV_NIK

            search_text = (
                f"Surat Keterangan Kematian Ranap {nama_pasien} "
                f"RM:{item['norm']} Noreg:{item['noreg']} "
                f"NoSurat:{nosurat} Diagnosa:{item['diagnosa']} Dokter:{nama_dokter}"
            )
            embed = vector_service.generate_embedding(search_text)

            new_doc = Document(
                kunjungan_id=kunjungan_id,
                pasien_id=item["pasien_id"],
                document_type="surat_kematian",
                title=f"Surat Keterangan Kematian - {nama_pasien}",
                filename=filename,
                storage_path=file_path,
                original_path=file_path,
                uploaded_by=uploader_id,
                uploaded_at=datetime.now(timezone.utc),
                status="pending",
                description=f"No. Surat: {nosurat} • Noreg: {item['noreg']} • RM: {item['norm']} • Dokter: {nama_dokter}",
                file_size=file_size,
                target_signer_nip=signer_nik,
                target_signer_name=nama_dokter,
                tte_status="UNSIGNED",
                pdf_hash=doc_hash,
                metadata_json=json.dumps(item),
                embedding=embed
            )
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)

            notif = UserNotification(
                user_id=uploader_id,
                user_nip=signer_nik,
                title="Surat Kematian Ranap (Sync Otomatis SIMRS)",
                message=f"Surat Keterangan Kematian ({nosurat}) a.n. {nama_pasien} (RM: {item['norm']}) siap ditandatangani.",
                document_type="surat_kematian",
                pending_count=1,
                is_read=False
            )
            db.add(notif)
            synced_docs.append(new_doc)

        db.commit()
        return {
            "total_fetched_from_mysql": len(records),
            "newly_synced_count": len(synced_docs),
            "already_existing_count": skipped_count,
            "synced_documents": synced_docs,
            "raw_records": records
        }


simrs_mysql_service = SimrsMysqlReadService()
