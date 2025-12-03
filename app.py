import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

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

def create_kwitansi_pdf(data, ttd_image=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ==== WARNA DASAR HALAMAN ====
    c.setFillColor(colors.HexColor("#cfe2f3"))  # biru muda background
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # ==== KARTU PUTIH UTAMA (rounded) ====
    card_x = 1.5 * cm
    card_y = 2 * cm
    card_width = width - 3 * cm
    card_height = height - 4 * cm

    c.setFillColor(colors.white)
    c.roundRect(card_x, card_y, card_width, card_height, 18, stroke=0, fill=1)

    # ==== HEADER DI DALAM KARTU ====
    header_height = 3 * cm
    c.setFillColor(colors.HexColor("#cfe2f3"))
    c.roundRect(card_x, card_y + card_height - header_height,
                card_width, header_height, 18, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawCentredString(card_x + card_width / 2,
                        card_y + card_height - header_height/2 + 4,
                        "KWITANSI PEMBAYARAN")

    # Garis putih pemisah header
    c.setStrokeColor(colors.white)
    c.setLineWidth(3)
    c.line(card_x, card_y + card_height - header_height,
           card_x + card_width, card_y + card_height - header_height)

    # ==== KONTEN DALAM KARTU ====
    margin_left = card_x + 1.3 * cm
    y = card_y + card_height - header_height - 1.0 * cm
    line_height = 16

    # Baris nomor & tanggal
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawString(margin_left, y, f"Nomor: {data['nomor']}")
    c.drawRightString(card_x + card_width - 1.3*cm, y,
                      f"Tanggal: {data['tanggal']}")
    y -= line_height * 2

    # Telah diterima dari
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin_left, y, "Telah diterima dari:")
    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left + 15, y, data['penerima'])
    y -= line_height * 2

    # Jumlah uang
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

    # Untuk pembayaran
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin_left, y, "Untuk pembayaran:")
    y -= line_height

    # Kotak deskripsi pembayaran
    keterangan_lines = data['keterangan'].split('\n')
    box_height = line_height * (len(keterangan_lines) + 1.5)
    box_width = card_width - 2.6*cm
    box_x = margin_left
    box_y = y - box_height

    y_in_box = y
    c.setFont("Helvetica-Bold", 12)
    # judul keterangan (baris pertama sebelum titik dua)
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

    # Metode pembayaran
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(margin_left, y, "Metode pembayaran:")
    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#1f4e79"))
    c.drawString(margin_left + 15, y, data['metode'])
    y -= line_height * 3

    # Tanda tangan
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

st.title("Generator Kwitansi Pembayaran")

# Input form
nomor = st.text_input("Nomor Kwitansi", value="", placeholder="contoh: 001/AA-DEV/XII/2025")
tanggal = st.date_input("Tanggal", datetime.now())  # tanggal date_input tidak ada placeholder, biarkan default sekarang
penerima = st.text_input("Telah diterima dari", value="", placeholder="contoh: PT. Sumber Uang")
jumlah = st.number_input("Jumlah Uang (Rp)", min_value=0, step=1000, value=0, format="%d")
keterangan = st.text_area("Untuk pembayaran", value="", placeholder="contoh: Pengembangan Website, meliputi:\n- Pengembangan frontend (UI/UX, layout, navigasi)\n- Pengembangan backend (struktur WordPress & admin panel)\n- Manajemen konten awal\n- Keamanan & server setup\n- Revisi, meeting, dan koordinasi teknis")
metode = st.text_input("Metode pembayaran", value="", placeholder="contoh: Transfer Bank X")
penerima_ttd = st.text_input("Penerima pembayaran (Nama)", value="", placeholder="contoh: Nama Anda")
jabatan = st.text_input("Jabatan penerima", value="", placeholder="contoh: (Developer)")


# Upload tanda tangan
uploaded_ttd = st.file_uploader("Upload gambar tanda tangan (PNG/JPG)", type=["png", "jpg", "jpeg"])

ttd_image = None
if uploaded_ttd:
    img = Image.open(uploaded_ttd)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        # Buat background putih
        background = Image.new("RGB", img.size, (255, 255, 255))
        # Paste img di background dengan mask alpha channel
        background.paste(img, mask=img.split()[-1])
        ttd_image = background
    else:
        ttd_image = img.convert("RGB")

if st.button("Generate Kwitansi dan Download PDF"):
    jumlah_int = int(jumlah)
    jumlah_kata = number_to_indonesian_words(jumlah_int)
    jumlah_formatted = f"{jumlah_int:,.0f}".replace(',', '.')

    data = {
        "nomor": nomor,
        # lebih kompatibel di Windows juga
        "tanggal": f"{tanggal.day} {tanggal.strftime('%B %Y')}",
        "penerima": penerima,
        "jumlah_formatted": jumlah_formatted,
        "jumlah_kata": jumlah_kata,
        "keterangan": keterangan,
        "metode": metode,
        "penerima_ttd": penerima_ttd,
        "jabatan": jabatan
    }

    pdf_buffer = create_kwitansi_pdf(data, ttd_image)
    st.success("Kwitansi berhasil dibuat!")
    st.download_button(
        label="Download Kwitansi PDF",
        data=pdf_buffer,
        file_name=f"kwitansi_{nomor.replace('/','_')}.pdf",
        mime="application/pdf"
    )