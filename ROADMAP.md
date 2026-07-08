# Zero Hour Clone — Gap Analysis & Roadmap

What `generals.html` is missing to become an *accurate* clone of C&C Generals: Zero Hour.
Current state: 1 flat map, 2 cosmetic factions sharing one 6-unit / 6-building roster, supply-truck
economy, power grid, fog of war, timed-wave skirmish AI, touch controls.

Legend: 🔴 core to the Generals feel · 🟡 important for accuracy · 🟢 polish/nice-to-have
Effort: S (< 1 session) · M (1–2 sessions) · L (multi-session)

---

## 1. Factions & Generals

- [ ] 🔴 **China as a third faction** (we only have USA + GLA reskins) — hordes of cheap units,
      horde bonus, propaganda healing, mines on buildings. (L)
- [ ] 🔴 **Real faction asymmetry** — today both sides share identical stats/rosters:
  - USA: expensive high-tech, drones, aircraft focus, supply drop income
  - China: mass + firepower, slow heavy tanks, horde/nationalism bonuses
  - GLA: cheap/fragile, **no power requirement**, scavenging, tunnels, stealth (L)
- [ ] 🟡 **Zero Hour's 9 specialist Generals** (Air Force, Laser, Superweapon / Tank, Infantry,
      Nuke / Toxin, Demolition, Stealth) with modified rosters & prices. (L, late-stage)
- [ ] 🟢 Generals Challenge mode (boss ladder vs. each general). (L)

## 2. Units

Current roster per side: Dozer, Supply Truck, rifle infantry, rocket infantry, tank, fast car.

- [ ] 🔴 **Aircraft as a class** — nothing airborne exists: no airfield, flight movement, ammo/rearm
      cycle, anti-air vs. ground weapon split, crash deaths. (Raptor, Stealth Fighter, Aurora,
      Comanche, MiG, Helix, Chinook, Combat Chinook.) (L)
- [ ] 🔴 **Missing ground rosters** (per faction, ~12–18 units each vs. our 6):
  - USA: Pathfinder (sniper), Colonel Burton (hero), Paladin, Tomahawk (artillery), Avenger,
    Ambulance, Sentry Drone, Microwave Tank
  - China: Red Guard, Tank Hunter, Hacker, Black Lotus (hero), Battlemaster, **Overlord**
    (with turret add-ons), Gattling Tank, Dragon Tank (flame), Inferno Cannon, Nuke Cannon,
    Troop Crawler, ECM Tank
  - GLA: Terrorist (suicide), **Angry Mob**, Hijacker, Jarmen Kell (hero), Marauder,
    Toxin Tractor, Quad Cannon, Rocket Buggy, Bomb Truck (disguise), **SCUD Launcher**,
    Radar Van, Combat Cycle (M each batch; L overall)
- [ ] 🔴 **Veterancy** — XP per kill, 3 chevron ranks, heroic self-heal. (S/M)
- [ ] 🔴 **Transports & garrisons** — infantry garrisoning civilian buildings & bunkers, firing
      ports (Technical/Troop Crawler/Chinook carry), garrison-clearing weapons (flashbang,
      flame, toxin). (L)
- [ ] 🟡 **Armor/damage-type matrix** — we use one flat damage number + a small anti-building
      bonus. Real game: damage types (gun, cannon, rocket, flame, sniper, toxin…) vs. armor
      classes (infantry, light, tank, structure, aircraft) with per-pair multipliers. (M)
- [ ] 🟡 **Special abilities & toggles** — capture building (Ranger/Red Guard/Rebel), sniper
      stealth, deploy-to-fire artillery, weapon toggles, suicide detonation, hero abilities. (L)
- [ ] 🟡 **Stealth & detection** — stealthed units/structures, detectors (Radar Van, drones). (M)
- [ ] 🟡 **Infantry crushing** by vehicles; Overlord crushes tanks. (S)
- [ ] 🟡 **GLA salvage** — destroyed vehicles drop salvage crates that upgrade GLA vehicles. (M)
- [ ] 🟢 Stances (aggressive / guard / hold fire), waypoint queues, formations. (M)
- [ ] 🟢 USA repair drones; Ambulance heal. (S/M)

## 3. Buildings

Current: Command Center, Reactor, Barracks, Supply Center, War Factory, Patriot.

