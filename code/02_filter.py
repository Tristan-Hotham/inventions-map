"""Decide which Wikidata items are inventions, and give each a category (written to WORK/inventions.json).

Many of the 24,186 items with an inventor-or-discoverer (P61) or a time of discovery or invention (P575) are not
inventions at all: islands, comets, moons, theorems, minerals, artworks, archaeological finds, diseases, sports, ideas.
The filter works in four steps:
1. Hard drops: an item is dropped if any of its instance-of classes is a natural object, artwork or find, place,
   person, disease, theory or idea, sport or game, dish, brand, malware and the like (DROP_CLASS), unless one of its
   classes is literally 'invention'.
2. Class keeps: an item is kept if one of its classes is a kind of technology (KEEP_CLASS: weapon, vehicle, machine,
   instrument, medicine, software, writing system, material...). The category comes from the label (LABEL_RULES) where
   it matches, else from the class.
3. Items with no class or only generic classes ('product', 'concept', 'device', 'technique'...) are kept only if their
   English label matches a technology word (LABEL_RULES). Wikidata often describes general kinds of thing such as
   'refrigerator' with subclass-of rather than instance-of, so they arrive with no class at all.
4. Hand overrides (OVR) by Wikidata ID, from reading through every kept item with 10 or more sitelinks and every dropped
   item with 20 or more: a category to force-keep, or None to drop (scientific discoveries such as 'electron',
   physical effects, foods and dishes, clothes, theories, words).
Kept items need at least MIN_SL sitelinks (Wikipedia and other Wikimedia pages), the measure of fame used throughout.
"""
from collections import Counter
from common import *

MIN_SL = 5

DROP_CLASS = re.compile(r"\b(human|fictional|island|atoll|archipelago|reef|moon|comet|planet|asteroid|cubewano|plutino|centaur|"
    r"trans-Neptunian|galax|constellation|star\b|nebula|pulsar|crater|cave|archaeolog|hoard|treasure|tomb|grave|burial|sarcophag|"
    r"sculpture|statue|painting|fresco|mosaic|figurine|stele|inscription|manuscript|tablet|codex|mineral|meteorite|diamond|gem|"
    r"disease|disorder|syndrome|symptom|clinical sign|pandemic|virus|SARS|variant|theorem|conjecture|lemma|hypothes|theor(y|ies)|"
    r"law\b|paradox|mathematical|number|integer|polyhedron|graph\b|function\b|constant|equation|inequality|axiom|country|state\b|"
    r"territor|city|settlement|region|continent|lake|river|mountain|volcano|glacier|strait|bay\b|peninsula|cape\b|headland|"
    r"protected area|nature|sport|game\b|chess|ideolog|movement|dish|food\b|cocktail|cultivar|grape|brand|trademark|literary|"
    r"work of art|art genre|art style|fossil|skull|skeleton|mummy|bog body|specimen|holotype|particle|phenomenon|effect\b|scandal|meme|"
    r"leak|vulnerabilit|malware|computer virus|worm\b|rootkit|religio|philosoph|psycholog|economic|political|social|concept|term\b|"
    r"discipline|field of study|branch of|language\b|ruins|temple|church|monument|museum|shipwreck|helmet|hoax|urban legend|"
    r"conspiracy|pseudoscience|alternative medicine|quackery|individual animal|organization|business|event|festival|"
    r"oil field|gas field|mine\b|phonetic alphabet|unit\b|prefix|dance|music genre|poetic|literature|television series|mascot|"
    r"journalism|project|experiment|cell type|anatomical|protein|enzyme|isotope|chemical entity|chemical substance|"
    r"group of stereoisomers|cellular component|biological process|electoral|policy|cryptid|astronomical|map\b|trilemma|argument)", re.I)

