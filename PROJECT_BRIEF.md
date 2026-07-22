# Project Brief: Building a Zero Hour Mobile Clone From Scratch

A self-contained specification for building — from an empty file — a single-file,
offline, mobile-playable HTML5 real-time strategy game cloning the mechanics of
*Command & Conquer: Generals — Zero Hour*. This is a from-zero build plan, not a status
report: it assumes nothing exists yet and lays out what to build, in what order, and how.

---

## 1. End goal

One file, `generals.html`. Opened directly from disk (`file://`) on a phone or desktop
browser, with zero network connectivity, it runs a full RTS: base-building economy,
multiple asymmetric factions, real combat depth (armor types, veterancy, pathfinding),
a competent AI opponent, and a polished touch-first UI — as close as reasonably
achievable to the real game's *mechanics and balance*, built entirely from original,
procedurally-generated assets.

## 2. Hard constraints (do not relax these)

1. **Single HTML file.** Everything — markup, styles, game logic, and every visual
   asset — lives in one `.html` file. No external files, no CDN links, no fonts or
   images fetched over the network, no build step (no bundler, no npm dependency at
   runtime). It must work opened cold from a `file://` URL with the network off.
2. **All assets are procedural.** Every unit, building, terrain prop, and UI icon is an
   inline SVG string assembled by a small JS template helper (e.g. a `defAsset(name, w,
   h, svgBodyString)` function that builds a `data:image/svg+xml` URI and an `Image`
   object from it), then drawn to a `<canvas>`. Sound is synthesized at runtime with the
   WebAudio API (oscillators, filtered noise buffers for explosions) — never sample
   playback of external audio files.
3. **Clone mechanics and stats, not assets.** Unit roles, costs, damage math, tech
   trees, faction identities, pacing — all fair game to replicate closely, because
   *rules and numbers aren't copyrightable in the way art and audio are*. The real
   game's sprites, music, sound effects, voice lines, UI chrome, and campaign
   story/cutscenes must never be reproduced or embedded — build original equivalents
   for all of it.
4. **Phone-first controls.** Design every interaction for touch first: tap-to-select,
   tap-to-move/attack, drag-to-pan, pinch-to-zoom, drag-box multi-select, long-press for
   secondary actions (e.g. control-group assignment). Desktop mouse/keyboard should work
   as a fallback that falls naturally out of the same input handlers, not a parallel
   system.
5. **Runs at real framerate on a mid-range phone.** Keep the render loop cheap: batch
   canvas draws, cap particle counts, avoid O(n²) scans once unit counts grow (spatial
   partitioning becomes necessary past roughly 100 simultaneous units), and prefer
   simple procedural geometry over expensive per-frame path construction.

## 3. Recommended file architecture

Structure the single file internally as clearly separated sections (comment-delimited
regions work fine — no module system is available without a build step):

1. **Boilerplate & CSS** — mobile viewport meta (`viewport-fit=cover`,
   `user-scalable=no`), a `<canvas>` for the game world, HTML for the HUD chrome
   (topbar, command bar, minimap, toast, modal overlay).
2. **Utility math** — `clamp`, `dist`, `lerp`, `rnd`, angle-difference helpers. Small
   and boring; write it once, reuse everywhere.
3. **Asset pipeline** — the `defAsset` SVG helper described above, then one call per
   sprite needed (units, buildings, terrain props, icons). Keep faction color palettes
   as small lookup objects so sprite generator functions can be parameterized by
   faction rather than duplicated per faction.
4. **Data tables** — unit stats, building stats, damage/armor matrices, faction
   definitions. **Make this data-driven from the very first faction**, not just when a
   second one is added: define a faction as `{ name, powerNeeded, units: {...},
   buildings: {...}, menu: [...] }` keyed by shared *type keys* (`dozer`, `truck`,
   `inf`, `tank`, `cc`, `power`, `rax`, ...) even when only one faction exists yet.
   Every other system should read stats through accessor functions
   (`unitDef(team, type)`, `bldDef(team, type)`) and never hardcode a number inline.
   Retrofitting this later is expensive; starting with it is nearly free.
