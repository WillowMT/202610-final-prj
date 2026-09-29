# 📦 Analysis Report — Project 1: CPU Instruction Execution

Deliverables for the Image Brightness Processing scenario, based on data in [data-collection-template.md](data-collection-template.md), `Data Collection Sheet.xlsx`, and screenshots in `Screenshots/`.

**Assumptions used throughout:** clock 2.4 GHz (1 cycle = 0.417 ns); 8 W edge processor; $0.12/kWh; 2M images uploaded/day, 50% require adjustment (1M images/day); average image 12 MB ≈ 12 Mpixels = **183 chunks** of 256×256 pixels (65,536 pixels each); SLA = 4-hour maximum latency.

## 1️⃣ Instruction Trace (5+ Experiments)

**Experiment set A — full runs (16/16 pixels, 50 ms/step):**

| # | Experiment | Screenshots | Result |
|---|---|---|---|
| 1 | Best Case (all 0) | `BC-1.png`, `BC-2.png` | 351 cycles, CPP 21.9 |
| 2 | Worst Case (alternating 64/192) | `WC-1.png`, `WC-2.png` | 502 cycles, CPP 31.4 |
| 3 | Real Case 1 (70% dark) | `RC1-1.png`, `RC1-2.png` | 406 cycles, CPP 25.4 |
| 4 | Real Case 2 (clustered) | `RC2-1.png`, `RC2-2.png` | 444 cycles, CPP 27.8 |

**Experiment 5 — exploratory speed series:** 20 earlier partial runs (1/16 pixels) at 50/500/1000 ms per step across Worst Case and Real Case 1. Findings: animation speed has **no effect** on cycle counts, and every run's total is exactly explained by `Total Cycles = base + 47 × cache misses + 15 × branch mispredictions`. This validated the cost model used below.

### Program (from Instruction Sequence panel)

| PC | Instruction | Base cost |
|---|---|---|
| 0x00 | LOAD R0, #0 | 1c |
| 0x04 | LOAD R1, #1024 | 1c |
| 0x08 | LOOP: LOAD R3, [R1] | 3c (+47 if miss) |
| 0x0C | CMP R3, R2 | 1c |
| 0x10 | BLT DARK | 1c (+15 if mispredicted) |
| 0x14 | SUB R4, R3, R7 | 1c (bright path only) |
| 0x18 | JMP STORE | 2c (bright path only) |
| 0x1C | DARK: ADD R4, R3, R6 | 1c (dark path only) |
| 0x20 | STORE: STORE R4, [R1] | 3c (+47 if miss) |
| 0x24 | INC R1, #1 | 1c |
| 0x28 | INC R0, #1 | 1c |
| 0x2C | CMP R0, #16 | 1c |
| 0x30 | BNE LOOP | 1c (+15 if mispredicted) |
| 0x34 | HALT | 1c |

### Cycle-by-cycle trace — one steady-state iteration

**Best Case (dark pixel, cache hit):** LOAD(3) → CMP(1) → BLT taken(1) → ADD(1) → STORE(3) → INC R1(1) → INC R0(1) → CMP(1) → BNE taken(1) = **13 cycles**. Iteration 1 adds +47 (compulsory miss on first LOAD).

**Worst Case (bright pixel):** LOAD(3) → CMP(1) → BLT *not taken*(1) → SUB(1) → JMP(2) → STORE(3) → INC R1(1) → INC R0(1) → CMP(1) → BNE(1) = **14 cycles** + 15-cycle pipeline flush whenever BLT is mispredicted. The branch flips every iteration (64 ⇄ 192), so BLT mispredicts repeatedly.

**Register/memory state at HALT (identical across cases):** R0 = 0x10 (16), R1 = 0x410 (end address), R2 = 0x80 (threshold), R6 = 0x20 (+32), R7 = −8; PC progressed 0x00 → 0x34; output grids filled (Best: all 32; Worst: 96/184 alternating; RC1/RC2 per screenshot pixel grids).

### Per-iteration cache and branch events

- **Cache:** 3 misses per 16-pixel run (RC2: 4) — compulsory misses on first touch of each new cache line; all other loads/stores hit (3-cycle accesses).
- **Branches:** 32 branches per run = 16 × BNE + 16 × BLT. **BNE was predicted correctly every time in all cases** (taken 15×, falls through once). All mispredictions occur on **BLT**:
  - Best: BLT correct 16/16 (always taken) → 0 mispredictions
  - Worst: BLT correct 7/16 → 9 mispredictions (alternating pattern defeats the predictor)
  - RC1: BLT correct 13/16 (11 dark pixels + 2 lucky) → 3 mispredictions
  - RC2: BLT correct 14/16 → 2 mispredictions, both at the bright→dark region transition where the pattern changes

## 2️⃣ Performance Data

