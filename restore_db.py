"""
restore_db.py — SQL Dump faylidan bazani tiklash (Advanced Parser)

Production bazasidan olingan `rent_db.sql` faylini Dashboard (Neon.tech) bazasiga yuklaydi.
Bu versiya `COPY` komandalarini va psql-maxsus komandalarini (`\restrict` kabi)
to'g'ri qayta ishlash uchun maxsus parserdan foydalanadi.

DIQQAT! Bu skript mavjud barcha ma'lumotlarni o'chirib yuboradi (DROP SCHEMA public CASCADE).
"""

import os
import io
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Config credentials ni xavfsiz o'qish
try:
    from config import DB_CONFIG
except ImportError:
    # Fallback agar config.py o'qilmasa (lekin bu yerda bo'lishi kerak)
    import os
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME", ""),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", ""),
        "port": os.getenv("DB_PORT", "5432"),
    }

DUMP_FILE = "rent_db.sql"


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def execute_sql_dump(cur, filename):
    """
    SQL faylni o'qib, COPY statementlarini ajratib, qolganini execute qiladi.
    """
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    buffer = []
    copy_buffer = []
    in_copy_mode = False
    copy_command = ""

    print(f"📄 Fayl o'qildi: {len(lines)} qator.")

    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 1. COPY blok ichidamisiz?
        if in_copy_mode:
            if stripped == r'\.':
                # COPY tugadi
                in_copy_mode = False
                if copy_buffer:
                    # COPY ni bajarish
                    csv_io = io.StringIO("".join(copy_buffer))
                    try:
                        print(f"   📋 COPY bajarilmoqda: {copy_command[:50]}...")
                        cur.copy_expert(copy_command, csv_io)
                    except Exception as e:
                        print(f"❌ COPY Xatolik (Line {i}): {e}")
                        raise e
                copy_buffer = []
                copy_command = ""
            else:
                copy_buffer.append(line)
            continue

        # 2. Yangi COPY buyrug'i?
        # pg_dump COPY ni alohida qatorda yozadi
        if line.startswith("COPY ") and "FROM stdin" in line:
            # Oldingi yig'ilgan SQL larni bajarish
            if buffer:
                try:
                    cur.execute("".join(buffer))
                except Exception as e:
                    print(f"❌ SQL Xatolik (Line {i}): {e}")
                    raise e
                buffer = []
            
            # COPY rejimiga o'tish
            in_copy_mode = True
            copy_command = line.strip().rstrip(';') # ; olib tashlash kerakmi? copy_expert uchun odatda ha/yo'q farqi yo'q, lekin SQL da ; bor
            # copy_expert query string sifatida to'liq command ni kutyapti, shu jumladan FROM STDIN
            copy_command = line.strip() 
            continue

        # 3. Psql maxsus komandalari (\connect, \restrict va h.k)
        if stripped.startswith('\\') and not in_copy_mode:
            continue

        # 4. Role/Ownership komandalarini filtrlash (Neon.tech da 'postgres' roli yo'q bo'lishi mumkin)
        if "OWNER TO" in stripped or stripped.startswith("GRANT") or stripped.startswith("REVOKE"):
            # print(f"   ⏩ Role command ignored: {stripped[:40]}...")
            continue
        
        # 5. Oddiy SQL (yig'ib boramiz)
        if not stripped:
            continue
            
        if stripped.startswith('--'):
            continue

        buffer.append(line)
        
        # Agar qator ; bilan tugasa, execute qilamiz (xotirani tejash uchun)
        if stripped.endswith(';'):
            try:
                cur.execute("".join(buffer))
                buffer = []
            except Exception as e:
                # Ba'zan ; string ichida bo'lishi mumkin, lekin pg_dump da kamdan-kam
                print(f"⚠️ SQL Execute warning (Line {i}): {e}")
                # Davom etamiz, balki buffer to'liq emasdir
                # Lekin pg_dump da har doim ; yangi qatorda yoki oxirida bo'ladi
                pass


    # Qolgan buffer
    if buffer:
        cur.execute("".join(buffer))


def restore_database():
    if not os.path.exists(DUMP_FILE):
        print(f"❌ Fayl topilmadi: {DUMP_FILE}")
        return

    print("🔌 Bazaga ulanmoqda...")
    try:
        conn = get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Ulanish xatosi (config va .env ni tekshiring): {e}")
        return

    # 1. Tozalash
    print("🧹 Eski ma'lumotlar tozalanmoqda (DROP SCHEMA public)...")
    try:
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;") # Neon.tech uchun
        print("✅ Baza tozalandi.")
    except Exception as e:
        print(f"❌ Tozalash xatosi: {e}")
        conn.close()
        return

    # 2. Parser bilan yuklash
    print(f"📂 {DUMP_FILE} parser orqali yuklanmoqda...")
    try:
        execute_sql_dump(cur, DUMP_FILE)
        print("✅ SQL dump muvaffaqiyatli yuklandi!")
    except Exception as e:
        print(f"❌ Yuklash jarayonida xatolik: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("⚠️  DIQQAT! Bu skript Dashboard bazasini TO'LIQ TOZALAYDI va qayta yozadi.")
    confirm = input(f"'{DUMP_FILE}' faylidan tiklashni tasdiqlaysizmi? (ha/yo'q): ")
    if confirm.lower() in ['ha', 'yes', 'y']:
        restore_database()
