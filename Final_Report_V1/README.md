# Final Report V1

Start with **[Final_Report.md](Final_Report.md)**. It combines the current project's Runs 1–4, Runs 5–8 from [Scarlet-astra/BSC104_final_project](https://github.com/Scarlet-astra/BSC104_final_project/tree/016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9), and the new traced runs and measured optimizations recorded in this folder.

## Contents

| File or folder | Purpose |
|---|---|
| [Final_Report.md](Final_Report.md) | Combined report: twelve recorded runs, step traces, measured optimization study, scaling and cost sections |
| [Grading.md](Grading.md) | Provisional assessment (100/100 under the proposed rubric) with recovered deductions and remaining caveats |
| [Repository_Comparison.md](Repository_Comparison.md) | Source comparison, corrections and merge decisions |
| [Appendix_Pixel_Paths.md](Appendix_Pixel_Paths.md) | Reconstructed paths for Runs 1–8; Runs 9–12 have recorded logs in `Traces/` |
| [Traces/](Traces/) | Runs 9–12: raw step records (`*_trace.json`), readable step logs, 24 checkpoint screenshots, drivers and analysis scripts, `trace_summary.json` |
| [Optimizations/](Optimizations/) | Four variant simulators, measurement raw data (800 runs), `measured_summary.json`, generator and analysis scripts, sample screenshots |
| [data.json](data.json) | Normalized metrics, pixel lists and provenance for all twelve runs |
| [source_manifest.json](source_manifest.json) | Repository commit IDs and checksums of the 41 archived source files |
| [evidence_manifest.json](evidence_manifest.json) | SHA-256 checksums of the 53 trace and optimization evidence files |
| [verify_final_report.py](verify_final_report.py) | Python 3 verifier for the whole package; standard library only |
| [Sources/Local](Sources/Local/) | Unmodified Local reports, logs, simulator, instructions, workbook, reproduction guide, original verifier and eight screenshots |
| [Sources/Scarlet](Sources/Scarlet/) | Unmodified Scarlet reports, logs, simulator, instructions, two workbooks and twelve screenshots |

## Status

- **Twelve recorded experiments**: three per test case (Runs 1–8 final states; Runs 9–12 complete step traces).
- **Event-level evidence**: Runs 9–12 record every cache event and brightness prediction with positions; all cycle intervals checked against the cost model.
- **Measured optimizations**: branch-free selection, unrolling, pointer loop-testing and their combination; 40 runs per case per program (800 runs), all outputs verified.
- **Remaining limitations**: prefetching stays a calculation (the simulator has no cache contents); variant results are model measurements with documented cost assumptions; Runs 1–8 keep their reconstructed paths only.

## Verify

From the repository root:

```bash
python3 Final_Report_V1/verify_final_report.py
```

Or from this folder:

```bash
python3 verify_final_report.py
```

The package is self-contained and can be moved with its `Sources/`, `Traces/` and `Optimizations/` folders. The verifier is read-only: it checks source and evidence checksums, re-derives all report tables from `data.json` and the raw records, validates the 800 measured runs, checks the grading arithmetic, and resolves every local link.

## Reproduce or extend the report

1. Read the archived assignment scenario, both Logs.md files, `Repository_Comparison.md` and the step logs in `Traces/`.
2. Retain source filenames, run IDs and the marker comments (`<!-- table:... -->`) that the verifier uses to locate tables.
3. Recalculate from total cycles and integer event counts; round only for display. Keep estimates, inferred inputs and model measurements labelled.
4. To add a new traced run, reuse the pattern of `Traces/collect_trace.js` and `Traces/analyze_traces.py`, then regenerate `trace_summary.json` and `data.json`.
5. To change a variant, edit `Optimizations/make_variants.py`, regenerate, re-run `measure_runs.js`, and re-summarize with `summarize_measurements.py` before updating the report.
6. After any change to `Traces/` or `Optimizations/`, rebuild `evidence_manifest.json` (hash every file in those folders) so the verifier accepts the new state.

The Local [Report_Maker.md](Sources/Local/Report_Maker.md) documents the earlier four-run workflow. For this twelve-run version, use the status, interpretation corrections and checks in this folder.
