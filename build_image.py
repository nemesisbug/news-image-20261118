#!/usr/bin/env python3
"""Draw 'The Day in Six Frames' - 18 November 2026 world news in one image.

Six comic-strip panels (2 rows x 3 columns), each a flat drawn scene plus a
headline, a one-line summary and a location tag. Deterministic: no network,
no timestamps, no randomness. Output: entry.png, 1024x1024.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
BOLD = FONT_DIR + "LiberationSans-Bold.ttf"
REG = FONT_DIR + "LiberationSans-Regular.ttf"

PAPER = (246, 241, 231)
NAVY = (20, 33, 61)
NAVY2 = (28, 46, 84)
INK = (24, 28, 38)
WHITE = (255, 255, 255)
RED = (192, 57, 43)
GOLD = (232, 163, 61)
TEAL = (31, 111, 107)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def starburst(draw, cx, cy, r_out, r_in, points, fill):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


# ---------------------------------------------------------------- scenes
def scene_gulf(d, x, y, w, h):
    """Night sky over Bahrain: skyline, radar dish, signal arcs, all-clear moon."""
    d.rectangle([x, y, x + w, y + h], fill=(27, 42, 74))
    for sx, sy, sr in [(x + 30, y + 22, 2), (x + 90, y + 40, 2), (x + 170, y + 18, 3),
                       (x + 230, y + 46, 2), (x + 280, y + 26, 2), (x + 140, y + 58, 2)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 244, 200))
    d.ellipse([x + w - 62, y + 14, x + w - 22, y + 54], fill=(244, 230, 170))
    d.ellipse([x + w - 54, y + 18, x + w - 22, y + 50], fill=(27, 42, 74))
    # skyline
    base = y + h
    for bx, bw, bh in [(0, 34, 52), (36, 26, 78), (64, 30, 60), (96, 22, 88),
                       (120, 40, 46), (162, 26, 70), (190, 30, 56), (222, 24, 82),
                       (248, 34, 50), (284, 32, 64)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(13, 22, 40))
        for wy in range(base - bh + 8, base - 6, 14):
            d.rectangle([x + bx + 6, wy, x + bx + 12, wy + 6], fill=(255, 214, 120))
    # radar dish + arcs
    rx, ry = x + 52, y + h - 84
    d.line([rx, ry + 18, rx, ry + 46], fill=(120, 200, 160), width=4)
    d.pieslice([rx - 24, ry - 14, rx + 24, ry + 34], start=180, end=360,
               fill=(120, 200, 160))
    for r in (34, 48, 62):
        d.arc([rx - r, ry - r + 16, rx + r, ry + r + 16], start=300, end=390,
              fill=(120, 200, 160), width=3)


def scene_bridge(d, x, y, w, h):
    """Kerch Bridge at dusk: deck, arch, water, blast starburst."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 163, 61))
    d.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(244, 196, 110))
    d.ellipse([x + w - 70, y + 16, x + w - 26, y + 60], fill=(255, 236, 180))
    # water
    d.rectangle([x, y + int(h * 0.68), x + w, y + h], fill=(46, 98, 140))
    for wx in range(x + 8, x + w - 20, 46):
        d.line([wx, y + h - 22, wx + 26, y + h - 22], fill=(140, 190, 220), width=3)
        d.line([wx + 12, y + h - 40, wx + 34, y + h - 40], fill=(140, 190, 220), width=3)
    # bridge deck + arch + pylons
    deck_y = y + int(h * 0.68)
    d.rectangle([x, deck_y - 8, x + w, deck_y + 4], fill=(70, 76, 88))
    d.rectangle([x + 30, deck_y - 52, x + 38, deck_y], fill=(70, 76, 88))
    d.rectangle([x + w - 46, deck_y - 52, x + w - 38, deck_y], fill=(70, 76, 88))
    d.arc([x + 30, deck_y - 96, x + w - 30, deck_y + 30], start=180, end=360,
          fill=(90, 96, 110), width=6)
    # blast
    bx, by = x + int(w * 0.58), deck_y - 46
    starburst(d, bx, by, 44, 20, 10, (255, 120, 40))
    starburst(d, bx, by, 28, 13, 10, (255, 214, 90))
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(255, 255, 255))


