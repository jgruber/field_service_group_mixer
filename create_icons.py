#!/usr/bin/env python3
"""Generate icons/icon-192.png and icons/icon-512.png from the app's SVG design."""
import struct, zlib, math, os

def _chunk(tag, data):
    t = tag.encode() if isinstance(tag, str) else tag
    crc = zlib.crc32(t + data) & 0xffffffff
    return struct.pack('>I', len(data)) + t + data + struct.pack('>I', crc)

def encode_png(size, rows_rgba):
    raw = bytearray()
    for row in rows_rgba:
        raw += b'\x00'
        for r, g, b, a in row:
            raw += bytes([r, g, b, a])
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + _chunk('IHDR', ihdr)
            + _chunk('IDAT', zlib.compress(bytes(raw), 9))
            + _chunk('IEND', b''))

def make_icon(size):
    BG   = (67,  56,  202, 255)   # #4338ca
    W    = (255, 255, 255, 255)
    WD   = (255, 255, 255, 166)   # 65 % white (person 2)
    NONE = (0,   0,   0,   0)

    s  = size / 32.0
    cr = 6 * s  # corner radius

    px = [[list(BG) for _ in range(size)] for _ in range(size)]

    def in_rect(x, y):
        cx, cy = x + .5, y + .5
        if cx < cr        and cy < cr:        return (cx-cr)**2          + (cy-cr)**2          <= cr*cr
        if cx > size - cr and cy < cr:        return (cx-(size-cr))**2   + (cy-cr)**2          <= cr*cr
        if cx < cr        and cy > size - cr: return (cx-cr)**2          + (cy-(size-cr))**2   <= cr*cr
        if cx > size - cr and cy > size - cr: return (cx-(size-cr))**2   + (cy-(size-cr))**2   <= cr*cr
        return True

    def paint(x, y, col):
        if 0 <= x < size and 0 <= y < size and in_rect(x, y):
            px[y][x] = list(col)

    def circle(ocx, ocy, or_, col):
        cx, cy, r = ocx * s, ocy * s, or_ * s
        for y in range(max(0, int(cy - r) - 1), min(size, int(cy + r) + 2)):
            for x in range(max(0, int(cx - r) - 1), min(size, int(cx + r) + 2)):
                if (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= r * r:
                    paint(x, y, col)

    def body(ocx, otop, orx, ory, col):
        cx, top, rx, ry = ocx * s, otop * s, orx * s, ory * s
        for y in range(int(top), min(size, int(top + ry) + 2)):
            t = (y + .5 - top) / ry
            if t >= 1:
                break
            w = rx * math.sqrt(max(0, 1 - t * t))
            for x in range(max(0, int(cx - w)), min(size, int(cx + w) + 1)):
                paint(x, y, col)

    # clip corners to transparent
    for y in range(size):
        for x in range(size):
            if not in_rect(x, y):
                px[y][x] = list(NONE)

    # person 2 (back, dimmer) — SVG: cx=21, cy=10, r=4
    circle(21, 10, 4, WD)
    body(21, 18, 8, 8, WD)

    # person 1 (front) — SVG: cx=11, cy=10, r=4
    circle(11, 10, 4, W)
    body(11, 18, 8, 8, W)

    return [[tuple(p) for p in row] for row in px]

os.makedirs('icons', exist_ok=True)
for sz in (192, 512):
    data = encode_png(sz, make_icon(sz))
    path = f'icons/icon-{sz}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Wrote {path} ({len(data):,} bytes)')
