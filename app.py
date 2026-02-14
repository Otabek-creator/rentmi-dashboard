"""
🏠 2RentMe Analytics Dashboard
Streamlit yordamida qurilgan professional analitik panel

✅ Performance: Query caching at app level
✅ Design: Professional light/dark theme with toggle
✅ Analyics: GA4 Integration (Auto-switch Demo/Real)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from database import execute_query
from services.analytics_service import AnalyticsService
import queries

# ======================== PAGE CONFIG ========================
st.set_page_config(
    page_title="2RentMe Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================== THEME STATE ========================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

IS_DARK = st.session_state.theme == "dark"

# ======================== CUSTOM CSS — PROFESSIONAL ========================

if IS_DARK:
    css_vars = """
    :root {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --metric-value-color: #f1f5f9;
        --border-color: rgba(148, 163, 184, 0.15);
        --border-hover: rgba(99, 102, 241, 0.4);
        --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
        --shadow-hover: 0 12px 40px rgba(99, 102, 241, 0.15);
        --section-bg: rgba(99, 102, 241, 0.08);
        --sidebar-bg: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        --header-bg: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
        --header-p-color: #94a3b8;
        --scrollbar-track: rgba(255,255,255,0.05);
        --scrollbar-thumb: rgba(99, 102, 241, 0.3);
        --streamlit-header-bg: rgba(15, 23, 42, 0.9);
        --demo-bg: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(245, 158, 11, 0.1));
        --demo-text: #fbbf24;
        --radio-bg: rgba(255, 255, 255, 0.04);
        --radio-hover: rgba(99, 102, 241, 0.12);
    }
    """
else:
    css_vars = """
    :root {
        --bg-primary: #f8fafc;
        --bg-secondary: #ffffff;
        --bg-card: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --metric-value-color: #1e293b;
        --border-color: #e2e8f0;
        --border-hover: rgba(99, 102, 241, 0.4);
        --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.04);
        --shadow-hover: 0 8px 30px rgba(99, 102, 241, 0.12);
        --section-bg: rgba(99, 102, 241, 0.04);
        --sidebar-bg: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        --header-bg: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #7c3aed 100%);
        --header-p-color: rgba(255, 255, 255, 0.85);
        --scrollbar-track: #f1f5f9;
        --scrollbar-thumb: rgba(99, 102, 241, 0.25);
        --streamlit-header-bg: rgba(248, 250, 252, 0.95);
        --demo-bg: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.06));
        --demo-text: #b45309;
        --radio-bg: #f8fafc;
        --radio-hover: rgba(99, 102, 241, 0.08);
    }
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    {css_vars}

    /* ===== GLOBAL ===== */
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }}
    .stApp p, .stApp span, .stApp li, .stApp td, .stApp th,
    .stApp label, .stApp div {{
        color: var(--text-primary);
    }}

    /* Hide streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: var(--streamlit-header-bg) !important;
        backdrop-filter: blur(20px);
    }}

    /* ===== MAIN HEADER ===== */
    .main-header {{
        background: var(--header-bg);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.15);
        position: relative;
        overflow: hidden;
    }}
    .main-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 60%);
        animation: headerGlow 8s ease-in-out infinite;
    }}
    @keyframes headerGlow {{
        0%, 100% {{ transform: translate(0, 0); }}
        50% {{ transform: translate(-20px, 10px); }}
    }}
    .main-header h1 {{
        margin: 0; font-size: 2.2rem; font-weight: 800;
        letter-spacing: -1px; position: relative; z-index: 1;
        color: white !important;
    }}
    .main-header p {{
        margin: 0.5rem 0 0 0;
        color: var(--header-p-color) !important;
        font-size: 0.95rem; font-weight: 400;
        position: relative; z-index: 1;
    }}

    /* ===== METRIC CARDS ===== */
    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        padding: 1.5rem 1.2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--shadow-card);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .metric-card::before {{
        content: '';
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
        border-radius: 16px 16px 0 0;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: var(--border-hover);
    }}
    .metric-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .metric-value {{
        font-size: 2.4rem; font-weight: 800;
        color: var(--metric-value-color) !important;
        line-height: 1.1; letter-spacing: -0.5px;
    }}
    .metric-delta {{
        font-size: 0.9rem; font-weight: 600;
        margin-top: 0.2rem; display: block;
    }}
    .delta-up {{ color: #10b981; }}
    .delta-down {{ color: #ef4444; }}
    .metric-label {{
        font-size: 0.8rem; color: var(--text-muted) !important;
        margin-top: 0.5rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.5px;
    }}

    /* ===== SECTION HEADERS ===== */
    .section-header {{
        font-size: 1.2rem; font-weight: 700;
        color: var(--text-primary) !important;
        margin: 2rem 0 1rem 0;
        padding: 0.8rem 1.2rem;
        border-left: 4px solid;
        border-image: linear-gradient(180deg, #6366f1, #8b5cf6) 1;
        background: var(--section-bg);
        border-radius: 0 12px 12px 0;
        letter-spacing: -0.3px;
    }}

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }}
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio span {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stSidebar"] .stRadio > div {{
        gap: 2px !important;
    }}
    [data-testid="stSidebar"] .stRadio > div > label {{
        background: var(--radio-bg) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid var(--border-color) !important;
    }}
    [data-testid="stSidebar"] .stRadio > div > label:hover {{
        background: var(--radio-hover) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }}

    /* ===== DEMO BOX ===== */
    .demo-box {{
        background: var(--demo-bg);
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
    }}
    .demo-box, .demo-box *, .demo-box span, .demo-box p, .demo-box b {{
        color: var(--demo-text) !important;
    }}

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--scrollbar-track); }}
    ::-webkit-scrollbar-thumb {{ background: var(--scrollbar-thumb); border-radius: 3px; }}

    /* ===== BUTTONS ===== */
    .stButton > button {{
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
    }}
