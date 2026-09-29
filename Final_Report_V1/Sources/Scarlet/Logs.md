# Logs: recorded simulator screens (Runs 5–8)

Text transcribed from the twelve screenshots in `Screenshots/`. Each run has three screenshots: the top screen (status, controls, quick metrics, summary statistics), the middle screen (instruction sequence and registers), and the bottom screen (pixel data, execution summary, detailed metrics). All screenshots show the final state after all 16 pixels were processed.

These runs are numbered 5–8 so they can be added directly after Runs 1–4 in the group's main logs. They repeat the same four test cases, recorded separately on 29 September 2026 at 500 ms per step.

| Run | Run ID | Test case | Screenshots | Total cycles |
|---|---|---|---|---|
| 5 | BC-500-R2 | Best: all 0 | `BC-R2-1.png`, `BC-R2-2.png`, `BC-R2-3.png` | 413 |
| 6 | WC-500-R2 | Worst: alternating | `WC-R2-1.png`, `WC-R2-2.png`, `WC-R2-3.png` | 504 |
| 7 | RC1-500-R2 | Real Case 1: 70% dark | `RC1-R2-1.png`, `RC1-R2-2.png`, `RC1-R2-3.png` | 436 |
| 8 | RC2-500-R2 | Real Case 2: clustered | `RC2-R2-1.png`, `RC2-R2-2.png`, `RC2-R2-3.png` | 459 |

## Visible instruction sequence

All four middle screenshots show the upper part of the instruction list. The `0x1C` line is partly clipped at the bottom of the panel.

```text
0x00  LOAD R0, #0           1c
0x04  LOAD R1, #1024        1c
0x08  LOOP: LOAD R3, [R1]   3c
0x0C  CMP R3, R2            1c
0x10  BLT DARK              1c
0x14  SUB R4, R3, R7        1c
0x18  JMP STORE             2c
```

The separate Current PC display shows `0x34` in every run.

## Run 5: Best Case (all pixels 0)

Screenshots: `BC-R2-1.png` (top), `BC-R2-2.png` (registers and pixel data), `BC-R2-3.png` (detailed metrics).

### Top screen (BC-R2-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Best Case: All Dark (0)
SPEED: 500 ms per step
```

| Quick metric | Value |
|---|---|
| Total Cycles | 413 |
| Cycles Per Pixel | 25.8 |
| Cache Hits / Misses | 12/4 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 31/32 |
| Pipeline Stalls | 203 |
| Pixels Processed | 16/16 |

### Middle screen (BC-R2-2)

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0x00 |
| R4 | 0x20 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | 0x08 |

Execution summary:

```text
Current Instruction: 0x30 BNE LOOP
Action: All 16 pixels completed! Proceeding to HALT (0x34)
Pixels Processed: 16/16
```

Input pixels (16 black cells; the numbers are printed in black and cannot be read, so the values come from the test case definition):

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Row 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Output pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 32 |
| Row 2 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 32 |

### Bottom screen (BC-R2-3)

```text
PERFORMANCE SUMMARY
Test Case: best
Pixels Processed: 16/16
Total Cycles: 413
Cycles Per Pixel: 25.81
Estimated Full Image (256×256): 1,691,648 cycles

CACHE PERFORMANCE
Cache Hits: 12
Cache Misses: 4
Hit Rate: 75.0%
Stall Cycles: 203

BRANCH PREDICTION
Correct Predictions: 31
Total Branches: 32
Accuracy: 96.9%
```

## Run 6: Worst Case (alternating)

Screenshots: `WC-R2-1.png` (top), `WC-R2-2.png` (registers), `WC-R2-3.png` (pixel data and detailed metrics).

### Top screen (WC-R2-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Worst Case: Alternating
SPEED: 500 ms per step
```

| Quick metric | Value |
|---|---|
| Total Cycles | 504 |
| Cycles Per Pixel | 31.5 |
| Cache Hits / Misses | 12/4 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 26/32 |
| Pipeline Stalls | 278 |
| Pixels Processed | 16/16 |

### Middle screen (WC-R2-2)

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0xC0 |
| R4 | 0xB8 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | 0x08 |

### Bottom screen (WC-R2-3)

Execution summary:

```text
Current Instruction: 0x30 BNE LOOP
Action: All 16 pixels completed! Proceeding to HALT (0x34)
Pixels Processed: 16/16
```

Input pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 64 | 192 | 64 | 192 | 64 | 192 | 64 | 192 |
| Row 2 | 64 | 192 | 64 | 192 | 64 | 192 | 64 | 192 |

Output pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 96 | 184 | 96 | 184 | 96 | 184 | 96 | 184 |
| Row 2 | 96 | 184 | 96 | 184 | 96 | 184 | 96 | 184 |

Detailed metrics:

```text
PERFORMANCE SUMMARY
Test Case: worst
Pixels Processed: 16/16
Total Cycles: 504
Cycles Per Pixel: 31.50
Estimated Full Image (256×256): 2,064,384 cycles

CACHE PERFORMANCE
Cache Hits: 12
Cache Misses: 4
Hit Rate: 75.0%
Stall Cycles: 278

BRANCH PREDICTION
Correct Predictions: 26
Total Branches: 32
Accuracy: 81.3%
```

