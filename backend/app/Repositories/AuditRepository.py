from sqlmodel import Session, select
from app.Models.DocumentAuditLog import DocumentAuditLog
from typing import List

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_document(self, document_id: int) -> List[DocumentAuditLog]:
        query = select(DocumentAuditLog).where(DocumentAuditLog.document_id == document_id).order_by(DocumentAuditLog.created_at.desc())
        return self.db.exec(query).all()

    def get_recent(self, limit: int = 50) -> List[DocumentAuditLog]:
        query = select(DocumentAuditLog).order_by(DocumentAuditLog.created_at.desc()).limit(limit)
        return self.db.exec(query).all()
