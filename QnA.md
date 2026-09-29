# Presentation Q&A — Project 1: CPU Instruction Execution (Image Brightness)

**Purpose:** four questions will be asked after the presentation. These 15 questions cover the likely ground, hardest first. Each answer is written to be said aloud in 20–60 seconds. Section, figure and appendix references point into `Final_Report_V1/Final_Report.md`, which is self-contained.

## Quick facts to memorize

- **Setup:** 4 required cases, 12 recorded runs (3 per case), 16 pixels per run.
- **Cycle totals:** Best 351 / 413 / 366; Worst 502 / 504 / 378; Real 1 406 / 436 / 451; Real 2 444 / 459 / 397.
- **Costs:** dark pixel = 13 cycles, bright pixel = 15; setup = 2; cache miss adds 47 (50 total per missed load); wrong branch adds 15.
- **Bottleneck:** cache misses were the largest delay in 11 of 12 runs (72.6% of all stall cycles).
- **Optimization winners (40 runs per case):** Unrolled wins Best (316.45, −12.8%); Combined wins the other three (Worst 329.58, −34.5%; Real 1 337.80, −23.2%; Real 2 335.45, −19.2%).
- **Costs result:** one 8 W processor = $8.41/year electricity; 1 server for the 4-hour SLA; no million-dollar saving from the given numbers.
- **Key line:** the handout's "500 → 350 cycles" matches our **16-pixel chunk** totals, not full images.

---

## Q1. What did you do in this project?

We analyzed how the CPU executes the brightness-adjustment program, instruction by instruction. We ran 12 experiments across the four required cases, recorded complete step-by-step traces for one run per case, measured cycles, cache misses and branch outcomes, tested four optimization programs with 800 executions, and scaled the results to full-size images and server costs. The main finding: random cache misses cause most of the waiting, and a combined branch-free, unrolled program cuts the Worst Case mean by 34.5%. The full evidence is in the report and its Appendices A–D.

## Q2. The handout says current CPP is about 7 and the target is under 5. Your numbers are 22–31. Why?

Because the handout's figures are illustrative, not measurements of this simulator. The supplied simulator charges 13–15 cycles per pixel **before any stalls**, so its floor is 210 ÷ 16 = 13.125 CPP — nothing can reach 5 on this model. We report the measured values and flag the mismatch in Section 2.4. *If pressed:* the handout's "500 → 350 cycles" claim matches our 16-pixel chunk totals (351–504), which suggests those figures describe the sample chunk, not a full image.

## Q3. Why does the Best Case sometimes predict a branch wrong? And why isn't the Worst Case 0% accurate?

The simulator doesn't predict from pixel data — it draws a fixed probability per case: 95% correct for Best, 50% for Worst, 80% for both real cases. So Best has a 5% wrong chance on each of 16 decisions, and one wrong prediction across a run is not surprising. Worst averages about 50%, which matches our measured 44–63% per run (54% pooled). The handout's "0%" is not what this model does (Section 1.6).

## Q4. Same case, same inputs — why do the cycle totals differ between runs?

Because cache and branch outcomes are random draws. Each load has about an 80% hit chance, so misses differ run to run (we observed 1–4), and each miss adds 47 cycles; each wrong prediction adds 15. The base cycles were identical within every case — all differences came from those two random terms. That is exactly why we repeated each case three times, and each optimization program 40 times.

## Q5. What is the bottleneck — cache or branches?

Cache misses, in 11 of 12 runs. Cache delay was 47–188 cycles per run versus 0–135 for branch mistakes, and misses were 72.6% of all stall cycles. The one exception is Run 10: a lucky single-miss draw left its seven mispredictions as the larger delay. A miss costs 50 cycles total versus 15 for a misprediction, so normally the ranking is not close (Section 2.2).

## Q6. You modified the simulator to test optimizations. Are those "measurements" real?

They are real executions of the same cost model, not hardware benchmarks. We replaced only the program and its step logic; the instruction costs, cache randomness and branch probabilities stayed the same. The new instructions we assumed (`CSEL` at 1 cycle, `INC #4`, base+offset loads) are documented assumptions in Section 3.1 — the scenario frames the CPU as ARM-like, so they are plausible, but a real compiler would need real benchmarks to confirm. All 800 executions satisfy the same cost equation and every output pixel was checked.

## Q7. Why does unrolling win the Best Case, but the combined program win the other three?

