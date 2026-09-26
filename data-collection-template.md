# Data Collection Template — Project 1

## 📊 Data Collection Template

Copy this into your Excel spreadsheet. Summary rows average all recorded runs per test case (detailed runs below).

| Test Case | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Cache Hit % | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|
| Best (All 0) | | | | | | | | |
| Worst (Alternating) | 47.1 | 47.1 | 8 | 4 | 66.7% | 14 | 24 | 58.3% |
| Real Case 1 (70% Dark) | 54.0 | 54.0 | 3 | 5 | 37.5% | 13 | 16 | 81.3% |
| Real Case 2 (Clustered) | | | | | | | | |

*Worst and Real Case 1 rows summarize 12 and 8 recorded runs respectively. Total Cycles is the sum across runs; Cycles/Pixel is the per-run average (each run processed 1/16 pixels). Best Case and Real Case 2 have not been run yet — left empty.*

## Detailed Runs

### Real Case 1 (70% Dark)

| Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|---|---|
| RC1-50-R1 | 50 | 19 | 19.0 | 1 | 0 | 100.0% | 0 | 2 | 2 | 100.0% |
| RC1-50-R2 | 50 | 66 | 66.0 | 0 | 1 | 0.0% | 47 | 2 | 2 | 100.0% |
| RC1-50-R3 | 50 | 34 | 34.0 | 1 | 0 | 100.0% | 15 | 1 | 2 | 50.0% |
| RC1-50-R4 | 50 | 81 | 81.0 | 0 | 1 | 0.0% | 62 | 1 | 2 | 50.0% |
| RC1-500-R1 | 500 | 19 | 19.0 | 1 | 0 | 100.0% | 0 | 2 | 2 | 100.0% |
| RC1-500-R2 | 500 | 66 | 66.0 | 0 | 1 | 0.0% | 47 | 2 | 2 | 100.0% |
| RC1-500-R3 | 500 | 81 | 81.0 | 0 | 1 | 0.0% | 62 | 1 | 2 | 50.0% |
| RC1-1000-R1 | 1000 | 66 | 66.0 | 0 | 1 | 0.0% | 47 | 2 | 2 | 100.0% |

### Worst Case Alternating

| Run ID | Speed (ms/step) | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Hit % | Stall Cycles | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|---|---|
| WCA-50-R1 | 50 | 19 | 19.0 | 1 | 0 | 100.0% | 0 | 2 | 2 | 100.0% |
| WCA-50-R2 | 50 | 49 | 49.0 | 1 | 0 | 100.0% | 30 | 0 | 2 | 0.0% |
| WCA-50-R3 | 50 | 34 | 34.0 | 1 | 0 | 100.0% | 15 | 1 | 2 | 50.0% |
| WCA-500-R1 | 500 | 19 | 19.0 | 1 | 0 | 100.0% | 0 | 2 | 2 | 100.0% |
| WCA-500-R2 | 500 | 66 | 66.0 | 0 | 1 | 0.0% | 47 | 2 | 2 | 100.0% |
| WCA-500-R3 | 500 | 34 | 34.0 | 1 | 0 | 100.0% | 15 | 1 | 2 | 50.0% |
| WCA-500-R4 | 500 | 49 | 49.0 | 1 | 0 | 100.0% | 30 | 0 | 2 | 0.0% |
| WCA-500-R5 | 500 | 96 | 96.0 | 0 | 1 | 0.0% | 77 | 0 | 2 | 0.0% |
| WCA-1000-R1 | 1000 | 19 | 19.0 | 1 | 0 | 100.0% | 0 | 2 | 2 | 100.0% |
| WCA-1000-R2 | 1000 | 66 | 66.0 | 0 | 1 | 0.0% | 47 | 2 | 2 | 100.0% |
| WCA-1000-R3 | 1000 | 81 | 81.0 | 0 | 1 | 0.0% | 62 | 1 | 2 | 50.0% |
| WCA-1000-R4 | 1000 | 34 | 34.0 | 1 | 0 | 100.0% | 15 | 1 | 2 | 50.0% |

## Notes

- Run IDs group screenshot pairs into unique runs (each pair = top-panel screenshot + DETAILED METRICS screenshot of the same run).
- All runs show `Pixels Processed: 1/16`, so Cycles/Pixel equals Total Cycles (setup cost not amortized).
- Speed (ms/step) only controls animation delay — it has no effect on cycle counts.
- Observed run types are fully explained by: `Total Cycles = 19 + 47 × (cache misses) + 15 × (branch mispredictions)`.
