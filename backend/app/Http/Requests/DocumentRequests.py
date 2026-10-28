from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class DocumentGenerateSimrsRequest(BaseModel):
    kunjungan_id: int
    pasien_id: int
    document_type: str = "konsul_spesialis"
    title: Optional[str] = "Lembar Konsultasi Dokter Spesialis Rawat Inap"
    target_signer_nip: Optional[str] = "198304152011011003"
    target_signer_name: Optional[str] = "dr. RIZKI HABIBIE, Sp.PD."
    pasien: Dict[str, Any]
    konsultasi: Dict[str, Any]
    jawaban: Optional[Dict[str, Any]] = None
    pengirim: Optional[Dict[str, Any]] = None
    konsulan: Optional[Dict[str, Any]] = None
    auto_sign_bsre: bool = False

class SimrsAutoIngestRequest(BaseModel):
    """Payload otomatis dari modul SIMRS (Surat Kematian, Konsul, Resume, dll)"""
    kunjungan_id: int
    pasien_id: int
    document_type: str # surat_kematian, konsul_spesialis, resume_medis, dll.
    title: str
    target_signer_nip: str
    target_signer_name: str
    content_data: Dict[str, Any]
    notify_user: bool = True

class SuratKematianRanapRequest(BaseModel):
    """Payload Khusus Dokumen Surat Keterangan Kematian Rawat Inap (Ranap SIMRS-V3)"""
    noreg: str
    norm: str
    nosrtmeninggal: Optional[str] = None
    jamMeninggal: Optional[str] = None
    tglkeluar: Optional[str] = None
    diagnosa: Optional[str] = None
    pasien: Dict[str, Any]
    dpjp: Dict[str, Any]
    signer_nik: Optional[str] = "0803202100007062"
    sign_now: bool = False
    passphrase: Optional[str] = None

class TteSignRequest(BaseModel):
    document_id: int
    passphrase: Optional[str] = "Bsre2026.#!"
    catatan: Optional[str] = None

class BatchTteSignRequest(BaseModel):
    """Permintaan TTE Banyak Dokumen Sekaligus (Batch Sign)"""
    document_ids: List[int]
    passphrase: Optional[str] = "Bsre2026.#!"
    catatan: Optional[str] = None

class DocumentApproveRequest(BaseModel):
    approved: bool = True
    catatan: Optional[str] = None

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10

class PulangkanPasienRanapRequest(BaseModel):
    noreg: str
    norm: Optional[str] = None
    nama_pasien: Optional[str] = None
    tglkeluar: Optional[str] = None
    carakeluar: Optional[str] = "C003"
    keadaan_keluar: Optional[str] = "Meninggal"
    nosrtmeninggal: Optional[str] = None
    jamMeninggal: Optional[str] = None
    diagnosa: Optional[str] = None
    kddrygmenyatakan: Optional[str] = None
    pasien: Optional[Dict[str, Any]] = None
    dpjp: Optional[Dict[str, Any]] = None
