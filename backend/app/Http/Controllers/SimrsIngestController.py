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
from app.Services.WebSocketService import dispatch_ws_event
from app.Http.Middleware.AuthMiddleware import get_current_user
from app.Http.Requests.DocumentRequests import (
    SimrsAutoIngestRequest,
    SuratKematianRanapRequest,
    PulangkanPasienRanapRequest
)

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
    auto_sync: bool = False,
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


def _build_data_fingerprint(payload: dict) -> str:
    """Membentuk fingerprint data klinis utama untuk mendeteksi adanya revisi/perubahan di SIMRS."""
    if not payload:
        return ""
    dok = payload.get("dokter") or payload.get("dpjp") or {}
    parts = [
        str(payload.get("nosrtmeninggal") or payload.get("nomor_surat") or "").strip().lower(),
        str(payload.get("jamMeninggal") or payload.get("jam_meninggal") or "").strip()[:5].lower(),
        str(payload.get("diagnosa") or payload.get("sebabkematian_ket") or "").strip().lower(),
        str(dok.get("nama") or "").strip().lower(),
    ]
    return "|".join(parts)


def _prepare_versioned_payload(existing_doc: Optional[Document], new_payload: dict) -> tuple:
    """
    Mengelola versioning dokumen secara otomatis:
    - Jika existing_doc sudah SIGNED_BSRE, arsipkan PDF lama ke revision_history dan naikkan versi (v2.0, v3.0, dst).
    - Jika existing_doc masih UNSIGNED (di Inbox), timpa draft pada versi yang sama.
    """
    prev_version = 1
    revision_history = []
    was_signed = False

    if existing_doc and existing_doc.metadata_json:
        try:
            old_meta = json.loads(existing_doc.metadata_json)
            prev_version = int(old_meta.get("version", 1))
            revision_history = list(old_meta.get("revision_history", []))
        except Exception:
            prev_version = 1
            revision_history = []
            old_meta = {}
    else:
        old_meta = {}

    if existing_doc and existing_doc.tte_status == "SIGNED_BSRE":
        was_signed = True
        revision_entry = {
            "version": prev_version,
            "version_label": f"v{prev_version}.0",
            "filename": existing_doc.filename,
            "storage_path": existing_doc.storage_path,
            "pdf_hash": existing_doc.pdf_hash,
            "signed_at": existing_doc.tte_signed_at.isoformat() if existing_doc.tte_signed_at else None,
            "signer_name": existing_doc.tte_signer_name or existing_doc.target_signer_name,
            "bsre_id": existing_doc.tte_bsre_id,
            "summary": (
                f"No: {old_meta.get('nosrtmeninggal', '-')} • "
                f"Jam: {str(old_meta.get('jamMeninggal', '-'))[:5]} • "
                f"Diagnosa: {old_meta.get('diagnosa', '-')}"
            )
        }
        revision_history.append(revision_entry)
        new_version = prev_version + 1
    else:
        new_version = prev_version

    new_payload["version"] = new_version
    new_payload["version_label"] = f"v{new_version}.0"
    new_payload["revision_history"] = revision_history
    new_payload["data_fingerprint"] = _build_data_fingerprint(new_payload)
    return new_version, revision_history, was_signed


