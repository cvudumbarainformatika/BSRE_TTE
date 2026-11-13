from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Dict, Any, Optional
from config.database import get_session
from app.Models.User import User
from app.Models.DocumentAuditLog import DocumentAuditLog
from app.Repositories.AuditRepository import AuditRepository
from app.Http.Middleware.AuthMiddleware import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("/document/{document_id}", response_model=List[DocumentAuditLog])
def get_document_audit_trail(
    document_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Mengambil jejak audit lengkap sebuah dokumen"""
    repo = AuditRepository(db)
    return repo.get_by_document(document_id)

@router.get("/recent", response_model=List[DocumentAuditLog])
def get_recent_audits(
    limit: int = 50,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Mengambil aktivitas audit terbaru di sistem (Model mentah)"""
    repo = AuditRepository(db)
    return repo.get_recent(limit)

@router.get("/trail")
def get_full_audit_trail(
    limit: int = Query(default=100, ge=1, le=500),
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="ALL"), # ALL, SUCCESS, FAILED, TTE_ONLY
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar Log Audit Trail lengkap sesuai kriteria Zoom Kominfo & BSSN:
    1. Tanggal & waktu transaksi TTE
    2. Nama user penandatangan / pemohon
    3. Keterangan status (BERHASIL / GAGAL)
    4. Identitas dokumen (Judul, No. Surat, Nama Pasien, No. RM)
    5. Alasan bila gagal
    """
    repo = AuditRepository(db)
    data = repo.get_enriched_audit_trail(limit=limit, search=search, action_filter=status)
    return {
        "status": "success",
        "total": len(data),
        "data": data
    }
