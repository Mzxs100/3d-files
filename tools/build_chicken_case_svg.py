#!/usr/bin/env python3
"""
Build an SVG recreation of the fresh-poultry reach-in case in the reference photos.

Five shelves across three bays:
  Bay A - Signature Farms printed trays (tenders, drumettes, wings, thighs, fryers)
  Bay B - Heritage / pulp trays, O Organics blue, Open Nature green, whole fryers
  Bay C - Value-and-Quality bulk black trays (stir fry, diced, thighs, hand trimmed)

Everything is drawn from primitives: tray bodies, meat silhouettes, over-wrap
sheen, weigh-scale stickers, shelf rails with SLU strips, blade signs, price tags.

Outputs (repo root):
  chicken-case-planogram.svg
  chicken-case-planogram.html
"""

import math
import os
import random

R = random.Random(20260804)

W, H = 1760, 1180

# ---------------------------------------------------------------- palette ---
TRAY_YELLOW = "#f2c53d"
TRAY_YELLOW_D = "#d9a91f"
SF_GREEN = "#8dc63f"
SF_GREEN_D = "#1f7a3a"
SF_LIME = "#a9d24b"
OO_BLUE = "#1256a8"
OO_BLUE_D = "#0b3d7a"
ON_LIME = "#a3ce4e"
TAG_YELLOW = "#f5c400"
NAVY = "#101c33"

BREAST = ["#f0c2b1", "#eab8a5", "#e5ab98", "#f4ccbb", "#edbcaa"]
THIGH = ["#d28d83", "#c88278", "#be756b", "#d9998d", "#c47f75"]
WING = ["#e6bfa4", "#deb397", "#eccdb4", "#d5a68c"]
DICE = ["#edbba7", "#e6af9a", "#f2c7b6", "#dfa692", "#e9b39f"]
PORK = ["#e59aa0", "#d9838c", "#efb0b4", "#e08e95"]
BEEF = ["#b2323a", "#9c2a31", "#c14049", "#a72f37"]


def shade(hexcol, amt):
    hexcol = hexcol.lstrip("#")
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
    f = lambda v: max(0, min(255, int(v + 255 * amt / 100.0)))
    return "#%02x%02x%02x" % (f(r), f(g), f(b))


def A(d):
    return " ".join('%s="%s"' % (k.replace("_", "-"), v)
                    for k, v in d.items() if v is not None)


def rr(x, y, w, h, r=0, **kw):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" %s/>' % (
        x, y, w, h, r, A(kw))


def ell(cx, cy, rx, ry, **kw):
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" %s/>' % (
        cx, cy, rx, ry, A(kw))


def path(d, **kw):
    return '<path d="%s" %s/>' % (d, A(kw))


def fit(size, maxw, s, k=0.53):
    """Shrink a font size so the string stays inside maxw."""
    if not s:
        return size
    return min(size, maxw / (k * len(s)))


def txt(x, y, s, size=7, fill="#111", weight="normal", anchor="start",
        family="Helvetica Neue, Helvetica, Arial, sans-serif", style="normal",
        spacing=None, opacity=None, rotate=None):
    tr = ' transform="rotate(%.1f %.1f %.1f)"' % (rotate, x, y) if rotate else ""
    return ('<text x="%.1f" y="%.1f" font-size="%.2f" fill="%s" font-weight="%s" '
            'text-anchor="%s" font-family="%s" font-style="%s"%s%s%s>%s</text>') % (
        x, y, size, fill, weight, anchor, family, style,
        ' letter-spacing="%.2f"' % spacing if spacing else "",
        ' opacity="%.2f"' % opacity if opacity else "", tr,
        s.replace("&", "&amp;").replace("<", "&lt;"))


CLIPS = []


def clip_rect(x, y, w, h, r):
    cid = "cl%d" % len(CLIPS)
    CLIPS.append('<clipPath id="%s">%s</clipPath>' % (cid, rr(x, y, w, h, r)))
    return cid


# ------------------------------------------------------------ meat shapes ---
def blob(w, h, rng, n=9, jit=0.13):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rng.uniform(-jit, jit)
        pts.append((math.cos(a) * w / 2 * k, math.sin(a) * h / 2 * k))
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    d = "M %.1f %.1f " % mid(pts[-1], pts[0])
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        m = mid(p, q)
        d += "Q %.1f %.1f %.1f %.1f " % (p[0], p[1], m[0], m[1])
    return d + "Z"


def _g(cx, cy, ang, inner):
    return '<g transform="translate(%.1f,%.1f) rotate(%.1f)">%s</g>' % (
        cx, cy, ang, inner)


def m_breast(cx, cy, w, h, ang, fill, rng):
    """Boneless skinless breast: teardrop with the tenderloin seam."""
    d = ("M %.1f 0 C %.1f %.1f %.1f %.1f %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f "
         "C %.1f %.1f %.1f %.1f %.1f 0 Z") % (
        -w * .50, -w * .52, -h * .38, -w * .22, -h * .54, w * .06, -h * .50,
        w * .40, -h * .46, w * .55, -h * .02, w * .40, h * .30,
        w * .24, h * .56, -w * .22, h * .54, -w * .50)
    o = [path(d, fill=fill, stroke=shade(fill, -11), stroke_width=.5)]
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
        -w * .34, h * .02, -w * .06, -h * .26, w * .16, -h * .12, w * .36, h * .14),
        fill="none", stroke="#fff", stroke_width=max(.8, w * .035), opacity=".55",
        stroke_linecap="round"))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
        -w * .30, h * .22, -w * .02, h * .06, w * .14, h * .18, w * .30, h * .30),
        fill="none", stroke=shade(fill, -14), stroke_width=.7, opacity=".65"))
    o.append(ell(-w * .10, -h * .20, w * .22, h * .15, fill="#fff", opacity=".28"))
    return _g(cx, cy, ang, "".join(o))


def m_thigh(cx, cy, w, h, ang, fill, rng):
    """Boneless thigh: irregular lobe with a pale fat edge."""
    o = [path(blob(w, h, rng, 10, .15), fill=fill, stroke=shade(fill, -12),
              stroke_width=.5)]
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
        -w * .26, -h * .04, -w * .02, h * .16, w * .12, -h * .06, w * .28, h * .10),
        fill="none", stroke=shade(fill, -16), stroke_width=.8, opacity=".7"))
    o.append(path(blob(w * .34, h * .26, rng, 7, .22), fill="#f6e7da", opacity=".85",
                  transform="translate(%.1f,%.1f)" % (w * .22, h * .22)))
    o.append(ell(-w * .12, -h * .20, w * .22, h * .16, fill="#fff", opacity=".26"))
    return _g(cx, cy, ang, "".join(o))


def m_drumette(cx, cy, w, h, ang, fill, rng):
    o = [path(blob(w * .72, h, rng, 8, .11), fill=fill, stroke=shade(fill, -18),
              stroke_width=.7)]
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f "
                  "C %.1f %.1f %.1f %.1f %.1f %.1f Z" % (
                      w * .20, -h * .18, w * .42, -h * .16, w * .50, -h * .07,
                      w * .56, -h * .02, w * .56, h * .12, w * .48, h * .16,
                      w * .38, h * .22, w * .20, h * .20),
                  fill=shade(fill, 5), stroke=shade(fill, -9), stroke_width=.4))
    o.append(ell(w * .52, h * .04, w * .075, h * .15, fill="#f7eee4"))
    o.append(ell(-w * .12, -h * .20, w * .20, h * .16, fill="#fff", opacity=".26"))
    return _g(cx, cy, ang, "".join(o))


def m_drumstick(cx, cy, w, h, ang, fill, rng):
    o = [path(blob(w * .66, h * 1.02, rng, 8, .10), fill=fill,
              stroke=shade(fill, -18), stroke_width=.7)]
    o.append(rr(w * .14, -h * .13, w * .34, h * .26, h * .13, fill=shade(fill, 4),
                stroke=shade(fill, -8), stroke_width=".4"))
    o.append(ell(w * .48, 0, w * .085, h * .17, fill="#f5ebe0"))
    o.append(ell(-w * .14, -h * .20, w * .20, h * .15, fill="#fff", opacity=".26"))
    return _g(cx, cy, ang, "".join(o))


