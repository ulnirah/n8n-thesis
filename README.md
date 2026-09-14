# Uncertainty-Aware Risk Screening from Imperfect Building Information Models

**Thesis repository for the NORISK Erasmus Mundus Joint Master**

**Author:** Aulia Annisa Rahmatillah      
**Programme:** The International Masters in Risk Assessment and Management of Civil Infrastructures – NORISK        
**University:** Technical University of Catalonia (UPC), Barcelona, Spain      
**Supervisor:** Seyedmilad Komarizadehasl      
**Co-supervisor:** Mahyad Komary      

---

## Overview

This repository contains the computational artefacts developed for the MSc thesis:

> **Uncertainty-Aware Risk Screening from Imperfect Building Information Models: Schema Validation, Quantity Take-Off Robustness, and Explainable Risk Registers in an n8n Workflow**

The thesis investigates how imperfect IFC/BIM information affects automated infrastructure risk screening and develops a reproducible workflow for evaluating and communicating that uncertainty.

The proposed framework introduces the **BIM Quality Index (BQI)**, a continuous and weighted quality metric based on four dimensions:

1. Property completeness
2. Property validity
3. Quantity take-off (QTO) coverage
4. Cross-pipeline agreement

The BQI is calculated from two independent IFC extraction pipelines and propagated into an uncertainty-aware risk band. Controlled fault injection is then used to evaluate the response of the BQI and downstream risk screening to known BIM information defects.

The complete extraction, validation, scoring, screening, and reporting chain is orchestrated in **n8n**. Scoring and analysis logic are externalised into version-controlled scripts and rule tables to support deterministic execution, auditability, and reproducibility.

---

## Main Contributions

The repository implements the main computational contributions of the thesis:

### BIM Quality Index (BQI)

A continuous, weighted, and schema-aware metric that evaluates BIM information quality at element and model level.

The four BQI dimensions are:

| Dimension | Description |
|---|---|
| D1 – Completeness | Presence of required BIM property information |
| D2 – Validity | Validity of available property values |
| D3 – QTO Coverage | Availability of required quantity information |
| D4 – QTO Agreement | Agreement between independent extraction pipelines |

### Cross-pipeline QTO robustness

Two independent extraction pathways are compared:

- **Pipeline A:** DDC-based IFC-to-XLSX extraction
- **Pipeline B:** IfcOpenShell-based IFC extraction

Elements are matched using IFC `GlobalId`. Quantity fields are compared across the two pipelines, and Spearman rank correlation is used as a ground-truth-free agreement metric.

### Uncertainty-aware risk screening

Likelihood, exposure, and consequence proxies are derived from IFC information and combined into a raw risk score.

The BQI is then used to widen the risk result into an uncertainty band consisting of:

- lower risk bound;
- raw risk score; and
- conservative adjusted risk bound.

The adjusted upper bound is used for screening and ranking.

### Fault injection and measurement analysis

Controlled IFC faults are introduced to evaluate the behaviour of the BQI as a measurement instrument.

The experimental design covers:

- six fault types;
- three severity levels;
- baseline runs;
- single-file configurations; and
- dual-file configurations for faults where cross-pipeline disagreement must be isolated.

---

## Experimental Corpus

The study uses eight openly available IFC sample models from buildingSMART repositories.

Seven models satisfy the inclusion criteria for the main experiments. The eighth model is retained as a negative control.

The corpus covers four design domains across IFC 4 and IFC 4.3:

- building architecture;
- building structural;
- bridge; and
- road.

The baseline models are stored in:

```text
sample-models/baseline/
```

Fault-injected variants are stored in:

```text
sample-models/fault-injected/
```

Detailed corpus provenance and model-level information are documented in:

```text
sample-models/README.md
```



---

## What is Original vs. What is Adapted

This thesis builds on the DDC toolkit as infrastructure. The table below clarifies the boundary between what is given and what is the original contribution of this work.

| Component | Source | Description |
|-----------|--------|-------------|
| IFC → XLSX conversion | DDC (`IfcExporter.exe`) | Converts IFC files to structured Excel data |
| Basic IFC validation | DDC (`n8n_4`) | Schema compliance, property fill rates |
| QTO extraction to HTML | DDC (`n8n_9`) | Quantity take-off report generation |
| Batch processing | DDC (`n8n_3`) | Processes multiple files in one run |
| ETL extract + parse | DDC (`n8n_8`) | Extracts and parses XLSX for downstream use |
| **BQI scoring formula** | **Original** | Weighted scoring of BIM trustworthiness per element and per model |
| **Uncertainty-aware risk screening** | **Original** | Likelihood + consequence proxies from BIM-only data |
| **Confidence bounds from BQI** | **Original** | Missing-data penalties and conservative screening |
| **Fault injection methodology** | **Original** | Controlled error injection and robustness benchmarking |
| **QTO robustness analysis** | **Original** | Spearman rank correlation between two extraction methods |
| **Explainable risk register** | **Original** | Auditable output linking risk scores to BIM data quality |

---

## Repository Structure

