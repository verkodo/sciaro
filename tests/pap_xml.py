# SPDX-License-Identifier: CC-BY-4.0
"""Cases for the wage tax 2026, computed by the BMF's own machine-readable programme flowchart.

The BMF publishes the flowchart of Anlage 1 also as pseudocode, Lohnsteuer2026.xml ("Stand: 2025-10-23 12:40",
ITZBund; on bmf-steuerrechner.de, the source of its calculator; retrieved 2026-11-18). This script runs that file
exactly - its Java expressions over BigDecimal, read with Python's ast and evaluated from a short whitelist, with
fractions; nothing in it is executed as code - on random plausible inputs and writes them with the results to
tests/lst_2026_pap.jsonl, which tests/lst_2026.py checks against de/bmf/pap_lst_2026.vk. Plausible means what the
plan asks callers to ensure (section 3.1): pensions within the wage, the factor only in class IV and without
allowances, no additions in class VI. To regenerate: python3 -I tests/pap_xml.py Lohnsteuer2026.xml
"""
import ast
import json
import random
import re
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from fractions import Fraction

SEED, COUNT, EDGE = 2026, 600, 200
rnd = random.Random(SEED)
OUT = ["LSTLZZ", "SOLZLZZ", "BK", "STS", "SOLZS", "BKS", "VFRB", "VFRBS1", "VFRBS2", "WVFRB", "WVFRBO", "WVFRBM"]
INTS = ("STKL", "LZZ", "R", "KRV", "ALV", "PKV", "PVS", "PVZ", "af", "ALTER1", "AJAHR", "VJAHR", "ZMVB")


