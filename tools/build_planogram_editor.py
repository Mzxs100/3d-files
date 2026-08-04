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

    html = TEMPLATE.replace("__SVG__", svg).replace(
        "__DATA__", json.dumps(data, separators=(",", ":")))
    out = os.path.join(root, "planogram-editor.html")
    with open(out, "w") as f:
        f.write(html)
    print("wrote planogram-editor.html  (%d slots, %d products, %d KB)"
          % (len(SLOTS), len(catalog), len(html) / 1024))


TEMPLATE = r"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fresh Poultry Case — Planogram Editor</title>
<style>
:root{
  --bg:#f2f2f0; --panel:#ffffff; --ink:#16181a; --muted:#6b7076; --line:#dcdcd8;
  --accent:#2f6df6; --accent-soft:#e6eeff; --warn:#c9541f;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#121315; --panel:#1c1e21; --ink:#e9eaec; --muted:#9aa0a6;
         --line:#2e3236; --accent:#6ea0ff; --accent-soft:#1d2942; }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:15px/1.5 "Helvetica Neue",Helvetica,Arial,sans-serif}
header{padding:16px 20px 12px;border-bottom:1px solid var(--line);
       display:flex;flex-wrap:wrap;gap:12px;align-items:center}
h1{font-size:1.05rem;margin:0;letter-spacing:-.01em;white-space:nowrap}
.sub{color:var(--muted);font-size:.82rem;margin:0;flex:1 1 260px;min-width:200px}
.tools{display:flex;gap:8px;flex-wrap:wrap}
button{font:inherit;font-size:.82rem;padding:6px 11px;border-radius:7px;
       border:1px solid var(--line);background:var(--panel);color:var(--ink);
       cursor:pointer}
button:hover{border-color:var(--accent)}
button.on{background:var(--accent);border-color:var(--accent);color:#fff}
button:disabled{opacity:.45;cursor:default}
main{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:18px;
     padding:18px 20px 40px;align-items:start}
@media (max-width:1080px){main{grid-template-columns:1fr}}
.stage{background:var(--panel);border:1px solid var(--line);border-radius:12px;
       padding:10px;overflow:auto}
svg#case{width:100%;height:auto;min-width:760px;display:block;border-radius:8px}
.slot{cursor:pointer}
.slot .ring{fill:none;stroke:none;stroke-width:3}
.slot:hover .ring{stroke:var(--accent);stroke-opacity:.75;stroke-dasharray:6 4}
.slot.sel .ring{stroke:#ffd400;stroke-opacity:1;stroke-width:4}
.slot.swap .ring{stroke:#ff8a3d;stroke-opacity:1;stroke-width:4}
.slot.changed .ring{stroke:#4ad07a;stroke-opacity:.9;stroke-width:2.5}
.slot.changed.sel .ring{stroke:#ffd400}
.slot.empty use{display:none}
.slot.empty .ring{stroke:var(--muted);stroke-opacity:.6;stroke-dasharray:5 5}
aside{position:sticky;top:14px;display:flex;flex-direction:column;gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
      padding:14px}
.card h2{font-size:.74rem;text-transform:uppercase;letter-spacing:.09em;
         color:var(--muted);margin:0 0 9px}
.now{font-weight:600;font-size:.95rem;margin:0 0 3px}
.where{color:var(--muted);font-size:.8rem;margin:0}
.hint{color:var(--muted);font-size:.8rem;margin:6px 0 0}
input[type=search]{width:100%;padding:7px 9px;border:1px solid var(--line);
  border-radius:7px;background:transparent;color:var(--ink);font:inherit;
  font-size:.85rem;margin-bottom:9px}
.palette{max-height:46vh;overflow:auto;margin:0 -4px;padding:0 4px}
.grp{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;
     color:var(--muted);margin:10px 0 5px}
.opt{display:flex;gap:9px;align-items:center;width:100%;text-align:left;
     padding:5px 7px;border:1px solid transparent;border-radius:8px;
     background:none;cursor:pointer;font-size:.84rem}
.opt:hover{background:var(--accent-soft);border-color:transparent}
.opt.cur{border-color:var(--accent);background:var(--accent-soft)}
.opt svg{flex:none;width:38px;height:40px;border-radius:4px;background:#0d0e10}
.opt span{min-width:0}
.row{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}
.count{font-variant-numeric:tabular-nums;text-transform:none;
       letter-spacing:0;color:#4ad07a}
kbd{font:inherit;font-size:.75rem;border:1px solid var(--line);border-radius:4px;
    padding:0 4px;background:var(--bg)}
footer{padding:0 20px 40px;color:var(--muted);font-size:.78rem;max-width:70ch}
</style>

<header>
  <h1>Planogram Editor</h1>
  <p class="sub">Click any facing, then pick what actually belongs there.
     Changes are saved in this browser.</p>
  <div class="tools">
    <button id="swapBtn" title="Swap two facings">Swap two</button>
    <button id="undoBtn" disabled>Undo</button>
    <button id="resetBtn">Reset all</button>
    <button id="jsonBtn">Export JSON</button>
    <button id="svgBtn">Download SVG</button>
  </div>
</header>

<main>
  <div class="stage">__SVG__</div>
  <aside>
    <div class="card">
      <h2>Selected facing</h2>
      <p class="now" id="curName">Nothing selected</p>
      <p class="where" id="curWhere">Click a pack in the case.</p>
      <div class="row">
        <button id="emptyBtn" disabled>Empty this spot</button>
        <button id="revertBtn" disabled>Revert spot</button>
      </div>
      <p class="hint"><kbd>Esc</kbd> deselect · <kbd>Del</kbd> empty ·
         <kbd>←</kbd><kbd>→</kbd> move along the shelf</p>
    </div>
    <div class="card">
      <h2>Products <span class="count" id="chg"></span></h2>
      <input type="search" id="find" placeholder="Filter products…">
      <div class="palette" id="palette"></div>
    </div>
  </aside>
</main>

<footer>
  Generated by <code>tools/build_planogram_editor.py</code>. Every facing is an
  instance of a drawn package, so swapping one re-renders it at the shelf's own
  size. “Download SVG” writes the corrected case as a clean standalone file with
  the editor chrome stripped out.
</footer>

<script>
const DATA = __DATA__;
const CASE = document.getElementById('case');
const slots = DATA.slots, catalog = DATA.catalog;
const byCat = {}; catalog.forEach(c => byCat[c.id] = c);
const ORIGINAL = slots.map(s => s.cat);
const KEY = 'poultry-planogram-v1';
const VARIANTS = catalog[0].gids.length;

let sel = null, swapFrom = null, swapMode = false;
const undo = [];

/* ---------------------------------------------------------------- render */
function el(i){ return CASE.querySelector('.slot[data-i="' + i + '"]'); }

function paint(i){
  const s = slots[i], g = el(i), u = g.querySelector('use');
  g.classList.toggle('empty', !s.cat);
  g.classList.toggle('changed', s.cat !== ORIGINAL[i]);
  if (!s.cat) return;
  const c = byCat[s.cat], gid = c.gids[i % VARIANTS];
  u.setAttribute('href', '#' + gid);
  u.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', '#' + gid);
  u.setAttribute('transform', 'translate(' + s.x + ',' + s.y + ') scale(' +
                 (s.w / c.w).toFixed(4) + ',' + (s.h / c.h).toFixed(4) + ')');
}

function bayOf(x){
  for (const b of DATA.bays) if (x < b.x) return b.name;
  return DATA.bays[DATA.bays.length - 1].name;
}

function refresh(){
  const n = slots.filter((s, i) => s.cat !== ORIGINAL[i]).length;
  document.getElementById('chg').textContent = n ? '· ' + n + ' changed' : '';
  document.getElementById('undoBtn').disabled = !undo.length;
  const s = sel === null ? null : slots[sel];
  document.getElementById('curName').textContent =
    s ? (s.cat ? byCat[s.cat].name : 'Empty spot') : 'Nothing selected';
  document.getElementById('curWhere').textContent = s
    ? 'Shelf ' + (s.shelf + 1) + ' of 5 · ' + bayOf(s.x) +
      (s.back ? ' · back row' : ' · front row')
    : 'Click a pack in the case.';
  document.getElementById('emptyBtn').disabled = sel === null;
  document.getElementById('revertBtn').disabled =
    sel === null || slots[sel].cat === ORIGINAL[sel];
  document.querySelectorAll('.opt').forEach(o =>
    o.classList.toggle('cur', s && o.dataset.cat === s.cat));
  save();
}

/* ----------------------------------------------------------------- edits */
function setCat(i, cat){
  if (slots[i].cat === cat) return;
  undo.push({ i: i, cat: slots[i].cat });
  slots[i].cat = cat;
  paint(i);
  refresh();
}

function swap(a, b){
  undo.push({ pair: [a, b], ca: slots[a].cat, cb: slots[b].cat });
  const t = slots[a].cat; slots[a].cat = slots[b].cat; slots[b].cat = t;
  paint(a); paint(b); refresh();
}

function select(i){
  if (sel !== null) el(sel).classList.remove('sel');
  sel = i;
  if (i !== null){
    el(i).classList.add('sel');
  }
  refresh();
}

/* ------------------------------------------------------------ persistence */
function save(){
  try { localStorage.setItem(KEY, JSON.stringify(slots.map(s => s.cat))); }
  catch (e) {}
}
function load(){
  try {
    const v = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (Array.isArray(v) && v.length === slots.length)
      v.forEach((c, i) => { slots[i].cat = c; });
  } catch (e) {}
}

/* ---------------------------------------------------------------- palette */
function thumb(c){
  return '<svg viewBox="0 0 ' + (c.w + 10) + ' ' + (c.h + 14) +
         '" aria-hidden="true"><use href="#' + c.gids[0] + '" xlink:href="#' +
         c.gids[0] + '" transform="translate(5,4)"/></svg>';
}

function buildPalette(filter){
  const box = document.getElementById('palette');
  const f = (filter || '').trim().toLowerCase();
  let html = '', group = '';
  catalog.forEach(c => {
    if (f && (c.name + ' ' + c.group).toLowerCase().indexOf(f) < 0) return;
    if (c.group !== group){ group = c.group; html += '<p class="grp">' + group + '</p>'; }
    html += '<button class="opt" data-cat="' + c.id + '">' + thumb(c) +
            '<span>' + c.name + '</span></button>';
  });
  box.innerHTML = html || '<p class="hint">No product matches that.</p>';
  box.querySelectorAll('.opt').forEach(o => o.onclick = () => {
    if (sel === null){
      const w = document.getElementById('curWhere');
      w.textContent = 'Pick a facing in the case first, then choose a product.';
      w.style.color = 'var(--warn)';
      setTimeout(() => { w.style.color = ''; refresh(); }, 1800);
      return;
    }
    setCat(sel, o.dataset.cat);
  });
  refresh();
}

/* ------------------------------------------------------------------ wiring */
CASE.querySelectorAll('.slot').forEach(g => {
  g.addEventListener('click', ev => {
    ev.stopPropagation();
    const i = +g.dataset.i;
    if (swapMode){
      if (swapFrom === null){ swapFrom = i; g.classList.add('swap'); return; }
      el(swapFrom).classList.remove('swap');
      if (swapFrom !== i) swap(swapFrom, i);
      swapFrom = null; swapMode = false;
      document.getElementById('swapBtn').classList.remove('on');
      select(i); return;
    }
    select(i);
  });
});

document.getElementById('swapBtn').onclick = function(){
  swapMode = !swapMode;
  this.classList.toggle('on', swapMode);
  if (!swapMode && swapFrom !== null){
    el(swapFrom).classList.remove('swap'); swapFrom = null;
  }
};
document.getElementById('emptyBtn').onclick = () => { if (sel !== null) setCat(sel, null); };
document.getElementById('revertBtn').onclick = () => {
  if (sel !== null) setCat(sel, ORIGINAL[sel]);
};
document.getElementById('undoBtn').onclick = () => {
  const u = undo.pop(); if (!u) return;
  if (u.pair){ slots[u.pair[0]].cat = u.ca; slots[u.pair[1]].cat = u.cb;
               paint(u.pair[0]); paint(u.pair[1]); }
  else { slots[u.i].cat = u.cat; paint(u.i); }
  refresh();
};
document.getElementById('resetBtn').onclick = () => {
  if (!confirm('Reset every facing to the photographed layout?')) return;
  undo.length = 0;
  slots.forEach((s, i) => { s.cat = ORIGINAL[i]; paint(i); });
  refresh();
};

function download(name, text, type){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: type }));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

document.getElementById('jsonBtn').onclick = () => {
  const out = slots.map((s, i) => ({
    spot: i, shelf: s.shelf + 1, bay: bayOf(s.x),
    row: s.back ? 'back' : 'front',
    product: s.cat ? byCat[s.cat].name : null,
    changed: s.cat !== ORIGINAL[i] || undefined
  }));
  download('planogram.json', JSON.stringify(out, null, 2), 'application/json');
};

document.getElementById('svgBtn').onclick = () => {
  const clone = CASE.cloneNode(true);
  clone.removeAttribute('id');
  clone.setAttribute('width', CASE.viewBox.baseVal.width);
  clone.setAttribute('height', CASE.viewBox.baseVal.height);
  clone.querySelectorAll('.hit,.ring').forEach(n => n.remove());
  clone.querySelectorAll('.slot').forEach(g => {
    if (g.classList.contains('empty')) g.remove();
    g.removeAttribute('class'); g.removeAttribute('data-i');
  });
  download('chicken-case-planogram.svg',
           '<?xml version="1.0" encoding="UTF-8"?>\n' +
           new XMLSerializer().serializeToString(clone), 'image/svg+xml');
};

document.getElementById('find').oninput = e => buildPalette(e.target.value);
document.querySelector('.stage').addEventListener('click', () => select(null));
document.querySelector('aside').addEventListener('click', e => e.stopPropagation());
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'Escape') return select(null);
  if (sel === null) return;
  if (e.key === 'Delete' || e.key === 'Backspace'){ e.preventDefault(); setCat(sel, null); }
  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight'){
    e.preventDefault();
    const cur = slots[sel];
    const same = slots.map((s, i) => ({ s: s, i: i }))
      .filter(o => o.s.shelf === cur.shelf && o.s.back === cur.back)
      .sort((a, b) => a.s.x - b.s.x);
    const at = same.findIndex(o => o.i === sel);
    const nx = same[at + (e.key === 'ArrowRight' ? 1 : -1)];
    if (nx) select(nx.i);
  }
});

load();
slots.forEach((s, i) => paint(i));
buildPalette('');
</script>
"""


if __name__ == "__main__":
    main()
