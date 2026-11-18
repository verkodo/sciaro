# SPDX-License-Identifier: CC-BY-4.0
"""The wage tax 2026 (de/bmf/pap_lst_2026.vk, de/bmf/pap_lst_dba_2026.vk) against the BMF's test tables and more.

The tables are those of the "Programmablaufplan für die maschinelle Berechnung der vom Arbeitslohn einzubehaltenden
Lohnsteuer … für 2026" (Anlage 1 to the BMF letter of 2025-11-12, IV C 5 - S 2361/00025/016/028), pages 39 and 40:
the annual wage tax in euros for annual wages from 5,000 to 110,000 euros in tax classes I to VI – taken from the
text of the PDF by a program, not typed. The plan has no tables for other pay periods, the solidarity surcharge or the
church tax; for those, a few cases computed with the BMF's "Lohnsteuerrechner 2026" (bmf-steuerrechner.de, retrieved
2026-11-13), which follows the plan. Every other part of the plan - pensions, the relief for old age, allowances and
additions, the factor method, other emoluments, the outputs for double taxation treaties - is checked against
tests/lst_2026_pap.jsonl: 600 cases computed by the BMF's machine-readable flowchart (tests/pap_xml.py). The limit on
pensions under double taxation treaties (Anlage 3) and the wage tax tables (Anlage 2) are checked against their own test
tables.
Run from the repository: python3 tests/lst_2026.py (needs `verkodo`).
"""
import json
import pathlib
import subprocess
import sys
import tempfile

NORM = "de.bmf.pap_lst_2026.wage_tax"
DBA_NORM = "de.bmf.pap_lst_dba_2026.limited_wage_tax"
CLASSES = ["i", "ii", "iii", "iv", "v", "vi"]
TABLE_NORM = "de.bmf.pap_lst_tab_2026.table_entry"
TREATIES = [("turkey", "i"), ("turkey", "vi"), ("norway", "i"), ("norway", "vi"), ("spain", "i"), ("spain", "vi")]

# "Allgemeine maschinelle Jahreslohnsteuer 2026 (Prüftabelle)": ALV, KRV and PKV = 0, KVZ = 2.90; PVZ = 0 in class II,
# 1 in the others. Rows: annual wage, then the tax in classes I to VI.
GENERAL = [
    (5000, 0, 0, 0, 0, 372, 558),
    (7500, 0, 0, 0, 0, 647, 838),
    (10000, 0, 0, 0, 0, 922, 1117),
    (12500, 0, 0, 0, 0, 1197, 1397),
    (15000, 0, 0, 0, 0, 1472, 1676),
    (17500, 51, 0, 0, 51, 1778, 1956),
    (20000, 380, 0, 0, 380, 2234, 2766),
    (22500, 782, 32, 0, 782, 3073, 3604),
    (25000, 1251, 359, 0, 1251, 3911, 4443),
    (27500, 1742, 759, 0, 1742, 4749, 5281),
    (30000, 2248, 1230, 0, 2248, 5588, 6120),
    (32500, 2767, 1724, 0, 2767, 6426, 6952),
    (35000, 3300, 2233, 294, 3300, 7216, 7682),
    (37500, 3847, 2756, 628, 3847, 7954, 8436),
    (40000, 4407, 3293, 1000, 4407, 8720, 9218),
    (42500, 4982, 3843, 1406, 4982, 9512, 10030),
    (45000, 5570, 4408, 1850, 5570, 10334, 10865),
    (47500, 6172, 4987, 2324, 6172, 11171, 11703),
    (50000, 6788, 5580, 2810, 6788, 12010, 12542),
    (52500, 7417, 6186, 3302, 7417, 12848, 13380),
    (55000, 8060, 6807, 3802, 8060, 13687, 14218),
    (57500, 8718, 7442, 4308, 8718, 14525, 15057),
    (60000, 9389, 8091, 4822, 9389, 15364, 15895),
    (62500, 10073, 8754, 5342, 10073, 16202, 16734),
    (65000, 10772, 9430, 5870, 10772, 17040, 17572),
    (67500, 11484, 10121, 6402, 11484, 17879, 18410),
    (70000, 12220, 10835, 6952, 12220, 18729, 19260),
    (72500, 13062, 11647, 7574, 13062, 19681, 20213),
    (75000, 13922, 12476, 8206, 13922, 20633, 21165),
    (77500, 14799, 13323, 8846, 14799, 21585, 22117),
    (80000, 15694, 14188, 9496, 15694, 22538, 23070),
    (82500, 16607, 15071, 10154, 16607, 23490, 24022),
    (85000, 17538, 15971, 10822, 17538, 24443, 24974),
    (87500, 18486, 16890, 11498, 18486, 25395, 25927),
    (90000, 19438, 17826, 12182, 19438, 26347, 26879),
    (92500, 20390, 18777, 12876, 20390, 27300, 27831),
    (95000, 21343, 19729, 13580, 21343, 28252, 28784),
    (97500, 22295, 20682, 14292, 22295, 29204, 29736),
    (100000, 23248, 21634, 15012, 23248, 30157, 30689),
    (102500, 24243, 22629, 15774, 24243, 31152, 31684),
    (105000, 25293, 23679, 16590, 25293, 32202, 32734),
    (107500, 26343, 24729, 17416, 26343, 33252, 33784),
    (110000, 27393, 25779, 18252, 27393, 34302, 34834),
]

