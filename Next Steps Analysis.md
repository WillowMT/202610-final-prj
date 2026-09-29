# 🎯 Next Steps After Running Simulator — Analysis

Answers to the six "Next Steps" questions, based on the data collected in [data-collection-template.md](data-collection-template.md) and `Data Collection Sheet.xlsx`.

## 1️⃣ Collect Data

All 4 test cases were run to completion (16/16 pixels, 50 ms/step). Metrics recorded from the DETAILED METRICS panel:

| Test Case | Total Cycles | Cycles/Pixel | Cache Hits/Misses | Hit % | Pipeline Stalls | Branch Correct/Total | Accuracy % |
|---|---|---|---|---|---|---|---|
| Best (All 0) | 351 | 21.9 | 13 / 3 | 81.3% | 141 | 32 / 32 | 100.0% |
| Worst (Alternating) | 502 | 31.4 | 13 / 3 | 81.3% | 276 | 23 / 32 | 71.9% |
| Real Case 1 (70% Dark) | 406 | 25.4 | 13 / 3 | 81.3% | 186 | 29 / 32 | 90.6% |
| Real Case 2 (Clustered) | 444 | 27.8 | 12 / 4 | 75.0% | 218 | 30 / 32 | 93.8% |

## 2️⃣ Analyze Results: Why Did Each Case Perform Differently?

All four cases execute the **same instructions** — the only difference is the pixel data, which changes two things: **branch behavior** and **cache behavior**.

- **Best Case (351 cycles):** Every pixel is 0, so the `BLT DARK` branch always goes the same way. The predictor is right every time (32/32, 100%), so there are zero branch penalties.
- **Worst Case (502 cycles):** Pixels alternate 64, 192, 64, 192…, so the branch flips direction every iteration. The predictor gets only 23/32 right (71.9%), producing **9 mispredictions × 15-cycle pipeline flushes = 135 penalty cycles** — the main reason it is 43% slower than Best Case (502 vs 351).
- **Real Case 1 (406 cycles):** A realistic mix (70% dark). The predictor learns the dominant path and achieves 90.6% accuracy (3 mispredictions), sitting between the extremes.
- **Real Case 2 (444 cycles):** Bright pixels clustered in the top half, dark in the bottom half. The predictor adapts when the pattern changes, so branch accuracy is actually good (93.8%, only 2 mispredictions) — but it suffers **one extra cache miss** (4 vs 3), adding a 47-cycle penalty.

**The decomposition confirms it:** in every run, `Stall Cycles = 47 × cache misses + 15 × branch mispredictions` exactly (e.g., Worst Case: 3×47 + 9×15 = 276). The remaining "base" cost is nearly constant (~210–226 cycles). Performance differences come almost entirely from stalls, not from the instructions themselves.

## 3️⃣ Find the Bottleneck: Cache, Branches, or Memory Bandwidth?

**The primary bottleneck is branch mispredictions; cache misses are secondary.**

| Case | Base cycles | Branch penalty | Cache penalty | Stall share of total |
|---|---|---|---|---|
| Best | 210 | 0 | 141 | 40% |
| Worst | 226 | 135 | 141 | 55% |
| Real Case 1 | 220 | 45 | 141 | 46% |
| Real Case 2 | 226 | 30 | 188 | 49% |

- Branch penalties range from **0 to 135 cycles** — a swing of 135 cycles caused purely by data pattern. This is the biggest lever.
- Cache penalties are fairly stable (141 cycles = 3 misses) except Real Case 2 (188 = 4 misses). Even at 81% hit rate, the 3 compulsory misses on a 16-pixel chunk already cost 40% of total runtime.
- **Memory bandwidth is not a bottleneck** at this scale: only 16 loads + 16 stores, and the access pattern is perfectly sequential. It would only matter for the full-size image if prefetching were poor.

## 4️⃣ Optimize: How to Improve

Ordered by expected impact:

