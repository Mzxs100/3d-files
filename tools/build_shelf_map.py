#!/usr/bin/env python3
"""
Build a printable shelf map (planogram reset guide) from the case layout.

Black-on-white, landscape, no shelf-strip chrome — just a grid of numbered
positions with a drawing of the pack that belongs in each one:

  page 1      whole case at a glance, every position coded  (tape inside the door)
  pages 2-6   one page per shelf, large enough to work from
  last page   product key with the facing count for each item

Output: shelf-map.html
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_chicken_case_svg as B                                   # noqa: E402
import build_planogram_editor as E                                   # noqa: E402

BAYS = [("A", "Signature Select", B.AX1 + 12, B.AX1 - B.AX0),
        ("B", "Organic & whole fryers", B.BX1 + 12, B.BX1 - B.BX0),
        ("C", "Value and Quality bulk", 10 ** 9, B.CX1 - B.CX0)]

SHORT = [
    ("Signature Select", "SS"), ("Boneless skinless", "B/S"),
    ("boneless skinless", "b/s"), (" value pack", " value pk"),
]


def bay_of(x):
    for code, _, lim, _w in BAYS:
        if x < lim:
            return code
    return "C"


def short_name(name):
    base = name.split(" · ")[0]
    for a, b in SHORT:
        base = base.replace(a, b)
    return base


def tags_for(shelf, x0, x1):
    """Value tags whose ticket overlaps this span of shelf."""
    out = []
    for sh, tx, desc, d, c in B.VALUE_TAGS:
        if sh == shelf and tx < x1 and tx + 166 > x0:
            out.append(("$%s.%s/lb" % (d, c), desc))
    return out


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    B.put = E.capture
    B.build()
    slots = E.SLOTS

    # ---------------------------------------------------- product catalogue
    cats, sizes = {}, {}
    for sl in slots:
        k = E.key_of(sl)
        cats.setdefault(k, sl)
        sizes.setdefault(k, {}).setdefault((sl["w"], sl["h"]), 0)
        sizes[k][(sl["w"], sl["h"])] += 1

    sprite, cat = [], {}
    for i, (k, sl) in enumerate(cats.items()):
        w, h = max(sizes[k].items(), key=lambda kv: kv[1])[0]
        B.R.seed(4242 + i)
        gid = "t%d" % i
        sprite.append('<g id="%s">%s</g>' % (
            gid, getattr(B, sl["fn"])(0, 0, w, h, **sl["kw"])))
        nm = E.name_of(sl).replace(" · no price tag", "")
        cat[k] = {"gid": gid, "w": w, "h": h, "name": nm,
                  "short": short_name(nm),
                  "group": E.GROUPS.get(sl["fn"], "Other"), "n": 0}

    for sl in slots:
        sl["key"] = E.key_of(sl)
        cat[sl["key"]]["n"] += 1

    # ------------------------------------------------------------ positions
    shelves = []
    for s in range(5):
        mine = [sl for sl in slots if sl["shelf"] == s]
        front = sorted([sl for sl in mine if not sl["back"]], key=lambda d: d["x"])
        back = sorted([sl for sl in mine if sl["back"]], key=lambda d: d["x"])
        per_bay = {}
        for sl in front:
            per_bay.setdefault(bay_of(sl["x"]), []).append(sl)
        bays = []
        for code, label, _, gw in BAYS:
            items = per_bay.get(code, [])
            positions = []
            for n, sl in enumerate(items, 1):
                behind = [b for b in back
                          if b["x"] < sl["x"] + sl["w"] and b["x"] + b["w"] > sl["x"]]
                positions.append({
                    "code": "%d-%s%d" % (s + 1, code, n),
                    "key": sl["key"],
                    "tags": tags_for(s, sl["x"], sl["x"] + sl["w"]),
                    "deep": 1 + len(behind),
                    "behind": [b["key"] for b in behind
                               if b["key"] != sl["key"]],
                })
            span = (items[0]["x"], items[-1]["x"] + items[-1]["w"]) if items else (0, 0)
            bays.append({"code": code, "label": label, "positions": positions,
                         "grow": gw, "tags": tags_for(s, *span)})
        shelves.append(bays)

    # ----------------------------------------------------------------- html
    def thumb(key, cls="th"):
        c = cat[key]
        return ('<svg class="%s" viewBox="0 0 %.0f %.0f" aria-hidden="true">'
                '<use href="#%s"/></svg>' % (cls, c["w"] + 8, c["h"] + 16, c["gid"]))

    def cell(pos, big=False):
        c = cat[pos["key"]]
        h = ['<div class="cell">']
        h.append('<div class="code">%s%s</div>' % (
            pos["code"],
            "".join('<span class="tag">%s</span>' % t[0] for t in pos["tags"])))
        h.append(thumb(pos["key"], "th big" if big else "th"))
        h.append('<div class="nm">%s</div>' % esc(c["name" if big else "short"]))
        meta = []
        if pos["deep"] > 1:
            meta.append("%d deep" % pos["deep"])
        if meta:
            h.append('<div class="meta">%s</div>' % " · ".join(meta))
        for k in pos["behind"]:
            h.append('<div class="meta behind">also here: %s</div>'
                     % esc(cat[k]["short"]))
        h.append("</div>")
        return "".join(h)

    P = []
    # ---- page 1: the whole case
    P.append('<section class="page">')
    P.append('<div class="ph"><div><h1>Fresh Poultry Case — Shelf Map</h1>'
             '<p class="sub">Reset guide · %d facings · 5 shelves · 3 bays. '
             'Shelf 1 is the top shelf; positions run left to right.</p></div>'
             '<div class="sign">Reviewed <span></span></div></div>' % len(slots))
    P.append('<div class="grid">')
    P.append('<div class="bayhead"><div class="gut"></div>')
    for code, label, _, gw in BAYS:
        P.append('<div class="bh" style="flex-grow:%d">Bay %s — %s</div>'
                 % (gw, code, label))
    P.append("</div>")
    for s, bays in enumerate(shelves):
        P.append('<div class="shelfrow">')
        P.append('<div class="gut"><b>%d</b><span>SHELF</span></div>' % (s + 1))
        for b in bays:
            P.append('<div class="bay" style="flex-grow:%d">' % b["grow"])
            P.append('<div class="cells">%s</div>'
                     % "".join(cell(p) for p in b["positions"]))
            P.append("</div>")
        P.append("</div>")
    P.append("</div>")
    P.append('<p class="foot">Face every label to the front. Rotate stock front '
             'to back — oldest dates forward. Leave the empty spots empty unless '
             'told otherwise.</p>')
    P.append("</section>")

    # ---- pages 2-6: one shelf each
    for s, bays in enumerate(shelves):
        P.append('<section class="page detail">')
        P.append('<div class="ph"><div><h1>Shelf %d <span class="of">of 5</span></h1>'
                 '<p class="sub">%s</p></div>'
                 '<div class="sign">Reviewed <span></span></div></div>'
                 % (s + 1, ["Top shelf", "Second shelf", "Middle shelf",
                            "Fourth shelf", "Bottom shelf"][s]))
        for b in bays:
            if not b["positions"]:
                continue
            P.append('<div class="dbay">')
            P.append('<div class="dbh"><b>Bay %s</b> %s%s</div>' % (
                b["code"], b["label"],
                "".join(' <span class="tag">%s %s</span>' % (t[0], esc(t[1]))
                        for t in b["tags"])))
            P.append('<div class="cells wide">%s</div>'
                     % "".join(cell(p, big=True) for p in b["positions"]))
            P.append("</div>")
        P.append("</section>")

    # ---- last page: product key
    P.append('<section class="page">')
    P.append('<div class="ph"><div><h1>Product Key</h1>'
             '<p class="sub">Every item in the case and how many facings it '
             'holds.</p></div></div>')
    P.append('<table class="key"><thead><tr><th></th><th>Product</th>'
             '<th>Group</th><th class="r">Facings</th></tr></thead><tbody>')
    merged = {}
    for c in cat.values():
        m = merged.setdefault(c["name"], dict(c, n=0))
        m["n"] += c["n"]
    for c in sorted(merged.values(), key=lambda c: (c["group"], c["name"])):
        P.append('<tr><td class="tc">%s</td><td>%s</td><td class="g">%s</td>'
                 '<td class="r num">%d</td></tr>' % (
                     '<svg class="th key" viewBox="0 0 %.0f %.0f"><use href="#%s"/>'
                     '</svg>' % (c["w"] + 8, c["h"] + 16, c["gid"]),
                     esc(c["name"]), esc(c["group"]), c["n"]))
    P.append("</tbody></table></section>")

    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "shelf_map_template.html")).read()
    html = (tpl.replace("__SPRITE__", "".join(sprite))
               .replace("__DEFS__", B.defs() + "<defs>%s</defs>" % "".join(B.CLIPS))
               .replace("__PAGES__", "".join(P)))
    out = os.path.join(root, "shelf-map.html")
    with open(out, "w") as f:
        f.write(html)
    print("wrote shelf-map.html  (%d positions, %d products, %d KB)"
          % (sum(len(b["positions"]) for sh in shelves for b in sh),
             len(cat), len(html) / 1024))


if __name__ == "__main__":
    main()
