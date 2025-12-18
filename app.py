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
    
    # A. Date Selection
    col_date, col_select = st.columns([1, 2])
    with col_date:
        entry_date = st.date_input("Date of Entry", datetime.date.today())
    
    # B. The Metric Selector
    with col_select:
        data_sources = st.multiselect(
            "Select data to log today:",
            options=["⚖️ Scale (Renpho)", "⌚ Watch (Garmin)", "🧠 Symptoms & Notes"],
            default=["⚖️ Scale (Renpho)", "🧠 Symptoms & Notes"]
        )

    st.markdown("---")

    # C. The Form
    with st.form("dynamic_log_form"):
        # Initialize variables as None
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

        # --- SUBMIT BUTTON (CRITICAL: Must be aligned with the IF statements, NOT inside them) ---
        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Selected Data", type="primary")

        if submitted:
            # 1. Build the "Daily Logs" Payload
            daily_payload = {"date": str(entry_date)}
            
            if "⚖️ Scale (Renpho)" in data_sources and weight > 0:
                daily_payload["weight_kg"] = weight
            
            if "🧠 Symptoms & Notes" in data_sources:
                daily_payload["gout_pain_level"] = gout_pain
                daily_payload["stress_level"] = anxiety
                if notes: daily_payload["notes"] = notes
                if sleep_score and sleep_score > 0: daily_payload["sleep_score"] = sleep_score

            # 2. Build the "Biometrics" Payload
            bio_payload = {"date": str(entry_date)}
            
            if "⚖️ Scale (Renpho)" in data_sources:
                if body_fat > 0: bio_payload["body_fat_percent"] = body_fat
                if muscle > 0: bio_payload["muscle_mass_kg"] = muscle
                if visceral > 0: bio_payload["visceral_fat"] = visceral
                if bone > 0: bio_payload["bone_mass_kg"] = bone
                if water > 0: bio_payload["water_kg"] = water
                if metabolic_age > 0: bio_payload["metabolic_age"] = metabolic_age
                if protein > 0: bio_payload["protein_kg"] = protein
                if bmr > 0: bio_payload["bmr"] = bmr

            if "⌚ Watch (Garmin)" in data_sources:
                if resting_hr > 0: bio_payload["resting_hr"] = resting_hr
                if steps > 0: bio_payload["steps"] = steps
                if body_battery_high > 0: bio_payload["body_battery_high"] = body_battery_high
                if body_battery_low > 0: bio_payload["body_battery_low"] = body_battery_low
                if cal_active > 0: bio_payload["calories_active"] = cal_active
                if cal_resting > 0: bio_payload["calories_resting"] = cal_resting

            try:
                # Upsert Daily Log
                if len(daily_payload) > 1:
                    supabase.table("daily_logs").upsert(daily_payload).execute()
                
                # Upsert Biometrics
                if len(bio_payload) > 1:
                    supabase.table("biometrics").upsert(bio_payload).execute()

                st.success(f"✅ Data saved for {entry_date.strftime('%d %B')}!")
                
            except Exception as e:
                st.error(f"Error saving to database: {e}")