5. **World state** — a single `state` object (money, camera, selection, entity arrays
   for units/buildings/projectiles/particles/piles, fog-of-war grid, AI state) plus
   entity factory functions (`makeUnit`, `makeBuilding`, `makePile`). Keep entities as
   plain objects, not classes — it keeps `page.evaluate()`-style headless testing and
   quick inspection trivial.
6. **Simulation systems**, each a `updateX(dt)` function called once per frame:
   movement/steering, combat & projectiles, production queues, economy/harvesting,
   construction, fog of war, skirmish AI, particle effects.
7. **Rendering** — one `render()` that draws terrain (pre-rendered to an offscreen
   canvas and blitted, not redrawn per frame), then piles, buildings, units,
   projectiles, particles, UI overlays, and the minimap.
8. **Input handling** — pointer event listeners on the canvas translating screen
   coordinates to world coordinates via the camera transform, with mode state (normal
   select / placing a building / attack-move / box-select) driving what a tap or drag
   does.
9. **HUD/command bar** — rebuilt on selection change from the current selection's
   context (idle worker → build menu; production building → unit queue; combat units →
   attack-move/stop). Read costs and prerequisites from the data tables, never inline.
10. **Main loop** — `requestAnimationFrame` loop computing `dt`, calling the update
    functions in a fixed order, then `render()`.

## 4. Build order (phased, foundation to feature-complete)

Build in this order — each phase should be fully playable and tested before the next
begins. Do not attempt to build faction #2 or advanced systems before phase 1-3 are
solid; the data-driven pattern in §3.4 is what makes later phases cheap.

**Phase 0 — Skeleton.** Canvas + mobile viewport + touch pan/zoom camera. The asset
pipeline (`defAsset`) working end-to-end with one placeholder sprite. A bare game loop
running at stable framerate. Nothing playable yet, but the plumbing is proven.

**Phase 1 — One faction, one base, minimum viable RTS loop.** Single faction: a builder
unit, one resource-gathering unit, a handful of buildings (command center, power plant,
barracks, resource depot, one production factory, one static defense), 4-6 combat
units. Supply crates on the map, a gatherer loop (go to pile → load → return to depot →
deposit → repeat, automatically). Tap-select / tap-move / tap-attack. A minimap. Win/loss
conditions and a restart function. This phase alone should feel like a real, if simple,
RTS skirmish against no opponent yet.

