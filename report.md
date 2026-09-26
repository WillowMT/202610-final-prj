# Project 1 Report: What Happens Inside the CPU (Explained Simply)

## The Big Picture

Imagine a photo app that has to brighten millions of photos every day. Brightening a photo means going through every single pixel and adjusting its color value. This project used a simulator to watch a CPU do that work, one instruction at a time, and to figure out **where the time actually goes**.

We ran the simulator on two test cases:

- **RC1 (Real Case 1)** — an indoor photo: mostly dark pixels (70%), some bright ones.
- **WCA (Worst Case Alternating)** — a photo where dark and bright pixels alternate perfectly: dark, bright, dark, bright...

And we recorded 20 runs total. Each run processed **1 pixel** out of a 16-pixel test chunk.

---

## First, What Do All the Numbers Mean?

When the CPU processes one pixel, three things can cost time:

### 1. The baseline work: 19 cycles

Just doing the work — load the pixel, compare it to the threshold (128), add or subtract the offset, store it back. If everything goes perfectly, one pixel costs **19 cycles**. This is the floor. You can't go below it.

### 2. Cache misses: +47 cycles each

The CPU keeps recently used data in a tiny, super-fast memory called the **cache**. Reading from cache takes ~3 cycles. If the data isn't there (a **cache miss**), the CPU has to go to the main memory, which takes ~50 cycles.

> **Analogy:** The cache is like a small fridge next to your desk. Main memory is the supermarket across town. If the snack you want is in the fridge — 3 seconds. If not, you drive to the supermarket — 47 seconds of extra waiting.

In our data, **one cache miss added exactly 47 extra cycles**, every single time.

### 3. Branch mispredictions: +15 cycles each

The CPU doesn't wait to finish one instruction before starting the next — it works like an assembly line (a **pipeline**). When it hits an IF statement ("is this pixel dark?"), it **guesses** the answer so the assembly line keeps moving. If it guesses right, no time lost. If it guesses wrong (**misprediction**), it has to throw away the work it started and redo it — costing **15 cycles**.

> **Analogy:** It's like a waiter who predicts your order before you finish speaking. If he predicts right, food arrives faster. If wrong, the kitchen throws the dish away and starts over.

---

## The Magic Formula

Every single one of our 20 runs fits this one formula — no exceptions:

```
Total Cycles = 19 + 47 × (cache misses) + 15 × (branch mispredictions)
```

Here are all six run types we observed, and how the formula explains them:

| Run type | Cycles | Cache | Branch guessing | Why |
|---|---|---|---|---|
| Best | 19 | hit | 2/2 correct | Perfect run — pure baseline |
| | 34 | hit | 1/2 | +1 wrong guess |
| | 49 | hit | 0/2 | +2 wrong guesses |
| | 66 | miss | 2/2 | +1 cache miss |
| | 81 | miss | 1/2 | +1 miss, +1 wrong guess |
| Worst | 96 | miss | 0/2 | +1 miss, +2 wrong guesses |

---

## What We Concluded

### 1. The cache is the #1 enemy

One cache miss (**47 cycles**) costs **more than double** the entire baseline pixel (**19 cycles**). The difference between the best run (19) and the worst run (96) is a full **5× slowdown** — caused by just one miss and two bad guesses.

**Fix:** Keep memory access predictable and sequential (read pixel 0, then 1, then 2...). The hardware prefetcher then loads data into the cache *before* the CPU asks for it, and the 47-cycle penalty disappears.

### 2. The alternating pattern is the worst case for a reason

WCA's pixels go dark, bright, dark, bright. The predictor sees "dark, dark, dark..." then gets surprised by a bright pixel, then surprised again by a dark one. In our WCA runs, the predictor was sometimes **right 0 times out of 2** — something that never happened in RC1's mostly-dark photo.

**Fix:** Rewrite the algorithm **without branches** at all. For example: always compute both versions (add 32 and subtract 8) and pick the right one with a trick instruction, or use a saturating-add instruction. No IF = nothing to predict = no 15-cycle surprises. This is the "branch-free code" optimization mentioned in the project materials.

### 3. The speed slider is a red herring

The 50 / 500 / 1000 ms setting is just how fast the *animation* steps through instructions. It has **zero effect** on the cycle counts. (In our spreadsheet, WCA looked "better" at 50 ms than at 500 ms — that's only because we happened to capture different runs, not because of the speed.)

### 4. One warning about the numbers

Each run processed only 1 of 16 pixels, and every run includes the CPU's warm-up (loading the loop counter, address, etc.). So 19 cycles-per-pixel **overestimates** the steady-state cost. In a real full run, the setup cost is shared across all 16 pixels (or all 65,536 pixels of a real image), so the per-pixel cost would settle closer to the loop body alone.

---

## So What? (Why This Matters)

The scenario says the company processes 2+ million images a day on power-limited edge servers. From the data:

- **Eliminating cache misses** saves 47 cycles per miss — the single biggest win.
- **Eliminating branches** saves 15 cycles per wrong guess and flattens the worst case (WCA's 96-cycle run would drop to 66).
- Small per-pixel savings multiply enormously: a 256×256 image has 65,536 pixels, and saving even 1 cycle per pixel saves **65,536 cycles per image** — across 2 million images/day, that's **131 billion cycles saved daily**.

## Bottom Line

> The CPU isn't slow because the math is hard — the math is trivial. It's slow because of *waiting*: waiting for memory (47 cycles) and waiting after wrong guesses (15 cycles). The best optimization order is: **fix the cache access pattern first, then remove the branches.**