# class -> category when the label does not decide
KEEP_CLASS = [
    (r"weapon|firearm|rifle|pistol|revolver|machine gun|artillery|ammunition|cannon|missile|torpedo|grenade|explosive|tank\b|combat vehicle|military vehicle|warship|execution method", "weapons"),
    (r"musical instrument|instrument model|\btoy|toyline|construction set|combination puzzle|photographic|cinematic|animation technique|camera", "culture"),
    (r"vehicle|aircraft|locomotive|rolling stock|watercraft|boat type|ship type|automobile|car model|motorcycle|bicycle|mode of transport|means of transport|spacecraft|launch vehicle|balloon|airship|railway", "transport"),
    (r"medication|drug|vaccine|pharmaceutical|medical device|medical procedure|surg|remedy|essential medicines|antibiotic|medical instrument", "medicine"),
    (r"software|programming language|computer|protocol|file format|network|algorithm|data structure|telecommunication|communication technology|technical standard|storage|processor|memory|cryptosystem|cipher|cryptograph|encoding|website|web browser|operating system|video game console|integrated circuit|semiconductor|electronic component|television|radio|telephone|telegraph|mass media|service on Internet|chatbot|artificial intelligence|hypertext|markup language|barcode|audio release format|physical media format|media format|optical disc|form of communication", "comms"),
    (r"writing system|alphabet|script\b|syllabary|abugida|abjad|notation|numeral|shorthand|printing|typeface|calendar|map projection|character encoding", "writing"),
    (r"measuring instrument|scientific instrument|astronomical instrument|optical instrument|telescope|microscope|laboratory equipment|meteorological instrument|clock|watch\b|navigational instrument|sensor|detector", "science"),
    (r"engine|turbine|motor\b|generator|battery|electrical element|lamp|light source|reactor|machine|mechanism|valve gear|pump", "energy"),
    (r"cooking appliance|home appliance|household|kitchen|furniture|fastener", "home"),
    (r"agricultural|food preservation|food processing", "food"),
    (r"invention|technology|material|polymer|plastic|alloy|fiber|fibre|textile|glass|concrete|\btool|device|instrument|product category|type of product|tangible good|technique|industrial process|chemical process|process\b|method", "tools"),
]
KEEP_CLASS = [(re.compile(p, re.I), c) for p, c in KEEP_CLASS]

