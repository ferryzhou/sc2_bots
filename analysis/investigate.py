"""Generate a full investigation report for a replay (or a batch of them).

This is the one command to run after a loss. It reuses the metric functions in
``loss_analysis`` and emits a self-contained **markdown report** with:

  1. an auto-generated **root-cause verdict** (macro-broke vs combat-loss vs
     under-invested/greed vs won), from heuristics over the same metrics;
  2. head-to-head **economy** (workers / bases / minerals / gas, banked + income);
  3. **accumulated** resources mined and army value produced (+ share to army);
  4. the minute-level **army-value timeline with the fight each minute inline**;
  5. the decisive **engagements** and the **peak composition + upgrades**.

    python analysis/investigate.py <replay> [replay2 ...] [--our N] [--out FILE]

Default our_pid is 1. Without --out the report prints to stdout; with --out it
is written to that path (and, for a batch, each report is concatenated).

The debugging discipline it encodes: *first* ask "did production run and did the
economy look good?" (section 2), and only if macro was fine attribute the loss to
combat (sections 1, 3, 4). The verdict block states which it was.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loss_analysis as la  # noqa: E402  (needs analysis/ on sys.path first)


def infer_result(stats, pid):
    """'win' / 'loss' / 'unknown' for pid, from final army supply.

    vs-Computer replays have no player results; the loser's army is wiped, so
    its final food_used collapses to ~0 while the winner still has supply.
    """
    def final_food(p):
        return stats[p][-1].food_used if stats.get(p) else None
    me, them = final_food(pid), final_food(2 if pid == 1 else 1)
    if me is None or them is None:
        return "unknown"
    if me <= 5 and them > 15:
        return "loss"
    if them <= 5 and me > 15:
        return "win"
    return "unknown"


def verdict(units, stats, ours, theirs, length):
    """Classify the root cause from the metrics. Returns (headline, bullets)."""
    marks = list(range(60, length + 1, 60))
    pw1 = max((int(la.stat_at(stats, ours, t, "workers_active_count")) for t in marks), default=0)
    pw2 = max((int(la.stat_at(stats, theirs, t, "workers_active_count")) for t in marks), default=0)
    floats = sum(1 for t in marks if int(la.stat_at(stats, ours, t, "minerals_current")) > 700)
    tot_lost, _ = la.deaths_in(units, ours, 0, length)
    tot_killed, _ = la.deaths_in(units, theirs, 0, length)
    trade = tot_killed / tot_lost if tot_lost else 9.9
    made1 = la.army_value_made(units, ours, length)
    made2 = la.army_value_made(units, theirs, length)
    made_ratio = made1 / made2 if made2 else 9.9
    m1, g1 = la.collected_by(stats, ours, length)
    invest = made1 / (m1 + g1) if (m1 + g1) else 0
    m2, g2 = la.collected_by(stats, theirs, length)
    invest_e = made2 / (m2 + g2) if (m2 + g2) else 0

    # first decisive battle: earliest minute we lost >= 500 value at trade < 0.6.
    # Capture the standing-army value ratio going in (sampled at the minute start).
    first_battle = None
    for t in marks:
        lost1, _ = la.deaths_in(units, ours, t - 60, t)
        lost2, _ = la.deaths_in(units, theirs, t - 60, t)
        if lost1 >= 500 and (lost2 / lost1 if lost1 else 9.9) < 0.6:
            ov0, os0, _ = la.alive_army(units, ours, t - 60)
            ev0, es0, _ = la.alive_army(units, theirs, t - 60)
            aratio = ov0 / ev0 if ev0 else 9.9
            first_battle = (t, lost1, lost2, lost2 / lost1,
                            ov0, os0, ev0, es0, aratio)
            break

    bullets = [
        f"peak workers {pw1} vs {pw2}; floating(>700 min) samples {floats}",
        f"army value produced {made1} vs {made2} (ratio {made_ratio:.2f}); "
        f"invested {invest:.0%} of income into army vs enemy {invest_e:.0%}",
        f"overall trade {trade:.2f} (killed {tot_killed} / lost {tot_lost})",
    ]
    if first_battle:
        t, l1, l2, tr, ov0, os0, ev0, es0, aratio = first_battle
        bullets.append(
            f"first decisive fight {la.mmss(t)}: went in at army value "
            f"{ov0} vs {ev0} (**ratio {aratio:.2f}**), supply {os0} vs {es0}; "
            f"lost {l1} for {l2} — trade {tr:.2f}")

    # heuristics, most-specific first. Low peak workers only signals a macro
    # failure in a game long enough to have developed economy -- in a short
    # game it just means we died early (a combat/timing problem, not macro).
    long_game = length >= 720  # 12 min
    macro_broke = floats > 4 or (pw1 < 35 and long_game)
    combat_loss = made_ratio >= 0.85 and trade < 0.7
    under_invested = made_ratio < 0.7 and invest < invest_e

    if combat_loss:
        head = ("COMBAT LOSS — built enough army (ratio "
                f"{made_ratio:.2f}) but lost it at bad trades ({trade:.2f}); "
                "composition / engagement, not production")
    elif under_invested:
        head = ("UNDER-INVESTED / GREED — too little into army (produced "
                f"{made_ratio:.2f}× enemy, {invest:.0%} of income vs {invest_e:.0%}); "
                "caught before teching up"
                + (" by an early timing" if not long_game else ""))
    elif macro_broke:
        head = "MACRO BROKE — economy/production failed before combat mattered"
    else:
        head = f"MIXED — trade {trade:.2f}, army-made ratio {made_ratio:.2f}; see metrics"
    return head, bullets


def report(path, ours, out):
    theirs = 2 if ours == 1 else 1
    r, units, stats, upgrades = la.load(path)
    length = int(r.game_length.seconds)
    marks = list(range(60, length + 1, 60))
    res = infer_result(stats, ours)
    head, bullets = verdict(units, stats, ours, theirs, length)

    p = out.append
    p(f"# Investigation: {os.path.basename(path)}")
    p("")
    p(f"- map **{r.map_name}**, length **{r.game_length}**, our pid **{ours}** — "
      f"result: **{res.upper()}**")
    p("")
    p(f"## Verdict — {head}")
    p("")
    for b in bullets:
        p(f"- {b}")
    p("")

    # 1) economy head-to-head. Ratios (us/enemy): workers, mining speed (income
    # rate), and accumulated resources mined -- worker parity can still hide a
    # resource deficit (fewer bases, less gas, lower saturation).
    p("## Economy (ratios are us/enemy: workers | mining speed | total mined)")
    p("")
    p("| time | workers | bases | min bank/inc | gas bank/inc "
      "| wkr ratio | mine-speed ratio | mined ratio |")
    p("|------|:-------:|:-----:|:------------:|:------------:"
      "|:---------:|:----------------:|:-----------:|")
    for t in marks:
        w1 = int(la.stat_at(stats, ours, t, "workers_active_count"))
        w2 = int(la.stat_at(stats, theirs, t, "workers_active_count"))
        b1, b2 = la.bases_at(units, ours, t), la.bases_at(units, theirs, t)
        m1b = int(la.stat_at(stats, ours, t, "minerals_current"))
        m1r = int(la.stat_at(stats, ours, t, "minerals_collection_rate"))
        m2b = int(la.stat_at(stats, theirs, t, "minerals_current"))
        m2r = int(la.stat_at(stats, theirs, t, "minerals_collection_rate"))
        g1b = int(la.stat_at(stats, ours, t, "vespene_current"))
        g1r = int(la.stat_at(stats, ours, t, "vespene_collection_rate"))
        g2b = int(la.stat_at(stats, theirs, t, "vespene_current"))
        g2r = int(la.stat_at(stats, theirs, t, "vespene_collection_rate"))
        wr = (w1 / w2) if w2 else 1.0
        inc1, inc2 = m1r + g1r, m2r + g2r          # mining speed = total income rate
        spd = (inc1 / inc2) if inc2 else 1.0
        cm1, cg1 = la.collected_by(stats, ours, t)
        cm2, cg2 = la.collected_by(stats, theirs, t)
        mined = ((cm1 + cg1) / (cm2 + cg2)) if (cm2 + cg2) else 1.0
        flag = " ⚠️" if (w2 and w1 < 0.85 * w2) else ""
        sflag = " ⚠️" if (inc2 and inc1 < 0.85 * inc2) else ""
        p(f"| {la.mmss(t)} | {w1} v {w2}{flag} | {b1} v {b2} | "
          f"{m1b}/{m1r} v {m2b}/{m2r} | {g1b}/{g1r} v {g2b}/{g2r} | "
          f"{wr:.2f} | {spd:.2f}{sflag} | {mined:.2f} |")
    p("")

    # 2) accumulated
    p("## Accumulated — resources mined & army value produced")
    p("")
    p("| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |")
    p("|------|:------------------:|:---------------------:|:-------------:|:---------:|")
    for t in marks:
        m1, g1 = la.collected_by(stats, ours, t)
        m2, g2 = la.collected_by(stats, theirs, t)
        a1, a2 = la.army_value_made(units, ours, t), la.army_value_made(units, theirs, t)
        t1, t2 = m1 + g1, m2 + g2
        s1 = a1 / t1 if t1 else 0
        s2 = a2 / t2 if t2 else 0
        p(f"| {la.mmss(t)} | {int(m1)}/{int(g1)}/{int(t1)} | "
          f"{int(m2)}/{int(g2)}/{int(t2)} | {a1} v {a2} | {s1:.0%} / {s2:.0%} |")
    fm1, fg1 = la.collected_by(stats, ours, length)
    fm2, fg2 = la.collected_by(stats, theirs, length)
    fa1 = la.army_value_made(units, ours, length)
    fa2 = la.army_value_made(units, theirs, length)
    ft1, ft2 = fm1 + fg1, fm2 + fg2
    p("")
    p(f"- **TOTAL mined** us {int(ft1)} vs enemy {int(ft2)} "
      f"(ratio {ft1/ft2 if ft2 else 0:.2f})")
    p(f"- **TOTAL army value produced** us {fa1} vs enemy {fa2} "
      f"(ratio {fa1/fa2 if fa2 else 0:.2f}); invested {fa1/ft1 if ft1 else 0:.0%} "
      f"vs enemy {fa2/ft2 if ft2 else 0:.0%}")
    p("")

    # 3) army value + battle timeline
    p("## Army value + the fight each minute")
    p("")
    p("| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |")
    p("|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|")
    for t in marks:
        ov, os_, _ = la.alive_army(units, ours, t)
        ev, es_, _ = la.alive_army(units, theirs, t)
        ratio = (ov / ev) if ev else (9.9 if ov else 1.0)
        oup = sum(1 for s, _ in upgrades[ours] if s <= t)
        eup = sum(1 for s, _ in upgrades[theirs] if s <= t)
        lost1, _ = la.deaths_in(units, ours, t - 60, t)
        lost2, _ = la.deaths_in(units, theirs, t - 60, t)
        fight = "—"
        if max(lost1, lost2) >= 200:
            tr = (lost2 / lost1) if lost1 else 9.9
            tag = "**BATTLE**" if max(lost1, lost2) >= 700 else "skirm"
            fight = f"{tag} {lost1}/{lost2} — {tr:.2f}"
        p(f"| {la.mmss(t)} | {ov}/{os_} | {ev}/{es_} | {ratio:.1f} | "
          f"{oup}/{eup} | {fight} |")
    p("")

    # 4) engagements + composition
    p("## Decisive engagements (30s buckets, most value lost)")
    p("")
    buckets = []
    for t0 in range(0, length, 30):
        lv, lc = la.deaths_in(units, ours, t0, t0 + 30)
        ev_, ec = la.deaths_in(units, theirs, t0, t0 + 30)
        if lv >= 300 or ev_ >= 300:
            buckets.append((t0, lv, lc, ev_, ec))
    buckets.sort(key=lambda b: -b[1])
    for t0, lv, lc, ev_, ec in buckets[:6]:
        ov, os_, ocomp = la.alive_army(units, ours, t0)
        env, es_, ecomp = la.alive_army(units, theirs, t0)
        tr = (ev_ / lv) if lv else 9.9
        p(f"- **{la.mmss(t0)}** we lost {lv} ({la._fmt(lc)}); they lost {ev_} "
          f"({la._fmt(ec)}) — trade **{tr:.2f}**")
        p(f"  - going in: us {ov}v/{os_}s {la._fmt(ocomp)} · enemy {env}v/{es_}s {la._fmt(ecomp)}")
    p("")
    peak_t = max(marks, key=lambda t: la.alive_army(units, ours, t)[0]) if marks else length
    ov, os_, ocomp = la.alive_army(units, ours, peak_t)
    env, es_, ecomp = la.alive_army(units, theirs, peak_t)
    p(f"## Peak composition @ {la.mmss(peak_t)} ({ov}v/{os_}s)")
    p("")
    p(f"- us: {la._fmt(ocomp)}")
    p(f"- enemy: {la._fmt(ecomp)}")
    p(f"- our upgrades ({len(upgrades[ours])}): {[n for _, n in upgrades[ours]]}")
    p(f"- enemy upgrades ({len(upgrades[theirs])}): {[n for _, n in upgrades[theirs]]}")
    p("")
    return head


def main():
    argv = sys.argv[1:]
    ours = 1
    out_path = None
    replays = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--our":
            ours = int(argv[i + 1]); i += 2
        elif a == "--out":
            out_path = argv[i + 1]; i += 2
        else:
            replays.append(a); i += 1
    if not replays:
        print(__doc__)
        sys.exit(1)

    lines = []
    summary = []
    for path in replays:
        head = report(path, ours, lines)
        summary.append((os.path.basename(path), head))
        lines.append("\n---\n")
    text = "\n".join(lines)

    if out_path:
        with open(out_path, "w") as f:
            f.write(text)
        print(f"wrote {out_path}")
        print("\nverdicts:")
        for name, head in summary:
            print(f"  {name}: {head}")
    else:
        print(text)


if __name__ == "__main__":
    main()
