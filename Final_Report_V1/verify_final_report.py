"""Read-only checks for the twelve-run report package.

Verifies source and evidence checksums, Runs 1-8 against their archived logs,
Runs 9-12 against their raw step traces, every numeric table in Final_Report.md,
the 800 measured optimization runs, the marking arithmetic in Grading.md and
every local link. Python 3 standard library only.

This does not authenticate screenshot capture, measure hardware, or decide
academic credit. The qualitative judgment in Grading.md follows from the stated
evidence and the proposed rubric recorded there.
"""
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
NAMES = {"best": "Best", "worst": "Worst", "real1": "Real 1", "real2": "Real 2"}
PREFIXES = {"best": "BC", "worst": "WC", "real1": "RC1", "real2": "RC2"}
ORDER = ["best", "worst", "real1", "real2"]
TRACE_FILES = {"best": "Run9_BC_trace.json", "worst": "Run10_WC_trace.json",
               "real1": "Run11_RC1_trace.json", "real2": "Run12_RC2_trace.json"}
STEP_NAMES = ["setup", "first_load", "first_branch", "pixel1_done", "pixel8_done", "final"]
DARK = ["0x08", "0x0C", "0x10", "0x1C", "0x20", "0x24", "0x28", "0x2C", "0x30"]
BRIGHT = ["0x08", "0x0C", "0x10", "0x14", "0x18", "0x20", "0x24", "0x28", "0x2C", "0x30"]
COSTS = {"0x00": 1, "0x04": 1, "0x08": 3, "0x0C": 1, "0x10": 1, "0x14": 1, "0x18": 2,
         "0x1C": 1, "0x20": 3, "0x24": 1, "0x28": 1, "0x2C": 1, "0x30": 1}
