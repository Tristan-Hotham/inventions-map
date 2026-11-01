# Where inventions came from

A world map of inventions and where they came from, from the first stone tools 3.3 million years ago to today, with the moving centre of invention. Three layers: 115 early innovations at 155 places, placed and dated by hand from nine English Wikipedia pages; the 314 entries since 1500 in Wikipedia's Timeline of historic inventions; and 1,443 inventions from Wikidata, ranked by sitelinks.

Interactive page: https://maps.tristanhotham.com/inventions-map/
Paper: https://doi.org/10.5281/zenodo.23856736
Blog post: https://blog.tristanhotham.com/2026/10/31/inventions-map/

## Headline results

- Invented more than once: on the pages' own account, farming began independently in 11 places (the Fertile Crescent, the Yangtze and Yellow River basins, New Guinea, southern Mexico, the Amazon, the Andes, the Ethiopian highlands, the Sahel, West Africa and eastern North America), writing in 4 (Mesopotamia, Egypt, China, Mesoamerica) and zero in 3 (Babylon, the Maya, India).
- The centre of invention (mean position of each period's landmarks) moves from Africa in the deep past to West Asia from 10,000 BC to AD 1 (51% of the landmarks of 5000 to 2000 BC), to China from AD 1 to 1500 (50%), to Europe from 1500 (all of 1500 to 1700; 77% of 1850 to 1900), and to North America from 1950 to 2000 (55%).
- Wikidata has 177 dated inventions from the 19th century and 282 from the 20th, but 34 from before 1500.
- Most inventive cities in Wikidata (within 25 km): London (47), New York (37), Paris (27), Vienna (16), mostly inventors' birthplaces.
- Bias: 91% of Wikidata's mapped inventions are in Europe or North America, which have 14% of today's people; sub-Saharan Africa has 4 and South Asia 8. 83% of Wikidata inventions are credited to a named person. This maps the written record of invention, mostly in English, not invention itself.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/06_build_site.py`; `data/points.json` is loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/early_innovations.csv` | 155 rows for 115 early innovations: place, date range as the page gives it, rough coordinates and their precision, kind (independent, candidates, finds, single), the page and the quoted passage. CC BY-SA 4.0. |
| `data/timeline_1500_on.csv` | The 314 timeline entries since 1500 with their text, category, place and how it was placed. CC BY-SA 4.0. |
| `data/inventions_wikidata.csv` | 1,443 Wikidata inventions: ID, name, sitelinks, year, category, classes, placement method, place, point, country, region, city area, inventors (0.2 MB). |
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
- Timeline since 1500: placed by a place named in the entry, else a named person's Wikidata birthplace, else a named country; 120 entries (38%) placed by hand at country level, flagged.
- Wikidata: 24,186 items with an inventor or date of invention, filtered by class and name and checked by hand; 1,443 with 5+ sitelinks. Placed at the location of invention or discovery (52), else the first inventor's birthplace (949), else the country of origin (21); 421 unplaced.
- Centre of invention: weighted mean latitude and longitude per period; candidate places share one count.
- Caveats: English-language sources, uneven coverage, individual credit, rough early coordinates, present-day borders and population.

## How to rerun

Needs Python 3 with numpy, shapely, pyproj, matplotlib, fontTools and Pillow, xelatex (TeX Gyre Pagella, Inter) and pdftotext; node with Playwright for the QA screenshots. Raw inputs are read in place (paths in `code/common.py`): three QLever query results on Wikidata and nine saved Wikipedia pages (retrieved 2026), and Natural Earth countries and populated places. Intermediate files go to `/dev/shm/inventions/work` (set `INVTMP` to change).

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

Hotham, T. (2026) Where inventions came from: a map of invention from the first stone tools to the present, from Wikipedia and Wikidata. Zenodo. https://doi.org/10.5281/zenodo.23856736

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
