# CPU instruction execution: image brightness processing

**BSC104 final project · Analysis report · 29 September 2026**

## Summary

Twelve recorded experiments support this report: three runs on each of the four required test cases. Runs 1–8 are final-state runs from two group data collections. Runs 9–12 are full step-by-step traces, one per case. Every run processed 16 pixels. Cache misses were the largest source of waiting in eleven of the twelve runs. The exception is the traced Worst Case run, where one rare miss left its seven branch mispredictions as the larger delay.

The three recorded totals per case are 351, 413 and 366 for Best; 502, 504 and 378 for Worst; 406, 436 and 451 for Real Case 1; and 444, 459 and 397 for Real Case 2. The spread inside a case comes from the simulator's random cache and branch outcomes. Runs 9–12 also record the cache result and branch outcome for each of the 16 iterations, filling in the event positions that the earlier final-state runs could not capture.

All 192 recorded input/output pairs are consistent with the brightness rule: 141 inputs were read directly (93 from screenshot transcriptions, 48 from live step records), 48 are the all-zero Best Case definition, and three Real Case 2 values were inferred from their outputs. The optimization results in Section 3 are measurements: branch-free selection, four-pixel loop unrolling, pointer loop-testing and their combination were implemented as modified copies of the simulator, and each program ran 40 times per test case (800 measured runs, every output checked). The combined program gives the best measured mean for Worst Case (−34.5%), Real Case 1 (−23.2%) and Real Case 2 (−19.2%); unrolling gives the best Best-Case mean (−12.8%). Cache prefetching remains a calculation because the simulator models no cache contents.

Section 5 maps the findings to the assignment requirements. The screenshots, pixel tables, traces and optimization measurements behind these findings are all in Appendices A–D.

## Sources and method

The course brief for Project 1, *CPU Instruction Execution: Image Brightness Processing*, asks for four deliverables: instruction traces, performance data, optimization analysis, and extrapolation with cost estimates. The accompanying simulator guide, *How to Use Project 1 Simulator*, adds questions about the bottleneck and the saving from reducing CPP by one. This report addresses those requirements in Sections 1–5; Section 6 lists the course materials.

| Source set | Collection | Evidence included in this report |
|---|---|---|
| Local | First collection, 50 ms animation delay | Runs 1–4, eight screenshots in Appendix A.1, and pixel tables in Appendix B.1–B.4 |
| Scarlet | Second collection, 500 ms animation delay | Runs 5–8, twelve screenshots in Appendix A.1, and pixel tables in Appendix B.5–B.8 |
| Step traces and optimization study | Additional measurements using the same baseline model | Runs 9–12, 24 checkpoint screenshots in Appendix A.2, complete traces in Appendix C, and 800 optimization measurements in Appendix D |

Both original collections used identical copies of the supplied simulator and course instructions. The labels Local and Scarlet distinguish the collections; their different animation delays do not change the cycle model.

Recorded metrics for Runs 1–8 were transcribed from completed simulator runs and checked against the screenshots in Appendix A.1. Runs 9–12 were recorded instruction by instruction using the unchanged baseline simulator. The optimization study used that baseline and four modified programs under the stated cost assumptions. Section 1.3 gives the baseline instruction behavior; Section 3 explains the changed programs and measurement procedure. Averages, reconstructed paths and workload projections are calculations; the optimization results are measurements within this teaching model.

**Where the screenshots sit.** Figures 1–4 show pixel memory, Figures 5–16 show execution checkpoints, and Figures 17–20 show final metrics for all four cases. Appendix A embeds all 44 run screenshots and five optimization sample screenshots. Pixel and metric figures are unscaled crops; checkpoint figures rearrange the four status boxes above the register panel from the **same screenshot**. Values, colors and existing visibility limitations are preserved. The figures are copies of existing captures, prepared for readability.

**How the appendices are organized.** Appendix A holds every screenshot. Appendix B lists the reconstructed pixel paths for Runs 1–8, and Appendix C prints the recorded traces and pixel events for Runs 9–12. Appendix D contains all 800 optimization measurement records, totals and statistical calculations. References to sections, figures and appendices refer to this document.

## 1. Instruction trace and experiment evidence

### 1.1 The twelve experiments

Each screenshot group records one completed run. The 20 final-state screenshots and 24 checkpoint screenshots therefore support twelve experiments, not 44. All runs finished 16/16 pixels, with final PC `0x34`.

<!-- table:runs -->
| Run | Run ID | Case and input pattern | Animation delay | Evidence within this report |
|---|---|---|---|---|
| 1 | BC-50-R1 | Best: sixteen zeros | 50 ms | Appendix A.1, Run 1; Appendix B.1 |
| 2 | WC-50-R1 | Worst: alternating 64 and 192 | 50 ms | Appendix A.1, Run 2; Appendix B.2 |
| 3 | RC1-50-R1 | Real 1: 11 dark and 5 bright pixels | 50 ms | Appendix A.1, Run 3; Appendix B.3 |
| 4 | RC2-50-R1 | Real 2: 8 bright followed by 8 dark | 50 ms | Appendix A.1, Run 4; Appendix B.4 |
| 5 | BC-500-R2 | Best: sixteen zeros | 500 ms | Appendix A.1, Run 5; Appendix B.5 |
| 6 | WC-500-R2 | Worst: alternating 64 and 192 | 500 ms | Appendix A.1, Run 6; Appendix B.6 |
| 7 | RC1-500-R2 | Real 1: same input list as Run 3 | 500 ms | Appendix A.1, Run 7; Appendix B.7 |
| 8 | RC2-500-R2 | Real 2: new values, same 8/8 split | 500 ms | Appendix A.1, Run 8; Appendix B.8 |
| 9 | BC-50-R3 | Best: sixteen zeros, full step trace | 50 ms | Figures 1, 5–7, 17; Appendix A.2, Run 9; Appendix C.1 |
| 10 | WC-50-R3 | Worst: alternating, full step trace | 50 ms | Figures 2, 8–10, 18; Appendix A.2, Run 10; Appendix C.2 |
| 11 | RC1-50-R3 | Real 1: same fixed list, full step trace | 50 ms | Figures 3, 11–13, 19; Appendix A.2, Run 11; Appendix C.3 |
| 12 | RC2-50-R3 | Real 2: new values, full step trace | 50 ms | Figures 4, 14–16, 20; Appendix A.2, Run 12; Appendix C.4 |

The animation setting is a delay between displayed instructions, not the CPU clock. The code uses it in `setTimeout`, separately from cycle accounting, so it cannot change any cycle count; larger values only make the animation slower. The different totals within a case come from random cache and branch outcomes.

Real Case 1's fixed list is 68.75% dark, close to the 70% label. Real Case 2 is generated when the page loads. Runs 4, 8 and 12 repeat a distribution, not exactly the same input image; all three still have identical instruction costs because each has eight bright pixels.

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
| Instruction executions per run | Best (Runs 1, 5, 9) | Worst (Runs 2, 6, 10) | Real 1 (Runs 3, 7, 11) | Real 2 (Runs 4, 8, 12) |
|---|---|---|---|---|
| Each setup instruction: 0x00, 0x04 | 1 | 1 | 1 | 1 |
| Each of 0x08, 0x0C, 0x10 | 16 | 16 | 16 | 16 |
| Each of 0x14, 0x18 | 0 | 8 | 5 | 8 |
| 0x1C | 16 | 8 | 11 | 8 |
| Each of 0x20, 0x24, 0x28, 0x2C, 0x30 | 16 | 16 | 16 | 16 |
| Total executed instructions | 146 | 154 | 151 | 154 |
| Base cycles before delays | 210 | 226 | 220 | 226 |

### 1.4 Pixel paths, final state and event history

Appendix B contains all 128 inputs of Runs 1–8, their evidence basis, outputs, paths and cumulative base-cycle totals. Appendix C contains the recorded pixel events and every instruction step for Runs 9–12. For pixel `n`, the load address is `1023 + n`. After that iteration, R0 = `n`, R1 = `1024 + n`, R3 contains its input and R4 contains its output.

Every run finishes with R0 = 16 (`0x10`) and R1 = 1040 (`0x410`). The execution summary shows the last executed instruction, `0x30 BNE LOOP`, while Current PC shows the next position, `0x34`. The final R3/R4 pairs are 0/32 for Best, 192/184 for Worst, 140/132 for Real 1, 60/92 for Run 4, and 55/87 for Run 8. R7 is clipped in Local's screenshots; Scarlet's register screenshots and all four trace runs show `0x08` directly.

The input evidence has three levels:

- 93 inputs come from screenshot transcriptions (Runs 1–8, read directly from readable cells), and 48 more were read from the live step records of Runs 9–12.
- 48 Best Case inputs (Runs 1, 5, 9) come from the all-zero test definition; the cell text is black on black.
- Three Real Case 2 values were inferred from their outputs: Run 4 pixels 9 and 12 (6 from output 38) and Run 8 pixel 15 (8 from output 40). Run 12's Real Case 2 inputs were all recorded directly, so it adds no inference.

All pairs are mathematically consistent with the brightness rule. The three inferred pairs cannot independently establish output correctness because the same rule was used to obtain their inputs.

#### Visible pixel memory: one completed run per case

The top grid in each figure shows the input pixels; the bottom grid shows the stored outputs. Read each grid left to right, then top to bottom. Dark cells retain the simulator's low-contrast text; the numeric input/output lists are printed in Appendix C.1–C.4.

![Figure 1: Run 9 Best Case input and output pixel grids.](Figures/Run9_BC_final_pixels.png)

**Figure 1: Best Case, Run 9.** All sixteen zero inputs produce 32. The input numbers are black on black, so their values come from the case definition rather than a visual reading. The pixel table is in Appendix C.1.

![Figure 2: Run 10 Worst Case input and output pixel grids.](Figures/Run10_WC_final_pixels.png)

**Figure 2: Worst Case, Run 10.** Alternating inputs 64 and 192 become 96 and 184, respectively. The pixel table is in Appendix C.2.

![Figure 3: Run 11 Real Case 1 input and output pixel grids.](Figures/Run11_RC1_final_pixels.png)

**Figure 3: Real Case 1, Run 11.** The mixed input takes both arithmetic paths; for example, the first two pixels change from 35 to 67 and from 180 to 172. The pixel table is in Appendix C.3.

![Figure 4: Run 12 Real Case 2 input and output pixel grids.](Figures/Run12_RC2_final_pixels.png)

**Figure 4: Real Case 2, Run 12.** The first eight bright pixels take subtraction and the last eight dark pixels take addition. The first pixel changes from 232 to 224; pixel 9 changes from 1 to 33. The pixel table is in Appendix C.4.

For an actual timing history, define `M_i = 1` for a cache miss on pixel i and `B_i = 1` for an incorrect brightness prediction. Then:

```text
Cycles for pixel i = base_path_cycles_i + 47 × M_i + 15 × B_i
Running actual cycles after pixel n = 2 + sum(cycles for pixels 1 through n)
```

Runs 1–8 provide the sums of `M_i` and `B_i` but not their positions. Runs 9–12 record every position. Run 1 has no incorrect predictions, so all its `B_i` values are zero; even there, its three cache-miss positions remain unknown. Assigning delays to specific pixels in Runs 1–8 would fabricate an event history; Runs 9–12 were recorded specifically to avoid that.

Only observed events are included in the recorded timing histories. Expected values or reconstructed paths cannot establish the missing event positions in Runs 1–8.

### 1.5 Recorded step traces (Runs 9–12)

Each traced run was recorded by advancing the simulator one instruction at a time through its own STEP behavior and recording the state after every step: executed PC, cycle interval, running total, registers, pixel counter, and the cache/branch message. Appendix C prints every executed PC, next PC, cycle increment, running total and cache/branch event. Each run also has six checkpoint screenshots in Appendix A.2: setup, first load, first branch decision, pixel 1 done, pixel 8 done, and final. Setup, pixel-1 and final-state panels are embedded below. The traces come straight from the simulator's stepping; no values were reconstructed:

<!-- table:trace-runs -->
| Run | Run ID | Total cycles | Base cycles | Steps recorded | Cache misses (positions of 16) | Brightness mispredictions (positions) |
|---|---|---|---|---|---|---|
| 9 | BC-50-R3 | 366 | 210 | 146 | 3 (pixels 7, 13, 14) | 1 (pixels 11) |
| 10 | WC-50-R3 | 378 | 226 | 154 | 1 (pixels 10) | 7 (pixels 2, 6, 7, 10, 11, 13, 16) |
| 11 | RC1-50-R3 | 451 | 220 | 151 | 3 (pixels 3, 5, 7) | 6 (pixels 1, 2, 12, 13, 15, 16) |
| 12 | RC2-50-R3 | 397 | 226 | 154 | 3 (pixels 4, 9, 16) | 2 (pixels 2, 13) |

The per-pixel tables and full per-instruction tables are in Appendix C. Checks applied to all four traces: each cycle increment equals the instruction's cost plus 47 for a miss or 15 for a misprediction; the per-pixel base costs sum to 13 or 15 by path; and the per-step totals reproduce the final counters exactly.

Three points stand out from the traces:

- Run 10 drew only one cache miss where the model expects about 3.2, giving the lowest Worst Case total of all: 378 against 502 and 504 in Runs 2 and 6. That single miss plus seven mispredictions account for all 152 of its stall cycles.
- Even Best Case can mispredict, as Run 9 does once. The model draws a 95% hit chance rather than reading the pixel pattern, so a wrong prediction can land anywhere.
- Event positions carry no pattern. Run 12's mispredictions (pixels 2 and 13) and its misses (pixels 4, 9 and 16) are scattered, because each outcome is drawn at random; the trace just records where the draws landed.

Together with the totals in Section 2, the traces satisfy the assignment's requirement for an instruction-by-instruction record and per-iteration events.

#### Reading the execution checkpoints

Each figure below combines intact status boxes and the register panel from one recorded screenshot, arranged vertically for readability. **Current PC is the next instruction:** it is `0x08` after setup and after the first loop iteration, then `0x34` when all pixels are complete. Returning to `0x08` is expected loop behavior. The full PC sequence, including intermediate loads and branches, is printed in Appendix C; Appendix A.2 also shows the first-load and first-branch screenshots. Any register-panel clipping is inherited from the original capture.

#### Best Case checkpoints (Run 9)

![Figure 5: Run 9 after setup, with PC 0x08, R0 zero and R1 0x400.](Figures/Run9_BC_setup_state.png)

**Figure 5: Run 9 after setup.** R0 is zero and R1 points to the first pixel (`0x400`); no pixels or branch predictions have been counted.

![Figure 6: Run 9 after pixel 1, with R0 0x01, R1 0x401 and output R4 0x20.](Figures/Run9_BC_pixel1_done_state.png)

**Figure 6: Run 9, pixel 1 complete.** R3 = `0x00` becomes R4 = `0x20` (32). The pointer advances to `0x401` and PC returns to `0x08`.

![Figure 7: Run 9 final state, PC 0x34, 16 pixels, 31 of 32 branches correct and 156 stall cycles.](Figures/Run9_BC_final_state.png)

**Figure 7: Run 9 complete.** R0 = `0x10` and R1 = `0x410`; the counters show 31/32 correct branches and 156 stall cycles. Figure 17 shows the total of 366 cycles.

#### Worst Case checkpoints (Run 10)

![Figure 8: Run 10 after setup, with PC 0x08 and no pixels processed.](Figures/Run10_WC_setup_state.png)

**Figure 8: Run 10 after setup.** The Worst Case starts with the same counter and pointer state as Best Case.

![Figure 9: Run 10 after pixel 1, showing input R3 0x40 and output R4 0x60.](Figures/Run10_WC_pixel1_done_state.png)

**Figure 9: Run 10, pixel 1 complete.** Input 64 (`0x40`) becomes 96 (`0x60`); both branch predictions so far are correct and no stall cycles have accumulated.

![Figure 10: Run 10 final state, PC 0x34, 16 pixels, 25 of 32 branches correct and 152 stall cycles.](Figures/Run10_WC_final_state.png)

**Figure 10: Run 10 complete.** The last bright pixel changes from `0xC0` to `0xB8` (192 to 184). Seven wrong predictions leave 25/32 correct; Figure 18 shows the single cache miss and 378-cycle total.

#### Real Case 1 checkpoints (Run 11)

![Figure 11: Run 11 after setup, with PC 0x08, R0 zero and R1 0x400.](Figures/Run11_RC1_setup_state.png)

**Figure 11: Run 11 after setup.** The pointer is ready for the first indoor-photo pixel, with all event counters at zero.

![Figure 12: Run 11 after pixel 1, showing R3 0x23, R4 0x43, 1 of 2 branches correct and 15 stalls.](Figures/Run11_RC1_pixel1_done_state.png)

**Figure 12: Run 11, pixel 1 complete.** Input 35 becomes 67 (`0x23` → `0x43`). The 1/2 branch counter and 15 stall cycles show the first brightness misprediction; the recorded load was a hit (Appendix C.3).

![Figure 13: Run 11 final state, PC 0x34, 16 pixels, 26 of 32 branches correct and 231 stalls.](Figures/Run11_RC1_final_state.png)

**Figure 13: Run 11 complete.** The final input/output registers contain 140 and 132 (`0x8C` → `0x84`). Figure 19 shows the matching 451-cycle total and cache counters.

#### Real Case 2 checkpoints (Run 12)

![Figure 14: Run 12 after setup, with PC 0x08 and zero processed pixels.](Figures/Run12_RC2_setup_state.png)

**Figure 14: Run 12 after setup.** The clustered case starts at pixel address `0x400`, before any pixel load or branch decision.

![Figure 15: Run 12 after pixel 1, showing input R3 0xE8 and output R4 0xE0.](Figures/Run12_RC2_pixel1_done_state.png)

**Figure 15: Run 12, pixel 1 complete.** The first bright input changes from 232 to 224 (`0xE8` → `0xE0`). R0 advances to one, R1 to `0x401`, and PC returns to `0x08`.

![Figure 16: Run 12 final state, PC 0x34, 16 pixels, 30 of 32 branches correct and 171 stalls.](Figures/Run12_RC2_final_state.png)

**Figure 16: Run 12 complete.** The last dark input changes from 92 to 124 (`0x5C` → `0x7C`). The final counters show 30/32 correct branches and 171 stalls; Figure 20 shows the 397-cycle total.

