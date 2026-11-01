## Title

[OC] Where inventions came from, 3.3 million years on one map: farming was invented 11 separate times, and the "centre of invention" moved from Mesopotamia to China, Europe and the US

## Body

I mapped 115 early innovations (placed and dated from the text of nine Wikipedia pages, keeping ranges and multiple places), the 314 entries since 1500 in Wikipedia's Timeline of historic inventions, and 1,443 inventions from Wikidata. The red line is the average position of each period's landmark inventions: Africa in the deep past, West Asia from 10,000 BC (51% of landmarks from 5000 to 2000 BC), China from AD 1 to 1500 (50%), Europe from 1500 (100% of 1500 to 1700), North America from 1950 (55%). Big caveat: 91% of Wikidata's mapped inventions are in Europe or North America (home to 14% of people today), and 83% are credited to one named person. It maps the written record, mostly English, not human ingenuity. Interactive map with a time slider, play button and search: https://maps.tristanhotham.com/inventions-map/

## Source comment

Sources: English Wikipedia (CC BY-SA 4.0), 2026: Timeline of historic inventions, Timeline of prehistory, Neolithic Revolution, Domestication, History of writing, Wheel, Bronze Age, List of Indian inventions and discoveries, Islamic Golden Age. Wikidata via QLever (CC0), 2026: items with an inventor (P61) or time of invention (P575), filtered to technologies, placed at the location of invention, else the inventor's birthplace, else the country of origin. Natural Earth (public domain). Centre of invention = mean latitude and longitude of each period's landmarks.

Tools: Python (shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/inventions-map/
Paper: https://doi.org/10.5281/zenodo.23856736
Blog post: https://blog.tristanhotham.com/2026/10/31/inventions-map/
