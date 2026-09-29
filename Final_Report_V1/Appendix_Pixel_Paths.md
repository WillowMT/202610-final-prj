# Appendix: all 128 pixel paths

This appendix is part of [Final_Report.md](Final_Report.md). It covers Runs 1–8; Runs 9–12 have fully recorded step logs in [Traces/](Traces/) instead. It is reconstructed from the two archived Logs.md files and the unchanged simulator. It is not a saved instruction-event history.

Running instruction totals include 2 setup cycles but exclude cache and branch delays. For pixel n, the load address is 1023 + n; after the iteration R0 = n and R1 = 1024 + n. R3 holds the input and R4 the output.

Dark PC path: `08 → 0C → 10 → 1C → 20 → 24 → 28 → 2C → 30` (13 cycles). Bright PC path: `08 → 0C → 10 → 14 → 18 → 20 → 24 → 28 → 2C → 30` (15 cycles). Both return to 08 after pixels 1–15 and end at 34 after pixel 16.

Input basis: **read** = transcribed from a readable screenshot; **definition** = black input confirmed by the Best Case definition; **inferred** = calculated from the output and unable to independently verify that output.

## Run 1: BC-50-R1

Source: [original log](Sources/Local/Logs.md). All screenshots: [screen 1](Sources/Local/Screenshots/BC-1.png), [screen 2](Sources/Local/Screenshots/BC-2.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `210 + (3 × 47) + (0 × 15) = 351 cycles`. The three cache-miss positions were not saved. There were no incorrect predictions, so every brightness prediction in this run was correct.

## Run 2: WC-50-R1

Source: [original log](Sources/Local/Logs.md). All screenshots: [screen 1](Sources/Local/Screenshots/WC-1.png), [screen 2](Sources/Local/Screenshots/WC-2.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `226 + (3 × 47) + (9 × 15) = 502 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.

## Run 3: RC1-50-R1

Source: [original log](Sources/Local/Logs.md). All screenshots: [screen 1](Sources/Local/Screenshots/RC1-1.png), [screen 2](Sources/Local/Screenshots/RC1-2.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `220 + (3 × 47) + (3 × 15) = 406 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.

## Run 4: RC2-50-R1

Source: [original log](Sources/Local/Logs.md). All screenshots: [screen 1](Sources/Local/Screenshots/RC2-1.png), [screen 2](Sources/Local/Screenshots/RC2-2.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `226 + (4 × 47) + (2 × 15) = 444 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.

## Run 5: BC-500-R2

Source: [original log](Sources/Scarlet/Logs.md). All screenshots: [screen 1](Sources/Scarlet/Screenshots/BC-R2-1.png), [screen 2](Sources/Scarlet/Screenshots/BC-R2-2.png), [screen 3](Sources/Scarlet/Screenshots/BC-R2-3.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `210 + (4 × 47) + (1 × 15) = 413 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.

## Run 6: WC-500-R2

Source: [original log](Sources/Scarlet/Logs.md). All screenshots: [screen 1](Sources/Scarlet/Screenshots/WC-R2-1.png), [screen 2](Sources/Scarlet/Screenshots/WC-R2-2.png), [screen 3](Sources/Scarlet/Screenshots/WC-R2-3.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `226 + (4 × 47) + (6 × 15) = 504 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.

## Run 7: RC1-500-R2

Source: [original log](Sources/Scarlet/Logs.md). All screenshots: [screen 1](Sources/Scarlet/Screenshots/RC1-R2-1.png), [screen 2](Sources/Scarlet/Screenshots/RC1-R2-2.png), [screen 3](Sources/Scarlet/Screenshots/RC1-R2-3.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `220 + (3 × 47) + (5 × 15) = 436 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.

## Run 8: RC2-500-R2

Source: [original log](Sources/Scarlet/Logs.md). All screenshots: [screen 1](Sources/Scarlet/Screenshots/RC2-R2-1.png), [screen 2](Sources/Scarlet/Screenshots/RC2-R2-2.png), [screen 3](Sources/Scarlet/Screenshots/RC2-R2-3.png).

| Pixel | Input | Input basis | Output | Path | Instruction cycles | Running instruction total |
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

Reconciliation: `226 + (4 × 47) + (3 × 15) = 459 cycles`. Cache-miss positions and the positions of incorrect predictions were not saved.
