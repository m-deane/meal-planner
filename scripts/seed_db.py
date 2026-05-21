"""Load seed.sql into the database if it exists and the recipes table is empty."""
import sqlite3
import os
import sys

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///data/recipes.db")
if DB_PATH.startswith("sqlite:///"):
    db_file = DB_PATH[len("sqlite:///"):]
elif DB_PATH.startswith("sqlite://"):
    db_file = DB_PATH[len("sqlite://"):]
else:
    print("Non-SQLite database — skipping seed.", flush=True)
    sys.exit(0)

seed_file = os.path.join(os.path.dirname(__file__), "..", "data", "seed.sql")
seed_file = os.path.normpath(seed_file)

if not os.path.exists(seed_file):
    print(f"No seed file at {seed_file} — skipping.", flush=True)
    sys.exit(0)

conn = sqlite3.connect(db_file)
try:
    count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count > 0:
        print(f"Database already has {count} recipes — skipping seed.", flush=True)
        sys.exit(0)
except Exception:
    pass

print(f"Seeding database from {seed_file} ...", flush=True)
with open(seed_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Only execute INSERT statements — schema is already created by init-db
inserts = [l for l in lines if l.strip().upper().startswith("INSERT")]
insert_sql = "BEGIN TRANSACTION;\n" + "".join(inserts) + "\nCOMMIT;"
conn.executescript(insert_sql)
count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
print(f"Seeded {count} recipes.", flush=True)
conn.close()
