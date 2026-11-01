"""Place every invention on the map, give it a present-day country, a world region and (where it has a point of its own)
a city area. Also checks the hand table of early innovations against the Wikipedia page text and builds the outlines.

Placement of a Wikidata invention, the first of these that exists:
  1 'made'     location of discovery (P189) or location of creation (P1071) with coordinates: 'invented at'
  2 'inventor' birthplace (P19) of the first-listed inventor (P61) with coordinates: 'inventor from', not 'invented at'
  3 'country'  the country of origin (P495), at the country's Wikidata coordinate: a rough country centre
Hand-table rows ('early', code/early.py) keep their own rough points and precision.
Country: the present-day Natural Earth (1:10m) country the point falls in. Region: see REGION_OF below.
City areas: points of kind 1 or 2 within 25 km of a Natural Earth populated place of 150,000 people or more go to the
nearest such place; a place within 25 km of a bigger one is merged into it (so Charlottenburg counts with Berlin).
"""
import math, html as H, unicodedata
from collections import Counter
from shapely.geometry import shape, mapping, Point
from shapely.strtree import STRtree
from common import *
import early

FIX = {"CNM": "CYP", "ESB": "CYP", "WSB": "CYP", "PSX": "PSE", "SAH": "ESH", "KAS": "IND"}
iso_of = lambda p: FIX.get(p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"], p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"])
NAFR = {"DZA", "EGY", "LBY", "MAR", "TUN", "ESH", "SDN"}
NAM = {"USA", "CAN", "GRL", "BMU", "SPM"}
CAU = {"GEO", "ARM", "AZE"}


def region_of(iso, meta):
    m = meta.get(iso)
    if not m:
        return None
    c, s = m["cont"], m["sub"]
    if iso in NAM:
        return "North America"
    if iso in NAFR or iso == "IRN" or iso in CAU or s == "Western Asia":
        return "West Asia and North Africa"
    if c == "Europe":
        return "Europe"
    if c in ("North America", "South America"):
        return "Latin America"
    if c == "Africa":
        return "Sub-Saharan Africa"
    if s == "Southern Asia":
        return "South Asia"
    if s == "Eastern Asia":
        return "East Asia"
    if s == "Central Asia":
        return "Central Asia, Siberia and the steppe"
    return "Southeast Asia and Oceania"


def rnd(c, k=2):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(c[0], k), round(c[1], k)]
    return [rnd(x, k) for x in c]


