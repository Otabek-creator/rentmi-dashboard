"""
config.py — Dashboard va Production bazalar konfiguratsiyasi

Dashboard DB:  st.secrets["postgres"]     → Neon.tech (dashboard o'qiydi)
Source DB:     st.secrets["source_postgres"] → Production (ETL o'qiydi)
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ======================== DASHBOARD DATABASE ========================
# Streamlit Cloud da st.secrets ishlatiladi, localda esa .env
DB_CONFIG = None
try:
    if "postgres" in st.secrets:
        DB_CONFIG = dict(st.secrets["postgres"])
        if "sslmode" not in DB_CONFIG:
            DB_CONFIG["sslmode"] = "require"
except Exception:
    pass

if DB_CONFIG is None:
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME", "rentme_analytics"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "12345"),
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "5432"),
    }

# ======================== SOURCE (PRODUCTION) DATABASE ========================
# ETL uchun — production bazadan ma'lumot olish
SOURCE_DB_CONFIG = None
try:
    if "source_postgres" in st.secrets:
        SOURCE_DB_CONFIG = dict(st.secrets["source_postgres"])
        if "sslmode" not in SOURCE_DB_CONFIG:
            SOURCE_DB_CONFIG["sslmode"] = "require"
except Exception:
    pass

# Fallback: .env dan o'qish (lokal ishlatish uchun)
if SOURCE_DB_CONFIG is None:
    _src_host = os.getenv("SOURCE_DB_HOST")
    if _src_host:
        SOURCE_DB_CONFIG = {
            "dbname": os.getenv("SOURCE_DB_NAME", "rentme_production"),
            "user": os.getenv("SOURCE_DB_USER", "postgres"),
            "password": os.getenv("SOURCE_DB_PASSWORD", ""),
            "host": _src_host,
            "port": os.getenv("SOURCE_DB_PORT", "5432"),
        }

# ======================== FIREBASE ========================
FIREBASE_CREDENTIALS = None
try:
    if "firebase" in st.secrets:
        FIREBASE_CREDENTIALS = dict(st.secrets["firebase"])
        FIREBASE_CREDENTIALS_PATH = None
except Exception:
    pass

if FIREBASE_CREDENTIALS is None:
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "../backend/apps/notification/data/firebase-adminsdk.json"
    )
else:
    FIREBASE_CREDENTIALS_PATH = None

# ======================== FLAGS ========================
# Production rejimda = source_postgres mavjud
IS_PRODUCTION = SOURCE_DB_CONFIG is not None