LABEL_RULES = [
    (r"\b(gun|guns|rifle|pistol|revolver|cannon|bomb|grenade|missile|torpedo|napalm|bazooka|sword|crossbow|catapult|trebuchet|guillotine|bayonet|machine gun|arquebus|musket|flintlock|bolt action|ballistite|poudre b|land mine|naval mine|tank|dreadnought|greek fire|fire lance|nuclear weapon|camouflage|brodie helmet)\b", "weapons"),
    (r"(vaccin|penicillin|antibiotic|aspirin|insulin|anaesthe|anesthe|surg|stethoscope|syringe|hypodermic|catheter|dialysis|defibrillator|pacemaker|implant|prosthe|orthopedic|bandage|tomograph|endoscop|iron lung|ventilator|inhaler|contact lens|glasses|spectacles|bifocal|trifocal|hearing aid|dentur|morphine|ibuprofen|paracetamol|chemotherapy|transfusion|blood bank|sphygmo|condom|contracepti|nicotine patch|bag valve|airway|forceps|autoinjector|ilizarov|osseointegration|caesarean|cesarean|x-ray|radiograph|antisepsis|aspirin|stent|heart-lung|cochlear|cast\b|pinard|pulmonary|aortic|heller|norwood|blalock|mohs|plastination|anaesthetic|veress|magill|hemocytometer|growth medium|petri)", "medicine"),
    (r"(piano|violin|guitar|organ\b|flute|trumpet|saxophone|clarinet|synthesi[sz]er|theremin|harp\b|drum|accordion|harmonica|ondes|trautonium|moog|chapman stick|sudrophone|saxotromba|marxophone|rhythmicon|waterphone|archicembalo|harpsichord|tuning fork|photograph|camera|cinema|kinetoscope|zoetrope|phénakistoscope|phenakistoscope|praxinoscope|thaumatrope|zoopraxiscope|mutoscope|animation|kaleidoscope|toy|doll|cube\b|pyraminx|ferris wheel|roller coaster|view-master|gramophone|phonograph|loudspeaker|film frame|daguerreotype|heliography|collodion|instant film|photo booth|cinéorama|théâtre optique|action figure|laugh track|wah-wah|effects unit|stereoscope|magic lantern|teddy|frisbee|aerobie|jungle gym|lava lamp)", "culture"),
    (r"(automobile|\bcar\b|bicycle|tricycle|locomotive|railway|\btrain\b|tram\b|airplane|aircraft|airship|balloon|helicopter|hovercraft|\bship\b|steamboat|boat|submarine|canoe|kayak|\bsled|parachute|rocket|monorail|aérotrain|aerotrain|vactrain|aerowagon|skybus|traffic light|macadam|tarmac|chipseal|tunnel boring|tunnelling shield|transporter bridge|cruise control|transmission|derailleur|freewheel|brake|coupler|bogie|sleeping car|couchette|motorcycle|unicycle|dandy horse|velocipede|hippomobile|hopper car|wing fence|naca cowling|grid fin|drogue|gyro monorail|ducted propeller|scuba|aqua-lung|rebreather|caster angle|electric vehicle|carsharing|dual-clutch|torque converter|ice resurfacer|snow blower|tamping machine|forwarder|telescopic handler|harvester|steam shovel|brougham|chuckwagon|rozière|flyboard|dubonnet|tweel|mecanum|whipple shield|gravity assist|vasimr|variable specific impulse)", "transport"),
    (r"(telephone|\bphone|radio|television|telegraph|internet|\bweb\b|world wide web|e-?mail|computer|software|programming|protocol|network|cipher|encryption|cryptograph|\bdisk\b|\bdisc\b|cd-r|cd-rom|dvd|blu-ray|usb|memory|processor|integrated circuit|mosfet|semiconductor|transistor|thyristor|diode|antenna|coaxial|modem|fax|mouse|keyboard|cursor|function key|windows key|display|screen protector|neural network|deep learning|perceptron|machine learning|algorithm|chatbot|blockchain|bitcoin|cookie|qr code|barcode|bar code|universal product code|pdf417|maxicode|codabar|bluetooth|wi-fi|smart card|payment terminal|teller machine|ip camera|wearable|video game|teleprompter|iconoscope|orthicon|vacuum tube|triode|magic eye|traveling-wave tube|cavity magnetron|eidophor|core rope|drum memory|transistor|regular expression|request for comments|datagram|http|html|search engine|operating system|scroll wheel|infinite scrolling|emoji|smiley|vector clock|reed.solomon|turbo code|bch code|golomb|gold code|code\b|auto-encoder|autoencoder|adversarial|lstm|long short-term|recurrent|gated recurrent|boltzmann|hopfield|support vector|transformer \(|ada?line|seven-segment|logic device|array logic|nano-ram|twistor|treap|tree\b|array\b|queue|signature|secret sharing|feistel|playfair|vigenère|jefferson disk|substitution cipher|rockex)", "comms"),
    (r"(alphabet|script\b|writing|braille|shorthand|notation|numeral|\bzero\b|printing|printing press|movable type|typewriter|pencil|\bpen\b|ballpoint|fountain pen|ink\b|\bpaper\b|papyrus|parchment|lithograph|xerograph|photocop|newspaper|encyclopedia|dictionary|projection|calendar|bar chart|pie chart|gantt|pareto|treemap|sparkline|abacus|slide rule|stenotype|linotype|cyclostyle|electrotyp|chromolithograph|blueprint|correction tape|rolodex|embossing tape|tonic sol-fa|morse|semaphore|positional|decimal|sorting|euler diagram|venn|smith chart|karnaugh|harris matrix|contingency table|dot plot)", "writing"),
    (r"(microscop|telescope|thermometer|thermoscope|barometer|hygrometer|anemometer|weighing scale|\bbalance\b|clock|\bwatch\b|chronometer|sextant|octant|astrolabe|backstaff|jacob's staff|compass|gyroscope|spectromet|spectroscop|spectrograph|micrometer|pyrometer|bolometer|radiometer|actinometer|pyranometer|variometer|viscometer|pycnometer|cyanometer|aneroid|potentiometer|stroboscope|oscillo|gauge|ruler|caliper|pendulum|cloud chamber|wire chamber|projection chamber|bubble chamber|detector|interferometer|prism|lens\b|achromat|apochromat|laser|maser|radar|sonar|lidar|seismo|flask|burette|pipette|measuring cylinder|test tube|kipp|autoclave|centrifuge|synchrotron|cyclotron|microtron|accelerator|ion trap|langmuir probe|gunter's chain|theodolite|graphometer|blink comparator|spinthariscope|crookes|kibble|stevenson screen|storm glass|crescograph|sphygmograph|electron microprobe|coherence tomography|metal detector|stud finder|geiger|pitot|electroscope|galvanometer|ammeter|voltmeter|tokamak|fresnel|nicol|mirror system|retrofocus|cooke triplet|pellin|mangin|camera obscura|seismometer|hourglass|sundial|water clock|escapement|mainspring|jewel bearing|level\b|set square|combination square|protractor|parallel rulers|planimeter|recorder|kater)", "science"),
    (r"(refrigerator|vacuum cleaner|dishwasher|washing machine|microwave|oven|stove|rice cooker|slow cooker|pressure cooker|toaster|kettle|shower|toilet|flushometer|bidet|zipper|button|hook and loop|velcro|safety pin|binder clip|paper clip|scissors|\bfork\b|table knife|utility knife|chopsticks|umbrella|\bmatch|lighter|\block\b|electronic lock|furniture|chair|massage|lawn mower|sewing machine|air condition|thermostat|bag\b|paper bag|string bag|bottle|crown cork|can opener|tin can|sharpener|shampoo|soap|toothbrush|toothpaste|diaper|tampon|pantyhose|cotton swab|price tag|cash register|vending|parking meter|shopping cart|coffee filter|espresso|aeropress|dish drying|food mill|cheese slicer|paint roller|pedal bin|hair clipper|kimchi refrigerator|electronic bidet|crowd control barrier|strandkorb|exercise ball|wall bars|treadmill|walker\b|paper shredder|paper cutter|lamp\b|gas lighting|gas mantle|thermal bag|smoke detector|fire extinguisher|elevator|escalator|plumbing|wardian|aquarium|swivel|screen\b|bunk)", "home"),
    (r"(farming|agricultur|plough|\bplow|harvest|reap|thresh|seed drill|tractor|irrigation|fertili[sz]|pasteuri[sz]|canning|margarine|processed cheese|\bbread\b|beer|wine\b|noodle|cup noodle|sugar|flour|carbonated|soda|corn flakes|hydroponic|aeroponic|vertical farming|greenhouse|beehive|langstroth|queen excluder|bee smoker|cotton gin|grow light|mulesing|domestication|fermentation|spherification|instant coffee|canned coffee|dutch-process|creamed honey|peptone|crab stick|chicken nugget|green wall)", "food"),
    (r"(steel|\biron\b|bronze|copper|\bglass\b|laminated glass|borosilicate|concrete|cement|brick|plywood|parallam|rubber|vulcani|plastic|nylon|polyester|acrylic|fib(re|er)|graphene|cellophane|teflon|bakelite|aluminium|aluminum|alloy|\bdye\b|pigment|ultramarine|purple of cassius|paint\b|glue|adhesive|\btape\b|gaffer|surgical tape|\btool\b|wrench|hammer|\bsaw\b|bandsaw|concrete saw|\bdrill|forstner|screw|torx|nail\b|needle|\brope\b|barbed wire|weld|lathe|planer|shaper|axe\b|pottery|ceramic|porcelain|raku|ware\b|weaving|loom|spinning|textile|thread|distillation|electrolysis|hydrogenation|process\b|vapor deposition|sanforization|sherardising|salt glaze|kiln|furnace|forge|smelting|casting|neodymium|ferrocement|carbon fib|dynamite|thermite|fracturing|gömböc|dazzle|toile|forging|mining|bessemer|crucible|lost-wax|electrotyping|lithography|plating|galvani)", "tools"),
    (r"(engine|turbine|motor\b|generator|dynamo|battery|fuel cell|solar cell|solar water|electric|transformer|inductor|capacitor|steam|power\b|reactor|light bulb|incandescent|lightning rod|pump|compressor|press\b|hydraulic|machine|gear\b|crank|governor|piston|valve|boiler|wind turbine|windmill|watermill|water wheel|pelton|nuclear|magnet\b|crystal oscillator|three-phase|arc lamp|neon lamp|davy lamp|safety lamp|wheel\b|pulley|lever|crane|conveyor|ball screw|bearing|linkage|parallel motion|jackhammer|accumulator|vortex tube|stirling|rankine|diesel|aeolipile|heron|ocean thermal|energy|solar|photovoltaic|ćuk|converter|damper|fusible plug|automaton|robot|governor|hourglass)", "energy"),
]
LABEL_RULES = [(re.compile(p, re.I), c) for p, c in LABEL_RULES]
GENERIC = re.compile(r"^(product|concept|device|technique|method|technology|type of device|type of physical object|type of product|"
                     r"product category|tangible good|system|technical system|model|process|feature|notion|idea|term|artificial object|"
                     r"invention|material|tool|type of tool|instrument|object|class|classification|solution|procedure|project)$", re.I)

