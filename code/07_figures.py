"""Static figures: header.png (1200 x 630), blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png).
Every number drawn comes from data/results.json or the CSV files in data/."""
import csv
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from figstyle import *

R = jload(f"{DATA}/results.json")
PTS = jload(f"{DATA}/points.json")
CAT = {k: c for k, _, c in CATS}
REGC = dict(REGIONS)
BLOG = os.path.join(ROOT, "release", "blog"); PAPER = os.path.join(ROOT, "release", "paper")
for d in (BLOG, PAPER):
    os.makedirs(d, exist_ok=True)
BB = R["centre"]["backbone"]


def both(fig, name):
    fig.savefig(f"{PAPER}/f_{name}.png", dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(f"{BLOG}/b_{name}.png", dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def path(ax, lw=2.6, num=True, fs=10):
    x, y = proj([p["lon"] for p in BB], [p["lat"] for p in BB])
    ax.plot(x, y, color="white", lw=lw + 3.5, zorder=8, solid_capstyle="round")
    ax.plot(x, y, color=HOT, lw=lw, zorder=9, solid_capstyle="round")
    ax.scatter(x, y, s=[30 + 3 * p["n_items"] for p in BB], color=HOT, edgecolor="white", lw=1.4, zorder=10)
    return x, y


def early_points(ax, s=70, links=True):
    E = PTS["early"]; groups = {}
    for r in E:
        groups.setdefault(r[1], []).append(r)
    if links:
        for g in groups.values():
            if len(g) > 1 and g[0][4] in ("finds", "candidates"):
                for r in g[1:]:
                    x, y = proj([g[0][9], r[9]], [g[0][8], r[8]])
                    ax.plot(x, y, color=CAT[g[0][3]], lw=1.1, ls=(0, (4, 3)), alpha=.75, zorder=4)
    for r in E:
        x, y = proj(r[9], r[8]); ind = r[4] == "independent"
        ax.scatter(x, y, marker="D", s=s * (1.25 if ind else 1), color=CAT[r[3]], edgecolor=FG if ind else "white", lw=1.1 if ind else .7, zorder=6)


# ---------- 1 early map with the centre path ----------
fig = plt.figure(figsize=(12, 6.6), facecolor=BG); ax = fig.add_axes([0, .06, 1, .94]); ax.set_facecolor(BG)
world(ax, ec="#FFFFFF")
early_points(ax)
x, y = path(ax)
for i, p in enumerate(BB):
    ax.annotate(str(i + 1), (x[i], y[i]), xytext=(6, 5) if i % 2 else (4, -13), textcoords="offset points", fontsize=9, color=HOT, fontweight="bold", zorder=11,
                path_effects=[__import__("matplotlib.patheffects", fromlist=["x"]).withStroke(linewidth=3, foreground=BG)])
h = [Line2D([], [], marker="D", ls="", color=c, mec="white", ms=8, label=n) for k, n, c in CATS if any(r[3] == k for r in PTS["early"])]
h += [Line2D([], [], color=HOT, lw=2.6, marker="o", ms=7, mec="white", label="Centre of invention (numbered periods)")]
h += [Line2D([], [], marker="D", ls="", mfc="white", mec=FG, mew=1.4, ms=9, label="outlined: arose independently in several places")]
ax.legend(handles=h, loc="lower left", ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(0.0, -0.08))
both(fig, "early_map")

# ---------- 2 shares by period ----------
fig, ax = plt.subplots(figsize=(10, 6.2), facecolor=BG); ax.set_facecolor(BG)
for i, p in enumerate(BB):
    x0 = 0
    for r, c in REGIONS:
        v = p["shares"][r]
        if v > 0:
            ax.barh(i, v, left=x0, color=c, height=.78, edgecolor=BG, lw=.6); x0 += v
ax.set_yticks(range(len(BB))); ax.set_yticklabels([f"{i + 1}. {p['label']}  ({round(p['n_items'])})" for i, p in enumerate(BB)], fontsize=9.5)
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels([f"{v}%" for v in (0, 25, 50, 75, 100)])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(handles=[Rectangle((0, 0), 1, 1, color=c, label=r) for r, c in REGIONS], ncol=3, frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(.42, -.07))
fig.subplots_adjust(left=.33, right=.97, top=.97, bottom=.2)
both(fig, "shares")

# ---------- 3 per century ----------
C = R["centuries"]
fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
xs = np.arange(len(C))
ax.bar(xs - .2, [c["backbone"] for c in C], width=.4, color=COOL, label="Landmark list (early innovations, then the Wikipedia timeline)")
ax.bar(xs + .2, [c["wikidata"] for c in C], width=.4, color=GOLD, label="Wikidata inventions with a date")
ax.set_xticks([i for i, c in enumerate(C) if c["c"] % 500 == 0]); ax.set_xticklabels([(f"{-c['c']} BC" if c["c"] < 0 else "AD 1" if c["c"] == 0 else str(c["c"])) for c in C if c["c"] % 500 == 0])
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_ylabel("inventions per century"); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
fig.subplots_adjust(left=.08, right=.98, top=.95, bottom=.12)
both(fig, "centuries")

# ---------- 4 Wikidata map by placement method ----------
fig = plt.figure(figsize=(12, 6.3), facecolor=BG); ax = fig.add_axes([0, .05, 1, .95]); ax.set_facecolor(BG)
world(ax, ec="#FFFFFF")
for r in PTS["wd"][::-1]:
    x, y = proj(r[8], r[7]); s = 4 + 1.6 * r[2] ** .75 / 2
    if r[5] == "made":
        ax.scatter(x, y, s=s, color=CAT[r[4]], edgecolor="white", lw=.4, zorder=5)
    elif r[5] == "inventor":
        ax.scatter(x, y, s=s, facecolor="none", edgecolor=CAT[r[4]], lw=1, zorder=4, alpha=.85)
    else:
        ax.scatter(x, y, s=s, facecolor="none", edgecolor=CAT[r[4]], lw=.8, ls=":", zorder=3, alpha=.6)
h = [Line2D([], [], marker="o", ls="", color=c, ms=7, label=n) for k, n, c in CATS]
h += [Line2D([], [], marker="o", ls="", mfc="none", mec=MUT, ms=8, mew=1.3, label="ring: inventor's birthplace")]
ax.legend(handles=h, loc="lower left", ncol=4, frameon=False, fontsize=8.3, bbox_to_anchor=(0, -0.07))
both(fig, "wikidata_map")

# ---------- 5 cities ----------
ci = R["cities"]["top"][:15][::-1]
fig, ax = plt.subplots(figsize=(8.5, 5.6), facecolor=BG); ax.set_facecolor(BG)
y = np.arange(len(ci))
ax.barh(y, [c["n_inv"] for c in ci], color=COOL, label="inventor born here")
ax.barh(y, [c["n_made"] for c in ci], left=[c["n_inv"] for c in ci], color="#8FB3DB", label="invented or discovered here")
ax.barh(y, [c["n"] - c["n_inv"] - c["n_made"] for c in ci], left=[c["n_inv"] + c["n_made"] for c in ci], color="#C9C2B4")
for i, c in enumerate(ci):
    ax.text(c["n"] + .6, i, str(c["n"]), va="center", fontsize=9)
ax.set_yticks(y); ax.set_yticklabels([c["name"] for c in ci])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0); ax.legend(frameon=False, loc="lower right", fontsize=9)
fig.subplots_adjust(left=.2, right=.97, top=.97, bottom=.08)
both(fig, "cities")

# ---------- 6 bias ----------
RN = [r for r, _ in REGIONS]
wd = {r["reg"]: r["pct"] for r in R["regions"]}; tl = R["timeline_regions"]; pop = R["bias"]["pop_pct"]
fig, ax = plt.subplots(figsize=(10, 5.8), facecolor=BG); ax.set_facecolor(BG)
y = np.arange(len(RN))
ax.barh(y - .27, [wd[r] for r in RN], height=.26, color=HOT, label="Wikidata inventions with a point")
ax.barh(y, [tl[r] for r in RN], height=.26, color=COOL, label="Wikipedia timeline since 1500")
ax.barh(y + .27, [pop[r] for r in RN], height=.26, color=MUT, alpha=.55, label="Share of people today")
for i, r in enumerate(RN):
    ax.text(wd[r] + .6, i - .27, f"{wd[r]:.1f}%" if wd[r] < 10 else f"{wd[r]:.0f}%", va="center", fontsize=8.5)
    ax.text(pop[r] + .6, i + .27, f"{pop[r]:.1f}%" if pop[r] < 10 else f"{pop[r]:.0f}%", va="center", fontsize=8.5, color=MUT)
ax.set_yticks(y); ax.set_yticklabels(RN); ax.invert_yaxis()
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0); ax.set_xlim(0, 72); ax.set_xticks([0, 20, 40, 60]); ax.set_xticklabels(["0%", "20%", "40%", "60%"])
ax.legend(frameon=False, loc="lower right", fontsize=9)
fig.subplots_adjust(left=.36, right=.97, top=.97, bottom=.08)
both(fig, "bias")

# ---------- header 1200 x 630 ----------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([.3, .02, .72, .9]); ax.set_facecolor(BG)
world(ax, ec="#FFFFFF", ext=(-11.5e6, 15.5e6, -5.6e6, 8.4e6))
early_points(ax, s=34)
path(ax, lw=2.2)
fig.text(.035, .80, "Where", fontproperties=DISP, fontsize=50, color=FG, va="baseline")
fig.text(.035, .67, "inventions", fontproperties=DISP, fontsize=50, color=COOL, va="baseline")
fig.text(.035, .54, "came from", fontproperties=DISP, fontsize=50, color=HOT, va="baseline")
fig.text(.037, .44, f"{R['early']['n_innov']} early innovations, {R['timeline']['n']} landmarks\nsince 1500 and {R['source']['n']:,} Wikidata inventions,\n3.3 million years ago to today", fontsize=12, color=FG, va="top", linespacing=1.5)
fig.text(.037, .2, "red line: the centre of invention", fontsize=11, color=HOT, va="top")
fig.text(.037, .06, "maps.tristanhotham.com/inventions-map", fontsize=10, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
plt.close(fig)
print("figures done")