## Run 7: Real Case 1 (70% dark)

Screenshots: `RC1-R2-1.png` (top), `RC1-R2-2.png` (registers and pixel data), `RC1-R2-3.png` (pixel data and detailed metrics).

### Top screen (RC1-R2-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Real Case 1: 70% Dark
SPEED: 500 ms per step
```

| Quick metric | Value |
|---|---|
| Total Cycles | 436 |
| Cycles Per Pixel | 27.3 |
| Cache Hits / Misses | 13/3 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 27/32 |
| Pipeline Stalls | 216 |
| Pixels Processed | 16/16 |

### Middle screen (RC1-R2-2)

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0x8C |
| R4 | 0x84 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | 0x08 |

### Bottom screen (RC1-R2-3)

Execution summary:

```text
Current Instruction: 0x30 BNE LOOP
Action: All 16 pixels completed! Proceeding to HALT (0x34)
Pixels Processed: 16/16
```

Input pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 35 | 180 | 42 | 60 | 210 | 88 | 50 | 115 |
| Row 2 | 230 | 45 | 72 | 195 | 30 | 95 | 80 | 140 |

Output pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 67 | 172 | 74 | 92 | 202 | 120 | 82 | 147 |
| Row 2 | 222 | 77 | 104 | 187 | 62 | 127 | 112 | 132 |

Detailed metrics:

```text
PERFORMANCE SUMMARY
Test Case: real1
Pixels Processed: 16/16
Total Cycles: 436
Cycles Per Pixel: 27.25
Estimated Full Image (256×256): 1,785,856 cycles

CACHE PERFORMANCE
Cache Hits: 13
Cache Misses: 3
Hit Rate: 81.3%
Stall Cycles: 216

BRANCH PREDICTION
Correct Predictions: 27
Total Branches: 32
Accuracy: 84.4%
```

## Run 8: Real Case 2 (clustered)

Screenshots: `RC2-R2-1.png` (top), `RC2-R2-2.png` (registers), `RC2-R2-3.png` (pixel data and detailed metrics).

### Top screen (RC2-R2-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Real Case 2: Clustered
SPEED: 500 ms per step
```

| Quick metric | Value |
|---|---|
| Total Cycles | 459 |
| Cycles Per Pixel | 28.7 |
| Cache Hits / Misses | 12/4 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 29/32 |
| Pipeline Stalls | 233 |
| Pixels Processed | 16/16 |

### Middle screen (RC2-R2-2)

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0x37 |
| R4 | 0x57 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | 0x08 |

### Bottom screen (RC2-R2-3)

Execution summary:

```text
Current Instruction: 0x30 BNE LOOP
Action: All 16 pixels completed! Proceeding to HALT (0x34)
Pixels Processed: 16/16
```

Input pixels. One value in row 2 (position 7) is too dark to read in the screenshot. Its output is 40, and dark pixels gain 32, so the input is `40 − 32 = 8`. This entry is marked as deduced.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 215 | 210 | 254 | 221 | 231 | 244 | 220 | 236 |
| Row 2 | 39 | 27 | 41 | 71 | 80 | 92 | 8 (deduced) | 55 |

Output pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 207 | 202 | 246 | 213 | 223 | 236 | 212 | 228 |
| Row 2 | 71 | 59 | 73 | 103 | 112 | 124 | 40 | 87 |

Detailed metrics:

```text
PERFORMANCE SUMMARY
Test Case: real2
Pixels Processed: 16/16
Total Cycles: 459
Cycles Per Pixel: 28.69
Estimated Full Image (256×256): 1,880,064 cycles

CACHE PERFORMANCE
Cache Hits: 12
Cache Misses: 4
Hit Rate: 75.0%
Stall Cycles: 233

BRANCH PREDICTION
Correct Predictions: 29
Total Branches: 32
Accuracy: 90.6%
```

## Transcription notes

- Register values are shown in hexadecimal. Decimal checks: R0 = 0x10 = 16, R1 = 0x410 = 1040, R2 = 0x80 = 128, R6 = 0x20 = 32, R7 = 0x08 = 8.
- R3 and R4 hold the last processed pixel and its adjusted value: Best 0 → 32 (0x00 → 0x20), Worst 192 → 184 (0xC0 → 0xB8), Real Case 1 140 → 132 (0x8C → 0x84), Real Case 2 55 → 87 (0x37 → 0x57).
- Unlike Runs 1–4, the R7 row is fully visible in all four middle screenshots, so its value (8) is read directly rather than taken from the code.
- Real Case 2 pixels are randomly generated each time the page loads, so Run 8's pixel list differs from Run 4's. These values belong to this run only.
- The speed was 500 ms per step for these runs, compared with 50 ms for Runs 1–4. The speed setting only controls the animation delay and does not affect any cycle count or metric.
- No event log panel exists in this simulator version, so the order of individual cache and branch events was not recorded.
