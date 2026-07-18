# Investigation: aiur_hard_zerg.SC2Replay

- map **Pylon AIE**, length **19.50**, our pid **1** — result: **LOSS**

## Verdict — COMBAT LOSS — built enough army (ratio 1.00) but lost it at bad trades (0.37); composition / engagement, not production

- peak workers 49 vs 60; floating(>700 min) samples 0
- army value produced 12375 vs 12325 (ratio 1.00); invested 36% of income into army vs enemy 31%
- overall trade 0.37 (killed 3750 / lost 10225)
- first decisive fight 12:00: lost 800 for 75 — trade 0.09

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

# Investigation: aiur_hard_terran.SC2Replay

- map **Pylon AIE**, length **13.13**, our pid **1** — result: **LOSS**

## Verdict — COMBAT LOSS — built enough army (ratio 1.45) but lost it at bad trades (0.36); composition / engagement, not production

- peak workers 49 vs 43; floating(>700 min) samples 0
- army value produced 4425 vs 3050 (ratio 1.45); invested 25% of income into army vs enemy 18%
- overall trade 0.36 (killed 1375 / lost 3850)
- first decisive fight 10:00: lost 1475 for 350 — trade 0.24

## Economy (workers | bases | minerals bank/inc | gas bank/inc)

| time | workers | bases | min bank/inc | gas bank/inc | wkr ratio |
|------|:-------:|:-----:|:------------:|:------------:|:---------:|
| 1:00 | 15 v 15 | 1 v 1 | 155/755 v 65/783 | 0/0 v 0/0 | 1.00 |
| 2:00 | 19 v 18 | 1 v 1 | 95/811 v 285/727 | 0/0 v 36/179 | 1.06 |
| 3:00 | 21 v 20 | 1 v 1 | 135/923 v 200/839 | 76/223 v 123/156 | 1.05 |
| 4:00 | 25 v 20 | 1 v 1 | 75/951 v 575/1063 | 192/313 v 331/291 | 1.25 |
| 5:00 | 26 v 21 | 1 v 1 | 215/979 v 625/951 | 324/358 v 538/335 | 1.24 |
| 6:00 | 27 v 24 | 2 v 1 | 35/979 v 860/1035 | 423/313 v 716/335 | 1.12 |
| 7:00 | 30 v 26 | 2 v 1 | 45/1091 v 1515/1315 | 451/291 v 898/335 | 1.15 |
| 8:00 | 35 v 25 | 2 v 1 | 10/1427 v 2200/1119 | 683/313 v 1076/313 | 1.40 |
| 9:00 | 42 v 25 | 2 v 2 | 10/1707 v 1525/979 | 821/492 v 779/313 | 1.68 |
| 10:00 | 49 v 25 | 2 v 2 | 245/1847 v 1415/1119 | 999/671 v 753/335 | 1.96 |
| 11:00 | 32 v 28 | 1 v 2 | 95/923 v 310/895 | 1195/358 v 206/358 | 1.14 |
| 12:00 | 20 v 36 ⚠️ | 1 v 2 | 95/643 v 30/1147 | 1359/358 v 400/694 | 0.56 |
| 13:00 | 20 v 43 ⚠️ | 1 v 2 | 35/475 v 135/1511 | 1607/335 v 752/604 | 0.47 |

## Accumulated — resources mined & army value produced

| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |
|------|:------------------:|:---------------------:|:-------------:|:---------:|
| 1:00 | 524/0/524 | 505/0/505 | 0 v 0 | 0% / 0% |
| 2:00 | 1321/0/1321 | 1297/14/1312 | 0 v 0 | 0% / 0% |
| 3:00 | 2230/59/2289 | 2057/171/2228 | 0 v 50 | 0% / 2% |
| 4:00 | 3157/342/3500 | 2971/435/3406 | 200 v 200 | 6% / 6% |
| 5:00 | 4099/655/4754 | 4006/752/4758 | 300 v 400 | 6% / 8% |
| 6:00 | 5069/975/6045 | 4947/1061/6009 | 575 v 750 | 10% / 12% |
| 7:00 | 6080/1303/7384 | 6132/1385/7517 | 775 v 1000 | 10% / 13% |
| 8:00 | 7190/1628/8818 | 7349/1709/9058 | 1175 v 1250 | 13% / 14% |
| 9:00 | 8752/1997/10750 | 8426/2029/10456 | 1575 v 1425 | 15% / 14% |
| 10:00 | 10548/2549/13097 | 9442/2335/11778 | 1875 v 1575 | 14% / 13% |
| 11:00 | 12269/3168/15437 | 10416/2637/13054 | 3250 v 1775 | 21% / 14% |
| 12:00 | 13029/3551/16581 | 11414/3196/14611 | 3650 v 2675 | 22% / 18% |
| 13:00 | 13602/3898/17500 | 12748/3853/16601 | 4425 v 2925 | 25% / 18% |

