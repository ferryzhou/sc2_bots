# Investigation: aiur_hard_zerg_fixed2.SC2Replay

- map **Pylon AIE**, length **21.21**, our pid **1** — result: **LOSS**

## Verdict — COMBAT LOSS — built enough army (ratio 0.91) but lost it at bad trades (0.52); composition / engagement, not production

- peak workers 61 vs 60; floating(>700 min) samples 0
- army value produced 9575 vs 10500 (ratio 0.91); invested 26% of income into army vs enemy 29%
- overall trade 0.52 (killed 4700 / lost 9050)
- first decisive fight 15:00: went in at army value 3700 vs 3250 (**ratio 1.14**), supply 44 vs 50; lost 4050 for 850 — trade 0.21

## Economy (workers | bases | minerals bank/inc | gas bank/inc)

| time | workers | bases | min bank/inc | gas bank/inc | wkr ratio |
|------|:-------:|:-----:|:------------:|:------------:|:---------:|
| 1:00 | 15 v 15 | 1 v 1 | 165/755 v 20/783 | 0/0 v 0/0 | 1.00 |
| 2:00 | 18 v 17 | 1 v 1 | 25/923 v 340/839 | 0/0 v 24/134 | 1.06 |
| 3:00 | 21 v 16 | 1 v 1 | 60/923 v 170/727 | 84/201 v 90/179 | 1.31 |
| 4:00 | 25 v 19 | 1 v 1 | 85/951 v 110/643 | 100/291 v 222/335 | 1.32 |
| 5:00 | 26 v 20 | 1 v 1 | 5/1035 v 105/811 | 249/313 v 304/335 | 1.30 |
| 6:00 | 28 v 20 | 2 v 1 | 30/1063 v 35/755 | 227/313 v 386/335 | 1.40 |
| 7:00 | 32 v 26 | 2 v 1 | 50/895 v 285/1007 | 355/291 v 614/313 | 1.23 |
| 8:00 | 39 v 26 | 2 v 1 | 65/1623 v 735/1007 | 195/335 v 725/335 | 1.50 |
| 9:00 | 41 v 25 | 2 v 1 | 265/1791 v 655/1035 | 381/515 v 749/335 | 1.64 |
| 10:00 | 40 v 24 | 1 v 2 | 325/1035 v 605/895 | 321/358 v 694/313 | 1.67 |
| 11:00 | 42 v 24 | 2 v 2 | 80/923 v 335/755 | 459/403 v 522/291 | 1.75 |
| 12:00 | 46 v 34 | 2 v 2 | 80/1035 v 270/1399 | 671/447 v 600/291 | 1.35 |
| 13:00 | 49 v 37 | 2 v 2 | 275/1539 v 160/1511 | 765/627 v 832/313 | 1.32 |
| 14:00 | 53 v 37 | 3 v 3 | 55/1539 v 130/1595 | 1037/671 v 810/313 | 1.43 |
| 15:00 | 59 v 37 | 3 v 3 | 90/1679 v 395/1623 | 1201/694 v 467/313 | 1.59 |
| 16:00 | 59 v 45 | 3 v 3 | 95/2127 v 115/1063 | 1407/649 v 111/380 | 1.31 |
| 17:00 | 44 v 60 ⚠️ | 2 v 3 | 60/1399 v 265/1959 | 1433/739 v 460/783 | 0.73 |
| 18:00 | 49 v 58 ⚠️ | 2 v 3 | 320/1707 v 585/2407 | 1717/694 v 265/828 | 0.84 |
| 19:00 | 53 v 60 | 3 v 3 | 110/1567 v 825/2127 | 1951/649 v 363/963 | 0.88 |
| 20:00 | 61 v 60 | 3 v 3 | 60/1287 v 1745/2407 | 2201/716 v 438/985 | 1.02 |
| 21:00 | 40 v 60 ⚠️ | 3 v 4 | 25/1007 v 1740/2323 | 2603/739 v 276/940 | 0.67 |

## Accumulated — resources mined & army value produced

| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |
|------|:------------------:|:---------------------:|:-------------:|:---------:|
| 1:00 | 521/0/521 | 547/0/547 | 0 v 200 | 0% / 37% |
| 2:00 | 1309/0/1309 | 1367/3/1371 | 0 v 200 | 0% / 15% |
| 3:00 | 2204/74/2278 | 2127/159/2287 | 0 v 600 | 0% / 26% |
| 4:00 | 3080/353/3434 | 2775/450/3225 | 0 v 750 | 0% / 23% |
| 5:00 | 4050/666/4717 | 3511/774/4285 | 0 v 1425 | 0% / 33% |
| 6:00 | 5108/979/6088 | 4308/1098/5406 | 275 v 1900 | 5% / 35% |
| 7:00 | 6195/1303/7498 | 5142/1422/6565 | 475 v 2175 | 6% / 33% |
| 8:00 | 7468/1631/9099 | 6126/1746/7872 | 475 v 2175 | 5% / 28% |
| 9:00 | 9193/2071/11265 | 7170/2059/9230 | 475 v 2775 | 4% / 30% |
| 10:00 | 10560/2436/12996 | 8187/2375/10563 | 1025 v 2875 | 8% / 27% |
| 11:00 | 11534/2827/14362 | 9086/2699/11786 | 2075 v 3525 | 14% / 30% |
| 12:00 | 12490/3253/15743 | 10089/3012/13102 | 2425 v 4125 | 15% / 31% |
| 13:00 | 13847/3849/17696 | 11534/3333/14868 | 2775 v 4275 | 16% / 29% |
| 14:00 | 15367/4498/19866 | 13083/3653/16736 | 3700 v 4275 | 19% / 26% |
| 15:00 | 16985/5132/22118 | 14696/3977/18674 | 4575 v 4775 | 21% / 26% |
| 16:00 | 18664/5778/24443 | 16165/4309/20475 | 5450 v 5800 | 22% / 28% |
| 17:00 | 20385/6423/26809 | 17760/4958/22719 | 5975 v 6050 | 22% / 27% |
| 18:00 | 21794/7110/28904 | 20093/5753/25846 | 6350 v 6600 | 22% / 26% |
| 19:00 | 23412/7796/31209 | 22262/6629/28891 | 7650 v 7950 | 25% / 28% |
| 20:00 | 24993/8494/33487 | 24459/7599/32059 | 8875 v 8050 | 27% / 25% |
| 21:00 | 26387/9259/35646 | 26810/8573/35383 | 9225 v 9900 | 26% / 28% |

- **TOTAL mined** us 36205 vs enemy 36437 (ratio 0.99)
- **TOTAL army value produced** us 9575 vs enemy 10500 (ratio 0.91); invested 26% vs enemy 29%

## Army value + the fight each minute

| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |
|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|
| 1:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 2:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 3:00 | 0/0 | 600/6 | 0.0 | 0/0 | — |
| 4:00 | 0/0 | 750/10 | 0.0 | 0/0 | — |
| 5:00 | 0/0 | 1425/21 | 0.0 | 0/0 | — |
| 6:00 | 275/4 | 1900/32 | 0.1 | 1/0 | — |
| 7:00 | 475/8 | 2175/35 | 0.2 | 1/1 | — |
| 8:00 | 475/8 | 2150/34 | 0.2 | 2/1 | — |
| 9:00 | 475/8 | 1850/30 | 0.3 | 3/1 | **BATTLE** 0/900 — 9.90 |
| 10:00 | 1025/14 | 1850/28 | 0.6 | 3/1 | — |
| 11:00 | 2075/26 | 2500/40 | 0.8 | 4/2 | — |
| 12:00 | 2425/30 | 3100/48 | 0.8 | 4/3 | — |
| 13:00 | 2775/34 | 3250/50 | 0.9 | 4/3 | — |
| 14:00 | 3700/44 | 3250/50 | 1.1 | 4/4 | — |
| 15:00 | 525/6 | 2900/38 | 0.2 | 4/4 | **BATTLE** 4050/850 — 0.21 |
| 16:00 | 350/4 | 3925/49 | 0.1 | 5/6 | **BATTLE** 1050/0 — 0.00 |
| 17:00 | 350/4 | 4075/49 | 0.1 | 5/6 | skirm 525/100 — 0.19 |
| 18:00 | 375/4 | 3375/39 | 0.1 | 5/6 | **BATTLE** 350/1250 — 3.57 |
| 19:00 | 1675/18 | 4525/54 | 0.4 | 5/6 | skirm 0/200 — 9.90 |
| 20:00 | 2900/32 | 4500/53 | 0.6 | 6/7 | — |
| 21:00 | 175/2 | 5200/57 | 0.0 | 6/9 | **BATTLE** 3075/1150 — 0.37 |

