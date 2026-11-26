#!/usr/bin/env python3
"""news-image-20261127: draw a one-page newspaper front page summing up the
world news of Friday 27 November 2026, and write it to /output/entry.png.

Pure Python 3.13 standard library only: no network, no files read, fully
deterministic (the same bytes on every run). The picture is drawn from
scratch with a small built-in 5x7 bitmap font and vector shapes, so the
repository needs no image asset at all.

Run locally:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 230)
INK = (22, 22, 24)
RED = (178, 38, 30)
BLUE = (29, 78, 137)
GOLD = (176, 132, 44)
SKY = (174, 205, 226)
CLOUD = (96, 104, 116)
DARK = (52, 58, 68)
FLAME = (224, 110, 30)
FLAME2 = (240, 178, 44)
GREEN = (46, 110, 62)
GREY = (120, 116, 108)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font: each glyph is 7 rows of 5 bits, written as strings.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw uppercase-capable text; returns the x just past the last glyph."""
    s = s.upper()
    for ch in s:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(cv, x + col * scale, y + row * scale,
                              scale, scale, color)
        x += 6 * scale
    return x


def wrap_lines(s, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    words = s.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_w, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    lh = leading if leading is not None else 10 * scale
    for line in wrap_lines(s, scale, max_w):
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)


def fill_rect(cv, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cv.w, x + w), min(cv.h, y + h)
    for yy in range(y0, y1):
        base = (yy * cv.w + x0) * 3
        cv.px[base:(base + (x1 - x0) * 3)] = bytes(color) * (x1 - x0)


def hline(cv, x, y, w, color, t=1):
    fill_rect(cv, x, y, w, t, color)


def vline(cv, x, y, h, color, t=1):
    fill_rect(cv, x, y, t, h, color)


