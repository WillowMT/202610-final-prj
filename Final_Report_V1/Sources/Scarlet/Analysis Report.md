# Analysis report: CPU instruction execution (Runs 5–8)

## Introduction

This report examines how the CPU simulator adjusts image brightness. A pixel below 128 is increased by 32; a pixel at or above 128 is reduced by 8. It covers four new runs (Runs 5–8), one for each test case, and compares them with the group's earlier Runs 1–4 of the same cases. Together, the two sets give eight complete experiments, which covers the assignment's requirement of at least five.

The evidence comes from the [transcribed run logs](Logs.md), the [data collection sheet](data-collection-template.md), the [Excel workbook](Data%20Collection%20Sheet.xlsx), and twelve saved screenshots. The [project scenario](Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md) gives the requirements, and the [simulator code](Project1_CPU_Simulator.html) is used to check how instructions and delays are counted.

## 1. Instruction trace and experiment evidence

### 1.1 Recorded experiments

All four runs completed 16 pixels at 500 ms per animation step. Each set of three screenshots is one run.

| Experiment | Run ID | Test case | Total cycles | Text log | Top screen | Registers | Pixels and detailed metrics |
|---|---|---|---|---|---|---|---|
| 5 | BC-500-R2 | Best: all pixels are 0 | 413 | [Run 5](Logs.md#run-5-best-case-all-pixels-0) | [BC-R2-1](Screenshots/BC-R2-1.png) | [BC-R2-2](Screenshots/BC-R2-2.png) | [BC-R2-3](Screenshots/BC-R2-3.png) |
| 6 | WC-500-R2 | Worst: alternating 64 and 192 | 504 | [Run 6](Logs.md#run-6-worst-case-alternating) | [WC-R2-1](Screenshots/WC-R2-1.png) | [WC-R2-2](Screenshots/WC-R2-2.png) | [WC-R2-3](Screenshots/WC-R2-3.png) |
| 7 | RC1-500-R2 | Real Case 1: 70% dark | 436 | [Run 7](Logs.md#run-7-real-case-1-70-dark) | [RC1-R2-1](Screenshots/RC1-R2-1.png) | [RC1-R2-2](Screenshots/RC1-R2-2.png) | [RC1-R2-3](Screenshots/RC1-R2-3.png) |
| 8 | RC2-500-R2 | Real Case 2: clustered | 459 | [Run 8](Logs.md#run-8-real-case-2-clustered) | [RC2-R2-1](Screenshots/RC2-R2-1.png) | [RC2-R2-2](Screenshots/RC2-R2-2.png) | [RC2-R2-3](Screenshots/RC2-R2-3.png) |

The screenshots show final states only. They do not record each instruction as it happened, so the positions of individual cache misses and branch mistakes are unknown.

### 1.2 Instruction sequence and cycle costs

The program counter (PC) holds the address of the next instruction. Registers are small storage locations inside the CPU. R0 counts processed pixels, R1 holds the pixel address, R2 holds the threshold 128, R3 holds the current pixel, R4 holds the adjusted value, R6 holds 32 and R7 holds 8.

| PC | Instruction | Purpose | Cycles before extra delays |
|---|---|---|---|
| 0x00 | `LOAD R0, #0` | Start the pixel counter at zero | 1 |
| 0x04 | `LOAD R1, #1024` | Set the first pixel address | 1 |
| 0x08 | `LOAD R3, [R1]` | Read the current pixel from memory | 3; add 47 for a cache miss |
| 0x0C | `CMP R3, R2` | Compare the pixel with 128 | 1 |
| 0x10 | `BLT DARK` | Jump to the dark path if the pixel is below 128 | 1; add 15 for an incorrect prediction |
| 0x14 | `SUB R4, R3, R7` | Subtract 8 from a bright pixel | 1 |
| 0x18 | `JMP STORE` | Skip the dark-pixel calculation | 2 |
| 0x1C | `ADD R4, R3, R6` | Add 32 to a dark pixel | 1 |
| 0x20 | `STORE R4, [R1]` | Save the adjusted pixel | 3 |
| 0x24 | `INC R1, #1` | Move to the next pixel address | 1 |
| 0x28 | `INC R0, #1` | Count one more pixel | 1 |
| 0x2C | `CMP R0, #16` | Check whether 16 pixels are done | 1 |
| 0x30 | `BNE LOOP` | Repeat until all pixels are done | 1 |
| 0x34 | `HALT` | Stop position | Not counted by this simulator version |

The two possible paths for one pixel are:

```text
Dark:   08 → 0C → 10 → 1C → 20 → 24 → 28 → 2C → 30
Cycles:  3 +  1 +  1 +  1 +  3 +  1 +  1 +  1 +  1 = 13

Bright: 08 → 0C → 10 → 14 → 18 → 20 → 24 → 28 → 2C → 30
Cycles:  3 +  1 +  1 +  1 +  2 +  3 +  1 +  1 +  1 +  1 = 15
```

A bright pixel costs 2 more cycles because it needs the extra `JMP`. For a complete 16-pixel run:

```text
Instruction cycles = 2 setup cycles + 13 × dark pixels + 15 × bright pixels
```

### 1.3 Registers and pixel output

At completion, every run shows R0 = 16 (`0x10`) and R1 = 1040 (`0x410`): the counter reached 16 and the address moved forward 16 times from 1024. R2 = 128, R6 = 32 and R7 = 8 are visible in all four register screenshots.

| Case | Final input in R3 | Final output in R4 | Check |
|---|---|---|---|
| Best | 0 (`0x00`) | 32 (`0x20`) | 0 + 32 = 32 |
| Worst | 192 (`0xC0`) | 184 (`0xB8`) | 192 − 8 = 184 |
| Real Case 1 | 140 (`0x8C`) | 132 (`0x84`) | 140 − 8 = 132 |
| Real Case 2 | 55 (`0x37`) | 87 (`0x57`) | 55 + 32 = 87 |

In every run, the execution summary names `0x30 BNE LOOP` as the last instruction while the PC display shows `0x34`. These agree: the final loop check has finished and the PC has moved to the stop position.

### 1.4 Cache and branch events

The simulator gives each pixel read about an 80% chance of a cache hit; a miss adds 47 cycles. For the brightness decision (`BLT`), the chance of a correct prediction is set by the test case: 95% for Best, 50% for Worst and 80% for both real cases. These are random draws, not a predictor learning the pixel pattern. The loop check (`BNE`) is always counted as correct.

Each run has 32 counted branches: 16 brightness decisions and 16 loop checks. All mistakes therefore belong to the brightness decision:

| Case | Correct brightness predictions (of 16) | Correct loop checks (of 16) | Incorrect predictions |
|---|---|---|---|
| Best | 15 | 16 | 1 |
| Worst | 10 | 16 | 6 |
| Real Case 1 | 11 | 16 | 5 |
| Real Case 2 | 13 | 16 | 3 |

Best Case had one incorrect prediction in this run even though every pixel follows the same path. This comes from the simulator's fixed 95% chance, not from the data, and shows that the results include randomness.

### 1.5 Instruction counts reconstructed from the logs

A value below 128 follows the dark path; any other value follows the bright path. Counting the paths gives the number of times each instruction runs:

| Instruction | Best | Worst | Real Case 1 | Real Case 2 |
|---|---|---|---|---|
| 0x00 and 0x04: setup | 2 | 2 | 2 | 2 |
| 0x08, 0x0C, 0x10: load, compare, decide | 16 each | 16 each | 16 each | 16 each |
| 0x14: subtract 8 | 0 | 8 | 5 | 8 |
| 0x18: jump after subtraction | 0 | 8 | 5 | 8 |
| 0x1C: add 32 | 16 | 8 | 11 | 8 |
| 0x20 to 0x30: store and loop control | 16 each | 16 each | 16 each | 16 each |
| Total executed instructions, excluding HALT | 146 | 154 | 151 | 154 |
| Instruction cycles before delays | 210 | 226 | 220 | 226 |

Adding the recorded delays reproduces all four totals exactly:

```text
Best:        210 + (4 × 47) + (1 × 15) = 210 + 203 = 413
Worst:       226 + (4 × 47) + (6 × 15) = 226 + 278 = 504
Real Case 1: 220 + (3 × 47) + (5 × 15) = 220 + 216 = 436
Real Case 2: 226 + (4 × 47) + (3 × 15) = 226 + 233 = 459
```

## 2. Performance data

### 2.1 Recorded results

Cycles per pixel (CPP) is total cycles divided by 16. A stall is extra waiting caused by a cache miss or an incorrect branch prediction.

| Metric | Best | Worst | Real Case 1 | Real Case 2 |
|---|---|---|---|---|
| Total cycles | 413 | 504 | 436 | 459 |
| CPP | 25.81 | 31.50 | 27.25 | 28.69 |
| Cache hits / misses | 12 / 4 | 12 / 4 | 13 / 3 | 12 / 4 |
| Cache miss rate | 25.0% | 25.0% | 18.8% | 25.0% |
| Correct branches / total | 31 / 32 | 26 / 32 | 27 / 32 | 29 / 32 |
| Branch misprediction rate | 3.1% | 18.8% | 15.6% | 9.4% |
| Stall cycles | 203 | 278 | 216 | 233 |
| Register spills | 0 (from code) | 0 (from code) | 0 (from code) | 0 (from code) |

A register spill means moving a register value to memory because there are not enough registers. The program uses only eight registers of the 32 available and contains no spill instructions, so there are zero spills. The simulator has no spill counter, so this is a finding from the code rather than a measurement.

### 2.2 Explaining the cycle totals

```text
Total cycles = instruction cycles + (cache misses × 47) + (incorrect predictions × 15)
```

| Case | Dark | Bright | Instruction cycles | Cache delay | Branch delay | Total |
|---|---|---|---|---|---|---|
| Best | 16 | 0 | 210 | 188 | 15 | 413 |
| Worst | 8 | 8 | 226 | 188 | 90 | 504 |
| Real Case 1 | 11 | 5 | 220 | 141 | 75 | 436 |
| Real Case 2 | 8 | 8 | 226 | 188 | 45 | 459 |

Cache misses were the largest source of delay in every run. Best and Worst Case had the same cache delay (188 cycles), so the 91-cycle difference between them comes from branch mistakes (90 − 15 = 75 cycles) and the bright pixels' extra jumps (16 cycles): `75 + 16 = 91`. Worst Case used about 22.0% more cycles than Best Case.

Real Case 1 had one fewer cache miss than the others, which saved 47 cycles, but five branch mistakes. Real Case 2 is clustered (8 bright, then 8 dark), so its pattern changes only once. It had fewer branch mistakes than Worst Case (3 against 6) despite having the same 8/8 split.

### 2.3 Comparison with the assignment targets

All four CPP values are far above the target of fewer than 5 cycles per pixel. Even with no delays at all, this program needs 13 cycles for a dark pixel and 15 for a bright pixel, so the target cannot be reached without changing the program. The cache hit rates (75.0% to 81.3%) are below the target of more than 95%. Branch accuracy exceeds the 90% target in Best Case (96.9%) and Real Case 2 (90.6%), but not in Worst Case (81.3%) or Real Case 1 (84.4%).

### 2.4 Checking all recorded output pixels

All 64 output values in `Logs.md` follow the brightness rule (below 128: +32; otherwise: −8).

| Run | Dark pixels | Bright pixels | Outputs consistent with the rule |
|---|---|---|---|
| Best | 16 | 0 | 16 / 16 |
| Worst | 8 | 8 | 16 / 16 |
| Real Case 1 | 11 | 5 | 16 / 16 |
| Real Case 2 | 8 | 8 | 16 / 16 |

Best Case's black input cells are recorded as zero from the test-case definition. Real Case 2's input at pixel 15 is recorded as 8 because its output is 40 and `40 − 32 = 8`; the other 15 Real Case 2 inputs are readable.

### 2.5 Comparison with Runs 1–4 (repeat runs)

Because each test case has now been run twice, the effect of the simulator's randomness can be seen directly.

| Case | Runs 1–4 total (50 ms) | Runs 5–8 total (500 ms) | Difference | Average of two runs | Same instruction cycles? |
|---|---|---|---|---|---|
| Best | 351 | 413 | +62 | 382.0 | Yes: 210 |
| Worst | 502 | 504 | +2 | 503.0 | Yes: 226 |
| Real Case 1 | 406 | 436 | +30 | 421.0 | Yes: 220 |
| Real Case 2 | 444 | 459 | +15 | 451.5 | Yes: 226 (different random pixels, same 8/8 split) |

The instruction cycles are identical for each case, because they depend only on the pixel pattern. Every difference comes from the random delays:

- Best: one more cache miss (+47) and one branch mistake (+15), so `47 + 15 = 62`.
- Worst: one more cache miss (+47) and three fewer branch mistakes (−45), so `47 − 45 = 2`.
- Real Case 1: the same cache misses, two more branch mistakes: `2 × 15 = 30`.
- Real Case 2: the same cache misses, one more branch mistake: `15`.

This confirms two things. First, the animation speed (50 ms or 500 ms) does not affect the results. Second, a single run is only an example; averages over several runs give a fairer comparison. On the averages, the ranking is unchanged: Best < Real Case 1 < Real Case 2 < Worst.

## 3. Optimization analysis

The supplied simulator cannot run changed programs, so none of the results below are measured. Each is a calculation from the recorded runs and the instruction costs, with its assumptions stated.

### 3.1 Three proposed methods

| Method | How it helps | Most relevant cases | Limitation |
|---|---|---|---|
| Cache prefetching | Fetch upcoming pixels into the cache before they are needed, so the CPU does not wait. | All cases, since cache delays were the largest in every run. | Adds some work; the first read may still miss. The simulator has no prefetch control. |
| Branch-free code | Replace the `BLT`/`SUB`/`JMP`/`ADD` decision with a conditional select, so there is no brightness jump to predict. | Worst Case and Real Case 1, which had the most branch mistakes. | Every pixel now does both calculations, which costs a cycle more than the dark path. |
| Loop unrolling | Handle four pixels per loop pass, so the counter update, check and repeat run 4 times instead of 16. | All cases equally. | Longer program; does not remove the brightness decision on its own. |

### 3.2 How each saving is calculated

**Prefetching.** The 16 pixels are 16 bytes stored next to each other, which fit in one typical 64-byte cache line. With prefetching, a realistic best outcome is one unavoidable miss at the start. Estimated saving = `(recorded misses − 1) × 47`.

**Branch-free code.** On ARM processors (the scenario's CPU), a conditional select instruction such as `CSEL` chooses between two values without jumping. One possible version per pixel:

```text
ADD  R4, R3, R6        ; dark result   (1 cycle)
SUB  R5, R3, R7        ; bright result (1 cycle)
CMP  R3, R2            ;               (1 cycle)
CSEL R4, R5, R4, GE    ; pick bright result if pixel ≥ 128 (assumed 1 cycle)
```

This replaces the dark path's 3 decision cycles and the bright path's 5 with 4 cycles for every pixel. Each pixel then costs `3 + 4 + 3 + 1 + 1 + 1 + 1 = 14` cycles, so a 16-pixel run costs `2 + 16 × 14 = 226` instruction cycles, with no brightness mispredictions. The loop check is still counted as always correct.

**Loop unrolling.** If the counter update, counter compare and repeat each cost 1 cycle but run 4 times instead of 16, the saving is `3 × (16 − 4) = 36` cycles.

### 3.3 Estimated results for each run

Each cell shows the estimated total and the change from the recorded total. Only the "Recorded" column is a measured result.

| Case | Recorded | Prefetching (1 miss left) | Branch-free code | Loop unrolling (−36) |
|---|---|---|---|---|
| Best | 413 | 272 (−34.1%) | 414 (+0.2%) | 377 (−8.7%) |
| Worst | 504 | 363 (−28.0%) | 414 (−17.9%) | 468 (−7.1%) |
| Real Case 1 | 436 | 342 (−21.6%) | 367 (−15.8%) | 400 (−8.3%) |
| Real Case 2 | 459 | 318 (−30.7%) | 414 (−9.8%) | 423 (−7.8%) |

The branch-free column is calculated as `226 + recorded cache delay`.

### 3.4 Which method works best for which case

- **Prefetching gives the largest estimated saving in every case**, because cache misses were the biggest delay in all four runs.
- **Branch-free code depends on the data.** It helps most when the pattern is hard to predict (Worst Case, −17.9%; Real Case 1, −15.8%). In Best Case it makes things slightly worse (+0.2%), because the predictor was almost always right and the branch-free version adds a cycle to every dark pixel. This is the key trade-off: removing branches only pays off when they are frequently mispredicted.
- **Loop unrolling gives a small, steady saving** (about 7–9%) in every case, since all cases repeat the same loop checks.

The methods can also be combined. For Worst Case, prefetching plus branch-free code plus unrolling would give an estimated `226 − 36 + 47 = 237` cycles, less than half of the recorded 504. This is a calculation, not a measured result.

To measure these properly, each changed version should process the same pixel lists, produce the same outputs, and be repeated several times because of the simulator's random outcomes.

## 4. Extrapolation and cost impact

### 4.1 Assumptions

- One image = 256 × 256 = 65,536 pixels.
- 2,000,000 processed images per day, as requested in the deliverables.
- One 2.4 GHz processor per server, used only for this task.
- 8 W processor power, electricity at $0.12 per kWh, 365 days per year.
- A four-hour completion deadline (the scenario's service-level agreement, SLA).

The scenario also says 50% of uploaded images need adjustment; that halves every daily figure below. These estimates cover only the brightness instructions, not file handling or whole-server power.

### 4.2 Cycles for a 256 × 256 image

```text
Number of 16-pixel groups = 65,536 ÷ 16 = 4,096
Estimated image cycles = recorded 16-pixel total × 4,096
```

| Case | Cycles for 16 pixels | Estimated cycles per image |
|---|---|---|
| Best | 413 | 1,691,648 |
| Worst | 504 | 2,064,384 |
| Real Case 1 | 436 | 1,785,856 |
| Real Case 2 | 459 | 1,880,064 |

These match the simulator's displayed estimates. They assume the 16-pixel sample's average cost continues across the whole image.

### 4.3 Total cycles for 2 million images per day

At 2.4 GHz the processor completes 2,400,000,000 cycles per second.

```text
Daily cycles = cycles per image × 2,000,000
Processor time (s) = daily cycles ÷ 2,400,000,000
```

| Case | Cycles per day | Processor time per day |
|---|---|---|
| Best | 3,383,296,000,000 | 1,409.71 s (23.50 min) |
| Worst | 4,128,768,000,000 | 1,720.32 s (28.67 min) |
| Real Case 1 | 3,571,712,000,000 | 1,488.21 s (24.80 min) |
| Real Case 2 | 3,760,128,000,000 | 1,566.72 s (26.11 min) |

Real Case 1 is used as the worked example below, as the most realistic photo pattern.

### 4.4 Electricity cost for 24-hour operation

```text
8 W = 0.008 kW
Daily energy = 0.008 × 24 = 0.192 kWh
Daily cost = 0.192 × $0.12 = $0.02304
Annual cost = $0.02304 × 365 ≈ $8.41
```

This is the cost of running one processor at 8 W all day. The part used only by Real Case 1's processing time is:

```text
Energy = (1,488.21 ÷ 3,600) × 0.008 ≈ 0.003307 kWh/day
Cost ≈ 0.003307 × $0.12 ≈ $0.000397/day, about $0.145 per year
```

### 4.5 Server count for the four-hour deadline

Four hours = 14,400 seconds.

```text
Servers needed = processor time ÷ 14,400, rounded up
```

For Real Case 1: `1,488.21 ÷ 14,400 ≈ 0.103`, which rounds up to **one server**. Even Worst Case needs only `1,720.32 ÷ 14,400 ≈ 0.119` of one server's four-hour capacity. So one server is enough for the brightness calculation alone in all cases. A real service would need more, for larger photos, file handling and spare capacity.

### 4.6 Annual savings from a 20% cycle reduction

For Real Case 1, a 20% reduction lowers CPP from 27.25 to 21.80 (a proposed improvement, not measured).

```text
Improved daily cycles = 3,571,712,000,000 × 0.80 = 2,857,369,600,000
Improved processor time = 1,488.21 × 0.80 ≈ 1,190.57 s/day
Time saved ≈ 297.64 s/day
```

| Power-use assumption | Estimated annual electricity saving |
|---|---|
| Processor stays at 8 W for 24 hours regardless | $0 (the annual cost stays about $8.41) |
| The full 8 W is avoided during the saved time | `297.64 ÷ 3,600 × 0.008 × $0.12 × 365` ≈ $0.029 |

A 20% cycle reduction also lets the same server process 25% more images in the same time (`1 ÷ 0.80 = 1.25`). At this scale the server count stays at one, so no hardware saving can be calculated from the information given. The savings become significant only at much larger scale, for example with full-size photos or many more images, where the number of servers is above one.

## 5. Conclusion

Best Case used the fewest cycles (413) and Worst Case the most (504). Cache misses were the largest source of waiting in every run. Branch mistakes were the main reason Worst Case took longer than Best Case, since their cache delays were equal.

Repeating each test case (Runs 1–4 and 5–8) showed that instruction cycles stay the same for each case while the random delays change the totals by between 2 and 62 cycles. The ranking of the cases stayed the same on the averages.

The estimates suggest prefetching would help most in every case, branch-free code helps only when branches are often mispredicted, and loop unrolling gives a small saving everywhere.

| Requirement | Evidence | Status |
|---|---|---|
| At least five experiments | Runs 5–8 here, plus Runs 1–4 | Covered: eight complete runs |
| Instruction-by-instruction record | Costs, paths, instruction counts, Appendix B | Partial: a STEP FORWARD trace of individual delays is still to be recorded |
| Registers, memory values, PC | Final registers, all pixels, reconstructed paths | Covered for final state |
| Cache and branch events per iteration | Totals per run | Partial: positions of individual events not recorded |
| Performance data | Cycles, CPP, miss rate, misprediction rate, spills | Covered |
| Compare three optimizations | Three methods with calculated estimates per case | Covered as estimates; not measured |
| Scaling and cost | Section 4 | Covered as estimates |

## Appendix A: screenshots

### Best Case

![Best Case summary](Screenshots/BC-R2-1.png)
![Best Case registers and pixels](Screenshots/BC-R2-2.png)
![Best Case detailed metrics](Screenshots/BC-R2-3.png)

### Worst Case

![Worst Case summary](Screenshots/WC-R2-1.png)
![Worst Case registers](Screenshots/WC-R2-2.png)
![Worst Case pixels and detailed metrics](Screenshots/WC-R2-3.png)

### Real Case 1

![Real Case 1 summary](Screenshots/RC1-R2-1.png)
![Real Case 1 registers and pixels](Screenshots/RC1-R2-2.png)
![Real Case 1 pixels and detailed metrics](Screenshots/RC1-R2-3.png)

### Real Case 2

![Real Case 2 summary](Screenshots/RC2-R2-1.png)
![Real Case 2 registers](Screenshots/RC2-R2-2.png)
![Real Case 2 pixels and detailed metrics](Screenshots/RC2-R2-3.png)

## Appendix B: reconstructed pixel-by-pixel paths

These tables use the input and output lists in `Logs.md`, read left to right across row 1 and then row 2. They are calculated from the final state and the program, not recorded step by step. The running total includes the 2 setup cycles and excludes cache and branch delays, because the positions of those delays were not recorded.

For pixel `n`, R1 is `1023 + n` when the pixel is loaded. After the pixel is processed, R0 is `n` and R1 is `1024 + n`.

### B.5 Best Case (Run 5)

| Pixel | Input (R3) | Output (R4) | Path | Cycles for pixel | Running instruction total |
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

Reconciliation: `210 + (4 × 47) + (1 × 15) = 413`.

### B.6 Worst Case (Run 6)

| Pixel | Input (R3) | Output (R4) | Path | Cycles for pixel | Running instruction total |
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

Reconciliation: `226 + (4 × 47) + (6 × 15) = 504`.

### B.7 Real Case 1 (Run 7)

| Pixel | Input (R3) | Output (R4) | Path | Cycles for pixel | Running instruction total |
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

Reconciliation: `220 + (3 × 47) + (5 × 15) = 436`.

### B.8 Real Case 2 (Run 8)

| Pixel | Input (R3) | Output (R4) | Path | Cycles for pixel | Running instruction total |
|---|---|---|---|---|---|
| 1 | 215 | 207 | Bright | 15 | 17 |
| 2 | 210 | 202 | Bright | 15 | 32 |
| 3 | 254 | 246 | Bright | 15 | 47 |
| 4 | 221 | 213 | Bright | 15 | 62 |
| 5 | 231 | 223 | Bright | 15 | 77 |
| 6 | 244 | 236 | Bright | 15 | 92 |
| 7 | 220 | 212 | Bright | 15 | 107 |
| 8 | 236 | 228 | Bright | 15 | 122 |
| 9 | 39 | 71 | Dark | 13 | 135 |
| 10 | 27 | 59 | Dark | 13 | 148 |
| 11 | 41 | 73 | Dark | 13 | 161 |
| 12 | 71 | 103 | Dark | 13 | 174 |
| 13 | 80 | 112 | Dark | 13 | 187 |
| 14 | 92 | 124 | Dark | 13 | 200 |
| 15 | 8 (deduced) | 40 | Dark | 13 | 213 |
| 16 | 55 | 87 | Dark | 13 | 226 |

Reconciliation: `226 + (4 × 47) + (3 × 15) = 459`.
