import os
import uuid
import json
import aiofiles
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status
from fastapi.responses import FileResponse
from sqlmodel import Session
from typing import Optional

from config.database import get_session
from config.settings import settings
from app.Models.User import User, UserRole
from app.Models.Document import Document
from app.Repositories.DocumentRepository import DocumentRepository
from app.Services.VirusScanService import virus_scanner
from app.Services.PdfGeneratorService import pdf_service
from app.Services.BsreTteService import bsre_service
from app.Services.VectorSearchService import vector_service
from app.Services.AuditService import audit_service
from app.Http.Middleware.AuthMiddleware import get_current_user, require_roles
from app.Http.Requests.DocumentRequests import (
    DocumentGenerateSimrsRequest, DocumentApproveRequest, SemanticSearchRequest
)

router = APIRouter(prefix="/document", tags=["Documents"])

@router.post("/{kunjungan_id}/upload")
async def upload_document(
    kunjungan_id: int,
    request: Request,
    file: UploadFile = File(...),
    pasien_id: int = Form(...),
    document_type: str = Form("general"),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Upload dokumen baru:
    1. Validasi ekstensi (PDF only).
    2. Simpan sementara & Scan virus dengan ClamAV.
    3. Jika lolos, simpan ke storage permanen.
    4. Hitung hash & generate semantic vector embedding.
    5. Simpan ke database dengan retensi 5 tahun.
    6. Catat audit log.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format file tidak didukung. Hanya file PDF yang diperbolehkan."
        )

    # 1. Simpan ke storage sementara untuk scanning
    temp_dir = os.path.join(settings.BASE_STORAGE_PATH, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
    temp_path = os.path.join(temp_dir, temp_filename)

    async with aiofiles.open(temp_path, "wb") as f_out:
        while chunk := await file.read(1024 * 64):
            await f_out.write(chunk)

    # 2. Virus scan dengan ClamAV
    scan_result = virus_scanner.scan_file(temp_path)
    if not scan_result["is_clean"]:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File ditolak: {scan_result['message']}"
        )

    # 3. Pindahkan ke permanent storage
    doc_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", str(kunjungan_id))
    os.makedirs(doc_dir, exist_ok=True)
    final_filename = f"DOC_{kunjungan_id}_{pasien_id}_{uuid.uuid4().hex[:8]}.pdf"
    final_path = os.path.join(doc_dir, final_filename)
    os.rename(temp_path, final_path)

    # 4. Hitung hash dan file size
    file_size = os.path.getsize(final_path)
    pdf_hash = bsre_service.calculate_file_hash(final_path)

    # 5. Semantic vector embedding (pgvector)
    text_to_embed = f"{title or file.filename} {description or ''} {document_type} kunjungan:{kunjungan_id}"
    embedding_vec = vector_service.generate_embedding(text_to_embed)

    # 6. Simpan model Document
    doc = Document(
        kunjungan_id=kunjungan_id,
        pasien_id=pasien_id,
        document_type=document_type,
        title=title or file.filename,
        filename=final_filename,
        storage_path=final_path,
        original_path=file.filename,
        uploaded_by=current_user.id,
        uploaded_at=datetime.now(timezone.utc),
        status="pending",
        description=description,
        file_size=file_size,
        tte_status="UNSIGNED",
        pdf_hash=pdf_hash,
        embedding=embedding_vec
    )

    repo = DocumentRepository(db)
    saved_doc = repo.create(doc)

    # 7. Audit Log
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    audit_service.log(
        db=db,
        document_id=saved_doc.id,
        user_id=current_user.id,
        username=current_user.username,
        user_role=role_val,
        action="UPLOAD",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"filename": final_filename, "size": file_size, "virus_scan": scan_result}
    )

    return {
        "message": "Dokumen berhasil diunggah dan diverifikasi aman.",
        "data": saved_doc
    }