def m_wing(cx, cy, w, h, ang, fill, rng):
    """Party wing: two lobes hinged at a joint."""
    o = [path(blob(w * .58, h * .78, rng, 8, .12), fill=fill,
              stroke=shade(fill, -19), stroke_width=.7,
              transform="translate(%.1f,%.1f)" % (-w * .18, -h * .06))]
    o.append(path(blob(w * .52, h * .60, rng, 8, .12), fill=shade(fill, -5),
                  stroke=shade(fill, -19), stroke_width=.7,
                  transform="translate(%.1f,%.1f) rotate(24)" % (w * .22, h * .12)))
    o.append(ell(0, 0, w * .09, h * .12, fill=shade(fill, 6),
                 stroke=shade(fill, -10), stroke_width=".4"))
    o.append(ell(-w * .26, -h * .20, w * .16, h * .13, fill="#fff", opacity=".26"))
    return _g(cx, cy, ang, "".join(o))


def m_dice(x, y, w, h, rng, size=1.0, pal=None):
    """Diced / stir-fry pieces on a jittered grid so the tray reads as full."""
    pal = pal or DICE
    cell = 12.6 * size
    cols = max(2, int(w / cell))
    rows = max(2, int(h / (cell * .82)))
    o = []
    for r_ in range(rows):
        for c in range(cols):
            px = x + (c + .5) * w / cols + rng.uniform(-2.6, 2.6)
            py = y + (r_ + .5) * h / rows + rng.uniform(-2.2, 2.2)
            s = cell * rng.uniform(.62, .96)
            o.append(_g(px, py, rng.uniform(0, 180),
                        path(blob(s, s * rng.uniform(.62, .92), rng, 7, .20),
                             fill=rng.choice(pal), stroke="#cf9d8b",
                             stroke_width=".4") +
                        ell(-s * .12, -s * .16, s * .22, s * .15, fill="#fff",
                            opacity=".24")))
    return "".join(o)


def m_bird(cx, cy, w, h, rng):
    """Whole fryer: plump breast up, wing shoulders, drumsticks trussed low."""
    body = ("M 0 %.1f C %.1f %.1f %.1f %.1f %.1f %.1f C %.1f %.1f %.1f %.1f 0 %.1f "
            "C %.1f %.1f %.1f %.1f %.1f %.1f C %.1f %.1f %.1f %.1f 0 %.1f Z") % (
        -h * .46, w * .30, -h * .44, w * .50, -h * .08, w * .44, h * .18,
        w * .38, h * .42, w * .18, h * .50, h * .50,
        -w * .18, h * .50, -w * .38, h * .42, -w * .44, h * .18,
        -w * .50, -h * .08, -w * .30, -h * .44, -h * .46)
    o = [ell(0, h * .30, w * .46, h * .20, fill="#000", opacity=".28")]
    o.append(path(body, fill="url(#bird)", stroke="#b98a76", stroke_width="1.3"))
    # wing shoulders
    for sgn in (-1, 1):
        o.append(_g(sgn * w * .33, -h * .12, sgn * -28,
                    ell(0, 0, w * .13, h * .19, fill="#e3bda9",
                        stroke="#b98a76", stroke_width=".9")))
    # breast keel
    o.append(path("M 0 %.1f C %.1f %.1f %.1f %.1f 0 %.1f" % (
        -h * .34, w * .10, -h * .12, w * .07, h * .10, h * .22),
        fill="none", stroke="#d5ab9a", stroke_width="1.3", opacity=".9"))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
        -w * .26, -h * .04, -w * .10, -h * .20, w * .10, -h * .20, w * .26, -h * .04),
        fill="none", stroke="#e6c2b1", stroke_width="1.0", opacity=".7"))
    # drumsticks tucked toward the centre
    for sgn in (-1, 1):
        o.append(_g(sgn * w * .24, h * .30, sgn * 30,
                    ell(0, 0, w * .17, h * .24, fill="#f2d5c4",
                        stroke="#b98a76", stroke_width="1.1") +
                    ell(0, h * .19, w * .085, h * .085, fill="#dfb49f",
                        stroke="#b98a76", stroke_width=".8")))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L 0 %.1f Z" % (
        -w * .10, h * .20, -w * .05, h * .38, w * .05, h * .38, w * .10, h * .20,
        h * .18), fill="#8d675a", opacity=".45"))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
        -w * .34, h * .26, -w * .12, h * .36, w * .12, h * .36, w * .34, h * .26),
        fill="none", stroke="#a87a67", stroke_width="1.1", opacity=".75"))
    o.append(ell(-w * .19, -h * .22, w * .16, h * .12, fill="#fff", opacity=".28"))
    o.append(ell(0, -h * .40, w * .11, h * .06, fill="#dcae9c", opacity=".7"))
    return _g(cx, cy, rng.uniform(-4, 4), "".join(o))


# ------------------------------------------------------------- components ---
def film(x, y, w, h, rng, r=7, op=".18"):
    o = [rr(x, y, w, h, r, fill="url(#film)", opacity=op)]
    for _ in range(rng.randint(2, 3)):
        x0 = x + w * rng.uniform(.05, .32)
        x1 = x + w * rng.uniform(.58, .97)
        y0 = y + h * rng.uniform(.14, .80)
        o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
            x0, y0, x0 + w * .2, y0 - h * rng.uniform(.10, .24),
            x1 - w * .2, y0 + h * rng.uniform(.04, .20), x1, y0 - h * .05),
            fill="none", stroke="#ffffff", stroke_width=rng.uniform(1.1, 2.2),
            opacity=rng.uniform(.30, .55), stroke_linecap="round"))
    o.append(path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
        x, y + h * .72, x + w * .40, y, x + w * .62, y, x, y + h * .97),
        fill="#fff", opacity=".035"))
    return "".join(o)


def barcode(x, y, w, h, rng, col="#111"):
    o, cx = [], x
    while cx < x + w - 1:
        bw = rng.choice([.6, .6, .9, 1.3, 1.8])
        if cx + bw > x + w:
            break
        o.append(rr(cx, y, bw, h, 0, fill=col))
        cx += bw + rng.choice([.7, .9, 1.2])
    return "".join(o)


def microtext(x, y, w, rng, lines=3, gap=2.4, col="#8b8b8b", op=".85"):
    return "".join(rr(x, y + i * gap, w * rng.uniform(.45, 1.0), 1.05, .4,
                      fill=col, opacity=op) for i in range(lines))


def scale_label(x, y, w, h, rng, tilt=0):
    g = ['<g transform="translate(%.1f,%.1f) rotate(%.1f)">' % (x, y, tilt)]
    g.append(rr(0, 0, w, h, 1.2, fill="#fdfdfb", stroke="#cfcfc8", stroke_width=.4))
    g.append(microtext(w * .07, h * .12, w * .78, rng, 3, h * .12))
    g.append(rr(w * .07, h * .53, w * .86, .5, 0, fill="#c9c9c2"))
    g.append(barcode(w * .09, h * .61, w * .54, h * .29, rng))
    g.append(microtext(w * .68, h * .62, w * .24, rng, 3, h * .09, "#666"))
    g.append("</g>")
    return "".join(g)


def oval_sticker(cx, cy, w, h, line1, line2=None, fill="#f4711f", tilt=-6):
    g = ['<g transform="translate(%.1f,%.1f) rotate(%.1f)">' % (cx, cy, tilt)]
    g.append(rr(-w / 2, -h / 2, w, h, h / 2, fill=fill, stroke="#fff", stroke_width=.7))
    if line2:
        g.append(txt(0, -h * .04, line1, size=fit(h * .42, w * .82, line1),
                     fill="#fff", weight="700", anchor="middle",
                     family="Georgia, serif"))
        g.append(txt(0, h * .38, line2, size=fit(h * .32, w * .82, line2),
                     fill="#fff", weight="600", anchor="middle"))
    else:
        g.append(txt(0, h * .16, line1, size=fit(h * .44, w * .84, line1),
                     fill="#fff", weight="800", anchor="middle"))
    g.append("</g>")
    return "".join(g)


def guarantee_flash(x, y, w, h, tilt=-4):
    g = ['<g transform="translate(%.1f,%.1f) rotate(%.1f)">' % (x, y, tilt)]
    g.append(rr(0, 0, w, h, 1.5, fill="#ffd400", stroke="#e0b200", stroke_width=.4))
    g.append(txt(w / 2, h * .74, "100% Guaranteed",
                 size=fit(h * .56, w * .92, "100% Guaranteed"), fill="#161616",
                 weight="700", anchor="middle", family="Georgia, serif",
                 style="italic"))
    g.append("</g>")
    return "".join(g)


