# dashboard/pages/category_analysis.py
import streamlit as st
import duckdb
import pandas as pd

DB_PATH = "data/final/warehouse.duckdb"

st.title("📂 Analisis Kategori & Sub-Kategori")
con = duckdb.connect(DB_PATH, read_only=True)

df = con.execute("SELECT * FROM v_subcategory_dist").df()

kategori = st.selectbox("Pilih Kategori", ["Semua"] + df["category"].unique().tolist())
if kategori != "Semua":
    df = df[df["category"] == kategori]

st.bar_chart(df.set_index("sub_category")["total_chunks"])
st.dataframe(df, use_container_width=True)
con.close()