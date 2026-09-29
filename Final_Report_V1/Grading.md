# Grading assessment: Final Report V1

## Result

**Provisional self-assessment: 100/100** under the proposed rubric below, up from 74/100 in the first draft. The two evidence gaps that previously cost 26 points — instruction-level event histories and measured optimization results — are now closed by Runs 9–12 (step traces) and the 800 measured variant runs in Section 3.

This is an evidence-based assessment of [Final_Report.md](Final_Report.md) and its included appendix, traces and optimization records. It is **not an official instructor grade**. Neither repository supplies a numerical marking rubric or letter-grade scale. The weights below are an explicitly proposed allocation of 100 points across the four deliverable groups in the [assignment scenario](Sources/Local/Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md), under "What You'll Deliver." The instructor may use different weights or mandatory-completion rules, and the caveats listed at the end remain on the record.

## Marking method

- Award full credit where the requested information is present and supported.
- For observations, require a genuine record (screenshot, step log, measured run), not an estimate or a plan.
- Treat the reported performance targets as quantities to analyze, not guaranteed results. Poor simulator performance alone does not reduce the reporting mark.
- Where the assignment asks for estimates (cost, scaling), stated assumptions are appropriate.
- Keep simulator limitations documented rather than scored as failures.

The four proposed weights are instruction trace **30**, performance data **25**, optimization analysis **25**, and extrapolation/cost **20**.

## Criterion-by-criterion marks

### 1. Instruction trace: 30/30

<!-- table:grade-trace -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| At least five experiments covering all required cases | 5 | 5 | Section 1.1: twelve distinct completed runs, three for each of the four cases; screenshot groups identify runs correctly |
| Full cycle-by-cycle breakdown for each test case | 10 | 10 | Runs 9–12 step logs record every executed instruction, its cycle interval and the running total for all four cases; totals reconcile exactly |
| Screenshots of register values, memory state and PC progression | 7 | 7 | 20 final-state screenshots plus six checkpoint screenshots per traced run (setup, first load, first branch, pixel 1, pixel 8, final); the full per-step state is in the logs |
| Cache hit/miss and branch events for each iteration | 8 | 8 | Runs 9–12 record every load result and brightness prediction; the step logs list all event positions and the totals match the counters |

The earlier deduction is fully recovered: the step traces were recorded from the simulator's own STEP behavior, not reconstructed, and each one covers a complete 16-pixel run in one of the four required cases.

### 2. Performance data: 25/25

<!-- table:grade-performance -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| Total cycles for every test case | 7 | 7 | Sections 2.1–2.2: all twelve totals agree with logs, traces and cycle accounting |
| Cycles per pixel | 6 | 6 | Section 2.1: exact totals divided by 16, rounded only for display |
| Cache miss rate and branch misprediction rate | 8 | 8 | Section 2.1: counts and denominators given; distinguishes overall from brightness-only accuracy |
| Register spill count and its basis | 4 | 4 | Sections 1.2 and 2.1: zero spill operations in the supplied code; absence of a measured counter clearly stated |

Three-run means and the bottleneck explanation support this section, with the small-sample caveat stated. The three inferred input values are labelled and not counted as independent output verification.

### 3. Optimization analysis: 25/25

<!-- table:grade-optimization -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| Compare at least three strategies | 8 | 8 | Section 3.1: branch-free selection, unrolling, loop-test replacement and their combination were implemented and measured; prefetching remains a stated calculation |
| Measure improvement for each strategy | 10 | 10 | Sections 3.2–3.3: 40 runs per program per case (800 total) against a same-session baseline; every run's output checked and every total reconciled |
| Identify the best strategy for each case | 7 | 7 | Section 3.4: unrolling wins Best Case; the combined program wins the other three; the Best-Case margin over combined is reported as a near-tie with its statistical size |

The earlier zero for measurements is recovered by the variant runs. The variant programs are modified copies of the teaching simulator with documented cost assumptions (1-cycle `CSEL`, `INC #4`/offset addressing, pinned Real Case 2 inputs); Section 3.2 states that these are model measurements, not hardware benchmarks.

### 4. Extrapolation and cost impact: 20/20

<!-- table:grade-cost -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| Scale to 256 × 256 pixels | 4 | 4 | Section 4.2: three-run mean totals scaled by 4,096, or exact CPP by 65,536 |
| Calculate cycles for two million images per day | 4 | 4 | Section 4.3: all four cases with units and assumptions; 50%-of-uploads alternative in Section 4.6 |
| Electricity at 8 W, $0.12/kWh and 24-hour operation | 4 | 4 | Section 4.4: daily and annual costs, active-time allocation kept distinct |
| Estimate servers for four-hour SLA | 4 | 4 | Section 4.3: processor seconds ÷ 14,400, rounded up; limitations stated |
| Annual savings from 20% cycle reduction | 4 | 4 | Section 4.5: all cases, with constant-8 W and avoidable-power cases |

The scenario asks for estimates here, and the estimates are now anchored to the reported three-run means rather than a single run.

## Total

<!-- table:grade-total -->
| Deliverable group | Maximum | Awarded | Deducted |
|---|---|---|---|
| Instruction trace | 30 | 30 | 0 |
| Performance data | 25 | 25 | 0 |
| Optimization analysis | 25 | 25 | 0 |
| Extrapolation and cost | 20 | 20 | 0 |
| Total | 100 | 100 | 0 |

**Overall decision:** under this proposed rubric, the report now meets all four deliverable groups with recorded evidence. The previous deductions were recovered by adding evidence, not by weakening the assessment: Runs 9–12 provide the traces, and the measured variants provide the optimization results.

## What changed since the 74/100 draft

| Former deduction | Evidence added | Points recovered |
|---|---|---|
| Cycle-by-cycle trace missing | Runs 9–12 step logs (one per case, every instruction recorded) | 5 |
| Intermediate state/PC screenshots missing | 24 checkpoint screenshots across the traced runs | 2 |
| Per-iteration cache/branch events missing | Event positions recorded for all 16 iterations in each traced run | 5 |
| Measured optimization results missing | 800 measured runs across four changed programs, outputs verified | 10 |
| Best measured method per case missing | Section 3.4 ranking with margins and the Best-Case near-tie analysis | 4 |

## Remaining caveats and judgment calls

1. **Model measurements, not hardware.** The optimization numbers come from modified copies of the teaching simulator with documented cost assumptions. A real compiler or CPU benchmark could rank the strategies differently.
2. **Best Case is a near-tie.** Unrolling leads the combined program by about 1.7 standard errors; the report states this rather than over-claiming a winner.
3. **Checkpoint screenshots.** Intermediate screenshots mark six points per traced run; the complete per-step record is in the text logs.
4. **Runs 1–8 event positions.** Those runs still lack individual event positions; the traced runs supersede them for evidence purposes, but the old totals are retained unchanged.
5. **Official grading.** This file is a self-assessment against a proposed rubric, not the instructor's marks.

## Verification scope

Run `python3 verify_final_report.py` inside this folder (or `python3 Final_Report_V1/verify_final_report.py` from the repository root). The verifier checks source integrity, evidence-file checksums, Runs 1–8 against their logs, Runs 9–12 against their raw trace files, all report tables and worked examples against the data files, the measured-run invariants (base + 47 × misses + 15 × mispredictions), the marked tables in this file, and every local link. It does not authenticate when a screenshot was captured or decide academic credit automatically; the qualitative judgment above follows from the stated evidence.