def frac(x):
    """BigDecimal as a fraction, exactly; a double by its shortest decimal form, as BigDecimal.valueOf does."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(Decimal(repr(x)))
    return Fraction(x)


def set_scale(x, n, mode):
    """BigDecimal.setScale: n decimal places, ROUND_DOWN toward zero, ROUND_UP away from zero."""
    q = Fraction(1, 10 ** n)
    v = frac(x) / q
    t = v.numerator // v.denominator if v >= 0 else -((-v.numerator) // v.denominator)  # toward zero
    if mode == "UP" and t != v:
        t += 1 if v > 0 else -1
    return t * q


METHODS = {
    "add": lambda a, b: frac(a) + frac(b),
    "subtract": lambda a, b: frac(a) - frac(b),
    "multiply": lambda a, b: frac(a) * frac(b),
    "divide": lambda a, b, n=None, mode=None: frac(a) / frac(b) if n is None else set_scale(frac(a) / frac(b), n, mode),
    "setScale": lambda a, n, mode: set_scale(a, n, mode),
    "compareTo": lambda a, b: (frac(a) > frac(b)) - (frac(a) < frac(b)),
    "longValue": lambda a: int(set_scale(a, 0, "DOWN")),
}


def rewrite(expr):
    e = expr.replace("&&", " and ").replace("||", " or ")
    e = re.sub(r"BigDecimal\.ROUND_(UP|DOWN)", r"'\1'", e)
    e = e.replace("BigDecimal.ZERO", "0").replace("BigDecimal.ONE", "1")
    e = re.sub(r"BigDecimal\.valueOf\s*\(", "valueOf(", e)
    return e.strip()


class Machine:
    def __init__(self, root):
        self.root = root
        self.methods = {m.get("name"): m for m in root.iter("METHOD")}
        self.env = {}
        for c in root.iter("CONSTANT"):
            v = c.get("value").strip()
            if v.startswith("{"):
                self.env[c.get("name")] = [self.ev(rewrite(p)) for p in v.strip("{} ").split(",")]
            else:
                self.env[c.get("name")] = self.ev(rewrite(v))

    def ev(self, src):
        return self.node(ast.parse(src, mode="eval").body)

    def node(self, n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float, str)):
            return n.value if not isinstance(n.value, float) else frac(n.value)
        if isinstance(n, ast.Name):
            return self.env.get(n.id, 0)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -self.node(n.operand)
        if isinstance(n, ast.BinOp) and type(n.op) in (ast.Add, ast.Sub, ast.Mult):
            a, b = self.node(n.left), self.node(n.right)
            return a + b if isinstance(n.op, ast.Add) else a - b if isinstance(n.op, ast.Sub) else a * b
        if isinstance(n, ast.Subscript):
            return self.node(n.value)[self.node(n.slice)]
        if isinstance(n, ast.BoolOp):
            vals = [self.node(v) for v in n.values]
            return all(vals) if isinstance(n.op, ast.And) else any(vals)
        if isinstance(n, ast.Compare) and len(n.ops) == 1:
            a, b = self.node(n.left), self.node(n.comparators[0])
            op = type(n.ops[0])
            return {ast.Eq: a == b, ast.NotEq: a != b, ast.Lt: a < b, ast.LtE: a <= b,
                    ast.Gt: a > b, ast.GtE: a >= b}[op]
        if isinstance(n, ast.Call):
            args = [self.node(a) for a in n.args]
            if isinstance(n.func, ast.Name) and n.func.id == "valueOf":
                return frac(args[0])
            if isinstance(n.func, ast.Attribute) and n.func.attr in METHODS:
                return METHODS[n.func.attr](self.node(n.func.value), *args)
        raise ValueError(f"not allowed: {ast.dump(n)}")

    def run_block(self, el):
        for c in el:
            if c.tag == "EVAL":
                name, expr = c.get("exec").split("=", 1)
                self.env[name.strip()] = self.ev(rewrite(expr))
            elif c.tag == "EXECUTE":
                self.run_block(self.methods[c.get("method")])
            elif c.tag == "IF":
                branch = c.find("THEN") if self.ev(rewrite(c.get("expr"))) else c.find("ELSE")
                if branch is not None:
                    self.run_block(branch)

    def run(self, inputs):
        base = dict(self.env)
        for i in self.root.iter("INPUT"):
            d = i.get("default")
            self.env[i.get("name")] = self.ev(rewrite(d)) if d else 0
        for k, v in inputs.items():
            self.env[k] = frac(v) if isinstance(v, str) else v
        self.run_block(self.root.find(".//MAIN"))
        out = {o.get("name"): self.env.get(o.get("name"), 0) for o in self.root.iter("OUTPUT")}
        self.env = base
        return out


def cents(lo, hi, p=1.0):
    return rnd.randint(lo, hi) if rnd.random() < p else 0


def case():
    stkl = rnd.randint(1, 6)
    lzz = rnd.randint(1, 4)
    scale = {1: 1, 2: 12, 3: 360 / 7, 4: 360}[lzz]
    re4 = int(rnd.choice([rnd.randint(0, 3_000_000), rnd.randint(0, 25_000_000)]) / scale)
    pens = rnd.random() < 0.4
    vbez = rnd.randint(0, re4) if pens else 0
    c = dict(STKL=stkl, LZZ=lzz, RE4=re4, VBEZ=vbez, R=rnd.randint(0, 1),
             KRV=int(rnd.random() < 0.2), ALV=int(rnd.random() < 0.2), PKV=int(rnd.random() < 0.2),
             KVZ=str(rnd.choice([0, 1.7, 2.5, 2.9, 3.4])), PVS=int(rnd.random() < 0.1))
    c["PVZ"] = int(rnd.random() < 0.4)
    c["PVA"] = 0 if c["PVZ"] else rnd.randint(0, 4)
    c["PKPV"] = cents(0, 100_000) if c["PKV"] else 0
    c["PKPVAGZ"] = cents(0, 50_000, 0.6) if c["PKV"] else 0
    c["ZKF"] = str(rnd.choice([0, 0, 0.5, 1, 1.5, 2, 3])) if stkl <= 4 else "0"
    c["af"] = 1 if stkl == 4 and rnd.random() < 0.4 else 0
    c["f"] = round(rnd.uniform(0.5, 1.0), 3) if c["af"] else 1.0
    if not c["af"]:
        c["LZZFREIB"] = cents(0, re4, 0.3)
        c["LZZHINZU"] = cents(0, 200_000, 0.15) if stkl != 6 else 0
    if pens or rnd.random() < 0.1:
        c["VJAHR"] = rnd.randint(1995, 2062)
        c["VBEZM"] = rnd.randint(0, 600_000)
        c["VBEZS"] = cents(0, 500_000, 0.3)
        c["ZMVB"] = rnd.randint(0 if lzz != 1 else 1, 12)
    if rnd.random() < 0.3:
        c["ALTER1"] = 1
        c["AJAHR"] = rnd.randint(1995, 2062)
    if rnd.random() < 0.5:
        sonstb = cents(0, 5_000_000, 0.9)
        c["SONSTB"] = sonstb
        c["SONSTENT"] = cents(0, sonstb, 0.3)
        c["VBS"] = cents(0, sonstb, 0.3) if pens else 0
        c["STERBE"] = cents(0, c["VBS"], 0.4) if c["VBS"] else 0
        c["MBV"] = cents(0, 300_000, 0.2)
        c["JRE4"] = int(re4 * scale) + cents(0, 1_000_000, 0.3)
        c["JVBEZ"] = min(int(vbez * scale), c["JRE4"])
        c["JRE4ENT"] = cents(0, c["JRE4"] // 2, 0.15)
        c["JFREIB"] = 0 if c["af"] else cents(0, 1_000_000, 0.3)
        c["JHINZU"] = cents(0, 500_000, 0.15) if stkl != 6 and not c["af"] else 0
    return c


def edge_case():
    """Rare paths: untaxed benefits (MBV) that make the tax on other emoluments negative, with the factor method."""
    c = case()
    c["STKL"] = rnd.choice([1, 3, 4, 4, 4])
    c["af"], c["f"] = 0, 1.0
    if c["STKL"] == 4 and rnd.random() < 0.7:
        c["af"], c["f"] = 1, round(rnd.uniform(0.5, 1.0), 3)
        c["LZZFREIB"] = c["LZZHINZU"] = c["JFREIB"] = c["JHINZU"] = 0
    c["ZKF"] = c["ZKF"] if c["STKL"] <= 4 else "0"
    c["SONSTB"] = cents(0, 200_000, 0.5)
    c["SONSTENT"] = c["VBS"] = c["STERBE"] = 0
    c["MBV"] = rnd.randint(1, 3_000_000)
    c["R"] = 1
    c["JRE4"] = c.get("JRE4") or int(c["RE4"] * {1: 1, 2: 12, 3: 360 / 7, 4: 360}[c["LZZ"]])
    c["JVBEZ"] = min(c.get("JVBEZ", 0), c["JRE4"])
    return c


def to_vk(c):
    g = lambda k: c.get(k, 0)
    e = lambda k: str(Decimal(g(k)) / 100)
    return dict(stkl=["i", "ii", "iii", "iv", "v", "vi"][c["STKL"] - 1],
                lzz=["year", "month", "week", "day"][c["LZZ"] - 1],
                wage=e("RE4"), zkf=c["ZKF"], r=str(bool(c["R"])).lower(),
                ins=dict(krv=bool(c["KRV"]), alv=bool(c["ALV"]), pkv=bool(c["PKV"]), kvz=c["KVZ"], pvs=bool(c["PVS"]),
                         pvz=bool(c["PVZ"]), pva=c["PVA"], pkpv=e("PKPV"), pkpvagz=e("PKPVAGZ")),
                af=str(bool(c["af"])).lower(), f=str(c["f"]), lzzfreib=e("LZZFREIB"), lzzhinzu=e("LZZHINZU"),
                vbez=e("VBEZ"), vbezm=e("VBEZM"), vbezs=e("VBEZS"), vjahr=str(g("VJAHR")), zmvb=str(g("ZMVB")),
                alter1=str(bool(g("ALTER1"))).lower(), ajahr=str(g("AJAHR")), sonstb=e("SONSTB"),
                sonstent=e("SONSTENT"), sterbe=e("STERBE"), vbs=e("VBS"), mbv=e("MBV"), jre4=e("JRE4"),
                jre4ent=e("JRE4ENT"), jvbez=e("JVBEZ"), jfreib=e("JFREIB"), jhinzu=e("JHINZU"))


def main():
    machine = Machine(ET.parse(sys.argv[1]).getroot())
    for n in range(COUNT):
        c = case() if n < COUNT - EDGE else edge_case()
        out = machine.run({k: (str(v) if isinstance(v, int) and k not in INTS else v) for k, v in c.items()})
        euros = {k.lower(): str(Decimal(int(out[k])) / 100) for k in OUT}
        print(json.dumps({"inputs": to_vk(c), "expected": euros}, ensure_ascii=False))


if __name__ == "__main__":
    main()