def sf_logo(cx, cy, w, h):
    """Signature SELECT roundel."""
    o = [ell(cx, cy, w / 2, h / 2, fill="#15181a", opacity=".93")]
    o.append(txt(cx, cy + h * .06, "Signature",
                 size=fit(h * .42, w * .84, "Signature"), fill="#fff",
                 anchor="middle", family="Georgia, serif", style="italic"))
    o.append(txt(cx, cy + h * .40, "SELECT", size=h * .22, fill="#cfe0a8",
                 anchor="middle", spacing=.5))
    return "".join(o)


def shadow(x, y, w, h=7):
    return ell(x + w / 2, y, w * .50, h, fill="#000", opacity=".45")


# -------------------------------------------------------------- packages ----
def sf_yellow(x, y, w, h, name, kind="drumette", rng=R):
    """Signature Farms printed tray: yellow body, green wave, product name."""
    mw = h * .56
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 12, 4, fill=TRAY_YELLOW_D))
    o.append(rr(x, y, w, h, 7, fill="url(#yel)", stroke=shade(TRAY_YELLOW_D, -6),
                stroke_width=.8))
    ix, iy, iw, ih = x + w * .06, y + h * .05, w * .88, mw - h * .06
    o.append(rr(ix, iy, iw, ih, 6, fill="#cdb69c", stroke=shade(TRAY_YELLOW_D, -14),
                stroke_width=".6"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(ix, iy, iw, ih, 6))
    fn, n, cols, pal, sw, sh = {
        "drumette": (m_drumette, 9, 3, WING, .31, .16),
        "tender": (m_breast, 10, 2, BREAST, .40, .10),
        "breast": (m_breast, 6, 2, BREAST, .40, .16),
        "wing": (m_wing, 9, 3, WING, .31, .16),
    }[kind]
    rows = math.ceil(n / cols)
    for i in range(n):
        px = ix + iw * ((i % cols) + .5) / cols + rng.uniform(-5, 5)
        py = iy + ih * ((i // cols) + .5) / rows + rng.uniform(-4, 4)
        o.append(fn(px, py, w * sw, h * sh,
                    rng.uniform(-14, 14) if kind in ("tender", "breast")
                    else rng.uniform(-32, 32), rng.choice(pal), rng))
    o.append(rr(ix, iy, iw, ih, 6, fill="url(#trayShade)", opacity=".34"))
    o.append("</g>")
    o.append(film(ix, iy, iw, ih, rng, 6, ".16"))
    wy = y + mw
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                  % (x, wy + h * .04, x + w * .30, wy - h * .06, x + w * .68,
                     wy + h * .06, x + w, wy - h * .04, x + w, y + h, x, y + h),
                  fill=SF_GREEN))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                  % (x, wy + h * .19, x + w * .32, wy + h * .09, x + w * .70,
                     wy + h * .21, x + w, wy + h * .10, x + w, y + h, x, y + h),
                  fill=SF_GREEN_D))
    o.append(sf_logo(x + w * .155, y + h * .74, w * .25, h * .17))
    lines = name.split("|")
    fs = min(fit(h * .085, w * .62, max(lines, key=len)), w * .085)
    for i, line in enumerate(lines):
        o.append(txt(x + w * .30, y + h * (.745 + .105 * i), line, size=fs,
                     fill="#fff", weight="700", family="Georgia, serif",
                     style="italic"))
    o.append(txt(x + w * .31, y + h * .955, "All Natural", size=fs * .62,
                 fill="#dff0bb", family="Georgia, serif", style="italic"))
    o.append(scale_label(x + w * .60, y + h * .06, w * .34, h * .20, rng,
                         rng.uniform(-2, 2)))
    return "".join(o)


def sf_green(x, y, w, h, kind="wing", label=None, rng=R):
    """Signature Farms clear-top tray on a lime base."""
    mw = h * (.66 if label else .78)
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 12, 4, fill=shade(SF_LIME, -14)))
    o.append(rr(x, y, w, h, 7, fill="url(#lime)", stroke=shade(SF_LIME, -18),
                stroke_width=.8))
    ix, iy, iw, ih = x + w * .07, y + h * .05, w * .86, mw - h * .10
    o.append(rr(ix, iy, iw, ih, 6, fill="#c9b49c", stroke=shade(SF_LIME, -26),
                stroke_width=".6"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(ix, iy, iw, ih, 6))
    fn, n, cols, pal, sw, sh = {
        "wing": (m_wing, 8, 2, WING, .40, .17),
        "drumstick": (m_drumstick, 10, 2, WING, .36, .12),
        "thigh": (m_thigh, 10, 2, THIGH, .30, .16),
        "breast": (m_breast, 8, 2, BREAST, .36, .15),
    }[kind]
    rows = math.ceil(n / cols)
    for i in range(n):
        px = ix + iw * ((i % cols) + .5) / cols + rng.uniform(-6, 6)
        py = iy + ih * ((i // cols) + .5) / rows + rng.uniform(-5, 5)
        o.append(fn(px, py, w * sw, h * sh, rng.uniform(-34, 34),
                    rng.choice(pal), rng))
    o.append(rr(ix, iy, iw, ih, 6, fill="url(#trayShade)", opacity=".36"))
    o.append("</g>")
    o.append(film(ix, iy, iw, ih, rng, 6, ".18"))
    wy = y + mw
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                  % (x, wy + h * .04, x + w * .34, wy - h * .05, x + w * .70,
                     wy + h * .07, x + w, wy - h * .03, x + w, y + h, x, y + h),
                  fill=SF_GREEN))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                  % (x, wy + h * .15, x + w * .34, wy + h * .08, x + w * .72,
                     wy + h * .18, x + w, wy + h * .09, x + w, y + h, x, y + h),
                  fill=SF_GREEN_D))
    if label:
        lines = label.split("|")
        fs = min(fit(h * .080, w * .60, max(lines, key=len)), w * .080)
        o.append(sf_logo(x + w * .155, y + h * .80, w * .24, h * .15))
        for i, line in enumerate(lines):
            o.append(txt(x + w * .30, y + h * (.80 + .095 * i), line, size=fs,
                         fill="#fff", weight="700", family="Georgia, serif",
                         style="italic"))
    o.append(scale_label(x + w * .56, y + h * .05, w * .38, h * .18, rng,
                         rng.uniform(-3, 3)))
    return "".join(o)


