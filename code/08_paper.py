"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png sit beside them). 10.5281/zenodo.23856736 stays a placeholder."""
import csv, subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Where_Inventions_Came_From"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

# facts stated in words in the paper (beyond those checked by 06_build_site.py)
B = R["centre"]["backbone"]
assert B[6]["label"] == "1500 to 1700" and B[6]["shares"]["Europe"] == 100 and B[12]["label"] == "2000 to 2026" and B[12]["shares"]["North America"] == 100
assert B[0]["top"] == B[1]["top"] == "Sub-Saharan Africa"
assert [c["iso"] for c in R["countries"]["top"][:4]] == ["USA", "GBR", "FRA", "DEU"]
assert 30 <= R["timeline"]["hand_pct"] <= 45          # 'about two in five'
assert R["early"]["n_indep"] == 6


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


s = R["source"]
TP = ("\\begin{table}[tbp]\\centering\\small\\caption{From query to map: the Wikidata layer.}\\label{tab:pipe}"
      "\\begin{tabular}{p{10.5cm}r}\\toprule Step & Items\\\\\\midrule\n"
      f"Rows returned by the query & {s['n_rows']:,}\\\\\n"
      f"Items (inventor or discoverer, or a date of invention or discovery) & {s['n_items']:,}\\\\\n"
      f"\\quad dropped: class is not a technology (place, person, artwork, find, idea...) & {s['drop_class']:,}\\\\\n"
      f"\\quad dropped: no English label & {s['drop_nolabel']:,}\\\\\n"
      f"\\quad dropped: no technology class or word, or dropped by hand & {s['drop_other']:,}\\\\\n"
      f"Kept as inventions & {s['n_tech']:,}\\\\\n"
      f"\\quad with {R['meta']['min_sl']} or more sitelinks (the Wikidata layer) & {s['n']:,}\\\\\n"
      f"\\quad\\quad placed at a location of invention or discovery & {s['n_made']:,}\\\\\n"
      f"\\quad\\quad placed at the inventor's birthplace & {s['n_inventor']:,}\\\\\n"
      f"\\quad\\quad placed at the country of origin & {s['n_country']:,}\\\\\n"
      f"\\quad\\quad not placed & {s['n_unplaced']:,}\\\\\n"
      f"\\quad\\quad with a date & {s['n_dated']:,}\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(g['name'].split(' (')[0])} & {g['n']} & {tex('; '.join(g['origins']))}\\\\\n" for g in R["early"]["indep"])
TI = ("\\begin{table}[tbp]\\centering\\small\\caption{Innovations that arose independently in several places, according to the pages.}\\label{tab:indep}"
      "\\begin{tabular}{p{2.6cm}rp{10.6cm}}\\toprule Innovation & Places & Where\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for i, p in enumerate(B):
    rows += f"{i + 1} & {tex(p['label'])} & {p['n_items']} & {p['lat']:.1f}, {p['lon']:.1f} & {tex(p['where'])} & {tex(p['top'])} ({p['top_pct']:.0f}\\%)\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{The centre of invention: mean latitude and longitude of each period's landmark inventions, and the region with the largest share.}\\label{tab:centre}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{rlrlp{3.3cm}p{3.9cm}}\\toprule & Period & Items & Lat, lon & Centre falls & Largest share\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(c['name'])} & {tex(c['country'])} & {c['n']} & {c['n_inv']} & {c['n_made']} & {tex(', '.join(c['top'][:3]))}\\\\\n" for c in R["cities"]["top"][:15])
TCI = ("\\begin{table}[tbp]\\centering\\small\\caption{City areas with the most Wikidata inventions: all, inventor born there, made or discovered there, and the best known.}\\label{tab:cities}\\setlength{\\tabcolsep}{4pt}"
       "\\begin{tabular}{llrrrp{6cm}}\\toprule City & Country & All & Born & Made & Best known\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for e in csv.DictReader(open(f"{DATA}/early_innovations.csv", encoding="utf-8")):
    src = {"Timeline of historic inventions": "TH", "Timeline of prehistory": "TP", "Neolithic Revolution": "NR", "History of writing": "HW", "Wheel": "WH",
           "Domestication": "DO", "Bronze Age": "BA", "List of Indian inventions and discoveries": "IN", "Islamic Golden Age": "IG"}
    rows += f"{tex(e['innovation'])} & {tex(e['origin'])} & {tex(e['dates'])} & {tex(e['kind'])} & {'+'.join(src[x] for x in e['sources'].split('; '))}\\\\\n"
TE = ("\\clearpage\\section*{Appendix: the early innovations}\\footnotesize Sources: TH Timeline of historic inventions; TP Timeline of prehistory; NR Neolithic Revolution; DO Domestication; HW History of writing; WH Wheel; BA Bronze Age; IN List of Indian inventions and discoveries; IG Islamic Golden Age. The quoted passage for every row is in \\texttt{data/early\\_innovations.csv}.\n"
      "\\setlength{\\tabcolsep}{4pt}\\begin{longtable}{p{3.3cm}p{5.2cm}p{3.3cm}p{1.7cm}l}\\caption{Early innovations, places and dates as the pages give them.}\\label{tab:early}\\\\\\toprule Innovation & Place & Date & Kind & Page\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\normalsize")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_|DOI\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
t = t.replace("{{TABLE_PIPELINE}}", TP).replace("{{TABLE_INDEP}}", TI).replace("{{TABLE_CENTRE}}", TC).replace("{{TABLE_CITIES}}", TCI).replace("{{TABLE_EARLY}}", TE)
assert "{{" not in t.replace("10.5281/zenodo.23856736", "") and "--" not in t and "\u2014" not in t and "\u2013" not in t
for bad in ("DSIT", "DCMS"):
    assert bad not in t
t = t.replace("10.5281/zenodo.23856736", "\\{\\{DOI\\}\\}")
t = t.replace("\\href{https://doi.org/\\{\\{DOI\\}\\}}", "\\href{https://doi.org/}").replace("\\url{https://doi.org/\\{\\{DOI\\}\\}}", "https://doi.org/\\{\\{DOI\\}\\}")
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
