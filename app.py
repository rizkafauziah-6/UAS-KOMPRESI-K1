import streamlit as st
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import io
import pandas as pd
import plotly.express as px
import time
import math

def get_size(byte_data):
    return len(byte_data) / 1024  # dalam KB

def calculate_reduction(original, compressed):
    if original == 0:
        return 0
    return ((original - compressed) / original) * 100

def compress_svd(img, k=30):
    img_array = np.array(img)
    compressed_channels = []
    for i in range(3):
        U, S, V = np.linalg.svd(img_array[:, :, i], full_matrices=False)
        compressed_channel = np.dot(U[:, :k], np.dot(np.diag(S[:k]), V[:k, :]))
        compressed_channels.append(compressed_channel)
    
    img_compressed = np.stack(compressed_channels, axis=2)
    img_compressed = np.clip(img_compressed, 0, 255).astype('uint8')
    return Image.fromarray(img_compressed)

def compress_kmeans(img, colors=16):
    img_array = np.array(img)
    w, h, d = img_array.shape
    img_reshaped = img_array.reshape(w * h, d)
    
    kmeans = KMeans(n_clusters=colors, n_init=1, random_state=42).fit(img_reshaped[::20])
    labels = kmeans.predict(img_reshaped)
    
    img_compressed = kmeans.cluster_centers_[labels].reshape(w, h, d)
    img_compressed = np.clip(img_compressed, 0, 255).astype('uint8')
    return Image.fromarray(img_compressed)

def calculate_psnr(img1, img2):
    # img1, img2: PIL Images in RGB and same size
    arr1 = np.array(img1).astype(np.float64)
    arr2 = np.array(img2).astype(np.float64)
    if arr1.shape != arr2.shape:
        return 0.0
    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        return float('inf')
    max_i = 255.0
    psnr = 20 * math.log10(max_i) - 10 * math.log10(mse)
    return psnr

st.title("Studi Komparasi Kompresi Gambar")
st.write("Silakan upload minimal 10 gambar JPEG/JPG untuk diuji.")

