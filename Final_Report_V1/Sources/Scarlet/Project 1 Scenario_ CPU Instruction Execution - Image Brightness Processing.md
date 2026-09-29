# 🖥️ Project 1: CPU Instruction Execution

**Real-World Scenario: Image Brightness Processing**

## 📌 Executive Overview

A photography software company has developed a batch image processing system that adjusts the brightness of thousands of photographs in their cloud storage. The system runs on edge processors with limited CPU cycles and memory. Your task is to analyze how the CPU executes a critical image brightness adjustment algorithm at the instruction level.

**Business Impact:** Reducing CPU cycles per image from 500 to 350 cycles would enable processing 40% more images per second, reducing cloud infrastructure costs by millions annually.

## 🌍 Real-World Context

### The System

A photography platform (similar to Adobe Cloud, Google Photos, or Shutterstock) processes customer-uploaded images. Every day:

- 📸 2+ million images are uploaded
- ⚙️ 50% require automatic brightness adjustment
- 💾 Average image: 5-25 MB (processed in 256x256 pixel chunks)
- 🔄 Batch processing runs 24/7 on distributed edge servers
- ⏱️ Service Level Agreement: 4-hour maximum latency for processing

### The Algorithm

Brightness adjustment uses a simple but computationally intensive loop:

```
FOR each pixel in image chunk (65,536 pixels in 256x256):
    LOAD pixel value from memory
    CHECK if pixel intensity < threshold (128)
    IF yes: ADD brightness offset (32) to pixel
    IF no: SUBTRACT small offset (8) for tone balance
    STORE adjusted pixel back to memory
```

### Hardware Constraints

| Component | Specification | Impact on Brightness Processing |
|---|---|---|
| CPU Clock | 2.4 GHz (ARM Cortex) | Each instruction takes 0.4 nanoseconds |
| Registers | 32 general-purpose (32-bit each) | Must store: loop counter, pixel address, thresholds, offsets |
| L1 Cache | 32 KB data cache, 4-way associative | Holds ~8,000 pixels (12% of chunk) - frequent misses |
| Memory Bandwidth | 6.4 GB/s (DDR4) | 65,536 reads + 65,536 writes = 524 KB per chunk |
| Power Budget | 8 watts (edge processor) | Higher cycle counts = higher power consumption & heat |

## 🎯 Complexity Factors in This Scenario

**Why This Isn't Simple:**

- **Instruction Dependencies:** Each iteration depends on the previous pixel's processing. The CPU cannot parallelize across iterations, creating pipeline stalls.
- **Branch Misprediction:** The IF statement creates conditional branches. Modern CPUs predict branch outcomes. If 50% of pixels trigger the ADD path, the predictor gets it right 50% of the time, causing expensive pipeline flushes on misses.
- **Memory Access Patterns:** Reading/writing pixels sequentially seems predictable, but JPEG compression artifacts mean some chunks access memory in patterns that confuse hardware prefetchers, increasing cache misses from 5% to 45%.
- **Register Pressure:** The algorithm needs to keep multiple values in registers simultaneously (loop counter, pixel address, threshold, offset, current pixel, temp result). With only 32 general-purpose registers, the CPU must spill some to stack memory, creating extra LOAD/STORE instructions.
- **Compiler Optimization Trade-offs:** The compiler can unroll loops to process 4 pixels per iteration (reducing branches by 75%), but this doubles register usage and may cause spills. Or it can inline the function to avoid CALL/RETURN overhead, but this makes the binary 20% larger.
- **Energy Efficiency vs Speed:** Running at full 2.4 GHz uses 8 watts. Running at 1.8 GHz uses 4 watts but increases processing time by 33%. For 2 million images/day, this trade-off costs thousands in electricity and SLA violations.

## 📋 Detailed Scenario: Image Brightness Adjustment Instruction Flow

**Problem Statement:** You are a performance engineer at the photography platform. Your task is to:

1. **Trace Execution:** Simulate CPU instruction execution for a small image chunk (16 pixels instead of 65,536 for tractability)
2. **Measure Cycles:** Count the exact number of CPU cycles consumed, including cache misses and branch predictions
3. **Identify Bottlenecks:** Find which instructions take the most time and why
4. **Optimize:** Test 3-4 different instruction orderings or compiler strategies and measure improvement
5. **Extrapolate:** Project findings to full-size images and estimate annual cost savings

### Test Cases You Must Analyze

| Test Case | Pixel Intensities | Why It Matters |
|---|---|---|
| Best Case | All pixels = 0 (pure black) | All pixels take ADD path; branch predictor works perfectly |
| Worst Case | Alternating 64, 192, 64, 192... | Branch predictor fails every iteration; maximum pipeline flushes |
| Real Case 1 | Indoor photo: 70% dark, 30% bright pixels | Realistic distribution; predictor gets ~70% correct |
| Real Case 2 | Sunset photo: clustered bright in top-half, dark in bottom-half | Predictor adapts; different patterns in different image regions |

## 📊 Key Performance Metrics You'll Measure

| Metric | Target | Notes |
|---|---|---|
| Cycles Per Pixel (CPP) | <5 cycles | Current: ~7 cycles. Every 0.5 cycle saved = 40 million pixels more per day |
| Cache Hit Rate | >95% | L1 cache miss = 50+ cycle penalty. Bad prefetching = 10% miss rate increase |
| Branch Prediction Accuracy | >90% | Misprediction = 15 cycle pipeline flush. Alternating pattern = 0% accuracy |
| Register Spill Count | 0 spills | Extra LOAD/STORE to stack memory = 200+ cycle penalty per spill |

## 🎓 What You'll Learn

By completing this project, you will understand:

- ✓ **CPU Fetch-Decode-Execute Cycle:** How each instruction moves through the pipeline and affects overall execution time
- ✓ **Register Management:** How limited registers force spilling and performance degradation
- ✓ **Cache Hierarchy:** Why sequential access patterns matter and how cache misses compound
- ✓ **Branch Prediction:** How data patterns affect predictor accuracy and pipeline performance
- ✓ **Instruction-Level Parallelism (ILP):** How out-of-order execution can hide some latencies but not others
- ✓ **Energy-Performance Trade-offs:** Why you can't always run at full clock speed and meet cost targets
- ✓ **Real-World Optimization:** How small instruction-level changes scale to millions of images and thousands of dollars

## 📦 What You'll Deliver

### In Your Analysis Report

**1. Instruction Trace (5+ experiments):**
- Full cycle-by-cycle breakdown for each test case
- Screenshots showing register values, memory state, PC progression
- Cache hit/miss events and branch predictions for each iteration

**2. Performance Data:**
- Total cycles for each test case
- Cycles per pixel (CPP) metric
- Cache miss rate, branch mispredict rate
- Register spill count

**3. Optimization Analysis:**
- Compare 3+ optimization strategies (e.g., loop unrolling, branch-free code, loop tiling)
- Measure improvement for each strategy
- Identify which strategy works best for which test case

**4. Extrapolation & Cost Impact:**
- Scale findings to full-size images (256x256 pixels = 65,536 pixels)
- Calculate total cycles for processing 2 million images/day
- Estimate electricity cost (8 watts, $0.12/kWh, 24-hour operation)
- Estimate server count needed to meet 4-hour SLA
- Project annual cost savings from 20% cycle reduction

## 📁 Supporting Materials Available

- **Simulator:** Interactive HTML widget to trace CPU execution and collect metrics
- **Reference Guide:** CPU architecture details (pipeline stages, cache parameters, latencies)
- **Data Templates:** Excel sheets for organizing experimental results
- **Video Tutorial:** How to use the simulator and interpret results (if available)

---

*Project 1: CPU Instruction Execution - Image Brightness Processing*
*Real-world scenario designed for hands-on learning of CPU architecture and performance optimization*