# "Besondere maschinelle Jahreslohnsteuer 2026 (Prüftabelle)": ALV, KRV and PKV = 1; PKPV = 50,000 cents in class III,
# 0 in class VI and 30,000 cents in the others (monthly amounts).
SPECIAL = [
    (5000, 0, 0, 0, 0, 18, 700),
    (7500, 0, 0, 0, 0, 368, 1050),
    (10000, 0, 0, 0, 0, 718, 1400),
    (12500, 0, 0, 0, 0, 1068, 1750),
    (15000, 0, 0, 0, 0, 1418, 2359),
    (17500, 40, 0, 0, 40, 1768, 3409),
    (20000, 461, 0, 0, 461, 2415, 4459),
    (22500, 995, 153, 0, 995, 3465, 5509),
    (25000, 1604, 607, 0, 1604, 4515, 6559),
    (27500, 2234, 1173, 0, 2234, 5565, 7514),
    (30000, 2886, 1788, 0, 2886, 6615, 8460),
    (32500, 3559, 2424, 76, 3559, 7564, 9446),
    (35000, 4254, 3083, 466, 4254, 8510, 10473),
    (37500, 4971, 3763, 914, 4971, 9498, 11523),
    (40000, 5710, 4464, 1420, 5710, 10529, 12573),
    (42500, 6470, 5188, 1982, 6470, 11579, 13623),
    (45000, 7252, 5932, 2584, 7252, 12629, 14673),
    (47500, 8055, 6699, 3198, 8055, 13679, 15723),
    (50000, 8880, 7487, 3824, 8880, 14729, 16773),
    (52500, 9727, 8297, 4458, 9727, 15779, 17823),
    (55000, 10595, 9128, 5106, 10595, 16829, 18873),
    (57500, 11485, 9981, 5762, 11485, 17879, 19923),
    (60000, 12396, 10856, 6430, 12396, 18929, 20973),
    (62500, 13330, 11752, 7110, 13330, 19979, 22023),
    (65000, 14284, 12670, 7798, 14284, 21029, 23073),
    (67500, 15261, 13610, 8500, 15261, 22079, 24123),
    (70000, 16259, 14571, 9210, 16259, 23129, 25173),
    (72500, 17279, 15554, 9932, 17279, 24179, 26223),
    (75000, 18320, 16559, 10666, 18320, 25229, 27273),
    (77500, 19370, 17585, 11410, 19370, 26279, 28323),
    (80000, 20420, 18631, 12164, 20420, 27329, 29373),
    (82500, 21470, 19681, 12930, 21470, 28379, 30423),
    (85000, 22520, 20731, 13706, 22520, 29429, 31473),
    (87500, 23570, 21781, 14492, 23570, 30479, 32523),
    (90000, 24620, 22831, 15290, 24620, 31529, 33573),
    (92500, 25670, 23881, 16098, 25670, 32579, 34623),
    (95000, 26720, 24931, 16918, 26720, 33629, 35673),
    (97500, 27770, 25981, 17748, 27770, 34679, 36723),
    (100000, 28820, 27031, 18590, 28820, 35729, 37773),
    (102500, 29870, 28081, 19442, 29870, 36779, 38823),
    (105000, 30920, 29131, 20304, 30920, 37829, 39873),
    (107500, 31970, 30181, 21178, 31970, 38879, 40923),
    (110000, 33020, 31231, 22062, 33020, 39929, 41973),
]

