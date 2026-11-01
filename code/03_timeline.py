"""The modern backbone: every dated entry from 1500 onwards in English Wikipedia's 'Timeline of historic inventions'
(CC BY-SA 4.0), placed on the map (written to WORK/timeline.json).

The page is a curated list of 'particularly significant' inventions, so unlike Wikidata it does not grow with how much
has been typed in about a country; it is used with the hand table of early innovations for the centre of invention.
Each entry is placed by the first of these that works:
  1 'inventor'  a person named in the entry who is an inventor or discoverer (P61) in the Wikidata extract with a birthplace
                point: their birthplace ('inventor from'). The first such name in the entry wins.
  2 'place'     a hand reading of the entry (PLACE below): the city, lab or company named in the entry, or where the entry
                says it happened, at that place's rough coordinates.
  3 'country'   a country or nationality named in the entry (Hungarian, Scotsman, in Finland), at the country's centre.
Entries the hand reading could not place are kept but not mapped.
"""
import html as H
from collections import Counter
from common import *

PAGE = "wiki_timeline_of_historic_inventions.json"

# hand reading: entry start (year + first words) -> (place label, lat, lon). Used only when no inventor matched, or to
# correct a match that is not the inventor (for example a person mentioned in passing).
PLACE = {
    "1605: Newspaper": ("Strasbourg", 48.58, 7.75),
    "1608: Telescope": ("Middelburg, Netherlands", 51.50, 3.61),
    "1620: Compound microscopes": ("Netherlands", 52.1, 5.3),
    "1630: first use of the flintlock": None,
    "1745: Musschenbroek": ("Leiden", 52.16, 4.49),
    "1560: Floating dry dock": ("Venice", 45.44, 12.33),
    "1780: Hyder Ali": ("Mysore, India", 12.30, 76.64),
    "1888: The first practical pneumatic": ("Scotland", 56.5, -4.2),
    "1856: James Harrison": ("Geelong, Australia", -38.15, 144.36),
    "1875: Fyodor Pirotsky": ("Saint Petersburg", 59.94, 30.31),
    "1884: Hungarian engineers": ("Budapest", 47.50, 19.04),
    "1897: Surgical masks": ("Wrocław (Breslau)", 51.11, 17.03),
    "1915: The first operational military tanks": ("United Kingdom", 52.5, -1.5),
    "1925: The Fischer": ("Mülheim an der Ruhr", 51.43, 6.88),
    "1926: The Yagi": ("Sendai, Japan (Tohoku Imperial University)", 38.26, 140.87),
    "1927: The quartz clock": ("Bell Telephone Laboratories, New York", 40.74, -74.01),
    "1938: Nuclear fission": ("Berlin", 52.52, 13.40),
    "1945: The atomic bomb": ("Los Alamos, United States", 35.88, -106.30),
    "1945: Percy Spencer": ("Waltham, Massachusetts (Raytheon)", 42.38, -71.24),
    "1947: Floyd Farris": ("Tulsa, Oklahoma (Stanolind)", 36.15, -95.99),
    "1947: The first transistor": ("Bell Labs, Murray Hill, New Jersey", 40.68, -74.40),
    "1948: The first atomic clock": ("Washington, D.C. (National Bureau of Standards)", 38.90, -77.04),
    "1950: Bertie the Brain": ("Toronto", 43.65, -79.38),
    "1950: The Toroidal chamber": ("Moscow", 55.75, 37.62),
    "1952: The first thermonuclear weapon": ("Enewetak Atoll (United States test)", 38.9, -77.0),
    "1956: The hard disk drive": ("San Jose, California (IBM)", 37.34, -121.89),
    "1957: The first personal computer": ("United States (IBM)", 41.1, -73.7),
    "1957: The first artificial satellite": ("Baikonur (Soviet Union)", 45.92, 63.34),
    "1959: The MOSFET": ("Bell Labs, Murray Hill, New Jersey", 40.68, -74.40),
    "1960:  The first combined oral contraceptive": ("United States", 39.8, -98.6),
    "1960: First robotic exoskeleton": None,
    "1964: Shinkansen": ("Tokyo", 35.68, 139.69),
    "1967: E. A. Johnson": ("Malvern, England (Royal Radar Establishment)", 52.11, -2.33),
    "1969: The NPL network": ("Teddington, England (NPL)", 51.42, -0.33),
    "1970: The pocket calculator": None,
    "1971: The first single-chip microprocessor": ("Santa Clara, California (Intel)", 37.35, -121.95),
    "1971: The first space station": ("Baikonur (Soviet Union)", 45.92, 63.34),
    "1971: IBM developed": ("San Jose, California (IBM)", 37.34, -121.89),
    "1972: The first video game console": ("United States (Magnavox)", 39.8, -98.6),
    "1973: The first fiber optic": ("United States (Optelecom)", 39.1, -77.2),
    "1973: The first commercial graphical": ("Palo Alto, California (Xerox)", 37.44, -122.14),
    "1973: The first capacitive touchscreen": ("CERN, Geneva", 46.23, 6.05),
    "1975: First general purpose home automation": ("Glenrothes, Scotland (Pico Electronics)", 56.20, -3.18),
    "1977: The first self-driving car": ("Tsukuba, Japan", 36.08, 140.08),
    "1978: The Global Positioning System": ("United States", 39.8, -98.6),
    "1978: Birth of the first child": ("Oldham, England", 53.54, -2.11),
    "1979: The first handheld game console": ("United States (Milton Bradley)", 42.1, -72.6),
    "1979: Nippon Telegraph": ("Tokyo", 35.68, 139.69),
    "1979: Public dialup": ("Columbus, Ohio (CompuServe)", 39.96, -83.00),
    "1980: Flash memory": ("Kawasaki, Japan (Toshiba)", 35.53, 139.70),
    "1981: The first reusable spacecraft": ("Houston (NASA)", 29.76, -95.37),
    "1981: Televerket": ("Sweden", 59.33, 18.07),
    "1981: Comvik": ("Sweden", 59.33, 18.07),
    "1982: A CD-ROM": ("Tokyo and Eindhoven (Sony and Philips)", 35.68, 139.69),
    "1982: Direct to home satellite": ("London", 51.51, -0.13),
    "1982: The first laptop": ("Japan (Epson)", 36.05, 138.1),
    "1983: Ameritech": ("Chicago", 41.88, -87.63),
    "1984: The first commercially available cell phone": ("Schaumburg, Illinois (Motorola)", 42.03, -88.08),
    "1986: Technophone": ("United Kingdom", 52.5, -1.5),
    "1990: The first search engine": ("Montreal (McGill University)", 45.50, -73.58),
    "1991: The first commercial flash": ("Sunnyvale, California (SunDisk)", 37.37, -122.04),
    "1991: The first sim card": ("Munich", 48.14, 11.58),
    "1994: IBM Simon": ("United States (IBM)", 41.1, -73.7),
    "1994: First generation of Bluetooth": ("Lund, Sweden (Ericsson)", 55.70, 13.19),
    "1994: A Tetris variant": ("Germany (Hagenuk)", 54.32, 10.13),
    "1995: DVD": ("Japan and the Netherlands", 35.68, 139.69),
    "1996: The Ciena": ("United States", 39.1, -76.8),
    "1996: Mobile web": ("Finland (Nokia)", 60.17, 24.94),
    "1996: Bolt and Six": ("New York", 40.71, -74.01),
    "1996: Myriad Genetics": ("Salt Lake City", 40.76, -111.89),
    "1999: The first digital video recorder": ("Alviso, California (TiVo)", 37.43, -121.97),
    "1999: NTT DoCoMo": ("Tokyo", 35.68, 139.69),
    "2001: The Food and Drug": ("United States", 39.8, -98.6),
}
COUNTRY_WORDS = [  # (pattern, label, lat, lon)
    (r"\bHungarian\b", "Hungary", 47.2, 19.4), (r"\bScots?man\b|\bScottish\b", "Scotland", 56.5, -4.2), (r"\bFrench(man)?\b", "France", 46.6, 2.4),
    (r"\bGerman\b", "Germany", 51.1, 10.4), (r"\bAmerican\b", "United States", 39.8, -98.6), (r"\bBritish\b|\bEnglish\b", "United Kingdom", 52.5, -1.5),
    (r"\bin Finland\b", "Finland", 62.0, 25.7), (r"\bJapan\b", "Japan", 36.2, 138.3), (r"\bChina\b", "China", 35.0, 105.0),
    (r"\bin Italy\b", "Italy", 42.8, 12.5), (r"\bSwedish\b", "Sweden", 59.3, 18.1), (r"\bRussian?\b", "Russia", 55.75, 37.6),
    (r"\bCanadian\b", "Canada", 45.4, -75.7), (r"\bAustralia\b", "Australia", -33.9, 151.2), (r"\bKorean?\b", "South Korea", 37.57, 126.98),
]

