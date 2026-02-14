"""
🏠 2RentMe Analytics Dashboard
Streamlit yordamida qurilgan professional analitik panel

✅ Performance: Query caching, connection pooling
✅ Design: Glassmorphism, gradient cards, micro-animations
"""

# Force reload
# Streamlit yordamida qurilgan analitik panel

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from database import execute_query, create_tables
from firebase_service import get_firebase_summary
import queries

# ======================== PAGE CONFIG ========================
st.set_page_config(
    page_title="2RentMe Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================== CUSTOM CSS — PROFESSIONAL ========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== GLOBAL ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #0a0a1a;
        color: #e2e8f0;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(10, 10, 26, 0.8);
        backdrop-filter: blur(20px);
    }

    /* ===== MAIN HEADER ===== */
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(255,255,255,0.08);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 60%);
        animation: headerGlow 8s ease-in-out infinite;
    }
    @keyframes headerGlow {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(-20px, 10px); }
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        background: linear-gradient(135deg, #fff 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.7;
        font-size: 0.95rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 1.5rem 1.2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
        border-radius: 16px 16px 0 0;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 2rem 0 1rem 0;
        padding: 0.8rem 1.2rem;
        border-left: 4px solid;
        border-image: linear-gradient(180deg, #6366f1, #8b5cf6) 1;
        background: rgba(99, 102, 241, 0.05);
        border-radius: 0 12px 12px 0;
        letter-spacing: -0.3px;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1145 50%, #302b63 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }

    /* Sidebar radio buttons */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
    }

    /* ===== DEMO BOX ===== */
    .demo-box {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(245, 158, 11, 0.1));
        border: 1px solid rgba(251, 191, 36, 0.3);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
        color: #fbbf24 !important;
    }
    .demo-box *, .demo-box span, .demo-box p {
        color: #fbbf24 !important;
    }

    /* ===== CHART CONTAINER ===== */
    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }

    /* ===== FIREBASE CARD ===== */
    .firebase-card {
        background: linear-gradient(135deg, #ff6a00, #ee0979);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 40px rgba(238, 9, 121, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* ===== INFO CARD ===== */
    .info-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 1.5rem;
        border-radius: 14px;
        transition: all 0.3s ease;
    }
    .info-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
    .info-card h4 {
        color: #e2e8f0;
        margin: 0 0 0.5rem 0;
    }
    .info-card p {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 0 0 0.8rem 0;
    }

    /* ===== REVENUE CARD ===== */
    .revenue-card {
        background: linear-gradient(135deg, #059669, #10b981);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .revenue-card h3 {
        margin: 0 0 1.2rem 0;
        font-weight: 700;
    }
    .revenue-card p {
        font-size: 1rem;
        margin: 0.6rem 0;
    }

    /* ===== STATUS BADGE ===== */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-active {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-console {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-inactive {
        background: rgba(107, 114, 128, 0.2);
        color: #9ca3af;
        border: 1px solid rgba(107, 114, 128, 0.3);
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 500;
        color: #94a3b8;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        background: rgba(99, 102, 241, 0.1);
    }

    /* ===== DATAFRAME ===== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.1);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 3px;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }

    /* ===== ANIMATION KEYFRAMES ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .metric-card, .chart-container, .info-card {
        animation: fadeInUp 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)


# ======================== PLOTLY THEME ========================
PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    xaxis=dict(showgrid=False, color="#64748b"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#64748b"),
    margin=dict(l=0, r=0, t=10, b=0),
    height=350,
    legend=dict(
        font=dict(color="#94a3b8"),
        bgcolor="rgba(0,0,0,0)",
    ),
)

# ======================== HELPER FUNCTIONS ========================

@st.cache_data(ttl=300, show_spinner=False)
def safe_query(query):
    """Xavfsiz so'rov — xatolik bo'lsa bo'sh DataFrame qaytaradi (5 daq cached)"""
    try:
        return execute_query(query)
    except Exception as e:
        st.error(f"❌ So'rov xatosi: {e}")
        return pd.DataFrame()


def get_scalar(query, default=0):
    """Bitta qiymat qaytaruvchi so'rov"""
    df = safe_query(query)
    if df.empty:
        return default
    return df.iloc[0, 0] or default


def clear_all_cache():
    """Barcha keshni tozalash"""
    safe_query.clear()
    st.cache_data.clear()


def metric_card(icon, value, label):
    """Professional metrika kartochkasi"""
    if isinstance(value, str):
        formatted_value = value
    else:
        try:
            formatted_value = f"{value:,}"
        except (ValueError, TypeError):
            formatted_value = str(value)

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(text):
    """Bo'lim sarlavhasi"""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def apply_plotly_theme(fig, height=350):
    """Plotly grafikga dark theme ni qo'llash"""
    layout = {**PLOTLY_LAYOUT, "height": height}
    fig.update_layout(**layout)
    return fig


# ======================== COLOR PALETTES ========================
COLORS = {
    "primary": ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8"],
    "status": {"pending": "#f59e0b", "approved": "#10b981", "rejected": "#ef4444", "canceled": "#6b7280"},
    "platform": {"android": "#3ddc84", "ios": "#007aff"},
    "gradient": ["#6366f1", "#8b5cf6", "#ec4899", "#f43f5e", "#06b6d4", "#10b981"],
    "chart": ["#6366f1", "#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#a78bfa"],
}

ROLE_LABELS = {
    "ordinary": "Oddiy",
    "tenant": "Ijarachi",
    "homeowner": "Uy egasi",
    "realtor": "Rieltor",
    "admin": "Admin",
    "client": "Mijoz",
}

STATUS_LABELS = {
    "pending": "Kutilmoqda",
    "approved": "Tasdiqlangan",
    "rejected": "Rad etilgan",
}


# ======================== SIDEBAR ========================

with st.sidebar:
    st.markdown("## 🏠 2RentMe")

    st.markdown("""
    <div class="demo-box">
        <span style="font-weight: 700; font-size: 0.9rem; display: block; margin-bottom: 4px;">⚠️ DEMO REJIM</span>
        <span style="font-size: 0.8rem;">Ma'lumotlar sun'iy (demo)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "📊 Bo'lim tanlang",
        [
            "🏠 Umumiy ko'rsatkichlar",
            "👤 Foydalanuvchilar",
            "📱 Qurilmalar",
            "🏘️ Mulklar va E'lonlar",
            "📋 Arizalar va Shartnomalar",
            "🔔 Xabarlar",
            "🔥 Firebase",
            "📊 App Analytics",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 🛠️ Admin Panel")

    if st.button("🔄 Bazani yangilash"):
        with st.spinner("Jadvallar yaratilmoqda..."):
            try:
                create_tables()
                st.success("✅ Jadvallar yaratildi!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Xatolik: {e}")

    if st.button("🎲 Demo ma'lumot qo'shish"):
        with st.spinner("Demo ma'lumotlar qo'shilmoqda..."):
            try:
                from database import seed_demo_data
                seed_demo_data()
                st.success("✅ Demo ma'lumotlar qo'shildi!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Xatolik: {e}")

    if st.button("🗑️ Keshni tozalash"):
        clear_all_cache()
        st.success("✅ Kesh tozalandi!")
        st.rerun()

    st.markdown("---")
    st.markdown(f"📅 **{datetime.now().strftime('%Y-%m-%d %H:%M')}**")


# ======================== MAIN HEADER ========================

st.markdown("""
<div class="main-header">
    <h1>🏠 2RentMe Analytics Dashboard</h1>
    <p>Ijara platformasi analitik paneli — barcha ko'rsatkichlar bir joyda</p>
</div>
""", unsafe_allow_html=True)


# ===============================================================
# ==================== SAHIFALAR ================================
# ===============================================================


# ==================== 1. UMUMIY ====================
if page == "🏠 Umumiy ko'rsatkichlar":

    # Top metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        metric_card("👥", get_scalar(queries.TOTAL_USERS), "Jami foydalanuvchilar")
    with col2:
        metric_card("✅", get_scalar(queries.ACTIVE_USERS), "Faol foydalanuvchilar")
    with col3:
        metric_card("📱", get_scalar(queries.ONLINE_DEVICES), "Onlayn qurilmalar")
    with col4:
        metric_card("🏠", get_scalar(queries.TOTAL_PROPERTIES), "Jami mulklar")
    with col5:
        metric_card("📢", get_scalar(queries.TOTAL_ANNOUNCEMENTS), "Jami e'lonlar")
    with col6:
        metric_card("📋", get_scalar(queries.TOTAL_REQUESTS), "Jami arizalar")

    st.markdown("")

    # Second row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("📝", get_scalar(queries.TOTAL_CONTRACTS), "Shartnomalar")
    with col2:
        metric_card("⏳", get_scalar(queries.PENDING_REQUESTS), "Kutilayotgan arizalar")
    with col3:
        metric_card("🔔", get_scalar(queries.NOTIFICATIONS_SENT), "Yuborilgan xabarlar")
    with col4:
        metric_card("🆕", get_scalar(queries.NEW_USERS_THIS_MONTH), "Yangi userlar (oy)")

    st.markdown("")

    # Charts row
    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📈 Ro'yxatdan o'tish trendi (30 kun)")
        df = safe_query(queries.USERS_REGISTRATION_TREND)
        if not df.empty:
            fig = px.area(df, x="date", y="count",
                         color_discrete_sequence=["#6366f1"],
                         labels={"date": "Sana", "count": "Yangi userlar"})
            apply_plotly_theme(fig, 300)
            fig.update_traces(fill='tozeroy', fillcolor='rgba(99,102,241,0.15)',
                            line=dict(width=2.5))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ma'lumot topilmadi")

    with col_right:
        section_header("📊 Foydalanuvchilar rol bo'yicha")
        df = safe_query(queries.USERS_BY_ROLE)
        if not df.empty:
            df["role_label"] = df["role"].map(ROLE_LABELS).fillna(df["role"])
            fig = px.pie(df, values="count", names="role_label",
                        color_discrete_sequence=COLORS["chart"],
                        hole=0.5)
            apply_plotly_theme(fig, 300)
            fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15))
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ma'lumot topilmadi")

    # Bottom charts
    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📱 Qurilma turlari")
        df = safe_query(queries.DEVICES_BY_TYPE)
        if not df.empty:
            fig = px.bar(df, x="device_type", y="count",
                        color="device_type",
                        color_discrete_map=COLORS["platform"],
                        labels={"device_type": "Platforma", "count": "Soni"})
            apply_plotly_theme(fig, 300)
            fig.update_layout(showlegend=False)
            fig.update_traces(marker=dict(cornerradius=8))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ma'lumot topilmadi")

    with col_right:
        section_header("📋 Arizalar holati")
        df = safe_query(queries.REQUESTS_BY_STATUS)
        if not df.empty:
            df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
            fig = px.bar(df, x="status_label", y="count",
                        color="status",
                        color_discrete_map=COLORS["status"],
                        labels={"status_label": "Holat", "count": "Soni"})
            apply_plotly_theme(fig, 300)
            fig.update_layout(showlegend=False)
            fig.update_traces(marker=dict(cornerradius=8))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ma'lumot topilmadi")


# ==================== 2. FOYDALANUVCHILAR ====================
elif page == "👤 Foydalanuvchilar":

    section_header("👤 Foydalanuvchilar analitikasi")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("👥", get_scalar(queries.TOTAL_USERS), "Jami")
    with col2:
        metric_card("✅", get_scalar(queries.ACTIVE_USERS), "Faol")
    with col3:
        metric_card("🆕", get_scalar(queries.NEW_USERS_TODAY), "Bugungi yangi")
    with col4:
        metric_card("📅", get_scalar(queries.NEW_USERS_THIS_WEEK), "Haftalik yangi")

    st.markdown("")

    # Charts
    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📈 Kunlik ro'yxatdan o'tish (30 kun)")
        df = safe_query(queries.USERS_REGISTRATION_TREND)
        if not df.empty:
            fig = px.bar(df, x="date", y="count",
                        color_discrete_sequence=["#6366f1"],
                        labels={"date": "Sana", "count": "Yangi userlar"})
            apply_plotly_theme(fig)
            fig.update_traces(marker=dict(cornerradius=6))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📊 Oylik trend (12 oy)")
        df = safe_query(queries.USERS_REGISTRATION_MONTHLY)
        if not df.empty:
            df["month_label"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m")
            fig = px.line(df, x="month_label", y="count",
                         markers=True,
                         color_discrete_sequence=["#8b5cf6"],
                         labels={"month_label": "Oy", "count": "Yangi userlar"})
            apply_plotly_theme(fig)
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("🧑‍🤝‍🧑 Rol bo'yicha taqsimot")
        df = safe_query(queries.USERS_BY_ROLE)
        if not df.empty:
            df["role_label"] = df["role"].map(ROLE_LABELS).fillna(df["role"])
            fig = px.pie(df, values="count", names="role_label",
                        color_discrete_sequence=COLORS["chart"], hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("🪪 Identifikatsiya holati")
        df = safe_query(queries.IDENTIFIED_USERS)
        if not df.empty:
            fig = px.pie(df, values="count", names="status",
                        color_discrete_sequence=["#10b981", "#ef4444"], hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    section_header("👫 Jins bo'yicha taqsimot")
    df = safe_query(queries.USERS_GENDER_DISTRIBUTION)
    if not df.empty:
        fig = px.bar(df, x="gender", y="count",
                    color="gender", color_discrete_sequence=COLORS["chart"],
                    labels={"gender": "Jins", "count": "Soni"})
        apply_plotly_theme(fig, 300)
        fig.update_layout(showlegend=False)
        fig.update_traces(marker=dict(cornerradius=8))
        st.plotly_chart(fig, use_container_width=True)


# ==================== 3. QURILMALAR ====================
elif page == "📱 Qurilmalar":

    section_header("📱 Qurilmalar analitikasi")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("📱", get_scalar(queries.TOTAL_DEVICES), "Jami qurilmalar")
    with col2:
        metric_card("🟢", get_scalar(queries.ONLINE_DEVICES), "Onlayn")
    with col3:
        offline = get_scalar(queries.TOTAL_DEVICES) - get_scalar(queries.ONLINE_DEVICES)
        metric_card("🔴", offline, "Oflayn")
    with col4:
        metric_card("🕐", get_scalar(queries.RECENTLY_ACTIVE_DEVICES), "24 soatda faol")

    st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📊 Platforma taqsimoti")
        df = safe_query(queries.DEVICES_BY_TYPE)
        if not df.empty:
            fig = px.pie(df, values="count", names="device_type",
                        color_discrete_map=COLORS["platform"],
                        hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value+label',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("🟢 Onlayn / Oflayn")
        df = safe_query(queries.DEVICES_BY_STATUS)
        if not df.empty:
            color_map = {"online": "#10b981", "offline": "#6b7280"}
            fig = px.pie(df, values="count", names="status",
                        color="status", color_discrete_map=color_map,
                        hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value+label',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    section_header("📱 Eng ko'p ishlatiladigan qurilmalar")
    df = safe_query(queries.POPULAR_DEVICE_NAMES)
    if not df.empty:
        fig = px.bar(df, x="count", y="name", orientation='h',
                    color="count", color_continuous_scale=["#6366f1", "#a78bfa", "#c4b5fd"],
                    labels={"name": "Qurilma", "count": "Soni"})
        apply_plotly_theme(fig, 400)
        fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False,
                         coloraxis_showscale=False)
        fig.update_traces(marker=dict(cornerradius=6))
        st.plotly_chart(fig, use_container_width=True)


# ==================== 4. MULKLAR VA E'LONLAR ====================
elif page == "🏘️ Mulklar va E'lonlar":

    section_header("🏘️ Mulklar va E'lonlar")

    # Cache views stats for this page
    views_df = safe_query(queries.ANNOUNCEMENTS_VIEWS_STATS)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("🏠", get_scalar(queries.TOTAL_PROPERTIES), "Jami mulklar")
    with col2:
        metric_card("📢", get_scalar(queries.TOTAL_ANNOUNCEMENTS), "Jami e'lonlar")
    with col3:
        total_views = int(views_df.iloc[0]["total_views"]) if not views_df.empty and views_df.iloc[0]["total_views"] else 0
        metric_card("👁️", total_views, "Jami ko'rishlar")
    with col4:
        phone_views = int(views_df.iloc[0]["total_phone_views"]) if not views_df.empty and views_df.iloc[0]["total_phone_views"] else 0
        metric_card("📞", phone_views, "Telefon ko'rishlar")

    st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("🏠 Mulk turi bo'yicha")
        df = safe_query(queries.PROPERTIES_BY_TYPE)
        if not df.empty:
            type_labels = {"apartment": "Kvartira", "house": "Uy", "studio": "Studiya", "villa": "Villa"}
            df["type_label"] = df["type"].map(type_labels).fillna(df["type"])
            fig = px.pie(df, values="count", names="type_label",
                        color_discrete_sequence=COLORS["chart"], hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📋 Moderatsiya holati")
        df = safe_query(queries.ANNOUNCEMENTS_BY_MODERATION)
        if not df.empty:
            df["status_label"] = df["moderated_status"].map(STATUS_LABELS).fillna(df["moderated_status"])
            fig = px.pie(df, values="count", names="status_label",
                        color="moderated_status",
                        color_discrete_map=COLORS["status"],
                        hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    section_header("🔝 Eng ko'p ko'rilgan e'lonlar (Top 10)")
    df = safe_query(queries.TOP_VIEWED_ANNOUNCEMENTS)
    if not df.empty:
        display_df = df[["id", "views", "phone_views", "price", "currency", "created_at"]].copy()
        display_df.columns = ["ID", "Ko'rishlar", "Tel. ko'rishlar", "Narx", "Valyuta", "Yaratilgan"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("🏗️ Mulk holati")
        df = safe_query(queries.RENTABLE_VS_NOT)
        if not df.empty:
            fig = px.pie(df, values="count", names="status",
                        color_discrete_sequence=["#10b981", "#f59e0b"], hole=0.5)
            apply_plotly_theme(fig, 300)
            fig.update_traces(textinfo='percent+value+label',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📈 E'lonlar trendi (30 kun)")
        df = safe_query(queries.ANNOUNCEMENTS_CREATED_TREND)
        if not df.empty:
            fig = px.area(df, x="date", y="count",
                         color_discrete_sequence=["#f59e0b"],
                         labels={"date": "Sana", "count": "Yangi e'lonlar"})
            apply_plotly_theme(fig, 300)
            fig.update_traces(fill='tozeroy', fillcolor='rgba(245,158,11,0.15)',
                            line=dict(width=2.5))
            st.plotly_chart(fig, use_container_width=True)


# ==================== 5. ARIZALAR VA SHARTNOMALAR ====================
elif page == "📋 Arizalar va Shartnomalar":

    section_header("📋 Arizalar va Shartnomalar")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("📋", get_scalar(queries.TOTAL_REQUESTS), "Jami arizalar")
    with col2:
        metric_card("⏳", get_scalar(queries.PENDING_REQUESTS), "Kutilayotgan")
    with col3:
        metric_card("📝", get_scalar(queries.TOTAL_CONTRACTS), "Jami shartnomalar")
    with col4:
        metric_card("✅", get_scalar(queries.ACTIVE_CONTRACTS), "Faol shartnomalar")

    st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📊 Arizalar holati")
        df = safe_query(queries.REQUESTS_BY_STATUS)
        if not df.empty:
            df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
            fig = px.pie(df, values="count", names="status_label",
                        color="status", color_discrete_map=COLORS["status"],
                        hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📝 Shartnomalar holati")
        df = safe_query(queries.CONTRACTS_BY_STATUS)
        if not df.empty:
            df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
            fig = px.pie(df, values="count", names="status_label",
                        color="status", color_discrete_map=COLORS["status"],
                        hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value',
                            textfont=dict(color="white", size=11))
            st.plotly_chart(fig, use_container_width=True)

    section_header("📈 Arizalar trendi (30 kun)")
    df = safe_query(queries.REQUESTS_TREND)
    if not df.empty:
        fig = px.bar(df, x="date", y="count",
                    color_discrete_sequence=["#6366f1"],
                    labels={"date": "Sana", "count": "Arizalar"})
        apply_plotly_theme(fig, 300)
        fig.update_traces(marker=dict(cornerradius=6))
        st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📋 Shartnoma turi")
        df = safe_query(queries.CONTRACTS_BY_TYPE)
        if not df.empty:
            type_labels = {"fixed": "Muddatli", "monthly": "Oylik", "month_to_month": "Oyma-oy", "yearly": "Yillik"}
            df["type_label"] = df["contract_type"].map(type_labels).fillna(df["contract_type"])
            fig = px.bar(df, x="type_label", y="count",
                        color="type_label", color_discrete_sequence=COLORS["chart"],
                        labels={"type_label": "Turi", "count": "Soni"})
            apply_plotly_theme(fig, 300)
            fig.update_layout(showlegend=False)
            fig.update_traces(marker=dict(cornerradius=8))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("💰 Shartnomalar daromadi")
        df = safe_query(queries.CONTRACTS_REVENUE)
        if not df.empty and df.iloc[0]["total_revenue"]:
            rev = df.iloc[0]
            st.markdown(f"""
            <div class="revenue-card">
                <h3>💰 Daromad statistikasi</h3>
                <p><b>Umumiy daromad:</b> {rev['total_revenue']:,.0f} so'm</p>
                <p><b>O'rtacha narx:</b> {rev['avg_price']:,.0f} so'm</p>
                <p><b>Shartnomalar soni:</b> {rev['count']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Tasdiqlangan shartnomalar topilmadi")


# ==================== 6. XABARLAR ====================
elif page == "🔔 Xabarlar":

    section_header("🔔 Xabarlar (Notifications)")

    # Query once, use multiple times
    read_df = safe_query(queries.NOTIFICATION_READ_RATE)
    read_count = int(read_df.iloc[0]["read_count"]) if not read_df.empty and read_df.iloc[0]["read_count"] else 0
    read_rate = float(read_df.iloc[0]["read_rate"]) if not read_df.empty and read_df.iloc[0]["read_rate"] else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("🔔", get_scalar(queries.TOTAL_NOTIFICATIONS), "Jami xabarlar")
    with col2:
        metric_card("✈️", get_scalar(queries.NOTIFICATIONS_SENT), "Yuborilgan")
    with col3:
        metric_card("📖", read_count, "O'qilgan")
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{read_rate}%</div>
            <div class="metric-label">O'QILISH DARAJASI</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    section_header("📈 Xabarlar trendi (30 kun)")
    df = safe_query(queries.NOTIFICATIONS_TREND)
    if not df.empty:
        fig = px.bar(df, x="date", y="count",
                    color_discrete_sequence=["#f59e0b"],
                    labels={"date": "Sana", "count": "Yuborilgan xabarlar"})
        apply_plotly_theme(fig)
        fig.update_traces(marker=dict(cornerradius=6))
        st.plotly_chart(fig, use_container_width=True)

    # O'qilish gauge
    section_header("🎯 O'qilish darajasi")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=read_rate,
        title={"text": "Notification o'qilish %", "font": {"color": "#e2e8f0", "size": 16}},
        number={"font": {"color": "#e2e8f0", "size": 40}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748b", "tickfont": {"color": "#64748b"}},
            "bar": {"color": "#10b981"},
            "bgcolor": "rgba(255,255,255,0.03)",
            "bordercolor": "rgba(255,255,255,0.1)",
            "steps": [
                {"range": [0, 30], "color": "rgba(239, 68, 68, 0.15)"},
                {"range": [30, 70], "color": "rgba(245, 158, 11, 0.15)"},
                {"range": [70, 100], "color": "rgba(16, 185, 129, 0.15)"},
            ],
            "threshold": {"line": {"color": "#ef4444", "width": 2}, "value": 50},
        },
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ==================== 7. FIREBASE ====================
elif page == "🔥 Firebase":

    section_header("🔥 Firebase Integration")

    firebase_info = get_firebase_summary()

    # Connection card
    st.markdown(f"""
    <div class="firebase-card">
        <h3 style="margin: 0 0 0.8rem 0; font-weight: 700;">🔥 Firebase Project</h3>
        <p style="margin: 0.3rem 0; font-size: 1rem;"><b>Project ID:</b> {firebase_info['project_id']}</p>
        <p style="margin: 0.3rem 0; font-size: 1rem;"><b>Holat:</b> {firebase_info['connection_status']}</p>
    </div>
    """, unsafe_allow_html=True)

    if firebase_info.get("firebase_console_url"):
        st.markdown(f"🔗 [Firebase Console ochish]({firebase_info['firebase_console_url']})")

    st.info(f"ℹ️ {firebase_info['note']}")

    # Firebase xizmatlari haqida ma'lumot
    section_header("📚 Firebase xizmatlari")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>📩 Cloud Messaging (FCM)</h4>
            <p>Push notification yuborish. RentMe da allaqachon ishlatilmoqda — arizalar, shartnomalar, xabarlar uchun.</p>
            <span class="status-badge badge-active">Faol</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>📊 Analytics (GA4)</h4>
            <p>Foydalanuvchi xatti-harakatlari, sessiyalar, ekranlar, eventlar tracking. Firebase Console orqali ko'rish mumkin.</p>
            <span class="status-badge badge-console">Console orqali</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>🔐 Authentication</h4>
            <p>Foydalanuvchi autentifikatsiyasi. RentMe da OTP orqali JWT ishlatilmoqda (Firebase Auth emas).</p>
            <span class="status-badge badge-inactive">Ishlatilmayapti</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # FCM statistika (DB dan)
    section_header("📩 Push Notification statistikasi (DB)")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("📨", get_scalar(queries.NOTIFICATIONS_SENT), "Yuborilgan FCM")
    with col2:
        read_df = safe_query(queries.NOTIFICATION_READ_RATE)
        total_notif = int(read_df.iloc[0]["total"]) if not read_df.empty and read_df.iloc[0]["total"] else 0
        metric_card("📬", total_notif, "Yetkazilgan")
    with col3:
        metric_card("📱", get_scalar(queries.TOTAL_DEVICES), "FCM tokenli qurilmalar")

    st.markdown("")

    # Firebase prezentatsiya uchun
    section_header("📋 Firebase funktsionalliklari")

    st.markdown("""
    | # | Xizmat | Tavsif | RentMe da holati |
    |---|--------|--------| -----------------|
    | 1 | **Cloud Messaging (FCM)** | Push notification yuborish | ✅ Faol ishlatilmoqda |
    | 2 | **Analytics (GA4)** | User behavior tracking | 📊 Firebase Console |
    | 3 | **Crashlytics** | Ilova crash reportlari | ⚙️ Sozlash mumkin |
    | 4 | **Remote Config** | Ilovani masofaviy sozlash | ⚙️ Sozlash mumkin |
    | 5 | **Cloud Firestore** | NoSQL database | ❌ PostgreSQL ishlatilmoqda |
    | 6 | **Authentication** | Login/Register | ❌ OTP+JWT ishlatilmoqda |
    | 7 | **Cloud Storage** | Fayl saqlash | ❌ Media folder ishlatilmoqda |
    | 8 | **Cloud Functions** | Serverless funksiyalar | ⚙️ Sozlash mumkin |
    | 9 | **Performance Monitoring** | Ilova ishlash tezligi | ⚙️ Sozlash mumkin |
    | 10 | **A/B Testing** | Eksperiment o'tkazish | ⚙️ Sozlash mumkin |
    """)


# ==================== 8. APP ANALYTICS (GA4) ====================
elif page == "📊 App Analytics":
    from analytics_service import get_ga4_data, get_top_pages, get_demo_analytics_data, get_demo_top_pages

    section_header("📊 Mobil Ilova Analitikasi (Google Analytics 4)")

    # 1. Konfiguratsiya tekshiruvi
    GA_PROPERTY_ID = None
    if "firebase" in st.secrets and "property_id" in st.secrets["firebase"]:
        GA_PROPERTY_ID = st.secrets["firebase"]["property_id"]

    # Ma'lumot olish (Real yoki Demo)
    is_demo = False
    if GA_PROPERTY_ID:
        df_trend = get_ga4_data(GA_PROPERTY_ID)
        df_pages = get_top_pages(GA_PROPERTY_ID)
        if df_trend is None:
            st.warning("⚠️ GA4 API ga ulanib bo'lmadi. Demo rejimga o'tilmoqda.")
            is_demo = True
            df_trend = get_demo_analytics_data()
            df_pages = get_demo_top_pages()
    else:
        st.info("ℹ️ GA4 Property ID topilmadi. Demo ma'lumotlar ko'rsatilmoqda.")
        is_demo = True
        df_trend = get_demo_analytics_data()
        df_pages = get_demo_top_pages()

    if is_demo:
        st.markdown("""
        <div class="demo-box">
            <b>⚠️ DEMO MODE</b>: Bu ma'lumotlar sun'iy generatsiya qilingan.
            Real ma'lumotlarni ulash uchun secrets ga <code>property_id</code> qo'shing.
        </div>
        """, unsafe_allow_html=True)

    # 2. Asosiy ko'rsatkichlar (KPIs)
    if not df_trend.empty:
        latest = df_trend.iloc[-1]

        # O'rtacha sessiya vaqti (daqiqada)
        avg_session_min = latest["duration"] / latest["users"] / 60 if latest["users"] > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("👥", int(latest["users"]), "Faol Foydalanuvchilar (Bugun)")
        with col2:
            metric_card("⏱️", f"{avg_session_min:.1f} daq", "O'rtacha foydalanish vaqti")
        with col3:
            metric_card("👀", int(latest["views"]), "Sahifa ko'rishlar soni")

        st.markdown("---")

        # 3. Grafiklar
        col_left, col_right = st.columns(2)

        with col_left:
            section_header("📈 Foydalanish vaqti trendi (30 kun)")
            df_trend["avg_duration_min"] = df_trend["duration"] / df_trend["users"] / 60

            fig = px.area(df_trend, x="date", y="avg_duration_min",
                         labels={"date": "Sana", "avg_duration_min": "Daqiqa"},
                         color_discrete_sequence=["#10b981"])
            apply_plotly_theme(fig)
            fig.update_traces(fill='tozeroy', fillcolor='rgba(16,185,129,0.15)',
                            line=dict(width=2.5))
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            section_header("📱 Eng ko'p kirilgan sahifalar")
            if not df_pages.empty:
                df_pages.columns = ["Sahifa nomi", "Ko'rishlar"]
                st.dataframe(
                    df_pages,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Ko'rishlar": st.column_config.ProgressColumn(
                            "Ko'rishlar",
                            format="%d",
                            min_value=0,
                            max_value=int(df_pages["Ko'rishlar"].max()),
                        ),
                    }
                )
            else:
                st.info("Sahifa ma'lumotlari mavjud emas")
