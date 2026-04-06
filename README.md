# Uncertainty-Aware Risk Screening from Imperfect BIM Using N8N

**Author:** Aulia Annisa Rahmatillah      
**Programme:** The International Masters in Risk Assessment and Management of Civil Infrastructures – NORISK        
**University:** Technical University of Catalonia (UPC), Barcelona, Spain      
**Supervisor:** Seyedmilad Komarizadehasl      
**Co-supervisor:** Mahyad Komary      

---

## Overview

This repository contains all materials for the thesis:

> *Uncertainty-Aware Risk Screening from Imperfect BIM Using N8N with IFC Validation, QTO Robustness, and Explainable Risk Registers*

The project builds an automated n8n workflow that processes open IFC/BIM models to produce uncertainty-aware risk registers — without requiring field monitoring data.

The pipeline is built on top of the [DDC CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN) as its core conversion and validation infrastructure. The original contributions of this thesis — BQI scoring, uncertainty-aware risk screening, fault injection benchmarking, and QTO robustness analysis — are developed on top of that foundation.

---

## Thesis Tasks

| # | Task | Status |
|---|------|--------|
| 1 | Select and prepare BIM inputs (IFC sample models) | ✅ Done — 8 IFC files (IFC4 + IFC4.3), buildingSMART samples |
| 2 | Build end-to-end n8n workflow (trigger → convert → validate → extract → report) | 🔄 In progress — adapting DDC n8n_4 (validation) + n8n_9 (QTO) for IFC |
| 3 | Define BIM Quality Index (BQI) | 🔲 Not started |
| 4 | Develop uncertainty-aware risk screening model | 🔲 Not started |
| 5 | Benchmark robustness via fault injection | 🔲 Not started |
| 6 | Check QTO robustness across extraction methods | 🔲 Not started |
| 7 | Deliver final package | 🔲 Not started |

---

## What is Original vs. What is Adapted

This thesis builds on the DDC toolkit as infrastructure. The table below clarifies the boundary between what is given and what is the original contribution of this work.

| Component | Source | Description |
|-----------|--------|-------------|
| IFC → XLSX conversion | DDC (`IfcExporter.exe`) | Converts IFC files to structured Excel data |
| Basic IFC validation | DDC (`n8n_4`) | Schema compliance, property fill rates |
| QTO extraction to HTML | DDC (`n8n_9`) | Quantity take-off report generation |
| **BQI scoring formula** | **Original** | Weighted scoring of BIM trustworthiness per element and per model |
| **Uncertainty-aware risk screening** | **Original** | Likelihood + consequence proxies from BIM-only data |
| **Confidence bounds from BQI** | **Original** | Missing-data penalties and conservative screening |
| **Fault injection methodology** | **Original** | Controlled error injection and robustness benchmarking |
| **QTO robustness analysis** | **Original** | Spearman correlation between two extraction methods |
| **Explainable risk register** | **Original** | Auditable output linking risk scores to BIM data quality |

---

## Repository Structure

```
n8n-thesis/
├── sample-models/
│   ├── baseline/               # Clean original IFC files (reference models)
│   └── fault-injected/         # Broken variants for robustness testing (Task 5)
│
├── workflows/
│   ├── ddc-base/               # Original DDC workflows (unchanged reference)
│   │   ├── n8n_1_basic_conversion.json
│   │   ├── n8n_4_validation.json
│   │   └── n8n_9_qto_report.json
│   └── thesis/                 # Adapted and custom workflows (this thesis)
│       ├── n8n_ifc_validation_adapted.json
│       ├── n8n_qto_extraction.json
│       └── n8n_risk_register.json
│
├── outputs/
│   ├── qto/                    # QTO results (CSV/JSON)
│   ├── bqi/                    # BQI scores and confidence labels
│   └── reports/                # PDF/HTML risk reports
│
├── scripts/                    # Python scripts (ifcopenshell, QTO comparison)
│
└── docs/
    ├── bqi-definition.md           # BQI scoring formula and rules
    ├── risk-rules-table.md         # Risk screening logic
    ├── validation-ruleset.md       # IFC validation rules
    └── ddc-adaptation-notes.md     # What was changed from DDC base workflows
```

---

## Tools & Technologies

| Tool | Role in This Thesis |
|------|---------------------|
| **n8n** | Workflow automation and orchestration — runs the entire pipeline |
| **DDC IfcExporter** | Converts IFC files to XLSX for downstream processing |
| **DDC n8n_4** | Base validation workflow — adapted for IFC schema and property checks |
| **DDC n8n_9** | Base QTO workflow — adapted for IFC element types (IfcWall, IfcSlab, etc.) |
| **IFC / ifcopenshell** | BIM data extraction and second QTO method (Task 6 comparison) |
| **Python** | BQI scoring, fault injection, Spearman rank correlation |
| **GitHub** | Version control and model storage |

---

## Sample IFC Models

Baseline IFC files sourced from:

- buildingSMART Sample Test Files (IFC4 & IFC4.3): https://github.com/buildingSMART/Sample-Test-Files
- buildingSMART Community Sample Files: https://github.com/buildingsmart-community/Community-Sample-Test-Files

All baseline models are stored in `sample-models/baseline/`. Fault-injected variants (Task 5) will be generated programmatically and stored in `sample-models/fault-injected/`.

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
| Apr 2026 | DDC workflows studied and documented |
| — | Task 2 in progress — adapting DDC workflows for IFC inputs |
