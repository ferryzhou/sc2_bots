# Investigation: aiur_hard_zerg.SC2Replay

- map **Pylon AIE**, length **19.50**, our pid **1** — result: **LOSS**

## Verdict — COMBAT LOSS — built enough army (ratio 1.00) but lost it at bad trades (0.37); composition / engagement, not production

- peak workers 49 vs 60; floating(>700 min) samples 0
- army value produced 12375 vs 12325 (ratio 1.00); invested 36% of income into army vs enemy 31%
- overall trade 0.37 (killed 3750 / lost 10225)
- first decisive fight 12:00: went in at army value 2350 vs 3325 (**ratio 0.71**), supply 44 vs 43; lost 800 for 75 — trade 0.09

## Economy (workers | bases | minerals bank/inc | gas bank/inc)

| time | workers | bases | min bank/inc | gas bank/inc | wkr ratio |
|------|:-------:|:-----:|:------------:|:------------:|:---------:|
| 1:00 | 15 v 14 | 1 v 1 | 170/783 v 175/755 | 0/0 v 0/0 | 1.07 |
| 2:00 | 18 v 16 | 1 v 2 | 15/867 v 105/839 | 0/0 v 0/0 | 1.12 |
| 3:00 | 22 v 17 | 1 v 2 | 120/923 v 80/895 | 84/201 v 72/134 | 1.29 |
| 4:00 | 24 v 18 | 1 v 2 | 55/951 v 255/951 | 196/313 v 63/179 | 1.33 |
| 5:00 | 26 v 22 | 1 v 2 | 215/1063 v 245/783 | 328/358 v 59/335 | 1.18 |
| 6:00 | 26 v 30 | 2 v 2 | 105/1035 v 185/867 | 431/358 v 316/604 | 0.87 |
| 7:00 | 29 v 30 | 2 v 2 | 105/1063 v 220/1063 | 555/313 v 555/671 | 0.97 |
| 8:00 | 34 v 41 ⚠️ | 2 v 2 | 75/1343 v 275/1511 | 687/335 v 919/671 | 0.83 |
| 9:00 | 41 v 50 ⚠️ | 2 v 2 | 30/1707 v 540/1903 | 793/380 v 1104/671 | 0.82 |
| 10:00 | 48 v 48 | 2 v 2 | 110/1623 v 685/1959 | 901/627 v 1118/649 | 1.00 |
| 11:00 | 49 v 49 | 2 v 2 | 260/1819 v 310/1987 | 1153/604 v 1049/627 | 1.00 |
| 12:00 | 49 v 51 | 2 v 2 | 185/1511 v 1205/2015 | 1259/627 v 1326/649 | 0.96 |
| 13:00 | 49 v 51 | 2 v 2 | 65/1567 v 2460/2099 | 1423/649 v 1719/671 | 0.96 |
| 14:00 | 49 v 50 | 2 v 3 | 100/1483 v 1705/1847 | 1887/671 v 987/671 | 0.98 |
| 15:00 | 49 v 49 | 2 v 3 | 95/1567 v 2210/1511 | 2151/649 v 893/649 | 1.00 |
| 16:00 | 49 v 57 | 2 v 3 | 90/1511 v 1430/1819 | 2615/649 v 933/604 | 0.86 |
| 17:00 | 49 v 58 ⚠️ | 2 v 3 | 50/1315 v 2165/2043 | 3079/627 v 1439/918 | 0.84 |
| 18:00 | 49 v 59 ⚠️ | 2 v 3 | 30/1427 v 2480/1903 | 3547/649 v 1638/940 | 0.83 |
| 19:00 | 49 v 60 ⚠️ | 2 v 4 | 110/1315 v 1700/2099 | 4015/671 v 530/963 | 0.82 |

## Accumulated — resources mined & army value produced

| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |
|------|:------------------:|:---------------------:|:-------------:|:---------:|
| 1:00 | 533/0/533 | 524/0/524 | 0 v 200 | 0% / 38% |
| 2:00 | 1339/0/1339 | 1377/0/1377 | 0 v 200 | 0% / 15% |
| 3:00 | 2230/77/2308 | 2262/70/2333 | 0 v 400 | 0% / 17% |
| 4:00 | 3134/349/3484 | 3073/219/3292 | 100 v 625 | 3% / 19% |
| 5:00 | 4090/666/4756 | 3884/457/4342 | 300 v 825 | 6% / 19% |
| 6:00 | 5153/986/6140 | 4798/874/5673 | 575 v 1375 | 9% / 24% |
| 7:00 | 6188/1311/7499 | 5842/1512/7355 | 675 v 1725 | 9% / 23% |
| 8:00 | 7209/1635/8844 | 7059/2158/9217 | 1075 v 2225 | 12% / 24% |
| 9:00 | 8748/1985/10733 | 8701/2807/11508 | 1475 v 2375 | 14% / 21% |
| 10:00 | 10469/2496/12965 | 10679/3456/14135 | 1850 v 2825 | 14% / 20% |
| 11:00 | 12199/3134/15333 | 12684/4105/16790 | 2350 v 3325 | 15% / 20% |
| 12:00 | 13939/3764/17703 | 14629/4743/19372 | 3700 v 4025 | 21% / 21% |
| 13:00 | 15473/4413/19887 | 16612/5388/22000 | 4900 v 4075 | 25% / 19% |
| 14:00 | 16979/5070/22050 | 18608/6037/24645 | 6175 v 4925 | 28% / 20% |
| 15:00 | 18514/5723/24237 | 20212/6675/26888 | 7300 v 6175 | 30% / 23% |
| 16:00 | 20034/6379/26413 | 21677/7287/28964 | 8475 v 6475 | 32% / 22% |
| 17:00 | 21526/7028/28555 | 23575/8152/31728 | 9675 v 7225 | 34% / 23% |
| 18:00 | 22986/7681/30667 | 25329/9007/34336 | 10675 v 7425 | 35% / 22% |
| 19:00 | 24366/8326/32693 | 27367/9984/37352 | 11675 v 9175 | 36% / 25% |

- **TOTAL mined** us 34253 vs enemy 39920 (ratio 0.86)
- **TOTAL army value produced** us 12375 vs enemy 12325 (ratio 1.00); invested 36% vs enemy 31%

## Army value + the fight each minute

| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |
|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|
| 1:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 2:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 3:00 | 0/0 | 400/0 | 0.0 | 0/0 | — |
| 4:00 | 100/2 | 625/5 | 0.2 | 0/0 | — |
| 5:00 | 300/6 | 825/8 | 0.4 | 0/0 | — |
| 6:00 | 575/10 | 1375/13 | 0.4 | 1/0 | — |
| 7:00 | 675/12 | 1725/19 | 0.4 | 1/0 | — |
| 8:00 | 1075/20 | 2225/26 | 0.5 | 1/0 | — |
| 9:00 | 1475/28 | 2375/28 | 0.6 | 2/0 | — |
| 10:00 | 1850/34 | 2825/35 | 0.7 | 2/0 | — |
| 11:00 | 2350/44 | 3325/43 | 0.7 | 3/1 | — |
| 12:00 | 2900/44 | 3950/50 | 0.7 | 3/2 | **BATTLE** 800/75 — 0.09 |
| 13:00 | 2600/38 | 3450/42 | 0.8 | 4/2 | **BATTLE** 1500/550 — 0.37 |
| 14:00 | 2525/44 | 3850/48 | 0.7 | 4/3 | **BATTLE** 1350/450 — 0.33 |
| 15:00 | 1500/24 | 4350/57 | 0.3 | 4/5 | **BATTLE** 2150/750 — 0.35 |
| 16:00 | 1650/30 | 3250/42 | 0.5 | 5/7 | **BATTLE** 1025/1400 — 1.37 |
| 17:00 | 2350/44 | 3825/49 | 0.6 | 5/8 | skirm 500/175 — 0.35 |
| 18:00 | 1950/36 | 3875/49 | 0.5 | 5/9 | **BATTLE** 1400/150 — 0.11 |
| 19:00 | 2150/40 | 5425/64 | 0.4 | 5/10 | **BATTLE** 800/200 — 0.25 |

