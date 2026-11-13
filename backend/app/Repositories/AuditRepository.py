import json
from sqlmodel import Session, select
from app.Models.DocumentAuditLog import DocumentAuditLog
from app.Models.Document import Document
from typing import List, Dict, Any, Optional

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_document(self, document_id: int) -> List[DocumentAuditLog]:
        query = select(DocumentAuditLog).where(DocumentAuditLog.document_id == document_id).order_by(DocumentAuditLog.created_at.desc())
        return self.db.exec(query).all()

    def get_recent(self, limit: int = 50) -> List[DocumentAuditLog]:
        query = select(DocumentAuditLog).order_by(DocumentAuditLog.created_at.desc()).limit(limit)
        return self.db.exec(query).all()

    def get_enriched_audit_trail(
        self,
        limit: int = 100,
        search: Optional[str] = None,
        action_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Mengambil log audit trail lengkap sesuai ketentuan Audit BSSN / Kominfo:
        - Tanggal & Waktu
        - Nama User Penandatangan / Petugas
        - Keterangan Berhasil / Gagal
        - Dokumen yang di-TT (Nama Dokumen, No. Surat, Nama Pasien, No. RM)
        - Alasan bila gagal
        """
        query = select(DocumentAuditLog)

        if action_filter and action_filter != "ALL":
            if action_filter == "SUCCESS":
                query = query.where(DocumentAuditLog.action.in_(["SIGN_TTE_BSRE", "APPROVE"]))
            elif action_filter == "FAILED":
                query = query.where(DocumentAuditLog.action.in_(["SIGN_TTE_FAILED", "REJECT"]))
            elif action_filter == "TTE_ONLY":
                query = query.where(DocumentAuditLog.action.in_(["SIGN_TTE_BSRE", "SIGN_TTE_FAILED"]))
            else:
                query = query.where(DocumentAuditLog.action == action_filter)

        query = query.order_by(DocumentAuditLog.created_at.desc()).limit(limit)
        logs = self.db.exec(query).all()

        if not logs:
            return []

        # Batch query Document untuk mencegah N+1 Query
        doc_ids = list({log.document_id for log in logs if log.document_id})
        doc_map = {}
        if doc_ids:
            docs = self.db.exec(select(Document).where(Document.id.in_(doc_ids))).all()
            for d in docs:
                doc_map[d.id] = d

        enriched_list = []
        for log in logs:
            doc = doc_map.get(log.document_id)

            # Parse details JSON
            details_obj = {}
            if log.details:
                try:
                    details_obj = json.loads(log.details) if isinstance(log.details, str) else log.details
                except Exception:
                    details_obj = {"raw": log.details}

            # Ekstrak data pasien & nomor surat dari metadata dokumen jika ada
            nama_pasien = None
            norm = None
            nomor_surat = None

            if doc and doc.metadata_json:
                try:
                    meta = json.loads(doc.metadata_json) if isinstance(doc.metadata_json, str) else doc.metadata_json
                    nama_pasien = meta.get("pasien", {}).get("nama") or meta.get("pasien", {}).get("nama_panggil") or meta.get("nama_pasien")
                    norm = meta.get("norm") or meta.get("pasien", {}).get("norm")
                    nomor_surat = meta.get("nomor_surat") or meta.get("nosrtmeninggal")
                except Exception:
                    pass

            if not nama_pasien and doc and doc.title and " - " in doc.title:
                parts = doc.title.split(" - ")
                if len(parts) >= 2:
                    nama_pasien = parts[1].strip()

            if not nomor_surat and details_obj.get("nomor_surat"):
                nomor_surat = details_obj.get("nomor_surat")

            # Tentukan status keterangan & alasan gagal
            action = log.action
            if action in ("SIGN_TTE_BSRE", "APPROVE"):
                status_ket = "BERHASIL"
            elif action in ("SIGN_TTE_FAILED", "REJECT"):
                status_ket = "GAGAL"
            else:
                status_ket = "INFO"

            alasan_gagal = None
            if status_ket == "GAGAL":
                alasan_gagal = (
                    details_obj.get("error_message")
                    or details_obj.get("reason")
                    or details_obj.get("catatan")
                    or "Kegagalan otorisasi atau penandatanganan sertifikat BSrE"
                )

            item = {
                "id": log.id,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "username": log.username,
                "user_role": log.user_role,
                "action": action,
                "status": status_ket,
                "document_id": log.document_id,
                "document_title": doc.title if doc else details_obj.get("doc_title", f"Dokumen #{log.document_id}"),
                "document_type": doc.document_type if doc else details_obj.get("document_type", "general"),
                "nomor_surat": nomor_surat,
                "nama_pasien": nama_pasien,
                "norm": str(norm) if norm else None,
                "alasan_gagal": alasan_gagal,
                "ip_address": log.ip_address,
                "details": details_obj
            }

            # Filter search lokal jika diberikan query search
            if search:
                s_lower = search.lower()
                combined_text = (
                    f"{item['username']} {item['document_title']} {item['nama_pasien'] or ''} "
                    f"{item['nomor_surat'] or ''} {item['action']} {item['status']} {item['alasan_gagal'] or ''}"
                ).lower()
                if s_lower not in combined_text:
                    continue

            enriched_list.append(item)

        return enriched_list
