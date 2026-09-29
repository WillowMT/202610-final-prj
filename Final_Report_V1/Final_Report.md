# CPU instruction execution: image brightness processing

**BSC104 final project · Combined report, version 1 · 29 September 2026**

## Summary

This report combines eight recorded experiments from two group repositories. Each of the four required test cases was run twice, processing 16 pixels per run. The mean cycle totals were 382 for Best Case, 503 for Worst Case, 421 for Real Case 1, and 451.5 for Real Case 2. Cache misses caused the largest delay in every recorded run. Incorrect branch predictions explain most of the difference between Best and Worst Case.

All 128 transcribed input/output pairs are consistent with the brightness rule. Three inputs were inferred from their outputs, so those three checks are not independent confirmation. The report includes instruction costs, reconstructed pixel paths, all eight performance records, three optimization proposals with explicit cost assumptions, and image-scale and electricity calculations.

The combined evidence meets the minimum of five experiments. Two requirements remain incomplete: actual instruction-by-instruction histories with per-iteration cache/branch events, and measured results from at least three optimized programs. Final-state screenshots and calculated savings cannot establish those results. The requirement table in Section 5 and [Grading.md](Grading.md) assess the evidence on that basis.

## Sources and method

The main requirements are the four deliverables in the supplied [project scenario](Sources/Local/Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md). The [quick guide](Sources/Local/How%20to%20Use%20Project%201%20CPU%20Simulator%20-%20Quick%20Guide.md) supplies six supporting questions. The more detailed scenario governs where the guide gives a simpler workflow.

| Source set | Repository snapshot | Contribution |
|---|---|---|
| Local | WillowMT/202610-final-prj, `16affd82bf9f668d5671e055aa3e76297dfe63dd` | Runs 1–4, eight screenshots, logs, reports, workbook and verification script |
| Scarlet | Scarlet-astra/BSC104_final_project, `016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9` | Runs 5–8, twelve screenshots, repeat-run analysis, workbook and blank trace template |

The [repository comparison](Repository_Comparison.md) explains what was retained and corrected. Unmodified source files are included in `Sources/`; [source_manifest.json](source_manifest.json) records their origin and SHA-256 checksums. Both copies of the simulator, scenario and quick guide are identical. The archived reports are source documents; this combined report contains the reconciled conclusions.

Recorded metrics come from the [Local logs](Sources/Local/Logs.md) and [Scarlet logs](Sources/Scarlet/Logs.md), checked against screenshots. Instruction behavior comes from the [simulator source](Sources/Local/Project1_CPU_Simulator.html). Averages, reconstructed paths, optimization totals and workload projections are calculations. No additional simulator runs were performed to create this merged report.

## 1. Instruction trace and experiment evidence

### 1.1 The eight experiments

Each screenshot group records one completed run. The 20 screenshots therefore support eight experiments. All runs finished 16/16 pixels, with final PC `0x34`.

| Run | Run ID | Case and input pattern | Animation delay | Source evidence |
|---|---|---|---|---|
| 1 | BC-50-R1 | Best: sixteen zeros | 50 ms | [Summary/registers](Sources/Local/Screenshots/BC-1.png), [pixels/metrics](Sources/Local/Screenshots/BC-2.png) |
| 2 | WC-50-R1 | Worst: alternating 64 and 192 | 50 ms | [Summary/registers](Sources/Local/Screenshots/WC-1.png), [pixels/metrics](Sources/Local/Screenshots/WC-2.png) |
| 3 | RC1-50-R1 | Real 1: 11 dark and 5 bright pixels | 50 ms | [Summary/registers](Sources/Local/Screenshots/RC1-1.png), [pixels/metrics](Sources/Local/Screenshots/RC1-2.png) |
| 4 | RC2-50-R1 | Real 2: 8 bright followed by 8 dark | 50 ms | [Summary/registers](Sources/Local/Screenshots/RC2-1.png), [pixels/metrics](Sources/Local/Screenshots/RC2-2.png) |
| 5 | BC-500-R2 | Best: sixteen zeros | 500 ms | [Summary](Sources/Scarlet/Screenshots/BC-R2-1.png), [registers/pixels](Sources/Scarlet/Screenshots/BC-R2-2.png), [metrics](Sources/Scarlet/Screenshots/BC-R2-3.png) |
| 6 | WC-500-R2 | Worst: alternating 64 and 192 | 500 ms | [Summary](Sources/Scarlet/Screenshots/WC-R2-1.png), [registers](Sources/Scarlet/Screenshots/WC-R2-2.png), [pixels/metrics](Sources/Scarlet/Screenshots/WC-R2-3.png) |
| 7 | RC1-500-R2 | Real 1: same input list as Run 3 | 500 ms | [Summary](Sources/Scarlet/Screenshots/RC1-R2-1.png), [registers](Sources/Scarlet/Screenshots/RC1-R2-2.png), [pixels/metrics](Sources/Scarlet/Screenshots/RC1-R2-3.png) |
| 8 | RC2-500-R2 | Real 2: new values, same 8/8 split | 500 ms | [Summary](Sources/Scarlet/Screenshots/RC2-R2-1.png), [registers](Sources/Scarlet/Screenshots/RC2-R2-2.png), [pixels/metrics](Sources/Scarlet/Screenshots/RC2-R2-3.png) |

