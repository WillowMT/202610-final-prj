# Next steps after running the simulator

This report answers the six questions in the project's quick guide. It uses the four completed runs in the [transcribed logs](Logs.md), the [data collection sheet](data-collection-template.md), the [Excel workbook](Data%20Collection%20Sheet.xlsx), and the saved screenshots. The results are from a teaching simulator rather than a physical processor.

## 1. Collect data

Each test case processed all 16 pixels at an animation setting of 50 ms per step. Cycles per pixel (CPP) means the average number of CPU cycles used to process one pixel. A lower CPP is better.

| Test case | Total cycles | CPP | Cache hits / misses | Cache hit rate | Stall cycles | Correct branches / total | Branch accuracy |
|---|---|---|---|---|---|---|---|
| Best: all 0 | 351 | 21.94 | 13 / 3 | 81.3% | 141 | 32 / 32 | 100.0% |
| Worst: alternating | 502 | 31.38 | 13 / 3 | 81.3% | 276 | 23 / 32 | 71.9% |
| Real Case 1: 70% dark | 406 | 25.38 | 13 / 3 | 81.3% | 186 | 29 / 32 | 90.6% |
| Real Case 2: clustered | 444 | 27.75 | 12 / 4 | 75.0% | 218 | 30 / 32 | 93.8% |

CPP is shown to two decimal places, as in the detailed screenshots. The data collection sheet shows it to one decimal place. Calculations below use total cycles divided by 16 before rounding.

The animation setting controls how quickly the instructions appear on screen. It is not the processor's clock speed.

The full logs also provide each run's input/output pixel lists and final registers. All 64 output entries are consistent with the brightness rule. Best Case's zero inputs come from the test-case definition, and two Real Case 2 input values are inferred from their outputs, as labelled in `Logs.md`. The main report's [pixel-by-pixel appendix](Analysis%20Report.md#appendix-b-reconstructed-pixel-by-pixel-paths) shows the calculated paths and instruction costs.

## 2. Why did each case perform differently?

The program adds 32 to a dark pixel and subtracts 8 from a bright pixel. The bright-pixel path also includes an extra jump instruction, which costs 2 cycles. The cases therefore differ in both their instruction costs and their delays.

A cache is a small, fast memory area. A cache miss adds 47 cycles in this simulator. A branch is a choice about which instruction to execute next; an incorrect branch prediction adds 15 cycles.

| Test case | Instruction cycles before delays | Cache delay cycles | Branch delay cycles | Total cycles |
|---|---|---|---|---|
| Best | 210 | 141 | 0 | 351 |
| Worst | 226 | 141 | 135 | 502 |
| Real Case 1 | 220 | 141 | 45 | 406 |
| Real Case 2 | 226 | 188 | 30 | 444 |

- Best Case had no incorrect branch predictions in the recorded run. All 16 pixels followed the shorter, dark-pixel path, so it used the fewest cycles.
- Worst Case had nine incorrect predictions, which added 135 cycles. Its eight bright pixels also added 16 instruction cycles compared with Best Case. Together, these explain the 151-cycle difference: `135 + 16 = 151`.
- Real Case 1 had three incorrect predictions and five bright pixels. It used `45 + 10 = 55` more cycles than Best Case.
- Real Case 2 had fewer branch mistakes than Real Case 1, but one extra cache miss and three more bright pixels. The difference was `47 − 15 + 6 = 38` cycles, so Real Case 2 still took longer.

The simulator uses random outcomes for cache hits and branch predictions. It gives different test cases different chances of a correct branch prediction, but it does not actually learn a pixel pattern. The explanations above describe these four recorded runs; another run may produce different totals.

## 3. What is the main bottleneck?

**Cache misses caused the largest recorded delay in every case.** They added 141 cycles in Best, Worst, and Real Case 1, and 188 cycles in Real Case 2. These amounts were larger than the branch delay in the same runs.

Branch mistakes still explain most of the difference between Best and Worst Case. Their cache delays were equal, while Worst Case had 135 extra branch-delay cycles.

The two findings answer different questions: cache misses were the largest source of waiting within each run, while branch mistakes were the main reason Worst Case took longer than Best Case.

Memory bandwidth means how much data can move to or from memory each second. The simulator does not measure it, so these results cannot establish whether it would limit a real image-processing system.

## 4. How could performance be improved?

The following are proposed improvements. No optimized runs have been recorded, so their actual savings have not yet been measured.