### 1.6 What the simulator models

Each load has an approximately 80% random chance of a cache hit. The model does not simulate cache lines, associativity, capacity replacement, prefetching or memory bandwidth. It cannot demonstrate a compulsory first miss or a miss caused by a particular image boundary.

For `BLT`, correct-prediction probabilities are 95% for Best, 50% for Worst, and 80% for both real cases. These probabilities are selected by the case label; they do not come from a predictor learning the values. `BNE` is always counted as correct, including its final not-taken decision. Each run therefore has 16 brightness predictions plus 16 correct loop predictions. The unconditional `JMP` is not included in that metric.

These details explain why Run 5 has a wrong prediction despite all-zero input, and why clustering alone cannot explain the exact branch outcomes. The code also contains no register allocator, out-of-order scheduler or measured memory-bandwidth model. Broader scenario descriptions provide context, not additional observations from this simulator.

## 2. Performance data and bottlenecks

### 2.1 All recorded results

CPP is calculated from total cycles divided by 16. Displayed figures are rounded only after calculation. Spill count is **0 from code inspection** in all twelve runs; there is no measured spill counter. Runs 9–12 are the traces of Section 1.5.

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
| 9 | Best | 366 | 22.88 | 13 | 3 | 31 | 32 | 156 |
| 10 | Worst | 378 | 23.63 | 15 | 1 | 25 | 32 | 152 |
| 11 | Real 1 | 451 | 28.19 | 13 | 3 | 26 | 32 | 231 |
| 12 | Real 2 | 397 | 24.81 | 13 | 3 | 30 | 32 | 171 |

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
| 9 | 81.3% | 18.8% | 96.9% | 3.1% | 93.8% |
| 10 | 93.8% | 6.3% | 78.1% | 21.9% | 56.3% |
| 11 | 81.3% | 18.8% | 81.3% | 18.8% | 62.5% |
| 12 | 81.3% | 18.8% | 93.8% | 6.3% | 87.5% |

For example, Run 2 has nine wrong predictions: overall error is `9/32 = 28.125%`, while brightness-only error is `9/16 = 56.25%`. Rounded complementary rates can add to 100.1%; the counts are the calculation source.

#### Final metrics visible in the simulator

The following crops show the final metrics for the same four traced runs pictured above. They are **individual run results**, not the three-run means in Section 2.3 or the 40-run optimization means in Section 3. The estimated full-image value displayed in each screenshot belongs to that individual run.

![Figure 17: Run 9 final metrics showing 366 cycles, 22.88 CPP, 13 cache hits, 3 misses and 31 of 32 correct branches.](Figures/Run9_BC_final_metrics.png)

**Figure 17: Best Case, Run 9.** 366 cycles; 13 hits and 3 misses; 31/32 correct branches; 156 stall cycles.

![Figure 18: Run 10 final metrics showing 378 cycles, 23.63 CPP, 15 cache hits, 1 miss and 25 of 32 correct branches.](Figures/Run10_WC_final_metrics.png)

**Figure 18: Worst Case, Run 10.** 378 cycles; 15 hits and 1 miss; 25/32 correct branches; 152 stall cycles. Its unusually small miss count explains why this run is faster than the other Worst Case runs.

![Figure 19: Run 11 final metrics showing 451 cycles, 28.19 CPP, 13 cache hits, 3 misses and 26 of 32 correct branches.](Figures/Run11_RC1_final_metrics.png)

**Figure 19: Real Case 1, Run 11.** 451 cycles; 13 hits and 3 misses; 26/32 correct branches; 231 stall cycles.

![Figure 20: Run 12 final metrics showing 397 cycles, 24.81 CPP, 13 cache hits, 3 misses and 30 of 32 correct branches.](Figures/Run12_RC2_final_metrics.png)

**Figure 20: Real Case 2, Run 12.** 397 cycles; 13 hits and 3 misses; 30/32 correct branches; 171 stall cycles.

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
| 9 | 16 | 0 | 210 | 141 | 15 | 366 |
| 10 | 8 | 8 | 226 | 47 | 105 | 378 |
| 11 | 11 | 5 | 220 | 141 | 90 | 451 |
| 12 | 8 | 8 | 226 | 141 | 30 | 397 |

Across all twelve runs, `2,646 base + 1,786 cache + 675 branch = 5,107 cycles`. Cache misses account for about 72.6% of the 2,461 stall cycles in total, and for the largest single delay in eleven of the twelve runs. The exception is Run 10, whose single cache miss left its seven branch mispredictions as the larger delay. This identifies the two recorded sources of waiting rather than proving that memory bandwidth limits a real server.

The base load and store costs are 48 cycles each per run. Misses add another 47–188 cycles to the load instruction depending on the run. Brightness prediction mistakes add 0–135 cycles to `BLT`. These are the main instruction-level costs worth investigating.

### 2.3 Repeated runs and averages

Each mean below uses the three recorded runs of a case. Pooled rates use the combined counts: 48 loads and 96 branch predictions per case. They are descriptive results from a small sample, not reliable population averages or a production workload mix.

<!-- table:averages -->
| Case | Run totals | Spread | Mean cycles | Mean CPP | Pooled cache hit rate | Pooled branch accuracy | Pooled brightness-only accuracy |
|---|---|---|---|---|---|---|---|
| Best | 351, 413, 366 | 62 | 376.7 | 23.54 | 79.2% | 97.9% | 95.8% |
| Worst | 502, 504, 378 | 126 | 461.3 | 28.83 | 83.3% | 77.1% | 54.2% |
| Real 1 | 406, 436, 451 | 45 | 431.0 | 26.94 | 81.3% | 85.4% | 70.8% |
| Real 2 | 444, 459, 397 | 62 | 433.3 | 27.08 | 77.1% | 92.7% | 85.4% |

Run 10's rare single miss explains part of Worst Case's 126-cycle spread; its two siblings recorded three and four misses. The base instruction cycles are identical within every case (210 / 226 / 220 / 226), because they depend only on the pixel pattern. Every difference therefore comes from the random delays: each additional miss adds 47 cycles and each wrong brightness prediction adds 15.

Within the three-run groups, Best recorded 10 cache misses and Worst 8, putting Worst's mean cache delay about 31 cycles lower. Its mean branch delay was 100 cycles higher, though, and its base cost 16 cycles higher; those two differences explain the 84.7-cycle gap between the means. In every run except Run 10, cache delay exceeded branch delay.

### 2.4 Assignment targets

| Target from the scenario | Combined finding |
|---|---|
| CPP < 5 | None meets it; even a delay-free all-dark baseline needs 210/16 = 13.125 CPP |
| Cache hit rate > 95% | None meets it; per-run rates are 75.0% or 81.25%, with Run 10 at 93.75% as a lucky draw |
| Overall branch accuracy > 90% | Runs 1, 3, 4, 5, 8, 9 and 12 meet it; the others do not |
| Register spills = 0 | No spill instructions are present; this is a code finding |

Falling short of a target is itself a result to explain; the arithmetic behind these numbers is checked in Section 2.2 and Appendix D. The guide's sample CPP figures, and its claims of perfect or zero prediction accuracy, are not measurements of this code.

## 3. Optimization analysis

### 3.1 Strategies tested and measured

Four changed programs were built from the original simulator, plus the unchanged baseline. All five programs ran 40 times per test case with identical inputs, and their outputs were checked every run. The section reports measured results.

<!-- table:programs -->
| Program | Change to the program | Base cycles (Best / Worst / Real 1 / Real 2) | Conditional branches per run | Brightness mispredictions |
|---|---|---|---|---|
| Baseline | Recorded program: 13/15-cycle paths | 210 / 226 / 220 / 226 | 32 (16 BLT + 16 loop) | Possible |
| Branch-free | Compute both candidates, select with `CSEL`; no `BLT`/`JMP` | 226 / 226 / 226 / 226 | 16 (loop only) | Impossible |
| Unrolled | Four-pixel straight-line block; `INC #4` loop control | 162 / 178 / 172 / 178 | 20 (16 BLT + 4 loop) | Possible |
| Loop-test | Loop tests the pointer (`CMP R1, #1040`); counter removed | 194 / 210 / 204 / 210 | 32 (16 BLT + 16 loop) | Possible |
| Combined | Unrolled block + branch-free selection | 178 / 178 / 178 / 178 | 4 (loop only) | Impossible |

Shared assumptions: instruction costs, cache randomization (80% hits, +47 per miss) and branch probabilities (95% / 50% / 80% / 80%) follow the original simulator; `CSEL` is modelled at 1 cycle like the other ALU operations; `INC R1, #4`, `INC R0, #4` and base+offset loads are assumed available as model extensions inspired by the scenario's ARM Cortex context. These forms and their costs are assumptions, not verified hardware timings. The loop-test variant eliminates the now-redundant counter register. Real Case 2 uses the Run 8 input list printed in Appendix B.8 so every program processes identical inputs. Best Case, Worst Case and Real Case 1 use the fixed lists in Appendix B.1–B.3.

Prefetching remains a calculation only, because the simulator draws hits randomly and models no cache contents or lines; Section 3.5 keeps its ceiling estimates against the measured baseline.

### 3.2 How the measurements were taken

Each variant replaces the baseline instruction program and its execution logic while retaining the simulator interface and the shared cost model. For every repeat, an automated driver initializes the chosen program, advances it instruction by instruction until completion, records its final counters and checks all 16 output pixels against the brightness rule. Each of the five programs is run 40 times for each of the four cases: `5 × 40 × 4 = 800` executions. Inputs are held constant within a case, but each execution draws new random cache and branch outcomes; repetitions across programs are not paired random trials.

Every execution satisfies `cycles = base + 47 × misses + 15 × mispredictions`, and all output checks passed. Conditional-branch counts are 32 for the baseline and loop-test, 20 for unrolled, 16 for branch-free, and 4 for combined. Appendix D.1–D.4 prints the cycle, miss and wrong-prediction counts for all 800 executions. Appendix D.5 gives the totals and standard errors needed to reproduce the summary comparisons.

These are measurements from the same teaching model as the recorded runs, not hardware benchmarks. The baseline measured here gives slightly different means than the twelve recorded runs because a 40-run sample and a 3-run sample differ, and because the pinned Real Case 2 list is one of many possible inputs.

Appendix A.3 shows a captured final state for each of the five programs. Those pictures illustrate individual executions; the measurement tables in Appendix D, rather than the sample screenshots, support the 40-run means below.

### 3.3 Measured results

<!-- table:measured -->
| Case | Baseline (N=40) | Branch-free | Unrolled | Loop-test | Combined |
|---|---|---|---|---|---|
| Best | 362.73 | 376.40 (+3.8%) | 316.45 (-12.8%) | 352.50 (-2.8%) | 342.50 (-5.6%) |
| Worst | 502.93 | 389.33 (-22.6%) | 460.25 (-8.5%) | 468.63 (-6.8%) | 329.58 (-34.5%) |
| Real 1 | 439.83 | 376.40 (-14.4%) | 390.10 (-11.3%) | 404.63 (-8.0%) | 337.80 (-23.2%) |
| Real 2 | 415.35 | 372.88 (-10.2%) | 385.53 (-7.2%) | 400.75 (-3.5%) | 335.45 (-19.2%) |

Percentages are reductions of the mean total cycles against the same-session baseline; a positive value means the program was slower. The standard error of each cell mean is about 8–15 cycles.

<!-- table:measured-ranges -->
| Case | Baseline | Branch-free | Unrolled | Loop-test | Combined |
|---|---|---|---|---|---|
| Best | 362.73 [257–554] | 376.40 [226–508] | 316.45 [192–427] | 352.50 [194–647] | 342.50 [225–554] |
| Worst | 502.93 [346–720] | 389.33 [273–508] | 460.25 [300–642] | 468.63 [285–627] | 329.58 [225–507] |
| Real 1 | 439.83 [327–637] | 376.40 [226–555] | 390.10 [264–638] | 404.63 [249–531] | 337.80 [178–507] |
| Real 2 | 415.35 [288–600] | 372.88 [226–555] | 385.53 [255–599] | 400.75 [240–614] | 335.45 [178–554] |

Why the numbers move: every run decomposes exactly into `base + 47 × misses + 15 × mispredictions`, and only the two random terms differ across programs.

- **Branch-free** raises every pixel to 14 cycles (base 226 in every case) and eliminates brightness mispredictions entirely. It wins where mispredictions were frequent (Worst: −22.6%) and loses where they were rare (Best: +3.8%), because the removed delay no longer covers the extra ALU work.
- **Unrolling** cuts loop control from four cycles per pixel to one, giving bases of 162–178. It keeps the `BLT` decisions and their mispredictions.
- **Loop-test** removes the counter instruction (bases 194–210) and keeps everything else; its savings are steady and small (−2.8% to −8.0%).
- **Combined** has the branch-free base with an unrolled loop and no brightness branches at all. For Worst Case, the mean decomposes exactly: base 226 → 178 (−48), mispredictions 8.20 → 0 (−123.0) and random misses −2.35, giving the measured −173.35.

### 3.4 Best measured strategy for each case

<!-- table:best-strategy -->
| Case | Best measured program | Mean cycles | Margin over next best | Margin over baseline |
|---|---|---|---|---|
| Best | Unrolled | 316.45 | 26.05 over combined | 46.28 (-12.8%) |
| Worst | Combined | 329.58 | 59.75 over branch-free | 173.35 (-34.5%) |
| Real 1 | Combined | 337.80 | 38.60 over branch-free | 102.03 (-23.2%) |
| Real 2 | Combined | 335.45 | 37.43 over branch-free | 79.90 (-19.2%) |

On Worst, Real 1 and Real 2, the combined program's margins (about 2.2–4.5 standard errors over the next-best program, and 4.9–11 over the baseline) support the ranking: removing brightness branches and shortening the loop together help everywhere mispredictions or bright pixels occur. Best Case is a statistical near-tie between unrolling and the combined program: the 26-cycle gap is about 1.7 standard errors, and a deterministic argument explains the convergence: unrolling saves 16 base cycles that the combined program still spends, while the combined program avoids the roughly 15 cycles of Best-Case branch delay that unrolling still pays. A real compiler would need real benchmarks to settle that pair.

### 3.5 Prefetching: still calculated, against the measured baseline

No faithful prefetch variant could be implemented, because the simulator has no cache contents to prefetch into; it only draws hits and misses at random. The table therefore keeps the two calculation cases from the earlier analysis, now anchored to the measured baseline: removing every recorded cache delay (an upper bound) and reducing misses to one per run without adding work (a sensitivity case).

<!-- table:prefetch -->
| Case | Measured baseline mean | Mean misses | Remove all cache delay | One-miss estimate |
|---|---|---|---|---|
| Best | 362.73 | 3.05 | 219.38 | 266.38 |
| Worst | 502.93 | 3.275 | 349.01 | 396.01 |
| Real 1 | 439.83 | 3.6 | 270.63 | 317.63 |
| Real 2 | 415.35 | 3.175 | 266.13 | 313.13 |

Even the one-miss estimate would beat the recorded baseline and the unrolled and loop-test programs on Worst Case, but it would still trail the measured branch-free (389.33) and combined (329.58) programs. The cache ceiling is what makes both kinds of delay worth attacking together. If a real prefetch implementation added instructions or failed to catch every miss, its advantage would shrink.

## 4. Extrapolation and cost impact

### 4.1 Workload assumptions

The required calculation treats an image as one 256 × 256 chunk: 65,536 pixels. It uses 2,000,000 processed images/day, one dedicated 2.4 GHz processor per modeled server, 8 W processor power, $0.12/kWh and 365 days/year. The entire daily batch is assumed to arrive together and must finish within four hours. This is a conservative batch interpretation of the stated latency deadline.

The scenario also says only 50% of uploads need adjustment. The 1,000,000-image alternative is shown separately. Actual 5–25 MB photos may contain many chunks; compressed file size alone does not determine their pixel count. Decoding, I/O, networking, other tasks and whole-server power are outside these estimates. One clock cycle is about 0.417 ns at 2.4 GHz; one instruction can take several cycles.

### 4.2 Scaling the recorded results

```text
Groups per image = 65,536 / 16 = 4,096
Image cycles = 16-pixel total × 4,096 = exact CPP × 65,536
```

The factor 4,096 applies to the 16-pixel total, not CPP. Each case below uses its exact three-run mean, so the individual runs' spread (Section 2.3) is not hidden. This scaling includes the small run's setup cost in each group, matching the simulator display; a single large loop might amortize setup differently, which has not been measured.

<!-- table:image-runs -->
| Case | Mean 16-pixel cycles | Estimated cycles per 256 × 256 image |
|---|---|---|
| Best | 376.7 | 1,542,827 |
| Worst | 461.3 | 1,889,621 |
| Real 1 | 431.0 | 1,765,376 |
| Real 2 | 433.3 | 1,774,933 |

### 4.3 Daily cycles and four-hour server count

Use each case's three-run mean to avoid selecting a favorable run. These four scenarios are alternatives, not four workloads to add together.

```text
Daily cycles = mean image cycles × 2,000,000
Processor seconds = daily cycles / 2,400,000,000
Servers = ceiling(processor seconds / 14,400)
```

<!-- table:scaling -->
| Case | Mean image cycles | Daily cycles | Processor seconds/day | Fraction of four-hour capacity | Whole servers |
|---|---|---|---|---|---|
| Best | 1,542,827 | 3,085,653,333,333 | 1,285.69 | 0.0893 | 1 |
| Worst | 1,889,621 | 3,779,242,666,667 | 1,574.68 | 0.1094 | 1 |
| Real 1 | 1,765,376 | 3,530,752,000,000 | 1,471.15 | 0.1022 | 1 |
| Real 2 | 1,774,933 | 3,549,866,666,667 | 1,479.11 | 0.1027 | 1 |

The simplified calculation needs one server in all cases. Even the largest individual run, Run 6, needs only 1,720.32 processor seconds, below 14,400. This is an arithmetic lower-bound model for the brightness stage, not a production capacity measurement. No workload mixture was supplied, so Real 1 serves as a worked example only; it is not claimed to be the average uploaded photograph.

### 4.4 Electricity for 24-hour operation

