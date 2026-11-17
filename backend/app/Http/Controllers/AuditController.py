from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import csv
import io
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

@router.get("/export")
def export_audit_trail_csv(
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="ALL"),
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Ekspor Rekapitulasi Audit Trail Aktivitas Dokumen & TTE BSrE ke format CSV (Excel-Compatible).
    Mencakup rincian penandatanganan, unduhan (ke-berapa), cetakan (ke-berapa), dan alasan bila gagal.
    """
    repo = AuditRepository(db)
    data = repo.get_enriched_audit_trail(limit=limit, search=search, action_filter=status)

    output = io.StringIO()
    # Tulis UTF-8 BOM agar Excel membukanya langsung dengan karakter rapi
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    # Header Kolom Laporan
    writer.writerow([
        "No Log",
        "Waktu Kejadian",
        "Aksi / Aktivitas",
        "Status",
        "Iterasi / Keterangan",
        "Judul Dokumen",
        "Nomor Surat",
        "Nama Pasien",
        "No. RM",
        "User Pelaksana",
        "Role / Jabatan",
        "Alamat IP",
        "Keterangan / Alasan Gagal / ID BSrE"
    ])

    for item in data:
        details = item.get("details") or {}
        iterasi = details.get("keterangan") or ""
        if not iterasi:
            if item.get("action") == "DOWNLOAD" and details.get("iteration"):
                iterasi = f"Unduhan ke-{details.get('iteration')}"
            elif item.get("action") == "PRINT" and details.get("iteration"):
                iterasi = f"Cetakan ke-{details.get('iteration')}"

        ket_tambahan = item.get("alasan_gagal") or details.get("bsre_id") or details.get("catatan") or "-"

        writer.writerow([
            item.get("id"),
            item.get("created_at") or "-",
            item.get("action") or "-",
            item.get("status") or "-",
            iterasi or "-",
            item.get("document_title") or "-",
            item.get("nomor_surat") or "-",
            item.get("nama_pasien") or "-",
            item.get("norm") or "-",
            item.get("username") or "-",
            item.get("user_role") or "-",
            item.get("ip_address") or "-",
            ket_tambahan
        ])

    csv_data = output.getvalue()
    filename = f"Rekap_Audit_Trail_RSUD_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_data.encode('utf-8-sig'),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
