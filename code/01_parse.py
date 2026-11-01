"""Parse the three QLever TSVs into one record per Wikidata item (written to WORK/items.json).

Rules
- One record per item. Lexemes (L...) and blank nodes (Wikidata 'unknown value') are dropped.
- Date: the earliest parsable P575 year (BC years are negative; values like -1200000 are kept). Unknown values are ignored.
- Classes: the English labels of the item's instance-of (P31) classes; items with no P31 class (common for general kinds
  of thing such as 'refrigerator', which Wikidata describes with subclass-of instead) have an empty list.
- Inventors: each P61 value with its label, birthplace label, birthplace point and citizenship label.
- Locations: P189 (location of discovery) and P1071 (location of creation) with their points; P495 (country of origin)
  with the country's point.
"""
import csv, sys
from collections import defaultdict
from common import *

csv.field_size_limit(sys.maxsize)
POINT = re.compile(r"POINT\(([-\d.eE+]+) ([-\d.eE+]+)\)")
YEAR = re.compile(r'^"?(-?\d{1,7})-\d\d-\d\dT')


def val(v):
    v = (v or "").strip()
    if "/.well-known/genid/" in v:
        return ""
    if v.startswith("<" + WD):
        return v[len(WD) + 1:-1]
    m = re.match(r'^"(.*)"(@[\w-]+|\^\^<[^>]+>)?$', v, re.S)
    if m:
        return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
    return v


def pt(v):
    m = POINT.match(v or "")
    if not m:
        return None
    lon, lat = float(m.group(1)), float(m.group(2))
    return [round(lon, 4), round(lat, 4)] if -180 <= lon <= 180 and -90 <= lat <= 90 else None


def rows(name):
    R = list(csv.reader(open(f"{RAW}/{name}", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    head = [h.lstrip("?") for h in R[0]]
    for r in R[1:]:
        yield dict(zip(head, [val(x) for x in r + [""] * (len(head) - len(r))]))


I = {}
n_rows = 0
for r in rows("wikidata_inventions_A_labels_dates_classes.tsv"):
    n_rows += 1
    q = r["item"]
    if not re.fullmatch(r"Q\d+", q):
        continue
    d = I.setdefault(q, {"q": q, "n": "", "sl": 0, "y": None, "cls": []})
    if r["label"] and not d["n"]:
        d["n"] = r["label"]
    try:
        d["sl"] = max(d["sl"], int(r["sl"] or 0))
    except ValueError:
        pass
    m = YEAR.match(r["d"] or "")
    if m:
        y = int(m.group(1))
        if y <= 2026:
            d["y"] = y if d["y"] is None else min(d["y"], y)
    if r["clsL"] and r["clsL"] not in d["cls"]:
        d["cls"].append(r["clsL"])

INV = defaultdict(dict)
for r in rows("wikidata_inventions_B_inventors.tsv"):
    q, p = r["item"], r["inv"]
    if q not in I or not p:
        continue
    e = INV[q].setdefault(p, {"q": p, "n": r["invL"], "bp": r["bpL"], "pt": None, "cit": []})
    if not e["pt"] and pt(r["bpc"]):
        e["pt"] = pt(r["bpc"]); e["bp"] = r["bpL"] or e["bp"]
    if r["citL"] and r["citL"] not in e["cit"]:
        e["cit"].append(r["citL"])
LOC = defaultdict(list)
for r in rows("wikidata_inventions_C_locations.tsv"):
    q = r["item"]
    if q not in I:
        continue
    e = {"p": r["prop"], "n": r["locL"], "pt": pt(r["locc"]), "co": r["coL"]}
    if e not in LOC[q]:
        LOC[q].append(e)
for q, d in I.items():
    # inventors in Wikidata-ID order (older, usually better-known items first)
    d["inv"] = sorted(INV.get(q, {}).values(), key=lambda e: int(e["q"][1:]))
    d["loc"] = LOC.get(q, [])
jsave({"n_rows": n_rows, "items": list(I.values())}, f"{WORK}/items.json")
print("rows", n_rows, "items", len(I), "with inventor", sum(1 for d in I.values() if d["inv"]), "with location", sum(1 for d in I.values() if d["loc"]),
      "with date", sum(1 for d in I.values() if d["y"] is not None))
