# Data Collection Template — Project 1 (Runs 5–8)

## Summary

One full run per test case (all 16 pixels processed, 500 ms/step).

| Test Case | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Cache Hit % | Branch Correct | Branch Total | Accuracy % | Stalls |
|---|---|---|---|---|---|---|---|---|---|
| Best (All 0) | 413 | 25.8 | 12 | 4 | 75.0% | 31 | 32 | 96.9% | 203 |
| Worst (Alternating) | 504 | 31.5 | 12 | 4 | 75.0% | 26 | 32 | 81.3% | 278 |
| Real Case 1 (70% Dark) | 436 | 27.3 | 13 | 3 | 81.3% | 27 | 32 | 84.4% | 216 |
| Real Case 2 (Clustered) | 459 | 28.7 | 12 | 4 | 75.0% | 29 | 32 | 90.6% | 233 |

## Detailed runs

| Run | Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % | Screenshots |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | BC-500-R2 | 500 | 413 | 25.81 | 12 | 4 | 75.0% | 203 | 31 | 32 | 96.9% | `BC-R2-1/2/3.png` |
| 6 | WC-500-R2 | 500 | 504 | 31.50 | 12 | 4 | 75.0% | 278 | 26 | 32 | 81.3% | `WC-R2-1/2/3.png` |
| 7 | RC1-500-R2 | 500 | 436 | 27.25 | 13 | 3 | 81.3% | 216 | 27 | 32 | 84.4% | `RC1-R2-1/2/3.png` |
| 8 | RC2-500-R2 | 500 | 459 | 28.69 | 12 | 4 | 75.0% | 233 | 29 | 32 | 90.6% | `RC2-R2-1/2/3.png` |

## Combined with Runs 1–4

| Test Case | Run 1–4 total | Run 5–8 total | Average |
|---|---|---|---|
| Best | 351 | 413 | 382.0 |
| Worst | 502 | 504 | 503.0 |
| Real Case 1 | 406 | 436 | 421.0 |
| Real Case 2 | 444 | 459 | 451.5 |

## Notes

- Each run processed all 16 pixels, so Cycles/Pixel = Total Cycles ÷ 16.
- Speed (ms/step) only controls the animation delay; it has no effect on cycle counts.
- Estimated Full Image (256×256): Best 1,691,648 · Worst 2,064,384 · Real 1 1,785,856 · Real 2 1,880,064 cycles.
- Real Case 2 pixels are random per page load, so Run 8 and Run 4 used different pixel lists (both 8 bright, 8 dark).
