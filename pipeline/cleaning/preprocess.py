# pipeline/cleaning/preprocess.py
"""
Preprocessing MULTI-FILE: CD Series + Croner Series
Output: data/clean/chunks_clean.json + chunks_df.csv (gabungan)
"""

import json
import re
import pandas as pd
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
RAW_FILES = [
    RAW_FILES = sorted(Path("data/raw").glob("*.json"))
]
OUT_JSON   = Path("data/clean/chunks_clean.json")
OUT_CSV    = Path("data/clean/chunks_df.csv")
MIN_TOKENS = 20

# ── CLEANING ──────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

# ── NORMALIZE: samakan field dari dua format berbeda ─────────────────────────
def normalize_chunk(chunk: dict, source_file: str) -> dict | None:
    text_clean = clean_text(chunk.get("text", ""))
    if estimate_tokens(text_clean) < MIN_TOKENS:
        return None

    user_role = chunk.get("user_role", [])
    if isinstance(user_role, str):
        user_role = [user_role]

    keywords = chunk.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [keywords]

    # Handle perbedaan field antar dataset
    chapter = (
        chunk.get("chapter")           # field CD Series
        or chunk.get("source_section") # field Croner Series
        or ""
    )
    series = (
        chunk.get("series")            # field CD Series
        or chunk.get("applies_to")     # field Croner Series
        or ""
    )

    return {
        "chunk_id"     : chunk.get("chunk_id", ""),
        "source_file"  : source_file,                    # ← kolom baru: asal file
        "series"       : series,
        "applies_to"   : chunk.get("applies_to", ""),
        "category"     : chunk.get("category", ""),
        "sub_category" : chunk.get("sub_category", ""),
        "source_doc"   : chunk.get("source_doc", ""),
        "chapter"      : chapter,
        "page"         : chunk.get("page", ""),          # kosong untuk Croner
        "fault_code"   : chunk.get("fault_code"),        # None untuk Croner
        "user_role"    : user_role,
        "keywords"     : keywords,
        "language"     : chunk.get("language", "en"),
        "text"         : text_clean,
        "token_est"    : estimate_tokens(text_clean),
    }

# ── PIPELINE UTAMA ────────────────────────────────────────────────────────────
def run_preprocessing():
    all_chunks = []
    all_meta   = []

    for raw_path in RAW_FILES:
        if not raw_path.exists():
            print(f"⚠️  File tidak ditemukan, dilewati: {raw_path}")
            continue

        print(f"🔄 Load: {raw_path.name}")
        with open(raw_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        chunks_raw = raw.get("chunks", [])
        source_name = raw_path.stem
        dropped = 0

        for chunk in chunks_raw:
            result = normalize_chunk(chunk, source_file=source_name)
            if result is None:
                dropped += 1
            else:
                all_chunks.append(result)

        print(f"   ✅ {len(chunks_raw) - dropped} chunk bersih, {dropped} di-drop")
        all_meta.append(raw.get("dataset_meta", {}))

    # ── Simpan JSON ──
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "preprocessing": {
            "total_clean"  : len(all_chunks),
            "sources"      : [p.stem for p in RAW_FILES if p.exists()],
        },
        "chunks": all_chunks,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Disimpan ke {OUT_JSON}")

    # ── Simpan CSV ──
    df = pd.DataFrame(all_chunks)
    df["user_role"] = df["user_role"].apply(lambda x: ", ".join(x))
    df["keywords"]  = df["keywords"].apply(lambda x: ", ".join(x))
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"💾 Disimpan ke {OUT_CSV}")

    # ── Ringkasan ──
    print()
    print("=" * 55)
    print("RINGKASAN PREPROCESSING GABUNGAN")
    print("=" * 55)
    print(f"  Total chunk gabungan : {len(df)}")
    print(f"  CD Series            : {len(df[df['source_file'].str.contains('cd')])}")
    print(f"  Croner Series        : {len(df[df['source_file'].str.contains('croner')])}")
    print(f"  Bahasa en            : {len(df[df['language']=='en'])}")
    print(f"  Bahasa id            : {len(df[df['language']=='id'])}")
    print(f"  Token rata-rata      : {df['token_est'].mean():.1f}")
    print(f"  Kategori unik        : {df['category'].nunique()}")

if __name__ == "__main__":
    run_preprocessing()