## Decisive engagements (30s buckets, most value lost)

- **20:00** we lost 2900 (8xStalker, 4xImmortal); they lost 1150 (10xRoach, 1xHydralisk) — trade **0.40**
  - going in: us 2900v/32s 8xStalker, 4xImmortal · enemy 4500v/53s 11xRoach, 6xHydralisk, 4xQueen, 4xInfestor, 3xOverseer, 1xViper
- **14:00** we lost 2075 (3xZealot, 3xStalker, 2xImmortal, 1xColossus); they lost 475 (13xZergling, 1xHydralisk) — trade **0.23**
  - going in: us 3700v/44s 8xStalker, 4xImmortal, 3xZealot, 1xColossus · enemy 3250v/50s 16xZergling, 10xRoach, 6xHydralisk, 4xOverseer, 1xQueen
- **14:30** we lost 1975 (7xStalker, 2xImmortal); they lost 375 (3xZergling, 1xOverseer, 1xRoach) — trade **0.19**
  - going in: us 2150v/24s 8xStalker, 2xImmortal · enemy 3075v/39s 10xRoach, 5xHydralisk, 4xOverseer, 3xQueen, 3xZergling
- **15:00** we lost 525 (3xStalker); they lost 0 (-) — trade **0.00**
  - going in: us 525v/6s 3xStalker · enemy 2900v/38s 11xRoach, 5xHydralisk, 3xQueen, 3xOverseer
- **15:30** we lost 525 (3xStalker); they lost 0 (-) — trade **0.00**
  - going in: us 525v/6s 3xStalker · enemy 3425v/45s 12xRoach, 6xHydralisk, 3xQueen, 3xOverseer, 1xZergling, 1xInfestor
- **16:00** we lost 350 (2xStalker); they lost 0 (-) — trade **0.00**
  - going in: us 350v/4s 2xStalker · enemy 3925v/49s 12xRoach, 6xHydralisk, 3xQueen, 3xOverseer, 3xInfestor, 1xZergling

## Peak composition @ 14:00 (3700v/44s)

- us: 8xStalker, 4xImmortal, 3xZealot, 1xColossus
- enemy: 16xZergling, 10xRoach, 6xHydralisk, 4xOverseer, 1xQueen
- our upgrades (6): ['ProtossGroundArmorsLevel1', 'ProtossGroundWeaponsLevel1', 'Charge', 'ProtossGroundArmorsLevel2', 'ProtossGroundWeaponsLevel2', 'ProtossGroundArmorsLevel3']
- enemy upgrades (17): ['zerglingmovementspeed', 'ZergMeleeWeaponsLevel1', 'Burrow', 'ZergMissileWeaponsLevel1', 'overlordspeed', 'ZergGroundArmorsLevel1', 'GlialReconstitution', 'ZergMeleeWeaponsLevel2', 'ZergGroundArmorsLevel2', 'ZergFlyerWeaponsLevel1', 'NeuralParasite', 'ZergMissileWeaponsLevel2', 'TunnelingClaws', 'ZergMeleeWeaponsLevel3', 'ZergFlyerArmorsLevel1', 'ZergGroundArmorsLevel3', 'ZergMissileWeaponsLevel3']


---
