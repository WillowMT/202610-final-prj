"""Build the three optimization variants from the original simulator.

Each variant file is the original Project1_CPU_Simulator.html plus an appended
script that replaces the instruction program and the stepForward() function.
The teaching model's costs, cache randomization and messages are preserved.
Run: python3 make_variants.py <original simulator> <output folder>
"""
from pathlib import Path
import json
import sys

ENGINE = """
<script>
// Optimization variant appended by make_variants.py on 29 September 2026.
// The instruction program and stepForward() are replaced below. All cost rules,
// cache randomness, branch probabilities and messages follow the original file.
(function () {
  const PROGRAM = JSON.parse('__PROGRAM_JSON__');
  testCases.real2 = [215, 210, 254, 221, 231, 244, 220, 236, 39, 27, 41, 71, 80, 92, 8, 55];
  instructions.length = 0;
  for (const item of PROGRAM) instructions.push(item);
  const haltIndex = PROGRAM.findIndex(function (i) { return i.kind === 'halt'; });
  function summaryHTML(instr, msg) {
    return '<div><strong>Current Instruction:</strong> ' + instr.addr + ' ' + instr.code + '</div>' +
      '<div style="color: #ffff00; margin-top: 4px;"><strong>Action:</strong> ' + msg + '</div>' +
      '<div style="margin-top: 4px;"><strong>Pixels Processed:</strong> ' + state.pixelIndex + '/16</div>';
  }
  stepForward = function () {
    if (state.pc >= instructions.length || state.pc === haltIndex) {
      state.running = false; stopTimer();
      updateStatus('\u2713 Complete! All 16 pixels processed.'); updateDisplay(); return false;
    }
    const instr = instructions[state.pc];
    let cycles = instr.cycles, nextPc = state.pc + 1, msg = '';
    state.prevRegisters = { ...state.registers };
    switch (instr.kind) {
      case 'setup0': state.registers.r0 = 0; msg = 'Initialized loop counter R0 = 0'; break;
      case 'setup1': state.registers.r1 = 1024; msg = 'Initialized RAM pixel pointer R1 = 1024'; break;
      case 'load': {
        const px = state.pixelIndex + (instr.offset || 0);
        if (Math.random() > 0.2) {
          state.cache.hits++;
          msg = 'Cache HIT: Loaded pixel[' + px + '] = ' + state.pixels[px] + ' into R3';
        } else {
          state.cache.misses++; cycles += 47; state.stalls += 47;
          msg = 'Cache MISS (+47 cycles stall): Loaded pixel[' + px + '] = ' + state.pixels[px] + ' from DRAM';
        }
        state.registers.r3 = state.pixels[px] || 0; break; }
      case 'cmpb': msg = 'Compared pixel R3 (' + state.registers.r3 + ') with threshold R2 (128)'; break;
      case 'blt':
        state.branchTotal++;
        if (Math.random() < (state.testCase === 'best' ? 0.95 : (state.testCase === 'worst' ? 0.50 : 0.80))) {
          state.branchHits++; msg = 'Branch HIT: ';
        } else {
          cycles += 15; state.stalls += 15; msg = 'Branch MISPREDICT (+15 cycles stall): ';
        }
        if (state.registers.r3 < state.registers.r2) {
          msg += 'Pixel is dark (< 128) -> Jumping to DARK (' + PROGRAM[instr.darkPc].addr + ')'; nextPc = instr.darkPc;
        } else {
          msg += 'Pixel is bright (>= 128) -> Continuing to SUB (' + PROGRAM[instr.brightPc].addr + ')'; nextPc = instr.brightPc;
        }
        break;
      case 'sub': state.registers.r4 = Math.max(0, state.registers.r3 - state.registers.r7);
        msg = 'Bright pixel: Reduced glare (R4 = ' + state.registers.r3 + ' - 8 = ' + state.registers.r4 + ')'; break;
      case 'jmp': msg = 'Unconditional Jump to STORE (' + PROGRAM[instr.target].addr + ')'; nextPc = instr.target; break;
      case 'add': state.registers.r4 = Math.min(255, state.registers.r3 + state.registers.r6);
        msg = 'Dark pixel: Boosted brightness (R4 = ' + state.registers.r3 + ' + 32 = ' + state.registers.r4 + ')'; break;
      case 'store': {
        const px = state.pixelIndex + (instr.offset || 0);
        state.outputPixels[px] = state.registers.r4;
        msg = 'Stored output pixel[' + px + '] = ' + state.registers.r4 + ' into memory'; break; }
      case 'inc1': state.registers.r1++; msg = 'Incremented memory pointer R1 = ' + state.registers.r1; break;
      case 'inc1p': state.registers.r1++; state.pixelIndex = state.registers.r1 - 1024;
        msg = 'Incremented memory pointer R1 = ' + state.registers.r1 + ' (address is the loop control)'; break;
      case 'inc4': state.registers.r1 += 4; msg = 'Incremented memory pointer R1 = ' + state.registers.r1 + ' (four pixels)'; break;
      case 'inc0': state.registers.r0++; state.pixelIndex++;
        msg = 'Incremented pixel counter R0 = ' + state.registers.r0 + ' (' + state.pixelIndex + '/16 completed)'; break;
      case 'inc04': state.registers.r0 += 4; state.pixelIndex += 4;
        msg = 'Incremented pixel counter R0 = ' + state.registers.r0 + ' (' + state.pixelIndex + '/16 completed)'; break;
      case 'cmpn': msg = 'Checked loop condition (R0 == 16)'; break;
      case 'cmp1': msg = 'Checked loop condition (R1 == 1040)'; break;
      case 'bne1':
        state.branchTotal++;
        if (state.registers.r1 < 1040) {
          state.branchHits++; msg = 'Loop continuation: R1 < 1040 -> Branching back to LOOP (' + PROGRAM[instr.target].addr + ')'; nextPc = instr.target;
        } else {
          state.branchHits++; msg = 'All 16 pixels completed! Proceeding to HALT (' + PROGRAM[haltIndex].addr + ')'; nextPc = haltIndex;
        }
        break;
      case 'bne':
        state.branchTotal++;
        if (state.registers.r0 < 16) {
          state.branchHits++; msg = 'Loop continuation: R0 < 16 -> Branching back to LOOP (' + PROGRAM[instr.target].addr + ')'; nextPc = instr.target;
        } else {
          state.branchHits++; msg = 'All 16 pixels completed! Proceeding to HALT (' + PROGRAM[haltIndex].addr + ')'; nextPc = haltIndex;
        }
        break;
      case 'cand': state.registers.r4 = Math.min(255, state.registers.r3 + state.registers.r6);
        msg = 'Branch-free: dark candidate R4 = ' + state.registers.r4; break;
      case 'csub': state.registers.r5 = Math.max(0, state.registers.r3 - state.registers.r7);
        msg = 'Branch-free: bright candidate R5 = ' + state.registers.r5; break;
      case 'csel': state.registers.r4 = state.registers.r3 >= state.registers.r2 ? state.registers.r5 : state.registers.r4;
        msg = 'Branch-free select: R4 = ' + state.registers.r4 + ' (no brightness branch to predict)'; break;
    }
    state.cycles += cycles;
    state.pc = nextPc;
    document.getElementById('executionSummary').innerHTML = summaryHTML(instr, msg);
    updateDisplay();
    if (state.pc === haltIndex || state.pc >= instructions.length) {
      state.running = false; stopTimer();
      updateStatus('\u2713 Complete! All 16 pixels processed.');
      return false;
    }
    return true;
  };
})();
</script>
"""