```text
8 W = 0.008 kW
Daily energy = 0.008 × 24 = 0.192 kWh
Daily cost = 0.192 × $0.12 = $0.02304
Annual cost = $0.02304 × 365 = $8.4096
```

This is one processor's cost at a constant 8 W. Finishing the image calculation earlier does not reduce that fixed bill.

For comparison, Real 1's calculated active time is `1,471.146667 seconds/day`. Its processing-only energy is `1,471.146667 / 3,600 × 0.008 = 0.00326921 kWh/day`, costing about **$0.00039231/day**, or **$0.14319/year**. This allocates power only to the modeled processing interval; it excludes idle power and is not the full 24-hour cost.

### 4.5 Annual savings from a 20% cycle reduction

This is the hypothetical reduction requested in the assignment, separate from the measured optimizations. For Real 1's mean:

```text
Exact mean CPP: 431 / 16 = 26.9375
Improved CPP: 26.9375 × 0.80 = 21.55
Improved daily cycles: 3,530,752,000,000 × 0.80 = 2,824,601,600,000
Improved time: 1,471.146667 × 0.80 = 1,176.917333 seconds/day
Time saved: 294.229333 seconds/day
```

<!-- table:annual-savings -->
| Case | Seconds saved/day | Annual saving if full 8 W is avoided during saved time | Annual saving at constant 8 W all day |
|---|---|---|---|
| Best | 257.14 | $0.025028 | $0 |
| Worst | 314.94 | $0.030654 | $0 |
| Real 1 | 294.23 | $0.028638 | $0 |
| Real 2 | 295.82 | $0.028793 | $0 |

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

For the 50%-of-uploads alternative, daily cycles, processing times and processing-dependent energy/savings halve. One CPP then saves 27.306667 seconds and about $0.00000728178/day. Real 1's daily baseline becomes 1,765,376,000,000 cycles and 735.573333 seconds. The integer server count remains one, and a constant 24-hour 8 W bill does **not** halve.

## 5. Requirement coverage and conclusion

The table below tracks each assignment requirement and the evidence that answers it.

| Assignment criterion | Location and evidence | Status |
|---|---|---|
| At least five experiments; all four test cases | Section 1.1: twelve complete runs, three per case | Met |
| Full cycle-by-cycle breakdown for each test case | Section 1.5 and Appendix C: every executed PC, next PC, cycle increment and running total for Runs 9–12 | Met |
| Screenshots of registers, memory state and PC progression | Figures 1–20 embed pixel grids, checkpoint states and metrics; Appendix A shows all 44 run screenshots | Met |
| Cache hit/miss and branch events each iteration | Section 1.5 and Appendix C: all 64 pixel iterations in Runs 9–12, including individual events | Met |
| Total cycles for each test case | Section 2.1 | Met |
| CPP | Section 2.1 | Met |
| Cache miss and branch misprediction rates | Section 2.1, with denominators stated | Met |
| Register spill count | Sections 1.2 and 2.1 | Addressed as zero from code; no separate counter |
| Compare at least three optimizations | Section 3.1: four measured programs plus the prefetch calculation | Met |
| Measure each strategy's improvement | Sections 3.2–3.3 and Appendix D: 800 measured runs against a same-session baseline, outputs checked | Met |
| Best strategy for each test case | Section 3.4, with the Best-Case near-tie stated | Met |
| Scale to 65,536 pixels and two million images/day | Sections 4.2–4.3 | Met as requested projections |
| Electricity at 8 W, $0.12/kWh and 24-hour operation | Section 4.4 | Met |
| Server count for four-hour SLA | Section 4.3 | Met under stated assumptions |
| Annual savings for 20% cycle reduction | Section 4.5 | Met, with fixed-power and avoidable-power cases |

The six quick-guide questions are covered by Section 2.1 (collect), Sections 2.2–2.3 (explain), Section 2.2 (bottleneck), Section 3 (optimize), Section 4.2 (extrapolate) and Section 4.6 (one-CPP saving).

The combined runs exceed the minimum experiment count and show how random delays change repeated results. The recorded ranking of baseline performance across three-run means is Best (376.7), Real 1 (431.0), Real 2 (433.3), then Worst (461.3). Cache misses dominate waiting in eleven of twelve runs; the extra Worst Case cost is largely branch mistakes. The measured study answers the assignment's optimization requirement: unrolling is best for Best Case, the combined branch-free unrolled program is best for the other three cases, and branch-free selection alone only pays off when mispredictions are frequent. Prefetching remains the one strategy without a measured implementation, because the teaching model has no cache contents to prefetch.

Some limits stay on the record. All measurements come from the teaching model and its stated cost assumptions, not from hardware, and Runs 1–8 still lack individual event positions. Testing the variants with a real compiler would need different tools. None of that blocks the deliverables: Appendix C holds the complete traces for all four test cases, and Appendix D the individual measurements behind the reported means.

## 6. Course materials and evidence sources

1. **BSC104 course brief:** *CPU Instruction Execution: Image Brightness Processing*. Defines the brightness algorithm, the required test cases, the performance targets, and the workload and power assumptions.
2. **BSC104 simulator guide:** *How to Use Project 1 Simulator*. Describes the observation workflow and the one-CPP cost question.
3. **Supplied Project 1 CPU Instruction Simulator.** Determines the instruction behavior and measured counters. Sections 1.2–1.6 state its rules and limits; Section 3.1 states the assumptions behind the modified programs.
4. **Group experimental observations.** Runs 1–4 are the Local collection; Runs 5–8 are the Scarlet collection. Runs 9–12 and the 800-run optimization study were recorded for this report. Appendices A–D contain the evidence and numerical records needed to check the findings.

<!-- generated-evidence:start -->

## Appendix A: Screenshot gallery

The following 49 figures embed the full-resolution captures: 20 final-state screenshots for Runs 1–8, 24 checkpoints for Runs 9–12, and five optimization samples. Images are displayed individually at document width. Figures 1–20 in the main discussion give larger views of selected panels. Dark pixel cells and clipped register entries retain the original capture's limitations; the numeric pixel records are printed in Appendices B and C.

### A.1 Original final-state evidence: Runs 1–8

#### Run 1: Best Case, BC-50-R1

![Figure A1: Run 1, final-state capture 1.](Sources/Local/Screenshots/BC-1.png)

**Figure A1: Run 1, final-state capture 1.** BC-50-R1.

![Figure A2: Run 1, final-state capture 2.](Sources/Local/Screenshots/BC-2.png)

**Figure A2: Run 1, final-state capture 2.** BC-50-R1.

#### Run 2: Worst Case, WC-50-R1

![Figure A3: Run 2, final-state capture 1.](Sources/Local/Screenshots/WC-1.png)

**Figure A3: Run 2, final-state capture 1.** WC-50-R1.

![Figure A4: Run 2, final-state capture 2.](Sources/Local/Screenshots/WC-2.png)

**Figure A4: Run 2, final-state capture 2.** WC-50-R1.

#### Run 3: Real Case 1, RC1-50-R1

![Figure A5: Run 3, final-state capture 1.](Sources/Local/Screenshots/RC1-1.png)

**Figure A5: Run 3, final-state capture 1.** RC1-50-R1.

![Figure A6: Run 3, final-state capture 2.](Sources/Local/Screenshots/RC1-2.png)

**Figure A6: Run 3, final-state capture 2.** RC1-50-R1.

#### Run 4: Real Case 2, RC2-50-R1

![Figure A7: Run 4, final-state capture 1.](Sources/Local/Screenshots/RC2-1.png)

**Figure A7: Run 4, final-state capture 1.** RC2-50-R1.

![Figure A8: Run 4, final-state capture 2.](Sources/Local/Screenshots/RC2-2.png)

**Figure A8: Run 4, final-state capture 2.** RC2-50-R1.

#### Run 5: Best Case, BC-500-R2

![Figure A9: Run 5, final-state capture 1.](Sources/Scarlet/Screenshots/BC-R2-1.png)

**Figure A9: Run 5, final-state capture 1.** BC-500-R2.

![Figure A10: Run 5, final-state capture 2.](Sources/Scarlet/Screenshots/BC-R2-2.png)

**Figure A10: Run 5, final-state capture 2.** BC-500-R2.

![Figure A11: Run 5, final-state capture 3.](Sources/Scarlet/Screenshots/BC-R2-3.png)

**Figure A11: Run 5, final-state capture 3.** BC-500-R2.

#### Run 6: Worst Case, WC-500-R2

![Figure A12: Run 6, final-state capture 1.](Sources/Scarlet/Screenshots/WC-R2-1.png)

**Figure A12: Run 6, final-state capture 1.** WC-500-R2.

![Figure A13: Run 6, final-state capture 2.](Sources/Scarlet/Screenshots/WC-R2-2.png)

**Figure A13: Run 6, final-state capture 2.** WC-500-R2.

![Figure A14: Run 6, final-state capture 3.](Sources/Scarlet/Screenshots/WC-R2-3.png)

**Figure A14: Run 6, final-state capture 3.** WC-500-R2.

#### Run 7: Real Case 1, RC1-500-R2

![Figure A15: Run 7, final-state capture 1.](Sources/Scarlet/Screenshots/RC1-R2-1.png)

**Figure A15: Run 7, final-state capture 1.** RC1-500-R2.

![Figure A16: Run 7, final-state capture 2.](Sources/Scarlet/Screenshots/RC1-R2-2.png)

**Figure A16: Run 7, final-state capture 2.** RC1-500-R2.

![Figure A17: Run 7, final-state capture 3.](Sources/Scarlet/Screenshots/RC1-R2-3.png)

**Figure A17: Run 7, final-state capture 3.** RC1-500-R2.

#### Run 8: Real Case 2, RC2-500-R2

![Figure A18: Run 8, final-state capture 1.](Sources/Scarlet/Screenshots/RC2-R2-1.png)

**Figure A18: Run 8, final-state capture 1.** RC2-500-R2.

![Figure A19: Run 8, final-state capture 2.](Sources/Scarlet/Screenshots/RC2-R2-2.png)

**Figure A19: Run 8, final-state capture 2.** RC2-500-R2.

![Figure A20: Run 8, final-state capture 3.](Sources/Scarlet/Screenshots/RC2-R2-3.png)

**Figure A20: Run 8, final-state capture 3.** RC2-500-R2.

### A.2 Complete checkpoint sequences: Runs 9–12

Each six-image sequence belongs to one experiment. The setup capture follows the two initialization instructions; the next PC is 0x08. The corresponding full instruction sequences are in Appendix C.

#### Run 9: Best Case, BC-50-R3

![Figure A21: Run 9, after setup.](Traces/Run9_BC_01_setup.png)

**Figure A21: Run 9, after setup.** BC-50-R3.

![Figure A22: Run 9, first load.](Traces/Run9_BC_02_first_load.png)

**Figure A22: Run 9, first load.** BC-50-R3.

![Figure A23: Run 9, first branch.](Traces/Run9_BC_03_first_branch.png)

**Figure A23: Run 9, first branch.** BC-50-R3.

![Figure A24: Run 9, pixel 1 complete.](Traces/Run9_BC_04_pixel1_done.png)

**Figure A24: Run 9, pixel 1 complete.** BC-50-R3.

![Figure A25: Run 9, pixel 8 complete.](Traces/Run9_BC_05_pixel8_done.png)

**Figure A25: Run 9, pixel 8 complete.** BC-50-R3.

![Figure A26: Run 9, final state.](Traces/Run9_BC_06_final.png)

**Figure A26: Run 9, final state.** BC-50-R3.

#### Run 10: Worst Case, WC-50-R3

![Figure A27: Run 10, after setup.](Traces/Run10_WC_01_setup.png)

**Figure A27: Run 10, after setup.** WC-50-R3.

![Figure A28: Run 10, first load.](Traces/Run10_WC_02_first_load.png)

**Figure A28: Run 10, first load.** WC-50-R3.

![Figure A29: Run 10, first branch.](Traces/Run10_WC_03_first_branch.png)

**Figure A29: Run 10, first branch.** WC-50-R3.

![Figure A30: Run 10, pixel 1 complete.](Traces/Run10_WC_04_pixel1_done.png)

**Figure A30: Run 10, pixel 1 complete.** WC-50-R3.

![Figure A31: Run 10, pixel 8 complete.](Traces/Run10_WC_05_pixel8_done.png)

**Figure A31: Run 10, pixel 8 complete.** WC-50-R3.

![Figure A32: Run 10, final state.](Traces/Run10_WC_06_final.png)

**Figure A32: Run 10, final state.** WC-50-R3.

#### Run 11: Real Case 1, RC1-50-R3

![Figure A33: Run 11, after setup.](Traces/Run11_RC1_01_setup.png)

**Figure A33: Run 11, after setup.** RC1-50-R3.

![Figure A34: Run 11, first load.](Traces/Run11_RC1_02_first_load.png)

**Figure A34: Run 11, first load.** RC1-50-R3.

![Figure A35: Run 11, first branch.](Traces/Run11_RC1_03_first_branch.png)

**Figure A35: Run 11, first branch.** RC1-50-R3.

![Figure A36: Run 11, pixel 1 complete.](Traces/Run11_RC1_04_pixel1_done.png)

**Figure A36: Run 11, pixel 1 complete.** RC1-50-R3.

![Figure A37: Run 11, pixel 8 complete.](Traces/Run11_RC1_05_pixel8_done.png)

**Figure A37: Run 11, pixel 8 complete.** RC1-50-R3.

![Figure A38: Run 11, final state.](Traces/Run11_RC1_06_final.png)

**Figure A38: Run 11, final state.** RC1-50-R3.

#### Run 12: Real Case 2, RC2-50-R3

![Figure A39: Run 12, after setup.](Traces/Run12_RC2_01_setup.png)

**Figure A39: Run 12, after setup.** RC2-50-R3.

![Figure A40: Run 12, first load.](Traces/Run12_RC2_02_first_load.png)

**Figure A40: Run 12, first load.** RC2-50-R3.

![Figure A41: Run 12, first branch.](Traces/Run12_RC2_03_first_branch.png)

**Figure A41: Run 12, first branch.** RC2-50-R3.

![Figure A42: Run 12, pixel 1 complete.](Traces/Run12_RC2_04_pixel1_done.png)

**Figure A42: Run 12, pixel 1 complete.** RC2-50-R3.

![Figure A43: Run 12, pixel 8 complete.](Traces/Run12_RC2_05_pixel8_done.png)

**Figure A43: Run 12, pixel 8 complete.** RC2-50-R3.

![Figure A44: Run 12, final state.](Traces/Run12_RC2_06_final.png)

**Figure A44: Run 12, final state.** RC2-50-R3.

### A.3 Optimization sample screenshots

These five images show individual executions from the optimization study, separate from Runs 1–12. Their displayed values are not the 40-run means. Appendix D contains the measurements used to calculate those means.

![Figure A45: Baseline sample final state.](Optimizations/baseline_final_state.png)

**Figure A45: Baseline sample final state.** One individual execution; the averages are in Appendix D.

![Figure A46: Branch-free sample final state.](Optimizations/branchfree_final_state.png)

**Figure A46: Branch-free sample final state.** One individual execution; the averages are in Appendix D.

![Figure A47: Unrolled sample final state.](Optimizations/unrolled_final_state.png)

**Figure A47: Unrolled sample final state.** One individual execution; the averages are in Appendix D.

![Figure A48: Loop-test sample final state.](Optimizations/looptest_final_state.png)

**Figure A48: Loop-test sample final state.** One individual execution; the averages are in Appendix D.

![Figure A49: Combined sample final state.](Optimizations/combined_final_state.png)

**Figure A49: Combined sample final state.** One individual execution; the averages are in Appendix D.

## Appendix B: Reconstructed pixel paths for Runs 1–8

These tables contain all 128 input/output pairs for Runs 1–8. They reconstruct the instruction paths from the pixel values; they are not recorded timing histories. Running base totals include the two setup cycles and exclude all random delays.

**Input basis:** read = transcribed from a readable screenshot; definition = zero input specified by Best Case; inferred = obtained from the output using the brightness rule. An inferred input cannot independently verify the same output.

**Paths:** Dark = 08 → 0C → 10 → 1C → 20 → 24 → 28 → 2C → 30 (13 cycles); Bright = 08 → 0C → 10 → 14 → 18 → 20 → 24 → 28 → 2C → 30 (15 cycles). Addresses are hexadecimal. Both return to 08 after pixels 1–15 and finish at 34 after pixel 16. For pixel n, the load address is 1023 + n; after the iteration R0 = n, R1 = 1024 + n, R3 contains the input, and R4 contains the output.

### B.1 Run 1: BC-50-R1

<!-- table:pixel-paths-1 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 0 | definition | 32 | Dark | 13 | 15 |
| 2 | 0 | definition | 32 | Dark | 13 | 28 |
| 3 | 0 | definition | 32 | Dark | 13 | 41 |
| 4 | 0 | definition | 32 | Dark | 13 | 54 |
| 5 | 0 | definition | 32 | Dark | 13 | 67 |
| 6 | 0 | definition | 32 | Dark | 13 | 80 |
| 7 | 0 | definition | 32 | Dark | 13 | 93 |
| 8 | 0 | definition | 32 | Dark | 13 | 106 |
| 9 | 0 | definition | 32 | Dark | 13 | 119 |
| 10 | 0 | definition | 32 | Dark | 13 | 132 |
| 11 | 0 | definition | 32 | Dark | 13 | 145 |
| 12 | 0 | definition | 32 | Dark | 13 | 158 |
| 13 | 0 | definition | 32 | Dark | 13 | 171 |
| 14 | 0 | definition | 32 | Dark | 13 | 184 |
| 15 | 0 | definition | 32 | Dark | 13 | 197 |
| 16 | 0 | definition | 32 | Dark | 13 | 210 |

Reconciliation: `210 + 3 × 47 + 0 × 15 = 351 cycles`. Cache-miss positions were not saved. No brightness prediction was wrong.

### B.2 Run 2: WC-50-R1