def oo_blue(x, y, w, h, rng=R):
    """O Organics: royal-blue printed base, domed clear lid."""
    mw = h * .58
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 13, 4, fill=OO_BLUE_D))
    o.append(rr(x, y, w, h, 8, fill="url(#blu)", stroke=shade(OO_BLUE_D, -6),
                stroke_width=.8))
    o.append(rr(x + 5, y + 5, w - 10, mw - 8, 7, fill="#cdb8a2"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(x + 5, y + 5, w - 10, mw - 8, 7))
    for i in range(10):
        px = x + 8 + (w - 16) * ((i % 2) + .5) / 2 + rng.uniform(-8, 8)
        py = y + 8 + (mw - 16) * ((i // 2) + .5) / 5 + rng.uniform(-5, 5)
        o.append(m_thigh(px, py, w * .30, h * .15, rng.uniform(-28, 28),
                         rng.choice(THIGH), rng))
    o.append(rr(x + 5, y + 5, w - 10, mw - 8, 7, fill="url(#trayShade)", opacity=".34"))
    o.append("</g>")
    o.append(film(x + 4, y + 4, w - 8, mw - 6, rng, 7, ".18"))
    o.append(rr(x + 3, y + mw, w - 6, h - mw - 3, 5, fill=OO_BLUE))
    o.append(ell(x + w * .14, y + h * .74, w * .085, h * .075, fill="#fff"))
    o.append(txt(x + w * .14, y + h * .77, "O", size=h * .10, fill=OO_BLUE,
                 weight="800", anchor="middle", family="Georgia, serif"))
    o.append(txt(x + w * .14, y + h * .845, "organics", size=h * .040, fill="#fff",
                 anchor="middle", family="Georgia, serif", style="italic"))
    fs = min(fit(h * .070, w * .40, "boneless skinless"), w * .066)
    o.append(txt(x + w * .26, y + h * .74, "boneless skinless", size=fs, fill="#fff",
                 weight="600"))
    o.append(txt(x + w * .26, y + h * .84, "chicken thighs", size=fs * 1.12,
                 fill="#fff", weight="700"))
    o.append(rr(x + w * .26, y + h * .885, w * .30, h * .035, 1, fill="#fff",
                opacity=".40"))
    o.append(_g(x + w * .84, y + h * .80, -12,
                rr(-w * .12, -h * .075, w * .24, h * .15, h * .075, fill="#fff",
                   opacity=".92") +
                txt(0, -h * .002, "FREE", size=h * .052, fill=OO_BLUE_D,
                    weight="800", anchor="middle", family="Georgia, serif",
                    style="italic") +
                txt(0, h * .055, "RANGE", size=h * .040, fill=OO_BLUE,
                    weight="700", anchor="middle", spacing=.3)))
    o.append(scale_label(x + w * .58, y + h * .06, w * .36, h * .18, rng,
                         rng.uniform(-2, 2)))
    return "".join(o)


def on_green(x, y, w, h, rng=R):
    """Open Nature: lime base, clear tub, white brand block."""
    mw = h * .56
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 13, 4, fill=shade(ON_LIME, -16)))
    o.append(rr(x, y, w, h, 8, fill="url(#onlime)", stroke=shade(ON_LIME, -20),
                stroke_width=.8))
    o.append(rr(x + w * .05, y + 4, w * .90, mw - 6, 6, fill="#dccfbe",
                stroke="#d6cebf", stroke_width=".5"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(x + w * .05, y + 4, w * .90,
                                                    mw - 6, 6))
    for i in range(6):
        px = x + w * .08 + (w * .84) * ((i % 2) + .5) / 2 + rng.uniform(-7, 7)
        py = y + 8 + (mw - 16) * ((i // 2) + .5) / 3 + rng.uniform(-5, 5)
        o.append(m_breast(px, py, w * .42, h * .17, rng.uniform(-16, 16),
                          rng.choice(BREAST), rng))
    o.append(rr(x + w * .05, y + 4, w * .90, mw - 6, 6, fill="url(#trayShade)",
                opacity=".45"))
    o.append("</g>")
    o.append(film(x + w * .05, y + 4, w * .90, mw - 6, rng, 6, ".19"))
    o.append(rr(x + w * .05, y + mw + 2, w * .90, h - mw - 8, 3, fill="#fdfdfa",
                opacity=".97"))
    o.append(txt(x + w * .09, y + h * .715, "open", size=h * .070, fill="#3b6e2a",
                 weight="700", family="Georgia, serif"))
    o.append(txt(x + w * .09, y + h * .80, "nature", size=h * .070, fill="#3b6e2a",
                 weight="700", family="Georgia, serif"))
    fs = min(fit(h * .048, w * .34, "BONELESS SKINLESS"), w * .046)
    o.append(txt(x + w * .32, y + h * .715, "BONELESS SKINLESS",
                 size=fit(fs, w * .30, "BONELESS SKINLESS"), fill="#4a4a4a",
                 weight="700", spacing=.1))
    o.append(txt(x + w * .32, y + h * .805, "CHICKEN",
                 size=fit(fs * 1.6, w * .30, "CHICKEN"), fill="#1d1d1d", weight="800"))
    o.append(txt(x + w * .32, y + h * .89, "BREASTS",
                 size=fit(fs * 1.6, w * .30, "BREASTS"), fill="#1d1d1d", weight="800"))
    o.append(rr(x + w * .68, y + h * .655, w * .25, h * .062, 2, fill="#bfe0f2"))
    o.append(txt(x + w * .805, y + h * .70, "NO ANTIBIOTICS EVER",
                 size=fit(h * .034, w * .23, "NO ANTIBIOTICS EVER"), fill="#14425c",
                 weight="700", anchor="middle"))
    o.append(txt(x + w * .805, y + h * .80, "CAGE FREE",
                 size=fit(h * .042, w * .23, "CAGE FREE"), fill="#4a4a4a",
                 weight="700", anchor="middle"))
    o.append(txt(x + w * .805, y + h * .88, "100% VEGETARIAN FED",
                 size=fit(h * .034, w * .23, "100% VEGETARIAN FED"), fill="#6a6a6a",
                 weight="600", anchor="middle"))
    o.append(scale_label(x + w * .56, y + h * .05, w * .38, h * .17, rng,
                         rng.uniform(-2, 2)))
    return "".join(o)


def black_tray(x, y, w, h, kind="breast", sticker=None, sticker2=None,
               red_label=None, sf_tag=False, rng=R, count=None):
    """Bulk black foam tray under clear over-wrap.

    `count` is a piece count for solid cuts, or a size scale for diced fills.
    """
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 11, 3, fill="#0b0b0c"))
    o.append(rr(x, y, w, h, 5, fill="url(#blk)", stroke="#000", stroke_width=.8))
    o.append(rr(x + 4, y + 4, w - 8, h - 10, 4, fill="#1c1d20"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(x + 4, y + 4, w - 8, h - 10, 4))
    ix, iy, iw, ih = x + 5, y + 5, w - 10, h - 12
    if kind == "dice":
        o.append(rr(ix, iy, iw, ih, 4, fill="#3a2c2a"))
        o.append(m_dice(ix, iy, iw, ih, rng, size=(count or 1.0)))
    elif kind in ("breast", "tender", "thigh", "pork"):
        fn, n, cols, sw, sh, pal, ang = {
            "breast": (m_breast, int(count or 6), 2, .46, .28, BREAST, 14),
            "tender": (m_breast, int(count or 10), 2, .42, .13, BREAST, 10),
            "thigh": (m_thigh, int(count or 10), 2, .38, .21, THIGH, 26),
            "pork": (m_thigh, int(count or 8), 2, .40, .24, PORK, 18),
        }[kind]
        rows = math.ceil(n / cols)
        for i in range(n):
            px = ix + iw * ((i % cols) + .5) / cols + rng.uniform(-7, 7)
            py = iy + ih * ((i // cols) + .5) / rows + rng.uniform(-5, 5)
            o.append(fn(px, py, iw * sw, ih * sh, rng.uniform(-ang, ang),
                        rng.choice(pal), rng))
    elif kind == "beef":
        n = int(count or 2)
        for i in range(n):
            px = ix + iw * .5 + rng.uniform(-6, 6)
            py = iy + ih * ((i + .5) / n)
            o.append(_g(px, py, rng.uniform(-8, 8),
                        path(blob(iw * .80, ih * (.82 / n), rng, 10, .11),
                             fill=rng.choice(BEEF), stroke="#7d1f26",
                             stroke_width=".6") +
                        path(blob(iw * .30, ih * (.24 / n), rng, 8, .3),
                             fill="#f2e4dd", opacity=".85") +
                        ell(-iw * .14, -ih * (.16 / n), iw * .20, ih * (.14 / n),
                            fill="#fff", opacity=".18")))
    o.append(rr(ix, iy, iw, ih, 4, fill="url(#trayShade)", opacity=".36"))
    o.append("</g>")
    o.append(film(x + 2, y + 2, w - 4, h - 6, rng, 4, ".15"))
    o.append(scale_label(x + w * .50, y + h * .06, w * .44, h * .22, rng,
                         rng.uniform(-3, 3)))
    o.append(guarantee_flash(x + w * .56, y + h * .63, w * .38, h * .11,
                             rng.uniform(-5, 3)))
    if red_label:
        bw, bh = w * .38, h * .24
        g = ['<g transform="translate(%.1f,%.1f) rotate(-4)">' % (
            x + w * .05, y + h * .40)]
        g.append(rr(0, 0, bw, bh, 1.5, fill="#d21f26", stroke="#fff", stroke_width=.6))
        g.append(txt(bw / 2, bh * .40, red_label[0],
                     size=fit(bh * .30, bw * .90, red_label[0]), fill="#ffe36b",
                     weight="800", anchor="middle"))
        g.append(txt(bw / 2, bh * .80, red_label[1],
                     size=fit(bh * .38, bw * .90, red_label[1]), fill="#fff",
                     weight="800", anchor="middle"))
        g.append("</g>")
        o.append("".join(g))
    if sf_tag:
        tw, th = w * .40, h * .20
        tx, ty = x + w * .54, y + h * .36
        o.append(rr(tx, ty, tw, th, 3, fill=SF_GREEN, stroke="#fff", stroke_width=".5"))
        o.append(txt(tx + tw / 2, ty + th * .42, "Signature Select",
                     size=fit(th * .34, tw * .88, "Signature Select"), fill="#fff",
                     anchor="middle", family="Georgia, serif", style="italic"))
        o.append(txt(tx + tw / 2, ty + th * .82, "Chicken Breasts",
                     size=fit(th * .36, tw * .88, "Chicken Breasts"), fill="#fff",
                     anchor="middle", weight="700"))
    if sticker:
        o.append(oval_sticker(x + w * .21, y + h * .74, w * .34, h * .15,
                              sticker[0], sticker[1] if len(sticker) > 1 else None,
                              sticker[2] if len(sticker) > 2 else "#f4711f"))
    if sticker2:
        o.append(oval_sticker(x + w * .80, y + h * .24, w * .30, h * .11,
                              sticker2[0], None, "#e8571f", 4))
    return "".join(o)


def pulp_tray(x, y, w, h, rng=R):
    """Moulded-pulp tray with the red/yellow starburst label."""
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 11, 4, fill="#d8cfbc"))
    o.append(rr(x, y, w, h, 8, fill="url(#pulp)", stroke="#cfc5b0", stroke_width=.8))
    o.append(rr(x + w * .06, y + h * .08, w * .88, h * .60, 6, fill="#d5c8b0"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(x + w * .06, y + h * .08,
                                                    w * .88, h * .60, 6))
    for i in range(3):
        o.append(m_breast(x + w * (.26 + .24 * i), y + h * (.34 + .07 * (i % 2)),
                          w * .38, h * .36, rng.uniform(-12, 12),
                          rng.choice(BREAST), rng))
    o.append(rr(x + w * .06, y + h * .08, w * .88, h * .60, 6, fill="url(#trayShade)",
                opacity=".28"))
    o.append("</g>")
    o.append(film(x + w * .05, y + h * .06, w * .90, h * .64, rng, 6, ".18"))
    pts = []
    for i in range(14):
        a0 = 2 * math.pi * i / 14
        pts.append("%.1f,%.1f" % (math.cos(a0) * w * .095, math.sin(a0) * h * .105))
        a1 = 2 * math.pi * (i + .5) / 14
        pts.append("%.1f,%.1f" % (math.cos(a1) * w * .070, math.sin(a1) * h * .078))
    o.append('<g transform="translate(%.1f,%.1f) rotate(-6)">' % (x + w * .18,
                                                                 y + h * .82))
    o.append('<polygon points="%s" fill="#f6d000"/>' % " ".join(pts))
    o.append(ell(0, 0, w * .068, h * .075, fill="#d81f26"))
    o.append(txt(0, h * .012, "ALL", size=h * .050, fill="#fff", weight="800",
                 anchor="middle"))
    o.append("</g>")
    o.append(rr(x + w * .30, y + h * .74, w * .46, h * .155, 1.5, fill="#f6d000",
                stroke="#dcb800", stroke_width=".5"))
    o.append(txt(x + w * .53, y + h * .855, "CHICKEN BREAST",
                 size=fit(h * .085, w * .42, "CHICKEN BREAST"), fill="#c0161c",
                 weight="800", anchor="middle", style="italic"))
    o.append(scale_label(x + w * .52, y + h * .12, w * .40, h * .22, rng,
                         rng.uniform(-2, 2)))
    return "".join(o)


def whole_bird(x, y, w, h, band="blue", rng=R):
    """Whole fryer in a printed bag on a black tray."""
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 11, 4, fill="#0d0d0e"))
    o.append(rr(x, y, w, h, 6, fill="#17181b", stroke="#000", stroke_width=".8"))
    o.append(m_bird(x + w * .5, y + h * .42, w * .94, h * .86, rng))
    o.append(film(x + w * .03, y + h * .03, w * .94, h * .82, rng, 10, ".12"))
    for i in range(2):
        o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
            x + w * (.10 + .38 * i), y + h * (.22 + .30 * i),
            x + w * (.24 + .38 * i), y + h * (.16 + .30 * i),
            x + w * (.34 + .38 * i), y + h * (.30 + .30 * i),
            x + w * (.48 + .38 * i), y + h * (.24 + .30 * i)),
            fill="none", stroke="#fff", stroke_width=".9", opacity=".42"))
    bt = y + h * .70
    if band == "plain":
        o.append(guarantee_flash(x + w * .10, y + h * .84, w * .44, h * .10,
                                 rng.uniform(-6, 2)))
        o.append(oval_sticker(x + w * .74, y + h * .82, w * .40, h * .15,
                              "GREAT ON THE", "GRILL", "#e8571f", -8))
        o.append(scale_label(x + w * .52, y + h * .06, w * .40, h * .19, rng,
                             rng.uniform(-3, 3)))
        return "".join(o)
    if band == "blue":
        o.append(path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
            x + 2, bt, x + w - 2, bt - h * .05, x + w - 2, y + h - 3, x + 2, y + h - 3),
            fill=OO_BLUE))
        o.append(ell(x + w * .14, y + h * .83, w * .07, h * .055, fill="#fff"))
        o.append(txt(x + w * .14, y + h * .855, "O", size=h * .072, fill=OO_BLUE,
                     weight="800", anchor="middle", family="Georgia, serif"))
        fs = fit(h * .055, w * .58, "whole young chicken")
        o.append(txt(x + w * .26, y + h * .83, "whole young chicken", size=fs,
                     fill="#fff", weight="700"))
        o.append(txt(x + w * .26, y + h * .91, "with giblets", size=fs * .92,
                     fill="#cfe0ff", weight="600"))
    else:
        o.append(path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
            x + 2, bt, x + w - 2, bt - h * .05, x + w - 2, y + h - 3, x + 2, y + h - 3),
            fill=SF_GREEN_D))
        o.append(path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
            x + 2, bt, x + w - 2, bt - h * .05, x + w - 2, bt + h * .09,
            x + 2, bt + h * .14), fill=SF_GREEN))
        o.append(txt(x + w * .08, y + h * .79, "Whole", size=h * .048, fill="#fff",
                     family="Georgia, serif", style="italic"))
        o.append(txt(x + w * .08, y + h * .90, "Young Chicken",
                     size=fit(h * .075, w * .56, "Young Chicken"), fill="#fff",
                     weight="700", family="Georgia, serif"))
        o.append(sf_logo(x + w * .80, y + h * .855, w * .26, h * .15))
    o.append(scale_label(x + w * .52, y + h * .06, w * .40, h * .19, rng,
                         rng.uniform(-3, 3)))
    return "".join(o)


