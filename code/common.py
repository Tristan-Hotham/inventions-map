"""Shared paths and helpers for the inventions-map project.

Raw inputs (read in place, never modified), all fetched in 2026:
  /home/claude/newdata/raw7/inv/wikidata_inventions_A_labels_dates_classes.tsv
      QLever query result on Wikidata (CC0): 24,208 items that have P575 (time of discovery or invention) or P61
      (discoverer or inventor), excluding taxa, astronomical objects and chemical compounds. Columns ?item, ?label (English),
      ?sl (number of sitelinks), ?d (P575 value), ?clsL (English label of each instance-of (P31) class; one row per class).
  /home/claude/newdata/raw7/inv/wikidata_inventions_B_inventors.tsv
      ?item, ?inv (P61 inventor or discoverer), ?invL label, ?bpL label of the inventor's birthplace (P19), ?bpc its
      coordinates, ?citL label of the inventor's country of citizenship (P27). One row per combination.
  /home/claude/newdata/raw7/inv/wikidata_inventions_C_locations.tsv
      ?item, ?prop (P189 location of discovery, P1071 location of creation, P495 country of origin), ?locL label,
      ?locc coordinates, ?coL label of the location's country.
  /home/claude/newdata/raw7/inv/wiki_*.json
      English Wikipedia parsed HTML (CC BY-SA 4.0) {title, revid, html} of nine pages, used for the hand-checked table
      of early innovations (code/early.py): Timeline of historic inventions, Neolithic Revolution, History of writing,
      Wheel, Timeline of prehistory, Domestication, Bronze Age, List of Indian inventions and discoveries, Islamic Golden Age.
  /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson, ne_50m_admin_0_countries.geojson,
      ne_10m_populated_places_simple.geojson (Natural Earth, public domain)
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("INV_RAW", "/home/claude/newdata/raw7/inv")
GEO = os.environ.get("INV_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("INV_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("INVTMP", "/dev/shm/inventions"), "work")   # intermediates live outside the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "inventions-map"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "10.5281/zenodo.23856736"                  # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/inventions-map/"            # filled in by the publisher
RETRIEVED = "2026"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
WD = "http://www.wikidata.org/entity/"

# categories: key, display name, colour (light theme). Order is the legend order.
CATS = [
    ("food", "Food and farming", "#4E8B3A"),
    ("tools", "Tools and materials", "#8C6A3F"),
    ("writing", "Writing, numbers and printing", "#7A3E9D"),
    ("transport", "Transport", "#2F5D8C"),
    ("energy", "Energy and machines", "#D69A1A"),
    ("science", "Instruments and measurement", "#2A9BA8"),
    ("medicine", "Medicine and health", "#C2457A"),
    ("comms", "Communication and computing", "#3C4FB0"),
    ("home", "Home and everyday life", "#C9732E"),
    ("culture", "Music, images and play", "#5E9E92"),
    ("weapons", "Weapons and war", "#A3202E"),
]
CATNAME = {k: n for k, n, _ in CATS}
CATCOL = {k: c for k, _, c in CATS}

# world regions used for the shares and the centre of invention
REGIONS = [
    ("Europe", "#2F5D8C"), ("North America", "#A3202E"), ("East Asia", "#D69A1A"), ("South Asia", "#C9732E"),
    ("West Asia and North Africa", "#7A3E9D"), ("Sub-Saharan Africa", "#4E8B3A"), ("Latin America", "#C2457A"),
    ("Southeast Asia and Oceania", "#2A9BA8"), ("Central Asia, Siberia and the steppe", "#8C6A3F"),
]


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text taken from Wikidata or Wikipedia (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def yearname(y):
    """Readable year: 3,300,000 years ago, 70,000 years ago, 9500 BC, AD 105, 1879."""
    y = int(round(y))
    if y < -1_000_000:
        return f"{-y / 1e6:.1f} million years ago".replace(".0 ", " ")
    if y < -20000:
        return f"{round(-y, -3):,} years ago"
    if y < 0:
        return f"{-y} BC"
    if y < 1000:
        return f"AD {y}"
    return str(y)


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "yr": return yearname(v)
    raise ValueError(f)
