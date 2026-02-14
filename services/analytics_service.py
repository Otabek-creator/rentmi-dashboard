import random
import pandas as pd
import json
from datetime import datetime, timedelta
import streamlit as st

class AnalyticsService:
    def __init__(self):
        self.use_mock = True
        self.property_id = None
        self.client = None
        
        # Check for secrets and library
        try:
            # 1. Try [google_analytics] with nested JSON (Old way)
            if "google_analytics" in st.secrets:
                self.property_id = st.secrets["google_analytics"].get("property_id")
                creds = st.secrets["google_analytics"].get("credentials_json")
                if creds:
                    if isinstance(creds, str):
                        self.creds_dict = json.loads(creds)
                    else:
                        self.creds_dict = creds

            # 2. Try [firebase] with flat structure (User's way)
            elif "firebase" in st.secrets:
                self.property_id = st.secrets["firebase"].get("property_id")
                # Use the whole section as credentials dict
                self.creds_dict = dict(st.secrets["firebase"])

            if self.property_id and hasattr(self, 'creds_dict'):
                # Try to import
                try:
                    from google.analytics.data_v1beta import BetaAnalyticsDataClient
                    from google.oauth2 import service_account
                    
                    credentials = service_account.Credentials.from_service_account_info(self.creds_dict)
                    self.client = BetaAnalyticsDataClient(credentials=credentials)
                    self.use_mock = False
                    # print("✅ GA4 Client initialized successfully!")
                except ImportError:
                    print("⚠️ google-analytics-data library not found. Using mock data.")
                except Exception as e:
                    print(f"⚠️ Error initializing GA4 client: {e}. Using mock data.")
        except Exception:
            # Secrets file might be missing or other env issues
            pass

    def get_dashboard_metrics(self, days=30):
        """
        Returns a dictionary with:
        - key_metrics: { dau, mau, sessions, avg_duration, bounce_rate, ... }
        - trends: DataFrame [date, active_users, sessions]
        - device_stats: DataFrame [device_category, sessions]
        - top_pages: DataFrame [page_path, views]
        """
        if self.use_mock:
            return self._generate_mock_data(days)
        else:
            try:
                return self._fetch_real_data(days)
            except Exception as e:
                print(f"❌ Error fetching GA4 data: {e}")
                return self._generate_mock_data(days)

    def _generate_mock_data(self, days):
        """Generates realistic demo data."""
        # 1. Key Metrics
        dau = random.randint(150, 300)
        mau = dau * random.randint(15, 25)  # Sticky factor ~20%
        sessions = mau * random.randint(3, 8)
        avg_duration = random.randint(120, 400) # seconds
        bounce_rate = random.uniform(25, 65)
        
        # 2. Daily Trend
        dates = [datetime.today() - timedelta(days=i) for i in range(days)]
        dates.sort()
        
        trend_data = []
        base_users = 150
        for d in dates:
            # Add some randomness and weekly seasonality
            day_factor = 1.2 if d.weekday() < 5 else 0.8
            users = int(base_users * day_factor * random.uniform(0.9, 1.3))
            base_users += random.randint(-2, 5) # Slow trend
            
            trend_data.append({
                'date': d.strftime("%Y-%m-%d"),
                'active_users': users,
                'sessions': int(users * random.uniform(1.1, 1.5))
            })
        
        # 3. Device Stats (Mock fallback, but preferably use REAL DB if available)
        # Note: app.py can overwrite this with real DB data if desired.
        device_data = {
            'Mobile': random.randint(60, 80),
            'Desktop': random.randint(15, 30),
            'Tablet': random.randint(1, 5)
        }
        
        # 4. Top Pages
        pages = [
            ('/', 'Bosh sahifa'),
            ('/search', 'Qidiruv'),
            ('/properties/view', 'Mulk ko\'rish'),
            ('/profile', 'Profil'),
            ('/login', 'Kirish'),
            ('requests', 'Arizalar')
        ]
        page_data = []
        total_views = sessions * 2
        for p, title in pages:
            views = int(total_views * random.uniform(0.05, 0.4))
            total_views -= views
            page_data.append({'pagePath': p, 'screenName': title, 'screenPageViews': views})
            
        page_data.sort(key=lambda x: x['screenPageViews'], reverse=True)

        return {
            "source": "demo",
            "key_metrics": {
                "dau": dau,
                "mau": mau,
                "sessions": sessions,
                "avg_session_duration": avg_duration,
                "bounce_rate": bounce_rate
            },
            "trends": pd.DataFrame(trend_data),
            "device_stats": pd.DataFrame(list(device_data.items()), columns=['deviceCategory', 'sessions']),
            "top_pages": pd.DataFrame(page_data)
        }

    def _fetch_real_data(self, days):
        """Fetches data from Google Analytics Data API."""
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions")
            ],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        )
        
        response = self.client.run_report(request)
        
        # Parse Trends
        trend_data = []
        total_users = 0
        total_sessions = 0
        
        for row in response.rows:
            date_str = row.dimension_values[0].value
            # GA4 returns YYYYMMDD
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            users = int(row.metric_values[0].value)
            sessions = int(row.metric_values[1].value)
            
            trend_data.append({
                'date': date_obj.strftime("%Y-%m-%d"),
                'active_users': users,
                'sessions': sessions
            })
            total_users += users
            total_sessions += sessions
            
        trend_df = pd.DataFrame(trend_data).sort_values('date')
        
        # Parse Totals (Approximation for simple dashboard)
        # For accurate DAU/MAU we need separate requests or aggregation
        # Here we simplify: activeUsers over 30 days is MAU.
        # Average of daily activeUsers is approx DAU.
        
        mau = total_users # Distinct users in date range (Actually sum of daily is WRONG for unique users. Need separate request for 30 day metric.)
        # GA4 metric "activeUsers" with date dimension is DAILY active users.
        # If we remove date dimension, we get Total Active Users (MAU).
        
        # Request 2: Overview Metrics
        req_overview = RunReportRequest(
            property=f"properties/{self.property_id}",
            metrics=[
                Metric(name="activeUsers"), # MAU
                Metric(name="sessions"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="dauPerMau") # Engagement rate? No, user engagement. dau/mau is manual calc usually.
            ],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")]
        )
        resp_overview = self.client.run_report(req_overview)
        
        overview_row = resp_overview.rows[0] if resp_overview.rows else None
        
        key_metrics = {
            "dau": int(trend_df['active_users'].mean()) if not trend_df.empty else 0, # Avg DAU
            "mau": int(overview_row.metric_values[0].value) if overview_row else 0,
            "sessions": int(overview_row.metric_values[1].value) if overview_row else 0,
            "avg_session_duration": float(overview_row.metric_values[2].value) if overview_row else 0,
            "bounce_rate": float(overview_row.metric_values[3].value) * 100 if overview_row else 0
        }

        # Request 3: Device Categories
        req_device = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="deviceCategory")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")]
        )
        resp_device = self.client.run_report(req_device)
        device_data = []
        for row in resp_device.rows:
            device_data.append({
                'deviceCategory': row.dimension_values[0].value,
                'sessions': int(row.metric_values[0].value)
            })
            
        # Request 4: Top Pages
        req_pages = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle") # screenName equivalent
            ],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
            limit=10
        )
        resp_pages = self.client.run_report(req_pages)
        page_data = []
        for row in resp_pages.rows:
            page_data.append({
                'pagePath': row.dimension_values[0].value,
                'screenName': row.dimension_values[1].value,
                'screenPageViews': int(row.metric_values[0].value)
            })

        return {
            "source": "ga4",
            "key_metrics": key_metrics,
            "trends": trend_df,
            "device_stats": pd.DataFrame(device_data),
            "top_pages": pd.DataFrame(page_data)
        }