# hand overrides by Wikidata ID: category to keep, None to drop. Built by reading the kept and dropped lists.
OVR = {
    # kept, with a category fixed by hand
    "Q68": "comms", "Q1420": "transport", "Q11035": "comms", "Q11656": "comms", "Q5322": "energy", "Q5325": "energy", "Q267298": "energy",
    "Q11658": "energy", "Q85810444": "comms", "Q185639": "weapons", "Q48171": "science", "Q189880": "comms", "Q908463": "comms",
    "Q959646": "culture", "Q1334758": "science", "Q379754": "home", "Q966893": "writing", "Q173412": "science", "Q16629185": "culture",
    "Q944090": "comms", "Q1427360": "comms", "Q14169302": None, "Q83913": "comms", "Q173431": "comms", "Q199769": "writing",
    "Q1031639": "transport", "Q1094365": "tools", "Q1022471": "tools", "Q1164918": "writing", "Q1135572": "transport",
    "Q11032": "writing", "Q872": "comms", "Q26540": "comms", "Q7987": "comms", "Q12190": "medicine", "Q47433": "writing",
    "Q101761": "home", "Q172587": "tools", "Q189511": "home", "Q208040": "tools", "Q186819": "culture", "Q181008": "culture",
    "Q178032": "energy", "Q174053": "energy", "Q187956": "transport", "Q209440": "energy", "Q188245": "tools", "Q203174": "medicine",
    "Q960800": "tools", "Q188990": "medicine", "Q192803": "writing", "Q191413": "transport", "Q864088": "medicine",
    "Q188639": "comms", "Q487875": "science", "Q857300": "medicine", "Q899868": "medicine", "Q337724": "energy", "Q192902": "comms",
    "Q747713": "home", "Q873501": "comms", "Q714750": "science", "Q257916": "science", "Q628007": "comms", "Q181331": "home",
    "Q211586": "comms", "Q245471": "comms", "Q603227": "comms", "Q21161871": "transport", "Q749635": "energy", "Q755662": "comms",
    "Q427161": "tools", "Q202957": "comms", "Q898762": "tools", "Q1128559": "energy", "Q163889": "comms", "Q1172965": "culture",
    "Q623950": "comms", "Q893396": "food", "Q203071": "comms", "Q208442": "writing", "Q667558": "writing", "Q621412": "writing",
    "Q243350": "writing", "Q104394": "writing", "Q214796": "writing", "Q427676": "writing",
    "Q11633": "culture", "Q8811": "comms", "Q115564437": "comms", "Q47043": "culture", "Q20514253": "comms", "Q12203": "comms",
    "Q186969": "medicine", "Q177941": "tools", "Q18216": "medicine", "Q170484": "culture", "Q229345": "culture", "Q183976": "comms",
    "Q149757": "comms", "Q150758": "comms", "Q2063": "comms", "Q249": "comms", "Q422244": "medicine", "Q575650": "comms",
    "Q46794": "comms", "Q208138": "science", "Q201436": "comms", "Q107701": "writing", "Q207786": "culture", "Q211736": "energy",
    "Q622424": "energy", "Q35221": "science", "Q4990531": "medicine", "Q844123": "tools", "Q23361": "science",
    "Q17084460": "comms", "Q46872": "culture", "Q1417461": "food", "Q56192172": "writing", "Q326237": "transport", "Q940334": "comms",
    "Q3033860": "culture", "Q160719": "culture", "Q744618": "culture", "Q185120": "home", "Q867068": "tools", "Q511450": "weapons",
    "Q421898": "tools", "Q418758": "medicine", "Q541151": "writing", "Q963903": "writing", "Q1141440": "writing", "Q1485203": "culture",
    "Q742318": "science", "Q261468": "writing", "Q1152543": "writing", "Q581192": "writing", "Q207684": "medicine", "Q422112": "medicine",
    "Q167447": "culture", "Q21204": "writing", "Q244627": "comms", "Q1165219": "comms", "Q263544": "comms", "Q624546": "comms",
    "Q831575": "writing", "Q865144": "writing",
    # dropped: discoveries, phenomena, ideas, methods of analysis, places, words, foods and finds
    "Q12725": None, "Q8183": None, "Q11448": None, "Q163820": None, "Q80294": None, "Q178377": None, "Q131303": None,
    "Q188533": None, "Q237525": None, "Q208042": None, "Q203698": None, "Q74304": None, "Q10861030": None, "Q726474": None,
    "Q23638": None, "Q345137": None, "Q396845": None, "Q865788": None, "Q865019": None, "Q652675": None, "Q560589": None,
    "Q596446": None, "Q747702": None, "Q1139051": None, "Q49385": None, "Q846110": None, "Q840304": None, "Q2091716": None,
    "Q868454": None, "Q301990": None, "Q1501864": None, "Q2299867": None, "Q816151": None, "Q2075856": None, "Q183759": None,
    "Q23529": None, "Q496327": None, "Q1711677": None, "Q642514": "comms",
    "Q1089649": None, "Q186610": None, "Q30312614": None, "Q901378": None, "Q1856554": None, "Q576578": None, "Q1820313": None,
    "Q1263570": None, "Q1364980": None, "Q1003136": None, "Q220986": None, "Q1612436": None, "Q1812910": None, "Q1362264": None,
    "Q2711120": None, "Q5807210": None, "Q336907": None, "Q1436211": None, "Q498419": None, "Q1294584": None, "Q1929599": None,
    "Q1503202": None, "Q864261": None, "Q705651": None, "Q2227780": None, "Q389963": None, "Q7981210": None, "Q771940": None,
    "Q2470499": None, "Q10862754": None, "Q3748369": None, "Q64470499": None, "Q12029714": None, "Q744654": None, "Q1205942": None,
    "Q2452504": None, "Q2912993": None, "Q1046024": None, "Q847158": None, "Q1784754": None, "Q2036525": None, "Q3738960": None,
    "Q640851": None, "Q2539852": None, "Q20789991": None, "Q1151289": None, "Q1138628": None, "Q385545": None, "Q2003186": None,
    "Q2916210": None, "Q2417519": None, "Q2197698": None, "Q1162673": "medicine", "Q1147813": "writing", "Q127878612": "comms",
    "Q1322057": "comms", "Q1020380": "comms", "Q640119": "comms", "Q4428206": "comms", "Q636990": "weapons", "Q1136013": "comms",
    "Q1230557": "food", "Q139622": "science", "Q884408": "science", "Q732942": "comms", "Q1033196": "comms", "Q7832459": "comms",
    "Q17102763": "medicine", "Q2742627": "home", "Q905353": "home", "Q1751629": "weapons", "Q1088166": "culture", "Q1628577": "comms",
    "Q564946": None, "Q565368": None, "Q7131240": "weapons",
}


