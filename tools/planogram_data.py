#!/usr/bin/env python3
"""
Grid model and shared data for the planogram app.

The case is a grid, not a scatter of packs. Every shelf splits into three bay
tracks (A, B, C); every track is a row of cells; every cell holds one item at a
depth. Cell geometry is derived from the track, so nothing carries hand-placed
coordinates:

    cell width = (track width - gutters) * cell.units / sum(units)

`units` is the cell's share of its track and defaults to 1, which is the hook
for items that need a smaller or larger pack space — drop a cell to 0.5 and the
rest of the track takes up the slack automatically.

Adding a section later: give build_section() another layout builder that
populates B.BODY / B.FRONT and calls B.put() per facing; the grid is inferred
from what it places.
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_chicken_case_svg as B                                   # noqa: E402

VARIANTS = 2
GUTTER = 10           # space between cells in a track
BACK_RISE = 46        # how far a back-row pack sits above the front one
BACK_INSET = 6        # and how much narrower it is on each side
GAP_MIN = 100         # a bare run this wide becomes an empty cell

GROUPS = {
    "sf_yellow": "Signature Select — printed tray",
    "sf_green": "Signature Select — clear-top tray",
    "oo_blue": "O Organics",
    "on_green": "Open Nature",
    "black_tray": "Bulk black tray",
    "whole_bird": "Whole fryer",
    "pulp_tray": "Other brands",
    "heritage_tub": "Other brands",
}

NAMES = {
    ("sf_yellow", "tender"): "SS Chicken Breast Tenders",
    ("sf_yellow", "drumette"): "SS Chicken Wing Drummettes",
    ("sf_yellow", "breast"): "SS Chicken Breasts",
    ("sf_yellow", "wing"): "SS Chicken Wings",
    ("sf_green", "wing"): "SS Small Chicken Wings",
    ("sf_green", "drumstick"): "SS Chicken Drumstick value pack",
    ("sf_green", "thigh"): "SS Chicken Thigh value pack",
    ("sf_green", "breast"): "SS Chicken Breast value pack",
    ("black_tray", "tender"): "Chicken breast strips",
    ("black_tray", "dice"): "Diced chicken breast",
    ("black_tray", "breast"): "Boneless skinless breasts",
    ("black_tray", "thigh"): "Boneless skinless thighs",
    ("black_tray", "pork"): "Pork",
    ("black_tray", "beef"): "Beef",
    ("oo_blue", None): "O Organics b/s chicken thighs",
    ("on_green", None): "Open Nature b/s chicken breasts",
    ("pulp_tray", None): "All Natural chicken breast (pulp tray)",
    ("heritage_tub", None): "Heritage shaved chicken breast",
    ("whole_bird", None): "Whole fryer",
}

SHORT = [("Signature Select", "SS"), ("Boneless skinless", "B/S"),
         ("boneless skinless", "b/s"), (" value pack", " value pk")]

# Items the bar always carries, whether or not they are on the shelf today.
EXTRAS = [
    ("sf_yellow", {"name": "Chicken|Wings", "kind": "wing"}, 148, 148),
    ("sf_green", {"kind": "breast", "label": "Chicken|Breasts"}, 132, 148),
    ("black_tray", {"kind": "dice", "count": 1.15,
                    "sticker": ("FRY", "SAUTÉ")}, 132, 104),
    ("black_tray", {"kind": "tender", "count": 10}, 110, 140),
    ("whole_bird", {"band": "green"}, 120, 152),
]

RAW = []


def capture(fn, x, w, shelf, h=146, back=False, tilt=None, **kw):
    RAW.append({"fn": fn.__name__, "kw": kw, "shelf": shelf, "back": bool(back),
                "x": round(x, 1), "w": round(w, 1), "h": round(h, 1)})


def key_of(slot):
    return slot["fn"] + "|" + json.dumps(slot["kw"], sort_keys=True, default=str)


def cat_id(slot):
    return hashlib.md5(key_of(slot).encode()).hexdigest()[:7]


def name_of(slot):
    fn, kw = slot["fn"], slot["kw"]
    base = NAMES.get((fn, kw.get("kind")), NAMES.get((fn, None), fn))
    bits = []
    if kw.get("label"):
        base = "SS " + kw["label"].replace("|", " ")
    if kw.get("name"):
        base = "SS " + kw["name"].replace("|", " ")
    if kw.get("band") == "blue":
        base = "O Organics whole young chicken"
    elif kw.get("band") == "green":
        base = "SS Whole Young Chicken"
    elif kw.get("band") == "plain":
        base = "Whole chicken, over-wrapped"
    if kw.get("red_label"):
        bits.append("red label")
    if kw.get("sf_tag"):
        bits.append("SS breast tag")
    st = kw.get("sticker")
    if st:
        bits.append(" ".join(t for t in st[:2] if t).title())
    if kw.get("sticker2"):
        bits.append(kw["sticker2"][0].title())
    return base + (" · " + ", ".join(bits) if bits else "")


def short_of(name):
    base = name.split(" · ")[0]
    for a, b in SHORT:
        base = base.replace(a, b)
    return base


# --------------------------------------------------------------- the grid ---
def tracks_of():
    """One track per shelf and bay, inferred from what the layout placed."""
    bays = [("A", B.AX0, B.AX1), ("B", B.BX0, B.BX1), ("C", B.CX0, B.CX1)]
    posts = [(B.AX1 + 4, B.AX1 + 20), (B.BX1 + 4, B.BX1 + 20)]
    out = []
    for sh in range(5):
        for code, x0, x1 in bays:
            here = [s for s in RAW if s["shelf"] == sh and x0 - 16 <= s["x"] < x1]
            front = sorted([s for s in here if not s["back"]], key=lambda d: d["x"])
            back = sorted([s for s in here if s["back"]], key=lambda d: d["x"])

            # bare runs wide enough to hold a pack become empty cells,
            # measured only within this bay
            lo, hi = x0 - 16, x1
            occ = sorted((max(lo, a), min(hi, b)) for a, b in
                         [(s["x"], s["x"] + s["w"]) for s in front] + posts
                         if b > lo and a < hi)
            cur, holes = lo, []
            for a, b in occ:
                if a - cur >= GAP_MIN:
                    holes.append({"x": cur + 5, "w": a - cur - 10, "h": 0,
                                  "cat": None})
                cur = max(cur, b)
            if hi - cur >= GAP_MIN:
                holes.append({"x": cur + 5, "w": hi - cur - 10, "h": 0,
                              "cat": None})

            cells = [{"x": f["x"], "w": f["w"], "h": f["h"], "cat": cat_id(f)}
                     for f in front] + holes
            cells.sort(key=lambda c: c["x"])
            for c in cells:
                c["deep"] = 1

            for b in back:
                hit = None
                for c in cells:
                    if b["x"] < c["x"] + c["w"] and b["x"] + b["w"] > c["x"]:
                        hit = c
                        break
                if hit is None:                       # a back pack on its own
                    cells.append({"x": b["x"], "w": b["w"], "h": b["h"],
                                  "cat": cat_id(b), "deep": 1})
                    cells.sort(key=lambda c: c["x"])
                elif hit["cat"] is None:              # bring it to the front
                    hit["cat"], hit["h"] = cat_id(b), b["h"]
                else:
                    hit["deep"] += 1

            hs = [c["h"] for c in cells if c["h"]]
            fill = max(hs) if hs else 146
            for col, c in enumerate(cells):
                out.append({"shelf": sh, "bay": code, "col": col, "units": 1.0,
                            "deep": c["deep"], "cat": c["cat"],
                            "h": round(c["h"] or fill, 1)})
    return out


def fit(art, cw, ch, cx, cb):
    """A pack keeps its proportions inside its cell, bottom-aligned."""
    if not art:
        return {"px": round(cx, 1), "py": round(cb, 1), "pw": 0, "ph": 0}
    k = min(1.0, cw / art["w"], ch / art["h"])
    w, h = art["w"] * k, art["h"] * k
    return {"px": round(cx + (cw - w) / 2, 1), "py": round(cb - h, 1),
            "pw": round(w, 1), "ph": round(h, 1)}


def place(cells, by_cat):
    """Give every cell its geometry, then expand it into drawable slots."""
    span = [("A", B.AX0, B.AX1), ("B", B.BX0, B.BX1), ("C", B.CX0, B.CX1)]
    slots = []
    for sh in range(5):
        for code, x0, x1 in span:
            track = sorted([c for c in cells if c["shelf"] == sh
                            and c["bay"] == code], key=lambda c: c["col"])
            if not track:
                continue
            total = sum(c["units"] for c in track) or 1
            avail = (x1 - x0) - GUTTER * (len(track) - 1)
            cursor = x0
            for c in track:
                w = avail * c["units"] / total
                c["x"], c["w"] = round(cursor, 1), round(w, 1)
                c["y"] = round(B.DECK[sh] - c["h"], 1)
                c["slots"] = []
                art = by_cat.get(c["cat"])
                for d in range(c["deep"] - 1, -1, -1):
                    cx = cursor + BACK_INSET * d
                    cw = w - BACK_INSET * 2 * d
                    cb = B.DECK[sh] - BACK_RISE * d
                    sl = {"cx": round(cx, 1), "cw": round(cw, 1),
                          "cy": round(cb - c["h"], 1), "ch": c["h"], "cell": 0}
                    sl.update(fit(art, cw, c["h"], cx, cb))
                    c["slots"].append(len(slots))
                    slots.append(sl)
                cursor += w + GUTTER
    for i, c in enumerate(cells):
        for s in c.get("slots", []):
            slots[s]["cell"] = i
    return slots


def build_section():
    del RAW[:]
    B.put = capture
    B.build()
    behind, trim = "".join(B.BODY).split("<!--trim-->")
    front = "".join(B.FRONT)

    cats, sizes = {}, {}
    for s in RAW:
        k = key_of(s)
        cats.setdefault(k, s)
        sizes.setdefault(k, {}).setdefault((s["w"], s["h"]), 0)
        sizes[k][(s["w"], s["h"])] += 1
    for fn, kw, w, h in EXTRAS:
        k = key_of({"fn": fn, "kw": kw})
        if k not in cats:
            cats[k] = {"fn": fn, "kw": kw}
            sizes[k] = {(w, h): 1}

    defs, catalog = [], []
    for k, s in cats.items():
        w, h = max(sizes[k].items(), key=lambda kv: kv[1])[0]
        gids = []
        for v in range(VARIANTS):
            B.R.seed(90210 + v * 7919 + (int(hashlib.md5(k.encode())
                                             .hexdigest()[:6], 16) & 0xffff))
            gid = "p%s_%d" % (hashlib.md5(k.encode()).hexdigest()[:7], v)
            defs.append('<g id="%s">%s</g>'
                        % (gid, getattr(B, s["fn"])(0, 0, w, h, **s["kw"])))
            gids.append(gid)
        nm = name_of(s)
        catalog.append({"id": hashlib.md5(k.encode()).hexdigest()[:7],
                        "name": nm, "short": short_of(nm),
                        "group": GROUPS.get(s["fn"], "Other"),
                        "gids": gids, "w": w, "h": h})
    catalog.sort(key=lambda c: (c["group"], c["name"]))

    by_cat = {c["id"]: c for c in catalog}
    cells = tracks_of()
    slots = place(cells, by_cat)

    bays = [{"code": "A", "label": "Signature Select", "x": B.AX0,
             "w": B.AX1 - B.AX0},
            {"code": "B", "label": "Organic & whole fryers", "x": B.BX0,
             "w": B.BX1 - B.BX0},
            {"code": "C", "label": "Value and Quality bulk", "x": B.CX0,
             "w": B.CX1 - B.CX0}]
    tags = [{"shelf": sh, "x": tx, "w": 166, "price": "$%s.%s/lb" % (d, c),
             "desc": desc} for sh, tx, desc, d, c in B.VALUE_TAGS]

    return {"cells": cells, "slots": slots, "catalog": catalog,
            "defs": "".join(defs), "behind": behind, "trim": trim,
            "front": front, "bays": bays, "tags": tags, "shelves": 5,
            "w": B.W, "h": B.H}


# ------------------------------------------------------------- the drawing --
def case_svg(sec, cls="case"):
    W, H = sec["w"], sec["h"]
    by_cat = {c["id"]: c for c in sec["catalog"]}
    cells = sec["cells"]
    p = ['<svg class="%s" xmlns="http://www.w3.org/2000/svg" '
         'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 %d %d" '
         'role="img" aria-label="Editable planogram grid of a fresh-poultry '
         'case">' % (cls, W, H)]
    p.append(B.rr(0, 0, W, H, 0, fill="#07080a"))
    p.append(B.rr(18, 10, W - 36, H - 22, 10, fill="url(#case)",
                  stroke="#54595e", stroke_width="3"))
    p.append(B.rr(26, 18, W - 52, H - 38, 6, fill="#0b0c0e"))
    for k in range(5):
        p.append(B.rr(34, B.BAND_TOP[k] - 10, 1692, 54, 0, fill="url(#lamp)"))
    p.append(sec["behind"])

    # the grid itself, hidden until the app turns it on
    p.append('<g class="gridlines">')
    for c in cells:
        p.append('<rect class="gcell" x="%.1f" y="%.1f" width="%.1f" '
                 'height="%.1f" rx="4"/>'
                 % (c["x"], B.BAND_TOP[c["shelf"]] + 6, c["w"],
                    B.DECK[c["shelf"]] - B.BAND_TOP[c["shelf"]] - 8))
    p.append("</g>")

    p.append('<g class="slots">')
    for i, sl in enumerate(sec["slots"]):
        c = cells[sl["cell"]]
        art = by_cat.get(c["cat"])
        p.append('<g class="slot%s" data-i="%d" data-cell="%d" tabindex="0" '
                 'role="button">' % ("" if art else " empty", i, sl["cell"]))
        if art:
            gid = art["gids"][sl["cell"] % VARIANTS]
            p.append('<use href="#%s" xlink:href="#%s" transform="translate(%.1f,'
                     '%.1f) scale(%.4f,%.4f)"/>'
                     % (gid, gid, sl["px"], sl["py"],
                        sl["pw"] / art["w"], sl["ph"] / art["h"]))
        else:
            p.append('<use transform="translate(%.1f,%.1f)"/>' % (sl["cx"], sl["cy"]))
        p.append('<rect class="hit" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'rx="5" fill="transparent"/>'
                 % (sl["cx"], sl["cy"], sl["cw"], sl["ch"]))
        p.append('<rect class="ring" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'rx="5"/>' % (sl["cx"], sl["cy"], sl["cw"], sl["ch"]))
        p.append("</g>")
    p.append("</g>")

    for px in (B.AX1 + 6, B.BX1 + 6):
        p.append(B.rr(px, 20, 12, H - 62, 2, fill="url(#post)"))
    p.append(sec["trim"])
    p.append(sec["front"])
    p.append(B.rr(26, B.DECK[4] + 32, W - 52, H - B.DECK[4] - 52, 3, fill="#0a0b0c"))
    for i in range(46):
        p.append(B.rr(34 + i * 36.5, B.DECK[4] + 40, 22, H - B.DECK[4] - 74, 1,
                      fill="#171a1c"))
    p.append(B.rr(0, 0, W, H, 0, fill="url(#vig)", pointer_events="none"))
    p.append(B.rr(26, 18, W - 52, H - 38, 6, fill="url(#glass)",
                  pointer_events="none"))
    p.append("</svg>")
    return "".join(p)


def sprite(sections):
    return ('<svg class="sprite" aria-hidden="true" focusable="false">%s'
            '<defs>%s</defs><defs>%s</defs></svg>'
            % (B.defs(), "".join(B.CLIPS),
               "".join(s["defs"] for s in sections)))
