from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from config.database import get_session
from app.Models.User import User
from app.Models.Notification import UserNotification
from app.Http.Middleware.AuthMiddleware import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/my")
def get_my_notifications(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Mengambil daftar notifikasi untuk user saat ini"""
    query = select(UserNotification).where(
        (UserNotification.user_id == current_user.id) |
        (UserNotification.user_nip == current_user.nip)
    ).order_by(UserNotification.created_at.desc())
    
    notifications = db.exec(query).all()
    unread_count = sum(1 for n in notifications if not n.is_read)
    
    return {
        "unread_count": unread_count,
        "notifications": notifications
    }

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Mengambil jumlah notifikasi belum dibaca untuk badge merah di navbar"""
    query = select(UserNotification).where(
        ((UserNotification.user_id == current_user.id) | (UserNotification.user_nip == current_user.nip)),
        UserNotification.is_read == False
    )
    items = db.exec(query).all()
    total_pending_docs = sum(item.pending_count for item in items) if items else 0
    return {
        "unread_notifications": len(items),
        "total_pending_docs": total_pending_docs
    }

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Tandai notifikasi telah dibaca"""
    notif = db.get(UserNotification, notification_id)
    if notif and (notif.user_id == current_user.id or notif.user_nip == current_user.nip):
        notif.is_read = True
        db.add(notif)
        db.commit()
    return {"success": True}
