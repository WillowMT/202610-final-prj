# Comparison of the two repositories

## Snapshots reviewed

| Label | Repository | Pinned commit | Archived evidence |
|---|---|---|---|
| Local | [WillowMT/202610-final-prj](https://github.com/WillowMT/202610-final-prj/tree/16affd82bf9f668d5671e055aa3e76297dfe63dd) | `16affd82bf9f668d5671e055aa3e76297dfe63dd` | [Sources/Local](Sources/Local/) |
| Scarlet | [Scarlet-astra/BSC104_final_project](https://github.com/Scarlet-astra/BSC104_final_project/tree/016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9) | `016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9` | [Sources/Scarlet](Sources/Scarlet/) |

Comparison date: 29 September 2026. Local was clean at the start of this work. The package preserves 41 source files, including all 20 screenshots and three Excel workbooks. [source_manifest.json](source_manifest.json) records a SHA-256 checksum and byte count for every archived file.

## Contributions and differences

| Area | Local repository | Scarlet repository | Combined treatment |
|---|---|---|---|
| Assignment scenario and quick guide | Contains both | Contains both | Byte-identical; use the scenario's full deliverables as the standard |
| Simulator | `Project1_CPU_Simulator.html` | Same file | Byte-identical; all eight runs share the same cost and randomness rules |
| Experiments | Runs 1–4, 50 ms, one per case | Runs 5–8, 500 ms, one per case | Eight completed experiments; preserve IDs and distinguish display delay from cycles |
| Cycle totals, in Best/Worst/Real 1/Real 2 order | 351 / 502 / 406 / 444 | 413 / 504 / 436 / 459 | Retain all eight totals; paired means 382 / 503 / 421 / 451.5 |
| Screenshots | Two per run, eight total | Three per run, twelve total | All twenty retained with separate source paths |
| Register evidence | R7 clipped | R7 = 8 visible | Keep Local's visibility caveat; use Scarlet's direct reading as additional evidence |
| Best/Worst/Real 1 inputs | Fixed case lists | Same lists | Exact repeat inputs |
| Real 2 inputs | Eight bright, eight dark; pixels 9 and 12 inferred | Different values; same split; pixel 15 inferred | Keep both input lists and all three inference labels |
| Output checks | 64 pairs | 64 pairs | 128 consistent pairs; three are not independent checks |
| Performance tables | Four runs, reconstructed costs | Four additional runs and two-run cycle averages | Recalculate all rates, paired means and delay breakdowns from counts |
| Optimization comparison | Zero-delay upper bounds and 36-cycle unrolling estimate | One-miss scenario, branch-free replacement-cost model and unrolling | Retain ceiling and sensitivity cases separately; use explicit replacement costs |
| Step trace | No recorded event history | `Step_Trace_Worst_Case.xlsx` is a blank template | Neither provides actual instruction-level timing or complete event sequences |
| Workbooks | Summary, case data and charts | Data workbook plus trace template | Preserve originals; combined numerical tables are in the report and data.json |
| Cost calculations | Worked example uses Run 3 | Worked example uses Run 7 | Use the exact paired Real 1 mean, and also show all four cases |
| Reproduction/checks | Report_Maker.md and four-run verifier | No equivalent script | Archive Local tools; add an eight-run package verifier |

## Corrections made during synthesis

1. **Experiment count.** Local's statement that a fifth run is missing is superseded by the imported Runs 5–8. Repeated references to Local's results in Scarlet's documents do not create extra experiments. Eight is the count, not twelve, sixteen or twenty.

2. **Trace completeness.** Both repositories contain final-state evidence and reconstructed paths. Scarlet's trace workbook has no observations in its cache, branch or measured-cycle entry cells. Its prefilled inputs and formulas are preparation, not a ninth run. The screenshots show final PC, not a captured PC progression.

3. **Prefetching assumptions.** Scarlet describes the pixels as 16 bytes in one typical 64-byte cache line and calls one initial miss realistic. The simulator has abstract addresses and randomly drawn hits, with no cache-line implementation. The scenario's separate bandwidth arithmetic assumes four-byte pixels. The report therefore labels one remaining miss as a sensitivity assumption and charges no claim of measured prefetch performance to it.

4. **Branch-free costs.** Local's removal of branch penalties is a savings ceiling, not a full changed-program cost. Scarlet includes the cost of calculating both outputs and selecting. The combined model uses 226 base cycles and retains original cache penalties, explicitly assuming the operation costs. It makes both Best Case runs slower: 351 → 367 and 413 → 414.

5. **Optimization rankings.** A zero-cache-delay ceiling and a one-miss scenario produce different rankings. For Run 2, branch-free selection is estimated at 367 cycles versus 408 for the one-miss scenario. Across both Worst runs, the respective means are 390.5 and 385.5. The report gives conditional rankings and no measured winner.

6. **Pattern explanations.** Scarlet's prose sometimes attributes branch outcomes to alternating or clustered pixels. Actual prediction accuracy is drawn using fixed probabilities determined by the case label. The revised explanation uses that code behavior and avoids claiming that this predictor learned a boundary.

7. **Animation direction and causality.** The quick guide reverses the speed-slider description: larger millisecond delays make animation slower. Code inspection, rather than comparing two random samples, establishes that delay is separate from cycle accounting.

8. **Instruction and spill claims.** HALT displays 1 cycle but is never charged. R7 is +8, used by a subtraction. Eight register entries are defined, seven are used by baseline instructions, and R5 is unused. The scenario's 32-register CPU is not fully simulated. Zero spills is a source-code conclusion, not an exported counter.

9. **Scaling.** The guide's factor 4,096 applies to a 16-pixel total; CPP must be multiplied by 65,536. Exact totals, rather than rounded CPP, are used. Setup cost is scaled with the sample, matching the simulator display.

10. **Electricity and workload.** The two-million-processed-image deliverable is the main model; the 50%-of-uploads interpretation is a separate sensitivity case. Only processing-dependent totals halve under that alternative. Constant 8 W, 24-hour electricity cost remains $8.4096/year. A 20% speed improvement does not automatically reduce that bill.

## Evidence precedence

The assignment scenario defines what must be delivered. For recorded data, screenshots and their labelled transcriptions establish what was observed. Simulator code explains the counters and paths. Derived calculations use those inputs with stated assumptions. Example values in the quick guide, blank template formulas and untested optimizations do not become observations.

Source documents were retained unchanged so a reader can inspect the original reasoning and differences. Their older status statements are not the final assessment. [Final_Report.md](Final_Report.md) is the reconciled report; [Grading.md](Grading.md) assesses that version.

## What the merge resolves

The combined evidence clears the five-experiment minimum, adds repeat comparisons, improves R7 visibility, and makes the optimization trade-offs more explicit. It still does not supply a recorded per-instruction trace, per-iteration event sequence, or measured optimized implementation. Those are the two main evidence gaps: trace collection and optimization testing.