# "Allgemeine" and "Besondere Jahreslohnsteuertabelle 2026 (Prüftabelle)" of the plan for the wage tax tables (Anlage 2,
# pages 21 and 22): for 43 steps of 36 euros, the annual wage tax in tax classes I to VI, computed at the top of the step
# (lower bound + 35.99 euros). General: MALVKRVPKV = 0, KVZ = 2.90; special: MALVKRVPKV = 1. Rows: the lower bound of the
# step, then the tax in classes I to VI.
TABLE_GENERAL = [
    (4968, 0, 0, 0, 0, 377, 563),
    (7488, 0, 0, 0, 0, 656, 847),
    (9972, 0, 0, 0, 0, 931, 1127),
    (12492, 0, 0, 0, 0, 1210, 1410),
    (14976, 0, 0, 0, 0, 1486, 1690),
    (17496, 55, 0, 0, 55, 1782, 1982),
    (19980, 404, 0, 0, 404, 2289, 2821),
    (22500, 818, 36, 0, 818, 3141, 3673),
    (24984, 1291, 361, 0, 1291, 3980, 4512),
    (27468, 1784, 760, 0, 1784, 4819, 5351),
    (29988, 2299, 1234, 0, 2299, 5671, 6203),
    (32472, 2820, 1726, 26, 2820, 6510, 7024),
    (34992, 3363, 2239, 332, 3363, 7300, 7766),
    (37476, 3912, 2758, 670, 3912, 8042, 8528),
    (39996, 4483, 3299, 1052, 4483, 8824, 9326),
    (42480, 5060, 3847, 1464, 5060, 9620, 10142),
    (45000, 5659, 4416, 1918, 5659, 10458, 10990),
    (47484, 6263, 4991, 2398, 6263, 11297, 11829),
    (49968, 6882, 5580, 2884, 6882, 12137, 12668),
    (52488, 7524, 6192, 3386, 7524, 12988, 13520),
    (54972, 8170, 6809, 3886, 8170, 13827, 14359),
    (57492, 8840, 7449, 4402, 8840, 14679, 15211),
    (59976, 9514, 8093, 4918, 9514, 15518, 16050),
    (62496, 10212, 8762, 5448, 10212, 16370, 16902),
    (64980, 10914, 9434, 5976, 10914, 17209, 17741),
    (67500, 11640, 10131, 6520, 11640, 18060, 18592),
    (69984, 12381, 10841, 7070, 12381, 18911, 19443),
    (72468, 13220, 11647, 7690, 13220, 19858, 20389),
    (74988, 14090, 12484, 8330, 14090, 20818, 21349),
    (77472, 14965, 13325, 8966, 14965, 21764, 22296),
    (79992, 15871, 14198, 9624, 15871, 22724, 23256),
    (82476, 16782, 15075, 10280, 16782, 23670, 24202),
    (84996, 17723, 15983, 10954, 17723, 24630, 25162),
    (87480, 18667, 16895, 11628, 18667, 25576, 26108),
    (90000, 19627, 17839, 12320, 19627, 26536, 27068),
    (92484, 20573, 18784, 13010, 20573, 27483, 28014),
    (94968, 21520, 19731, 13712, 21520, 28429, 28961),
    (97488, 22479, 20690, 14430, 22479, 29389, 29920),
    (99972, 23426, 21636, 15148, 23426, 30335, 30867),
    (102492, 24430, 22641, 15918, 24430, 31339, 31871),
    (104976, 25473, 23684, 16730, 25473, 32382, 32914),
    (107496, 26532, 24742, 17564, 26532, 33441, 33973),
    (109980, 27575, 25786, 18398, 27575, 34484, 35016),
]

