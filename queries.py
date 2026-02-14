"""
queries.py — Barcha SQL so'rovlar (PostgreSQL)

RentMe bazasidagi jadvallardan analitik ma'lumotlarni olish uchun
SQL so'rovlar to'plami.

DIQQAT: Jadvallar nomlari Django production bazasiga moslashtirildi.
users -> "user"
devices -> user_device
announcements -> property_announcements
rental_requests -> property_rentalrequest
contracts -> contract
notifications -> notification
user_notifications -> user_notification
comments -> comment
"""

# ==================== UMUMIY STATISTIKA ====================

TOTAL_USERS = """
SELECT COUNT(*) as total FROM "user" WHERE is_deleted = FALSE
"""

ACTIVE_USERS = """
SELECT COUNT(*) as total FROM "user" WHERE is_active = TRUE AND is_deleted = FALSE
"""

NEW_USERS_TODAY = """
SELECT COUNT(*) as total FROM "user"
WHERE DATE(date_joined) = CURRENT_DATE AND is_deleted = FALSE
"""

NEW_USERS_THIS_WEEK = """
SELECT COUNT(*) as total FROM "user"
WHERE date_joined >= CURRENT_DATE - INTERVAL '7 days' AND is_deleted = FALSE
"""

NEW_USERS_THIS_MONTH = """
SELECT COUNT(*) as total FROM "user"
WHERE date_joined >= CURRENT_DATE - INTERVAL '30 days' AND is_deleted = FALSE
"""

# ==================== USERLAR BO'YICHA ====================

USERS_BY_ROLE = """
SELECT role, COUNT(*) as count
FROM "user" WHERE is_deleted = FALSE
GROUP BY role ORDER BY count DESC
"""

USERS_REGISTRATION_TREND = """
SELECT DATE(date_joined) as date, COUNT(*) as count
FROM "user" WHERE is_deleted = FALSE AND date_joined >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(date_joined)
ORDER BY date
"""

USERS_REGISTRATION_MONTHLY = """
SELECT DATE_TRUNC('month', date_joined) as month, COUNT(*) as count
FROM "user" WHERE is_deleted = FALSE AND date_joined >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', date_joined)
ORDER BY month
"""

USERS_GENDER_DISTRIBUTION = """
SELECT
    COALESCE(gender, 'ko''rsatilmagan') as gender,
    COUNT(*) as count
FROM "user" WHERE is_deleted = FALSE
GROUP BY gender
"""

IDENTIFIED_USERS = """
SELECT
    CASE WHEN is_identified THEN 'Tasdiqlangan' ELSE 'Tasdiqlanmagan' END as status,
    COUNT(*) as count
FROM "user" WHERE is_deleted = FALSE
GROUP BY is_identified
"""

# ==================== QURILMALAR ====================

TOTAL_DEVICES = """
SELECT COUNT(*) as total FROM user_device WHERE is_deleted = FALSE
"""

ONLINE_DEVICES = """
SELECT COUNT(*) as total FROM user_device WHERE status = 'online' AND is_deleted = FALSE
"""

DEVICES_BY_TYPE = """
SELECT device_type, COUNT(*) as count
FROM user_device WHERE is_deleted = FALSE
GROUP BY device_type ORDER BY count DESC
"""

DEVICES_BY_STATUS = """
SELECT status, COUNT(*) as count
FROM user_device WHERE is_deleted = FALSE
GROUP BY status
"""

POPULAR_DEVICE_NAMES = """
SELECT name, COUNT(*) as count
FROM user_device WHERE is_deleted = FALSE
GROUP BY name ORDER BY count DESC LIMIT 10
"""

RECENTLY_ACTIVE_DEVICES = """
SELECT COUNT(*) as total FROM user_device
WHERE last_synced_at >= NOW() - INTERVAL '24 hours' AND is_deleted = FALSE
"""

# ==================== MULKLAR ====================

TOTAL_PROPERTIES = """
SELECT COUNT(*) as total FROM properties WHERE is_deleted = FALSE
"""

PROPERTIES_BY_TYPE = """
SELECT type, COUNT(*) as count
FROM properties WHERE is_deleted = FALSE
GROUP BY type ORDER BY count DESC
"""

PROPERTIES_BY_STATUS = """
SELECT status, COUNT(*) as count
FROM properties WHERE is_deleted = FALSE
GROUP BY status
"""

RENTABLE_VS_NOT = """
SELECT
    CASE WHEN is_rentable THEN 'Ijaraga tayyor' ELSE 'Band' END as status,
    COUNT(*) as count
FROM properties WHERE is_deleted = FALSE
GROUP BY is_rentable
"""

