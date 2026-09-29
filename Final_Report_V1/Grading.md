# Grading assessment: Final Report V1

## Result

**Provisional self-assessment: 74/100.** The report provides a well-supported eight-run analysis, accurate performance calculations and the required workload/cost projections. It is incomplete on actual instruction-event histories and measured optimizations.

This is an evidence-based assessment of [Final_Report.md](Final_Report.md) and its included appendix/source evidence. It is **not an official instructor grade**. Neither repository supplies a numerical marking rubric or letter-grade scale. The weights below are an explicitly proposed allocation of 100 points across the four deliverable groups in the [assignment scenario](Sources/Local/Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md), under “What You'll Deliver.” The instructor may use different weights or mandatory-completion rules.

## Marking method

- Award full credit where the requested information is present and supported.
- Award partial credit for useful reconstructed analysis when the instruction specifically requests an observed trace.
- Give no measurement credit to estimates, plans, formula-filled templates or proposed code that has not been executed.
- Treat the reported performance targets as quantities to analyze, not guaranteed results. Poor simulator performance alone does not reduce the reporting mark.
- Assess documented simulator limitations explicitly. Zero spill operations can be established from the unchanged code even without a separate spill counter.

The four proposed weights are instruction trace **30**, performance data **25**, optimization analysis **25**, and extrapolation/cost **20**. The largest evidence deductions are in the two experimental areas.

## Criterion-by-criterion marks

### 1. Instruction trace: 18/30

<!-- table:grade-trace -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| At least five experiments covering all required cases | 5 | 5 | Report Section 1.1: eight distinct completed runs, two for each of the four cases; screenshot groups identified correctly |
| Full cycle-by-cycle breakdown for each test case | 10 | 5 | Sections 1.3–1.4 and 2.2, plus Appendix_Pixel_Paths.md: all costs, paths and totals reconcile, but no observed per-instruction cycle intervals or random delay order |
| Screenshots of register values, memory state and PC progression | 7 | 5 | Section 1.1 links all 20 screenshots, showing final registers, pixels and PC; intermediate register/memory states and PC progression are not recorded |
| Cache hit/miss and branch events for each iteration | 8 | 3 | Sections 1.4–1.5 and 2.2 explain event totals and penalties; the per-pixel locations are missing, except that Run 1 has no wrong branches |

The trace workbook is blank in its observation cells. Its existence does not change this mark. Reconstructed paths are useful analysis but cannot establish the lost random event sequence.

### 2. Performance data: 25/25

<!-- table:grade-performance -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| Total cycles for every test case | 7 | 7 | Sections 2.1–2.2: all eight totals agree with logs and cycle accounting |
| Cycles per pixel | 6 | 6 | Section 2.1: exact totals divided by 16, rounded only for display |
| Cache miss rate and branch misprediction rate | 8 | 8 | Section 2.1: counts and denominators given; distinguishes overall from brightness-only accuracy |
| Register spill count and its basis | 4 | 4 | Sections 1.2 and 2.1: zero spill operations in the supplied code, absence of a measured counter clearly stated |

Two-run averages and the bottleneck explanation support this section. They are properly described as a small sample. The three inferred input values are labelled, and the report does not count them as independent output verification.

### 3. Optimization analysis: 11/25

<!-- table:grade-optimization -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| Compare at least three strategies | 8 | 8 | Sections 3.1–3.3 compare prefetching, branch-free selection and loop unrolling; replacement costs and limitations are stated |
| Measure improvement for each strategy | 10 | 0 | Neither repository includes executed optimized programs, their run logs or measured comparisons |
| Identify the best strategy for each case | 7 | 3 | Section 3.3 provides conditional per-case rankings and explains Best Case regressions, but there is no measured winner |

The zero-cache-delay ceiling and one-miss sensitivity case are not separate tested optimizations. The combined 237-cycle calculation is also not an experiment. The proposed protocol in Section 3.4 is appropriate future work but earns no measurement points.

### 4. Extrapolation and cost impact: 20/20

<!-- table:grade-cost -->
| Criterion | Maximum | Awarded | Evidence and reason |
|---|---|---|---|
| Scale to 256 × 256 pixels | 4 | 4 | Section 4.2: all eight totals scaled by 4,096, or exact CPP by 65,536 |
| Calculate cycles for two million images per day | 4 | 4 | Section 4.3: all four paired means, units and assumptions given; 50%-of-uploads alternative in Section 4.6 |
| Electricity at 8 W, $0.12/kWh and 24-hour operation | 4 | 4 | Section 4.4: daily and annual costs, with active-time allocation kept distinct |
| Estimate servers for four-hour SLA | 4 | 4 | Section 4.3: divide processor time by 14,400 seconds and round up; brightness-only model limitations stated |
| Annual savings from 20% cycle reduction | 4 | 4 | Section 4.5: all cases, active-to-idle assumption and zero saving under constant 8 W |

The scenario asks for estimates here, so stated model assumptions are appropriate. No extra deduction is made for the very small savings: those follow from the supplied numbers. The report also answers the quick guide's one-CPP saving question in Section 4.6.

## Total

<!-- table:grade-total -->
| Deliverable group | Maximum | Awarded | Deducted |
|---|---|---|---|
| Instruction trace | 30 | 18 | 12 |
| Performance data | 25 | 25 | 0 |
| Optimization analysis | 25 | 11 | 14 |
| Extrapolation and cost | 20 | 20 | 0 |
| Total | 100 | 74 | 26 |

**Overall decision:** the required topics are addressed, but full empirical compliance has not been achieved. The report should not be labelled “all requirements completed” on the current evidence. A teacher who makes measured optimizations or complete traces mandatory could apply a stricter cap; no such numerical cap is stated in the supplied instructions.

## Work needed to recover the deducted points

| Missing evidence | Required addition | Points currently withheld |
|---|---|---|
| Actual cycle-by-cycle traces | Record each executed instruction, cycle increment and running total for runs covering every test case; identify cache and branch penalties at their actual steps | 5 |
| Intermediate state and PC progression screenshots | Save identifiable intermediate register, pixel/memory and PC states from those same runs, including both brightness paths | 2 |
| Per-iteration cache and branch events | Record every pixel's load result and brightness prediction, plus the loop outcome; reconcile event counts with final totals | 5 |
| Measured optimization improvements | Execute at least three changed implementations against a comparable baseline, retain outputs and logs, repeat the trials and compute improvements from measurements | 10 |
| Best measured method per case | Use the measured comparison to establish per-case winners and explain costs, variance and any regression | 4 |

These are possible points to recover under this proposed rubric, not promised future marks. New evidence must be correct and reproducible. The existing eight runs already meet the experiment-count minimum; collecting another final-state screenshot by itself does not address the trace or optimization deductions.

## Verification scope

Run `python3 Final_Report_V1/verify_final_report.py` from the repository root, or `python3 verify_final_report.py` inside this folder. The verifier checks source integrity, archived log/data agreement, pixel-rule consistency, report tables, calculations, appendix paths, local links and marking arithmetic. It does not authenticate when a screenshot was captured, measure an optimized program, or decide academic credit automatically. The qualitative marks above are the stated assessment judgment.
