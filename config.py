import os
from dotenv import load_dotenv

load_dotenv()

# Local PostgreSQL
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "rentme_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Firebase credentials
FIREBASE_CREDENTIALS_PATH = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    "../backend/apps/notification/data/firebase-adminsdk.json"
)

# SQLAlchemy connection string (agar kerak bo'lsa)
DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)