<!-- table:pixel-paths-2 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 64 | read | 96 | Dark | 13 | 15 |
| 2 | 192 | read | 184 | Bright | 15 | 30 |
| 3 | 64 | read | 96 | Dark | 13 | 43 |
| 4 | 192 | read | 184 | Bright | 15 | 58 |
| 5 | 64 | read | 96 | Dark | 13 | 71 |
| 6 | 192 | read | 184 | Bright | 15 | 86 |
| 7 | 64 | read | 96 | Dark | 13 | 99 |
| 8 | 192 | read | 184 | Bright | 15 | 114 |
| 9 | 64 | read | 96 | Dark | 13 | 127 |
| 10 | 192 | read | 184 | Bright | 15 | 142 |
| 11 | 64 | read | 96 | Dark | 13 | 155 |
| 12 | 192 | read | 184 | Bright | 15 | 170 |
| 13 | 64 | read | 96 | Dark | 13 | 183 |
| 14 | 192 | read | 184 | Bright | 15 | 198 |
| 15 | 64 | read | 96 | Dark | 13 | 211 |
| 16 | 192 | read | 184 | Bright | 15 | 226 |

Reconciliation: `226 + 3 × 47 + 9 × 15 = 502 cycles`. Cache-miss and wrong-prediction positions were not saved.

### B.3 Run 3: RC1-50-R1

<!-- table:pixel-paths-3 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 35 | read | 67 | Dark | 13 | 15 |
| 2 | 180 | read | 172 | Bright | 15 | 30 |
| 3 | 42 | read | 74 | Dark | 13 | 43 |
| 4 | 60 | read | 92 | Dark | 13 | 56 |
| 5 | 210 | read | 202 | Bright | 15 | 71 |
| 6 | 88 | read | 120 | Dark | 13 | 84 |
| 7 | 50 | read | 82 | Dark | 13 | 97 |
| 8 | 115 | read | 147 | Dark | 13 | 110 |
| 9 | 230 | read | 222 | Bright | 15 | 125 |
| 10 | 45 | read | 77 | Dark | 13 | 138 |
| 11 | 72 | read | 104 | Dark | 13 | 151 |
| 12 | 195 | read | 187 | Bright | 15 | 166 |
| 13 | 30 | read | 62 | Dark | 13 | 179 |
| 14 | 95 | read | 127 | Dark | 13 | 192 |
| 15 | 80 | read | 112 | Dark | 13 | 205 |
| 16 | 140 | read | 132 | Bright | 15 | 220 |

Reconciliation: `220 + 3 × 47 + 3 × 15 = 406 cycles`. Cache-miss and wrong-prediction positions were not saved.

### B.4 Run 4: RC2-50-R1

<!-- table:pixel-paths-4 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 236 | read | 228 | Bright | 15 | 17 |
| 2 | 209 | read | 201 | Bright | 15 | 32 |
| 3 | 228 | read | 220 | Bright | 15 | 47 |
| 4 | 200 | read | 192 | Bright | 15 | 62 |
| 5 | 217 | read | 209 | Bright | 15 | 77 |
| 6 | 222 | read | 214 | Bright | 15 | 92 |
| 7 | 238 | read | 230 | Bright | 15 | 107 |
| 8 | 228 | read | 220 | Bright | 15 | 122 |
| 9 | 6 | inferred | 38 | Dark | 13 | 135 |
| 10 | 78 | read | 110 | Dark | 13 | 148 |
| 11 | 56 | read | 88 | Dark | 13 | 161 |
| 12 | 6 | inferred | 38 | Dark | 13 | 174 |
| 13 | 47 | read | 79 | Dark | 13 | 187 |
| 14 | 11 | read | 43 | Dark | 13 | 200 |
| 15 | 25 | read | 57 | Dark | 13 | 213 |
| 16 | 60 | read | 92 | Dark | 13 | 226 |

Reconciliation: `226 + 4 × 47 + 2 × 15 = 444 cycles`. Cache-miss and wrong-prediction positions were not saved.

### B.5 Run 5: BC-500-R2

<!-- table:pixel-paths-5 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 0 | definition | 32 | Dark | 13 | 15 |
| 2 | 0 | definition | 32 | Dark | 13 | 28 |
| 3 | 0 | definition | 32 | Dark | 13 | 41 |
| 4 | 0 | definition | 32 | Dark | 13 | 54 |
| 5 | 0 | definition | 32 | Dark | 13 | 67 |
| 6 | 0 | definition | 32 | Dark | 13 | 80 |
| 7 | 0 | definition | 32 | Dark | 13 | 93 |
| 8 | 0 | definition | 32 | Dark | 13 | 106 |
| 9 | 0 | definition | 32 | Dark | 13 | 119 |
| 10 | 0 | definition | 32 | Dark | 13 | 132 |
| 11 | 0 | definition | 32 | Dark | 13 | 145 |
| 12 | 0 | definition | 32 | Dark | 13 | 158 |
| 13 | 0 | definition | 32 | Dark | 13 | 171 |
| 14 | 0 | definition | 32 | Dark | 13 | 184 |
| 15 | 0 | definition | 32 | Dark | 13 | 197 |
| 16 | 0 | definition | 32 | Dark | 13 | 210 |

Reconciliation: `210 + 4 × 47 + 1 × 15 = 413 cycles`. Cache-miss and wrong-prediction positions were not saved.

### B.6 Run 6: WC-500-R2

<!-- table:pixel-paths-6 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 64 | read | 96 | Dark | 13 | 15 |
| 2 | 192 | read | 184 | Bright | 15 | 30 |
| 3 | 64 | read | 96 | Dark | 13 | 43 |
| 4 | 192 | read | 184 | Bright | 15 | 58 |
| 5 | 64 | read | 96 | Dark | 13 | 71 |
| 6 | 192 | read | 184 | Bright | 15 | 86 |
| 7 | 64 | read | 96 | Dark | 13 | 99 |
| 8 | 192 | read | 184 | Bright | 15 | 114 |
| 9 | 64 | read | 96 | Dark | 13 | 127 |
| 10 | 192 | read | 184 | Bright | 15 | 142 |
| 11 | 64 | read | 96 | Dark | 13 | 155 |
| 12 | 192 | read | 184 | Bright | 15 | 170 |
| 13 | 64 | read | 96 | Dark | 13 | 183 |
| 14 | 192 | read | 184 | Bright | 15 | 198 |
| 15 | 64 | read | 96 | Dark | 13 | 211 |
| 16 | 192 | read | 184 | Bright | 15 | 226 |

Reconciliation: `226 + 4 × 47 + 6 × 15 = 504 cycles`. Cache-miss and wrong-prediction positions were not saved.

### B.7 Run 7: RC1-500-R2

<!-- table:pixel-paths-7 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 35 | read | 67 | Dark | 13 | 15 |
| 2 | 180 | read | 172 | Bright | 15 | 30 |
| 3 | 42 | read | 74 | Dark | 13 | 43 |
| 4 | 60 | read | 92 | Dark | 13 | 56 |
| 5 | 210 | read | 202 | Bright | 15 | 71 |
| 6 | 88 | read | 120 | Dark | 13 | 84 |
| 7 | 50 | read | 82 | Dark | 13 | 97 |
| 8 | 115 | read | 147 | Dark | 13 | 110 |
| 9 | 230 | read | 222 | Bright | 15 | 125 |
| 10 | 45 | read | 77 | Dark | 13 | 138 |
| 11 | 72 | read | 104 | Dark | 13 | 151 |
| 12 | 195 | read | 187 | Bright | 15 | 166 |
| 13 | 30 | read | 62 | Dark | 13 | 179 |
| 14 | 95 | read | 127 | Dark | 13 | 192 |
| 15 | 80 | read | 112 | Dark | 13 | 205 |
| 16 | 140 | read | 132 | Bright | 15 | 220 |

Reconciliation: `220 + 3 × 47 + 5 × 15 = 436 cycles`. Cache-miss and wrong-prediction positions were not saved.

### B.8 Run 8: RC2-500-R2

<!-- table:pixel-paths-8 -->
| Pixel | Input | Basis | Output | Path | Base cycles | Running base |
|---|---|---|---|---|---|---|
| 1 | 215 | read | 207 | Bright | 15 | 17 |
| 2 | 210 | read | 202 | Bright | 15 | 32 |
| 3 | 254 | read | 246 | Bright | 15 | 47 |
| 4 | 221 | read | 213 | Bright | 15 | 62 |
| 5 | 231 | read | 223 | Bright | 15 | 77 |
| 6 | 244 | read | 236 | Bright | 15 | 92 |
| 7 | 220 | read | 212 | Bright | 15 | 107 |
| 8 | 236 | read | 228 | Bright | 15 | 122 |
| 9 | 39 | read | 71 | Dark | 13 | 135 |
| 10 | 27 | read | 59 | Dark | 13 | 148 |
| 11 | 41 | read | 73 | Dark | 13 | 161 |
| 12 | 71 | read | 103 | Dark | 13 | 174 |
| 13 | 80 | read | 112 | Dark | 13 | 187 |
| 14 | 92 | read | 124 | Dark | 13 | 200 |
| 15 | 8 | inferred | 40 | Dark | 13 | 213 |
| 16 | 55 | read | 87 | Dark | 13 | 226 |

Reconciliation: `226 + 4 × 47 + 3 × 15 = 459 cycles`. Cache-miss and wrong-prediction positions were not saved.

## Appendix C: Complete recorded instruction traces for Runs 9–12

This appendix prints all 605 executed instruction steps and all 64 pixel iterations from the four traced runs. These are observed simulator records. Best Case inputs use the all-zero case definition; the other inputs were read from the recorded state.

**How to read the tables:** the pixel table gives input, output, the load's cache outcome, the brightness branch's prediction outcome, base cycles, delay cycles and the running total after the loop check. Instruction tables give the executed PC and next PC, cycles added, running total and event. Addresses are hexadecimal; Section 1.3 maps every PC to its instruction. A step with running total T and increment d occupies counted cycles T − d + 1 through T. A dash means no cache or prediction event at that instruction. BNE is always counted as correctly predicted, including its final not-taken decision. HALT is the final next-PC position and is not charged a step or cycle.

### C.1 Run 9: BC-50-R3

**Best Case:** 146 steps, 366 cycles, 13 cache hits, 3 misses, 31/32 correct branches, and 156 stall cycles. Checkpoint images appear in Appendix A.2.

<!-- table:trace-pixels-9 -->
| Pixel | Input | Output | Cache | BLT | Base | Delay | Running |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 32 | HIT | Correct | 13 | 0 | 15 |
| 2 | 0 | 32 | HIT | Correct | 13 | 0 | 28 |
| 3 | 0 | 32 | HIT | Correct | 13 | 0 | 41 |
| 4 | 0 | 32 | HIT | Correct | 13 | 0 | 54 |
| 5 | 0 | 32 | HIT | Correct | 13 | 0 | 67 |
| 6 | 0 | 32 | HIT | Correct | 13 | 0 | 80 |
| 7 | 0 | 32 | MISS | Correct | 13 | 47 | 140 |
| 8 | 0 | 32 | HIT | Correct | 13 | 0 | 153 |
| 9 | 0 | 32 | HIT | Correct | 13 | 0 | 166 |
| 10 | 0 | 32 | HIT | Correct | 13 | 0 | 179 |
| 11 | 0 | 32 | HIT | Wrong | 13 | 15 | 207 |
| 12 | 0 | 32 | HIT | Correct | 13 | 0 | 220 |
| 13 | 0 | 32 | MISS | Correct | 13 | 47 | 280 |
| 14 | 0 | 32 | MISS | Correct | 13 | 47 | 340 |
| 15 | 0 | 32 | HIT | Correct | 13 | 0 | 353 |
| 16 | 0 | 32 | HIT | Correct | 13 | 0 | 366 |

#### Run 9: recorded steps 1–40

<!-- table:trace-steps-9-1 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 1 | 0x00 | 0x04 | 1 | 1 | - |
| 2 | 0x04 | 0x08 | 1 | 2 | - |
| 3 | 0x08 | 0x0C | 3 | 5 | Cache hit |
| 4 | 0x0C | 0x10 | 1 | 6 | - |
| 5 | 0x10 | 0x1C | 1 | 7 | BLT correct |
| 6 | 0x1C | 0x20 | 1 | 8 | - |
| 7 | 0x20 | 0x24 | 3 | 11 | - |
| 8 | 0x24 | 0x28 | 1 | 12 | - |
| 9 | 0x28 | 0x2C | 1 | 13 | - |
| 10 | 0x2C | 0x30 | 1 | 14 | - |
| 11 | 0x30 | 0x08 | 1 | 15 | BNE correct |
| 12 | 0x08 | 0x0C | 3 | 18 | Cache hit |
| 13 | 0x0C | 0x10 | 1 | 19 | - |
| 14 | 0x10 | 0x1C | 1 | 20 | BLT correct |
| 15 | 0x1C | 0x20 | 1 | 21 | - |
| 16 | 0x20 | 0x24 | 3 | 24 | - |
| 17 | 0x24 | 0x28 | 1 | 25 | - |
| 18 | 0x28 | 0x2C | 1 | 26 | - |
| 19 | 0x2C | 0x30 | 1 | 27 | - |
| 20 | 0x30 | 0x08 | 1 | 28 | BNE correct |
| 21 | 0x08 | 0x0C | 3 | 31 | Cache hit |
| 22 | 0x0C | 0x10 | 1 | 32 | - |
| 23 | 0x10 | 0x1C | 1 | 33 | BLT correct |
| 24 | 0x1C | 0x20 | 1 | 34 | - |
| 25 | 0x20 | 0x24 | 3 | 37 | - |
| 26 | 0x24 | 0x28 | 1 | 38 | - |
| 27 | 0x28 | 0x2C | 1 | 39 | - |
| 28 | 0x2C | 0x30 | 1 | 40 | - |
| 29 | 0x30 | 0x08 | 1 | 41 | BNE correct |
| 30 | 0x08 | 0x0C | 3 | 44 | Cache hit |
| 31 | 0x0C | 0x10 | 1 | 45 | - |
| 32 | 0x10 | 0x1C | 1 | 46 | BLT correct |
| 33 | 0x1C | 0x20 | 1 | 47 | - |
| 34 | 0x20 | 0x24 | 3 | 50 | - |
| 35 | 0x24 | 0x28 | 1 | 51 | - |
| 36 | 0x28 | 0x2C | 1 | 52 | - |
| 37 | 0x2C | 0x30 | 1 | 53 | - |
| 38 | 0x30 | 0x08 | 1 | 54 | BNE correct |
| 39 | 0x08 | 0x0C | 3 | 57 | Cache hit |
| 40 | 0x0C | 0x10 | 1 | 58 | - |

#### Run 9: recorded steps 41–80

<!-- table:trace-steps-9-41 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 41 | 0x10 | 0x1C | 1 | 59 | BLT correct |
| 42 | 0x1C | 0x20 | 1 | 60 | - |
| 43 | 0x20 | 0x24 | 3 | 63 | - |
| 44 | 0x24 | 0x28 | 1 | 64 | - |
| 45 | 0x28 | 0x2C | 1 | 65 | - |
| 46 | 0x2C | 0x30 | 1 | 66 | - |
| 47 | 0x30 | 0x08 | 1 | 67 | BNE correct |
| 48 | 0x08 | 0x0C | 3 | 70 | Cache hit |
| 49 | 0x0C | 0x10 | 1 | 71 | - |
| 50 | 0x10 | 0x1C | 1 | 72 | BLT correct |
| 51 | 0x1C | 0x20 | 1 | 73 | - |
| 52 | 0x20 | 0x24 | 3 | 76 | - |
| 53 | 0x24 | 0x28 | 1 | 77 | - |
| 54 | 0x28 | 0x2C | 1 | 78 | - |
| 55 | 0x2C | 0x30 | 1 | 79 | - |
| 56 | 0x30 | 0x08 | 1 | 80 | BNE correct |
| 57 | 0x08 | 0x0C | 50 | 130 | Cache miss |
| 58 | 0x0C | 0x10 | 1 | 131 | - |
| 59 | 0x10 | 0x1C | 1 | 132 | BLT correct |
| 60 | 0x1C | 0x20 | 1 | 133 | - |
| 61 | 0x20 | 0x24 | 3 | 136 | - |
| 62 | 0x24 | 0x28 | 1 | 137 | - |
| 63 | 0x28 | 0x2C | 1 | 138 | - |
| 64 | 0x2C | 0x30 | 1 | 139 | - |
| 65 | 0x30 | 0x08 | 1 | 140 | BNE correct |
| 66 | 0x08 | 0x0C | 3 | 143 | Cache hit |
| 67 | 0x0C | 0x10 | 1 | 144 | - |
| 68 | 0x10 | 0x1C | 1 | 145 | BLT correct |
| 69 | 0x1C | 0x20 | 1 | 146 | - |
| 70 | 0x20 | 0x24 | 3 | 149 | - |
| 71 | 0x24 | 0x28 | 1 | 150 | - |
| 72 | 0x28 | 0x2C | 1 | 151 | - |
| 73 | 0x2C | 0x30 | 1 | 152 | - |
| 74 | 0x30 | 0x08 | 1 | 153 | BNE correct |
| 75 | 0x08 | 0x0C | 3 | 156 | Cache hit |
| 76 | 0x0C | 0x10 | 1 | 157 | - |
| 77 | 0x10 | 0x1C | 1 | 158 | BLT correct |
| 78 | 0x1C | 0x20 | 1 | 159 | - |
| 79 | 0x20 | 0x24 | 3 | 162 | - |
| 80 | 0x24 | 0x28 | 1 | 163 | - |

#### Run 9: recorded steps 81–120