- [ ] 🔴 **Airfield** (build/rearm aircraft, 4 pads). (M — depends on aircraft)
- [ ] 🔴 **Superweapons** — Particle Uplink Cannon (steerable beam), Nuclear Missile, SCUD Storm,
      with global countdown timers visible to both players. (M/L)
- [ ] 🔴 **Tech-tree gating** — real prerequisites (e.g. War Factory needs Supply Center; advanced
      units need Strategy Center / Propaganda Center / Palace; rank-gated units). Ours only gates
      by which building produces what. (S/M)
- [ ] 🔴 **Sell & repair buildings** — sell for ~50%, paid structure repair button (dozers repair
      free right now; real game charges). (S)
- [ ] 🟡 **Faction-specific defenses & tech buildings** — Strategy Center (battle plans), Supply
      Drop Zone, Detention Camp; Gattling Cannon, Bunker, Speaker Tower, Internet Center,
      Propaganda Center; Stinger Site (crewed), **Tunnel Network** (instant unit teleport between
      tunnels + auto-defense), Demo Trap, Black Market, Palace, **fake buildings**. (L)
- [ ] 🟡 **GLA holes** — destroyed GLA buildings leave a hole that rebuilds itself unless killed. (S/M)
- [ ] 🟡 **Neutral tech buildings on the map** — capturable Oil Derrick (income), Hospital,
      Repair Bay, Reinforcement Pad, plus garrisonable civilian houses. (M)
- [ ] 🟢 Multiple dozers accelerating one construction; build-queue of structures for GLA workers. (S)

## 4. Economy

- [ ] 🔴 **Faction gatherers** — USA Chinook (air gather, larger loads), China Supply Truck,
      GLA Worker (gathers *and* builds, cheap). One truck type today. (M)
- [ ] 🟡 **Secondary income** — USA Supply Drop Zone, China Hackers (+Internet Center),
      GLA Black Market trickle; capturable Oil Derricks. (M)
- [ ] 🟡 **Accurate costs/build times** — ours are approximations; audit against real values
      per faction. (S, data entry)
- [ ] 🟢 Starting-cash options; bounty (GLA Demo general) style modifiers. (S)

## 5. Upgrades

Entirely missing as a system (research-at-building, one-time purchases):

- [ ] 🔴 **Upgrade framework** — purchasable at specific buildings, applies to unit classes,
      shows in build bar. (M)
- [ ] 🟡 USA: TOW Missile (Humvee), Composite Armor, Rocket Pods, Drone upgrades, Flashbangs,
      Advanced Training, Chemical Suits
- [ ] 🟡 China: Black Napalm, Chain Guns, Nationalism, Uranium Shells, Mines, Subliminal
      Messaging, Satellite Hack
- [ ] 🟡 GLA: AP Bullets/Rockets, Toxin Shells, Anthrax Beta, Junk Repair, Camouflage,
      Arm the Mob, Buggy Ammo (each S once framework exists)

## 6. Generals Powers (promotion system)

- [ ] 🔴 **Rank/XP system** — earn stars from kills, spend points in a powers tree. (M)
- [ ] 🟡 The powers themselves, per faction with cooldown timers: Spy Drone, Paratrooper Drop,
      A-10 Strike (we removed the placeholder), Emergency Repair, Fuel Air Bomb, Spectre Gunship,
      Artillery Barrage, Cluster Mines, Carpet Bomb, Frenzy, Cash Bounty, Rebel Ambush,
      Anthrax Bomb, GPS Scrambler, Sneak Attack tunnel. (M/L)

## 7. Combat Fidelity

- [ ] 🟡 Persistent ground hazards — toxin puddles, firestorms/napalm that burn & spread,
      radiation from nukes; trees catch fire. (M)
- [ ] 🟡 Point Defense Laser / ECM deflection countering missiles. (S/M)
- [ ] 🟡 Artillery arcs & area denial (Tomahawk/SCUD lobbed projectiles, Inferno firewalls). (M)
- [ ] 🟢 Wreck husks, salvage drops, aircraft crash trajectories, richer explosion variety. (M)
- [ ] 🟢 Friendly-fire splash (real game has it; we only damage enemies). (S)

## 8. Maps & Terrain

- [ ] 🔴 **Terrain that matters** — impassable cliffs, ramps/elevation, water, destructible
      bridges, real chokepoints. Our map is a flat open square with decorative props. (L)
- [ ] 🔴 **Multiple maps + skirmish setup screen** — map picker, start positions, # of AI
      opponents, team setup, starting cash, superweapon on/off. (M)