The animation setting is a delay between displayed instructions, not the CPU clock. The code uses it in `setTimeout`, separately from cycle accounting. Larger delay values make the animation slower. The different totals between repeats come from random cache and branch outcomes. The two runs alone would not prove that speed is irrelevant; the code establishes that fact.

Real Case 1's fixed list is 68.75% dark, close to the 70% label. Real Case 2 is generated when the page loads. Runs 4 and 8 repeat a distribution, not exactly the same input image; both still have identical instruction costs because each has eight bright pixels.

### 1.2 Algorithm, registers and execution

For each input pixel `p`, the required output is `p + 32` if `p < 128`, otherwise `p - 8`. The program loads a pixel, compares it with the threshold, chooses an arithmetic path, stores the result, then updates the address and loop counter.

Conceptually, fetch selects the instruction at the PC, decode identifies its operation and register operands, and execute performs it and chooses the next PC. The teaching simulator advances one whole instruction at a time. It does not record individual hardware pipeline stages or overlapping instructions.

| Register | Role |
|---|---|
| R0 | Processed-pixel counter |
| R1 | Pixel pointer, starting at 1024 |
| R2 | Threshold, 128 |
| R3 | Current input pixel |
| R4 | Adjusted output pixel |
| R5 | Initialized to zero; unused in the baseline loop |
| R6 | Dark-pixel addition, 32 |
| R7 | Positive subtraction operand, 8 |

The interface defines eight registers. The scenario describes a processor with 32 general-purpose registers, but the simulator is not a full model of that processor. There are seven registers used by the baseline instructions and no stack spill/reload instructions.

### 1.3 Instruction costs and PC paths

| PC | Instruction | Base cycles | Effect and next instruction |
|---|---|---|---|
| 0x00 | `LOAD R0, #0` | 1 | Set counter to 0; next 0x04 |
| 0x04 | `LOAD R1, #1024` | 1 | Set starting address; next 0x08 |
| 0x08 | `LOAD R3, [R1]` | 3 | Read pixel; add 47 if a cache miss; next 0x0C |
| 0x0C | `CMP R3, R2` | 1 | Compare brightness; next 0x10 |
| 0x10 | `BLT DARK` | 1 | Dark → 0x1C, bright → 0x14; add 15 if prediction is incorrect |
| 0x14 | `SUB R4, R3, R7` | 1 | Bright output = input − 8; next 0x18 |
| 0x18 | `JMP STORE` | 2 | Jump to 0x20 |
| 0x1C | `ADD R4, R3, R6` | 1 | Dark output = input + 32; next 0x20 |
| 0x20 | `STORE R4, [R1]` | 3 | Write output; next 0x24 |
| 0x24 | `INC R1, #1` | 1 | Advance address; next 0x28 |
| 0x28 | `INC R0, #1` | 1 | Advance pixel count; next 0x2C |
| 0x2C | `CMP R0, #16` | 1 | Check completion; next 0x30 |
| 0x30 | `BNE LOOP` | 1 | Return to 0x08, or move to 0x34 after pixel 16 |
| 0x34 | `HALT` | 0 counted | Displayed stop position; the simulator stops before executing it |

The instruction list labels `HALT` as 1 cycle, but the simulator returns before adding that cycle. Stores always cost 3 cycles; only pixel loads contribute to the cache hit/miss counters. A cache-miss load costs **50 cycles total**, which is its 3-cycle base plus 47 extra cycles.

