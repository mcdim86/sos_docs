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

def get_shifts_by_specialty(df, specialty):
    df["Ημ/νία Έναρξης"] = pd.to_datetime(df["Ημ/νία Έναρξης"])
    df["Ημερομηνία Λήξης"] = pd.to_datetime(df["Ημερομηνία Λήξης"])

    if specialty and specialty != "Όλες οι ειδικότητες":
        df = df[df["Ειδικότητα"] == specialty]

    return df[["Όνομα πόρου", "Ειδικότητα", "Ημ/νία Έναρξης", "Ημερομηνία Λήξης"]].sort_values(by=["Ημ/νία Έναρξης"])

def get_doctors_now(df):
    now = datetime.now()

    df = df.copy()
    df = df.dropna(subset=["Ημ/νία Έναρξης", "Ημερομηνία Λήξης"])

    df["Ημ/νία Έναρξης"] = pd.to_datetime(df["Ημ/νία Έναρξης"], errors="coerce")
    df["Ημερομηνία Λήξης"] = pd.to_datetime(df["Ημερομηνία Λήξης"], errors="coerce")

    df = df.dropna(subset=["Ημ/νία Έναρξης", "Ημερομηνία Λήξης"])

    current = df[(df["Ημ/νία Έναρξης"] <= now) & (df["Ημερομηνία Λήξης"] >= now)]

    return current[["Όνομα πόρου", "Ειδικότητα", "Ημ/νία Έναρξης", "Ημερομηνία Λήξης"]].sort_values(by=["Ειδικότητα", "Ημ/νία Έναρξης"])
 st.write("Τώρα:", now)
st.write(df[["Όνομα πόρου", "Ημ/νία Έναρξης", "Ημερομηνία Λήξης"]].head())

if uploaded_file:
    try:
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        df = pd.read_excel(uploaded_file, sheet_name=sheet_names[0])

        tab1, tab2, tab3 = st.tabs(["Έλεγχος Βάρδιας", "Εφημερίες ανά Ειδικότητα", "Ποιοι είναι τώρα σε βάρδια"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_date = st.date_input("Επίλεξε Ημερομηνία", datetime.today())
            with col2:
                start_hour = st.time_input("Ώρα Έναρξης Βάρδιας", value=time(7, 0))
            with col3:
                end_hour = st.time_input("Ώρα Λήξης Βάρδιας", value=time(15, 0))

            specialties = ["Όλες οι ειδικότητες"] + sorted(df["Ειδικότητα"].dropna().unique())
            selected_specialty = st.selectbox("Επίλεξε Ειδικότητα", specialties, key="spec1")

            if st.button("Εμφάνιση Διαθέσιμων Ιατρών"):
                result = filter_doctors(df, selected_date, start_hour, end_hour, selected_specialty)
                st.success(f"Βρέθηκαν {len(result)} διαθέσιμοι ιατροί.")
                st.dataframe(result, use_container_width=True)

        with tab2:
            specialties = sorted(df["Ειδικότητα"].dropna().unique())
            selected_specialty2 = st.selectbox("Ειδικότητα για εμφάνιση εφημεριών", specialties, key="spec2")
            if st.button("Εμφάνιση Εφημεριών"):
                result = get_shifts_by_specialty(df, selected_specialty2)
                st.success(f"Βρέθηκαν {len(result)} βάρδιες για την ειδικότητα {selected_specialty2}.")
                st.dataframe(result, use_container_width=True)

        with tab3:
            if st.button("Ποιοι είναι τώρα σε βάρδια;"):
                result = get_doctors_now(df)
                st.success(f"Αυτή τη στιγμή είναι σε βάρδια {len(result)} ιατροί.")
                st.dataframe(result, use_container_width=True)

    except Exception as e:
        st.error(f"Σφάλμα κατά την επεξεργασία του αρχείου: {e}")