**Phase 2 — Combat & unit depth.** Projectile-based combat with damage types (e.g.
bullet/rocket/cannon) and armor classes (infantry/light vehicle/heavy vehicle/
structure) combined into a multiplier matrix — this single system does more for
"feeling like an RTS" than almost anything else. Add veterancy (kills grant XP, ranks
grant stat bonuses and a visual marker). Replace naive move-toward-target movement with
real steering: obstacle avoidance around buildings (a wall-following approach handles
this well without needing full pathfinding yet), stuck detection, and separation so
groups of units don't jam against each other. Add control groups, tech-tree
prerequisites gating what can be built, sell/repair, and fog of war (a coarse grid
tracking live-visibility vs. explored-memory, rendered as a shroud plus the same
filtering applied to the minimap and to hit-testing so hidden enemies can't be tapped).

**Phase 3 — A skirmish AI opponent.** The AI must earn money over time and spend it
through its own production buildings exactly like the player does — never spawn units
for free or instantaneously; that's an exploit, not a challenge. Stage produced units
and launch them as timed waves rather than the instant they're built. Add a difficulty
system (economy rate, wave cadence/size, and — at higher difficulties — whether the AI
rebuilds destroyed structures from a remembered base layout while its command center
survives). Add base-under-attack alerts for the player. At this point the game is a
complete, single-faction skirmish against a real opponent.

**Phase 4 — Multiple asymmetric factions.** Add a second and third faction using the
data-driven pattern from §3.4. Give each a genuine identity, not just a palette swap:
different economy rules (e.g. one faction needs no power infrastructure at all and uses
a cheap dual-role unit that both builds and gathers), different combat character (e.g.
mass-cheap-units-with-a-proximity-bonus vs. balanced-and-expensive vs.
cheap-and-fragile-but-fast), distinct building rosters and defense types. Add
faction-select and enemy-faction-select pickers to the pre-game setup screen.

**Phase 5 — Air power.** An airfield building; a handful of aircraft per relevant
faction with real flight movement (distinct from ground steering), an ammo/rearm cycle
(return to a pad, wait, relaunch), and a weapon-class split so not everything can shoot
at aircraft. An air-capable gatherer for at least one faction.

**Phase 6 — Progression systems.** An upgrade framework: purchasable, one-time,
per-building unlocks that modify a unit class's stats or unlock a new ability, surfaced
in the build bar with clear cost/prerequisite display. A rank/XP meta-layer feeding a
tree of faction-specific timed special abilities (support powers — think airstrikes,
paratroop drops, emergency repair, artillery barrages — each with its own cooldown and
targeting). Superweapon-tier buildings with a globally-visible countdown timer once
under construction, giving the opponent a chance to race to destroy it.

**Phase 7 — Deeper rosters & special mechanics.** Expand each faction toward a dozen or
more units: snipers, artillery, suicide/demolition units, one or two named hero units
with unique abilities, transport vehicles that carry infantry with firing ports,
building garrisons, stealth units and detector counters, vehicle-crushes-infantry
mechanics, and a salvage/scavenging economy for the faction whose identity calls for it.

**Phase 8 — Terrain & maps.** This is the point to replace the phase-2 steering/
wall-following movement with real grid-based pathfinding (A* or similar) — terrain with
actual impassable cliffs, elevation, water, and destructible bridges cannot be handled
by local steering alone. Build several distinct maps and a pre-game setup screen (map
choice, AI opponent count, starting cash, superweapons on/off). Add capturable neutral
map structures (income buildings, garrisonable civilian structures).

**Phase 9 — Combat fidelity & polish.** Persistent battlefield hazards that spread or
linger (fire, toxin), lobbed/arcing artillery projectiles with area denial, wreck
husks and salvage drops, friendly-fire on splash weapons, a real animation pass
(walking cycles, turret recoil, construction scaffolding), richer explosion/particle
variety.

**Phase 10 — Meta & stretch goals.** Save/load (this is the one place `localStorage`
fits the single-file constraint well), a post-match score/stats screen, original
scripted single-player missions with objectives and triggers (write new scenarios —
never reproduce the real campaign's story or dialogue), and, as a substantial stretch
goal, peer-to-peer multiplayer (which requires a deterministic fixed-tick simulation —
a significant architecture change, not a bolt-on).

**Optional, any time after phase 3:** a distinctive visual design language for the HUD
is a free creative choice — it doesn't have to imitate the real game's UI (and per
§2.3, shouldn't). Whatever direction is chosen, keep it self-contained (inline CSS/SVG
only, no external fonts/icons) and verify it doesn't cost enough frame time to violate
§2.5 on real devices.

## 5. Engineering conventions to establish from day one

- **Verify every change by actually running it**, not just by reading the diff. Because
  the whole game is a single static file with no bundler, it's straightforward to drive
  headlessly with a browser automation tool (e.g. Playwright against the `file://`
  path): navigate to the file, call the game's own globals directly from injected page
  scripts (`makeUnit`, `makeBuilding`, `orderMove`, the `state` object, etc. are all
  plain top-level globals — no build step means nothing hides them), assert on
  resulting state, and screenshot anything visual to eyeball it. Watch for any thrown
  page errors or console errors on every run — there should be none, ever.
  Build a standing regression check covering movement/steering, the economy loop,
  construction, combat, and restart, and re-run it after any change that touches those
  systems; extend it as new systems are added rather than discarding it.
- **Never hardcode a stat outside the data tables.** If a new unit, building, or
  faction requires touching AI logic, production code, or rendering code beyond adding
  its data-table entry, the abstraction has leaked — fix the abstraction, not just the
  one new entry.
- **Balance changes need actual playtesting, not just a number tweak.** When adjusting
  AI aggression, economy rates, or unit stats, run a multi-minute simulated playthrough
  (fast-forwarded via the headless harness) and look at the resulting trajectory, not
  just a single snapshot assertion.
- **Commit in small, focused increments** with descriptive messages explaining what
  changed and why — one phase or one clearly-scoped feature per commit, not a giant
  end-of-session dump.
- **Keep a living roadmap document** tracking what's built, what's next, and rough
  priority/effort per remaining item, versus the real game's actual feature set. Update
  it as work completes so any future session (or collaborator) can resume from an
  accurate picture without re-deriving it.

## 6. Copy-paste prompt to start this project from scratch

Everything below the divider is meant to be handed to a model as a single opening
message to build this project from nothing, with full context and end-to-end autonomy.

---

> Build a single-file HTML5 real-time strategy game — a clone of *Command & Conquer:
> Generals: Zero Hour*'s mechanics — playable offline on a phone. Output goes in one
> file, `generals.html`. This is a long-horizon project: plan for it, then build the
> foundation first and verify it thoroughly before adding depth.
>
> **Non-negotiable constraints:**
> 1. Everything — HTML, CSS, JS, and every visual asset — lives in the single
>    `generals.html` file. No external files, no CDN links, no network calls at
>    runtime, no build step. It must run from a `file://` URL with zero connectivity.
> 2. Every visual asset is a procedural inline SVG (build a small `defAsset(name, w, h,
>    svgBody)` helper that produces a `data:image/svg+xml` `Image`, and draw everything
>    to canvas through it). Every sound is synthesized at runtime with WebAudio
>    (oscillators/noise), never sampled audio. Never reproduce the real game's art,
>    music, sound effects, voice lines, UI chrome, or campaign story — replicate its
>    *mechanics and balance*, not its assets.
> 3. From the very first faction, make unit/building stats data-driven: a faction is an
>    object keyed by shared type keys (dozer/gatherer/infantry/tank/command-
>    center/power-plant/barracks/factory/defense-turret, etc.), and every gameplay
>    system reads through accessor functions rather than hardcoding numbers. This
>    matters even before a second faction exists — retrofitting it later is expensive.
> 4. Design every interaction touch-first: tap-select, tap-move/attack, drag-pan,
>    pinch-zoom, drag-box-select, long-press for secondary actions. Desktop
>    mouse/keyboard should fall out of the same handlers as a natural fallback.
> 5. Keep it cheap enough to hold real framerate on a mid-range phone: batch canvas
>    draws, pre-render static terrain to an offscreen canvas, cap particle counts, and
>    watch for O(n²) scans as unit counts grow.
>
> **Build order — do not skip ahead:**
> 1. Skeleton: canvas, mobile viewport, touch pan/zoom camera, the asset pipeline
>    proven with one placeholder sprite, a stable `requestAnimationFrame` loop.
> 2. One faction, minimum viable RTS loop: builder + gatherer + a handful of buildings
>    and combat units, an automatic supply-crate gather-and-deposit loop, tap
>    select/move/attack, a minimap, win/loss conditions, restart.
> 3. Combat and unit depth: a damage-type × armor-class multiplier matrix, veterancy,
>    real obstacle-avoiding steering (not naive move-toward-target), control groups,
>    tech-tree prerequisites, sell/repair, fog of war.
> 4. A real skirmish AI: earns and spends money through its own buildings over time
>    (never instant/free spawns), launches staged timed waves, has difficulty levels,
>    and — at higher difficulty — rebuilds destroyed structures while its base survives.
> 5. Multiple asymmetric factions built on the data-driven pattern from constraint #3,
>    each with a genuinely distinct economy and combat identity, with faction-select
>    pickers on a pre-game setup screen.
> 6. Air power, an upgrade framework, a rank/XP-driven special-abilities system, and
>    superweapons with visible countdown timers.
> 7. Deeper per-faction rosters (snipers, artillery, hero units, transports/garrisons,
>    stealth/detection, crushing, salvage), real grid-based pathfinding and terrain
>    with actual impassable cliffs/water/bridges, multiple maps and a setup screen,
>    then combat-fidelity and animation polish, then save/load and a score screen.
>
> **Working method:** verify everything by actually running it — since there's no
> build step, drive the file headlessly with a browser automation tool, call the
> game's own state and functions directly, assert outcomes, and screenshot anything
> visual. Confirm zero console/page errors on every check. Keep a living roadmap
> document tracking progress and next steps against the real game's actual feature
> set, and commit in small, descriptive, focused increments as you go. Work
> autonomously and use good judgment on sequencing and scope — this is not expected to
> finish in one session. Stop to ask only when genuinely blocked by an ambiguous design
> choice with no clear "closer to the real game" answer, or before anything
> destructive/irreversible.