- **TOTAL mined** us 17635 vs enemy 16954 (ratio 1.04)
- **TOTAL army value produced** us 4425 vs enemy 3050 (ratio 1.45); invested 25% vs enemy 18%

## Army value + the fight each minute

| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |
|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|
| 1:00 | 0/0 | 0/0 | 1.0 | 0/0 | — |
| 2:00 | 0/0 | 0/0 | 1.0 | 0/0 | — |
| 3:00 | 0/0 | 50/1 | 0.0 | 0/0 | — |
| 4:00 | 200/4 | 200/4 | 1.0 | 0/0 | — |
| 5:00 | 300/6 | 400/8 | 0.8 | 0/0 | — |
| 6:00 | 575/10 | 750/14 | 0.8 | 1/0 | — |
| 7:00 | 675/12 | 1000/18 | 0.7 | 1/0 | — |
| 8:00 | 1075/20 | 1250/22 | 0.9 | 1/0 | — |
| 9:00 | 1275/24 | 1425/25 | 0.9 | 2/0 | skirm 200/0 — 0.00 |
| 10:00 | 100/2 | 1225/21 | 0.1 | 2/0 | **BATTLE** 1475/350 — 0.24 |
| 11:00 | 900/10 | 1275/22 | 0.7 | 2/3 | skirm 575/150 — 0.26 |
| 12:00 | 0/0 | 1800/26 | 0.0 | 3/4 | **BATTLE** 1300/375 — 0.29 |
| 13:00 | 575/8 | 1550/22 | 0.4 | 4/4 | skirm 200/500 — 2.50 |

## Decisive engagements (30s buckets, most value lost)

- **11:00** we lost 1000 (3xStalker, 1xImmortal, 1xZealot); they lost 250 (2xMarauder) — trade **0.25**
  - going in: us 900v/10s 3xStalker, 1xImmortal · enemy 1275v/22s 8xMarine, 7xMarauder
- **9:00** we lost 875 (7xZealot, 1xStalker); they lost 300 (6xMarine) — trade **0.34**
  - going in: us 1275v/24s 11xZealot, 1xStalker · enemy 1425v/25s 11xMarine, 7xMarauder
- **9:30** we lost 600 (6xZealot); they lost 50 (1xMarine) — trade **0.08**
  - going in: us 700v/14s 7xZealot · enemy 1175v/20s 7xMarauder, 6xMarine
- **10:00** we lost 400 (4xZealot); they lost 0 (-) — trade **0.00**
  - going in: us 100v/2s 1xZealot · enemy 1225v/21s 7xMarine, 7xMarauder
- **11:30** we lost 300 (3xZealot); they lost 125 (1xMarauder) — trade **0.42**
  - going in: us 200v/4s 2xZealot · enemy 1125v/20s 10xMarine, 5xMarauder
- **12:00** we lost 200 (2xZealot); they lost 500 (4xMarauder) — trade **2.50**
  - going in: us 0v/0s - · enemy 1800v/26s 12xMarine, 4xMarauder, 2xRaven, 1xWidowMine

## Peak composition @ 9:00 (1275v/24s)

- us: 11xZealot, 1xStalker
- enemy: 11xMarine, 7xMarauder
- our upgrades (4): ['ProtossGroundWeaponsLevel1', 'ProtossGroundArmorsLevel1', 'BlinkTech', 'ProtossGroundWeaponsLevel2']
- enemy upgrades (8): ['ShieldWall', 'Stimpack', 'TerranInfantryWeaponsLevel1', 'PunisherGrenades', 'TerranInfantryArmorsLevel1', 'HighCapacityBarrels', 'TerranVehicleWeaponsLevel1', 'TerranInfantryWeaponsLevel2']


---

# Investigation: aiur_hard_protoss.SC2Replay

- map **Pylon AIE**, length **09.59**, our pid **1** — result: **LOSS**

## Verdict — UNDER-INVESTED / GREED — too little into army (produced 0.42× enemy, 15% of income vs 30%); caught before teching up by an early timing

- peak workers 30 vs 26; floating(>700 min) samples 0
- army value produced 1350 vs 3225 (ratio 0.42); invested 15% of income into army vs enemy 30%
- overall trade 0.33 (killed 450 / lost 1350)
- first decisive fight 8:00: lost 800 for 225 — trade 0.28

## Economy (workers | bases | minerals bank/inc | gas bank/inc)