@router.post("/generate-simrs")
async def generate_simrs_document(
    req: DocumentGenerateSimrsRequest,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF resmi dari data SIMRS (seperti Lembar Konsultasi Dokter Spesialis RSUD Dr Mohammad Saleh).
    Mengonversi data JSON rekam medis menjadi PDF siap TTE dan cetak.
    """
    doc_dir = os.path.join(settings.BASE_STORAGE_PATH, "documents", str(req.kunjungan_id))
    os.makedirs(doc_dir, exist_ok=True)
    
    unique_suffix = uuid.uuid4().hex[:8]
    pdf_filename = f"KONSUL_{req.kunjungan_id}_{req.pasien_id}_{unique_suffix}.pdf"
    pdf_path = os.path.join(doc_dir, pdf_filename)

    # Siapkan data untuk generator
    simrs_data = {
        "pasien": req.pasien,
        "konsultasi": req.konsultasi,
        "jawaban": req.jawaban or {},
        "pengirim": req.pengirim or {
            "nama": current_user.nama,
            "nip": current_user.nip or "-",
            "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        },
        "konsulan": req.konsulan or {
            "nama": req.konsultasi.get("dokter_konsulan", "-"),
            "nip": "198304152011011003"
        }
    }

    # Generate file PDF
    pdf_service.generate_simrs_konsul_pdf(simrs_data, pdf_path)
    file_size = os.path.getsize(pdf_path)
    pdf_hash = bsre_service.calculate_file_hash(pdf_path)

    # Gabungkan teks untuk representasi semantik pgvector
    searchable_text = f"""
    Pasien: {req.pasien.get('nama', '')} NoRM: {req.pasien.get('norm', '')} Ruang: {req.pasien.get('ruangan', '')}
    Konsul: {req.konsultasi.get('ikhtisar_klinik', '')}
    Jawaban: {req.jawaban.get('pendapat_saran', '') if req.jawaban else ''}
    Dokter: {req.konsultasi.get('dokter_konsulan', '')} DPJP: {req.pasien.get('dokter_dpjp', '')}
    """
    embedding_vec = vector_service.generate_embedding(searchable_text)

    # Simpan ke DB
    doc = Document(
        kunjungan_id=req.kunjungan_id,
        pasien_id=req.pasien_id,
        document_type=req.document_type,
        title=req.title or "Lembar Konsultasi Dokter Spesialis Rawat Inap",
        filename=pdf_filename,
        storage_path=pdf_path,
        original_path="SIMRS_FRONTEND_GENERATOR",
        uploaded_by=current_user.id,
        uploaded_at=datetime.now(timezone.utc),
        status="pending" if not req.jawaban else "approved",
        description=f"Konsultasi untuk {req.pasien.get('nama')} - {req.konsultasi.get('dokter_konsulan')}",
        file_size=file_size,
        tte_status="UNSIGNED",
        pdf_hash=pdf_hash,
        metadata_json=json.dumps(simrs_data),
        embedding=embedding_vec
    )

    repo = DocumentRepository(db)
    saved_doc = repo.create(doc)

    # Audit log
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    audit_service.log(
        db=db,
        document_id=saved_doc.id,
        user_id=current_user.id,
        username=current_user.username,
        user_role=role_val,
        action="GENERATE_SIMRS_PDF",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"type": req.document_type, "pasien": req.pasien.get("nama")}
    )

    return {
        "message": "Dokumen SIMRS berhasil dikonversi ke PDF.",
        "data": saved_doc
    }

@router.get("")
def list_documents(
    kunjungan_id: Optional[int] = None,
    pasien_id: Optional[int] = None,
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    tte_status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List dokumen dengan pagination dan filter"""
    offset = (page - 1) * per_page
    repo = DocumentRepository(db)
    items, total = repo.list_documents(
        kunjungan_id=kunjungan_id,
        pasien_id=pasien_id,
        status=status,
        document_type=document_type,
        tte_status=tte_status,
        search=search,
        limit=per_page,
        offset=offset
    )

    return {
        "data": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    }

@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Detail dokumen beserta metadata"""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    
    metadata = {}
    if doc.metadata_json:
        try:
            metadata = json.loads(doc.metadata_json)
        except Exception:
            pass

    return {
        "document": doc,
        "metadata": metadata
    }

@router.get("/{document_id}/view")
def view_document_inline(
    document_id: int,
    request: Request,
    version: Optional[int] = None,
    db: Session = Depends(get_session)
):
    """Stream PDF untuk viewer / iframe inline (mendukung preview versi revisi terdahulu via ?version=1)"""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan")

    target_path = doc.storage_path
    target_filename = doc.filename

    if version is not None and doc.metadata_json:
        try:
            meta = json.loads(doc.metadata_json)
            cur_ver = int(meta.get("version", 1))
            if version != cur_ver:
                for rev in meta.get("revision_history", []):
                    if int(rev.get("version", 0)) == version and rev.get("storage_path"):
                        if os.path.exists(rev["storage_path"]):
                            target_path = rev["storage_path"]
                            target_filename = rev.get("filename") or target_filename
                        break
        except Exception:
            pass

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="File PDF fisik tidak ditemukan")

    # Pastikan metadata PDF memiliki Title resmi agar browser PDF viewer tidak menampilkan '(anonymous)'
    try:
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(target_path)
        meta = reader.metadata
        if not meta or not meta.title or meta.title == "(anonymous)":
            writer = PdfWriter()
            writer.append(reader)
            doc_title = doc.title or "Surat Keterangan Kematian"
            writer.add_metadata({
                "/Title": doc_title,
                "/Author": "UOBK RSUD DOKTER MOHAMAD SALEH",
                "/Creator": "Sistem E-Archive TTE BSrE BSSN",
                "/Subject": doc.description or doc_title
            })
            with open(target_path, "wb") as f_out:
                writer.write(f_out)
    except Exception as e:
        logger.warning(f"Gagal memperbarui metadata PDF title: {e}")

    return FileResponse(
        target_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{target_filename}"'}
    )

@router.get("/{document_id}/view/{filename}")
def view_document_inline_named(
    document_id: int,
    filename: str,
    request: Request,
    version: Optional[int] = None,
    db: Session = Depends(get_session)
):
    """Wrapper stream PDF dengan nama file eksplisit di URL agar browser menampilkan judul dokumen"""
    return view_document_inline(document_id=document_id, request=request, version=version, db=db)

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Download dokumen PDF resmi"""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan")

    # Catat audit log download
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    audit_service.log(
        db=db,
        document_id=doc.id,
        user_id=current_user.id,
        username=current_user.username,
        user_role=role_val,
        action="DOWNLOAD",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"filename": doc.filename}
    )

    return FileResponse(
        doc.storage_path,
        media_type="application/pdf",
        filename=doc.filename
    )