```text
Dark:   08 → 0C → 10 → 1C → 20 → 24 → 28 → 2C → 30     = 13 base cycles
Bright: 08 → 0C → 10 → 14 → 18 → 20 → 24 → 28 → 2C → 30 = 15 base cycles

Base cycles for 16 pixels = 2 + 13 × dark_count + 15 × bright_count
                         = 210 + 2 × bright_count
Executed instructions    = 2 + 9 × dark_count + 10 × bright_count
```

<!-- table:instruction-counts -->
| Instruction executions per run | Best (1, 5) | Worst (2, 6) | Real 1 (3, 7) | Real 2 (4, 8) |
|---|---|---|---|---|
| Each setup instruction: 0x00, 0x04 | 1 | 1 | 1 | 1 |
| Each of 0x08, 0x0C, 0x10 | 16 | 16 | 16 | 16 |
| Each of 0x14, 0x18 | 0 | 8 | 5 | 8 |
| 0x1C | 16 | 8 | 11 | 8 |
| Each of 0x20, 0x24, 0x28, 0x2C, 0x30 | 16 | 16 | 16 | 16 |
| Total executed instructions | 146 | 154 | 151 | 154 |
| Base cycles before delays | 210 | 226 | 220 | 226 |

### 1.4 Pixel paths, final state and missing event history

The [pixel-path appendix](Appendix_Pixel_Paths.md) contains all 128 inputs, their evidence basis, outputs, paths and cumulative base-cycle totals. For pixel `n`, the load address is `1023 + n`. After that iteration, R0 = `n`, R1 = `1024 + n`, R3 contains its input and R4 contains its output.

Every run finishes with R0 = 16 (`0x10`) and R1 = 1040 (`0x410`). The execution summary shows the last executed instruction, `0x30 BNE LOOP`, while Current PC shows the next position, `0x34`. The final R3/R4 pairs are 0/32 for Best, 192/184 for Worst, 140/132 for Real 1, 60/92 for Run 4, and 55/87 for Run 8. R7 is clipped in Local's screenshots; Scarlet's register screenshots show `0x08` directly.

The input evidence has three levels:

- 93 inputs were transcribed from readable cells.
- 32 Best Case inputs come from the all-zero test definition; the cell text is black on black.
- Run 4 pixels 9 and 12 are inferred as 6 from output 38; Run 8 pixel 15 is inferred as 8 from output 40.

All pairs are mathematically consistent with the brightness rule. The three inferred pairs cannot independently establish output correctness because the same rule was used to obtain their inputs.

For an actual timing history, define `M_i = 1` for a cache miss on pixel i and `B_i = 1` for an incorrect brightness prediction. Then:

```text
Cycles for pixel i = base_path_cycles_i + 47 × M_i + 15 × B_i
Running actual cycles after pixel n = 2 + sum(cycles for pixels 1 through n)
```

The screenshots provide the sums of `M_i` and `B_i`, but not their positions. Run 1 has no incorrect predictions, so all its `B_i` values are zero; even there, the three cache-miss positions remain unknown. Assigning delays to specific pixels would fabricate an event history.

The archived [Worst Case trace workbook](Sources/Scarlet/Step_Trace_Worst_Case.xlsx) contains a prepared template. Its observation cells F12:G27 and J11:J27 are empty. Formula-generated expected totals in that file are not recorded results. It also records events per pixel rather than every executed instruction, so it needs an instruction-level companion to meet the full trace requirement.

### 1.5 What the simulator models

Each load has an approximately 80% random chance of a cache hit. The model does not simulate cache lines, associativity, capacity replacement, prefetching or memory bandwidth. It cannot demonstrate a compulsory first miss or a miss caused by a particular image boundary.

For `BLT`, correct-prediction probabilities are 95% for Best, 50% for Worst, and 80% for both real cases. These probabilities are selected by the case label; they do not come from a predictor learning the values. `BNE` is always counted as correct, including its final not-taken decision. Each run therefore has 16 brightness predictions plus 16 correct loop predictions. The unconditional `JMP` is not included in that metric.