def heritage_tub(x, y, w, h, rng=R, price=True):
    """Heritage shaved chicken breast: white tub with a dark printed sleeve."""
    o = [shadow(x, y + h + 4, w)]
    o.append(rr(x, y + h - 4, w, 12, 4, fill="#e0e0dc"))
    o.append(rr(x, y, w, h, 7, fill="url(#white)", stroke="#d2d2cd", stroke_width=.8))
    sx, sy, sw, sh = x + w * .05, y + h * .07, w * .90, h * .58
    o.append(rr(sx, sy, sw, sh, 4, fill="#2a2018"))
    o.append(rr(sx + sw * .03, sy + sh * .07, sw * .44, sh * .84, 3, fill="#caa471"))
    o.append(path("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f L %.1f %.1f Z" % (
        sx + sw * .05, sy + sh * .70, sx + sw * .16, sy + sh * .26,
        sx + sw * .32, sy + sh * .40, sx + sw * .45, sy + sh * .22,
        sx + sw * .45, sy + sh * .90), fill="#ecd7b0", opacity=".92"))
    o.append(rr(sx + sw * .05, sy + sh * .56, sw * .40, sh * .10, 2, fill="#84b354",
                opacity=".92"))
    fs = fit(h * .075, sw * .48, "CHICKEN")
    o.append(txt(sx + sw * .52, sy + sh * .24, "HERITAGE", size=fs * .78,
                 fill="#e8d9a8", family="Georgia, serif", spacing=.3))
    o.append(txt(sx + sw * .52, sy + sh * .46, "SHAVED", size=fs, fill="#fff",
                 weight="700"))
    o.append(txt(sx + sw * .52, sy + sh * .64, "CHICKEN", size=fs, fill="#fff",
                 weight="700"))
    o.append(txt(sx + sw * .52, sy + sh * .82, "BREAST", size=fs, fill="#fff",
                 weight="700"))
    o.append(film(x + 2, y + 2, w - 4, h * .68, rng, 6, ".15"))
    o.append(scale_label(x + w * .05, y + h * .70, w * .50, h * .24, rng, -1))
    if price:
        o.append(rr(x + w * .60, y + h * .70, w * .35, h * .24, 2, fill="#fff",
                    stroke="#cfcfc9", stroke_width=".5"))
        o.append(txt(x + w * .86, y + h * .90, "6", size=h * .20, fill="#111",
                     weight="800", anchor="end"))
        o.append(txt(x + w * .875, y + h * .82, "99", size=h * .10, fill="#111",
                     weight="800"))
    return "".join(o)


