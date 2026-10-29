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
from app.Services.WebSocketService import dispatch_ws_event
from app.Http.Middleware.AuthMiddleware import get_current_user, require_roles
from app.Http.Requests.DocumentRequests import TteSignRequest, BatchTteSignRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tte", tags=["TTE BSRE"])


@router.get("/pending-my-documents")
def get_pending_my_documents(
    document_type: Optional[str] = None,
    target_signer: Optional[str] = None,
    auto_sync_mysql: bool = False,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar dokumen global yang belum ditandatangani (TTE BSRE).
    Dapat difilter berdasarkan jenis dokumen (document_type) maupun
    pejabat/dokter penandatangan tujuan (target_signer).
    """
    if auto_sync_mysql:
        try:
            simrs_mysql_service.sync_surat_kematian_to_postgres(db, limit=15)
        except Exception as e:
            logger.warning(f"Auto-sync MySQL SIMRS dilewati: {e}")

    all_pending = db.exec(
        select(Document)
        .where(Document.tte_status != "SIGNED_BSRE")
        .order_by(Document.uploaded_at.desc())
    ).all()

    type_counts = defaultdict(int)
    signer_counts = defaultdict(int)
    for doc in all_pending:
        type_counts[doc.document_type] += 1
        s_name = doc.target_signer_name or "Belum Ditentukan"
        signer_counts[s_name] += 1

    filtered_items = all_pending
    if document_type:
        filtered_items = [d for d in filtered_items if d.document_type == document_type]
    if target_signer:
        filtered_items = [d for d in filtered_items if (d.target_signer_name or "Belum Ditentukan") == target_signer]

    return {
        "total_pending": len(all_pending),
        "filtered_count": len(filtered_items),
        "summary_by_type": dict(type_counts),
        "summary_by_signer": dict(signer_counts),
        "signer_info": {
            "nama": current_user.nama,
            "nip": current_user.nip
        },
        "data": filtered_items
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

    if not req.passphrase or len(req.passphrase.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Otorisasi BSrE Gagal: Passphrase BSrE wajib diisi."
        )

    docs = db.exec(
        select(Document).where(
            Document.id.in_(req.document_ids),
            Document.tte_status != "SIGNED_BSRE"
        )
    ).all()

    if not docs:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan atau sudah ditandatangani sebelumnya.")

    nip = current_user.nip or ""
    nama = current_user.nama
    execution_time = datetime.now(timezone.utc)
    qr_dir = os.path.join(settings.BASE_STORAGE_PATH, "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    success_list = []
    failed_list = []
    last_signer_name = nama
    last_signer_nip = nip

    for doc in docs:
        try:
            if not os.path.exists(doc.storage_path):
                failed_list.append({"id": doc.id, "error": "File PDF fisik dokumen tidak ditemukan di server storage."})
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
            effective_signer_nip = doc.target_signer_nip or nip

            # Ambil NIK asli dokter penandatangan dari metadata dokumen E-RM
            doc_signer_nik = None
            if meta_payload:
                dok_obj = meta_payload.get("dokter") or meta_payload.get("dpjp") or {}
                doc_signer_nik = dok_obj.get("nik")
            effective_signer_nik = doc_signer_nik or (settings.BSRE_DEV_NIK if settings.BSRE_MOCK_MODE else current_user.nik)

            last_signer_name = effective_signer_name
            last_signer_nip = effective_signer_nip

            sign_result = bsre_service.sign_document(
                input_pdf_path=orig_pdf_path,
                output_pdf_path=signed_path,
                signer_name=effective_signer_name,
                signer_nik=effective_signer_nik,
                signer_nip=effective_signer_nip,
                doc_id=doc.id,
                passphrase=req.passphrase.strip(),
                metadata_payload=meta_payload
            )

            qr_path = os.path.join(qr_dir, f"qr_doc_{doc.id}.png")
            verify_url = bsre_service.generate_qr_verification(
                doc.id,
                effective_signer_nik or effective_signer_nip,
                effective_signer_name,
                qr_path,
                metadata_payload=meta_payload
            )

            doc.original_path = orig_pdf_path
            doc.storage_path = signed_path
            doc.filename = signed_filename
            doc.tte_status = "SIGNED_BSRE"
            doc.tte_bsre_id = sign_result["bsre_id"]
            doc.tte_signed_at = execution_time
            doc.tte_signer_nip = effective_signer_nip
            doc.tte_signer_name = effective_signer_name
            doc.qr_code_path = qr_path
            doc.pdf_hash = sign_result["pdf_hash"]
            doc.status = "signed"

            db.add(doc)

            sig_record = TteSignature(
                document_id=doc.id,
                bsre_request_id=sign_result["bsre_id"],
                signer_nip=effective_signer_nip or "TERVERIFIKASI",
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
                username=effective_signer_name,
                user_role="Penandatangan TTE",
                action="SIGN_TTE_BSRE",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details={
                    "bsre_id": sign_result["bsre_id"],
                    "signer_name": effective_signer_name,
                    "signer_nip": effective_signer_nip,
                    "catatan": req.catatan or "Ditandatangani secara elektronik (TTE BSrE BSSN)"
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

    # Broadcast WebSocket ke SIMRS Web, Mobile React Native, dan SSO
    for sid in success_list:
        signed_doc = repo.get_by_id(sid)
        if signed_doc:
            doc_noreg = signed_doc.kunjungan_id
            ver_label = "v1.0"
            if signed_doc.metadata_json:
                try:
                    meta_obj = json.loads(signed_doc.metadata_json)
                    ver_label = f"v{meta_obj.get('version', 1)}.0"
                except Exception:
                    pass
            dispatch_ws_event(
                event_type="DOCUMENT_SIGNED",
                noreg=doc_noreg,
                document_id=signed_doc.id,
                version_label=ver_label,
                extra={"signer_name": last_signer_name, "title": signed_doc.title}
            )

    return {
        "message": f"Berhasil menandatangani {len(success_list)} dokumen secara elektronik via BSrE BSSN.",
        "signed_count": len(success_list),
        "failed_count": len(failed_list),
        "signed_at": execution_time.isoformat(),
        "signer": {
            "name": last_signer_name,
            "nip": last_signer_nip
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
        err_reason = "Gagal menandatangani dokumen dengan BSrE BSSN."
        if batch_res.get("failed_details"):
            err_reason = batch_res["failed_details"][0].get("error") or err_reason
        raise HTTPException(status_code=400, detail=err_reason)
    return {
        "message": f"Dokumen berhasil ditandatangani secara elektronik oleh {batch_res['signer']['name']} via BSrE BSSN.",
        "data": batch_res
    }


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
