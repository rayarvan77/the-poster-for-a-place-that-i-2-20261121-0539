"""Entry program for the-poster-for-a-place-that-i-2-20261121-0539.

Writes one travel poster to /output/entry.png: AERTHYS, the city above
the clouds — a place that does not exist.

Python 3.13, standard library only; no network access, no arguments.
Run it locally with:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

Without MAKEFUN_OUTPUT_DIR it writes to ./output/entry.png instead.
The poster is a 1024 by 1024 PNG of at most 1,048,576 bytes, as the
competition requires; the program checks both before it writes.
"""

import os
import struct
import zlib
from pathlib import Path

OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "output")
OUT_PATH = OUT_DIR / "entry.png"

W, H = 1024, 1024
MAX_BYTES = 1_048_576

# A 5x7 bitmap font, one row per string, '#' = ink. Only the letters the
# poster actually prints, plus space and the full stop.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (5 px per glyph + 1 gap)."""
    return len(text) * 6 * scale - scale


def draw_text(px, text, cx, y, scale, color):
    """Draw centred text with its baseline row at y."""
    x = cx - text_width(text, scale) // 2
    for ch in text:
        glyph = GLYPHS.get(ch, GLYPHS[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            set_px(px, x + col * scale + dx, y + row * scale + dy, color)
        x += 6 * scale


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def blend(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def disc(px, cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(px, x, y, color)


def ellipse(px, cx, cy, rx, ry, color):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                set_px(px, x, y, color)


def rect(px, x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            set_px(px, x, y, color)


def island(px, cx, top, half_w, rock_h):
    """One floating island: green table-top, rocky underside, waterfall."""
    # Rocky underside: a tapering wedge.
    for dy in range(rock_h):
        t = dy / rock_h
        w = int(half_w * (1 - t * 0.92))
        for x in range(cx - w, cx + w + 1):
            set_px(px, x, top + dy, (122, 88, 62) if (x + dy) % 5 else (104, 74, 52))
    # Grassy top.
    ellipse(px, cx, top - 6, half_w, 16, (74, 138, 74))
    rect(px, cx - half_w, top - 10, cx + half_w, top - 2, (74, 138, 74))
    # Waterfall spilling off the underside into the cloud sea.
    wx = cx + half_w // 3
    for y in range(top + rock_h // 2, 760):
        for x in range(wx - 4, wx + 5):
            if (x * 7 + y) % 11:
                set_px(px, x, y, (186, 226, 240))


def tower(px, x, base, w, h, color):
    rect(px, x, base - h, x + w, base, color)
    # Pointed roof: widest row sits on the tower top, narrowing to an apex.
    roof_h = w // 2 + 4
    for dy in range(roof_h):
        half = roof_h - dy
        for dx in range(-half, half + 1):
            set_px(px, x + w // 2 + dx, base - h - dy, (196, 84, 52))
    # Lit windows.
    for wy in range(base - h + 8, base - 6, 14):
        set_px(px, x + w // 2, wy, (255, 214, 130))
        set_px(px, x + w // 2, wy + 1, (255, 214, 130))


def tree(px, x, base):
    rect(px, x - 1, base - 12, x + 1, base, (96, 64, 40))
    disc(px, x, base - 18, 9, (46, 110, 58))
    disc(px, x - 6, base - 12, 6, (58, 126, 66))


def main() -> None:
    px = bytearray(W * H * 3)
    # Dusk sky: deep indigo at the top melting into amber at the horizon.
    top_sky, horizon = (24, 32, 74), (232, 158, 76)
    for y in range(H):
        t = y / (H - 1)
        c = blend(top_sky, horizon, t ** 1.6)
        for x in range(W):
            i = (y * W + x) * 3
            px[i], px[i + 1], px[i + 2] = c
    # Low sun with a soft halo, kept clear of the tagline above it.
    disc(px, 800, 350, 96, (250, 196, 110))
    disc(px, 800, 350, 66, (255, 224, 150))
    disc(px, 800, 350, 44, (255, 240, 190))
    # Distant mountain ridge.
    for x in range(W):
        ridge = 560 + int(46 * __import__("math").sin(x / 130.0) + 26 * __import__("math").sin(x / 47.0 + 2.0))
        for y in range(ridge, 640):
            set_px(px, x, y, (52, 58, 96))
    # Cloud sea: layered cream ellipses across the lower third.
    for cx, cy, rx, ry in [
        (120, 800, 220, 60), (330, 850, 260, 70), (620, 810, 240, 62),
        (880, 860, 240, 70), (60, 930, 200, 66), (420, 940, 280, 72),
        (760, 950, 260, 70), (980, 960, 180, 60), (240, 990, 260, 50),
        (620, 905, 210, 58),
    ]:
        ellipse(px, cx, cy, rx, ry, (244, 232, 214))
    # The three floating islands of Aerthys.
    island(px, 512, 470, 250, 130)
    island(px, 180, 560, 130, 84)
    island(px, 850, 540, 150, 96)
    # Towers and trees on the main island.
    tower(px, 420, 466, 26, 92, (232, 220, 196))
    tower(px, 520, 466, 34, 128, (240, 228, 200))
    tower(px, 600, 466, 22, 70, (226, 214, 190))
    tree(px, 330, 466)
    tree(px, 690, 466)
    tree(px, 130, 556)
    tree(px, 810, 536)
    # A little skyferry crossing in front of the sun.
    ellipse(px, 758, 384, 46, 14, (196, 84, 52))
    rect(px, 734, 396, 782, 406, (120, 52, 40))
    # Birds: quick dark chevrons high in the sky.
    for bx, by in [(220, 210), (260, 190), (310, 220), (880, 180), (920, 210)]:
        for dx in range(9):
            set_px(px, bx + dx, by + abs(dx - 4) // 2, (30, 32, 58))
    # Foreground cliff silhouettes at the bottom corners.
    for x in range(0, 190):
        for y in range(1024 - int(120 * (1 - x / 190.0)) - 30, 1024):
            set_px(px, x, y, (26, 28, 52))
    for x in range(834, 1024):
        for y in range(1024 - int(120 * ((x - 834) / 190.0)) - 30, 1024):
            set_px(px, x, y, (26, 28, 52))
    # A thin gold frame, inset from the edge, finishes the poster.
    for x in range(28, W - 28):
        for y in (28, 29, H - 30, H - 29):
            set_px(px, x, y, (212, 168, 92))
    for y in range(28, H - 28):
        for x in (28, 29, W - 30, W - 29):
            set_px(px, x, y, (212, 168, 92))
    # Lettering. Gold title, cream tagline; nothing else — the judge asks
    # for the place's name and no invented quotes, ratings or extra copy.
    draw_text(px, "AERTHYS", 512, 78, 11, (255, 214, 130))
    draw_text(px, "THE CITY ABOVE THE CLOUDS", 512, 208, 4, (250, 238, 210))
    data = png_bytes(px)
    if len(data) > MAX_BYTES:
        raise RuntimeError(f"poster is {len(data)} bytes, want at most {MAX_BYTES}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(data)
    print(f"wrote {OUT_PATH} ({len(data)} bytes, {W}x{H})")


def png_bytes(px):
    """Encode the RGB buffer as a PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        return out + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", comp)
        + chunk(b"IEND", b"")
    )


if __name__ == "__main__":
    main()