These details explain why Run 5 has a wrong prediction despite all-zero input, and why clustering alone cannot explain the exact branch outcomes in Runs 4 and 8. The code also contains no register allocator, out-of-order scheduler or measured memory-bandwidth model. Broader scenario descriptions provide context, not additional observations from this simulator.

## 2. Performance data and bottlenecks

### 2.1 All recorded results

CPP is calculated from total cycles divided by 16. Displayed figures are rounded only after calculation. Spill count is **0 from code inspection** in all eight runs; there is no measured spill counter.

<!-- table:results -->
| Run | Case | Total cycles | CPP | Cache hits | Cache misses | Correct branches | Total branches | Stall cycles |
|---|---|---|---|---|---|---|---|---|
| 1 | Best | 351 | 21.94 | 13 | 3 | 32 | 32 | 141 |
| 2 | Worst | 502 | 31.38 | 13 | 3 | 23 | 32 | 276 |
| 3 | Real 1 | 406 | 25.38 | 13 | 3 | 29 | 32 | 186 |
| 4 | Real 2 | 444 | 27.75 | 12 | 4 | 30 | 32 | 218 |
| 5 | Best | 413 | 25.81 | 12 | 4 | 31 | 32 | 203 |
| 6 | Worst | 504 | 31.50 | 12 | 4 | 26 | 32 | 278 |
| 7 | Real 1 | 436 | 27.25 | 13 | 3 | 27 | 32 | 216 |
| 8 | Real 2 | 459 | 28.69 | 12 | 4 | 29 | 32 | 233 |

The cache denominator is 16 loads, not all 32 pixel reads and writes. The reported branch denominator is 32, including the always-correct loop checks. Brightness-only accuracy uses 16 as its denominator and shows a less flattering result.

<!-- table:rates -->
| Run | Cache hit rate | Cache miss rate | Overall branch accuracy | Overall misprediction rate | Brightness-only accuracy |
|---|---|---|---|---|---|
| 1 | 81.3% | 18.8% | 100.0% | 0.0% | 100.0% |
| 2 | 81.3% | 18.8% | 71.9% | 28.1% | 43.8% |
| 3 | 81.3% | 18.8% | 90.6% | 9.4% | 81.3% |
| 4 | 75.0% | 25.0% | 93.8% | 6.3% | 87.5% |
| 5 | 75.0% | 25.0% | 96.9% | 3.1% | 93.8% |
| 6 | 75.0% | 25.0% | 81.3% | 18.8% | 62.5% |
| 7 | 81.3% | 18.8% | 84.4% | 15.6% | 68.8% |
| 8 | 75.0% | 25.0% | 90.6% | 9.4% | 81.3% |

For example, Run 2 has nine wrong predictions: overall error is `9/32 = 28.125%`, while brightness-only error is `9/16 = 56.25%`. Rounded complementary rates can add to 100.1%; the counts are the calculation source.

### 2.2 Exact reconciliation

```text
Cache delay = 47 × cache misses
Branch delay = 15 × (total branches − correct branches)
Stall cycles = cache delay + branch delay
Total cycles = base cycles + stall cycles
```

<!-- table:reconciliation -->
| Run | Dark | Bright | Base cycles | Cache delay | Branch delay | Total cycles |
|---|---|---|---|---|---|---|
| 1 | 16 | 0 | 210 | 141 | 0 | 351 |
| 2 | 8 | 8 | 226 | 141 | 135 | 502 |
| 3 | 11 | 5 | 220 | 141 | 45 | 406 |
| 4 | 8 | 8 | 226 | 188 | 30 | 444 |
| 5 | 16 | 0 | 210 | 188 | 15 | 413 |
| 6 | 8 | 8 | 226 | 188 | 90 | 504 |
| 7 | 11 | 5 | 220 | 141 | 75 | 436 |
| 8 | 8 | 8 | 226 | 188 | 45 | 459 |

Across all runs, `1,764 base + 1,316 cache + 435 branch = 3,515 cycles`. Cache misses account for about 75.2% of the 1,751 stall cycles. This identifies the largest recorded source of waiting, rather than proving that memory bandwidth limits a real server.

The base load and store costs are 48 cycles each per run. Misses add another 141 or 188 cycles to the load instruction. Brightness prediction mistakes add 0–135 cycles to `BLT`. These are the main instruction-level costs worth investigating.

### 2.3 Repeat-run comparison

