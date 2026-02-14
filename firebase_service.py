"""
firebase_service.py — Firebase Admin SDK orqali ma'lumot olish (Optimized)

✅ @st.cache_resource — Firebase bir marta initializatsiya qilinadi
"""

import os
import firebase_admin
from firebase_admin import credentials
import streamlit as st

from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_CREDENTIALS


@st.cache_resource
def initialize_firebase():
    """Firebase Admin SDK ni ishga tushirish (cached)"""
    if firebase_admin._apps:
        return firebase_admin.get_app()

    try:
        if FIREBASE_CREDENTIALS:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            app = firebase_admin.initialize_app(cred)
            print(f"✅ Firebase initialized (from secrets): {app.project_id}")
            return app
        else:
            cred_path = os.path.abspath(FIREBASE_CREDENTIALS_PATH)
            if not os.path.exists(cred_path):
                print(f"⚠️  Firebase credentials topilmadi: {cred_path}")
                return None

            cred = credentials.Certificate(cred_path)
            app = firebase_admin.initialize_app(cred)
            print(f"✅ Firebase initialized (from file): {app.project_id}")
            return app

    except Exception as e:
        print(f"❌ Firebase init error: {e}")
        return None


@st.cache_data(ttl=600)
def get_firebase_project_info():
    """Firebase loyiha ma'lumotlari (10 daqiqa cached)"""
    app = initialize_firebase()
    if not app:
        return {
            "project_id": "N/A",
            "status": "❌ Ulanmagan",
        }

    return {
        "project_id": app.project_id,
        "status": "✅ Ulangan",
    }


def get_firebase_summary():
    """
    Firebase bo'yicha umumiy ma'lumotlar.

    Eslatma: Firebase Analytics (GA4) real-time API cheklangandir.
    Google Analytics Data API orqali olish mumkin, lekin buning uchun
    GA4 property ID kerak.

    Hozircha faqat loyiha holati va FCM ma'lumotlarini ko'rsatamiz.
    """
    info = get_firebase_project_info()

    return {
        "project_id": info["project_id"],
        "connection_status": info["status"],
        "note": (
            "Firebase Analytics ma'lumotlari Google Analytics 4 orqali "
            "BigQuery ga eksport qilinadi. Real-time statistika uchun "
            "Firebase Console dan foydalaning."
        ),
        "firebase_console_url": (
            f"https://console.firebase.google.com/project/{info['project_id']}/analytics"
            if info["project_id"] != "N/A" else None
        ),
    }
