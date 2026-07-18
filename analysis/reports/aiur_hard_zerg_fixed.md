# Investigation: aiur_hard_zerg_fixed.SC2Replay

- map **Pylon AIE**, length **27.32**, our pid **1** — result: **LOSS**

## Verdict — MIXED — trade 1.08, army-made ratio 1.07; see metrics

- peak workers 51 vs 60; floating(>700 min) samples 0
- army value produced 13350 vs 12475 (ratio 1.07); invested 39% of income into army vs enemy 22%
- overall trade 1.08 (killed 8525 / lost 7875)

## Economy (workers | bases | minerals bank/inc | gas bank/inc)

| time | workers | bases | min bank/inc | gas bank/inc | wkr ratio |
|------|:-------:|:-----:|:------------:|:------------:|:---------:|
| 1:00 | 15 v 15 | 1 v 1 | 155/727 v 25/811 | 0/0 v 0/0 | 1.00 |
| 2:00 | 18 v 17 | 1 v 1 | 20/895 v 325/755 | 0/0 v 20/111 | 1.06 |
| 3:00 | 21 v 17 | 1 v 1 | 90/839 v 260/783 | 96/223 v 136/156 | 1.24 |
| 4:00 | 24 v 20 | 1 v 1 | 90/951 v 300/783 | 208/335 v 314/313 | 1.20 |
| 5:00 | 26 v 22 | 1 v 1 | 105/1007 v 245/839 | 432/291 v 146/313 | 1.18 |
| 6:00 | 29 v 24 | 2 v 1 | 15/1063 v 190/951 | 264/313 v 249/313 | 1.21 |
| 7:00 | 32 v 26 | 2 v 1 | 60/979 v 580/1035 | 317/313 v 435/358 | 1.23 |
| 8:00 | 40 v 26 | 2 v 1 | 30/1735 v 1325/951 | 265/358 v 667/358 | 1.54 |
| 9:00 | 47 v 25 | 2 v 2 | 25/1707 v 1355/1035 | 399/627 v 695/313 | 1.88 |
| 10:00 | 49 v 24 | 2 v 2 | 70/1903 v 1660/951 | 517/649 v 777/313 | 2.04 |
| 11:00 | 51 v 33 | 2 v 2 | 30/811 v 875/699 | 623/313 v 672/291 | 1.55 |
| 12:00 | 51 v 43 | 2 v 2 | 50/699 v 905/1539 | 675/425 v 687/671 | 1.19 |
| 13:00 | 51 v 46 | 2 v 2 | 120/1427 v 555/1623 | 543/403 v 418/649 | 1.11 |
| 14:00 | 51 v 45 | 2 v 2 | 120/1315 v 555/1679 | 539/470 v 307/649 | 1.13 |
| 15:00 | 51 v 43 | 2 v 3 | 85/1455 v 675/1679 | 591/470 v 296/627 | 1.19 |
| 16:00 | 51 v 42 | 2 v 3 | 10/1427 v 1125/1595 | 627/447 v 281/627 | 1.21 |
| 17:00 | 51 v 48 | 2 v 3 | 30/1455 v 130/1259 | 615/582 v 16/627 | 1.06 |
| 18:00 | 51 v 60 | 2 v 3 | 20/1483 v 690/2323 | 713/649 v 76/985 | 0.85 |
| 19:00 | 51 v 59 | 2 v 3 | 15/1483 v 1050/1903 | 827/671 v 292/828 | 0.86 |
| 20:00 | 51 v 60 | 2 v 3 | 95/1287 v 1885/2379 | 991/671 v 548/918 | 0.85 |
| 21:00 | 43 v 60 ⚠️ | 1 v 4 | 45/0 v 2770/2183 | 1287/291 v 840/940 | 0.72 |
| 22:00 | 21 v 60 ⚠️ | 1 v 4 | 45/0 v 3040/1539 | 1497/167 v 758/783 | 0.35 |
| 23:00 | 21 v 58 ⚠️ | 1 v 4 | 45/0 v 2040/1987 | 1579/0 v 275/638 | 0.36 |
| 24:00 | 21 v 60 ⚠️ | 1 v 4 | 45/0 v 3325/2267 | 1579/0 v 660/985 | 0.35 |
| 25:00 | 21 v 60 ⚠️ | 1 v 4 | 45/0 v 4150/2295 | 1579/0 v 760/985 | 0.35 |
| 26:00 | 20 v 60 ⚠️ | 1 v 4 | 45/0 v 4440/2323 | 1579/0 v 731/963 | 0.33 |
| 27:00 | 20 v 60 ⚠️ | 1 v 4 | 45/0 v 4820/2351 | 1579/0 v 406/985 | 0.33 |

## Accumulated — resources mined & army value produced