PROPERTIES_CREATED_TREND = """
SELECT DATE(created_at) as date, COUNT(*) as count
FROM properties WHERE is_deleted = FALSE AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date
"""

# ==================== E'LONLAR ====================

TOTAL_ANNOUNCEMENTS = """
SELECT COUNT(*) as total FROM property_announcements WHERE is_deleted = FALSE
"""

ANNOUNCEMENTS_BY_MODERATION = """
SELECT moderated_status, COUNT(*) as count
FROM property_announcements WHERE is_deleted = FALSE
GROUP BY moderated_status
"""

TOP_VIEWED_ANNOUNCEMENTS = """
SELECT id, title, views, phone_views, price, currency, created_at
FROM property_announcements WHERE is_deleted = FALSE
ORDER BY views DESC LIMIT 10
"""

ANNOUNCEMENTS_VIEWS_STATS = """
SELECT
    SUM(views) as total_views,
    SUM(phone_views) as total_phone_views,
    AVG(views) as avg_views,
    MAX(views) as max_views
FROM property_announcements WHERE is_deleted = FALSE
"""

ANNOUNCEMENTS_CREATED_TREND = """
SELECT DATE(created_at) as date, COUNT(*) as count
FROM property_announcements WHERE is_deleted = FALSE AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date
"""

# ==================== ARIZALAR (RENTAL REQUESTS) ====================

TOTAL_REQUESTS = """
SELECT COUNT(*) as total FROM property_rentalrequest WHERE is_deleted = FALSE
"""

REQUESTS_BY_STATUS = """
SELECT status, COUNT(*) as count
FROM property_rentalrequest WHERE is_deleted = FALSE
GROUP BY status
"""

REQUESTS_TREND = """
SELECT DATE(created_at) as date, COUNT(*) as count
FROM property_rentalrequest WHERE is_deleted = FALSE AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date
"""

PENDING_REQUESTS = """
SELECT COUNT(*) as total FROM property_rentalrequest
WHERE status = 'pending' AND is_deleted = FALSE
"""

# ==================== SHARTNOMALAR ====================

TOTAL_CONTRACTS = """
SELECT COUNT(*) as total FROM contract WHERE is_deleted = FALSE
"""

CONTRACTS_BY_STATUS = """
SELECT status, COUNT(*) as count
FROM contract WHERE is_deleted = FALSE
GROUP BY status
"""

CONTRACTS_BY_TYPE = """
SELECT contract_type, COUNT(*) as count
FROM contract WHERE is_deleted = FALSE
GROUP BY contract_type ORDER BY count DESC
"""

ACTIVE_CONTRACTS = """
SELECT COUNT(*) as total FROM contract
WHERE status = 'approved' AND end_date >= CURRENT_DATE AND is_deleted = FALSE
"""

CONTRACTS_REVENUE = """
SELECT
    SUM(price) as total_revenue,
    AVG(price) as avg_price,
    COUNT(*) as count
FROM contract WHERE status = 'approved' AND is_deleted = FALSE
"""

# ==================== XABARLAR (NOTIFICATIONS) ====================

TOTAL_NOTIFICATIONS = """
SELECT COUNT(*) as total FROM notification WHERE is_deleted = FALSE
"""

NOTIFICATIONS_SENT = """
SELECT COUNT(*) as total FROM notification WHERE is_sent = TRUE AND is_deleted = FALSE
"""

NOTIFICATION_READ_RATE = """
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN is_read THEN 1 ELSE 0 END) as read_count,
    ROUND(100.0 * SUM(CASE WHEN is_read THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) as read_rate
FROM user_notification WHERE is_deleted = FALSE
"""

NOTIFICATIONS_TREND = """
SELECT DATE(sent_at) as date, COUNT(*) as count
FROM notification
WHERE is_sent = TRUE AND is_deleted = FALSE AND sent_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(sent_at)
ORDER BY date
"""

# ==================== SHARHLAR ====================

TOTAL_COMMENTS = """
SELECT COUNT(*) as total FROM comment WHERE is_deleted = FALSE
"""

COMMENTS_RATING_DISTRIBUTION = """
SELECT rating, COUNT(*) as count
FROM comment WHERE is_deleted = FALSE AND rating IS NOT NULL
GROUP BY rating ORDER BY rating
"""

AVERAGE_RATING = """
SELECT ROUND(AVG(rating)::numeric, 2) as avg_rating
FROM comment WHERE is_deleted = FALSE AND rating IS NOT NULL
"""
