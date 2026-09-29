// Trace driver used to record Runs 9-12 (one per test case) on 29 September 2026.
// It sets the case and speed, initializes a fresh run, then advances the simulator
// one instruction at a time via its own stepForward() function, recording the
// displayed execution summary and full register/event state after every step.
document.getElementById('speed').value = 50;
document.getElementById('speedValue').textContent = '50';
document.getElementById('testCase').value = CASE_NAME;
initSimulation();
window.__trace = { case: CASE_NAME, input: [...state.pixels], steps: [] };
window.__step = function () {
  const beforePc = state.pc;
  const beforeCycles = state.cycles;
  stepForward();
  const summary = document.getElementById('executionSummary').textContent;
  window.__trace.steps.push({
    pc: instructions[beforePc].addr,
    nextPC: (instructions[state.pc] || { addr: '0x34' }).addr,
    cyclesAdded: state.cycles - beforeCycles,
    runningCycles: state.cycles,
    r0: state.registers.r0, r1: state.registers.r1, r2: state.registers.r2,
    r3: state.registers.r3, r4: state.registers.r4, r5: state.registers.r5,
    r6: state.registers.r6, r7: state.registers.r7,
    pixelIndex: state.pixelIndex,
    hits: state.cache.hits, misses: state.cache.misses,
    branchHits: state.branchHits, branchTotal: state.branchTotal,
    stalls: state.stalls,
    summary: summary.replace(/\s+/g, ' ')
  });
};
