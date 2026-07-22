# Project Brief: Zero Hour Mobile Clone

A condensed handoff document: what this project is, what's built, what's left, and a
self-contained prompt you can paste into a fresh model session to keep driving it toward
the end goal without re-explaining any of this.

---

## 1. What this is

`generals.html` — a single-file, offline, mobile-playable HTML5 real-time strategy game
cloning the mechanics of *Command & Conquer: Generals — Zero Hour*. No build step, no
dependencies, no network calls. Open it in any browser (phone or desktop) and it runs.

**Hard constraints (do not relax these):**
- **Single HTML file.** Everything — HTML, CSS, JS, and every visual asset — lives in
  `generals.html`. No external files, no CDN links, no fonts/images fetched over the
  network. It must keep working from a `file://` URL with zero connectivity.
- **All assets are procedural.** Every unit, building, terrain prop, and UI icon is an
  inline SVG string built by JS template functions (`defAsset(...)`), turned into a
  `data:image/svg+xml` URI, and drawn to a `<canvas>`. Sound is WebAudio-synthesized
  (oscillators + noise buffers), not sample playback. This is deliberate, not a
  shortcut: it's what keeps the file self-contained *and* clear of EA's copyrighted
  art, audio, and voice content.
- **We clone mechanics and stats, not assets.** Unit roles, costs, damage math, tech
  trees, faction identities — fair game to replicate closely. Original sprites,
  original music/SFX character, original UI chrome (we built our own "Liquid Glass"
  glass-morphism system rather than reusing EA's HUD look) — all original work.
- **Phone-first controls.** Tap-to-select, tap-to-move/attack, drag-to-pan,
  pinch-to-zoom, drag-box multi-select, long-press control groups. Desktop mouse/keyboard
  works as a fallback, not the primary target.
- **No mandatory build tooling.** Editing directly in the HTML file (via `Edit`/`Read`)
  is the normal workflow. Testing is done headlessly with Playwright driving a real
  Chromium instance against the `file://` path — see §4.

## 2. Repo state

- Repo: `Mzxs100/3d-files` (GitHub, via the `github` MCP server tools when available).
- Working branch: `claude/generals-game-html-svg-k9daib` (also pushed to `main`'s remote
  history via PRs as the user requests — **do not open a PR unless explicitly asked**).
- Key files at repo root:
  - `generals.html` — the game. ~2,000 lines, single file, as described above.
  - `ROADMAP.md` — the living gap-analysis and milestone tracker versus the real Zero
    Hour. **Read this first in any new session** — it has fine-grained checkboxes,
    priority tags (🔴 core / 🟡 accuracy / 🟢 polish), effort estimates, and a
    milestone-ordered build plan (M1, M2, M3...). Two milestones are checked off so far.
  - `PROJECT_BRIEF.md` — this file.
  - A handful of unrelated 3D asset files (`.glb`, a `.png`) from an earlier unrelated
    task in this workspace — ignore them, they are not part of this project.

## 3. What's built so far (condensed — full detail in ROADMAP.md)

**Core game loop:** pan/zoom canvas world, fog of war (live-vision + explored-memory
shroud, minimap included), a supply-crate economy (gatherer units loop pile→depot
automatically and retry rather than idling on failure), power grid (factions that need
it), building construction via worker units with resumable/interruptible sites, a
touch-first command bar that context-switches based on selection.

**Combat:** projectile-based (bullet/rocket/shell types) with splash damage, a real
armor-class × damage-type multiplier matrix (guns shred infantry, rockets crack armor
and buildings, cannons are all-round), veterancy (XP from kills, 3 chevron ranks with
stat bonuses, heroic self-heal).

**Pathfinding:** steering-based movement with bug-algorithm wall-following (units commit
to one rotational direction around a blocking building and follow its edges rather than
oscillating), stuck-detection sidestep detours, and priority separation (moving units
shove idle ones instead of both jamming).

**Three playable/AI-controllable factions** (data-driven — see §5): USA (balanced
high-tech), China (cheap infantry hordes with a proximity damage bonus, heavy Overlord
tank, Gattling anti-infantry defenses, no-Chinook-yet), GLA (no power requirement at
all, cheap dual-role Worker units that both build and gather, Quad Cannons). Faction
pickers for both player and AI opponent, plus an Easy/Normal/Hard difficulty picker, all
live on the deploy screen.

**Skirmish AI:** production-driven economy (no instant/exploit spawning — the AI earns
money over time and queues units through its own buildings like the player does),
staged wave launches on a timer, a standing home guard, and (Normal/Hard) autonomous
rebuilding of destroyed structures from a base blueprint while its Command Center
survives.

**UI/UX layer:** control groups (1/2/3, tap-select/long-press-assign/tap-again-to-jump),
base-under-attack alerts (toast + flashing minimap ping, throttled), sell-building,
tech-tree prerequisite gating with locked buttons, in-page restart (no reload needed).
A from-scratch **"Liquid Glass" UI system**: real SDF-based lens refraction via
runtime-generated `feDisplacementMap` filters (not CSS blur-and-border
glassmorphism) — rounded-rect signed-distance-field displacement maps, diffusion of the
backdrop before lensing, chromatic-fringe rim splitting, with an automatic frosted-blur
fallback for engines that reject `url()` backdrop filters (WebKit/Firefox) and a
runtime fps sentinel that degrades to the fallback on weak GPUs.

## 4. Engineering conventions established this project

Follow these — they're load-bearing for keeping quality high across sessions:

- **Every change is verified headlessly before it's called done.** The pattern used
  throughout: write a small Playwright script (`playwright-core`, launched with
  `executablePath: '/opt/pw-browsers/chromium'`, already installed in this
  environment — do not run `playwright install`), `page.goto('file:///.../generals.html')`,
  drive it with `page.evaluate()` calls that reach into the game's own global functions
  (`makeUnit`, `makeBuilding`, `orderMove`, `state`, etc. are all plain globals — no
  build step means no bundler hiding them), assert on state, and screenshot key moments.
  Scratchpad scripts live under the session's scratchpad dir (see environment prompt);
  `test6.js` there is the standing regression suite — rerun it after every change that
  touches movement, economy, construction, repair, AI pacing, or restart, and extend it
  when adding new systems rather than starting over.
- **No console errors, ever.** `page.on('pageerror', ...)` / `page.on('console', ...)`
  should report nothing on every test run.
- **Data-driven factions.** All unit/building stats live in the `FACTIONS` object keyed
  by faction id, with shared *type keys* (`dozer`, `truck`, `inf`, `rocket`, `tank`,
  `car`, `cc`, `power`, `rax`, `sup`, `fact`, `turret`, plus faction-specific extras like
  `heavy`/`quad`/`worker`). Every other system (AI, tech gating, production queues, fog,
  repair, rendering) reads through `unitDef(team, type)` / `bldDef(team, type)` and never
  hardcodes a stat — this is what let three factions drop in without touching combat,
  AI, or UI code. **Preserve this pattern** for any new faction, unit, or building.
- **Commit discipline:** small, focused commits per feature/milestone, descriptive
  bodies (what changed and why, not a diff summary), `Co-Authored-By` trailer as used in
  prior commits. Push to the working branch. Never force-push, never `--no-verify`,
  never touch `main` directly. Only open a PR if explicitly asked.
- **Update ROADMAP.md as you complete items** — flip `[ ]` to `[x]`, add a short "✅ Mx"
  note, and update the milestone summary line at the bottom. It's the single source of
  truth for progress across sessions; keep it honest (mark partial work as "(phase 1)"
  rather than fully checking something that's only half-implemented).
- **Balance changes need a rationale, not just a number tweak** — when adjusting AI
  aggression, economy rates, or unit stats, briefly test the "feel" (multi-minute
  simulated playthroughs via `page.evaluate`/`waitForTimeout` loops) rather than just
  asserting a single state snapshot.

## 5. What's left (see ROADMAP.md for the full checklist)

Roughly in priority order per the roadmap's own milestone plan:

- **M3 — Air war:** airfield building, 4-6 aircraft per relevant faction, flight
  movement, rearm/ammo cycles, anti-air vs. ground weapon split, USA Chinook air-gather.
- **Upgrade framework + Generals Powers:** purchasable per-building upgrades that modify
  unit classes; an XP/rank system spending points on faction-specific timed abilities
  (paratroopers, artillery barrages, emergency repair, etc.) — original implementations
  of the *mechanic*, not the real game's specific audio/art.
- **Superweapons:** Particle Cannon / Nuclear Missile / SCUD Storm equivalents with
  global visible countdown timers.
- **Deeper rosters per faction** (~12-18 units instead of today's 6-7): snipers, heroes,
  artillery, suicide units, transports/garrisons, stealth & detection, crushing,
  salvage.
- **Terrain that matters:** cliffs, ramps, water, destructible bridges, real
  chokepoints — this requires swapping today's steering pathfinding for grid-based A*,
  flagged in the roadmap as an engine prerequisite.
- **Multiple maps + skirmish setup screen**, AI base *expansion* (not just rebuilding),
  AI difficulty personalities, spatial hashing for larger battles, combat-fidelity
  polish (persistent hazards, artillery arcs, wreck husks), save/load, score screen.

## 6. Copy-paste prompt for a fresh session

Everything below the divider is meant to be handed to a new model instance (this one or
another) as a single opening message to resume work with full context and end-to-end
autonomy. It intentionally repeats some of the above so it stands alone.

---

> You are continuing development on an existing project: a single-file HTML5 clone of
> *Command & Conquer: Generals — Zero Hour*, playable offline on a phone. The file is
> `generals.html` at the repo root. Two other files matter: `ROADMAP.md` (the living
> gap-analysis and milestone tracker versus the real game — read it first, every time)
> and `PROJECT_BRIEF.md` (a condensed project overview and the engineering conventions
> established so far — read it second).
>
> **Your mandate:** keep driving this project toward an increasingly accurate, deeper,
> and more polished clone of Zero Hour's mechanics, working down `ROADMAP.md` in
> milestone order (M3 is next unless the user redirects you), while never breaking what
> already works. This is a long-horizon effort spanning many sessions — you are not
> expected to finish the whole roadmap in one pass. Do the highest-value, best-sequenced
> slice you can in this session, verify it thoroughly, commit and push it, update the
> roadmap, and leave the project in a shippable state before you stop.
>
> **Non-negotiable constraints:**
> 1. Everything stays in the single `generals.html` file — no external assets, no CDN
>    dependencies, no network calls at runtime. It must run from a `file://` URL with
>    zero connectivity, on a phone.
> 2. Every visual asset is a procedural inline SVG (`defAsset(...)` pattern already in
>    the file); every sound is WebAudio-synthesized. Never embed or reference the real
>    game's art, audio, music, voice lines, or campaign story — those are EA's IP.
>    Mechanics, unit roles, costs, and stat balancing are fair game to replicate closely.
> 3. Follow the data-driven faction pattern already established (`FACTIONS` object,
>    shared type keys, `unitDef`/`bldDef` accessors) for any new units, buildings, or
>    factions — don't hardcode stats into gameplay systems.
> 4. Controls are phone-first (touch/tap/drag/pinch); keep desktop mouse/keyboard
>    working as a secondary path.
>
> **Working method:**
> 1. Read `ROADMAP.md` and `PROJECT_BRIEF.md` fully before touching code.
> 2. Pick the next milestone (or ask the user only if genuinely ambiguous which to
>    prioritize — otherwise use judgment and proceed).
> 3. Plan the slice of work at a level that fits in the session, considering what
>    depends on what (e.g., aircraft need an airfield building and a flight-movement
>    system before anti-air weapons make sense).
> 4. Implement directly in `generals.html`.
> 5. Verify headlessly: use `playwright-core` with
>    `executablePath: '/opt/pw-browsers/chromium'` to drive a real browser against the
>    `file://` path to the game, exercise the new system plus a regression pass on
>    movement/economy/construction/combat/restart, assert on `page.evaluate()` state,
>    watch for any `pageerror`/console errors (there should be none), and screenshot
>    anything visual to eyeball it.
> 6. Commit with a descriptive message explaining what and why, push to the current
>    working branch (check `git branch`/`git status` first — do not assume; never force
>    push, never touch `main` directly, never open a PR unless asked).
> 7. Update `ROADMAP.md` — check off what's done, note partial work honestly, update the
>    milestone summary.
> 8. Send the user the updated `generals.html` file and a concise summary of what
>    changed, what you verified, and what's next.
>
> Work autonomously and make reasonable judgment calls rather than stopping to ask about
> every decision — this session is expected to run with minimal hand-holding. Only pause
> for genuinely blocking ambiguity (e.g., a design fork with no clear "more accurate to
> Zero Hour" answer) or before anything destructive/irreversible.
