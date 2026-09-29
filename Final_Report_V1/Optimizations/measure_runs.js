// Measurement harness used on 29 September 2026 to compare the baseline program
// with the three optimization variants. Each call runs the selected test case
// n times through the page's own initSimulation() and stepForward(), records the
// final counters, and checks every output value against the brightness rule.
// Real Case 2 is pinned to the saved Run 8 input list so all four programs
// process identical inputs.
window.__measure = function (caseName, n) {
  testCases.real2 = [215, 210, 254, 221, 231, 244, 220, 236, 39, 27, 41, 71, 80, 92, 8, 55];
  const out = [];
  for (let i = 0; i < n; i++) {
    document.getElementById('testCase').value = caseName;
    initSimulation();
    let g = 0;
    while (state.pc < instructions.length - 1 && g++ < 400) stepForward();
    const expected = state.pixels.map(p => p < 128 ? Math.min(255, p + 32) : Math.max(0, p - 8));
    out.push({
      cycles: state.cycles,
      hits: state.cache.hits, misses: state.cache.misses,
      correct: state.branchHits, branches: state.branchTotal,
      wrong: state.branchTotal - state.branchHits,
      stalls: state.stalls,
      ok: state.outputPixels.every((v, j) => v === expected[j])
    });
  }
  return out;
};
'__measure ready';
