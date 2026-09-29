"""Validate and summarize the measured optimization runs.

Reads measure_baseline.json and the four variant files, checks the exact cycle
invariant (base + 47 x misses + 15 x wrong) for every one of the 800 runs,
checks branch denominators, then writes measured_summary.json.

Run: python3 summarize_measurements.py
"""
from pathlib import Path
import json
import math
from decimal import Decimal, ROUND_HALF_UP

ROOT = Path(__file__).resolve().parent
FIXED = {
    "best": [0] * 16,
    "worst": [64, 192] * 8,
    "real1": [35, 180, 42, 60, 210, 88, 50, 115, 230, 45, 72, 195, 30, 95, 80, 140],
    "real2": [215, 210, 254, 221, 231, 244, 220, 236, 39, 27, 41, 71, 80, 92, 8, 55],
}
# branches = executed conditional-branch instructions per completed run
# baseline, branchfree: BNE per pixel (16) plus, for baseline, BLT per pixel (16)
# unrolled/looptest: BLT per pixel (16) plus BNE per group (4) or per pixel (16)
# combined/looptest variants share the straight-line block or the pointer loop
PROGRAMS = {
    "baseline": ("measure_baseline.json", "Baseline (recorded program)", 32),
    "branchfree": ("measure_branchfree.json", "Branch-free selection", 16),
    "unrolled": ("measure_unrolled.json", "Four-pixel loop unrolling", 20),
    "looptest": ("measure_looptest.json", "Pointer loop test (counter removed)", 32),
    "combined": ("measure_combined.json", "Branch-free + unrolling", 4),
}


def base_cycles(program, case):
    pixels = FIXED[case]
    if program == "baseline":
        return 2 + sum(13 if p < 128 else 15 for p in pixels)
    if program == "branchfree":
        return 2 + 16 * 14
    if program == "unrolled":
        return 2 + sum((9 if p < 128 else 11) + 1 for p in pixels)
    if program == "looptest":
        return 2 + sum(12 if p < 128 else 14 for p in pixels)
    if program == "combined":
        return 2 + 16 * 11
    raise ValueError(program)


result = {"programs": {}, "cells": {}, "offsets": {}}
for program, (file, label, branches) in PROGRAMS.items():
    data = json.loads((ROOT / file).read_text())
    result["programs"][program] = label
    result["offsets"][program] = {case: base_cycles(program, case) for case in FIXED}
    for case, rows in data.items():
        base = base_cycles(program, case)
        for row in rows:
            wrong = row["branches"] - row["correct"]
            assert row["branches"] == branches, (program, case, row)
            assert wrong == row["wrong"], (program, case, row)
            if program in ("branchfree", "combined"):
                assert wrong == 0, (program, case, row)
            assert row["cycles"] == base + 47 * row["misses"] + 15 * wrong, (program, case, row)
            assert row["stalls"] == 47 * row["misses"] + 15 * wrong
            assert row["ok"] is True
        cycles = [row["cycles"] for row in rows]
        exact = Decimal(sum(cycles)) / Decimal(len(cycles))
        sem = Decimal(str(math.sqrt(sum((c - float(exact)) ** 2 for c in cycles) / (len(cycles) - 1) / len(cycles))))
        result["cells"].setdefault(program, {})[case] = {
            "n": len(rows), "mean": float(exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "min": min(cycles), "max": max(cycles),
            "sem": float(sem.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
            "misses_mean": float((Decimal(sum(r["misses"] for r in rows)) / len(rows)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)),
            "wrong_mean": float((Decimal(sum(r["wrong"] for r in rows)) / len(rows)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)),
            "base": base,
        }
        print(f"{program:10s} {case:6s} n={len(rows)} base={base:3d} mean={float(exact):7.2f} min={min(cycles):3d} max={max(cycles):3d} sem={float(sem):4.1f}")
(ROOT / "measured_summary.json").write_text(json.dumps(result, indent=2) + "\n")
print("measured_summary.json written; all 800 runs satisfy cycles = base + 47 x misses + 15 x wrong")
