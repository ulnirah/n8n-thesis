# Thesis Workflow

This folder contains the n8n workflow that produced every result in the thesis:

**IFC input → dual extraction → QTO comparison → BQI → risk screening → risk register and sensitivity export**

| File | Role | SHA-256 (thesis Annex III) |
|---|---|---|
| `n8n_ifc_dual_pipeline.json` | Complete thesis workflow: 44 functional nodes in six blocks, plus 7 documentation notes | `4FC6B1A9B3881CC020EFA85B25270860DEBFA7CB1E62C9BF0E977F144A7410EC` |

It was built and run with **n8n 2.7.5** on Windows. It uses the external **DDC IFC Exporter 17.1.1.0** for Pipeline A and **IfcOpenShell 0.8.5** for Pipeline B. The original DDC workflows are kept separately in [`../ddc-base/`](../ddc-base/) as reference.

---

## Architecture

| Block | Nodes | Role |
|---|---|---|
| 0 Configuration | 0.0–0.1 | Trigger and run parameters |
| 1 Pipeline A | 1.1–1.10 | DDC conversion to XLSX, parsing, spatial filter, tag `A_ddc` |
| 2 Pipeline B | 2.1–2.7 | IfcOpenShell extraction, schema and domain detection, filter, tag `B_ifcopenshell` |
| 3 QTO comparison and BQI | 3.1–3.5 | Merge, comparison, element coverage, D1–D4 and BQI, SRCC |
| 4 Risk screening | 4.1–4.5 | Exposure, likelihood, consequence, risk band, ranking and labels |
| 5 Output generation | 5.1–5.7 | HTML risk register and per-element sensitivity JSON |

Three diagnostic nodes (Pipeline A, Pipeline B, BQI & Risk) dump intermediate results for inspection. They are outside the main sequence.

---

## Block 0 — Configuration

Node **0.1 Config** holds every run parameter:

| Field | Meaning | Thesis value |
|---|---|---|
| `path_to_converter` | Full path to `IfcExporter.exe` | local path |
| `project_file` | IFC file for Pipeline A (and for Pipeline B in single-file runs) | local path |
| `project_file_b` | Faulted IFC file for Pipeline B; set only for dual-file runs | local path or empty |
| `output_dir` | Folder for the report and the sensitivity JSON | local path |
| `script_dir` | Folder holding `extract_ifc.py` | local path |
| `group_by` | Grouping field inherited from the DDC workflows; not used by later nodes | `Category` |
| `bqi_weights` | Weights of D1–D4 | 0.35, 0.25, 0.20, 0.20 |
| `alpha` | Uncertainty coefficient α | 0.55 |
| `coverage_threshold` | Element coverage threshold | 95% |

The exported file still contains the paths of the original workstation, and `project_file_b` is filled in. Clear `project_file_b` for single-file runs; otherwise Pipeline B reads that file and the run becomes a dual-file run.

---

## Block 1 — Pipeline A: DDC Extraction

1. **1.1** Builds the expected XLSX path, `<IFC file name>_ifc.xlsx` next to the input file.
2. **1.2–1.3** If that XLSX already exists, conversion is skipped and the file is reused (1.3a).
3. **1.3b** Otherwise runs `IfcExporter.exe`.
4. **1.4** Checks the result; a failed conversion stops the run (1.4b, Stop and Error).
5. **1.5–1.8** Reads and parses the XLSX rows.
6. **1.9** Removes spatial rows such as `IfcProject`, `IfcSite`, `IfcBuilding` and `IfcBuildingStorey`.
7. **1.10** Tags every item as `A_ddc`.

Because of the cache in 1.2–1.3, delete old `_ifc.xlsx` files of faulted variants before a campaign; otherwise Pipeline A may read a stale conversion ([`../../docs/ddc-adaptation-notes.md`](../../docs/ddc-adaptation-notes.md), Section 12.5).

---

## Block 2 — Pipeline B: IfcOpenShell Extraction

1. **2.1** Downloads `scripts/extract_ifc.py` from the `main` branch of this repository into a local scripts folder.
2. **2.2** Verifies Python and IfcOpenShell.
3. **2.3** Runs `extract_ifc.py` with `--include-properties --include-materials` on `project_file_b` if it is set, otherwise on `project_file`.
4. **2.4** Parses the JSON output: elements, properties, quantities, materials, spatial structure and metadata.
5. **2.5** Detects the schema and domain. IFC 4 files are assigned the Building domain; IFC 4.3 files are classified from their element and spatial types.
6. **2.6** Removes metadata items and the categories `IfcProject`, `IfcSite`, `IfcBuilding`, `IfcBuildingStorey`, `IfcSpace` and `IfcFurniture`.
7. **2.7** Tags every item as `B_ifcopenshell`.

---

## Block 3 — QTO Comparison and BQI

- **3.1 Merge A+B** combines the items of both pipelines.
- **3.2 QTO comparison** matches elements on `GlobalId` and builds one comparison row per field name found in either pipeline, after removing the set prefix. Rows where both pipelines return a number are classified `exact`, `negligible`, `minor` or `significant`; all other rows are `only_in_A` or `only_in_B`.
- **3.3 Coverage Analysis** computes element coverage (shared / union of GlobalIds) and the coverage verdict: FAIL if any critical type is unmatched, REVIEW if other types are unmatched or coverage is below 95%, otherwise PASS.
- **3.4 BQI Scoring** scores every element on the four dimensions and combines them with the Config weights:
  - **D1** Property completeness
  - **D2** Property validity
  - **D3** QTO coverage
  - **D4** Cross-pipeline agreement: the share of comparison rows classified `exact` or `negligible`
