"""
🏠 2RentMe Analytics Dashboard
Streamlit yordamida qurilgan analitik panel
"""

# Force reload
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

# ======================== CUSTOM CSS ========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.8;
        font-size: 0.95rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9ff);
        border: 1px solid #e8ecf4;
        padding: 1.4rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }

    /* Section header */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e8ecf4;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #302b63);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #302b63);
    }
    /* Default sidebar text color */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: white;
    }
    
    /* Demo box override */
    .demo-box {
        background-color: #fffbeb;
        border: 1px solid #fbbf24;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        color: #000000 !important;
    }
    .demo-box *, .demo-box span, .demo-box p {
        color: #000000 !important;
    }

    .firebase-card {
        background: linear-gradient(135deg, #ff9a56, #ff6a00);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ======================== HELPER FUNCTIONS ========================

def safe_query(query):
    """Xavfsiz so'rov — xatolik bo'lsa bo'sh DataFrame qaytaradi"""
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


def metric_card(icon, value, label):
    """Chiroyli metrika kartochkasi"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(text):
    """Bo'lim sarlavhasi"""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


# ======================== COLOR PALETTES ========================
COLORS = {
    "primary": ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd"],
    "status": {"pending": "#f59e0b", "approved": "#10b981", "rejected": "#ef4444", "canceled": "#6b7280"},
    "platform": {"android": "#3ddc84", "ios": "#007aff"},
    "gradient": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe"],
    "chart": px.colors.qualitative.Set2,
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
        ],
        index=0,
    )

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
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            )
            fig.update_traces(fill='tozeroy', fillcolor='rgba(99,102,241,0.1)')
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
                        hole=0.45)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
                showlegend=True,
                legend=dict(orientation="h", y=-0.1),
            )
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ma'lumot topilmadi")

    # Bottom charts
    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📱 Qurilma turlari")
        df = safe_query(queries.DEVICES_BY_TYPE)
        if not df.empty:
            colors = [COLORS["platform"].get(t, "#999") for t in df["device_type"]]
            fig = px.bar(df, x="device_type", y="count",
                        color="device_type",
                        color_discrete_map=COLORS["platform"],
                        labels={"device_type": "Platforma", "count": "Soni"})
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ma'lumot topilmadi")

    with col_right:
        section_header("📋 Arizalar holati")
        df = safe_query(queries.REQUESTS_BY_STATUS)
        if not df.empty:
            df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
            colors = [COLORS["status"].get(s, "#999") for s in df["status"]]
            fig = px.bar(df, x="status_label", y="count",
                        color="status",
                        color_discrete_map=COLORS["status"],
                        labels={"status_label": "Holat", "count": "Soni"})
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            )
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
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            )
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
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            )
            st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("🧑‍🤝‍🧑 Rol bo'yicha taqsimot")
        df = safe_query(queries.USERS_BY_ROLE)
        if not df.empty:
            df["role_label"] = df["role"].map(ROLE_LABELS).fillna(df["role"])
            fig = px.pie(df, values="count", names="role_label",
                        color_discrete_sequence=COLORS["chart"], hole=0.4)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("🪪 Identifikatsiya holati")
        df = safe_query(queries.IDENTIFIED_USERS)
        if not df.empty:
            fig = px.pie(df, values="count", names="status",
                        color_discrete_sequence=["#10b981", "#ef4444"], hole=0.4)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)

    section_header("👫 Jins bo'yicha taqsimot")
    df = safe_query(queries.USERS_GENDER_DISTRIBUTION)
    if not df.empty:
        fig = px.bar(df, x="gender", y="count",
                    color="gender", color_discrete_sequence=COLORS["chart"],
                    labels={"gender": "Jins", "count": "Soni"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=300,
            showlegend=False,
        )
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
                        hole=0.45)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value+label')
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("🟢 Onlayn / Oflayn")
        df = safe_query(queries.DEVICES_BY_STATUS)
        if not df.empty:
            color_map = {"online": "#10b981", "offline": "#6b7280"}
            fig = px.pie(df, values="count", names="status",
                        color="status", color_discrete_map=color_map,
                        hole=0.45)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value+label')
            st.plotly_chart(fig, use_container_width=True)

    section_header("📱 Eng ko'p ishlatiladigan qurilmalar")
    df = safe_query(queries.POPULAR_DEVICE_NAMES)
    if not df.empty:
        fig = px.bar(df, x="count", y="name", orientation='h',
                    color="count", color_continuous_scale="Viridis",
                    labels={"name": "Qurilma", "count": "Soni"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=400,
            yaxis=dict(autorange="reversed"), showlegend=False,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)


# ==================== 4. MULKLAR VA E'LONLAR ====================
elif page == "🏘️ Mulklar va E'lonlar":

    section_header("🏘️ Mulklar va E'lonlar")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("🏠", get_scalar(queries.TOTAL_PROPERTIES), "Jami mulklar")
    with col2:
        metric_card("📢", get_scalar(queries.TOTAL_ANNOUNCEMENTS), "Jami e'lonlar")
    with col3:
        views_df = safe_query(queries.ANNOUNCEMENTS_VIEWS_STATS)
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
                        color_discrete_sequence=COLORS["chart"], hole=0.4)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📋 Moderatsiya holati")
        df = safe_query(queries.ANNOUNCEMENTS_BY_MODERATION)
        if not df.empty:
            df["status_label"] = df["moderated_status"].map(STATUS_LABELS).fillna(df["moderated_status"])
            fig = px.pie(df, values="count", names="status_label",
                        color="moderated_status",
                        color_discrete_map=COLORS["status"],
                        hole=0.4)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value')
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
                        color_discrete_sequence=["#10b981", "#f59e0b"], hole=0.4)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=300,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value+label')
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📈 E'lonlar trendi (30 kun)")
        df = safe_query(queries.ANNOUNCEMENTS_CREATED_TREND)
        if not df.empty:
            fig = px.area(df, x="date", y="count",
                         color_discrete_sequence=["#f59e0b"],
                         labels={"date": "Sana", "count": "Yangi e'lonlar"})
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=300,
            )
            fig.update_traces(fill='tozeroy', fillcolor='rgba(245,158,11,0.1)')
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
                        hole=0.45)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📝 Shartnomalar holati")
        df = safe_query(queries.CONTRACTS_BY_STATUS)
        if not df.empty:
            df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
            fig = px.pie(df, values="count", names="status_label",
                        color="status", color_discrete_map=COLORS["status"],
                        hole=0.45)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)

    section_header("📈 Arizalar trendi (30 kun)")
    df = safe_query(queries.REQUESTS_TREND)
    if not df.empty:
        fig = px.bar(df, x="date", y="count",
                    color_discrete_sequence=["#6366f1"],
                    labels={"date": "Sana", "count": "Arizalar"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=300,
        )
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
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=300,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("💰 Shartnomalar daromadi")
        df = safe_query(queries.CONTRACTS_REVENUE)
        if not df.empty and df.iloc[0]["total_revenue"]:
            rev = df.iloc[0]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10b981, #059669);
                        padding: 1.5rem; border-radius: 14px; color: white;">
                <h3 style="margin: 0 0 1rem 0;">💰 Daromad statistikasi</h3>
                <p style="font-size: 1rem; margin: 0.5rem 0;">
                    <b>Umumiy daromad:</b> {rev['total_revenue']:,.0f} so'm
                </p>
                <p style="font-size: 1rem; margin: 0.5rem 0;">
                    <b>O'rtacha narx:</b> {rev['avg_price']:,.0f} so'm
                </p>
                <p style="font-size: 1rem; margin: 0.5rem 0;">
                    <b>Shartnomalar soni:</b> {rev['count']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Tasdiqlangan shartnomalar topilmadi")


# ==================== 6. XABARLAR ====================
elif page == "🔔 Xabarlar":

    section_header("🔔 Xabarlar (Notifications)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("🔔", get_scalar(queries.TOTAL_NOTIFICATIONS), "Jami xabarlar")
    with col2:
        metric_card("✈️", get_scalar(queries.NOTIFICATIONS_SENT), "Yuborilgan")
    with col3:
        read_df = safe_query(queries.NOTIFICATION_READ_RATE)
        read_count = int(read_df.iloc[0]["read_count"]) if not read_df.empty and read_df.iloc[0]["read_count"] else 0
        metric_card("📖", read_count, "O'qilgan")
    with col4:
        read_rate = float(read_df.iloc[0]["read_rate"]) if not read_df.empty and read_df.iloc[0]["read_rate"] else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{read_rate}%</div>
            <div class="metric-label">O'qilish darajasi</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    section_header("📈 Xabarlar trendi (30 kun)")
    df = safe_query(queries.NOTIFICATIONS_TREND)
    if not df.empty:
        fig = px.bar(df, x="date", y="count",
                    color_discrete_sequence=["#f59e0b"],
                    labels={"date": "Sana", "count": "Yuborilgan xabarlar"})
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    # O'qilish gauge
    section_header("🎯 O'qilish darajasi")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=read_rate,
        title={"text": "Notification o'qilish %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#10b981"},
            "steps": [
                {"range": [0, 30], "color": "#fef2f2"},
                {"range": [30, 70], "color": "#fefce8"},
                {"range": [70, 100], "color": "#f0fdf4"},
            ],
            "threshold": {"line": {"color": "#ef4444", "width": 2}, "value": 50},
        },
    ))
    fig.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)


