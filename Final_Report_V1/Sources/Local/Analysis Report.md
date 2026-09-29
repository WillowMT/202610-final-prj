# Analysis report: CPU instruction execution

## Introduction

This report examines how the CPU simulator adjusts image brightness. A pixel below 128 is increased by 32; a pixel at or above 128 is reduced by 8. I compare the four recorded test cases, explain their cycle counts, and estimate the effect on the larger workload in the assignment.

The evidence comes from the [transcribed run logs](Logs.md), [data collection sheet](data-collection-template.md), [Excel workbook and charts](Data%20Collection%20Sheet.xlsx), and saved screenshots. The [project scenario](Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md) provides the assignment requirements. The [simulator code](Project1_CPU_Simulator.html) is used to check how instructions and delays are counted.

## 1. Instruction trace and experiment evidence

### 1.1 Recorded experiments

All four recorded runs completed 16 pixels at 50 ms per animation step. Each pair of screenshots represents one run, not two experiments.

| Experiment | Test case | Total cycles | Text log | Controls and registers | Output pixels and detailed results |
|---|---|---|---|---|---|
| 1 | Best: all pixels are 0 | 351 | [Run 1](Logs.md#run-1-best-case-all-pixels-0) | [BC-1](Screenshots/BC-1.png) | [BC-2](Screenshots/BC-2.png) |
| 2 | Worst: alternating 64 and 192 | 502 | [Run 2](Logs.md#run-2-worst-case-alternating) | [WC-1](Screenshots/WC-1.png) | [WC-2](Screenshots/WC-2.png) |
| 3 | Real Case 1: 70% dark | 406 | [Run 3](Logs.md#run-3-real-case-1-70-dark) | [RC1-1](Screenshots/RC1-1.png) | [RC1-2](Screenshots/RC1-2.png) |
| 4 | Real Case 2: clustered bright and dark pixels | 444 | [Run 4](Logs.md#run-4-real-case-2-clustered) | [RC2-1](Screenshots/RC2-1.png) | [RC2-2](Screenshots/RC2-2.png) |

The assignment asks for at least five experiments. Only four complete runs are supported by the current evidence, so a fifth complete experiment is still required. The screenshots show final states; they do not record every instruction as it happened.

The logs preserve all 16 input and output values for each run, with unreadable or inferred values identified. These allow the pixel paths and instruction counts to be reconstructed. That reconstruction is included below and in Appendix B; it does not create another experiment or recover the missing order of random delays.

### 1.2 Instruction sequence and cycle costs

The program counter (PC) identifies the next instruction. Registers are small storage locations inside the CPU. In this program, R0 counts processed pixels, R1 holds the pixel address, R3 holds the current pixel, and R4 holds the adjusted value.

The following costs and paths come from the supplied simulator code. They explain the recorded totals, but do not replace a saved step-by-step trace of each run.

| PC | Instruction | Purpose | Cycles before extra delays |
|---|---|---|---|
| 0x00 | `LOAD R0, #0` | Start the pixel counter at zero | 1 |
| 0x04 | `LOAD R1, #1024` | Set the first pixel address | 1 |
| 0x08 | `LOAD R3, [R1]` | Read the current pixel | 3; add 47 for a cache miss |
| 0x0C | `CMP R3, R2` | Compare the pixel with 128 | 1 |
| 0x10 | `BLT DARK` | Choose the dark-pixel path if the value is below 128 | 1; add 15 for an incorrect prediction |
| 0x14 | `SUB R4, R3, R7` | Subtract 8 from a bright pixel | 1 |
| 0x18 | `JMP STORE` | Skip the dark-pixel calculation | 2 |
| 0x1C | `ADD R4, R3, R6` | Add 32 to a dark pixel | 1 |
| 0x20 | `STORE R4, [R1]` | Save the adjusted output pixel | 3 |
| 0x24 | `INC R1, #1` | Move to the next pixel address | 1 |
| 0x28 | `INC R0, #1` | Increase the processed-pixel count | 1 |
| 0x2C | `CMP R0, #16` | Check whether 16 pixels are complete | 1 |
| 0x30 | `BNE LOOP` | Repeat until all pixels are complete | 1 |
| 0x34 | `HALT` | End position displayed by the simulator | No additional cycle is counted in this version |

Although the instruction list displays a 1-cycle cost for `HALT`, the code stops as soon as the PC reaches it. This explains why it is not added to the recorded totals. Stores always cost 3 cycles in this version; cache misses are counted only when reading pixels at `0x08`.

After the two setup instructions, the possible paths for one pixel are:

```text
Dark:   08 → 0C → 10 → 1C → 20 → 24 → 28 → 2C → 30
Cycles:  3 +  1 +  1 +  1 +  3 +  1 +  1 +  1 +  1 = 13

Bright: 08 → 0C → 10 → 14 → 18 → 20 → 24 → 28 → 2C → 30
Cycles:  3 +  1 +  1 +  1 +  2 +  3 +  1 +  1 +  1 +  1 = 15
```

These totals exclude cache and branch delays. After the loop check, the PC returns to `0x08` or finishes at `0x34`.

The instruction cost for a complete run is therefore:

```text
Instruction cycles = 2 setup cycles + 13 × dark pixels + 15 × bright pixels
                   = 210 + 2 × bright pixels, for a 16-pixel run
```

### 1.3 Registers and pixel output

At completion, R0 is 16 (`0x10`) and R1 is 1040 (`0x410`). The logs show R2 = 128 and R6 = 32. R7's value is clipped in the screenshots; the simulator code defines it as positive 8 because the instruction subtracts it.

The final pixel values differ between cases:

| Case | Final input in R3 | Final output in R4 | Check |
|---|---|---|---|
| Best | 0 | 32 | 0 + 32 = 32 |
| Worst | 192 | 184 | 192 − 8 = 184 |
| Real Case 1 | 140 | 132 | 140 − 8 = 132 |
| Real Case 2 | 60 | 92 | 60 + 32 = 92 |

The screenshots also show all 16 output pixels. Best Case produces sixteen values of 32, while Worst Case alternates between 96 and 184. These match the required brightness adjustment.

In every log, the execution summary names `0x30 BNE LOOP` as the last instruction, while the PC display shows `0x34`. These agree: the final loop check has finished, and the PC has moved to the stop position.

### 1.4 Cache and branch events

The simulator gives each pixel read an approximately 80% chance of a cache hit. A miss adds 47 cycles. It does not track actual cache contents, so the saved totals cannot show that a miss happened on the first pixel or on a particular memory boundary.

For the brightness decision (`BLT`), the chance of a correct prediction is 95% in Best Case, 50% in Worst Case, and 80% in both real cases. These are random choices in the program, rather than a predictor learning the image pattern. The loop check (`BNE`) is always counted as correct, including its final check.

Each run therefore has 32 counted branches: 16 brightness decisions and 16 loop checks. All recorded mistakes belong to the brightness decisions:

| Case | Correct brightness predictions, out of 16 | Correct loop checks, out of 16 | Total incorrect predictions |
|---|---|---|---|
| Best | 16 | 16 | 0 |
| Worst | 7 | 16 | 9 |
| Real Case 1 | 13 | 16 | 3 |
| Real Case 2 | 14 | 16 | 2 |

The exact pixel numbers at which the misses and mistakes occurred were not saved. In particular, there is no evidence that Real Case 2's two mistakes occurred where the bright region changed to dark. A full trace needs to record each instruction's PC, register changes, cache result, branch result, and cycle increase while stepping through the run.

### 1.5 Instruction counts reconstructed from the logs

For each logged input, a value below 128 follows the dark path; any other value follows the bright path. Counting these paths gives the following number of executions for each instruction. These are calculated from the pixel lists and program, rather than copied from an instruction-history screen.

| Instruction | Best | Worst | Real Case 1 | Real Case 2 |
|---|---|---|---|---|
| 0x00: initialize R0 | 1 | 1 | 1 | 1 |
| 0x04: initialize R1 | 1 | 1 | 1 | 1 |
| 0x08: load pixel | 16 | 16 | 16 | 16 |
| 0x0C: compare brightness | 16 | 16 | 16 | 16 |
| 0x10: choose brightness path | 16 | 16 | 16 | 16 |
| 0x14: subtract 8 | 0 | 8 | 5 | 8 |
| 0x18: jump after subtraction | 0 | 8 | 5 | 8 |
| 0x1C: add 32 | 16 | 8 | 11 | 8 |
| 0x20: store output | 16 | 16 | 16 | 16 |
| 0x24: advance pixel address | 16 | 16 | 16 | 16 |
| 0x28: update pixel counter | 16 | 16 | 16 | 16 |
| 0x2C: compare counter with 16 | 16 | 16 | 16 | 16 |
| 0x30: repeat or finish | 16 | 16 | 16 | 16 |
| Total executed instructions, excluding HALT | 146 | 154 | 151 | 154 |
| Instruction cycles before delays | 210 | 226 | 220 | 226 |

An instruction count differs from a cycle count because some instructions take more than one cycle. Multiplying each count by its cost in Section 1.2 gives the final row. Adding the logged delays then reproduces all four totals:

```text
Best:        210 + 141 = 351
Worst:       226 + 276 = 502
Real Case 1: 220 + 186 = 406
Real Case 2: 226 + 218 = 444
```

## 2. Performance data

### 2.1 Recorded results

Cycles per pixel (CPP) is total cycles divided by 16. A stall is extra waiting time caused by a cache miss or an incorrect branch prediction.

| Metric | Best | Worst | Real Case 1 | Real Case 2 |
|---|---|---|---|---|
| Total cycles | 351 | 502 | 406 | 444 |
| CPP, rounded to two decimals | 21.94 | 31.38 | 25.38 | 27.75 |
| Cache hits | 13 | 13 | 13 | 12 |
| Cache misses | 3 | 3 | 3 | 4 |
| Cache miss rate | 18.8% | 18.8% | 18.8% | 25.0% |
| Correct branches / total | 32 / 32 | 23 / 32 | 29 / 32 | 30 / 32 |
| Branch misprediction rate | 0.0% | 28.1% | 9.4% | 6.3% |
| Stall cycles | 141 | 276 | 186 | 218 |
| Register spill count | Not separately measured | Not separately measured | Not separately measured | Not separately measured |

Cache miss rate is `misses ÷ (hits + misses) × 100`, using the 16 pixel reads counted by the simulator. Branch misprediction rate is `(total branches − correct branches) ÷ total branches × 100`. Both percentages are calculated from the counts before rounding.

A register spill means temporarily moving a register value to memory because register space is insufficient. The supplied program contains no spill instructions, and the simulator has no spill counter. There are zero spill operations in this program, but this is a finding from its code rather than a separate measured result.

### 2.2 Explaining the cycle totals

```text
Cache delay = cache misses × 47
Branch delay = incorrect predictions × 15
Total cycles = instruction cycles + cache delay + branch delay
```

| Case | Dark pixels | Bright pixels | Instruction cycles | Cache delay | Branch delay | Total cycles |
|---|---|---|---|---|---|---|
| Best | 16 | 0 | 210 | 141 | 0 | 351 |
| Worst | 8 | 8 | 226 | 141 | 135 | 502 |
| Real Case 1 | 11 | 5 | 220 | 141 | 45 | 406 |
| Real Case 2 | 8 | 8 | 226 | 188 | 30 | 444 |

Real Case 1 contains 11 dark pixels out of 16, or 68.75%, which is close to its 70% label.

Cache misses were the largest source of delay within each recorded run. Branch mistakes explain most of the difference between Best and Worst Case: their cache delays are equal, but Worst Case has 135 extra branch-delay cycles and 16 extra instruction cycles. It uses 151 more cycles overall, about 43.0% more than Best Case.

The simulator does not measure memory bandwidth, so the results cannot confirm whether data-transfer speed would limit a real system.

### 2.3 Comparison with the assignment targets

All four recorded CPP values are above the scenario's target of fewer than 5 cycles per pixel. Their cache hit rates, 75.0% to 81.3%, also fall below the target of more than 95%. Best Case and both real cases exceed the 90% branch-accuracy target; Worst Case does not.

These are single-run results. The simulator's random outcomes mean that repeated runs are needed before drawing conclusions about average performance. The sample numbers in the quick guide are examples, not the results of these experiments.

### 2.4 Checking all recorded output pixels

I checked the pixel lists in `Logs.md` against the brightness rule, not just the final value in R4. All 64 output entries are consistent with the rule and with the paths in Appendix B.

| Run | Dark pixels | Bright pixels | Output entries consistent with the rule |
|---|---|---|---|
| Best | 16 | 0 | 16 / 16 |
| Worst | 8 | 8 | 16 / 16 |
| Real Case 1 | 11 | 5 | 16 / 16 |
| Real Case 2 | 8 | 8 | 16 / 16 |

The source limitations still matter. Best Case's black input cells are recorded as zero from the test-case definition. Real Case 2's input values at pixels 9 and 12 are recorded as 6 because their outputs are 38 and `38 − 32 = 6`. Those two inferred inputs cannot independently prove the output calculation; the other 14 Real Case 2 inputs are readable in the screenshot.

## 3. Optimization analysis

### 3.1 Comparison of three proposed methods

No optimized versions have been tested in the recorded experiments. The following comparison explains what should be tested and why; measured improvements are still needed for this part of the assignment.

| Method | How it could help | Most relevant cases | Limitation |
|---|---|---|---|
| Cache prefetching | Fetch upcoming pixel data earlier so the CPU spends less time waiting. | All four cases, especially Real Case 2 with four misses. | It adds work and may not avoid every miss. The current simulator has no prefetch control. |
| Branch-free code | Calculate or select the adjusted value without the brightness-based jump. | Worst Case, which recorded nine branch mistakes. | The replacement instructions also cost cycles. It may offer little benefit when predictions are already correct. |
| Loop unrolling | Process four pixels before updating the loop counter and checking whether to repeat. | All four cases, because all repeat the same loop checks. | It makes the program longer and can use more registers. It does not automatically remove each pixel's brightness decision. |

### 3.2 Calculated possible savings, not measured improvements

The recorded delays show how many cycles could be avoided in an ideal case. The first two rows below assume every listed delay is removed with no added instruction cost. They are upper limits on delay savings, not predictions of the actual optimized totals.

| Calculation | Best | Worst | Real Case 1 | Real Case 2 |
|---|---|---|---|---|
| Cache-delay cycles that could be removed: misses × 47 | 141 | 141 | 141 | 188 |
| Branch-delay cycles that could be removed: mistakes × 15 | 0 | 135 | 45 | 30 |
| Loop-instruction saving under the four-pixel assumption below | 36 | 36 | 36 | 36 |

For loop unrolling, assume the counter update, counter comparison, and repeat instruction still cost 1 cycle each, but execute four times rather than sixteen. The saving is `3 × (16 − 4) = 36 cycles`. This assumes a suitable update by four; the pixel address still advances for every pixel. Extra work in a real implementation could reduce this saving.

For example, removing all cache delays from the recorded Worst Case without adding work would give `502 − 141 = 361 cycles`, a 28.1% reduction. Removing only its branch delays would give `502 − 135 = 367 cycles`, a 26.9% reduction. Neither result is an observed optimized run.

I would test cache prefetching first across all cases, and also test branch-free code on Worst Case. Its branch delays are nearly as large as its cache delays. For Best Case, there were no branch mistakes to remove in the saved run. The best method for each case can only be confirmed by testing.

To measure improvement, each changed version should process the same pixels and produce the same output as the original. Repeat the runs, record average cycles, and use:

```text
Improvement (%) = (original average cycles − improved average cycles)
                  ÷ original average cycles × 100
```

The supplied interface cannot switch between these methods. A modified version or another approved tool is needed to obtain those measurements.

### 3.3 Comparing the possible savings across the four logs

The following table applies the calculations in Section 3.2 to each recorded run. Each cell shows the calculated remaining cycles and the percentage reduction from that run's total. Only the original column contains recorded results.

| Case | Original recorded cycles | Remove cache delays only | Remove branch delays only | Reduce loop instructions by 36 cycles |
|---|---|---|---|---|
| Best | 351 | 210 (40.2%) | 351 (0.0%) | 315 (10.3%) |
| Worst | 502 | 361 (28.1%) | 367 (26.9%) | 466 (7.2%) |
| Real Case 1 | 406 | 265 (34.7%) | 361 (11.1%) | 370 (8.9%) |
| Real Case 2 | 444 | 256 (42.3%) | 414 (6.8%) | 408 (8.1%) |

The cache-delay column assumes that every recorded cache delay is avoided. It is not a measured prefetching result. Similarly, removing branch delays does not account for any instruction changes needed to implement branch-free code. The loop column uses the stated four-pixel assumption. These calculations compare opportunities for improvement, not proven optimized programs.

On this basis, avoiding cache delays offers the largest possible saving in all four logs. Branch changes are particularly worth testing on Worst Case because its branch-delay saving is almost as large. On Real Case 2, the calculated loop-instruction saving is larger than its branch-delay saving. Actual tests are needed to see whether the added work changes these rankings.

For those tests, the input and output lists in `Logs.md` provide a fixed comparison. Real Case 2 must use its saved pixel list, including the two values marked as inferred, rather than newly generated values. Each new result should record its method, run ID, input list, cycles, and output check. Repeating each method would help separate its effect from random cache and branch outcomes.

## 4. Extrapolation and cost impact

### 4.1 Assumptions

For the calculations below, I use:

- One assignment image of 256 × 256 pixels, or 65,536 pixels.
- 2,000,000 processed images per day, as requested in the deliverables.
- One 2.4 GHz processor per modelled server, available entirely for this task.
- 8 W of processor power, electricity at $0.12 per kWh, and 365 days per year.
- A four-hour completion deadline, called the service-level agreement (SLA) in the scenario.

The scenario also describes larger uploaded photos and says that 50% need adjustment. The main calculation follows the specific request for 2 million processed 256 × 256 images; the 50% alternative is shown below. File size in MB does not establish the number of pixels, so no extra image-size multiplier is assumed.

These estimates cover the brightness-processing instructions only. Reading image files, other software, and whole-server power use are not measured.

### 4.2 Cycles for a 256 × 256 image

```text
Number of 16-pixel groups = 65,536 ÷ 16 = 4,096
Estimated image cycles = recorded 16-pixel cycles × 4,096
                       = unrounded CPP × 65,536
```

The factor 4,096 applies to total cycles for 16 pixels, not directly to CPP.

| Case | Cycles for 16 pixels | Estimated cycles per 256 × 256 image |
|---|---|---|
| Best | 351 | 1,437,696 |
| Worst | 502 | 2,056,192 |
| Real Case 1 | 406 | 1,662,976 |
| Real Case 2 | 444 | 1,818,624 |

These match the simulator's displayed estimates. They assume the small test's average cycle cost continues across the whole image. Larger-image performance has not been measured.

### 4.3 Total cycles for 2 million images per day

At 2.4 GHz, the processor completes 2,400,000,000 cycles per second. One cycle lasts about 0.417 nanoseconds, but an instruction can take several cycles.

```text
Daily cycles = estimated cycles per image × 2,000,000
Processor time in seconds = daily cycles ÷ 2,400,000,000
```

| Case | Estimated cycles per day | Processor time per day |
|---|---|---|
| Best | 2,875,392,000,000 | 1,198.08 seconds (19.97 minutes) |
| Worst | 4,112,384,000,000 | 1,713.49 seconds (28.56 minutes) |
| Real Case 1 | 3,325,952,000,000 | 1,385.81 seconds (23.10 minutes) |
| Real Case 2 | 3,637,248,000,000 | 1,515.52 seconds (25.26 minutes) |

Real Case 1 is used for the worked cost example, without assuming it is the average of all real photos. If only 1 million images require processing, its daily total becomes 1,662,976,000,000 cycles, or 692.91 seconds of processor time. The other cases' daily cycles and processing times also halve.

### 4.4 Electricity cost for 24-hour operation

For one processor using 8 W throughout the day:

```text
8 W = 0.008 kW
Daily energy = 0.008 × 24 = 0.192 kWh
Daily cost = 0.192 × $0.12 = $0.02304
Annual cost = $0.02304 × 365 = $8.4096, approximately $8.41
```

This is the cost of continuous 8 W operation. It does not fall simply because the image calculation finishes earlier.

For comparison, the portion attributed to Real Case 1's calculated processing time is:

```text
Processing energy = (1,385.8133 ÷ 3,600) × 0.008 ≈ 0.00307959 kWh/day
Processing cost = 0.00307959 × $0.12 ≈ $0.00036955/day
```

That is about $0.1349 per year for the processing time alone. It excludes the rest of the day, so it is not the same as the full 24-hour electricity bill.

### 4.5 Server count for the four-hour deadline

Assume all 2 million assignment images must be completed within one four-hour period. Four hours equals 14,400 seconds.

```text
Required servers = processor time for the whole workload ÷ 14,400
                   rounded up to the next whole number
```

For Real Case 1, `1,385.8133 ÷ 14,400 ≈ 0.0962`, so the estimate rounds up to one server. Even Worst Case needs only `1,713.4933 ÷ 14,400 ≈ 0.1190` of this modelled server's four-hour capacity, which also rounds up to one.

Thus, one server is enough for the simplified brightness calculation in all four cases. This is not a measured requirement for a photo-storage service: larger photos, file handling, other tasks, and backup capacity would also affect the real server count.

### 4.6 Annual cost savings from a 20% cycle reduction

Using Real Case 1, a 20% reduction would change the exact CPP from 25.375 to 20.30. This is a proposed improvement, not a measured result.

```text
Improved daily cycles = 3,325,952,000,000 × 0.80 = 2,660,761,600,000
Improved processor time = 1,385.8133 × 0.80 ≈ 1,108.65 seconds/day
Time saved = 1,385.8133 × 0.20 ≈ 277.16 seconds/day
```

The electricity saving depends on what happens during the saved time:

| Power-use assumption | Estimated annual electricity saving |
|---|---|
| The processor still uses 8 W for 24 hours every day | $0; the annual cost remains about $8.41 |
| The full 8 W can be avoided during the saved processing time | About $0.027, or 2.7 cents |

The second estimate is `277.1627 ÷ 3,600 × 0.008 × $0.12 × 365 ≈ $0.027`. Actual savings depend on how much power the processor uses when idle. Under the 1-million-image alternative, this processing-time saving would be half as large.

A 20% cycle reduction would allow 25% more images to be processed in the same time, because `1 ÷ 0.80 = 1.25`. However, the minimum whole-server count in this calculation remains one before and after the change. No server purchase or rental saving can be calculated from the supplied information.

## 5. Conclusion and remaining work

Best Case used the fewest cycles and Worst Case used the most. Cache misses were the largest source of waiting within every recorded run. Branch mistakes accounted for most of the extra time in Worst Case compared with Best Case. The results suggest that reducing both kinds of delay is worth testing.

Using the full transcription in `Logs.md`, the report now includes every pixel's calculated path, a check of all 64 output values, instruction counts for every run, and comparisons of possible savings. The assignment evidence is complete in some areas and still partial in others:

| Requirement | Evidence now included | Status |
|---|---|---|
| At least five experiments | Four recorded runs, each linked to its log and screenshots | One more complete run needed |
| Instruction-by-instruction cycle record | Instruction costs, execution counts, and calculated pixel paths | Partial: actual delay order and per-step cycle totals were not saved |
| Registers, memory values, and PC progression | Final registers, all input/output pixels, and paths reconstructed from the code | Partial: intermediate screenshots or a recorded step history still needed |
| Cache and branch events for each iteration | Recorded totals and the delays they explain | Individual event positions still missing |
| Performance data | Total cycles, CPP, cache miss rate, and branch misprediction rate | Complete for four runs; spills assessed from code because no counter is provided |
| Compare at least three optimizations | Three methods and their calculated possible savings | Measured improved runs and a confirmed best method still needed |
| Image scaling, daily workload, and cost impact | Calculations in Section 4 with stated assumptions | Covered as estimates |

The next complete run should have a new ID and a step record with these fields:

```text
Run ID | Pixel number | Executed PC | Next PC | Cycles added | Running cycles
R0 | R1 | R3 | R4 | Output written | Cache hit/miss | Branch correct/incorrect
```

A new run can provide its own missing event history, but it cannot recover the random events from an earlier run. At least one additional complete run and measured tests of three changed versions are still needed. These should be added as new evidence, keeping the four original logs available for comparison.

## Appendix A: screenshots of the recorded results

The following figures show final registers, output pixels, and detailed metrics. Links to the controls and summary screenshots are in Section 1.1.

### Best Case

![Best Case final registers, output pixels, and detailed metrics](Screenshots/BC-2.png)

### Worst Case

![Worst Case final registers, output pixels, and detailed metrics](Screenshots/WC-2.png)

### Real Case 1

![Real Case 1 final registers, output pixels, and detailed metrics](Screenshots/RC1-2.png)

### Real Case 2

![Real Case 2 final registers, output pixels, and detailed metrics](Screenshots/RC2-2.png)

## Appendix B: reconstructed pixel-by-pixel paths

These tables use the input and output lists in `Logs.md`, read left to right across the first row and then the second. They are a calculation from the final-state logs and the program, not a recording of each instruction's actual timing.

For pixel number `n`, R1 is `1023 + n` when the pixel is loaded. After that pixel is processed, R0 is `n` and R1 is `1024 + n`. R3 holds the input; R4 holds the output. The last pixel in every run therefore ends with R0 = 16 and R1 = 1040, matching the logs.

- **Dark path:** `0x08 → 0x0C → 0x10 → 0x1C → 0x20 → 0x24 → 0x28 → 0x2C → 0x30`, costing 13 cycles before delays.
- **Bright path:** `0x08 → 0x0C → 0x10 → 0x14 → 0x18 → 0x20 → 0x24 → 0x28 → 0x2C → 0x30`, costing 15 cycles before delays.

Both paths return to `0x08` after pixels 1–15 and end at `0x34` after pixel 16. A dark path means the brightness branch is taken; it does not by itself show whether the prediction was correct.

The running instruction total includes the 2 setup cycles and excludes all cache and branch delays. Actual running cycle totals cannot be reconstructed without knowing where those delays occurred.

### B.1 Best Case

Source: [Run 1 log](Logs.md#run-1-best-case-all-pixels-0). All inputs are zero by the test-case definition; the black input cells are not readable individually.

| Pixel | Input (R3) | Output (R4) | Path | Instruction cycles for pixel | Running instruction total |
|---|---|---|---|---|---|
| 1 | 0 | 32 | Dark | 13 | 15 |
| 2 | 0 | 32 | Dark | 13 | 28 |
| 3 | 0 | 32 | Dark | 13 | 41 |
| 4 | 0 | 32 | Dark | 13 | 54 |
| 5 | 0 | 32 | Dark | 13 | 67 |
| 6 | 0 | 32 | Dark | 13 | 80 |
| 7 | 0 | 32 | Dark | 13 | 93 |
| 8 | 0 | 32 | Dark | 13 | 106 |
| 9 | 0 | 32 | Dark | 13 | 119 |
| 10 | 0 | 32 | Dark | 13 | 132 |
| 11 | 0 | 32 | Dark | 13 | 145 |
| 12 | 0 | 32 | Dark | 13 | 158 |
| 13 | 0 | 32 | Dark | 13 | 171 |
| 14 | 0 | 32 | Dark | 13 | 184 |
| 15 | 0 | 32 | Dark | 13 | 197 |
| 16 | 0 | 32 | Dark | 13 | 210 |

Final reconciliation: `210 + (3 × 47) + (0 × 15) = 351 cycles`. The zero incorrect predictions establish that every brightness prediction was correct in this run. The positions of the three cache misses remain unknown.

### B.2 Worst Case

Source: [Run 2 log](Logs.md#run-2-worst-case-alternating).

| Pixel | Input (R3) | Output (R4) | Path | Instruction cycles for pixel | Running instruction total |
|---|---|---|---|---|---|
| 1 | 64 | 96 | Dark | 13 | 15 |
| 2 | 192 | 184 | Bright | 15 | 30 |
| 3 | 64 | 96 | Dark | 13 | 43 |
| 4 | 192 | 184 | Bright | 15 | 58 |
| 5 | 64 | 96 | Dark | 13 | 71 |
| 6 | 192 | 184 | Bright | 15 | 86 |
| 7 | 64 | 96 | Dark | 13 | 99 |
| 8 | 192 | 184 | Bright | 15 | 114 |
| 9 | 64 | 96 | Dark | 13 | 127 |
| 10 | 192 | 184 | Bright | 15 | 142 |
| 11 | 64 | 96 | Dark | 13 | 155 |
| 12 | 192 | 184 | Bright | 15 | 170 |
| 13 | 64 | 96 | Dark | 13 | 183 |
| 14 | 192 | 184 | Bright | 15 | 198 |
| 15 | 64 | 96 | Dark | 13 | 211 |
| 16 | 192 | 184 | Bright | 15 | 226 |

Final reconciliation: `226 + (3 × 47) + (9 × 15) = 502 cycles`. The exact pixels affected by the three cache misses and nine incorrect predictions are not recorded.

### B.3 Real Case 1

Source: [Run 3 log](Logs.md#run-3-real-case-1-70-dark).

| Pixel | Input (R3) | Output (R4) | Path | Instruction cycles for pixel | Running instruction total |
|---|---|---|---|---|---|
| 1 | 35 | 67 | Dark | 13 | 15 |
| 2 | 180 | 172 | Bright | 15 | 30 |
| 3 | 42 | 74 | Dark | 13 | 43 |
| 4 | 60 | 92 | Dark | 13 | 56 |
| 5 | 210 | 202 | Bright | 15 | 71 |
| 6 | 88 | 120 | Dark | 13 | 84 |
| 7 | 50 | 82 | Dark | 13 | 97 |
| 8 | 115 | 147 | Dark | 13 | 110 |
| 9 | 230 | 222 | Bright | 15 | 125 |
| 10 | 45 | 77 | Dark | 13 | 138 |
| 11 | 72 | 104 | Dark | 13 | 151 |
| 12 | 195 | 187 | Bright | 15 | 166 |
| 13 | 30 | 62 | Dark | 13 | 179 |
| 14 | 95 | 127 | Dark | 13 | 192 |
| 15 | 80 | 112 | Dark | 13 | 205 |
| 16 | 140 | 132 | Bright | 15 | 220 |

Final reconciliation: `220 + (3 × 47) + (3 × 15) = 406 cycles`. The exact pixels affected by the three cache misses and three incorrect predictions are not recorded.

### B.4 Real Case 2

Source: [Run 4 log](Logs.md#run-4-real-case-2-clustered). Inputs at pixels 9 and 12 remain marked as inferred from the output, as in `Logs.md`.

| Pixel | Input (R3) | Output (R4) | Path | Instruction cycles for pixel | Running instruction total |
|---|---|---|---|---|---|
| 1 | 236 | 228 | Bright | 15 | 17 |
| 2 | 209 | 201 | Bright | 15 | 32 |
| 3 | 228 | 220 | Bright | 15 | 47 |
| 4 | 200 | 192 | Bright | 15 | 62 |
| 5 | 217 | 209 | Bright | 15 | 77 |
| 6 | 222 | 214 | Bright | 15 | 92 |
| 7 | 238 | 230 | Bright | 15 | 107 |
| 8 | 228 | 220 | Bright | 15 | 122 |
| 9 | 6 (inferred) | 38 | Dark | 13 | 135 |
| 10 | 78 | 110 | Dark | 13 | 148 |
| 11 | 56 | 88 | Dark | 13 | 161 |
| 12 | 6 (inferred) | 38 | Dark | 13 | 174 |
| 13 | 47 | 79 | Dark | 13 | 187 |
| 14 | 11 | 43 | Dark | 13 | 200 |
| 15 | 25 | 57 | Dark | 13 | 213 |
| 16 | 60 | 92 | Dark | 13 | 226 |

Final reconciliation: `226 + (4 × 47) + (2 × 15) = 444 cycles`. The exact pixels affected by the four cache misses and two incorrect predictions are not recorded.
