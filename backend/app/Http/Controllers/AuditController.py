from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
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
    """Mengambil aktivitas audit terbaru di sistem"""
    repo = AuditRepository(db)
    return repo.get_recent(limit)
