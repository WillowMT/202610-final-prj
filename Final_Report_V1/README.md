# Final Report V1

Start with **[Final_Report.md](Final_Report.md)**. It combines the current project's Runs 1–4 with Runs 5–8 from [Scarlet-astra/BSC104_final_project](https://github.com/Scarlet-astra/BSC104_final_project/tree/016e2f92b9186c4a5ae9b7b9b27ed8eee4e915f9).

## Contents

| File or folder | Purpose |
|---|---|
| [Final_Report.md](Final_Report.md) | Combined report organized around all four assignment deliverables, with all eight runs and the six quick-guide questions |
| [Grading.md](Grading.md) | Provisional 74/100 assessment; proposed weights are clearly distinguished from an official rubric |
| [Repository_Comparison.md](Repository_Comparison.md) | Source comparison, corrections and merge decisions |
| [Appendix_Pixel_Paths.md](Appendix_Pixel_Paths.md) | All 128 input/output pairs, evidence labels, calculated paths and base-cycle totals; part of the report |
| [data.json](data.json) | Normalized metrics and pixel lists for all eight historical runs |
| [source_manifest.json](source_manifest.json) | Repository commit IDs and checksums of the 41 archived evidence files |
| [verify_final_report.py](verify_final_report.py) | Python 3 verifier for the eight-run package; standard library only |
| [Sources/Local](Sources/Local/) | Unmodified Local reports, logs, simulator, instructions, workbook, reproduction guide, original verifier and eight screenshots |
| [Sources/Scarlet](Sources/Scarlet/) | Unmodified Scarlet reports, logs, simulator, instructions, two workbooks and twelve screenshots |

## Status

There are eight completed baseline experiments, with two runs per case. All recorded cycle totals reconcile. The two outstanding evidence areas are **actual instruction/event histories** and **measured tests of three optimizations**. The report identifies these gaps and the grading deducts for them.

Archived source reports retain their original wording, including status statements that the combined report supersedes. The trace workbook is a blank template. The original four-run verifier remains archived for its original scope; use the new verifier for this package.

## Verify

From the repository root:

```bash
python3 Final_Report_V1/verify_final_report.py
```

Or from this folder:

```bash
python3 verify_final_report.py
```

The package is self-contained. It can be moved with its `Sources/` folder and verified without the live GitHub repository or temporary checkout. The verifier is read-only and uses paths relative to its own location.

## Reproduce or extend the report

1. Read the archived assignment scenario, both Logs.md files and Repository_Comparison.md.
2. Retain source filenames and run IDs. Count a screenshot group as one experiment.
3. Recalculate from total cycles and integer event counts; round only for display. Keep estimates and inferred inputs labelled.
4. Update the combined report and pixel appendix from any new evidence. A new event trace belongs to a new run, not an old run with guessed event positions.
5. Update the verifier and data schema deliberately if the experiment set changes. Keep this V1 snapshot intact when producing a later report version.
6. Reassess the grade using the actual evidence. Completing prose or adding a blank template does not establish a missing measurement.

The Local [Report_Maker.md](Sources/Local/Report_Maker.md) documents the earlier four-run workflow. For this eight-run version, use the status, interpretation corrections and checks in this folder.
