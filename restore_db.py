"""
restore_db.py — SQL Dump faylidan bazani tiklash

Production bazasidan olingan `rent_db.sql` faylini Dashboard (Neon.tech) bazasiga yuklaydi.
DIQQAT! Bu skript mavjud barcha ma'lumotlarni o'chirib yuboradi (DROP SCHEMA public CASCADE).
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_CONFIG

# SQL dump fayl nomi
DUMP_FILE = "rent_db.sql"

def get_connection():
    """Bazaga ulanish"""
    return psycopg2.connect(**DB_CONFIG)

def restore_database():
    """
    1. Schema public ni tozalash.
    2. rent_db.sql ni o'qish va ijro etish.
    """
    if not os.path.exists(DUMP_FILE):
        print(f"❌ Fayl topilmadi: {DUMP_FILE}")
        return

    print("🔌 Bazaga ulanmoqda...")
    try:
        conn = get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Ulanish xatosi: {e}")
        return

    # 1. Tozalash
    print("🧹 Eski ma'lumotlar tozalanmoqda (DROP SCHEMA public)...")
    try:
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;") # Yoki kerakli userga
        # Neon.tech da 'public' rolga grant berish ba'zan kerak bo'ladi
        print("✅ Baza tozalandi.")
    except Exception as e:
        print(f"❌ Tozalash xatosi: {e}")
        conn.close()
        return

    # 2. Fayl o'qish va yuklash
    print(f"📂 {DUMP_FILE} o'qilmoqda va yuklanmoqda...")
    
    # Faylni to'liq o'qib, execute qilish (oddiy usul)
    # Katta fayllar uchun psql command-line utility yaxshiroq, lekin python bilan ham bo'ladi
    try:
        with open(DUMP_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        cur.execute(sql_content)
        print("✅ SQL dump muvaffaqiyatli yuklandi!")
        
    except Exception as e:
        print(f"❌ Yuklash xatosi: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("⚠️  DIQQAT! Bu skript Dashboard bazasini TO'LIQ TOZALAYDI va qayta yozadi.")
    confirm = input(f"'{DUMP_FILE}' faylidan tiklashni tasdiqlaysizmi? (ha/yo'q): ")
    if confirm.lower() in ['ha', 'yes', 'y']:
        restore_database()
