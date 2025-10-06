import json
import sys, os
import requests
import re
import sqlite3

# okved = "05"
# buffer : int = 200

def do (okved : str, year = "", buffer = 200):

    # Check number of companies to download and ask about it
    url = f"https://bo.nalog.gov.ru/advanced-search/organizations?allFieldsMatch=false&okved={okved}{f"&period={year}" if year != "" else ""}&page=0&size=0"
    req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    js = json.loads(req.text)
    length = js["totalElements"]
    while True:
        print("Get INNs".center(39, "."))
        ask = input(f"Download {length} elements? (yes/no/number): ")
        if ask.lower() == "yes":
            break
        elif ask.lower() == "no":
            sys.exit()
        elif ask.isnumeric():
            if int(ask) % buffer == 0:
                length = int(ask)
                break
            else:
                print(f"Number must be divisible on buffer size ({buffer})")
                asked = min((int(ask) // buffer + 1) * buffer, length)
                if input(f"Will be downloaded: {asked}. Ok? ").lower() in ["yes", "ok"]:
                    length = asked
                    break

    if not "data" in os.listdir(): os.mkdir("data")
    db = sqlite3.connect(f"data/data-okved-{okved}.db")
    cur = db.cursor()
    t = 0
    while t * buffer < length:
        url = f"https://bo.nalog.gov.ru/advanced-search/organizations?allFieldsMatch=false&okved={okved}&page={str(t)}&size={str(buffer)}"
        req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        text = re.sub(r"<[^<>\n]*>", r"", req.text)
        js = json.loads(text)

        # file = open("data/file.json", "w")
        # json.dump(js, file, indent=4, ensure_ascii=False)

        columnsT1 = ["id", "inn", "shortName", "ogrn", "indexx", "region", "district",
                     "city", "settlement", "street", "house", "building", "office", "okved2",
                     "okopf", "okato", "okpo", "okfs", "statusCode", "statusDate"]
        com0 = "CREATE TABLE IF NOT EXISTS bfoStart (" + ",".join(a + " TEXT" for a in columnsT1) + ")"
        cur.execute(com0)
        columnsT1[columnsT1.index("indexx")] = "index"

        columnsT2 = ["id", "inn", "shortName", "period", "actualBfoDate", "gainSum", "knd", "hasAz", "hasKs",
                     "actualCorrectionNumber", "actualCorrectionDate", "isCb", "bfoPeriodTypes"]
        com2 = "CREATE TABLE IF NOT EXISTS bfoStartPlus (" + ",".join(a + " TEXT" for a in columnsT2) + ")"
        columnsT2.remove("bfoPeriodTypes")
        cur.execute(com2)
        db.commit()

        for go in range(buffer):
            if t * buffer + go == length:
                break
            com11 = "INSERT INTO bfoStart VALUES ("
            for i in columnsT1:
                inp = str(js["content"][go][i])
                if inp == "None":
                    com11 += "NULL,"
                    continue
                b = re.sub(r'"', r'', inp)
                b = re.sub(r"'", r'', inp)
                com11 += "'" + b + "',"
            com11 = com11[:-1] + ")"
            cur.execute(com11)
            db.commit()

            com21 = "INSERT INTO bfoStartPlus VALUES ("
            for i in columnsT2:
                if i in ["id", "inn", "shortName"]:
                    inp = str(js["content"][go][i])
                else:
                    inp = str(js["content"][go]["bfo"][i])
                b = re.sub(r'"', r'', inp)
                com21 += "'" + b + "',"
            inp = "[" + ",".join(str(a) for a in js["content"][go]["bfo"]["bfoPeriodTypes"]) + "]"
            com21 += "'" + inp + "'"
            com21 = com21 + ")"
            cur.execute(com21)
            db.commit()

            print((str(round((t * buffer + go + 1) / length*100, 1)) + " %").ljust(12) + "(" + str(t * buffer + go + 1) + ")" )
        t += 1