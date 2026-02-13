"""
etl.py — Extract, Transform, Load (PostgreSQL -> PostgreSQL)

Bu skript Production (Backend) bazasidan Local (Dashboard) bazasiga ma'lumot ko'chiradi.
Ikki baza ham PostgreSQL.

Qo'llanilishi:
1. .env faylida SOURCE_* (Production) va DB_* (Local) ma'lumotlarini to'g'irlang.
2. Skriptni ishga tushiring: `python etl.py`
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from database import create_tables, get_connection as get_target_connection

load_dotenv()

# Source (Production PostgreSQL) connection details
SOURCE_DB_CONFIG = {
    "dbname": os.getenv("SOURCE_DB_NAME", "rentme_production"),
    "user": os.getenv("SOURCE_DB_USER", "postgres"),
    "password": os.getenv("SOURCE_DB_PASSWORD", "your_production_password"),
    "host": os.getenv("SOURCE_DB_HOST", "127.0.0.1"),
    "port": os.getenv("SOURCE_DB_PORT", "5432"),
}


def get_source_connection():
    """Production Database ga ulanish"""
    try:
        conn = psycopg2.connect(**SOURCE_DB_CONFIG)
        print("✅ Production bazaga ulanildi!")
        return conn
    except Exception as e:
        print(f"❌ Production bazaga ulanib bo'lmadi: {e}")
        print("💡 .env faylida SOURCE_* ma'lumotlarini tekshiring.")
        return None


def migrate_data():
    """Ma'lumotlarni ko'chirish"""

    print("🔌 Production bazaga ulanmoqda...")
    pg_conn = get_source_connection()
    if not pg_conn:
        return

    print("🔌 Local PostgreSQL bazaga ulanmoqda...")
    try:
        # Jadvallarni qayta yaratish
        create_tables()
        target_conn = get_target_connection()
    except Exception as e:
        print(f"❌ Local PostgreSQL bazaga ulanib bo'lmadi: {e}")
        print("💡 DB_* ma'lumotlarini tekshiring va baza yaratilganiga ishonch hosil qiling.")
        return

    source_cur = pg_conn.cursor(cursor_factory=RealDictCursor)
    target_cur = target_conn.cursor()

    try:
        # === USERS ===
        print("Migrating users...")
        source_cur.execute("""
            SELECT id, phone_number, first_name, last_name, role, is_active, is_deleted,
                   date_joined, last_login, created_at, birth_date, gender, is_identified
            FROM "user" WHERE is_deleted = false
        """)
        users = source_cur.fetchall()
        
        # PostgreSQL executemany with execute_values is faster but strict.
        # Use simpler execute loop or executemany for safety with names.
        # Or improved executemany with %s
        
        user_list = [
            (u['id'], u['phone_number'], u['first_name'], u['last_name'], u['role'], u['is_active'], u['is_deleted'],
             u['date_joined'], u['last_login'], u['created_at'], u['birth_date'], u['gender'], u['is_identified'])
            for u in users
        ]
        
        target_cur.executemany("""
            INSERT INTO users (id, phone_number, first_name, last_name, role, is_active, is_deleted,
                               date_joined, last_login, created_at, birth_date, gender, is_identified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, user_list)
        print(f"  - {len(users)} ta user ko'chirildi.")

        # === DEVICES ===
        print("Migrating devices...")
        source_cur.execute("""
            SELECT id, user_id, status, device_id, fcm_token, name, device_type, is_deleted, created_at, last_synced_at
            FROM user_device WHERE is_deleted = false
        """)
        devices = source_cur.fetchall()
        device_list = [
            (d['id'], d['user_id'], d['status'], d['device_id'], d['fcm_token'], d['name'], d['device_type'],
             d['is_deleted'], d['created_at'], d['last_synced_at'])
            for d in devices
        ]
        target_cur.executemany("""
            INSERT INTO devices (id, user_id, status, device_id, fcm_token, name, device_type, is_deleted, created_at, last_synced_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, device_list)
        print(f"  - {len(devices)} ta qurilma ko'chirildi.")

        # === PROPERTIES ===
        print("Migrating properties...")
        source_cur.execute("""
            SELECT id, user_id, title, type, status, area, address, n_rooms, floor, is_rentable, is_deleted, created_at
            FROM properties WHERE is_deleted = false
        """)
        props = source_cur.fetchall()
        prop_list = []
        for p in props:
            # JSONB usually comes as dict from psycopg2 RealDictCursor
            title_json = json.dumps(p['title']) if p['title'] else None
            prop_list.append((
                p['id'], p['user_id'], title_json, p['type'], p['status'], p['area'], p['address'],
                p['n_rooms'], p['floor'], p['is_rentable'], p['is_deleted'], p['created_at']
            ))
            
        target_cur.executemany("""
            INSERT INTO properties (id, user_id, title, type, status, area, address, n_rooms, floor, is_rentable, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, prop_list)
        print(f"  - {len(props)} ta mulk ko'chirildi.")

        # === ANNOUNCEMENTS ===
        print("Migrating announcements...")
        source_cur.execute("""
            SELECT id, user_id, property_id, title, price, currency, moderated_status, views, phone_views,
                   is_available, is_moderated, is_deleted, created_at
            FROM property_announcements WHERE is_deleted = false
        """)
        anns = source_cur.fetchall()
        ann_list = []
        for a in anns:
            title_json = json.dumps(a['title']) if a['title'] else None
            ann_list.append((
                a['id'], a['user_id'], a['property_id'], title_json, a['price'], a['currency'], a['moderated_status'],
                a['views'], a['phone_views'], a['is_available'], a['is_moderated'], a['is_deleted'], a['created_at']
            ))

        target_cur.executemany("""
            INSERT INTO announcements (id, user_id, property_id, title, price, currency, moderated_status,
                                       views, phone_views, is_available, is_moderated, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, ann_list)
        print(f"  - {len(anns)} ta e'lon ko'chirildi.")

        # === REQUESTS ===
        print("Migrating rental requests...")
        try:
            source_cur.execute("""
                SELECT id, property_id, announcement_id, user_id_id as user_id, sender_id_id as sender_id, 
                       status, text, is_deleted, created_at
                FROM property_rentalrequest WHERE is_deleted = false
            """)
        except psycopg2.Error:
            pg_conn.rollback()
            print("⚠️ 'property_rentalrequest' jadvalidan user_id_id topilmadi, 'user_id' bilan urinib ko'ramiz...")
            source_cur.execute("""
                SELECT id, property_id, announcement_id, user_id, sender_id, 
                       status, text, is_deleted, created_at
                FROM property_rentalrequest WHERE is_deleted = false
            """)
            
        reqs = source_cur.fetchall()
        req_list = [
            (r['id'], r['property_id'], r['announcement_id'], r['user_id'], r['sender_id'],
             r['status'], r['text'], r['is_deleted'], r['created_at'])
            for r in reqs
        ]
        
        target_cur.executemany("""
            INSERT INTO rental_requests (id, property_id, announcement_id, user_id, sender_id, status, text, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, req_list)
        print(f"  - {len(reqs)} ta ariza ko'chirildi.")

        # === CONTRACTS ===
        print("Migrating contracts...")
        source_cur.execute("""
            SELECT id, rental_request_id, property_id, tenant_id, homeowner_id, status, price, start_date, end_date, contract_type, is_deleted, created_at
            FROM contract WHERE is_deleted = false
        """)
        conts = source_cur.fetchall()
        cont_list = [
            (c['id'], c['rental_request_id'], c['property_id'], c['tenant_id'], c['homeowner_id'],
             c['status'], c['price'], c['start_date'], c['end_date'], c['contract_type'], c['is_deleted'], c['created_at'])
            for c in conts
        ]
        target_cur.executemany("""
            INSERT INTO contracts (id, rental_request_id, property_id, tenant_id, homeowner_id, status, price, start_date, end_date, contract_type, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, cont_list)
        print(f"  - {len(conts)} ta shartnoma ko'chirildi.")

        # === NOTIFICATIONS ===
        print("Migrating notifications...")
        source_cur.execute("""
            SELECT id, title, description, send_to_all, is_sent, sent_at, is_deleted, created_at
            FROM notification WHERE is_deleted = false
        """)
        notifs = source_cur.fetchall()
        notif_list = [
            (n['id'], n['title'], n['description'], n['send_to_all'], n['is_sent'], n['sent_at'], n['is_deleted'], n['created_at'])
            for n in notifs
        ]
        target_cur.executemany("""
            INSERT INTO notifications (id, title, description, send_to_all, is_sent, sent_at, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, notif_list)
        print(f"  - {len(notifs)} ta xabar (template) ko'chirildi.")

        # === USER NOTIFICATIONS ===
        print("Migrating user notifications...")
        source_cur.execute("""
            SELECT id, user_id, notification_id, is_read, read_at, is_deleted, created_at
            FROM user_notification WHERE is_deleted = false
        """)
        unotifs = source_cur.fetchall()
        # Large table - batch it if necessary, but list comp is fine for <100k
        unotif_list = [
            (u['id'], u['user_id'], u['notification_id'], u['is_read'], u['read_at'], u['is_deleted'], u['created_at'])
            for u in unotifs
        ]
        target_cur.executemany("""
            INSERT INTO user_notifications (id, user_id, notification_id, is_read, read_at, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, unotif_list)
        print(f"  - {len(unotifs)} ta user xabarlari ko'chirildi.")

        # === COMMENTS ===
        print("Migrating comments...")
        source_cur.execute("""
            SELECT id, property_id, announcement_id, author_id, title, text, rating, is_approved, is_deleted, created_at
            FROM comment WHERE is_deleted = false
        """)
        comments = source_cur.fetchall()
        comment_list = [
            (c['id'], c['property_id'], c['announcement_id'], c['author_id'], c['title'], c['text'], c['rating'], c['is_approved'], c['is_deleted'], c['created_at'])
            for c in comments
        ]
        target_cur.executemany("""
            INSERT INTO comments (id, property_id, announcement_id, author_id, title, text, rating, is_approved, is_deleted, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, comment_list)
        print(f"  - {len(comments)} ta sharh ko'chirildi.")
        
    except Exception as e:
        target_conn.rollback()
        print(f"❌ Xatolik yuz berdi: {e}")
    finally:
        target_conn.commit()
        target_conn.close()
        pg_conn.close()
        print("\n✅ Migratsiya muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    print("⚠️  DIQQAT! Bu skript Production PostgreSQL dan Local PostgreSQL ga ma'lumot ko'chiradi.")
    confirm = input("Davom etamizmi? (ha/yo'q): ")
    if confirm.lower() in ['ha', 'yes', 'y']:
        migrate_data()
