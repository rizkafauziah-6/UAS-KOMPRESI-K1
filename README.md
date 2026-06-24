# **Studi Komparasi Algoritma Kompresi Gambar**

Aplikasi berbasis web interaktif untuk membandingkan performa tiga algoritma kompresi gambar: **SVD (Singular Value Decomposition)**, **K-Means Clustering**, dan **WebP (VP8 Codec)**.

🔗 **Live Demo:** [(https://uas-kompresi-k1-sismul.streamlit.app/)]

## **Fitur Utama**

* **Batch Processing:** Mendukung upload banyak gambar sekaligus.  
* **Auto-Optimization:** Gambar otomatis di-resize sebelum masuk algoritma komputasi berat agar proses instan.  
* **Real-time Preview:** Menampilkan perbandingan visual dan ukuran file secara langsung.  
* **Individual Download:** Tombol unduh khusus untuk tiap hasil kompresi.  
* **Data Visualization:** Dilengkapi grafik interaktif menggunakan Plotly untuk membandingkan persentase reduksi ukuran file.

## **Analisis Hasil Kompresi**

Berdasarkan grafik hasil pengujian pada 10 sampel gambar, ini hasil analisisnya:

* **WebP (Hijau):** Juara satu\! Algoritma ini ngasih reduksi file paling besar, stabil di angka 58% sampai 80%.  
* **SVD (Biru):** Juara dua. Lumayan oke buat motong ukuran file, rata-rata dapet di kisaran 36% sampai 58%.  
* **K-Means (Merah):** Paling buncit. Cuma bisa ngurangin ukuran file sekitar 16% sampai 42% aja buat sampel gambar-gambar ini.

**Kesimpulan:** Kalau butuh file sekecil mungkin, **WebP** adalah algoritma yang paling mantap dan direkomendasikan.

## **Teknologi yang Digunakan**

* **Bahasa:** Python  
* **Framework Web:** Streamlit  
* **Machine Learning & Math:** Scikit-learn, Numpy  
* **Image Processing:** Pillow  
* **Data Analytics:** Plotly, Pandas

## **Cara Menjalankan di Lokal**

1. Clone repository ini ke komputer kamu:  
   git clone \[https://github.com/username-kamu/nama-repo.git\](https://github.com/username-kamu/nama-repo.git)

2. Masuk ke folder project dan install dependensi:  
   pip install \-r requirements.txt

3. Jalankan aplikasi:  
   streamlit run app.py  
