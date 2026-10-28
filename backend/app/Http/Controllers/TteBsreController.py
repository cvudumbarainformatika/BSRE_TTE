import os
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Optional
from collections import defaultdict

from config.database import get_session
from config.settings import settings
from app.Models.User import User
from app.Models.Document import Document
from app.Models.DocumentAuditLog import TteSignature
from app.Models.Notification import UserNotification
from app.Repositories.DocumentRepository import DocumentRepository
from app.Services.BsreTteService import bsre_service
from app.Services.SimrsMysqlReadService import simrs_mysql_service
from app.Services.AuditService import audit_service
from app.Http.Middleware.AuthMiddleware import get_current_user, require_roles
from app.Http.Requests.DocumentRequests import TteSignRequest, BatchTteSignRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tte", tags=["TTE BSRE"])


@router.get("/pending-my-documents")
def get_pending_my_documents(
    document_type: Optional[str] = None,
    auto_sync_mysql: bool = False,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar dokumen yang belum ditandatangani (TTE BSRE)
    khusus milik user yang sedang login.
    Otomatis melakukan tarik data (Read-Only SELECT) dari MySQL SIMRS jika auto_sync_mysql=True.
    """
    if auto_sync_mysql:
        try:
            simrs_mysql_service.sync_surat_kematian_to_postgres(db, limit=15)
        except Exception as e:
            logger.warning(f"Auto-sync MySQL SIMRS dilewati: {e}")

    user_nip = current_user.nip
    query = select(Document).where(Document.tte_status != "SIGNED_BSRE")

    if current_user.role.value == "dokter" or str(current_user.role) == "dokter":
        if user_nip or current_user.nik:
            query = query.where(
                (Document.target_signer_nip == user_nip) |
                (Document.target_signer_nip == current_user.nik) |
                (Document.target_signer_nip == settings.BSRE_DEV_NIK) |
                (Document.target_signer_nip == None)
            )

    if document_type:
        query = query.where(Document.document_type == document_type)

    query = query.order_by(Document.uploaded_at.desc())
    items = db.exec(query).all()

    type_counts = defaultdict(int)
    for doc in items:
        type_counts[doc.document_type] += 1

    return {
        "total_pending": len(items),
        "summary_by_type": dict(type_counts),
        "signer_info": {
            "nama": current_user.nama,
            "nip": current_user.nip
        },
        "data": items
    }


@router.get("/user-status/{nik}")
async def check_bsre_user_status(nik: str):
    """Cek status sertifikat elektronik di BSrE BSSN"""
    return await bsre_service.check_user_status(nik)


@router.post("/batch-sign")
def batch_sign_documents(
    req: BatchTteSignRequest,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_roles(["dokter"]))
):
    """
    Tanda Tangan Banyak Dokumen Sekaligus (Batch Sign TTE BSRE):
    Menandatangani puluhan/ratusan dokumen dalam 1 kali otorisasi passphrase.
    """
    if not req.document_ids:
        raise HTTPException(status_code=400, detail="Pilih minimal 1 dokumen untuk ditandatangani.")

    signer_nik = current_user.nik or settings.BSRE_DEV_NIK
    if not req.passphrase or req.passphrase.strip() != settings.BSRE_DEV_PASSPHRASE:
        raise HTTPException(
            status_code=400,
            detail="Otorisasi BSrE Gagal: Passphrase BSrE yang Anda masukkan tidak sesuai."
        )

    docs = db.exec(
        select(Document).where(
            Document.id.in_(req.document_ids),
            Document.tte_status != "SIGNED_BSRE"
        )
    ).all()

    if not docs:
        raise HTTPException(status_code=404, detail="Tidak ada dokumen belum bertanda tangan yang ditemukan.")

    nip = current_user.nip or ""
    nama = current_user.nama
    execution_time = datetime.now(timezone.utc)
    qr_dir = os.path.join(settings.BASE_STORAGE_PATH, "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    success_list = []
    failed_list = []

    for doc in docs:
        try:
            if not os.path.exists(doc.storage_path):
                failed_list.append({"id": doc.id, "error": "File PDF fisik tidak ditemukan"})
                continue

            doc_dir = os.path.dirname(doc.storage_path)
            signed_filename = f"SIGNED_{doc.filename}" if not doc.filename.startswith("SIGNED_") else doc.filename
            signed_path = os.path.join(doc_dir, signed_filename)
            orig_pdf_path = doc.storage_path

            meta_payload = None
            if doc.metadata_json:
                try:
                    meta_payload = json.loads(doc.metadata_json)
                except Exception:
                    meta_payload = None

            effective_signer_name = doc.target_signer_name or nama

            sign_result = bsre_service.sign_document(
                input_pdf_path=orig_pdf_path,
                output_pdf_path=signed_path,
                signer_name=effective_signer_name,
                signer_nik=signer_nik,
                signer_nip=nip,
                doc_id=doc.id,
                passphrase=req.passphrase.strip(),
                metadata_payload=meta_payload
            )

            qr_path = os.path.join(qr_dir, f"qr_doc_{doc.id}.png")
            verify_url = bsre_service.generate_qr_verification(doc.id, signer_nik, effective_signer_name, qr_path, metadata_payload=meta_payload)

            doc.original_path = orig_pdf_path
            doc.storage_path = signed_path
            doc.filename = signed_filename
            doc.tte_status = "SIGNED_BSRE"
            doc.tte_bsre_id = sign_result["bsre_id"]
            doc.tte_signed_at = execution_time
            doc.tte_signer_nip = nip
            doc.tte_signer_name = effective_signer_name
            doc.qr_code_path = qr_path
            doc.pdf_hash = sign_result["pdf_hash"]
            doc.status = "signed"

            db.add(doc)

            sig_record = TteSignature(
                document_id=doc.id,
                bsre_request_id=sign_result["bsre_id"],
                signer_nip=nip or "TERVERIFIKASI",
                signer_name=effective_signer_name,
                signer_role="dokter",
                signed_at=execution_time,
                certificate_issuer=sign_result["certificate_issuer"],
                certificate_serial=sign_result["certificate_serial"],
                signature_hash=sign_result["pdf_hash"],
                qr_verify_url=verify_url,
                status="SUCCESS"
            )
            db.add(sig_record)

            audit_service.log(
                db=db,
                document_id=doc.id,
                user_id=current_user.id,
                username=current_user.username,
                user_role="dokter",
                action="BATCH_SIGN_TTE_BSRE",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details={
                    "batch_size": len(docs),
                    "bsre_id": sign_result["bsre_id"],
                    "signer_name": effective_signer_name
                }
            )

            success_list.append(doc.id)
        except Exception as e:
            failed_list.append({"id": doc.id, "error": str(e)})

    db.commit()

    unread_notifs = db.exec(
        select(UserNotification).where(
            (UserNotification.user_id == current_user.id) | (UserNotification.user_nip == nip),
            UserNotification.is_read == False
        )
    ).all()
    for n in unread_notifs:
        n.is_read = True
        db.add(n)
    db.commit()

    return {
        "message": f"Berhasil menandatangani {len(success_list)} dokumen secara elektronik via BSrE BSSN.",
        "signed_count": len(success_list),
        "failed_count": len(failed_list),
        "signed_at": execution_time.isoformat(),
        "signer": {
            "name": nama,
            "nip": nip
        },
        "success_ids": success_list,
        "failed_details": failed_list
    }


@router.post("/{document_id}/sign")
def sign_document_bsre(
    document_id: int,
    req: TteSignRequest,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_roles(["dokter"]))
):
    """Sign tunggal"""
    batch_res = batch_sign_documents(
        req=BatchTteSignRequest(document_ids=[document_id], passphrase=req.passphrase, catatan=req.catatan),
        request=request,
        db=db,
        current_user=current_user
    )
    if batch_res["signed_count"] == 0:
        raise HTTPException(status_code=400, detail="Gagal menandatangani dokumen.")
    return {"message": "Dokumen berhasil ditandatangani secara elektronik via BSRE BSSN.", "data": batch_res}


@router.get("/{document_id}/verify")
def verify_document_bsre(
    document_id: int,
    db: Session = Depends(get_session)
):
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    if doc.tte_status != "SIGNED_BSRE":
        return {
            "status": "UNSIGNED",
            "message": "Dokumen ini belum ditandatangani secara elektronik BSRE.",
            "document_id": doc.id,
            "title": doc.title
        }

    verification = bsre_service.verify_document(doc.storage_path, doc.pdf_hash)
    sig_record = db.exec(
        select(TteSignature).where(TteSignature.document_id == doc.id).order_by(TteSignature.signed_at.desc())
    ).first()

    return {
        "status": "VALID_BSRE" if verification["is_authentic"] else "TAMPERED",
        "document": {
            "id": doc.id,
            "title": doc.title,
            "kunjungan_id": doc.kunjungan_id,
            "pasien_id": doc.pasien_id,
            "document_type": doc.document_type
        },
        "signer": {
            "name": doc.tte_signer_name,
            "signed_at": doc.tte_signed_at,
        },
        "certificate": {
            "issuer": sig_record.certificate_issuer if sig_record else "Balai Sertifikasi Elektronik (BSRE) - BSSN",
            "sha256_hash": doc.pdf_hash
        },
        "integrity": verification
    }
