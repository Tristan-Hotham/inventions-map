"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23856736, https://doi.org/10.5281/zenodo.23856736 and https://blog.tristanhotham.com/2026/10/31/inventions-map/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Where_Inventions_Came_From"

# the page build checks the shared facts; these are the blog's own (alt text included)
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "06_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
C = R["cities"]["top"]
assert [c["n"] for c in C[:6]] == [47, 37, 27, 16, 12, 10] and [c["name"] for c in C[4:10]] == ["Chicago", "Boston", "Edinburgh", "Tokyo", "Munich", "Philadelphia"]
assert C[7]["name"] == "Tokyo" and all(c["iso"] in ("GBR", "USA", "FRA", "AUT") for c in C[:7])        # 'Tokyo is the first city outside Europe and North America'
assert R["centuries_top"]["wd_1800s"] == 177 and R["centuries_top"]["wd_1900s"] == 282
rg = {r["reg"]: r["pct"] for r in R["regions"]}; pop = R["bias"]["pop_pct"]
assert round(rg["Europe"]) == 65 and round(pop["Europe"]) == 10 and round(rg["North America"]) == 27 and round(pop["North America"]) == 5
assert rg["South Asia"] < 1 and round(pop["South Asia"]) == 24 and round(rg["Sub-Saharan Africa"], 1) == 0.4 and round(pop["Sub-Saharan Africa"]) == 14
assert len(R["centre"]["backbone"]) == 13
assert [p["where"] for p in R["centre"]["backbone"][:6]] == ["Sudan", "Oman", "Israel", "Iraq", "Iran", "Pakistan"] and R["centre"]["backbone"][6]["where"] == "France"

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG|DOI_URL\}\}|BLOG_URL\}\}|DOI\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
for ln in post.splitlines():
    if "{{IMG|" in ln:
        assert ln.startswith("{{IMG|") and ln.endswith("}}"), ln[:60]
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
s, e = R["source"], R["early"]
meta = {"title": "Where inventions came from",
        "slug": "inventions-map",
        "excerpt": f"I mapped the world's inventions from the first stone tools to the web: farming began in {e['farming_n']} places, writing in {e['writing_n']}, and the centre of invention moved from Mesopotamia to China, Europe and North America. The open record of it is {R['bias']['wd_eu_na_pct']:.0f}% Europe and North America.",
        "seo_description": "A map of where inventions came from over 3.3 million years: independent origins, the moving centre of invention, inventive cities and who gets the credit.",
        "tags": ["inventions", "history of technology", "maps", "data visualisation", "Wikipedia", "Wikidata", "farming", "writing", "history"],
        "header_alt": "Title card reading 'Where inventions came from' in black, blue and red on cream, beside a world map of coloured diamonds for early innovations and a red line, the centre of invention, running from East Africa through the Middle East to Pakistan, then from France across the Atlantic to the United States."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/inventions-map_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"inventions-map/{d}/{fn}")
    for fn in ("README.md", "LICENSE", "reddit/collage.py"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"inventions-map/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
zmeta = {"title": "Where Inventions Came From: A Map of Invention from the First Stone Tools to the Present, from Wikipedia and Wikidata",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["history of technology", "invention", "independent invention", "domestication", "Wikipedia", "Wikidata", "geographic bias", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "notes": "The tables of early innovations and of the Wikipedia timeline since 1500 quote and adapt English Wikipedia text and are licensed CC BY-SA 4.0.",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://en.wikipedia.org/wiki/Timeline_of_historic_inventions", "relation": "isDerivedFrom", "resource_type": "other"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
st = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in st, bad
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