Each mean below uses two runs of 16 pixels. Pooled rates use the combined counts: 32 loads and 64 branch predictions per case. They are descriptive results from a small sample, not reliable population averages or a production workload mix.

<!-- table:averages -->
| Case | First run cycles | Second run cycles | Difference | Mean cycles | Mean CPP | Pooled cache hit rate | Pooled branch accuracy |
|---|---|---|---|---|---|---|---|
| Best | 351 | 413 | +62 | 382.0 | 23.88 | 78.1% | 98.4% |
| Worst | 502 | 504 | +2 | 503.0 | 31.44 | 78.1% | 76.6% |
| Real 1 | 406 | 436 | +30 | 421.0 | 26.31 | 81.3% | 87.5% |
| Real 2 | 444 | 459 | +15 | 451.5 | 28.22 | 75.0% | 92.2% |

The changes are fully accounted for: Best adds one cache miss and one wrong branch (`47 + 15 = 62`); Worst adds one miss but removes three wrong branches (`47 − 45 = 2`); Real 1 adds two wrong branches (`30`); Real 2 adds one (`15`). No base instruction cost changes between either pair.

Best and Worst have equal mean cache delay, 164.5 cycles. Worst's mean branch delay is 105 cycles higher and its base cost is 16 higher, explaining the full `503 − 382 = 121` difference. Within each run, cache delay is still larger than branch delay. These two findings answer different questions.

### 2.4 Assignment targets

| Target from the scenario | Combined finding |
|---|---|
| CPP < 5 | None meets it; even a delay-free all-dark baseline needs 210/16 = 13.125 CPP |
| Cache hit rate > 95% | None meets it; observed per-run rates are 75.0% or 81.25% before rounding |
| Overall branch accuracy > 90% | Runs 1, 3, 4, 5 and 8 meet it; Runs 2, 6 and 7 do not |
| Register spills = 0 | No spill instructions are present; this is a code finding |

Missing a target is a performance result to explain. It is not evidence that the student's arithmetic is wrong. The sample CPP values and perfect/impossible prediction claims in the guide are not measurements of this code.

## 3. Optimization analysis

### 3.1 Three strategies and their assumptions

No measured optimized runs exist in either repository. The supplied interface has no editable instruction program or switches for these methods. The following calculations compare possible changes and show where measurements are still needed.

| Strategy | Proposed change | Cost model used here | Limitation |
|---|---|---|---|
| Cache prefetching | Request upcoming pixels before they are loaded | Sensitivity case: reduce misses to one, hold everything else fixed, assume zero added prefetch cost | One remaining miss is an assumption, not a demonstrated cache result |
| Branch-free selection | Compute both candidate outputs and select without `BLT`/`JMP` | Four 1-cycle decision operations; 226 base cycles for 16 pixels; retain recorded cache delay | Conditional select cost and unchanged cache behavior are assumptions |
| Four-pixel loop unrolling | Process four pixels before the counter update and loop check | Reduce three loop-control instructions from 16 executions to 4: save 36 cycles | Extra code/register costs are not modeled; pixel address updates still occur |

The Local report's zero-cache-delay calculation is retained as a theoretical ceiling. Scarlet's one-miss scenario is retained as a separate sensitivity case. The simulator has no cache-line model; a typical 64-byte line and a claim that these pixels occupy exactly 16 bytes cannot establish what prefetching would achieve. The scenario's 524,288-byte read/write example assumes four bytes per pixel, whereas this simulator uses abstract array entries and pointer increments of one.

The branch-free proposal uses the following conceptual operations, with **assumed**, not benchmarked, 1-cycle costs:

```text
dark_result   = input + 32
bright_result = input - 8
compare input with 128
select bright_result if input >= 128, otherwise dark_result
```

The old compare/branch/arithmetic region costs 3 cycles for a dark pixel or 5 for a bright pixel. The proposed region costs 4 for either. Including the load, store, address update and loop control gives `14 cycles/pixel`, plus 2 setup cycles: `226 base cycles`. Brightness mispredictions disappear in this model, while loop predictions were already always correct. R5 could hold the second candidate, but real register allocation still needs checking.

### 3.2 Calculated outcomes for all eight runs

Let `C` be recorded cycles, `M` recorded misses, and `W` wrong brightness predictions:

```text
Zero-cache-delay ceiling: C − 47 × M
One-miss sensitivity:    C − 47 × (M − 1)
Branch-free model:      226 + 47 × M
Four-pixel unrolling:   C − 36
Cycle reduction (%):    (C − calculated_total) / C × 100
```

The first numeric column below is recorded. All remaining totals are estimates. Parentheses show percentage cycle reductions; a negative reduction means the change makes the run slower.

<!-- table:optimizations -->
| Run | Recorded cycles | Zero cache delay ceiling | One-miss sensitivity | Branch-free model | Four-pixel unrolling |
|---|---|---|---|---|---|
| 1 | 351 | 210 (40.2%) | 257 (26.8%) | 367 (-4.6%) | 315 (10.3%) |
| 2 | 502 | 361 (28.1%) | 408 (18.7%) | 367 (26.9%) | 466 (7.2%) |
| 3 | 406 | 265 (34.7%) | 312 (23.2%) | 367 (9.6%) | 370 (8.9%) |
| 4 | 444 | 256 (42.3%) | 303 (31.8%) | 414 (6.8%) | 408 (8.1%) |
| 5 | 413 | 225 (45.5%) | 272 (34.1%) | 414 (-0.2%) | 377 (8.7%) |
| 6 | 504 | 316 (37.3%) | 363 (28.0%) | 414 (17.9%) | 468 (7.1%) |
| 7 | 436 | 295 (32.3%) | 342 (21.6%) | 367 (15.8%) | 400 (8.3%) |
| 8 | 459 | 271 (41.0%) | 318 (30.7%) | 414 (9.8%) | 423 (7.8%) |

The branch-free saving simplifies to `15W + 2 × bright_count − 16`. It must exceed zero to help. Run 1 has no branch delay to remove, so its total rises by 16 cycles. Run 5 removes 15 branch cycles but adds 16 base cycles, producing a one-cycle loss. In Run 3 it removes 45 branch cycles but adds 6 base cycles, giving a 39-cycle saving rather than the 45-cycle upper bound in the Local report.

### 3.3 Which strategy is most promising?

Using reductions of the paired mean totals, rather than averaging rounded percentages:

<!-- table:optimization-means -->
| Case | Recorded mean | One-miss mean estimate | Branch-free mean estimate | Unrolled mean estimate |
|---|---|---|---|---|
| Best | 382.0 | 264.5 (30.8%) | 390.5 (-2.2%) | 346.0 (9.4%) |
| Worst | 503.0 | 385.5 (23.4%) | 390.5 (22.4%) | 467.0 (7.2%) |
| Real 1 | 421.0 | 327.0 (22.3%) | 367.0 (12.8%) | 385.0 (8.6%) |
| Real 2 | 451.5 | 310.5 (31.2%) | 414.0 (8.3%) | 415.5 (8.0%) |

The one-miss assumption gives the largest mean saving in all four cases, but it has no measured support. Branch-free selection beats it in the individual Run 2 calculation, which shows that the ranking depends on the observed delays and chosen assumptions. Worst Case is the strongest branch-free candidate on paired means; Best Case becomes slower. Unrolling gives a steady 36-cycle saving under its assumptions.

Combining the three models gives `226 − 36 + 47 = 237 cycles` for 16 pixels, assuming one miss, no brightness branches, no added costs and no interaction penalties. That is 52.9% below Worst's mean of 503, but still 14.8125 CPP, above the target of 5. This combined estimate is not a fourth experiment or a measured optimization.

### 3.4 Measurements required to finish this section

Implement each changed program in a tool that supports it, retaining its source and cost rules. Compare baseline and variants on the same saved input lists, check every output, and repeat each case enough times to report a mean and spread. If randomness is controlled, use documented seeds or per-pixel event streams so program changes do not silently alter the comparison. Preserve the assumptions of the cache model when testing prefetching; simply replacing a miss count with one is a calculation.

Record method, case, repeat ID, input list, total cycles, instruction count, cache events, branch events, spill operations and output checks. Include each method's added instructions and any register pressure. Calculate measured reduction from the repeated baseline and optimized means, then identify the best measured strategy for each case. A plan for these tests earns no credit for results that have not yet been collected.

## 4. Extrapolation and cost impact

### 4.1 Workload assumptions

