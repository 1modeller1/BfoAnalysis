import re, os
import sqlite3
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from drawMaps import drawWorldMap, drawRegionMap

NUM = 0
def do (fileName = "drawPlots.txt"):
    def renderBlock (text):
        global NUM
        def replacer (match):
            before = match.group(1)
            after = match.group(2)
            if k.isupper():
                after = re.sub(rf"{k}\.", rf"{config[k]}.", after)
            else:
                after = re.sub(rf"\.{k}", rf".{config[k]}", after)
            return before + ":" + after

        def getData (axis):
            if match := re.search(rf"^{axis}: (.*)$", tex, flags=re.MULTILINE):
                run = match.group(1)
                tables = list(set(re.findall(r"([^ ]*)\.", run)))
                tables = list(set( [re.sub(r"(\(|\))", "", tab) for tab in tables] ))
                raws = list(set(re.findall(r"([^ ]*\.[^ ,\n]*)", run)))
                runN = ",".join([ "ROUND(" + a + ",2)" for a in re.findall(r"(?:,|^)(.*?)(?=,|$)", run)])

                com = f"SELECT{ " DISTINCT" if "parms" in settings and "DIS" in settings["parms"] else ""} "
                com += f"{runN} FROM {tables[0]}\n"
                for tab in tables[1:]:
                    com += f"JOIN {tab}\nON {tables[0]}.inn = {tab}.inn\n"
                if "period" in settings:
                    com += f"WHERE {" and ".join(tab + f".period = {settings["period"]}" for tab in tables if not tab in ["bfoStart", "bfoStartPlus"])}"
                    if "parms" in settings and "NON" in settings["parms"]:
                        if "WHERE" in com: com += " and "
                        else: com += "WHERE "
                        com +=" and ".join([a + " IS NOT NULL" for a in re.findall(r"(?:,|^)(.*?)(?=,|$)", run)])
                if "where" in settings:
                    if "WHERE" in com: com += " and "
                    else: com += "WHERE "
                    com += settings["where"]
                com += "\n"
                if "sortBy" in settings:
                    com += f"ORDER BY {settings["sortBy"]}"

                cur.execute(com)
                ans = [list(d) for d in zip(*cur)]
                return ans
            else:
                return None

        if m := re.findall(r"^parms(.*)", text, flags=re.MULTILINE):
            m = m[0]
            tex = re.sub(r"^parms.*", r"PARMS", text, flags=re.MULTILINE)
        else:
            tex = text

        for k in config.keys():
            tex = re.sub(r"(.+):(.+)", replacer, tex)
        tex = tex.replace("PARMS", f"parms{m}")

        settings = {}
        for line in tex.splitlines():
            if gr := re.findall(r"(.+): ?(.+)", line):
                gr = gr[0]
                settings[gr[0]] = gr[1]

        if re.search(rf"^mapW: (.*)$", tex, flags=re.MULTILINE):
            drawWorldMap(okved, tex, NUM, settings)
        if re.search(rf"^mapR: (.*)$", tex, flags=re.MULTILINE):
            drawRegionMap(okved, tex, NUM, settings)

        yy = getData("y")
        xx = getData("x")
        if yy == None and xx == None:
            return None
        elif yy == None:
            yy = [[a for a in range(len(xx[0]))]]
        elif xx == None:
            xx = [[a for a in range(len(yy[0]))]]

        while len(yy) < len(xx):
            yy.append(yy[-1])
        while len(xx) < len(yy):
            xx.append(xx[-1])
        if "equation" in settings:
            tmp = re.findall(r"(?:<|>|=)*(.*)", settings["equation"])[0]
            eq = [eval(tmp.replace("x", str(x))) for x in xx[0]]

        if "name" in settings:
            plt.title(settings["name"])
        if "nameX" in settings:
            plt.xlabel(settings["nameX"])
        if "nameY" in settings:
            plt.ylabel(settings["nameY"])
        if "xlim" in settings:
            xl = re.findall(r"(-?\d+.?\d*) (-?\d+.?\d*)", settings["xlim"])[0]
            plt.xlim([float(xl[0]), float(xl[1])])
        if "ylim" in settings:
            yl = re.findall(r"(-?\d+.?\d*) (-?\d+.?\d*)", settings["ylim"])[0]
            plt.ylim([float(yl[0]), float(yl[1])])
        plt.minorticks_on()
        plt.grid(which="minor", color="#d0d0d0", linewidth=0.5)
        plt.grid(color="#404040")
        if "parms" in settings and "LOGx" in settings["parms"]:
            plt.xscale("log")
        if "parms" in settings and "LOGy" in settings["parms"]:
            plt.yscale("log")
        if "parms" in settings and "symLOGy" in settings["parms"]:
            plt.yscale("symlog")
        if "parms" in settings and "symLOGx" in settings["parms"]:
            plt.xscale("symlog")

        if "legend" in settings:
            lg = re.findall(r"(?:,|^)(.*?)(?=,|$)", settings["legend"])
            for i, do in enumerate(zip(xx, yy)):
                plt.plot(do[0], do[1], "o", ms=2, label=lg[i])
            plt.legend(fontsize = 12)
        else:
            for do in zip(xx, yy):
                plt.plot(do[0], do[1], "o", ms=2)
        if "equation" in settings:
            ymin, ymax = plt.ylim()
            if "eColor" in settings:
                eColor = settings["eColor"]
            else:
                eColor = "red"

            if not "ylim" in settings:
                plt.ylim(ymin, ymax)
            if ">" in settings["equation"]:
                plt.fill_between(xx[0], eq, ymin, color=eColor, alpha=0.25)
            elif "<" in settings["equation"]:
                plt.fill_between(xx[0], eq, ymax, color=eColor, alpha=0.25)
            if "=" in settings["equation"]:
                plt.plot(xx[0], eq, color =eColor, alpha=0.5)

        if not "graphs" in os.listdir(): os.mkdir("graphs")
        plt.savefig(f"graphs/plot-{NUM}.png", dpi=200)
        plt.close()

        if "parms" in settings and "STAT" in settings["parms"]:
            if not "stat" in os.listdir(): os.mkdir("stat")
            if NUM == 0: file = open(f"stat/stat-{okved}.txt", "w")
            else: file = open(f"stat/stat-{okved}.txt", "a")

            for i, ys in enumerate(yy):
                ys = list(filter(lambda x: x != None, ys))
                stat = {}
                stat["mean"] = np.mean(ys) # мат ожидание
                stat["variance"] = np.var(ys, ddof=1) # дисперсия
                stat["std_dev"] = np.std(ys, ddof=1) # стандартное отклонение
                stat["skewness"] = stats.skew(ys) # ассиметрия
                stat["kurtosis"] = stats.kurtosis(ys) # эксцесс
                stat["median"] = np.median(ys) # медиана
                q1, q3 = np.percentile(ys, 25), np.percentile(ys, 75)
                stat["iqr"] = q3 - q1 # межквартальный размах

                names = {"mean" : "Мат ожидание", "variance" : "Дисперсия", "std_dev" : "Средне квадратическое отклонение",
                         "skewness" : "Асимметрия", "kurtosis" : "Эксцесс", "median" : "Медиана", "iqr" : "Межквартальный размах"}
                text = f"Plot-{NUM} {settings["name"] if "name" in settings else ""} ({lg[i] if "legend" in settings else "--"})\n"
                text += "\n".join(names[a] + ": " + f"{round(stat[a], 2):,}" for a in stat.keys())
                text += "\n\n"
                file.write(text)
            file.close()

        print(NUM, end=" / ", flush=True)
        NUM += 1

    file = open(fileName, "r")
    okved = re.findall(r"^[\d.]+", file.readline())[0]
    db = sqlite3.connect(f"data/data-okved-{okved}.db")
    cur = db.cursor()

    config = {}
    conf = False
    block = ""
    for line in file.readlines():
        if "config" in line:
            conf = True
        elif "---" in line:
            conf = False
            if block != "":
                renderBlock(block)
                block = ""
        elif conf:
            match = re.match(r"([^ ]*) ?= ?([^ \n#]*)", line)
            if match != None:
                config[match.group(1)] = match.group(2)
        else:
            block += line
    if block != "":
        renderBlock(block)

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        do(args[0])
    else:
        do()