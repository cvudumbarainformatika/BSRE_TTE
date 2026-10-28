from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Column as SAColumn, BigInteger, Text

class UserNotification(SQLModel, table=True):
    __tablename__ = "user_notifications"

    id: Optional[int] = Field(
        default=None, 
        sa_column=SAColumn(BigInteger, primary_key=True, autoincrement=True)
    )
    user_id: int = Field(sa_column=SAColumn(BigInteger, nullable=False, index=True))
    user_nip: Optional[str] = Field(default=None, max_length=50, index=True)
    title: str = Field(max_length=255)
    message: str = Field(sa_column=SAColumn(Text, nullable=False))
    document_type: Optional[str] = Field(default=None, max_length=100)
    pending_count: int = Field(default=1)
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
