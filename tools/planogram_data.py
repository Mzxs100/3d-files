#!/usr/bin/env python3
"""
Shared layout data for the planogram app.

Captures the case layout from build_chicken_case_svg without drawing the packs
inline, then draws each distinct package once into a reusable <g> so the app can
point any shelf spot at any product.

Adding a section later: give build_section() another (id, name, note, builder)
entry — the builder just needs to populate B.BODY / B.FRONT and call B.put() for
each facing, exactly as build() does today.
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_chicken_case_svg as B                                   # noqa: E402

VARIANTS = 2

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
# Add a tuple here and it shows up in the app ready to drop onto any spot.
EXTRAS = [
    ("sf_yellow", {"name": "Chicken|Wings", "kind": "wing"}, 148, 148),
    ("sf_green", {"kind": "breast", "label": "Chicken|Breasts"}, 132, 148),
    ("black_tray", {"kind": "dice", "count": 1.15,
                    "sticker": ("FRY", "SAUTÉ")}, 132, 104),
    ("black_tray", {"kind": "tender", "count": 10}, 110, 140),
    ("whole_bird", {"band": "green"}, 120, 152),
]

# A bare run of shelf at least this wide becomes an addressable empty spot,
# so anything you can see room for is something you can drop a pack into.
GAP_MIN = 100

SLOTS = []


def gap_slots(slots):
    """Empty, droppable spots for the bare runs between facings."""
    posts = [(B.AX1 + 4, B.AX1 + 20), (B.BX1 + 4, B.BX1 + 20)]
    out = []
    for sh in range(5):
        front = sorted([s for s in slots if s["shelf"] == sh and not s["back"]],
                       key=lambda d: d["x"])
        if not front:
            continue
        hs = sorted(s["h"] for s in front)
        h = hs[len(hs) // 2]
        occ = sorted([(s["x"], s["x"] + s["w"]) for s in front] + posts)
        free, cur = [], 34
        for a, b in occ:
            if a - cur > 1:
                free.append((cur, a))
            cur = max(cur, b)
        if 1726 - cur > 1:
            free.append((cur, 1726))
        for a, b in free:
            if b - a < GAP_MIN:
                continue
            out.append({"shelf": sh, "back": False, "x": round(a + 5, 1),
                        "y": round(B.DECK[sh] - h, 1), "w": round(b - a - 10, 1),
                        "h": round(h, 1), "tilt": 0, "cat": None})
    return out


def capture(fn, x, w, shelf, h=146, back=False, tilt=None, **kw):
    y = B.DECK[shelf] - h - (46 if back else 0)
    SLOTS.append({
        "fn": fn.__name__, "kw": kw, "shelf": shelf, "back": bool(back),
        "x": round(x, 1), "y": round(y, 1), "w": round(w, 1), "h": round(h, 1),
        "tilt": round(B.R.uniform(-1.1, 1.1) if tilt is None else tilt, 2),
    })


def key_of(slot):
    return slot["fn"] + "|" + json.dumps(slot["kw"], sort_keys=True, default=str)


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


def build_section():
    """Run the case builder, returning slots, chrome and the product catalogue."""
    del SLOTS[:]
    B.put = capture
    B.build()
    behind, trim = "".join(B.BODY).split("<!--trim-->")
    front = "".join(B.FRONT)

    cats, sizes = {}, {}
    for sl in SLOTS:
        k = key_of(sl)
        cats.setdefault(k, sl)
        sizes.setdefault(k, {}).setdefault((sl["w"], sl["h"]), 0)
        sizes[k][(sl["w"], sl["h"])] += 1

    for fn, kw, w, h in EXTRAS:
        sl = {"fn": fn, "kw": kw}
        k = key_of(sl)
        if k in cats:
            continue
        cats[k] = sl
        sizes[k] = {(w, h): 1}

    defs, catalog = [], []
    for k, sl in cats.items():
        w, h = max(sizes[k].items(), key=lambda kv: kv[1])[0]
        gids = []
        for v in range(VARIANTS):
            B.R.seed(90210 + v * 7919 + (int(hashlib.md5(k.encode())
                                             .hexdigest()[:6], 16) & 0xffff))
            gid = "p%s_%d" % (hashlib.md5(k.encode()).hexdigest()[:7], v)
            defs.append('<g id="%s">%s</g>'
                        % (gid, getattr(B, sl["fn"])(0, 0, w, h, **sl["kw"])))
            gids.append(gid)
        nm = name_of(sl)
        catalog.append({"id": hashlib.md5(k.encode()).hexdigest()[:7],
                        "name": nm, "short": short_of(nm),
                        "group": GROUPS.get(sl["fn"], "Other"),
                        "gids": gids, "w": w, "h": h})
    catalog.sort(key=lambda c: (c["group"], c["name"]))

    slots = []
    for sl in SLOTS:
        slots.append({"shelf": sl["shelf"], "back": sl["back"], "x": sl["x"],
                      "y": sl["y"], "w": sl["w"], "h": sl["h"],
                      "tilt": sl["tilt"],
                      "cat": hashlib.md5(key_of(sl).encode()).hexdigest()[:7]})
    slots.extend(gap_slots(slots))

    bays = [{"code": "A", "label": "Signature Select",
             "limit": B.AX1 + 12, "grow": B.AX1 - B.AX0},
            {"code": "B", "label": "Organic & whole fryers",
             "limit": B.BX1 + 12, "grow": B.BX1 - B.BX0},
            {"code": "C", "label": "Value and Quality bulk",
             "limit": 10 ** 9, "grow": B.CX1 - B.CX0}]
    tags = [{"shelf": sh, "x": tx, "w": 166, "price": "$%s.%s/lb" % (d, c),
             "desc": desc} for sh, tx, desc, d, c in B.VALUE_TAGS]

    return {"slots": slots, "catalog": catalog, "defs": "".join(defs),
            "behind": behind, "trim": trim, "front": front,
            "bays": bays, "tags": tags, "shelves": 5,
            "w": B.W, "h": B.H}


def case_svg(sec, cls="case"):
    """The section's SVG: chrome plus one <use> instance per shelf spot."""
    W, H = sec["w"], sec["h"]
    by_cat = {c["id"]: c for c in sec["catalog"]}
    p = ['<svg class="%s" xmlns="http://www.w3.org/2000/svg" '
         'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 %d %d" '
         'role="img" aria-label="Editable planogram of a fresh-poultry case">'
         % (cls, W, H)]
    p.append(B.rr(0, 0, W, H, 0, fill="#07080a"))
    p.append(B.rr(18, 10, W - 36, H - 22, 10, fill="url(#case)",
                  stroke="#54595e", stroke_width="3"))
    p.append(B.rr(26, 18, W - 52, H - 38, 6, fill="#0b0c0e"))
    for k in range(5):
        p.append(B.rr(34, B.BAND_TOP[k] - 10, 1692, 54, 0, fill="url(#lamp)"))
    p.append(sec["behind"])
    p.append('<g class="slots">')
    for i, sl in enumerate(sec["slots"]):
        c = by_cat.get(sl["cat"])
        cx, cy = sl["x"] + sl["w"] / 2, sl["y"] + sl["h"] / 2
        p.append('<g class="slot%s" data-i="%d" tabindex="0" role="button" '
                 'transform="rotate(%.2f %.1f %.1f)">'
                 % ("" if c else " empty", i, sl["tilt"], cx, cy))
        if c:
            gid = c["gids"][i % VARIANTS]
            p.append('<use href="#%s" xlink:href="#%s" transform="translate(%.1f,'
                     '%.1f) scale(%.4f,%.4f)"/>'
                     % (gid, gid, sl["x"], sl["y"],
                        sl["w"] / c["w"], sl["h"] / c["h"]))
        else:
            p.append('<use transform="translate(%.1f,%.1f)"/>'
                     % (sl["x"], sl["y"]))
        p.append('<rect class="hit" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'rx="5" fill="transparent"/>'
                 % (sl["x"], sl["y"], sl["w"], sl["h"]))
        p.append('<rect class="ring" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'rx="5"/>' % (sl["x"], sl["y"], sl["w"], sl["h"]))
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
    """One hidden SVG holding the gradients, clip paths and every product."""
    return ('<svg class="sprite" aria-hidden="true" focusable="false">%s'
            '<defs>%s</defs><defs>%s</defs></svg>'
            % (B.defs(), "".join(B.CLIPS),
               "".join(s["defs"] for s in sections)))