CC = {"GBR": ("United Kingdom", 52.5, -1.5), "FRA": ("France", 46.6, 2.4), "DEU": ("Germany", 51.1, 10.4), "USA": ("United States", 39.8, -98.6),
      "NLD": ("Netherlands", 52.2, 5.5), "JPN": ("Japan", 36.2, 138.3), "RUS": ("Russia", 55.75, 37.6), "SWE": ("Sweden", 59.3, 16.0),
      "CHE": ("Switzerland", 46.8, 8.2), "IRL": ("Ireland", 53.4, -7.9), "CAN": ("Canada", 45.4, -75.7), "BEL": ("Belgium", 50.6, 4.6),
      "NOR": ("Norway", 60.5, 9.0), "ISR": ("Israel", 31.5, 34.9)}
HAND = [  # (year, start of entry text, ISO3)
    (1589, "Stocking frame", "GBR"), (1746, "John Roebuck", "GBR"), (1769, "Nicolas-Joseph Cugnot", "FRA"), (1775, "Jesse Ramsden", "GBR"),
    (1783, "Claude de Jouffroy", "FRA"), (1783, "Joseph-Ralf", "FRA"), (1783, "Louis-Sébastien", "FRA"), (1785, "Martinus van Marum", "NLD"),
    (1786, "Andrew Meikle", "GBR"), (1789, "Edmund Cartwright", "GBR"), (1795, "Joseph Bramah", "GBR"), (1796, "Alois Senefelder", "DEU"),
    (1799, "The first paper machine", "FRA"), (1804, "Friedrich Sertürner", "DEU"), (1804, "Hanaoka", "JPN"), (1807, "Robert Fulton", "USA"),
    (1811, "Friedrich Koenig", "GBR"), (1812, "William Reid Clanny", "GBR"), (1814, "James Fox", "GBR"), (1816, "Francis Ronalds", "GBR"),
    (1817, "Baron Karl von Drais", "DEU"), (1818, "Marc Isambard Brunel", "GBR"), (1822, "Thomas Blanchard", "USA"), (1824, "Johann Nikolaus von Dreyse", "DEU"),
    (1826, "John Walker", "GBR"), (1826, "James Sharp", "GBR"), (1828, "James Beaumont Neilson", "GBR"), (1828, "Patrick Bell", "GBR"),
    (1829, "William Mann", "GBR"), (1830, "Edwin Budding", "GBR"), (1839, "William Otis", "USA"), (1841, "Alexander Bain", "GBR"),
    (1842, "William Robert Grove", "GBR"), (1842, "John Bennet Lawes", "GBR"), (1844, "Friedrich Gottlob Keller", "DEU"), (1844, "Francis Rynd", "IRL"),
    (1844, "Horace Wells", "USA"), (1845, "Isaac Charles Johnson", "GBR"), (1846, "Henri-Joseph Maus", "BEL"), (1846, "Elias Howe", "USA"),
    (1848, "Jonathan J. Couch", "USA"), (1848, "Linus Yale", "USA"), (1851, "George Jennings", "GBR"), (1852, "Elisha Otis", "USA"),
    (1852, "Henri Giffard", "FRA"), (1853, "François Coignet", "FRA"), (1856, "Alexander Parkes", "GBR"), (1857, "Heinrich Geissler", "DEU"),
    (1859, "Gaston Planté", "FRA"), (1862, "Richard Jordan Gatling", "USA"), (1867, "Lucien B. Smith", "USA"), (1873, "Frederick Ransome", "GBR"),
    (1874, "Gustave Trouvé", "FRA"), (1874, "Ferdinand von Zeppelin", "DEU"), (1878, "Henry Fleuss", "GBR"), (1884, "Hiram Maxim", "GBR"),
    (1884, "Paul Vieille", "FRA"), (1884, "Sir Charles Parsons", "GBR"), (1885, "John Kemp Starley", "GBR"), (1886, "Carl Gassner", "DEU"),
    (1886, "Charles Martin Hall", "USA"), (1886, "Karl Benz", "DEU"), (1887, "James Blyth", "GBR"), (1888, "John J. Loud", "USA"),
    (1890, "Robert Gair", "USA"), (1892, "Léon Bouly", "FRA"), (1892, "Thomas Ahearn", "CAN"), (1892, "John Froelich", "USA"),
    (1893, "William Stewart Halsted", "USA"), (1898, "Hans von Pechmann", "DEU"), (1899, "Waldemar Jungner", "SWE"), (1903, "The first successful gas turbine", "NOR"),
    (1904, "The Fleming valve", "GBR"), (1907, "The tuyères", "FRA"), (1913, "The Bergius process", "DEU"), (1916, "The Czochralski process", "DEU"),
    (1926, "Harry Ferguson", "GBR"), (1929, "The ball screw", "USA"), (1930, "The Phase-contrast", "NLD"), (1933, "Harry C. Jennings", "USA"),
    (1939, "G. S. Yunyev", "RUS"), (1940, "John Randall and Harry Boot", "GBR"), (1941, "Polyester is invented", "GBR"), (1942, "The V-2 rocket", "DEU"),
    (1946, "James Martin", "GBR"), (1947, "Holography is invented", "GBR"), (1948, "Basic oxygen steelmaking", "CHE"), (1952, "The float glass", "GBR"),
    (1953, "The first video tape recorder", "JPN"), (1955, "The intermodal container", "USA"), (1958, "The integrated circuit", "USA"),
    (1963, "The first electronic cigarette", "USA"), (1965, "Kevlar is invented", "USA"), (1972, "Herbert Boyer", "USA"), (1974, "The lithium-ion battery", "USA"),
    (1977, "Dr Walter Gilbert", "USA"), (1980, "Scientists Mark Skolnick", "USA"), (1981, "Kane Kramer", "GBR"), (1984, "DNA profiling", "GBR"),
    (1989, "Karlheinz Brandenburg", "DEU"), (1999, "The first capsule endoscopy", "ISR"), (2001, "Wikipedia is launched", "USA"),
    (2002, "Programmer Jonathon Abrams", "USA"), (2003, "Development of the Android", "USA"), (2004, "First podcast", "USA"), (2005, "YouTube", "USA"),
    (2006, "Amazon pioneered", "USA"), (2007, "Apple Inc.", "USA"), (2007, "First Kindle", "USA"), (2009, "The first quantum machine", "USA"),
    (2010, "The first synthetic organism", "USA"), (2014, "The first known", "USA"), (2016, "First commercially available artificial pancreas", "USA"),
    (2016, "First successful launch", "USA"), (2019, "IBM launches", "USA"), (2022, "OpenAI", "USA"), (1774, "John Wilkinson", "GBR"), (1776, "John Wilkinson", "GBR"),
    (1903, "The first successful controlled", "USA"), (1974, "The Transmission Control", "USA"),
]
SKIP_NAMES = {"Isaac Newton", "Galileo Galilei", "Thomas Edison"}   # only when they are mentioned in passing; see note below


