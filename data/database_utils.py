import sqlite3
from config import DB_PATH

def get_metadata_value(key: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM metadata WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    if not row: 
        raise KeyError(f"Metadata key '{key}' not found")
    return row[0]

def update_metadata(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO metadata (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
    """, (key, value))
    conn.commit()
    conn.close()

def truncate_patch_id(patch_id: str) -> str:
    parts = patch_id.split(".")
    return f"{parts[0]}.{parts[1]}"