<!-- table:trace-steps-9-81 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 81 | 0x28 | 0x2C | 1 | 164 | - |
| 82 | 0x2C | 0x30 | 1 | 165 | - |
| 83 | 0x30 | 0x08 | 1 | 166 | BNE correct |
| 84 | 0x08 | 0x0C | 3 | 169 | Cache hit |
| 85 | 0x0C | 0x10 | 1 | 170 | - |
| 86 | 0x10 | 0x1C | 1 | 171 | BLT correct |
| 87 | 0x1C | 0x20 | 1 | 172 | - |
| 88 | 0x20 | 0x24 | 3 | 175 | - |
| 89 | 0x24 | 0x28 | 1 | 176 | - |
| 90 | 0x28 | 0x2C | 1 | 177 | - |
| 91 | 0x2C | 0x30 | 1 | 178 | - |
| 92 | 0x30 | 0x08 | 1 | 179 | BNE correct |
| 93 | 0x08 | 0x0C | 3 | 182 | Cache hit |
| 94 | 0x0C | 0x10 | 1 | 183 | - |
| 95 | 0x10 | 0x1C | 16 | 199 | BLT wrong |
| 96 | 0x1C | 0x20 | 1 | 200 | - |
| 97 | 0x20 | 0x24 | 3 | 203 | - |
| 98 | 0x24 | 0x28 | 1 | 204 | - |
| 99 | 0x28 | 0x2C | 1 | 205 | - |
| 100 | 0x2C | 0x30 | 1 | 206 | - |
| 101 | 0x30 | 0x08 | 1 | 207 | BNE correct |
| 102 | 0x08 | 0x0C | 3 | 210 | Cache hit |
| 103 | 0x0C | 0x10 | 1 | 211 | - |
| 104 | 0x10 | 0x1C | 1 | 212 | BLT correct |
| 105 | 0x1C | 0x20 | 1 | 213 | - |
| 106 | 0x20 | 0x24 | 3 | 216 | - |
| 107 | 0x24 | 0x28 | 1 | 217 | - |
| 108 | 0x28 | 0x2C | 1 | 218 | - |
| 109 | 0x2C | 0x30 | 1 | 219 | - |
| 110 | 0x30 | 0x08 | 1 | 220 | BNE correct |
| 111 | 0x08 | 0x0C | 50 | 270 | Cache miss |
| 112 | 0x0C | 0x10 | 1 | 271 | - |
| 113 | 0x10 | 0x1C | 1 | 272 | BLT correct |
| 114 | 0x1C | 0x20 | 1 | 273 | - |
| 115 | 0x20 | 0x24 | 3 | 276 | - |
| 116 | 0x24 | 0x28 | 1 | 277 | - |
| 117 | 0x28 | 0x2C | 1 | 278 | - |
| 118 | 0x2C | 0x30 | 1 | 279 | - |
| 119 | 0x30 | 0x08 | 1 | 280 | BNE correct |
| 120 | 0x08 | 0x0C | 50 | 330 | Cache miss |

#### Run 9: recorded steps 121–146

<!-- table:trace-steps-9-121 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 121 | 0x0C | 0x10 | 1 | 331 | - |
| 122 | 0x10 | 0x1C | 1 | 332 | BLT correct |
| 123 | 0x1C | 0x20 | 1 | 333 | - |
| 124 | 0x20 | 0x24 | 3 | 336 | - |
| 125 | 0x24 | 0x28 | 1 | 337 | - |
| 126 | 0x28 | 0x2C | 1 | 338 | - |
| 127 | 0x2C | 0x30 | 1 | 339 | - |
| 128 | 0x30 | 0x08 | 1 | 340 | BNE correct |
| 129 | 0x08 | 0x0C | 3 | 343 | Cache hit |
| 130 | 0x0C | 0x10 | 1 | 344 | - |
| 131 | 0x10 | 0x1C | 1 | 345 | BLT correct |
| 132 | 0x1C | 0x20 | 1 | 346 | - |
| 133 | 0x20 | 0x24 | 3 | 349 | - |
| 134 | 0x24 | 0x28 | 1 | 350 | - |
| 135 | 0x28 | 0x2C | 1 | 351 | - |
| 136 | 0x2C | 0x30 | 1 | 352 | - |
| 137 | 0x30 | 0x08 | 1 | 353 | BNE correct |
| 138 | 0x08 | 0x0C | 3 | 356 | Cache hit |
| 139 | 0x0C | 0x10 | 1 | 357 | - |
| 140 | 0x10 | 0x1C | 1 | 358 | BLT correct |
| 141 | 0x1C | 0x20 | 1 | 359 | - |
| 142 | 0x20 | 0x24 | 3 | 362 | - |
| 143 | 0x24 | 0x28 | 1 | 363 | - |
| 144 | 0x28 | 0x2C | 1 | 364 | - |
| 145 | 0x2C | 0x30 | 1 | 365 | - |
| 146 | 0x30 | 0x34 | 1 | 366 | BNE correct |

### C.2 Run 10: WC-50-R3

**Worst Case:** 154 steps, 378 cycles, 15 cache hits, 1 misses, 25/32 correct branches, and 152 stall cycles. Checkpoint images appear in Appendix A.2.

<!-- table:trace-pixels-10 -->
| Pixel | Input | Output | Cache | BLT | Base | Delay | Running |
|---|---|---|---|---|---|---|---|
| 1 | 64 | 96 | HIT | Correct | 13 | 0 | 15 |
| 2 | 192 | 184 | HIT | Wrong | 15 | 15 | 45 |
| 3 | 64 | 96 | HIT | Correct | 13 | 0 | 58 |
| 4 | 192 | 184 | HIT | Correct | 15 | 0 | 73 |
| 5 | 64 | 96 | HIT | Correct | 13 | 0 | 86 |
| 6 | 192 | 184 | HIT | Wrong | 15 | 15 | 116 |
| 7 | 64 | 96 | HIT | Wrong | 13 | 15 | 144 |
| 8 | 192 | 184 | HIT | Correct | 15 | 0 | 159 |
| 9 | 64 | 96 | HIT | Correct | 13 | 0 | 172 |
| 10 | 192 | 184 | MISS | Wrong | 15 | 62 | 249 |
| 11 | 64 | 96 | HIT | Wrong | 13 | 15 | 277 |
| 12 | 192 | 184 | HIT | Correct | 15 | 0 | 292 |
| 13 | 64 | 96 | HIT | Wrong | 13 | 15 | 320 |
| 14 | 192 | 184 | HIT | Correct | 15 | 0 | 335 |
| 15 | 64 | 96 | HIT | Correct | 13 | 0 | 348 |
| 16 | 192 | 184 | HIT | Wrong | 15 | 15 | 378 |

#### Run 10: recorded steps 1–40

<!-- table:trace-steps-10-1 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 1 | 0x00 | 0x04 | 1 | 1 | - |
| 2 | 0x04 | 0x08 | 1 | 2 | - |
| 3 | 0x08 | 0x0C | 3 | 5 | Cache hit |
| 4 | 0x0C | 0x10 | 1 | 6 | - |
| 5 | 0x10 | 0x1C | 1 | 7 | BLT correct |
| 6 | 0x1C | 0x20 | 1 | 8 | - |
| 7 | 0x20 | 0x24 | 3 | 11 | - |
| 8 | 0x24 | 0x28 | 1 | 12 | - |
| 9 | 0x28 | 0x2C | 1 | 13 | - |
| 10 | 0x2C | 0x30 | 1 | 14 | - |
| 11 | 0x30 | 0x08 | 1 | 15 | BNE correct |
| 12 | 0x08 | 0x0C | 3 | 18 | Cache hit |
| 13 | 0x0C | 0x10 | 1 | 19 | - |
| 14 | 0x10 | 0x14 | 16 | 35 | BLT wrong |
| 15 | 0x14 | 0x18 | 1 | 36 | - |
| 16 | 0x18 | 0x20 | 2 | 38 | - |
| 17 | 0x20 | 0x24 | 3 | 41 | - |
| 18 | 0x24 | 0x28 | 1 | 42 | - |
| 19 | 0x28 | 0x2C | 1 | 43 | - |
| 20 | 0x2C | 0x30 | 1 | 44 | - |
| 21 | 0x30 | 0x08 | 1 | 45 | BNE correct |
| 22 | 0x08 | 0x0C | 3 | 48 | Cache hit |
| 23 | 0x0C | 0x10 | 1 | 49 | - |
| 24 | 0x10 | 0x1C | 1 | 50 | BLT correct |
| 25 | 0x1C | 0x20 | 1 | 51 | - |
| 26 | 0x20 | 0x24 | 3 | 54 | - |
| 27 | 0x24 | 0x28 | 1 | 55 | - |
| 28 | 0x28 | 0x2C | 1 | 56 | - |
| 29 | 0x2C | 0x30 | 1 | 57 | - |
| 30 | 0x30 | 0x08 | 1 | 58 | BNE correct |
| 31 | 0x08 | 0x0C | 3 | 61 | Cache hit |
| 32 | 0x0C | 0x10 | 1 | 62 | - |
| 33 | 0x10 | 0x14 | 1 | 63 | BLT correct |
| 34 | 0x14 | 0x18 | 1 | 64 | - |
| 35 | 0x18 | 0x20 | 2 | 66 | - |
| 36 | 0x20 | 0x24 | 3 | 69 | - |
| 37 | 0x24 | 0x28 | 1 | 70 | - |
| 38 | 0x28 | 0x2C | 1 | 71 | - |
| 39 | 0x2C | 0x30 | 1 | 72 | - |
| 40 | 0x30 | 0x08 | 1 | 73 | BNE correct |

#### Run 10: recorded steps 41–80

<!-- table:trace-steps-10-41 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 41 | 0x08 | 0x0C | 3 | 76 | Cache hit |
| 42 | 0x0C | 0x10 | 1 | 77 | - |
| 43 | 0x10 | 0x1C | 1 | 78 | BLT correct |
| 44 | 0x1C | 0x20 | 1 | 79 | - |
| 45 | 0x20 | 0x24 | 3 | 82 | - |
| 46 | 0x24 | 0x28 | 1 | 83 | - |
| 47 | 0x28 | 0x2C | 1 | 84 | - |
| 48 | 0x2C | 0x30 | 1 | 85 | - |
| 49 | 0x30 | 0x08 | 1 | 86 | BNE correct |
| 50 | 0x08 | 0x0C | 3 | 89 | Cache hit |
| 51 | 0x0C | 0x10 | 1 | 90 | - |
| 52 | 0x10 | 0x14 | 16 | 106 | BLT wrong |
| 53 | 0x14 | 0x18 | 1 | 107 | - |
| 54 | 0x18 | 0x20 | 2 | 109 | - |
| 55 | 0x20 | 0x24 | 3 | 112 | - |
| 56 | 0x24 | 0x28 | 1 | 113 | - |
| 57 | 0x28 | 0x2C | 1 | 114 | - |
| 58 | 0x2C | 0x30 | 1 | 115 | - |
| 59 | 0x30 | 0x08 | 1 | 116 | BNE correct |
| 60 | 0x08 | 0x0C | 3 | 119 | Cache hit |
| 61 | 0x0C | 0x10 | 1 | 120 | - |
| 62 | 0x10 | 0x1C | 16 | 136 | BLT wrong |
| 63 | 0x1C | 0x20 | 1 | 137 | - |
| 64 | 0x20 | 0x24 | 3 | 140 | - |
| 65 | 0x24 | 0x28 | 1 | 141 | - |
| 66 | 0x28 | 0x2C | 1 | 142 | - |
| 67 | 0x2C | 0x30 | 1 | 143 | - |
| 68 | 0x30 | 0x08 | 1 | 144 | BNE correct |
| 69 | 0x08 | 0x0C | 3 | 147 | Cache hit |
| 70 | 0x0C | 0x10 | 1 | 148 | - |
| 71 | 0x10 | 0x14 | 1 | 149 | BLT correct |
| 72 | 0x14 | 0x18 | 1 | 150 | - |
| 73 | 0x18 | 0x20 | 2 | 152 | - |
| 74 | 0x20 | 0x24 | 3 | 155 | - |
| 75 | 0x24 | 0x28 | 1 | 156 | - |
| 76 | 0x28 | 0x2C | 1 | 157 | - |
| 77 | 0x2C | 0x30 | 1 | 158 | - |
| 78 | 0x30 | 0x08 | 1 | 159 | BNE correct |
| 79 | 0x08 | 0x0C | 3 | 162 | Cache hit |
| 80 | 0x0C | 0x10 | 1 | 163 | - |

#### Run 10: recorded steps 81–120

<!-- table:trace-steps-10-81 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 81 | 0x10 | 0x1C | 1 | 164 | BLT correct |
| 82 | 0x1C | 0x20 | 1 | 165 | - |
| 83 | 0x20 | 0x24 | 3 | 168 | - |
| 84 | 0x24 | 0x28 | 1 | 169 | - |
| 85 | 0x28 | 0x2C | 1 | 170 | - |
| 86 | 0x2C | 0x30 | 1 | 171 | - |
| 87 | 0x30 | 0x08 | 1 | 172 | BNE correct |
| 88 | 0x08 | 0x0C | 50 | 222 | Cache miss |
| 89 | 0x0C | 0x10 | 1 | 223 | - |
| 90 | 0x10 | 0x14 | 16 | 239 | BLT wrong |
| 91 | 0x14 | 0x18 | 1 | 240 | - |
| 92 | 0x18 | 0x20 | 2 | 242 | - |
| 93 | 0x20 | 0x24 | 3 | 245 | - |
| 94 | 0x24 | 0x28 | 1 | 246 | - |
| 95 | 0x28 | 0x2C | 1 | 247 | - |
| 96 | 0x2C | 0x30 | 1 | 248 | - |
| 97 | 0x30 | 0x08 | 1 | 249 | BNE correct |
| 98 | 0x08 | 0x0C | 3 | 252 | Cache hit |
| 99 | 0x0C | 0x10 | 1 | 253 | - |
| 100 | 0x10 | 0x1C | 16 | 269 | BLT wrong |
| 101 | 0x1C | 0x20 | 1 | 270 | - |
| 102 | 0x20 | 0x24 | 3 | 273 | - |
| 103 | 0x24 | 0x28 | 1 | 274 | - |
| 104 | 0x28 | 0x2C | 1 | 275 | - |
| 105 | 0x2C | 0x30 | 1 | 276 | - |
| 106 | 0x30 | 0x08 | 1 | 277 | BNE correct |
| 107 | 0x08 | 0x0C | 3 | 280 | Cache hit |
| 108 | 0x0C | 0x10 | 1 | 281 | - |
| 109 | 0x10 | 0x14 | 1 | 282 | BLT correct |
| 110 | 0x14 | 0x18 | 1 | 283 | - |
| 111 | 0x18 | 0x20 | 2 | 285 | - |
| 112 | 0x20 | 0x24 | 3 | 288 | - |
| 113 | 0x24 | 0x28 | 1 | 289 | - |
| 114 | 0x28 | 0x2C | 1 | 290 | - |
| 115 | 0x2C | 0x30 | 1 | 291 | - |
| 116 | 0x30 | 0x08 | 1 | 292 | BNE correct |
| 117 | 0x08 | 0x0C | 3 | 295 | Cache hit |
| 118 | 0x0C | 0x10 | 1 | 296 | - |
| 119 | 0x10 | 0x1C | 16 | 312 | BLT wrong |
| 120 | 0x1C | 0x20 | 1 | 313 | - |

#### Run 10: recorded steps 121–154

<!-- table:trace-steps-10-121 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 121 | 0x20 | 0x24 | 3 | 316 | - |
| 122 | 0x24 | 0x28 | 1 | 317 | - |
| 123 | 0x28 | 0x2C | 1 | 318 | - |
| 124 | 0x2C | 0x30 | 1 | 319 | - |
| 125 | 0x30 | 0x08 | 1 | 320 | BNE correct |
| 126 | 0x08 | 0x0C | 3 | 323 | Cache hit |
| 127 | 0x0C | 0x10 | 1 | 324 | - |
| 128 | 0x10 | 0x14 | 1 | 325 | BLT correct |
| 129 | 0x14 | 0x18 | 1 | 326 | - |
| 130 | 0x18 | 0x20 | 2 | 328 | - |
| 131 | 0x20 | 0x24 | 3 | 331 | - |
| 132 | 0x24 | 0x28 | 1 | 332 | - |
| 133 | 0x28 | 0x2C | 1 | 333 | - |
| 134 | 0x2C | 0x30 | 1 | 334 | - |
| 135 | 0x30 | 0x08 | 1 | 335 | BNE correct |
| 136 | 0x08 | 0x0C | 3 | 338 | Cache hit |
| 137 | 0x0C | 0x10 | 1 | 339 | - |
| 138 | 0x10 | 0x1C | 1 | 340 | BLT correct |
| 139 | 0x1C | 0x20 | 1 | 341 | - |
| 140 | 0x20 | 0x24 | 3 | 344 | - |
| 141 | 0x24 | 0x28 | 1 | 345 | - |
| 142 | 0x28 | 0x2C | 1 | 346 | - |
| 143 | 0x2C | 0x30 | 1 | 347 | - |
| 144 | 0x30 | 0x08 | 1 | 348 | BNE correct |
| 145 | 0x08 | 0x0C | 3 | 351 | Cache hit |
| 146 | 0x0C | 0x10 | 1 | 352 | - |
| 147 | 0x10 | 0x14 | 16 | 368 | BLT wrong |
| 148 | 0x14 | 0x18 | 1 | 369 | - |
| 149 | 0x18 | 0x20 | 2 | 371 | - |
| 150 | 0x20 | 0x24 | 3 | 374 | - |
| 151 | 0x24 | 0x28 | 1 | 375 | - |
| 152 | 0x28 | 0x2C | 1 | 376 | - |
| 153 | 0x2C | 0x30 | 1 | 377 | - |
| 154 | 0x30 | 0x34 | 1 | 378 | BNE correct |

### C.3 Run 11: RC1-50-R3

**Real Case 1:** 151 steps, 451 cycles, 13 cache hits, 3 misses, 26/32 correct branches, and 231 stall cycles. Checkpoint images appear in Appendix A.2.

<!-- table:trace-pixels-11 -->
| Pixel | Input | Output | Cache | BLT | Base | Delay | Running |
|---|---|---|---|---|---|---|---|
| 1 | 35 | 67 | HIT | Wrong | 13 | 15 | 30 |
| 2 | 180 | 172 | HIT | Wrong | 15 | 15 | 60 |
| 3 | 42 | 74 | MISS | Correct | 13 | 47 | 120 |
| 4 | 60 | 92 | HIT | Correct | 13 | 0 | 133 |
| 5 | 210 | 202 | MISS | Correct | 15 | 47 | 195 |
| 6 | 88 | 120 | HIT | Correct | 13 | 0 | 208 |
| 7 | 50 | 82 | MISS | Correct | 13 | 47 | 268 |
| 8 | 115 | 147 | HIT | Correct | 13 | 0 | 281 |
| 9 | 230 | 222 | HIT | Correct | 15 | 0 | 296 |
| 10 | 45 | 77 | HIT | Correct | 13 | 0 | 309 |
| 11 | 72 | 104 | HIT | Correct | 13 | 0 | 322 |
| 12 | 195 | 187 | HIT | Wrong | 15 | 15 | 352 |
| 13 | 30 | 62 | HIT | Wrong | 13 | 15 | 380 |
| 14 | 95 | 127 | HIT | Correct | 13 | 0 | 393 |
| 15 | 80 | 112 | HIT | Wrong | 13 | 15 | 421 |
| 16 | 140 | 132 | HIT | Wrong | 15 | 15 | 451 |