| time | workers | bases | min bank/inc | gas bank/inc | wkr ratio |
|------|:-------:|:-----:|:------------:|:------------:|:---------:|
| 1:00 | 15 v 15 | 1 v 1 | 165/783 v 175/811 | 0/0 v 0/0 | 1.00 |
| 2:00 | 19 v 19 | 1 v 1 | 120/867 v 320/923 | 0/0 v 36/179 | 1.00 |
| 3:00 | 22 v 20 | 1 v 1 | 130/895 v 400/867 | 80/201 v 148/156 | 1.10 |
| 4:00 | 24 v 20 | 1 v 1 | 100/923 v 430/811 | 200/335 v 251/313 | 1.20 |
| 5:00 | 26 v 21 | 1 v 1 | 210/1035 v 500/811 | 328/335 v 404/313 | 1.24 |
| 6:00 | 27 v 24 | 2 v 1 | 50/1007 v 555/923 | 431/313 v 561/335 | 1.12 |
| 7:00 | 30 v 26 | 2 v 1 | 100/1119 v 620/923 | 517/335 v 514/335 | 1.15 |
| 8:00 | 16 v 26 ⚠️ | 2 v 1 | 35/447 v 410/951 | 585/111 v 392/313 | 0.62 |
| 9:00 | 3 v 26 ⚠️ | 2 v 2 | 5/167 v 205/979 | 585/0 v 424/335 | 0.12 |

## Accumulated — resources mined & army value produced

| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |
|------|:------------------:|:---------------------:|:-------------:|:---------:|
| 1:00 | 535/0/535 | 521/0/521 | 0 v 0 | 0% / 0% |
| 2:00 | 1356/0/1356 | 1370/14/1385 | 0 v 0 | 0% / 0% |
| 3:00 | 2237/63/2300 | 2279/178/2457 | 0 v 100 | 0% / 4% |
| 4:00 | 3122/342/3465 | 3141/469/3610 | 200 v 225 | 6% / 6% |
| 5:00 | 4078/666/4745 | 3957/785/4743 | 300 v 575 | 6% / 12% |
| 6:00 | 5108/990/6099 | 4828/1095/5924 | 575 v 1125 | 9% / 19% |
| 7:00 | 6148/1311/7459 | 5817/1415/7232 | 775 v 1700 | 10% / 24% |
| 8:00 | 7136/1597/8734 | 6786/1739/8526 | 1250 v 2375 | 14% / 28% |
| 9:00 | 7280/1616/8896 | 7747/2056/9803 | 1350 v 3075 | 15% / 31% |

- **TOTAL mined** us 9040 vs enemy 10886 (ratio 0.83)
- **TOTAL army value produced** us 1350 vs enemy 3225 (ratio 0.42); invested 15% vs enemy 30%

## Army value + the fight each minute

| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |
|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|
| 1:00 | 0/0 | 0/0 | 1.0 | 0/0 | — |
| 2:00 | 0/0 | 0/0 | 1.0 | 0/0 | — |
| 3:00 | 0/0 | 100/2 | 0.0 | 0/0 | — |
| 4:00 | 200/4 | 225/4 | 0.9 | 0/0 | — |
| 5:00 | 300/6 | 575/10 | 0.5 | 0/0 | — |
| 6:00 | 575/10 | 1125/18 | 0.5 | 1/1 | — |
| 7:00 | 775/14 | 1700/26 | 0.5 | 1/1 | — |
| 8:00 | 450/6 | 2150/30 | 0.2 | 1/1 | **BATTLE** 800/225 — 0.28 |
| 9:00 | 0/0 | 2750/38 | 0.0 | 2/1 | skirm 550/100 — 0.18 |

## Decisive engagements (30s buckets, most value lost)

- **7:00** we lost 600 (6xZealot); they lost 125 (1xAdept) — trade **0.21**
  - going in: us 775v/14s 6xZealot, 1xStalker · enemy 1700v/26s 8xAdept, 2xZealot, 2xStalker, 1xSentry
- **8:00** we lost 450 (2xStalker, 1xZealot); they lost 100 (1xZealot) — trade **0.22**
  - going in: us 450v/6s 2xStalker, 1xZealot · enemy 2150v/30s 7xAdept, 5xStalker, 2xSentry, 1xZealot

## Peak composition @ 7:00 (775v/14s)

- us: 6xZealot, 1xStalker
- enemy: 8xAdept, 2xZealot, 2xStalker, 1xSentry
- our upgrades (2): ['ProtossGroundWeaponsLevel1', 'ProtossGroundArmorsLevel1']
- enemy upgrades (4): ['WarpGateResearch', 'ProtossGroundWeaponsLevel1', 'ProtossGroundArmorsLevel1', 'BlinkTech']


---
