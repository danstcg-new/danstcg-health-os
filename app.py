import streamlit as st
from supabase import create_client, Client
import pandas as pd
import datetime

# 1. Setup Page Configuration
st.set_page_config(page_title="Dan's Health OS", page_icon="🩺", layout="wide")

# 2. Setup Supabase Connection
# Uses st.secrets which works on Cloud and Local
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error connecting to Database. Check your API Keys.")
    st.stop()

st.title("🩺 Daniel's Health Operating System")

# 3. The Sidebar (Navigation & Quick Actions)
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Daily Log", "Data View", "Settings"])

    st.divider()
    st.info(f"📅 Today: {datetime.date.today()}")

# 4. Page: Daily Log
if page == "Daily Log":
    st.subheader("📝 Daily Metrics Entry")

    with st.form("daily_entry_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", datetime.date.today())
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, format="%.2f")
            sleep_score = st.number_input("Sleep Score (Garmin)", 0, 100)

        with col2:
            gout_pain = st.slider("Gout Pain Level (1-10)", 0, 10, 0)
            stress = st.slider("Overall Stress Level", 0, 100)
            notes = st.text_area("Daily Notes / Symptoms")

        submitted = st.form_submit_button("💾 Save Entry")

        if submitted:
            # Prepare data for Supabase
            data = {
                "date": str(date),
                "weight_kg": weight,
                "sleep_score": sleep_score,
                "stress_level": stress,
                "gout_pain_level": gout_pain,
                "notes": notes
            }

            try:
                # Upsert handles both 'Insert' and 'Update' if date exists
                supabase.table("daily_logs").upsert(data).execute()
                st.success(f"✅ Data saved for {date}!")
            except Exception as e:
                st.error(f"Error saving data: {e}")

# 5. Page: Data View
elif page == "Data View":
    st.subheader("📊 Recent History")

    # Fetch data from Supabase
    try:
        response = supabase.table("daily_logs").select("*").order("date", desc=True).execute()
        df = pd.DataFrame(response.data)

        if not df.empty:
            # Show key metrics at top
            latest = df.iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Latest Weight", f"{latest['weight_kg']} kg")
            m2.metric("Sleep Score", f"{latest['sleep_score']}")
            m3.metric("Gout Pain", f"{latest['gout_pain_level']}/10")

            # Show the full table
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found. Go to 'Daily Log' to add your first entry!")

    except Exception as e:
        st.error(f"Could not load data: {e}")

elif page == "Settings":
    st.write("Settings and reference data will go here.")