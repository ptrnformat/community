"""Custom PTRN letterforms, derived from Arvo Bold (SIL OFL 1.1, Anton Koovit).

Units are Arvo's (2048 upm, cap height 1516, y up). Tweaks from stock Arvo Bold:
  - P and R bowls are rounded rectangles instead of round bowls, echoing the
    rounded-square cells of the mark.
  - R has a straight diagonal leg and a squared foot serif.
  - Every serif projects the same distance (SP) past its stem.
  - N is rebuilt with symmetric serifs.
"""
import math
import pathops

C = 1516      # cap height
ST = 274      # serif thickness
SP = 157      # serif projection past a stem
S0, S1 = 270, 602   # P/R stem x-range (332 wide)


def rect(x0, y0, x1, y1):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


def poly(pts):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo(pts[0])
    for q in pts[1:]:
        pen.lineTo(q)
    pen.closePath()
    return p


def rrect_right(x0, y0, x1, y1, r, steps=8):
    """Rectangle whose two right-hand corners are rounded with radius r."""
    pts = [(x0, y0), (x1 - r, y0)]
    for i in range(1, steps + 1):  # bottom-right corner
        a = -math.pi / 2 + (math.pi / 2) * i / steps
        pts.append((x1 - r + r * math.cos(a), y0 + r + r * math.sin(a)))
    pts.append((x1, y1 - r))
    for i in range(1, steps + 1):  # top-right corner
        a = (math.pi / 2) * i / steps
        pts.append((x1 - r + r * math.cos(a), y1 - r + r * math.sin(a)))
    pts.append((x0, y1))
    return poly(pts)


def union(*paths):
    out = pathops.Path()
    for p in paths:
        out = pathops.op(out, p, pathops.PathOp.UNION)
    return out


def diff(a, b):
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def stem_with_serifs():
    return union(
        rect(S0, 0, S1, C),                 # stem
        rect(S0 - SP, 0, S1 + SP, ST),      # foot serif
        rect(S0 - SP, C - ST + 1, S0, C),   # top-left serif
    )


def glyph_P():
    bowl = diff(rrect_right(S0, 563, 1348, C, 300), rrect_right(S1 - 1, 834, 987, C - ST + 1, 110))
    return union(stem_with_serifs(), bowl), 1400


def glyph_R():
    bowl = diff(rrect_right(S0, 604, 1409, C, 300), rrect_right(S1 - 1, 874, 1049, C - ST + 1, 110))
    leg = poly([(740, 700), (1110, 700), (1420, ST), (1050, ST)])
    foot = rect(1050, 0, 1420 + SP, ST)
    return union(stem_with_serifs(), bowl, leg, foot), 1420 + SP + 60


def glyph_T():
    return union(
        rect(530, 0, 862, C),
        rect(530 - SP, 0, 862 + SP, ST),
        rect(20, C - ST + 1, 1399, C),
        rect(20, 1055, 346, C),
        rect(1071, 1055, 1399, C),
    ), 1430


def glyph_N():
    dx = 45
    L0, L1, R0, R1 = 238 + dx, 561 + dx, 1200 + dx, 1524 + dx
    return union(
        rect(L0, 0, L1, C),
        rect(R0, 0, R1, C),
        poly([(L0, C), (573 + dx, C), (R1, 0), (1192 + dx, 0)]),
        rect(L0 - SP, 0, L1 + SP, ST),
        rect(L0 - SP, C - ST + 1, L0, C),
        rect(R0 - SP, C - ST + 1, R1 + SP, C),
    ), R1 + SP + 60


GLYPHS = {"P": glyph_P, "R": glyph_R, "T": glyph_T, "N": glyph_N}


def svg_d(path, s, tx, ty):
    """Path data scaled by s, flipped (font y-up to SVG y-down), translated."""
    out = []
    for verb, pts in path:
        if verb == pathops.PathVerb.MOVE:
            out.append("M%.2f %.2f" % (tx + pts[0][0] * s, ty - pts[0][1] * s))
        elif verb == pathops.PathVerb.LINE:
            out.append("L%.2f %.2f" % (tx + pts[0][0] * s, ty - pts[0][1] * s))
        elif verb == pathops.PathVerb.QUAD:
            out.append("Q" + " ".join("%.2f %.2f" % (tx + x * s, ty - y * s) for x, y in pts))
        elif verb == pathops.PathVerb.CUBIC:
            out.append("C" + " ".join("%.2f %.2f" % (tx + x * s, ty - y * s) for x, y in pts))
        elif verb == pathops.PathVerb.CLOSE:
            out.append("Z")
    return "".join(out)


def bounds(ch):
    return GLYPHS[ch]()[0].bounds


def centered(ch, cx, cy, cap):
    """Letter ch scaled to the given cap height, its bounding box centered on (cx, cy)."""
    p, _ = GLYPHS[ch]()
    s = cap / C
    x0, y0, x1, y1 = p.bounds
    tx = cx - (x0 + x1) / 2 * s
    ty = cy + (y0 + y1) / 2 * s
    return svg_d(p, s, tx, ty)


def word(text, x, baseline, cap, track=0):
    """Set a word from the custom glyphs. Returns (path data, end x)."""
    s = cap / C
    d = []
    cx = x
    for ch in text:
        p, adv = GLYPHS[ch]()
        d.append(svg_d(p, s, cx, baseline))
        cx += adv * s + track
    return "".join(d), cx - track