The required calculation treats an image as one 256 × 256 chunk: 65,536 pixels. It uses 2,000,000 processed images/day, one dedicated 2.4 GHz processor per modeled server, 8 W processor power, $0.12/kWh and 365 days/year. The entire daily batch is assumed to arrive together and must finish within four hours. This is a conservative batch interpretation of the stated latency deadline.

The scenario also says only 50% of uploads need adjustment. We show that 1,000,000-image alternative separately. Actual 5–25 MB photos may contain many chunks; compressed file size alone does not determine their pixel count. Decoding, I/O, networking, other tasks and whole-server power are outside these estimates. One clock cycle is about 0.417 ns at 2.4 GHz; one instruction can take several cycles.

### 4.2 Scaling all eight recorded runs

```text
Groups per image = 65,536 / 16 = 4,096
Image cycles = 16-pixel total × 4,096 = exact CPP × 65,536
```

The factor 4,096 applies to the 16-pixel total, not CPP. This scaling includes the small run's setup cost in each group, matching the simulator display. A single large loop might amortize setup differently; it has not been measured here.

<!-- table:image-runs -->
| Run | Recorded cycles | Estimated image cycles |
|---|---|---|
| 1 | 351 | 1,437,696 |
| 2 | 502 | 2,056,192 |
| 3 | 406 | 1,662,976 |
| 4 | 444 | 1,818,624 |
| 5 | 413 | 1,691,648 |
| 6 | 504 | 2,064,384 |
| 7 | 436 | 1,785,856 |
| 8 | 459 | 1,880,064 |

### 4.3 Daily cycles and four-hour server count

Use each case's exact two-run mean to avoid selecting a favorable repeat. These four scenarios are alternatives, not four workloads to add together.

```text
Daily cycles = mean image cycles × 2,000,000
Processor seconds = daily cycles / 2,400,000,000
Servers = ceiling(processor seconds / 14,400)
```

<!-- table:scaling -->
| Case | Mean image cycles | Daily cycles | Processor seconds/day | Fraction of four-hour capacity | Whole servers |
|---|---|---|---|---|---|
| Best | 1,564,672 | 3,129,344,000,000 | 1,303.89 | 0.0905 | 1 |
| Worst | 2,060,288 | 4,120,576,000,000 | 1,716.91 | 0.1192 | 1 |
| Real 1 | 1,724,416 | 3,448,832,000,000 | 1,437.01 | 0.0998 | 1 |
| Real 2 | 1,849,344 | 3,698,688,000,000 | 1,541.12 | 0.1070 | 1 |

The simplified calculation needs one server in all cases. Even the largest individual result, Run 6, needs only 1,720.32 processor seconds, below 14,400. This is an arithmetic lower-bound model for the brightness stage, not a production capacity measurement. No workload mixture was supplied, so Real 1 is used only as a worked example, not asserted to be the average uploaded photograph.

### 4.4 Electricity for 24-hour operation

```text
8 W = 0.008 kW
Daily energy = 0.008 × 24 = 0.192 kWh
Daily cost = 0.192 × $0.12 = $0.02304
Annual cost = $0.02304 × 365 = $8.4096
```

This is one processor's cost at a constant 8 W. Finishing the image calculation earlier does not reduce that fixed bill.

For comparison, Real 1's calculated active time is `1,437.013333 seconds/day`. Its processing-only energy is `1,437.013333 / 3,600 × 0.008 = 0.00319336 kWh/day`, costing about **$0.00038320/day**, or **$0.13987/year**. This allocates power only to the modeled processing interval; it excludes idle power and is not the full 24-hour cost.

### 4.5 Annual savings from a 20% cycle reduction

This is the hypothetical reduction requested in the assignment, separate from the untested optimization models. For Real 1's mean:

```text
Exact mean CPP: 421 / 16 = 26.3125
Improved CPP: 26.3125 × 0.80 = 21.05
Improved daily cycles: 3,448,832,000,000 × 0.80 = 2,759,065,600,000
Improved time: 1,437.013333 × 0.80 = 1,149.610667 seconds/day
Time saved: 287.402667 seconds/day
```

<!-- table:annual-savings -->
| Case | Seconds saved/day | Annual saving if full 8 W is avoided during saved time | Annual saving at constant 8 W all day |
|---|---|---|---|
| Best | 260.78 | $0.025382 | $0 |
| Worst | 343.38 | $0.033422 | $0 |
| Real 1 | 287.40 | $0.027974 | $0 |
| Real 2 | 308.22 | $0.030000 | $0 |

