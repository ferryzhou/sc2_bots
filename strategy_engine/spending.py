"""Generic bank allocation: honor a spend priority without starving.

A recurring macro problem at every stage of the game: a cheap, frequent action (a
probe, a Zealot) drains the resources a more important expensive action (a Nexus,
an upgrade, a tech structure) needs, so the important one never gets afforded --
the "starvation" bug. It shows up in the opening (probes delay the natural), on
expansions (army spend delays the next base), and in the mid/late game (army spend
delays upgrades or a tech switch).

One primitive resolves all of them, for any plan -- scripted build order OR a
reactive production queue: given the bank and a PRIORITY-ORDERED list of wants,
return which are affordable *now*, reserving for higher-priority **blocking** wants
first (so the bank accumulates toward them) while letting **soft** recurring wants
(probes, army) spend only from the surplus that remains.

Framework-agnostic and tiny: the caller builds the ordered ``Want`` list from
whatever plan it has (a bot, a build script, a test), calls :func:`plan_spend`,
and issues the keys it returns. Workers are just another ``Want`` in the list, so
"pause probes to bank the Nexus" falls out for free -- put the Nexus above probes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Want:
    """One desired purchase. Priority is the position in the list (earlier = higher).

    ``blocking`` (default): if it can't be afforded yet, reserve its cost so the
    bank banks toward it and lower wants are starved -- use for things that must
    happen next (an expansion, a supply building, a key upgrade/tech). ``soft``
    (blocking=False): if it can't be afforded after reservations, just skip it --
    use for recurring filler that should spend only surplus (probes, army units).
    """

    key: str
    minerals: float = 0.0
    vespene: float = 0.0
    blocking: bool = True


def plan_spend(minerals: float, vespene: float, wants: List[Want]) -> List[str]:
    """Return the keys issuable now, in priority order.

    Walks wants highest-priority first, tracking committed (spent + reserved)
    resources. A want is issuable iff the bank still covers it after everything
    committed above it. An unaffordable *blocking* want reserves its cost (banking
    toward it, starving everything below); an unaffordable *soft* want is skipped
    without blocking lower wants.
    """
    committed_m = committed_v = 0.0
    issuable: List[str] = []
    for w in wants:
        if minerals - committed_m >= w.minerals and vespene - committed_v >= w.vespene:
            issuable.append(w.key)
            committed_m += w.minerals
            committed_v += w.vespene
        elif w.blocking:
            # reserve toward it (bank up, block lower wants) -- but never reserve
            # more of a resource than the bank holds, or a want that needs NONE of
            # that resource would be wrongly blocked (a gas reserve must not block
            # a mineral-only unit).
            committed_m = min(committed_m + w.minerals, minerals)
            committed_v = min(committed_v + w.vespene, vespene)
        # soft + unaffordable -> skip, do not block lower wants
    return issuable
