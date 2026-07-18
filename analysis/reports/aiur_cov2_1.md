# Investigation: aiur_cov2_1.SC2Replay

- map **Pylon AIE**, length **18.52**, our pid **1** — result: **LOSS**

## Verdict — UNDER-INVESTED / GREED — too little into army (produced 0.50× enemy, 19% of income vs 24%); caught before teching up

- peak workers 42 vs 60; floating(>700 min) samples 7
- army value produced 3675 vs 7400 (ratio 0.50); invested 19% of income into army vs enemy 24%
- overall trade 1.97 (killed 3500 / lost 1775)
- first decisive fight 15:00: went in at army value 1900 vs 2900 (**ratio 0.66**), supply 22 vs 28; lost 525 for 200 — trade 0.38

## Economy (workers | bases | minerals bank/inc | gas bank/inc)

| time | workers | bases | min bank/inc | gas bank/inc | wkr ratio |
|------|:-------:|:-----:|:------------:|:------------:|:---------:|
| 1:00 | 15 v 15 | 1 v 1 | 160/755 v 20/783 | 0/0 v 0/0 | 1.00 |
| 2:00 | 18 v 17 | 1 v 1 | 25/895 v 325/839 | 0/0 v 24/134 | 1.06 |
| 3:00 | 21 v 17 | 1 v 1 | 115/839 v 260/699 | 96/246 v 144/179 | 1.24 |
| 4:00 | 24 v 19 | 1 v 1 | 150/923 v 255/755 | 200/335 v 226/313 | 1.26 |
| 5:00 | 26 v 19 | 1 v 1 | 305/1007 v 255/783 | 278/313 v 262/358 | 1.37 |
| 6:00 | 27 v 20 | 2 v 1 | 40/1147 v 205/755 | 285/335 v 344/335 | 1.35 |
| 7:00 | 31 v 23 | 2 v 1 | 70/1119 v 100/839 | 413/335 v 422/335 | 1.35 |
| 8:00 | 36 v 26 | 2 v 1 | 35/979 v 765/1035 | 545/335 v 654/335 | 1.38 |
| 9:00 | 42 v 25 | 2 v 2 | 30/1119 v 760/1035 | 497/403 v 582/335 | 1.68 |
| 10:00 | 39 v 25 | 1 v 2 | 25/27 v 935/951 | 489/0 v 664/313 | 1.56 |
| 11:00 | 39 v 35 | 1 v 2 | 460/1035 v 550/1343 | 555/313 v 442/380 | 1.11 |
| 12:00 | 39 v 44 | 1 v 2 | 750/755 v 760/1651 | 591/358 v 482/447 | 0.89 |
| 13:00 | 39 v 45 | 1 v 2 | 880/643 v 580/1679 | 673/335 v 394/649 | 0.87 |
| 14:00 | 39 v 45 | 1 v 2 | 770/559 v 650/1679 | 605/335 v 612/671 | 0.87 |
| 15:00 | 39 v 45 | 1 v 3 | 940/559 v 875/1707 | 737/313 v 522/649 | 0.87 |
| 16:00 | 39 v 45 | 1 v 3 | 1110/559 v 1925/1735 | 869/313 v 886/649 | 0.87 |
| 17:00 | 39 v 58 ⚠️ | 1 v 3 | 1330/615 v 1500/2155 | 901/313 v 826/627 | 0.67 |
| 18:00 | 39 v 60 ⚠️ | 1 v 3 | 1750/643 v 2200/2043 | 1133/313 v 1160/985 | 0.65 |

## Accumulated — resources mined & army value produced

| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |
|------|:------------------:|:---------------------:|:-------------:|:---------:|
| 1:00 | 512/0/512 | 547/0/547 | 0 v 200 | 0% / 37% |
| 2:00 | 1286/0/1286 | 1363/3/1366 | 0 v 200 | 0% / 15% |
| 3:00 | 2143/85/2229 | 2122/163/2286 | 0 v 450 | 0% / 20% |
| 4:00 | 3024/353/3378 | 2849/461/3311 | 100 v 550 | 3% / 17% |
| 5:00 | 3975/673/4649 | 3618/785/4404 | 100 v 850 | 2% / 19% |
| 6:00 | 4982/986/5969 | 4383/1113/5496 | 275 v 1300 | 5% / 24% |
| 7:00 | 6111/1314/7425 | 5170/1430/6601 | 725 v 1900 | 10% / 29% |
| 8:00 | 7076/1638/8714 | 6121/1757/7879 | 1075 v 2050 | 12% / 26% |
| 9:00 | 8078/1977/10056 | 7114/2085/9200 | 1425 v 2050 | 14% / 22% |
| 10:00 | 8670/2186/10856 | 8103/2409/10512 | 1425 v 2475 | 13% / 24% |
| 11:00 | 9467/2428/11895 | 9100/2718/11819 | 1425 v 3025 | 12% / 26% |
| 12:00 | 10371/2744/13116 | 10537/3177/13714 | 1425 v 3050 | 11% / 22% |
| 13:00 | 11122/3072/14194 | 12183/3717/15901 | 2450 v 3850 | 17% / 24% |
| 14:00 | 11723/3396/15119 | 13857/4363/18221 | 2625 v 4400 | 17% / 24% |
| 15:00 | 12310/3724/16034 | 15527/5015/20543 | 2625 v 4550 | 16% / 22% |
| 16:00 | 12887/4048/16936 | 17206/5668/22875 | 3500 v 5350 | 21% / 23% |
| 17:00 | 13465/4372/17838 | 18815/6295/25110 | 3675 v 5900 | 21% / 23% |
| 18:00 | 14052/4700/18752 | 20998/7164/28162 | 3675 v 6850 | 20% / 24% |

