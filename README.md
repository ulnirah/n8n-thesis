# Uncertainty-Aware Risk Screening from Imperfect Building Information Models

**Thesis repository for the NORISK Erasmus Mundus Joint Master**

**Author:** Aulia Annisa Rahmatillah  
**Programme:** International Master's in Risk Assessment and Management of Civil Infrastructures (NORISK)  
**Institution:** Universitat Politècnica de Catalunya (UPC), Barcelona, Spain  
**Supervisor:** Seyedmilad Komarizadehasl  
**Co-supervisor:** Mahyad Komary  

---

## Overview

This repository contains the computational artefacts developed for the MSc thesis:

> **Uncertainty-Aware Risk Screening from Imperfect Building Information Models: Schema Validation, Quantity Take-Off Robustness, and Explainable Risk Registers in an n8n Workflow**

The thesis investigates how imperfect IFC/BIM information affects automated infrastructure risk screening and develops a reproducible workflow for measuring BIM information quality, propagating that uncertainty into risk screening, and producing auditable risk registers.

The framework introduces the **BIM Quality Index (BQI)**, a continuous weighted quality metric with four dimensions:

1. Property completeness
2. Property validity
3. Quantity take-off (QTO) coverage
4. Cross-pipeline agreement

The BQI is calculated from two independent IFC extraction pipelines and propagated into an uncertainty-aware risk band. Controlled fault injection is used to evaluate how the BQI responds to known BIM information defects and how those changes affect downstream risk screening.

The complete extraction, validation, scoring, screening, and reporting chain is orchestrated in **n8n**. Supporting extraction, fault-injection, verification, and analysis logic is implemented in version-controlled scripts, while the methodological rules and parameter definitions are documented in the repository.

The repository is intended to accompany the thesis and provide the implementation, input, documentation, and representative output artefacts underlying the reported results.

---

## Contributions and Provenance

The repository combines external infrastructure from the DataDrivenConstruction (DDC) CAD-to-data toolkit with computational components developed for this thesis.

### Main thesis contributions

| Contribution | Description |
|---|---|
| **BIM Quality Index (BQI)** | Continuous weighted evaluation of BIM information quality at element and model level |
| **Cross-pipeline QTO robustness** | Comparison of quantities extracted independently by DDC and IfcOpenShell using `GlobalId` matching and Spearman rank correlation |
| **Uncertainty-aware risk screening** | Propagation of BIM information quality into a risk band containing lower, raw, and conservative adjusted risk values |
| **Fault-injection measurement analysis** | Controlled evaluation of BQI response to six IFC fault types across three severity levels |
| **Explainable risk register** | Auditable risk-screening output linking element-level risk results to BIM information quality |
| **Sensitivity analysis** | Evaluation of parameter sensitivity and ranking stability |

### External and adapted components

| Component | Source | Role in the thesis |
|---|---|---|
| IFC → XLSX conversion | DDC `IfcExporter` | Pipeline A IFC-to-tabular conversion |
| Original DDC workflows | DDC workflow collection | Preserved as reference artefacts and methodological provenance |
| IfcOpenShell extraction | Thesis-controlled script | Independent Pipeline B extraction pathway |
| BQI, risk, fault injection, analysis and reporting | This thesis repository | Original thesis-specific computational logic |

The original DDC workflow collection is retained separately under:

```text
workflows/ddc-reference/
```

The DDC IFC Exporter is used as the extraction component for Pipeline A. The thesis-specific BQI, comparison, fault-injection, risk-screening, sensitivity, verification, and reporting logic is implemented in the thesis workflow and supporting scripts.

Detailed adaptation notes are provided in:

```text
docs/ddc-adaptation-notes.md
```

---

## Workflow Architecture

The thesis implements a modular dual-pipeline architecture in n8n.

```text
                         IFC input
                            |
              +-------------+-------------+
              |                           |
              v                           v
       Pipeline A                   Pipeline B
     DDC / IFC → XLSX            IfcOpenShell / JSON
              |                           |
              +-------------+-------------+
                            |
                     GlobalId matching
                            |
                            v
                    QTO comparison
                            |
                            v
                       BQI scoring
                            |
                            v
                    Risk screening
                            |
                            v
                 Uncertainty propagation
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          HTML risk register    Sensitivity JSON
```

### Pipeline A: DDC extraction

Pipeline A uses the DDC IFC Exporter to convert IFC input into structured tabular data.

The exporter is treated as an external extraction component. The thesis does not claim ownership of its internal implementation.

### Pipeline B: IfcOpenShell extraction

Pipeline B uses the thesis-controlled `extract_ifc.py` script to independently extract IFC elements, properties, quantities, materials, schema metadata, and spatial information.

Pipeline B provides the second extraction path used for cross-pipeline comparison.

### QTO comparison and BQI

The two extraction streams are merged using IFC `GlobalId`.

The workflow then:

- identifies matched and unmatched elements;
- compares shared quantity fields;
- evaluates element coverage;
- calculates the four BQI dimensions; and
- computes the cross-pipeline agreement metrics.

