# Logs: recorded simulator screens

Text transcribed from the eight screenshots in `Screenshots/`. Each run has two screenshots: the top screen (status, controls, quick metrics, summary statistics) and the bottom screen (instruction sequence, pixel data, execution summary, detailed metrics). The screenshots show the final state after all 16 pixels were processed.

| Run | Test case | Screenshots | Total cycles |
|---|---|---|---|
| 1 | Best: all 0 | `BC-1.png`, `BC-2.png` | 351 |
| 2 | Worst: alternating | `WC-1.png`, `WC-2.png` | 502 |
| 3 | Real Case 1: 70% dark | `RC1-1.png`, `RC1-2.png` | 406 |
| 4 | Real Case 2: clustered | `RC2-1.png`, `RC2-2.png` | 444 |

## Visible instruction sequence

The screenshots show the same program, but the instruction panel is scrolled to different positions. `BC-1`, `BC-2`, `WC-1`, `WC-2`, `RC1-2`, `RC2-1`, and `RC2-2` show the lower part of the list, with `0x34 HALT` highlighted. The `0x18` line is partly clipped at the top of some panels.

```text
0x18  JMP STORE              2c
0x1C  DARK: ADD R4, R3, R6   1c
0x20  STORE: STORE R4, [R1]  3c
0x24  INC R1, #1             1c
0x28  INC R0, #1             1c
0x2C  CMP R0, #16            1c
0x30  BNE LOOP               1c
0x34  HALT                   1c   (highlighted)
```

The [RC1-1 screenshot](Screenshots/RC1-1.png) shows the upper part of the instruction list instead:

```text
0x00  LOAD R0, #0           1c
0x04  LOAD R1, #1024        1c
0x08  LOOP: LOAD R3, [R1]   3c
0x0C  CMP R3, R2           1c
0x10  BLT DARK             1c
0x14  SUB R4, R3, R7       1c
0x18  JMP STORE            2c
```

The beginning of `0x1C DARK: ADD R4, R3, R6` is partly visible at the bottom of that panel. `HALT` is outside its visible area, although the separate Current PC display shows `0x34`.

## Run 1: Best Case (all pixels 0)

Screenshots: `BC-1.png` (top screen), `BC-2.png` (bottom screen).

### Top screen (BC-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Best Case: All Dark (0)
SPEED: 50 ms per step (slider at the minimum)
```

| Quick metric | Value |
|---|---|
| Total Cycles | 351 |
| Cycles Per Pixel | 21.9 |
| Cache Hits / Misses | 13/3 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 32/32 |
| Pipeline Stalls | 141 |
| Pixels Processed | 16/16 |

Registers:

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0x00 |
| R4 | 0x20 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | Not visible (cut off at the bottom of the screenshot) |

### Bottom screen (BC-2)

Execution summary:

```text
Current Instruction: 0x30 BNE LOOP
Action: All 16 pixels completed! Proceeding to HALT (0x34)
Pixels Processed: 16/16
```

Input pixels (16 black cells; no numbers are readable, and the test case defines them as 0):

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Row 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Output pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 32 |
| Row 2 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 32 |

Detailed metrics:

```text
PERFORMANCE SUMMARY
Test Case: best
Pixels Processed: 16/16
Total Cycles: 351
Cycles Per Pixel: 21.94
Estimated Full Image (256×256): 1,437,696 cycles

CACHE PERFORMANCE
Cache Hits: 13
Cache Misses: 3
Hit Rate: 81.3%
Stall Cycles: 141

BRANCH PREDICTION
Correct Predictions: 32
Total Branches: 32
Accuracy: 100.0%
```

## Run 2: Worst Case (alternating)

Screenshots: `WC-1.png` (top screen), `WC-2.png` (bottom screen).

### Top screen (WC-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Worst Case: Alternating
SPEED: 50 ms per step (slider at the minimum)
```

| Quick metric | Value |
|---|---|
| Total Cycles | 502 |
| Cycles Per Pixel | 31.4 |
| Cache Hits / Misses | 13/3 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 23/32 |
| Pipeline Stalls | 276 |
| Pixels Processed | 16/16 |

Registers:

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0xC0 |
| R4 | 0xB8 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | Not visible (cut off at the bottom of the screenshot) |

### Bottom screen (WC-2)

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
Total Cycles: 502
Cycles Per Pixel: 31.38
Estimated Full Image (256×256): 2,056,192 cycles

CACHE PERFORMANCE
Cache Hits: 13
Cache Misses: 3
Hit Rate: 81.3%
Stall Cycles: 276

