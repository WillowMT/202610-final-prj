# Report Maker: how to rebuild this report

This file explains how the reports in this folder were produced and how to replicate the process for new runs. Follow the steps in order.

## What you need

- `Project1_CPU_Simulator.html` — the simulator (open it in a browser).
- `Project 1 Scenario_ CPU Instruction Execution - Image Brightness Processing.md` — the assignment requirements ("What You'll Deliver" lists what the report must cover).
- `How to Use Project 1 CPU Simulator - Quick Guide.md` — the six "Next Steps" questions and the workflow.
- `verify_logs_report_gaps.py` — the verification script (needs Python 3 only, no extra packages).

## Step 1: Record runs in the simulator

1. Open `Project1_CPU_Simulator.html` in a browser.
2. For each test case (Best, Worst, Real Case 1, Real Case 2): select it, click START SIMULATION, then click RUN ALL.
3. Wait for "Complete! All 16 pixels processed."
4. Keep the speed at 50 ms per step. This is the documented convention; the speed slider only controls the animation and never the cycle counts.

## Step 2: Screenshot each run (2 per run)

- **Top screen:** status bar, controls panel, quick metrics, summary statistics, and the visible registers.
- **Bottom screen:** instruction sequence, pixel data (input and output grids), execution summary, and the full detailed metrics block. Scroll so the metrics are not cut off.
- **Naming:** save as `Screenshots/<case>-1.png` and `Screenshots/<case>-2.png`, where `<case>` is `BC`, `WC`, `RC1`, or `RC2`.
- If you record the same case again, keep the old screenshots as evidence and give the new run a new run ID (for example `BC-50-R2`). Do not overwrite old files.

## Step 3: Write Logs.md

- Add one section per run using the heading format `## Run N: <title>` (the verification script and the report links depend on this exact format).
- Transcribe values exactly from the panels. Do not guess. Keep the panel labels (status, test case, quick metrics, summary statistics, registers, execution summary, detailed metrics).
- Copy the pixel grids as two markdown tables per run: input first, output second, each with the header `|  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |` and two rows of eight values.
- Label anything that cannot be read directly:
  - unreadable cell → use the test case definition and say so (for example, Best Case inputs are 0 by definition),
  - value worked out from another value → mark it `(deduced)`,
  - clipped row → write "Not visible (cut off...)".
- Keep a "Transcription notes" section at the end for these caveats.

## Step 4: Fill the data files

- `data-collection-template.md`: add one detailed run row per run and keep the summary table in sync with them.
- `Data Collection Sheet.xlsx`: one sheet per test case plus the Summary sheet. Summary cells use formulas, and the three charts read from the Summary sheet. When you add runs, extend the row ranges in the formulas and charts.

## Step 5: Write the reports

### Analysis Report.md (main report)

Cover the four requirements from the scenario:

1. **Instruction trace:** program costs table (PC, instruction, cost), the dark/bright path for one pixel, and the instruction counts per run. Add a `### B.N <title>` trace section per run in the same order as Logs.md, with one row per pixel: pixel number, input, output, path, cycles for the pixel, running instruction total.
2. **Performance data:** total cycles, cycles per pixel (CPP), cache miss rate, branch misprediction rate, and the register spill situation.
3. **Optimization analysis:** at least three methods. Measured results when you have them; otherwise calculations clearly labelled as estimates. Never present a calculation as a recorded result.
4. **Extrapolation and cost impact:** use the stated assumptions (256×256 image = 65,536 pixels, 2M images/day, 2.4 GHz, 8 W, $0.12/kWh, 4-hour deadline).

### Next Steps Analysis.md

Answer the six questions from the quick guide, using values from Logs.md and the data files.

### Writing rules

- Every number must trace back to Logs.md or the simulator code.
- Label recorded results and estimates differently.
- Single runs are examples, not averages, because cache and branch outcomes are random.

## Step 6: Verify before submitting

Run the verification script from this folder:

```bash
python3 verify_logs_report_gaps.py
```

Expected output for the current four runs: one "Run N: checked..." line per run, then "All four logs reconcile...". The script checks:

- every metric, percentage, and comparison value in the reports against Logs.md,
- all 64 output pixels against the brightness rule (below 128: +32; otherwise: -8),
- instruction execution counts and the cycle reconciliation per run,
- table layouts and all local links and anchors.

If the script fails, fix the data or the report it names. Do not weaken the script to hide a mismatch.

Also do the manual checks: re-open the screenshots next to Logs.md, and confirm the totals with:

```text
Total cycles = instruction cycles + (47 × cache misses) + (15 × incorrect predictions)
```

## Formulas used

```text
Instruction cycles = 2 setup cycles + 13 × dark pixels + 15 × bright pixels
Instruction counts per PC come from the pixel paths in Logs.md
Estimated image cycles = 16-pixel total × 4,096 (= CPP × 65,536)
```

## Conventions

- Run IDs: `<case>-<speed>-R<number>`, for example `BC-50-R1`.
- Detailed metrics show CPP to two decimals; the quick metric shows one decimal. Keep both as recorded.
- The comparison table cells use the format `<cycles> (<pct>%)`.

## When the project moves to the next stage

The verification script is written for the current stage: exactly four runs, the RC2 pixels 9 and 12 marked `(inferred)`, and four statements about missing work near the end of the file. When you add the fifth experiment, the step-by-step traces, or measured optimization results:

1. Add the new log section (`## Run 5: ...`) and its report trace (`### B.5 ...`), keeping the two in the same order.
2. Extend the tables in the reports; the script compares column by column.
3. Update the script where it is stage-specific: the `== 4` run-count check, the RC2 `(inferred)` rule, and the final four "missing work" assertions. The numeric checks keep working as long as the table headings and labels stay the same.

See `Readme.md` for the current status of what is done and what is still needed.
