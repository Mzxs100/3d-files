# June's Place — concept website

A mobile-first, Apple-style marketing site for **June's Place**, the cozy
coffee shop on Main Street in Rexburg, Idaho. Built to match the shop's real
character: warm espresso-and-cream palette, eclectic/cozy feel, locally
sourced treats, and the playful Harry-Potter-flavored whimsy regulars love.

## What's here

| File | Purpose |
|------|---------|
| `index.html` | Single-page site (semantic, accessible, no framework) |
| `styles.css` | Mobile-first stylesheet — breakpoints at 720px & 1000px |
| `script.js` | Sticky nav, mobile drawer, scroll-reveal (vanilla JS) |
| `assets/logo-mark.svg` | Coffee-cup logo mark with steam + sparkle |
| `assets/logo-lockup.svg` | Horizontal logo + "June's Place" wordmark |
| `assets/favicon.svg` | Rounded app-style favicon |
| `assets/icons.svg` | Reusable SVG icon sprite (cup, leaf, pin, clock, etc.) |

All artwork is hand-built SVG — no image dependencies, so the page is fast and
crisp on every screen. The icon sprite is also inlined in `index.html` for a
zero-extra-request load; `assets/icons.svg` is provided for reuse elsewhere.

## Design notes

- **Mobile-first:** base styles target small screens; `min-width` media queries
  progressively enhance to tablet and desktop layouts.
- **Apple-like polish:** translucent blurred sticky nav, generous whitespace,
  large serif display type (Fraunces), soft shadows, and gentle scroll motion.
- **Theme:** espresso `#3b2616`, cream `#f7f1e6`, gold `#c8a04b`. The "Step
  inside" section recreates the room's vibe (cozy seating, local art, a touch
  of wizardry, makers' market) with pure-CSS gradient tiles.
- **Accessible:** keyboard-reachable nav, ARIA labels, and a
  `prefers-reduced-motion` fallback.

## Run it

It's static — just open `index.html`, or serve the folder:

```bash
cd junes-place
python3 -m http.server 8000   # then visit http://localhost:8000
```

> Fan-made concept. Menu, pricing, and hours are illustrative and not official.
> Not affiliated with June's Place.
