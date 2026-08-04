#!/usr/bin/env python3
"""
Build the planogram app — one page holding every section, the item bar and the
printable reset map.

    python3 tools/build_app.py     ->  planogram-app.html

Sections are data. Today there is one; add another by appending to SECTIONS with
its own layout builder, and the tabs, item bar and map all pick it up.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import planogram_data as D                                          # noqa: E402

SECTIONS = [
    {"id": "poultry", "name": "Fresh Poultry",
     "note": "5 shelves · 3 bays · reach-in case"},
]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    built, markup, catalog = [], [], {}
    for meta in SECTIONS:
        sec = D.build_section()
        sec.update(meta)
        built.append(sec)
        markup.append('<div class="section" data-sec="%s" hidden>%s</div>'
                      % (meta["id"], D.case_svg(sec)))
        for c in sec["catalog"]:
            catalog[c["id"]] = c

    data = {
        "catalog": sorted(catalog.values(), key=lambda c: (c["group"], c["name"])),
        "variants": D.VARIANTS,
        "sections": [{"id": s["id"], "name": s["name"], "note": s["note"],
                      "slots": s["slots"], "bays": s["bays"], "tags": s["tags"],
                      "shelves": s["shelves"], "w": s["w"], "h": s["h"]}
                     for s in built],
    }

    tabs = "".join(
        '<button class="tab" data-sec="%s"><b>%s</b><span>%s</span></button>'
        % (s["id"], s["name"], s["note"]) for s in built)

    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "app_template.html")).read()
    html = (tpl.replace("__SPRITE__", D.sprite(built))
               .replace("__SECTIONS__", "".join(markup))
               .replace("__TABS__", tabs)
               .replace("__DATA__", json.dumps(data, separators=(",", ":"))))

    out = os.path.join(root, "planogram-app.html")
    with open(out, "w") as f:
        f.write(html)
    print("wrote planogram-app.html  (%d section(s), %d spots, %d items, %d KB)"
          % (len(built), sum(len(s["slots"]) for s in built),
             len(data["catalog"]), len(html) / 1024))


if __name__ == "__main__":
    main()
