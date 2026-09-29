# Next steps after running the simulator (Runs 5–8)

This report answers the six questions in the project's quick guide, using the four runs in the [transcribed logs](Logs.md), the [data collection sheet](data-collection-template.md) and the [Excel workbook](Data%20Collection%20Sheet.xlsx). The results come from a teaching simulator, not a physical processor.

## 1. Collect data

Each test case processed all 16 pixels at an animation setting of 500 ms per step. Cycles per pixel (CPP) is the average number of CPU cycles used per pixel; lower is better.

| Test case | Total cycles | CPP | Cache hits / misses | Cache hit rate | Stall cycles | Correct branches / total | Branch accuracy |
|---|---|---|---|---|---|---|---|
| Best: all 0 | 413 | 25.81 | 12 / 4 | 75.0% | 203 | 31 / 32 | 96.9% |
| Worst: alternating | 504 | 31.50 | 12 / 4 | 75.0% | 278 | 26 / 32 | 81.3% |
| Real Case 1: 70% dark | 436 | 27.25 | 13 / 3 | 81.3% | 216 | 27 / 32 | 84.4% |
| Real Case 2: clustered | 459 | 28.69 | 12 / 4 | 75.0% | 233 | 29 / 32 | 90.6% |

The animation setting only controls how quickly steps appear on screen. It is not the processor's clock speed, and it does not change any result. Runs 1–4 were recorded at 50 ms per step and show the same instruction cycles for every case.

All 64 output values follow the brightness rule. Best Case's inputs come from the test-case definition (the black cells are unreadable), and one Real Case 2 input is deduced from its output, as labelled in `Logs.md`.

## 2. Why did each case perform differently?

The program adds 32 to a dark pixel and subtracts 8 from a bright pixel. The bright path also needs an extra jump that costs 2 cycles. A cache miss adds 47 cycles, and an incorrect branch prediction adds 15.

| Test case | Instruction cycles | Cache delay | Branch delay | Total |
|---|---|---|---|---|
| Best | 210 | 188 | 15 | 413 |
| Worst | 226 | 188 | 90 | 504 |
| Real Case 1 | 220 | 141 | 75 | 436 |
| Real Case 2 | 226 | 188 | 45 | 459 |

Compared with Best Case:

- **Worst Case** had five more branch mistakes (+75 cycles) and eight bright pixels (+16 cycles): `75 + 16 = 91` more cycles.
- **Real Case 1** had one fewer cache miss (−47), four more branch mistakes (+60) and five bright pixels (+10): `−47 + 60 + 10 = 23` more cycles.
- **Real Case 2** had the same cache misses, two more branch mistakes (+30) and eight bright pixels (+16): `30 + 16 = 46` more cycles.

Worst Case is slowest because its pattern switches between dark and bright on every pixel, which is the hardest pattern to predict. Real Case 2 has the same 8/8 split but switches only once, so it had half as many branch mistakes (3 against 6).

The simulator decides cache hits and branch predictions randomly, with a fixed chance per test case, rather than learning the pattern. A repeat run can give a different total, as the comparison with Runs 1–4 shows (differences of 2 to 62 cycles).

## 3. What is the main bottleneck?

**Cache misses caused the largest delay in every run:** 188 cycles in Best, Worst and Real Case 2, and 141 in Real Case 1. In every case this was larger than the branch delay.

**Branch mistakes explain the difference between cases.** Best and Worst Case had exactly the same cache delay, so Worst Case's extra time comes from its branch mistakes and extra jumps.

Memory bandwidth is not measured by the simulator, so these results cannot show whether data-transfer speed would limit a real system.

## 4. How could performance be improved?

These are proposed improvements. The simulator cannot run changed programs, so the savings are calculated, not measured. Full workings are in [Section 3 of the main report](Analysis%20Report.md#3-optimization-analysis).

| Method | Explanation | Estimated effect |
|---|---|---|
| Cache prefetching | Load upcoming pixels into the cache before they are needed. The 16 pixels fit in one cache line, so ideally only the first read misses. | Largest saving in every case: −34.1% Best, −28.0% Worst, −21.6% Real 1, −30.7% Real 2. |
| Branch-free code | Use a conditional select (`CSEL` on ARM) instead of jumping, so there is nothing to mispredict. Every pixel then costs 14 cycles. | Helps unpredictable data: −17.9% Worst, −15.8% Real 1, −9.8% Real 2. Slightly worse for Best Case (+0.2%), where predictions were already almost always right. |
| Loop unrolling | Process four pixels per loop pass, so the loop control runs 4 times instead of 16. | Saves 36 cycles in every case (about 7–9%). |

Combining all three for Worst Case gives an estimated 237 cycles, less than half the recorded 504.

## 5. How do the results scale to a 256 × 256 image?

```text
Number of 16-pixel groups = 65,536 ÷ 16 = 4,096
Estimated image cycles = total cycles for 16 pixels × 4,096
```

| Test case | Cycles for 16 pixels | Estimated cycles for 256 × 256 |
|---|---|---|
| Best | 413 | 1,691,648 |
| Worst | 504 | 2,064,384 |
| Real Case 1 | 436 | 1,785,856 |
| Real Case 2 | 459 | 1,880,064 |

These match the simulator's estimates. They assume the small sample's average cost continues across the whole image.

## 6. How much money could be saved per day by reducing CPP by 1?

Using 2,000,000 images per day, 65,536 pixels per image, 2.4 GHz, 8 W and $0.12 per kWh:

```text
Cycles saved per image = 1 × 65,536 = 65,536
Daily cycles saved = 65,536 × 2,000,000 = 131,072,000,000
Daily processor time saved = 131,072,000,000 ÷ 2,400,000,000 ≈ 54.61 seconds
```

If the processor can avoid its full 8 W during the saved time:

```text
Energy saved per day = 0.008 kW × (54.61 ÷ 3,600) h ≈ 0.000121 kWh
Cost saved per day ≈ 0.000121 × $0.12 ≈ $0.0000146
```

| Processed images per day | Processor time saved | Possible electricity saving per day |
|---|---|---|
| 2,000,000 | 54.61 seconds | $0.0000146 |
| 1,000,000 (the 50% that need adjustment) | 27.31 seconds | $0.0000073 |

If the processor stays at 8 W all day, its electricity cost is fixed at `0.008 × 24 × $0.12 = $0.02304` per day, and finishing sooner saves nothing.

For Real Case 1, reducing CPP from 27.25 to 26.25 cuts processing time by about 3.7%, which lets the same processor handle about 3.8% more images. At this workload one server is enough either way, so no hardware saving can be calculated; the saving matters at larger scale, where fewer servers would be needed.

## Sources

- [Logs.md](Logs.md): Runs 5–8, pixel lists, final registers, detailed metrics.
- [Quick guide](How%20to%20Use%20Project%201%20CPU%20Simulator%20-%20Quick%20Guide.md): "Next Steps After Running Simulator".
- [Project scenario](Project%201%20Scenario_%20CPU%20Instruction%20Execution%20-%20Image%20Brightness%20Processing.md): hardware values and workload.
- [Simulator](Project1_CPU_Simulator.html): instruction costs and how delays are counted.
