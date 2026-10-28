from sqlmodel import Session
from app.Models.DocumentAuditLog import DocumentAuditLog
from datetime import datetime, timezone
import json

class AuditService:
    @staticmethod
    def log(
        db: Session,
        document_id: int,
        user_id: int,
        username: str,
        user_role: str,
        action: str,
        ip_address: str = None,
        user_agent: str = None,
        details: dict = None
    ) -> DocumentAuditLog:
        """Mencatat aktivitas audit log dokumen"""
        details_str = json.dumps(details) if isinstance(details, dict) else str(details or "")
        audit = DocumentAuditLog(
            document_id=document_id,
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details_str,
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

audit_service = AuditService()
