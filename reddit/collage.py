"""Reddit collage (r/dataisbeautiful style): reddit/where_inventions_came_from.png, 2400 px wide, light background.
A world map of the early innovations and the Wikipedia timeline, with the centre of invention drawn across it; a
timeline strip of regional shares by period with milestone inventions; a full legend; key numbers. Every number comes
from data/results.json; labels sit on open sea or paper, never on the data, and there are no leader lines."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patheffects as pe

R = jload(f"{DATA}/results.json"); PTS = jload(f"{DATA}/points.json")
CAT = {k: c for k, _, c in CATS}; REGC = dict(REGIONS); BB = R["centre"]["backbone"]
e, sh, b, s = R["early"], R["shift"], R["bias"], R["source"]
HALO = [pe.withStroke(linewidth=6, foreground=BG)]
W_IN, H_IN = 24, 40.3
fig = plt.figure(figsize=(W_IN, H_IN), dpi=100, facecolor=BG)
fx = lambda px: px / (W_IN * 100); fy = lambda py: 1 - py / (H_IN * 100)     # pixel positions from the top left

# ---------- title ----------
fig.text(fx(90), fy(170), "Where inventions came from", fontproperties=DISP, fontsize=118, color=FG)
fig.text(fx(94), fy(255), f"3.3 million years on one map: {e['n_innov']} early innovations from Wikipedia, its {R['timeline']['n']} landmark inventions since 1500,",
         fontproperties=SERP, fontsize=33, color=FG)
fig.text(fx(94), fy(305), "and the centre of invention (red), the average position of each period's landmarks, as it moved across the world.",
         fontproperties=SERP, fontsize=33, color=FG)

# ---------- map ----------
MX = (-16.9e6, 16.1e6, -6.3e6, 8.7e6)
mh = 2400 * (MX[3] - MX[2]) / (MX[1] - MX[0])
ax = fig.add_axes([0, fy(360 + mh), 1, mh / (H_IN * 100)]); ax.set_facecolor(BG)
world(ax, ec="#FFFFFF", ext=MX, lw=.5)
# timeline entries since 1500: small squares
for r in PTS["tl"]:
    x, y = proj(r[8], r[7])
    ax.scatter(x, y, marker="s", s=34, color=CAT[r[3]], edgecolor="white", lw=.6, zorder=5, alpha=.9)
# early innovations: diamonds; outlined where independent
for r in PTS["early"]:
    x, y = proj(r[9], r[8]); ind = r[4] == "independent"
    ax.scatter(x, y, marker="D", s=150 if ind else 95, color=CAT[r[3]], edgecolor=FG if ind else "white", lw=2 if ind else 1, zorder=6)
# the centre of invention
px, py = proj([p["lon"] for p in BB], [p["lat"] for p in BB])
ax.plot(px, py, color="white", lw=12, zorder=8, solid_capstyle="round", solid_joinstyle="round")
ax.plot(px, py, color=HOT, lw=5.5, zorder=9, solid_capstyle="round", solid_joinstyle="round")
dx, dy = list(px), list(py)
for i in range(1, len(BB)):          # display nudge only: dots closer than 450 km to the previous one move apart vertically
    if np.hypot(dx[i] - dx[i - 1], dy[i] - dy[i - 1]) < 4.5e5:
        dy[i - 1] += 2.6e5; dy[i] -= 2.6e5
for i in range(len(BB)):
    ax.scatter(dx[i], dy[i], s=620, color=HOT, edgecolor="white", lw=2.5, zorder=10)
    ax.text(dx[i], dy[i], str(i + 1), ha="center", va="center", fontsize=14, color="white", fontweight="bold", zorder=11, family=MONO)


def sea(lon, lat, txt, big, col=FG, w=None, ha="left"):
    x, y = proj(lon, lat)
    ax.text(x, y, big, fontproperties=DISP, fontsize=50, color=col, ha=ha, va="bottom", zorder=12, path_effects=HALO)
    ax.text(x, y - 1.3e5, txt, fontsize=19, color=FG, ha=ha, va="top", zorder=12, linespacing=1.35, path_effects=HALO)


sea(-176, -24, "times farming began independently:\nthe Fertile Crescent, the Yangtze,\nthe Yellow River, New Guinea, Mexico,\nthe Amazon, the Andes, Ethiopia, the\nSahel, West Africa, eastern N. America", str(e["farming_n"]), col=CAT["food"])
sea(48, -38, "of the landmarks from AD 1 to 1500\nare Chinese: paper, printing,\nporcelain, gunpowder and more", f"{sh['eastasia_ad1']:.0f}%", col=REGC["East Asia"])
sea(-42, -34, "independent inventions of\nwriting: Mesopotamia, Egypt,\nChina and the Maya", str(e["writing_n"]), col=CAT["writing"])
sea(-58, 33, "of the landmarks from 1500\nto 1700 are European", "100%", col=REGC["Europe"])
sea(-168, 18, "North America leads\nfrom 1950 to 2000", f"{sh['na_1950']:.0f}%", col=REGC["North America"])

# ---------- the centre, period by period (on paper, below the map) ----------
top = 360 + mh + 40
fig.text(fx(90), fy(top + 30), "The centre of invention, period by period", fontproperties=DISPB, fontsize=36, color=FG)
fig.text(fx(90), fy(top + 72), "Numbers match the red dots. Columns: period, where the centre falls, and the region with the largest share of that period's landmarks.", fontsize=19, color=MUT)
col_w = 1160
for i, p in enumerate(BB):
    c, rr = divmod(i, 7)
    x0, y0 = 90 + c * col_w, top + 120 + rr * 50
    fig.patches.append(plt.Circle((fx(x0 + 18), fy(y0 - 7)), radius=fx(17), transform=fig.transFigure, color=HOT, figure=fig))
    fig.text(fx(x0 + 18), fy(y0 - 7), str(i + 1), ha="center", va="center", fontsize=15, color="white", fontweight="bold")
    SHORTR = {"West Asia and North Africa": "W. Asia, N. Africa", "Sub-Saharan Africa": "Sub-Sah. Africa"}
    fig.text(fx(x0 + 50), fy(y0), p["short"], fontsize=19, color=FG, fontweight="bold")
    where = p["where"].replace("open sea, nearest land ", "sea off ")
    fig.text(fx(x0 + 345), fy(y0), f"{where}", fontsize=19, color=MUT)
    fig.text(fx(x0 + 615), fy(y0), f"{SHORTR.get(p['top'], p['top'])} {p['top_pct']:.0f}%", fontsize=19, color=REGC[p["top"]], fontweight="bold")

# ---------- timeline strip ----------
ts = top + 520
fig.text(fx(90), fy(ts), "Where each period's landmark inventions came from", fontproperties=DISPB, fontsize=36, color=FG)
fig.text(fx(90), fy(ts + 42), "Share by world region; period widths are not to scale, because 3.3 million years would leave no room for the last 500.", fontsize=19, color=MUT)
sx0, sx1, sy0, sh_ = 90, 2310, ts + 250, 300
bw = (sx1 - sx0) / len(BB)
axs = fig.add_axes([fx(sx0), fy(sy0 + sh_), fx(sx1 - sx0), sh_ / (H_IN * 100)]); axs.set_xlim(0, len(BB)); axs.set_ylim(0, 100); axs.axis("off")
for i, p in enumerate(BB):
    y = 0
    for rg, c in REGIONS:
        v = p["shares"][rg]
        if v > 0:
            axs.add_patch(Rectangle((i + .04, y), .92, v, color=c, lw=0)); y += v
    axs.text(i + .5, -6, str(i + 1), ha="center", va="top", fontsize=16, color=HOT, fontweight="bold")
    axs.text(i + .5, -16, p["short"].replace(" to ", "\nto "), ha="center", va="top", fontsize=13.5, color=FG, linespacing=1.15)
# milestone inventions above the strip, in two rows so no two labels touch
MIL = [(0, "stone tools"), (0, "fire"), (1, "bow and arrow"), (1, "pottery"), (2, "farming"), (3, "wheel, writing"), (4, "alphabet, coins"),
       (5, "paper, zero, gunpowder"), (6, "telescope"), (7, "steam engine"), (8, "steam locomotive"), (9, "telephone"), (10, "aeroplane, transistor"), (11, "web, smartphone"), (12, "iPhone, blockchain")]
seen = {}
for i, t in MIL:
    seen.setdefault(i, []).append(t)
for i, ts_ in seen.items():
    txt = ", ".join(ts_)
    row = i % 2
    fig.text(fx(sx0 + (i + .5) * bw), fy(sy0 - 18 - row * 44), txt, ha="center", va="bottom", fontsize=15.5, color=FG, style="italic")

# ---------- legend ----------
lg = sy0 + sh_ + 200
fig.text(fx(90), fy(lg), "Legend", fontproperties=DISPB, fontsize=36, color=FG)
axl = fig.add_axes([fx(80), fy(lg + 230), fx(2260), 200 / (H_IN * 100)]); axl.axis("off")
h1 = [Line2D([], [], marker="D", ls="", color=c, mec="white", ms=17, label=n) for k, n, c in CATS]
leg1 = axl.legend(handles=h1, title="Kind of invention (colour)", loc="upper left", ncol=4, frameon=False, fontsize=19, title_fontsize=21, alignment="left",
                  handletextpad=.6, columnspacing=2.2, labelspacing=.8, bbox_to_anchor=(0, 1))
axl.add_artist(leg1)
h2 = [Line2D([], [], marker="D", ls="", color="#999", mec="white", ms=16, label="Early innovation (hand table from 9 Wikipedia pages)"),
      Line2D([], [], marker="D", ls="", color="#999", mec=FG, mew=2.2, ms=18, label="Outlined: arose independently in several places"),
      Line2D([], [], marker="s", ls="", color="#999", mec="white", ms=12, label="Wikipedia Timeline of historic inventions, 1500 on"),
      Line2D([], [], color=HOT, lw=5, marker="o", ms=20, mec="white", mew=2.5, label="Centre of invention: mean position of each period's landmarks")]
axm = fig.add_axes([fx(80), fy(lg + 450), fx(2260), 180 / (H_IN * 100)]); axm.axis("off")
axm.legend(handles=h2, title="Marks", loc="upper left", ncol=2, frameon=False, fontsize=19, title_fontsize=21, alignment="left", labelspacing=.8, columnspacing=2.5, bbox_to_anchor=(0, 1))
axr = fig.add_axes([fx(80), fy(lg + 620), fx(2260), 160 / (H_IN * 100)]); axr.axis("off")
axr.legend(handles=[Rectangle((0, 0), 1, 1, color=c, label=r) for r, c in REGIONS], title="World region (timeline strip)", loc="upper left", ncol=4, frameon=False,
           fontsize=19, title_fontsize=21, alignment="left", columnspacing=2, bbox_to_anchor=(0, 1))

# ---------- caveat panel ----------
cv = lg + 720
axc = fig.add_axes([fx(90), fy(cv + 300), fx(2220), 300 / (H_IN * 100)]); axc.axis("off")
axc.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=.02", fc="#ECE6D9", ec="none", transform=axc.transAxes))
axc.text(.02, .78, f"{b['wd_eu_na_pct']:.0f}%", fontproperties=DISP, fontsize=64, color=HOT, va="center", transform=axc.transAxes)
axc.text(.16, .8, f"of the {s['n_placed']:,} inventions Wikidata lets us map are in Europe or North America,\nhome to {b['pop_eu_na_pct']:.0f}% of people today.",
         fontsize=21, color=FG, va="center", transform=axc.transAxes)
axc.text(.02, .3, f"Sub-Saharan Africa has {b['wd_ssa']} of them and South Asia {b['wd_sa']}. {s['with_inventor_pct']:.0f}% are credited to a named person: Wikidata's only\n"
         "inventor of the car is Ferdinand Verbiest, a Flemish Jesuit in China, and it credits gunpowder to a legendary German\nmonk. This maps the written record of invention, mostly in English, not human ingenuity.",
         fontsize=19.5, color=FG, va="center", transform=axc.transAxes, linespacing=1.4)

# ---------- footer ----------
ft = cv + 370
FOOT = ["Sources: English Wikipedia (CC BY-SA 4.0), 2026: Timeline of historic inventions, Timeline of prehistory, Neolithic Revolution,",
        "Domestication, History of writing, Wheel, Bronze Age, List of Indian inventions and discoveries, Islamic Golden Age; dates and places",
        "as the pages give them, coordinates rough. Wikidata (CC0) for the bias panel. Natural Earth (public domain). Equal Earth projection.",
        "Analysis and chart: Tristan Hotham, with Python and matplotlib   ·   maps.tristanhotham.com/inventions-map"]
for k, line in enumerate(FOOT):
    fig.text(fx(90), fy(ft + 32 * k), line, fontsize=17, color=MUT)
OUTF = os.path.join(ROOT, "reddit", "where_inventions_came_from.png")
fig.savefig(OUTF, dpi=100, facecolor=BG)
print("collage", OUTF, "height px", ft + 150, "of", H_IN * 100)