def label_cat(n):
    for rx, c in LABEL_RULES:
        if rx.search(n):
            return c
    return None


def classify(d):
    if d["q"] in OVR:
        return OVR[d["q"]], "override"
    cls = d["cls"]
    if not d["n"]:
        return None, "no English label"
    is_inv = any(c.lower() == "invention" for c in cls)
    if not is_inv and any(DROP_CLASS.search(c) for c in cls):
        return None, "dropped class"
    lc = label_cat(d["n"])
    specific = [c for c in cls if not GENERIC.match(c)]
    for c in cls:
        for rx, cat in KEEP_CLASS:
            if rx.search(c) and (cat != "tools" or not specific or c in specific):
                return lc or cat, "class"
    if not specific and lc:
        return lc, "label"
    return None, "not a technology class" if specific else "no technology word"


if __name__ == "__main__":
    J = jload(f"{WORK}/items.json")
    keep, why = [], Counter()
    for d in J["items"]:
        cat, how = classify(d)
        d["cat"], d["how"] = cat, how
        why[(cat is not None, how)] += 1
        if cat and d["sl"] >= MIN_SL:
            keep.append(d)
    print(why.most_common())
    print("kept", len(keep), Counter(d["cat"] for d in keep).most_common())
    jsave({"items": J["items"], "keep": [d["q"] for d in keep]}, f"{WORK}/classified.json")