def scene_manila(d, x, y, w, h):
    """Airplane over Manila bay at sunrise, city skyline below."""
    d.rectangle([x, y, x + w, y + h], fill=(127, 179, 213))
    d.rectangle([x, y, x + w, y + int(h * 0.45)], fill=(168, 205, 230))
    d.ellipse([x + 24, y + 14, x + 66, y + 56], fill=(255, 228, 150))
    for cx, cy, cw in [(x + 190, y + 18, 70), (x + 20, y + 84, 60)]:
        d.ellipse([cx, cy, cx + cw, cy + 18], fill=(255, 255, 255))
        d.ellipse([cx + 14, cy - 8, cx + cw - 10, cy + 10], fill=(255, 255, 255))
    # skyline
    base = y + h
    for bx, bw, bh in [(0, 40, 40), (44, 26, 62), (74, 34, 48), (112, 22, 70),
                       (138, 36, 44), (178, 28, 66), (210, 30, 50), (244, 36, 58),
                       (284, 32, 42)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(52, 84, 112))
    # airplane (side view, dark outline so it reads against the sky)
    px, py = x + int(w * 0.5), y + int(h * 0.48)
    outline = (52, 84, 112)
    d.polygon([(px + 44, py - 8), (px + 82, py - 2), (px + 44, py + 6)],
              fill=(255, 255, 255), outline=outline)
    d.polygon([(px - 62, py - 2), (px - 84, py - 18), (px - 84, py - 2)],
              fill=(230, 236, 242), outline=outline)
    d.polygon([(px - 8, py - 8), (px + 24, py - 36), (px + 34, py - 8)],
              fill=(230, 236, 242), outline=outline)
    d.polygon([(px - 8, py + 8), (px + 20, py + 30), (px + 30, py + 8)],
              fill=(220, 226, 232), outline=outline)
    d.ellipse([px - 62, py - 10, px + 62, py + 10], fill=(255, 255, 255), outline=outline, width=2)
    for wx in range(px - 40, px + 40, 14):
        d.rectangle([wx, py - 3, wx + 7, py + 3], fill=(20, 33, 61))


def scene_nvidia(d, x, y, w, h):
    """Rising green bars and a chip on dark green."""
    d.rectangle([x, y, x + w, y + h], fill=(11, 61, 46))
    for gx in range(x, x + w, 26):
        d.line([gx, y, gx, y + h], fill=(16, 74, 56), width=1)
    # bars
    base = y + h - 18
    bars = [(18, 34), (58, 52), (98, 44), (138, 72), (178, 66), (218, 96), (258, 118)]
    for bx, bh in bars:
        d.rectangle([x + bx, base - bh, x + bx + 28, base], fill=(118, 185, 0))
    d.line([x + 18, base - 34, x + 215, base - 96], fill=(255, 255, 255), width=4)
    d.polygon([(x + 215, base - 96), (x + 201, base - 90), (x + 209, base - 78)],
              fill=(255, 255, 255))
    # chip, top right, clear of the trend line
    cx, cy = x + w - 88, y + 14
    d.rectangle([cx, cy, cx + 60, cy + 42], fill=(20, 33, 61), outline=(118, 185, 0), width=3)
    d.rectangle([cx + 17, cy + 12, cx + 43, cy + 30], fill=(118, 185, 0))
    for pin in range(5):
        d.line([cx + 7 + pin * 11, cy, cx + 7 + pin * 11, cy - 8], fill=(200, 220, 200), width=3)
        d.line([cx + 7 + pin * 11, cy + 42, cx + 7 + pin * 11, cy + 50], fill=(200, 220, 200), width=3)


