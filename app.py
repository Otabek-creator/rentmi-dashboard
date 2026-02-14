"""
🏠 2RentMe Analytics Dashboard
Streamlit yordamida qurilgan professional analitik panel

✅ Performance: Query caching at app level
✅ Design: Modern top-tab navigation, light theme
✅ Analytics: GA4 Integration (Auto-switch Demo/Real)
✅ Filter: Date range filtering with growth %
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from database import execute_query
from services.analytics_service import AnalyticsService
import queries

# ======================== PAGE CONFIG ========================
st.set_page_config(
    page_title="2RentMe Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ======================== CUSTOM CSS ========================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

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
        --demo-bg: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.06));
        --demo-text: #b45309;
    }

    /* ===== GLOBAL ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    .stApp p, .stApp span, .stApp li, .stApp td, .stApp th,
    .stApp label, .stApp div {
        color: var(--text-primary);
    }

    /* Hide streamlit branding & sidebar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(248, 250, 252, 0.95) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* ===== TOP TABS STYLING (STICKY NAVBAR) ===== */
    .stTabs {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 0;
        padding: 0.4rem 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-bottom: 1px solid var(--border-color);
        margin: -1rem -1rem 1.5rem -1rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        border-bottom: none !important;
        padding: 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 12px;
        padding: 0 1.2rem;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: -0.2px;
        color: var(--text-secondary) !important;
        background: transparent;
        border: none !important;
        white-space: nowrap;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.06);
        color: #4f46e5 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ===== METRIC CARDS (COMPACT) ===== */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        padding: 0.8rem 0.8rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: var(--shadow-card);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
        border-radius: 12px 12px 0 0;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
        border-color: var(--border-hover);
    }
    .metric-icon { font-size: 1.3rem; margin-bottom: 0.2rem; }
    .metric-value {
        font-size: 1.5rem; font-weight: 800;
        color: var(--metric-value-color) !important;
        line-height: 1.1; letter-spacing: -0.5px;
    }
    .metric-delta {
        font-size: 0.7rem; font-weight: 600;
        margin-top: 0.1rem; display: block;
    }
    .delta-up { color: #10b981; }
    .delta-down { color: #ef4444; }
    .metric-label {
        font-size: 0.65rem; color: var(--text-muted) !important;
        margin-top: 0.3rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.3px;
    }

    /* ===== SECTION HEADERS (COMPACT) ===== */
    .section-header {
        font-size: 0.95rem; font-weight: 700;
        color: var(--text-primary) !important;
        margin: 1rem 0 0.6rem 0;
        padding: 0.5rem 0.8rem;
        border-left: 3px solid;
        border-image: linear-gradient(180deg, #6366f1, #8b5cf6) 1;
        background: var(--section-bg);
        border-radius: 0 8px 8px 0;
        letter-spacing: -0.3px;
    }

    /* ===== DEMO BOX ===== */
    .demo-box {
        background: var(--demo-bg);
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .demo-box, .demo-box *, .demo-box span, .demo-box p, .demo-box b {
        color: var(--demo-text) !important;
    }

    /* ===== DATE FILTER ===== */
    .date-filter-row .stDateInput > div {
        border-radius: 10px;
    }
    .date-filter-row .stDateInput label {
        font-size: 0.75rem !important;
        font-weight: 600;
        color: var(--text-muted) !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.25); border-radius: 3px; }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)


# ======================== PLOTLY THEME ========================

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#475569", size=12),
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)", color="#475569"),
    margin=dict(l=0, r=0, t=30, b=0),
    height=250,
    legend=dict(font=dict(color="#475569"), bgcolor="rgba(0,0,0,0)"),
)


# ======================== HELPER FUNCTIONS ========================

@st.cache_data(ttl=300, show_spinner=False)
def safe_query(query, params=None):
    """Xavfsiz so'rov (5 daq cached)"""
    try:
        return execute_query(query, params)
    except Exception as e:
        st.error(f"❌ So'rov xatosi: {e}")
        return pd.DataFrame()


def get_scalar(query, default=0, params=None):
    """Bitta qiymat qaytaruvchi so'rov"""
    df = safe_query(query, params)
    if df.empty:
        return default
    return df.iloc[0, 0] or default


def calc_growth(current, previous):
    """O'sish foizini hisoblash"""
    if previous > 0:
        return int((current - previous) / previous * 100)
    return 0


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
        delta_html = f'<span class="metric-delta {delta_class}">{delta_sign}{delta}% oldingi davrga nisbatan</span>'

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


def apply_plotly_theme(fig, height=250):
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


# ======================== DATE FILTER ========================

if "filter_start" not in st.session_state:
    st.session_state.filter_start = datetime.now().date() - timedelta(days=30)
if "filter_end" not in st.session_state:
    st.session_state.filter_end = datetime.now().date()

