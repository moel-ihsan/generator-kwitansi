# Generator Kwitansi Pembayaran - Streamlit

Aplikasi web sederhana untuk **membuat kwitansi pembayaran dalam format PDF** dengan desain modern dan fitur upload tanda tangan digital.

## Fitur

- Input data kwitansi seperti nomor, tanggal, penerima, jumlah uang, keterangan, metode pembayaran, dan tanda tangan.
- Otomatis mengkonversi angka jumlah uang ke dalam teks bahasa Indonesia (terbilang).
- Desain kwitansi dengan latar belakang dan layout rapi menggunakan ReportLab.
- Upload gambar tanda tangan (PNG/JPG) dan otomatis menyesuaikan ukuran.
- Generate dan download kwitansi dalam format PDF langsung dari browser.
- Input form menggunakan placeholder (default kosong, hanya petunjuk).

## Cara Pakai

1. Pastikan Python 3.7+ sudah terinstall di komputer kamu.
2. Clone repository ini atau download file `app.py` dan `requirements.txt`.
3. Install dependencies dengan perintah:

    ```bash
    pip install -r requirements.txt
    ```

4. Jalankan aplikasi Streamlit:

    ```bash
    streamlit run app.py
    ```

5. Buka browser dan akses http://localhost:8501 untuk mulai menggunakan aplikasi.

## Struktur File

- `app.py` : Script utama aplikasi Streamlit untuk generate kwitansi.
- `requirements.txt` : Daftar library Python yang dibutuhkan (streamlit, reportlab, pillow).

## Contoh Penggunaan

- Masukkan nomor kwitansi pada kolom Nomor Kwitansi (placeholder contoh: `001/AA-DEV/XII/2025`).
- Pilih tanggal kwitansi.
- Isi nama penerima, jumlah uang, keterangan pembayaran, metode pembayaran, nama penerima tanda tangan, dan jabatan.
- Upload file gambar tanda tangan (opsional).
- Klik tombol **Generate Kwitansi dan Download PDF**.
- Kwitansi PDF siap didownload.

## Lisensi

MIT License

---

**Developed by Maulana Ihsan Ahmad**

