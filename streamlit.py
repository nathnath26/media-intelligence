import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Dasbor Analitik Kampanye",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styling ---
# Inject custom CSS for a modern dark theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-image: linear-gradient(to br, #1a202c, #2d3748);
    }

    /* Card-like containers */
    .st-emotion-cache-1r4qj8v, .st-emotion-cache-1v0mbdj {
        background-color: rgba(45, 55, 72, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid #4A5568;
        border-radius: 1rem;
        padding: 1.5rem;
    }

    /* Headers and titles */
    h1, h2, h3 {
        color: #E2E8F0;
    }

    /* Input widgets */
    .stSelectbox > div > div > div {
        background-color: #2D3748;
    }

    /* Plotly chart background */
    .stPlotlyChart {
        border-radius: 0.5rem;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --- Functions ---

@st.cache_data
def clean_data(uploaded_file):
    """
    Cleans and preprocesses the uploaded CSV data.
    Caches the result to avoid reprocessing on every interaction.
    """
    if uploaded_file is None:
        return None

    try:
        # To read file from upload
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(stringio)

        # Data Cleaning
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0).astype(int)

        # Drop rows where Date is NaT after coercion
        df.dropna(subset=['Date'], inplace=True)
        return df

    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
        return None

def generate_summary(df):
    """Generates a key action summary based on the filtered data."""
    if df.empty:
        return "Tidak ada data untuk diringkas. Sesuaikan filter Anda."

    # 1. Top platform by engagement
    top_platform = df.groupby('Platform')['Engagements'].sum().idxmax()

    # 2. Dominant sentiment
    dominant_sentiment = df['Sentiment'].mode()[0] if not df['Sentiment'].empty else 'Tidak Diketahui'

    # 3. Most used media type
    top_media_type = df['Media Type'].mode()[0] if not df['Media Type'].empty else 'Tidak Diketahui'

    # 4. Top location by post count
    top_location = df['Location'].mode()[0] if not df['Location'].empty else 'Tidak Diketahui'

    summary = f"""
    <ul>
        <li style="margin-bottom: 8px;"><strong>Platform Utama:</strong> Fokuskan sumber daya di <strong>{top_platform}</strong>, karena platform ini menghasilkan keterlibatan tertinggi.</li>
        <li style="margin-bottom: 8px;"><strong>Konten Paling Efektif:</strong> Konten berjenis <strong>{top_media_type}</strong> paling sering digunakan. Pertimbangkan untuk meningkatkan produksi konten ini.</li>
        <li style="margin-bottom: 8px;"><strong>Persepsi Audiens:</strong> Sentimen yang dominan adalah <strong>{dominant_sentiment}</strong>. Manfaatkan suasana positif ini, atau jika negatif, selidiki penyebabnya.</li>
        <li style="margin-bottom: 8px;"><strong>Target Geografis:</strong> <strong>{top_location}</strong> adalah lokasi dengan aktivitas tertinggi. Pertimbangkan untuk membuat kampanye yang dilokalkan untuk area ini.</li>
    </ul>
    """
    return summary

# --- Main App ---

st.title("📊 Dasbor Analitik Kampanye")
st.markdown("<p style='color: #A0AEC0;'>Unggah data kampanye Anda untuk visualisasi dan wawasan strategis.</p>", unsafe_allow_html=True)


# --- Sidebar for Filters and Upload ---
with st.sidebar:
    st.header("✨ Kontrol & Filter")
    
    uploaded_file = st.file_uploader(
        "Unggah Data Kampanye (CSV)",
        type=['csv'],
        help="Pastikan file CSV Anda memiliki kolom: 'Date', 'Platform', 'Engagements', 'Sentiment', 'Media Type', 'Location'"
    )

    df = clean_data(uploaded_file)
    
    if df is not None:
        st.success(f"Data berhasil dimuat! {len(df)} catatan ditemukan.")
        
        st.markdown("---")
        st.header("⚙️ Filter Data")

        # Get unique values for filters
        platforms = ['All'] + sorted(df['Platform'].unique().tolist())
        sentiments = ['All'] + sorted(df['Sentiment'].unique().tolist())
        media_types = ['All'] + sorted(df['Media Type'].unique().tolist())
        locations = ['All'] + sorted(df['Location'].unique().tolist())
        
        # Date range
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()

        # Filter widgets
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

        # Apply filters
        df_filtered = df.copy()
        if selected_platform != 'All':
            df_filtered = df_filtered[df_filtered['Platform'] == selected_platform]
        if selected_sentiment != 'All':
            df_filtered = df_filtered[df_filtered['Sentiment'] == selected_sentiment]
        if selected_media_type != 'All':
            df_filtered = df_filtered[df_filtered['Media Type'] == selected_media_type]
        if selected_location != 'All':
            df_filtered = df_filtered[df_filtered['Location'] == selected_location]
        
        # Date range filtering
        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['Date'].dt.date >= start_date) & 
                (df_filtered['Date'].dt.date <= end_date)
            ]


# --- Main Dashboard Area ---
if df is None:
    st.info("Harap unggah file CSV melalui sidebar untuk memulai visualisasi data.")
else:
    # --- Key Action Summary ---
    st.subheader("🎯 Ringkasan Aksi Utama")
    summary_text = generate_summary(df_filtered)
    st.markdown(summary_text, unsafe_allow_html=True)
    st.markdown("---")


    # --- Visualizations ---
    st.subheader("📈 Visualisasi Data")

    col1, col2 = st.columns(2)

    with col1:
        # Sentiment Breakdown
        sentiment_counts = df_filtered['Sentiment'].value_counts()
        fig_sentiment = px.pie(
            sentiment_counts,
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Analisis Sentimen",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_sentiment.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend_orientation="h",
            font_color="#E2E8F0"
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)

        # Platform Engagements
        platform_engagements = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False)
        fig_platform = px.bar(
            platform_engagements,
            x=platform_engagements.index,
            y=platform_engagements.values,
            title="Keterlibatan per Platform",
            labels={'x': 'Platform', 'y': 'Total Keterlibatan'}
        )
        fig_platform.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#E2E8F0"
        )
        st.plotly_chart(fig_platform, use_container_width=True)


    with col2:
        # Media Type Mix
        media_type_counts = df_filtered['Media Type'].value_counts()
        fig_media = px.pie(
            media_type_counts,
            values=media_type_counts.values,
            names=media_type_counts.index,
            title="Komposisi Tipe Media",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_media.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend_orientation="h",
            font_color="#E2E8F0"
        )
        st.plotly_chart(fig_media, use_container_width=True)


        # Top 5 Locations
        top_locations = df_filtered['Location'].value_counts().nlargest(5)
        fig_locations = px.bar(
            top_locations,
            x=top_locations.index,
            y=top_locations.values,
            title="Top 5 Lokasi",
            labels={'x': 'Lokasi', 'y': 'Jumlah Postingan'}
        )
        fig_locations.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#E2E8F0"
        )
        st.plotly_chart(fig_locations, use_container_width=True)

    # Engagement Trend over Time
    engagement_trend = df_filtered.groupby(df_filtered['Date'].dt.date)['Engagements'].sum()
    fig_trend = px.line(
        engagement_trend,
        x=engagement_trend.index,
        y=engagement_trend.values,
        title="Tren Keterlibatan dari Waktu ke Waktu",
        labels={'x': 'Tanggal', 'y': 'Total Keterlibatan'},
        markers=True
    )
    fig_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#E2E8F0"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # --- Footer ---
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #A0AEC0;'>© 2024 Dasbor Analitik Modern. Diberdayakan oleh Gemini.</p>", unsafe_allow_html=True)