#### Run 11: recorded steps 1–40

<!-- table:trace-steps-11-1 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 1 | 0x00 | 0x04 | 1 | 1 | - |
| 2 | 0x04 | 0x08 | 1 | 2 | - |
| 3 | 0x08 | 0x0C | 3 | 5 | Cache hit |
| 4 | 0x0C | 0x10 | 1 | 6 | - |
| 5 | 0x10 | 0x1C | 16 | 22 | BLT wrong |
| 6 | 0x1C | 0x20 | 1 | 23 | - |
| 7 | 0x20 | 0x24 | 3 | 26 | - |
| 8 | 0x24 | 0x28 | 1 | 27 | - |
| 9 | 0x28 | 0x2C | 1 | 28 | - |
| 10 | 0x2C | 0x30 | 1 | 29 | - |
| 11 | 0x30 | 0x08 | 1 | 30 | BNE correct |
| 12 | 0x08 | 0x0C | 3 | 33 | Cache hit |
| 13 | 0x0C | 0x10 | 1 | 34 | - |
| 14 | 0x10 | 0x14 | 16 | 50 | BLT wrong |
| 15 | 0x14 | 0x18 | 1 | 51 | - |
| 16 | 0x18 | 0x20 | 2 | 53 | - |
| 17 | 0x20 | 0x24 | 3 | 56 | - |
| 18 | 0x24 | 0x28 | 1 | 57 | - |
| 19 | 0x28 | 0x2C | 1 | 58 | - |
| 20 | 0x2C | 0x30 | 1 | 59 | - |
| 21 | 0x30 | 0x08 | 1 | 60 | BNE correct |
| 22 | 0x08 | 0x0C | 50 | 110 | Cache miss |
| 23 | 0x0C | 0x10 | 1 | 111 | - |
| 24 | 0x10 | 0x1C | 1 | 112 | BLT correct |
| 25 | 0x1C | 0x20 | 1 | 113 | - |
| 26 | 0x20 | 0x24 | 3 | 116 | - |
| 27 | 0x24 | 0x28 | 1 | 117 | - |
| 28 | 0x28 | 0x2C | 1 | 118 | - |
| 29 | 0x2C | 0x30 | 1 | 119 | - |
| 30 | 0x30 | 0x08 | 1 | 120 | BNE correct |
| 31 | 0x08 | 0x0C | 3 | 123 | Cache hit |
| 32 | 0x0C | 0x10 | 1 | 124 | - |
| 33 | 0x10 | 0x1C | 1 | 125 | BLT correct |
| 34 | 0x1C | 0x20 | 1 | 126 | - |
| 35 | 0x20 | 0x24 | 3 | 129 | - |
| 36 | 0x24 | 0x28 | 1 | 130 | - |
| 37 | 0x28 | 0x2C | 1 | 131 | - |
| 38 | 0x2C | 0x30 | 1 | 132 | - |
| 39 | 0x30 | 0x08 | 1 | 133 | BNE correct |
| 40 | 0x08 | 0x0C | 50 | 183 | Cache miss |

#### Run 11: recorded steps 41–80

<!-- table:trace-steps-11-41 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 41 | 0x0C | 0x10 | 1 | 184 | - |
| 42 | 0x10 | 0x14 | 1 | 185 | BLT correct |
| 43 | 0x14 | 0x18 | 1 | 186 | - |
| 44 | 0x18 | 0x20 | 2 | 188 | - |
| 45 | 0x20 | 0x24 | 3 | 191 | - |
| 46 | 0x24 | 0x28 | 1 | 192 | - |
| 47 | 0x28 | 0x2C | 1 | 193 | - |
| 48 | 0x2C | 0x30 | 1 | 194 | - |
| 49 | 0x30 | 0x08 | 1 | 195 | BNE correct |
| 50 | 0x08 | 0x0C | 3 | 198 | Cache hit |
| 51 | 0x0C | 0x10 | 1 | 199 | - |
| 52 | 0x10 | 0x1C | 1 | 200 | BLT correct |
| 53 | 0x1C | 0x20 | 1 | 201 | - |
| 54 | 0x20 | 0x24 | 3 | 204 | - |
| 55 | 0x24 | 0x28 | 1 | 205 | - |
| 56 | 0x28 | 0x2C | 1 | 206 | - |
| 57 | 0x2C | 0x30 | 1 | 207 | - |
| 58 | 0x30 | 0x08 | 1 | 208 | BNE correct |
| 59 | 0x08 | 0x0C | 50 | 258 | Cache miss |
| 60 | 0x0C | 0x10 | 1 | 259 | - |
| 61 | 0x10 | 0x1C | 1 | 260 | BLT correct |
| 62 | 0x1C | 0x20 | 1 | 261 | - |
| 63 | 0x20 | 0x24 | 3 | 264 | - |
| 64 | 0x24 | 0x28 | 1 | 265 | - |
| 65 | 0x28 | 0x2C | 1 | 266 | - |
| 66 | 0x2C | 0x30 | 1 | 267 | - |
| 67 | 0x30 | 0x08 | 1 | 268 | BNE correct |
| 68 | 0x08 | 0x0C | 3 | 271 | Cache hit |
| 69 | 0x0C | 0x10 | 1 | 272 | - |
| 70 | 0x10 | 0x1C | 1 | 273 | BLT correct |
| 71 | 0x1C | 0x20 | 1 | 274 | - |
| 72 | 0x20 | 0x24 | 3 | 277 | - |
| 73 | 0x24 | 0x28 | 1 | 278 | - |
| 74 | 0x28 | 0x2C | 1 | 279 | - |
| 75 | 0x2C | 0x30 | 1 | 280 | - |
| 76 | 0x30 | 0x08 | 1 | 281 | BNE correct |
| 77 | 0x08 | 0x0C | 3 | 284 | Cache hit |
| 78 | 0x0C | 0x10 | 1 | 285 | - |
| 79 | 0x10 | 0x14 | 1 | 286 | BLT correct |
| 80 | 0x14 | 0x18 | 1 | 287 | - |

#### Run 11: recorded steps 81–120

<!-- table:trace-steps-11-81 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 81 | 0x18 | 0x20 | 2 | 289 | - |
| 82 | 0x20 | 0x24 | 3 | 292 | - |
| 83 | 0x24 | 0x28 | 1 | 293 | - |
| 84 | 0x28 | 0x2C | 1 | 294 | - |
| 85 | 0x2C | 0x30 | 1 | 295 | - |
| 86 | 0x30 | 0x08 | 1 | 296 | BNE correct |
| 87 | 0x08 | 0x0C | 3 | 299 | Cache hit |
| 88 | 0x0C | 0x10 | 1 | 300 | - |
| 89 | 0x10 | 0x1C | 1 | 301 | BLT correct |
| 90 | 0x1C | 0x20 | 1 | 302 | - |
| 91 | 0x20 | 0x24 | 3 | 305 | - |
| 92 | 0x24 | 0x28 | 1 | 306 | - |
| 93 | 0x28 | 0x2C | 1 | 307 | - |
| 94 | 0x2C | 0x30 | 1 | 308 | - |
| 95 | 0x30 | 0x08 | 1 | 309 | BNE correct |
| 96 | 0x08 | 0x0C | 3 | 312 | Cache hit |
| 97 | 0x0C | 0x10 | 1 | 313 | - |
| 98 | 0x10 | 0x1C | 1 | 314 | BLT correct |
| 99 | 0x1C | 0x20 | 1 | 315 | - |
| 100 | 0x20 | 0x24 | 3 | 318 | - |
| 101 | 0x24 | 0x28 | 1 | 319 | - |
| 102 | 0x28 | 0x2C | 1 | 320 | - |
| 103 | 0x2C | 0x30 | 1 | 321 | - |
| 104 | 0x30 | 0x08 | 1 | 322 | BNE correct |
| 105 | 0x08 | 0x0C | 3 | 325 | Cache hit |
| 106 | 0x0C | 0x10 | 1 | 326 | - |
| 107 | 0x10 | 0x14 | 16 | 342 | BLT wrong |
| 108 | 0x14 | 0x18 | 1 | 343 | - |
| 109 | 0x18 | 0x20 | 2 | 345 | - |
| 110 | 0x20 | 0x24 | 3 | 348 | - |
| 111 | 0x24 | 0x28 | 1 | 349 | - |
| 112 | 0x28 | 0x2C | 1 | 350 | - |
| 113 | 0x2C | 0x30 | 1 | 351 | - |
| 114 | 0x30 | 0x08 | 1 | 352 | BNE correct |
| 115 | 0x08 | 0x0C | 3 | 355 | Cache hit |
| 116 | 0x0C | 0x10 | 1 | 356 | - |
| 117 | 0x10 | 0x1C | 16 | 372 | BLT wrong |
| 118 | 0x1C | 0x20 | 1 | 373 | - |
| 119 | 0x20 | 0x24 | 3 | 376 | - |
| 120 | 0x24 | 0x28 | 1 | 377 | - |

#### Run 11: recorded steps 121–151

<!-- table:trace-steps-11-121 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 121 | 0x28 | 0x2C | 1 | 378 | - |
| 122 | 0x2C | 0x30 | 1 | 379 | - |
| 123 | 0x30 | 0x08 | 1 | 380 | BNE correct |
| 124 | 0x08 | 0x0C | 3 | 383 | Cache hit |
| 125 | 0x0C | 0x10 | 1 | 384 | - |
| 126 | 0x10 | 0x1C | 1 | 385 | BLT correct |
| 127 | 0x1C | 0x20 | 1 | 386 | - |
| 128 | 0x20 | 0x24 | 3 | 389 | - |
| 129 | 0x24 | 0x28 | 1 | 390 | - |
| 130 | 0x28 | 0x2C | 1 | 391 | - |
| 131 | 0x2C | 0x30 | 1 | 392 | - |
| 132 | 0x30 | 0x08 | 1 | 393 | BNE correct |
| 133 | 0x08 | 0x0C | 3 | 396 | Cache hit |
| 134 | 0x0C | 0x10 | 1 | 397 | - |
| 135 | 0x10 | 0x1C | 16 | 413 | BLT wrong |
| 136 | 0x1C | 0x20 | 1 | 414 | - |
| 137 | 0x20 | 0x24 | 3 | 417 | - |
| 138 | 0x24 | 0x28 | 1 | 418 | - |
| 139 | 0x28 | 0x2C | 1 | 419 | - |
| 140 | 0x2C | 0x30 | 1 | 420 | - |
| 141 | 0x30 | 0x08 | 1 | 421 | BNE correct |
| 142 | 0x08 | 0x0C | 3 | 424 | Cache hit |
| 143 | 0x0C | 0x10 | 1 | 425 | - |
| 144 | 0x10 | 0x14 | 16 | 441 | BLT wrong |
| 145 | 0x14 | 0x18 | 1 | 442 | - |
| 146 | 0x18 | 0x20 | 2 | 444 | - |
| 147 | 0x20 | 0x24 | 3 | 447 | - |
| 148 | 0x24 | 0x28 | 1 | 448 | - |
| 149 | 0x28 | 0x2C | 1 | 449 | - |
| 150 | 0x2C | 0x30 | 1 | 450 | - |
| 151 | 0x30 | 0x34 | 1 | 451 | BNE correct |

### C.4 Run 12: RC2-50-R3

**Real Case 2:** 154 steps, 397 cycles, 13 cache hits, 3 misses, 30/32 correct branches, and 171 stall cycles. Checkpoint images appear in Appendix A.2.

<!-- table:trace-pixels-12 -->
| Pixel | Input | Output | Cache | BLT | Base | Delay | Running |
|---|---|---|---|---|---|---|---|
| 1 | 232 | 224 | HIT | Correct | 15 | 0 | 17 |
| 2 | 244 | 236 | HIT | Wrong | 15 | 15 | 47 |
| 3 | 227 | 219 | HIT | Correct | 15 | 0 | 62 |
| 4 | 247 | 239 | MISS | Correct | 15 | 47 | 124 |
| 5 | 211 | 203 | HIT | Correct | 15 | 0 | 139 |
| 6 | 231 | 223 | HIT | Correct | 15 | 0 | 154 |
| 7 | 254 | 246 | HIT | Correct | 15 | 0 | 169 |
| 8 | 225 | 217 | HIT | Correct | 15 | 0 | 184 |
| 9 | 1 | 33 | MISS | Correct | 13 | 47 | 244 |
| 10 | 23 | 55 | HIT | Correct | 13 | 0 | 257 |
| 11 | 16 | 48 | HIT | Correct | 13 | 0 | 270 |
| 12 | 65 | 97 | HIT | Correct | 13 | 0 | 283 |
| 13 | 56 | 88 | HIT | Wrong | 13 | 15 | 311 |
| 14 | 94 | 126 | HIT | Correct | 13 | 0 | 324 |
| 15 | 96 | 128 | HIT | Correct | 13 | 0 | 337 |
| 16 | 92 | 124 | MISS | Correct | 13 | 47 | 397 |

#### Run 12: recorded steps 1–40

<!-- table:trace-steps-12-1 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 1 | 0x00 | 0x04 | 1 | 1 | - |
| 2 | 0x04 | 0x08 | 1 | 2 | - |
| 3 | 0x08 | 0x0C | 3 | 5 | Cache hit |
| 4 | 0x0C | 0x10 | 1 | 6 | - |
| 5 | 0x10 | 0x14 | 1 | 7 | BLT correct |
| 6 | 0x14 | 0x18 | 1 | 8 | - |
| 7 | 0x18 | 0x20 | 2 | 10 | - |
| 8 | 0x20 | 0x24 | 3 | 13 | - |
| 9 | 0x24 | 0x28 | 1 | 14 | - |
| 10 | 0x28 | 0x2C | 1 | 15 | - |
| 11 | 0x2C | 0x30 | 1 | 16 | - |
| 12 | 0x30 | 0x08 | 1 | 17 | BNE correct |
| 13 | 0x08 | 0x0C | 3 | 20 | Cache hit |
| 14 | 0x0C | 0x10 | 1 | 21 | - |
| 15 | 0x10 | 0x14 | 16 | 37 | BLT wrong |
| 16 | 0x14 | 0x18 | 1 | 38 | - |
| 17 | 0x18 | 0x20 | 2 | 40 | - |
| 18 | 0x20 | 0x24 | 3 | 43 | - |
| 19 | 0x24 | 0x28 | 1 | 44 | - |
| 20 | 0x28 | 0x2C | 1 | 45 | - |
| 21 | 0x2C | 0x30 | 1 | 46 | - |
| 22 | 0x30 | 0x08 | 1 | 47 | BNE correct |
| 23 | 0x08 | 0x0C | 3 | 50 | Cache hit |
| 24 | 0x0C | 0x10 | 1 | 51 | - |
| 25 | 0x10 | 0x14 | 1 | 52 | BLT correct |
| 26 | 0x14 | 0x18 | 1 | 53 | - |
| 27 | 0x18 | 0x20 | 2 | 55 | - |
| 28 | 0x20 | 0x24 | 3 | 58 | - |
| 29 | 0x24 | 0x28 | 1 | 59 | - |
| 30 | 0x28 | 0x2C | 1 | 60 | - |
| 31 | 0x2C | 0x30 | 1 | 61 | - |
| 32 | 0x30 | 0x08 | 1 | 62 | BNE correct |
| 33 | 0x08 | 0x0C | 50 | 112 | Cache miss |
| 34 | 0x0C | 0x10 | 1 | 113 | - |
| 35 | 0x10 | 0x14 | 1 | 114 | BLT correct |
| 36 | 0x14 | 0x18 | 1 | 115 | - |
| 37 | 0x18 | 0x20 | 2 | 117 | - |
| 38 | 0x20 | 0x24 | 3 | 120 | - |
| 39 | 0x24 | 0x28 | 1 | 121 | - |
| 40 | 0x28 | 0x2C | 1 | 122 | - |

#### Run 12: recorded steps 41–80

<!-- table:trace-steps-12-41 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 41 | 0x2C | 0x30 | 1 | 123 | - |
| 42 | 0x30 | 0x08 | 1 | 124 | BNE correct |
| 43 | 0x08 | 0x0C | 3 | 127 | Cache hit |
| 44 | 0x0C | 0x10 | 1 | 128 | - |
| 45 | 0x10 | 0x14 | 1 | 129 | BLT correct |
| 46 | 0x14 | 0x18 | 1 | 130 | - |
| 47 | 0x18 | 0x20 | 2 | 132 | - |
| 48 | 0x20 | 0x24 | 3 | 135 | - |
| 49 | 0x24 | 0x28 | 1 | 136 | - |
| 50 | 0x28 | 0x2C | 1 | 137 | - |
| 51 | 0x2C | 0x30 | 1 | 138 | - |
| 52 | 0x30 | 0x08 | 1 | 139 | BNE correct |
| 53 | 0x08 | 0x0C | 3 | 142 | Cache hit |
| 54 | 0x0C | 0x10 | 1 | 143 | - |
| 55 | 0x10 | 0x14 | 1 | 144 | BLT correct |
| 56 | 0x14 | 0x18 | 1 | 145 | - |
| 57 | 0x18 | 0x20 | 2 | 147 | - |
| 58 | 0x20 | 0x24 | 3 | 150 | - |
| 59 | 0x24 | 0x28 | 1 | 151 | - |
| 60 | 0x28 | 0x2C | 1 | 152 | - |
| 61 | 0x2C | 0x30 | 1 | 153 | - |
| 62 | 0x30 | 0x08 | 1 | 154 | BNE correct |
| 63 | 0x08 | 0x0C | 3 | 157 | Cache hit |
| 64 | 0x0C | 0x10 | 1 | 158 | - |
| 65 | 0x10 | 0x14 | 1 | 159 | BLT correct |
| 66 | 0x14 | 0x18 | 1 | 160 | - |
| 67 | 0x18 | 0x20 | 2 | 162 | - |
| 68 | 0x20 | 0x24 | 3 | 165 | - |
| 69 | 0x24 | 0x28 | 1 | 166 | - |
| 70 | 0x28 | 0x2C | 1 | 167 | - |
| 71 | 0x2C | 0x30 | 1 | 168 | - |
| 72 | 0x30 | 0x08 | 1 | 169 | BNE correct |
| 73 | 0x08 | 0x0C | 3 | 172 | Cache hit |
| 74 | 0x0C | 0x10 | 1 | 173 | - |
| 75 | 0x10 | 0x14 | 1 | 174 | BLT correct |
| 76 | 0x14 | 0x18 | 1 | 175 | - |
| 77 | 0x18 | 0x20 | 2 | 177 | - |
| 78 | 0x20 | 0x24 | 3 | 180 | - |
| 79 | 0x24 | 0x28 | 1 | 181 | - |
| 80 | 0x28 | 0x2C | 1 | 182 | - |

