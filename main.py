# main.py - LeadRadar Pro Entry Point
import streamlit as st
import json
import os
import requests
import pandas as pd

USER_FILE = "users.json"

# Users ka data load aur save karne ke functions
def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.file_dump(users, f, indent=4)

users_db = load_users()

# Session State Initialize karna
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Sidebar Auth Navigation
st.sidebar.title("🔐 Account Access")
auth_mode = st.sidebar.radio("Option Chunein:", ["Login", "Register", "Reset Password"])

# --- REGISTER FLOW ---
if auth_mode == "Register":
    st.title("📝 Naya Account Banayein")
    new_user = st.text_input("Username chunein:")
    new_pass = st.text_input("Password dalein:", type="password")
    confirm_pass = st.text_input("Password dobara dalein:", type="password")
    
    if st.button("Register"):
        if not new_user or not new_pass:
            st.error("Username aur Password khali nahi ho sakta!")
        elif new_user in users_db:
            st.error("Yeh username pehle se mojood hy!")
        elif new_pass != confirm_pass:
            st.error("Dono password match nahi ho rahe!")
        else:
            users_db[new_user] = new_pass
            save_users(users_db)
            st.success("Account kamyabi se ban gaya! Ab sidebar se Login karein.")

# --- RESET PASSWORD FLOW ---
elif auth_mode == "Reset Password":
    st.title("🔄 Password Reset Karein")
    user_to_reset = st.text_input("Apna Username dalein:")
    new_secret_pass = st.text_input("Naya Password dalein:", type="password")
    
    if st.button("Update Password"):
        if user_to_reset in users_db:
            users_db[user_to_reset] = new_secret_pass
            save_users(users_db)
            st.success("Password kamyabi se update ho gaya!")
        else:
            st.error("Username nahi mila!")

# --- LOGIN FLOW ---
elif auth_mode == "Login":
    if not st.session_state.logged_in:
        st.title("🔑 LeadRadar Pro Login")
        login_user = st.text_input("Username:")
        login_pass = st.text_input("Password:", type="password")
        
        if st.button("Sign In"):
            if login_user in users_db and users_db[login_user] == login_pass:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.error("Galt Username ya Password!")
    else:
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        # --- MAIN APP LOGIC (Aapka Asli Lead Extraction Tool) ---
        st.title("🎯 LeadRadar Pro — Smart B2B Lead Extractor")
        
        niche = st.text_input("Niche (e.g., Digital Marketing Agency)", placeholder="Dentist, Real Estate...")
        location = st.text_input("Location (e.g., London)", placeholder="New York, Dubai...")
        serp_key = st.text_input("SerpAPI Key (Private)", type="password")
        
        if st.button("Start Scraping Leads 🚀"):
            if not niche or not location or not serp_key:
                st.warning("Meharbani karke saari fields fill karein!")
            else:
                with st.spinner("Leads extract ho rahi hain..."):
                    try:
                        # FastAPI Backend Call
                        res = requests.get(
                            f"http://127.0.0.1:8000/scrape", 
                            params={"niche": niche, "location": location, "api_key": serp_key}
                        )
                        if res.status_code == 200:
                            data_json = res.json()
                            leads = data_json.get("data", [])
                            if leads:
                                df = pd.DataFrame(leads)
                                st.success(f"Mubarak ho! {len(df)} Leads mil gayeen.")
                                st.dataframe(df)
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button("Download Data (CSV)", csv, "leads.csv", "text/csv")
                            else:
                                st.info("Koi lead nahi mili, search criteria badlein.")
                        else:
                            st.error(f"Backend Error: {res.text}")
                    except Exception as e:
                        st.error(f"Connection fail: Pehle uvicorn server start karein! ({str(e)})")