```
n8n-thesis/
├── README.md                           ← You are here
│
├── sample-models/
│   ├── README.md                       ← Describes each IFC file and fault types
│   ├── baseline/                       ← 8 clean original IFC files (reference models)
│   └── fault-injected/                 ← Broken variants for robustness testing (Task 5)
│
├── workflows/
│   ├── README.md                       ← Explains ddc-base vs thesis split
│   ├── ddc-base/                       ← All 9 original DDC workflows (unchanged reference)
│   │   └── README.md                   ← What each DDC workflow does and its thesis relevance
│   └── thesis/                         ← Adapted and custom workflows for this thesis
│       └── README.md                   ← What was changed, why, and what is new
│
├── outputs/
│   ├── README.md                       ← Explains output types and file naming convention
│   ├── qto/                            ← QTO results (CSV/JSON)
│   ├── bqi/                            ← BQI scores and confidence labels
│   └── reports/                        ← PDF/HTML risk reports
│
├── scripts/
│   ├── README.md                       ← Describes each Python script and its purpose
│   └── (Python scripts — ifcopenshell, QTO comparison, fault injection)
│
└── docs/
    ├── README.md                       ← Guide to all documentation files
    ├── bqi-definition.md               ← BQI scoring formula and rules
    ├── risk-rules-table.md             ← Risk screening logic
    ├── validation-ruleset.md           ← IFC validation rules
    └── ddc-adaptation-notes.md         ← What was changed from DDC base workflows and why
```

---

## How the Pipeline Works

```
IFC File
   ↓
[DDC IfcExporter] ──────────────────────→ XLSX (element data)
   ↓                                           ↓
[n8n_4 Validation] ──→ Validation Report    [n8n_9 QTO] ──→ QTO Report
   ↓                                           ↓
[BQI Scoring] ────────────────────────────────┘
   ↓
BQI Score + Confidence Label
   ↓
[Risk Screening Model]
   ↓
Uncertainty-Aware Risk Register + PDF Report
```

**DDC toolkit handles:** conversion, validation, QTO extraction
**This thesis adds:** BQI scoring, risk screening, uncertainty propagation, fault injection benchmarking

---

## Tools & Technologies

| Tool | Role in This Thesis |
|------|---------------------|
| **n8n** | Workflow automation and orchestration — runs the entire pipeline |
| **DDC IfcExporter** | Converts IFC files to XLSX for downstream processing |
| **DDC n8n_1** | Base single-file conversion workflow |
| **DDC n8n_3** | Base batch conversion workflow — used for fault injection testing (Task 5) |
| **DDC n8n_4** | Base validation workflow — adapted for IFC schema and property checks |
| **DDC n8n_8** | Base ETL extract workflow — used as QTO Method 1 input (Task 6) |
| **DDC n8n_9** | Base QTO workflow — adapted for IFC element types |
| **IFC / ifcopenshell** | BIM data extraction and second QTO method (Task 6 comparison) |
| **Python** | BQI scoring, fault injection, Spearman rank correlation |
| **GitHub** | Version control and model storage |

---

## Sample IFC Models

8 baseline IFC files are stored in `sample-models/baseline/`, sourced from official buildingSMART repositories:

- buildingSMART Sample Test Files (IFC4 & IFC4.3): https://github.com/buildingSMART/Sample-Test-Files
- buildingSMART Community Sample Files: https://github.com/buildingsmart-community/Community-Sample-Test-Files

| File | Schema | Type |
|------|--------|------|
| `IFC4-Building-Architecture.ifc` | IFC 4.0.2.1 | Building — Architecture |
| `IFC4-Building-Structural.ifc` | IFC 4.0.2.1 | Building — Structural |
| `IFC4-Infra-Bridge.ifc` | IFC 4.0.2.1 | Infrastructure — Bridge |
| `IFC4-Infra-Road.ifc` | IFC 4.0.2.1 | Infrastructure — Road |
| `IFC4-wall-with-opening-and-window.ifc` | IFC 4.0.2.1 | Building — Wall detail |
| `IFC43-Building-Structural.ifc` | IFC 4.3 | Building — Structural |
| `IFC43-Infra-Bridge.ifc` | IFC 4.3 | Infrastructure — Bridge |
| `IFC43-Infra-Road.ifc` | IFC 4.3 | Infrastructure — Road |

Fault-injected variants (Task 5) will be generated programmatically and stored in `sample-models/fault-injected/`.

---

## Project Resources

| Resource | Description | Link |
|----------|-------------|------|
| DDC CAD-to-data toolkit | Core pipeline — IFC/Revit conversion, validation, QTO, and n8n workflows | [cad2data-Revit-IFC-DWG-DGN](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN) |
| n8n-skills | n8n skillset for building robust n8n workflows | [n8n-skills](https://github.com/czlonkowski/n8n-skills) |
| buildingSMART Sample Files | Source of baseline IFC models | [Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) |

---

## Progress Log

| Date | Update |
|------|--------|
| Apr 2026 | Repository created, folder structure established |
| Apr 2026 | Task 1 complete — 8 baseline IFC files added (IFC4 + IFC4.3) |
| Apr 2026 | All 9 DDC workflows uploaded to workflows/ddc-base/ |
| Apr 2026 | All folder READMEs created |
| Apr 2026 | Task 2 in progress — adapting DDC workflows for IFC inputs |
