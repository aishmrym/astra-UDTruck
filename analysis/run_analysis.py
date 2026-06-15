# analysis/run_analysis.py
"""
Buat analytical views di warehouse.duckdb.
Views ini yang akan dipanggil oleh dashboard Streamlit.
"""

import duckdb
from pathlib import Path

DB_PATH = Path("data/final/warehouse.duckdb")

VIEWS = {
    # Distribusi per kategori
    "v_category_dist": """
        SELECT category, COUNT(*) as total_chunks
        FROM chunks
        GROUP BY category
        ORDER BY total_chunks DESC
    """,
    # Distribusi per sub-kategori
    "v_subcategory_dist": """
        SELECT category, sub_category, COUNT(*) as total_chunks
        FROM chunks
        GROUP BY category, sub_category
        ORDER BY category, total_chunks DESC
    """,
    # Chunk dengan fault_code (tidak null)
    "v_fault_codes": """
        SELECT fault_code, sub_category, chapter, page, token_est
        FROM chunks
        WHERE fault_code IS NOT NULL
        ORDER BY fault_code
    """,
    # Distribusi token (panjang teks)
    "v_token_dist": """
        SELECT 
            CASE 
                WHEN token_est < 100 THEN 'pendek (<100)'
                WHEN token_est < 300 THEN 'sedang (100-299)'
                ELSE 'panjang (≥300)'
            END as kelompok,
            COUNT(*) as jumlah
        FROM chunks
        GROUP BY kelompok
    """,
    # Top keywords (perlu unpack dari string)
    "v_chapter_summary": """
        SELECT chapter, COUNT(*) as total_chunks, AVG(token_est) as avg_token
        FROM chunks
        GROUP BY chapter
        ORDER BY total_chunks DESC
    """,
}

def run_analysis():
    con = duckdb.connect(str(DB_PATH))
    print("🔄 Membuat analytical views...")
    
    for name, query in VIEWS.items():
        con.execute(f"DROP VIEW IF EXISTS {name}")
        con.execute(f"CREATE VIEW {name} AS {query}")
        count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"   ✅ {name} → {count} baris")

    con.close()
    print("\nSemua views siap. Dashboard bisa dipanggil.")

if __name__ == "__main__":
    run_analysis()