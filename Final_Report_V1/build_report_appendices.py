"""Render the report's self-contained evidence appendices from recorded data.

The default mode checks the generated section without writing. --write rebuilds
only the marked evidence section of Final_Report.md, leaving its authored text
and original evidence untouched. Python standard library only.
"""
import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
import math
from pathlib import Path
import re
import statistics


ROOT = Path(__file__).resolve().parent
START = "<!-- generated-evidence:start -->"
END = "<!-- generated-evidence:end -->"
CASES = {"best": "Best Case", "worst": "Worst Case", "real1": "Real Case 1", "real2": "Real Case 2"}
PREFIXES = {"best": "BC", "worst": "WC", "real1": "RC1", "real2": "RC2"}
PROGRAMS = {"baseline": "Baseline", "branchfree": "Branch-free", "unrolled": "Unrolled",
            "looptest": "Loop-test", "combined": "Combined"}
CHECKPOINTS = ["After setup", "First load", "First branch", "Pixel 1 complete", "Pixel 8 complete", "Final state"]
BASE = {"0x00": 1, "0x04": 1, "0x08": 3, "0x0C": 1, "0x10": 1, "0x14": 1,
        "0x18": 2, "0x1C": 1, "0x20": 3, "0x24": 1, "0x28": 1, "0x2C": 1, "0x30": 1}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def rounded(value):
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def table(header, rows, marker):
    lines = [f"<!-- table:{marker} -->", "| " + " | ".join(header) + " |",
             "|" + "|".join("---" for _ in header) + "|"]
    for row in rows:
        require(len(row) == len(header), f"Wrong number of cells: {marker}")
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_appendices():
    runs = read_json("data.json")["runs"]
    require([r["run"] for r in runs] == list(range(1, 13)), "Expected Runs 1–12")
    lines = ["## Appendix A: Screenshot gallery",
             "The following 49 figures embed the full-resolution captures: 20 final-state screenshots for "
             "Runs 1–8, 24 checkpoints for Runs 9–12, and five optimization samples. Images are displayed "
             "individually at document width. Figures 1–20 in the main discussion give "
             "larger views of selected panels. Dark pixel cells and clipped register entries retain the "
             "original capture's limitations; the numeric pixel records are printed in Appendices B and C."]
    figure = 0
    for index, run in enumerate(runs):
        n = run["run"]
        if index == 0:
            lines.append("### A.1 Original final-state evidence: Runs 1–8")
        elif index == 8:
            lines.extend(["### A.2 Complete checkpoint sequences: Runs 9–12",
                          "Each six-image sequence belongs to one experiment. The setup capture follows the "
                          "two initialization instructions; the next PC is 0x08. The corresponding full "
                          "instruction sequences are in Appendix C."])
        lines.append(f"#### Run {n}: {CASES[run['case']]}, {run['run_id']}")
        labels = CHECKPOINTS if n >= 9 else [f"Final-state capture {i + 1}" for i in range(len(run["screenshots"]))]
        for source, label in zip(run["screenshots"], labels):
            require((ROOT / source).is_file(), f"Missing screenshot: {source}")
            figure += 1
            caption = f"Figure A{figure}: Run {n}, {label.lower()}"
            lines.extend([f"![{caption}.]({source})", f"**{caption}.** {run['run_id']}."])
    require(figure == 44, "Expected 44 run screenshots")
    lines.extend(["### A.3 Optimization sample screenshots",
                  "These five images show individual executions from the optimization study, separate from "
                  "Runs 1–12. Their displayed values are not the 40-run means. Appendix D contains the "
                  "measurements used to calculate those means."])
    for key, label in PROGRAMS.items():
        source = f"Optimizations/{key}_final_state.png"
        require((ROOT / source).is_file(), f"Missing screenshot: {source}")
        figure += 1
        caption = f"Figure A{figure}: {label} sample final state"
        lines.extend([f"![{caption}.]({source})", f"**{caption}.** One individual execution; the averages are in Appendix D."])

    lines.extend(["## Appendix B: Reconstructed pixel paths for Runs 1–8",
                  "These tables contain all 128 input/output pairs for Runs 1–8. They reconstruct the "
                  "instruction paths from the pixel values; they are not recorded timing histories. "
                  "Running base totals include the two setup cycles and exclude all random delays.",
                  "**Input basis:** read = transcribed from a readable screenshot; definition = zero input "
                  "specified by Best Case; inferred = obtained from the output using the brightness rule. "
                  "An inferred input cannot independently verify the same output.",
                  "**Paths:** Dark = 08 → 0C → 10 → 1C → 20 → 24 → 28 → 2C → 30 (13 cycles); "
                  "Bright = 08 → 0C → 10 → 14 → 18 → 20 → 24 → 28 → 2C → 30 (15 cycles). Addresses "
                  "are hexadecimal. Both return to 08 after pixels 1–15 and finish at 34 after pixel 16. "
                  "For pixel n, the load address is 1023 + n; after the iteration R0 = n, R1 = 1024 + n, "
                  "R3 contains the input, and R4 contains the output."])
    basis_names = {"read from screenshot": "read", "case definition": "definition", "inferred from output": "inferred"}
    for run in runs[:8]:
        n = run["run"]
        lines.append(f"### B.{n} Run {n}: {run['run_id']}")
        rows, running = [], 2
        for i, (value, output, basis) in enumerate(zip(run["inputs"], run["outputs"], run["input_provenance"]), 1):
            cost = 13 if value < 128 else 15
            running += cost
            rows.append([i, value, basis_names[basis], output, "Dark" if value < 128 else "Bright", cost, running])
        lines.append(table(["Pixel", "Input", "Basis", "Output", "Path", "Base cycles", "Running base"], rows, f"pixel-paths-{n}"))
        wrong = run["branches"] - run["correct"]
        require(running + 47 * run["misses"] + 15 * wrong == run["cycles"], f"Run {n}: total mismatch")
        lines.append(f"Reconciliation: `{running} + {run['misses']} × 47 + {wrong} × 15 = {run['cycles']} cycles`. "
                     + ("Cache-miss positions were not saved. No brightness prediction was wrong." if wrong == 0 else
                        "Cache-miss and wrong-prediction positions were not saved."))

    lines.extend(["## Appendix C: Complete recorded instruction traces for Runs 9–12",
                  "This appendix prints all 605 executed instruction steps and all 64 pixel iterations "
                  "from the four traced runs. These are observed simulator records. Best Case inputs "
                  "use the all-zero case definition; the other inputs were read from the recorded state.",
                  "**How to read the tables:** the pixel table gives input, output, the load's cache outcome, "
                  "the brightness branch's prediction outcome, base cycles, delay cycles and the running total "
                  "after the loop check. Instruction tables give the executed PC and next PC, cycles added, "
                  "running total and event. Addresses are hexadecimal; Section 1.3 maps every PC to its "
                  "instruction. A step with running total T and increment d occupies counted cycles "
                  "T − d + 1 through T. A dash means no cache or prediction event at that instruction. "
                  "BNE is always counted as correctly predicted, including its final not-taken decision. "
                  "HALT is the final next-PC position and is not charged a step or cycle."])
    steps_count = 0
    for index, run in enumerate(runs[8:], 1):
        n = run["run"]
        raw = read_json(f"Traces/Run{n}_{PREFIXES[run['case']]}_trace.json")
        require(raw["input"] == run["inputs"], f"Run {n}: inputs differ")
        steps = raw["steps"]
        pixels, step_rows, total = [], [], 0
        for i, step in enumerate(steps, 1):
            pc = step["pc"]
            miss = "Cache MISS" in step["summary"]
            wrong = "Branch MISPREDICT" in step["summary"]
            require(step["cyclesAdded"] == BASE[pc] + 47 * miss + 15 * wrong, f"Run {n}, step {i}: cycles")
            total += step["cyclesAdded"]
            require(step["runningCycles"] == total, f"Run {n}, step {i}: running total")
            event = "-"
            if pc == "0x08":
                pixels.append({"input": step["r3"], "cache": "MISS" if miss else "HIT", "base": 0, "delay": 0})
                event = "Cache miss" if miss else "Cache hit"
            if pc not in ("0x00", "0x04"):
                pixels[-1]["base"] += BASE[pc]
                pixels[-1]["delay"] += 47 * miss + 15 * wrong
            if pc == "0x10":
                pixels[-1]["branch"] = "Wrong" if wrong else "Correct"
                event = "BLT wrong" if wrong else "BLT correct"
            elif pc == "0x20":
                pixels[-1]["output"] = step["r4"]
            elif pc == "0x30":
                pixels[-1]["running"] = total
                event = "BNE correct"
            step_rows.append([i, pc, step["nextPC"], step["cyclesAdded"], total, event])
        require(total == run["cycles"] and len(pixels) == 16, f"Run {n}: trace total")
        require([p["output"] for p in pixels] == run["outputs"], f"Run {n}: outputs differ")
        steps_count += len(steps)
        lines.extend([f"### C.{index} Run {n}: {run['run_id']}",
                      f"**{CASES[run['case']]}:** {len(steps)} steps, {total} cycles, {run['hits']} cache hits, "
                      f"{run['misses']} misses, {run['correct']}/{run['branches']} correct branches, "
                      f"and {run['stalls']} stall cycles. Checkpoint images appear in Appendix A.2.",
                      table(["Pixel", "Input", "Output", "Cache", "BLT", "Base", "Delay", "Running"],
                            [[i, p['input'], p['output'], p['cache'], p['branch'], p['base'], p['delay'], p['running']]
                             for i, p in enumerate(pixels, 1)], f"trace-pixels-{n}")])
        # Shorter tables keep the same columns and step numbers across page breaks.
        for start in range(0, len(step_rows), 40):
            end = min(start + 40, len(step_rows))
            lines.extend([f"#### Run {n}: recorded steps {start + 1}–{end}",
                          table(["Step", "Executed PC", "Next PC", "Cycles added", "Running total", "Event"],
                                step_rows[start:end], f"trace-steps-{n}-{start + 1}")])
    require(steps_count == 605, f"Expected 605 instruction steps, found {steps_count}")

    measured = {program: read_json(f"Optimizations/measure_{program}.json") for program in PROGRAMS}
    lines.extend(["## Appendix D: Individual optimization measurements",
                  "These tables contain all 800 recorded optimization executions: 40 repetitions for each "
                  "of five programs on each of four cases. Each cell is **cycles / cache misses / wrong "
                  "brightness predictions**. The repeat number identifies an execution within that program "
                  "and case; corresponding rows across programs do not share random draws. All 16 output "
                  "pixels passed the brightness-rule check in every execution.",
                  "Use the base cycles and branch counts in Section 3.1 to check each result: "
                  "`cycles = base + 47 × misses + 15 × wrong`. Cache hits equal 16 minus misses. "
                  "Correct branch predictions equal the program's conditional-branch count minus wrong. "
                  "Stall cycles equal 47 × misses + 15 × wrong. Thus the displayed triplets and program "
                  "definitions also determine the remaining final counters."])
    summary_rows, executions = [], 0
    for index, (case, label) in enumerate(CASES.items(), 1):
        lines.append(f"### D.{index} {label}: 40 repetitions per program")
        rows = []
        for i in range(40):
            row = [i + 1]
            for program in PROGRAMS:
                records = measured[program][case]
                require(len(records) == 40, f"Expected 40 runs: {program}/{case}")
                r = records[i]
                wrong = r["branches"] - r["correct"]
                require(r["ok"] is True and r["wrong"] == wrong, f"Invalid output/branch check: {program}/{case}")
                row.append(f"{r['cycles']} / {r['misses']} / {wrong}")
                executions += 1
            rows.append(row)
        lines.append(table(["Repeat"] + list(PROGRAMS.values()), rows, f"measure-records-{case}"))
        for program, name in PROGRAMS.items():
            records = measured[program][case]
            cycles = [r["cycles"] for r in records]
            summary_rows.append([label, name, sum(cycles), rounded(Decimal(sum(cycles)) / 40),
                                 rounded(statistics.stdev(cycles) / math.sqrt(40)),
                                 sum(r["misses"] for r in records), sum(r["wrong"] for r in records)])
    require(executions == 800, f"Expected 800 measurements, found {executions}")
    lines.extend(["### D.5 Totals and statistical calculations",
                  "Each row summarizes 40 observations. Mean cycles = sum of cycles / 40; mean misses "
                  "and mean wrong predictions are their totals divided by 40. Sample standard deviation "
                  "is `sqrt(sum((x − mean)^2) / 39)` and the standard error (SE) is that value divided "
                  "by `sqrt(40)`. For two independent means, the SE of their difference is "
                  "`sqrt(SE_1^2 + SE_2^2)`. Section 3.4's margins in standard errors divide the difference "
                  "between the means by this combined SE. Displayed means and SEs below are rounded to "
                  "two decimal places; the individual observations above permit recalculation at full precision.",
                  table(["Case", "Program", "Sum cycles", "Mean cycles", "SE cycles", "Total misses", "Total wrong"],
                        summary_rows, "measure-summary-totals")])
    return "\n\n".join(lines) + "\n"


