"""Validate the four recorded step traces (Runs 9-12) and generate readable logs.

Reads Run9_BC_trace.json ... Run12_RC2_trace.json (produced by collect_trace.js,
which drove the simulator's own stepForward() and recorded every step), checks
every cycle increment against the instruction costs and penalty messages, then
writes RunN_*_StepLog.md and trace_summary.json.

Run: python3 analyze_traces.py
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
CASES = {"best": ("9", "BC"), "worst": ("10", "WC"), "real1": ("11", "RC1"), "real2": ("12", "RC2")}
RUN_ID = {"best": "BC-50-R3", "worst": "WC-50-R3", "real1": "RC1-50-R3", "real2": "RC2-50-R3"}
COSTS = {"0x00": 1, "0x04": 1, "0x08": 3, "0x0C": 1, "0x10": 1, "0x14": 1, "0x18": 2,
         "0x1C": 1, "0x20": 3, "0x24": 1, "0x28": 1, "0x2C": 1, "0x30": 1}
DARK = ["0x08", "0x0C", "0x10", "0x1C", "0x20", "0x24", "0x28", "0x2C", "0x30"]
BRIGHT = ["0x08", "0x0C", "0x10", "0x14", "0x18", "0x20", "0x24", "0x28", "0x2C", "0x30"]

summary = {}
for case, (number, prefix) in CASES.items():
    path = ROOT / f"Run{number}_{prefix}_trace.json"
    trace = json.loads(path.read_text())
    assert trace["case"] == case and len(trace["input"]) == 16
    steps = trace["steps"]
    pix_cyc, pix_cache, pix_branch = [], [], []
    pixel, cycles = [], 0
    for step in steps:
        addr = step["pc"]
        miss = "Cache MISS" in step["summary"]
        mispred = "Branch MISPREDICT" in step["summary"]
        penalty = (47 if miss else 0) + (15 if mispred else 0)
        assert step["cyclesAdded"] == COSTS[addr] + penalty, (case, addr, step)
        cycles += step["cyclesAdded"]
        if addr == "0x08":
            pixel.append({"input": step["r3"], "cache": "MISS" if miss else "HIT", "branch": None,
                          "cycles": COSTS[addr], "delay": penalty})
        elif addr not in ("0x00", "0x04"):
            pixel[-1]["cycles"] += COSTS[addr]
            pixel[-1]["delay"] += penalty
            if addr == "0x10":
                pixel[-1]["branch"] = "MISPREDICT" if mispred else "HIT"
            elif addr == "0x20":
                pixel[-1]["output"] = step["r4"]
            elif addr == "0x30":
                pixel[-1]["running"] = step["runningCycles"]
    assert cycles == steps[-1]["runningCycles"], case
    assert len(pixel) == 16 and all("cache" in p and "branch" in p and "output" in p for p in pixel)
    assert sum(p["cycles"] for p in pixel) == sum(13 if p["input"] < 128 else 15 for p in pixel)
    assert sum(p["delay"] for p in pixel) == 47 * sum(p["cache"] == "MISS" for p in pixel) + 15 * sum(p["branch"] == "MISPREDICT" for p in pixel)
    dark_count = sum(p["input"] < 128 for p in pixel)
    base_cycles = 2 + sum(sum(COSTS[a] for a in (DARK if p["input"] < 128 else BRIGHT)) for p in pixel)
    misses = sum(p["cache"] == "MISS" for p in pixel)
    wrong = sum(p["branch"] == "MISPREDICT" for p in pixel)
    assert cycles == base_cycles + 47 * misses + 15 * wrong, case
    assert steps[-1]["pixelIndex"] == 16 and len(steps) == 2 + sum(9 if p["input"] < 128 else 10 for p in pixel)
    hits = 16 - misses
    correct = 32 - wrong
    summary[case] = {"run": int(number), "run_id": RUN_ID[case], "case": case,
                     "cycles": cycles, "base_cycles": base_cycles, "hits": hits, "misses": misses,
                     "correct": correct, "wrong": wrong, "brightness_correct": 16 - wrong,
                     "branches": 32, "stalls": 47 * misses + 15 * wrong,
                     "steps": len(steps), "pixels": pixel, "trace_file": path.name}
    lines = [f"# Run {number} step log: {RUN_ID[case]}", "",
             f"Part of [Final_Report.md](../Final_Report.md). Recorded on 29 September 2026 by stepping the",
             "simulator one instruction at a time and logging the state after every step",
             "(collect_trace.js). This is a genuine step record, not a reconstruction.", "",
             f"Case: {case}. Total cycles: **{cycles}**. Base instruction cycles: {base_cycles}.",
             f"Cache: {hits} hits / {misses} misses. Brightness predictions: {16 - wrong} correct / {wrong} wrong (of 16);",
             f"loop checks: 16/16 correct. All branch outcomes: {correct}/32 correct.",
             f"Stall cycles: {47 * misses + 15 * wrong} = {misses} × 47 + {wrong} × 15. Steps recorded: {len(steps)}.", "",
             "Screenshots: " + ", ".join(f"[{i}](Run{number}_{prefix}_{i:02d}_{name}.png)" for i, name in
             enumerate(["setup", "first_load", "first_branch", "pixel1_done", "pixel8_done", "final"], 1)) + ".", "",
             "## Per-pixel events (as recorded)", "",
             "| Pixel | Input | Output | Cache at 0x08 | Brightness at 0x10 | Instruction cycles | Delay cycles | Running cycles |",
             "|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(pixel, 1):
        lines.append(f"| {i} | {p['input']} | {p['output']} | {p['cache']} | {p['branch']} | {p['cycles']} | {p['delay']} | {p['running']} |")
    lines += ["", f"Reconciliation: `{base_cycles} + {misses} × 47 + {wrong} × 15 = {cycles}`.", "",
              "## Full instruction log", "",
              "| Step | PC | Cycles added | Running | Pixel | Cache event | Branch event |",
              "|---|---|---|---|---|---|---|"]
    for i, step in enumerate(steps, 1):
        cache = "MISS" if "Cache MISS" in step["summary"] else ("HIT" if "Cache HIT" in step["summary"] else "")
        branch = "MISPREDICT" if "Branch MISPREDICT" in step["summary"] else ("HIT" if "Branch HIT" in step["summary"] else "")
        lines.append(f"| {i} | {step['pc']} | {step['cyclesAdded']} | {step['runningCycles']} | {step['pixelIndex']} | {cache} | {branch} |")
    lines.append("")
    (ROOT / f"Run{number}_{prefix}_StepLog.md").write_text("\n".join(lines))
    print(f"Run {number} {RUN_ID[case]}: {cycles} cycles, {len(steps)} steps, base {base_cycles}, {misses} misses, {wrong} wrong — verified")

(ROOT / "trace_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("trace_summary.json written")