TABLE_SPECIAL = [
    (4968, 0, 0, 0, 0, 523, 700),
    (7488, 0, 0, 0, 0, 875, 1053),
    (9972, 0, 0, 0, 0, 1223, 1400),
    (12492, 0, 0, 0, 0, 1576, 1753),
    (14976, 213, 0, 0, 213, 1924, 2363),
    (17496, 688, 0, 0, 688, 2890, 3422),
    (19980, 1264, 341, 0, 1264, 3933, 4465),
    (22500, 1887, 851, 0, 1887, 4992, 5523),
    (24984, 2523, 1445, 0, 2523, 6035, 6567),
    (27468, 3180, 2066, 226, 3180, 7054, 7516),
    (29988, 3869, 2718, 642, 3869, 7984, 8466),
    (32472, 4569, 3381, 1110, 4569, 8942, 9446),
    (34992, 5301, 4076, 1644, 5301, 9958, 10484),
    (37476, 6045, 4783, 2224, 6045, 10996, 11528),
    (39996, 6821, 5522, 2836, 6821, 12054, 12586),
    (42480, 7607, 6272, 3450, 7607, 13098, 13629),
    (45000, 8427, 7054, 4084, 8427, 14156, 14688),
    (47484, 9256, 7847, 4720, 9256, 15199, 15731),
    (49968, 10107, 8661, 5368, 10107, 16243, 16774),
    (52488, 10992, 9509, 6034, 10992, 17301, 17833),
    (54972, 11886, 10366, 6702, 11886, 18344, 18876),
    (57492, 12814, 11257, 7390, 12814, 19403, 19934),
    (59976, 13751, 12158, 8080, 13751, 20446, 20978),
    (62496, 14724, 13093, 8792, 14724, 21504, 22036),
    (64980, 15703, 14036, 9502, 15703, 22548, 23079),
    (67500, 16719, 15015, 10234, 16719, 23606, 24138),
    (69984, 17742, 16001, 10968, 17742, 24649, 25181),
    (72468, 18783, 17009, 11710, 18783, 25693, 26224),
    (74988, 19842, 18053, 12476, 19842, 26751, 27283),
    (77472, 20885, 19096, 13240, 20885, 27794, 28326),
    (79992, 21943, 20154, 14028, 21943, 28853, 29384),
    (82476, 22987, 21198, 14814, 22987, 29896, 30428),
    (84996, 24045, 22256, 15622, 24045, 30954, 31486),
    (87480, 25088, 23299, 16430, 25088, 31998, 32529),
    (90000, 26147, 24358, 17260, 26147, 33056, 33588),
    (92484, 27190, 25401, 18090, 27190, 34099, 34631),
    (94968, 28233, 26444, 18930, 28233, 35143, 35674),
    (97488, 29292, 27503, 19792, 29292, 36201, 36733),
    (99972, 30335, 28546, 20654, 30335, 37244, 37776),
    (102492, 31393, 29604, 21540, 31393, 38303, 38834),
    (104976, 32437, 30648, 22422, 32437, 39346, 39878),
    (107496, 33495, 31706, 23330, 33495, 40404, 40936),
    (109980, 34538, 32749, 24234, 34538, 41448, 41979),
]