- **TOTAL mined** us 19518 vs enemy 30793 (ratio 0.63)
- **TOTAL army value produced** us 3675 vs enemy 7400 (ratio 0.50); invested 19% vs enemy 24%

## Army value + the fight each minute

| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |
|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|
| 1:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 2:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 3:00 | 0/0 | 450/6 | 0.0 | 0/0 | — |
| 4:00 | 100/2 | 550/8 | 0.2 | 0/0 | — |
| 5:00 | 0/0 | 850/14 | 0.0 | 0/0 | — |
| 6:00 | 175/2 | 1300/22 | 0.1 | 1/0 | — |
| 7:00 | 625/8 | 1900/28 | 0.3 | 1/0 | — |
| 8:00 | 975/12 | 2050/30 | 0.5 | 2/0 | — |
| 9:00 | 1325/16 | 2050/30 | 0.6 | 2/0 | — |
| 10:00 | 875/10 | 2275/29 | 0.4 | 2/0 | skirm 450/200 — 0.44 |
| 11:00 | 700/8 | 1525/13 | 0.5 | 2/0 | **BATTLE** 175/1300 — 7.43 |
| 12:00 | 700/8 | 1550/14 | 0.5 | 3/2 | — |
| 13:00 | 1725/20 | 2350/22 | 0.7 | 3/4 | — |
| 14:00 | 1900/22 | 2900/28 | 0.7 | 4/5 | — |
| 15:00 | 1375/16 | 2850/28 | 0.5 | 4/5 | skirm 525/200 — 0.38 |
| 16:00 | 1725/20 | 1850/12 | 0.9 | 4/6 | **BATTLE** 525/1800 — 3.43 |
| 17:00 | 1900/22 | 2400/16 | 0.8 | 5/7 | — |
| 18:00 | 1900/22 | 3350/24 | 0.6 | 5/7 | — |

## Decisive engagements (30s buckets, most value lost)

- **15:00** we lost 525 (3xStalker); they lost 1375 (5xMutalisk, 4xBaneling, 3xZergling) — trade **2.62**
  - going in: us 1375v/16s 5xStalker, 1xColossus · enemy 2850v/28s 7xMutalisk, 4xBaneling, 4xZergling, 3xOverseer, 3xQueen
- **14:30** we lost 350 (2xStalker); they lost 200 (1xMutalisk) — trade **0.57**
  - going in: us 1725v/20s 7xStalker, 1xColossus · enemy 3050v/30s 8xMutalisk, 4xBaneling, 4xZergling, 3xOverseer, 3xQueen
- **10:30** we lost 175 (1xStalker); they lost 400 (2xHydralisk, 1xRoach) — trade **2.29**
  - going in: us 875v/10s 5xStalker · enemy 1525v/15s 4xBaneling, 3xOverseer, 3xZergling, 2xHydralisk, 1xQueen, 1xRoach
- **10:00** we lost 0 (-); they lost 900 (6xRoach, 2xHydralisk) — trade **9.90**
  - going in: us 875v/10s 5xStalker · enemy 2275v/29s 7xRoach, 4xHydralisk, 3xOverseer, 3xZergling, 2xBaneling, 1xQueen
- **15:30** we lost 0 (-); they lost 425 (2xMutalisk, 1xZergling) — trade **9.90**
  - going in: us 1200v/14s 4xStalker, 1xColossus · enemy 2275v/17s 3xOverseer, 3xQueen, 2xMutalisk, 1xZergling, 1xBroodLord, 1xInfestor

## Peak composition @ 14:00 (1900v/22s)

- us: 8xStalker, 1xColossus
- enemy: 8xMutalisk, 4xBaneling, 4xZergling, 3xOverseer, 2xQueen
- our upgrades (7): ['ProtossGroundArmorsLevel1', 'ProtossGroundWeaponsLevel1', 'Charge', 'ProtossGroundArmorsLevel2', 'ProtossGroundWeaponsLevel2', 'ProtossGroundArmorsLevel3', 'ProtossGroundWeaponsLevel3']
- enemy upgrades (14): ['ZergMeleeWeaponsLevel1', 'zerglingmovementspeed', 'Burrow', 'CentrificalHooks', 'ZergMissileWeaponsLevel1', 'overlordspeed', 'ZergGroundArmorsLevel1', 'ZergMeleeWeaponsLevel2', 'ZergGroundArmorsLevel2', 'ZergFlyerWeaponsLevel1', 'ZergFlyerArmorsLevel1', 'ZergMissileWeaponsLevel2', 'ZergMeleeWeaponsLevel3', 'ZergFlyerWeaponsLevel2']


---