The active-time saving is `saved_seconds / 3,600 × 0.008 × $0.12 × 365`. Actual savings depend on the active-to-idle power difference, which was not supplied. If the processor remains at 8 W for 24 hours, the annual bill stays $8.4096.

A 20% cycle reduction gives `1/0.8 = 1.25`, or 25% more throughput at a fixed clock. The whole-server count remains one. There is no supported server purchase/rental saving or million-dollar electricity saving from the supplied workload and power figures.

### 4.6 Quick-guide question: saving one CPP

For two million assignment images per day:

```text
Daily cycles saved = 1 × 65,536 × 2,000,000 = 131,072,000,000
Seconds saved = 131,072,000,000 / 2,400,000,000 = 54.613333
Avoidable energy = 54.613333 / 3,600 × 0.008 = 0.00012136296 kWh/day
Possible daily saving = 0.00012136296 × $0.12 = $0.00001456356
```

For the 50%-of-uploads alternative, daily cycles, processing times and processing-dependent energy/savings halve. One CPP then saves 27.306667 seconds and about $0.00000728178/day. Real 1's daily baseline becomes 1,724,416,000,000 cycles and 718.506667 seconds. The integer server count remains one, and a constant 24-hour 8 W bill does **not** halve.

## 5. Requirement coverage and conclusion

The report follows all four requested deliverable areas. The distinction between a topic being discussed and its required measurements being complete is recorded below.

| Assignment criterion | Location and evidence | Status |
|---|---|---|
| At least five experiments; all four test cases | Section 1.1: eight complete runs, two per case | Met for experiment count |
| Full cycle-by-cycle breakdown for each case | Sections 1.3–1.4, 2.2 and pixel appendix | Partial: base paths and totals, no actual per-instruction timing history |
| Screenshots of registers, memory state and PC progression | Section 1.1 links all 20 screenshots; Section 1.4 explains final state | Partial: final registers/pixels/PC captured; intermediate progression not saved |
| Cache hit/miss and branch events each iteration | Sections 1.4–1.5 and 2.2 | Partial: totals and costs known; event locations missing |
| Total cycles for each test case | Section 2.1 | Met for all eight runs |
| CPP | Section 2.1 | Met |
| Cache miss and branch misprediction rates | Section 2.1 | Met, with denominators stated |
| Register spill count | Sections 1.2 and 2.1 | Addressed as zero from code; no separate counter |
| Compare at least three optimizations | Sections 3.1–3.3 | Met as a theoretical comparison |
| Measure each strategy's improvement | Section 3.4 defines required measurement method | Not met: no optimized execution results |
| Best strategy for each test case | Section 3.3 | Partial: conditional estimates, no measured winner |
| Scale to 65,536 pixels and two million images/day | Sections 4.2–4.3 | Met as requested projections |
| Electricity at 8 W, $0.12/kWh and 24-hour operation | Section 4.4 | Met |
| Server count for four-hour SLA | Section 4.3 | Met under stated assumptions |
| Annual savings for 20% cycle reduction | Section 4.5 | Met, with fixed-power and avoidable-power cases |

The six quick-guide questions are covered by Section 2.1 (collect), Sections 2.2–2.3 (explain), Section 2.2 (bottleneck), Section 3 (optimize), Section 4.2 (extrapolate) and Section 4.6 (one-CPP saving).

The combined runs strengthen the original analysis by exceeding the minimum experiment count and showing how random delays change repeated results. The calculated ranking of baseline performance is Best, Real 1, Real 2, then Worst. Cache misses dominate waiting; the extra Worst Case cost is largely explained by branch mistakes. Branch-free selection is worth testing on Worst Case but can hurt Best Case once replacement instructions are counted.

Full empirical completion still requires newly recorded instruction traces covering every test case and measured comparisons of at least three changed programs. For each trace, save executed PC, next PC, cycle interval, register changes, memory access/output and cache/branch event. Capture the execution summary after each STEP FORWARD: Current PC has already advanced, so its highlight may identify the next instruction. A new run must retain its own ID and final totals; it cannot recover an earlier run's random history.

The [grading assessment](Grading.md) marks the finished version against these requirements, with deductions tied to the missing evidence rather than hidden by the merged document.
