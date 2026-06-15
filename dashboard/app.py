# dashboard/app.py
import streamlit as st

st.set_page_config(
    page_title="UD Trucks CD Series — Knowledge Base",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 UD Trucks CD Series — Manual Knowledge Base")
st.markdown("""
Dashboard analisis dataset manual UD Trucks CD Series.  
Gunakan menu di sidebar untuk navigasi antar halaman.
""")

st.info("Pilih halaman di sidebar kiri untuk mulai eksplorasi data.")
