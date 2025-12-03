import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import random

def number_to_indonesian_words(number):
    units = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan"]
    teens = ["Sepuluh", "Sebelas", "Dua Belas", "Tiga Belas", "Empat Belas", "Lima Belas",
             "Enam Belas", "Tujuh Belas", "Delapan Belas", "Sembilan Belas"]
    tens = ["", "", "Dua Puluh", "Tiga Puluh", "Empat Puluh", "Lima Puluh",
            "Enam Puluh", "Tujuh Puluh", "Delapan Puluh", "Sembilan Puluh"]

    def convert_hundreds(n):
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n-10]
        elif n < 100:
            return tens[n//10] + (" " + units[n%10] if n % 10 != 0 else "")
        else:
            if n == 100:
                return "Seratus"
            else:
                return units[n//100] + " Ratus" + (" " + convert_hundreds(n%100) if n % 100 != 0 else "")

    if number == 0:
        return "Nol"
    elif number < 1000:
        return convert_hundreds(number)
    elif number < 1000000:
        ribu = number // 1000
        sisa = number % 1000
        ribu_text = "Seribu" if ribu == 1 else convert_hundreds(ribu) + " Ribu"
        sisa_text = "" if sisa == 0 else " " + convert_hundreds(sisa)
        return ribu_text + sisa_text
    else:
        return "Jumlah terlalu besar"

from reportlab.lib import colors

def create_kwitansi_pdf(data, ttd_image=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFillColor(colors.HexColor("#cfe2f3"))
    c.rect(0, 0, width, height, stroke=0, fill=1)

    card_x = 1.5 * cm
    card_y = 2 * cm
    card_width = width - 3 * cm
    card_height = height - 4 * cm

    c.setFillColor(colors.white)
    c.roundRect(card_x, card_y, card_width, card_height, 18, stroke=0, fill=1)

    header_height = 3 * cm
    c.setFillColor(colors.HexColor("#cfe2f3"))
    c.roundRect(card_x, card_y + card_height - header_height,
                card_width, header_height, 18, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawCentredString(card_x + card_width / 2,
                        card_y + card_height - header_height/2 + 4,
                        "KWITANSI PEMBAYARAN")

    c.setStrokeColor(colors.white)
    c.setLineWidth(3)
    c.line(card_x, card_y + card_height - header_height,
           card_x + card_width, card_y + card_height - header_height)

    margin_left = card_x + 1.3 * cm
    y = card_y + card_height - header_height - 1.0 * cm
    line_height = 16

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawString(margin_left, y, f"Nomor: {data['nomor']}")
    c.drawRightString(card_x + card_width - 1.3*cm, y,
                      f"Tanggal: {data['tanggal']}")
    y -= line_height * 2

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin_left, y, "Telah diterima dari:")
    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left + 15, y, data['penerima'])
    y -= line_height * 2

    c.setFont("Helvetica", 12)
    c.drawString(margin_left, y, "Sejumlah uang sebesar:")
    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawString(
        margin_left + 15,
        y,
        f"Rp {data['jumlah_formatted']} ,- ({data['jumlah_kata']} Rupiah)"
    )
    y -= line_height * 2

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin_left, y, "Untuk pembayaran:")
    y -= line_height

    keterangan_lines = data['keterangan'].split('\n')
    box_height = line_height * (len(keterangan_lines) + 1.5)
    box_width = card_width - 2.6*cm
    box_x = margin_left
    box_y = y - box_height

    y_in_box = y
    c.setFont("Helvetica-Bold", 12)
    first_line = keterangan_lines[0].strip()
    c.drawString(margin_left + 10, y_in_box, first_line)
    y_in_box -= line_height
    c.setFont("Helvetica", 12)

    for line in keterangan_lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('-'):
            c.drawString(margin_left + 25, y_in_box, f"• {line[1:].strip()}")
        else:
            c.drawString(margin_left + 10, y_in_box, line)
        y_in_box -= line_height

    y = box_y

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(margin_left, y, "Metode pembayaran:")
    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawString(margin_left + 15, y, data['metode'])
    y -= line_height * 3

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin_left, y, "Penerima pembayaran,")
    y -= line_height
    c.drawString(margin_left, y, "Tanda Tangan:")
    y -= line_height * 2

    if ttd_image:
        max_width = 4 * cm
        max_height = 2 * cm
        img_width, img_height = ttd_image.size
        ratio = min(max_width / img_width, max_height / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio

        c.drawInlineImage(
            ttd_image,
            margin_left,
            y - new_height + line_height,
            width=new_width,
            height=new_height
        )
        y -= new_height

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, y, data['penerima_ttd'])
    y -= line_height
    c.setFont("Helvetica", 11)
    c.drawString(margin_left, y, data['jabatan'])

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# --- STREAMLIT APP ---

st.title("Generator Kwitansi Pembayaran (Random Data)")

# Generate random data otomatis tanpa input manual
def random_nomor():
    return f"{random.randint(1,999):03d}/XX-DEV/{random.randint(1,12):02d}/2025"

def random_tanggal():
    day = random.randint(1,28)
    month = random.choice([
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
    year = 2025
    return f"{day} {month} {year}"

def random_penerima():
    names = [
        "PT. Sukses Mandiri", "CV. Kreatif Solusi", "Yayasan Bantu Sesama",
        "Universitas Syiah Kuala", "Dinas Pendidikan Aceh"]
    return random.choice(names)

def random_jumlah():
    return random.choice([500000, 1000000, 1500000, 2500000, 6000000])

def random_keterangan():
    options = [
        """Pengembangan Website Acehnese Archive, meliputi:
- Pengembangan frontend (UI/UX, layout, navigasi)
- Pengembangan backend (struktur WordPress & admin panel)
- Manajemen konten awal
- Keamanan & server setup
- Revisi, meeting, dan koordinasi teknis""",
        """Pengadaan Alat Tulis Kantor:
- Pembelian kertas, pulpen, dan alat tulis lainnya
- Distribusi ke seluruh bagian
- Monitoring dan evaluasi penggunaan""",
        """Pelatihan Karyawan Baru:
- Modul pelatihan dasar
- Workshop dan seminar
- Evaluasi hasil pelatihan""",
    ]
    return random.choice(options)

def random_metode():
    return random.choice([
        "Transfer Bank BSI (Bank Syariah Indonesia)",
        "Tunai (Cash)",
        "Cek Giro",
        "Transfer Bank Mandiri"
    ])

def random_penerima_ttd():
    return random.choice(["Maulana Ihsan Ahmad", "Dewi Sartika", "Budi Santoso"])

def random_jabatan():
    return random.choice(["Developer", "Manager Keuangan", "Admin"])


data = {
    "nomor": random_nomor(),
    "tanggal": random_tanggal(),
    "penerima": random_penerima(),
    "jumlah_formatted": f"{random_jumlah():,}".replace(',', '.'),
    "jumlah_kata": number_to_indonesian_words(random_jumlah()),
    "keterangan": random_keterangan(),
    "metode": random_metode(),
    "penerima_ttd": random_penerima_ttd(),
    "jabatan": random_jabatan()
}

if st.button("Generate Kwitansi PDF dan Download"):
    pdf_buffer = create_kwitansi_pdf(data)
    st.success("Kwitansi berhasil dibuat!")
    st.download_button(
        label="Download Kwitansi PDF",
        data=pdf_buffer,
        file_name=f"kwitansi_{data['nomor'].replace('/','_')}.pdf",
        mime="application/pdf"
    )
else:
    st.info("Tekan tombol di atas untuk membuat kwitansi dengan data random.")

