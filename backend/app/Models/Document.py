from sqlmodel import SQLModel, Field, Column
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column as SAColumn, Text, BigInteger

class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[int] = Field(
        default=None, 
        sa_column=SAColumn(BigInteger, primary_key=True, autoincrement=True)
    )
    kunjungan_id: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    pasien_id: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    document_type: str = Field(default="konsul_spesialis", max_length=100, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    filename: str = Field(max_length=255)
    storage_path: str = Field(max_length=512)
    original_path: Optional[str] = Field(default=None, max_length=512)
    
    uploaded_by: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    approved_by: Optional[int] = Field(default=None, sa_column=SAColumn(BigInteger, nullable=True))
    approved_at: Optional[datetime] = Field(default=None)
    
    # Status: pending, approved, rejected, signed
    status: str = Field(default="pending", max_length=20, index=True)
    description: Optional[str] = Field(default=None, sa_column=SAColumn(Text, nullable=True))
    file_size: Optional[int] = Field(default=0)
    
    # Target Penandatangan (Dokter / Nakes yang harus TTE)
    target_signer_nip: Optional[str] = Field(default=None, max_length=50, index=True)
    target_signer_name: Optional[str] = Field(default=None, max_length=255)
    is_notified: bool = Field(default=False)

    # TTE BSRE Specifics
    tte_status: str = Field(default="UNSIGNED", max_length=50, index=True)  # UNSIGNED, SIGNED_BSRE, VERIFIED_BSRE
    tte_bsre_id: Optional[str] = Field(default=None, max_length=100)
    tte_signed_at: Optional[datetime] = Field(default=None)
    tte_signer_nip: Optional[str] = Field(default=None, max_length=50)
    tte_signer_name: Optional[str] = Field(default=None, max_length=255)
    qr_code_path: Optional[str] = Field(default=None, max_length=512)
    pdf_hash: Optional[str] = Field(default=None, max_length=128)
    
    # Metadata Dokumen SIMRS (format JSON text)
    metadata_json: Optional[str] = Field(default=None, sa_column=SAColumn(Text, nullable=True))
    
    # Retensi Dokumen: Default 5 Tahun (Sesuai Permenkes No. 24 Tahun 2022)
    retention_until: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=365 * 5)
    )

    # pgvector embedding untuk similarity search
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=SAColumn(Vector(1536), nullable=True)
    )