### Risk screening

The workflow derives exposure, likelihood, and consequence proxies from IFC information, calculates the raw risk score, and propagates BIM information uncertainty through the BQI.

The resulting risk band contains:

- a lower bound;
- the raw risk score; and
- a conservative adjusted upper bound.

The adjusted upper bound is used for screening and ranking.

### Output generation

The workflow generates the HTML risk register and a per-element sensitivity dataset in JSON form. Diagnostic outputs may also be produced at block boundaries for traceability.

The thesis workflow export is stored in:

```text
workflows/thesis/
```

---

## Corpus and Experimental Design

### IFC corpus

The study uses eight openly available IFC sample models from buildingSMART repositories.

Seven models satisfy the inclusion criteria for the principal experiments. The eighth model is retained as a negative control.

The corpus covers four design domains across IFC 4 and IFC 4.3:

- building architecture;
- building structural;
- bridge; and
- road.

The baseline files are stored in:

```text
sample-models/baseline/
```

The corpus is documented in:

```text
sample-models/README.md
```

### Fault injection

The robustness evaluation uses six controlled IFC fault classes:

```text
F1
F2
F3
F4
F5
F6
```

Each fault is evaluated at three severity levels according to the experimental design defined in the thesis.

The fault-injection implementation generates reproducible variants from the baseline models and stores them in:

```text
sample-models/fault-injected/
```

Fault definitions, mutation logic, and provenance are documented in the corresponding sample-model and script READMEs.

### Experimental configurations

The experiments are organised into four principal configurations:

| Configuration | Purpose |
|---|---|
| **Baseline** | Establishes behaviour on the unmodified reference models |
| **Single File (F1, F2, F3, F5)** | Applies the fault to a single IFC input consumed by both extraction pipelines |
| **Single File (F4, F6)** | Evaluates F4 and F6 under the shared-input configuration |
| **Dual File (F4, F6)** | Assigns the perturbed input selectively to one pipeline to expose cross-pipeline disagreement |

The dual-file configuration is required for faults whose effect depends on disagreement between independent data consumers. When both pipelines read the same perturbed source, they can experience the same change and therefore cannot necessarily expose that disagreement.

The complete experimental output set is generated during reproduction and is not committed wholesale to the repository. Representative baseline outputs are provided under:

```text
examples/
```

---

## Representative Outputs

The repository includes representative output artefacts to illustrate the format and content of the thesis workflow results.

### HTML risk register

```text
examples/risk-register-baseline.html
```

contains a representative explainable risk-screening report with element-level screening information and supporting evidence.

### Sensitivity JSON

```text
examples/sensitivity-baseline.json
```

contains a representative per-element sensitivity dataset used by the downstream robustness and sensitivity analysis.

The complete set of experimental outputs used to produce the thesis results is reproducible from the documented corpus, configurations, workflow, scripts, and release provenance.

---

## Repository Structure

```text
n8n-thesis/
│
├── README.md
│
├── sample-models/
│   ├── README.md
│   ├── baseline/
│   └── fault-injected/
│
├── workflows/
│   ├── README.md
│   ├── ddc-reference/
│   └── thesis/
│       ├── README.md
│       └── n8n_ifc_dual_pipeline_v16.json
│
├── scripts/
│   ├── README.md
│   ├── extract_ifc.py
│   ├── fault_injection.py
│   ├── fault_analysis.py
│   ├── sensitivity_analysis.py
│   ├── alpha_characterization.py
│   ├── verify_exports.py
│   ├── verify_exports.ps1
│   └── harvest_reports.ps1
│
├── docs/
│   ├── README.md
│   ├── bqi-definition.md
│   ├── risk-rules-table.md
│   ├── validation-ruleset.md
│   └── ddc-adaptation-notes.md
│
└── examples/
│   ├── README.md
│   ├── risk-register-IFC4-Building-Architecture-2026-07-31-00-53.html
│   ├── risk-register-IFC4-Building-Structural-2026-07-31-00-53.html
│   ├── ...
│   ├── risk-register-IFC43-Infra-Road-2026-07-31-00-55.html
│   ├── sensitivity-IFC4-Building-Architecture.json
│   ├── sensitivity-IFC4-Building-Structural.json
│   ├── ...
│   └── sensitivity-IFC43-Infra-Road.json
```

---

## Software Artefacts

The principal thesis software artefacts are:

| Artefact | Path |
|---|---|
| n8n workflow export | `workflows/thesis/n8n_ifc_dual_pipeline_v16.json` |
| Pipeline B extraction | `scripts/extract_ifc.py` |
| Fault injection | `scripts/fault_injection.py` |
| Fault analysis | `scripts/fault_analysis.py` |
| Sensitivity analysis | `scripts/sensitivity_analysis.py` |
| α characterisation | `scripts/alpha_characterization.py` |
| Export verification | `scripts/verify_exports.py` |
| Export verification wrapper | `scripts/verify_exports.ps1` |
| Report aggregation | `scripts/harvest_reports.ps1` |