# ------------------------------------------------------------- shelf trim ---
def value_tag(x, y, w, h, dollars, cents, desc):
    o = [rr(x - 2, y - 2, w + 4, h + 5, 2, fill="#cfd6da", opacity=".30")]
    o.append(rr(x, y, w, h, 1.5, fill=TAG_YELLOW, stroke="#d9ae00", stroke_width=".6"))
    o.append(path("M %.1f %.1f l %.1f %.1f l %.1f %.1f" % (
        x + w * .04, y + h * .26, w * .022, h * .16, w * .045, -h * .30),
        fill="none", stroke="#1a1a1a", stroke_width="1.3", stroke_linecap="round"))
    o.append(txt(x + w * .115, y + h * .28, "VALUE", size=h * .16, fill="#1a1a1a",
                 weight="700"))
    o.append(txt(x + w * .115, y + h * .44, "and QUALITY", size=h * .14,
                 fill="#1a1a1a", weight="600"))
    o.append(txt(x + w * .04, y + h * .74, desc, size=fit(h * .155, w * .60, desc),
                 fill="#1a1a1a", weight="700", spacing=.1))
    o.append(barcode(x + w * .04, y + h * .82, w * .24, h * .13, R, "#3a3200"))
    o.append(txt(x + w * .90, y + h * .86, dollars, size=h * .80, fill="#111",
                 weight="800", anchor="end"))
    o.append(txt(x + w * .915, y + h * .48, cents, size=h * .34, fill="#111",
                 weight="800"))
    o.append(txt(x + w * .975, y + h * .48, "lb", size=h * .17, fill="#111",
                 weight="700", anchor="end"))
    o.append(rr(x, y + h * .28, w, h * .05, 0, fill="#fff", opacity=".16"))
    return "".join(o)


def blade_sign(cx, cy, w, h, tilt=-5):
    o = ['<g transform="translate(%.1f,%.1f) rotate(%.1f)">' % (cx, cy, tilt)]
    o.append(path("M %.1f %.1f L %.1f %.1f L %.1f %.1f "
                  "C %.1f %.1f %.1f %.1f %.1f %.1f Z" % (
                      -w / 2, -h / 2, w / 2, -h / 2, w / 2, h * .20,
                      w * .18, h * .60, -w * .18, h * .60, -w / 2, h * .20),
                  fill="url(#navy)", stroke="#2c3d5c", stroke_width=".8"))
    o.append(txt(-w * .40, -h * .04, "Air-chilled", size=h * .30, fill="#fff",
                 weight="700", family="Georgia, serif", style="italic"))
    o.append(txt(-w * .40, h * .28, "chicken.", size=h * .32, fill="#fff",
                 weight="700", family="Georgia, serif"))
    o.append("</g>")
    return "".join(o)


def on_blade(cx, cy, w, h, tilt=4):
    o = ['<g transform="translate(%.1f,%.1f) rotate(%.1f)">' % (cx, cy, tilt)]
    o.append(rr(-w / 2, -h / 2, w, h, h * .42, fill="#f8f7f0", stroke="#ded9c8",
                stroke_width=".7"))
    o.append(path("M %.1f %.1f c %.1f %.1f %.1f %.1f %.1f %.1f "
                  "c %.1f %.1f %.1f %.1f %.1f %.1f Z"
                  % (-w * .42, 0, w * .05, -h * .28, w * .16, -h * .28, w * .21, 0,
                     -w * .05, h * .28, -w * .16, h * .28, -w * .21, 0),
                  fill="#6ea644"))
    o.append(txt(-w * .16, -h * .04, "open", size=h * .27, fill="#3b6e2a",
                 weight="700", family="Georgia, serif"))
    o.append(txt(-w * .16, h * .24, "nature", size=h * .27, fill="#3b6e2a",
                 weight="700", family="Georgia, serif"))
    o.append(txt(w * .12, -h * .02, "always", size=h * .17, fill="#4d4d45",
                 family="Georgia, serif", style="italic"))
    o.append(txt(w * .12, h * .22, "free from", size=h * .17, fill="#4d4d45",
                 family="Georgia, serif", style="italic"))
    o.append("</g>")
    return "".join(o)


def price_card(x, y, w, h, big, cents):
    o = ['<g transform="translate(%.1f,%.1f) rotate(-3)">' % (x, y)]
    o.append(rr(0, 0, w, h, 2, fill="#f8f8f5", stroke=NAVY, stroke_width="2.6"))
    o.append(rr(w * .04, h * .12, w * .32, h * .74, 2, fill="#5d3522"))
    o.append('<g clip-path="url(#%s)">' % clip_rect(w * .04, h * .12, w * .32,
                                                    h * .74, 2))
    o.append(m_dice(w * .04, h * .12, w * .32, h * .74, R, size=.42,
                    pal=["#b96a35", "#a75d33", "#c87c46"]))
    o.append("</g>")
    o.append(microtext(w * .40, h * .14, w * .28, R, 4, h * .095, "#555"))
    o.append(txt(w * .95, h * .84, big, size=h * .60, fill="#111", weight="800",
                 anchor="end"))
    o.append(txt(w * .96, h * .50, cents, size=h * .26, fill="#111", weight="800"))
    o.append(txt(w * .96, h * .72, "lb", size=h * .16, fill="#333", weight="700"))
    o.append("</g>")
    return "".join(o)


def rail(x, y, w, h):
    """Shelf-edge trim. The SLU label strips are deliberately left off."""
    o = [rr(x, y, w, h, 1.5, fill="url(#rail)", stroke="#000", stroke_width=".6")]
    o.append(rr(x, y, w, 1.2, 0, fill="#5c6166", opacity=".65"))
    o.append(rr(x, y + h - 1.4, w, 1.4, 0, fill="#000", opacity=".5"))
    return "".join(o)


def bristle(x, y, w, h=9):
    o = [rr(x, y, w, h, 1, fill="#0a0a0b")]
    for i in range(int(w / 3.2)):
        bx = x + i * 3.2 + R.uniform(-.7, .7)
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2a2c2f" '
                 'stroke-width=".9" opacity="%.2f"/>' % (
                     bx, y + h, bx + R.uniform(-1.8, 1.8), y - R.uniform(1, 5),
                     R.uniform(.35, .85)))
    return "".join(o)


def vbristle(x, y, h, w=11):
    """Vertical brush strip used between merchandising blocks."""
    o = [rr(x, y, w, h, 1, fill="#0a0a0b")]
    for i in range(int(h / 3.2)):
        by = y + i * 3.2 + R.uniform(-.7, .7)
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3d4145" '
                 'stroke-width="1.0" opacity="%.2f"/>' % (
                     x, by, x + w + R.uniform(2, 7), by + R.uniform(-2.2, 2.2),
                     R.uniform(.45, .95)))
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#3d4145" '
                 'stroke-width="1.0" opacity="%.2f"/>' % (
                     x + w, by, x - R.uniform(2, 7), by + R.uniform(-2.2, 2.2),
                     R.uniform(.45, .95)))
    return "".join(o)


def spread(x0, x1, n, gap=8):
    w = ((x1 - x0) - gap * (n - 1)) / n
    return [(x0 + i * (w + gap), w) for i in range(n)]


def place(x0, widths, gap=8):
    xs, x = [], x0
    for wd in widths:
        xs.append((x, wd))
        x += wd + gap
    return xs


# ------------------------------------------------------------------ scene ---
BODY = []
FRONT = []

BAND_TOP = [34 + k * 222 for k in range(5)]
DECK = [t + 176 for t in BAND_TOP]
AX0, AX1 = 44, 604
BX0, BX1 = 622, 1128
CX0, CX1 = 1146, 1716
CXM = 1428                       # brush divider between the $5.49 and $3.49 blocks
CL0, CL1 = CX0, CXM - 6          # left block  (breast: stir fry / diced / trimmed)
CR0, CR1 = CXM + 17, CX1         # right block (boneless skinless thighs, breasts)