def draw_line(cv, x0, y0, x1, y1, color, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        fill_rect(cv, x0 - t // 2, y0 - t // 2, t, t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def fill_circle(cv, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        half = int((r * r - (yy - cy) ** 2) ** 0.5)
        fill_rect(cv, cx - half, yy, half * 2 + 1, 1, color)


def fill_ellipse(cv, cx, cy, rx, ry, color):
    for yy in range(cy - ry, cy + ry + 1):
        t = 1.0 - ((yy - cy) / ry) ** 2
        half = int(rx * (t ** 0.5)) if t > 0 else 0
        fill_rect(cv, cx - half, yy, half * 2 + 1, 1, color)


def fill_poly(cv, pts, color):
    """Scanline fill of a simple polygon given as [(x, y), ...]."""
    ys = [p[1] for p in pts]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(cv, int(xs[i]), yy, int(xs[i + 1]) - int(xs[i]) + 1, 1,
                      color)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------- pictograms ----
def draw_cloud(cv, x, y, s, color=CLOUD):
    """A rain cloud, s = overall width in px."""
    fill_ellipse(cv, x + int(s * 0.30), y + int(s * 0.42), int(s * 0.28),
                 int(s * 0.20), color)
    fill_ellipse(cv, x + int(s * 0.55), y + int(s * 0.32), int(s * 0.30),
                 int(s * 0.24), color)
    fill_ellipse(cv, x + int(s * 0.78), y + int(s * 0.44), int(s * 0.24),
                 int(s * 0.18), color)
    fill_rect(cv, x + int(s * 0.06), y + int(s * 0.42), int(s * 0.88),
              int(s * 0.20), color)


def draw_bolt(cv, x, y, s, color=GOLD):
    fill_poly(cv, [(x + int(s * 0.55), y),
                   (x + int(s * 0.15), y + int(s * 0.55)),
                   (x + int(s * 0.45), y + int(s * 0.55)),
                   (x + int(s * 0.35), y + s),
                   (x + int(s * 0.85), y + int(s * 0.42)),
                   (x + int(s * 0.52), y + int(s * 0.42))], color)


def draw_rain(cv, x, y, w, h, color=BLUE):
    for i in range(w // 26):
        rx = x + 8 + i * 26
        draw_line(cv, rx, y, rx - 8, y + 18, color, 3)


def draw_balloon(cv, x, y, s, color=RED):
    """A parade balloon: round body, stripes, ropes, little basket."""
    fill_ellipse(cv, x + s // 2, y + int(s * 0.32), int(s * 0.42),
                 int(s * 0.30), color)
    fill_ellipse(cv, x + s // 2, y + int(s * 0.32), int(s * 0.16),
                 int(s * 0.30), GOLD)
    fill_rect(cv, x + int(s * 0.42), y + int(s * 0.60), int(s * 0.16),
              int(s * 0.06), INK)
    draw_line(cv, x + int(s * 0.38), y + int(s * 0.62),
              x + int(s * 0.42), y + int(s * 0.82), INK, 3)
    draw_line(cv, x + int(s * 0.62), y + int(s * 0.62),
              x + int(s * 0.58), y + int(s * 0.82), INK, 3)
    fill_rect(cv, x + int(s * 0.40), y + int(s * 0.82), int(s * 0.20),
              int(s * 0.14), GOLD)


def draw_pylon(cv, x, y, s, color=DARK):
    """An electricity pylon with a warning bolt."""
    top, bot, mid = y, y + s, y + int(s * 0.45)
    draw_line(cv, x + int(s * 0.50), top, x + int(s * 0.28), bot, color, 4)
    draw_line(cv, x + int(s * 0.50), top, x + int(s * 0.72), bot, color, 4)
    draw_line(cv, x + int(s * 0.38), mid, x + int(s * 0.62), mid, color, 4)
    draw_line(cv, x + int(s * 0.14), top + int(s * 0.12),
              x + int(s * 0.86), top + int(s * 0.12), color, 4)
    draw_line(cv, x + int(s * 0.22), top + int(s * 0.24),
              x + int(s * 0.78), top + int(s * 0.24), color, 4)
    draw_bolt(cv, x + int(s * 0.62), y + int(s * 0.52), int(s * 0.34))


def draw_flame(cv, x, y, s, color=FLAME):
    fill_ellipse(cv, x + s // 2, y + int(s * 0.62), int(s * 0.36),
                 int(s * 0.34), color)
    fill_poly(cv, [(x + int(s * 0.50), y),
                   (x + int(s * 0.78), y + int(s * 0.45)),
                   (x + int(s * 0.86), y + int(s * 0.70)),
                   (x + int(s * 0.14), y + int(s * 0.70)),
                   (x + int(s * 0.24), y + int(s * 0.42))], color)
    fill_ellipse(cv, x + s // 2, y + int(s * 0.68), int(s * 0.18),
                 int(s * 0.20), FLAME2)


def draw_tanker(cv, x, y, s, color=DARK):
    """A fuel tanker truck with a flame above its tank."""
    fill_ellipse(cv, x + int(s * 0.42), y + int(s * 0.52), int(s * 0.38),
                 int(s * 0.26), color)
    fill_rect(cv, x + int(s * 0.06), y + int(s * 0.52), int(s * 0.14),
              int(s * 0.28), color)
    fill_rect(cv, x + int(s * 0.78), y + int(s * 0.34), int(s * 0.20),
              int(s * 0.46), RED)
    fill_circle(cv, x + int(s * 0.22), y + int(s * 0.84), int(s * 0.10), INK)
    fill_circle(cv, x + int(s * 0.62), y + int(s * 0.84), int(s * 0.10), INK)
    fill_circle(cv, x + int(s * 0.88), y + int(s * 0.84), int(s * 0.09), INK)
    draw_flame(cv, x + int(s * 0.30), y, int(s * 0.30))


def draw_bag(cv, x, y, s, color=BLUE):
    """A shopping bag with a percent tag."""
    fill_poly(cv, [(x + int(s * 0.12), y + int(s * 0.30)),
                   (x + int(s * 0.88), y + int(s * 0.30)),
                   (x + int(s * 0.80), y + s),
                   (x + int(s * 0.20), y + s)], color)
    draw_line(cv, x + int(s * 0.32), y + int(s * 0.32),
              x + int(s * 0.32), y + int(s * 0.12), INK, 4)
    draw_line(cv, x + int(s * 0.68), y + int(s * 0.32),
              x + int(s * 0.68), y + int(s * 0.12), INK, 4)
    draw_line(cv, x + int(s * 0.32), y + int(s * 0.12),
              x + int(s * 0.68), y + int(s * 0.12), INK, 4)
    fill_circle(cv, x + int(s * 0.50), y + int(s * 0.62), int(s * 0.24), GOLD)
    draw_text(cv, x + int(s * 0.38), y + int(s * 0.50), "%", 2, INK)


def draw_ball(cv, x, y, s, color=(139, 69, 19)):
    """An American football with laces."""
    fill_ellipse(cv, x + s // 2, y + s // 2, int(s * 0.46), int(s * 0.28),
                 color)
    hline(cv, x + int(s * 0.36), y + s // 2, int(s * 0.28), PAPER, 3)
    for dx in (-3, -1, 1, 3):
        vline(cv, x + s // 2 + dx * 5, y + s // 2 - 6, 12, PAPER, 3)


def draw_eu_stars(cv, x, y, s):
    fill_circle(cv, x + s // 2, y + s // 2, int(s * 0.46), BLUE)
    import math
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        sx = x + s // 2 + int(math.cos(a) * s * 0.32)
        sy = y + s // 2 + int(math.sin(a) * s * 0.32)
        fill_circle(cv, sx, sy, max(2, int(s * 0.035)), GOLD)


# -------------------------------------------------------------- layout ----
def panel(cv, x, y, w, h, kicker, headline, body, art, accent=RED):
    fill_rect(cv, x, y, w, h, (255, 255, 255))
    hline(cv, x, y, w, accent, 6)
    vline(cv, x, y, h, INK, 2)
    vline(cv, x + w - 2, y, h, INK, 2)
    hline(cv, x, y + h - 2, w, INK, 2)
    hline(cv, x, y, w, INK, 2)
    tw = w - 36
    draw_text(cv, x + 18, y + 16, kicker, 2, accent)
    art(cv, x + w - 72, y + 10, 56)
    hy = y + 42
    for line in wrap_lines(headline, 4, tw - 70)[:3]:
        draw_text(cv, x + 18, hy, line, 4, INK)
        hy += 34
    draw_para(cv, x + 18, hy + 4, body, 3, (60, 58, 54), tw, leading=22)


def build():
    cv = Canvas(W, H, PAPER)
    # frame
    fill_rect(cv, 0, 0, W, 10, INK)
    fill_rect(cv, 0, H - 10, W, 10, INK)
    fill_rect(cv, 0, 0, 10, H, INK)
    fill_rect(cv, W - 10, 0, 10, H, INK)

    # masthead
    title = "THE WORLD IN ONE DAY"
    draw_text(cv, (W - text_width(title, 8)) // 2, 34, title, 8, INK)
    hline(cv, 40, 118, W - 80, INK, 3)
    date = "FRIDAY  -  27 NOVEMBER 2026"
    draw_text(cv, (W - text_width(date, 4)) // 2, 132, date, 4, RED)
    hline(cv, 40, 168, W - 80, INK, 3)

    # ---- lead story: Thanksgiving storm stops the parade ----
    lx, ly, lw, lh = 28, 184, W - 56, 268
    fill_rect(cv, lx, ly, lw, lh, (255, 255, 255))
    hline(cv, lx, ly, lw, RED, 6)
    vline(cv, lx, ly, lh, INK, 2)
    vline(cv, lx + lw - 2, ly, lh, INK, 2)
    hline(cv, lx, ly + lh - 2, lw, INK, 2)
    hline(cv, lx, ly, lw, INK, 2)
    # storm scene, left half
    fill_rect(cv, lx + 14, ly + 14, 400, 240, SKY)
    draw_cloud(cv, lx + 40, ly + 30, 220)
    draw_bolt(cv, lx + 250, ly + 90, 70)
    draw_rain(cv, lx + 30, ly + 150, 360, 60)
    draw_balloon(cv, lx + 300, ly + 120, 100)
    draw_text(cv, lx + 30, ly + 218, "NEW YORK", 2, INK)
    # lead text, right half
    tx = lx + 440
    tw = lw - 470
    draw_text(cv, tx, ly + 18, "LEAD STORY  -  USA", 2, RED)
    hy = ly + 44
    for line in wrap_lines("STORM STOPS THE PARADE", 5, tw):
        draw_text(cv, tx, hy, line, 5, INK)
        hy += 42
    draw_para(cv, tx, hy + 4,
              "Thanksgiving storm postpones NYC's 100th Macy's parade for "
              "the first time. 500,000 homes lose power.",
              3, (60, 58, 54), tw, leading=26)

    # ---- row 1: Ukraine + Bangkok ----
    y1 = 468
    panel(cv, 28, y1, 476, 236, "WAR IN EUROPE",
          "ZELENSKYY WARNS OF NEW GRID ATTACK",
          "Kyiv fears a Russian strike on power. EU split over a 45bn "
          "euro loan.",
          lambda c, x, y, s: draw_pylon(c, x, y, s), BLUE)
    panel(cv, 520, y1, 476, 236, "ASIA  -  THAILAND",
          "REFINERY BLAST IN BANGKOK",
          "Blast and fire injures 9, three critically. All units shut "
          "down.",
          lambda c, x, y, s: draw_flame(c, x, y, s), FLAME)

    # ---- row 2: Cairo + Black Friday ----
    y2 = 720
    panel(cv, 28, y2, 476, 236, "MIDDLE EAST  -  EGYPT",
          "TANKER FIRE KILLS 31 NEAR CAIRO",
          "A fuel tanker blaze outside Cairo claims at least 31 lives.",
          lambda c, x, y, s: draw_tanker(c, x, y, s), RED)
    panel(cv, 520, y2, 476, 236, "SHOPPING  -  WORLD",
          "BLACK FRIDAY: ESSENTIALS FIRST",
          "Shoppers hunt everyday goods as well as gifts. Discounts run "
          "deeper than last year.",
          lambda c, x, y, s: draw_bag(c, x, y, s), GREEN)

    # ---- bottom ticker: sport + New Zealand ----
    ty = 972
    fill_rect(cv, 28, ty, W - 56, 34, INK)
    ticker = ("SPORT: STEELERS CUT RODGERS - SINNER OUT OF AUSTRALIAN "
              "OPEN - NZ VOTE COUNT DUE")
    draw_text(cv, (W - text_width(ticker, 2)) // 2, ty + 10, ticker, 2,
              (246, 241, 230))
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
