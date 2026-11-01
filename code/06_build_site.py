"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; results, site data, outlines and city labels are embedded, data/points.json is loaded by the page.
10.5281/zenodo.23856736, https://doi.org/10.5281/zenodo.23856736 and https://blog.tristanhotham.com/2026/10/31/inventions-map/ stay as placeholders for the publisher. Facts stated in words are checked here."""
import csv
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
WDC = list(csv.DictReader(open(f"{DATA}/inventions_wikidata.csv", encoding="utf-8")))
EC = list(csv.DictReader(open(f"{DATA}/early_innovations.csv", encoding="utf-8")))
B = {p["label"]: p for p in R["centre"]["backbone"]}
KEEP = ("DOI", "DOI_URL", "BLOG_URL")

# ---------- facts stated in words ----------
conts = {"Fertile Crescent": "Asia", "Yangtze": "Asia", "Yellow River": "Asia", "Kuk Swamp": "Oceania", "Southern Mexico": "North America",
         "Amazon": "South America", "Titicaca": "South America", "Ethiopian": "Africa", "Sahel": "Africa", "West Africa": "Africa", "Eastern North America": "North America"}
far = R["early"]["indep"][0]
assert far["key"] == "farming" and len(far["origins"]) == 11 and len({v for k, v in conts.items() if any(k in o for o in far["origins"])}) == 5   # 'five continents'
assert R["early"]["writing_n"] == 4 and R["early"]["zero_n"] == 3
assert R["shift"]["europe_lead_from"] == "1500 to 1700" and B["1500 to 1700"]["shares"]["Europe"] == 100      # 'every landmark on the list is European'
assert R["shift"]["na_first_lead"] == "1950 to 2000" and R["shift"]["wd_na_first_lead"] == "1950 to 2000"
assert B["AD 1 to 1500"]["top"] == "East Asia"
assert all(B[p]["top"] == "West Asia and North Africa" for p in ("10,000 to 5000 BC", "5000 to 2000 BC", "2000 BC to AD 1"))
assert B["3.3 million to 100,000 years ago"]["top"] == "Sub-Saharan Africa" and "Sudan" in B["3.3 million to 100,000 years ago"]["where"]  # 'in Africa'
cn = [e["innovation"] for e in EC if e["country"] == "CHN" and 0 <= int(e["year_from"]) < 1500]
for nm in ("Paper", "Banknote", "Woodblock printing", "Porcelain", "Gunpowder", "Movable type"):
    assert nm in cn or (nm == "Paper" and any(e["innovation"] == "Paper" and e["country"] == "CHN" for e in EC)), nm
assert R["shift"]["eastasia_1950"] < 20 and R["shift"]["wd_europe_1950"] < R["shift"]["wd_na_1950"]
assert [c["name"] for c in R["cities"]["top"][:4]] == ["London", "New York", "Paris", "Vienna"]
lon = [w for w in WDC if w["city_area"] == "London"]
assert any(w["name"] == "computer" and "Babbage" in w["inventors"] for w in lon) and any("Berners-Lee" in w["inventors"] for w in lon)
assert R["bias"]["examples"]["car"]["inv"] == ["Ferdinand Verbiest"] and R["bias"]["examples"]["car"]["iso"] == "BEL"
assert R["bias"]["gunpowder"]["inv"] == ["Berthold Schwarz"]
gp = next(e for e in EC if e["innovation"] == "Gunpowder"); assert gp["year_from"] == "801" and gp["country"] == "CHN"
assert any(e["innovation"] == "Control of fire" and e["precision"] == "wide" for e in EC)
assert R["centuries_top"]["wd_1900s"] > R["centuries_top"]["wd_1800s"] > 10 * R["centuries_top"]["wd_before_1500"] / 2
for k in ("Glass", "Coins", "Water clock"):
    assert any(e["innovation"] == k and e["kind"] == "candidates" for e in EC), k
assert R["bias"]["wd_ratio"] > 5


def fill(tpl):
    def sub(m):
        if m.group(1) in KEEP:
            return m.group(0)
        return fmt(get(R, m.group(1)), m.group(3))
    return re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", sub, tpl)


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl)
    assert not re.search(r"\{\{(?!DOI\}\}|DOI_URL\}\}|BLOG_URL\}\})", html)
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
