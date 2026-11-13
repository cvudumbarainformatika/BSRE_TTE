import os
import io
import re
import qrcode
from datetime import datetime, date
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.units import cm, mm
from config.settings import settings


BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

HARI_ID = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu"
}

EN_TO_ID_WORDS = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu",
    "January": "Januari", "February": "Februari", "March": "Maret", "April": "April",
    "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus",
    "September": "September", "October": "Oktober", "November": "November", "December": "Desember"
}


def to_indonesian_date(val, include_day=False) -> str:
    """Mengubah format tanggal menjadi Bahasa Indonesia resmi (Audit Kominfo / BSrE)"""
    if not val:
        now = datetime.now()
        day_str = f"{HARI_ID[now.weekday()]}, " if include_day else ""
        return f"{day_str}{now.day} {BULAN_ID[now.month]} {now.year}"

    if isinstance(val, (datetime, date)):
        day_str = f"{HARI_ID[val.weekday()]}, " if include_day else ""
        return f"{day_str}{val.day} {BULAN_ID[val.month]} {val.year}"

    val_str = str(val).strip()

    # Cek format ISO YYYY-MM-DD
    match_iso = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", val_str)
    if match_iso:
        try:
            y, m, d = int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3))
            dt = datetime(y, m, d)
            day_str = f"{HARI_ID[dt.weekday()]}, " if include_day else ""
            return f"{day_str}{d} {BULAN_ID.get(m, str(m))} {y}"
        except Exception:
            pass

    # Cek format DD-MM-YYYY
    match_dmy = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})", val_str)
    if match_dmy:
        try:
            d, m, y = int(match_dmy.group(1)), int(match_dmy.group(2)), int(match_dmy.group(3))
            dt = datetime(y, m, d)
            day_str = f"{HARI_ID[dt.weekday()]}, " if include_day else ""
            return f"{day_str}{d} {BULAN_ID.get(m, str(m))} {y}"
        except Exception:
            pass

    # Ganti kata-kata nama hari dan bulan bahasa Inggris jika sudah terlanjur berformat string
    res = val_str
    for en_word, id_word in EN_TO_ID_WORDS.items():
        res = re.sub(rf"\b{en_word}\b", id_word, res, flags=re.IGNORECASE)

    return res


