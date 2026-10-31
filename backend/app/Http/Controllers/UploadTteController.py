import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select
import pypdf

from config.database import get_session
from config.settings import settings
from app.Models.Document import Document
from app.Models.User import User
from app.Models.DocumentAuditLog import TteSignature
from app.Services.DocumentConverterService import converter_service
from app.Services.BsreTteService import bsre_service
from app.Services.AuditService import audit_service
from app.Services.VectorSearchService import vector_service
from app.Services.WebSocketService import dispatch_ws_event
from app.Http.Middleware.AuthMiddleware import get_current_user

logger = logging.getLogger("simrs_tte.upload_tte")
router = APIRouter(prefix="/upload-tte", tags=["Upload & TTE Interaktif"])

TEMP_UPLOAD_DIR = os.path.join(settings.BASE_STORAGE_PATH, "temp", "upload_tte")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".epub"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

@router.post("/convert-preview")
async def convert_and_preview(
    file: UploadFile = File(...)
):
    """
    Menerima berkas upload (PDF, DOCX, DOC, EPUB), mengonversi ke PDF jika diperlukan,
    dan menghasilkan info dimensi halaman serta preview gambar untuk kanvas drag & drop stempel.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format berkas '{ext}' tidak didukung. Format yang didukung: PDF, Word (.docx/.doc), EPUB (.epub)."
        )

    upload_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_UPLOAD_DIR, upload_id)
    os.makedirs(session_dir, exist_ok=True)

    input_path = os.path.join(session_dir, f"original_{file.filename}")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran berkas melebihi batas maksimal 25 MB.")

    with open(input_path, "wb") as f:
        f.write(content)

    # Konversi ke PDF jika bukan PDF
    try:
        pdf_path = converter_service.convert_to_pdf(input_path, session_dir)
    except Exception as e:
        logger.error(f"Gagal konversi berkas: {e}")
        raise HTTPException(status_code=400, detail=f"Gagal memproses/mengonversi berkas: {str(e)}")

    # Ambil info halaman PDF
    pdf_info = converter_service.get_pdf_metadata_and_pages(pdf_path)
    total_pages = pdf_info.get("total_pages", 1)

    # Render gambar halaman 1 (dan siapkan direktori untuk halaman berikutnya)
    previews = []
    for p in range(1, total_pages + 1):
        png_filename = f"page_{p}.png"
        png_path = os.path.join(session_dir, png_filename)
        # Render halaman 1 segera, halaman lain dapat di-render on-demand
        if p == 1:
            converter_service.render_page_to_png(pdf_path, p, png_path)
        
        previews.append({
            "page_number": p,
            "width": pdf_info["pages"][p-1]["width"] if p-1 < len(pdf_info["pages"]) else 595.27,
            "height": pdf_info["pages"][p-1]["height"] if p-1 < len(pdf_info["pages"]) else 841.89,
            "preview_url": f"/api/v1/upload-tte/page-preview/{upload_id}/{p}"
        })

    # Simpan manifest sesi upload
    manifest = {
        "upload_id": upload_id,
        "original_filename": file.filename,
        "original_path": input_path,
        "pdf_path": pdf_path,
        "total_pages": total_pages,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    with open(os.path.join(session_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f)

    return {
        "upload_id": upload_id,
        "original_filename": file.filename,
        "total_pages": total_pages,
        "pages": previews,
        "first_page": previews[0] if previews else None
    }


@router.get("/page-preview/{upload_id}/{page_number}")
def get_page_preview(upload_id: str, page_number: int):
    """Mengalirkan gambar PNG pratinjau halaman PDF untuk kanvas interaktif"""
    session_dir = os.path.join(TEMP_UPLOAD_DIR, upload_id)
    manifest_path = os.path.join(session_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        raise HTTPException(status_code=404, detail="Sesi upload tidak ditemukan")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    pdf_path = manifest["pdf_path"]
    png_path = os.path.join(session_dir, f"page_{page_number}.png")

    if not os.path.exists(png_path):
        # Render on-demand
        converter_service.render_page_to_png(pdf_path, page_number, png_path)

    if not os.path.exists(png_path):
        raise HTTPException(status_code=500, detail="Gagal me-render pratinjau halaman PDF")

    return FileResponse(png_path, media_type="image/png")


@router.post("/process-sign")
async def process_upload_and_sign(
    request: Request,
    upload_id: str = Form(...),
    nomor_surat: Optional[str] = Form(None),
    perihal: Optional[str] = Form(None),
    kategori: str = Form("general"),
    tipe_stempel: str = Form("qr_only"),
    passphrase: str = Form(...),
    target_page: int = Form(1),
    x_percent: float = Form(70.0),      # Posisi X persentase dari kiri (0 - 100)
    y_percent: float = Form(80.0),      # Posisi Y persentase dari atas (0 - 100)
    width_percent: float = Form(12.0),  # Lebar QR Code persentase terhadap lebar halaman
    height_percent: float = Form(12.0), # Tinggi QR Code (disamakan dengan lebar agar 1:1 persegi)
    db: Session = Depends(get_session)
):
    """
    Eksekusi pembubuhan stempel TTE BSrE interaktif pada koordinat yang ditentukan oleh user,
    menerapkan digital signature, dan menyimpan berkas ke repositori arsip permanen.
    """
    session_dir = os.path.join(TEMP_UPLOAD_DIR, upload_id)
    manifest_path = os.path.join(session_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        raise HTTPException(status_code=404, detail="Sesi berkas upload tidak ditemukan atau telah kedaluwarsa.")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    input_pdf_path = manifest["pdf_path"]
    original_filename = manifest["original_filename"]

    # Fallback nomor_surat & perihal jika dikosongkan pengguna
    nomor_surat = nomor_surat.strip() if (nomor_surat and nomor_surat.strip()) else "-"
    if not perihal or not perihal.strip():
        perihal = os.path.splitext(original_filename)[0].replace("_", " ").strip()

    # Validasi Passphrase
    if not passphrase or len(passphrase.strip()) < 3:
        raise HTTPException(status_code=400, detail="Otorisasi BSrE Gagal: Passphrase tidak boleh kosong.")

    # Tentukan penandatangan default (misal Dr. Hendra Wijaya / Dokter akun aktif)
    signer_name = "Dr. Hendra Wijaya"
    signer_nip = "198203102005011002"
    signer_nik = settings.BSRE_DEV_NIK if settings.BSRE_MOCK_MODE else "3508152612570002"

    if settings.BSRE_MOCK_MODE and passphrase.strip() != settings.BSRE_DEV_PASSPHRASE:
        raise HTTPException(
            status_code=400,
            detail=f"Otorisasi BSrE Gagal: Passphrase BSrE yang Anda masukkan salah untuk penandatangan {signer_name}."
        )

    # Baca dimensi halaman PDF target
    reader = pypdf.PdfReader(input_pdf_path)
    total_pages = len(reader.pages)
    if target_page < 1 or target_page > total_pages:
        target_page = total_pages

    page_obj = reader.pages[target_page - 1]
    page_w = float(page_obj.mediabox.width)
    page_h = float(page_obj.mediabox.height)

    # Konversi persentase ke koordinat point PDF (Sumbu Y PDF dimulai dari bawah ke atas)
    # Stempel QR selalu bujursangkar (1:1 aspect ratio) proporsional terhadap lebar halaman
    stamp_dim = (width_percent / 100.0) * page_w
    stamp_w = stamp_dim
    stamp_h = stamp_dim

    stamp_x = (x_percent / 100.0) * page_w
    # y_percent diukur dari ATAS halaman pada kanvas browser:
    stamp_y = page_h - ((y_percent / 100.0) * page_h) - stamp_h

    # Batasi agar tidak keluar kanvas
    stamp_x = max(10, min(stamp_x, page_w - stamp_w - 10))
    stamp_y = max(10, min(stamp_y, page_h - stamp_h - 10))

    # Direktori arsip permanen
    doc_id = int(str(uuid.uuid4().int)[:7])
    perm_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", "mandiri", str(doc_id))
    os.makedirs(perm_dir, exist_ok=True)
    
    clean_title = perihal.replace("/", "_").replace("\\", "_")
    output_pdf_filename = f"SIGNED_{clean_title}_{doc_id}.pdf"
    output_pdf_path = os.path.join(perm_dir, output_pdf_filename)

    # Metadata payload
    content_payload = {
        "judul": perihal,
        "nomor_surat": nomor_surat,
        "kategori": kategori,
        "tipe_stempel": tipe_stempel,
        "original_filename": original_filename,
        "target_page": target_page,
        "stamp_coords": {
            "x": stamp_x,
            "y": stamp_y,
            "w": stamp_w,
            "h": stamp_h,
            "page": target_page
        },
        "signer": {
            "nama": signer_name,
            "nip": signer_nip,
            "nik": signer_nik
        }
    }

    # Pembubuhan Stempel Visual dan TTE BSrE
    try:
        sign_res = bsre_service.stamp_custom_coordinate(
            input_pdf_path=input_pdf_path,
            output_pdf_path=output_pdf_path,
            signer_name=signer_name,
            signer_nip=signer_nip,
            signer_nik=signer_nik,
            doc_id=doc_id,
            target_page=target_page,
            x_point=stamp_x,
            y_point=stamp_y,
            width_point=stamp_w,
            height_point=stamp_h,
            stamp_type=tipe_stempel,
            metadata_payload=content_payload
        )
    except Exception as e:
        logger.error(f"Gagal melakukan stempel TTE: {e}")
        raise HTTPException(status_code=400, detail=f"Gagal menandatangani dokumen: {str(e)}")

    file_size = os.path.getsize(output_pdf_path)
    doc_hash = sign_res.get("pdf_hash") or bsre_service.calculate_file_hash(output_pdf_path)

    # Simpan ke tabel Document
    doc_record = Document(
        id=doc_id,
        kunjungan_id=doc_id,
        pasien_id=0,
        document_type=kategori,
        title=perihal,
        filename=output_pdf_filename,
        storage_path=output_pdf_path,
        original_path=input_pdf_path,
        uploaded_by=1,
        uploaded_at=datetime.now(timezone.utc),
        approved_by=1,
        approved_at=datetime.now(timezone.utc),
        status="signed",
        description=f"No. Dokumen: {nomor_surat} • Penandatangan: {signer_name}",
        file_size=file_size,
        target_signer_nip=signer_nip,
        target_signer_name=signer_name,
        is_notified=True,
        tte_status="SIGNED_BSRE",
        tte_bsre_id=sign_res.get("bsre_id"),
        tte_signed_at=datetime.now(timezone.utc),
        tte_signer_nip=signer_nip,
        tte_signer_name=signer_name,
        pdf_hash=doc_hash,
        metadata_json=json.dumps(content_payload)
    )
    db.add(doc_record)

    sig_record = TteSignature(
        document_id=doc_id,
        bsre_request_id=sign_res.get("bsre_id"),
        signer_nip=signer_nip,
        signer_name=signer_name,
        signer_role="pejabat",
        signed_at=doc_record.tte_signed_at,
        certificate_issuer="Balai Sertifikasi Elektronik (BSrE) - BSSN RI",
        certificate_serial=sign_res.get("certificate_serial", f"BSSN-{uuid.uuid4().hex[:8].upper()}"),
        signature_hash=doc_hash,
        qr_verify_url=sign_res.get("verify_url"),
        status="SUCCESS"
    )
    db.add(sig_record)
    db.commit()
    db.refresh(doc_record)

    # Audit Trail
    audit_service.log(
        db=db,
        document_id=doc_id,
        user_id=1,
        username=signer_name,
        user_role="Penandatangan TTE",
        action="SIGN_TTE_CUSTOM_UPLOAD",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={
            "nomor_surat": nomor_surat,
            "perihal": perihal,
            "target_page": target_page,
            "bsre_id": sign_res.get("bsre_id")
        }
    )

    # Siarkan WebSocket Real-Time
    dispatch_ws_event(
        event_type="DOCUMENT_SIGNED",
        noreg=doc_record.kunjungan_id,
        document_id=doc_id,
        version_label="v1.0",
        extra={"signer_name": signer_name, "title": doc_record.title}
    )

    return {
        "message": f"Dokumen '{perihal}' berhasil ditandatangani secara elektronik (BSrE BSSN)!",
        "document_id": doc_id,
        "tte_status": "SIGNED_BSRE",
        "preview_url": f"/api/v1/document/{doc_id}/view",
        "download_url": f"/api/v1/document/{doc_id}/download",
        "data": doc_record
    }