## Decisive engagements (30s buckets, most value lost)

- **14:00** we lost 1475 (11xZealot, 1xImmortal); they lost 750 (3xRavager, 1xHydralisk) — trade **0.51**
  - going in: us 2525v/44s 18xZealot, 2xStalker, 1xImmortal · enemy 3850v/48s 10xHydralisk, 5xRoach, 4xRavager, 3xOverseer, 3xQueen
- **12:30** we lost 1100 (3xStalker, 2xZealot, 1xImmortal); they lost 550 (4xRoach, 1xHydralisk) — trade **0.50**
  - going in: us 3325v/46s 10xZealot, 9xStalker, 2xImmortal · enemy 4000v/52s 10xHydralisk, 6xRoach, 4xRavager, 3xOverseer, 3xQueen, 2xZergling
- **15:00** we lost 1025 (5xZealot, 3xStalker); they lost 950 (5xHydralisk, 1xRavager) — trade **0.93**
  - going in: us 1500v/24s 8xZealot, 4xStalker · enemy 4350v/57s 12xRoach, 9xHydralisk, 3xOverseer, 3xQueen, 2xInfestor, 2xZergling
- **17:30** we lost 1000 (10xZealot); they lost 150 (2xZergling, 1xRoach) — trade **0.15**
  - going in: us 2350v/44s 20xZealot, 2xStalker · enemy 3875v/51s 12xRoach, 7xHydralisk, 3xOverseer, 3xQueen, 3xZergling, 2xInfestor
- **11:00** we lost 800 (8xZealot); they lost 75 (3xZergling) — trade **0.09**
  - going in: us 2350v/44s 20xZealot, 2xStalker · enemy 3325v/43s 7xHydralisk, 5xRoach, 4xRavager, 3xOverseer, 3xZergling, 2xQueen
- **18:30** we lost 800 (8xZealot); they lost 200 (2xZergling, 1xQueen) — trade **0.25**
  - going in: us 2450v/46s 21xZealot, 2xStalker · enemy 4325v/56s 12xRoach, 7xHydralisk, 4xQueen, 3xOverseer, 3xZergling, 2xInfestor

## Peak composition @ 12:00 (2900v/44s)

- us: 13xZealot, 7xStalker, 1xImmortal
- enemy: 10xHydralisk, 6xRoach, 4xRavager, 3xOverseer, 3xQueen
- our upgrades (5): ['ProtossGroundArmorsLevel1', 'ProtossGroundWeaponsLevel1', 'Charge', 'ProtossGroundArmorsLevel2', 'ProtossGroundWeaponsLevel2']
- enemy upgrades (20): ['Burrow', 'ZergGroundArmorsLevel1', 'ZergMissileWeaponsLevel1', 'overlordspeed', 'ZergMeleeWeaponsLevel1', 'GlialReconstitution', 'ZergFlyerWeaponsLevel1', 'ZergGroundArmorsLevel2', 'ZergMissileWeaponsLevel2', 'ZergFlyerArmorsLevel1', 'ZergMeleeWeaponsLevel2', 'NeuralParasite', 'ChitinousPlating', 'TunnelingClaws', 'ZergGroundArmorsLevel3', 'ZergFlyerWeaponsLevel2', 'ZergMissileWeaponsLevel3', 'ZergFlyerArmorsLevel2', 'ZergMeleeWeaponsLevel3', 'ZergFlyerWeaponsLevel3']


---