The original DDC workflow collection is separately preserved under:

```text
workflows/ddc-reference/
```

The SHA-256 values of the principal artefacts used for thesis deposit are recorded in the thesis provenance table.

---

## Tools and Technologies

| Tool / Technology | Role |
|---|---|
| **n8n** | Workflow automation and orchestration |
| **DDC CAD-to-data toolkit** | Pipeline A IFC conversion and reference workflow infrastructure |
| **IfcOpenShell** | Independent Pipeline B IFC extraction |
| **Python** | IFC extraction, fault injection, fault analysis, sensitivity analysis, and verification |
| **JavaScript** | n8n Code-node processing |
| **PowerShell** | Windows-side verification and report harvesting |
| **Git / GitHub** | Version control and reproducibility |

---

## Verification and Reproducibility

The repository includes utilities for verifying generated outputs and supporting reproducibility.

### `verify_exports.py`

Performs structural checks on the sensitivity JSON exports, including:

- JSON validity;
- required fields;
- `GlobalId` uniqueness;
- expected element counts;
- F6 element-removal behaviour; and
- recomputed model-level BQI values.

### `verify_exports.ps1`

Provides a Windows PowerShell wrapper for the export-verification procedure.

### `harvest_reports.ps1`

Collects information from generated reports and produces a summary dataset for downstream analysis.

---

## Versioning and Thesis Release

The final computational package is released under the Git tag:

```text
v1.0-thesis
```

The thesis records the exact 40-character commit SHA associated with this tag.

The principal software artefacts are additionally identified by SHA-256 hashes.

The intended provenance chain is:

```text
Repository
    |
    v
v1.0-thesis
    |
    v
Git commit SHA
    |
    +---- workflow
    +---- scripts
    +---- IFC inputs
    +---- documentation
    |
    v
SHA-256 verification
```

The `v1.0-thesis` tag should be treated as the frozen computational reference corresponding to the thesis deposit.

---

## Reproduction Overview

A reproduction of the computational study follows the general sequence:

```text
1. Obtain the repository at the thesis release tag
                         ↓
2. Obtain the documented IFC corpus
                         ↓
3. Prepare the required fault-injected variants
                         ↓
4. Configure the thesis n8n workflow
                         ↓
5. Run the required experimental configurations
                         ↓
6. Generate risk registers and sensitivity JSON
                         ↓
7. Verify the sensitivity exports
                         ↓
8. Aggregate report-level results
                         ↓
9. Perform the offline robustness and sensitivity analyses
```

Environment-specific requirements and configuration details are documented in the corresponding workflow, script, and documentation READMEs.

---

## External Resources

| Resource | Description | Link |
|---|---|---|
| DataDrivenConstruction CAD-to-data toolkit | IFC conversion and related workflow infrastructure | [GitHub repository](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN) |
| buildingSMART Sample Test Files | IFC sample models used for the corpus | [GitHub repository](https://github.com/buildingSMART/Sample-Test-Files) |
| buildingSMART Community Sample Files | Additional IFC sample models | [GitHub repository](https://github.com/buildingsmart-community/Community-Sample-Test-Files) |

---

## Thesis Mapping

| Thesis component | Repository location |
|---|---|
| IFC corpus and provenance | `sample-models/` |
| Dual-pipeline extraction architecture | `workflows/thesis/` |
| BQI definition and rules | `docs/bqi-definition.md` |
| Risk-screening rules | `docs/risk-rules-table.md` |
| IFC validation rules | `docs/validation-ruleset.md` |
| DDC adaptations | `docs/ddc-adaptation-notes.md` |
| Fault injection | `scripts/fault_injection.py` |
| Fault analysis | `scripts/fault_analysis.py` |
| α characterisation | `scripts/alpha_characterization.py` |
| Sensitivity analysis | `scripts/sensitivity_analysis.py` |
| Output verification | `scripts/verify_exports.py` |
| Report aggregation | `scripts/harvest_reports.ps1` |
| Representative outputs | `examples/` |

---

## Citation

When using this repository in academic work, please cite the associated MSc thesis:

> Rahmatillah, A. A. (2026). *Uncertainty-Aware Risk Screening from Imperfect Building Information Models: Schema Validation, Quantity Take-Off Robustness, and Explainable Risk Registers in an n8n Workflow*. Universitat Politècnica de Catalunya.

---

## Scope and Limitations

This repository supports the computational experiments reported in the thesis.

The study is limited to the IFC versions, corpus, fault taxonomy, parameter ranges, and experimental configurations defined in the thesis. The principal corpus consists of openly available buildingSMART sample models rather than proprietary project models.

The DDC IFC Exporter is an external component of Pipeline A, while the downstream comparison, BQI, risk-screening, analysis, and reporting logic is defined within the thesis workflow and supporting repository artefacts.

The repository should therefore be considered a reproducible research artefact supporting the thesis rather than a general-purpose commercial BIM validation or infrastructure risk-management system.

For the full methodological scope, assumptions, threats to validity, limitations, and conclusions, refer to the MSc thesis.
