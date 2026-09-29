# Data Collection Template — Project 1

## 📊 Data Collection Template

Copy this into your Excel spreadsheet. Summary rows average all recorded runs per test case (detailed runs below).

| Test Case | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Cache Hit % | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|
| Best (All 0) | 351 | 21.9 | 13 | 3 | 81.3% | 32 | 32 | 100.0% |
| Worst (Alternating) | 502 | 31.4 | 13 | 3 | 81.3% | 23 | 32 | 71.9% |
| Real Case 1 (70% Dark) | 406 | 25.4 | 13 | 3 | 81.3% | 29 | 32 | 90.6% |
| Real Case 2 (Clustered) | 444 | 27.8 | 12 | 4 | 75.0% | 30 | 32 | 93.8% |

*One full run per test case (all 16 pixels processed, 50ms/step). Cycles/Pixel matches the simulator's Cycles Per Pixel metric. Screenshots: `Screenshots/BC-*.png`, `WC-*.png`, `RC1-*.png`, `RC2-*.png`.*

## Detailed Runs

### Best Case (All 0)

| Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|---|---|
| BC-50-R1 | 50 | 351 | 21.9 | 13 | 3 | 81.3% | 141 | 32 | 32 | 100.0% |

### Worst Case Alternating

| Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|---|---|
| WC-50-R1 | 50 | 502 | 31.4 | 13 | 3 | 81.3% | 276 | 23 | 32 | 71.9% |

### Real Case 1 (70% Dark)

| Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|---|---|
| RC1-50-R1 | 50 | 406 | 25.4 | 13 | 3 | 81.3% | 186 | 29 | 32 | 90.6% |

### Real Case 2 (Clustered)

| Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|---|---|
| RC2-50-R1 | 50 | 444 | 27.8 | 12 | 4 | 75.0% | 218 | 30 | 32 | 93.8% |

## Notes

- Run IDs group screenshot pairs into unique runs (each pair = top-panel screenshot + DETAILED METRICS screenshot of the same run).
- Each run processed all 16 pixels (`Pixels Processed: 16/16`), so Cycles/Pixel equals Total Cycles ÷ 16.
- Speed (ms/step) only controls animation delay — it has no effect on cycle counts.
- Estimated Full Image (256×256): BC 1,437,696 · WC 2,056,192 · RC1 1,662,976 · RC2 1,818,624 cycles.