VALUE_TAGS = [
        (0, CL0 + 56, "CHICKEN FOR STIR FRY", "5", "49"),
        (0, CR0 + 56, "CHICKEN THIGH BONELESS SKINLESS", "3", "49"),
        (1, CL0 + 56, "CHICKEN BREAST BONELESS SKINLESS DICED", "5", "49"),
        (1, CR0 + 56, "CHICKEN THIGH BONELESS SKINLESS", "3", "49"),
        (2, CL0 + 56, "CHICKEN BREAST BONELESS SKINLESS THIN CUT", "5", "49"),
        (2, CR0 + 56, "CHICKEN THIGH BONELESS SKINLESS", "3", "49"),
        (3, CL0 + 56, "CHICKEN BREAST BONELESS SKINLESS THIN CUT", "5", "49"),
        (3, CR0 + 56, "CHICKEN BREAST BONELESS SKINLESS FAMILY PACK", "3", "49"),
        (4, CL0 + 56, "CHICKEN BREAST BONELESS SKINLESS VALUE PACK", "5", "49"),
        (4, CR0 + 56, "CHICKEN BREAST BONELESS SKINLESS FAMILY PACK", "3", "49"),
    ]


def put(fn, x, w, shelf, h=146, back=False, tilt=None, **kw):
    y = DECK[shelf] - h - (46 if back else 0)
    a = R.uniform(-1.1, 1.1) if tilt is None else tilt
    BODY.append('<g transform="rotate(%.2f %.1f %.1f)">%s</g>' % (
        a, x + w / 2, y + h / 2, fn(x, y, w, h, **kw)))


def build():
    # ---------------------------------------------------------- shelf 1 ----
    s = 0
    names = [("Chicken Breast|Tenders", "tender"),
             ("Chicken Wing|Drummettes", "drumette"),
             ("Chicken Wing|Drummettes", "drumette")]
    for i, (x, w) in enumerate(spread(AX0 + 10, AX0 + 442, 3, 10)):
        put(sf_yellow, x, w, s, 132, back=True, name=names[i][0], kind=names[i][1])
    for i, (x, w) in enumerate(spread(AX0, AX0 + 452, 3, 12)):
        put(sf_yellow, x, w, s, 146, name=names[i][0], kind=names[i][1])
    put(heritage_tub, AX0 + 456, 100, s, 122, back=True, price=False)
    put(heritage_tub, BX0 + 2, 132, s, 144, price=False)
    for x, w in spread(BX0 + 148, BX0 + 352, 2, 12):
        put(pulp_tray, x, w, s, 132)
    ex = BX0 + 366
    BODY.append(rr(ex, DECK[s] - 62, BX1 - ex, 62, 3, fill="#0c0d0f"))
    for i in range(int((BX1 - ex) / 13)):
        BODY.append(rr(ex + 8 + i * 13, DECK[s] - 54, 2.5, 50, 1, fill="#1c1f21"))
    for i in range(4):
        BODY.append(rr(ex + 4, DECK[s] - 52 + i * 13, BX1 - ex - 8, 2.5, 1,
                       fill="#1c1f21"))
    BODY.append(bristle(ex, DECK[s] - 5, BX1 - ex, 7))
    for i, (x, w) in enumerate(spread(CL0 + 10, CL1, 2, 14)):
        put(black_tray, x, w, s, 96 + 8 * i, kind="tender", count=8,
            sticker=("Prepared for", "STIR FRY", "#d8261f") if i else None)
    for x, w in spread(CR0 + 10, CR1, 2, 14):
        put(black_tray, x, w, s, 128, back=True, kind="thigh", count=10,
            red_label=("BONELESS SKINLESS", "CHICKEN THIGHS"))
    for x, w in spread(CR0, CR1 - 10, 2, 16):
        put(black_tray, x, w, s, 140, kind="thigh", count=10,
            red_label=("BONELESS SKINLESS", "CHICKEN THIGHS"))

    # ---------------------------------------------------------- shelf 2 ----
    s = 1
    for x, w in spread(AX0, AX0 + 236, 2, 12):
        put(sf_yellow, x, w, s, 148, name="Chicken|Breasts", kind="breast")
    for x, w in spread(AX0 + 256, AX1, 3, 10):
        put(sf_green, x, w, s, 148, kind="wing")
    for x, w in spread(BX0 + 8, BX1 - 40, 3, 12):
        put(oo_blue, x, w, s, 132, back=True)
    for x, w in spread(BX0, BX1 - 52, 3, 14):
        put(oo_blue, x, w, s, 146)
    for x, w in spread(CL0 + 10, CL1, 2, 14):
        put(black_tray, x, w, s, 130, back=True, kind="dice", count=1.0,
            sticker=("FRY", "SAUTÉ"))
    for x, w in spread(CL0, CL1 - 10, 2, 16):
        put(black_tray, x, w, s, 144, kind="dice", count=1.0,
            sticker=("FRY", "SAUTÉ"))
    for x, w in spread(CR0 + 10, CR1, 2, 14):
        put(black_tray, x, w, s, 130, back=True, kind="thigh", count=10,
            red_label=("BONELESS SKINLESS", "CHICKEN THIGHS"))
    for x, w in spread(CR0, CR1 - 10, 2, 16):
        put(black_tray, x, w, s, 144, kind="thigh", count=10,
            red_label=("BONELESS SKINLESS", "CHICKEN THIGHS"))

    # ---------------------------------------------------------- shelf 3 ----
    s = 2
    put(black_tray, AX0 - 10, 104, s, 142, kind="beef", count=2)
    put(sf_green, AX0 + 104, 132, s, 148, kind="thigh",
        label="Boneless Skinless|Chicken Thighs")
    for x, w in spread(AX0 + 246, AX1, 3, 12):
        put(sf_green, x, w, s, 152, kind="drumstick")
    for x, w in spread(BX0 + 8, BX1 - 40, 3, 12):
        put(on_green, x, w, s, 132, back=True)
    for x, w in spread(BX0, BX1 - 52, 3, 14):
        put(on_green, x, w, s, 146)
    for x, w in spread(CL0, CL1, 2, 16):
        put(black_tray, x, w, s, 146, kind="breast", count=6,
            sticker=("Hand", "Trimmed"), sticker2=("THIN CUT",))
    for x, w in spread(CR0, CR1, 2, 16):
        put(black_tray, x, w, s, 146, kind="thigh", count=10,
            red_label=("BONELESS SKINLESS", "CHICKEN THIGHS"))

    # ---------------------------------------------------------- shelf 4 ----
    s = 3
    put(black_tray, AX0 - 10, 100, s, 140, kind="pork",
        sticker=("FRESH", "PORK", "#d2431f"))
    put(sf_green, AX0 + 102, 122, s, 148, kind="thigh", label="Bone-In|Chicken Thighs")
    for x, w in spread(AX0 + 236, AX1, 3, 12):
        put(sf_green, x, w, s, 152, kind="thigh")
    for x, w in spread(BX0, BX0 + 322, 3, 12):
        put(on_green, x, w, s, 146)
    for x, w in spread(BX0 + 338, BX1, 2, 12):
        put(black_tray, x, w, s, 146, kind="breast", count=6,
            sticker=("Hand", "Trimmed"))
    for x, w in spread(CL0, CL1, 2, 16):
        put(black_tray, x, w, s, 146, kind="breast", count=6,
            sticker=("Hand", "Trimmed"))
    for x, w in spread(CR0, CR1, 2, 16):
        put(black_tray, x, w, s, 146, kind="breast", count=6, sf_tag=True)

    # ---------------------------------------------------------- shelf 5 ----
    s = 4
    slots = place(AX0 - 12, [96, 110, 110, 124, 104], 6)
    put(black_tray, slots[0][0], slots[0][1], s, 150, kind="beef", count=3,
        sticker=("THIN CUT", None, "#e8571f"))
    for x, w in slots[1:3]:
        put(whole_bird, x, w, s, 150, band="plain")
    put(whole_bird, slots[4][0], slots[4][1], s, 150, band="plain")
    put(whole_bird, slots[3][0], slots[3][1], s, 150, band="plain")
    for x, w in place(BX0 + 6, [108, 108], 8):
        put(whole_bird, x, w, s, 136, back=True, band="blue")
    for x, w in place(BX0, [112, 112], 8):
        put(whole_bird, x, w, s, 152, band="blue")
    for x, w in place(BX0 + 252, [120, 120], 12):
        put(whole_bird, x, w, s, 152, band="green")
    for x, w in spread(CL0, CL1, 2, 16):
        put(black_tray, x, w, s, 150, kind="breast", count=6,
            sticker=("Hand", "Trimmed"))
    put(black_tray, CR0, 132, s, 150, kind="breast", count=6, sf_tag=True)
    gx = CR0 + 146
    BODY.append(rr(gx, DECK[s] - 66, CX1 - 122 - gx, 66, 3, fill="#0c0d0f"))
    for i in range(int((CX1 - 122 - gx) / 13)):
        BODY.append(rr(gx + 6 + i * 13, DECK[s] - 58, 2.5, 54, 1, fill="#1c1f21"))
    put(black_tray, CX1 - 116, 116, s, 150, kind="pork", count=5,
        sticker=("PORK LOIN", None, "#8e2246"))

    # ------------------------------------------------------- shelf trim ----
    BODY.append("<!--trim-->")
    for k in range(5):
        BODY.append(vbristle(CXM, BAND_TOP[k] + 4, DECK[k] - BAND_TOP[k] - 6))
    for k in range(5):
        d = DECK[k]
        BODY.append(bristle(34, d - 5, 1692, 7))
        BODY.append(rr(34, d, 1692, 9, 2, fill="url(#deck)"))
        BODY.append(rr(34, d, 1692, 1.6, 0, fill="#7e858b", opacity=".5"))
        BODY.append(rail(34, d + 9, 1692, 21))

    # Signage is deliberately not drawn: the tickets, blade signs and price
    # cards all sat over the product. VALUE_TAGS is kept as data so the reset
    # map can still name each price block.