class PdfGeneratorService:
    # Kalimat wajib BSrE sesuai BAB IV Poin I Pedoman Kriteria Integrasi Sistem BSrE-BSSN (Halaman 7)
    BSRE_MANDATORY_FOOTER_LINE1 = "Dokumen ini telah ditandatangani secara elektronik menggunakan sertifikat elektronik"
    BSRE_MANDATORY_FOOTER_LINE2 = "yang telah diterbitkan oleh Balai Besar Sertifikasi Elektronik (BSrE), Badan Siber dan Sandi Negara"

    @staticmethod
    def get_asset_path(filename: str) -> str:
        return os.path.join(settings.BASE_STORAGE_PATH, "assets", filename)

    @classmethod
    def _draw_page_footer(cls, canvas_obj, doc_obj):
        """
        Menggambar footer resmi di bagian paling bawah setiap halaman PDF:
        1. Kalimat wajib Kriteria Integrasi Sistem BSrE-BSSN (di tengah bawah setiap halaman).
        2. Keterangan halaman 'Dokumen Sah dari RSUD MOH SALEH KOTA PROBOLINGGO | Hal Ke-X' (di kanan bawah).
        """
        canvas_obj.saveState()
        page_width = A4[0]

        # Baris informasi halaman RSUD (kanan bawah)
        canvas_obj.setFont("Times-Roman", 9)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.drawRightString(
            page_width - 2.0 * cm,
            1.75 * cm,
            f"Dokumen Sah dari RSUD MOH SALEH KOTA PROBOLINGGO | Hal Ke-{doc_obj.page}"
        )

        # Garis tipis pemisah footer BSrE
        canvas_obj.setStrokeColor(colors.HexColor("#cbd5e1"))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(2.0 * cm, 1.45 * cm, page_width - 2.0 * cm, 1.45 * cm)

        # Kalimat Wajib BSrE BSSN di setiap halaman (rata tengah bawah sesuai Pedoman Kriteria Integrasi Sistem Hal. 7)
        canvas_obj.setFont("Helvetica", 7.5)
        canvas_obj.setFillColor(colors.HexColor("#1e293b"))
        canvas_obj.drawCentredString(page_width / 2.0, 1.05 * cm, cls.BSRE_MANDATORY_FOOTER_LINE1)
        canvas_obj.drawCentredString(page_width / 2.0, 0.72 * cm, cls.BSRE_MANDATORY_FOOTER_LINE2)

        canvas_obj.restoreState()

    @classmethod
    def create_qr_with_center_logo(cls, data: str, logo_filename: str = "logo-rsud.png") -> PILImage.Image:
        """
        Menghasilkan PIL Image QR Code dengan logo RSUD dr. Mohamad Saleh (lingkaran merah-kuning logo-rsud.png)
        di tengahnya.
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        logo_path = cls.get_asset_path(logo_filename)
        if not os.path.exists(logo_path):
            logo_path = cls.get_asset_path("logo-rsud.png")

        if os.path.exists(logo_path):
            try:
                logo = PILImage.open(logo_path).convert("RGBA")
                qr_w, qr_h = qr_img.size
                logo_max_size = int(qr_w * 0.25)
                logo.thumbnail((logo_max_size, logo_max_size), PILImage.Resampling.LANCZOS)

                lw, lh = logo.size
                pad = 4
                bg = PILImage.new("RGBA", (lw + pad * 2, lh + pad * 2), (255, 255, 255, 255))
                bg.paste(logo, (pad, pad), logo)

                pos = ((qr_w - bg.width) // 2, (qr_h - bg.height) // 2)
                qr_img.paste(bg, pos, bg)
            except Exception:
                pass

        return qr_img

    @classmethod
    def _create_qr_image(cls, data: str, size: float = 2.6 * cm, logo_filename: str = "logo-rsud.png") -> RLImage:
        """Menghasilkan elemen ReportLab Image dari QR Code + Logo RSUD di tengah"""
        pil_img = cls.create_qr_with_center_logo(data, logo_filename=logo_filename)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        buffer.seek(0)
        return RLImage(buffer, width=size, height=size)

    @classmethod
    def generate_surat_kematian_pdf(cls, data: dict, output_path: str, is_signed: bool = False, verify_url: str = None) -> str:
        """
        Menghasilkan PDF 'SURAT KETERANGAN KEMATIAN' Rawat Inap:
        - KOP Surat dengan logo perisai hitam-putih (logo-kota-grey.png) di kiri.
        - 1 QR Code BSrE tunggal di area tanda tangan dokter dengan logo RSUD (logo-rsud.png yang ada kuningnya) di tengah.
        - Footer wajib BSrE BSSN di bagian paling bawah setiap halaman PDF.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Metadata resmi dokumen PDF agar judul di browser PDF viewer tidak 'anonymous'
        nama_pasien = ""
        if data.get("pasien") and isinstance(data["pasien"], dict):
            nama_pasien = data["pasien"].get("nama") or ""
        elif data.get("nama_pasien"):
            nama_pasien = data.get("nama_pasien")
        doc_title = data.get("judul") or "Surat Keterangan Kematian"
        full_title = f"{doc_title} - {nama_pasien}" if nama_pasien else doc_title
        no_surat = data.get("nosrtmeninggal") or data.get("nomor_surat") or ""

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            title=full_title,
            author="UOBK RSUD DOKTER MOHAMAD SALEH",
            subject=f"No. Dokumen: {no_surat}" if no_surat else doc_title,
            creator="Sistem E-Archive TTE BSrE BSSN",
            leftMargin=2.0 * cm,
            rightMargin=2.0 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2.3 * cm
        )

        styles = getSampleStyleSheet()
        kop_bold_style = ParagraphStyle('KopBold', parent=styles['Normal'], fontSize=12.5, leading=15, alignment=1, fontName="Helvetica-Bold")
        kop_sub_style = ParagraphStyle('KopSub', parent=styles['Normal'], fontSize=10, leading=13, alignment=1, fontName="Helvetica")
        doc_title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontSize=13.5, leading=17, alignment=1, fontName="Helvetica-Bold")
        doc_nomor_style = ParagraphStyle('DocNomor', parent=styles['Normal'], fontSize=10.5, leading=14, alignment=1, fontName="Helvetica-Bold")
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10.5, leading=15, fontName="Helvetica")
        body_indent_style = ParagraphStyle('BodyIndent', parent=styles['Normal'], fontSize=10.5, leading=16, firstLineIndent=18, fontName="Helvetica")
        cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=10.5, leading=14.5, fontName="Helvetica")
        ttd_center_style = ParagraphStyle('TtdCenter', parent=styles['Normal'], fontSize=10.5, leading=14.5, alignment=1, fontName="Helvetica")

        story = []

        # 1. KOP SURAT (Logo Perisai Hitam-Putih logo-kota-grey.png di kiri + Teks Tengah — Persis SS1)
        logo_kop_path = cls.get_asset_path("logo-kota-grey.png")
        if os.path.exists(logo_kop_path):
            logo_kop_el = RLImage(logo_kop_path, width=1.45 * cm, height=1.80 * cm)
        else:
            logo_kop_el = Paragraph("", body_style)

        kop_text_block = [
            Paragraph("<b>PEMERINTAH KOTA PROBOLINGGO</b>", kop_bold_style),
            Paragraph("<b>UOBK RSUD DOKTER MOHAMAD SALEH</b>", kop_bold_style),
            Paragraph("Jl. Mayjend Panjaitan No.65 Probolinggo Jawa Timur", kop_sub_style),
            Paragraph("Telp. (0335) 433478,433119,421118 Fax. (0335) 432702", kop_sub_style),
        ]

        kop_table = Table(
            [[Paragraph("", body_style), logo_kop_el, kop_text_block, Paragraph("", body_style)]],
            colWidths=[2.3 * cm, 1.8 * cm, 10.6 * cm, 2.3 * cm]
        )
        kop_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(kop_table)
        story.append(Spacer(1, 3 * mm))

        story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#64748b"), spaceBefore=1, spaceAfter=1.2))
        story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#94a3b8"), spaceBefore=0.5, spaceAfter=5 * mm))

        # 2. JUDUL & NOMOR SURAT
        judul = data.get("judul", "SURAT KETERANGAN KEMATIAN")
        nomor_surat = (
            data.get("nosrtmeninggal")
            or data.get("nomor_surat")
            or f"472.12/{str(data.get('kunjungan_id', '0001')).zfill(4)}/425.102.8/KEM/X/2026"
        )
        story.append(Paragraph(f"<u><b>{judul}</b></u>", doc_title_style))
        story.append(Spacer(1, 1.5 * mm))
        story.append(Paragraph(f"<b>NOMOR : {nomor_surat}</b>", doc_nomor_style))
        story.append(Spacer(1, 6 * mm))

        # 3. BIODATA DOKTER YANG MENYATAKAN
        story.append(Paragraph("Yang bertanda tangan di bawah ini :", body_style))
        story.append(Spacer(1, 2 * mm))

        dokter = data.get("dokter") or data.get("dpjp") or {}
        nama_dokter = dokter.get("nama", "dr. RIA NURMALA SETYANINGRUM")
        golongan = dokter.get("golongan", "IV/a")
        ket_golongan = dokter.get("ket_golongan", "Pembina")
        pangkat_str = f"{golongan} / {ket_golongan}" if golongan and ket_golongan else (golongan or ket_golongan or "-")
        jabatan = dokter.get("ket_jabatan") or dokter.get("jabatan") or "Dokter Madya"

        dokter_rows = [
            [Paragraph("", cell_style), Paragraph("Nama Dokter", cell_style), Paragraph(f": {nama_dokter}", cell_style)],
            [Paragraph("", cell_style), Paragraph("Pangkat / Gol", cell_style), Paragraph(f": {pangkat_str}", cell_style)],
            [Paragraph("", cell_style), Paragraph("Jabatan", cell_style), Paragraph(f": {jabatan}", cell_style)],
        ]
        dokter_table = Table(dokter_rows, colWidths=[0.6 * cm, 3.2 * cm, 13.2 * cm])
        dokter_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        story.append(dokter_table)
        story.append(Spacer(1, 3.5 * mm))

        # 4. PERNYATAAN MENINGGAL & BIODATA PASIEN
        story.append(Paragraph("Menyatakan bahwa :", body_style))
        story.append(Paragraph("<b>TELAH MENINGGAL DUNIA</b> , Saudara :", body_style))
        story.append(Spacer(1, 2 * mm))

        pasien = data.get("pasien", {})
        nama_pasien = pasien.get("nama_panggil") or pasien.get("nama") or "-"
        nktp = pasien.get("nktp") or pasien.get("nik") or "-"
        usia = pasien.get("usia") or "-"
        kelamin = pasien.get("kelamin") or "-"
        alamat = pasien.get("alamat") or "PROBOLINGGO"

        pasien_rows = [
            [Paragraph("", cell_style), Paragraph("Nama Lengkap", cell_style), Paragraph(f": {nama_pasien}", cell_style)],
            [Paragraph("", cell_style), Paragraph("Nomor KTP", cell_style), Paragraph(f": {nktp}", cell_style)],
            [Paragraph("", cell_style), Paragraph("Umur", cell_style), Paragraph(f": {usia}", cell_style)],
            [Paragraph("", cell_style), Paragraph("Jenis Kelamin", cell_style), Paragraph(f": {kelamin}", cell_style)],
            [Paragraph("", cell_style), Paragraph("Alamat", cell_style), Paragraph(f": {alamat}", cell_style)],
        ]
        pasien_table = Table(pasien_rows, colWidths=[0.6 * cm, 3.2 * cm, 13.2 * cm])
        pasien_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        story.append(pasien_table)
        story.append(Spacer(1, 5 * mm))

        # 5. WAKTU & PENYEBAB KEMATIAN
        tgl_meninggal_raw = data.get("tgl_meninggal") or pasien.get("tglkeluar")
        tgl_meninggal = to_indonesian_date(tgl_meninggal_raw, include_day=True)
        tgl_ttd = to_indonesian_date(tgl_meninggal_raw, include_day=False)
        jam_meninggal = data.get("jam_meninggal") or data.get("jamMeninggal") or "08:47"
        jam_clean = jam_meninggal.replace("WIB", "").strip()
        diagnosa_penyebab = (
            data.get("sebabkematian_ket")
            or data.get("diagnosa")
            or data.get("penyebab_langsung")
            or pasien.get("sebabkematian")
            or "Cardiac arrest, unspecified"
        )

        kalimat_waktu = (
            f"Pada Tanggal <b>{tgl_meninggal}</b> "
            f"tepatnya pada jam : <b>{jam_clean} WIB</b> , "
            f"dikarenakan {diagnosa_penyebab} ."
        )
        story.append(Paragraph(kalimat_waktu, body_indent_style))
        story.append(Spacer(1, 1.5 * mm))

        kalimat_penutup = (
            "Demikian Surat Keterangan Kematian ini kami terbitkan untuk dapat digunakan "
            "semestinya dan sebijak-bijaknya"
        )
        story.append(Paragraph(kalimat_penutup, body_indent_style))
        story.append(Spacer(1, 12 * mm))

        # 6. BLOK TANDA TANGAN DOKTER (Sisi Kanan Bawah)
        # Menggunakan logo RSUD sendiri (logo-rsud.png yang ada warna kuningnya) di tengah QR Code
        if is_signed and verify_url:
            qr_element = cls._create_qr_image(verify_url, size=2.6 * cm, logo_filename="logo-rsud.png")
            signature_middle_rows = [
                [Spacer(1, 2 * mm)],
                [qr_element],
                [Spacer(1, 2 * mm)],
            ]
        else:
            signature_middle_rows = [
                [Spacer(1, 30 * mm)],
            ]

        ttd_rows = [
            [Paragraph(f"Probolinggo, {tgl_ttd}", ttd_center_style)],
            [Paragraph("Mengetahui", ttd_center_style)],
            [Paragraph("Dokter,", ttd_center_style)],
            *signature_middle_rows,
            [Paragraph(f"{nama_dokter}", ttd_center_style)],
        ]
        ttd_block = Table(ttd_rows, colWidths=[7.5 * cm])
        ttd_block.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))

        ttd_wrapper = Table([[Paragraph("", body_style), ttd_block]], colWidths=[9.5 * cm, 7.5 * cm])
        story.append(KeepTogether(ttd_wrapper))

        # 7. BUILD PDF DENGAN FOOTER WAJIB BSrE DI SETIAP HALAMAN (onFirstPage & onLaterPages)
        doc.build(story, onFirstPage=cls._draw_page_footer, onLaterPages=cls._draw_page_footer)
        return output_path

    @classmethod
    def generate_simrs_konsul_pdf(cls, data: dict, output_path: str) -> str:
        """Lembar Konsultasi Dokter Spesialis Rawat Inap RSUD Dr. Mohammad Saleh"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=1.2 * cm, rightMargin=1.2 * cm,
            topMargin=1.0 * cm, bottomMargin=2.3 * cm
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontSize=11, leading=13, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)
        sub_title_style = ParagraphStyle('HeaderSubTitle', parent=styles['Normal'], fontSize=8, leading=10, alignment=1, fontName="Helvetica", textColor=colors.black)
        doc_title_style = ParagraphStyle('DocTitle', parent=styles['Heading2'], fontSize=10, leading=12, alignment=1, fontName="Helvetica-Bold", textColor=colors.black)
        label_style = ParagraphStyle('CellLabel', parent=styles['Normal'], fontSize=8, leading=10, fontName="Helvetica-Bold")
        val_style = ParagraphStyle('CellVal', parent=styles['Normal'], fontSize=8, leading=10, fontName="Helvetica")
        body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=8.5, leading=11, fontName="Helvetica")

        story = []

        kop_left = [
            Paragraph(f"<b>{settings.HOSPITAL_GOV_HEADER}</b>", title_style),
            Paragraph(f"<b>{settings.HOSPITAL_NAME}</b>", title_style),
            Paragraph(f"{settings.HOSPITAL_ADDRESS}", sub_title_style),
            Paragraph(f"{settings.HOSPITAL_PHONE}", sub_title_style),
        ]
        kop_right = [
            Paragraph("<b>LEMBAR KONSULTASI<br/>DOKTER SPESIALIS<br/>RAWAT INAP</b>", doc_title_style)
        ]
        kop_table = Table([[kop_left, kop_right]], colWidths=[13.0 * cm, 5.6 * cm])
        kop_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(kop_table)
        story.append(Spacer(1, 3 * mm))

        pasien = data.get("pasien", {})
        id_data = [
            [
                Paragraph("Nama Pasien", label_style),
                Paragraph(f": <b>{pasien.get('nama', '-')}</b>", val_style),
                Paragraph("No. RM / Noreg", label_style),
                Paragraph(f": <b>{pasien.get('norm', '-')} / {pasien.get('noreg', '-')}</b>", val_style),
            ],
            [
                Paragraph("Tgl Lahir / Usia", label_style),
                Paragraph(f": {pasien.get('tgllahir', '-')} ({pasien.get('usia', '-')})", val_style),
                Paragraph("Jenis Kelamin", label_style),
                Paragraph(f": {pasien.get('kelamin', '-')}", val_style),
            ],
        ]
        id_table = Table(id_data, colWidths=[3.2 * cm, 6.2 * cm, 3.2 * cm, 6.0 * cm])
        id_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(id_table)
        story.append(Spacer(1, 4 * mm))

        konsul = data.get("konsultasi", {})
        ikhtisar_text = konsul.get("ikhtisar_klinik", "Konsultasi kondisi klinis pasien...")
        ikhtisar_box = Table([
            [Paragraph("<b>Ikhtisar Klinik / Masalah Medik & Permintaan Konsul:</b>", label_style)],
            [Paragraph(ikhtisar_text.replace("\n", "<br/>"), body_style)]
        ], colWidths=[18.6 * cm])
        ikhtisar_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(ikhtisar_box)

        doc.build(story, onFirstPage=cls._draw_page_footer, onLaterPages=cls._draw_page_footer)
        return output_path


pdf_service = PdfGeneratorService()
