import sqlite3, shutil

okved = "01.1"

db = sqlite3.connect("data/data-okved-01.1.db")
cur = db.cursor()

tables = ["balance", "orgInfo", "finRes", "capChange", "fundsMove", "targFund"]
for a in tables:
    comDrop = f"DROP TABLE {a}"
    cur.execute(comDrop)
    db.commit()

shutil.copy2(f"data/data-okved-{okved}.db", f"copy/data-okved-{okved}.db")