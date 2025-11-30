# 🚗 Interactive Image Processing Demo (Vehicle Analysis)

Aplikasi berbasis Streamlit yang berfungsi sebagai *Interactive Image Processing Toolbox*. Proyek ini mendemonstrasikan 6 teknik fundamental dalam Pengolahan Citra Digital untuk meningkatkan kualitas (enhancement) dan mengekstrak fitur (feature extraction) dari citra, khususnya pada konteks **analisis citra kendaraan**.

Pengguna dapat mengunggah gambar dan menyesuaikan parameter *real-time* untuk setiap teknik.

## 🚀 Coba Aplikasinya Sekarang!

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vehicle-image-processing.streamlit.app/)

Klik *badge* di atas untuk mengakses aplikasi secara langsung dan menguji berbagai teknik *Image Processing* pada citra kendaraan Anda.

## 🛠️ Teknik yang Diimplementasikan

Proyek ini mengimplementasikan sebuah *pipeline* berjenjang (step-by-step) melalui tab yang terpisah, meliputi:

| No. | Teknik | Tujuan Fungsional |
| :--- | :--- | :--- |
| **1.** | **Histogram Equalization** | Normalisasi kontras; mengatasi foto **under/over-exposed**. |
| **2.** | **Noise Filtering** | Membersihkan **noise** (butiran acak) agar tepi lebih stabil. |
| **3.** | **Sharpening** | Meningkatkan **ketajaman** dan menonjolkan detail kendaraan yang kabur. |
| **4.** | **Edge Detection** | Ekstraksi **outline** (tepi) kendaraan yang jelas (Canny/Sobel). |
| **5.** | **Morphological Ops** | Merapikan hasil tepi/mask (Closing/Opening) untuk kontur yang **solid**. |
| **6.** | **Geometric Transform** | **Normalisasi** orientasi gambar (Rotasi/Scaling) sebelum pemrosesan AI. |

## 🚀 Instalasi dan Menjalankan Aplikasi

Aplikasi ini memerlukan Python 3.10+ (disarankan menggunakan **venv**).

1.  **Clone Repository:**
    ```bash
    git clone [https://github.com/YourUsername/image-processing-interactive-demo.git](https://github.com/YourUsername/image-processing-interactive-demo.git)
    cd image-processing-interactive-demo
    ```

2.  **Setup Virtual Environment (Disarankan):**
    ```bash
    # Ganti 'python3.12' sesuai versi yang Anda gunakan
    python3.12 -m venv .venv 
    source .venv/bin/activate  # atau .\ .venv\Scripts\activate di Windows
    ```

3.  **Instal Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan Streamlit:**
    ```bash
    streamlit run app.py
    ```
    Buka URL yang muncul di browser Anda (biasanya `http://localhost:8501`).