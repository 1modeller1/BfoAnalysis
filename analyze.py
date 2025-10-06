import re, os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

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

        # def replacer_2 (match):
        #     value = str( go[int(match.group(0))] )
        #     return value if value != "None" else "0"

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
                    com += f"WHERE {" and ".join(tab + f".period = {settings["period"]}" for tab in tables)}"
                    if "parms" in settings and "NON" in settings["parms"]:
                        if "WHERE" in com: com += " and "
                        com +=" and ".join([a + " IS NOT NULL" for a in re.findall(r"(?:,|^)(.*?)(?=,|$)", run)])
                    com += "\n"
                if "sortBy" in settings:
                    com += f"ORDER BY {settings["sortBy"]}"

                cur.execute(com)
                ans = [list(d) for d in zip(*cur)]
                # plt.plot()
                # plt.show()

                # ma = re.findall(r"(?:,|^)(.*?)(?=,|$)", run)
                # m = ["" for _ in ma]
                # for i, a in enumerate(ma):
                #     m[i] = a
                #     for b in raws:
                #         m[i] = m[i].replace(b, str(raws.index(b)))
                #
                # ys = [[] for _ in ma]
                # for go in ans:
                #     for mm in m:
                #         result = re.sub(r"\b\d+\b", replacer_2, mm)
                #         ys[i].append(eval(result))
                return ans

        if m := re.findall(r"^parms(.*)", text, flags=re.MULTILINE):
            m = m[0]
            tex = re.sub(r"^parms.*", r"PARMS", text, flags=re.MULTILINE)
        else:
            tex = text

        for k in config.keys():
            tex = re.sub(r"(.*):(.*)", replacer, tex)
        tex = tex.replace("PARMS", f"parms{m}")

        settings = {}
        for line in tex.splitlines():
            if gr := re.findall(r"(.*): ?(.*)", line)[0]:
                settings[gr[0]] = gr[1]

        yy = getData("y")
        xx = getData("x")
        if yy == None:
            yy = [[a for a in range(len(xx[0]))]]
        elif xx == None:
            xx = [[a for a in range(len(yy[0]))]]

        while len(yy) < len(xx):
            yy.append(yy[-1])
        while len(xx) < len(yy):
            xx.append(xx[-1])

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

        plt.savefig(f"graphs/plot-{NUM}.png", dpi=200)
        plt.close()

        if "STAT" in settings["parms"]:
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
                text = f"Plot-{NUM} {settings["name"] if "name" in settings else ""} ({lg[i] if "legend" else "" in settings})\n"
                text += "\n".join(names[a] + ": " + f"{round(stat[a], 2):,}" for a in stat.keys())
                text += "\n\n"
                file.write(text)
            file.close()

        print(NUM, end=" / ")
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