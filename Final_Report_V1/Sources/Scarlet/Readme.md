# Project 1 README: CPU Instruction Execution Simulator (Runs 5–8)

This folder contains my BSC104 Project 1 work: four new runs of the CPU simulator, one per test case, with the same report structure as the group's Runs 1–4 so the two can be merged.

## What has been done

### Recorded experiments (4 runs)

Four complete runs, one per test case. Each processed all 16 pixels at 500 ms per step and has three screenshots.

| Run | Test case | Screenshots (in `Screenshots/`) | Total cycles | Cycles/pixel | Cache hits/misses | Branch accuracy |
|---|---|---|---|---|---|---|
| 5 | Best: all 0 | BC-R2-1, 2, 3 | 413 | 25.81 | 12 / 4 | 31 / 32 (96.9%) |
| 6 | Worst: alternating | WC-R2-1, 2, 3 | 504 | 31.50 | 12 / 4 | 26 / 32 (81.3%) |
| 7 | Real Case 1: 70% dark | RC1-R2-1, 2, 3 | 436 | 27.25 | 13 / 3 | 27 / 32 (84.4%) |
| 8 | Real Case 2: clustered | RC2-R2-1, 2, 3 | 459 | 28.69 | 12 / 4 | 29 / 32 (90.6%) |

Together with Runs 1–4, the group now has **eight complete experiments**, which covers the assignment's "5+ experiments" requirement, and two runs per test case for comparing random variation.

### Files

| File | Purpose |
|---|---|
| `Analysis Report.md` | Main report: instruction trace, performance data, comparison with Runs 1–4, optimization analysis, scaling and cost |
| `Next Steps Analysis.md` | Answers the six "Next Steps" questions in the quick guide |
| `Logs.md` | Text transcription of all twelve screenshots, grouped by run |
| `data-collection-template.md` | Summary table, detailed run rows, and combined averages |
| `Data Collection Sheet.xlsx` | Excel workbook with formula-driven summary and a chart |
| `Screenshots/` | Evidence: three screenshots per run (top, registers, pixels/metrics) |
| `Step_Trace_Worst_Case.xlsx` | Fill-in sheet for the step-by-step trace (still to do) |
| `Project1_CPU_Simulator.html` | The simulator used for all runs |

### Checks completed

- All 64 output pixels follow the brightness rule (below 128: +32; otherwise: −8).
- Every run's total reconciles exactly: instruction cycles + (47 × cache misses) + (15 × incorrect predictions).
- Every figure in the reports was recalculated from the values in `Logs.md`.

## What still needs to be done

1. **Step-by-step trace.** Use STEP FORWARD on one test case and record, for each pixel, the cache result at `0x08`, the branch result at `0x10` and the running Total Cycles after `0x30`. A fill-in sheet for this (`Step_Trace_Worst_Case.xlsx`) has been prepared.
2. **Measured optimizations.** The simulator cannot run changed programs, so the three optimizations are calculated estimates. Confirm with the teacher whether estimates are acceptable.

## Known limitations

- Cache and branch outcomes are random, and each case was run once in this set. The comparison with Runs 1–4 shows totals can differ by 2 to 62 cycles between runs.
- Best Case input pixels are black and unreadable; their value (0) comes from the test case definition.
- One Real Case 2 input (pixel 15) is deduced from its output (40 − 32 = 8).
- These runs used 500 ms per step and Runs 1–4 used 50 ms. The speed only affects the animation, not the results.
