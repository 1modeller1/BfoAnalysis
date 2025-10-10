import os, re, sys

import addCompanies, addData, analyze, editSQL

def getOkved (okved) :
    if not okved:
        okved = input("okved: ")
        okved = okved.replace(" ", "")
    print(okved)
    return okved

def getOkvedAndYear (okved, year):
    if not okved:
        inp2 = input("okved (year): ")
        il = re.findall(r" ?([^ ]+) ?", inp2)
        if len(il) == 1:
            il.append("")
        okved, year = il
    print(okved + "  " + year)
    return okved, year

if __name__ == "__main__":
    args = sys.argv[1:]
    okved, year, file = "", "", ""
    if len(args) == 0:
        inp = input("Import companies inns, data, add locations or draw plots (maps)? (inn/data/addLoc/plot): ")
    if len(args) >= 1:
        inp = args[0]
    if len(args) >= 2:
        if inp == "plot":
            file = args[1]
        else:
            okved = args[1]
    if len(args) >= 3:
        year = args[2]

    if inp == "inn":
        okved, year = getOkvedAndYear(okved, year)
        addCompanies.do(okved, year)
    elif inp == "data":
        okved = getOkved(okved)
        addData.do(okved)
    elif inp == "plot":
        if file:
            analyze.do(file)
        else:
            analyze.do()
    elif inp == "addLoc":
        okved = getOkved(okved)
        editSQL.addLocations(okved)

# okved are there: https://www.consultant.ru/document/cons_doc_LAW_163320/
