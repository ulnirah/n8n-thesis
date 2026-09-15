# Thesis Workflow

This folder contains the **thesis-specific n8n workflow** used to orchestrate the complete computational pipeline:

**IFC input → dual extraction → QTO comparison → BQI → risk screening → sensitivity export → explainable risk register**

The workflow integrates external DDC conversion infrastructure with original thesis-specific processing and analysis logic.

---

## Workflow

| File | Role | Provenance |
|---|---|---|
| `n8n_ifc_dual_pipeline.json` | Complete thesis workflow from IFC input to final risk-screening and reporting outputs | Thesis-specific integrated workflow incorporating DDC Pipeline A and IfcOpenShell Pipeline B |

This is the **main reproducibility workflow** for the thesis.

It should be treated as the canonical workflow for the computational experiments reported in the thesis.

---

## Architecture

The workflow is organised into six logical blocks.

### Block 0 — Configuration

The configuration node centralises the parameters required for a run, including:

- DDC converter path;
- primary IFC input;
- optional second IFC input for dual-file experiments;
- output directory;
- BQI dimension weights;
- coverage threshold; and
- uncertainty coefficient `α`.

The BQI weights used by the reported configuration are:

| Dimension | Weight |
|---|---:|
| D1 — Completeness | 0.35 |
| D2 — Validity | 0.25 |
| D3 — QTO Coverage | 0.20 |
| D4 — QTO Agreement | 0.20 |

The default uncertainty coefficient is:

`α = 0.55`

The default element-coverage threshold is:

`95%`

---

## Block 1 — Pipeline A: DDC Extraction

Pipeline A uses the DDC IFC conversion infrastructure.

The workflow:

1. receives the IFC input;
2. builds the expected XLSX output path;
3. checks whether a converted XLSX already exists;
4. runs `IfcExporter.exe` when conversion is required;
5. reads the resulting XLSX file;
6. parses the tabular records;
7. filters out spatial entities; and
8. tags the resulting records as:

`A_ddc`

Pipeline A therefore provides the DDC-based tabular extraction pathway.

The DDC components used here are external infrastructure and are preserved separately under [`../ddc-base/`](../ddc-base/).

---

## Block 2 — Pipeline B: IfcOpenShell Extraction

Pipeline B provides an independent extraction pathway using **IfcOpenShell** and the thesis-controlled:

`scripts/extract_ifc.py`

The workflow:

1. retrieves the extraction script;
2. verifies the Python / IfcOpenShell environment;
3. runs the extraction;
4. parses the returned JSON;
5. detects the IFC schema and domain;
6. filters the analysis elements; and
7. tags the resulting records as:

`B_ifcopenshell`

Pipeline B extracts structured information including:

- elements;
- properties;
- quantities;
- materials;
- spatial information; and
- IFC metadata.

The two independent pipelines are required for the thesis treatment of cross-pipeline agreement.

---

## Block 3 — QTO Comparison and BQI

Block 3 contains the core thesis-specific information-quality analysis.

### QTO comparison

Pipeline A and Pipeline B are merged using IFC `GlobalId`.

Shared quantity fields are compared across the two extraction pathways.

The workflow records:

- matching elements;
- elements present in only one pipeline;
- quantity values from each pipeline;
- absolute differences;
- percentage differences; and
- quantity-field agreement classifications.

### Element coverage

Element presence is analysed separately from quantity-field coverage.

Missing elements are classified according to their severity for the downstream screening process.

### BQI scoring

Each scored element receives four quality dimensions:

- **D1 — Property completeness**
- **D2 — Property validity**
- **D3 — QTO coverage**
- **D4 — Cross-pipeline QTO agreement**

The element-level BQI is calculated as the weighted combination of these dimensions.

The model-level BQI is then obtained from the scored elements.

### SRCC analysis

The workflow calculates Spearman rank correlation coefficients for comparable quantity fields.

SRCC is used as the cross-pipeline rank-stability measure rather than as a replacement for the D4 dimension itself.

Element coverage and SRCC are therefore retained as distinct diagnostics.

---

## Block 4 — Risk Screening

Block 4 converts the information-quality results into an uncertainty-aware risk-screening result.

The workflow derives:

