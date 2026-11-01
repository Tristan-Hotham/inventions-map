"""All the numbers (data/results.json), the clean CSV files and the page data (data/points.json, data/site.json).

Three layers:
  early     the hand-checked table of early innovations (code/early.py), prehistory to 1439
  timeline  English Wikipedia's Timeline of historic inventions, 1500 onwards (code/03_timeline.py)
  wikidata  Wikidata inventions with 5 or more sitelinks (code/02_filter.py), ranked by sitelinks
The 'backbone' for the centre of invention is early (before 1500) plus timeline (1500 on): two curated lists, each item
counted once (rows the page gives as alternatives share one count between them). Wikidata, which is far bigger but much
less even, is the second measure from 1700.
Centre of invention: the weighted mean latitude and mean longitude of the points in each period (the 'centre of gravity'
on a flat map; a mean on the globe would be pulled towards the North Pole when Europe, America and Japan are averaged).
"""
import csv, math
from collections import Counter, defaultdict
from common import *

G = jload(f"{WORK}/geo.json"); meta = G["meta"]; BIG = G["big"]
E, T, W = G["early"], G["tl"], G["wd"]
J1 = jload(f"{WORK}/items.json"); J2 = jload(f"{WORK}/classified.json")
RN = [r for r, _ in REGIONS]
R = {"meta": {"page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG, "retrieved": RETRIEVED, "min_sl": 5}}

PER = [(-4e6, -98050, "3.3 million to 100,000 years ago"), (-98050, -10050, "100,000 to 12,000 years ago"),
       (-10050, -5000, "10,000 to 5000 BC"), (-5000, -2000, "5000 to 2000 BC"), (-2000, 0, "2000 BC to AD 1"),
       (0, 1500, "AD 1 to 1500"), (1500, 1700, "1500 to 1700"), (1700, 1800, "1700s"),
       (1800, 1850, "1800 to 1850"), (1850, 1900, "1850 to 1900"), (1900, 1950, "1900 to 1950"), (1950, 2000, "1950 to 2000"),
       (2000, 2027, "2000 to 2026")]
SHORT = ["3.3m to 100k ya", "100k to 12k ya", "10,000 to 5000 BC", "5000 to 2000 BC", "2000 BC to AD 1", "AD 1 to 1500",
         "1500 to 1700", "1700s", "1800 to 1850", "1850 to 1900", "1900 to 1950", "1950 to 2000", "2000 to 2026"]


def per_of(y):
    for i, (a, b, _) in enumerate(PER):
        if a <= y < b:
            return i
    return None


def smean(pts):
    """pts: (lat, lon, w) -> weighted mean latitude, mean longitude, and the mean distance (km) of the points from it."""
    sw = sum(w for _, _, w in pts)
    la = sum(a * w for a, _, w in pts) / sw; lo = sum(b * w for _, b, w in pts) / sw
    d = sum(w * 111.2 * math.hypot(a - la, (b - lo) * math.cos(math.radians((a + la) / 2))) for a, b, w in pts) / sw
    return round(la, 2), round(lo, 2), round(d)


def nearest_label(lat, lon):
    """A plain description of where a centre point falls: the country it is in, or 'sea' with the nearest country."""
    from shapely.geometry import shape, Point
    best = None
    for f in WORLD["features"]:
        g = SH[f["properties"]["iso"]]
        d = g.distance(Point(lon, lat))
        if best is None or d < best[0]:
            best = (d, f["properties"]["iso"])
    nm = meta.get(best[1], {}).get("name", best[1])
    return nm if best[0] == 0 else f"open sea, nearest land {nm}"


from shapely.geometry import shape
WORLD = jload(f"{DATA}/world.json")
SH = {}
for f in WORLD["features"]:
    g = shape(f["geometry"]); i = f["properties"]["iso"]
    SH[i] = g if i not in SH else SH[i].union(g)

# ---------- source and filtering ----------
why = Counter(d["how"] for d in J2["items"] if not d["cat"])
kept_any = sum(1 for d in J2["items"] if d["cat"])
meth = Counter(w["meth"] or "none" for w in W)
placed = [w for w in W if w["reg"]]
dated = [w for w in W if w["y"] is not None]
R["source"] = {"n_rows": J1["n_rows"], "n_items": len(J1["items"]), "n_tech": kept_any, "n_tech_pct": 100 * kept_any / len(J1["items"]),
               "n": len(W), "n_placed": len(placed), "placed_pct": 100 * len(placed) / len(W),
               "n_made": meth["made"], "n_inventor": meth["inventor"], "n_country": meth["country"], "n_unplaced": meth["none"],
               "inventor_pct": 100 * meth["inventor"] / len(placed), "made_pct": 100 * meth["made"] / len(placed),
               "n_dated": len(dated), "dated_pct": 100 * len(dated) / len(W), "n_dated_placed": sum(1 for w in dated if w["reg"]),
               "n_with_inventor": sum(1 for w in W if w["inv_n"]), "with_inventor_pct": 100 * sum(1 for w in W if w["inv_n"]) / len(W),
               "drop_class": why["dropped class"], "drop_nolabel": why["no English label"], "drop_other": why["not a technology class"] + why["no technology word"],
               "n_sl5_all": sum(1 for d in J1["items"] if d["sl"] >= 5), "n_early_dupe": sum(1 for w in W if w["in_early"])}
R["source"]["by_cat"] = [{"cat": k, "name": CATNAME[k], "n": sum(1 for w in W if w["cat"] == k)} for k, _, _ in CATS]

# ---------- early innovations ----------
keys = list(dict.fromkeys(e["key"] for e in E))
groups = {}
for e in E:
    groups.setdefault(e["key"], []).append(e)
indep = [{"key": k, "name": groups[k][0]["n"], "n": len(groups[k]), "origins": [g["origin"] for g in groups[k]],
          "y0": min(g["y0"] for g in groups[k]), "y1": max(g["y1"] for g in groups[k])} for k in keys if groups[k][0]["gtype"] == "independent"]
R["early"] = {"n_rows": len(E), "n_innov": len(keys), "n_pages": len({s for e in E for s in e["src"]}),
              "n_indep": len(indep), "indep": indep, "farming_n": len(groups["farming"]), "writing_n": len(groups["writing"]),
              "zero_n": len(groups["zero"]), "bronze_n": len(groups["bronze"]),
              "n_candidates": len({e["key"] for e in E if e["gtype"] == "candidates"}), "n_finds": len({e["key"] for e in E if e["gtype"] == "finds"}),
              "prec": dict(Counter(e["prec"] for e in E)), "oldest": yearname(min(e["y0"] for e in E)),
              "china_pre1500": sum(1 for k in keys if groups[k][0]["iso"] == "CHN" and groups[k][0]["y"] >= 0),
              "n_ad_pre1500": sum(1 for k in keys if groups[k][0]["y"] >= 0)}
R["early"]["china_ad_pct"] = 100 * R["early"]["china_pre1500"] / R["early"]["n_ad_pre1500"]

# ---------- timeline ----------
tm = Counter(r.get("meth") or "none" for r in T)
R["timeline"] = {"n": len(T), "n_placed": sum(1 for r in T if r["reg"]), "by_meth": dict(tm), "first": min(r["y0"] for r in T),
                 "n_1800": sum(1 for r in T if r["y0"] >= 1800), "n_hand": tm["hand"], "hand_pct": 100 * tm["hand"] / len(T)}

# ---------- backbone points, periods, centre, region shares ----------
BB = [{"lat": e["lat"], "lon": e["lon"], "w": e["w"], "y": e["y"], "reg": e["reg"], "iso": e["iso"], "src": "early"} for e in E]
BB += [{"lat": r["lat"], "lon": r["lon"], "w": 1.0, "y": r["y"], "reg": r["reg"], "iso": r["iso"], "src": "timeline"} for r in T if r["reg"] and r["y"] >= 1500]
WD = [{"lat": w["lat"], "lon": w["lon"], "w": 1.0, "y": w["y"], "reg": w["reg"], "iso": w["iso"]} for w in W if w["reg"] and w["y"] is not None and not w["in_early"]]


def periods(P, first=0, min_n=1):
    out = []
    for i, (a, b, lab) in enumerate(PER):
        if i < first:
            continue
        S = [p for p in P if a <= p["y"] < b]
        if len(S) < min_n:
            continue
        la, lo, rr = smean([(p["lat"], p["lon"], p["w"]) for p in S])
        tot = sum(p["w"] for p in S)
        sh = {r: 100 * sum(p["w"] for p in S if p["reg"] == r) / tot for r in RN}
        top = max(sh, key=sh.get)
        out.append({"i": i, "label": lab, "short": SHORT[i], "n": round(tot, 2), "n_items": len(S), "lat": la, "lon": lo, "r": rr,
                    "where": nearest_label(la, lo), "shares": {k: round(v, 2) for k, v in sh.items()}, "top": top, "top_pct": sh[top]})
    return out


R["centre"] = {"backbone": periods(BB), "wikidata": periods(WD, first=7, min_n=15)}
B = {p["i"]: p for p in R["centre"]["backbone"]}
WP = {p["i"]: p for p in R["centre"]["wikidata"]}
R["centre"]["min_wd_n"] = min(p["n_items"] for p in R["centre"]["wikidata"])
# headline shares: West Asia's lead, China's medieval share, Europe's peak, North America's rise
R["shift"] = {
    "wana_neolithic": B[2]["shares"]["West Asia and North Africa"], "wana_bronze": B[3]["shares"]["West Asia and North Africa"],
    "eastasia_ad1": B[5]["shares"]["East Asia"], "n_ad1": B[5]["n_items"],
    "europe_1700": B[7]["shares"]["Europe"], "europe_1800": B[8]["shares"]["Europe"], "europe_1850": B[9]["shares"]["Europe"],
    "na_1850": B[9]["shares"]["North America"], "na_1950": B[11]["shares"]["North America"], "na_2000": B[12]["shares"]["North America"],
    "europe_1950": B[11]["shares"]["Europe"], "eastasia_1950": B[11]["shares"]["East Asia"],
    "wd_europe_1800": WP[8]["shares"]["Europe"], "wd_na_1950": WP[11]["shares"]["North America"], "wd_europe_1950": WP[11]["shares"]["Europe"],
    "wd_eastasia_1950": WP[11]["shares"]["East Asia"], "eastasia_1950_n": B[11]["shares"]["East Asia"],
    "wd_2000_n": sum(1 for p in WD if p["y"] >= 2000),
}
# first period in which North America has the largest share
R["shift"]["na_first_lead"] = next(p["label"] for p in R["centre"]["backbone"] if p["top"] == "North America")
R["shift"]["wd_na_first_lead"] = next(p["label"] for p in R["centre"]["wikidata"] if p["top"] == "North America")
R["shift"]["europe_lead_from"] = next(p["label"] for p in R["centre"]["backbone"] if p["top"] == "Europe")

# ---------- per century ----------
cent = []
for c in range(-1000, 2001, 100):
    nb = sum(p["w"] for p in BB if c <= p["y"] < c + 100)
    nw = sum(1 for w in W if w["y"] is not None and c <= w["y"] < c + 100 and not w["in_early"])
    cent.append({"c": c, "label": (f"{-c // 100}th century BC" if c < 0 else f"{c // 100 + 1}th century"), "backbone": round(nb, 2), "wikidata": nw})
R["centuries"] = cent
R["centuries_top"] = {"wd_1800s": next(c["wikidata"] for c in cent if c["c"] == 1800), "wd_1900s": next(c["wikidata"] for c in cent if c["c"] == 1900),
                      "wd_before_1500": sum(1 for w in W if w["y"] is not None and w["y"] < 1500),
                      "wd_after_1800_pct": 100 * sum(1 for w in W if w["y"] is not None and w["y"] >= 1800) / len(dated)}
# eras for the deep past (counts of early innovations)
R["eras"] = [{"label": p["label"], "short": p["short"], "backbone": p["n"]} for p in R["centre"]["backbone"]]

# ---------- cities and countries (Wikidata layer; points of their own) ----------
ar = defaultdict(list)
for w in W:
    if w["area"] is not None:
        ar[w["area"]].append(w)
cities = []
for k, L in ar.items():
    c = BIG[k]
    cities.append({"name": c[0], "lon": c[1], "lat": c[2], "pop": c[3], "iso": c[4], "n": len(L), "n_made": sum(1 for w in L if w["meth"] == "made"),
                   "n_inv": sum(1 for w in L if w["meth"] == "inventor"), "sl": sum(w["sl"] for w in L),
                   "top": [w["n"] for w in sorted(L, key=lambda w: -w["sl"])[:4]]})
cities.sort(key=lambda c: (-c["n"], -c["sl"]))
for c in cities:
    c["country"] = meta.get({"GBR": "GBR"}.get(c["iso"], c["iso"]), {}).get("name", c["iso"])
R["cities"] = {"top": cities[:25], "n_areas": len(cities), "n_in_area": sum(c["n"] for c in cities),
               "top10_pct": 100 * sum(c["n"] for c in cities[:10]) / len(placed)}
cn = Counter(w["iso"] for w in placed)
R["countries"] = {"top": [{"iso": i, "name": meta[i]["name"], "n": n, "pct": 100 * n / len(placed)} for i, n in cn.most_common(20)], "n": len(cn)}
rg = Counter(w["reg"] for w in placed)
R["regions"] = [{"reg": r, "n": rg[r], "pct": 100 * rg[r] / len(placed)} for r in RN]
pop = Counter(); tot = 0
for i, m in meta.items():
    if m["reg"]:
        pop[m["reg"]] += m["pop"]; tot += m["pop"]
R["bias"] = {
    "pop_pct": {r: 100 * pop[r] / tot for r in RN},
    "wd_eu_na_pct": 100 * (rg["Europe"] + rg["North America"]) / len(placed),
    "pop_eu_na_pct": 100 * (pop["Europe"] + pop["North America"]) / tot,
    "tl_eu_na_pct": 100 * sum(1 for r in T if r["reg"] in ("Europe", "North America")) / sum(1 for r in T if r["reg"]),
    "wd_ssa": rg["Sub-Saharan Africa"], "wd_ssa_pct": 100 * rg["Sub-Saharan Africa"] / len(placed),
    "pop_ssa_pct": 100 * pop["Sub-Saharan Africa"] / tot, "wd_sa": rg["South Asia"], "wd_sa_pct": 100 * rg["South Asia"] / len(placed),
    "pop_sa_pct": 100 * pop["South Asia"] / tot, "wd_ea_pct": 100 * rg["East Asia"] / len(placed), "pop_ea_pct": 100 * pop["East Asia"] / tot,
    "early_named": 0, "wd_named_pct": R["source"]["with_inventor_pct"],
}
tlp = [r for r in T if r["reg"]]
R["timeline_regions"] = {r: 100 * sum(1 for x in tlp if x["reg"] == r) / len(tlp) for r in RN}
R["bias"]["wd_ratio"] = R["bias"]["wd_eu_na_pct"] / R["bias"]["pop_eu_na_pct"]
gp = next(w for w in W if w["n"] == "gunpowder")
R["bias"]["gunpowder"] = {"inv": gp["inv"][:1], "place": gp["place"], "reg": gp["reg"], "y": gp["y"], "meth": gp["meth"]}
multi = [w for w in W if w["inv_n"] > 1 and w["reg"]]
R["bias"]["multi_n"] = len(multi); R["bias"]["multi_pct"] = 100 * len(multi) / len(placed)
R["bias"]["examples"] = {n: next({"place": w["place"], "inv": w["inv"][:1], "inv_n": w["inv_n"], "iso": w["iso"]} for w in W if w["n"] == n) for n in ("car", "photography", "computer", "television")}
R["famous"] = [{"q": w["q"], "n": w["n"], "sl": w["sl"], "y": w["y"], "place": w["place"], "meth": w["meth"], "iso": w["iso"], "inv": w["inv"][:2]}
               for w in sorted(W, key=lambda w: -w["sl"])[:30]]
R["famous_placed_pct"] = 100 * sum(1 for f in R["famous"][:30] if f["iso"]) / 30
R["n_regions"] = len(RN)
jsave(R, f"{DATA}/results.json", indent=1)

# ---------- CSV files ----------
def wcsv(name, rows, cols):
    with open(f"{DATA}/{name}", "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f); wr.writerow(cols)
        for r in rows:
            wr.writerow([dash(r.get(c, "")) if isinstance(r.get(c, ""), str) else ("" if r.get(c) is None else r.get(c)) for c in cols])


MLAB = {"made": "location of invention or discovery (P189/P1071)", "inventor": "inventor's birthplace (P61, P19)", "country": "country of origin centre (P495)", None: ""}
wcsv("inventions_wikidata.csv", [dict(w, wikidata=w["q"], name=w["n"], sitelinks=w["sl"], year=w["y"], category=CATNAME[w["cat"]], placement_method=MLAB[w["meth"]],
                                      inventors="; ".join(w["inv"]), country=w["iso"] or "", region=w["reg"] or "", classes="; ".join(w["cls"]),
                                      city_area=(BIG[w["area"]][0] if w["area"] is not None else ""), also_in_early_table=int(w["in_early"]))
                                 for w in sorted(W, key=lambda w: -w["sl"])],
     ["wikidata", "name", "sitelinks", "year", "category", "classes", "placement_method", "place", "lat", "lon", "country", "region", "city_area", "inventors", "also_in_early_table"])
PG = G["pages"]
wcsv("early_innovations.csv", [dict(e, id=e["id"], innovation=e["n"], category=CATNAME[e["cat"]], kind=e["gtype"], year_from=e["y0"], year_to=e["y1"],
                                     dates=(yearname(e["y0"]) if e["y0"] == e["y1"] else f"{yearname(e['y0'])} to {yearname(e['y1'])}"),
                                     precision=e["prec"], weight=round(e["w"], 3), sources="; ".join(PG[s][0] for s in e["src"]),
                                     source_urls="; ".join(PG[s][1] for s in e["src"]), country=e["iso"] or "", region=e["reg"], wikidata=e["wd"])
                                for e in E],
     ["id", "innovation", "category", "kind", "origin", "year_from", "year_to", "dates", "lat", "lon", "precision", "country", "region", "weight", "sources", "source_urls", "quote", "wikidata"])
TM = {"inventor": "birthplace of the named inventor (Wikidata)", "place": "place named in the entry", "country": "country named in the entry", "hand": "country of the work, by hand (not in the entry)", None: ""}
wcsv("timeline_1500_on.csv", [dict(r, year_from=r["y0"], year_to=r["y1"], entry=r["t"], category=CATNAME[r["cat"]], placement_method=TM[r.get("meth")],
                                    person=r.get("person", ""), place=r.get("place", ""), country=r["iso"] or "", region=r["reg"] or "") for r in T],
     ["year_from", "year_to", "entry", "category", "placement_method", "person", "place", "lat", "lon", "country", "region"])
cols = ["period", "source", "items", "weighted_n", "centre_lat", "centre_lon", "centre_where"] + [f"share_{r}" for r in RN]
rows = []
for src in ("backbone", "wikidata"):
    for p in R["centre"][src]:
        rows.append(dict({"period": p["label"], "source": src, "items": p["n_items"], "weighted_n": p["n"], "centre_lat": p["lat"], "centre_lon": p["lon"],
                          "centre_where": p["where"]}, **{f"share_{r}": round(p["shares"][r], 1) for r in RN}))
wcsv("centre_of_invention.csv", rows, cols)
wcsv("centuries.csv", cent, ["c", "label", "backbone", "wikidata"])
wcsv("cities.csv", [dict(c, top_inventions="; ".join(c["top"])) for c in cities],
     ["name", "country", "lat", "lon", "pop", "n", "n_made", "n_inv", "sl", "top_inventions"])

# ---------- page data ----------
r4 = lambda v: None if v is None else round(v, 3)
PTS = {"cats": [[k, n, c] for k, n, c in CATS], "regions": [[r, c] for r, c in REGIONS],
       "early": [[e["id"], e["key"], e["n"], e["cat"], e["gtype"], e["origin"], e["y0"], e["y1"], r4(e["lat"]), r4(e["lon"]), e["prec"], "+".join(e["src"]), e["quote"], e["norig"]] for e in E],
       "tl": [[r["y0"], r["y1"], r["t"], r["cat"], r.get("meth"), r.get("person", ""), r.get("place", ""), r4(r.get("lat")), r4(r.get("lon"))] for r in T if r.get("lat") is not None],
       "wd": [[w["q"], w["n"], w["sl"], w["y"], w["cat"], w["meth"], w["place"], r4(w["lat"]), r4(w["lon"]), "; ".join(w["inv"][:3]), w["inv_n"]]
              for w in sorted(W, key=lambda w: -w["sl"]) if w["lat"] is not None and not w["in_early"]],
       "pages": {k: v for k, v in PG.items()}}
jsave(PTS, f"{DATA}/points.json")
SITE = {"centre": R["centre"], "cent": cent, "cities": cities[:25], "regions": R["regions"], "bias": R["bias"], "cname": {i: m["name"] for i, m in meta.items()}}
jsave(SITE, f"{DATA}/site.json")
print(json.dumps({k: R[k] for k in ("source", "early", "timeline", "shift")}, indent=0, ensure_ascii=False)[:3000])
print("cities", [(c["name"], c["n"]) for c in cities[:12]])
print("countries", [(c["iso"], c["n"]) for c in R["countries"]["top"][:10]])
for src in ("backbone", "wikidata"):
    for p in R["centre"][src]:
        print(src, p["label"], p["n_items"], p["lat"], p["lon"], p["where"], p["top"], round(p["top_pct"]))
print("bias", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in R["bias"].items() if k != "pop_pct"})
print("points.json", os.path.getsize(f"{DATA}/points.json") // 1024, "KB")