@router.post("/{document_id}/approve")
def approve_document(
    document_id: int,
    req: DocumentApproveRequest,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_roles(["dokter", "ppa"]))
):
    """Approval dokumen oleh Dokter atau Tenaga PPA"""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    doc.approved_by = current_user.id
    doc.approved_at = datetime.now(timezone.utc)
    doc.status = "approved" if req.approved else "rejected"
    if req.catatan:
        doc.description = f"{doc.description or ''} [Catatan: {req.catatan}]"

    updated = repo.update(doc)

    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    audit_service.log(
        db=db,
        document_id=doc.id,
        user_id=current_user.id,
        username=current_user.username,
        user_role=role_val,
        action="APPROVE" if req.approved else "REJECT",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"status": doc.status, "catatan": req.catatan}
    )

    return {"message": f"Dokumen berhasil di-{doc.status}", "data": updated}

@router.post("/semantic-search")
def semantic_search(
    req: SemanticSearchRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Pencarian semantik konten rekam medis menggunakan kemiripan vektor pgvector (1536-dim)
    """
    vec = vector_service.generate_embedding(req.query)
    repo = DocumentRepository(db)
    results = repo.search_semantic(vec, limit=req.limit)
    return {
        "query": req.query,
        "count": len(results),
        "data": results
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_roles(["dokter", "admin"]))
):
    """Hapus dokumen (khusus Dokter/Admin)"""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    if doc.tte_status == "SIGNED_BSRE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dokumen yang telah ditandatangani secara elektronik (TTE BSRE) tidak boleh dihapus demi kepatuhan hukum."
        )

    # Catat audit sebelum hapus
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    audit_service.log(
        db=db,
        document_id=doc.id,
        user_id=current_user.id,
        username=current_user.username,
        user_role=role_val,
        action="DELETE",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"deleted_file": doc.filename}
    )

    if os.path.exists(doc.storage_path):
        os.remove(doc.storage_path)

    repo.delete(doc)
    return {"message": "Dokumen berhasil dihapus."}