# ---------- outlines and countries ----------
W50 = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
feats = []
for f in W50["features"]:
    p = f["properties"]; iso = iso_of(p)
    g = shape(f["geometry"]).simplify(0.04, preserve_topology=True)
    if g.is_empty or iso == "ATA":
        continue
    gm = mapping(g)
    feats.append({"type": "Feature", "properties": {"iso": iso}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")
W10 = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
geoms, meta = [], {}
NAMES = {"KOS": "Kosovo", "PSE": "Palestine", "CYP": "Cyprus", "TWN": "Taiwan", "HKG": "Hong Kong", "CZE": "Czech Republic", "MKD": "North Macedonia",
         "COD": "DR Congo", "COG": "Republic of the Congo", "GBR": "United Kingdom", "KOR": "South Korea", "PRK": "North Korea", "RUS": "Russia",
         "IRN": "Iran", "SYR": "Syria", "VNM": "Vietnam", "LAO": "Laos", "BHS": "Bahamas", "GMB": "Gambia", "NLD": "Netherlands", "PHL": "Philippines",
         "CIV": "Ivory Coast", "TZA": "Tanzania", "BOL": "Bolivia", "VEN": "Venezuela", "MDA": "Moldova", "USA": "United States", "CHN": "China", "SWZ": "Eswatini"}
for f in W10["features"]:
    p = f["properties"]; iso = iso_of(p)
    geoms.append((iso, shape(f["geometry"]).buffer(0)))
    if iso in meta and (meta[iso]["pop"] or 0) >= (p["POP_EST"] or 0):
        continue
    meta[iso] = {"name": NAMES.get(iso, p["NAME_EN"] or p["NAME"]), "cont": p["CONTINENT"], "sub": p["SUBREGION"], "pop": p["POP_EST"] or 0}
for k in meta:
    if meta[k]["cont"] == "Seven seas (open ocean)":
        meta[k]["cont"] = "Africa" if meta[k]["sub"] in ("Eastern Africa", "Southern Africa") else "Asia" if "Asia" in meta[k]["sub"] else "Oceania"
for k in meta:
    meta[k]["reg"] = region_of(k, meta)
tree = STRtree([g for _, g in geoms])


def at(lon, lat):
    pt = Point(lon, lat)
    hit = [geoms[i][0] for i in tree.query(pt) if geoms[i][1].covers(pt)]
    if hit:
        return hit[0]
    near = [(geoms[i][1].distance(pt), geoms[i][0]) for i in tree.query(pt.buffer(0.3))]
    near = [x for x in near if x[0] < 0.3]
    return min(near)[1] if near else None


def km(lon1, lat1, lon2, lat2):
    a = math.sin(math.radians(lat2 - lat1) / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(min(1, a)))


P = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
BIG = sorted([(re.sub(r"\s+", " ", p["properties"]["name"]), p["properties"]["longitude"], p["properties"]["latitude"], int(p["properties"]["pop_max"] or 0), p["properties"]["adm0_a3"])
              for p in P if (p["properties"]["pop_max"] or 0) >= 150_000], key=lambda c: -c[3])
keep = []
for c in BIG:
    if not any(km(c[1], c[2], k[1], k[2]) <= 25 for k in keep):
        keep.append(c)
BIG = keep
btree = STRtree([Point(c[1], c[2]) for c in BIG])


def area_of(lon, lat):
    best = None
    for i in btree.query(Point(lon, lat).buffer(0.5)):
        c = BIG[i]; d = km(lon, lat, c[1], c[2])
        if d <= 25 and (best is None or d < best[0]):
            best = (d, int(i))
    return best[1] if best else None


# ---------- the hand table: check every quote against its page ----------
def page_text(f):
    h = jload(f"{RAW}/{f}")["html"]
    h = re.sub(r'<style.*?</style>|<sup[^>]*class="reference.*?</sup>', "", h, flags=re.S)
    return H.unescape(re.sub(r"<[^>]+>", " ", h))


def nz(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"(\d)\s*[–-]\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"[–—-]", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


TXT = {k: nz(page_text(f)) for k, f in early.FILES.items()}
REV = {k: jload(f"{RAW}/{f}")["revid"] for k, f in early.FILES.items()}
E = []
for i, r in enumerate(early.ROWS):
    key, name, cat, gtype, origin, y0, y1, lat, lon, prec, src, quote, extra = r
    srcs = [src] + ([extra["src2"]] if "src2" in extra else [])
    for frag in re.split(r"\.\.\.|;|\(2nd century BC\)", quote):
        f = nz(frag)
        if len(f) >= 8:
            assert any(f in TXT[s] for s in srcs), (key, origin, frag)
    assert y0 <= y1 and cat in CATNAME, (key, y0, y1)
    iso = at(lon, lat)
    reg = extra.get("reg") or (meta[iso]["reg"] if iso in meta else None)
    assert reg, (key, origin)
    E.append({"id": f"E{i + 1:03d}", "key": key, "n": name, "cat": cat, "gtype": gtype, "origin": origin, "y0": y0, "y1": y1, "y": (y0 + y1) / 2,
              "lat": lat, "lon": lon, "prec": prec, "src": srcs, "quote": quote, "wd": extra.get("wd", ""), "iso": iso, "reg": reg})
nalt = Counter(e["key"] for e in E if e["gtype"] == "candidates")
for e in E:
    e["w"] = 1 / nalt[e["key"]] if e["gtype"] == "candidates" else 1.0
    e["norig"] = sum(1 for x in E if x["key"] == e["key"])
print("early rows", len(E), "innovations", len({e['key'] for e in E}), Counter(e["gtype"] for e in E))

# ---------- Wikidata inventions ----------
J = jload(f"{WORK}/classified.json")
K = set(J["keep"]); EWD = {e["wd"] for e in E if e["wd"]}
how = Counter(); W = []
for d in J["items"]:
    if d["q"] not in K:
        continue
    pt, meth, place, inv = None, None, "", None
    for l in d["loc"]:
        if l["p"] in ("P189", "P1071") and l["pt"]:
            pt, meth, place = l["pt"], "made", l["n"]; break
    if not pt:
        for e in d["inv"]:
            if e["pt"]:
                pt, meth, place, inv = e["pt"], "inventor", e["bp"], e; break
    if not pt:
        for l in d["loc"]:
            if l["p"] == "P495" and l["pt"]:
                pt, meth, place = l["pt"], "country", l["n"]; break
    how[meth or "none"] += 1
    iso = at(*pt) if pt else None
    if not iso and pt:
        how["point outside any country"] += 1
    w = {"q": d["q"], "n": d["n"], "sl": d["sl"], "y": d["y"], "cat": d["cat"], "cls": d["cls"][:3], "meth": meth, "place": place,
         "lon": pt[0] if pt else None, "lat": pt[1] if pt else None, "iso": iso, "reg": meta[iso]["reg"] if iso in meta else None,
         "inv": [e["n"] for e in d["inv"] if e["n"]][:4], "inv_n": len(d["inv"]), "inv_cit": (inv or {}).get("cit", [])[:2],
         "in_early": d["q"] in EWD,
         "area": area_of(*pt) if pt and meth in ("made", "inventor") else None}
    W.append(w)
print("wikidata kept", len(W), dict(how), "also in hand table", sum(w["in_early"] for w in W))
# ---------- the modern timeline (03_timeline.py) ----------
T = jload(f"{WORK}/timeline.json")
TL_CAT = [(re.compile(p, re.I), c) for p, c in [
    (r"vaccin|stethoscope|anesthe|anaesthe|morphine|penicillin|x-ray|radiograph|hypodermic|surgical|rubber glove|defibrillator|contracepti|DNA|in vitro|genetic|endoscopy|pancreas|mrna|crispr|synthetic organism|wheelchair|inoculates|\\bgene\\b", "medicine"),
    (r"rifl|\bgun\b|cannon|missile|metal-cylinder rockets|bomb|weapon|smokeless powder|nitroglycerin|dynamite|military tanks|flintlock|thermonuclear|Pu-239", "weapons"),
    (r"telegraph|telephone|\bradio\b|television|computer|transistor|integrated circuit|MOSFET|microprocessor|internet|\bweb\b|network|\bdisk|memory|semaphore|satellite|search engine|smartphone|phone|video game|game console|\bDVD|CD-ROM|Global Positioning|cellular|e-commerce|social media|podcast|YouTube|Wikipedia|Friendster|Android|iPhone|Kindle|blockchain|NFT|quantum|cloud computing|Artificial Intelligence|calculat|cryptography|Transmission Control|touch|graphical user|fiber optic|sim card|Bluetooth|media player|audio compression|digital video|App store|floppy|vacuum tube|Fleming valve|crystal oscillator|Bertie|Logic Theorist|robot|exoskeleton|tape recorder|home automation|Tetris|Mobile web|antenna|laptop|solid-state|dialup|i-mode|wavelength|Lidar|magnetron|Analog", "comms"),
    (r"steamboat|locomotive|automobile|auto-mobile|\bcar\b|bicycle|airship|dirigible|balloon|parachute|flights?\b|turbo-jet|ramjet|tram\b|tire\b|hovercraft|tunnel|elevator|intermodal|Shinkansen|spacecraft|Space Shuttle|space station|self-driving|dandy horse|steam-powered vehicle|dry dock|rebreather|ejector seat|liquid fueled rocket|multi-use rocket|tractor", "transport"),
    (r"telescope|microscop|barometer|clock|thermometer|cloud chamber|radiocarbon|backstaff|slide rule|wristwatch|metal detector|radiometer|holography|laser|Leyden jar|phase-contrast|electron microscope|Toroidal", "science"),
    (r"newspaper|printing|lithograph|paper machine|wood pulp|Braille|Morse code|Projection map|ballpoint|blueprint", "writing"),
    (r"piano|photograph|daguerreotype|heliography|phonograph|kinetoscope|cinematograph|phonautograph|Rubik|color photography|\bfilm", "culture"),
    (r"refrigerat|ice making|pressure-cooker|friction match|lighter|lawn mower|sewing machine|safety pin|zipper|lock\b|toilet|vacuum cleaner|gas stove|oven|safety lamp|cardboard box|stocking frame|electronic cigarette", "home"),
    (r"canning|pasteuri|fertilizer|superphosphate|threshing|reaping|cotton gin|three-point hitch|Haber process", "food"),
    (r"engine|turbine|battery|voltaic pile|fuel cell|electric motor|generator|electromagnet|induction|relay|transformer|reactor|fission|steam|vacuum pump|compressor|accumulator|arc lamp|light bulb|incandescent|photovoltaic|solar|wind turbine|electric current|four-stroke|dry cell|rotary electromechanical|Geissler|ball screw|hot blast|power distribution", "energy"),
]]
for r in T["rows"]:
    r["iso"] = at(r["lon"], r["lat"]) if r.get("lat") is not None else None
    if r.get("iso_hand"):
        r["iso"] = r["iso_hand"]
    r["reg"] = meta[r["iso"]]["reg"] if r["iso"] in meta else None
    r["cat"] = next((c for rx, c in TL_CAT if rx.search(r["t"])), "tools")
    r["area"] = area_of(r["lon"], r["lat"]) if r.get("meth") in ("inventor", "place") else None
print("timeline", len(T["rows"]), "placed", sum(1 for r in T["rows"] if r["reg"]), Counter(r["reg"] for r in T["rows"]).most_common(4))
jsave({"early": E, "wd": W, "tl": T["rows"], "tl_revid": T["revid"], "meta": meta, "big": BIG, "revid": REV, "pages": early.PAGES}, f"{WORK}/geo.json")

cities = []
for f in P:
    p = f["properties"]; pop = p.get("pop_max") or 0
    if pop >= 150000 or p.get("adm0cap") == 1:
        cities.append({"name": re.sub(r"\s+", " ", p["name"]), "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(pop)})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{DATA}/cities.json")
print("cities", len(cities), "big", len(BIG), "world", os.path.getsize(f"{DATA}/world.json") // 1024, "KB")
