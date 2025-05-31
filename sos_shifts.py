import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Διαθέσιμοι Ιατροί", layout="wide")
st.title("Έλεγχος Διαθεσιμότητας Ιατρών")

uploaded_file = st.file_uploader("Ανέβασε αρχείο Excel", type=["xlsx"])

def filter_doctors(df, date, start_time, end_time, specialty=None):
    df["Ημ/νία Έναρξης"] = pd.to_datetime(df["Ημ/νία Έναρξης"])
    df["Ημερομηνία Λήξης"] = pd.to_datetime(df["Ημερομηνία Λήξης"])

    shift_start = datetime.combine(date, start_time)
    shift_end = datetime.combine(date, end_time)

    available = df[(df["Ημ/νία Έναρξης"] <= shift_end) & (df["Ημερομηνία Λήξης"] >= shift_start)]

    if specialty and specialty != "Όλες οι ειδικότητες":
        available = available[available["Ειδικότητα"] == specialty]

    return available[["Όνομα πόρου", "Ειδικότητα", "Ημ/νία Έναρξης", "Ημερομηνία Λήξης"]].sort_values(by=["Ειδικότητα", "Ημ/νία Έναρξης"])

if uploaded_file:
    try:
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        df = pd.read_excel(uploaded_file, sheet_name=sheet_names[0])

        col1, col2, col3 = st.columns(3)
        with col1:
            selected_date = st.date_input("Επίλεξε Ημερομηνία", datetime.today())
        with col2:
            start_hour = st.time_input("Ώρα Έναρξης Βάρδιας", value=time(7, 0))
        with col3:
            end_hour = st.time_input("Ώρα Λήξης Βάρδιας", value=time(15, 0))

        specialties = ["Όλες οι ειδικότητες"] + sorted(df["Ειδικότητα"].dropna().unique())
        selected_specialty = st.selectbox("Επίλεξε Ειδικότητα", specialties)

        if st.button("Εμφάνιση Διαθέσιμων Ιατρών"):
            result = filter_doctors(df, selected_date, start_hour, end_hour, selected_specialty)
            st.success(f"Βρέθηκαν {len(result)} διαθέσιμοι ιατροί.")
            st.dataframe(result, use_container_width=True)

    except Exception as e:
        st.error(f"Σφάλμα κατά την επεξεργασία του αρχείου: {e}")