| time | mined us (m/g/tot) | mined enemy (m/g/tot) | army made u/e | share u/e |
|------|:------------------:|:---------------------:|:-------------:|:---------:|
| 1:00 | 512/0/512 | 554/0/554 | 0 v 200 | 0% / 36% |
| 2:00 | 1290/0/1290 | 1370/3/1373 | 0 v 200 | 0% / 15% |
| 3:00 | 2148/89/2237 | 2111/152/2263 | 0 v 450 | 0% / 20% |
| 4:00 | 3015/368/3384 | 2833/438/3272 | 200 v 850 | 6% / 26% |
| 5:00 | 4022/692/4715 | 3625/759/4384 | 300 v 1550 | 6% / 35% |
| 6:00 | 5062/1009/6071 | 4530/1083/5613 | 575 v 1850 | 9% / 33% |
| 7:00 | 6106/1333/7439 | 5499/1392/6892 | 750 v 2350 | 10% / 34% |
| 8:00 | 7524/1672/9196 | 6525/1713/8238 | 950 v 2400 | 10% / 29% |
| 9:00 | 9296/2160/11457 | 7518/2033/9552 | 1050 v 2400 | 9% / 25% |
| 10:00 | 11143/2806/13949 | 8572/2350/10922 | 1950 v 2800 | 14% / 26% |
| 11:00 | 12724/3372/16097 | 9373/2670/12044 | 2850 v 3050 | 18% / 25% |
| 12:00 | 13442/3693/17135 | 10614/3080/13694 | 3725 v 3300 | 22% / 24% |
| 13:00 | 14584/4080/18665 | 12223/3725/15948 | 4600 v 4100 | 25% / 26% |
| 14:00 | 15866/4491/20358 | 13799/4367/18167 | 5475 v 5300 | 27% / 29% |
| 15:00 | 17223/4987/22211 | 15422/5020/20442 | 6175 v 5375 | 28% / 26% |
| 16:00 | 18692/5464/24157 | 17017/5672/22690 | 7400 v 6025 | 31% / 27% |
| 17:00 | 20152/5978/26131 | 18640/6314/24954 | 8625 v 6975 | 33% / 28% |
| 18:00 | 21649/6583/28232 | 20422/7023/27445 | 9850 v 7575 | 35% / 28% |
| 19:00 | 23113/7228/30342 | 22521/7915/30436 | 11250 v 7925 | 37% / 26% |
| 20:00 | 24461/7881/32343 | 24522/8821/33343 | 12475 v 8075 | 39% / 24% |
| 21:00 | 25431/8496/33928 | 26821/9799/36621 | 13175 v 8975 | 39% / 25% |
| 22:00 | 25431/8815/34246 | 28897/10681/39579 | 13350 v 9425 | 39% / 24% |
| 23:00 | 25431/8967/34399 | 30599/11481/42081 | 13350 v 9575 | 39% / 23% |
| 24:00 | 25431/8967/34399 | 32736/12312/45048 | 13350 v 10325 | 39% / 23% |
| 25:00 | 25431/8967/34399 | 34975/13289/48265 | 13350 v 10325 | 39% / 21% |
| 26:00 | 25431/8967/34399 | 37237/14259/51497 | 13350 v 11175 | 39% / 22% |
| 27:00 | 25431/8967/34399 | 39541/15237/54779 | 13350 v 12025 | 39% / 22% |

- **TOTAL mined** us 34399 vs enemy 56414 (ratio 0.61)
- **TOTAL army value produced** us 13350 vs enemy 12475 (ratio 1.07); invested 39% vs enemy 22%

## Army value + the fight each minute

| time | our army v/s | enemy v/s | ratio | upg u/e | fight (lost u/e, trade) |
|------|:------------:|:---------:|:-----:|:-------:|:-----------------------|
| 1:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 2:00 | 0/0 | 200/0 | 0.0 | 0/0 | — |
| 3:00 | 0/0 | 450/6 | 0.0 | 0/0 | — |
| 4:00 | 200/4 | 850/9 | 0.2 | 0/0 | — |
| 5:00 | 300/6 | 1550/20 | 0.2 | 0/0 | — |
| 6:00 | 575/10 | 1850/26 | 0.3 | 1/0 | — |
| 7:00 | 650/10 | 2325/31 | 0.3 | 1/0 | — |
| 8:00 | 850/14 | 2375/33 | 0.4 | 2/0 | — |
| 9:00 | 950/16 | 2375/33 | 0.4 | 3/0 | — |
| 10:00 | 1075/12 | 2275/29 | 0.5 | 3/0 | **BATTLE** 775/500 — 0.65 |
| 11:00 | 1275/14 | 1425/13 | 0.9 | 4/0 | **BATTLE** 700/1100 — 1.57 |
| 12:00 | 2150/24 | 1675/17 | 1.3 | 4/2 | — |
| 13:00 | 2675/30 | 2250/22 | 1.2 | 4/3 | skirm 350/225 — 0.64 |
| 14:00 | 3375/38 | 3375/33 | 1.0 | 4/4 | — |
| 15:00 | 3900/44 | 3275/33 | 1.2 | 4/5 | — |
| 16:00 | 4775/54 | 3650/38 | 1.3 | 5/6 | skirm 350/275 — 0.79 |
| 17:00 | 5825/66 | 4550/48 | 1.3 | 5/7 | — |
| 18:00 | 6875/78 | 4900/50 | 1.4 | 5/7 | skirm 175/250 — 1.43 |
| 19:00 | 7925/90 | 5250/52 | 1.5 | 5/7 | skirm 350/0 — 0.00 |
| 20:00 | 8975/102 | 5400/54 | 1.7 | 5/7 | — |
| 21:00 | 9325/106 | 6300/65 | 1.5 | 5/8 | skirm 350/0 — 0.00 |
| 22:00 | 8625/98 | 3600/37 | 2.4 | 5/11 | **BATTLE** 875/3150 — 3.60 |
| 23:00 | 8625/98 | 3750/39 | 2.3 | 5/11 | — |
| 24:00 | 8625/98 | 4500/49 | 1.9 | 5/11 | — |
| 25:00 | 8625/98 | 4500/49 | 1.9 | 5/13 | — |
| 26:00 | 5475/62 | 2650/27 | 2.1 | 5/15 | **BATTLE** 3150/2700 — 0.86 |
| 27:00 | 5475/62 | 3500/41 | 1.6 | 5/15 | — |

