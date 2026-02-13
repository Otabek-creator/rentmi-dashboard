"""
database.py — PostgreSQL ulanish va jadval yaratish

RentMe backendidan olingan ma'lumotlarni o'z local PostgreSQL bazangizda
saqlash uchun jadvallar yaratiladi.
"""

import pandas as pd
import psycopg2

from config import DB_CONFIG


def get_connection():
    """PostgreSQL ga ulanish"""
    return psycopg2.connect(**DB_CONFIG)


def execute_query(query, params=None):
    """SELECT so'rov bajarish, DataFrame qaytaradi"""
    conn = get_connection()
    try:
        # Pandas o'zi column namelarini to'g'ri oladi
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()


def execute_write(query, params=None):
    """INSERT/UPDATE/CREATE so'rov bajarish"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
    finally:
        conn.close()


def create_tables():
    """
    RentMe bazasidan kerakli jadvallarni local bazada yaratish.
    Bu jadvallar asl bazadagi jadvallarning soddalashtirilgan versiyasi —
    faqat analitika uchun kerakli ustunlar.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    -- ==================== USERS ====================
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        phone_number VARCHAR(100),
        first_name VARCHAR(150),
        last_name VARCHAR(150),
        role VARCHAR(50) DEFAULT 'ordinary',
        is_active BOOLEAN DEFAULT TRUE,
        is_deleted BOOLEAN DEFAULT FALSE,
        date_joined TIMESTAMP,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        birth_date DATE,
        gender VARCHAR(225),
        is_identified BOOLEAN DEFAULT FALSE
    );

    -- ==================== DEVICES ====================
    CREATE TABLE IF NOT EXISTS devices (
        id BIGINT PRIMARY KEY,
        user_id BIGINT REFERENCES users(id),
        status VARCHAR(10) DEFAULT 'offline',
        device_id VARCHAR(255),
        fcm_token VARCHAR(255),
        name VARCHAR(255),
        device_type VARCHAR(20),
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        last_synced_at TIMESTAMP
    );

    -- ==================== PROPERTIES ====================
    CREATE TABLE IF NOT EXISTS properties (
        id BIGINT PRIMARY KEY,
        user_id BIGINT REFERENCES users(id),
        title JSONB,
        type VARCHAR(50) DEFAULT 'apartment',
        status VARCHAR(50) DEFAULT 'draft',
        area FLOAT,
        address VARCHAR(255),
        n_rooms INTEGER,
        floor INTEGER,
        is_rentable BOOLEAN DEFAULT TRUE,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== ANNOUNCEMENTS ====================
    CREATE TABLE IF NOT EXISTS announcements (
        id BIGINT PRIMARY KEY,
        user_id BIGINT REFERENCES users(id),
        property_id BIGINT REFERENCES properties(id),
        title JSONB,
        price DECIMAL(12,2),
        currency VARCHAR(10) DEFAULT 'UZS',
        moderated_status VARCHAR(100) DEFAULT 'pending',
        views INTEGER DEFAULT 0,
        phone_views INTEGER DEFAULT 0,
        is_available BOOLEAN DEFAULT TRUE,
        is_moderated BOOLEAN DEFAULT FALSE,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== RENTAL REQUESTS ====================
    CREATE TABLE IF NOT EXISTS rental_requests (
        id BIGINT PRIMARY KEY,
        property_id BIGINT,
        announcement_id BIGINT,
        user_id BIGINT REFERENCES users(id),
        sender_id BIGINT,
        status VARCHAR(50) DEFAULT 'pending',
        text TEXT,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== CONTRACTS ====================
    CREATE TABLE IF NOT EXISTS contracts (
        id BIGINT PRIMARY KEY,
        rental_request_id BIGINT,
        property_id BIGINT,
        tenant_id BIGINT,
        homeowner_id BIGINT,
        status VARCHAR(100) DEFAULT 'pending',
        price DECIMAL(12,2),
        start_date DATE,
        end_date DATE,
        contract_type VARCHAR(50) DEFAULT 'fixed',
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== NOTIFICATIONS ====================
    CREATE TABLE IF NOT EXISTS notifications (
        id BIGINT PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        send_to_all BOOLEAN DEFAULT FALSE,
        is_sent BOOLEAN DEFAULT FALSE,
        sent_at TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== USER NOTIFICATIONS ====================
    CREATE TABLE IF NOT EXISTS user_notifications (
        id BIGINT PRIMARY KEY,
        user_id BIGINT REFERENCES users(id),
        notification_id BIGINT REFERENCES notifications(id),
        is_read BOOLEAN DEFAULT FALSE,
        read_at TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== COMMENTS / REVIEWS ====================
    CREATE TABLE IF NOT EXISTS comments (
        id BIGINT PRIMARY KEY,
        property_id BIGINT,
        announcement_id BIGINT,
        author_id BIGINT REFERENCES users(id),
        title VARCHAR(500),
        text TEXT,
        rating INTEGER,
        is_approved BOOLEAN DEFAULT TRUE,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ==================== FIREBASE SYNC LOG ====================
    CREATE TABLE IF NOT EXISTS firebase_sync_log (
        id BIGSERIAL PRIMARY KEY,
        sync_type VARCHAR(50),
        synced_at TIMESTAMP DEFAULT NOW(),
        records_synced INTEGER DEFAULT 0,
        status VARCHAR(20) DEFAULT 'success',
        error_message TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Barcha jadvallar yaratildi (PostgreSQL)!")


def seed_demo_data():
    """
    Demo/test ma'lumotlarni yaratish (PostgreSQL uchun).
    """
    import random
    import json
    from datetime import datetime, timedelta

    conn = get_connection()
    cur = conn.cursor()

    # Mavjud ma'lumot borligini tekshirish
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"⚠️  Bazada {count} ta user allaqachon bor. Demo data qo'shilmadi.")
        cur.close()
        conn.close()
        return

    roles = ['ordinary', 'tenant', 'homeowner', 'realtor', 'admin', 'client']
    genders = ['male', 'female', None]
    device_types = ['android', 'ios']
    statuses_device = ['online', 'offline']
    property_types = ['apartment', 'house', 'studio', 'villa']
    mod_statuses = ['pending', 'approved', 'rejected']
    request_statuses = ['pending', 'approved', 'rejected']
    contract_statuses = ['pending', 'approved', 'rejected']
    contract_types = ['fixed', 'monthly', 'month_to_month', 'yearly']

    now = datetime.now()

    # --- USERS (200 ta) ---
    print("👤 Userlar yaratilmoqda...")
    for i in range(1, 201):
        days_ago = random.randint(0, 365)
        joined = now - timedelta(days=days_ago)
        last_login = joined + timedelta(days=random.randint(0, days_ago)) if random.random() > 0.2 else None
        role = random.choices(roles, weights=[30, 25, 25, 10, 5, 5])[0]

        cur.execute("""
            INSERT INTO users (id, phone_number, first_name, last_name, role, is_active,
                             date_joined, last_login, birth_date, gender, is_identified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            f"+99890{random.randint(1000000, 9999999)}",
            f"User{i}",
            f"Lastname{i}",
            role,
            random.random() > 0.05,
            joined,
            last_login,
            (now - timedelta(days=random.randint(6570, 18250))).date() if random.random() > 0.3 else None,
            random.choice(genders),
            random.random() > 0.6,
        ))

    # --- DEVICES (150 ta) ---
    print("📱 Qurilmalar yaratilmoqda...")
    for i in range(1, 151):
        user_id = random.randint(1, 200)
        cur.execute("""
            INSERT INTO devices (id, user_id, status, device_id, fcm_token, name, device_type, created_at, last_synced_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            user_id,
            random.choice(statuses_device),
            f"dev_{i}_{random.randint(1000, 9999)}",
            f"fcm_token_{i}",
            random.choice(["Samsung Galaxy S24", "iPhone 15", "Xiaomi 14", "Pixel 8", "iPhone 14 Pro", "Samsung A54", "Redmi Note 13"]),
            random.choice(device_types),
            now - timedelta(days=random.randint(0, 300)),
            now - timedelta(hours=random.randint(0, 168)) if random.random() > 0.3 else None,
        ))

    # --- PROPERTIES (80 ta) ---
    print("🏠 Mulklar yaratilmoqda...")
    for i in range(1, 81):
        cur.execute("""
            INSERT INTO properties (id, user_id, title, type, status, area, n_rooms, floor, is_rentable, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            random.randint(1, 200),
            json.dumps({'uz': f'Kvartira {i}', 'ru': f'Квартира {i}', 'en': f'Apartment {i}'}),
            random.choice(property_types),
            random.choice(['draft', 'completed']),
            random.randint(25, 200),
            random.randint(1, 6),
            random.randint(1, 16),
            random.random() > 0.2,
            now - timedelta(days=random.randint(0, 300)),
        ))

    # --- ANNOUNCEMENTS (60 ta) ---
    print("📢 E'lonlar yaratilmoqda...")
    for i in range(1, 61):
        cur.execute("""
            INSERT INTO announcements (id, user_id, property_id, title, price, currency, moderated_status,
                                      views, phone_views, is_available, is_moderated, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            random.randint(1, 200),
            random.randint(1, 80),
            json.dumps({'uz': f'E\'lon {i}', 'ru': f'Объявление {i}', 'en': f'Announcement {i}'}),
            random.choice([500000, 800000, 1200000, 2000000, 3500000, 5000000, 300, 500, 800]),
            random.choice(["UZS", "UZS", "UZS", "USD"]),
            random.choice(mod_statuses),
            random.randint(0, 500),
            random.randint(0, 100),
            random.random() > 0.15,
            random.random() > 0.3,
            now - timedelta(days=random.randint(0, 200)),
        ))

    # --- RENTAL REQUESTS (100 ta) ---
    print("📋 Arizalar yaratilmoqda...")
    for i in range(1, 101):
        cur.execute("""
            INSERT INTO rental_requests (id, property_id, announcement_id, user_id, sender_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            random.randint(1, 80),
            random.randint(1, 60),
            random.randint(1, 200),
            random.randint(1, 200),
            random.choice(request_statuses),
            now - timedelta(days=random.randint(0, 180)),
        ))

    # --- CONTRACTS (40 ta) ---
    print("📝 Shartnomalar yaratilmoqda...")
    for i in range(1, 41):
        start = now - timedelta(days=random.randint(30, 365))
        cur.execute("""
            INSERT INTO contracts (id, rental_request_id, property_id, tenant_id, homeowner_id,
                                  status, price, start_date, end_date, contract_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            random.randint(1, 100),
            random.randint(1, 80),
            random.randint(1, 200),
            random.randint(1, 200),
            random.choice(contract_statuses),
            random.choice([500000, 800000, 1500000, 2500000, 4000000]),
            start.date(),
            (start + timedelta(days=random.choice([90, 180, 365]))).date(),
            random.choice(contract_types),
            start,
        ))

    # --- NOTIFICATIONS (50 ta) ---
    print("🔔 Xabarlar yaratilmoqda...")
    for i in range(1, 51):
        sent = random.random() > 0.2
        sent_at_val = now - timedelta(days=random.randint(0, 90)) if sent else None
        cur.execute("""
            INSERT INTO notifications (id, title, description, send_to_all, is_sent, sent_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            f"Xabar {i}",
            f"Bu test notification {i}",
            random.random() > 0.8,
            sent,
            sent_at_val,
            now - timedelta(days=random.randint(0, 90)),
        ))

    # --- USER NOTIFICATIONS (200 ta) ---
    print("📬 User xabarlar yaratilmoqda...")
    for i in range(1, 201):
        is_read = random.random() > 0.4
        cur.execute("""
            INSERT INTO user_notifications (id, user_id, notification_id, is_read, read_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            i,
            random.randint(1, 200),
            random.randint(1, 50),
            is_read,
            now - timedelta(hours=random.randint(0, 500)) if is_read else None,
            now - timedelta(days=random.randint(0, 90)),
        ))

    # --- COMMENTS (30 ta) ---
    print("💬 Sharhlar yaratilmoqda...")
    for i in range(1, 31):
        cur.execute("""
            INSERT INTO comments (id, property_id, announcement_id, author_id, title, text, rating, is_approved, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            i,
            random.randint(1, 80),
            random.randint(1, 60) if random.random() > 0.5 else None,
            random.randint(1, 200),
            f"Sharh {i}",
            f"Bu test sharh matni {i}",
            random.randint(1, 5),
            random.random() > 0.1,
            now - timedelta(days=random.randint(0, 150)),
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Demo ma'lumotlar muvaffaqiyatli yaratildi!")


if __name__ == "__main__":
    print("🔧 Jadvallar yaratilmoqda (PostgreSQL)...")
    try:
        create_tables()
        print()
        answer = input("Demo ma'lumotlarni yaratishni xohlaysizmi? (ha/yo'q): ").strip().lower()
        if answer in ("ha", "h", "yes", "y"):
            seed_demo_data()
        else:
            print("Demo data qo'shilmadi.")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        print("💡 Maslahat: .env faylida DB_USER, DB_PASSWORD va DB_NAME ni tekshiring.")
        print("💡 PostgreSQL server ishlayotganiga ishonch hosil qiling.")
