"""Perception: turn what we can see into the enemy_memory that feeds the engine.

This is the scouting->belief layer. Each step it folds currently-visible enemy
units and structures into a persistent memory dict whose keys mirror the
``enemy_*`` fields on strategy_engine.GameState, so the advisor can classify the
opponent, detect all-ins, and reason under incomplete information.

Structure counts are kept as "max ever seen" (we lose vision, buildings persist),
which is the conservative choice for threat detection.
"""

from sc2.ids.unit_typeid import UnitTypeId as U

TOWNHALLS = {U.NEXUS, U.HATCHERY, U.LAIR, U.HIVE, U.COMMANDCENTER,
             U.ORBITALCOMMAND, U.PLANETARYFORTRESS}
PRODUCTION = {U.GATEWAY, U.WARPGATE, U.ROBOTICSFACILITY, U.STARGATE,
              U.BARRACKS, U.FACTORY, U.STARPORT,
              U.ROACHWARREN, U.HYDRALISKDEN, U.SPAWNINGPOOL}
GAS = {U.ASSIMILATOR, U.REFINERY, U.EXTRACTOR}
WORKERS = {U.PROBE, U.SCV, U.DRONE}
STATIC_DEF = {U.PHOTONCANNON, U.SPINECRAWLER, U.BUNKER, U.MISSILETURRET, U.SPORECRAWLER}
CLOAK_HINTS = {U.DARKTEMPLAR, U.BANSHEE, U.DARKSHRINE, U.GHOST,
               U.ROACHWARREN, U.LURKERDENMP}
AIR_HINTS = {U.STARGATE, U.STARPORT, U.SPIRE, U.VOIDRAY, U.PHOENIX, U.ORACLE,
             U.MUTALISK, U.BANSHEE, U.LIBERATOR, U.CARRIER, U.TEMPEST}
# rough supply cost for estimating enemy army value from what we can see
ARMY_SUPPLY = {
    U.ZERGLING: 0.5, U.BANELING: 0.5, U.ROACH: 2, U.HYDRALISK: 2, U.QUEEN: 2,
    U.MUTALISK: 2, U.ULTRALISK: 6, U.LURKERMP: 3, U.RAVAGER: 3,
    U.ZEALOT: 2, U.STALKER: 2, U.ADEPT: 2, U.SENTRY: 2, U.IMMORTAL: 4,
    U.COLOSSUS: 6, U.ARCHON: 4, U.HIGHTEMPLAR: 2, U.DARKTEMPLAR: 2,
    U.VOIDRAY: 4, U.PHOENIX: 2, U.CARRIER: 6, U.TEMPEST: 5,
    U.MARINE: 1, U.MARAUDER: 2, U.HELLION: 2, U.SIEGETANK: 3, U.THOR: 6,
    U.CYCLONE: 3, U.MEDIVAC: 2, U.VIKINGFIGHTER: 2, U.BANSHEE: 3,
}


class Perception:
    def update(self, bot) -> dict:
        mem = getattr(bot, "enemy_memory", None)
        if mem is None:
            mem = {}
            bot.enemy_memory = mem

        enemies = bot.enemy_units | bot.enemy_structures
        home = bot.start_location

        def seen(types):
            return bot.enemy_structures.of_type(types).amount

        # max-ever counts (persist through fog)
        mem["enemy_base_count"] = max(mem.get("enemy_base_count") or 0, seen(TOWNHALLS)) or None
        mem["enemy_production_structures"] = max(
            mem.get("enemy_production_structures") or 0, seen(PRODUCTION))
        mem["enemy_gas_count"] = max(mem.get("enemy_gas_count") or 0, seen(GAS))
        mem["enemy_static_defense"] = max(mem.get("enemy_static_defense") or 0, seen(STATIC_DEF))

        # workers / army from what is visible right now (best effort)
        vis_workers = bot.enemy_units.of_type(WORKERS).amount
        mem["enemy_worker_count"] = max(mem.get("enemy_worker_count") or 0, vis_workers) or None
        army = sum(ARMY_SUPPLY.get(u.type_id, 0) for u in bot.enemy_units
                   if u.type_id not in WORKERS)
        if army:
            mem["enemy_army_supply"] = max(mem.get("enemy_army_supply") or 0.0, army)

        # qualitative flags
        if enemies:
            mem["last_scouted_time"] = bot.time
        if any(e.type_id in CLOAK_HINTS for e in enemies):
            mem["enemy_has_cloak"] = True
        if any(e.type_id in AIR_HINTS for e in enemies):
            mem["enemy_has_air"] = True
        # proxy: an enemy structure near our base
        if bot.enemy_structures and bot.enemy_structures.closest_distance_to(home) < 45:
            mem["enemy_proxy"] = True
        # army moving out: enemy army units near our base
        near = bot.enemy_units.filter(
            lambda u: u.type_id not in WORKERS and u.distance_to(home) < 55)
        mem["enemy_army_moving_out"] = near.amount >= 3

        return mem