| Metric | Best | Worst | RC1 | RC2 |
|---|---|---|---|---|
| Total cycles | 351 | 502 | 406 | 444 |
| Cycles per pixel (CPP) | 21.9 | 31.4 | 25.4 | 27.8 |
| Cache misses (of 16 accesses) | 3 | 3 | 3 | 4 |
| Cache miss rate | 18.8% | 18.8% | 18.8% | 25.0% |
| Branch mispredict rate | 0% | 28.1% | 9.4% | 6.3% |
| Pipeline stall cycles | 141 | 276 | 186 | 218 |
| Register spills | 0 | 0 | 0 | 0 |

- **Stall decomposition (exact in every run):** `Stall cycles = 47 × misses + 15 × mispredictions` (e.g., Worst: 3×47 + 9×15 = 276). Remaining base cost: 210–226 cycles.
- **Register spills = 0:** the 16-pixel loop fits comfortably in R0–R7; no stack spill/reload instructions appear in the trace.

## 3️⃣ Optimization Analysis

Three strategies compared, with improvement estimated from the measured cycle model (base + 47/miss + 15/mispredict):

| Strategy | Change | Best | Worst | RC1 | RC2 | Notes |
|---|---|---|---|---|---|---|
| Baseline (measured) | — | 351 | 502 | 406 | 444 | — |
| **A. Branch-free code** | Replace BLT/JMP with predicated arithmetic (compute both, select) | ~367 | ~367 | ~367 | ~414 | Removes all BLT mispredictions and the 2c JMP, adds 1 select op/pixel |
| **B. Loop unrolling (4×)** | INC R0/CMP/BNE run 4× less often | ~315 | ~466 | ~370 | ~408 | Saves only the 36 loop-overhead cycles — BNE was never mispredicted, so branches remain |
| **C. Cache prefetching** | Prefetch next pixel / write-buffer stores | ~210 | ~361 | ~265 | ~256 | Eliminates all miss penalties; branch penalties untouched |
| **A + C combined** | Branch-free + prefetch | ~226 | ~226 | ~226 | ~226 | Only unavoidable base work remains |

**Which strategy works best for which case:**

- **Worst Case:** Branch-free code wins by far (−27%), because data-dependent branching is its entire problem. Prefetching alone leaves it slow (361).
- **Best Case:** Prefetching wins (−40%); branch-free code actually *hurts* (+4.5%) — the always-taken branch was already free, and the extra arithmetic costs a cycle per pixel. A classic trade-off: optimizations for unpredictable data can penalize predictable data.
- **Real Cases:** Prefetching gives the biggest single win (−35%/−42%); branch-free adds a smaller further gain and makes performance **data-independent** (predictable SLAs).
- **Overall recommendation:** prefetching + branch-free code ≈ flat ~226 cycles/chunk regardless of image content — best worst-case latency and simplest capacity planning.

## 4️⃣ Extrapolation & Cost Impact

**Full-size image (256×256 = 65,536 pixels = 4,096 chunks):**

| Case | Per chunk | Per image (×4,096) |
|---|---|---|
| Best | 351 | 1,437,696 |
| Worst | 502 | 2,056,192 |
| RC1 | 406 | 1,662,976 |
| RC2 | 444 | 1,818,624 |

**Total cycles for 2M images/day** (using RC1 as the representative case, 183 chunks/image):

- Per image: 183 × 1,662,976 ≈ **3.04 × 10⁸ cycles** (0.127 s at 2.4 GHz)
- 1M adjusted images/day: **3.04 × 10¹¹ cycles/day** (all 2M uploaded: 6.09 × 10¹¹)

**Electricity cost** (8 W, $0.12/kWh, 24-hour operation):

- Busy compute: 126,800 s/day × 8 W = 0.282 kWh/day → **$0.034/day ≈ $12/year** (per site)
- Servers always on (9 × 8 W × 24 h): 1.728 kWh/day → **$0.21/day ≈ $77/year**
- Energy is negligible at this scale — **server count and throughput dominate cost.**

**Server count needed for the 4-hour SLA** (worst case: the full day's 1M adjusted images arrive inside one 4-hour window):

- Required throughput: 1,000,000 / 14,400 s = 69.4 images/s
- Per server: 2.4 GHz ÷ 3.04 × 10⁸ cycles = 7.9 images/s
- Servers needed: 69.4 ÷ 7.9 = **8.8 → 9 servers** (≈2 servers if load is evenly spread across 24 h)

**Annual cost savings from a 20% cycle reduction** (e.g., CPP 25.4 → 20.3 via optimization):

- Compute per day: 126,800 s → 101,440 s (−20%)
- Energy saving: ~$2.50/year — negligible
- SLA fleet: 8.8 → 7.0 → **8 servers instead of 9 (−11%)**, or equivalently **+25% throughput** (1/0.8) from the same fleet
- At the scenario's global scale (thousands of edge sites), removing ~17% of required processing capacity is what turns into "millions annually" — consistent with the scenario's own 500→350 cycle example (+43% images/s)

**Key insight:** in this workload, saving cycles buys throughput and fewer servers, not electricity. The cheapest cycle is the one a mispredicted branch never flushes.
