import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# Streamlit Cloud da st.secrets ishlatiladi, localda esa .env
try:
    if "postgres" in st.secrets:
        DB_CONFIG = dict(st.secrets["postgres"])
        # Neon.tech uchun SSL talab qilinishi mumkin
        if "sslmode" not in DB_CONFIG:
            DB_CONFIG["sslmode"] = "require"
    else:
        # Debugging: Agar secrets o'qilmasa, nimaga o'qilmayotganini bilish uchun
        print(f"⚠️ 'postgres' section not found in st.secrets. Available keys: {list(st.secrets.keys())}")
        raise KeyError("'postgres' not found")
except (FileNotFoundError, KeyError):
    # Fallback to local
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME", "rentme_analytics"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "12345"),
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "5432"),
    }

# Firebase credentials
# Streamlit Cloud da st.secrets["firebase"] ishlatiladi
if "firebase" in st.secrets:
    FIREBASE_CREDENTIALS = dict(st.secrets["firebase"])
    FIREBASE_CREDENTIALS_PATH = None # Fayl yo'li kerak emas
else:
    FIREBASE_CREDENTIALS = None
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "../backend/apps/notification/data/firebase-adminsdk.json" # Local path
    )

# SQLAlchemy connection string (agar kerak bo'lsa)
DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

