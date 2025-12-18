import streamlit as st
from supabase import create_client, Client
import pandas as pd
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Daniel's Health OS",
    page_icon="🩺",
    layout="wide"
)

# --- 2. DATABASE CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("⚠️ Connection Error: Could not find Supabase keys. Please check your Streamlit Secrets.")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🩺 Daniel's Health OS")
    st.markdown("---")
    page = st.radio("Navigate", ["📝 Daily Log", "🩸 Lab Results", "📊 Dashboard"])
    
    st.markdown("---")
    st.caption(f"📅 Today: {datetime.date.today().strftime('%d %b %Y')}")
    st.caption("📍 Kingston, TAS")

# --- 4. PAGE: DAILY LOG (The Dynamic Form) ---
if page == "📝 Daily Log":
    st.header("Daily Data Entry")
    
    # A. Date Selection (Crucial for historic back-filling)
    col_date, col_select = st.columns([1, 2])
    with col_date:
        entry_date = st.date_input("Date of Entry", datetime.date.today())
    
    # B. The Metric Selector (This controls what inputs appear)
    with col_select:
        data_sources = st.multiselect(
            "Select data to log today:",
            options=["⚖️ Scale (Renpho)", "⌚ Watch (Garmin)", "🧠 Symptoms & Notes"],
            default=["⚖️ Scale (Renpho)", "🧠 Symptoms & Notes"]
        )

    st.markdown("---")

    # C. The Form
    with st.form("dynamic_log_form"):
        # Initialize variables as None (so we know if they were skipped)
        weight = body_fat = muscle = visceral = bone = water = protein = bmr = metabolic_age = None
        sleep_score = resting_hr = body_battery_high = body_battery_low = steps = None
        cal_active = cal_resting = None
        gout_pain = anxiety = notes = None

        # --- SECTION 1: SCALE ---
        if "⚖️ Scale (Renpho)" in data_sources:
            st.subheader("⚖️ Renpho Scale Metrics")
            c1, c2, c3 = st.columns(3)
            with c1:
                weight = st.number_input("Weight (kg)", 0.0, 300.0, step=0.1, format="%.2f")
                body_fat = st.number_input("Body Fat (%)", 0.0, 100.0, step=0.1)
                visceral = st.number_input("Visceral Fat", 0, 50)
            with c2:
                muscle = st.number_input("Muscle Mass (kg)", 0.0, 200.0, step=0.1)
                bone = st.number_input("Bone Mass (kg)", 0.0, 20.0, step=0.1)
                water = st.number_input("Body Water (kg)", 0.0, 200.0, step=0.1)
            with c3:
                metabolic_age = st.number_input("Metabolic Age", 0, 120)
                protein = st.number_input("Protein (kg)", 0.0, 50.0, step=0.1)
                bmr = st.number_input("BMR (kcal)", 0, 5000)

        # --- SECTION 2: WATCH ---
        if "⌚ Watch (Garmin)" in data_sources:
            st.markdown("---")
            st.subheader("⌚ Garmin Stats")
            g1, g2, g3 = st.columns(3)
            with g1:
                sleep_score = st.number_input("Sleep Score (0-100)", 0, 100)
                resting_hr = st.number_input("Resting HR", 0, 200)
                steps = st.number_input("Steps", 0, 50000)
            with g2:
                body_battery_high = st.number_input("Body Battery (High)", 0, 100)
                body_battery_low = st.number_input("Body Battery (Low)", 0, 100)
            with g3:
                cal_active = st.number_input("Active Calories", 0, 5000)
                cal_resting = st.number_input("Resting Calories", 0, 3000)

        # --- SECTION 3: SYMPTOMS ---
        if "🧠 Symptoms & Notes" in data_sources:
            st.markdown("---")
            st.subheader("🧠 Health & Conditions")
            s1, s2 = st.columns(2)
            with s1:
                gout_pain = st.slider("🔥 Gout Pain (0=None, 10=Severe)", 0, 10, 0)
                anxiety = st.slider("😰 Anxiety Level (0=Calm, 10=Panic)", 0, 10, 0)
            with s2:
                notes = st.text_area("📝 Notes (Triggers, Meds, Mood)")

        # ---