## Decisive engagements (30s buckets, most value lost)

- **25:00** we lost 2450 (14xStalker); they lost 1750 (6xRoach, 4xHydralisk, 2xInfestor, 2xZergling) — trade **0.71**
  - going in: us 8625v/98s 45xStalker, 2xImmortal · enemy 4500v/49s 6xRoach, 5xOverseer, 5xQueen, 5xHydralisk, 3xRavager, 3xInfestor
- **9:30** we lost 775 (6xZealot, 1xStalker); they lost 475 (3xZergling, 2xRavager) — trade **0.61**
  - going in: us 1500v/22s 6xZealot, 3xStalker, 1xImmortal · enemy 2600v/36s 7xRoach, 5xZergling, 4xRavager, 3xOverseer, 3xBaneling, 1xQueen
- **25:30** we lost 700 (4xStalker); they lost 950 (3xRavager, 1xOverseer, 1xHydralisk) — trade **1.36**
  - going in: us 6175v/70s 31xStalker, 2xImmortal · enemy 2800v/25s 5xOverseer, 5xQueen, 3xRavager, 2xZergling, 1xInfestor, 1xHydralisk
- **10:00** we lost 525 (3xStalker); they lost 0 (-) — trade **0.00**
  - going in: us 1075v/12s 4xStalker, 1xImmortal · enemy 2275v/29s 7xRoach, 5xBaneling, 3xOverseer, 2xZergling, 2xRavager, 1xQueen
- **21:00** we lost 525 (3xStalker); they lost 3150 (8xMutalisk, 6xHydralisk, 4xRoach, 2xZergling, 1xOverseer) — trade **6.00**
  - going in: us 9325v/106s 49xStalker, 2xImmortal · enemy 6300v/65s 8xMutalisk, 6xOverseer, 6xHydralisk, 6xRoach, 4xQueen, 3xRavager
- **15:00** we lost 350 (2xStalker); they lost 250 (3xBaneling, 1xZergling) — trade **0.71**
  - going in: us 3900v/44s 18xStalker, 2xImmortal · enemy 3275v/33s 8xZergling, 8xMutalisk, 4xOverseer, 3xQueen, 3xBaneling

## Peak composition @ 21:00 (9325v/106s)

- us: 49xStalker, 2xImmortal
- enemy: 8xMutalisk, 6xOverseer, 6xHydralisk, 6xRoach, 4xQueen, 3xRavager
- our upgrades (5): ['ProtossGroundArmorsLevel1', 'ProtossGroundWeaponsLevel1', 'Charge', 'ProtossGroundArmorsLevel2', 'ProtossGroundWeaponsLevel2']
- enemy upgrades (22): ['zerglingmovementspeed', 'ZergMeleeWeaponsLevel1', 'Burrow', 'CentrificalHooks', 'ZergMissileWeaponsLevel1', 'overlordspeed', 'ZergGroundArmorsLevel1', 'GlialReconstitution', 'ZergMeleeWeaponsLevel2', 'ZergGroundArmorsLevel2', 'ZergFlyerWeaponsLevel1', 'ZergFlyerArmorsLevel1', 'ZergMissileWeaponsLevel2', 'ZergMeleeWeaponsLevel3', 'TunnelingClaws', 'ZergFlyerWeaponsLevel2', 'ZergGroundArmorsLevel3', 'ZergMissileWeaponsLevel3', 'ZergFlyerArmorsLevel2', 'ZergFlyerWeaponsLevel3', 'zerglingattackspeed', 'ZergFlyerArmorsLevel3']


---