BRANCH PREDICTION
Correct Predictions: 23
Total Branches: 32
Accuracy: 71.9%
```

## Run 3: Real Case 1 (70% dark)

Screenshots: `RC1-1.png` (top screen), `RC1-2.png` (bottom screen).

### Top screen (RC1-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Real Case 1: 70% Dark
SPEED: 50 ms per step (slider at the minimum)
```

| Quick metric | Value |
|---|---|
| Total Cycles | 406 |
| Cycles Per Pixel | 25.4 |
| Cache Hits / Misses | 13/3 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 29/32 |
| Pipeline Stalls | 186 |
| Pixels Processed | 16/16 |

Registers:

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0x8C |
| R4 | 0x84 |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | Not visible (cut off at the bottom of the screenshot) |

### Bottom screen (RC1-2)

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
Total Cycles: 406
Cycles Per Pixel: 25.38
Estimated Full Image (256×256): 1,662,976 cycles

CACHE PERFORMANCE
Cache Hits: 13
Cache Misses: 3
Hit Rate: 81.3%
Stall Cycles: 186

BRANCH PREDICTION
Correct Predictions: 29
Total Branches: 32
Accuracy: 90.6%
```

## Run 4: Real Case 2 (clustered)

Screenshots: `RC2-1.png` (top screen), `RC2-2.png` (bottom screen).

### Top screen (RC2-1)

```text
STATUS: ✓ Complete! All 16 pixels processed.
TEST CASE: Real Case 2: Clustered
SPEED: 50 ms per step (slider at the minimum)
```

| Quick metric | Value |
|---|---|
| Total Cycles | 444 |
| Cycles Per Pixel | 27.8 |
| Cache Hits / Misses | 12/4 |

| Summary statistic | Value |
|---|---|
| Current PC | 0x34 |
| Branch Predictions | 30/32 |
| Pipeline Stalls | 218 |
| Pixels Processed | 16/16 |

Registers:

| Register | Value |
|---|---|
| R0 | 0x10 |
| R1 | 0x410 |
| R2 | 0x80 |
| R3 | 0x3C |
| R4 | 0x5C |
| R5 | 0x00 |
| R6 | 0x20 |
| R7 | Not visible (cut off at the bottom of the screenshot) |

### Bottom screen (RC2-2)

Execution summary:

```text
Current Instruction: 0x30 BNE LOOP
Action: All 16 pixels completed! Proceeding to HALT (0x34)
Pixels Processed: 16/16
```

Input pixels. Two values in row 2 (positions 1 and 4) are too dark to read in the screenshot. The output pixels are 38 and 38, and dark pixels gain 32, so both input values are `38 − 32 = 6`. These two entries are marked as deduced.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 236 | 209 | 228 | 200 | 217 | 222 | 238 | 228 |
| Row 2 | 6 (deduced) | 78 | 56 | 6 (deduced) | 47 | 11 | 25 | 60 |

Output pixels:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Row 1 | 228 | 201 | 220 | 192 | 209 | 214 | 230 | 220 |
| Row 2 | 38 | 110 | 88 | 38 | 79 | 43 | 57 | 92 |

Detailed metrics:

```text
PERFORMANCE SUMMARY
Test Case: real2
Pixels Processed: 16/16
Total Cycles: 444
Cycles Per Pixel: 27.75
Estimated Full Image (256×256): 1,818,624 cycles

CACHE PERFORMANCE
Cache Hits: 12
Cache Misses: 4
Hit Rate: 75.0%
Stall Cycles: 218

BRANCH PREDICTION
Correct Predictions: 30
Total Branches: 32
Accuracy: 93.8%
```

## Transcription notes

- Register values are shown in hexadecimal on screen. Decimal checks: R0 = 0x10 = 16, R1 = 0x410 = 1040, R2 = 0x80 = 128, R3/R4 match the last processed pixel and its adjusted value (for example, Worst Case: R3 = 0xC0 = 192, R4 = 0xB8 = 184; 192 − 8 = 184).
- The R7 row is cut off at the bottom edge of all four top screenshots, so its value could not be transcribed. The program defines R7 as 8 and the subtract instruction removes it, but this is from the simulator code, not the screenshots.
- Register values R3 and R4 in the top screens match the final input and output pixels shown in the bottom screens of the same run.
- Real Case 2 uses randomly generated pixel values in the simulator, so its pattern differs from the fixed lists in the other cases. These values belong to this recorded run only.
- The event log panel described in the quick guide is not visible in any of the eight screenshots, so individual cache-hit, cache-miss, and branch events during the run could not be transcribed.
