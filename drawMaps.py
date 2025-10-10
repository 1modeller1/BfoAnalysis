import sys
from math import log10
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import box
from geopandas import gpd

import matplotlib.pyplot as plt
import sqlite3, os, re

NUM = 0

def drawWorldMap (okved, input, num, settings):

    db = sqlite3.connect(f"data/data-okved-{okved}.db")
    cursor = db.cursor()

    run = re.search(rf"^mapW: (.*)$", input, flags=re.MULTILINE).group(1)
    run += ", bfoStart.latitude, bfoStart.longitude"
    tables = list(set(re.findall(r"([^ ]*)\.", run) + ["bfoStart"]))
    tables = list(set([re.sub(r"(\(|\))", "", tab) for tab in tables]))
    raws = list(set(re.findall(r"([^ ]*\.[^ ,\n]*)", run)))
    runN = ",".join(["ROUND(" + a + ",2)" for a in re.findall(r"(?:,|^) ?(.*?)(?=,|$)", run)])

    com = f"SELECT{" DISTINCT" if "parms" in settings and "DIS" in settings["parms"] else ""} "
    com += f"{runN} FROM {tables[0]}\n"
    for tab in tables[1:]:
        com += f"JOIN {tab}\nON {tables[0]}.inn = {tab}.inn\n"
    if "period" in settings:
        com += f"WHERE {" and ".join(tab + f".period = {settings["period"]}" for tab in tables if not tab in ["bfoStart", "bfoStartPlus"])}"
    if "WHERE" in com:
        com += " and "
    else:
        com += "WHERE "
    com += " and ".join([a + " IS NOT NULL" for a in re.findall(r"(?:,|^)(.*?)(?=,|$)", run)])
    if "where" in settings:
        if "WHERE" in com:
            com += " and "
        else:
            com += "WHERE "
        com += settings["where"]
    com += "\n"
    if "sortBy" in settings:
        com += f"ORDER BY {settings["sortBy"]}"

    cursor.execute(com)
    values, lats, lons = [list(d) for d in zip(*cursor)]

    values = [log10(a) if a > 0 else 0.3 for a in values]
    maxD, minD = max(values), min(values)
    cValues = [round((v - minD) / (maxD - minD), 2) for v in values]

    colors = []
    for c in cValues:
        colors.append([round(1 - c, 2), c, 0])
    cValues = [c * 10 for c in cValues]

    plt.figure(figsize=(12,8))
    ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=105, central_latitude=60))
    ax.set_extent([27, 180, 41, 82], ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor='gray')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.COASTLINE)

    ax.scatter(lons, lats, s=cValues, c=values, cmap="RdYlGn", alpha=0.6, transform=ccrs.PlateCarree())

    if "name" in settings:
        plt.title(settings["name"])

    if not "maps" in os.listdir():
        os.mkdir("maps")
    plt.tight_layout()
    plt.savefig(f"maps/worldMap-{num}.png", dpi=200)

    plt.close()
    db.close()
    # plt.show()

def drawRegionMap (okved, input, num, settings):
    db = sqlite3.connect(f"data/data-okved-{okved}.db")
    cursor = db.cursor()

    run = re.search(rf"^mapR: (.*)$", input, flags=re.MULTILINE).group(1)
    run += ", bfoStart.latitude, bfoStart.longitude"
    tables = list(set(re.findall(r"([^ ]*)\.", run) + ["bfoStart"]))
    tables = list(set([re.sub(r"(\(|\))", "", tab) for tab in tables]))
    raws = list(set(re.findall(r"([^ ]*\.[^ ,\n]*)", run)))
    runN = ",".join(["ROUND(" + a + ",2)" for a in re.findall(r"(?:,|^) ?(.*?)(?=,|$)", run)])

    com = f"SELECT{" DISTINCT" if "parms" in settings and "DIS" in settings["parms"] else ""} "
    com += f"{runN} FROM {tables[0]}\n"
    for tab in tables[1:]:
        com += f"JOIN {tab}\nON {tables[0]}.inn = {tab}.inn\n"
    if "period" in settings:
        com += f"WHERE {" and ".join(tab + f".period = {settings["period"]}" for tab in tables if not tab in ["bfoStart", "bfoStartPlus"])}"
    if "WHERE" in com:
        com += " and "
    else:
        com += "WHERE "
    com += " and ".join([a + " IS NOT NULL" for a in re.findall(r"(?:,|^)(.*?)(?=,|$)", run)])
    if "where" in settings:
        if "WHERE" in com:
            com += " and "
        else:
            com += "WHERE "
        com += settings["where"]
    com += "\n"
    if "sortBy" in settings:
        com += f"ORDER BY {settings["sortBy"]}"

    cursor.execute(com)
    values, lats, lons = [list(d) for d in zip(*cursor)]

    values = [log10(a) if a > 0 else 0.2 for a in values]
    maxD, minD = max(values), min(values)
    cValues = [round((v - minD) / (maxD - minD), 2) for v in values]

    colors = []
    for c in cValues:
        colors.append([round(1 - c, 2), c, 0])
    cValues = [c * 10 for c in cValues]

    regions = gpd.read_file("regionsShape/gadm41_RUS_1.shp")
    regions["geometry"] = regions["geometry"].simplify(tolerance=0.1, preserve_topology=True)

    minx, miny, maxx, maxy = regions.total_bounds

    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([27, 180, 40, 82], crs=ccrs.PlateCarree())

    ocean = gpd.GeoDataFrame(geometry=[box(minx, miny - 5, maxx, maxy + 5)])
    ocean.plot(ax=ax, facecolor="#505050", edgecolor="none", transform=ccrs.PlateCarree())

    regions.plot(ax=ax, facecolor="gray", edgecolor="black", linewidth=0.5, transform=ccrs.PlateCarree())

    ax.scatter(lons, lats, s=cValues, c=values, cmap="RdYlGn", alpha=0.6, transform=ccrs.PlateCarree())

    if "name" in settings:
        plt.title(settings["name"])

    if not "maps" in os.listdir(): os.mkdir("maps")
    plt.tight_layout()
    plt.savefig(f"maps/regionMap-{num}.png", dpi=200)
    plt.close()
    db.close()

def simplePrepair (text):
    global NUM

    def replacer(match):
        before = match.group(1)
        after = match.group(2)
        if k.isupper():
            after = re.sub(rf"{k}\.", rf"{config[k]}.", after)
        else:
            after = re.sub(rf"\.{k}", rf".{config[k]}", after)
        return before + ":" + after

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
    elif re.search(rf"^mapR: (.*)$", tex, flags=re.MULTILINE):
        drawRegionMap(okved, tex, NUM, settings)
    print(NUM, end=" / ", flush=True)

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        fileName = args[0]
    else:
        fileName = "drawPlots.txt"
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
                simplePrepair(block)
                NUM += 1
        elif conf:
            match = re.match(r"([^ ]*) ?= ?([^ \n#]*)", line)
            if match != None:
                config[match.group(1)] = match.group(2)
        else:
            block += line
    if block != "":
        simplePrepair(block)