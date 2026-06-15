# analysis/run_analysis.py
import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/final/warehouse.duckdb")

pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 120)
pd.set_option("display.max_colwidth", 30)

VIEWS = {
    "v_category_dist": (
        """
        SELECT category, COUNT(*) as total_chunks
        FROM chunks
        GROUP BY category
        ORDER BY total_chunks DESC
        """,
        "Distribusi jumlah chunk per kategori. Kategori maintenance dan product mendominasi "
        "karena manual UD Trucks banyak membahas prosedur perawatan dan spesifikasi produk."
    ),
    "v_subcategory_dist": (
        """
        SELECT category, sub_category, COUNT(*) as total_chunks
        FROM chunks
        GROUP BY category, sub_category
        ORDER BY category, total_chunks DESC
        """,
        "Rincian sub-kategori dalam setiap kategori. Memperlihatkan topik mana yang paling "
        "banyak dibahas di dalam manual, seperti warning indicators dan prosedur servis."
    ),
    "v_token_dist": (
        """
        SELECT 
            CASE 
                WHEN token_est < 100 THEN 'pendek (<100 token)'
                WHEN token_est < 300 THEN 'sedang (100-299 token)'
                ELSE 'panjang (>=300 token)'
            END as kelompok,
            COUNT(*) as jumlah_chunk,
            ROUND(AVG(token_est), 1) as avg_token
        FROM chunks
        GROUP BY kelompok
        ORDER BY jumlah_chunk DESC
        """,
        "Distribusi panjang teks per chunk. Chunk panjang (>=300 token) mendominasi karena "
        "setiap chunk mencakup ~2 halaman PDF manual yang kaya konten teknis."
    ),
    "v_chapter_summary": (
        """
        SELECT chapter, COUNT(*) as total_chunks, 
               ROUND(AVG(token_est), 1) as avg_token,
               MIN(token_est) as min_token,
               MAX(token_est) as max_token
        FROM chunks
        GROUP BY chapter
        ORDER BY total_chunks DESC
        """,
        "Ringkasan per chapter manual. Chapter dengan chunk terbanyak menandakan bagian "
        "yang paling detail dalam manual, seperti bagian instrumen dan sistem engine."
    ),
    "v_user_role_dist": (
        """
        SELECT 
            CASE 
                WHEN user_role LIKE '%driver%' AND user_role LIKE '%fleet%' THEN 'driver & fleet_manager'
                WHEN user_role LIKE '%driver%' THEN 'driver'
                WHEN user_role LIKE '%fleet%' THEN 'fleet_manager'
                ELSE user_role
            END as target_pembaca,
            COUNT(*) as total_chunks
        FROM chunks
        GROUP BY target_pembaca
        ORDER BY total_chunks DESC
        """,
        "Distribusi target pembaca per chunk. Menunjukkan apakah konten ditujukan untuk "
        "driver, fleet manager, atau keduanya sekaligus."
    ),
    "v_top_keywords": (
        """
        SELECT keyword_item as keyword, COUNT(*) as frekuensi
        FROM (
            SELECT UNNEST(STRING_SPLIT(keywords, ', ')) as keyword_item
            FROM chunks
        )
        GROUP BY keyword_item
        ORDER BY frekuensi DESC
        LIMIT 20
        """,
        "Top 20 keyword paling sering muncul di seluruh chunk. Keyword seperti 'engine', "
        "'brake', dan 'warning' mendominasi karena fokus manual pada keselamatan operasional."
    ),
}

def run_analysis():
    con = duckdb.connect(str(DB_PATH))
    print("🔄 Membuat analytical views & menampilkan hasil...\n")

    for name, (query, description) in VIEWS.items():
        # Buat atau ganti view
        con.execute(f"DROP VIEW IF EXISTS {name}")
        con.execute(f"CREATE VIEW {name} AS {query}")

        # Ambil data & print
        df = con.execute(f"SELECT * FROM {name}").df()

        print("=" * 70)
        print(f"View: {name}")
        print("=" * 70)
        print(df.to_string(index=False))
        print()
        print(f"{len(df)} baris ditampilkan | {len(df.columns)} kolom: {df.columns.tolist()}")
        print()
        print(f"  {description}")
        print()

    con.close()
    print("✅ Semua views selesai dibuat dan tersimpan di warehouse.duckdb")

if __name__ == "__main__":
    run_analysis()