BRANCHES = {"baseline": 32, "branchfree": 16, "unrolled": 20, "looptest": 32, "combined": 4}
PROGRAM_LABELS = {"branchfree": "Branch-free", "unrolled": "Unrolled", "looptest": "Loop-test", "combined": "Combined"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def q(value, places):
    return Decimal(str(value)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


def pct(numerator, denominator):
    return f"{q(Decimal(numerator) * 100 / Decimal(denominator), 1)}%"


def tables(text):
    result, current = [], []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            current.append([cell.strip() for cell in line.strip("|").split("|")])
        elif current:
            check(len(current) >= 2, "Malformed Markdown table")
            check(all(len(row) == len(current[0]) for row in current), "Uneven Markdown table columns")
            result.append((current[0], current[2:]))
            current = []
    return result


def table_named(text, name):
    marker = f"<!-- table:{name} -->"
    check(text.count(marker) == 1, f"Missing or duplicate table marker: {name}")
    return tables(text.split(marker)[1])[0][1]


def equal_rows(text, name, expected):
    actual = table_named(text, name)
    expected = [[str(cell) for cell in row] for row in expected]
    check(len(actual) == len(expected), f"{name}: wrong row count ({len(actual)} vs {len(expected)})")
    for index, (got, wanted) in enumerate(zip(actual, expected), 1):
        check(got == wanted, f"{name}, row {index}:\n  got {got}\n  expected {wanted}")


def metric(body, name):
    match = re.search(r"^" + re.escape(name) + r": (.+)$", body, re.M)
    check(match is not None, f"Missing log metric: {name}")
    return match.group(1)


def read_log_runs(source):
    text = (ROOT / "Sources" / source / "Logs.md").read_text(encoding="utf-8")
    result = {}
    for match in re.finditer(r"^## Run (\d+): [^\n]+\n(.*?)(?=^## |\Z)", text, re.M | re.S):
        number, body = match.groups()
        result[int(number)] = body
    return result


def verify_sources():
    manifest = json.loads((ROOT / "source_manifest.json").read_text())
    commits = {"Local": "16affd82bf9f668d5671e055aa3e76297dfe63dd",
               "Scarlet": "016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9"}
    for label, commit in commits.items():
        check(manifest["repositories"][label]["commit"] == commit, f"Source commit changed: {label}")
    check(len(manifest["files"]) == 41, "Expected 41 source files")
    for item in manifest["files"]:
        path = ROOT / item["path"]
        check(path.is_file(), f"Missing source: {path}")
        content = path.read_bytes()
        check(len(content) == item["bytes"], f"Source size changed: {path}")
        check(hashlib.sha256(content).hexdigest() == item["sha256"], f"Source checksum changed: {path}")
    for name in ["Project1_CPU_Simulator.html",
                 "Project 1 Scenario_ CPU Instruction Execution - Image Brightness Processing.md",
                 "How to Use Project 1 CPU Simulator - Quick Guide.md"]:
        check((ROOT / "Sources/Local" / name).read_bytes() == (ROOT / "Sources/Scarlet" / name).read_bytes(),
              f"Shared source differs: {name}")
    images = [item for item in manifest["files"] if item["path"].endswith(".png")]
    check(len(images) == len({item["sha256"] for item in images}) == 20, "Expected 20 distinct source screenshots")
    print("Source integrity: 41 archived files and 20 distinct screenshots; shared instructions and simulator match.")


def verify_evidence_manifest():
    manifest = json.loads((ROOT / "evidence_manifest.json").read_text())
    recorded = {item["path"] for item in manifest["files"]}
    actual = set()
    for folder in ["Traces", "Optimizations"]:
        for file in (ROOT / folder).iterdir():
            if file.is_file():
                actual.add(str(file.relative_to(ROOT)))
    check(recorded == actual, f"Evidence manifest mismatch: {recorded ^ actual}")
    for item in manifest["files"]:
        path = ROOT / item["path"]
        content = path.read_bytes()
        check(len(content) == item["bytes"], f"Evidence size changed: {path}")
        check(hashlib.sha256(content).hexdigest() == item["sha256"], f"Evidence checksum changed: {path}")
    print(f"Evidence integrity: {len(recorded)} trace and optimization files match their recorded checksums.")


def verify_runs_1_8(runs):
    local, scarlet = read_log_runs("Local"), read_log_runs("Scarlet")
    logs = {**{n: ("Local", body) for n, body in local.items()}, **{n: ("Scarlet", body) for n, body in scarlet.items()}}
    check(set(logs) == set(range(1, 9)), "Expected Runs 1-8 in the archived logs")
    provenance = {}
    counts_table = []
    for r in runs:
        n = r["run"]
        check(1 <= n <= 8, "verify_runs_1_8 received a trace run")
        source, body = logs[n]
        check(r["source"] == source, f"Run {n}: wrong source")
        case = metric(body, "Test Case")
        check(r["case"] == case, f"Run {n}: case mismatch")
        speed = int(re.search(r"^SPEED: (\d+) ms", body, re.M).group(1))
        check(r["speed_ms"] == speed, f"Run {n}: speed mismatch")
        check(r["run_id"] == f"{PREFIXES[case]}-{speed}-R{1 if n <= 4 else 2}", f"Run {n}: wrong run id")
        grids = [rows for header, rows in tables(body) if header == [""] + list(map(str, range(1, 9)))]
        check(len(grids) == 2, f"Run {n}: expected two pixel grids")
        cells = [[cell for row in grid for cell in row[1:]] for grid in grids]
        inputs = [int(re.match(r"\d+", cell).group()) for cell in cells[0]]
        outputs = [int(cell) for cell in cells[1]]
        check(r["inputs"] == inputs and r["outputs"] == outputs, f"Run {n}: data differs from log")
        check(outputs == [p + 32 if p < 128 else p - 8 for p in inputs], f"Run {n}: brightness rule")
        basis = ["case definition" if case == "best" else "inferred from output" if "deduced" in cell
                 else "read from screenshot" for cell in cells[0]]
        check(r["input_provenance"] == basis, f"Run {n}: provenance")
        for value in basis:
            provenance[value] = provenance.get(value, 0) + 1
        for field, label in {"cycles": "Total Cycles", "hits": "Cache Hits", "misses": "Cache Misses",
                             "correct": "Correct Predictions", "branches": "Total Branches",
                             "stalls": "Stall Cycles"}.items():
            check(r[field] == int(metric(body, label)), f"Run {n}: {field}")
        check(metric(body, "Pixels Processed") == "16/16", f"Run {n}: incomplete")
        check(metric(body, "Cycles Per Pixel") == str(q(Decimal(r["cycles"]) / 16, 2)), f"Run {n}: logged CPP")
        check(metric(body, "Hit Rate") == pct(r["hits"], 16), f"Run {n}: logged hit rate")
        check(metric(body, "Accuracy") == pct(r["correct"], 32), f"Run {n}: logged accuracy")
        image = metric(body, "Estimated Full Image (256×256)")
        check(int(image.split()[0].replace(",", "")) == r["cycles"] * 4096, f"Run {n}: logged image")
        check(r["hits"] + r["misses"] == 16 and r["branches"] == 32, f"Run {n}: denominators")
        dark = sum(1 for p in inputs if p < 128)
        base = 2 + 13 * dark + 15 * (16 - dark)
        check(r["stalls"] == 47 * r["misses"] + 15 * (32 - r["correct"]), f"Run {n}: stalls")
        check(r["cycles"] == base + r["stalls"], f"Run {n}: total")
        counts_table.append(2 + 9 * dark + 10 * (16 - dark))
    check(counts_table == [146, 154, 151, 154] * 2, "Instruction counts for Runs 1-8")
    check(provenance == {"case definition": 32, "read from screenshot": 93, "inferred from output": 3},
          f"Runs 1-8 provenance totals: {provenance}")
    print("Runs 1-8: pixels, metrics, provenance and cycle accounting all match the archived logs.")
    return counts_table


def verify_traces(runs):
    summary = json.loads((ROOT / "Traces/trace_summary.json").read_text())
    provenance = {}
    counts_table = []
    for r in runs:
        n = r["run"]
        check(9 <= n <= 12, "verify_traces received a non-trace run")
        case = r["case"]
        check(r["source"] == "Trace" and r["speed_ms"] == 50 and r["run_id"] == f"{PREFIXES[case]}-50-R3",
              f"Run {n}: trace metadata")
        raw = json.loads((ROOT / "Traces" / TRACE_FILES[case]).read_text())
        check(raw["case"] == case and len(raw["input"]) == 16, f"Run {n}: raw trace header")
        steps = raw["steps"]
        pixel, cycles = [], 0
        for step in steps:
            addr = step["pc"]
            miss = "Cache MISS" in step["summary"]
            mispred = "Branch MISPREDICT" in step["summary"]
            check(addr in COSTS, f"Run {n}: unknown PC {addr}")
            check(step["cyclesAdded"] == COSTS[addr] + 47 * miss + 15 * mispred, f"Run {n}: cycle interval at {addr}")
            cycles += step["cyclesAdded"]
            check(step["runningCycles"] == cycles, f"Run {n}: running total at {addr}")
            if addr == "0x08":
                pixel.append({"input": step["r3"], "cache": "MISS" if miss else "HIT",
                              "branch": None, "cycles": COSTS[addr], "delay": 47 * miss})
            elif addr not in ("0x00", "0x04"):
                pixel[-1]["cycles"] += COSTS[addr]
                pixel[-1]["delay"] += 15 * mispred
                if addr == "0x10":
                    pixel[-1]["branch"] = "MISPREDICT" if mispred else "HIT"
                elif addr == "0x20":
                    pixel[-1]["output"] = step["r4"]
                elif addr == "0x30":
                    pixel[-1]["running"] = step["runningCycles"]
        check(len(pixel) == 16 and all(p["branch"] and "output" in p and "running" in p for p in pixel),
              f"Run {n}: pixel segmentation")
        check(steps[-1]["r0"] == 16 and steps[-1]["r1"] == 1040, f"Run {n}: final registers")
        dark = sum(1 for p in pixel if p["input"] < 128)
        base = 2 + sum(sum(COSTS[a] for a in (DARK if p["input"] < 128 else BRIGHT)) for p in pixel)
        misses = sum(p["cache"] == "MISS" for p in pixel)
        wrong = sum(p["branch"] == "MISPREDICT" for p in pixel)
        check(len(steps) == 2 + 9 * dark + 10 * (16 - dark), f"Run {n}: step count")
        check(r["cycles"] == cycles == base + 47 * misses + 15 * wrong, f"Run {n}: totals")
        check((r["hits"], r["misses"], r["correct"], r["branches"], r["stalls"]) ==
              (16 - misses, misses, 32 - wrong, 32, 47 * misses + 15 * wrong), f"Run {n}: counters")
        check(r["inputs"] == [p["input"] for p in pixel] and r["outputs"] == [p["output"] for p in pixel],
              f"Run {n}: trace pixels")
        check(r["input_provenance"] == (["case definition"] if case == "best" else ["read from trace"]) * 16,
              f"Run {n}: trace provenance")
        for value in r["input_provenance"]:
            provenance[value] = provenance.get(value, 0) + 1
        t = summary[case]
        check((t["cycles"], t["base_cycles"], t["steps"], t["hits"], t["misses"], t["correct"], t["wrong"],
               t["branches"], t["stalls"]) == (cycles, base, len(steps), 16 - misses, misses, 32 - wrong, wrong, 32,
                                              47 * misses + 15 * wrong), f"Run {n}: trace summary")
        check(t["pixels"] == pixel, f"Run {n}: per-pixel record")
        log = (ROOT / "Traces" / f"Run{n}_{PREFIXES[case]}_StepLog.md").read_text()
        check(f"Total cycles: **{cycles}**" in log, f"Run {n}: step log total")
        check(f"`{base} + {misses} × 47 + {wrong} × 15 = {cycles}`" in log, f"Run {n}: step log reconciliation")
        screenshots = [f"Traces/Run{n}_{PREFIXES[case]}_{i:02d}_{name}.png" for i, name in enumerate(STEP_NAMES, 1)]
        check(r["screenshots"] == screenshots, f"Run {n}: screenshot list")
        for shot in screenshots:
            check((ROOT / shot).is_file(), f"Run {n}: missing {shot}")
        counts_table.append(2 + 9 * dark + 10 * (16 - dark))
        print(f"Run {n} {r['run_id']}: {cycles} cycles, {len(steps)} steps, {misses} misses, {wrong} wrong — raw trace, "
              f"log and data.json agree.")
    check(counts_table == [146, 154, 151, 154], "Trace instruction counts")
    check(provenance == {"case definition": 16, "read from trace": 48}, f"Trace provenance totals: {provenance}")
    return counts_table


def measured_means():
    return json.loads((ROOT / "Optimizations/measured_summary.json").read_text())


def verify_measurements():
    measured = measured_means()
    total = 0
    for program, branches in BRANCHES.items():
        data = json.loads((ROOT / "Optimizations" / f"measure_{program}.json").read_text())
        check(set(data) == set(ORDER), f"{program}: cases")
        for case, rows in data.items():
            base = measured["offsets"][program][case]
            check(len(rows) == 40, f"{program}/{case}: expected 40 runs")
            for row in rows:
                wrong = row["branches"] - row["correct"]
                check(row["branches"] == branches, f"{program}/{case}: branch count")
                check(row["cycles"] == base + 47 * row["misses"] + 15 * wrong, f"{program}/{case}: invariant")
                check(row["stalls"] == 47 * row["misses"] + 15 * wrong, f"{program}/{case}: stalls")
                check(row["ok"] is True, f"{program}/{case}: output check")
                if program in ("branchfree", "combined"):
                    check(wrong == 0, f"{program}/{case}: mispredictions")
                total += 1
            cell = measured["cells"][program][case]
            cycles = [row["cycles"] for row in rows]
            mean = Decimal(sum(cycles)) / Decimal(len(cycles))
            check(q(mean, 2) == Decimal(str(cell["mean"])), f"{program}/{case}: mean")
            check(cell["min"] == min(cycles) and cell["max"] == max(cycles), f"{program}/{case}: range")
    check(total == 800, f"Expected 800 measured runs, found {total}")
    print("Measurements: 800 runs satisfy cycles = base + 47 x misses + 15 x mispredictions; all outputs correct.")


def verify_report_tables(runs, report, trace_counts):
    rows = table_named(report, "runs")
    for r, row in zip(runs, rows):
        check(row[0] == str(r["run"]) and row[1] == r["run_id"], f"Runs table: run {r['run']}")
        check(("StepLog" in row[4]) == (r["run"] >= 9), f"Runs table: evidence link for run {r['run']}")

    equal_rows(report, "results", [[r["run"], NAMES[r["case"]], r["cycles"], q(Decimal(r["cycles"]) / 16, 2),
        r["hits"], r["misses"], r["correct"], r["branches"], r["stalls"]] for r in runs])
    equal_rows(report, "rates", [[r["run"], pct(r["hits"], 16), pct(r["misses"], 16), pct(r["correct"], 32),
        pct(32 - r["correct"], 32), pct(r["correct"] - 16, 16)] for r in runs])
    equal_rows(report, "reconciliation", [[r["run"], sum(1 for p in r["inputs"] if p < 128),
        sum(1 for p in r["inputs"] if p >= 128), r["cycles"] - r["stalls"], 47 * r["misses"],
        15 * (32 - r["correct"]), r["cycles"]] for r in runs])

    dark = [sum(1 for p in r["inputs"] if p < 128) for r in runs[:4]]
    equal_rows(report, "instruction-counts", [
        ["Each setup instruction: 0x00, 0x04", 1, 1, 1, 1],
        ["Each of 0x08, 0x0C, 0x10", 16, 16, 16, 16],
        ["Each of 0x14, 0x18"] + [16 - d for d in dark],
        ["0x1C"] + dark,
        ["Each of 0x20, 0x24, 0x28, 0x2C, 0x30", 16, 16, 16, 16],
        ["Total executed instructions"] + trace_counts[:4],
        ["Base cycles before delays"] + [runs[i]["cycles"] - runs[i]["stalls"] for i in range(4)],
    ])

    expected_means = []
    for case in ORDER:
        group = [r for r in runs if r["case"] == case]
        cycles = [r["cycles"] for r in group]
        mean = Decimal(sum(cycles)) / 3
        hits = sum(r["hits"] for r in group)
        correct = sum(r["correct"] for r in group)
        expected_means.append([NAMES[case], ", ".join(map(str, cycles)), max(cycles) - min(cycles), q(mean, 1),
                               q(mean / 16, 2), pct(hits, 48), pct(correct, 96), pct(correct - 48, 48)])
    equal_rows(report, "averages", expected_means)

    summary = json.loads((ROOT / "Traces/trace_summary.json").read_text())
    trace_rows = []
    for case in ORDER:
        t = summary[case]
        misses = [str(i + 1) for i, p in enumerate(t["pixels"]) if p["cache"] == "MISS"]
        wrong = [str(i + 1) for i, p in enumerate(t["pixels"]) if p["branch"] == "MISPREDICT"]
        trace_rows.append([t["run"], t["run_id"], t["cycles"], t["base_cycles"], t["steps"],
                           f"{len(misses)} (pixels {', '.join(misses)})",
                           f"{len(wrong)} (pixels {', '.join(wrong)})"])
    equal_rows(report, "trace-runs", trace_rows)

    measured = measured_means()
    cells = measured["cells"]
    offsets = measured["offsets"]
    branch_text = {"baseline": "32 (16 BLT + 16 loop)", "branchfree": "16 (loop only)",
                   "unrolled": "20 (16 BLT + 4 loop)", "looptest": "32 (16 BLT + 16 loop)",
                   "combined": "4 (loop only)"}
    program_rows = []
    for program, change, mispredictions in [
        ("baseline", "Recorded program: 13/15-cycle paths", "Possible"),
        ("branchfree", "Compute both candidates, select with `CSEL`; no `BLT`/`JMP`", "Impossible"),
        ("unrolled", "Four-pixel straight-line block; `INC #4` loop control", "Possible"),
        ("looptest", "Loop tests the pointer (`CMP R1, #1040`); counter removed", "Possible"),
        ("combined", "Unrolled block + branch-free selection", "Impossible"),
    ]:
        bases = " / ".join(str(offsets[program][case]) for case in ORDER)
        program_rows.append([PROGRAM_LABELS.get(program, "Baseline"), change, bases, branch_text[program], mispredictions])
    equal_rows(report, "programs", program_rows)

    def delta_cell(case, program):
        base = Decimal(str(cells["baseline"][case]["mean"]))
        mean = Decimal(str(cells[program][case]["mean"]))
        delta = q(mean - base, 2)
        change = q((mean - base) * 100 / base, 1)
        sign = "+" if delta >= 0 else "-"
        return f"{q(mean, 2)} ({sign}{abs(change)}%)"

    equal_rows(report, "measured", [[NAMES[case], q(Decimal(str(cells["baseline"][case]["mean"])), 2)] +
        [delta_cell(case, p) for p in ["branchfree", "unrolled", "looptest", "combined"]] for case in ORDER])
    equal_rows(report, "measured-ranges", [[NAMES[case]] +
        [f"{q(Decimal(str(cells[p][case]['mean'])), 2)} [{cells[p][case]['min']}–{cells[p][case]['max']}]"
         for p in ["baseline", "branchfree", "unrolled", "looptest", "combined"]] for case in ORDER])

    best_rows = []
    for case in ORDER:
        base = Decimal(str(cells["baseline"][case]["mean"]))
        ranked = sorted(["branchfree", "unrolled", "looptest", "combined"], key=lambda p: cells[p][case]["mean"])
        first, second = ranked[0], ranked[1]
        mean = Decimal(str(cells[first][case]["mean"]))
        margin = Decimal(str(cells[second][case]["mean"])) - mean
        change = q((mean - base) * 100 / base, 1)
        best_rows.append([NAMES[case], PROGRAM_LABELS[first], q(mean, 2),
                          f"{q(margin, 2)} over {PROGRAM_LABELS[second].lower()}", f"{abs(q(mean - base, 2))} (-{abs(change)}%)"])
    equal_rows(report, "best-strategy", best_rows)

    prefetch_rows = []
    for case in ORDER:
        mean = Decimal(str(cells["baseline"][case]["mean"]))
        misses = Decimal(str(cells["baseline"][case]["misses_mean"]))
        prefetch_rows.append([NAMES[case], q(mean, 2), misses, q(mean - 47 * misses, 2), q(mean - 47 * (misses - 1), 2)])
    equal_rows(report, "prefetch", prefetch_rows)

    image_rows, scaling_rows, savings_rows = [], [], []
    for case in ORDER:
        group = [r for r in runs if r["case"] == case]
        mean = Decimal(sum(r["cycles"] for r in group)) / 3
        image = mean * 4096
        daily = image * 2000000
        seconds = daily / Decimal(2400000000)
        saved = seconds * Decimal("0.2")
        dollars = saved / 3600 * Decimal("0.008") * Decimal("0.12") * 365
        image_rows.append([NAMES[case], q(mean, 1), f"{q(image, 0):,}"])
        scaling_rows.append([NAMES[case], f"{q(image, 0):,}", f"{q(daily, 0):,}", f"{q(seconds, 2):,}",
                             q(seconds / 14400, 4), 1])
        savings_rows.append([NAMES[case], q(saved, 2), f"${q(dollars, 6)}", "$0"])
    equal_rows(report, "image-runs", image_rows)
    equal_rows(report, "scaling", scaling_rows)
    equal_rows(report, "annual-savings", savings_rows)

    total_cycles = sum(r["cycles"] for r in runs)
    base_sum = sum(r["cycles"] - r["stalls"] for r in runs)
    cache_sum = sum(47 * r["misses"] for r in runs)
    branch_sum = sum(15 * (32 - r["correct"]) for r in runs)
    real1_mean = Decimal(sum(r["cycles"] for r in runs if r["case"] == "real1")) / 3
    real1_seconds = real1_mean * 4096 * 2000000 / Decimal(2400000000)
    active_energy = real1_seconds / 3600 * Decimal("0.008")
    one_cpp_seconds = Decimal(65536) * 2000000 / Decimal(2400000000)
    one_cpp_cost = one_cpp_seconds / 3600 * Decimal("0.008") * Decimal("0.12")
    constants = [f"{total_cycles:,}", f"{base_sum:,}", f"{cache_sum:,}", f"{branch_sum:,}",
                 f"{cache_sum + branch_sum:,}", pct(cache_sum, cache_sum + branch_sum),
                 f"${q(Decimal('0.008') * 24 * Decimal('0.12') * 365, 4)}",
                 f"{q(real1_seconds, 6):,}",  # "1,471.146667"
                 f"{q(active_energy, 8)}", f"${q(active_energy * Decimal('0.12'), 8)}",
                 f"${q(active_energy * Decimal('0.12') * 365, 5)}",
                 f"{q(real1_mean * 4096 * 2000000 * Decimal('0.8'), 0):,}",
                 f"{q(real1_seconds * Decimal('0.8'), 6):,}", f"{q(real1_seconds * Decimal('0.2'), 6)}",
                 f"{q(one_cpp_seconds, 6)}", f"${q(one_cpp_cost, 11)}",
                 f"{q(one_cpp_seconds / 2, 6)}", f"${q(one_cpp_cost / 2, 11)}",
                 f"{q(real1_seconds / 2, 6)}", f"{q(real1_mean * 4096 * 1000000, 0):,}",
                 f"{q(Decimal(210) / 16, 3)}", f"{q(real1_mean / 16, 4)}"]
    for text in constants:
        check(text in report, f"Worked-example value missing: {text}")
    print("Report tables: runs, results, rates, reconciliation, counts, averages, traces, programs, measured results, "
          "prefetch and all four cost tables verified against the data files.")


def verify_template():
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(ROOT / "Sources/Scarlet/Step_Trace_Worst_Case.xlsx") as book:
        sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
        cells = {cell.attrib["r"]: cell for cell in sheet.findall(".//m:c", ns)}
        for address in [f"{col}{row}" for col in "FG" for row in range(12, 28)] + [f"J{row}" for row in range(11, 28)]:
            cell = cells.get(address)
            if cell is not None:
                check(not "".join(cell.itertext()).strip(), f"Trace template observation: {address}")
    print("Trace workbook: all observation cells remain blank; Runs 9-12 are the trace evidence.")


def verify_grading():
    text = (ROOT / "Grading.md").read_text()
    expected_sums = {"trace": (30, 30), "performance": (25, 25), "optimization": (25, 25), "cost": (20, 20)}
    for name, (maximum, awarded) in expected_sums.items():
        rows = table_named(text, "grade-" + name)
        check(sum(int(row[1]) for row in rows) == maximum, f"{name}: max sum")
        check(sum(int(row[2]) for row in rows) == awarded, f"{name}: awarded sum")
        for row in rows:
            check(row[1] == row[2], f"{name}: unexpected partial mark in {row[0]}")
    equal_rows(text, "grade-total", [["Instruction trace", 30, 30, 0], ["Performance data", 25, 25, 0],
                                     ["Optimization analysis", 25, 25, 0], ["Extrapolation and cost", 20, 20, 0],
                                     ["Total", 100, 100, 0]])
    check("not an official instructor grade" in text, "Missing self-assessment qualification")
    check("Model measurements, not hardware" in text, "Missing model-measurement caveat")
    print("Grading arithmetic: 30 + 25 + 25 + 20 = 100/100 under the proposed rubric; 0 points deducted.")


def slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def verify_links():
    count = 0
    for file in ROOT.rglob("*.md"):
        text = file.read_text(encoding="utf-8")
        check(text.count("```") % 2 == 0, f"Unbalanced code fence: {file}")
        tables(text)
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
            check(target.exists(), f"Broken link in {file.relative_to(ROOT)}: {link}")
            if parsed.fragment:
                headings = re.findall(r"^#+ (.+)$", target.read_text(encoding="utf-8"), re.M)
                check(unquote(parsed.fragment) in [slug(h) for h in headings], f"Broken anchor: {file}: {link}")
            count += 1
    print(f"Documents: {count} local links/anchors resolve; table shapes and code fences checked.")


def main():
    verify_sources()
    verify_evidence_manifest()
    data = json.loads((ROOT / "data.json").read_text())
    runs = data["runs"]
    check([r["run"] for r in runs] == list(range(1, 13)), "data.json must contain Runs 1-12")
    report = (ROOT / "Final_Report.md").read_text(encoding="utf-8")
    verify_runs_1_8(runs[:8])
    trace_counts = verify_traces(runs[8:])
    verify_measurements()
    verify_report_tables(runs, report, trace_counts)
    verify_template()
    verify_grading()
    verify_links()
    print("PASS: twelve-run package is internally consistent; traces and measured optimizations verified.")


if __name__ == "__main__":
    main()