1. exposure;
2. likelihood;
3. consequence;
4. raw risk;
5. BQI-dependent uncertainty widening;
6. adjusted risk; and
7. risk ranking.

The raw risk is:

`R_raw = Likelihood × Consequence`

The uncertainty widening is controlled by:

`α(1 − BQI)`

The adjusted upper value used for ranking is:

`R_adj = R_raw × [1 + α(1 − BQI)]`

The workflow also retains:

- `R_lower`;
- `R_raw`;
- `R_adj`;
- uncertainty-band width; and
- the BQI used in the calculation.

This allows the final register to show both the underlying risk proxy and the effect of information uncertainty.

---

## Block 5 — Ranking and Output Generation

The final block ranks and labels the screened elements and generates the reporting artefacts.

Outputs include:

- HTML risk register;
- per-element sensitivity JSON; and
- diagnostic summaries for pipeline, BQI, coverage, SRCC, and risk results.

The HTML report contains:

- overall screening verdict;
- model BQI;
- element coverage;
- high / medium / low risk counts;
- BQI dimension evidence;
- pipeline comparison;
- SRCC results;
- element coverage diagnostics;
- ranked risk elements; and
- uncertainty-band information.

The sensitivity JSON contains the per-element variables required by the offline analysis scripts.

---

## Single-File and Dual-File Operation

The workflow supports two experimental configurations.

### Single-file configuration

Both extraction pipelines receive the same IFC input.

This is the default configuration for the baseline workflow and for faults whose effect is intended to be observed directly within the shared source file.

### Dual-file configuration

A second IFC path can be supplied through:

`project_file_b`

Pipeline A continues to use `project_file`, while Pipeline B uses `project_file_b`.

This configuration is required for the experimental treatment of faults whose purpose is to create disagreement between the two data consumers.

In particular, the thesis uses the dual-file configuration for the F4 and F6 experiments.

---

## Fault-Injection Compatibility

The workflow does not itself generate the faulted IFC models.

Fault variants are generated externally using:

`scripts/fault_injection.py`

The resulting faulted model can then be supplied to the workflow as the relevant input.

For dual-file experiments, the faulted variant can be assigned specifically to Pipeline B while Pipeline A retains the corresponding baseline model.

---

## External and Original Components

The integrated workflow combines external DDC infrastructure with thesis-specific computational logic.

### External / adapted component

**DDC IFC conversion pathway**

The DDC `IfcExporter` is used to produce the tabular representation consumed by Pipeline A.

### Thesis-specific components

The integrated workflow implements:

- dual-pipeline orchestration;
- IFC schema and domain detection;
- GlobalId-based pipeline matching;
- QTO comparison;
- element coverage analysis;
- BQI scoring;
- SRCC analysis;
- uncertainty-aware risk screening;
- risk ranking;
- sensitivity export;
- deterministic reporting; and
- diagnostic outputs.

The DDC base workflows are preserved separately under:

[`../ddc-base/`](../ddc-base/)

---

## Relationship to Repository Scripts

The workflow relies on several version-controlled scripts stored under [`../../scripts/`](../../scripts/).

The most important runtime dependency is:

`scripts/extract_ifc.py`

Additional analysis scripts operate on the exported sensitivity and experiment data, including:

- `fault_injection.py`
- `fault_analysis.py`
- `sensitivity_analysis.py`
- `alpha_characterization.py`
- `verify_exports.py`

The workflow therefore provides the orchestration layer, while the scripts provide externalised and independently auditable computational logic.

---

## Reproducibility

The workflow is designed so that the computational chain can be reproduced from:

1. the baseline IFC corpus;
2. any required fault-injected IFC variants;
3. the version-controlled thesis workflow;
4. the version-controlled analysis scripts; and
5. the documented configuration parameters.

For the final thesis release, the workflow and its runtime script references should point to the **frozen repository release or exact commit**, rather than an unfrozen development branch.

This is particularly important for the runtime retrieval of `extract_ifc.py`.

---

## Provenance

The workflow references the following external and repository resources:

- [DataDrivenConstruction CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN)
- [buildingSMART Sample Test Files](https://github.com/buildingSMART/Sample-Test-Files)
- [Thesis repository](https://github.com/ulnirah/n8n-thesis)

The complete workflow export is retained in this folder so that the orchestration logic used for the thesis remains inspectable and version controlled.
