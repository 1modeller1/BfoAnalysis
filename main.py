import os, re

import addCompanies, addData, analyze

if __name__ == "__main__":
    inp = input("Import companies inns, data or draw plots? (inn/data/plot): ")
    if inp == "inn":
        inp2 = input("okved (year): ")
        il = re.findall(r" ?([^ ]+) ?", inp2)
        if len(il) == 1:
            il.append("")
        addCompanies.do(il[0], il[1])
    elif inp == "data":
        inp2 = input("okved: ")
        inp2 = inp2.replace(" ", "")
        addData.do(inp2)
    elif inp == "plot":
        inp2 = input("drawPlots file: ")
        if os.path.exists(inp2):
            analyze.do(inp2)
        else:
            analyze.do()

# okved are there: https://www.consultant.ru/document/cons_doc_LAW_163320/