- **3.5 SRCC Analysis** computes the Spearman rank correlation between the pipelines for each quantity field, as a separate diagnostic from D4.

The model BQI is the mean of the element BQIs. Full definitions: [`../../docs/bqi-definition.md`](../../docs/bqi-definition.md) and [`../../docs/validation-ruleset.md`](../../docs/validation-ruleset.md).

---

## Block 4 — Risk Screening

| Node | Computes |
|---|---|
| 4.1 Exposure | `E`, from the domain table, the category and `IsExternal` |
| 4.2 Likelihood | `L = E × (S_base + m_mat)`, clamped to [0, 1] |
| 4.3 Consequence | `C = Crit_base × (0.7 + 0.3 × q̂)` |
| 4.4 Risk score | `R_raw = L × C`, `R_adj = R_raw × [1 + α(1 − BQI)]`, `R_lower = R_raw × [1 − α(1 − BQI)]`, band width |
| 4.5 Rank & label | Ranking on `R_adj` and High / Medium / Low labels from the model's percentiles with floors of 0.40 and 0.15 |

The lookup tables are selected by the detected domain. Full rules: [`../../docs/risk-rules-table.md`](../../docs/risk-rules-table.md).

---

## Block 5 — Output Generation

- **5.1 Generate HTML** builds the risk register: screening verdict with reasons, headline figures, recommended action, ranked elements with their bands, BQI evidence and the pipeline cross-check.
- **5.2–5.5** Write the report to `output_dir` as `risk-register-<model>-<timestamp>.html` and open it.
- **5.6–5.7** Build and write the per-element sensitivity JSON, `sensitivity-<model>.json`, used by the offline analysis scripts.

The screening verdict and the recommended action are fixed rules; there is no language-model node in the workflow.

---

## Single-File and Dual-File Operation

| Configuration | `project_file` | `project_file_b` | Used for |
|---|---|---|---|
| Single file | Baseline or faulted IFC | empty | Baselines, and all six faults |
| Dual file | Baseline IFC | Faulted IFC | F4 and F6 |

In a single-file run both pipelines read the same file. In a dual-file run Pipeline A reads the baseline and Pipeline B the faulted variant, so a disagreement fault becomes observable in D4 (F4) and in element coverage (F6). Dual-file exports carry the `_DUALFILE` suffix.

The workflow does not generate the faulted files; they come from [`../../scripts/fault_injection.py`](../../scripts/fault_injection.py) and are stored in [`../../sample-models/fault-injected/`](../../sample-models/fault-injected/).

---

## Running the Workflow

1. Install n8n, the DDC IFC Exporter (Windows) and IfcOpenShell 0.8.5.
2. In n8n, choose **Import from File** and select `n8n_ifc_dual_pipeline.json`.
3. In **0.1 Config**, set `path_to_converter`, `project_file`, `output_dir` and `script_dir`, and `project_file_b` for dual-file runs.
4. In **2.1 Download script**, edit the download folder, which contains a fixed path from the original workstation, so that it matches `script_dir`.
5. Execute the workflow. The report and the sensitivity JSON appear in `output_dir`.

---

## Relationship to the Scripts

Only `extract_ifc.py` runs inside the workflow. The BQI, risk and reporting logic runs in the workflow's Code nodes. The other scripts in [`../../scripts/`](../../scripts/) run outside it: `fault_injection.py` before a campaign, and `verify_exports.py`, `harvest_reports.ps1`, `fault_analysis.py`, `sensitivity_analysis.py` and `alpha_characterization.py` on its outputs.

---

## Reproducibility

- The thesis cites repository release `v1.0.2`; Annex III lists the SHA-256 of this workflow file and of the scripts. The workflow file is identical in `v1.0.1` and `v1.0.2`.
- Node 2.1 downloads `extract_ifc.py` from `main`, not from a tagged release. The script has not changed since 3 July 2026, before the experimental campaign. To reproduce the thesis exactly, place the release copy of `extract_ifc.py` in `script_dir` and skip the download, or point Node 2.1 at the release tag in your own copy. Editing the workflow changes its SHA-256, so keep the published file unchanged.
- Behaviours worth knowing when reading the outputs are listed in the docs:
  - D4 counts every bracketed field, including non-numeric properties ([`bqi-definition.md`](../../docs/bqi-definition.md), Section 12.6);
  - the quantity-extent term is zero for every corpus element ([`risk-rules-table.md`](../../docs/risk-rules-table.md), Section 4.1);
  - the two pipelines filter different element types, which drives the baseline coverage verdicts of the building models ([`validation-ruleset.md`](../../docs/validation-ruleset.md), Section 17.3).

---

## Provenance

- [DataDrivenConstruction CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN): Pipeline A converter and original workflows
- [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files): corpus source
- [Thesis repository](https://github.com/ulnirah/n8n-thesis)
