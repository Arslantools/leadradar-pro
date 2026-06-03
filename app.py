import streamlit as st
import pandas as pd
import datetime

st.set_page_config(
    page_title="LeadRadar Pro",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 LeadRadar Pro")
st.markdown("### Lead Management & Tracking System")

if 'leads' not in st.session_state:
    st.session_state.leads = []

with st.sidebar:
    st.header("➕ Add New Lead")
    name = st.text_input("Lead Name")
    company = st.text_input("Company")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    status = st.selectbox("Status", ["New", "Contacted", "Qualified", "Proposal", "Closed Won", "Closed Lost"])
    value = st.number_input("Deal Value (PKR)", min_value=0, step=1000)
    notes = st.text_area("Notes")
    if st.button("Add Lead", type="primary"):
        if name:
            lead = {"id": len(st.session_state.leads)+1, "name": name, "company": company, "email": email, "phone": phone, "status": status, "value": value, "notes": notes, "date": str(datetime.date.today())}
            st.session_state.leads.append(lead)
            st.success(f"Lead added!")
        else:
            st.error("Enter lead name")

col1, col2, col3, col4 = st.columns(4)
total_leads = len(st.session_state.leads)
total_value = sum(l["value"] for l in st.session_state.leads)
won_leads = len([l for l in st.session_state.leads if l["status"] == "Closed Won"])
active_leads = len([l for l in st.session_state.leads if l["status"] not in ["Closed Won", "Closed Lost"]])
with col1:
    st.metric("Total Leads", total_leads)
with col2:
    st.metric("Active Leads", active_leads)
with col3:
    st.metric("Won Deals", won_leads)
with col4:
    st.metric("Total Value", f"PKR {total_value:,}")

st.divider()

if st.session_state.leads:
    st.subheader("📋 All Leads")
    filter_status = st.selectbox("Filter by Status", ["All", "New", "Contacted", "Qualified", "Proposal", "Closed Won", "Closed Lost"])
    filtered_leads = st.session_state.leads if filter_status == "All" else [l for l in st.session_state.leads if l["status"] == filter_status]
    df = pd.DataFrame(filtered_leads)
    st.dataframe(df, use_container_width=True)
    st.subheader("📊 Pipeline Status")
    status_counts = df["status"].value_counts()
    st.bar_chart(status_counts)
else:
    st.info("No leads yet. Add your first lead from the sidebar!")
