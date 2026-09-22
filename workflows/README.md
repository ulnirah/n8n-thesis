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

1. Clone the repository to `C:\n8n-thesis` and create the folder `C:\n8n-thesis\output`.
2. In n8n, open **Workflows → Import from File** and select `thesis/n8n_ifc_dual_pipeline.json`.
3. Open node **0.1 Config** and check:

   | Field | Value |
   |---|---|
   | `path_to_converter` | Full path to `IfcExporter.exe` (set to `C:\DDC_Converters_Windows_Packages\DDC_CONVERTER_IFC\IfcExporter.exe`) |
   | `project_file` | IFC file for Pipeline A, and for Pipeline B in single-file runs (set to M1 in `C:\n8n-thesis`) |
   | `project_file_b` | Faulted variant for Pipeline B in dual-file runs; **empty by default, leave it empty for single-file and baseline runs** |
   | `output_dir` | Folder for the reports and exports (`C:\n8n-thesis\output`) |
   | `script_dir` | Folder for `extract_ifc.py` (`C:\n8n-thesis\scripts`) |

   Change these only if your folders differ.

   The other Config values (BQI weights, α = 0.55, coverage threshold 95%) are the thesis parameters and should stay unchanged to reproduce the results.
4. Delete any old `<file name>_ifc.xlsx` next to the input file, so that Pipeline A converts the current file instead of reusing a stale conversion.
5. Click **Execute Workflow**.

Node 2.1 downloads `extract_ifc.py` from release `v1.0.2` into `script_dir`, so no other node needs editing.

---

## The DDC Base Workflows

The nine files in `ddc-base/` are kept exactly as published by DDC, to record where Pipeline A comes from. They contain DDC's own hardcoded paths (for example `C:\Users\Artem Boiko\...`) and are not needed to reproduce the thesis. Their contents are described in [`ddc-base/README.md`](ddc-base/README.md).

---

## Versions

The thesis cites repository release `v1.0.2`. In `v1.0.2` the workflow export was prepared for reuse (portable paths, empty `project_file_b`, script download pinned to the release, corrected notes and comments); its computation is identical to the export used for the thesis runs. The SHA-256 of `n8n_ifc_dual_pipeline.json` listed in Annex III is that of the export in `v1.0.1`. See [`thesis/README.md`](thesis/README.md) for the full list of changes.
