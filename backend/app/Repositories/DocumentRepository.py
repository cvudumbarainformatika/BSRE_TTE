from sqlmodel import Session, select, text
from app.Models.Document import Document
from typing import Optional, List
from datetime import datetime

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, doc: Document) -> Document:
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        return self.db.get(Document, doc_id)

    def list_documents(
        self,
        kunjungan_id: Optional[int] = None,
        pasien_id: Optional[int] = None,
        status: Optional[str] = None,
        document_type: Optional[str] = None,
        tte_status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> (List[Document], int):
        """
        Query dokumen dengan SQL-standard pagination dan filter.
        Kompatibel dengan MySQL dan PostgreSQL.
        """
        query = select(Document)

        if kunjungan_id:
            query = query.where(Document.kunjungan_id == kunjungan_id)
        if pasien_id:
            query = query.where(Document.pasien_id == pasien_id)
        if status:
            query = query.where(Document.status == status)
        if document_type:
            query = query.where(Document.document_type == document_type)
        if tte_status:
            query = query.where(Document.tte_status == tte_status)
        if search:
            # Case-insensitive like search (SQL standard LOWER)
            search_pattern = f"%{search.lower()}%"
            query = query.where(
                (text("LOWER(title) LIKE :q")) |
                (text("LOWER(filename) LIKE :q")) |
                (text("LOWER(description) LIKE :q"))
            ).params(q=search_pattern)

        # Count total
        total = len(self.db.exec(query).all())

        # Order by uploaded_at DESC and paginate
        query = query.order_by(Document.uploaded_at.desc()).offset(offset).limit(limit)
        items = self.db.exec(query).all()

        return items, total

    def search_semantic(self, embedding: List[float], limit: int = 10) -> List[Document]:
        """
        Pencarian kemiripan vektor pgvector menggunakan cosine distance (<=>)
        """
        try:
            # PostgreSQL pgvector query syntax
            stmt = text("""
                SELECT id, kunjungan_id, pasien_id, filename, title, document_type, 
                       storage_path, uploaded_by, uploaded_at, status, tte_status,
                       1 - (embedding <=> :vec::vector) AS similarity
                FROM document
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> :vec::vector ASC
                LIMIT :limit
            """)
            vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
            result = self.db.execute(stmt, {"vec": vec_str, "limit": limit}).fetchall()
            
            doc_ids = [row[0] for row in result]
            if not doc_ids:
                return []
            
            # Fetch full documents
            docs = self.db.exec(select(Document).where(Document.id.in_(doc_ids))).all()
            # Sort as per similarity order
            doc_map = {d.id: d for d in docs}
            return [doc_map[did] for did in doc_ids if did in doc_map]
        except Exception as e:
            # Fallback jika ekstensi vector belum aktif atau database MySQL
            return self.db.exec(select(Document).order_by(Document.uploaded_at.desc()).limit(limit)).all()

    def update(self, doc: Document) -> Document:
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete(self, doc: Document) -> bool:
        self.db.delete(doc)
        self.db.commit()
        return True
