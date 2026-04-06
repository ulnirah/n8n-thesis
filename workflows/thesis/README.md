# Thesis Workflows

This folder contains n8n workflow JSON files that are either:
- **Adapted** from DDC base workflows (modified for IFC inputs and thesis requirements)
- **Original** — newly created for this thesis with no DDC equivalent

---

## Workflow Status

| File | Based On | Status | Thesis Task |
|------|----------|--------|-------------|
| `n8n_ifc_validation_adapted.json` | DDC n8n_1 + n8n_4 | 🔲 Not started | Task 2 — IFC validation |
| `n8n_qto_extraction.json` | DDC n8n_8 + n8n_9 | 🔲 Not started | Task 2 + Task 6 — QTO extraction |
| `n8n_fault_injection_batch.json` | DDC n8n_3 | 🔲 Not started | Task 5 — batch processing of fault-injected models |
| `n8n_bqi_scoring.json` | Original | 🔲 Not started | Task 3 — BQI scoring from validation output |
| `n8n_risk_register.json` | Original | 🔲 Not started | Task 4 — uncertainty-aware risk screening |

---

## Workflow Descriptions

### n8n_ifc_validation_adapted
**Based on:** DDC n8n_1 (conversion) + n8n_4 (validation)
**Purpose:** Converts an IFC file to XLSX using IfcExporter, then validates the output against a custom IFC validation ruleset.

Changes from DDC original:
- Converter changed from `RvtExporter.exe` to `IfcExporter.exe`
- File extension changed from `.rvt` to `.ifc`
- Validation rules updated for IFC schema (naming, property sets, spatial structure, units)
- Output feeds into BQI scoring (Task 3)

---

### n8n_qto_extraction
**Based on:** DDC n8n_8 (ETL extract) + n8n_9 (QTO report)
**Purpose:** Extracts element inventory and quantities (counts, lengths, areas, volumes) from an IFC file and produces structured CSV/JSON output and an HTML QTO report.

Changes from DDC original:
- Converter changed to `IfcExporter.exe`
- Element filter updated from `OST_Walls` (Revit) to IFC element types (`IfcWall`, `IfcSlab`, `IfcBeam`, etc.)
- Output structured for downstream risk scoring (Task 4)
- Also used as Method 1 in QTO robustness comparison (Task 6)

---

### n8n_fault_injection_batch
**Based on:** DDC n8n_3 (batch conversion)
**Purpose:** Processes all fault-injected IFC models in `sample-models/fault-injected/` in batch, runs validation and QTO on each, and collects outputs for robustness analysis.

Changes from DDC original:
- Source folder pointed to `fault-injected/` directory
- File extension filter set to `.ifc`
- Outputs saved per fault type for comparison

---

### n8n_bqi_scoring
**Based on:** Original (no DDC equivalent)
**Purpose:** Reads validation output from n8n_ifc_validation_adapted and computes a BIM Quality Index (BQI) score per element and per model. Assigns confidence labels (High / Medium / Low).

Inputs: Validation output XLSX from n8n_4
Outputs: BQI score table (CSV/JSON) in `outputs/bqi/`

BQI formula and scoring rules are documented in `docs/bqi-definition.md`.

---

### n8n_risk_register
**Based on:** Original (no DDC equivalent)
**Purpose:** Implements the full uncertainty-aware risk screening model. Reads QTO output and BQI scores, computes likelihood proxy, consequence proxy, and risk score. Incorporates BQI as confidence bounds and missing-data penalties. Produces the final explainable risk register.

Inputs:
- QTO output from n8n_qto_extraction
- BQI scores from n8n_bqi_scoring

Outputs: Risk register (CSV/JSON) + PDF/HTML report in `outputs/reports/`

Risk logic is documented in `docs/risk-rules-table.md`.
