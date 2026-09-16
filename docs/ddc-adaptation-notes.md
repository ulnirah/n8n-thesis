# DDC Adaptation Notes

## Purpose

This document records how the external DataDrivenConstruction (DDC) tooling is used as the Pipeline A extraction path of the thesis workflow.

It keeps a clear boundary between:

1. the original DDC workflow artefacts, preserved in `workflows/ddc-base/`;
2. the DDC IFC Exporter, a closed binary used for IFC-to-tabular conversion; and
3. the orchestration, comparison, scoring and screening logic developed for this thesis.

The distinction matters for reproducibility and attribution. The thesis does not present DDC workflows as its own work, and does not claim ownership of the DDC IFC Exporter.

---

## 1. Role of DDC in the Thesis

The thesis screens risk from imperfect IFC data using two independent extraction paths:

- **Pipeline A** converts the IFC model to a table with the DDC IFC Exporter (version 17.1.1.0).
- **Pipeline B** reads the same model with IfcOpenShell (version 0.8.5) through `scripts/extract_ifc.py`.

The two outputs are matched on `GlobalId` and compared downstream. Their agreement is dimension D4 of the BIM Quality Index (BQI).

```text
                         IFC model
                            |
             +--------------+--------------+
             |                             |
             v                             v
        Pipeline A                    Pipeline B
    DDC IFC Exporter                 IfcOpenShell
      (IFC → XLSX)             (extract_ifc.py → JSON)
             |                             |
             +--------------+--------------+
                            |
                            v
          Merge by GlobalId, QTO comparison
                            |
                            v
                     BQI (D1–D4)
                            |
                            v
                  Risk screening, report
```

The DDC path provides one independent observation of the model. It is not the thesis methodology by itself.

---

## 2. Original DDC Artefacts

`workflows/ddc-base/` contains nine original workflow JSON files from the [DDC CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN), plus a README.

They are kept as upstream reference material, separately from the thesis workflow, so that it stays clear which material is DDC's and which was written for the thesis. They are not thesis workflows and are not run in the experiments.

---

## 3. The DDC IFC Exporter

### 3.1 Function

The exporter converts an IFC file into an XLSX file with one row per entity. It belongs to the extraction stage only. It does not determine:

- the BQI rules, weights or aggregation;
- the QTO comparison classes;
- the SRCC analysis;
- the risk proxies, uncertainty band or labels; or
- the verdict and report.

All of these are thesis logic running after the extraction boundary.

### 3.2 Closed component boundary

```text
IFC source
   |
   v
[DDC IFC Exporter]          external, closed binary, Windows
   |
   v
XLSX table
   |
   v
[thesis workflow]           parsing, filtering, comparison, scoring, screening
```

The exporter's internal behaviour cannot be inspected or rebuilt from this repository. The reproducibility claim therefore covers the logic after the extraction boundary, together with the configuration, versions and hashes needed to repeat the analysis.

---

## 4. Pipeline A in the Thesis Workflow

Block 1 of `workflows/thesis/n8n_ifc_dual_pipeline.json` wraps the exporter:

| Node | Step |
|---|---|
| 1.1 | Build the expected XLSX path: `<IFC file name>_ifc.xlsx` next to the input file |
| 1.2, 1.3 | Check whether that XLSX already exists; if so, skip conversion and reuse it (1.3a) |
| 1.3b | Otherwise run the DDC IFC Exporter |
| 1.4 | Check the conversion result; a failure stops the run (1.4b) rather than continuing with partial data |
| 1.5, 1.6 | Merge the two branches and set the XLSX path |
| 1.7, 1.8 | Read the XLSX and parse its rows |
| 1.9 | Filter out spatial rows such as `IfcProject`, `IfcSite`, `IfcBuilding` and `IfcBuildingStorey` |
| 1.10 | Tag every item as `A_ddc` |

### 4.1 Parsing and filtering

The XLSX rows are parsed into items keyed by `GlobalId`, with properties and quantities as bracketed fields such as `[Qto_WallBaseQuantities] NetVolume`. Spatial rows are removed so that only physical elements are compared. This filtering is part of the thesis workflow, not a modification of the exporter.

### 4.2 Pipeline tagging

