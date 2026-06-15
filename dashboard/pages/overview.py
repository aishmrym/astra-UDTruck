# dashboard/pages/overview.py
import streamlit as st
import duckdb
import pandas as pd

DB_PATH = "data/final/warehouse.duckdb"

st.title("📋 Overview Dataset")

con = duckdb.connect(DB_PATH, read_only=True)

total    = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
cats     = con.execute("SELECT COUNT(DISTINCT category) FROM chunks").fetchone()[0]
subcats  = con.execute("SELECT COUNT(DISTINCT sub_category) FROM chunks").fetchone()[0]
faults   = con.execute("SELECT COUNT(*) FROM chunks WHERE fault_code IS NOT NULL").fetchone()[0]
avg_tok  = con.execute("SELECT ROUND(AVG(token_est),1) FROM chunks").fetchone()[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Chunks", total)
col2.metric("Kategori", cats)
col3.metric("Sub-Kategori", subcats)
col4.metric("Chunk dengan Fault Code", faults)
col5.metric("Rata-rata Token", avg_tok)

st.divider()
st.subheader("Distribusi Kategori")
df_cat = con.execute("SELECT * FROM v_category_dist").df()
st.bar_chart(df_cat.set_index("category")["total_chunks"])

st.subheader("Ringkasan per Chapter")
df_chap = con.execute("SELECT * FROM v_chapter_summary").df()
st.dataframe(df_chap, use_container_width=True)

con.close()