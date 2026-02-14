"""
etl.py — Extract, Transform, Load (Production PostgreSQL → Dashboard PostgreSQL)

Production bazadan ma'lumotni olib, Dashboard (Neon.tech) bazasiga UPSERT qiladi.
Mavjud ma'lumotlar yangilanadi, yangilari qo'shiladi.

Qo'llanilishi:
  1. Streamlit Cloud: app.py dagi "Sinxronlash" tugmasi orqali
  2. Lokal: `python etl.py`
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor

from config import SOURCE_DB_CONFIG
from database import create_tables, get_connection as get_target_connection


def get_source_connection():
    """Production Database ga ulanish"""
    if SOURCE_DB_CONFIG is None:
        raise ConnectionError(
            "Production baza konfiguratsiyasi topilmadi. "
            "Streamlit Secrets ga [source_postgres] qo'shing."
        )
    return psycopg2.connect(**SOURCE_DB_CONFIG)


def sync_data():
    """
    Production → Dashboard sinxronlash (UPSERT).
    Qaytaradi: dict {jadval_nomi: ko'chirilgan_soni} yoki xatolik matni.
    """
    results = {}

    # 1. Source ga ulanish
    try:
        source_conn = get_source_connection()
    except Exception as e:
        return {"error": f"Production bazaga ulanib bo'lmadi: {e}"}

    # 2. Target ga ulanish + jadvallar yaratish
    try:
        create_tables()
        target_conn = get_target_connection()
    except Exception as e:
        source_conn.close()
        return {"error": f"Dashboard bazaga ulanib bo'lmadi: {e}"}

    source_cur = source_conn.cursor(cursor_factory=RealDictCursor)
    target_cur = target_conn.cursor()

    try:
        # ==================== USERS ====================
        source_cur.execute("""
            SELECT id, phone_number, first_name, last_name, role, is_active, is_deleted,
                   date_joined, last_login, created_at, birth_date, gender, is_identified
            FROM "user" WHERE is_deleted = false
        """)
        users = source_cur.fetchall()
        for u in users:
            target_cur.execute("""
                INSERT INTO users (id, phone_number, first_name, last_name, role, is_active, is_deleted,
                                   date_joined, last_login, created_at, birth_date, gender, is_identified)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    phone_number=EXCLUDED.phone_number, first_name=EXCLUDED.first_name,
                    last_name=EXCLUDED.last_name, role=EXCLUDED.role, is_active=EXCLUDED.is_active,
                    last_login=EXCLUDED.last_login, gender=EXCLUDED.gender, is_identified=EXCLUDED.is_identified
            """, (u['id'], u['phone_number'], u['first_name'], u['last_name'], u['role'],
                  u['is_active'], u['is_deleted'], u['date_joined'], u['last_login'],
                  u['created_at'], u['birth_date'], u['gender'], u['is_identified']))
        results["users"] = len(users)

        # ==================== DEVICES ====================
        source_cur.execute("""
            SELECT id, user_id, status, device_id, fcm_token, name, device_type,
                   is_deleted, created_at, last_synced_at
            FROM user_device WHERE is_deleted = false
        """)
        devices = source_cur.fetchall()
        for d in devices:
            target_cur.execute("""
                INSERT INTO devices (id, user_id, status, device_id, fcm_token, name, device_type,
                                     is_deleted, created_at, last_synced_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    status=EXCLUDED.status, fcm_token=EXCLUDED.fcm_token, name=EXCLUDED.name,
                    last_synced_at=EXCLUDED.last_synced_at
            """, (d['id'], d['user_id'], d['status'], d['device_id'], d['fcm_token'],
                  d['name'], d['device_type'], d['is_deleted'], d['created_at'], d['last_synced_at']))
        results["devices"] = len(devices)

        # ==================== PROPERTIES ====================
        source_cur.execute("""
            SELECT id, user_id, title, type, status, area, address, n_rooms, floor,
                   is_rentable, is_deleted, created_at
            FROM properties WHERE is_deleted = false
        """)
        props = source_cur.fetchall()
        for p in props:
            title_json = json.dumps(p['title']) if p['title'] else None
            target_cur.execute("""
                INSERT INTO properties (id, user_id, title, type, status, area, address, n_rooms, floor,
                                        is_rentable, is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    title=EXCLUDED.title, status=EXCLUDED.status, area=EXCLUDED.area,
                    is_rentable=EXCLUDED.is_rentable
            """, (p['id'], p['user_id'], title_json, p['type'], p['status'], p['area'],
                  p['address'], p['n_rooms'], p['floor'], p['is_rentable'], p['is_deleted'], p['created_at']))
        results["properties"] = len(props)

        # ==================== ANNOUNCEMENTS ====================
        source_cur.execute("""
            SELECT id, user_id, property_id, title, price, currency, moderated_status,
                   views, phone_views, is_available, is_moderated, is_deleted, created_at
            FROM property_announcements WHERE is_deleted = false
        """)
        anns = source_cur.fetchall()
        for a in anns:
            title_json = json.dumps(a['title']) if a['title'] else None
            target_cur.execute("""
                INSERT INTO announcements (id, user_id, property_id, title, price, currency, moderated_status,
                                           views, phone_views, is_available, is_moderated, is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    price=EXCLUDED.price, moderated_status=EXCLUDED.moderated_status,
                    views=EXCLUDED.views, phone_views=EXCLUDED.phone_views,
                    is_available=EXCLUDED.is_available, is_moderated=EXCLUDED.is_moderated
            """, (a['id'], a['user_id'], a['property_id'], title_json, a['price'], a['currency'],
                  a['moderated_status'], a['views'], a['phone_views'], a['is_available'],
                  a['is_moderated'], a['is_deleted'], a['created_at']))
        results["announcements"] = len(anns)

        # ==================== RENTAL REQUESTS ====================
        try:
            source_cur.execute("""
                SELECT id, property_id, announcement_id, user_id_id as user_id,
                       sender_id_id as sender_id, status, text, is_deleted, created_at
                FROM property_rentalrequest WHERE is_deleted = false
            """)
        except psycopg2.Error:
            source_conn.rollback()
            source_cur.execute("""
                SELECT id, property_id, announcement_id, user_id, sender_id,
                       status, text, is_deleted, created_at
                FROM property_rentalrequest WHERE is_deleted = false
            """)

        reqs = source_cur.fetchall()
        for r in reqs:
            target_cur.execute("""
                INSERT INTO rental_requests (id, property_id, announcement_id, user_id, sender_id,
                                             status, text, is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    status=EXCLUDED.status, text=EXCLUDED.text
            """, (r['id'], r['property_id'], r['announcement_id'], r['user_id'],
                  r['sender_id'], r['status'], r['text'], r['is_deleted'], r['created_at']))
        results["rental_requests"] = len(reqs)

        # ==================== CONTRACTS ====================
        source_cur.execute("""
            SELECT id, rental_request_id, property_id, tenant_id, homeowner_id,
                   status, price, start_date, end_date, contract_type, is_deleted, created_at
            FROM contract WHERE is_deleted = false
        """)
        conts = source_cur.fetchall()
        for c in conts:
            target_cur.execute("""
                INSERT INTO contracts (id, rental_request_id, property_id, tenant_id, homeowner_id,
                                       status, price, start_date, end_date, contract_type, is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    status=EXCLUDED.status, price=EXCLUDED.price,
                    start_date=EXCLUDED.start_date, end_date=EXCLUDED.end_date
            """, (c['id'], c['rental_request_id'], c['property_id'], c['tenant_id'],
                  c['homeowner_id'], c['status'], c['price'], c['start_date'],
                  c['end_date'], c['contract_type'], c['is_deleted'], c['created_at']))
        results["contracts"] = len(conts)

        # ==================== NOTIFICATIONS ====================
        source_cur.execute("""
            SELECT id, title, description, send_to_all, is_sent, sent_at, is_deleted, created_at
            FROM notification WHERE is_deleted = false
        """)
        notifs = source_cur.fetchall()
        for n in notifs:
            target_cur.execute("""
                INSERT INTO notifications (id, title, description, send_to_all, is_sent, sent_at,
                                           is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    is_sent=EXCLUDED.is_sent, sent_at=EXCLUDED.sent_at
            """, (n['id'], n['title'], n['description'], n['send_to_all'],
                  n['is_sent'], n['sent_at'], n['is_deleted'], n['created_at']))
        results["notifications"] = len(notifs)

        # ==================== USER NOTIFICATIONS ====================
        source_cur.execute("""
            SELECT id, user_id, notification_id, is_read, read_at, is_deleted, created_at
            FROM user_notification WHERE is_deleted = false
        """)
        unotifs = source_cur.fetchall()
        for u in unotifs:
            target_cur.execute("""
                INSERT INTO user_notifications (id, user_id, notification_id, is_read, read_at,
                                                is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    is_read=EXCLUDED.is_read, read_at=EXCLUDED.read_at
            """, (u['id'], u['user_id'], u['notification_id'], u['is_read'],
                  u['read_at'], u['is_deleted'], u['created_at']))
        results["user_notifications"] = len(unotifs)

        # ==================== COMMENTS ====================
        source_cur.execute("""
            SELECT id, property_id, announcement_id, author_id, title, text, rating,
                   is_approved, is_deleted, created_at
            FROM comment WHERE is_deleted = false
        """)
        comments = source_cur.fetchall()
        for c in comments:
            target_cur.execute("""
                INSERT INTO comments (id, property_id, announcement_id, author_id, title, text,
                                      rating, is_approved, is_deleted, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    rating=EXCLUDED.rating, is_approved=EXCLUDED.is_approved, text=EXCLUDED.text
            """, (c['id'], c['property_id'], c['announcement_id'], c['author_id'],
                  c['title'], c['text'], c['rating'], c['is_approved'],
                  c['is_deleted'], c['created_at']))
        results["comments"] = len(comments)

        # Commit
        target_conn.commit()

    except Exception as e:
        target_conn.rollback()
        results["error"] = str(e)
    finally:
        source_cur.close()
        target_cur.close()
        source_conn.close()
        target_conn.close()

    return results


# ==================== CLI MODE ====================
if __name__ == "__main__":
    print("⚠️  DIQQAT! Bu skript Production → Dashboard bazaga ma'lumot sinxronlaydi.")
    confirm = input("Davom etamizmi? (ha/yo'q): ")
    if confirm.lower() in ['ha', 'yes', 'y']:
        print("\n🔄 Sinxronlash boshlanmoqda...")
        result = sync_data()

        if "error" in result:
            print(f"\n❌ Xatolik: {result['error']}")
        else:
            print("\n✅ Sinxronlash muvaffaqiyatli!")
            for table, count in result.items():
                print(f"  📋 {table}: {count} ta yozuv")