def instruction(index, addr, code, cycles, kind, **extra):
    item = {"index": index, "addr": addr, "code": code, "cycles": cycles, "kind": kind}
    item.update(extra)
    return item


def core_sequence(start_index, addr_of, offset):
    base = 0
    return [
        instruction(base, addr_of(start_index + base), "LOAD R3, [R1]", 3, "load", offset=offset),
        instruction(base + 1, addr_of(start_index + base + 1), "CMP R3, R2", 1, "cmpb"),
        instruction(base + 2, addr_of(start_index + base + 2), "BLT DARK", 1, "blt",
                    darkPc=start_index + base + 5, brightPc=start_index + base + 3),
        instruction(base + 3, addr_of(start_index + base + 3), "SUB R4, R3, R7", 1, "sub"),
        instruction(base + 4, addr_of(start_index + base + 4), "JMP STORE", 2, "jmp",
                    target=start_index + base + 6),
        instruction(base + 5, addr_of(start_index + base + 5), "DARK: ADD R4, R3, R6", 1, "add"),
        instruction(base + 6, addr_of(start_index + base + 6), "STORE: STORE R4, [R1]", 3, "store", offset=offset),
    ]


def build_branchfree():
    return [
        instruction(0, "0x00", "LOAD R0, #0", 1, "setup0"),
        instruction(1, "0x04", "LOAD R1, #1024", 1, "setup1"),
        instruction(2, "0x08", "LOOP: LOAD R3, [R1]", 3, "load"),
        instruction(3, "0x0C", "ADD R4, R3, R6", 1, "cand"),
        instruction(4, "0x10", "SUB R5, R3, R7", 1, "csub"),
        instruction(5, "0x14", "CMP R3, R2", 1, "cmpb"),
        instruction(6, "0x18", "CSEL R4, R5, R4, GE", 1, "csel"),
        instruction(7, "0x1C", "STORE: STORE R4, [R1]", 3, "store"),
        instruction(8, "0x20", "INC R1, #1", 1, "inc1"),
        instruction(9, "0x24", "INC R0, #1", 1, "inc0"),
        instruction(10, "0x28", "CMP R0, #16", 1, "cmpn"),
        instruction(11, "0x2C", "BNE LOOP", 1, "bne", target=2),
        instruction(12, "0x30", "HALT", 1, "halt"),
    ]