# Filter qator — chap tarafda bo'sh, o'ng tarafda sanalar
fcol1, fcol2, fcol3 = st.columns([6, 2, 2])
with fcol2:
    start_date = st.date_input("📅 Boshlanish", value=st.session_state.filter_start, key="d_start")
    st.session_state.filter_start = start_date
with fcol3:
    end_date = st.date_input("📅 Tugash", value=st.session_state.filter_end, key="d_end")
    st.session_state.filter_end = end_date

# Oldingi davr (xuddi shuncha kunlik)
range_days = (end_date - start_date).days
prev_start = start_date - timedelta(days=range_days + 1)
prev_end = start_date - timedelta(days=1)

date_params = (str(start_date), str(end_date))
prev_params = (str(prev_start), str(prev_end))


# ======================== TOP TAB NAVIGATION ========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Umumiy Analitika",
    "👤 Foydalanuvchilar",
    "🏘️ Uy Egalari",
    "🤝 Ijarachilar",
    "📈 Session Analytics",
])

analytics_service = AnalyticsService()


# ==================== 1. UMUMIY ANALITIKA ====================
with tab1:

    cur_users = get_scalar(queries.users_in_range(), params=date_params)
    cur_requests = get_scalar(queries.requests_in_range(), params=date_params)
    cur_contracts = get_scalar(queries.contracts_in_range(), params=date_params)
    cur_properties = get_scalar(queries.properties_in_range(), params=date_params)
    total_active = get_scalar(queries.ACTIVE_USERS)

    prev_users = get_scalar(queries.users_in_prev_range(), params=prev_params)
    prev_requests = get_scalar(queries.requests_in_prev_range(), params=prev_params)
    prev_contracts = get_scalar(queries.contracts_in_prev_range(), params=prev_params)
    prev_properties = get_scalar(queries.properties_in_prev_range(), params=prev_params)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("👥", cur_users, "Yangi foydalanuvchilar", delta=calc_growth(cur_users, prev_users))
    with col2:
        metric_card("📝", cur_requests, "Arizalar", delta=calc_growth(cur_requests, prev_requests))
    with col3:
        metric_card("🤝", cur_contracts, "Shartnomalar", delta=calc_growth(cur_contracts, prev_contracts))
    with col4:
        metric_card("🏘️", cur_properties, "Yangi Mulklar", delta=calc_growth(cur_properties, prev_properties))
    with col5:
        metric_card("✅", total_active, "Faol Userlar (Online)")

    st.markdown("")

    cur_revenue = get_scalar(queries.revenue_in_range(), params=date_params)
    prev_revenue = get_scalar(queries.revenue_in_prev_range(), params=prev_params)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("💰", f"{cur_revenue:,.0f}", "Shartnoma tushumi", delta=calc_growth(cur_revenue, prev_revenue))
    with col2:
        total_all_users = get_scalar(queries.TOTAL_USERS)
        metric_card("📊", total_all_users, "Jami foydalanuvchilar (barchasi)")
    with col3:
        total_all_requests = get_scalar(queries.TOTAL_REQUESTS)
        metric_card("📋", total_all_requests, "Jami arizalar (barchasi)")

    section_header("📈 Kunlik Trendlar (Arizalar, Shartnomalar, Yangi Userlar)")
    df_trends = safe_query(queries.daily_trends_in_range(), params=date_params)
    if not df_trends.empty:
        df_trends = df_trends.rename(columns={"date": "sana", "requests": "Arizalar", "contracts": "Shartnomalar", "new_users": "Yangi userlar"})
        fig = px.line(df_trends, x="sana", y=["Arizalar", "Shartnomalar", "Yangi userlar"],
                     color_discrete_map={"Arizalar": "#6366f1", "Shartnomalar": "#10b981", "Yangi userlar": "#f59e0b"},
                     markers=True, labels={"sana": "Sana", "value": "Qiymati", "variable": "Ko'rsatkich"})
        apply_plotly_theme(fig, 280)
        fig.update_layout(legend_title_text="Ko'rsatkich", xaxis_title="Sana", yaxis_title="Soni")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend ma'lumotlari topilmadi")


# ==================== 2. FOYDALANUVCHILAR ====================
with tab2:
    section_header("👤 Foydalanuvchilar segmentatsiyasi")

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
            fig.update_traces(textinfo='percent+value', textfont=dict(color="#1e293b"))
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
with tab3:
    section_header("🏘️ Uy Egalari Analitikasi")

    total_owners = get_scalar(queries.TOTAL_HOMEOWNERS)
    inactive_owners = get_scalar(queries.HOMEOWNERS_WITHOUT_PROPERTY)
    active_percent = 100 - (int(inactive_owners / total_owners * 100) if total_owners > 0 else 0)
    cur_owners = get_scalar(queries.homeowners_in_range(), params=date_params)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("🏘️", total_owners, "Jami Uy Egalari")
    with col2:
        metric_card("🆕", cur_owners, f"Yangi ({start_date} — {end_date})")
    with col3:
        metric_card("⚠️", inactive_owners, "Mulk qo'shmaganlar")
    with col4:
        metric_card("✅", f"{active_percent}%", "Faollik darajasi")

    if inactive_owners > 0:
        st.warning(f"⚠️ **Diqqat:** {inactive_owners} ta uy egasi ro'yxatdan o'tgan lekin hali mulk qo'shmagan.")

    section_header("🏠 Mulklar holati")
    df = safe_query(queries.PROPERTIES_BY_STATUS)
    if not df.empty:
        fig = px.bar(df, x="status", y="count", color="status",
                    color_discrete_sequence=COLORS["chart"], title="Mulk statuslari")
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


