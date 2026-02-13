import os
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric
    )
    from google.oauth2 import service_account
except ImportError:
    BetaAnalyticsDataClient = None


def get_analytics_client():
    """Google Analytics klayentini yaratish"""
    # 1. Streamlit Secrets dan olish
    if "firebase" in st.secrets:
        creds_dict = dict(st.secrets["firebase"])
        return BetaAnalyticsDataClient.from_service_account_info(creds_dict)
    
    # 2. Local Fayldan olish (fallback)
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
    if os.path.exists(cred_path):
        return BetaAnalyticsDataClient.from_service_account_json(cred_path)
        
    return None

def get_ga4_data(property_id, days=30):
    """
    Real GA4 ma'lumotlarini olish.
    Agar ulanish bo'lmasa, None qaytaradi.
    """
    if not BetaAnalyticsDataClient:
        return None
        
    try:
        client = get_analytics_client()
        if not client:
            return None

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="screenPageViews"),
                Metric(name="userEngagementDuration"),
            ],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        )
        response = client.run_report(request)

        data = []
        for row in response.rows:
            data.append({
                "date": row.dimension_values[0].value,
                "users": int(row.metric_values[0].value),
                "views": int(row.metric_values[1].value),
                "duration": float(row.metric_values[2].value),
            })
            
        df = pd.DataFrame(data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
            df = df.sort_values("date")
            
        return df

    except Exception as e:
        print(f"⚠️ GA4 Error: {e}")
        return None


def get_top_pages(property_id):
    """Eng ko'p ko'rilgan sahifalar (Screen Name)"""
    if not BetaAnalyticsDataClient:
        return None
        
    try:
        client = get_analytics_client()
        if not client:
            return None

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="unifiedScreenName")], # Yoki pageTitle
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
            limit=10
        )
        response = client.run_report(request)

        data = []
        for row in response.rows:
            data.append({
                "page": row.dimension_values[0].value,
                "views": int(row.metric_values[0].value),
            })
            
        return pd.DataFrame(data)
    except Exception as e:
        print(f"⚠️ GA4 Pages Error: {e}")
        return None


def get_demo_analytics_data(days=30):
    """
    DEMO rejim uchun soxta ma'lumotlar.
    PM ga ko'rsatish uchun ideal.
    """
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    while current_date <= end_date:
        users = random.randint(100, 500)
        # O'rtacha 5-15 daqiqa (sekundlarda)
        duration = users * random.uniform(300, 900) 
        
        data.append({
            "date": current_date,
            "users": users,
            "views": users * random.randint(2, 8),
            "duration": duration
        })
        current_date += timedelta(days=1)
        
    return pd.DataFrame(data)

def get_demo_top_pages():
    """DEMO top sahifalar"""
    pages = [
        "Home Screen", "Search Results", "Property Details", 
        "User Profile", "Chat List", "Map View", 
        "Notifications", "Settings", "Login", "Register"
    ]
    data = []
    for page in pages:
        data.append({
            "page": page,
            "views": random.randint(1000, 50000)
        })
    return pd.DataFrame(data).sort_values("views", ascending=False)
