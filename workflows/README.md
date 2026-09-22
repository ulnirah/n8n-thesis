# Workflows

This folder contains the n8n workflow files of the repository, in two subfolders:

| Subfolder | Contents | Use |
|---|---|---|
| [`thesis/`](thesis/) | `n8n_ifc_dual_pipeline.json`, the single integrated workflow used for every experiment in the thesis | Import and run |
| [`ddc-base/`](ddc-base/) | The nine original workflows of the DataDrivenConstruction (DDC) CAD-to-data toolkit, unchanged | Reference only; not run in the experiments |

---

## The Thesis Workflow

`thesis/n8n_ifc_dual_pipeline.json` runs the whole chain in one workflow: 44 functional nodes in six blocks, plus seven documentation notes.

| Block | Nodes | What it does |
|---|---|---|
| 0 Configuration | 0.0–0.1 | Manual trigger and the Config node with all paths and parameters |
| 1 Pipeline A | 1.1–1.10 | Converts the IFC to XLSX with the DDC IFC Exporter (or reuses an existing conversion), parses it, filters spatial rows, tags items `A_ddc` |
| 2 Pipeline B | 2.1–2.7 | Downloads and runs `scripts/extract_ifc.py` with IfcOpenShell, detects schema and domain, filters elements, tags items `B_ifcopenshell` |
| 3 QTO comparison and BQI | 3.1–3.5 | Merges both pipelines by `GlobalId`, compares quantities, checks element coverage, scores D1–D4 and computes SRCC |
| 4 Risk screening | 4.1–4.5 | Exposure, likelihood, consequence, uncertainty band, ranking and labels |
| 5 Output generation | 5.1–5.7 | HTML risk register, sensitivity JSON export and file writing |

Details: [`thesis/README.md`](thesis/README.md), and the documents in [`../docs/`](../docs/).

---

## Relationship to the DDC Workflows

The thesis workflow was built as one integrated pipeline; it is not a set of adapted copies of the DDC workflows. From DDC it uses:

- the **DDC IFC Exporter** (`IfcExporter.exe`, version 17.1.1.0) as the Pipeline A converter; and
- the same convert-then-parse-XLSX pattern as the DDC conversion and extraction workflows (`n8n_1`, `n8n_8`).

Everything from Block 2 onwards (IfcOpenShell extraction, comparison, BQI, risk screening, reporting, fault injection and analysis) was developed for the thesis. The DDC validation, classification, cost and carbon workflows are not used. See [`../docs/ddc-adaptation-notes.md`](../docs/ddc-adaptation-notes.md).

---

## Importing and Running the Thesis Workflow

Requirements: Windows, n8n 2.7.5, DDC IFC Exporter 17.1.1.0, Python 3 with IfcOpenShell 0.8.5.

1. In n8n, open **Workflows → Import from File** and select `thesis/n8n_ifc_dual_pipeline.json`.
2. Open node **0.1 Config** and set:

   | Field | Value |
   |---|---|
   | `path_to_converter` | Full path to `IfcExporter.exe` |
   | `project_file` | IFC file for Pipeline A, and for Pipeline B in single-file runs |
   | `project_file_b` | Faulted variant for Pipeline B in dual-file runs; **leave empty for single-file and baseline runs** |
   | `output_dir` | Folder for the reports and exports |
   | `script_dir` | Local folder for `extract_ifc.py` |

   The other Config values (BQI weights, α = 0.55, coverage threshold 95%) are the thesis parameters and should stay unchanged to reproduce the results.
3. Open node **2.1 Download script** and change the download folder in its command to match `script_dir`.
4. Delete any old `<file name>_ifc.xlsx` next to the input file, so that Pipeline A converts the current file instead of reusing a stale conversion.
5. Click **Execute Workflow**.

> **Important.** The exported workflow still contains paths from the original workstation (`C:\Users\milad.komary\...`) in node 0.1 and node 2.1, and `project_file_b` is pre-filled with an F4 variant. Update both nodes before running, or the run will fail or silently use the dual-file configuration.

---

## The DDC Base Workflows

The nine files in `ddc-base/` are kept exactly as published by DDC, to record where Pipeline A comes from. They contain DDC's own hardcoded paths (for example `C:\Users\Artem Boiko\...`) and are not needed to reproduce the thesis. Their contents are described in [`ddc-base/README.md`](ddc-base/README.md).

---

## Versions

The thesis cites repository release `v1.0.2`, which lists the SHA-256 of `n8n_ifc_dual_pipeline.json` in Annex III. The workflow files are identical in `v1.0.1` and `v1.0.2`.