def text():
    h = jload(f"{RAW}/{PAGE}")["html"]
    h = re.sub(r'<style.*?</style>|<sup[^>]*class="reference.*?</sup>', "", h, flags=re.S)
    h = re.sub(r"</(p|li|h\d|tr|dd|dt)>", "\n", h)
    t = H.unescape(re.sub(r"<[^>]+>", "", h))
    return [l.strip() for l in t.splitlines()]


if __name__ == "__main__":
    L = text()
    start = next(i for i, l in enumerate(L) if l == "Early modern era")
    end = next(i for i, l in enumerate(L) if i > start and l in ("See also", "References", "Notes"))
    ROWS = []
    for l in L[start:end]:
        m = re.match(r"^(\d{4})(s?)(?:\s*[–-]\s*(\d{4}))?:\s*(.+)$", l)
        if not m:
            continue
        y0 = int(m.group(1)); y1 = int(m.group(3)) if m.group(3) else (y0 + 9 if m.group(2) else y0)
        ROWS.append({"y0": y0, "y1": y1, "y": (y0 + y1) / 2, "t": m.group(4).strip(), "key": l[:max(l.find(":") + 1, 0)] + " " + m.group(4).strip()})
    # inventors with a birthplace point, from the whole Wikidata extract
    J = jload(f"{WORK}/items.json")
    INV = {}
    for d in J["items"]:
        for e in d["inv"]:
            if e["n"] and e["pt"] and " " in e["n"] and len(e["n"]) >= 8:
                INV.setdefault(e["n"], e)
    names = sorted(INV, key=len, reverse=True)
    BYSUR = {}
    for n in names:
        t = n.split(",")[0].split()
        if len(t) >= 2 and len(t[-1]) >= 4 and t[-1][0].isupper():
            BYSUR.setdefault(t[-1], []).append(n)
    how = Counter()
    for r in ROWS:
        r["meth"] = None
        hd = next((iso for y, p, iso in HAND if y == r["y0"] and r["t"].startswith(p)), None)
        if hd:
            lab, la, lo = CC[hd]
            r.update(meth="hand", place=lab, lat=la, lon=lo, iso_hand=hd); how["hand"] += 1
            continue
        hand = next((v for k, v in PLACE.items() if r["key"].startswith(k) or (k[:5] == r["key"][:5] and r["t"].startswith(k[6:].strip()))), "none")
        if hand is None:
            how["unplaced (hand)"] += 1
            continue
        if hand != "none":
            r.update(meth="place", place=hand[0], lat=hand[1], lon=hand[2])
        else:
            hits = []
            for n in names:
                i = r["t"].find(n)
                if i >= 0 and not any(i >= a and i < b for a, b, _ in hits):
                    hits.append((i, i + len(n), n))
            if not hits:   # looser match: same surname and first initial (Samuel Morse = Samuel Finley Breese Morse)
                for m2 in re.finditer(r"\b([A-Z][\w'-]*)\.?((?:\s+[A-Z][\w.'-]*){0,3})\s+([A-Z][\w'-]{3,})\b", r["t"]):
                    for n in BYSUR.get(m2.group(3), []):
                        if n.split()[0] == m2.group(1) or (len(m2.group(1)) == 1 and n.split()[0][0] == m2.group(1)):
                            hits.append((m2.start(), m2.end(), n)); break
            hits.sort()
            if hits:
                e = INV[hits[0][2]]
                r.update(meth="inventor", person=e["n"], place=e["bp"], lon=e["pt"][0], lat=e["pt"][1], cit=e["cit"][:2])
            else:
                for rx, lab, la, lo in COUNTRY_WORDS:
                    if re.search(rx, r["t"]):
                        r.update(meth="country", place=lab, lat=la, lon=lo); break
        how[r["meth"] or "unplaced"] += 1
    jsave({"rows": ROWS, "revid": jload(f"{RAW}/{PAGE}")["revid"]}, f"{WORK}/timeline.json")
    print(len(ROWS), dict(how))
    for r in ROWS if os.environ.get("TL_VERBOSE") else []:
        print(r["y0"], r.get("meth"), "|", r.get("person", ""), "|", r.get("place", ""), "|", r["t"][:70])