| Method | Explanation | Expected benefit and limitation |
|---|---|---|
| Cache prefetching | Bring upcoming pixel data into the cache before it is needed. | Worth testing for all four cases because cache delays are large. Each fully avoided miss would save 47 delay cycles, but fetching early also takes work and may not prevent every miss. |
| Branch-free code | Select the adjusted pixel value without a jump based on its brightness. | Most relevant to Worst Case, which had nine branch mistakes. Removing those mistakes would avoid 135 delay cycles before accounting for the cost of the replacement instructions. |
| Loop unrolling | Process four pixels before checking whether the loop should repeat. | Reduces repeated loop checks. If the counter update, comparison, and repeat instruction each run 4 times instead of 16, their combined cost falls by 36 cycles. This is a calculation, not a measured result. |

The supplied simulator already counts every loop-repeat decision as correct. Unrolling would therefore save loop instructions in this model, rather than remove loop-prediction mistakes. It would still need a brightness decision for each pixel unless branch-free code was also used.

I would test prefetching across all four cases and branch-free code especially on Worst Case. The comparison should check that the output pixels remain correct and use repeated runs because the simulator includes random outcomes.

Calculations from the logs show how the opportunities differ. If no replacement work were needed, removing all recorded cache delays would reduce cycles by 40.2% in Best Case, 28.1% in Worst Case, 34.7% in Real Case 1, and 42.3% in Real Case 2. Removing only the branch delays would give 0.0%, 26.9%, 11.1%, and 6.8%, respectively. These are possible delay savings, not measured results from changed programs. The full comparison is in [Section 3.3 of the main report](Analysis%20Report.md#33-comparing-the-possible-savings-across-the-four-logs).

## 5. How do the results scale to a 256 × 256 image?

For this calculation, one image is the assignment's 256 × 256 image, containing 65,536 pixels.

```text
Number of 16-pixel groups = 65,536 ÷ 16 = 4,096
Estimated image cycles = total cycles for 16 pixels × 4,096
                       = unrounded CPP × 65,536
```

The quick guide's multiplier of 4,096 applies to the 16-pixel total, not directly to CPP.

| Test case | Total cycles for 16 pixels | Estimated cycles for 256 × 256 pixels |
|---|---|---|
| Best | 351 | 1,437,696 |
| Worst | 502 | 2,056,192 |
| Real Case 1 | 406 | 1,662,976 |
| Real Case 2 | 444 | 1,818,624 |

These values match the simulator's estimates. They assume the same average cost per pixel continues across the larger image, including the small test's setup cost. They are estimates, not measurements from processing a full-size image.

## 6. How much money could be saved per day by reducing CPP by 1?

I use 2,000,000 processed images per day to match the assignment's calculation requirement. Each image contains 65,536 pixels. The stated processor speed is 2.4 GHz, or 2.4 billion cycles per second; power is 8 W; electricity costs $0.12 per kWh.

The scenario also says that only 50% of uploaded images need adjustment. Results for that smaller workload of 1,000,000 processed images are included below.

```text
Cycles saved per image = 1 × 65,536 = 65,536
Daily cycles saved = 65,536 × 2,000,000 = 131,072,000,000
Daily processor time saved = 131,072,000,000 ÷ 2,400,000,000
                           ≈ 54.61 seconds
```

If the processor can avoid using its full 8 W during the saved time:

```text
Energy saved per day = 0.008 kW × (54.6133 ÷ 3,600) hours
                    ≈ 0.00012136 kWh
Cost saved per day = 0.00012136 × $0.12
                  ≈ $0.00001456
```

| Processed images per day | Processor time saved per day | Possible electricity saving per day |
|---|---|---|
| 2,000,000 | 54.61 seconds | $0.00001456 |
| 1,000,000 | 27.31 seconds | $0.00000728 |

These electricity savings depend on reducing power use during the saved time. If the processor stays at 8 W for all 24 hours, its daily electricity cost remains `0.008 × 24 × $0.12 = $0.02304`. Finishing sooner would not reduce that fixed cost.

For Real Case 1, reducing the exact CPP from 25.375 to 24.375 would reduce processing time by about 3.94%. The same processor could then complete about 4.10% more images in the same time. A money saving from buying or renting fewer servers cannot be calculated because no server prices or whole-system workload measurements are provided.

## Sources

- [Logs.md](Logs.md), for the four recorded runs, pixel lists, final registers, and detailed metrics.
- [Quick guide](How%20to%20Use%20Project%201%20CPU%20Simulator%20-%20Quick%20Guide.md), especially "Next Steps After Running Simulator".
- [Project scenario](Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md), for hardware values and workload requirements.
- [Simulator](Project1_CPU_Simulator.html), for instruction costs and how delays are counted.
- [Data collection sheet](data-collection-template.md) and the screenshot references in [Analysis Report.md](Analysis%20Report.md).
