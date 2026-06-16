import streamlit as st
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import io
import pandas as pd
import plotly.express as px

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
                    img_svd = compress_svd(img_original, k=30)
                    buf_svd = io.BytesIO()
                    img_svd.save(buf_svd, format='JPEG')
                    svd_bytes = buf_svd.getvalue()
                    svd_size = get_size(svd_bytes)
                    reduction_svd = calculate_reduction(orig_size, svd_size)
                    
                    st.image(img_svd, caption="SVD")
                    st.write(f"Ukuran: {svd_size:.2f} KB")
                    st.write(f"Reduksi: {reduction_svd:.2f}%")
                    st.download_button(label="Download", data=svd_bytes, file_name=f"svd_{file.name}", mime="image/jpeg", key=f"svd_{file.name}")

                # 2. K-Means
                with col2:
                    img_kmeans = compress_kmeans(img_original, colors=16)
                    buf_kmeans = io.BytesIO()
                    img_kmeans.save(buf_kmeans, format='JPEG')
                    kmeans_bytes = buf_kmeans.getvalue()
                    kmeans_size = get_size(kmeans_bytes)
                    reduction_kmeans = calculate_reduction(orig_size, kmeans_size)
                    
                    st.image(img_kmeans, caption="K-Means")
                    st.write(f"Ukuran: {kmeans_size:.2f} KB")
                    st.write(f"Reduksi: {reduction_kmeans:.2f}%")
                    st.download_button(label="Download", data=kmeans_bytes, file_name=f"kmeans_{file.name}", mime="image/jpeg", key=f"km_{file.name}")

                # 3. WebP
                with col3:
                    buf_webp = io.BytesIO()
                    img_original.save(buf_webp, format='WEBP', quality=50)
                    webp_bytes = buf_webp.getvalue()
                    webp_size = get_size(webp_bytes)
                    reduction_webp = calculate_reduction(orig_size, webp_size)
                    
                    img_webp_display = Image.open(buf_webp)
                    st.image(img_webp_display, caption="WebP")
                    st.write(f"Ukuran: {webp_size:.2f} KB")
                    st.write(f"Reduksi: {reduction_webp:.2f}%")
                    st.download_button(label="Download", data=webp_bytes, file_name=f"compressed_{file.name.rsplit('.', 1)[0]}.webp", mime="image/webp", key=f"wp_{file.name}")
                    
                st.divider()
                
                data_analisis.append({
                    'Nama File': file.name,
                    'SVD (%)': reduction_svd,
                    'K-Means (%)': reduction_kmeans,
                    'WebP (%)': reduction_webp
                })
                
        st.success('Semua gambar beres dikompresi!')
        
        st.markdown("## 📊 Grafik Analisis Perbandingan Reduksi Ukuran")
        st.write("Grafik ini nunjukin persentase efisiensi pengurangan file. Makin tinggi batang grafiknya, makin mantap kompresinya.")
        
        # Proses data biar grafiknya jejeran pakai Plotly
        df = pd.DataFrame(data_analisis)
        df_melted = df.melt(id_vars='Nama File', var_name='Algoritma', value_name='Reduksi Ukuran (%)')
        
        fig = px.bar(df_melted, x='Nama File', y='Reduksi Ukuran (%)', color='Algoritma', barmode='group')
        st.plotly_chart(fig, use_container_width=True)