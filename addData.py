import json
import sys, shutil, os
import requests
import re
import sqlite3

# У меня скорость скачивания 40 сек на 100 позиций

def do (okved):
    if not "copy" in os.listdir(): os.mkdir("copy")
    shutil.copy2(f"data/data-okved-{okved}.db", f"copy/data-okved-{okved}.db")

    def getIds ():
        file = sqlite3.connect(f"data/data-okved-{okved}.db")
        cursor = file.cursor()
        cursor.execute("SELECT DISTINCT id FROM bfoStart")
        return [d[0] for d in cursor]

    def gT (inp) -> str:
        inp = str(inp)
        if inp == None or inp == "" or inp == " ":
            return "NULL"
        else:
            inp = inp.replace("'", '"')
            inp = inp.replace("\n", ' ')
            return "'" + str(inp) + "'"

    def updateTable (inpJson, tableName, cursor, mainList):
        a_ = list(inpJson.keys())
        cursor.execute(f"PRAGMA table_info ({tableName});")
        b_ = [a[1] for a in cursor]
        ab_ = list(set(a_) ^ (set(a_) & set(b_)))

        for i in ab_:
            cursor.execute(f"""
            ALTER TABLE {tableName}
            ADD COLUMN {i} REAL;
            """)
        db.commit()

        codeIn = f"INSERT INTO {tableName} ({",".join(columnsMain + a_)}) VALUES ({",".join(mainList)}"
        for i in a_:
            codeIn += "," + gT(inpJson[i])
        codeIn += ");"

        cur.execute(codeIn)
        db.commit()

    ids = getIds()
    length = len(ids)

    if not "data" in os.listdir(): os.mkdir("data")
    db = sqlite3.connect(f"data/data-okved-{okved}.db")
    cur = db.cursor()

    columnsO = ["inn", "fullName", "kpp", "address", "okved2_id", "okved2_name", "okopf_id", "okopf_name", "okfs_id", "okfs_name", "okpo"]
    comO = "CREATE TABLE IF NOT EXISTS orgInfo (id TEXT," # organisation info
    comO += ",".join(a + " TEXT" for a in columnsO) + ")"
    columnsMain = ["id", "inn", "period", "type", "okud"]
    comB = f"CREATE TABLE IF NOT EXISTS balance ({",".join( a + " TEXT" for a in columnsMain)})"
    comF = f"CREATE TABLE IF NOT EXISTS finRes ({",".join( a + " TEXT" for a in columnsMain)})" # financial result
    comC = f"CREATE TABLE IF NOT EXISTS capChange ({",".join( a + " TEXT" for a in columnsMain)})" # capital change
    comM = f"CREATE TABLE IF NOT EXISTS fundsMove ({",".join( a + " TEXT" for a in columnsMain)})" # funds movement
    comT = f"CREATE TABLE IF NOT EXISTS targFund ({",".join( a + " TEXT" for a in columnsMain)})" # target funds using

    for a in [comB, comO, comF, comC, comM, comT]:
        cur.execute(a)
    db.commit()

    ERRORS = []
    for t, id in enumerate(ids):
        try:
            url = f"https://bo.nalog.gov.ru/nbo/organizations/{id}/bfo/"
            req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            js = json.loads(req.text)

            inn = js[0]["organizationInfo"]["inn"]
            comO1 = f"INSERT INTO orgInfo VALUES ({id},"
            for a in columnsO:
                if "name" in a:
                    n = a[:a.find("_")]
                    try:
                        comO1 += gT(js[0]["organizationInfo"][n]["name"]) + ","
                    except:
                        comO1 += "NULL,"
                else:
                    comO1 += gT(js[0]["organizationInfo"][a]) + ","
            comO1 = comO1[:-1] + ")"
            cur.execute(comO1)
            db.commit()

            for j in js:
                period = j["period"]
                for i in j["typeCorrections"]:
                    type = str(i["type"])
                    l = [["balance", "balance"], ["financialResult", "finRes"], ["capitalChange", "capChange"], ["fundsMovement", "fundsMove"],
                         ["targetedFundsUsing", "targFund"]]
                    for a in l:
                        if a[0] in i["correction"]:
                            i_ = i["correction"][a[0]]
                            updateTable(i_, a[1], cur, [id, inn, period, type, i_["okud"]])

            print((str(round((t + 1) / length * 100, 1)) + " %").ljust(12) + "(" + str(t + 1) + ")")
        except:
            print("ERROR")
            ERRORS.append(id)
    print(ERRORS)

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        inp = args[0]
    else:
        inp = input("okved: ")
    do(inp)