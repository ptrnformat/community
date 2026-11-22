"""Build every PTRN brand asset into an output folder.

Usage: python3 build.py <Arvo-Regular.ttf> <out-dir>
Needs: fonttools, skia-pathops, Pillow, and rsvg-convert (librsvg) for PNGs.
The custom P T R N letters come from letters.py; secondary text ("Working Group",
".ptrn", social-card text) is set in Arvo Regular and converted to outlines.
"""
import os
import subprocess
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import letters as L

REG = TTFont(sys.argv[1])
OUT = sys.argv[2]
RGS = REG.getGlyphSet()
RCM = REG.getBestCmap()
RCAP = 1516  # Arvo cap height in font units

SLATE = "#536A7F"     # brand color: the logo tile and the wordmark
INK = "#1C1C1C"       # body text on social previews
PAPER = "#FFFFFF"     # the mark's contents
MUTED = "#5E5E5E"


# ---------- helpers ----------

def text_reg(t, x, baseline, cap):
    """Arvo Regular text as outlines. Returns (path data, end x)."""
    s = cap / RCAP
    d = []
    cx = x
    for ch in t:
        g = RGS[RCM[ord(ch)]]
        sp = SVGPathPen(RGS)
        g.draw(TransformPen(sp, (s, 0, 0, -s, cx, baseline)))
        d.append(sp.getCommands())
        cx += g.width * s
    return "".join(d), cx


def text_reg_width(t, cap):
    return text_reg(t, 0, 0, cap)[1]


def svg(w, h, body, title, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" '
            f'width="{w:g}" height="{h:g}" role="img"><title>{title}</title>{b}{body}</svg>\n')


