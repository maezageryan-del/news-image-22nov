#!/usr/bin/env python3
"""render.py — draw the 22 November 2026 world-news broadsheet (1024x1024 PNG).

Reads stories.json next to this file, draws the whole front page with PIL
shapes only (no external images, no network), writes entry.png next to it.
Fully deterministic: fixed values only, no timestamps, no randomness.
Run twice and the sha256 is identical.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# --- palette: ink on newsprint -------------------------------------------
PAPER = (247, 243, 232)
PAPER2 = (255, 253, 246)
INK = (26, 23, 18)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
BLUE_DK = (18, 52, 96)
GOLD = (138, 109, 27)
TEAL = (31, 110, 104)
GREEN = (46, 111, 63)
ORANGE = (196, 96, 20)
PURPLE = (94, 66, 138)
GREY = (120, 112, 98)
TINT_BLUE = (214, 228, 240)
TINT_RED = (244, 214, 208)
TINT_GOLD = (244, 232, 196)
TINT_GREEN = (216, 234, 214)
TINT_GREY = (232, 228, 216)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False, serif=False):
    name = ("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf") if serif \
        else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, f, fill, lh, max_lines=None):
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        d.text((x, y + i * lh), line, font=f, fill=fill)
    return y + len(lines) * lh


def centre(d, text, cx, y, f, fill):
    d.text((cx - f.getlength(text) / 2, y), text, font=f, fill=fill)


def grain(d):
    """Deterministic paper grain: fixed function of coordinates only."""
    for yy in range(0, H, 4):
        for xx in range(0, W, 4):
            v = (xx * 37 + yy * 91) % 97
            if v < 5:
                d.point((xx, yy), fill=(233, 227, 210))
            elif v > 93:
                d.point((xx, yy), fill=(255, 252, 244))


def hatch(d, x0, y0, x1, y1, step=7, fill=(200, 190, 165)):
    x = x0 - (y1 - y0)
    while x < x1:
        d.line([(x, y1), (x + (y1 - y0), y0)], fill=fill, width=1)
        x += step


# --- flat pictograms (one per story) -------------------------------------
def ill_globe(d, x, y, w, h):
    # Sky gradient: three blue bands behind the globe.
    for i, col in enumerate([(226, 236, 244), (214, 228, 240), (196, 216, 234)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3 + 1], fill=col)
    cx, cy, r = x + w * 0.38, y + h * 0.52, min(w, h) * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE, outline=INK, width=2)
    # Landmasses on the globe: two green blobs clipped by the disc.
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 300, 30, fill=GREEN)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 150, 210, fill=(74, 140, 82))
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=PAPER2, width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=PAPER2, width=2)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 200, 340, fill=PAPER2, width=2)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 20, 160, fill=PAPER2, width=2)
    tx = x + w * 0.78
    d.rectangle([tx - 5, y + h * 0.18, tx + 5, y + h * 0.72], fill=PAPER2, outline=INK, width=2)
    d.ellipse([tx - 9, y + h * 0.66, tx + 9, y + h * 0.86], fill=RED, outline=INK, width=2)
    d.rectangle([tx - 2, y + h * 0.30, tx + 2, y + h * 0.68], fill=RED)
    for i in range(5):
        d.line([(x + w * 0.62 + i * 9, y + 8), (x + w * 0.62 + i * 9, y + 16)], fill=GOLD, width=3)


def ill_bahrain(d, x, y, w, h):
    # Dusk gradient sky: three bands, dark orange to near-black.
    for i, col in enumerate([(74, 48, 34), (52, 38, 32), (32, 26, 24)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3 + 1], fill=col)
    for bx, bw, bh in [(0.06, 0.20, 0.55), (0.30, 0.16, 0.72), (0.50, 0.22, 0.48), (0.76, 0.16, 0.62)]:
        d.rectangle([x + w * bx, y + h - h * bh, x + w * (bx + bw), y + h], fill=(20, 16, 14))
        for wy in range(3):
            col = GOLD if (wy % 2 == 0) else (214, 120, 40)
            d.rectangle([x + w * bx + 4, y + h - h * bh + 6 + wy * 12,
                         x + w * bx + 10, y + h - h * bh + 12 + wy * 12], fill=col)
    for fx, fh, col in [(0.14, 0.34, ORANGE), (0.20, 0.46, RED), (0.60, 0.30, ORANGE), (0.66, 0.42, (230, 170, 40))]:
        px, py = x + w * fx, y + h * 0.98
        d.polygon([(px - 12, py), (px - 4, py - h * fh), (px + 2, py - h * fh * 0.55),
                   (px + 8, py - h * fh * 0.8), (px + 14, py)], fill=col)
    for r in (10, 18, 26):
        d.arc([x + w * 0.82 - r, y + 10, x + w * 0.82 + r, y + 10 + 2 * r], 270, 90, fill=RED, width=3)


def ill_prison(d, x, y, w, h):
    import math
    d.rectangle([x, y, x + w, y + h], fill=(38, 40, 52))
    d.rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.60, y + h * 0.86],
                fill=(24, 25, 34), outline=GOLD, width=2)
    for i in range(5):
        bx = x + w * 0.14 + i * w * 0.11
        d.rectangle([bx - 3, y + h * 0.14, bx + 3, y + h * 0.86], fill=(180, 175, 160))
    cx, cy, r = x + w * 0.80, y + h * 0.46, min(w, h) * 0.30
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=GOLD, outline=INK)


def ill_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_BLUE)
    for wy in (0.66, 0.76):
        for i in range(6):
            d.arc([x + i * w / 5 - 8, y + h * wy, x + (i + 1) * w / 5 + 8, y + h * wy + 7],
                  0, 180, fill=BLUE, width=3)
    d.polygon([(x + w * 0.10, y + h * 0.68), (x + w * 0.90, y + h * 0.68),
               (x + w * 0.78, y + h * 0.88), (x + w * 0.22, y + h * 0.88)], fill=INK)
    d.rectangle([x + w * 0.42, y + h * 0.30, x + w * 0.58, y + h * 0.68], fill=RED)
    d.polygon([(x + w * 0.46, y + h * 0.30), (x + w * 0.50, y + h * 0.10),
               (x + w * 0.54, y + h * 0.30)], fill=ORANGE)
    d.polygon([(x + w * 0.62, y + h * 0.30), (x + w * 0.66, y + h * 0.12),
               (x + w * 0.70, y + h * 0.30)], fill=RED)


def ill_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_GOLD)
    d.line([(x + 6, y + h * 0.70), (x + w - 6, y + h * 0.70)], fill=INK, width=4)
    for i in range(5):
        bx = x + 14 + i * (w - 28) / 4
        d.line([(bx, y + h * 0.70), (bx, y + h * 0.34)], fill=INK, width=2)
    d.arc([x + 10, y + h * 0.18, x + w - 10, y + h * 0.75], 180, 360, fill=INK, width=3)
    sx, sy = x + w * 0.72, y + h * 0.30
    for k in range(8):
        d.line([(sx, sy), (sx + (10 if k % 2 == 0 else -10), sy - 10 if k < 4 else sy + 10)],
               fill=RED, width=2)


def ill_euro(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_BLUE)
    d.text((x + w * 0.30, y + h * 0.12), "€", font=font(int(h * 0.62), bold=True, serif=True), fill=BLUE_DK)
    for i in range(8):
        import math
        a = i * 3.14159 / 4
        sx, sy = x + w * 0.82 + 12 * math.cos(a), y + h * 0.5 + 12 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)


def ill_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 20, 24))
    sq = 7
    for r in range(3):
        for c in range(6):
            if (r + c) % 2 == 0:
                d.rectangle([x + 8 + c * sq, y + 8 + r * sq,
                             x + 8 + (c + 1) * sq, y + 8 + (r + 1) * sq], fill=PAPER2)
    d.polygon([(x + w * 0.30, y + h * 0.52), (x + w * 0.52, y + h * 0.52),
               (x + w * 0.58, y + h * 0.66), (x + w * 0.24, y + h * 0.66)], fill=RED)
    d.polygon([(x + w * 0.52, y + h * 0.52), (x + w * 0.78, y + h * 0.58),
               (x + w * 0.82, y + h * 0.66), (x + w * 0.58, y + h * 0.66)], fill=(200, 40, 30))
    for wx in (0.34, 0.72):
        d.ellipse([x + w * wx - 6, y + h * 0.64, x + w * wx + 6, y + h * 0.64 + 10],
                  fill=INK, outline=PAPER2, width=1)
    d.text((x + w * 0.55, y + h * 0.10), "50", font=font(max(14, int(h * 0.45)), bold=True, serif=True), fill=GOLD)


def ill_doc(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_GREEN)
    d.rectangle([x + w * 0.24, y + 6, x + w * 0.76, y + h - 6], fill=PAPER2, outline=INK, width=2)
    for i in range(3):
        d.line([(x + w * 0.30, y + 14 + i * 7), (x + w * 0.70, y + 14 + i * 7)], fill=GREY, width=2)
    d.text((x + w * 0.34, y + h * 0.48), "20", font=font(max(12, int(h * 0.42)), bold=True, serif=True), fill=RED)


def ill_fbi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_GREY)
    for i, cy in enumerate((0.30, 0.52, 0.74)):
        d.ellipse([x + w * 0.16, y + h * cy - 8, x + w * 0.52, y + h * cy + 8], fill=BLUE, outline=INK, width=2)
        d.line([(x + w * 0.16, y + h * cy - 8), (x + w * 0.52, y + h * cy - 8)], fill=PAPER2, width=1)
    cx, cy, r = x + w * 0.74, y + h * 0.42, 11
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    d.line([(cx + r * 0.7, cy + r * 0.7), (cx + r + 7, cy + r + 7)], fill=INK, width=3)


def ill_gavel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_RED)
    d.rectangle([x + w * 0.22, y + h * 0.28, x + w * 0.78, y + h * 0.46], fill=INK)
    d.line([(x + w * 0.50, y + h * 0.46), (x + w * 0.62, y + h * 0.78)], fill=INK, width=4)
    d.rectangle([x + w * 0.30, y + h * 0.78, x + w * 0.82, y + h * 0.88], fill=GOLD)


def ill_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_GREEN)
    d.rectangle([x + w * 0.24, y + h * 0.42, x + w * 0.76, y + h * 0.88], fill=BLUE, outline=INK, width=2)
    d.rectangle([x + w * 0.42, y + h * 0.38, x + w * 0.58, y + h * 0.46], fill=INK)
    d.line([(x + w * 0.30, y + h * 0.18), (x + w * 0.42, y + h * 0.36),
            (x + w * 0.72, y + h * 0.06)], fill=RED, width=4)


def ill_truck(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_GOLD)
    d.rectangle([x + w * 0.12, y + h * 0.34, x + w * 0.62, y + h * 0.72], fill=PAPER2, outline=INK, width=2)
    d.polygon([(x + w * 0.62, y + h * 0.44), (x + w * 0.86, y + h * 0.44),
               (x + w * 0.86, y + h * 0.72), (x + w * 0.62, y + h * 0.72)], fill=RED)
    for wx in (0.28, 0.52, 0.76):
        d.ellipse([x + w * wx - 5, y + h * 0.70, x + w * wx + 5, y + h * 0.70 + 10],
                  fill=INK, outline=PAPER2, width=1)
    d.rectangle([x + w * 0.22, y + h * 0.44, x + w * 0.34, y + h * 0.56], fill=GOLD)
    d.rectangle([x + w * 0.38, y + h * 0.44, x + w * 0.50, y + h * 0.56], fill=GREEN)


def ill_hospital(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINT_BLUE)
    d.rectangle([x + w * 0.26, y + h * 0.22, x + w * 0.74, y + h * 0.86], fill=PAPER2, outline=INK, width=2)
    cx, cy = x + w * 0.50, y + h * 0.44
    d.rectangle([cx - 4, cy - 12, cx + 4, cy + 12], fill=RED)
    d.rectangle([cx - 12, cy - 4, cx + 12, cy + 4], fill=RED)
    for i in range(3):
        d.rectangle([x + w * 0.32, y + h * 0.66 + i * 6, x + w * 0.68, y + h * 0.66 + i * 6 + 3],
                    fill=GREY)


ILL = {1: ill_globe, 2: ill_bahrain, 3: ill_prison, 4: ill_ship, 5: ill_bridge,
       6: ill_euro, 7: ill_f1, 8: ill_doc, 9: ill_fbi, 10: ill_gavel,
       11: ill_ballot, 12: ill_truck, 13: ill_hospital}

KICKER = {1: "GLOBAL  ·  COP31", 2: "MIDDLE EAST  ·  BAHRAIN", 3: "AMERICAS  ·  MEXICO"}

SHORT_DECK = {
    1: "After talks ran past Friday's deadline into Sunday's early hours, the presidency tables a new package text; approval due 06:00 GMT Sunday.",
    2: "Saturday night: the Guards claim strikes on Sheikh Isa air base and the US naval base at Juffair; sirens sound, defences fire, a civilian plant burns.",
    3: "Friday night: special forces seize Fausto Isidro Meza Flores, one of the FBI's 10 most-wanted, in Sinaloa; 11 killed as violence erupts.",
    4: "Sparta II ablaze and drifting in the Gulf of Finland.",
    5: "Zelensky defends the bridge strikes; Kryvyi Rih: 2 dead, 42 hurt.",
    6: "The EU designates €1bn in increased military aid for Ukraine.",
    7: "Antonelli on pole; Verstappen and Russell fight for second.",
    8: "Trump says a deal could last 20 years.",
    9: "The FBI is reportedly investigating a hack of its criminal database.",
    10: "Denmark accuses Russian intelligence of a murder plot in Denmark.",
    11: "Local elections: the ANC fights to keep control of cities.",
    12: "Three killed in an Israeli strike on a food-supply vehicle.",
    13: "Brazil's jailed ex-president in intensive care.",
}

SHORT_ALSO = {
    14: "Akvan aftermath: Odisha cleans up; 300,000 evacuated",
    15: "Modi opens Nitish Setu, linking Patna and Vaishali",
    16: "First: Japanese forces to use Indian sites for live fire",
    17: "Turkey seizes last big independent news outlet",
    18: "Bangladesh: 50+ Awami League houses destroyed",
    19: "US airlines warned of al-Qaeda-linked Thanksgiving threat",
    20: "Air India extends Jeddah suspension to 24 Nov",
    21: "Cyclone Akvan: 14 flights cancelled at Ranchi",
    22: "King Charles thanks Erdogan for organising COP31",
    23: "Mamdani plans to close New York's Rikers Island jail",
    24: "Nepal PM Balendra Shah to meet Modi on first visit",
    25: "Australia ends England's seven-match T20 streak",
    26: "Cummins keeps unanimous backing as Test captain",
    27: "Hagia Sophia's hidden tunnels: 420 m network cleaned",
    28: "Trafalgar Square tree sets off from Oslo to London",
    29: "Palisades fire: man guilty of starting deadly blaze",
    30: "Prince William: insurance for 10,000 forest staff",
    31: "South Korea repeats $75,000 bounty on exam cheating",
    32: "Hegseth sets fresh limits on US–Canada military ties",
    33: "IRGC claims two US drones downed near Hormuz",
    34: "Explosions, air defence over Kaliningrad, Sat. evening",
    35: "Estonia to shut road border with Russia from 1 Dec",
    36: "Germany: protests over education and military service",
    37: "Japan Tobacco to book $8.9bn loss on Russian holdings",
    38: "Crude oil futures fall more than 3%",
}

# Map pins: story n -> (x, y) in the 992-wide map area
PINS = {1: (585, 40), 2: (642, 54), 3: (150, 64), 4: (548, 16), 5: (545, 34),
        6: (493, 30), 7: (118, 50), 8: (222, 42), 9: (250, 60), 10: (516, 14),
        11: (526, 100), 12: (602, 50), 13: (286, 88)}

REGION_COLOURS = {"Europe": BLUE, "Asia": RED, "Middle East": ORANGE,
                  "Africa": GREEN, "Americas": PURPLE, "Oceania": TEAL,
                  "Global": INK}


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
        stories = json.load(f)
    by_n = {s["n"]: s for s in stories}

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    grain(d)

    # --- 1. top strip ------------------------------------------------------
    d.rectangle([0, 0, W, 24], fill=INK)
    centre(d, "38 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
           W // 2, 5, font(12, bold=True), PAPER)

    # --- 2. masthead -------------------------------------------------------
    centre(d, "THE WORLD IN ONE DAY", W // 2, 30, font(12, bold=True), RED)
    centre(d, "Sunday 22 November 2026", W // 2, 42, font(44, bold=True, serif=True), INK)
    # Ticker as a red band (white on red): the strongest first-screen pull
    # after the masthead, in the winning broadsheet's own idiom.
    d.rectangle([16, 88, 1008, 106], fill=RED)
    centre(d, "COP31 deal tabled  ·  Bahrain hit again  ·  El Chapo Isidro held  ·  Sparta II ablaze",
           W // 2, 91, font(13, bold=True), PAPER2)
    d.line([(16, 109), (1008, 109)], fill=INK, width=1)

    # --- 3. timeline spine -------------------------------------------------
    # One thin line, four dots, one short label under each dot. The labels
    # sit fully above the numbers strip (strip top is y=140).
    stops = [("SAT NIGHT", "Bahrain hit"), ("OVERNIGHT", "COP31 text tabled"),
             ("06:00 GMT", "Approval session"), ("TONIGHT", "Las Vegas GP 20:00 PST")]
    ty = 112
    d.line([(40, ty + 4), (984, ty + 4)], fill=GREY, width=2)
    for i, (t, e) in enumerate(stops):
        cx = 140 + i * 248
        d.ellipse([cx - 6, ty - 2, cx + 6, ty + 10], fill=RED, outline=INK, width=1)
        centre(d, t + " — " + e, cx, ty + 13, font(10, bold=True), INK)

    # --- 4. numbers strip: big numerals, one cell per figure --------------
    d.rectangle([0, 140, W, 188], fill=TINT_GOLD)
    nums = [("4th", "Bahrain strike in 9 days"), ("11", "killed in Sinaloa"),
            ("€1bn", "EU aid for Kyiv"), ("$75,000", "Seoul exam bounty"),
            ("420 m", "Hagia Sophia tunnels"), ("50", "laps · Las Vegas GP")]
    for i, (big, small) in enumerate(nums):
        cx = 16 + i * 165 + 82
        centre(d, big, cx, 145, font(22, bold=True, serif=True), RED)
        centre(d, small, cx, 172, font(9), (60, 54, 44))
        if i:
            d.line([(16 + i * 165, 148), (16 + i * 165, 180)], fill=RED, width=1)

    # --- 5. region colour bar ----------------------------------------------
    ry = 194
    parts = [("Europe 12", BLUE), ("Asia 9", RED), ("Middle East 4", ORANGE),
             ("Africa 1", GREEN), ("Americas 8", PURPLE), ("Oceania 2", TEAL),
             ("Global 2", INK)]
    total_w = sum(font(11, bold=True).getlength(t) + 34 for t, _ in parts)
    x = (W - total_w) // 2
    for label, col in parts:
        f = font(11, bold=True)
        d.rectangle([x, ry + 1, x + 12, ry + 13], fill=col)
        d.text((x + 16, ry), label, font=f, fill=INK)
        x += f.getlength(label) + 34

    # --- 6. three big lead panels ------------------------------------------
    # Red kicker band (region + story tag, white on red) mirrors the winning
    # broadsheet format: the eye hits the kicker first, then the picture.
    ly, lh, lw, gap = 210, 202, 325, 8
    for i, n in enumerate((1, 2, 3)):
        s = by_n[n]
        x = 16 + i * (lw + gap)
        d.rectangle([x + 3, ly + 3, x + lw + 3, ly + lh + 3], fill=(210, 202, 182))
        d.rectangle([x, ly, x + lw, ly + lh], fill=PAPER2, outline=INK, width=2)
        d.rectangle([x + 2, ly + 2, x + lw - 2, ly + 18], fill=RED)
        d.text((x + 10, ly + 4), str(n), font=font(13, bold=True), fill=PAPER2)
        d.text((x + 30, ly + 4), KICKER[n],
               font=font(10, bold=True), fill=PAPER2)
        ILL[n](d, x + 2, ly + 18, lw - 4, 76)
        hy = draw_lines(d, wrap(s["headline"], font(18, bold=True, serif=True), lw - 20),
                        x + 10, ly + 98, font(18, bold=True, serif=True), INK, 21, max_lines=2)
        d.line([(x + 10, hy + 2), (x + 70, hy + 2)], fill=RED, width=2)
        draw_lines(d, wrap(SHORT_DECK[n], font(10), lw - 20), x + 10, hy + 7,
                   font(10), (60, 54, 44), 12, max_lines=3)
        d.text((x + 10, ly + lh - 14), "SOURCE: " + s["source"].upper(),
               font=font(9, bold=True), fill=RED)
        d.text((x + lw - 10 - font(9, bold=True).getlength(s["region"].upper()),
                ly + lh - 14), s["region"].upper(), font=font(9, bold=True), fill=GREY)

    # --- 7. ten medium panels ----------------------------------------------
    # Region-coloured top strip on each panel, bigger headlines.
    my, mh, mw, mgap = 412, 104, 193, 2
    for j, n in enumerate(range(4, 14)):
        row, col = divmod(j, 5)
        x = 16 + col * (mw + mgap)
        y = my + row * (mh + 2)
        s = by_n[n]
        d.rectangle([x + 2, y + 2, x + mw + 2, y + mh + 2], fill=(210, 202, 182))
        d.rectangle([x, y, x + mw, y + mh], fill=PAPER2, outline=INK, width=1)
        ILL[n](d, x + 1, y + 1, mw - 2, 36)
        d.rectangle([x + 1, y + 1, x + mw - 1, y + 4], fill=REGION_COLOURS[s["region"]])
        d.ellipse([x + 5, y + 5, x + 23, y + 23], fill=REGION_COLOURS[s["region"]], outline=PAPER2, width=1)
        centre(d, str(n), x + 14, y + 7, font(10, bold=True), PAPER2)
        hy = draw_lines(d, wrap(s["headline"], font(12, bold=True, serif=True), mw - 12),
                        x + 6, y + 40, font(12, bold=True, serif=True), INK, 14, max_lines=2)
        draw_lines(d, wrap(SHORT_DECK[n], font(9), mw - 12), x + 6, hy + 2,
                   font(9), (60, 54, 44), 10, max_lines=2)
        d.text((x + 6, y + mh - 11), s["source"].upper(), font=font(8, bold=True), fill=RED)

    # --- 8. world map --------------------------------------------------------
    map_y, map_h = 622, 134
    d.rectangle([16, map_y, 1008, map_y + map_h], fill=BLUE_DK, outline=INK, width=2)
    centre(d, "WHERE IT HAPPENED", W // 2, map_y + 4, font(13, bold=True, serif=True), PAPER)
    # Halftone ocean: fixed dot grid in a lighter blue for texture.
    for yy in range(map_y + 24, map_y + map_h - 4, 9):
        for xx in range(20, 1004, 9):
            if ((xx * 13 + yy * 29) % 11) < 3:
                d.ellipse([xx, yy, xx + 2, yy + 2], fill=(38, 84, 138))
    hatch(d, 16, map_y + 22, 1008, map_y + map_h, step=14, fill=(26, 64, 112))
    mx, my0 = 16, map_y + 22
    continents = [
        [(60, 18), (150, 8), (230, 14), (250, 30), (210, 48), (180, 70), (140, 66), (110, 52), (70, 40)],
        [(255, 6), (285, 4), (290, 14), (262, 16)],
        [(240, 62), (290, 58), (320, 70), (310, 100), (280, 112), (255, 92), (238, 78)],
        [(470, 18), (520, 8), (555, 16), (550, 34), (520, 40), (490, 34), (468, 28)],
        [(480, 48), (540, 44), (575, 56), (565, 96), (530, 108), (500, 88), (482, 66)],
        [(560, 10), (700, 6), (820, 14), (900, 30), (880, 52), (800, 58), (720, 50), (640, 44), (580, 36), (558, 22)],
        [(800, 86), (860, 82), (880, 96), (840, 108), (800, 100)],
    ]
    for poly in continents:
        d.polygon([(mx + px, my0 + py) for px, py in poly], fill=(232, 220, 188), outline=(200, 186, 150))
    for n, (px, py) in PINS.items():
        cx, cy = mx + px, my0 + py
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=PAPER2, width=2)
        centre(d, str(n), cx, cy - 6, font(9, bold=True), PAPER2)

    # --- 9. ALSO list --------------------------------------------------------
    ay = 766
    d.text((16, ay), "ALSO ON SUNDAY 22 NOVEMBER — 25 MORE STORIES",
           font=font(13, bold=True, serif=True), fill=INK)
    d.line([(16, ay + 20), (1008, ay + 20)], fill=INK, width=2)
    f_also = font(10)
    rows = [(16, list(range(14, 27))), (512, list(range(27, 39)))]
    for col_x, nums in rows:
        for r, n in enumerate(nums):
            s = by_n[n]
            yy = int(ay + 26 + r * 10.5)
            d.text((col_x, yy), f"{n}. {SHORT_ALSO[n]} ({s['source']})",
                   font=f_also, fill=INK)

    # --- 10. date-check box --------------------------------------------------
    dy = 934
    d.rectangle([16, dy, 1008, dy + 32], fill=TINT_RED, outline=RED, width=1)
    d.text((24, dy + 2), "DATE CHECK — left out as Saturday 21 November's news: the missiles that "
                         "landed in Poland, the Kyiv barrage, the Nasdaq −5.3% rout, the Peru 6.9 quake.",
           font=font(10, bold=True), fill=INK)
    d.text((24, dy + 16), "Older still: the Shenzhen declaration (19 Nov), the ICJ verdict itself (19 Nov).",
           font=font(10), fill=INK)

    # --- 11. claims-checked box ----------------------------------------------
    cy = 970
    d.rectangle([16, cy, 1008, cy + 32], fill=TINT_BLUE, outline=BLUE, width=1)
    d.text((24, cy + 2), "CLAIMS CHECKED — NOT shown as fact: a COP31 “Pact” — the text is tabled, "
                         "approval due 06:00 GMT Sunday.",
           font=font(10, bold=True), fill=INK)
    d.text((24, cy + 16), "“Kyiv heat restored” — not verified.",
           font=font(10), fill=INK)

    # --- 12. footer ------------------------------------------------------------
    fy = 1008
    d.line([(16, fy - 4), (1008, fy - 4)], fill=INK, width=1)
    d.text((16, fy), "Every story here happened, or was first reported, on Sunday 22 November 2026; "
                     "overnight events are labelled with their night. Sources: AP · AFP · Reuters · "
                     "WSJ · BBC · CNN · USGS · F1 · PTI",
           font=font(9), fill=(60, 54, 44))

    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
