from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import re
from urllib.parse import unquote

root = Path.cwd()
logs = (root / "Logs.md").read_text()
report = (root / "Analysis Report.md").read_text()
next_steps = (root / "Next Steps Analysis.md").read_text()
simulator = (root / "Project1_CPU_Simulator.html").read_text()


def tables(text):
    result, current = [], []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            current.append([x.strip() for x in line.strip("|").split("|")])
        elif current:
            assert len(current) >= 2
            assert all(len(row) == len(current[0]) for row in current)
            result.append((current[0], current[2:]))
            current = []
    return result


def get_table(text, field):
    matches = [rows for header, rows in tables(text) if field in header]
    assert len(matches) == 1, field
    return matches[0]


def rounded(number, places):
    return str(Decimal(number).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


links = 0
for name, text in [("Logs.md", logs), ("Analysis Report.md", report), ("Next Steps Analysis.md", next_steps)]:
    tables(text)
    assert text.count("```") % 2 == 0, name
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        path, _, anchor = target.partition("#")
        file = root / unquote(path or name)
        assert file.exists(), (name, target)
        if anchor:
            headings = re.findall(r"^#+ (.+)$", file.read_text(), re.M)
            assert unquote(anchor) in [slug(h) for h in headings], (name, target)
        links += 1

costs = {pc: int(cycles) for pc, cycles in re.findall(
    r"\{ addr: '(0x[0-9A-Fa-f]+)', code: '[^']*', cycles: (\d+) \}", simulator
)}
dark_path = ["0x08", "0x0C", "0x10", "0x1C", "0x20", "0x24", "0x28", "0x2C", "0x30"]
bright_path = ["0x08", "0x0C", "0x10", "0x14", "0x18", "0x20", "0x24", "0x28", "0x2C", "0x30"]
assert sum(costs[pc] for pc in dark_path) == 13
assert sum(costs[pc] for pc in bright_path) == 15

run_texts = re.split(r"^## Run \d+: .+$", logs, flags=re.M)[1:]
trace_texts = re.split(r"^### B\.\d .+$", report, flags=re.M)[1:]
assert len(run_texts) == len(trace_texts) == 4
instruction_counts = next(rows for header, rows in tables(report)
                          if header == ["Instruction", "Best", "Worst", "Real Case 1", "Real Case 2"])
comparison = get_table(report, "Original recorded cycles")
performance = dict((row[0], row[1:]) for row in get_table(report, "Metric"))
count_summary = instruction_counts[-2:]
data_tables = next(rows for header, rows in tables(report) if header[0] == "Case" and "Dark pixels" in header)

for run_number, (run, trace) in enumerate(zip(run_texts, trace_texts)):
    grids = [rows for header, rows in tables(run) if header == ["", "1", "2", "3", "4", "5", "6", "7", "8"]]
    assert len(grids) == 2
    input_cells, output_cells = [[cell for row in grid for cell in row[1:]] for grid in grids]
    inputs = [int(re.match(r"\d+", cell).group()) for cell in input_cells]
    outputs = [int(cell) for cell in output_cells]
    assert len(inputs) == len(outputs) == 16
    assert [p + 32 if p < 128 else p - 8 for p in inputs] == outputs
    metrics = {key: value.strip() for key, value in re.findall(r"^([A-Za-z /()×0-9]+): (.+)$", run, re.M)}
    cycles = int(metrics["Total Cycles"])
    misses = int(metrics["Cache Misses"])
    hits = int(metrics["Cache Hits"])
    wrong = int(metrics["Total Branches"]) - int(metrics["Correct Predictions"])
    stalls = int(metrics["Stall Cycles"])
    count = Counter({"0x00": 1, "0x04": 1})
    cumulative = costs["0x00"] + costs["0x04"]
    pixel_rows = get_table(trace, "Pixel")
    assert len(pixel_rows) == 16
    for index, (pixel, output, row) in enumerate(zip(inputs, outputs, pixel_rows), 1):
        path = dark_path if pixel < 128 else bright_path
        cost = sum(costs[pc] for pc in path)
        count.update(path)
        cumulative += cost
        inferred = run_number == 3 and index in [9, 12]
        expected_input = str(pixel) + (" (inferred)" if inferred else "")
        assert row == [str(index), expected_input, str(output), "Dark" if pixel < 128 else "Bright", str(cost), str(cumulative)], row
    assert stalls == 47*misses + 15*wrong
    assert cycles == cumulative + stalls
    assert hits + misses == 16
    for row in instruction_counts[:-2]:
        pc = row[0].split(":")[0]
        assert int(row[run_number+1]) == count[pc], (pc, run_number)
    assert int(count_summary[0][run_number+1]) == sum(count.values())
    assert int(count_summary[1][run_number+1]) == cumulative
    assert performance["Total cycles"][run_number] == str(cycles)
    assert performance["CPP, rounded to two decimals"][run_number] == rounded(Decimal(cycles)/16, 2)
    assert performance["Stall cycles"][run_number] == str(stalls)
    final_regs = dict(get_table(run, "Register"))
    assert int(final_regs["R3"], 16) == inputs[-1]
    assert int(final_regs["R4"], 16) == outputs[-1]
    assert int(final_regs["R0"], 16) == 16
    assert int(final_regs["R1"], 16) == 1040
    expected_cells = []
    for saved in [misses*47, wrong*15, 36]:
        expected_cells.append(f"{cycles-saved} ({rounded(Decimal(saved)/cycles*100,1)}%)")
    assert comparison[run_number][1:] == [str(cycles)] + expected_cells
    dark = sum(p < 128 for p in inputs)
    assert data_tables[run_number][1:] == [str(dark), str(16-dark), str(cumulative), str(47*misses), str(15*wrong), str(cycles)]
    print(f"Run {run_number+1}: checked all 16 pixel paths, {sum(count.values())} instruction executions, final registers, and {cycles} total cycles.")

assert "fifth complete experiment is still required" in report
assert "Individual event positions still missing" in report
assert "No optimized versions have been tested" in report
assert "upper part of the instruction list" in logs
print(f"All four logs reconcile. Verified 64 pixel rows, calculated comparisons, and {links} local links and anchors. Missing experiments remain explicitly identified.")