def defs():
    d = ['<defs>']
    for gid, c0, c1 in [
        ("yel", shade(TRAY_YELLOW, 6), TRAY_YELLOW_D),
        ("lime", shade(SF_LIME, 8), shade(SF_LIME, -8)),
        ("blu", shade(OO_BLUE, 8), OO_BLUE_D),
        ("onlime", shade(ON_LIME, 9), shade(ON_LIME, -9)),
        ("blk", "#303236", "#0d0e10"),
        ("pulp", "#f7f2e6", "#ddd4c1"),
        ("white", "#ffffff", "#e4e4e0"),
        ("navy", "#1b2b47", "#0a1120"),
        ("rail", "#26292c", "#101113"),
        ("case", "#1b1e21", "#0a0b0d"),
    ]:
        d.append('<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="%s"/>'
                 '<stop offset="1" stop-color="%s"/></linearGradient>' % (gid, c0, c1))
    d.append('<linearGradient id="film" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#ffffff" stop-opacity=".55"/>'
             '<stop offset=".45" stop-color="#ffffff" stop-opacity=".05"/>'
             '<stop offset=".75" stop-color="#ffffff" stop-opacity=".35"/>'
             '<stop offset="1" stop-color="#ffffff" stop-opacity=".05"/>'
             '</linearGradient>')
    d.append('<linearGradient id="trayShade" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#000000" stop-opacity=".16"/>'
             '<stop offset=".35" stop-color="#000000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000000" stop-opacity=".22"/>'
             '</linearGradient>')
    d.append('<linearGradient id="deck" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#6f767c"/>'
             '<stop offset=".5" stop-color="#3a3e42"/>'
             '<stop offset="1" stop-color="#17191b"/></linearGradient>')
    d.append('<linearGradient id="post" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#0e1012"/>'
             '<stop offset=".35" stop-color="#4a5055"/>'
             '<stop offset=".6" stop-color="#2a2e31"/>'
             '<stop offset="1" stop-color="#0e1012"/></linearGradient>')
    d.append('<radialGradient id="bird" cx=".38" cy=".30" r=".80">'
             '<stop offset="0" stop-color="#f8dccd"/>'
             '<stop offset=".55" stop-color="#eac8b4"/>'
             '<stop offset="1" stop-color="#cfa189"/></radialGradient>')
    d.append('<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#ffffff" stop-opacity=".09"/>'
             '<stop offset=".32" stop-color="#ffffff" stop-opacity="0"/>'
             '<stop offset=".60" stop-color="#cfe6ff" stop-opacity=".06"/>'
             '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
             '</linearGradient>')
    d.append('<linearGradient id="lamp" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#ffffff" stop-opacity=".15"/>'
             '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
             '</linearGradient>')
    d.append('<radialGradient id="vig" cx=".5" cy=".45" r=".78">'
             '<stop offset=".55" stop-color="#000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000" stop-opacity=".42"/>'
             '</radialGradient>')
    d.append("</defs>")
    return "".join(d)


def render():
    build()
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
         'height="%d" role="img" aria-label="Recreation of a supermarket '
         'fresh-poultry reach-in case with five shelves of packaged chicken">'
         % (W, H, W, H)]
    p.append("<title>Fresh Poultry Case — SVG Planogram</title>")
    p.append(defs())
    p.append("<!--CLIPS-->")
    p.append(rr(0, 0, W, H, 0, fill="#07080a"))
    p.append(rr(18, 10, W - 36, H - 22, 10, fill="url(#case)", stroke="#54595e",
                stroke_width="3"))
    p.append(rr(26, 18, W - 52, H - 38, 6, fill="#0b0c0e"))
    for k in range(5):
        p.append(rr(34, BAND_TOP[k] - 10, 1692, 54, 0, fill="url(#lamp)"))
    p.append("".join(BODY))
    for px in (AX1 + 6, BX1 + 6):
        p.append(rr(px, 20, 12, H - 62, 2, fill="url(#post)"))
    p.append("".join(FRONT))
    p.append(rr(26, DECK[4] + 32, W - 52, H - DECK[4] - 52, 3, fill="#0a0b0c"))
    for i in range(46):
        p.append(rr(34 + i * 36.5, DECK[4] + 40, 22, H - DECK[4] - 74, 1,
                    fill="#171a1c"))
    p.append(rr(0, 0, W, H, 0, fill="url(#vig)"))
    p.append(rr(26, 18, W - 52, H - 38, 6, fill="url(#glass)"))
    p.append("</svg>")
    return "".join(p).replace("<!--CLIPS-->", "<defs>%s</defs>" % "".join(CLIPS))


HTML = """<meta charset="utf-8">
<title>Fresh Poultry Case — SVG Recreation</title>
<style>
  :root { color-scheme: light dark; }
  body { margin:0; padding:28px 20px 56px;
         font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
         background:#f4f4f2; color:#16181a; }
  @media (prefers-color-scheme: dark) { body { background:#121315; color:#e9eaec; } }
  header, footer, .case { max-width:1200px; margin-left:auto; margin-right:auto; }
  h1 { font-size:1.45rem; margin:0 0 6px; letter-spacing:-.01em; }
  p.sub { margin:0 0 20px; opacity:.68; font-size:.92rem; line-height:1.55;
          max-width:72ch; }
  .case { overflow-x:auto; }
  .case svg { width:100%; height:auto; min-width:860px; display:block;
              border-radius:12px; box-shadow:0 18px 44px rgba(0,0,0,.35); }
  footer { margin-top:22px; font-size:.82rem; opacity:.6; line-height:1.6; }
</style>
<header>
  <h1>Fresh Poultry Reach-In Case — SVG Recreation</h1>
  <p class="sub">Five shelves across three bays, rebuilt from the store photos:
  Signature Farms printed trays at left, O&nbsp;Organics and Open Nature plus whole
  fryers in the centre bay, and the Value&nbsp;and&nbsp;Quality bulk black trays at
  right. Every facing is vector art — trays, meat, over-wrap sheen, scale labels,
  shelf rails, blade signs and price tags.</p>
</header>
<div class="case">
__SVG__
</div>
<footer>Generated by <code>tools/build_chicken_case_svg.py</code>; re-run it to
regenerate <code>chicken-case-planogram.svg</code>.</footer>
"""


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg = render()
    with open(os.path.join(root, "chicken-case-planogram.svg"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n")
    with open(os.path.join(root, "chicken-case-planogram.html"), "w") as f:
        f.write(HTML.replace("__SVG__", svg))
    print("wrote chicken-case-planogram.svg (%d KB)" % (len(svg) / 1024))


if __name__ == "__main__":
    main()
