#!/usr/bin/env python3
"""
Build an interactive planogram editor from the case drawing.

Reuses build_chicken_case_svg.py: every distinct package in the layout is drawn
once into a reusable <g> (two random variants each so neighbouring facings do
not look cloned), and each shelf spot becomes a <use> instance that the page can
re-point at any other product.

Output: planogram-editor.html  (self-contained, no network needed)
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_chicken_case_svg as B                                   # noqa: E402

VARIANTS = 2

# --------------------------------------------------------------- capture ----
SLOTS = []


def capture(fn, x, w, shelf, h=146, back=False, tilt=None, **kw):
    y = B.DECK[shelf] - h - (46 if back else 0)
    SLOTS.append({
        "fn": fn.__name__, "kw": kw, "shelf": shelf, "back": bool(back),
        "x": round(x, 1), "y": round(y, 1), "w": round(w, 1), "h": round(h, 1),
        "tilt": round(B.R.uniform(-1.1, 1.1) if tilt is None else tilt, 2),
    })


def key_of(slot):
    return slot["fn"] + "|" + json.dumps(slot["kw"], sort_keys=True, default=str)


def gid_of(key, v):
    return "p%s_%d" % (hashlib.md5(key.encode()).hexdigest()[:7], v)


# ------------------------------------------------------------- catalogue ----
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
    if kw.get("price") is False:
        bits.append("no price tag")
    return base + (" · " + ", ".join(bits) if bits else "")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    B.put = capture
    B.build()

    behind, trim = "".join(B.BODY).split("<!--trim-->")
    front = "".join(B.FRONT)

    # one catalogue entry per distinct package, nominal size = its commonest size
    cats, sizes = {}, {}
    for sl in SLOTS:
        k = key_of(sl)
        cats.setdefault(k, sl)
        sizes.setdefault(k, {}).setdefault((sl["w"], sl["h"]), 0)
        sizes[k][(sl["w"], sl["h"])] += 1

    defs_products = []
    catalog = []
    for k, sl in cats.items():
        w, h = max(sizes[k].items(), key=lambda kv: kv[1])[0]
        gids = []
        for v in range(VARIANTS):
            B.R.seed(90210 + v * 7919 + (hash(k) & 0xffff))
            art = getattr(B, sl["fn"])(0, 0, w, h, **sl["kw"])
            gid = gid_of(k, v)
            defs_products.append('<g id="%s">%s</g>' % (gid, art))
            gids.append(gid)
        catalog.append({
            "id": hashlib.md5(k.encode()).hexdigest()[:7],
            "name": name_of(sl), "group": GROUPS.get(sl["fn"], "Other"),
            "gids": gids, "w": w, "h": h,
        })
    catalog.sort(key=lambda c: (c["group"], c["name"]))

    for sl in SLOTS:
        sl["cat"] = hashlib.md5(key_of(sl).encode()).hexdigest()[:7]
        del sl["fn"], sl["kw"]

    # ------------------------------------------------------------- scene ---
    W, H = B.W, B.H
    svg = ['<svg id="case" xmlns="http://www.w3.org/2000/svg" '
           'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 %d %d" '
           'role="img" aria-label="Editable planogram of a fresh-poultry case">'
           % (W, H)]
    svg.append("<title>Fresh Poultry Case — editable planogram</title>")
    svg.append(B.defs())
    svg.append("<defs>%s</defs>" % "".join(defs_products))
    svg.append("<!--CLIPS-->")
    svg.append(B.rr(0, 0, W, H, 0, fill="#07080a"))
    svg.append(B.rr(18, 10, W - 36, H - 22, 10, fill="url(#case)",
                    stroke="#54595e", stroke_width="3"))
    svg.append(B.rr(26, 18, W - 52, H - 38, 6, fill="#0b0c0e"))
    for k in range(5):
        svg.append(B.rr(34, B.BAND_TOP[k] - 10, 1692, 54, 0, fill="url(#lamp)"))
    svg.append(behind)

    svg.append('<g id="slots">')
    by_cat = {c["id"]: c for c in catalog}
    for i, sl in enumerate(SLOTS):
        c = by_cat[sl["cat"]]
        gid = c["gids"][i % VARIANTS]
        cx, cy = sl["x"] + sl["w"] / 2, sl["y"] + sl["h"] / 2
        svg.append('<g class="slot" data-i="%d" transform="rotate(%.2f %.1f %.1f)">'
                   % (i, sl["tilt"], cx, cy))
        svg.append('<use href="#%s" xlink:href="#%s" transform="translate(%.1f,%.1f) '
                   'scale(%.4f,%.4f)"/>' % (gid, gid, sl["x"], sl["y"],
                                            sl["w"] / c["w"], sl["h"] / c["h"]))
        svg.append('<rect class="hit" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                   'rx="5" fill="transparent"/>' % (sl["x"], sl["y"], sl["w"], sl["h"]))
        svg.append('<rect class="ring" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                   'rx="5"/>' % (sl["x"], sl["y"], sl["w"], sl["h"]))
        svg.append("</g>")
    svg.append("</g>")

    for px in (B.AX1 + 6, B.BX1 + 6):
        svg.append(B.rr(px, 20, 12, H - 62, 2, fill="url(#post)"))
    svg.append(trim)
    svg.append(front)
    svg.append(B.rr(26, B.DECK[4] + 32, W - 52, H - B.DECK[4] - 52, 3, fill="#0a0b0c"))
    for i in range(46):
        svg.append(B.rr(34 + i * 36.5, B.DECK[4] + 40, 22, H - B.DECK[4] - 74, 1,
                        fill="#171a1c"))
    svg.append(B.rr(0, 0, W, H, 0, fill="url(#vig)", pointer_events="none"))
    svg.append(B.rr(26, 18, W - 52, H - 38, 6, fill="url(#glass)",
                    pointer_events="none"))
    svg.append("</svg>")
    svg = "".join(svg).replace("<!--CLIPS-->",
                               "<defs>%s</defs>" % "".join(B.CLIPS))

    bays = [("Left bay — Signature Select", B.AX1 + 12),
            ("Centre bay — organic & whole fryers", B.BX1 + 12),
            ("Right bay — Value and Quality bulk", W)]
    data = {"slots": SLOTS, "catalog": catalog,
            "bays": [{"name": n, "x": x} for n, x in bays]}

    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "editor_template.html")).read()
    html = tpl.replace("__SVG__", svg).replace(
        "__DATA__", json.dumps(data, separators=(",", ":")))
    out = os.path.join(root, "planogram-editor.html")
    with open(out, "w") as f:
        f.write(html)
    print("wrote planogram-editor.html  (%d slots, %d products, %d KB)"
          % (len(SLOTS), len(catalog), len(html) / 1024))

if __name__ == "__main__":
    main()
