# dashboard/pages/keyword_faultcode.py
import streamlit as st
import duckdb
import pandas as pd
from collections import Counter

DB_PATH = "data/final/warehouse.duckdb"

st.title("🔍 Keyword & Fault Code")
con = duckdb.connect(DB_PATH, read_only=True)

# Fault codes
st.subheader("Chunk dengan Fault Code")
df_fault = con.execute("SELECT * FROM v_fault_codes").df()
st.dataframe(df_fault, use_container_width=True)

# Top keywords
st.subheader("Top 20 Keywords")
df_all = con.execute("SELECT keywords FROM chunks").df()
all_kw = []
for kw_str in df_all["keywords"]:
    all_kw.extend([k.strip() for k in str(kw_str).split(",")])
top_kw = pd.DataFrame(Counter(all_kw).most_common(20), columns=["keyword", "frekuensi"])
st.bar_chart(top_kw.set_index("keyword")["frekuensi"])

con.close()