Items from the two paths carry an explicit pipeline label, `A_ddc` or `B_ifcopenshell`, so every observation keeps its source through comparison and diagnostics.

### 4.3 Cross-pipeline matching and comparison

Node 3.1 merges the two pipelines, and Node 3.2 compares them element by element on `GlobalId`, after removing the set prefix from field names (so `[Qto_WallBaseQuantities] NetVolume` and `[BaseQuantities] NetVolume` are the same field). Rows are classified as `exact`, `negligible`, `minor`, `significant`, or, when a numeric value is not available in both pipelines, `only_in_A` / `only_in_B`.

D4 is the share of an element's comparison rows classified `exact` or `negligible`. Neither pipeline is treated as ground truth: the relative difference is measured against Pipeline A only as a reference for scale. The full definition, including which rows enter the denominator, is in [`bqi-definition.md`](bqi-definition.md), Section 4.4.

---

## 5. What Is Not from DDC

| Component | Origin |
|---|---|
| Dual-pipeline orchestration in n8n | Thesis |
| IfcOpenShell extraction (`extract_ifc.py`) | Thesis |
| D1–D4 definitions, rule tables, weights and aggregation | Thesis |
| QTO comparison classes and element coverage verdict | Thesis |
| SRCC analysis | Thesis |
| Fault injection, including the dual-file configuration | Thesis |
| Risk proxies, uncertainty band, ranking and labels | Thesis |
| Screening verdict and risk-register report | Thesis |
| Sensitivity analysis and α characterisation | Thesis |

The DDC contribution is limited to the conversion used by Pipeline A, and to the original workflows kept as reference.

---

## 6. Relationship to the IfcOpenShell Pipeline

The two paths are deliberately independent:

```text
Pipeline A:  IFC → DDC IFC Exporter → XLSX → parsed items
Pipeline B:  IFC → IfcOpenShell → extract_ifc.py → JSON items
```

The aim is not to show that one tool is right and the other wrong. Two independent readings of the same file make disagreement observable, which a single tool cannot do. Independence matters for D4 in particular: an error shared by both paths would appear as agreement.

---

## 7. Single-File and Dual-File Operation

### Single-file configuration

The same IFC file is given to both pipelines (`project_file` only):

```text
            IFC file (baseline or faulted)
                  /           \
                 v             v
            Pipeline A      Pipeline B
```

This is used for the baselines and for all six faults. For F1, F2, F3 and F5 it is the test configuration; for F4 and F6 it is the control, in which the fault is invisible by construction because both pipelines read the same changed values.

### Dual-file configuration

The baseline file goes to Pipeline A and the faulted variant to Pipeline B (`project_file` and `project_file_b`):

```text
      baseline IFC               faulted IFC
           |                          |
           v                          v
      Pipeline A                 Pipeline B
```

This is used for F4 and F6. The injected change now exists between the two inputs, so the disagreement becomes observable in D4 and in element coverage.

---

## 8. Interpreting DDC Output

The DDC output is one extraction path's view of the model. It is not:

- a complete representation of IFC semantics;
- a statement of model quality on its own;
- a ground-truth quantity source; or
- a measure of physical reliability.

Agreement between DDC and IfcOpenShell increases confidence in the extracted information, but does not prove both are correct. Disagreement shows that the two readings differ, not which one is wrong.

---

## 9. Reproducibility Boundary

```text
source IFC
    |
    +--> Pipeline A: DDC IFC Exporter 17.1.1.0         (external)
    |
    +--> Pipeline B: IfcOpenShell 0.8.5 + extract_ifc.py (thesis)
    |
    v
comparison → BQI → risk screening → register and sensitivity export   (thesis)
```

Under thesis control:

- the workflow configuration (node 0.1);
- the fault definitions, severities and seed, with one manifest generated per faulted file;
- Pipeline B extraction;
- the comparison, BQI and risk rules;
- the sensitivity and α analyses; and
- report generation.

The DDC IFC Exporter remains an external dependency at the Pipeline A boundary.

---

## 10. Repository Organisation

```text
workflows/
├── README.md
├── ddc-base/
│   ├── README.md
│   └── 9 original DDC workflow JSON files
└── thesis/
    ├── README.md
    └── n8n_ifc_dual_pipeline.json
```

