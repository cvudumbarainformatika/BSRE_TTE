import os
import uuid
import json
import re
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Optional

from config.database import get_session
from config.settings import settings
from app.Models.Document import Document
from app.Models.User import User
from app.Models.Notification import UserNotification
from app.Models.DocumentAuditLog import TteSignature
from app.Services.PdfGeneratorService import pdf_service
from app.Services.BsreTteService import bsre_service
from app.Services.SimrsMysqlReadService import simrs_mysql_service
from app.Services.VectorSearchService import vector_service
from app.Services.AuditService import audit_service
from app.Http.Middleware.AuthMiddleware import get_current_user
from app.Http.Requests.DocumentRequests import SimrsAutoIngestRequest, SuratKematianRanapRequest

router = APIRouter(prefix="/simrs", tags=["SIMRS Automated Ingest & MySQL Read-Only Sync"])


def _extract_numeric_id(raw_str: str, fallback: int = 50001) -> int:
    digits = re.sub(r"\D", "", str(raw_str or ""))
    if not digits:
        return fallback
    return int(digits[:12])


@router.get("/ranap/surat-kematian/mysql-list")
def list_surat_kematian_from_mysql(
    limit: int = 20,
    search: Optional[str] = None,
    auto_sync: bool = True,
    db: Session = Depends(get_session)
):
    """
    Mengambil daftar Surat Keterangan Kematian Rawat Inap langsung dari Database MySQL SIMRS
    menggunakan koneksi Read-Only (viewer) dari .env, sekaligus menyinkronkannya ke Signature Inbox PostgreSQL.
    """
    try:
        if auto_sync:
            sync_info = simrs_mysql_service.sync_surat_kematian_to_postgres(db=db, limit=limit)
            raw_records = sync_info["raw_records"]
        else:
            raw_records = simrs_mysql_service.fetch_surat_kematian_ranap(limit=limit, search=search)
            sync_info = {"newly_synced_count": 0, "already_existing_count": len(raw_records)}

        # Gabungkan dengan status TTE terkini dari PostgreSQL (1 BATCH QUERY SUPER CEPAT, ZERO N+1 QUERY)
        kunj_ids = [rec["kunjungan_id"] for rec in raw_records]
        pg_docs = db.exec(
            select(Document)
            .where(Document.document_type == "surat_kematian", Document.kunjungan_id.in_(kunj_ids))
            .order_by(Document.uploaded_at.desc())
        ).all()

        doc_map = {}
        for d in pg_docs:
            if d.kunjungan_id not in doc_map:
                doc_map[d.kunjungan_id] = d

        enriched = []
        for rec in raw_records:
            kunj_id = rec["kunjungan_id"]
            pg_doc = doc_map.get(kunj_id)

            rec["document_id"] = pg_doc.id if pg_doc else None
            rec["tte_status"] = pg_doc.tte_status if pg_doc else "UNSIGNED"
            rec["tte_signed_at"] = pg_doc.tte_signed_at if pg_doc else None
            rec["tte_signer_name"] = pg_doc.tte_signer_name if pg_doc else rec["dokter"]["nama"]
            rec["preview_url"] = f"/api/v1/document/{pg_doc.id}/view" if pg_doc else None
            rec["download_url"] = f"/api/v1/document/{pg_doc.id}/download" if pg_doc else None
            enriched.append(rec)

        return {
            "source": f"MySQL SIMRS Read-Only ({settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME})",
            "total": len(enriched),
            "sync_summary": {
                "newly_synced": sync_info.get("newly_synced_count", 0),
                "already_existing": sync_info.get("already_existing_count", 0)
            },
            "data": enriched
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca MySQL SIMRS: {str(e)}")


@router.post("/ranap/surat-kematian/sync-mysql")
def trigger_sync_surat_kematian_mysql(
    limit: int = 20,
    db: Session = Depends(get_session)
):
    """
    Sinkronisasi penuh data Surat Keterangan Kematian Ranap dari MySQL SIMRS (Read-Only)
    ke PostgreSQL Document Service & Signature Inbox.
    """
    try:
        result = simrs_mysql_service.sync_surat_kematian_to_postgres(db=db, limit=limit)
        return {
            "message": f"Sinkronisasi selesai: {result['newly_synced_count']} dokumen baru masuk Signature Inbox, {result['already_existing_count']} dokumen sudah tersinkron.",
            "newly_synced_count": result["newly_synced_count"],
            "already_existing_count": result["already_existing_count"],
            "total_fetched_from_mysql": result["total_fetched_from_mysql"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal sinkronisasi MySQL SIMRS: {str(e)}")


@router.get("/ranap/surat-kematian/status")
def get_surat_kematian_ranap_status(
    noreg: str,
    db: Session = Depends(get_session)
):
    """
    Mengecek status TTE BSrE Surat Keterangan Kematian Ranap berdasarkan Noreg SIMRS.
    """
    kunjungan_id = _extract_numeric_id(noreg)
    docs = db.exec(
        select(Document)
        .where(
            Document.document_type == "surat_kematian",
            Document.kunjungan_id == kunjungan_id
        )
        .order_by(Document.uploaded_at.desc())
    ).all()

    if not docs:
        return {
            "exists": False,
            "noreg": noreg,
            "kunjungan_id": kunjungan_id,
            "tte_status": "NOT_FINALIZED",
            "message": "Surat Kematian belum tersinkron ke layanan TTE BSrE."
        }

    latest_doc = docs[0]
    return {
        "exists": True,
        "noreg": noreg,
        "kunjungan_id": kunjungan_id,
        "document_id": latest_doc.id,
        "tte_status": latest_doc.tte_status,
        "status": latest_doc.status,
        "tte_signed_at": latest_doc.tte_signed_at,
        "tte_signer_name": latest_doc.tte_signer_name,
        "pdf_hash": latest_doc.pdf_hash,
        "preview_url": f"/api/v1/document/{latest_doc.id}/view",
        "download_url": f"/api/v1/document/{latest_doc.id}/download",
        "verify_url": f"/api/v1/tte/{latest_doc.id}/verify",
        "data": latest_doc
    }


@router.post("/ranap/surat-kematian/finalize")
def finalize_surat_kematian_ranap(
    req: SuratKematianRanapRequest,
    request: Request,
    db: Session = Depends(get_session)
):
    """
    Finalisasi & TTE BSrE untuk Dokumen Surat Keterangan Kematian Rawat Inap.
    """
    kunjungan_id = _extract_numeric_id(req.noreg, 50999)
    pasien_id = _extract_numeric_id(req.norm, 280999)

    signer_nik = req.signer_nik or req.dpjp.get("nik") or settings.BSRE_DEV_NIK
    signer_nip = req.dpjp.get("nip") or ""
    signer_name = req.dpjp.get("nama") or "dr. RIA NURMALA SETYANINGRUM"

    if req.sign_now:
        if not req.passphrase or req.passphrase.strip() != settings.BSRE_DEV_PASSPHRASE:
            raise HTTPException(
                status_code=400,
                detail="Passphrase BSrE salah! Silakan masukkan Passphrase BSrE yang benar."
            )

    doc_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", "ranap_kematian", str(kunjungan_id))
    os.makedirs(doc_dir, exist_ok=True)

    filename = f"SURAT_KEMATIAN_RANAP_{kunjungan_id}_{pasien_id}_{uuid.uuid4().hex[:6]}.pdf"
    file_path = os.path.join(doc_dir, filename)

    nama_pasien = req.pasien.get("nama_panggil") or req.pasien.get("nama") or "Pasien Ranap"
    nomor_surat = req.nosrtmeninggal or f"472.12/{str(kunjungan_id)[-4:]}/425.102.8/KEM/X/2026"

    content_payload = {
        "kunjungan_id": kunjungan_id,
        "noreg": req.noreg,
        "norm": req.norm,
        "judul": "SURAT KETERANGAN KEMATIAN",
        "nosrtmeninggal": nomor_surat,
        "nomor_surat": nomor_surat,
        "tgl_meninggal": req.tglkeluar or req.pasien.get("tglkeluar") or datetime.now().strftime("%d %B %Y"),
        "jamMeninggal": req.jamMeninggal or "08:47",
        "jam_meninggal": req.jamMeninggal or "08:47",
        "diagnosa": req.diagnosa or req.pasien.get("sebabkematian") or "Cardiac arrest, unspecified",
        "sebabkematian_ket": req.diagnosa or req.pasien.get("sebabkematian") or "Cardiac arrest, unspecified",
        "pasien": req.pasien,
        "dpjp": req.dpjp,
        "dokter": {
            "nama": signer_name,
            "nip": signer_nip,
            "nik": signer_nik,
            "golongan": req.dpjp.get("golongan", "IV/a"),
            "ket_golongan": req.dpjp.get("ket_golongan", "Pembina"),
            "ket_jabatan": req.dpjp.get("ket_jabatan", "Dokter Madya")
        }
    }

    # Cek apakah sudah ada dokumen sebelumnya untuk kunjungan_id ini
    existing_doc = db.exec(
        select(Document).where(
            Document.document_type == "surat_kematian",
            Document.kunjungan_id == kunjungan_id
        ).order_by(Document.uploaded_at.desc())
    ).first()

    pdf_service.generate_surat_kematian_pdf(content_payload, file_path, is_signed=False)
    file_size = os.path.getsize(file_path)
    doc_hash = bsre_service.calculate_file_hash(file_path)

    search_text = f"Surat Keterangan Kematian Ranap {nama_pasien} RM:{req.norm} Noreg:{req.noreg} Diagnosa:{content_payload['diagnosa']} Dokter:{signer_name}"
    embed = vector_service.generate_embedding(search_text)

    target_user = db.exec(
        select(User).where((User.nik == signer_nik) | (User.nip == signer_nip) | (User.username == "dr_rizki"))
    ).first()
    uploader_id = target_user.id if target_user else 1

    if existing_doc:
        doc = existing_doc
        doc.title = f"Surat Keterangan Kematian - {nama_pasien}"
        doc.filename = filename
        doc.storage_path = file_path
        doc.original_path = file_path
        doc.file_size = file_size
        doc.target_signer_name = signer_name
        doc.metadata_json = json.dumps(content_payload)
        doc.pdf_hash = doc_hash
    else:
        doc = Document(
            kunjungan_id=kunjungan_id,
            pasien_id=pasien_id,
            document_type="surat_kematian",
            title=f"Surat Keterangan Kematian - {nama_pasien}",
            filename=filename,
            storage_path=file_path,
            original_path=file_path,
            uploaded_by=uploader_id,
            uploaded_at=datetime.now(timezone.utc),
            status="pending",
            description=f"No. Surat: {nomor_surat} • Noreg: {req.noreg} • Dokter: {signer_name}",
            file_size=file_size,
            target_signer_nip=signer_nik,
            target_signer_name=signer_name,
            tte_status="UNSIGNED",
            pdf_hash=doc_hash,
            metadata_json=json.dumps(content_payload),
            embedding=embed
        )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    if req.sign_now:
        signed_filename = f"SIGNED_{filename}"
        signed_path = os.path.join(doc_dir, signed_filename)
        qr_dir = os.path.join(settings.BASE_STORAGE_PATH, "qr_codes")
        os.makedirs(qr_dir, exist_ok=True)

        sign_result = bsre_service.sign_document(
            input_pdf_path=file_path,
            output_pdf_path=signed_path,
            signer_name=signer_name,
            signer_nik=signer_nik,
            signer_nip=signer_nip,
            doc_id=doc.id,
            passphrase=req.passphrase.strip(),
            metadata_payload=content_payload
        )

        qr_path = os.path.join(qr_dir, f"qr_doc_{doc.id}.png")
        verify_url = bsre_service.generate_qr_verification(doc.id, signer_nik, signer_name, qr_path, metadata_payload=content_payload)

        doc.storage_path = signed_path
        doc.filename = signed_filename
        doc.tte_status = "SIGNED_BSRE"
        doc.tte_bsre_id = sign_result["bsre_id"]
        doc.tte_signed_at = datetime.now(timezone.utc)
        doc.tte_signer_nip = signer_nip
        doc.tte_signer_name = signer_name
        doc.qr_code_path = qr_path
        doc.pdf_hash = sign_result["pdf_hash"]
        doc.status = "signed"
        db.add(doc)

        sig_record = TteSignature(
            document_id=doc.id,
            bsre_request_id=sign_result["bsre_id"],
            signer_nip=signer_nip or "TERVERIFIKASI",
            signer_name=signer_name,
            signer_role="dokter",
            signed_at=doc.tte_signed_at,
            certificate_issuer=sign_result["certificate_issuer"],
            certificate_serial=sign_result["certificate_serial"],
            signature_hash=sign_result["pdf_hash"],
            qr_verify_url=verify_url,
            status="SUCCESS"
        )
        db.add(sig_record)
        db.commit()
        db.refresh(doc)

        audit_service.log(
            db=db,
            document_id=doc.id,
            user_id=uploader_id,
            username=target_user.username if target_user else "simrs_ranap",
            user_role="dokter",
            action="RANAP_SURAT_KEMATIAN_DIRECT_TTE_BSRE",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"noreg": req.noreg, "nosrtmeninggal": nomor_surat, "bsre_id": sign_result["bsre_id"]}
        )

        return {
            "message": f"Surat Keterangan Kematian ({nomor_surat}) berhasil ditandatangani secara elektronik BSrE BSSN!",
            "tte_status": "SIGNED_BSRE",
            "document_id": doc.id,
            "preview_url": f"/api/v1/document/{doc.id}/view",
            "download_url": f"/api/v1/document/{doc.id}/download",
            "verify_url": f"/api/v1/tte/{doc.id}/verify",
            "data": doc
        }

    return {
        "message": f"Surat Keterangan Kematian ({nomor_surat}) tersimpan di Signature Inbox.",
        "tte_status": "UNSIGNED",
        "document_id": doc.id,
        "preview_url": f"/api/v1/document/{doc.id}/view",
        "download_url": f"/api/v1/document/{doc.id}/download",
        "data": doc
    }
