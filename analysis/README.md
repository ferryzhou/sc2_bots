# analysis/ — replay investigation toolchain

Run with the py3.12 venv (`/root/venv312/bin/python`, has sc2reader).

## Investigate a loss (start here)

```
python analysis/investigate.py <replay> [more ...] [--our N] [--out FILE]
```

One command → a full markdown report with an auto **root-cause verdict**
(combat-loss vs under-invested/greed vs macro-broke), head-to-head economy,
accumulated resources & army value, and a minute-level army timeline with each
fight inline. See `.claude/skills/loss-investigation/SKILL.md` for how to read it.

Reports land in `analysis/reports/`. Narrative write-ups (TL;DR + solutions) go
in `analysis/<BOT>_LOSS_ANALYSIS.md` (template: `AIUR_LOSS_ANALYSIS.md`).

## Lower-level tools

| script | question it answers |
|--------|---------------------|
| `game_report.py <replay> [player]` | did production run & economy look good? (one player) |
| `loss_analysis.py <replay> [pid]`  | the same metrics as investigate, as a text dump |
| `extract_build_order.py`, `extract_openings.py` | build orders / openings from replays |
| `verify_build.py`, `verify_openings.py` | did a bot reproduce a scripted build? |

## Conventions

- sc2reader **load_level=3** (tracker events); level 4 crashes on vs-AI replays.
- vs-Computer replays have no player result — it's inferred from final army supply.
- Unit costs / army value: static table in `loss_analysis.py` (`COST`).
