# DDC Base Workflows

This folder contains all 9 original workflow JSON files from the [DDC CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN).

> ⚠️ **Do not modify these files.** They are kept here as unchanged reference copies. All adaptations for this thesis are in the `workflows/thesis/` folder.

---

## Workflow Reference Table

| File | DDC Name | What It Does | Relevance to This Thesis |
|------|----------|-------------|--------------------------|
| `n8n_1_basic_conversion.json` | Basic Conversion | Converts a single IFC/Revit/DWG file to XLSX + DAE | ✅ **Core** — starting point for Task 2, adapted to use IfcExporter |
| `n8n_2_all_settings_conversion.json` | Advanced Settings Conversion | Same as n8n_1 but with export mode options (basic/standard/complete) | 🔲 Not used — n8n_1 is sufficient for thesis |
| `n8n_3_batch_converter.json` | Batch Conversion + Reporting | Processes multiple files in a folder, generates HTML report | ✅ **Core** — used in Task 5 to batch-process all fault-injected models |
| `n8n_4_validation.json` | BIM Validation | Validates XLSX data against a rules spreadsheet, produces color-coded Excel report | ✅ **Core** — adapted for IFC in Task 2, raw validation scores feed into BQI (Task 3) |
| `n8n_5_classification_llm.json` | AI Classification with LLM + RAG | Classifies elements using AI (OpenAI/Anthropic) and a mapping file | 🔲 Not used — requires LLM API keys, not part of thesis scope |
| `n8n_6_cost_estimation.json` | Construction Cost Estimation | Estimates construction costs using AI and DDC CWICR database | 🔲 Not used — cost estimation is outside thesis scope |
| `n8n_7_carbon_footprint.json` | Carbon Footprint CO2 Estimator | Calculates embodied carbon emissions using AI | 🔲 Not used — carbon analysis is outside thesis scope |
| `n8n_8_etl_extract.json` | Simple ETL Extract + Parse XLSX | Converts file, reads XLSX, parses data for downstream use | ✅ **Supporting** — used in Task 6 as the first QTO extraction method for comparison |
| `n8n_9_qto_html_report.json` | QTO HTML Report Generator | Filters elements, groups by type, sums volumes, generates HTML QTO report | ✅ **Core** — adapted for IFC element types in Task 2, used as one QTO method in Task 6 |

---

## Key Observations for This Thesis

**Workflows used (5 of 9):** n8n_1, n8n_3, n8n_4, n8n_8, n8n_9

**Workflows not used (4 of 9):** n8n_2, n8n_5, n8n_6, n8n_7
- n8n_2 is redundant given n8n_1
- n8n_5, n8n_6, n8n_7 require external LLM API keys and are outside thesis scope

---

## Important: IFC vs Revit Differences

All DDC workflows were originally written for Revit (`.rvt`) files. When adapting for IFC, the following changes are needed in the thesis workflows:

| What Changes | Revit (original) | IFC (adapted) |
|---|---|---|
| Converter executable | `RvtExporter.exe` | `IfcExporter.exe` |
| File extension filter | `.rvt` | `.ifc` |
| Wall category filter | `OST_Walls` | `IfcWall` |
| Column name prefix | `Type Name : String` | depends on IFC schema |
| Converter path variable | `path_to_converter` | `path_to_converter` (same, different value) |

These changes are documented in detail in `docs/ddc-adaptation-notes.md`.

---

## Known Issues

| Workflow | Issue | Fix |
|----------|-------|-----|
| n8n_4 (validation) | Python `os` module blocked in n8n versions 1.98–1.101 | Run `npx n8n@latest` |
| All workflows | Paths hardcoded to `C:\Users\Artem Boiko\...` | Update Set Variables node before running |
| n8n_4 (validation) | Requires `DDC_BIM_Requirements_Table_for_Revit_IFC_DWG.xlsx` | File must exist at the path specified in Set Validation Rules Path node |