def build_unrolled():
    program = [
        instruction(0, "0x00", "LOAD R0, #0", 1, "setup0"),
        instruction(1, "0x04", "LOAD R1, #1024", 1, "setup1"),
    ]
    addr_of = lambda i: "0x%02X" % (0x08 + 4 * (i - 2))
    for copy_number in range(4):
        start = len(program)
        for item in core_sequence(start, addr_of, copy_number):
            if item["kind"] == "load":
                item["code"] = ("LOOP: LOAD R3, [R1]" if copy_number == 0 else "LOAD R3, [R1, #%d]" % copy_number)
            program.append(item)
    end = len(program)
    program.append(instruction(end, addr_of(end), "INC R1, #4", 1, "inc4"))
    program.append(instruction(end + 1, addr_of(end + 1), "INC R0, #4", 1, "inc04"))
    program.append(instruction(end + 2, addr_of(end + 2), "CMP R0, #16", 1, "cmpn"))
    program.append(instruction(end + 3, addr_of(end + 3), "BNE LOOP", 1, "bne", target=2))
    program.append(instruction(end + 4, addr_of(end + 4), "HALT", 1, "halt"))
    return program


def build_combined():
    program = [
        instruction(0, "0x00", "LOAD R0, #0", 1, "setup0"),
        instruction(1, "0x04", "LOAD R1, #1024", 1, "setup1"),
    ]
    addr_of = lambda i: "0x%02X" % (0x08 + 4 * (i - 2))
    for copy_number in range(4):
        start = len(program)
        program.append(instruction(start, addr_of(start),
                                   "LOOP: LOAD R3, [R1]" if copy_number == 0 else "LOAD R3, [R1, #%d]" % copy_number, 3, "load",
                                   offset=copy_number))
        program.append(instruction(start + 1, addr_of(start + 1), "ADD R4, R3, R6", 1, "cand"))
        program.append(instruction(start + 2, addr_of(start + 2), "SUB R5, R3, R7", 1, "csub"))
        program.append(instruction(start + 3, addr_of(start + 3), "CMP R3, R2", 1, "cmpb"))
        program.append(instruction(start + 4, addr_of(start + 4), "CSEL R4, R5, R4, GE", 1, "csel"))
        program.append(instruction(start + 5, addr_of(start + 5), "STORE: STORE R4, [R1]", 3, "store", offset=copy_number))
    end = len(program)
    program.append(instruction(end, addr_of(end), "INC R1, #4", 1, "inc4"))
    program.append(instruction(end + 1, addr_of(end + 1), "INC R0, #4", 1, "inc04"))
    program.append(instruction(end + 2, addr_of(end + 2), "CMP R0, #16", 1, "cmpn"))
    program.append(instruction(end + 3, addr_of(end + 3), "BNE LOOP", 1, "bne", target=2))
    program.append(instruction(end + 4, addr_of(end + 4), "HALT", 1, "halt"))
    return program


def build_looptest():
    return [
        instruction(0, "0x00", "LOAD R0, #0", 1, "setup0"),
        instruction(1, "0x04", "LOAD R1, #1024", 1, "setup1"),
        instruction(2, "0x08", "LOOP: LOAD R3, [R1]", 3, "load"),
        instruction(3, "0x0C", "CMP R3, R2", 1, "cmpb"),
        instruction(4, "0x10", "BLT DARK", 1, "blt", darkPc=7, brightPc=5),
        instruction(5, "0x14", "SUB R4, R3, R7", 1, "sub"),
        instruction(6, "0x18", "JMP STORE", 2, "jmp", target=8),
        instruction(7, "0x1C", "DARK: ADD R4, R3, R6", 1, "add"),
        instruction(8, "0x20", "STORE: STORE R4, [R1]", 3, "store"),
        instruction(9, "0x24", "INC R1, #1", 1, "inc1p"),
        instruction(10, "0x28", "CMP R1, #1040", 1, "cmp1"),
        instruction(11, "0x2C", "BNE LOOP", 1, "bne1", target=2),
        instruction(12, "0x30", "HALT", 1, "halt"),
    ]


def main():
    original = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2])
    assert "</body>" in original, "Original simulator structure changed"
    for name, program in [
        ("Simulator_BranchFree.html", build_branchfree()),
        ("Simulator_Unrolled.html", build_unrolled()),
        ("Simulator_Combined.html", build_combined()),
        ("Simulator_LoopTest.html", build_looptest()),
    ]:
        blob = json.dumps([{k: v for k, v in item.items() if k != "index"} for item in program])
        script = ENGINE.replace("__PROGRAM_JSON__", blob)
        target = out / name
        target.write_text(original.replace("</body>", script + "</body>"), encoding="utf-8")
        print(f"{name}: {len(program)} instructions")


if __name__ == "__main__":
    main()
