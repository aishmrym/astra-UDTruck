# pipeline/modelling/build_storage.py
"""
Bangun storage DuckDB dari chunks_df.csv (hasil preprocessing).
Tabel: chunks (satu tabel utama, tidak perlu star schema karena data sudah flat)
"""

import duckdb
import pandas as pd
from pathlib import Path

CLEAN_CSV  = Path("data/clean/chunks_df.csv")
DB_PATH    = Path("data/final/warehouse.duckdb")

def build_storage():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Load data bersih...")
    df = pd.read_csv(CLEAN_CSV)
    print(f"   {len(df)} chunk dimuat.")

    print("🔄 Simpan ke DuckDB...")
    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS chunks")
    con.execute("""
        CREATE TABLE chunks AS SELECT * FROM df
    """)

    # Verifikasi
    count = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    cats  = con.execute("SELECT DISTINCT category FROM chunks").fetchall()
    print(f"   ✅ {count} baris tersimpan di tabel 'chunks'")
    print(f"   Kategori: {[c[0] for c in cats]}")
    con.close()
    print(f"   💾 Database: {DB_PATH}")

if __name__ == "__main__":
    build_storage()