@router.get("/ranap/surat-kematian/status")
def get_surat_kematian_ranap_status(
    noreg: str,
    db: Session = Depends(get_session)
):
    """
    Mengecek status TTE BSrE & versi Surat Keterangan Kematian Ranap berdasarkan Noreg SIMRS.
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
            "version": 1,
            "version_label": "v1.0",
            "revision_history": [],
            "signed_snapshot": None,
            "message": "Surat Kematian belum tersinkron ke layanan TTE BSrE."
        }

    latest_doc = docs[0]
    meta = {}
    if latest_doc.metadata_json:
        try:
            meta = json.loads(latest_doc.metadata_json)
        except Exception:
            meta = {}

    ver = int(meta.get("version", 1))
    dok_meta = meta.get("dokter") or meta.get("dpjp") or {}
    signed_snapshot = {
        "nosrtmeninggal": meta.get("nosrtmeninggal") or meta.get("nomor_surat") or "",
        "jamMeninggal": str(meta.get("jamMeninggal") or meta.get("jam_meninggal") or "")[:5],
        "diagnosa": meta.get("diagnosa") or meta.get("sebabkematian_ket") or "",
        "dokter_nama": dok_meta.get("nama") or latest_doc.target_signer_name or ""
    }

    return {
        "exists": True,
        "noreg": noreg,
        "kunjungan_id": kunjungan_id,
        "document_id": latest_doc.id,
        "tte_status": latest_doc.tte_status,
        "status": latest_doc.status,
        "version": ver,
        "version_label": f"v{ver}.0",
        "revision_history": meta.get("revision_history", []),
        "signed_snapshot": signed_snapshot,
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
    Finalisasi, Kirim ke Inbox, atau TTE / TTE Ulang (Revisi v2.0+) untuk Surat Keterangan Kematian Rawat Inap.
    """
    kunjungan_id = _extract_numeric_id(req.noreg, 50999)
    pasien_id = _extract_numeric_id(req.norm, 280999)

    signer_nik = req.dpjp.get("nik") or req.signer_nik or (settings.BSRE_DEV_NIK if settings.BSRE_MOCK_MODE else "")
    signer_nip = req.dpjp.get("nip") or ""
    signer_name = req.dpjp.get("nama") or "dr. RIA NURMALA SETYANINGRUM"

    if req.sign_now:
        if not req.passphrase or len(req.passphrase.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail=f"Otorisasi BSrE Gagal: Passphrase BSrE tidak boleh kosong untuk penandatangan {signer_name}."
            )
        if settings.BSRE_MOCK_MODE and req.passphrase.strip() != settings.BSRE_DEV_PASSPHRASE:
            raise HTTPException(
                status_code=400,
                detail=f"Otorisasi BSrE Gagal: Passphrase BSrE yang Anda masukkan salah untuk penandatangan {signer_name}."
            )

    doc_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", "ranap_kematian", str(kunjungan_id))
    os.makedirs(doc_dir, exist_ok=True)

    # Perkaya data dasar dari MySQL SIMRS lalu timpa dengan perubahan terbaru dari request (req)
    mysql_rec = None
    try:
        records = simrs_mysql_service.fetch_surat_kematian_ranap(limit=5, search=req.noreg)
        for r in records:
            if r.get("noreg") == req.noreg:
                mysql_rec = r
                break
    except Exception:
        mysql_rec = None

    nama_pasien = (
        req.pasien.get("nama_panggil")
        or req.pasien.get("nama")
        or (mysql_rec["pasien"].get("nama") if mysql_rec else None)
        or "Pasien Ranap"
    )
    nomor_surat = (
        req.nosrtmeninggal
        or (mysql_rec.get("nosrtmeninggal") if mysql_rec else None)
        or f"472.12/{str(kunjungan_id)[-4:]}/425.102.8/KEM/X/2026"
    )

    if mysql_rec:
        signer_name = req.dpjp.get("nama") or mysql_rec["dokter"].get("nama") or signer_name
        signer_nip = req.dpjp.get("nip") or mysql_rec["dokter"].get("nip") or signer_nip
        signer_nik = req.dpjp.get("nik") or mysql_rec["dokter"].get("nik") or signer_nik
        content_payload = dict(mysql_rec)
        if req.nosrtmeninggal:
            content_payload["nosrtmeninggal"] = req.nosrtmeninggal
            content_payload["nomor_surat"] = req.nosrtmeninggal
        if req.jamMeninggal:
            content_payload["jamMeninggal"] = req.jamMeninggal
            content_payload["jam_meninggal"] = req.jamMeninggal
        if req.diagnosa and req.diagnosa != "-":
            content_payload["diagnosa"] = req.diagnosa
            content_payload["sebabkematian_ket"] = req.diagnosa
        if req.tglkeluar:
            content_payload["tgl_meninggal"] = req.tglkeluar
        if req.dpjp and req.dpjp.get("nama"):
            content_payload["dokter"] = {
                **content_payload.get("dokter", {}),
                "nama": signer_name,
                "nip": signer_nip,
                "nik": signer_nik
            }
    else:
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

    existing_doc = db.exec(
        select(Document).where(
            Document.document_type == "surat_kematian",
            Document.kunjungan_id == kunjungan_id
        ).order_by(Document.uploaded_at.desc())
    ).first()

    new_version, revision_history, was_signed = _prepare_versioned_payload(existing_doc, content_payload)
    ver_label = f"v{new_version}.0"

    filename = f"SURAT_KEMATIAN_RANAP_{kunjungan_id}_{pasien_id}_v{new_version}_{uuid.uuid4().hex[:5]}.pdf"
    file_path = os.path.join(doc_dir, filename)

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
        doc.uploaded_at = datetime.now(timezone.utc)
        doc.description = f"No. Surat: {nomor_surat} • Noreg: {req.noreg} • Dokter: {signer_name} ({ver_label})"
        doc.target_signer_name = signer_name
        doc.target_signer_nip = signer_nip or signer_nik
        doc.metadata_json = json.dumps(content_payload)
        doc.pdf_hash = doc_hash
        doc.tte_status = "UNSIGNED"
        doc.status = "pending"
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
            description=f"No. Surat: {nomor_surat} • Noreg: {req.noreg} • Dokter: {signer_name} ({ver_label})",
            file_size=file_size,
            target_signer_nip=signer_nip or signer_nik,
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

        try:
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
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        qr_path = os.path.join(qr_dir, f"qr_doc_{doc.id}_v{new_version}.png")
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

        action_name = f"RE_SIGN_TTE_BSRE ({ver_label})" if was_signed else f"SIGN_TTE_BSRE ({ver_label})"
        audit_service.log(
            db=db,
            document_id=doc.id,
            user_id=uploader_id,
            username=signer_name,
            user_role="Penandatangan TTE",
            action=action_name,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={
                "version": ver_label,
                "noreg": req.noreg,
                "nomor_dokumen": nomor_surat,
                "bsre_id": sign_result["bsre_id"],
                "signer_name": signer_name,
                "signer_nip": signer_nip
            }
        )

        # Broadcast WebSocket ke SIMRS Web & Mobile App (Signed)
        dispatch_ws_event(
            event_type="DOCUMENT_SIGNED",
            noreg=req.noreg,
            document_id=doc.id,
            version_label=ver_label,
            extra={"signer_name": signer_name, "title": doc.title}
        )

        return {
            "message": f"Surat Keterangan Kematian ({ver_label}) berhasil ditandatangani secara elektronik oleh {signer_name}!",
            "tte_status": "SIGNED_BSRE",
            "version": new_version,
            "version_label": ver_label,
            "document_id": doc.id,
            "preview_url": f"/api/v1/document/{doc.id}/view",
            "download_url": f"/api/v1/document/{doc.id}/download",
            "verify_url": f"/api/v1/tte/{doc.id}/verify",
            "data": doc
        }

    inbox_action = f"REVISE_TO_INBOX_TTE ({ver_label})" if was_signed else f"SEND_TO_INBOX_TTE ({ver_label})"
    audit_service.log(
        db=db,
        document_id=doc.id,
        user_id=uploader_id,
        username=signer_name,
        user_role="E-RM",
        action=inbox_action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={
            "version": ver_label,
            "noreg": req.noreg,
            "nomor_dokumen": nomor_surat,
            "target_signer": signer_name
        }
    )

    msg = (
        f"Revisi {ver_label} Surat Keterangan Kematian ({nomor_surat}) berhasil dikirim ke Inbox TTE ({signer_name}) untuk di-TTE ulang."
        if was_signed
        else f"Surat Keterangan Kematian ({nomor_surat}) berhasil dikirim ke Inbox TTE ({signer_name})."
    )

    # Broadcast WebSocket ke SIMRS Web & Mobile App (Pending/Inbox)
    dispatch_ws_event(
        event_type="DOCUMENT_PENDING",
        noreg=req.noreg,
        document_id=doc.id,
        version_label=ver_label,
        extra={"target_signer": signer_name, "title": doc.title}
    )

    return {
        "message": msg,
        "tte_status": "UNSIGNED",
        "version": new_version,
        "version_label": ver_label,
        "document_id": doc.id,
        "preview_url": f"/api/v1/document/{doc.id}/view",
        "download_url": f"/api/v1/document/{doc.id}/download",
        "data": doc
    }


