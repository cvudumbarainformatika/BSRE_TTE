from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Column as SAColumn, Text, BigInteger

class DocumentAuditLog(SQLModel, table=True):
    __tablename__ = "document_audit_logs"

    id: Optional[int] = Field(
        default=None, 
        sa_column=SAColumn(BigInteger, primary_key=True, autoincrement=True)
    )
    document_id: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    user_id: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    username: str = Field(max_length=50)
    user_role: str = Field(max_length=50)
    action: str = Field(max_length=50, index=True) # UPLOAD, VIEW, DOWNLOAD, APPROVE, SIGN_TTE, VERIFY_TTE, DELETE
    ip_address: Optional[str] = Field(default=None, max_length=50)
    user_agent: Optional[str] = Field(default=None, max_length=255)
    details: Optional[str] = Field(default=None, sa_column=SAColumn(Text, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

class TteSignature(SQLModel, table=True):
    __tablename__ = "tte_signatures"

    id: Optional[int] = Field(
        default=None, 
        sa_column=SAColumn(BigInteger, primary_key=True, autoincrement=True)
    )
    document_id: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    bsre_request_id: str = Field(max_length=100, index=True)
    signer_nip: str = Field(max_length=50)
    signer_name: str = Field(max_length=255)
    signer_role: str = Field(max_length=50)
    signed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    certificate_issuer: Optional[str] = Field(default="BSRE BSSN", max_length=255)
    certificate_serial: Optional[str] = Field(default=None, max_length=100)
    signature_hash: Optional[str] = Field(default=None, max_length=255)
    qr_verify_url: Optional[str] = Field(default=None, max_length=512)
    status: str = Field(default="SUCCESS", max_length=50)

class DocumentTemplate(SQLModel, table=True):
    __tablename__ = "document_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=50)
    name: str = Field(max_length=255)
    category: str = Field(default="medis", max_length=100)
    description: Optional[str] = Field(default=None)
    html_template: Optional[str] = Field(default=None, sa_column=SAColumn(Text, nullable=True))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