uploaded_files = st.file_uploader("Upload Gambar", type=['jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    st.write(f"**Total gambar diupload: {len(uploaded_files)}**")
    
    if st.button("Mulai Kompresi"):
        with st.spinner('Tunggu bentar ya, lagi proses kompresi...'):
            data_analisis = []
            
            for file in uploaded_files:
                st.markdown(f"### File: {file.name}")
                
                img_original = Image.open(file).convert('RGB')
                img_original.thumbnail((500, 500)) 
                
                buf_orig = io.BytesIO()
                img_original.save(buf_orig, format='JPEG', quality=90)
                orig_bytes = buf_orig.getvalue()
                orig_size = get_size(orig_bytes)
                
                st.image(img_original, caption=f"Original (Resized, {orig_size:.2f} KB)", width=300)
                
                col1, col2, col3 = st.columns(3)
                
                # 1. SVD
                with col1:
                    t0 = time.perf_counter()
                    img_svd = compress_svd(img_original, k=30)
                    t1 = time.perf_counter()
                    time_svd = t1 - t0
                    buf_svd = io.BytesIO()
                    img_svd.save(buf_svd, format='JPEG')
                    svd_bytes = buf_svd.getvalue()
                    svd_size = get_size(svd_bytes)
                    reduction_svd = calculate_reduction(orig_size, svd_size)
                    psnr_svd = calculate_psnr(img_original, img_svd)
                    ratio_svd = orig_size / svd_size if svd_size > 0 else 0
                    
                    st.image(img_svd, caption="SVD")
                    st.write(f"Ukuran: {svd_size:.2f} KB")
                    st.write(f"Reduksi: {reduction_svd:.2f}%")
                    st.write(f"PSNR: {psnr_svd:.2f} dB")
                    st.write(f"Rasio kompresi: {ratio_svd:.2f}x")
                    st.write(f"Waktu proses: {time_svd:.3f} s")
                    st.download_button(label="Download", data=svd_bytes, file_name=f"svd_{file.name}", mime="image/jpeg", key=f"svd_{file.name}")

                # 2. K-Means
                with col2:
                    t0 = time.perf_counter()
                    img_kmeans = compress_kmeans(img_original, colors=16)
                    t1 = time.perf_counter()
                    time_kmeans = t1 - t0
                    buf_kmeans = io.BytesIO()
                    img_kmeans.save(buf_kmeans, format='JPEG')
                    kmeans_bytes = buf_kmeans.getvalue()
                    kmeans_size = get_size(kmeans_bytes)
                    reduction_kmeans = calculate_reduction(orig_size, kmeans_size)
                    psnr_km = calculate_psnr(img_original, img_kmeans)
                    ratio_km = orig_size / kmeans_size if kmeans_size > 0 else 0
                    
                    st.image(img_kmeans, caption="K-Means")
                    st.write(f"Ukuran: {kmeans_size:.2f} KB")
                    st.write(f"Reduksi: {reduction_kmeans:.2f}%")
                    st.write(f"PSNR: {psnr_km:.2f} dB")
                    st.write(f"Rasio kompresi: {ratio_km:.2f}x")
                    st.write(f"Waktu proses: {time_kmeans:.3f} s")
                    st.download_button(label="Download", data=kmeans_bytes, file_name=f"kmeans_{file.name}", mime="image/jpeg", key=f"km_{file.name}")

                # 3. WebP
                with col3:
                    t0 = time.perf_counter()
                    buf_webp = io.BytesIO()
                    img_original.save(buf_webp, format='WEBP', quality=50)
                    t1 = time.perf_counter()
                    time_webp = t1 - t0
                    webp_bytes = buf_webp.getvalue()
                    webp_size = get_size(webp_bytes)
                    reduction_webp = calculate_reduction(orig_size, webp_size)
                    
                    img_webp_display = Image.open(buf_webp)
                    st.image(img_webp_display, caption="WebP")
                    st.write(f"Ukuran: {webp_size:.2f} KB")
                    st.write(f"Reduksi: {reduction_webp:.2f}%")
                    psnr_webp = calculate_psnr(img_original, img_webp_display)
                    ratio_webp = orig_size / webp_size if webp_size > 0 else 0
                    st.write(f"PSNR: {psnr_webp:.2f} dB")
                    st.write(f"Rasio kompresi: {ratio_webp:.2f}x")
                    st.write(f"Waktu proses: {time_webp:.3f} s")
                    st.download_button(label="Download", data=webp_bytes, file_name=f"compressed_{file.name.rsplit('.', 1)[0]}.webp", mime="image/webp", key=f"wp_{file.name}")
                    
                st.divider()
                
                data_analisis.append({
                    'Nama File': file.name,
                    'SVD (%)': reduction_svd,
                    'K-Means (%)': reduction_kmeans,
                    'WebP (%)': reduction_webp,
                    'SVD PSNR (dB)': psnr_svd,
                    'K-Means PSNR (dB)': psnr_km,
                    'WebP PSNR (dB)': psnr_webp,
                    'SVD Ratio': ratio_svd,
                    'K-Means Ratio': ratio_km,
                    'WebP Ratio': ratio_webp,
                    'SVD Time (s)': time_svd,
                    'K-Means Time (s)': time_kmeans,
                    'WebP Time (s)': time_webp
                })
                
        st.success('Semua gambar beres dikompresi!')
        
        st.markdown("## 📊 Grafik Analisis")
        st.write("Grafik menampilkan perbandingan Reduksi Ukuran, PSNR, dan Rasio Kompresi untuk tiap algoritma.")

        df = pd.DataFrame(data_analisis)

        # Reduksi ukuran
        df_red = df[['Nama File', 'SVD (%)', 'K-Means (%)', 'WebP (%)']]
        df_red_melt = df_red.melt(id_vars='Nama File', var_name='Algoritma', value_name='Reduksi (%)')
        fig1 = px.bar(df_red_melt, x='Nama File', y='Reduksi (%)', color='Algoritma', barmode='group', title='Reduksi Ukuran (%)')
        st.plotly_chart(fig1, use_container_width=True)

        # PSNR
        df_psnr = df[['Nama File', 'SVD PSNR (dB)', 'K-Means PSNR (dB)', 'WebP PSNR (dB)']]
        df_psnr_melt = df_psnr.melt(id_vars='Nama File', var_name='Algoritma', value_name='PSNR (dB)')
        # Tampilkan PSNR (nilai lebih tinggi = lebih baik)
        fig2 = px.bar(df_psnr_melt, x='Nama File', y='PSNR (dB)', color='Algoritma', barmode='group', title='PSNR (dB)')
        st.plotly_chart(fig2, use_container_width=True)

        # Rasio kompresi
        df_ratio = df[['Nama File', 'SVD Ratio', 'K-Means Ratio', 'WebP Ratio']]
        df_ratio_melt = df_ratio.melt(id_vars='Nama File', var_name='Algoritma', value_name='Rasio')
        fig3 = px.bar(df_ratio_melt, x='Nama File', y='Rasio', color='Algoritma', barmode='group', title='Rasio Kompresi (orig_size / comp_size)')
        st.plotly_chart(fig3, use_container_width=True)

        # Tabel ringkasan
        st.markdown("### Ringkasan Data")
        st.dataframe(df)