def rr(x, y, w, h, r):
    return (f"M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}"
            f"A{r} {r} 0 0 1 {x + w - r} {y + h}H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}"
            f"V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)


def png(src, dst, w=None, h=None, bg=None):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    cmd = ["rsvg-convert", src, "-o", dst]
    if w:
        cmd += ["-w", str(w)]
    if h:
        cmd += ["-h", str(h)]
    if bg:
        cmd += ["-b", bg]
    subprocess.run(cmd, check=True)


# ---------- the mark (120 x 120 units) ----------

def cells(c):
    """The 2x2 grid in color c: P and N solid with the letter cut out, T and R outlined."""
    cap = 24
    P = L.centered("P", 32.5, 32.5, cap)
    T = L.centered("T", 87.5, 32.5, cap)
    R = L.centered("R", 32.5, 87.5, cap)
    N = L.centered("N", 87.5, 87.5, cap)
    return (f'<path fill-rule="evenodd" fill="{c}" d="{rr(8, 8, 49, 49, 5)}{P}{rr(63, 63, 49, 49, 5)}{N}"/>'
            f'<g fill="none" stroke="{c}" stroke-width="2.5">'
            f'<rect x="64.25" y="9.25" width="46.5" height="46.5" rx="4"/>'
            f'<rect x="9.25" y="64.25" width="46.5" height="46.5" rx="4"/></g>'
            f'<path fill="{c}" d="{T}{R}"/>')


def mark_tile(ox=0, oy=0, scale=1):
    """Primary mark: white grid on a slate tile. Works on light and dark backgrounds."""
    return (f'<g transform="translate({ox} {oy}) scale({scale})">'
            f'<rect width="120" height="120" rx="14" fill="{SLATE}"/>{cells(PAPER)}</g>')


def mark_outline(c, ox=0, oy=0, scale=1):
    """One-color mark: the grid inside a rounded border, no tile."""
    return (f'<g transform="translate({ox} {oy}) scale({scale})">'
            f'<rect x="1.5" y="1.5" width="117" height="117" rx="10" fill="none" stroke="{c}" stroke-width="3"/>'
            f'{cells(c)}</g>')


def icon_tile(ox=0, oy=0, scale=1):
    """Small-size icon: two white squares on a slate tile."""
    return (f'<g transform="translate({ox} {oy}) scale({scale})">'
            f'<rect width="120" height="120" rx="18" fill="{SLATE}"/>'
            f'<rect x="16" y="16" width="40" height="40" rx="5" fill="{PAPER}"/>'
            f'<rect x="64" y="64" width="40" height="40" rx="5" fill="{PAPER}"/></g>')


def icon_outline(c, ox=0, oy=0, scale=1):
    """One-color small-size icon."""
    return (f'<g transform="translate({ox} {oy}) scale({scale})">'
            f'<rect x="5" y="5" width="110" height="110" rx="16" fill="none" stroke="{c}" stroke-width="10"/>'
            f'<rect x="19" y="19" width="38" height="38" rx="4" fill="{c}"/>'
            f'<rect x="63" y="63" width="38" height="38" rx="4" fill="{c}"/></g>')


WM_CAP = 44
WM_TRACK = 4


def wordmark(x, baseline, cap=WM_CAP):
    return L.word("PTRN", x, baseline, cap, track=WM_TRACK * cap / WM_CAP)


def lockups(mark_fn, text_color):
    """Horizontal, stacked and Working Group lockups around a 120-unit mark."""
    out = {}
    wd, wend = wordmark(0, 0)
    d, end = wordmark(148, 82)
    out["lockup-horizontal"] = svg(round(end, 1), 120, mark_fn(0, 0) + f'<path fill="{text_color}" d="{d}"/>', "PTRN")

    sw = max(wend, 120)
    d, _ = wordmark((sw - wend) / 2, 192)
    out["lockup-stacked"] = svg(round(sw, 1), 196, mark_fn((sw - 120) / 2, 0) + f'<path fill="{text_color}" d="{d}"/>', "PTRN")

    sub = 22
    d1, e1 = wordmark(148, 58)
    d2, e2 = text_reg("Working Group", 148, 98, sub)
    out["wg-horizontal"] = svg(round(max(e1, e2), 1), 120, mark_fn(0, 0) + f'<path fill="{text_color}" d="{d1}{d2}"/>',
                               "PTRN Working Group")

    ww = text_reg_width("Working Group", sub)
    sw = max(wend, ww, 120)
    d1, _ = wordmark((sw - wend) / 2, 192)
    d2, _ = text_reg("Working Group", (sw - ww) / 2, 192 + 18 + sub, sub)
    out["wg-stacked"] = svg(round(sw, 1), 192 + 18 + sub + 8, mark_fn((sw - 120) / 2, 0) +
                            f'<path fill="{text_color}" d="{d1}{d2}"/>', "PTRN Working Group")

    d, end = wordmark(0, 44)
    out["wordmark"] = svg(round(end, 1), 44, f'<path fill="{text_color}" d="{d}"/>', "PTRN")
    return out


def file_icon():
    ew = text_reg_width(".ptrn", 13)
    ext, _ = text_reg(".ptrn", (96 - ew) / 2, 104, 13)
    body = (f'<path d="M10 4H64L88 28V114a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2Z" fill="{PAPER}" stroke="{SLATE}" '
            f'stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M64 4V28H88" fill="none" stroke="{SLATE}" stroke-width="4" stroke-linejoin="round"/>'
            + icon_tile(26, 38, 0.36) + f'<path fill="{SLATE}" d="{ext}"/>')
    return svg(96, 120, body, ".ptrn file")


# ---------- builders ----------

def build_logos():
    made = []  # (svg path, png kind)
    L_DIR = f"{OUT}/brand/logo/svg"
    O_DIR = f"{OUT}/brand/production/svg"
    I_DIR = f"{OUT}/brand/icon/svg"

    write(f"{L_DIR}/ptrn-mark.svg", svg(120, 120, mark_tile(), "PTRN")); made.append((f"{L_DIR}/ptrn-mark.svg", "square"))
    for kind, content in lockups(lambda x, y: mark_tile(x, y), SLATE).items():
        p = f"{L_DIR}/ptrn-{kind}.svg"
        write(p, content); made.append((p, "wide"))

    for name, c in (("black", "#000000"), ("white", "#FFFFFF")):
        p = f"{O_DIR}/ptrn-mark-{name}.svg"
        write(p, svg(120, 120, mark_outline(c), "PTRN")); made.append((p, "square"))
        p = f"{O_DIR}/ptrn-icon-{name}.svg"
        write(p, svg(120, 120, icon_outline(c), "PTRN")); made.append((p, "square"))
        for kind, content in lockups(lambda x, y, c=c: mark_outline(c, x, y), c).items():
            if kind in ("lockup-horizontal", "wordmark"):
                p = f"{O_DIR}/ptrn-{kind}-{name}.svg"
                write(p, content); made.append((p, "wide"))

    write(f"{I_DIR}/ptrn-icon.svg", svg(120, 120, icon_tile(), "PTRN")); made.append((f"{I_DIR}/ptrn-icon.svg", "square"))
    write(f"{I_DIR}/ptrn-file-icon.svg", file_icon()); made.append((f"{I_DIR}/ptrn-file-icon.svg", "square"))
    return made


def build_pngs(made):
    for p, kind in made:
        base = os.path.basename(p)[:-4]
        pdir = os.path.join(os.path.dirname(os.path.dirname(p)), "png")
        if kind == "square":
            for size in (256, 512, 1024):
                png(p, f"{pdir}/{base}-{size}.png", h=size)
        else:
            for h in (240, 480):
                png(p, f"{pdir}/{base}-{h}h.png", h=h)


def full_bleed(size, content_scale):
    """Slate square edge to edge, white grid centered (for avatars and touch icons)."""
    inner = 104 * content_scale  # the grid spans 8..112 in mark units
    off = (size - inner) / 2 - 8 * content_scale
    return svg(size, size, f'<g transform="translate({off} {off}) scale({content_scale})">{cells(PAPER)}</g>',
               "PTRN", bg=SLATE)


def build_favicons():
    fav = f"{OUT}/brand/favicon"
    write(f"{fav}/favicon.svg", svg(120, 120, icon_tile(), "PTRN"))
    for s in (16, 32, 48):
        png(f"{fav}/favicon.svg", f"{fav}/favicon-{s}.png", w=s, h=s)
    tmp = f"{OUT}/.tmp-touch.svg"
    write(tmp, full_bleed(180, 180 * 0.66 / 104))
    png(tmp, f"{fav}/apple-touch-icon.png", w=180, h=180)
    write(tmp, full_bleed(512, 512 * 0.62 / 104))
    png(tmp, f"{fav}/icon-192.png", w=192, h=192)
    png(tmp, f"{fav}/icon-512.png", w=512, h=512)
    os.remove(tmp)
    from PIL import Image
    imgs = [Image.open(f"{fav}/favicon-{s}.png").convert("RGBA") for s in (16, 32, 48)]
    imgs[2].save(f"{fav}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])


def build_avatar():
    tmp = f"{OUT}/.tmp-avatar.svg"
    write(tmp, full_bleed(500, 500 * 0.64 / 104))
    png(tmp, f"{OUT}/brand/avatar/ptrn-avatar.png", w=500, h=500)
    os.remove(tmp)


SOCIAL = {
    "org": ("ptrnformat", "An open file format for stitched-craft patterns"),
    "spec": ("ptrnformat/spec", "The .ptrn specification, schemas and stitch registry"),
    "ptrn-js": ("ptrnformat/ptrn-js", "JavaScript library for reading and writing .ptrn files"),
    "website": ("ptrnformat/website", "Source for ptrnformat.org"),
    "community": ("ptrnformat/community", "Governance, brand and working group resources"),
    "dot-github": ("ptrnformat/.github", "Default community health files"),
}


def build_social():
    W, H = 1280, 640
    for key, (title, desc) in SOCIAL.items():
        s = 1.6
        lw = wordmark(0, 0)[1]
        x0 = (W - (148 + lw) * s) / 2
        y0 = 150
        d, _ = wordmark(x0 + 148 * s, y0 + 82 * s, WM_CAP * s)
        body = mark_tile(x0, y0, s) + f'<path fill="{SLATE}" d="{d}"/>'
        tw = text_reg_width(title, 34)
        td, _ = text_reg(title, (W - tw) / 2, 470, 34)
        dw = text_reg_width(desc, 22)
        dd, _ = text_reg(desc, (W - dw) / 2, 520, 22)
        body += f'<path fill="{INK}" d="{td}"/><path fill="{MUTED}" d="{dd}"/>'
        tmp = f"{OUT}/.tmp-social.svg"
        write(tmp, svg(W, H, body, title, bg="#FFFFFF"))
        png(tmp, f"{OUT}/brand/social/ptrn-social-{key}.png", w=W, h=H)
        os.remove(tmp)


if __name__ == "__main__":
    made = build_logos()
    build_pngs(made)
    build_favicons()
    build_avatar()
    build_social()
    print("built", len(made), "svg logos")
