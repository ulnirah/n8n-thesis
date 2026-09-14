# Scripts

This directory contains the Python and PowerShell scripts supporting the computational experiments in the thesis.

The scripts provide functionality that is externalised from the n8n workflow, including IFC extraction, fault injection, fault-response analysis, parameter sensitivity analysis, uncertainty-coefficient characterisation, output verification, and report aggregation.

The scripts are version-controlled together with the thesis workflow so that the computational logic used in the reported experiments is inspectable and reproducible.

---

## Script Inventory

| Script | Purpose |
|---|---|
| `extract_ifc.py` | Independent Pipeline B IFC extraction using IfcOpenShell |
| `fault_injection.py` | Generates controlled fault-injected IFC variants |
| `fault_analysis.py` | Analyses BQI responses to injected faults |
| `sensitivity_analysis.py` | Evaluates parameter sensitivity and ranking stability |
| `alpha_characterization.py` | Characterises the uncertainty coefficient α |
| `verify_exports.py` | Verifies the structural integrity of sensitivity JSON exports |
| `verify_exports.ps1` | PowerShell wrapper for export verification |
| `harvest_reports.ps1` | Aggregates information from generated risk-register reports |

---

## IFC Extraction

### `extract_ifc.py`

This script implements the independent IFC extraction pathway used as **Pipeline B** in the thesis workflow.

It uses IfcOpenShell to extract structured information from IFC files, including:

- IFC schema metadata;
- IFC elements;
- element properties;
- quantities;
- materials; and
- spatial hierarchy information.

The extracted data are returned as JSON and consumed by the n8n workflow for schema detection, domain detection, QTO comparison, BQI scoring, and risk screening.

The script is retrieved by the n8n workflow at run time and is therefore treated as a version-controlled thesis artefact.

---

## Fault Injection

### `fault_injection.py`

Generates controlled IFC fault variants from the baseline corpus.

The fault-injection framework implements the six fault classes used in the thesis:

```text
F1
F2
F3
F4
F5
F6
```

The generated variants are parameterised according to the experimental design, including the fault severity/injection level and random seed where applicable.

The resulting IFC files are stored under:

```text
sample-models/fault-injected/
```

---

## Fault Analysis

### `fault_analysis.py`

Processes the results of the fault-injection experiments.

The analysis supports the evaluation of:

- fault detection;
- BQI monotonicity;
- selectivity;
- inter-dimensional coupling; and
- fault-specific response patterns.

The outputs support the fault-injection results reported in the thesis.

---

## Sensitivity Analysis

### `sensitivity_analysis.py`

Performs the offline sensitivity analysis used to evaluate how the screening results respond to changes in selected framework parameters.

The analysis includes ranking-stability assessment using rank correlation metrics and supports the parameter-sensitivity results reported in the thesis.

---

## α Characterisation

### `alpha_characterization.py`

Characterises the uncertainty coefficient **α** used in the uncertainty-aware risk propagation step.

The script evaluates the defined α range and supports the characterisation reported in the thesis.

---

## Output Verification

### `verify_exports.py`

Performs structural verification of the generated sensitivity JSON exports.

The checks include:

- valid JSON structure;
- required element fields;
- unique `GlobalId` values;
- expected element counts;
- F6 element-reduction behaviour; and
- recomputation of model-level BQI values.

The verification script does not modify the source sensitivity files.

### `verify_exports.ps1`

PowerShell wrapper used to run the export-verification process in the Windows environment used for the experiments.

---

## Report Aggregation

### `harvest_reports.ps1`

Harvests information from the generated HTML risk-register reports and aggregates the extracted information into a summary dataset for downstream analysis.

---

## Dependencies

The Python scripts use the following main packages:

```text
ifcopenshell
pandas
scipy
openpyxl
```

Typical installation:

```bash
pip install ifcopenshell pandas scipy openpyxl
```

### Package roles

- **ifcopenshell** – IFC reading, extraction, and manipulation
- **pandas** – tabular data processing and export
- **scipy** – statistical analysis, including Spearman rank correlation
- **openpyxl** – Excel/XLSX handling where required

The exact dependency requirements may differ between scripts. Refer to the script source and execution environment when reproducing a specific analysis.

---

## General Usage

Scripts are intended to be executed from the repository root or with paths adjusted to the local environment.

### IFC extraction

Example:

```bash
python scripts/extract_ifc.py \
  sample-models/baseline/IFC4-Building-Structural.ifc \
  --include-properties \
  --include-materials
```

### Fault injection

The exact command-line arguments depend on the experiment configuration and are defined in the script and thesis methodology.

The generated fault-injected models are stored under:

```text
sample-models/fault-injected/
```

### Verification

Example:

```bash
python scripts/verify_exports.py <campaign-root>
```

For the Windows PowerShell workflow:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_exports.ps1
```

### Report harvesting

The report-harvesting script is intended to be run over the directory containing the generated experimental reports.

---

## Relationship to the n8n Workflow

The scripts in this directory are not a replacement for the n8n workflow.

The workflow provides the end-to-end orchestration, while the scripts provide externalised computational components and offline analysis utilities.

The main relationship is:

```text
IFC inputs
    |
    v
n8n workflow
    |
    +--> extract_ifc.py
    |
    +--> BQI / risk processing
    |
    +--> HTML risk register
    |
    +--> sensitivity JSON
              |
              +--> fault_analysis.py
              +--> sensitivity_analysis.py
              +--> alpha_characterization.py
              +--> verify_exports.py
              +--> harvest_reports.ps1
```

---

## Reproducibility and Provenance

The scripts are version-controlled as part of the thesis repository.

The final thesis release identifies the exact repository state using:

- the Git release tag;
- the associated commit SHA; and
- SHA-256 hashes of the principal software artefacts.

The script versions used for the reported experiments should therefore be taken from the frozen thesis release rather than from a later development state.
