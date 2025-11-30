import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

# ===================================================================
# FUNGSI-FUNGSI BERSAMA (Helpers)
# ===================================================================

# Fungsi-fungsi load_image_from_upload, to_rgb, dan plot_histogram
# tetap sama seperti sebelumnya
def load_image_from_upload(uploader):
    """Membaca file uploader Streamlit menjadi gambar OpenCV."""
    if uploader is not None:
        file_bytes = np.asarray(bytearray(uploader.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        if image is None:
             st.error("Gagal memuat gambar. Pastikan format file benar.")
             return None
        return image
    return None

def to_rgb(image):
    """Konversi gambar BGR (OpenCV) ke RGB (Streamlit/PIL)."""
    if image is None:
        return None
    if len(image.shape) == 2 or image.shape[2] == 1:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def plot_histogram(image):
    """Membuat grafik histogram dari gambar BGR atau Grayscale."""
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.set_title("Histogram Intensitas Piksel", fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=6)
    
    if len(image.shape) == 2 or image.shape[2] == 1:
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        ax.plot(hist, color='black', linewidth=1)
        ax.set_xlim([0, 256])
    else:
        colors = ('b', 'g', 'r')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            ax.plot(hist, color=color, linewidth=1, label=color.upper())
        ax.set_xlim([0, 256])
        ax.legend(fontsize=6)
    
    plt.close(fig)
    return fig

# ===================================================================
# FUNGSI-FUNGSI TEKNIK (Tidak Berubah)
# ===================================================================
def apply_equalization(image):
    if image is None: return None
    if len(image.shape) == 3:
        img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    return cv2.equalizeHist(image)

def apply_sharpening(image, amount, ksize):
    if image is None: return None
    k_size_odd = (ksize * 2) + 1
    blurred = cv2.GaussianBlur(image, (k_size_odd, k_size_odd), 0)
    sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
    return sharpened

def apply_noise_reduction(image, filter_type, ksize):
    if image is None: return None
    k_size_odd = (ksize * 2) + 1
    if filter_type == "Gaussian Blur":
        return cv2.GaussianBlur(image, (k_size_odd, k_size_odd), 0)
    elif filter_type == "Median Blur":
        return cv2.medianBlur(image, k_size_odd)
    return image

def apply_edge_detection(image_bgr, method, thresh1, thresh2, blur_ksize):
    if image_bgr is None: return None
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur_k_odd = (blur_ksize * 2) + 1
    blurred_image = cv2.GaussianBlur(gray, (blur_k_odd, blur_k_odd), 0)
    
    if method == "Canny":
        return cv2.Canny(blurred_image, thresh1, thresh2)
    elif method == "Sobel":
        sobel_x = cv2.Sobel(blurred_image, cv2.CV_64F, 1, 0, ksize=5)
        sobel_y = cv2.Sobel(blurred_image, cv2.CV_64F, 0, 1, ksize=5)
        sobel_abs = cv2.magnitude(sobel_x, sobel_y)
        return cv2.convertScaleAbs(sobel_abs)
    return blurred_image

def apply_morphology(image_mask, morph_type, ksize):
    if image_mask is None: return None
    # Pastikan input adalah 1 channel (grayscale/binary)
    if len(image_mask.shape) == 3:
         image_mask = cv2.cvtColor(image_mask, cv2.COLOR_BGR2GRAY)
         
    kernel = np.ones((ksize, ksize), np.uint8)
    if morph_type == "Opening":
        return cv2.morphologyEx(image_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    elif morph_type == "Closing":
        return cv2.morphologyEx(image_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    return image_mask

def apply_geometric(image, angle, scale):
    if image is None: return None
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    return cv2.warpAffine(image, M, (w, h))

# ===================================================================
# APLIKASI UTAMA (STREAMLIT)
# ===================================================================

st.set_page_config(layout="wide", page_title="Vehicle Image Analysis (UAS)")

st.title("Vehicle Image Analysis Toolbox 🚗")
st.markdown("Aplikasi berbasis 6 Teknik Image Processing untuk UAS.")
st.markdown("---")

# --- FILE UPLOADER (Pusat - di Sidebar) ---
st.sidebar.title("Kontrol File")
uploaded_file = st.sidebar.file_uploader("Upload Gambar Kendaraan (Drag & Drop)", type=["jpg", "jpeg", "png", "bmp"], key="uploader_main")
original_image = load_image_from_upload(uploaded_file)

if original_image is None:
    st.info("👈 Silakan upload gambar melalui sidebar untuk memulai analisis.")
    st.stop()

# --- TABS SESUAI 6 TEKNIK ---
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🖼️ Original & Info",
    "📈 1. Histogram EQ",
    "🧼 2. Noise Filtering",
    "🔪 3. Sharpening",
    "⚫ 4. Edge Detection",
    "⚙️ 5. Morphology Ops",
    "🔄 6. Geometric Transform"
])

# ===================================================================
# --- TAB 0: ORIGINAL & INFO ---
# ===================================================================
with tab0:
    st.header("Gambar Original & Metadata")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Original Image (BGR)")
        st.image(to_rgb(original_image), use_column_width=True, caption=f"Original Size: {original_image.shape[1]}x{original_image.shape[0]}")
    with colB:
        st.subheader("Analisis Histogram Awal")
        st.pyplot(plot_histogram(original_image))
        st.info("Gunakan Tab 1 untuk membandingkan perubahan kontras.")

# ===================================================================
# --- TAB 1: HISTOGRAM EQUALIZATION ---
# ===================================================================
with tab1:
    st.header("1. Histogram Equalization")
    st.write("Teknik untuk mengatasi gambar **low-light/over-exposed** dan meningkatkan kontras.")
    
    # KONTROL KHUSUS TAB INI (sederhana: ON/OFF)
    use_eq = st.checkbox("Terapkan Histogram Equalization (YUV)", value=False, key="t1_use_eq")

    processed_eq = apply_equalization(original_image.copy()) if use_eq else original_image.copy()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(to_rgb(original_image), use_column_width=True)
        st.pyplot(plot_histogram(original_image))
    
    with col2:
        st.subheader("Hasil Equalization")
        st.image(to_rgb(processed_eq), use_column_width=True)
        st.pyplot(plot_histogram(processed_eq))

# ===================================================================
# --- TAB 2: NOISE FILTERING ---
# ===================================================================
with tab2:
    st.header("2. Noise Filtering (Smoothing)")
    st.write("Membersihkan **noise** (bintik) sebelum deteksi tepi.")
    
    # KONTROL KHUSUS TAB INI
    st.markdown("### Kontrol Parameter Filter")
    filter_type = st.selectbox("Tipe Filter", ["Gaussian Blur", "Median Blur"], key="t2_filter_select")
    kernel_size_filter = st.slider("Kernel Size (N*2 + 1)", 0, 10, 2, key="t2_filter_ksize")
    
    processed_filter = apply_noise_reduction(original_image.copy(), filter_type, kernel_size_filter)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(to_rgb(original_image), use_column_width=True)
        st.caption("Fokus pada area gelap untuk melihat noise.")
    with col2:
        k_size_val = (kernel_size_filter * 2) + 1
        st.subheader(f"Hasil {filter_type} (K={k_size_val})")
        st.image(to_rgb(processed_filter), use_column_width=True)
        st.caption("Noise berkurang, tepi menjadi lebih stabil.")
        
# ===================================================================
# --- TAB 3: SHARPENING ---
# ===================================================================
with tab3:
    st.header("3. Sharpening (Ketajaman)")
    st.write("Menajamkan tepi dan detail yang tumpul/kabur pada kendaraan.")
    
    # KONTROL KHUSUS TAB INI
    st.markdown("### Kontrol Parameter Sharpening")
    sharpen_amount = st.slider("Strength (Amount)", 0.0, 5.0, 1.5, 0.1, key="t3_sharp_amount")
    sharpen_ksize = st.slider("Detail Kernel (N*2+1)", 1, 10, 2, key="t3_sharp_ksize")

    if sharpen_amount > 0:
        processed_sharp = apply_sharpening(original_image.copy(), sharpen_amount, sharpen_ksize)
    else:
        processed_sharp = original_image.copy()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(to_rgb(original_image), use_column_width=True)
    with col2:
        st.subheader(f"Hasil Sharpening (A={sharpen_amount})")
        st.image(to_rgb(processed_sharp), use_column_width=True)
        st.caption("Garis kendaraan terlihat lebih tegas dan detail.")
        
# ===================================================================
# --- TAB 4: EDGE DETECTION ---
# ===================================================================
with tab4:
    st.header("4. Edge Detection (Outline Kendaraan)")
    st.write("Ekstraksi tepi kendaraan sebagai fitur utama untuk AI recognition/counting.")
    
    # KONTROL KHUSUS TAB INI
    st.markdown("### Kontrol Parameter Edge Detection")
    edge_method = st.selectbox("Metode Deteksi Tepi", ["Canny", "Sobel"], key="t4_edge_method")
    edge_blur_ksize = st.slider("Blur Pre-Edge (N*2+1) [Opsional]", 0, 5, 1, key="t4_edge_blur")
    
    thresh1, thresh2 = 50, 150
    if edge_method == "Canny":
        thresh1 = st.slider("Canny Threshold 1 (MinVal)", 0, 255, 50, key="t4_canny1")
        thresh2 = st.slider("Canny Threshold 2 (MaxVal)", 0, 255, 150, key="t4_canny2")
        
    edges = apply_edge_detection(original_image.copy(), edge_method, thresh1, thresh2, edge_blur_ksize)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(to_rgb(original_image), use_column_width=True)
    with col2:
        st.subheader(f"Hasil {edge_method} Edges")
        st.image(edges, use_column_width=True, caption="Outline kendaraan murni (Grayscale)")
        st.info("Edges murni ini adalah input ideal untuk Morphology (Tab 5).")

# ===================================================================
# --- TAB 5: MORPHOLOGICAL OPERATIONS ---
# ===================================================================
with tab5:
    st.header("5. Morphological Operations")
    st.write("Merapikan hasil *edge* atau *mask* (menutup celah/menghapus noise) agar kontur solid.")
    
    # KONTROL KHUSUS TAB INI
    st.markdown("### Kontrol Parameter Morphology")
    morph_type = st.selectbox("Tipe Operasi", ["Opening", "Closing"], key="t5_morph_select")
    kernel_size_morph = st.slider("Ukuran Kernel", 1, 10, 2, key="t5_morph_ksize")

    st.markdown("---")
    st.subheader("Input Image (Asumsi Edge Detection)")
    
    # Kita menggunakan hasil Edge Canny dasar sebagai input untuk Morphology
    edges_input = apply_edge_detection(original_image.copy(), "Canny", 50, 150, 1)

    processed_morph = apply_morphology(edges_input, morph_type, kernel_size_morph)
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Input: Raw Canny Edge. Fokus pada noise/celah.")
        st.image(edges_input, use_column_width=True)
    with col2:
        st.caption(f"Hasil {morph_type} (K={kernel_size_morph})")
        st.image(processed_morph, use_column_width=True)
        st.info(f"{morph_type} membuat kontur lebih rapi/solid.")

# ===================================================================
# --- TAB 6: GEOMETRIC TRANSFORMATIONS ---
# ===================================================================
with tab6:
    st.header("6. Geometric Transformations")
    st.write("Meluruskan gambar, memperbaiki distorsi, atau merotasi kendaraan.")
    
    # KONTROL KHUSUS TAB INI
    st.markdown("### Kontrol Parameter Geometric")
    angle = st.slider("Rotasi (Derajat)", -45, 45, 0, key="t6_angle") # Rentang Rotasi diperluas
    scale = st.slider("Zoom (Scaling)", 0.5, 2.0, 1.0, 0.1, key="t6_scale")
    
    processed_geom = apply_geometric(original_image.copy(), angle, scale)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(to_rgb(original_image), use_column_width=True)
    with col2:
        st.subheader(f"Hasil Transformasi (R={angle}°, S={scale})")
        st.image(to_rgb(processed_geom), use_column_width=True, caption="Citra kendaraan meluruskan/dirotasi.")
        st.info("Teknik ini menormalisasi orientasi kendaraan sebelum AI processing.")

# ===================================================================
# --- DOWNLOAD BUTTON (Samping) ---
# ===================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Download Output")
st.sidebar.write("Pilih hasil dari tab mana yang ingin diunduh:")

# Contoh: Download Sharpening
if st.sidebar.button("Download Sharpening (Tab 3 Output)"):
    # Kita harus panggil lagi fungsi dengan nilai terakhir (yang tersimpan di state)
    final_sharp_amount = st.session_state.t3_sharp_amount
    final_sharp_ksize = st.session_state.t3_sharp_ksize
    final_img_download = apply_sharpening(original_image.copy(), final_sharp_amount, final_sharp_ksize)
    
    is_success, buffer = cv2.imencode(".png", final_img_download)
    if is_success:
        st.sidebar.download_button(
            label="📥 Download Sharpening", 
            data=buffer.tobytes(), 
            file_name=f"sharpened_{uploaded_file.name}", 
            mime="image/png"
        )