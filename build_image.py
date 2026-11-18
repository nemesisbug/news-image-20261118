#!/usr/bin/env python3
"""Draw 'The World in One Day' v3 - 18 November 2026 world news, dense front page.

36 real, verified 18 Nov 2026 stories in three columns (headline + one-line
summary each), masthead, recognisable lon/lat world map with pins for the six
lead stories, and a 'By the numbers' strip. Deterministic: no network, no
timestamps, no randomness. Output: entry.png, 1024x1024, < 1 MiB.

v3 fixes (blind-review HOLD on v2): body copy line-height raised to 16px so no
descender ever touches the next line; SpaceX, diesel, M51.3, Spain strike and
Korea Java stories corrected/replaced with verified 17-18 Nov reporting;
map redrawn from lon/lat coastlines with legible pin labels and legend.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
BOLD = FONT_DIR + "LiberationSans-Bold.ttf"
REG = FONT_DIR + "LiberationSans-Regular.ttf"

PAPER = (247, 243, 235)
NAVY = (20, 33, 61)
NAVY2 = (28, 46, 84)
INK = (24, 28, 38)
GREY = (74, 78, 88)
WHITE = (255, 255, 255)
RED = (192, 57, 43)
GOLD = (232, 163, 61)
MAP_BG = (214, 230, 238)
LAND = (176, 196, 178)
GRID = (200, 218, 226)
LINE = (222, 217, 205)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w, first_w=None):
    """Greedy word wrap; first line may have a different width."""
    words = text.split()
    lines, cur = [], ""
    limit = first_w if first_w is not None else max_w
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            limit = max_w
    if cur:
        lines.append(cur)
    return lines


# (tag, accent, headline, summary) - every fact verified against 17-18 Nov 2026 editions.
STORIES = [
    ("GULF", (27, 42, 74), "Bahrain sounds all-clear as Gulf tensions flare",
     "Bahrain lifts its shelter alert as Kuwait downs drones; the US strikes an Iranian missile site in reply."),
    ("UKRAINE", (192, 57, 43), "Ukraine hits Crimea bridge a second day",
     "Kyiv strikes the Kerch Bridge for a second straight day as Russia pounds bridges in Kyiv; the bridge is partly down."),
    ("DIPLOMACY", (31, 111, 167), "Trump lands in Manila for Quad talks",
     "Trump arrives in Manila for Quad talks ahead of his China visit, as ASEAN and East Asia Summit leaders meet."),
    ("BUSINESS", (11, 61, 46), "Nvidia doubles revenue without Huang",
     "Nvidia posts $115.8bn quarterly revenue, up 103% year on year; its board says it will not reinstate Jensen Huang."),
    ("ISRAEL", (128, 32, 32), "Eisenkot bloc ousts Netanyahu ally as speaker",
     "The Knesset elects Matan Kahana speaker, 66-52, replacing Amir Ohana in a blow to caretaker PM Netanyahu."),
    ("MARKETS", (120, 80, 10), "AI trade unwind sinks global stocks",
     "Stocks fall worldwide ahead of Nvidia results: S&P 500 -1%, Dow -1.6%, Europe and the UK -1.8%, worst since March."),
    ("TECH", (90, 60, 140), "Anthropic prices record IPO today",
     "Anthropic prices its IPO at $70-$78 a share, a sale of up to $64.4bn valuing it near $1.4tn; trading starts Thursday."),
    ("MIDEAST", (128, 32, 32), "Britain sanctions settlement firms",
     "The UK sanctions eight firms over illegal West Bank settlements; Australia announces fresh sanctions too."),
    ("TRADE", (31, 111, 107), "Canada and China extend trade deals",
     "Canada and China extend trade deals as Xi meets Carney ahead of the APEC summit."),
    ("KOREA", (31, 111, 167), "Putin to meet Lee at APEC summit",
     "The Kremlin says Putin will meet South Korea's Lee Jae Myung in Shenzhen, their first face-to-face talks."),
    ("USA", (27, 42, 74), "Man held over threat to blow up biofuel plant",
     "An Illinois man is charged after a bomb threat at a Peoria biofuels plant forced 2,500 homes to evacuate."),
    ("EUROPE", (31, 111, 167), "Estonia to shut Russia border",
     "Estonia plans to close its border crossings with Russia from December after an attempted attack on a defence firm."),
    ("CZECHIA", (192, 57, 43), "Huge Prague rally defends free media",
     "Hundreds of thousands march in Prague against a proposed media law, demanding press independence."),
    ("RUSSIA", (192, 57, 43), "Russia and Ukraine trade drone strikes",
     "Russia and Ukraine trade drone attacks days after Abu Dhabi talks end with no deal, only a prisoner-swap plan."),
    ("USA", (27, 42, 74), "One router grounds every US flight",
     "An FAA ground stop halts all US departures for four hours after a router fault; 15,000 flights are cancelled."),
    ("FRANCE", (31, 111, 167), "Student protests swell as unions join",
     "Student protests escalate across France, with blockades at high schools and universities as unions join in."),
    ("SPAIN", (192, 57, 43), "Spain rail strike halts trains",
     "A nationwide rail strike disrupts trains across Spain, a week after its first general strike in 14 years."),
    ("GERMANY", (11, 61, 46), "Germany's wise men lift growth call to 1.3%",
     "Germany's Council of Economic Experts raises its 2026 growth forecast to 1.3%, from 0.5%."),
    ("ENERGY", (120, 80, 10), "Russian diesel tankers turn away from US",
     "Tankers carrying Russian diesel turn away from US ports, a month after Trump's deal, as buyers fear lawsuits."),
    ("CLIMATE", (31, 111, 107), "England still in drought across 82% of land",
     "England stays in drought across 82% of its territory after its hottest summer on record, with reservoirs low."),
    ("INDIA", (180, 110, 20), "Modi pushes free e-visas at ASEAN summit",
     "PM Modi proposes free e-visas and maritime cooperation at the East Asia Summit in Manila."),
    ("INDIA", (180, 110, 20), "India re-elected to ITU Council to 2030",
     "India wins re-election to the International Telecommunication Union Council for 2027-2030."),
    ("TAIWAN", (31, 111, 167), "US presses UN body over Taiwan flights",
     "The US presses a UN aviation agency over Taiwan flight restrictions; China hits back."),
    ("SPORT", (11, 61, 46), "Dhoni retires from IPL, becomes CSK mentor",
     "MS Dhoni, 45, ends his IPL playing career after 278 matches and five titles and becomes Chennai's mentor."),
    ("SPORT", (11, 61, 46), "Jay Shah re-elected ICC chairman",
     "Jay Shah is re-elected ICC chairman for a second consecutive term."),
    ("BANKS", (120, 80, 10), "Deutsche Bank 'ignored risk warnings'",
     "Leaked files show Deutsche Bank dismissed compliance warnings over risky clients, including Russian oligarchs."),
    ("LAW", (27, 42, 74), "Trump BBC deposition deadline extended",
     "A judge extends Trump's deposition deadline in his $10bn BBC defamation suit to 22 January."),
    ("CARIBBEAN", (31, 111, 107), "St Kitts to wind down passport sales",
     "St Kitts and Nevis will wind down its citizenship-by-investment scheme after the EU threatened visa-free access."),
    ("HEALTH", (192, 57, 43), "US loses measles-free status",
     "The US loses its measles elimination status after 26 years amid record cases."),
    ("UKRAINE", (192, 57, 43), "UN: 372 civilians killed in Ukraine in October",
     "The UN says at least 372 civilians were killed in Ukraine in October."),
    ("GAZA", (128, 32, 32), "Gaza families down to one hot meal",
     "The WFP says displaced families in Gaza get one hot meal every two days as cooking gas runs short."),
    ("JAPAN", (180, 110, 20), "Japan exports rise for 14th month",
     "Japan's exports grow for a 14th straight month in October, hitting a record ¥11.8tn on semiconductor demand."),
    ("SPACE", (90, 60, 140), "SpaceX catches Starship from orbit, loses booster",
     "SpaceX catches Ship 42 from orbit for the first time; the Super Heavy booster aborts its catch and is lost."),
    ("WEATHER", (31, 111, 107), "Cyclone Akvan grows in Bay of Bengal",
     "Cyclone Akvan intensifies over the Bay of Bengal, with India's weather office warning coastal states."),
    ("LATVIA", (31, 111, 167), "Kulbergs government wins vote",
     "Latvia's parliament approves the new Kulbergs government in a confidence vote."),
    ("INDIA", (180, 110, 20), "Amazon pledges $7bn for renewables",
     "Amazon pledges $7bn for renewable energy in India by 2030."),
]

NUMBERS = [
    ("$115.8bn", "Nvidia quarterly revenue"),
    ("66-52", "Knesset speaker vote"),
    ("$64.4bn", "Anthropic IPO sale"),
    ("$64,844", "Bitcoin as stocks slid"),
    ("82%", "of England in drought"),
    ("372", "killed in Ukraine in Oct"),
]

# --- world map: lon/lat coastline polygons, equirectangular projection -----
MAP_TOP, MAP_BOT = 84, 192
MAP_Y0, MAP_Y1 = 104, 188
LAT_TOP, LAT_BOT = 82, -58


def project(lon, lat):
    x = (lon + 180) / 360 * W
    y = MAP_Y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (MAP_Y1 - MAP_Y0)
    return (x, y)


CONTINENTS = [
    # North America
    [(-168, 66), (-161, 58), (-153, 58), (-145, 60), (-140, 60), (-135, 58),
     (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-100, 18), (-95, 19), (-90, 21), (-86, 16), (-83, 9),
     (-80, 8), (-77, 8), (-79, 9), (-82, 13), (-84, 16), (-87, 15),
     (-88, 18), (-90, 14), (-92, 15), (-94, 17), (-97, 16), (-97, 19),
     (-96, 19), (-93, 18), (-90, 19), (-87, 21), (-84, 22), (-82, 25),
     (-80, 26), (-81, 31), (-79, 33), (-76, 35), (-74, 39), (-70, 42),
     (-68, 44), (-65, 45), (-60, 47), (-55, 47), (-53, 49), (-55, 52),
     (-60, 55), (-64, 58), (-68, 58), (-72, 55), (-78, 55), (-80, 58),
     (-85, 60), (-88, 60), (-92, 62), (-95, 66), (-100, 68), (-110, 68),
     (-120, 69), (-130, 70), (-140, 70), (-150, 70), (-158, 71),
     (-165, 68)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 74), (-30, 76),
     (-45, 76), (-55, 75), (-58, 72), (-55, 68), (-52, 64), (-48, 60)],
    # South America
    [(-79, 9), (-77, 7), (-75, 10), (-72, 12), (-68, 11), (-64, 10),
     (-60, 8), (-55, 6), (-52, 5), (-50, 0), (-48, -2), (-44, -3),
     (-40, -5), (-37, -6), (-35, -8), (-37, -12), (-39, -16), (-40, -20),
     (-42, -23), (-46, -24), (-48, -27), (-52, -32), (-55, -35),
     (-58, -38), (-62, -41), (-65, -43), (-67, -46), (-68, -50),
     (-70, -52), (-72, -50), (-73, -45), (-73, -40), (-73, -35),
     (-72, -30), (-71, -25), (-70, -20), (-75, -15), (-78, -10),
     (-80, -5), (-81, 0), (-80, 3), (-79, 7)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-1, 49), (2, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65),
     (20, 65), (18, 69), (25, 71), (31, 70), (30, 66), (24, 60), (20, 58),
     (18, 55), (13, 54), (8, 55), (5, 58), (0, 57), (-3, 55), (-5, 53),
     (-3, 51), (-5, 50), (-2, 48), (-5, 47), (-2, 44), (-4, 44), (-6, 43),
     (-9, 43), (-9, 37), (-5, 36), (0, 38), (3, 42), (7, 44), (12, 44),
     (14, 45), (19, 45), (23, 40), (26, 38), (23, 37), (20, 40), (19, 42),
     (15, 44), (12, 44), (8, 44), (3, 43), (0, 38), (-2, 37), (-6, 36),
     (-9, 37)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 54), (0, 52),
     (-2, 51), (-4, 50)],
    # Africa
    [(-17, 15), (-16, 20), (-13, 27), (-9, 31), (-5, 35), (0, 36),
     (10, 37), (11, 34), (19, 32), (25, 32), (30, 31), (32, 31), (34, 28),
     (35, 24), (37, 20), (39, 16), (41, 12), (43, 11), (48, 11), (51, 11),
     (51, 6), (48, 2), (44, -2), (41, -4), (40, -8), (40, -12), (39, -16),
     (36, -20), (35, -23), (33, -26), (31, -29), (28, -33), (25, -34),
     (20, -35), (17, -33), (15, -28), (13, -22), (12, -18), (13, -12),
     (12, -8), (9, -1), (9, 4), (6, 4), (2, 6), (-4, 5), (-8, 5),
     (-11, 7), (-14, 9), (-17, 12)],
    # Asia
    [(28, 41), (30, 36), (36, 36), (39, 32), (43, 29), (48, 29), (50, 27),
     (54, 26), (57, 26), (61, 25), (66, 25), (69, 23), (72, 20), (76, 14),
     (77, 8), (80, 9), (82, 16), (86, 20), (89, 22), (92, 21), (94, 17),
     (97, 15), (99, 10), (101, 6), (103, 1), (104, 2), (103, 7), (101, 11),
     (100, 13), (103, 10), (105, 9), (107, 11), (109, 14), (109, 18),
     (106, 20), (108, 21), (110, 20), (113, 22), (116, 23), (119, 25),
     (120, 28), (121, 31), (120, 34), (122, 37), (124, 39), (126, 40),
     (128, 38), (127, 35), (129, 35), (130, 38), (132, 42), (135, 43),
     (138, 46), (141, 50), (141, 53), (140, 56), (137, 59), (140, 60),
     (142, 59), (150, 60), (156, 52), (158, 53), (162, 56), (162, 60),
     (169, 60), (170, 66), (178, 65), (178, 68), (170, 68), (160, 70),
     (150, 72), (140, 72), (130, 72), (120, 73), (110, 74), (100, 76),
     (90, 75), (80, 73), (70, 72), (60, 69), (55, 62), (55, 55), (50, 50),
     (48, 47), (44, 44), (40, 42), (36, 41), (32, 41)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (141, 44), (143, 42), (141, 39), (140, 36), (138, 35),
     (136, 34), (133, 34), (131, 33)],
    # Sumatra + Borneo
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (105, -7), (102, -5),
     (99, -2), (96, 2)],
    [(109, 0), (112, -2), (114, -3), (117, -3), (117, 1), (114, 3),
     (111, 2)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (147, -39), (150, -37), (153, -32), (153, -27),
     (151, -24), (149, -20), (146, -19), (143, -15), (142, -11),
     (141, -13), (139, -17), (136, -15), (135, -12), (132, -12),
     (130, -13), (128, -14), (126, -14), (124, -15), (122, -17),
     (120, -20), (117, -20), (114, -22)],
]
# pins: (lon, lat, number, label, label side 'r' right / 'l' left)
PINS = [
    (51, 26, "1", "GULF", "r"),
    (34, 45, "2", "CRIMEA", "r"),
    (121, 15, "3", "MANILA", "r"),
    (0, 51, "4", "LONDON", "r"),
    (116, 40, "5", "BEIJING", "l"),
    (-74, 41, "6", "NEW YORK", "r"),
]


def draw_map(d):
    d.rectangle([0, MAP_TOP, W, MAP_BOT], fill=MAP_BG)
    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        x = (lon + 180) / 360 * W
        d.line([x, MAP_Y0, x, MAP_Y1], fill=GRID, width=1)
    for lat in range(-30, 81, 30):
        y = MAP_Y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (MAP_Y1 - MAP_Y0)
        d.line([0, y, W, y], fill=GRID, width=1)
    for poly in CONTINENTS:
        d.polygon([project(lon, lat) for lon, lat in poly],
                  fill=LAND, outline=(150, 172, 154))
    d.text((24, 90), "WHERE THE DAY HAPPENED", font=font(BOLD, 11), fill=NAVY2)
    legend = "1 GULF  ·  2 CRIMEA  ·  3 MANILA  ·  4 LONDON  ·  5 BEIJING  ·  6 NEW YORK"
    f_leg = font(BOLD, 11)
    d.text((W - 24 - d.textlength(legend, font=f_leg), 90), legend,
           font=f_leg, fill=NAVY2)
    f_pin = font(BOLD, 11)
    f_lab = font(BOLD, 11)
    for lon, lat, num, label, side in PINS:
        x, y = project(lon, lat)
        x, y = int(round(x)), int(round(y))
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED, outline=WHITE, width=2)
        nw = d.textlength(num, font=f_pin)
        d.text((x - nw / 2, y - 8), num, font=f_pin, fill=WHITE)
        lw = d.textlength(label, font=f_lab)
        if side == "r":
            lx, ly = x + 12, y - 6
        else:
            lx, ly = x - 12 - lw, y - 6
        d.rectangle([lx - 2, ly - 1, lx + lw + 2, ly + 12], fill=MAP_BG)
        d.text((lx, ly), label, font=f_lab, fill=NAVY)


def main():
    assert len(STORIES) == 36, len(STORIES)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 80], fill=NAVY)
    d.rectangle([0, 80, W, 84], fill=RED)
    d.text((20, 8), "THE WORLD IN ONE DAY", font=font(BOLD, 40), fill=WHITE)
    d.text((20, 52), "WEDNESDAY 18 NOVEMBER 2026  ·  36 STORIES  ·  6 CONTINENTS  ·  ONE FRONT PAGE",
           font=font(BOLD, 15), fill=GOLD)
    d.rectangle([W - 158, 10, W - 20, 68], outline=GOLD, width=2)
    d.text((W - 146, 14), "36", font=font(BOLD, 26), fill=WHITE)
    d.text((W - 108, 22), "STORIES", font=font(BOLD, 16), fill=GOLD)
    d.text((W - 146, 46), "in one image", font=font(REG, 12), fill=(200, 210, 225))

    draw_map(d)

    # ---- story grid: 3 cols x 12 rows ----------------------------------
    # Body copy: 11pt on a 16px baseline grid (1.45x) - descenders can never
    # touch the next line's ascenders. No row rules: worst-case rows reach
    # the row edge, so rules would strike through descenders.
    margin, gap = 20, 12
    col_w = (W - 2 * margin - 2 * gap) // 3   # 320
    row_h = 59
    grid_y = 196
    f_head = font(BOLD, 14)
    f_sum = font(REG, 11)
    for i, (tag, accent, head, summ) in enumerate(STORIES):
        col, row = i % 3, i // 3
        x = margin + col * (col_w + gap)
        y = grid_y + row * row_h
        tag_txt = tag + "  "
        tag_w = d.textlength(tag_txt, font=f_head)
        lines = wrap(d, head, f_head, col_w, first_w=col_w - tag_w)
        assert len(lines) <= 2, (i, head, lines)
        # headline line 1 carries the tag in accent colour
        d.text((x, y), tag_txt, font=f_head, fill=accent)
        d.text((x + tag_w, y), lines[0], font=f_head, fill=INK)
        hy = y + 15
        if len(lines) > 1:
            d.text((x, hy), lines[1], font=f_head, fill=INK)
            hy += 15
        slines = wrap(d, summ, f_sum, col_w)
        assert len(slines) <= 2, (i, summ, slines)
        sy = hy
        for ln in slines:
            d.text((x, sy), ln, font=f_sum, fill=GREY)
            sy += 16
        # last summary baseline + 13px glyph depth must stay inside the row
        assert hy + 16 * (len(slines) - 1) + 13 <= y + row_h, (i, summ)
    # column dividers
    for cx in (margin + col_w + gap // 2, margin + 2 * col_w + gap + gap // 2):
        d.line([cx, grid_y, cx, grid_y + 12 * row_h - 6], fill=LINE, width=1)

    # ---- by the numbers --------------------------------------------------
    ny0 = 908
    d.rectangle([0, ny0, W, ny0 + 54], fill=NAVY2)
    d.text((20, ny0 + 6), "BY THE NUMBERS", font=font(BOLD, 13), fill=GOLD)
    seg_w = (W - 40) // 6
    f_num = font(BOLD, 17)
    f_cap = font(REG, 10)
    for j, (num, cap) in enumerate(NUMBERS):
        sx = 20 + j * seg_w
        d.text((sx, ny0 + 22), num, font=f_num, fill=WHITE)
        cap_lines = wrap(d, cap, f_cap, seg_w - 8)
        cy = ny0 + 40
        for ln in cap_lines[:1]:
            d.text((sx, cy), ln, font=f_cap, fill=(200, 210, 225))

    # ---- footer ----------------------------------------------------------
    d.text((20, 970), "Sources: Reuters · AP · BBC · The Guardian · Al Jazeera · Hindustan Times — 18 November 2026",
           font=font(REG, 12), fill=(110, 108, 100))
    d.text((20, 988), "Every headline verified against 17–18 November 2026 editions. Drawn with Python + Pillow; no network, no timestamps — byte-identical reruns.",
           font=font(REG, 11), fill=(110, 108, 100))

    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