def scene_sanctions(d, x, y, w, h):
    """A stamped document: red SANCTIONED seal over a paper sheet."""
    d.rectangle([x, y, x + w, y + h], fill=(239, 230, 208))
    # document
    dx, dy, dw, dh = x + 78, y + 12, 160, h - 24
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(255, 255, 255), outline=(120, 110, 95), width=2)
    for ly in range(dy + 22, dy + dh - 52, 16):
        d.line([dx + 18, ly, dx + dw - 18, ly], fill=(150, 150, 150), width=3)
    d.line([dx + 18, dy + 14, dx + 84, dy + 14], fill=(24, 28, 38), width=4)
    # red stamp
    sx, sy = x + int(w * 0.62), y + int(h * 0.62)
    d.ellipse([sx - 52, sy - 52, sx + 52, sy + 52], outline=RED, width=5)
    d.ellipse([sx - 40, sy - 40, sx + 40, sy + 40], outline=RED, width=2)
    f_stamp = font(BOLD, 12)
    tw = d.textlength("SANCTIONED", font=f_stamp)
    d.text((sx - tw / 2, sy - 7), "SANCTIONED", font=f_stamp, fill=RED)


def scene_trade(d, x, y, w, h):
    """Cargo ship with stacked containers crossing a teal sea."""
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 220))
    d.ellipse([x + w - 66, y + 12, x + w - 26, y + 52], fill=(255, 236, 180))
    for cx, cy, cw in [(x + 20, y + 26, 64), (x + 150, y + 44, 76)]:
        d.ellipse([cx, cy, cx + cw, cy + 16], fill=(255, 255, 255))
    # sea
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(31, 111, 107))
    for wx in range(x + 10, x + w - 24, 52):
        d.line([wx, y + h - 16, wx + 30, y + h - 16], fill=(140, 200, 195), width=3)
    # hull
    hy = y + int(h * 0.62)
    d.polygon([(x + 24, hy + 6), (x + w - 24, hy + 6), (x + w - 52, hy + 44),
               (x + 52, hy + 44)], fill=(150, 40, 32))
    d.rectangle([x + 24, hy + 6, x + w - 24, hy + 14], fill=(24, 28, 38))
    # containers
    conts = [(RED, 0), ((232, 163, 61), 1), ((46, 98, 140), 2), ((31, 111, 107), 3)]
    for i, (col, _) in enumerate(conts):
        cx0 = x + 52 + i * 56
        d.rectangle([cx0, hy - 34, cx0 + 52, hy + 4], fill=col, outline=(255, 255, 255), width=2)
        d.rectangle([cx0, hy - 66, cx0 + 52, hy - 36], fill=col, outline=(255, 255, 255), width=2)
    # bridge tower
    d.rectangle([x + w - 76, hy - 66, x + w - 44, hy + 4], fill=(240, 240, 240))
    d.rectangle([x + w - 76, hy - 66, x + w - 44, hy - 52], fill=(20, 33, 61))


SCENES = [scene_gulf, scene_bridge, scene_manila, scene_nvidia, scene_sanctions, scene_trade]

PANELS = [
    ("GULF", (27, 42, 74), "Bahrain sounds all-clear",
     "as Gulf tensions flare",
     "Bahrain lifts its shelter alert as Kuwait downs drones; the US hits an Iranian missile site after Iran targeted a US radar base."),
    ("EUROPE", (192, 57, 43), "Ukraine hits Crimea",
     "bridge a second day",
     "Kyiv strikes the Kerch Bridge for a second straight day as Russia pounds bridges in Kyiv."),
    ("DIPLOMACY", (31, 111, 167), "Trump lands in Manila",
     "for Quad talks",
     "Trump arrives in Manila for Quad talks ahead of his China visit, as ASEAN and East Asia Summit leaders meet."),
    ("BUSINESS", (11, 61, 46), "Nvidia doubles revenue",
     "without Huang",
     "Nvidia posts $115.8bn quarterly revenue, up 103% year on year - its first report since CEO Jensen Huang resigned."),
    ("MIDDLE EAST", (128, 32, 32), "Britain sanctions",
     "settlement firms",
     "The UK sanctions eight firms over illegal West Bank settlements; Australia announces fresh sanctions too."),
    ("TRADE", (31, 111, 107), "Canada and China",
     "extend trade deals",
     "Canada and China extend trade deals as Xi meets Carney ahead of the APEC summit."),
]

