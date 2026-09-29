# 🎮 How to Use Project 1 Simulator

**Step-by-Step Guide to CPU Instruction Execution**

## ⚡ Quick Start (2 Minutes)

1. **Open Simulator**
   - Click on: `Project1_CPU_Instruction_Simulator.html`

2. **Choose Test Case**
   - Dropdown shows 4 options:
     - Best Case: All pixels = 0 (easiest)
     - Worst Case: Alternating pattern (hardest)
     - Real Case 1: 70% dark (realistic)
     - Real Case 2: Clustered bright/dark

3. **Click START SIMULATION**
   - Prepares the simulator for your test case

4. **Click STEP FORWARD or RUN ALL**
   - STEP FORWARD: Execute one instruction at a time (watch what happens)
   - RUN ALL: Run entire algorithm automatically

5. **Collect Results**
   - Screenshot the final metrics or copy the "DETAILED METRICS" section

## 🎛️ Control Panel (Left Side)

| Control | Description |
|---|---|
| **TEST CASE** | Choose which pixel pattern to test. Each case shows different CPU behavior. |
| **SPEED** | Slider controls animation speed (50-1000ms per instruction). Lower = slower, higher = faster. |
| **▶ START** | Initialize simulator with chosen test case. Must click this first! |
| **↓ STEP** | Execute ONE instruction. Watch register values change in real-time. |
| **⏩ RUN ALL** | Execute entire algorithm automatically. Faster than stepping through manually. |
| **🔄 RESET** | Clear all data and restart. Use this to switch to a different test case. |

## 📊 Understanding the Display

### 📝 Instruction Sequence (Top-Left)

- Yellow highlight: Currently executing instruction
- Gray text: Already completed instructions
- PC (Program Counter): Memory address of instruction
- Code: The actual CPU instruction
- Cycles: How many CPU cycles this instruction normally takes

### 📦 Registers (Top-Right)

- **R0:** Loop counter (counts pixels 0-15)
- **R1:** Pixel address (starts at 1024)
- **R2:** Threshold value (128 = midpoint brightness)
- **R3:** Current pixel value (loaded from memory)
- **R4:** Result pixel (adjusted brightness)
- **R6:** Add offset (+32 for dark pixels)
- **R7:** Subtract offset (-8 for bright pixels)

💡 **Watch R3 and R4:** You'll see pixel values being read and adjusted.

### 🎨 Pixel Data (Middle-Left)

- Top grid: Original pixel values (grayscale colors)
- Bottom grid: Adjusted pixel values after brightness processing
- Darker pixels: Get +32 brightness (become lighter)
- Brighter pixels: Get -8 brightness (become slightly darker for tone balance)

### 💾 Memory & ⚡ Cache (Middle-Right)

- Memory: Shows pixels being read/written
- Cache: Shows hits (fast, 3 cycles) vs misses (slow, 50 cycles)
- Red highlight: Cache miss = penalty cycles
- Green highlight: Cache hit = normal speed

### 📋 Event Log (Bottom-Right)

- Red: Cache misses (performance problem)
- Orange: Branch mispredictions (pipeline flush)
- Blue: Pipeline stalls (waiting for data)

### 📊 Detailed Metrics (Bottom)

- Total cycles for this test case
- Cycles per pixel (CPP) - key metric for optimization
- Cache hit rate (% of memory accesses that are fast)
- Branch prediction accuracy
- Estimated cycles for full-size image (256×256)

## 📈 Key Metrics You're Measuring

| Metric | What It Means | Good Value | Bad Value |
|---|---|---|---|
| Total Cycles | Sum of all CPU cycles used | <100 for 16 pixels | >200 for 16 pixels |
| Cycles Per Pixel | Average cycles spent on each pixel | <5 CPP | >10 CPP |
| Cache Hit Rate | % of memory accesses that find data in fast cache | >95% hits | <50% hits |
| Branch Accuracy | % of branch predictions that were correct | >90% correct | <50% correct |
| Pipeline Stalls | Extra cycles wasted waiting for data | 0 stalls | >100 stalls |

## 📋 Complete Workflow for Analysis

