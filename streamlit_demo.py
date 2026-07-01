"""Optional Streamlit demo for MediGraph AI."""

import streamlit as st

st.set_page_config(page_title="MediGraph AI Demo", page_icon="🏥", layout="wide")

st.title("MediGraph AI - Clinical Orientation Demo")
st.warning("This system does not replace a professional medical consultation.")

st.markdown("""
## Educational Multi-Agent Clinical Orientation System

This Streamlit demo provides a simplified interface to the MediGraph AI platform.

For the full experience, use the React frontend or FastAPI directly.
""")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Page", ["Patient Registration", "Questionnaire", "Report"])

if page == "Patient Registration":
    st.header("Patient Registration")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=150)
    gender = st.selectbox("Gender", ["male", "female", "other"])
    history = st.text_area("Medical History")
    complaint = st.text_area("Chief Complaint")

    if st.button("Register"):
        st.success(f"Patient {name} registered (demo mode)")

elif page == "Questionnaire":
    st.header("Diagnostic Questionnaire")
    st.progress(0.4, text="Question 2 of 5")
    st.subheader("When did the symptoms begin?")
    answer = st.text_area("Your answer")
    if st.button("Submit Answer"):
        st.info("Answer submitted (demo mode)")

elif page == "Report":
    st.header("Clinical Orientation Report")
    st.markdown("**Disclaimer:** This system does not replace a professional medical consultation.")
    st.json({"status": "demo", "message": "Connect to FastAPI for full reports"})