Unrolling is the pure loop-control win: 16 base cycles saved, and Best Case has almost no mispredictions to remove. The combined program also removes the brightness branches, but its selection step costs 4 extra base cycles per pixel — worth it wherever mispredictions or bright pixels occur, which is the other three cases. On Best it is a near-tie: unrolling leads by 26 cycles, about 1.7 standard errors (Section 3.4).

## Q8. The handout suggests loop tiling. Why didn't you test it? Why is prefetching only calculated?

Both target cache behavior, but the simulator has no cache contents, no cache lines and no prefetching — it draws hits and misses at random. Tiling or prefetching cannot change a random draw, so any "result" would be invented. We kept prefetching as an explicit ceiling calculation and documented why. Tiling is unmeasurable for the same reason: there is nothing to tile or reuse in a 16-pixel single pass under this model (Sections 3.1 and 3.5).

## Q9. Three inputs were "inferred from the output". Isn't that circular — using the formula to verify itself?

It would be if we counted them as verification, so we don't. Three of 192 cells — under 2% — were unreadable in the screenshots, so we reconstructed the input from the output using the brightness rule, marked each one "inferred" in Appendix B, and excluded them from the output-verification claim. The other 189 inputs were read directly or defined by the case, and all pairs are consistent with the rule (Section 1.4).

## Q10. The handout says the change would save "millions annually". You report $8.41/year and one server. Why the gap?

Because the handout's headline figure is not derivable from its own numbers. At 8 W and $0.12/kWh, one processor's whole year of electricity is $8.41; the full daily workload fits in one server using about 10% of the 4-hour window, so the server count stays one. We reported what the given assumptions support instead of inventing a large saving. Also, the handout's "500 → 350 cycles per image" matches our 16-pixel chunk totals, not full images of 1.5–1.9 million cycles — another sign the overview is illustrative (Sections 4.3–4.5).

## Q11. The scenario describes register pressure and spills; you report zero spills. Why?

The supplied simulator defines eight registers and the program uses seven — one spare — and the model contains no stack or spill instructions at all. So the honest answer for this tool is: zero spills by code inspection, with no measured spill counter. The scenario's 32-register spill discussion describes a fuller CPU than this teaching simulator implements. We say that plainly in Sections 1.2 and 2.1.

## Q12. The deliverable says "5+ experiments" with full trace evidence; you present 4 complete traces. Is that a gap?

We recorded 12 experiments — three per required case — and complete cycle-by-cycle traces for each of the four test cases (Runs 9–12). The other eight are final-state runs with reconstructed path tables. We deliberately did not fabricate per-instruction event positions for Runs 1–8; only observed records are presented as traces. If a fifth full trace is expected, we can record another run with the same tooling in minutes — the method is documented (Sections 1.1 and 1.5).

## Q13. How do we know the traces and screenshots are genuine, not fabricated?

Every trace was recorded by stepping the actual simulator and logging its state after each instruction; the six checkpoint screenshots per run come from the same captures. The totals reconcile exactly with the cost model, and an independent audit re-derived every table from the raw records — 205 checks, zero failures. The package verifier also re-checks checksums for all 53 evidence files and every report table, and it passes (report header, Appendices A–D).

## Q14. What are the limitations, and what would you do with more time?

The results come from a teaching model with documented assumptions, not hardware. Its cache and branch behavior is random with fixed probabilities, not a learning predictor, and Runs 1–8 lack individual event positions. With more time we would: record a fifth full trace and more repeats; build a cache-aware variant to test tiling and prefetching for real; and validate the winning program with an actual compiler and hardware benchmark (Section 5, Limitations).

## Q15. Your Run 10 Worst Case (378 cycles) was faster than Run 5 Best Case (413). How is that possible?

Randomness. Run 10 drew only one cache miss, while Run 5 drew four. A miss costs 47 extra cycles, which outweighs Run 10's extra mispredictions (7 × 15 = 105 versus Run 5's 1 × 15). Run 10: 226 + 47 + 105 = 378. So the Worst Case wasn't easy — it got a lucky miss draw. This is exactly why we report three repeats per case and compare means, not single runs (Sections 2.2–2.3).

---

## If a question truly surprises you

1. Restate what you actually measured, with a number.
2. If it wasn't measured, say so, and say what you would check to find out.
3. Point to the section or appendix that holds the evidence — never invent a number.