</style>
""", unsafe_allow_html=True)


# ======================== PLOTLY THEME (dynamic) ========================

_plotly_text_color = "#94a3b8" if IS_DARK else "#475569"
_plotly_grid_color = "rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.06)"
_plotly_pie_text = "white" if IS_DARK else "#1e293b"

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=_plotly_text_color, size=12),
    xaxis=dict(showgrid=False, color=_plotly_text_color),
    yaxis=dict(showgrid=True, gridcolor=_plotly_grid_color, color=_plotly_text_color),
    margin=dict(l=0, r=0, t=30, b=0),
    height=350,
    legend=dict(font=dict(color=_plotly_text_color), bgcolor="rgba(0,0,0,0)"),
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


def metric_card(icon, value, label, delta=None):
    """Professional metrika kartochkasi"""
    if isinstance(value, str):
        formatted_value = value
    else:
        try:
            formatted_value = f"{value:,}"
        except (ValueError, TypeError):
            formatted_value = str(value)

    delta_html = ""
    if delta is not None:
        delta_class = "delta-up" if delta >= 0 else "delta-down"
        delta_sign = "+" if delta >= 0 else ""
        delta_html = f'<span class="metric-delta {delta_class}">{delta_sign}{delta}% (o\'tgan oy)</span>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(text):
    """Bo'lim sarlavhasi"""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def apply_plotly_theme(fig, height=350):
    """Plotly grafikga theme qo'llash"""
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
    "ordinary": "Oddiy", "tenant": "Ijarachi", "homeowner": "Uy egasi",
    "realtor": "Rieltor", "admin": "Admin", "client": "Mijoz",
}

STATUS_LABELS = {
    "pending": "Kutilmoqda", "approved": "Tasdiqlangan", "rejected": "Rad etilgan",
}


# ======================== SIDEBAR ========================