#### Run 12: recorded steps 81–120

<!-- table:trace-steps-12-81 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 81 | 0x2C | 0x30 | 1 | 183 | - |
| 82 | 0x30 | 0x08 | 1 | 184 | BNE correct |
| 83 | 0x08 | 0x0C | 50 | 234 | Cache miss |
| 84 | 0x0C | 0x10 | 1 | 235 | - |
| 85 | 0x10 | 0x1C | 1 | 236 | BLT correct |
| 86 | 0x1C | 0x20 | 1 | 237 | - |
| 87 | 0x20 | 0x24 | 3 | 240 | - |
| 88 | 0x24 | 0x28 | 1 | 241 | - |
| 89 | 0x28 | 0x2C | 1 | 242 | - |
| 90 | 0x2C | 0x30 | 1 | 243 | - |
| 91 | 0x30 | 0x08 | 1 | 244 | BNE correct |
| 92 | 0x08 | 0x0C | 3 | 247 | Cache hit |
| 93 | 0x0C | 0x10 | 1 | 248 | - |
| 94 | 0x10 | 0x1C | 1 | 249 | BLT correct |
| 95 | 0x1C | 0x20 | 1 | 250 | - |
| 96 | 0x20 | 0x24 | 3 | 253 | - |
| 97 | 0x24 | 0x28 | 1 | 254 | - |
| 98 | 0x28 | 0x2C | 1 | 255 | - |
| 99 | 0x2C | 0x30 | 1 | 256 | - |
| 100 | 0x30 | 0x08 | 1 | 257 | BNE correct |
| 101 | 0x08 | 0x0C | 3 | 260 | Cache hit |
| 102 | 0x0C | 0x10 | 1 | 261 | - |
| 103 | 0x10 | 0x1C | 1 | 262 | BLT correct |
| 104 | 0x1C | 0x20 | 1 | 263 | - |
| 105 | 0x20 | 0x24 | 3 | 266 | - |
| 106 | 0x24 | 0x28 | 1 | 267 | - |
| 107 | 0x28 | 0x2C | 1 | 268 | - |
| 108 | 0x2C | 0x30 | 1 | 269 | - |
| 109 | 0x30 | 0x08 | 1 | 270 | BNE correct |
| 110 | 0x08 | 0x0C | 3 | 273 | Cache hit |
| 111 | 0x0C | 0x10 | 1 | 274 | - |
| 112 | 0x10 | 0x1C | 1 | 275 | BLT correct |
| 113 | 0x1C | 0x20 | 1 | 276 | - |
| 114 | 0x20 | 0x24 | 3 | 279 | - |
| 115 | 0x24 | 0x28 | 1 | 280 | - |
| 116 | 0x28 | 0x2C | 1 | 281 | - |
| 117 | 0x2C | 0x30 | 1 | 282 | - |
| 118 | 0x30 | 0x08 | 1 | 283 | BNE correct |
| 119 | 0x08 | 0x0C | 3 | 286 | Cache hit |
| 120 | 0x0C | 0x10 | 1 | 287 | - |

#### Run 12: recorded steps 121–154

<!-- table:trace-steps-12-121 -->
| Step | Executed PC | Next PC | Cycles added | Running total | Event |
|---|---|---|---|---|---|
| 121 | 0x10 | 0x1C | 16 | 303 | BLT wrong |
| 122 | 0x1C | 0x20 | 1 | 304 | - |
| 123 | 0x20 | 0x24 | 3 | 307 | - |
| 124 | 0x24 | 0x28 | 1 | 308 | - |
| 125 | 0x28 | 0x2C | 1 | 309 | - |
| 126 | 0x2C | 0x30 | 1 | 310 | - |
| 127 | 0x30 | 0x08 | 1 | 311 | BNE correct |
| 128 | 0x08 | 0x0C | 3 | 314 | Cache hit |
| 129 | 0x0C | 0x10 | 1 | 315 | - |
| 130 | 0x10 | 0x1C | 1 | 316 | BLT correct |
| 131 | 0x1C | 0x20 | 1 | 317 | - |
| 132 | 0x20 | 0x24 | 3 | 320 | - |
| 133 | 0x24 | 0x28 | 1 | 321 | - |
| 134 | 0x28 | 0x2C | 1 | 322 | - |
| 135 | 0x2C | 0x30 | 1 | 323 | - |
| 136 | 0x30 | 0x08 | 1 | 324 | BNE correct |
| 137 | 0x08 | 0x0C | 3 | 327 | Cache hit |
| 138 | 0x0C | 0x10 | 1 | 328 | - |
| 139 | 0x10 | 0x1C | 1 | 329 | BLT correct |
| 140 | 0x1C | 0x20 | 1 | 330 | - |
| 141 | 0x20 | 0x24 | 3 | 333 | - |
| 142 | 0x24 | 0x28 | 1 | 334 | - |
| 143 | 0x28 | 0x2C | 1 | 335 | - |
| 144 | 0x2C | 0x30 | 1 | 336 | - |
| 145 | 0x30 | 0x08 | 1 | 337 | BNE correct |
| 146 | 0x08 | 0x0C | 50 | 387 | Cache miss |
| 147 | 0x0C | 0x10 | 1 | 388 | - |
| 148 | 0x10 | 0x1C | 1 | 389 | BLT correct |
| 149 | 0x1C | 0x20 | 1 | 390 | - |
| 150 | 0x20 | 0x24 | 3 | 393 | - |
| 151 | 0x24 | 0x28 | 1 | 394 | - |
| 152 | 0x28 | 0x2C | 1 | 395 | - |
| 153 | 0x2C | 0x30 | 1 | 396 | - |
| 154 | 0x30 | 0x34 | 1 | 397 | BNE correct |

## Appendix D: Individual optimization measurements

These tables contain all 800 recorded optimization executions: 40 repetitions for each of five programs on each of four cases. Each cell is **cycles / cache misses / wrong brightness predictions**. The repeat number identifies an execution within that program and case; corresponding rows across programs do not share random draws. All 16 output pixels passed the brightness-rule check in every execution.

Use the base cycles and branch counts in Section 3.1 to check each result: `cycles = base + 47 × misses + 15 × wrong`. Cache hits equal 16 minus misses. Correct branch predictions equal the program's conditional-branch count minus wrong. Stall cycles equal 47 × misses + 15 × wrong. Thus the displayed triplets and program definitions also determine the remaining final counters.

### D.1 Best Case: 40 repetitions per program

<!-- table:measure-records-best -->
| Repeat | Baseline | Branch-free | Unrolled | Loop-test | Combined |
|---|---|---|---|---|---|
| 1 | 492 / 6 / 0 | 508 / 6 / 0 | 303 / 3 / 0 | 397 / 4 / 1 | 366 / 4 / 0 |
| 2 | 445 / 5 / 0 | 461 / 5 / 0 | 286 / 2 / 2 | 382 / 4 / 0 | 225 / 1 / 0 |
| 3 | 413 / 4 / 1 | 414 / 4 / 0 | 380 / 4 / 2 | 335 / 3 / 0 | 413 / 5 / 0 |
| 4 | 351 / 3 / 0 | 461 / 5 / 0 | 427 / 5 / 2 | 444 / 5 / 1 | 225 / 1 / 0 |
| 5 | 351 / 3 / 0 | 461 / 5 / 0 | 192 / 0 / 2 | 365 / 3 / 2 | 366 / 4 / 0 |
| 6 | 492 / 6 / 0 | 226 / 0 / 0 | 271 / 2 / 1 | 241 / 1 / 0 | 366 / 4 / 0 |
| 7 | 287 / 1 / 2 | 414 / 4 / 0 | 271 / 2 / 1 | 303 / 2 / 1 | 366 / 4 / 0 |
| 8 | 460 / 5 / 1 | 320 / 2 / 0 | 271 / 2 / 1 | 476 / 6 / 0 | 272 / 2 / 0 |
| 9 | 304 / 2 / 0 | 414 / 4 / 0 | 256 / 2 / 0 | 350 / 3 / 1 | 366 / 4 / 0 |
| 10 | 319 / 2 / 1 | 414 / 4 / 0 | 271 / 2 / 1 | 335 / 3 / 0 | 272 / 2 / 0 |
| 11 | 319 / 2 / 1 | 320 / 2 / 0 | 303 / 3 / 0 | 256 / 1 / 1 | 319 / 3 / 0 |
| 12 | 304 / 2 / 0 | 273 / 1 / 0 | 350 / 4 / 0 | 382 / 4 / 0 | 413 / 5 / 0 |
| 13 | 460 / 5 / 1 | 320 / 2 / 0 | 397 / 5 / 0 | 429 / 5 / 0 | 272 / 2 / 0 |
| 14 | 398 / 4 / 0 | 461 / 5 / 0 | 256 / 2 / 0 | 288 / 2 / 0 | 366 / 4 / 0 |
| 15 | 257 / 1 / 0 | 367 / 3 / 0 | 412 / 5 / 1 | 335 / 3 / 0 | 225 / 1 / 0 |
| 16 | 257 / 1 / 0 | 367 / 3 / 0 | 303 / 3 / 0 | 397 / 4 / 1 | 319 / 3 / 0 |
| 17 | 460 / 5 / 1 | 367 / 3 / 0 | 286 / 2 / 2 | 271 / 1 / 2 | 413 / 5 / 0 |
| 18 | 366 / 3 / 1 | 367 / 3 / 0 | 412 / 5 / 1 | 256 / 1 / 1 | 413 / 5 / 0 |
| 19 | 351 / 3 / 0 | 414 / 4 / 0 | 271 / 2 / 1 | 412 / 4 / 2 | 460 / 6 / 0 |
| 20 | 413 / 4 / 1 | 414 / 4 / 0 | 412 / 5 / 1 | 288 / 2 / 0 | 319 / 3 / 0 |
| 21 | 351 / 3 / 0 | 414 / 4 / 0 | 318 / 3 / 1 | 365 / 3 / 2 | 225 / 1 / 0 |
| 22 | 351 / 3 / 0 | 367 / 3 / 0 | 397 / 5 / 0 | 318 / 2 / 2 | 413 / 5 / 0 |
| 23 | 413 / 4 / 1 | 414 / 4 / 0 | 303 / 3 / 0 | 350 / 3 / 1 | 366 / 4 / 0 |
| 24 | 257 / 1 / 0 | 414 / 4 / 0 | 256 / 2 / 0 | 350 / 3 / 1 | 319 / 3 / 0 |
| 25 | 304 / 2 / 0 | 320 / 2 / 0 | 286 / 2 / 2 | 382 / 4 / 0 | 272 / 2 / 0 |
| 26 | 304 / 2 / 0 | 367 / 3 / 0 | 427 / 5 / 2 | 241 / 1 / 0 | 319 / 3 / 0 |
| 27 | 257 / 1 / 0 | 414 / 4 / 0 | 286 / 2 / 2 | 350 / 3 / 1 | 413 / 5 / 0 |
| 28 | 396 / 3 / 3 | 320 / 2 / 0 | 365 / 4 / 1 | 271 / 1 / 2 | 319 / 3 / 0 |
| 29 | 351 / 3 / 0 | 273 / 1 / 0 | 271 / 2 / 1 | 491 / 6 / 1 | 319 / 3 / 0 |
| 30 | 304 / 2 / 0 | 273 / 1 / 0 | 412 / 5 / 1 | 647 / 9 / 2 | 366 / 4 / 0 |
| 31 | 319 / 2 / 1 | 320 / 2 / 0 | 303 / 3 / 0 | 365 / 3 / 2 | 319 / 3 / 0 |
| 32 | 398 / 4 / 0 | 508 / 6 / 0 | 224 / 1 / 1 | 256 / 1 / 1 | 272 / 2 / 0 |
| 33 | 381 / 3 / 2 | 367 / 3 / 0 | 254 / 1 / 3 | 241 / 1 / 0 | 319 / 3 / 0 |
| 34 | 351 / 3 / 0 | 367 / 3 / 0 | 303 / 3 / 0 | 335 / 3 / 0 | 319 / 3 / 0 |
| 35 | 492 / 6 / 0 | 461 / 5 / 0 | 224 / 1 / 1 | 335 / 3 / 0 | 554 / 8 / 0 |
| 36 | 287 / 1 / 2 | 367 / 3 / 0 | 365 / 4 / 1 | 476 / 6 / 0 | 413 / 5 / 0 |
| 37 | 319 / 2 / 1 | 320 / 2 / 0 | 256 / 2 / 0 | 194 / 0 / 0 | 460 / 6 / 0 |
| 38 | 272 / 1 / 1 | 367 / 3 / 0 | 365 / 4 / 1 | 365 / 3 / 2 | 319 / 3 / 0 |
| 39 | 554 / 7 / 1 | 320 / 2 / 0 | 380 / 4 / 2 | 303 / 2 / 1 | 366 / 4 / 0 |
| 40 | 349 / 2 / 3 | 320 / 2 / 0 | 333 / 3 / 2 | 523 / 7 / 0 | 272 / 2 / 0 |

### D.2 Worst Case: 40 repetitions per program

<!-- table:measure-records-worst -->
| Repeat | Baseline | Branch-free | Unrolled | Loop-test | Combined |
|---|---|---|---|---|---|
| 1 | 534 / 4 / 8 | 367 / 3 / 0 | 561 / 4 / 13 | 518 / 4 / 8 | 319 / 3 / 0 |
| 2 | 551 / 5 / 6 | 414 / 4 / 0 | 315 / 1 / 6 | 330 / 0 / 8 | 272 / 2 / 0 |
| 3 | 519 / 4 / 7 | 414 / 4 / 0 | 439 / 3 / 8 | 409 / 2 / 7 | 319 / 3 / 0 |
| 4 | 346 / 0 / 8 | 320 / 2 / 0 | 405 / 1 / 12 | 392 / 1 / 9 | 272 / 2 / 0 |
| 5 | 442 / 3 / 5 | 320 / 2 / 0 | 456 / 4 / 6 | 456 / 3 / 7 | 507 / 7 / 0 |
| 6 | 566 / 5 / 7 | 273 / 1 / 0 | 486 / 4 / 8 | 347 / 1 / 6 | 272 / 2 / 0 |
| 7 | 581 / 5 / 8 | 414 / 4 / 0 | 488 / 5 / 5 | 332 / 1 / 5 | 366 / 4 / 0 |
| 8 | 472 / 3 / 7 | 414 / 4 / 0 | 548 / 5 / 9 | 471 / 3 / 8 | 413 / 5 / 0 |
| 9 | 579 / 4 / 11 | 508 / 6 / 0 | 582 / 7 / 5 | 565 / 5 / 8 | 272 / 2 / 0 |
| 10 | 440 / 2 / 8 | 320 / 2 / 0 | 627 / 7 / 8 | 285 / 0 / 5 | 366 / 4 / 0 |
| 11 | 423 / 1 / 10 | 414 / 4 / 0 | 469 / 3 / 10 | 471 / 3 / 8 | 366 / 4 / 0 |
| 12 | 502 / 3 / 9 | 461 / 5 / 0 | 533 / 5 / 8 | 531 / 3 / 12 | 225 / 1 / 0 |
| 13 | 457 / 3 / 6 | 414 / 4 / 0 | 300 / 1 / 5 | 580 / 5 / 9 | 272 / 2 / 0 |
| 14 | 549 / 4 / 9 | 367 / 3 / 0 | 424 / 3 / 7 | 550 / 5 / 7 | 319 / 3 / 0 |
| 15 | 442 / 3 / 5 | 461 / 5 / 0 | 518 / 5 / 7 | 381 / 3 / 2 | 272 / 2 / 0 |
| 16 | 562 / 3 / 13 | 414 / 4 / 0 | 345 / 1 / 8 | 439 / 2 / 9 | 272 / 2 / 0 |
| 17 | 534 / 4 / 8 | 367 / 3 / 0 | 439 / 3 / 8 | 582 / 6 / 6 | 413 / 5 / 0 |
| 18 | 393 / 1 / 8 | 320 / 2 / 0 | 377 / 2 / 7 | 597 / 6 / 7 | 366 / 4 / 0 |
| 19 | 457 / 3 / 6 | 414 / 4 / 0 | 390 / 1 / 11 | 394 / 2 / 6 | 319 / 3 / 0 |
| 20 | 485 / 2 / 11 | 461 / 5 / 0 | 424 / 3 / 7 | 409 / 2 / 7 | 413 / 5 / 0 |
| 21 | 549 / 4 / 9 | 367 / 3 / 0 | 332 / 2 / 4 | 456 / 3 / 7 | 413 / 5 / 0 |
| 22 | 455 / 2 / 9 | 461 / 5 / 0 | 454 / 3 / 9 | 422 / 1 / 11 | 366 / 4 / 0 |
| 23 | 532 / 3 / 11 | 367 / 3 / 0 | 424 / 3 / 7 | 612 / 6 / 8 | 225 / 1 / 0 |
| 24 | 442 / 3 / 5 | 414 / 4 / 0 | 627 / 7 / 8 | 377 / 1 / 8 | 319 / 3 / 0 |
| 25 | 442 / 3 / 5 | 320 / 2 / 0 | 642 / 7 / 9 | 518 / 4 / 8 | 272 / 2 / 0 |
| 26 | 470 / 2 / 10 | 461 / 5 / 0 | 595 / 6 / 9 | 471 / 3 / 8 | 319 / 3 / 0 |
| 27 | 641 / 5 / 12 | 414 / 4 / 0 | 392 / 2 / 8 | 469 / 2 / 11 | 413 / 5 / 0 |
| 28 | 517 / 3 / 10 | 367 / 3 / 0 | 486 / 4 / 8 | 518 / 4 / 8 | 366 / 4 / 0 |
| 29 | 519 / 4 / 7 | 320 / 2 / 0 | 439 / 3 / 8 | 473 / 4 / 5 | 319 / 3 / 0 |
| 30 | 536 / 5 / 5 | 414 / 4 / 0 | 514 / 3 / 13 | 362 / 1 / 7 | 272 / 2 / 0 |
| 31 | 566 / 5 / 7 | 414 / 4 / 0 | 471 / 4 / 7 | 441 / 3 / 6 | 319 / 3 / 0 |
| 32 | 613 / 6 / 7 | 367 / 3 / 0 | 345 / 1 / 8 | 597 / 6 / 7 | 225 / 1 / 0 |
| 33 | 376 / 0 / 10 | 414 / 4 / 0 | 345 / 1 / 8 | 580 / 5 / 9 | 460 / 6 / 0 |
| 34 | 457 / 3 / 6 | 367 / 3 / 0 | 454 / 3 / 9 | 488 / 4 / 6 | 319 / 3 / 0 |
| 35 | 549 / 4 / 9 | 414 / 4 / 0 | 439 / 3 / 8 | 473 / 4 / 5 | 366 / 4 / 0 |
| 36 | 502 / 3 / 9 | 414 / 4 / 0 | 518 / 5 / 7 | 627 / 6 / 9 | 366 / 4 / 0 |
| 37 | 502 / 3 / 9 | 414 / 4 / 0 | 394 / 3 / 5 | 488 / 4 / 6 | 272 / 2 / 0 |
| 38 | 720 / 7 / 11 | 320 / 2 / 0 | 394 / 3 / 5 | 394 / 2 / 6 | 272 / 2 / 0 |
| 39 | 440 / 2 / 8 | 367 / 3 / 0 | 563 / 5 / 10 | 441 / 3 / 6 | 413 / 5 / 0 |
| 40 | 455 / 2 / 9 | 320 / 2 / 0 | 456 / 4 / 6 | 499 / 2 / 13 | 272 / 2 / 0 |

