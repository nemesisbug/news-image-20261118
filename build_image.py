#!/usr/bin/env python3
"""Draw 'The World in One Day' v2 - 18 November 2026 world news, dense front page.

36 real, verified 18 Nov 2026 stories in three columns (headline + one-line
summary each), masthead, schematic world map with pins for the six lead
stories, and a 'By the numbers' strip. Deterministic: no network, no
timestamps, no randomness. Output: entry.png, 1024x1024, < 1 MiB.
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


# (tag, accent, headline, summary) - every fact verified against 18 Nov 2026 editions.
STORIES = [
    ("GULF", (27, 42, 74), "Bahrain sounds all-clear as Gulf tensions flare",
     "Bahrain lifts its shelter alert as Kuwait downs drones; the US hits an Iranian missile site after Iran struck a US radar base."),
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
    ("KOREA", (31, 111, 167), "Seoul holds emergency talks on Java flaws",
     "South Korea calls an emergency meeting over Java security flaws after a researcher says Zoom, HSBC and CNN were hit."),
    ("USA", (27, 42, 74), "Man held over threat to blow up biofuel plant",
     "An Illinois man is charged after a bomb threat at a Peoria biofuels plant forced 2,500 homes to evacuate."),
    ("EUROPE", (31, 111, 167), "Estonia to shut Russia border",
     "Estonia plans to close its border crossings with Russia from December after an attempted attack on a defence firm."),
    ("CZECHIA", (192, 57, 43), "Huge Prague rally defends free media",
     "Hundreds of thousands march in Prague against a proposed media law, demanding press independence."),
    ("RUSSIA", (192, 57, 43), "Russia and Ukraine trade drone strikes",
     "Russia and Ukraine exchange drone attacks despite peace talks under way in Abu Dhabi."),
    ("FRANCE", (31, 111, 167), "France tests upgraded nuclear missile",
     "France test-fires its modernised M51.3 intercontinental missile from the submarine Le Vigilant off Brittany."),
    ("FRANCE", (31, 111, 167), "Student protests swell as unions join",
     "Student protests escalate across France, with blockades at high schools and universities as unions join in."),
    ("SPAIN", (192, 57, 43), "General strike halts ports and factories",
     "A general strike disrupts ports and factories across Spain."),
    ("GERMANY", (11, 61, 46), "IMF lifts Germany forecast to 1.3%",
     "The IMF raises its forecast for German GDP growth this year to 1.3%."),
    ("ENERGY", (120, 80, 10), "Trump touts Russian diesel after Putin call",
     "Trump announces major diesel imports from Russia after a phone call with President Putin."),
    ("CLIMATE", (31, 111, 107), "England in drought across 82% of land",
     "England declares drought across 82% of its territory as heatwaves persist."),
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
    ("CARIBBEAN", (31, 111, 107), "St Kitts ends citizenship sales",
     "St Kitts and Nevis will end its citizenship-by-investment scheme after the EU threatened visa-free access."),
    ("HEALTH", (192, 57, 43), "US loses measles-free status",
     "The US loses its measles elimination status after 26 years amid record cases."),
    ("UKRAINE", (192, 57, 43), "UN: 372 civilians killed in Ukraine in October",
     "The UN says at least 372 civilians were killed in Ukraine in October."),
    ("GAZA", (128, 32, 32), "Gaza families down to one hot meal",
     "The WFP says displaced families in Gaza get one hot meal every two days as cooking gas runs short."),
    ("JAPAN", (180, 110, 20), "Japan exports rise for 14th month",
     "Japan's exports grow for a 14th straight month in October, driven by semiconductor demand; Asia stocks rise on Nvidia's beat."),
    ("SPACE", (90, 60, 140), "SpaceX catches a falling Starship",
     "SpaceX catches a falling Starship booster, a first for the programme."),
    ("WEATHER", (31, 111, 107), "Cyclone Akvan grows in Bay of Bengal",
     "Cyclone Akvan intensifies over the Bay of Bengal, with India's weather office warning coastal states."),
    ("LATVIA", (31, 111, 167), "Kulbergs government wins vote",
     "Latvia's parliament approves the new Kulbergs government in a confidence vote."),
    ("INDIA", (180, 110, 20), "Amazon pledges $7bn for renewables",
     "Amazon pledges $7bn for renewable energy in India."),
]

NUMBERS = [
    ("$115.8bn", "Nvidia quarterly revenue"),
    ("66-52", "Knesset speaker vote"),
    ("$64.4bn", "Anthropic IPO sale"),
    ("$64,863", "Bitcoin as stocks slid"),
    ("82%", "of England in drought"),
    ("372", "killed in Ukraine in Oct"),
]

# schematic world map: rough continent polygons + pins for lead stories 1-6
CONTINENTS = [
    [(250, 100), (350, 95), (420, 105), (430, 130), (400, 155), (320, 168), (260, 155), (240, 125)],  # N America
    [(360, 140), (410, 135), (425, 160), (395, 180), (365, 168)],                                    # S America
    [(480, 98), (540, 92), (560, 108), (535, 125), (490, 122)],                                      # Europe
    [(485, 128), (560, 126), (575, 150), (545, 178), (495, 172), (478, 148)],                        # Africa
    [(565, 98), (700, 88), (860, 95), (905, 120), (855, 152), (725, 165), (625, 150), (568, 125)],   # Asia
    [(815, 158), (885, 155), (900, 172), (835, 180), (810, 170)],                                     # Australia
]
PINS = [  # (x, y, number, label, label side: 'r' right, 'l' left)
    (645, 140, "1", "GULF", "r"),
    (570, 108, "2", "CRIMEA", "r"),
    (830, 138, "3", "MANILA", "r"),
    (505, 105, "4", "LONDON", "r"),
    (765, 102, "5", "BEIJING", "l"),
    (300, 125, "6", "NEW YORK", "r"),
]


def draw_map(d):
    d.rectangle([0, 84, W, 182], fill=MAP_BG)
    for poly in CONTINENTS:
        d.polygon(poly, fill=LAND, outline=(150, 172, 154))
    f_pin = font(BOLD, 11)
    f_lab = font(BOLD, 10)
    for x, y, num, label, side in PINS:
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED, outline=WHITE, width=2)
        nw = d.textlength(num, font=f_pin)
        d.text((x - nw / 2, y - 8), num, font=f_pin, fill=WHITE)
        if side == "r":
            d.text((x + 12, y - 6), label, font=f_lab, fill=NAVY)
        else:
            d.text((x - 12 - d.textlength(label, font=f_lab), y - 6), label, font=f_lab, fill=NAVY)
    d.text((24, 92), "WHERE THE DAY HAPPENED", font=font(BOLD, 11), fill=NAVY2)
    d.text((W - 24 - d.textlength("1 GULF  2 CRIMEA  3 MANILA  4 LONDON  5 BEIJING  6 NEW YORK",
                                  font=font(REG, 11)), 164),
           "1 GULF  2 CRIMEA  3 MANILA  4 LONDON  5 BEIJING  6 NEW YORK",
           font=font(REG, 11), fill=(90, 100, 112))


def main():
    assert len(STORIES) == 36, len(STORIES)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 84], fill=NAVY)
    d.rectangle([0, 84, W, 88], fill=RED)
    d.text((20, 10), "THE WORLD IN ONE DAY", font=font(BOLD, 40), fill=WHITE)
    d.text((20, 56), "WEDNESDAY 18 NOVEMBER 2026  ·  36 STORIES  ·  6 CONTINENTS  ·  ONE FRONT PAGE",
           font=font(BOLD, 15), fill=GOLD)
    d.rectangle([W - 158, 12, W - 20, 72], outline=GOLD, width=2)
    d.text((W - 146, 18), "36", font=font(BOLD, 26), fill=WHITE)
    d.text((W - 108, 26), "STORIES", font=font(BOLD, 16), fill=GOLD)
    d.text((W - 146, 50), "in one image", font=font(REG, 12), fill=(200, 210, 225))

    draw_map(d)

    # ---- story grid: 3 cols x 12 rows ----------------------------------
    margin, gap = 20, 12
    col_w = (W - 2 * margin - 2 * gap) // 3   # 320
    row_h = 57
    grid_y = 190
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
            sy += 13
        assert sy <= y + row_h, (i, sy - y)
        if row < 11:
            d.line([x, y + row_h - 5, x + col_w, y + row_h - 5], fill=LINE, width=1)
    # column dividers
    for cx in (margin + col_w + gap // 2, margin + 2 * col_w + gap + gap // 2):
        d.line([cx, grid_y, cx, grid_y + 12 * row_h - 6], fill=LINE, width=1)

    # ---- by the numbers --------------------------------------------------
    ny0 = 882
    d.rectangle([0, ny0, W, ny0 + 62], fill=NAVY2)
    d.text((20, ny0 + 8), "BY THE NUMBERS", font=font(BOLD, 13), fill=GOLD)
    seg_w = (W - 40) // 6
    f_num = font(BOLD, 17)
    f_cap = font(REG, 10)
    for j, (num, cap) in enumerate(NUMBERS):
        sx = 20 + j * seg_w
        d.text((sx, ny0 + 26), num, font=f_num, fill=WHITE)
        cap_lines = wrap(d, cap, f_cap, seg_w - 8)
        cy = ny0 + 46
        for ln in cap_lines[:1]:
            d.text((sx, cy), ln, font=f_cap, fill=(200, 210, 225))

    # ---- footer ----------------------------------------------------------
    d.text((20, 956), "Sources: Reuters · AP · BBC · The Guardian · Al Jazeera · Hindustan Times — 18 November 2026",
           font=font(REG, 12), fill=(110, 108, 100))
    d.text((20, 978), "Every headline verified against 18 November 2026 editions. Drawn with Python + Pillow; no network, no timestamps — byte-identical reruns.",
           font=font(REG, 11), fill=(110, 108, 100))

    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