1. **Branch-free (predicated) code** — eliminate the `BLT`/`JMP` entirely by computing both results and selecting arithmetically, e.g.:
   ```
   ADD R5, R3, R6      ; brightened value (pixel + 32)
   SUB R4, R3, R7      ; tone-balanced value (pixel - 8)
   ; select R4 based on R3 < R2 with a conditional/flagless instruction
   ```
   This removes the 50/50 branch on image content. Expected saving: up to **135 cycles** on Worst Case (all mispredictions gone).
2. **Loop unrolling (4×)** — process 4 pixels per iteration so `BNE LOOP` executes 4× instead of 16×, and `CMP`/`INC R0` also run 4× less often. Fewer branches = fewer misprediction opportunities and fewer loop-overhead instructions. Caveat: uses more registers — watch for spills (each spill costs 200+ cycles).
3. **Cache prefetching** — pixel addresses are sequential (`INC R1, #1`), so a hardware/software prefetch of the next pixel (and write-buffers for stores) removes the remaining misses. Expected saving: **47 cycles per miss eliminated** (e.g., 141 on Best/Real 1, 188 on Real Case 2).
4. **Combined effect:** branch-free code + prefetching would reduce Worst Case from 502 to roughly **226 + 141 = ~367 cycles** (only compulsory misses remain), a ~27% improvement — close to the scenario's 500→350 target.

## 5️⃣ Extrapolate: Scale to a Full 256×256 Image

A 256×256 image has 65,536 pixels = 4,096 chunks of 16 pixels, so multiply the 16-pixel run's Total Cycles by 4,096 (equivalently: Cycles/Pixel × 65,536):

| Test Case | 16-pixel run (cycles) | Full image (cycles) |
|---|---|---|
| Best (All 0) | 351 | 1,437,696 |
| Worst (Alternating) | 502 | 2,056,192 |
| Real Case 1 (70% Dark) | 406 | 1,662,976 |
| Real Case 2 (Clustered) | 444 | 1,818,624 |

These match the simulator's own "Estimated Full Image" values. Note the spread: a bad data pattern costs **~618,000 extra cycles per image** (Worst vs Best) if the code is branch-heavy — that penalty repeats for every image processed.

## 6️⃣ Calculate Cost: Savings From Reducing CPP by 1

**Assumptions** (from the scenario): 2M images uploaded/day, 50% need adjustment → **1,000,000 images/day**; clock 2.4 GHz (1 cycle = 0.417 ns); 8 W edge processor; $0.12/kWh, 24/7 operation. A full image takes CPP × 65,536 cycles, so reducing CPP by 1 saves **65,536 cycles per image**.

**Compute time saved per day:**

- 1,000,000 images × 65,536 cycles = 6.55 × 10¹⁰ cycles/day
- At 2.4 GHz → **27.3 seconds of CPU time per day** freed up

**Energy cost saved per day:**

- 27.3 s × 8 W = 218 J = 6.1 × 10⁻⁵ kWh
- 6.1 × 10⁻⁵ kWh × $0.12 = **≈ $0.0000073 per day** (≈ $0.003/year)

**Throughput gained (the real lever):**

- Images/second per server ∝ 1/(CPP × 65,536). Cutting CPP from 25.4 to 24.4 (Real Case 1) increases per-server throughput by 25.4/24.4 − 1 ≈ **+4.1%**.
- That means ~4% fewer servers (or 4% more headroom against the 4-hour SLA) for the same workload. For a cloud platform spending millions annually on processing infrastructure, a 4% fleet reduction is worth **tens of thousands of dollars per year** — and this compounds with every image processed.
- This matches the scenario's own math: cutting cycles per image from 500 to 350 (−30%) yields 500/350 ≈ **+43% more images/second** (stated as 40%).

**Takeaway:** saving 1 CPP is nearly free in electricity but buys ~4% more throughput per server — at cloud scale, infrastructure savings (not energy) are where the money is.
