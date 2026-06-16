# pipeline/ingestion/load_data.py
import json
from pathlib import Path

RAW_DIR = Path("data/raw")

def load_and_validate(path: Path) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "chunks" in data, f"'chunks' tidak ditemukan di {path.name}!"
    meta   = data.get("dataset_meta", {})
    chunks = data["chunks"]

    required_fields = ["chunk_id", "category", "sub_category", "text", "keywords", "user_role"]
    missing = {}
    for chunk in chunks:
        for field in required_fields:
            if field not in chunk:
                missing.setdefault(field, 0)
                missing[field] += 1

    print(f"\n{'='*50}")
    print(f"FILE  : {path.name}")
    print(f"{'='*50}")
    print(f"  Nama    : {meta.get('name', '-')}")
    print(f"  Series  : {meta.get('truck_model') or meta.get('series', '-')}")
    print(f"  Versi   : {meta.get('version', '-')}")
    print(f"  Chunks  : {len(chunks)} (meta: {meta.get('total_chunks', '?')})")
    print(f"  Bahasa  : {meta.get('language', '-')}")

    if missing:
        print(f"  ⚠️  Field hilang: {missing}")
    else:
        print(f"  ✅ Semua field wajib lengkap")

    return len(chunks)

if __name__ == "__main__":
    json_files = sorted(RAW_DIR.glob("*.json"))
    if not json_files:
        print("⚠️  Tidak ada file JSON di data/raw/")
    else:
        total = 0
        for path in json_files:
            total += load_and_validate(path)
        print(f"\n✅ Total: {len(json_files)} file, {total} chunk siap diproses.")