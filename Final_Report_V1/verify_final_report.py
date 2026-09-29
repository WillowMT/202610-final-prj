"""Read-only checks for the archived eight-run report. Python 3, standard library only.

This verifies internal consistency, not screenshot authenticity, measured optimizations,
or the academic judgment used to assign partial credit in Grading.md.
"""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
NAMES = {"best": "Best", "worst": "Worst", "real1": "Real 1", "real2": "Real 2"}
PREFIXES = {"best": "BC", "worst": "WC", "real1": "RC1", "real2": "RC2"}
DARK = "0x08 0x0C 0x10 0x1C 0x20 0x24 0x28 0x2C 0x30".split()
BRIGHT = "0x08 0x0C 0x10 0x14 0x18 0x20 0x24 0x28 0x2C 0x30".split()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def rounded(value, places=2):
    return str(Decimal(str(value)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def pct(numerator, denominator):
    return rounded(Decimal(numerator) * 100 / Decimal(denominator), 1) + "%"


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
    check(len(actual) == len(expected), f"{name}: wrong row count")
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
    commits = {
        "Local": "16affd82bf9f668d5671e055aa3e76297dfe63dd",
        "Scarlet": "016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9",
    }
    for label, commit in commits.items():
        check(manifest["repositories"][label]["commit"] == commit, f"Source commit changed: {label}")
    check(len(manifest["files"]) == 41, "Expected 41 source files")
    paths = set()
    for item in manifest["files"]:
        path = ROOT / item["path"]
        check(path.is_file(), f"Missing source: {path}")
        content = path.read_bytes()
        check(len(content) == item["bytes"], f"Source size changed: {path}")
        check(hashlib.sha256(content).hexdigest() == item["sha256"], f"Source checksum changed: {path}")
        check(item["path"] not in paths, f"Duplicate manifest entry: {path}")
        paths.add(item["path"])
    for name in [
        "Project1_CPU_Simulator.html",
        "Project 1 Scenario_ CPU Instruction Execution - Image Brightness Processing.md",
        "How to Use Project 1 CPU Simulator - Quick Guide.md",
    ]:
        check((ROOT / "Sources/Local" / name).read_bytes() ==
              (ROOT / "Sources/Scarlet" / name).read_bytes(), f"Shared source differs: {name}")
    images = [item for item in manifest["files"] if item["path"].endswith(".png")]
    check(len(images) == len({item["sha256"] for item in images}) == 20, "Expected 20 distinct screenshots")
    print("Source integrity: 41 archived files and 20 distinct screenshots; shared instructions and simulator match.")


def verify_runs(runs, report, appendix):
    check([r["run"] for r in runs] == list(range(1, 9)), "Expected Runs 1–8 exactly once")
    simulator = (ROOT / "Sources/Local/Project1_CPU_Simulator.html").read_text()
    costs = {pc: int(cost) for pc, cost in re.findall(
        r"\{ addr: '(0x[0-9A-Fa-f]+)', code: '[^']*', cycles: (\d+) \}", simulator)}
    check(sum(costs[pc] for pc in DARK) == 13, "Dark instruction path changed")
    check(sum(costs[pc] for pc in BRIGHT) == 15, "Bright instruction path changed")
    check("cycles += 47" in simulator and "cycles += 15" in simulator, "Penalty model changed")
    logs = {source: read_log_runs(source) for source in ("Local", "Scarlet")}
    check(set(logs["Local"]) == {1, 2, 3, 4} and set(logs["Scarlet"]) == {5, 6, 7, 8}, "Unexpected source run IDs")
    appendices = {int(n): body for n, body in re.findall(
        r"^## Run (\d+): [^\n]+\n(.*?)(?=^## |\Z)", appendix, re.M | re.S)}
    check(set(appendices) == set(range(1, 9)), "Missing pixel appendix sections")
    provenance = Counter()
    instruction_count_rows = []
    for r in runs:
        n = r["run"]
        source = "Local" if n <= 4 else "Scarlet"
        check(r["source"] == source, f"Run {n}: wrong source")
        body = logs[source][n]
        case = metric(body, "Test Case")
        check(r["case"] == case and case in NAMES, f"Run {n}: case mismatch")
        expected_speed = int(re.search(r"^SPEED: (\d+) ms", body, re.M).group(1))
        check(r["speed_ms"] == expected_speed, f"Run {n}: speed mismatch")
        check(r["run_id"] == f"{PREFIXES[case]}-{expected_speed}-R{1 if n <= 4 else 2}", f"Run {n}: wrong run ID")
        grids = [rows for header, rows in tables(body) if header == [""] + list(map(str, range(1, 9)))]
        check(len(grids) == 2, f"Run {n}: expected input and output grids")
        cells = [[cell for row in grid for cell in row[1:]] for grid in grids]
        inputs = [int(re.match(r"\d+", cell).group()) for cell in cells[0]]
        outputs = [int(cell) for cell in cells[1]]
        check(len(inputs) == len(outputs) == 16, f"Run {n}: expected 16 pixels")
        check(r["inputs"] == inputs and r["outputs"] == outputs, f"Run {n}: data differs from log grids")
        check(outputs == [p+32 if p < 128 else p-8 for p in inputs], f"Run {n}: brightness-rule mismatch")
        basis = ["case definition" if case == "best" else "inferred from output" if "deduced" in cell else
                 "read from screenshot" for cell in cells[0]]
        check(r["input_provenance"] == basis, f"Run {n}: input provenance lost")
        provenance.update(basis)
        for field, label in {"cycles": "Total Cycles", "hits": "Cache Hits", "misses": "Cache Misses",
                             "correct": "Correct Predictions", "branches": "Total Branches", "stalls": "Stall Cycles"}.items():
            check(r[field] == int(metric(body, label)), f"Run {n}: {field} differs from log")
        check(metric(body, "Pixels Processed") == "16/16", f"Run {n}: incomplete run")
        check(metric(body, "Cycles Per Pixel") == rounded(Decimal(r["cycles"])/16), f"Run {n}: logged CPP")
        check(metric(body, "Hit Rate") == pct(r["hits"], 16), f"Run {n}: logged hit rate")
        check(metric(body, "Accuracy") == pct(r["correct"], 32), f"Run {n}: logged accuracy")
        image = metric(body, "Estimated Full Image (256×256)")
        check(int(image.split()[0].replace(",", "")) == r["cycles"]*4096, f"Run {n}: logged image estimate")
        check(r["hits"] + r["misses"] == 16 and r["branches"] == 32, f"Run {n}: event denominators")
        check(16 <= r["correct"] <= 32, f"Run {n}: impossible correct branch count")
        expected_images = [f"Sources/{source}/Screenshots/{PREFIXES[case]}{'-R2' if n > 4 else ''}-{i}.png"
                           for i in range(1, 4 if n > 4 else 3)]
        check(r["screenshots"] == expected_images, f"Run {n}: screenshot references")
        for image in expected_images:
            check((ROOT / image).is_file() and image in report, f"Run {n}: screenshot missing from package/report")
        registers = dict(next(rows for header, rows in tables(body) if header == ["Register", "Value"]))
        for reg, value in {"R0": 16, "R1": 1040, "R2": 128, "R3": inputs[-1], "R4": outputs[-1], "R5": 0, "R6": 32}.items():
            check(int(registers[reg], 16) == value, f"Run {n}: final {reg} mismatch")
        if n > 4:
            check(int(registers["R7"], 16) == 8, f"Run {n}: R7 mismatch")
        else:
            check(registers["R7"].startswith("Not visible"), f"Run {n}: R7 caveat missing")
        counts = Counter({"0x00": 1, "0x04": 1})
        cumulative, expected_rows = costs["0x00"] + costs["0x04"], []
        for i, (p, output, evidence) in enumerate(zip(inputs, outputs, basis), 1):
            path = DARK if p < 128 else BRIGHT
            cost = sum(costs[pc] for pc in path)
            counts.update(path)
            cumulative += cost
            evidence = {"case definition": "definition", "inferred from output": "inferred", "read from screenshot": "read"}[evidence]
            expected_rows.append(list(map(str, [i, p, evidence, output, "Dark" if p < 128 else "Bright", cost, cumulative])))
        actual_rows = next(rows for header, rows in tables(appendices[n]) if header[0] == "Pixel")
        check(actual_rows == expected_rows, f"Run {n}: pixel appendix mismatch")
        check(r["stalls"] == 47*r["misses"] + 15*(32-r["correct"]), f"Run {n}: stall reconciliation")
        check(r["cycles"] == cumulative + r["stalls"], f"Run {n}: total reconciliation")
        r["base"] = cumulative
        r["dark"] = sum(p < 128 for p in inputs)
        r["bright"] = 16-r["dark"]
        instruction_count_rows.append(sum(counts.values()))
        print(f"Run {n}: {r['cycles']} cycles, {sum(counts.values())} instructions; pixels, evidence labels, metrics and final registers agree.")
    check(instruction_count_rows == [146, 154, 151, 154]*2, "Instruction count table mismatch")
    equal_rows(report, "instruction-counts", [
        ["Each setup instruction: 0x00, 0x04", 1, 1, 1, 1],
        ["Each of 0x08, 0x0C, 0x10", 16, 16, 16, 16],
        ["Each of 0x14, 0x18"] + [r["bright"] for r in runs[:4]],
        ["0x1C"] + [r["dark"] for r in runs[:4]],
        ["Each of 0x20, 0x24, 0x28, 0x2C, 0x30", 16, 16, 16, 16],
        ["Total executed instructions"] + instruction_count_rows[:4],
        ["Base cycles before delays"] + [r["base"] for r in runs[:4]],
    ])
    check(provenance == {"case definition": 32, "read from screenshot": 93, "inferred from output": 3}, "Input provenance counts")
    check(sum(r["cycles"] for r in runs) == 3515 and sum(r["base"] for r in runs) == 1764, "Aggregate cycle accounting")


def verify_report_tables(runs, report):
    equal_rows(report, "results", [[r["run"], NAMES[r["case"]], r["cycles"], rounded(Decimal(r["cycles"])/16),
        r["hits"], r["misses"], r["correct"], r["branches"], r["stalls"]] for r in runs])
    equal_rows(report, "rates", [[r["run"], pct(r["hits"], 16), pct(r["misses"], 16), pct(r["correct"], 32),
        pct(32-r["correct"], 32), pct(r["correct"]-16, 16)] for r in runs])
    equal_rows(report, "reconciliation", [[r["run"], r["dark"], r["bright"], r["base"],
        47*r["misses"], 15*(32-r["correct"]), r["cycles"]] for r in runs])

    def estimate(total, original):
        return f"{total} ({pct(Decimal(original)-Decimal(total), original)})"

    equal_rows(report, "optimizations", [[r["run"], r["cycles"]] +
        [estimate(t, r["cycles"]) for t in [r["cycles"]-47*r["misses"], r["cycles"]-47*(r["misses"]-1),
         226+47*r["misses"], r["cycles"]-36]] for r in runs])
    equal_rows(report, "image-runs", [[r["run"], r["cycles"], f"{r['cycles']*4096:,}"] for r in runs])
    means, optimizations, scaling, savings = [], [], [], []
    for case in NAMES:
        pair = [r for r in runs if r["case"] == case]
        check(len(pair) == 2, f"Expected two runs for {case}")
        a, b = pair
        mean = Decimal(a["cycles"]+b["cycles"])/2
        means.append([NAMES[case], a["cycles"], b["cycles"], f"{b['cycles']-a['cycles']:+d}", rounded(mean, 1),
                      rounded(mean/16), pct(a["hits"]+b["hits"], 32), pct(a["correct"]+b["correct"], 64)])
        m = Decimal(a["misses"]+b["misses"])/2
        optimizations.append([NAMES[case], rounded(mean, 1)] +
            [estimate(rounded(t, 1), mean) for t in [mean-(m-1)*47, 226+m*47, mean-36]])
        image = int(mean*4096)
        daily = image*2000000
        seconds = Decimal(daily)/2400000000
        servers = (daily + 2400000000*14400 - 1)//(2400000000*14400)
        scaling.append([NAMES[case], f"{image:,}", f"{daily:,}", f"{seconds:,.2f}", rounded(seconds/14400, 4), servers])
        saved = seconds*Decimal("0.2")
        dollars = saved/3600*Decimal("0.008")*Decimal("0.12")*365
        savings.append([NAMES[case], rounded(saved), "$"+rounded(dollars, 6), "$0"])
    equal_rows(report, "averages", means)
    equal_rows(report, "optimization-means", optimizations)
    equal_rows(report, "scaling", scaling)
    equal_rows(report, "annual-savings", savings)
    # Independently calculate the key worked-example values in prose.
    real1_mean = sum(Decimal(r["cycles"]) for r in runs if r["case"] == "real1")/2
    real1_daily = real1_mean*4096*2000000
    real1_seconds = real1_daily/2400000000
    active_energy = real1_seconds/3600*Decimal("0.008")
    active_cost = active_energy*Decimal("0.12")
    one_cpp_cycles = Decimal(65536)*2000000
    one_cpp_seconds = one_cpp_cycles/2400000000
    one_cpp_cost = one_cpp_seconds/3600*Decimal("0.008")*Decimal("0.12")
    total_stalls = sum(r["stalls"] for r in runs)
    cache_stalls = sum(r["misses"]*47 for r in runs)
    values = [f"{sum(r['cycles'] for r in runs):,}", f"{sum(r['base'] for r in runs):,}",
              f"{cache_stalls:,}", str(total_stalls-cache_stalls), f"{total_stalls:,}", pct(cache_stalls, total_stalls),
              "$"+rounded(Decimal("0.008")*24*Decimal("0.12")*365, 4), rounded(active_energy, 8),
              "$"+rounded(active_cost, 8), "$"+rounded(active_cost*365, 5), f"{int(real1_daily*Decimal('0.8')):,}",
              f"{real1_seconds*Decimal('0.8'):,.6f}", rounded(real1_seconds*Decimal("0.2"), 6),
              f"{int(one_cpp_cycles):,}", rounded(one_cpp_seconds, 6), "$"+rounded(one_cpp_cost, 11),
              rounded(one_cpp_seconds/2, 6), "$"+rounded(one_cpp_cost/2, 11), rounded(real1_seconds/2, 6),
              rounded(Decimal(226-36+47)/16, 4)]
    for text in values:
        check(text in report, f"Worked-example value missing: {text}")
    check(rounded(Decimal(131072000000)/2400000000/3600*Decimal("0.008")*Decimal("0.12"), 11)
          == "0.00001456356", "One-CPP cost formula")
    check("No measured optimized runs exist" in report, "Missing optimization evidence limitation")
    print("Report calculations: 10 numeric tables, scaling, optimization assumptions and worked examples checked.")


def verify_template():
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(ROOT / "Sources/Scarlet/Step_Trace_Worst_Case.xlsx") as book:
        sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
        cells = {cell.attrib["r"]: cell for cell in sheet.findall(".//m:c", ns)}
        observation_cells = [f"{col}{row}" for col in "FG" for row in range(12, 28)] + [f"J{row}" for row in range(11, 28)]
        for address in observation_cells:
            cell = cells.get(address)
            if cell is not None:
                check(not "".join(cell.itertext()).strip(), f"Trace template has an observation: {address}")
    print("Trace workbook: all 49 observation cells are blank; no measured trace counted.")


def verify_grading():
    text = (ROOT / "Grading.md").read_text()
    sums = []
    for name, maximum, awarded in [("trace", 30, 18), ("performance", 25, 25), ("optimization", 25, 11), ("cost", 20, 20)]:
        rows = table_named(text, "grade-"+name)
        for row in rows:
            check(0 <= int(row[2]) <= int(row[1]), f"Invalid mark: {row[0]}")
        check(sum(int(row[1]) for row in rows) == maximum, f"{name}: max sum")
        check(sum(int(row[2]) for row in rows) == awarded, f"{name}: awarded sum")
        sums.append((maximum, awarded))
    expected = [[label, maximum, awarded, maximum-awarded] for label, (maximum, awarded) in zip(
        ["Instruction trace", "Performance data", "Optimization analysis", "Extrapolation and cost"], sums)]
    expected.append(["Total", 100, 74, 26])
    equal_rows(text, "grade-total", expected)
    check("not an official instructor grade" in text, "Missing self-assessment qualification")
    print("Grading arithmetic: 18 + 25 + 11 + 20 = 74/100; 26 points deducted under the proposed rubric.")


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
    data = json.loads((ROOT / "data.json").read_text())
    runs = data["runs"]
    report = (ROOT / "Final_Report.md").read_text(encoding="utf-8")
    appendix = (ROOT / "Appendix_Pixel_Paths.md").read_text(encoding="utf-8")
    verify_runs(runs, report, appendix)
    verify_report_tables(runs, report)
    verify_template()
    verify_grading()
    verify_links()
    print("PASS: eight-run package is internally consistent. Trace and measured-optimization gaps remain explicitly identified.")


if __name__ == "__main__":
    main()