# "Prüftabelle für das Jahr 2026" of the plan on double taxation treaties (Anlage 3, page 14): the annual wage tax on a
# pension in classes I and VI under the treaties with Türkiye, Norway and Spain. KRV = 1, PVA, PVS and PKV = 0, PVZ = 1,
# KVZ = 2.90; VJAHR = 2026, ZMVB = 12, VBEZS = 0, VBEZM = the annual pension / 12 (fractions of a cent dropped).
# Rows: annual pension, then Türkiye I, VI, Norway I, VI, Spain I, VI.
DBA = [
    (5000, 0, 500, 0, 534, 0, 250),
    (7500, 0, 750, 0, 801, 0, 375),
    (10000, 0, 1000, 0, 1113, 0, 500),
    (12500, 0, 1250, 0, 1425, 0, 625),
    (15000, 0, 1500, 0, 1737, 0, 750),
    (17500, 0, 1750, 293, 2208, 293, 875),
    (20000, 0, 2000, 726, 3000, 726, 1000),
    (22500, 0, 2250, 1245, 3375, 1125, 1125),
    (25000, 0, 2500, 1795, 3750, 1250, 1250),
    (27500, 340, 2750, 2361, 4125, 1375, 1375),
    (30000, 784, 3000, 2945, 4500, 1500, 1500),
    (32500, 1309, 3250, 3546, 4875, 1625, 1625),
    (35000, 1861, 3500, 4165, 5250, 1750, 1750),
    (37500, 2430, 3750, 4800, 5625, 1875, 1875),
    (40000, 3016, 4000, 5453, 6000, 2000, 2000),
    (42500, 3619, 4250, 6123, 6375, 2125, 2125),
    (45000, 4239, 4500, 6750, 6750, 2250, 2250),
    (47500, 4750, 4750, 7125, 7125, 2375, 2375),
    (50000, 5000, 5000, 7500, 7500, 2500, 2500),
    (52500, 5250, 5250, 7875, 7875, 2625, 2625),
    (55000, 5500, 5500, 8250, 8250, 2750, 2750),
    (57500, 5750, 5750, 8625, 8625, 2875, 2875),
    (60000, 6000, 6000, 9000, 9000, 3000, 3000),
    (62500, 6250, 6250, 9375, 9375, 3125, 3125),
    (65000, 6500, 6500, 9750, 9750, 3250, 3250),
    (67500, 6750, 6750, 10125, 10125, 3375, 3375),
    (70000, 7000, 7000, 10500, 10500, 3500, 3500),
    (72500, 7250, 7250, 10875, 10875, 3625, 3625),
    (75000, 7500, 7500, 11250, 11250, 3750, 3750),
    (77500, 7750, 7750, 11625, 11625, 3875, 3875),
    (80000, 8000, 8000, 12000, 12000, 4000, 4000),
    (82500, 8250, 8250, 12375, 12375, 4125, 4125),
    (85000, 8500, 8500, 12750, 12750, 4250, 4250),
    (87500, 8750, 8750, 13125, 13125, 4375, 4375),
    (90000, 9000, 9000, 13500, 13500, 4500, 4500),
    (92500, 9250, 9250, 13875, 13875, 4625, 4625),
    (95000, 9500, 9500, 14250, 14250, 4750, 4750),
    (97500, 9750, 9750, 14625, 14625, 4875, 4875),
    (100000, 10000, 10000, 15000, 15000, 5000, 5000),
    (102500, 10250, 10250, 15375, 15375, 5125, 5125),
    (105000, 10500, 10500, 15750, 15750, 5250, 5250),
    (107500, 10750, 10750, 16125, 16125, 5375, 5375),
    (110000, 11000, 11000, 16500, 16500, 5500, 5500),
]


# The BMF's "Lohnsteuerrechner 2026" (bmf-steuerrechner.de, retrieved 2026-11-13): ALV, KRV and PKV = 0, KVZ = 2.90,
# no pensions, allowances or additions. Church tax with 8 % (Bavaria); the calculator shows the church tax, not its
# base, so the test compares 8 % of BK, rounded down to cents. Rows: pay period, wage, class, ZKF, church, PVZ, PVA,
# then the wage tax, solidarity surcharge and church tax for the pay period in euros.
CALCULATOR = [
    ("month", "4000", "i", "1", True, False, 0, "531.83", "0", "23.65"),
    ("week", "1500", "iii", "2", True, False, 1, "173.48", "0", "5.74"),
    ("day", "300", "i", "0", False, True, 0, "73.75", "2.05", "0"),
    ("month", "9000", "iv", "1.5", True, False, 0, "2227.41", "32.77", "157.7"),
    ("month", "3000", "v", "0", True, True, 0, "625.66", "0", "50.05"),
]


# Inputs the tables and the calculator leave at zero.
NONE = dict(af="false", f="1", lzzfreib="0", lzzhinzu="0", vbez="0", vbezm="0", vbezs="0", vjahr="0", zmvb="0",
            alter1="false", ajahr="0", sonstb="0", sonstent="0", sterbe="0", vbs="0", mbv="0", jre4="0", jre4ent="0",
            jvbez="0", jfreib="0", jhinzu="0")
PAP = pathlib.Path(__file__).with_name("lst_2026_pap.jsonl")