`workflows/ddc-base/` preserves the upstream artefacts. `workflows/thesis/` holds the integrated workflow used for every experiment. The two are kept apart so that provenance stays visible.

---

## 11. Adaptation Principles

### 11.1 Preserve the upstream boundary

The exporter is used as supplied; its implementation is not rewritten or presented as thesis work.

### 11.2 Keep downstream logic deterministic

After extraction, comparison, BQI, risk and reporting are controlled by explicit rules and configuration, with no generative model in the scoring path.

### 11.3 Record provenance

The exporter version, the workflow configuration and the SHA-256 hashes of the inputs and artefacts are recorded (thesis Annex III).

### 11.4 Avoid ground-truth assumptions

DDC output is one independent observation, not a reference dataset.

---

## 12. Limitations

### 12.1 External, closed dependency

The exporter's internal implementation is outside this repository, and results depend on the exporter version used (17.1.1.0).

### 12.2 Windows only

The exporter is a Windows executable, so Pipeline A, and therefore the full workflow, runs on Windows. Porting is left to future work.

### 12.3 Extraction-specific behaviour

Differences between the pipelines can come from legitimate differences in schema interpretation, property and quantity handling, number formatting, or filtering. A disagreement is an observable extraction discrepancy, not automatically an error.

### 12.4 No independent QTO ground truth

The comparison establishes agreement between two extraction paths, not correctness against measured quantities.

### 12.5 Conversion cache

Pipeline A reuses an existing XLSX with the expected name instead of converting again (nodes 1.2–1.3). This speeds up repeated runs; it is why dual-file runs, where Pipeline A reads the already-converted baseline, are faster (thesis Section 4.7). Because the cache is matched by file name (`<IFC file name>_ifc.xlsx`), a stale XLSX left from an earlier run would be read instead of converting the current file. `scripts/fault_analysis.py` warns if an F4 single-file run shows any BQI change, which would indicate this; the fix is to delete the stale XLSX files and re-run.

### 12.6 Scope of supported rules

The BQI rules cover the property and quantity sets defined in the rule tables (twelve building entities). They are not a universal validator for every IFC entity or infrastructure domain.

---

## 13. Practical Reproduction Notes

1. Use the corpus and fault variants in `sample-models/`.
2. Install the DDC IFC Exporter 17.1.1.0 on a Windows machine.
3. Import `workflows/thesis/n8n_ifc_dual_pipeline.json` into n8n 2.7.5.
4. Install IfcOpenShell 0.8.5 for Pipeline B.
5. In node **0.1 Config**, set `path_to_converter`, `project_file`, `project_file_b` (dual-file runs only), `output_dir` and `script_dir`.
6. Clear old XLSX conversions of faulted files before a campaign (Section 12.5).
7. Use the configuration that matches each experiment: single-file for baselines and all faults, dual-file for F4 and F6.
8. Record the repository release, the Config values and the input-file hashes for provenance.

---

## 14. Related Documents

Scoring definitions:

- [`bqi-definition.md`](bqi-definition.md)
- [`validation-ruleset.md`](validation-ruleset.md)
- [`risk-rules-table.md`](risk-rules-table.md)

Corpus and fault construction:

- [`../sample-models/README.md`](../sample-models/README.md)
- [`../sample-models/fault-injected/README.md`](../sample-models/fault-injected/README.md)

Integrated workflow:

- [`../workflows/thesis/README.md`](../workflows/thesis/README.md)

Thesis references: Section 3.2 (dual-pipeline architecture), Section 3.5.3 (dual-file design), Section 3.7 (n8n implementation), Annex III (provenance).

---

## 15. Provenance Statement

```text
UPSTREAM / EXTERNAL
    DDC IFC Exporter (Pipeline A conversion)
    Original DDC workflows (reference only, workflows/ddc-base/)
          |
          v
THESIS
    orchestration and configuration
    IfcOpenShell extraction
    parsing, filtering and matching
    QTO comparison and element coverage
    BQI
    risk screening and reporting
    fault injection and sensitivity analysis
```

The goal is not to remove the external dependency, but to make its location, function and limits explicit. This document describes repository release `v1.0.2`.