# ==================== 7. FIREBASE ====================
elif page == "🔥 Firebase":

    section_header("🔥 Firebase Integration")

    firebase_info = get_firebase_summary()

    # Connection card
    st.markdown(f"""
    <div class="firebase-card">
        <h3 style="margin: 0 0 0.8rem 0;">🔥 Firebase Project</h3>
        <p style="margin: 0.3rem 0;"><b>Project ID:</b> {firebase_info['project_id']}</p>
        <p style="margin: 0.3rem 0;"><b>Holat:</b> {firebase_info['connection_status']}</p>
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
        <div style="background: #f8f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #e8ecf4;">
            <h4>📩 Cloud Messaging (FCM)</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">
                Push notification yuborish.
                RentMe da allaqachon ishlatilmoqda — arizalar,
                shartnomalar, xabarlar uchun.
            </p>
            <span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">Faol</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: #f8f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #e8ecf4;">
            <h4>📊 Analytics (GA4)</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">
                Foydalanuvchi xatti-harakatlari, sessiyalar,
                ekranlar, eventlar tracking.
                Firebase Console orqali ko'rish mumkin.
            </p>
            <span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">Console orqali</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: #f8f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #e8ecf4;">
            <h4>🔐 Authentication</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">
                Foydalanuvchi autentifikatsiyasi.
                RentMe da OTP orqali JWT ishlatilmoqda
                (Firebase Auth emas).
            </p>
            <span style="background: #6b7280; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">Ishlatilmayapti</span>
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
    section_header("📋 Firebase funktsionalliklari (prezentatsiya uchun)")

    st.markdown("""
    | # | Xizmat | Tavsif | RentMe da holati |
    |---|--------|--------|-----------------|
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
