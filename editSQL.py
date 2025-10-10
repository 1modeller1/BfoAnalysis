import sqlite3, shutil, os
import sys

import pgeocode
from math import isnan


# okved = "24"
# db = sqlite3.connect("data/data-okved-24.db")
# cursor = db.cursor()

# tables = ["balance", "orgInfo", "finRes", "capChange", "fundsMove", "targFund"]

# for a in tables:
#     comDrop = f"DROP TABLE {a}"
#     cur.execute(comDrop)
#     db.commit()

# shutil.copy2(f"data/data-okved-{okved}.db", f"copy/data-okved-{okved}.db")

# ----------------------------

# com = """
#     select id, inn, B.current1310 FROM balance B
#     where B.period = 2024 and B.current1310 is not null
#     ORDER BY B.current1310 DESC
# """
#
# cur.execute(com)
# l = [d for d in cur]
#
# for i, a in enumerate(l):
#     print(f"id: {str(a[0])}  inn: {str(a[1])}  1310: {str(a[2])}")
#     if i == 100:
#         break

# ----------------------------

def addLocations (okved):
    if not "copy" in os.listdir(): os.mkdir("copy")
    shutil.copy2(f"data/data-okved-{okved}.db", f"copy/data-okved-{okved}.db")

    db = sqlite3.connect(f"data/data-okved-{okved}.db")
    cursor = db.cursor()
    com = f"""
    SELECT s.indexx, s.id FROM bfoStart s
    where s.indexx is not NULL;
    """

    cursor.execute(com)
    data = [d for d in cursor]

    lats, lons, ids = [], [], []
    nomi = pgeocode.Nominatim('ru')
    l = len(data)

    for i, d in enumerate(data):
        info = nomi.query_postal_code(d[0])
        x, y = info.latitude, info.longitude
        if isnan(x) or isnan(y):
            continue
        x, y = round(x, 2), round(y, 2)

        lats.append(x)
        lons.append(y)
        ids.append(d[1])

        if round(i / l*100, 2) % 1:
            print(str(int(i / l*100)) + " %", flush=True)

    com = """
    PRAGMA table_info (bfoStart);
    """
    cursor.execute(com)
    isTables = [d[1] for d in cursor]
    db.commit()
    if not ("latitude" in isTables and "longitude" in isTables):
        com = """
        BEGIN TRANSACTION;
        ALTER TABLE bfoStart
        ADD COLUMN latitude REAL;
        ALTER TABLE bfoStart
        ADD COLUMN longitude REAL;
        """
        cursor.executescript(com)
        db.commit()

    for let, lon, id in zip(lats, lons, ids):
        cursor.execute(f"""
        UPDATE bfoStart
        SET latitude = {let}, longitude = {lon}
        WHERE id = '{id}'
        """)
    db.commit()

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        okved = args[0]
    else:
        okved = input("okved: ")
    addLocations(okved)