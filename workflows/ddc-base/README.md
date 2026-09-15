# DDC Base Workflows

This folder contains the original workflow JSON files from the
[DataDrivenConstruction (DDC) CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN).

They are preserved as **external reference artefacts** documenting the DDC workflow infrastructure on which the thesis Pipeline A is based.

> **Do not modify these files.**
>
> The thesis-specific workflow is stored separately under
> [`workflows/thesis/`](../thesis/).

---

## Role in the Thesis

The DDC toolkit provides the external conversion infrastructure used by
**Pipeline A** of the thesis workflow.

In the thesis workflow:

```text
IFC model
   │
   ▼
DDC IfcExporter
   │
   ▼
XLSX
   │
   ▼
Parsed tabular element data
   │
   ▼
Pipeline A
```

Pipeline A is then compared against the independent **Pipeline B**, which uses
IfcOpenShell and the thesis-controlled `scripts/extract_ifc.py` extractor.

```text
                 ┌──────────────────────┐
                 │      IFC input       │
                 └──────────┬───────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       Pipeline A                  Pipeline B
     DDC IfcExporter              IfcOpenShell
              │                           │
              ▼                           ▼
           XLSX                         JSON
              │                           │
              └─────────────┬─────────────┘
                            ▼
                 QTO comparison + BQI
                            │
                            ▼
                     Risk screening
                            │
                            ▼
                   Report + sensitivity
```

The thesis uses **DDC IFC Exporter v17.1.1.0** as Pipeline A. The independent
Pipeline B uses **IfcOpenShell 0.8.5** and `extract_ifc.py`. :contentReference[oaicite:1]{index=1}

---

## Original DDC Workflow Files

The original DDC toolkit contains the following workflow families:

| File | DDC Workflow | Relationship to Thesis |
|---|---|---|
| `n8n_1_basic_conversion.json` | Basic Conversion | Reference for the IFC/CAD-to-tabular conversion pathway represented by Pipeline A |
| `n8n_2_all_settings_conversion.json` | Advanced Settings Conversion | External DDC variant; not a thesis-specific workflow |
| `n8n_3_batch_converter.json` | Batch Conversion + Reporting | External DDC batch-processing functionality; not part of the core thesis workflow architecture |
| `n8n_4_validation.json` | BIM Validation | External DDC validation functionality; thesis BQI scoring is implemented separately |
| `n8n_5_classification_llm.json` | AI Classification / RAG | Outside the computational scope of the thesis |
| `n8n_6_cost_estimation.json` | Construction Cost Estimation | Outside the thesis scope |
| `n8n_7_carbon_footprint.json` | Carbon Footprint Estimation | Outside the thesis scope |
| `n8n_8_etl_extract.json` | ETL / XLSX extraction | Reference for tabular extraction and downstream processing concepts |
| `n8n_9_qto_html_report.json` | QTO reporting | Reference for DDC-based quantity extraction/reporting concepts |

These files are preserved to make the external provenance of the DDC
infrastructure explicit. They should not be interpreted as nine thesis
contributions or as nine workflows executed unchanged in the final
experimental pipeline.

---

## What Was Adapted for the Thesis

The thesis workflow does **not** simply execute the original DDC workflows
unchanged.

Instead, the DDC infrastructure is incorporated into **Block 1: Pipeline A**,
where the workflow:

1. receives an IFC input;
2. checks whether the expected XLSX conversion already exists;
3. executes `IfcExporter.exe` when conversion is required;
4. reads the generated XLSX file;
5. parses the tabular records;
6. removes spatial entities from the analysis stream; and
7. tags the resulting records as `A_ddc`.

The thesis workflow then combines these records with the independently extracted
Pipeline B data.

---

## Thesis-Specific Logic

The following components are implemented in the thesis workflow rather than
being claimed as original DDC functionality:

### Block 0 — Configuration

Centralises:

- input IFC paths;
- DDC converter path;
- output directory;
- BQI dimension weights;
- uncertainty coefficient `α`;
- coverage threshold; and
- optional second IFC input for dual-file experiments.

### Block 1 — Pipeline A

Uses the DDC IFC conversion pathway to create and parse the XLSX representation.

### Block 2 — Pipeline B

Downloads the version-controlled `extract_ifc.py` script and uses IfcOpenShell
to extract:

- IFC elements;
- properties;
- quantities;
- materials;
- spatial information; and
- schema metadata.

### Block 3 — QTO Comparison and BQI

This is thesis-specific processing.

It performs:

- `GlobalId` matching between Pipeline A and Pipeline B;
- quantity comparison;
- element coverage analysis;
- BQI dimension scoring;
- model-level BQI aggregation; and
- SRCC-based cross-pipeline analysis.

The four BQI dimensions are:

- **D1:** property completeness;
- **D2:** property validity;
- **D3:** QTO coverage;
- **D4:** cross-pipeline QTO agreement.

### Block 4 — Risk Screening

Uses the thesis risk-screening formulation to derive:

- exposure;
- likelihood;
- consequence;
- raw risk;
- BQI-dependent uncertainty widening;
- adjusted risk; and
- final risk ranking.

### Block 5 — Output Generation

Produces the thesis reporting artefacts, including:

- HTML risk register;
- per-element sensitivity JSON; and
- diagnostic outputs.

---

## External versus Original Components

The repository distinguishes the external DDC infrastructure from the original
thesis contribution.

### External / adapted

- DDC IFC conversion infrastructure;
- DDC `IfcExporter.exe`;
- DDC tabular/XLSX extraction pathway;
- selected concepts from the original DDC n8n workflows.

### Thesis-specific

- dual-pipeline architecture;
- BQI framework;
- schema-aware scoring rules;
- GlobalId-based cross-pipeline comparison;
- element coverage analysis;
- SRCC protocol;
- controlled F1–F6 fault-injection evaluation;
- uncertainty-aware risk screening;
- sensitivity analysis;
- deterministic reporting; and
- n8n orchestration of the complete chain.

This distinction is important for provenance and authorship: the DDC toolkit is an
external dependency, while the quality-assessment, uncertainty, comparison,
and screening framework constitutes the computational contribution of the thesis.

---

## Adaptation Documentation

The changes made when incorporating the DDC infrastructure into the thesis
workflow are documented separately in:

[`docs/ddc-adaptation-notes.md`](../../docs/ddc-adaptation-notes.md)

That document should be treated as the detailed record of configuration,
environment, and workflow adaptations.

---

## Preservation Policy

The files in this folder are retained as **reference copies** of the external
DDC workflow infrastructure.

They should remain unchanged after being added to the repository.

The reproducible thesis workflow is:

[`workflows/thesis/`](../thesis/)

rather than the individual base DDC workflow files.
