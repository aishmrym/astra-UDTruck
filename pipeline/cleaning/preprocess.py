# src/02_preprocess.py
"""
Preprocessing cd_series_manual.json untuk pipeline RAG.

Yang dilakukan:
1. Load JSON mentah
2. Bersihkan field 'text' (ringan — sesuai prinsip RAG)
3. Normalisasi field metadata (user_role & keywords jadi string)
4. Filter chunk kosong / teks terlalu pendek
5. Hitung token count estimasi
6. Simpan output: chunks_clean.json + chunks_df.csv
"""

import json
import re
import pandas as pd
from pathlib import Path

RAW_PATH    = Path("data/raw/cd_series_manual.json")
OUT_JSON    = Path("data/clean/chunks_clean.json")
OUT_CSV     = Path("data/clean/chunks_df.csv")
MIN_TOKENS  = 20   # chunk dengan estimasi token < ini dianggap terlalu pendek

# ── 1. Load ───────────────────────────────────────────────────────────────────

def load_raw(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ── 2. Pembersihan teks (ringan — prinsip RAG) ────────────────────────────────

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Hapus karakter kontrol non-printable (form feed, null, dll)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    # Rapikan spasi berlebih & baris kosong ganda
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim
    text = text.strip()
    return text

# ── 3. Estimasi jumlah token (kasar: 1 token ≈ 4 karakter) ───────────────────

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

# ── 4. Preprocessing satu chunk ───────────────────────────────────────────────

def preprocess_chunk(chunk: dict) -> dict | None:
    """Return chunk yang sudah bersih, atau None kalau harus di-drop."""

    text_clean = clean_text(chunk.get("text", ""))

    # Drop kalau teks terlalu pendek
    if estimate_tokens(text_clean) < MIN_TOKENS:
        return None

    # Normalisasi user_role & keywords jadi list of string (jaga-jaga kalau ada yang aneh)
    user_role = chunk.get("user_role", [])
    if isinstance(user_role, str):
        user_role = [user_role]

    keywords = chunk.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [keywords]

    return {
        "chunk_id"     : chunk.get("chunk_id", ""),
        "series"       : chunk.get("series", ""),
        "applies_to"   : chunk.get("applies_to", ""),
        "category"     : chunk.get("category", ""),
        "sub_category" : chunk.get("sub_category", ""),
        "source_doc"   : chunk.get("source_doc", ""),
        "chapter"      : chunk.get("chapter", ""),
        "page"         : chunk.get("page", ""),
        "fault_code"   : chunk.get("fault_code"),          # boleh None
        "user_role"    : user_role,
        "keywords"     : keywords,
        "language"     : chunk.get("language", "en"),
        "text"         : text_clean,
        "token_est"    : estimate_tokens(text_clean),
    }

# ── 5. Pipeline utama ─────────────────────────────────────────────────────────

def run_preprocessing():
    print("🔄 Load raw data...")
    raw = load_raw(RAW_PATH)
    chunks_raw = raw["chunks"]
    print(f"   {len(chunks_raw)} chunk ditemukan.")

    print("🔄 Preprocessing setiap chunk...")
    chunks_clean = []
    dropped = 0
    for chunk in chunks_raw:
        result = preprocess_chunk(chunk)
        if result is None:
            dropped += 1
        else:
            chunks_clean.append(result)

    print(f"   ✅ {len(chunks_clean)} chunk bersih")
    print(f"   ⚠️  {dropped} chunk di-drop (teks terlalu pendek)")

    # ── Simpan JSON ──
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "dataset_meta": raw["dataset_meta"],
        "preprocessing": {
            "total_raw"    : len(chunks_raw),
            "total_clean"  : len(chunks_clean),
            "total_dropped": dropped,
            "min_tokens"   : MIN_TOKENS,
        },
        "chunks": chunks_clean,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"   💾 Disimpan ke {OUT_JSON}")

    # ── Simpan CSV (flatten user_role & keywords jadi string) ──
    df = pd.DataFrame(chunks_clean)
    df["user_role"] = df["user_role"].apply(lambda x: ", ".join(x))
    df["keywords"]  = df["keywords"].apply(lambda x: ", ".join(x))
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"   💾 Disimpan ke {OUT_CSV}")

    # ── Ringkasan statistik ──
    print()
    print("=" * 50)
    print("RINGKASAN PREPROCESSING")
    print("=" * 50)
    print(f"  Total chunk bersih  : {len(chunks_clean)}")
    print(f"  Estimasi token min  : {df['token_est'].min()}")
    print(f"  Estimasi token max  : {df['token_est'].max()}")
    print(f"  Estimasi token rata : {df['token_est'].mean():.1f}")
    print(f"  Kategori unik       : {df['category'].nunique()} → {df['category'].unique().tolist()}")
    print(f"  Sub-kategori unik   : {df['sub_category'].nunique()}")
    print(f"  Chunk punya fault_code: {df['fault_code'].notna().sum()}")

if __name__ == "__main__":
    run_preprocessing()