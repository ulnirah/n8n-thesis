# Uncertainty-Aware Risk Screening from Imperfect BIM Using N8N

**Author:** Aulia Annisa Rahmatillah
**Programme:** EMJM NORISK — Erasmus Mundus Joint Master's in Risk Assessment and Management of Civil Infrastructures  
**University:** Technical University of Catalonia (UPC), Barcelona, Spain  
**Supervisor:** Seyedmilad Komarizadehasl  
**Co-supervisor:** Mahyad Komarizadehasl  

---

## Overview

This repository contains all materials for the thesis:
> *Uncertainty-Aware Risk Screening from Imperfect BIM Using N8N with IFC Validation, QTO Robustness, and Explainable Risk Registers*

The project builds an automated n8n workflow that processes open IFC/BIM models to produce uncertainty-aware risk registers — without requiring field monitoring data.

---

## Thesis Tasks

| # | Task | Status |
|---|------|--------|
| 1 | Select and prepare BIM inputs (IFC sample models) | 🔲 In progress |
| 2 | Build end-to-end n8n workflow (trigger → validate → extract → report) | 🔲 Not started |
| 3 | Define BIM Quality Index (BQI) | 🔲 Not started |
| 4 | Develop uncertainty-aware risk screening model | 🔲 Not started |
| 5 | Benchmark robustness via fault injection | 🔲 Not started |
| 6 | Check QTO robustness across extraction methods | 🔲 Not started |
| 7 | Deliver final package | 🔲 Not started |

---

## Repository Structure
```
n8n-thesis/
├── sample-models/
│   ├── baseline/        # Clean original IFC files (reference models)
│   └── fault-injected/  # Broken variants for robustness testing (Task 5)
├── workflows/           # n8n workflow JSON exports
├── outputs/
│   ├── qto/             # QTO results (CSV/JSON)
│   ├── bqi/             # BQI scores and confidence labels
│   └── reports/         # PDF risk reports
├── scripts/             # Python scripts (ifcopenshell, QTO comparison)
└── docs/
    ├── bqi-definition.md      # BQI scoring formula and rules
    ├── risk-rules-table.md    # Risk screening logic
    └── validation-ruleset.md  # IFC validation rules
```

---

## Tools & Technologies

- **n8n** — workflow automation and orchestration
- **IFC / ifcopenshell** — BIM data extraction and QTO
- **DDC CAD-to-data toolkit** — IFC/Revit conversion and validation
- **Python** — BQI scoring, fault injection, Spearman correlation
- **GitHub** — version control and model storage

---

## Key References

- DDC Toolkit: https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto
- buildingSMART Sample IFC Files: https://github.com/buildingSMART/Sample-Test-Files