### D.3 Real Case 1: 40 repetitions per program

<!-- table:measure-records-real1 -->
| Repeat | Baseline | Branch-free | Unrolled | Loop-test | Combined |
|---|---|---|---|---|---|
| 1 | 344 / 2 / 2 | 367 / 3 / 0 | 358 / 3 / 3 | 484 / 5 / 3 | 319 / 3 / 0 |
| 2 | 421 / 3 / 4 | 320 / 2 / 0 | 281 / 2 / 1 | 405 / 3 / 4 | 272 / 2 / 0 |
| 3 | 485 / 5 / 2 | 414 / 4 / 0 | 386 / 2 / 8 | 454 / 5 / 1 | 225 / 1 / 0 |
| 4 | 498 / 4 / 6 | 320 / 2 / 0 | 390 / 4 / 2 | 360 / 3 / 1 | 319 / 3 / 0 |
| 5 | 436 / 3 / 5 | 320 / 2 / 0 | 328 / 3 / 1 | 469 / 5 / 2 | 272 / 2 / 0 |
| 6 | 359 / 2 / 3 | 320 / 2 / 0 | 559 / 6 / 7 | 422 / 4 / 2 | 413 / 5 / 0 |
| 7 | 500 / 5 / 3 | 273 / 1 / 0 | 514 / 6 / 4 | 390 / 3 / 3 | 460 / 6 / 0 |
| 8 | 453 / 4 / 3 | 461 / 5 / 0 | 358 / 3 / 3 | 420 / 3 / 5 | 366 / 4 / 0 |
| 9 | 500 / 5 / 3 | 320 / 2 / 0 | 405 / 4 / 3 | 439 / 5 / 0 | 507 / 7 / 0 |
| 10 | 483 / 4 / 5 | 320 / 2 / 0 | 405 / 4 / 3 | 484 / 5 / 3 | 225 / 1 / 0 |
| 11 | 468 / 4 / 4 | 367 / 3 / 0 | 638 / 8 / 6 | 484 / 5 / 3 | 272 / 2 / 0 |
| 12 | 423 / 4 / 1 | 367 / 3 / 0 | 311 / 2 / 3 | 516 / 6 / 2 | 272 / 2 / 0 |
| 13 | 468 / 4 / 4 | 320 / 2 / 0 | 341 / 2 / 5 | 313 / 2 / 1 | 413 / 5 / 0 |
| 14 | 406 / 3 / 3 | 320 / 2 / 0 | 405 / 4 / 3 | 281 / 1 / 2 | 507 / 7 / 0 |
| 15 | 376 / 3 / 1 | 367 / 3 / 0 | 578 / 8 / 2 | 499 / 5 / 4 | 366 / 4 / 0 |
| 16 | 374 / 2 / 4 | 414 / 4 / 0 | 266 / 2 / 0 | 373 / 2 / 5 | 319 / 3 / 0 |
| 17 | 532 / 6 / 2 | 414 / 4 / 0 | 373 / 3 / 4 | 405 / 3 / 4 | 319 / 3 / 0 |
| 18 | 344 / 2 / 2 | 273 / 1 / 0 | 343 / 3 / 2 | 420 / 3 / 5 | 413 / 5 / 0 |
| 19 | 391 / 3 / 2 | 273 / 1 / 0 | 328 / 3 / 1 | 358 / 2 / 4 | 319 / 3 / 0 |
| 20 | 406 / 3 / 3 | 367 / 3 / 0 | 386 / 2 / 8 | 313 / 2 / 1 | 366 / 4 / 0 |
| 21 | 391 / 3 / 2 | 414 / 4 / 0 | 467 / 5 / 4 | 422 / 4 / 2 | 272 / 2 / 0 |
| 22 | 592 / 6 / 6 | 320 / 2 / 0 | 328 / 3 / 1 | 482 / 4 / 6 | 366 / 4 / 0 |
| 23 | 391 / 3 / 2 | 461 / 5 / 0 | 390 / 4 / 2 | 531 / 6 / 3 | 272 / 2 / 0 |
| 24 | 376 / 3 / 1 | 367 / 3 / 0 | 499 / 6 / 3 | 390 / 3 / 3 | 366 / 4 / 0 |
| 25 | 470 / 5 / 1 | 367 / 3 / 0 | 279 / 1 / 4 | 390 / 3 / 3 | 319 / 3 / 0 |
| 26 | 421 / 3 / 4 | 508 / 6 / 0 | 437 / 5 / 2 | 360 / 3 / 1 | 366 / 4 / 0 |
| 27 | 498 / 4 / 6 | 508 / 6 / 0 | 422 / 5 / 1 | 501 / 6 / 1 | 366 / 4 / 0 |
| 28 | 421 / 3 / 4 | 414 / 4 / 0 | 328 / 3 / 1 | 467 / 4 / 5 | 272 / 2 / 0 |
| 29 | 468 / 4 / 4 | 461 / 5 / 0 | 516 / 7 / 1 | 249 / 0 / 3 | 413 / 5 / 0 |
| 30 | 453 / 4 / 3 | 367 / 3 / 0 | 407 / 5 / 0 | 375 / 3 / 2 | 366 / 4 / 0 |
| 31 | 609 / 7 / 4 | 508 / 6 / 0 | 356 / 2 / 6 | 467 / 4 / 5 | 319 / 3 / 0 |
| 32 | 391 / 3 / 2 | 367 / 3 / 0 | 264 / 1 / 3 | 296 / 1 / 3 | 272 / 2 / 0 |
| 33 | 637 / 6 / 9 | 320 / 2 / 0 | 296 / 2 / 2 | 343 / 2 / 3 | 413 / 5 / 0 |
| 34 | 374 / 2 / 4 | 367 / 3 / 0 | 358 / 3 / 3 | 313 / 2 / 1 | 178 / 0 / 0 |
| 35 | 329 / 2 / 1 | 414 / 4 / 0 | 435 / 4 / 5 | 281 / 1 / 2 | 272 / 2 / 0 |
| 36 | 466 / 3 / 7 | 508 / 6 / 0 | 373 / 3 / 4 | 390 / 3 / 3 | 413 / 5 / 0 |
| 37 | 438 / 4 / 2 | 273 / 1 / 0 | 390 / 4 / 2 | 407 / 4 / 1 | 413 / 5 / 0 |
| 38 | 485 / 5 / 2 | 555 / 7 / 0 | 484 / 6 / 2 | 437 / 4 / 3 | 272 / 2 / 0 |
| 39 | 327 / 1 / 4 | 226 / 0 / 0 | 311 / 2 / 3 | 420 / 3 / 5 | 272 / 2 / 0 |
| 40 | 389 / 2 / 5 | 414 / 4 / 0 | 311 / 2 / 3 | 375 / 3 / 2 | 366 / 4 / 0 |

### D.4 Real Case 2: 40 repetitions per program

<!-- table:measure-records-real2 -->
| Repeat | Baseline | Branch-free | Unrolled | Loop-test | Combined |
|---|---|---|---|---|---|
| 1 | 350 / 2 / 2 | 367 / 3 / 0 | 458 / 5 / 3 | 304 / 2 / 0 | 319 / 3 / 0 |
| 2 | 489 / 4 / 5 | 414 / 4 / 0 | 302 / 2 / 2 | 319 / 2 / 1 | 319 / 3 / 0 |
| 3 | 365 / 2 / 3 | 367 / 3 / 0 | 334 / 3 / 1 | 240 / 0 / 2 | 319 / 3 / 0 |
| 4 | 476 / 5 / 1 | 320 / 2 / 0 | 473 / 5 / 4 | 443 / 4 / 3 | 460 / 6 / 0 |
| 5 | 412 / 3 / 3 | 320 / 2 / 0 | 426 / 4 / 4 | 443 / 4 / 3 | 272 / 2 / 0 |
| 6 | 320 / 2 / 0 | 414 / 4 / 0 | 441 / 4 / 5 | 597 / 6 / 7 | 319 / 3 / 0 |
| 7 | 382 / 3 / 1 | 414 / 4 / 0 | 379 / 3 / 4 | 287 / 1 / 2 | 272 / 2 / 0 |
| 8 | 442 / 3 / 5 | 414 / 4 / 0 | 349 / 3 / 2 | 458 / 4 / 4 | 366 / 4 / 0 |
| 9 | 333 / 1 / 4 | 273 / 1 / 0 | 302 / 2 / 2 | 428 / 4 / 2 | 554 / 8 / 0 |
| 10 | 506 / 5 / 3 | 508 / 6 / 0 | 426 / 4 / 4 | 379 / 2 / 5 | 366 / 4 / 0 |
| 11 | 410 / 2 / 6 | 414 / 4 / 0 | 379 / 3 / 4 | 287 / 1 / 2 | 366 / 4 / 0 |
| 12 | 506 / 5 / 3 | 367 / 3 / 0 | 334 / 3 / 1 | 349 / 2 / 3 | 319 / 3 / 0 |
| 13 | 333 / 1 / 4 | 320 / 2 / 0 | 364 / 3 / 3 | 443 / 4 / 3 | 319 / 3 / 0 |
| 14 | 491 / 5 / 2 | 461 / 5 / 0 | 396 / 4 / 2 | 428 / 4 / 2 | 319 / 3 / 0 |
| 15 | 395 / 2 / 5 | 461 / 5 / 0 | 347 / 2 / 5 | 428 / 4 / 2 | 272 / 2 / 0 |
| 16 | 412 / 3 / 3 | 555 / 7 / 0 | 426 / 4 / 4 | 396 / 3 / 3 | 366 / 4 / 0 |
| 17 | 506 / 5 / 3 | 273 / 1 / 0 | 287 / 2 / 1 | 428 / 4 / 2 | 319 / 3 / 0 |
| 18 | 521 / 5 / 4 | 273 / 1 / 0 | 475 / 6 / 1 | 522 / 6 / 2 | 366 / 4 / 0 |
| 19 | 365 / 2 / 3 | 555 / 7 / 0 | 426 / 4 / 4 | 490 / 5 / 3 | 460 / 6 / 0 |
| 20 | 444 / 4 / 2 | 273 / 1 / 0 | 441 / 4 / 5 | 317 / 1 / 4 | 319 / 3 / 0 |
| 21 | 320 / 2 / 0 | 367 / 3 / 0 | 334 / 3 / 1 | 443 / 4 / 3 | 272 / 2 / 0 |
| 22 | 600 / 7 / 3 | 320 / 2 / 0 | 255 / 1 / 2 | 270 / 0 / 4 | 225 / 1 / 0 |
| 23 | 350 / 2 / 2 | 273 / 1 / 0 | 302 / 2 / 2 | 552 / 6 / 4 | 178 / 0 / 0 |
| 24 | 459 / 4 / 3 | 273 / 1 / 0 | 364 / 3 / 3 | 456 / 3 / 7 | 366 / 4 / 0 |
| 25 | 335 / 2 / 1 | 226 / 0 / 0 | 443 / 5 / 2 | 428 / 4 / 2 | 272 / 2 / 0 |
| 26 | 350 / 2 / 2 | 320 / 2 / 0 | 599 / 8 / 3 | 364 / 2 / 4 | 413 / 5 / 0 |
| 27 | 506 / 5 / 3 | 414 / 4 / 0 | 332 / 2 / 4 | 319 / 2 / 1 | 272 / 2 / 0 |
| 28 | 444 / 4 / 2 | 320 / 2 / 0 | 473 / 5 / 4 | 381 / 3 / 2 | 319 / 3 / 0 |
| 29 | 476 / 5 / 1 | 320 / 2 / 0 | 317 / 2 / 3 | 255 / 0 / 3 | 366 / 4 / 0 |
| 30 | 365 / 2 / 3 | 508 / 6 / 0 | 302 / 2 / 2 | 411 / 3 / 4 | 319 / 3 / 0 |
| 31 | 444 / 4 / 2 | 367 / 3 / 0 | 501 / 4 / 9 | 366 / 3 / 1 | 272 / 2 / 0 |
| 32 | 444 / 4 / 2 | 367 / 3 / 0 | 381 / 4 / 1 | 426 / 3 / 5 | 225 / 1 / 0 |
| 33 | 459 / 4 / 3 | 367 / 3 / 0 | 317 / 2 / 3 | 304 / 2 / 0 | 460 / 6 / 0 |
| 34 | 348 / 1 / 5 | 320 / 2 / 0 | 332 / 2 / 4 | 396 / 3 / 3 | 366 / 4 / 0 |
| 35 | 335 / 2 / 1 | 367 / 3 / 0 | 317 / 2 / 3 | 285 / 0 / 5 | 413 / 5 / 0 |
| 36 | 288 / 1 / 1 | 414 / 4 / 0 | 364 / 3 / 3 | 381 / 3 / 2 | 413 / 5 / 0 |
| 37 | 412 / 3 / 3 | 414 / 4 / 0 | 505 / 6 / 3 | 428 / 4 / 2 | 319 / 3 / 0 |
| 38 | 536 / 5 / 5 | 320 / 2 / 0 | 473 / 5 / 4 | 599 / 7 / 4 | 319 / 3 / 0 |
| 39 | 350 / 2 / 2 | 461 / 5 / 0 | 334 / 3 / 1 | 366 / 3 / 1 | 319 / 3 / 0 |
| 40 | 335 / 2 / 1 | 414 / 4 / 0 | 411 / 4 / 3 | 614 / 7 / 5 | 319 / 3 / 0 |

### D.5 Totals and statistical calculations

Each row summarizes 40 observations. Mean cycles = sum of cycles / 40; mean misses and mean wrong predictions are their totals divided by 40. Sample standard deviation is `sqrt(sum((x − mean)^2) / 39)` and the standard error (SE) is that value divided by `sqrt(40)`. For two independent means, the SE of their difference is `sqrt(SE_1^2 + SE_2^2)`. Section 3.4's margins in standard errors divide the difference between the means by this combined SE. Displayed means and SEs below are rounded to two decimal places; the individual observations above permit recalculation at full precision.

<!-- table:measure-summary-totals -->
| Case | Program | Sum cycles | Mean cycles | SE cycles | Total misses | Total wrong |
|---|---|---|---|---|---|---|
| Best Case | Baseline | 14509 | 362.73 | 11.98 | 122 | 25 |
| Best Case | Branch-free | 15056 | 376.40 | 10.40 | 128 | 0 |
| Best Case | Unrolled | 12658 | 316.45 | 10.09 | 119 | 39 |
| Best Case | Loop-test | 14100 | 352.50 | 14.10 | 125 | 31 |
| Best Case | Combined | 13700 | 342.50 | 11.41 | 140 | 0 |
| Worst Case | Baseline | 20117 | 502.93 | 11.61 | 131 | 328 |
| Worst Case | Branch-free | 15573 | 389.33 | 8.24 | 139 | 0 |
| Worst Case | Unrolled | 18410 | 460.25 | 13.97 | 140 | 314 |
| Worst Case | Loop-test | 18745 | 468.63 | 13.59 | 125 | 298 |
| Worst Case | Combined | 13183 | 329.58 | 10.58 | 129 | 0 |
| Real Case 1 | Baseline | 17593 | 439.83 | 11.49 | 144 | 135 |
| Real Case 1 | Branch-free | 15056 | 376.40 | 12.16 | 128 | 0 |
| Real Case 1 | Unrolled | 15604 | 390.10 | 13.81 | 147 | 121 |
| Real Case 1 | Loop-test | 16185 | 404.63 | 11.17 | 135 | 112 |
| Real Case 1 | Combined | 13512 | 337.80 | 11.88 | 136 | 0 |
| Real Case 2 | Baseline | 16614 | 415.35 | 11.80 | 127 | 107 |
| Real Case 2 | Branch-free | 14915 | 372.88 | 12.61 | 125 | 0 |
| Real Case 2 | Unrolled | 15421 | 385.53 | 11.76 | 138 | 121 |
| Real Case 2 | Loop-test | 16030 | 400.75 | 14.72 | 125 | 117 |
| Real Case 2 | Combined | 13418 | 335.45 | 11.36 | 134 | 0 |

<!-- generated-evidence:end -->