def verify_self_contained(report):
    image_pattern = r"!\[[^\]]*\]\(([^)]+)\)"
    images = re.findall(image_pattern, report)
    require(len(images) == 69, f"Expected 20 figures and 49 screenshots, found {len(images)} images")
    for source in images:
        require((ROOT / source).is_file(), f"Missing embedded image: {source}")
    text = re.sub(image_pattern, "", report)
    require(not re.search(r"\[[^\]]*\]\((?!#)[^)]+\)", text), "Report links to another document or image")
    require(not re.search(r"\b[\w/.-]+\.(?:md|json|xlsx|py|js|html)\b", text), "Report prose names a repository file")
    require("click" not in text.lower() and "linked above" not in text.lower(), "Report relies on clickable evidence")
    require(report.count(START) == report.count(END) == 1, "Missing or duplicate evidence boundaries")
    actual = report.split(START, 1)[1].split(END, 1)[0]
    require(actual == "\n\n" + render_appendices() + "\n", "Embedded appendices differ from recorded evidence; rebuild them")
    print("Standalone report: 69 embedded images, 128 reconstructed pixel rows, 64 recorded pixel rows, "
          "605 instruction steps and 800 optimization records verified; no external-file reading references.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the marked report evidence section")
    args = parser.parse_args()
    path = ROOT / "Final_Report.md"
    report = path.read_text(encoding="utf-8")
    require(report.count(START) == report.count(END) == 1, "Missing or duplicate evidence boundaries")
    if args.write:
        before, rest = report.split(START, 1)
        _, after = rest.split(END, 1)
        report = before + START + "\n\n" + render_appendices() + "\n" + END + after
        verify_self_contained(report)
        path.write_text(report, encoding="utf-8")
    else:
        verify_self_contained(report)


if __name__ == "__main__":
    main()
