# Sistem Absensi Face Recognition

Sistem absensi berbasis cloud yang mengimplementasikan teknologi pengenalan wajah (face recognition) dengan integrasi cloud computing dan AWS DynamoDB .

## Gambaran Umum

Proyek ini mengimplementasikan sistem absensi otomatis menggunakan teknologi pengenalan wajah, komputasi awan, dan AWS DynamoDB untuk meningkatkan akurasi dan transparansi dalam pencatatan kehadiran. Sistem ini dilengkapi dengan aplikasi client yang ringan, pemrosesan berbasis cloud, dan kemampuan pemantauan secara real-time.

## Arsitektur Sistem

Sistem terdiri dari tiga komponen utama:

1. **Aplikasi Client (`client.py`)**
   - Menangkap video secara real-time
   - Mendeteksi wajah dan mengirim data ke server cloud
   - Memberikan umpan balik visual untuk deteksi wajah

2. **Pemrosesan Server (`server.ipynb`)**
   - Berjalan di Google Colaboratory
   - Menangani pemrosesan pengenalan wajah
   - Mengelola interaksi dengan AWS DynamoDB
   - Memproses data kehadiran

3. **Dashboard Admin (`dashboard.py`)**
   - Pemantauan kehadiran secara real-time
   - Antarmuka pelaporan interaktif
   - Visualisasi analitik
   - Kontrol administratif

## Teknologi yang Digunakan


![python](./readme/icons8-python.gif)
![](./readme/deepface.gif)
![](./readme/aws.gif)
![](./readme/googlecolab.gif)
![](./readme/opencv.gif)
![](./readme/websokett.gif)
![](<img src="./readme/ngrok.avif" width="64" height="64" alt="ngrok logo">)

## Fitur

- Deteksi dan pengenalan wajah secara real-time
- Pemrosesan berbasis cloud untuk skalabilitas yang lebih baik
- Penyimpanan data yang aman di AWS DynamoDB
- Dashboard interaktif untuk pemantauan kehadiran
- Sistem umpan balik visual
- Pencatatan kehadiran otomatis

## Prasyarat

- Python 3.x
- Akun AWS dengan akses DynamoDB
- Akun Google (untuk Colaboratory)
- Koneksi internet yang stabil
- Paket Python yang diperlukan (lihat requirements.txt)

## Instalasi

1. Clone repositori:
    ```bash
    git clone [url-repositori]
    cd face-recognition-attendance
    ```

2. Instalasi paket yang diperlukan:
    ```bash
    pip install -r requirements ...
    ```

3. Konfigurasi kredensial AWS:
- Siapkan file kredensial AWS
- Konfigurasi akses DynamoDB

4. Menjalankan komponen:
    ```bash
    # Menjalankan aplikasi client
    python client.py

    # Menjalankan dashboard
    python dashboard.py

    # Buka dan jalankan server.ipynb di Google Colaboratory
    Server.ipynb
    ```

## Keterbatasan Saat Ini

- Membutuhkan koneksi internet yang stabil
- Akurasi pengenalan wajah bergantung pada kualitas gambar dan pencahayaan
- Batasan waktu sesi Google Colaboratory
- Latensi pemrosesan bergantung pada kondisi jaringan

## Rencana Pengembangan

1. Migrasi ke infrastruktur cloud yang lebih stabil
2. Implementasi mekanisme backup otomatis
3. Peningkatan akurasi pengenalan wajah
4. Kemampuan mode offline
5. Fitur keamanan lanjutan



## Kontribusi

Kontribusi untuk meningkatkan sistem ini sangat disambut. Silakan ikuti langkah-langkah berikut:

1. Fork repositori
2. Buat branch fitur
3. Commit perubahan Anda
4. Push ke branch
5. Buat Pull Request

## Lisensi

[...]

## Kontak

Jika Anda memiliki pertanyaan atau saran, silakan buka issue baru di repository ini.

[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/6285157517798)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/ryan.septiawan__/)