with st.sidebar:
    st.markdown("## 🏠 2RentMe")

    # Theme toggle
    theme_label = "🌙 Tungi rejim" if not IS_DARK else "☀️ Kunduzgi rejim"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "📊 Bo'lim tanlang",
        [
            "📊 Umumiy Analitika",
            "👤 Foydalanuvchilar",
            "🏘️ Uy Egalari",
            "🤝 Ijarachilar",
            "📈 Session Analytics",
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

# Initialize Session Analytics Service
analytics_service = AnalyticsService()

# ===============================================================
# ==================== SAHIFALAR ================================
# ===============================================================

# ==================== 1. UMUMIY ANALITIKA ====================
if page == "📊 Umumiy Analitika":

    # Top Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("👥", get_scalar(queries.TOTAL_USERS), "Jami foydalanuvchilar")
    with col2:
        metric_card("📝", get_scalar(queries.TOTAL_REQUESTS), "Jami arizalar")
    with col3:
        metric_card("🤝", get_scalar(queries.TOTAL_CONTRACTS), "Shartnomalar")
    with col4:
        metric_card("🏘️", get_scalar(queries.TOTAL_PROPERTIES), "Jami Mulklar")
    with col5:
        metric_card("✅", get_scalar(queries.ACTIVE_USERS), "Faol Userlar (Online)")

    st.markdown("")

    # Growth & Avg
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_req = get_scalar(queries.DAILY_REQUESTS_AVG)
        growth_req = get_scalar(queries.DAILY_REQUESTS_AVG_GROWTH)
        metric_card("📅", f"{float(avg_req):.1f}", "O'rtacha kunlik arizalar", delta=int(growth_req))
    
    with col2:
        new_users_week = get_scalar(queries.NEW_USERS_LAST_WEEK)
        new_users_prev = get_scalar(queries.NEW_USERS_PREV_WEEK)
        growth_users = ((new_users_week - new_users_prev) / new_users_prev * 100) if new_users_prev > 0 else 0
        metric_card("🆕", new_users_week, "Yangi Userlar (7 kun)", delta=int(growth_users))

    with col3:
        metric_card("💰", f"{get_scalar(queries.CONTRACTS_REVENUE):,.0f}", "Shartnoma tushumi")

    # Main Chart: Daily Trends
    section_header("📈 Kunlik Trendlar (Arizalar, Shartnomalar, Yangi Userlar)")
    df_trends = safe_query(queries.DAILY_TRENDS_CHART)
    if not df_trends.empty:
        fig = px.line(df_trends, x="date", y=["requests", "contracts", "new_users"],
                     color_discrete_map={"requests": "#6366f1", "contracts": "#10b981", "new_users": "#f59e0b"},
                     markers=True)
        apply_plotly_theme(fig, 400)
        fig.update_layout(legend_title_text="Ko'rsatkich")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend ma'lumotlari topilmadi")

# ==================== 2. FOYDALANUVCHILAR ====================
elif page == "👤 Foydalanuvchilar":
    section_header("👤 Foydalanuvchilar segmentatsiyasi")
    
    # Katta raqamlar
    total = get_scalar(queries.TOTAL_USERS)
    identified = get_scalar(queries.IDENTIFIED_USERS_COUNT)
    scored = get_scalar(queries.SCORED_USERS_COUNT)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("👥", total, "Jami")
    with col2:
        pct = int(identified / total * 100) if total > 0 else 0
        metric_card("🪪", f"{identified} ({pct}%)", "Identifikatsiyadan o'tgan")
    with col3:
        pct = int(scored / total * 100) if total > 0 else 0
        metric_card("⭐", f"{scored} ({pct}%)", "Scoringdan o'tgan")

    col_left, col_right = st.columns(2)
    
    with col_left:
        section_header("🧑‍🤝‍🧑 Rol bo'yicha taqsimot")
        df = safe_query(queries.USERS_BY_ROLE)
        if not df.empty:
            df["role_label"] = df["role"].map(ROLE_LABELS).fillna(df["role"])
            fig = px.pie(df, values="count", names="role_label",
                        color_discrete_sequence=COLORS["chart"], hole=0.5)
            apply_plotly_theme(fig)
            fig.update_traces(textinfo='percent+value', textfont=dict(color=_plotly_pie_text))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("👫 Jins bo'yicha")
        df = safe_query(queries.USERS_GENDER_DISTRIBUTION)
        if not df.empty:
            fig = px.bar(df, x="gender", y="count", color="gender", color_discrete_sequence=COLORS["chart"])
            apply_plotly_theme(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ==================== 3. UY EGALARI ====================
elif page == "🏘️ Uy Egalari":
    section_header("🏘️ Uy Egalari Analitikasi")
    
    total_owners = get_scalar(queries.TOTAL_HOMEOWNERS)
    inactive_owners = get_scalar(queries.HOMEOWNERS_WITHOUT_PROPERTY)
    active_percent = 100 - (int(inactive_owners / total_owners * 100) if total_owners > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("🏘️", total_owners, "Jami Uy Egalari")
    with col2:
        metric_card("⚠️", inactive_owners, "Mulk qo'shmaganlar (Action needed!)")
    with col3:
        metric_card("✅", f"{active_percent}%", "Faollik darajasi")

    if inactive_owners > 0:
        st.warning(f"⚠️ **Diqqat:** {inactive_owners} ta uy egasi ro'yxatdan o'tgan lekin hali mulk qo'shmagan. Ularga notification yuborish tavsiya etiladi.")

    # Property Status
    section_header("🏠 Mulklar holati")
    df = safe_query(queries.PROPERTIES_BY_STATUS)
    if not df.empty:
        fig = px.bar(df, x="status", y="count", color="status", 
                    color_discrete_sequence=COLORS["chart"], title="Mulk statuslari")
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

# ==================== 4. IJARACHILAR ====================
elif page == "🤝 Ijarachilar":
    section_header("🤝 Ijarachilar Analitikasi")
    
    total_tenants = get_scalar(queries.TOTAL_TENANTS)
    no_requests = get_scalar(queries.TENANTS_WITHOUT_REQUESTS)
    
    col1, col2 = st.columns(2)
    with col1:
        metric_card("🤝", total_tenants, "Jami Ijarachilar")
    with col2:
        metric_card("😴", no_requests, "Ariza yubormaganlar")
        
    st.info(f"💡 {no_requests} ta ijarachi ro'yxatdan o'tgan, lekin hali birorta ham ariza yubormagan. Ularni faollashtirish kerak.")
    
    section_header("📋 Arizalar statusi")
    df = safe_query(queries.REQUESTS_BY_STATUS)
    if not df.empty:
        df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
        fig = px.pie(df, values="count", names="status_label", 
                    color="status", color_discrete_map=COLORS["status"], hole=0.4)
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

# ==================== 5. SESSION ANALYTICS ====================
elif page == "📈 Session Analytics":
    
    # Check if demo or real
    if analytics_service.use_mock:
        st.markdown(f"""
        <div class="demo-box">
            <b>⚠️ DIQQAT: Demo Mode</b><br>
            Google Analytics 4 (GA4) ulanmaganligi sababli, quyidagi ma'lumotlar <b>DEMO (tasodifiy)</b> hisoblanadi.
            Real ma'lumotlarni ko'rish uchun <code>secrets.toml</code> ga GA4 ma'lumotlarini kiriting.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ Real Data: Google Analytics 4 Connected")
        
    data = analytics_service.get_dashboard_metrics(days=30)
    key = data["key_metrics"]
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("👥", key["dau"], "DAU (Daily Active)")
    with col2:
        metric_card("📅", key["mau"], "MAU (Monthly Active)")
    with col3:
        sticky = int(key["dau"]/key["mau"]*100) if key["mau"] > 0 else 0
        metric_card("🧲", f"{sticky}%", "Sticky Factor")
    with col4:
        metric_card("⏱️", f"{int(key['avg_session_duration'])}s", "O'rtacha sessiya")
    with col5:
        metric_card("🚪", f"{int(key['bounce_rate'])}%", "Bounce Rate")

    # Trends
    section_header("📈 Kunlik Faollik (Users vs Sessions)")
    df_trend = data["trends"]
    if not df_trend.empty:
        fig = px.area(df_trend, x="date", y=["active_users", "sessions"],
                     color_discrete_sequence=["#6366f1", "#10b981"])
        apply_plotly_theme(fig, 350)
        st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)
    
    with col_left:
        section_header("📱 Qurilma turlari")
        df_dev = data["device_stats"]
        if not df_dev.empty:
            fig = px.pie(df_dev, values="sessions", names="deviceCategory", hole=0.5,
                        color_discrete_sequence=COLORS["chart"])
            apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            
    with col_right:
        section_header("📄 Eng ko'p ko'rilgan sahifalar")
        df_pages = data["top_pages"]
        st.dataframe(df_pages, hide_index=True, use_container_width=True)