### ✓ For Each Test Case (Do 4 times - once per case)

1. Click **RESET** to clear previous data
2. Select test case from dropdown
3. Click **START SIMULATION**
4. Choose: **STEP FORWARD** (to observe) OR **RUN ALL** (to get results faster)
5. Wait for "SIMULATION COMPLETE" message
6. Take screenshot of DETAILED METRICS (bottom panel)
7. Copy key numbers: Total Cycles, CPP, Cache Hit Rate, Branch Accuracy
8. Record in your Excel data collection sheet

### Optional: Detailed Observation (For Deep Learning)

Instead of RUN ALL, try STEP FORWARD 3-4 times per test case to see:

- How registers change with each instruction
- When cache hits vs misses happen
- How branch predictor works (right/wrong)
- When pixels get brightened or darkened

## 📊 Data Collection Template

Copy this into your Excel spreadsheet:

| Test Case | Total Cycles | Cycles/Pixel | Cache Hits | Cache Misses | Cache Hit % | Branch Correct | Branch Total | Accuracy % |
|---|---|---|---|---|---|---|---|---|
| Best (All 0) | | | | | | | | |
| Worst (Alternating) | | | | | | | | |
| Real Case 1 (70% Dark) | | | | | | | | |
| Real Case 2 (Clustered) | | | | | | | | |

## 👉 Example: Running "Best Case" Test

### Step 1: Select & Start

- Dropdown: "Best Case: All Dark (0)"
- Click: "START SIMULATION"
- Status shows: "Simulation initialized"

### Step 2: Run Simulation

- Click: "RUN ALL"
- Watch the progress...
  - Instruction Window: PC moves 0x00 → 0x04 → 0x08... until 0x34
  - Registers: R0 increases (0→1→2...→16)
  - Pixels: Output grid fills with adjusted pixel values

### Step 3: Check Results

- Status shows: "✓ Execution complete!"
- Scroll to: "DETAILED METRICS" panel
- See example output:
  - Total Cycles: 87
  - Cycles Per Pixel: 5.44
  - Cache Hits: 14
  - Cache Misses: 2
  - Hit Rate: 87.5%
  - Branch Accuracy: 100% (Best case!)

### Step 4: Record Data

- Screenshot DETAILED METRICS
- Copy numbers into Excel sheet under "Best Case" row

## ❓ Common Questions

**Q: Why does "Worst Case" have higher cycles than "Best Case"?**
A: Branch mispredictions cause 15+ cycle penalties. Worst case alternates pixels, so predictor gets it wrong half the time. Best case all pixels are dark, so predictor gets it right every time.

**Q: What is "Cycles Per Pixel" and why does it matter?**
A: It's the average CPU time spent per pixel. For 2M images/day, reducing CPP from 7 to 5 = 40% faster processing = millions in cost savings!

**Q: What is cache and why do misses hurt?**
A: Cache is super-fast memory (3 cycles to access). Misses force CPU to fetch from slow main memory (50 cycles). One miss = 47 wasted cycles!

**Q: Why do I need to run all 4 test cases?**
A: Each shows different behavior. Best/Worst show extreme cases. Real cases show what actually happens in real photos. Comparing teaches you about CPU optimization.

**Q: What should I put in my analysis report?**
A: (1) Screenshot of results for each test case, (2) Explanation of why each case had different performance, (3) Which metrics matter most, (4) How to optimize (e.g., branch-free code), (5) Cost impact on full 256×256 images.

## 🎯 Next Steps After Running Simulator

1. **Collect Data:** Run all 4 test cases, record metrics in Excel
2. **Analyze Results:** Why did each case perform differently?
3. **Find Bottleneck:** Is it cache, branches, or memory bandwidth?
4. **Optimize:** Write your analysis on how to improve (loop unrolling, branch prediction, cache prefetching)
5. **Extrapolate:** Scale CPP to full 256×256 image (multiply by 4096)
6. **Calculate Cost:** How much money saved per day if you reduce CPP by 1?

---

*Project 1: CPU Instruction Simulator Usage Guide*
*Ready to learn about CPU architecture? Open the simulator and start experimenting!*
