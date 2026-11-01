"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
s, e, t, sh, b, c = R["source"], R["early"], R["timeline"], R["shift"], R["bias"], R["cities"]
N = lambda v: f"{round(v):,}"
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
readme = f"""# Where inventions came from

A world map of inventions and where they came from, from the first stone tools 3.3 million years ago to today, with the moving centre of invention. Three layers: {e['n_innov']} early innovations at {e['n_rows']} places, placed and dated by hand from nine English Wikipedia pages; the {t['n']} entries since 1500 in Wikipedia's Timeline of historic inventions; and {N(s['n'])} inventions from Wikidata, ranked by sitelinks.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- Invented more than once: on the pages' own account, farming began independently in {e['farming_n']} places (the Fertile Crescent, the Yangtze and Yellow River basins, New Guinea, southern Mexico, the Amazon, the Andes, the Ethiopian highlands, the Sahel, West Africa and eastern North America), writing in {e['writing_n']} (Mesopotamia, Egypt, China, Mesoamerica) and zero in {e['zero_n']} (Babylon, the Maya, India).
- The centre of invention (mean position of each period's landmarks) moves from Africa in the deep past to West Asia from 10,000 BC to AD 1 ({sh['wana_bronze']:.0f}% of the landmarks of 5000 to 2000 BC), to China from AD 1 to 1500 ({sh['eastasia_ad1']:.0f}%), to Europe from 1500 (all of 1500 to 1700; {sh['europe_1850']:.0f}% of 1850 to 1900), and to North America from 1950 to 2000 ({sh['na_1950']:.0f}%).
- Wikidata has {R['centuries_top']['wd_1800s']} dated inventions from the 19th century and {R['centuries_top']['wd_1900s']} from the 20th, but {R['centuries_top']['wd_before_1500']} from before 1500.
- Most inventive cities in Wikidata (within 25 km): {c['top'][0]['name']} ({c['top'][0]['n']}), {c['top'][1]['name']} ({c['top'][1]['n']}), {c['top'][2]['name']} ({c['top'][2]['n']}), {c['top'][3]['name']} ({c['top'][3]['n']}), mostly inventors' birthplaces.
- Bias: {b['wd_eu_na_pct']:.0f}% of Wikidata's mapped inventions are in Europe or North America, which have {b['pop_eu_na_pct']:.0f}% of today's people; sub-Saharan Africa has {b['wd_ssa']} and South Asia {b['wd_sa']}. {s['with_inventor_pct']:.0f}% of Wikidata inventions are credited to a named person. This maps the written record of invention, mostly in English, not invention itself.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/06_build_site.py`; `data/points.json` is loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/early_innovations.csv` | {e['n_rows']} rows for {e['n_innov']} early innovations: place, date range as the page gives it, rough coordinates and their precision, kind (independent, candidates, finds, single), the page and the quoted passage. CC BY-SA 4.0. |
| `data/timeline_1500_on.csv` | The {t['n']} timeline entries since 1500 with their text, category, place and how it was placed. CC BY-SA 4.0. |
| `data/inventions_wikidata.csv` | {N(s['n'])} Wikidata inventions: ID, name, sitelinks, year, category, classes, placement method, place, point, country, region, city area, inventors ({size('inventions_wikidata.csv')}). |
| `data/centre_of_invention.csv` | The centre and the regional shares per period, for the landmark list and for Wikidata. |
| `data/centuries.csv`, `data/cities.csv` | Inventions per century; city areas with their counts. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/points.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data. |
| `code/` | Scripts, run in order (below), the hand table (`early.py`) and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the last check of the page at desktop and phone widths. |

## Method in brief

- Early innovations: read from the text of nine English Wikipedia pages; dates and places as the pages give them, with ranges and several places kept; coordinates rough (site, region, country or continent). Every quoted passage is checked against the saved page.
- Timeline since 1500: placed by a place named in the entry, else a named person's Wikidata birthplace, else a named country; {t['n_hand']} entries ({t['hand_pct']:.0f}%) placed by hand at country level, flagged.
- Wikidata: {N(s['n_items'])} items with an inventor or date of invention, filtered by class and name and checked by hand; {N(s['n'])} with {R['meta']['min_sl']}+ sitelinks. Placed at the location of invention or discovery ({s['n_made']}), else the first inventor's birthplace ({s['n_inventor']}), else the country of origin ({s['n_country']}); {s['n_unplaced']} unplaced.
- Centre of invention: weighted mean latitude and longitude per period; candidate places share one count.
- Caveats: English-language sources, uneven coverage, individual credit, rough early coordinates, present-day borders and population.

## How to rerun

Needs Python 3 with numpy, shapely, pyproj, matplotlib, fontTools and Pillow, xelatex (TeX Gyre Pagella, Inter) and pdftotext; node with Playwright for the QA screenshots. Raw inputs are read in place (paths in `code/common.py`): three QLever query results on Wikidata and nine saved Wikipedia pages (retrieved {RETRIEVED}), and Natural Earth countries and populated places. Intermediate files go to `/dev/shm/inventions/work` (set `INVTMP` to change).

```
python3 code/01_parse.py        # parse the Wikidata query results
python3 code/02_filter.py       # which items are inventions, and their category
python3 code/03_timeline.py     # the Wikipedia timeline since 1500
python3 code/04_geo.py          # place everything; check the hand table against the pages
python3 code/05_results.py      # results.json, CSV files and page data
python3 code/06_build_site.py   # index.html (checks the facts stated in words)
python3 code/07_figures.py      # header, blog and paper figures
python3 code/08_paper.py        # paper PDF
python3 code/09_readme.py       # README, LICENSE, Reddit post
python3 code/10_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
node code/12_qa.js              # screenshots (serve the folder on port 8818 first)
```

## Sources and licences

- English Wikipedia pages listed above, CC BY-SA 4.0. The early-innovation and timeline tables quote and adapt their text and are shared under CC BY-SA 4.0.
- Wikidata, via QLever (https://qlever.cs.uni-freiburg.de/wikidata). CC0.
- Natural Earth countries and populated places (public domain).
- Base map tiles on the page: © Esri.

Other derived data, text and figures: CC BY 4.0. Code: MIT (see LICENSE).

## Citation

Hotham, T. (2026) Where inventions came from: a map of invention from the first stone tools to the present, from Wikipedia and Wikidata. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "DSIT", "DCMS"):
    assert bad not in readme, bad
assert "--" not in readme.replace("|---|---|", "")
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
data/early_innovations.csv, data/timeline_1500_on.csv, code/early.py (its
table) and the short quotations shown on the page quote and adapt English
Wikipedia text and are released under CC BY-SA 4.0. The other text, figures and
derived data files are released under CC BY 4.0; they are derived from Wikidata
(CC0) and Natural Earth (public domain).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)

post = f"""## Title