- [ ] 🟡 Destructible/burnable trees, civilian towns with garrisons, scorch decals that persist. (M)
- [ ] 🟢 More than 1v1: 3–4 player FFA / 2v2 with team logic. (M/L)

## 9. Skirmish AI

- [ ] 🔴 **Difficulty levels** (Easy → Brutal) tuning income, aggression, micro. (S/M)
- [ ] 🔴 **AI base building** — our AI never *constructs* anything; it should place new
      structures, rebuild losses, expand to fresh supply piles, add defenses under pressure. (M/L)
- [ ] 🟡 AI uses generals powers, superweapons, upgrades; varies attack composition and attack
      routes (flanks); defends its harvesters; retreats damaged groups. (M/L)
- [ ] 🟢 Per-faction AI personalities. (M)

## 10. Modes, Meta & Persistence

- [ ] 🟡 **Save/load** match state (localStorage — fits the single-file constraint). (M)
- [ ] 🟡 Post-match score screen (units built/lost, buildings razed, economy graph). (S/M)
- [ ] 🟢 Campaign-style scripted missions with objectives/triggers (original scenarios — the real
      campaign's story/cutscenes/audio are EA's copyrighted content and can't be copied). (L)
- [ ] 🟢 Multiplayer (WebRTC peer-to-peer would require a deterministic lockstep sim —
      a big architectural change). (L+)

## 11. UI/UX

- [ ] 🔴 **Control groups** (assign/recall squads — critical for RTS feel; long-press number
      row on mobile). (S/M)
- [ ] 🔴 Better command bar: unit portraits w/ health, multi-type selection tabs, per-item queue
      cancel (we only refund the last), ability buttons with cooldown sweeps. (M)
- [ ] 🟡 Alerts — "base under attack" minimap pings, idle-worker button, low-power warning. (S)
- [ ] 🟡 Attack-target cursors/markers, rally-point flags, veterancy chevrons on health bars. (S)
- [ ] 🟢 Desktop hotkeys, edge-scroll, camera bookmarks; gamepad? (S/M)

## 12. Audio & Visual Identity

- [ ] 🟡 Unit voice acknowledgments & EVA-style announcer — must be **original recordings or
      synthesized placeholders**; the real game's voice lines, music, and sounds are copyrighted
      and can't be reproduced. (M)
- [ ] 🟡 Animation pass — walking infantry, turret recoil, dozer blade, construction scaffolds,
      idle animations, muzzle variety. All doable in our SVG/canvas pipeline. (M)
- [ ] 🟢 Music — original soundtrack in the game's spirit (WebAudio-generated or licensed). (M)

## 13. Engine Debt (prerequisites for the above)

- [ ] 🔴 **Grid A\* pathfinding** — current steering + wall-follow works for open maps but will
      not survive real cliffs/bridges/mazes. Needed before Maps & Terrain. (M)
- [ ] 🟡 Spatial hashing for unit queries (O(n²) separation/targeting caps us at ~100 units;
      real ZH battles run 200+). (S/M)
- [ ] 🟡 Data-driven definitions — move all unit/building/upgrade stats into one JSON block so
      factions/generals are data, not code. (S/M)
- [ ] 🟢 Deterministic fixed-tick simulation (only needed for multiplayer/replays). (L)

---

## Suggested milestone order

1. **M1 — "Feels like Generals"**: armor/damage matrix, veterancy, sell/repair, control groups,
   tech-tree gating, base-under-attack alerts, AI difficulty + AI base building. *(mostly S/M items)*
2. **M2 — China + real asymmetry**: data-driven stats, China roster/buildings, GLA no-power +
   workers + tunnels, faction gatherers.
3. **M3 — Air war**: airfield, 4–6 aircraft, anti-air split, Chinook gathering.
4. **M4 — Upgrades + Generals powers + superweapons** (with countdowns).
5. **M5 — Maps**: A* pathfinding, terrain classes, bridges, map picker, tech buildings, garrisons.
6. **M6 — Meta**: save/load, score screen, scripted missions, (stretch) multiplayer.

**Constraint notes:** everything must stay a single offline HTML file (assets stay procedural
SVG/WebAudio — which also keeps us clear of EA's copyrighted art, audio, and story content; game
*mechanics* and stat values are fine to replicate). Phone performance is the other ceiling —
spatial hashing and capped particle counts before any 200-unit battles.