@router.post("/ranap/pulangkan-pasien")
def pulangkan_pasien_ranap(
    req: PulangkanPasienRanapRequest,
    request: Request,
    db: Session = Depends(get_session)
):
    """
    Dipanggil otomatis dari SIMRS saat memulangkan pasien rawat inap:
    - Jika pasien pulang dalam keadaan meninggal (carakeluar == 'C003'):
      1. Ambil data terbaru dari MySQL SIMRS + payload request.
      2. Jika dokumen SUDAH DI-TTE (SIGNED_BSRE):
         - Cek apakah ada perubahan data (jam meninggal, diagnosa, no surat, atau dokter).
         - Jika TIDAK ada perubahan: Tidak perlu kirim ke Inbox lagi (ALREADY_SIGNED).
         - Jika ADA perubahan data: Otomatis buat Revisi baru (v2.0+) dan masukkan ke Inbox TTE!
      3. Jika BELUM DI-TTE: Otomatis buat/perbarui draft PDF di Inbox TTE.
    """
    is_meninggal = (
        (req.carakeluar and req.carakeluar.upper() == "C003") or
        (req.keadaan_keluar and "MENINGGAL" in req.keadaan_keluar.upper())
    )

    if not is_meninggal:
        return {
            "success": True,
            "status": "NOT_DECEASED",
            "message": "Pasien dipulangkan bukan dalam kondisi meninggal. Tidak ada pengiriman Surat Kematian ke Inbox TTE.",
            "is_inbox_sent": False
        }

    kunjungan_id = _extract_numeric_id(req.noreg, 50999)

    existing_doc = db.exec(
        select(Document).where(
            Document.document_type == "surat_kematian",
            Document.kunjungan_id == kunjungan_id
        ).order_by(Document.uploaded_at.desc())
    ).first()

    # Ambil data lengkap dari MySQL SIMRS berdasarkan noreg lalu gabungkan dengan input terbaru
    mysql_rec = None
    try:
        records = simrs_mysql_service.fetch_surat_kematian_ranap(limit=5, search=req.noreg)
        for r in records:
            if r.get("noreg") == req.noreg:
                mysql_rec = r
                break
        if not mysql_rec and records:
            mysql_rec = records[0]
    except Exception:
        mysql_rec = None

    if mysql_rec:
        pasien_id = mysql_rec["pasien_id"]
        norm_val = mysql_rec["norm"]
        nama_pasien = mysql_rec["pasien"].get("nama") or req.nama_pasien or "Pasien Ranap"
        nomor_surat = req.nosrtmeninggal or mysql_rec.get("nosrtmeninggal") or f"472.12/{str(kunjungan_id)[-4:]}/425.102.8/KEM/X/2026"
        signer_name = (req.dpjp or {}).get("nama") or mysql_rec["dokter"].get("nama") or "dr. RIA NURMALA SETYANINGRUM"
        signer_nip = (req.dpjp or {}).get("nip") or mysql_rec["dokter"].get("nip") or ""
        signer_nik = (req.dpjp or {}).get("nik") or mysql_rec["dokter"].get("nik") or settings.BSRE_DEV_NIK
        content_payload = dict(mysql_rec)
        if req.nosrtmeninggal:
            content_payload["nosrtmeninggal"] = req.nosrtmeninggal
            content_payload["nomor_surat"] = req.nosrtmeninggal
        if req.jamMeninggal:
            content_payload["jamMeninggal"] = req.jamMeninggal
            content_payload["jam_meninggal"] = req.jamMeninggal
        if req.diagnosa and req.diagnosa != "-":
            content_payload["diagnosa"] = req.diagnosa
            content_payload["sebabkematian_ket"] = req.diagnosa
    else:
        norm_val = req.norm or "000000"
        pasien_id = _extract_numeric_id(norm_val, 280999)
        pasien_dict = req.pasien or {}
        dpjp_dict = req.dpjp or {}
        nama_pasien = req.nama_pasien or pasien_dict.get("nama_panggil") or pasien_dict.get("nama") or "Pasien Ranap"
        nomor_surat = req.nosrtmeninggal or f"472.12/{str(kunjungan_id)[-4:]}/425.102.8/KEM/X/2026"
        signer_name = dpjp_dict.get("nama") or "dr. RIA NURMALA SETYANINGRUM"
        signer_nip = dpjp_dict.get("nip") or ""
        signer_nik = settings.BSRE_DEV_NIK
        content_payload = {
            "kunjungan_id": kunjungan_id,
            "noreg": req.noreg,
            "norm": norm_val,
            "judul": "SURAT KETERANGAN KEMATIAN",
            "nosrtmeninggal": nomor_surat,
            "nomor_surat": nomor_surat,
            "tgl_meninggal": req.tglkeluar or datetime.now().strftime("%d %B %Y"),
            "jamMeninggal": req.jamMeninggal or "00:00",
            "jam_meninggal": req.jamMeninggal or "00:00",
            "diagnosa": req.diagnosa or "-",
            "sebabkematian_ket": req.diagnosa or "-",
            "pasien": {
                "noreg": req.noreg,
                "norm": norm_val,
                "nama": nama_pasien,
                "nama_panggil": nama_pasien,
                **pasien_dict
            },
            "dpjp": {
                "nama": signer_name,
                "nip": signer_nip,
                **dpjp_dict
            },
            "dokter": {
                "nama": signer_name,
                "nip": signer_nip,
                "nik": signer_nik,
                "golongan": dpjp_dict.get("golongan", ""),
                "ket_golongan": dpjp_dict.get("ket_golongan", ""),
                "ket_jabatan": dpjp_dict.get("ket_jabatan", "Dokter")
            }
        }

    # Jika sudah SIGNED_BSRE, cek apakah ada perubahan data dibanding versi yang telah di-TTE
    if existing_doc and existing_doc.tte_status == "SIGNED_BSRE":
        old_fp = ""
        if existing_doc.metadata_json:
            try:
                old_meta = json.loads(existing_doc.metadata_json)
                old_fp = old_meta.get("data_fingerprint") or _build_data_fingerprint(old_meta)
            except Exception:
                old_fp = ""
        new_fp = _build_data_fingerprint(content_payload)
        if old_fp and old_fp == new_fp:
            return {
                "success": True,
                "status": "ALREADY_SIGNED",
                "message": f"Dokumen Surat Kematian ({existing_doc.title}) sudah berstatus Sah TTE BSrE dan tidak ada perubahan data.",
                "document_id": existing_doc.id,
                "tte_status": "SIGNED_BSRE",
                "is_inbox_sent": False,
                "data": existing_doc
            }

    new_version, revision_history, was_signed = _prepare_versioned_payload(existing_doc, content_payload)
    ver_label = f"v{new_version}.0"

    doc_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", "ranap_kematian", str(kunjungan_id))
    os.makedirs(doc_dir, exist_ok=True)
    filename = f"SURAT_KEMATIAN_RANAP_{kunjungan_id}_{pasien_id}_v{new_version}_{uuid.uuid4().hex[:5]}.pdf"
    file_path = os.path.join(doc_dir, filename)

    pdf_service.generate_surat_kematian_pdf(content_payload, file_path, is_signed=False)
    file_size = os.path.getsize(file_path)
    doc_hash = bsre_service.calculate_file_hash(file_path)
    search_text = f"Surat Keterangan Kematian Ranap {nama_pasien} RM:{norm_val} Noreg:{req.noreg} Diagnosa:{content_payload.get('diagnosa', '')} Dokter:{signer_name}"
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
        doc.uploaded_at = datetime.now(timezone.utc)
        doc.description = f"No. Surat: {nomor_surat} • Noreg: {req.noreg} • Dokter: {signer_name} ({ver_label})"
        doc.target_signer_name = signer_name
        doc.target_signer_nip = signer_nip or signer_nik
        doc.metadata_json = json.dumps(content_payload)
        doc.pdf_hash = doc_hash
        doc.tte_status = "UNSIGNED"
        doc.status = "pending"
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
            description=f"No. Surat: {nomor_surat} • Noreg: {req.noreg} • Dokter: {signer_name} ({ver_label})",
            file_size=file_size,
            target_signer_nip=signer_nip or signer_nik,
            target_signer_name=signer_name,
            tte_status="UNSIGNED",
            pdf_hash=doc_hash,
            metadata_json=json.dumps(content_payload),
            embedding=embed
        )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    action_label = f"REVISE_TO_INBOX_TTE ({ver_label})" if was_signed else f"SEND_TO_INBOX_TTE ({ver_label})"
    audit_service.log(
        db=db,
        document_id=doc.id,
        user_id=uploader_id,
        username=signer_name,
        user_role="E-RM",
        action=action_label,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={
            "version": ver_label,
            "noreg": req.noreg,
            "nomor_dokumen": nomor_surat,
            "target_signer": signer_name,
            "reason": "Perubahan data kepulangan/surat kematian di E-RM" if was_signed else "Pulangkan pasien meninggal (C003)"
        }
    )

    notif_title = f"Revisi {ver_label} Surat Kematian Masuk ke Inbox TTE" if was_signed else "Surat Kematian Masuk ke Inbox TTE"
    notif_msg = (
        f"Data Surat Kematian pasien {nama_pasien} (RM: {norm_val}) diperbarui di E-RM. Draft Revisi {ver_label} menunggu TTE ulang."
        if was_signed
        else f"Pasien {nama_pasien} (RM: {norm_val}) dipulangkan meninggal. Surat Kematian otomatis masuk ke Inbox TTE."
    )
    notif = UserNotification(
        user_id=uploader_id,
        title=notif_title,
        message=notif_msg,
        document_id=doc.id,
        is_read=False
    )
    db.add(notif)
    db.commit()

    # Broadcast WebSocket ke SIMRS Web & Mobile App (Pending/Inbox via Pulangkan Pasien)
    dispatch_ws_event(
        event_type="DOCUMENT_PENDING",
        noreg=req.noreg,
        document_id=doc.id,
        version_label=ver_label,
        extra={"target_signer": signer_name, "title": doc.title}
    )

    return {
        "success": True,
        "status": "REVISED_TO_INBOX" if was_signed else "SENT_TO_INBOX",
        "version": new_version,
        "version_label": ver_label,
        "message": (
            f"Perubahan data terdeteksi! Revisi {ver_label} Surat Keterangan Kematian ({nama_pasien}) otomatis dikirim ke Inbox TTE ({signer_name})."
            if was_signed
            else f"Surat Keterangan Kematian pasien {nama_pasien} otomatis dikirim ke Inbox TTE ({signer_name})."
        ),
        "document_id": doc.id,
        "tte_status": "UNSIGNED",
        "is_inbox_sent": True,
        "data": doc
    }
