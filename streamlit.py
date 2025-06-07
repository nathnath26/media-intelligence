import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Dasbor Analitik Kampanye",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styling ---
# Menambahkan CSS kustom untuk tema gelap modern
st.markdown("""
<style>
    /* Latar belakang utama */
    .stApp {
        background-image: linear-gradient(to br, #111827, #1f2937);
        color: #e5e7eb;
    }

    /* Kontainer seperti kartu */
    .st-emotion-cache-1r4qj8v, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1y4p8pa {
        background-color: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid #4b5563;
        border-radius: 1rem;
        padding: 1.5rem;
    }

    /* Header dan judul */
    h1, h2, h3 {
        color: #ffffff;
    }

    /* Widget input */
    .stSelectbox > div > div > div, .stDateInput > div > div > input {
        background-color: #374151;
        border-radius: 0.5rem;
    }
    
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border-radius: 9999px;
        border: none;
        padding: 0.5rem 1.25rem;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
    }

    /* Latar belakang grafik Plotly */
    .stPlotlyChart {
        border-radius: 0.5rem;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --- Fungsi ---

@st.cache_data
def clean_data(uploaded_file):
    """
    Membersihkan dan memproses data CSV yang diunggah.
    Menyimpan hasil di cache untuk menghindari pemrosesan ulang pada setiap interaksi.
    """
    if uploaded_file is None:
        return None

    try:
        # Untuk membaca file dari unggahan
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(stringio)

        # Pembersihan Data
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0).astype(int)

        # Hapus baris di mana Tanggal menjadi NaT setelah konversi
        df.dropna(subset=['Date'], inplace=True)
        return df

    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
        return None

def generate_summary(df):
    """Menghasilkan ringkasan aksi utama berdasarkan data yang difilter."""
    if df.empty:
        return ""

    try:
        # 1. Platform teratas berdasarkan keterlibatan
        platform_engagements = df.groupby('Platform')['Engagements'].sum()
        top_platform = platform_engagements.idxmax() if not platform_engagements.empty else 'Tidak Tersedia'

        # 2. Sentimen dominan
        dominant_sentiment = df['Sentiment'].mode()[0] if not df['Sentiment'].empty else 'Tidak Tersedia'

        # 3. Tipe media yang paling sering digunakan
        top_media_type = df['Media Type'].mode()[0] if not df['Media Type'].empty else 'Tidak Tersedia'

        # 4. Lokasi teratas berdasarkan jumlah postingan
        top_location = df['Location'].mode()[0] if not df['Location'].empty else 'Tidak Tersedia'

        summary = f"""
        <ul>
            <li style="margin-bottom: 8px;"><strong>Platform Utama:</strong> Fokuskan sumber daya di <strong>{top_platform}</strong>, karena platform ini menghasilkan keterlibatan tertinggi.</li>
            <li style="margin-bottom: 8px;"><strong>Konten Paling Efektif:</strong> Konten berjenis <strong>{top_media_type}</strong> paling sering digunakan. Pertimbangkan untuk meningkatkan produksi konten ini.</li>
            <li style="margin-bottom: 8px;"><strong>Persepsi Audiens:</strong> Sentimen yang dominan adalah <strong>{dominant_sentiment}</strong>. Manfaatkan suasana positif ini, atau jika negatif, selidiki penyebabnya.</li>
            <li style="margin-bottom: 8px;"><strong>Target Geografis:</strong> <strong>{top_location}</strong> adalah lokasi dengan aktivitas tertinggi. Pertimbangkan untuk membuat kampanye yang dilokalkan untuk area ini.</li>
        </ul>
        """
        return summary
    except Exception:
        return "Gagal membuat ringkasan. Periksa kolom data Anda."

# --- Aplikasi Utama ---

st.title("📊 Dasbor Analitik Kampanye")
st.markdown("<p style='color: #9ca3af;'>Unggah data kampanye Anda untuk visualisasi dan wawasan strategis.</p>", unsafe_allow_html=True)


# --- Sidebar untuk Filter dan Unggah ---
with st.sidebar:
    st.header("✨ Kontrol & Filter")
    
    uploaded_file = st.file_uploader(
        "Unggah Data Kampanye (CSV)",
        type=['csv'],
        help="Pastikan file CSV Anda memiliki kolom: 'Date', 'Platform', 'Engagements', 'Sentiment', 'Media Type', 'Location'"
    )
    
    df_original = clean_data(uploaded_file)
    df_filtered = pd.DataFrame()

    if df_original is not None:
        st.success(f"Data berhasil dimuat! {len(df_original)} catatan ditemukan.")
        st.markdown("---")
        st.header("⚙️ Filter Data")

        platforms = ['All'] + sorted(df_original['Platform'].unique().tolist())
        sentiments = ['All'] + sorted(df_original['Sentiment'].unique().tolist())
        media_types = ['All'] + sorted(df_original['Media Type'].unique().tolist())
        locations = ['All'] + sorted(df_original['Location'].unique().tolist())
        
        min_date = df_original['Date'].min().date()
        max_date = df_original['Date'].max().date()

        selected_platform = st.selectbox("Platform", platforms)
        selected_sentiment = st.selectbox("Sentimen", sentiments)
        selected_media_type = st.selectbox("Tipe Media", media_types)
        selected_location = st.selectbox("Lokasi", locations)
        
        date_range = st.date_input(
            "Rentang Tanggal",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        df_filtered = df_original.copy()
        if selected_platform != 'All':
            df_filtered = df_filtered[df_filtered['Platform'] == selected_platform]
        if selected_sentiment != 'All':
            df_filtered = df_filtered[df_filtered['Sentiment'] == selected_sentiment]
        if selected_media_type != 'All':
            df_filtered = df_filtered[df_filtered['Media Type'] == selected_media_type]
        if selected_location != 'All':
            df_filtered = df_filtered[df_filtered['Location'] == selected_location]
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['Date'].dt.date >= start_date) & 
                (df_filtered['Date'].dt.date <= end_date)
            ]

# --- Area Dasbor Utama ---
if df_original is None:
    st.info("Harap unggah file CSV melalui sidebar untuk memulai visualisasi data.")
elif df_filtered.empty:
    st.warning("Tidak ada data yang cocok dengan filter yang Anda pilih. Coba sesuaikan filter Anda.")
else:
    # --- Ringkasan Aksi Utama ---
    st.subheader("🎯 Ringkasan Aksi Utama")
    if st.button("Buat Rekomendasi"):
        summary_text = generate_summary(df_filtered)
        if summary_text:
            st.markdown(summary_text, unsafe_allow_html=True)
        else:
            st.warning("Tidak dapat membuat ringkasan. Silakan periksa data Anda.")
    else:
        st.info("Klik tombol di atas untuk membuat ringkasan strategis berdasarkan filter saat ini.")

    st.markdown("---")
    st.subheader("📈 Visualisasi Data")

    col1, col2 = st.columns(2)

    plot_config = {
        'template': "plotly_dark",
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font_color': "#e5e7eb"
    }

    with col1:
        sentiment_counts = df_filtered['Sentiment'].value_counts()
        fig_sentiment = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index, title="Analisis Sentimen", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_sentiment.update_layout(**plot_config, legend_orientation="h")
        st.plotly_chart(fig_sentiment, use_container_width=True)

        platform_engagements = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False)
        fig_platform = px.bar(platform_engagements, x=platform_engagements.index, y=platform_engagements.values, title="Keterlibatan per Platform", labels={'x': 'Platform', 'y': 'Total Keterlibatan'})
        fig_platform.update_layout(**plot_config)
        st.plotly_chart(fig_platform, use_container_width=True)

    with col2:
        media_type_counts = df_filtered['Media Type'].value_counts()
        fig_media = px.pie(media_type_counts, values=media_type_counts.values, names=media_type_counts.index, title="Komposisi Tipe Media", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_media.update_layout(**plot_config, legend_orientation="h")
        st.plotly_chart(fig_media, use_container_width=True)

        top_locations = df_filtered['Location'].value_counts().nlargest(5)
        fig_locations = px.bar(top_locations, x=top_locations.index, y=top_locations.values, title="Top 5 Lokasi", labels={'x': 'Lokasi', 'y': 'Jumlah Postingan'})
        fig_locations.update_layout(**plot_config)
        st.plotly_chart(fig_locations, use_container_width=True)

    engagement_trend = df_filtered.groupby(df_filtered['Date'].dt.date)['Engagements'].sum()
    fig_trend = px.line(engagement_trend, x=engagement_trend.index, y=engagement_trend.values, title="Tren Keterlibatan dari Waktu ke Waktu", labels={'x': 'Tanggal', 'y': 'Total Keterlibatan'}, markers=True)
    fig_trend.update_layout(**plot_config)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # --- Footer ---
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #9ca3af;'>© 2024 Dasbor Analitik Modern. Diberdayakan oleh Gemini.</p>", unsafe_allow_html=True)

