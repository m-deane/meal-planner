"""Load seed SQL files into the database if it exists and the recipes table is empty."""
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

base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))

conn = sqlite3.connect(db_file)


def run_seed_file(path: str, insert_only: bool = False) -> None:
    """Execute a seed SQL file against the open connection."""
    if not os.path.exists(path):
        print(f"No seed file at {path} — skipping.", flush=True)
        return

    print(f"Loading {path} ...", flush=True)
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    if insert_only:
        # Legacy mode: seed.sql came from sqlite3 .dump and contains CREATE TABLE
        # statements that conflict with init-db. Filter to INSERT lines only and
        # rewrite as INSERT OR IGNORE so duplicates are silently skipped.
        lines = sql.splitlines(keepends=True)
        insert_lines = [
            l.replace("INSERT INTO", "INSERT OR IGNORE INTO", 1)
            for l in lines
            if l.strip().upper().startswith("INSERT")
        ]
        sql = "BEGIN TRANSACTION;\n" + "".join(insert_lines) + "\nCOMMIT;"

    conn.executescript(sql)
    print(f"  Done: {path}", flush=True)


def run_backfill() -> None:
    """Derive allergen links + ingredient categories from ingredient names.

    Recipes loaded from the raw SQL dumps bypass the scraper's allergen/category
    population, leaving recipe_allergens empty. This idempotent pass fills them
    in via the shared food taxonomy. Connects through SQLAlchemy to the same DB.
    """
    try:
        from src.database.connection import session_scope
        from src.database.seed import backfill_allergens_and_categories
        with session_scope() as s:
            stats = backfill_allergens_and_categories(s)
        print(f"  Allergen/category backfill: {stats}", flush=True)
    except Exception as e:  # never let backfill failure break seeding
        print(f"  Backfill skipped ({e})", flush=True)


try:
    count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count > 0:
        print(f"Database already has {count} recipes — skipping recipe seed.", flush=True)
        # Still seed ingredients if the table is empty (upgrade path)
        ing_count = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
        if ing_count == 0:
            print("Ingredients table empty — seeding ingredients.", flush=True)
            run_seed_file(os.path.join(base_dir, "seed_ingredients.sql"))
        else:
            print(f"Ingredients already seeded ({ing_count} rows) — skipping.", flush=True)
        conn.close()
        run_backfill()
        sys.exit(0)
except SystemExit:
    raise
except Exception:
    pass

# Fresh DB: seed recipes first (insert_only=True because seed.sql is a raw .dump)
run_seed_file(os.path.join(base_dir, "seed.sql"), insert_only=True)
# Then seed ingredients (already uses INSERT OR IGNORE, no filtering needed)
run_seed_file(os.path.join(base_dir, "seed_ingredients.sql"))

count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
ing_count = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
print(f"Seeded {count} recipes, {ing_count} ingredients.", flush=True)
conn.close()
run_backfill()
