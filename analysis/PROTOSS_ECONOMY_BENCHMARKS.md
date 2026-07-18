# Protoss economy benchmarks (greedy macro) & Aiur's gaps

Study of how pro Protoss maximize economy + army from a greedy opening, the
concrete benchmarks to hit, and where AiurBot falls short. Sources at the bottom.

## The greedy macro opening (16 Nexus / gate-expand)

The standard economic opening pros use when safe:

```
 9  Pylon                (chrono Nexus for probes from here)
13  Gateway
14  Assimilator (gas)
15  probe to natural
16  Nexus (NATURAL)       <- ~1:50-2:15, ~380-400 min when the probe arrives
17  Cybernetics Core      (as the gate finishes)
    Warp Gate research    ASAP, chrono'd
20  Pylon, 2nd gas
    3rd base              ~4:30-5:30, before the natural fully saturates
```

Key idea: **only a Pylon + 1 Gateway + gas go down before the Nexus.** Everything
else (2nd gate, robo, forge, twilight) waits until the natural is placed, so
minerals bank for a ~2:00 expansion.

## Benchmarks to hit

| Metric | Pro macro Protoss | Aiur (before) | Aiur (after eco fixes) |
|--------|-------------------|---------------|------------------------|
| Natural (2nd base) | **~1:50–2:20** | ~5:00–6:00 ❌ | **~3:10** ⬆ |
| 3rd base | ~4:30–5:30 | ~9:00–13:00 ❌ | ~8:00 ⬆ (gated by army) |
| Warp Gate research | ASAP (~3:00) | **never** ❌ | **still never** ❌ |
| Workers | 22/base; ~44 @2, ~66 @3; finish 66–80 | slow | ~62 @10:00 ⬆ |
| Total supply @10:00 | ~120–140 | ~78 | ~98 ⬆ |
| **Total supply @12:00** | **~150–175** | ~102 ❌ | ~113 ⬆ (surviving games) |
| Max (200 supply) | ~13–15:00 | never | not yet |

**After the eco fixes**: the natural came ~1.5 min earlier and supply rose ~10–20,
but it plateaus around ~100–113 because the **3rd base is gated behind having a
covering army (14 supply), which Aiur can't field until ~8:00 without Warp Gate.**
Warp Gate is the keystone: faster army production → the 3rd base comes sooner →
supply compounds → *and* there's an army to defend the greedier economy (a fast
natural with no Warp Gate got punished at ~10:00 in testing).

The single-number target the user set — **150+ supply at 12:00** — is the right
bar. Aiur was at ~102 because the natural is 3–4 minutes late and Warp Gate is
missing, which delays both the worker ramp and army production.

## Chrono Boost technique

- **Opening (0–~4 min):** chrono the **Nexus (probes)** — the biggest economic
  lever — plus the Cyber Core's **Warp Gate research** the moment it starts.
- **Mid game:** shift chrono to **upgrades** (they compound every fight) and then
  **production** (gateways/robo/stargate) so units come faster off a bigger economy.

Aiur previously chrono'd production first and probes only *last* (and only under
44 workers), so the opening economy never got the early boost.

## Fixes applied (this pass — economy)

1. **Greedy natural** (`aiur/main.py:_tech`): once Gateway + Cyber are up, hold all
   further tech until the natural is down, so minerals bank for a ~2:30 Nexus.
   Guarded by `defense.emergency` — greed only when safe; a real rush techs to
   defense instead.
2. **Chrono probes first** (`aiur/main.py:_chrono`): in the opening pump probes
   (and Warp Gate research); shift to upgrades then production once developed.

## Still open (next pass — army tempo)

- **Warp Gate research + warp-in.** Aiur has no Warp Gate at all, so gateways
  produce slowly and can't warp-in reinforcements. Adding it needs warp-in logic
  (warp units onto a power field off cooldown), so it's a separate, careful change
  — but it's the biggest remaining army-tempo lever.

## Sources

- [Spawning Tool — Protoss build orders (PvX)](https://lotv.spawningtool.com/build/pvx/)
- [Liquipedia — Macro](https://liquipedia.net/starcraft2/Macro) ·
  [Mental Checklist](https://liquipedia.net/starcraft2/Mental_Checklist)
- [The Helper — Protoss 16 Nexus](https://www.thehelper.net/threads/protoss-16-nexus.147926/)
- [TL.net — Protoss macro build for beginners](https://tl.net/forum/bw-strategy/514054-protoss-macro-build-order-for-beginners)