def plain(stkl, lzz, wage, zkf, r, krv, alv, pkv, kvz, pvz, pva, pkpv):
    ins = dict(krv=krv, alv=alv, pkv=pkv, kvz=kvz, pvs=False, pvz=pvz, pva=pva, pkpv=pkpv, pkpvagz="0")
    return dict(stkl=stkl, lzz=lzz, wage=wage, zkf=zkf, r=str(r).lower(), ins=ins, **NONE)


def cents(x):
    return round(float(x) * 100)


def cents_down(x):
    """An amount in euros with fractions of a cent dropped."""
    return f"{int(x * 100) // 100}.{int(x * 100) % 100:02d}"


def cases():
    """(name, inputs, expected outputs, norm)."""
    for wage, *taxes in GENERAL:
        for c, tax in zip(CLASSES, taxes):
            yield f"general {wage} class {c.upper()}", plain(c, "year", str(wage), "0", False, False, False, False,
                                                             "2.90", c != "ii", 0, "0"), {"lstjahr": tax}, NORM
    for wage, *taxes in SPECIAL:
        for c, tax in zip(CLASSES, taxes):
            pkpv = {"iii": "500", "vi": "0"}.get(c, "300")
            yield f"special {wage} class {c.upper()}", plain(c, "year", str(wage), "0", False, True, True, True,
                                                             "0", True, 0, pkpv), {"lstjahr": tax}, NORM
    for lzz, wage, c, zkf, church, pvz, pva, lst, solz, kist in CALCULATOR:
        yield (f"calculator {lzz} {wage} class {c.upper()}",
               plain(c, lzz, wage, zkf, church, False, False, False, "2.90", pvz, pva, "0"),
               {"lstlzz": lst, "solzlzz": solz, "kist": kist}, NORM)
    for special, table in (("false", TABLE_GENERAL), ("true", TABLE_SPECIAL)):
        for low, *taxes in table:
            for c, tax in zip(CLASSES, taxes):
                inputs = dict(special=special, kvz="2.90", pvs="false", lzz="year", stkl=c, zkf="0", zre4=str(low))
                kind = "special" if special == "true" else "general"
                yield (f"table {kind} {low} class {c.upper()}", inputs, {"lstlzz": tax, "lzalog": f"{low + 35}.99"},
                       TABLE_NORM)
    for pension, *taxes in DBA:
        for (land, c), tax in zip(TREATIES, taxes):
            ins = dict(krv=True, alv=False, pkv=False, kvz="2.90", pvs=False, pvz=True, pva=0, pkpv="0", pkpvagz="0")
            inputs = dict(land=land, stkl=c, lzz="year", ins=ins, vbez=str(pension), vbezm=str(cents_down(pension / 12)),
                          vbezs="0", vjahr="2026", zmvb="12", vbs="0", sterbe="0", sonstent="0", jvbez="0", jre4ent="0",
                          jfreib="0", jhinzu="0", lzzfreib="0", lzzhinzu="0")
            yield f"treaty {pension} {land} class {c.upper()}", inputs, {"lstlzz": tax}, DBA_NORM
    for n, line in enumerate(PAP.read_text().splitlines(), start=1):
        case = json.loads(line)
        yield f"flowchart case {n}", case["inputs"], case["expected"], NORM


def got(out, key):
    if key == "kist":  # 8 % of BK, rounded down to cents
        return cents(out["bk"]) * 8 // 100
    return cents(out[key])


def evaluate(norm, inputs):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("".join(json.dumps(i) + "\n" for i in inputs))
    out = subprocess.run(["verkodo", "eval", ".", "--norm", norm, "--cases", f.name],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    return [json.loads(o) for o in out]


def main():
    all_cases = list(cases())
    wrong = []
    for norm in (NORM, TABLE_NORM, DBA_NORM):
        mine = [c for c in all_cases if c[3] == norm]
        for (name, _, exp, _), o in zip(mine, evaluate(norm, [c[1] for c in mine])):
            for key, value in exp.items():
                if got(o, key) != cents(value):
                    wrong.append(f"{name}: {key} expected {value}, got {got(o, key) / 100}")
    print("\n".join(wrong) if wrong else "", end="\n" if wrong else "")
    print(f"{len(all_cases) - len({w.split(':')[0] for w in wrong})} of {len(all_cases)} as in the test tables, the"
          " calculator and the flowchart")
    sys.exit(1 if wrong else 0)


if __name__ == "__main__":
    main()