[OC] Where inventions came from, 3.3 million years on one map: farming was invented {e['farming_n']} separate times, and the "centre of invention" moved from Mesopotamia to China, Europe and the US

## Body

I mapped {e['n_innov']} early innovations (placed and dated from the text of nine Wikipedia pages, keeping ranges and multiple places), the {t['n']} entries since 1500 in Wikipedia's Timeline of historic inventions, and {N(s['n'])} inventions from Wikidata. The red line is the average position of each period's landmark inventions: Africa in the deep past, West Asia from 10,000 BC ({sh['wana_bronze']:.0f}% of landmarks from 5000 to 2000 BC), China from AD 1 to 1500 ({sh['eastasia_ad1']:.0f}%), Europe from 1500 (100% of 1500 to 1700), North America from 1950 ({sh['na_1950']:.0f}%). Big caveat: {b['wd_eu_na_pct']:.0f}% of Wikidata's mapped inventions are in Europe or North America (home to {b['pop_eu_na_pct']:.0f}% of people today), and {s['with_inventor_pct']:.0f}% are credited to one named person. It maps the written record, mostly English, not human ingenuity. Interactive map with a time slider, play button and search: {PAGE}

## Source comment

Sources: English Wikipedia (CC BY-SA 4.0), 2026: Timeline of historic inventions, Timeline of prehistory, Neolithic Revolution, Domestication, History of writing, Wheel, Bronze Age, List of Indian inventions and discoveries, Islamic Golden Age. Wikidata via QLever (CC0), 2026: items with an inventor (P61) or time of invention (P575), filtered to technologies, placed at the location of invention, else the inventor's birthplace, else the country of origin. Natural Earth (public domain). Centre of invention = mean latitude and longitude of each period's landmarks.

Tools: Python (shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}
"""
for bad in ("—", "–", "--"):
    assert bad not in post, bad
os.makedirs(os.path.join(ROOT, "reddit"), exist_ok=True)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("README", len(readme.split()), "words; post", len(post.split()), "words")
