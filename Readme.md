# Project 1 README: CPU Instruction Execution Simulator

This folder contains the BSC104 Project 1 work: analyzing how a CPU executes an image brightness algorithm, using the HTML simulator in this folder. The status below summarizes what is finished and what remains.

> **Update (29 September 2026):** The combined deliverable is now [Final_Report_V1/](Final_Report_V1/README.md). It merges this folder's Runs 1–4 with Runs 5–8 from the group repository, adds four full step traces (Runs 9–12, recorded from the simulator) and a measured optimization study (four program variants, 40 runs per case each). The sections below describe this folder's original four-run stage and are kept as the historical record: item 1 of "What still needs to be done" was satisfied by the imported Runs 5–8, and items 2 and 3 are completed in the combined report.

## What has been done

### Recorded experiments (4 runs)

Four complete runs, one per test case. Each run processed all 16 pixels at 50 ms per step and has its own screenshots and metrics.

| Test case | Screenshots (in `Screenshots/`) | Total cycles | Cycles/pixel | Cache hits/misses | Branch accuracy |
|---|---|---|---|---|---|
| Best: all 0 | BC-1, BC-2 | 351 | 21.94 | 13 / 3 | 32 / 32 (100.0%) |
| Worst: alternating | WC-1, WC-2 | 502 | 31.38 | 13 / 3 | 23 / 32 (71.9%) |
| Real Case 1: 70% dark | RC1-1, RC1-2 | 406 | 25.38 | 13 / 3 | 29 / 32 (90.6%) |
| Real Case 2: clustered | RC2-1, RC2-2 | 444 | 27.75 | 12 / 4 | 30 / 32 (93.8%) |

### Files produced

| File | Purpose |
|---|---|
| `Analysis Report.md` | Main report: instruction trace evidence, performance data, optimization analysis, extrapolation and cost impact |
| `Next Steps Analysis.md` | Answers the six "Next Steps" questions in the quick guide |
| `Logs.md` | Text transcription of all eight screenshots, grouped by run, with unreadable values clearly labelled |
| `data-collection-template.md` | Summary table and detailed run rows |
| `Data Collection Sheet.xlsx` | Excel workbook: formula-driven summary per test case and three charts with data labels |
| `Report_Maker.md` | Instructions for rebuilding and verifying this report |
| `verify_logs_report_gaps.py` | Script that automatically checks the logs, reports, and links (run with Python 3) |
| `Screenshots/` | The evidence: two screenshots per run (top screen and bottom screen) |
| `Project1_CPU_Simulator.html` | The simulator used for all runs |

### Checks already completed

- All 64 recorded output pixels follow the brightness rule (below 128: add 32; otherwise: subtract 8).
- Every run's total reconciles exactly: instruction cycles + (47 × cache misses) + (15 × incorrect branch predictions).
- The reports were audited for correct calculations, and all values in `Logs.md` were re-checked against the eight screenshots.
- `verify_logs_report_gaps.py` re-checks all of the above automatically; `Report_Maker.md` explains how to rebuild the report.

## What still needs to be done

1. **Record a fifth complete experiment.** The assignment asks for 5+ experiments; only four runs exist so far.
2. **Save instruction-by-instruction traces.** Use STEP FORWARD and record, for each step: the executed instruction (PC), register changes (R0–R4), cache hit or miss, branch correct or incorrect, and the running cycle count. The saved screenshots show only the final state, so the order of delays during a run is still missing.
3. **Test and measure at least three optimizations.** Suggested: cache prefetching, branch-free code, and loop unrolling. For a fair test, each version must process the same pixel lists (saved in `Logs.md`), produce the same outputs, and be repeated several times because cache and branch outcomes are random.
4. **Optional evidence cleanups.**
   - Capture the register panel without the R7 row being cut off.
   - Capture the event log during a run (it is not visible in any screenshot).
   - Confirm the two Real Case 2 input values that were deduced (pixels 9 and 12 = 6, inferred from their output of 38).

## Known limitations

- The simulator's cache and branch outcomes are random, and each test case was run only once. The results are examples, not averages.
- Best Case input pixels are black and unreadable; their value (0) comes from the test case definition.
- Two Real Case 2 input values are deduced rather than read directly, as noted above.
- The R7 register value is cut off in the top screenshots; the simulator code defines it as 8.

## How to run the simulator

1. Open `Project1_CPU_Simulator.html` in a browser.
2. Choose a test case from the dropdown, then click START SIMULATION.
3. Use RUN ALL for quick results, or STEP FORWARD to watch one instruction at a time.
4. STEP FORWARD is also how the missing step-by-step traces can be collected.
