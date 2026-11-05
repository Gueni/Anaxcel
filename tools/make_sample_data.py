#!/usr/bin/env python
# coding=utf-8
"""Generate sample spreadsheets in data/ for trying out and testing Anaxcel.

Usage:  py tools/make_sample_data.py
"""
import os

import numpy as np
import pandas as pd

ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA        = os.path.join(ROOT, "data")
rng         = np.random.default_rng(42)

DEFECTS     = ["Scratch", "Dent", "Misalignment", "Crack", "Discoloration", "Missing part",
               "Loose screw", "Bad solder", "Wrong label", "Burr", "Warping", "Contamination"]
WEIGHTS     = np.array([30, 22, 14, 9, 7, 5, 4, 3, 2, 2, 1, 1], dtype=float)
LINES       = ["Line A", "Line B", "Line C"]
PRODUCTS    = ["Widget", "Gadget", "Gizmo", "Sprocket", "Bracket", "Housing", "Valve", "Pump"]
REGIONS     = ["North", "South", "East", "West"]


def defects(n, start):
    return pd.DataFrame({
        "Date":       pd.to_datetime(start) + pd.to_timedelta(rng.integers(0, 90, n), unit="D"),
        "Line":       rng.choice(LINES, n),
        "Defect":     rng.choice(DEFECTS, n, p=WEIGHTS / WEIGHTS.sum()),
        "Count":      rng.integers(1, 20, n),
        "Cost (EUR)": rng.gamma(2.0, 35.0, n).round(2),
    }).sort_values("Date", ignore_index=True)


def sales(n):
    return pd.DataFrame({
        "Order":    np.arange(100000, 100000 + n),
        "Region":   rng.choice(REGIONS, n),
        "Product":  rng.choice(PRODUCTS, n, p=[.35, .2, .15, .1, .08, .06, .04, .02]),
        "Quantity": rng.integers(1, 50, n),
        "Revenue":  rng.lognormal(5, 1, n).round(2),
    })


def main():
    os.makedirs(DATA, exist_ok=True)
    defects(400, "2026-01-01").to_excel(os.path.join(DATA, "defects_q1.xlsx"), index=False)
    defects(450, "2026-04-01").to_excel(os.path.join(DATA, "defects_q2.xlsx"), index=False)
    defects(500, "2026-07-01").to_csv(os.path.join(DATA, "defects_q3.csv"), index=False)
    defects(300, "2026-10-01").to_csv(os.path.join(DATA, "defects_q4_semicolon.csv"), index=False, sep=";")
    sales(200_000).to_csv(os.path.join(DATA, "sales_large.csv"), index=False)
    sales(50).to_csv(os.path.join(DATA, "sales_no_header.csv"), index=False, header=False)
    for name in sorted(os.listdir(DATA)):
        print(f"  data/{name}  ({os.path.getsize(os.path.join(DATA, name)) // 1024} KB)")


if __name__ == "__main__":
    main()
