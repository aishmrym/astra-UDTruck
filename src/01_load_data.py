# src/01_load_data.py
"""
Load & validasi cd_series_manual.json
Output: ringkasan dataset ke console
"""

import json
import os

RAW_PATH = "data/raw/cd_series_manual.json"

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def validate_structure(data: dict):
    """Cek apakah JSON punya key yang diharapkan."""
    assert "dataset_meta" in data, "Key 'dataset_meta' tidak ditemukan!"
    assert "chunks" in data, "Key 'chunks' tidak ditemukan!"

    meta = data["dataset_meta"]
    chunks = data["chunks"]

    print("=" * 50)
    print("DATASET META")
    print("=" * 50)
    print(f"  Nama      : {meta.get('name')}")
    print(f"  Series    : {meta.get('series')}")
    print(f"  Versi     : {meta.get('version')}")
    print(f"  Tanggal   : {meta.get('processed_date')}")
    print(f"  Total chunk (meta): {meta.get('total_chunks')}")
    print(f"  Total chunk (aktual): {len(chunks)}")
    print()

    # Cek field wajib tiap chunk
    required_fields = ["chunk_id", "category", "sub_category", "chapter",
                       "page", "fault_code", "user_role", "keywords", "text"]
    missing_report = {}
    for chunk in chunks:
        for field in required_fields:
            if field not in chunk:
                missing_report.setdefault(field, 0)
                missing_report[field] += 1

    if missing_report:
        print("⚠️  Field yang hilang di beberapa chunk:")
        for field, count in missing_report.items():
            print(f"    {field}: {count} chunk")
    else:
        print("✅ Semua field wajib ada di setiap chunk.")

    return chunks

if __name__ == "__main__":
    data = load_json(RAW_PATH)
    chunks = validate_structure(data)
    print(f"\nSelesai. {len(chunks)} chunk siap diproses.")