# ==================== 4. IJARACHILAR ====================
with tab4:
    section_header("🤝 Ijarachilar Analitikasi")

    total_tenants = get_scalar(queries.TOTAL_TENANTS)
    no_requests = get_scalar(queries.TENANTS_WITHOUT_REQUESTS)
    cur_tenants = get_scalar(queries.tenants_in_range(), params=date_params)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("🤝", total_tenants, "Jami Ijarachilar")
    with col2:
        metric_card("🆕", cur_tenants, f"Yangi ({start_date} — {end_date})")
    with col3:
        metric_card("😴", no_requests, "Ariza yubormaganlar")

    st.info(f"💡 {no_requests} ta ijarachi ro'yxatdan o'tgan, lekin hali birorta ham ariza yubormagan.")

    section_header("📋 Arizalar statusi (tanlangan davr)")
    df = safe_query(queries.requests_by_status_in_range(), params=date_params)
    if not df.empty:
        df["status_label"] = df["status"].map(STATUS_LABELS).fillna(df["status"])
        fig = px.pie(df, values="count", names="status_label",
                    color="status", color_discrete_map=COLORS["status"], hole=0.4)
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tanlangan davrda arizalar topilmadi")


# ==================== 5. SESSION ANALYTICS ====================
with tab5:

    session_days = max(range_days, 1)
    data = analytics_service.get_dashboard_metrics(days=session_days)
    key = data["key_metrics"]

    if analytics_service.use_mock:
        st.markdown("""
        <div class="demo-box">
            <b>⚠️ DIQQAT: Demo Mode</b><br>
            Google Analytics 4 (GA4) ulanmaganligi sababli, quyidagi ma'lumotlar <b>DEMO (tasodifiy)</b> hisoblanadi.
            Real ma'lumotlarni ko'rish uchun <code>secrets.toml</code> ga GA4 ma'lumotlarini kiriting.
        </div>
        """, unsafe_allow_html=True)
    else:
        if analytics_service.last_error:
            st.error(f"❌ GA4 Xatolik: {analytics_service.last_error}")
            st.warning("⚠️ Ma'lumotlarni olib bo'lmadi. Demo ma'lumotlar ko'rsatilmoqda.")
        else:
            st.success("✅ Haqiqiy ma'lumot: Google Analytics 4 ulangan")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("👥", key["dau"], "Kunlik faol foydalanuvchilar")
    with col2:
        metric_card("📅", key["mau"], "Oylik faol foydalanuvchilar")
    with col3:
        sticky = int(key["dau"]/key["mau"]*100) if key["mau"] > 0 else 0
        metric_card("🧲", f"{sticky}%", "Qaytish ko'rsatkichi")
    with col4:
        metric_card("⏱️", f"{int(key['avg_session_duration'])}s", "O'rtacha sessiya")
    with col5:
        metric_card("🚪", f"{int(key['bounce_rate'])}%", "Tark etish darajasi")

    section_header("📈 Kunlik Faollik (Foydalanuvchilar va Sessiyalar)")
    df_trend = data["trends"]
    if not df_trend.empty:
        df_trend = df_trend.rename(columns={"date": "sana", "active_users": "Faol foydalanuvchilar", "sessions": "Sessiyalar"})
        fig = px.area(df_trend, x="sana", y=["Faol foydalanuvchilar", "Sessiyalar"],
                     color_discrete_sequence=["#6366f1", "#10b981"],
                     labels={"sana": "Sana", "value": "Qiymati", "variable": "Ko'rsatkich"})
        apply_plotly_theme(fig, 250)
        fig.update_layout(xaxis_title="Sana", yaxis_title="Qiymati")
        st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("📱 Qurilma turlari")
        df_dev = data["device_stats"]
        if not df_dev.empty:
            device_labels = {"desktop": "Kompyuter", "mobile": "Telefon", "tablet": "Planshet"}
            df_dev["Qurilma"] = df_dev["deviceCategory"].map(device_labels).fillna(df_dev["deviceCategory"])
            fig = px.pie(df_dev, values="sessions", names="Qurilma", hole=0.5,
                        color_discrete_sequence=COLORS["chart"])
            apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("📄 Eng ko'p ko'rilgan sahifalar")
        df_pages = data["top_pages"]
        st.dataframe(df_pages, hide_index=True, use_container_width=True)
