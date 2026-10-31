import os
import subprocess
import logging
from typing import Dict, Any, Optional
import pypdf

logger = logging.getLogger("simrs_tte.converter")

class DocumentConverterService:
    """
    Layanan Konversi Multi-Format (DOCX, DOC, EPUB, PDF) menjadi dokumen PDF Standar
    dan rendering pratinjau halaman untuk kanvas penempatan TTE interaktif.
    """

    def is_libreoffice_available(self) -> bool:
        """Cek ketersediaan command soffice/libreoffice di sistem"""
        for bin_name in ["soffice", "libreoffice"]:
            try:
                res = subprocess.run([bin_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0:
                    return True
            except Exception:
                pass
        return False

    def convert_to_pdf(self, input_file_path: str, output_dir: str) -> str:
        """
        Konversi berkas (DOCX, DOC, EPUB, PDF) menjadi format PDF.
        Mengembalikan path berkas PDF hasil konversi.
        """
        os.makedirs(output_dir, exist_ok=True)
        ext = os.path.splitext(input_file_path)[1].lower()
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_pdf_path = os.path.join(output_dir, f"{base_name}.pdf")

        # 1. Jika sudah PDF
        if ext == ".pdf":
            # Validasi file PDF bisa dibaca
            try:
                reader = pypdf.PdfReader(input_file_path)
                if len(reader.pages) > 0:
                    return input_file_path
            except Exception as e:
                logger.error(f"Berkas PDF tidak valid: {e}")
                raise ValueError("Berkas PDF rusak atau tidak dapat dibaca.")

        # 2. Jika format Word (.docx / .doc)
        elif ext in [".docx", ".doc"]:
            logger.info(f"Mengonversi dokumen Word {input_file_path} ke PDF...")
            cmd = [
                "soffice",
                "--headless",
                "--convert-to", "pdf:writer_pdf_Export",
                "--outdir", output_dir,
                input_file_path
            ]
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, text=True)
                if result.returncode != 0:
                    logger.error(f"Gagal konversi LibreOffice: {result.stderr}")
                    raise RuntimeError(f"Gagal mengonversi Word ke PDF: {result.stderr or result.stdout}")
                
                generated_pdf = os.path.join(output_dir, f"{base_name}.pdf")
                if not os.path.exists(generated_pdf):
                    raise RuntimeError("Berkas PDF hasil konversi Word tidak ditemukan di direktori tujuan.")
                return generated_pdf
            except Exception as e:
                logger.error(f"Error saat mengeksekusi konversi Word: {e}")
                raise RuntimeError(f"Gagal memproses dokumen Word: {e}")

        # 3. Jika format EPUB (.epub)
        elif ext == ".epub":
            logger.info(f"Mengonversi berkas EPUB {input_file_path} ke PDF...")
            return self._convert_epub_to_pdf(input_file_path, output_pdf_path)

        else:
            raise ValueError(f"Format berkas '{ext}' tidak didukung. Format yang didukung: PDF, DOCX, DOC, EPUB.")

    def _convert_epub_to_pdf(self, epub_path: str, output_pdf_path: str) -> str:
        """Konversi EPUB ke PDF menggunakan ekstraksi konten teks terstruktur dan ReportLab"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            book = epub.read_epub(epub_path)
            title = book.get_metadata('DC', 'title')
            doc_title = title[0][0] if title else "Dokumen EPUB"

            doc = SimpleDocTemplate(
                output_pdf_path,
                pagesize=A4,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54,
                title=doc_title,
                author="E-RM Microservice TTE BSrE"
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'EpubTitle',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#0f172a"),
                spaceAfter=14
            )
            h2_style = ParagraphStyle(
                'EpubH2',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#1e293b"),
                spaceBefore=12,
                spaceAfter=8
            )
            body_style = ParagraphStyle(
                'EpubBody',
                parent=styles['BodyText'],
                fontSize=10,
                leading=15,
                textColor=colors.HexColor("#334155"),
                spaceAfter=8
            )

            story = [
                Paragraph(doc_title, title_style),
                Spacer(1, 10)
            ]

            # Iterasi isi dokumen EPUB
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                content = item.get_content().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(content, 'html.parser')
                
                for el in soup.find_all(['h1', 'h2', 'h3', 'p']):
                    text = el.get_text().strip()
                    if not text:
                        continue
                    clean_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    if el.name == 'h1':
                        story.append(Paragraph(clean_text, title_style))
                    elif el.name in ['h2', 'h3']:
                        story.append(Paragraph(clean_text, h2_style))
                    else:
                        story.append(Paragraph(clean_text, body_style))

            doc.build(story)
            return output_pdf_path

        except Exception as e:
            logger.error(f"Gagal konversi EPUB ke PDF: {e}")
            raise RuntimeError(f"Gagal memproses berkas EPUB: {e}")

    def get_pdf_metadata_and_pages(self, pdf_path: str) -> Dict[str, Any]:
        """Ambil info jumlah halaman dan dimensi PDF"""
        try:
            reader = pypdf.PdfReader(pdf_path)
            total_pages = len(reader.pages)
            pages_info = []

            for i, page in enumerate(reader.pages):
                box = page.mediabox
                pages_info.append({
                    "page_number": i + 1,
                    "width": float(box.width),
                    "height": float(box.height)
                })

            return {
                "total_pages": total_pages,
                "pages": pages_info,
                "first_page_width": pages_info[0]["width"] if pages_info else 595.27,
                "first_page_height": pages_info[0]["height"] if pages_info else 841.89
            }
        except Exception as e:
            logger.error(f"Gagal membaca info halaman PDF: {e}")
            return {"total_pages": 1, "pages": [{"page_number": 1, "width": 595.27, "height": 841.89}]}

    def render_page_to_png(self, pdf_path: str, page_number: int, output_png_path: str) -> str:
        """
        Render halaman PDF tertentu ke gambar PNG untuk kanvas interaktif.
        Jika modul PyMuPDF (fitz) tersedia, gunakan fitz untuk hasil berkualitas tinggi.
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            if page_number < 1 or page_number > len(doc):
                page_number = 1
            page = doc[page_number - 1]
            # Zoom 2.0 untuk ketajaman retina kanvas
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
            pix.save(output_png_path)
            doc.close()
            return output_png_path
        except Exception as e:
            logger.warning(f"PyMuPDF rendering gagal/tidak tersedia: {e}")
            return ""

converter_service = DocumentConverterService()
