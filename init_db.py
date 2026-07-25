"""
init_db.py — Run this ONCE before starting the Flask app.
Creates anganwadi.db with schema + seed data, then trains the ML model.
"""
import os, sqlite3, sys

BASE    = os.path.dirname(__file__)
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "anganwadi.db"))

def run_sql_file(con, path):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    con.executescript(sql)
    con.commit()

def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    run_sql_file(con, os.path.join(BASE, "db", "schema.sql"))
    print("Schema created.")
    run_sql_file(con, os.path.join(BASE, "db", "seed.sql"))
    print("Seed data loaded.")
    con.close()
    print(f"Database ready: {DB_PATH}")

    print("Training ML model...")
    sys.path.insert(0, os.path.join(BASE, "ml"))
    from train import train
    train(DB_PATH)
    print("Model ready: ml/model.pkl")
    print("\nAll done! Now run:  python app.py")

if __name__ == "__main__":
    init()