TICKER = ("Dhoni retires from IPL and becomes CSK mentor  ·  Cyclone Akvan strengthens "
          "in the Bay of Bengal  ·  Latvia approves the Kulbergs government  ·  "
          "Amazon pledges $7bn for renewables in India")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 124], fill=RED)
    f_title = font(BOLD, 52)
    f_sub = font(BOLD, 22)
    d.text((24, 14), "THE DAY IN SIX FRAMES", font=f_title, fill=WHITE)
    sub = "THE WORLD IN ONE DAY  ·  WEDNESDAY 18 NOVEMBER 2026"
    d.text((24, 76), sub, font=f_sub, fill=GOLD)
    # frame number badge top right
    d.rectangle([W - 162, 18, W - 24, 100], outline=GOLD, width=3)
    f_badge = font(BOLD, 24)
    d.text((W - 150, 26), "6 FRAMES", font=f_badge, fill=WHITE)
    f_badge2 = font(REG, 16)
    d.text((W - 150, 62), "one day", font=f_badge2, fill=(200, 210, 225))

    # ---- panels --------------------------------------------------------
    margin, gap = 24, 14
    pw = (W - 2 * margin - 2 * gap) // 3          # 316
    ph = 372
    grid_y = 138
    scene_h = 140
    f_num = font(BOLD, 26)
    f_tag = font(BOLD, 17)
    f_head = font(BOLD, 24)
    f_body = font(REG, 18)

    for i, (tag, accent, head1, head2, body) in enumerate(PANELS):
        col, row = i % 3, i // 3
        x = margin + col * (pw + gap)
        y = grid_y + row * (ph + gap)
        # panel card
        d.rectangle([x, y, x + pw, y + ph], fill=WHITE, outline=(210, 205, 192), width=2)
        # scene
        SCENES[i](d, x + 2, y + 2, pw - 4, scene_h)
        # number badge overlapping scene corner (kept clear of the tag row)
        bx, by = x + 12, y + scene_h - 30
        d.ellipse([bx, by, bx + 40, by + 40], fill=accent, outline=WHITE, width=3)
        num = str(i + 1)
        nw = d.textlength(num, font=f_num)
        d.text((bx + 20 - nw / 2, by + 5), num, font=f_num, fill=WHITE)
        # tag
        ty = y + scene_h + 14
        d.text((x + 16, ty), tag, font=f_tag, fill=accent)
        d.line([x + 16, ty + 24, x + pw - 16, ty + 24], fill=(225, 220, 208), width=2)
        # headline (two lines, as given)
        hy = ty + 34
        d.text((x + 16, hy), head1, font=f_head, fill=INK)
        d.text((x + 16, hy + 30), head2, font=f_head, fill=INK)
        # body
        by2 = hy + 72
        lines = wrap(d, body, f_body, pw - 32)
        text_block(d, x + 16, by2, lines, f_body, (70, 74, 84), 22)

    # ---- ticker --------------------------------------------------------
    ty0 = 138 + 2 * ph + gap + 12                 # 908
    d.rectangle([0, ty0, W, ty0 + 64], fill=NAVY2)
    f_tick_tag = font(BOLD, 19)
    f_tick = font(REG, 18)
    d.text((24, ty0 + 12), "ALSO IN BRIEF", font=f_tick_tag, fill=GOLD)
    tag_w = d.textlength("ALSO IN BRIEF  ", font=f_tick_tag)
    tick_lines = wrap(d, TICKER, f_tick, W - 48 - tag_w)
    text_block(d, 24 + tag_w, ty0 + 12, tick_lines, f_tick, WHITE, 21)

    # ---- sources -------------------------------------------------------
    f_src = font(REG, 16)
    d.text((24, ty0 + 74), "Sources: Reuters · AP · BBC · TechCrunch · Al Jazeera — 18 November 2026",
           font=f_src, fill=(110, 108, 100))

    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
