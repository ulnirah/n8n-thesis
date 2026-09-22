# DDC Base Workflows

This folder contains the nine original n8n workflow files from the
[DataDrivenConstruction (DDC) CAD-to-data toolkit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN).

They are kept as **external reference material**. They document the DDC tooling behind Pipeline A, but none of them is run in the thesis experiments.

> **Do not modify these files.**
>
> The workflow used for every thesis result is in [`../thesis/`](../thesis/).

---

## Role in the Thesis

The thesis uses one DDC component directly: the **DDC IFC Exporter 17.1.1.0** (`IfcExporter.exe`), which converts an IFC file into an XLSX table for **Pipeline A**. **Pipeline B** reads the same file independently with **IfcOpenShell 0.8.5** and [`scripts/extract_ifc.py`](../../scripts/extract_ifc.py).

```text
                         IFC input
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
         Pipeline A                  Pipeline B
     DDC IFC Exporter               IfcOpenShell
      (IFC → XLSX)            (extract_ifc.py → JSON)
              │                           │
              └─────────────┬─────────────┘
                            ▼
          Merge by GlobalId, QTO comparison, BQI
                            │
                            ▼
                      Risk screening
                            │
                            ▼
              Risk register + sensitivity JSON
```

---

## Files in This Folder

| File | DDC workflow | Relationship to the thesis |
|---|---|---|
| `n8n_1_Revit_IFC_DWG_Conversation_simple.json` | Basic conversion | Reference for the IFC-to-table conversion used in Pipeline A |
| `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json` | Conversion with all settings | DDC variant; not used |
| `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json` | Batch conversion and reporting | DDC batch processing; not used |
| `n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json` | BIM validation | DDC validation; the thesis BQI is implemented separately |
| `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json` | Classification with LLM and RAG | Outside the thesis scope |
| `n8n_6_Construction_Price_Estimation_with_LLM_for_Revt_and_IFC.json` | Cost estimation with LLM | Outside the thesis scope |
| `n8n_7_Carbon_Footprint_CO2_Estimator_for_Revit and_IFC.json` | Carbon footprint estimation | Outside the thesis scope |
| `n8n_8_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json` | Conversion and XLSX parsing | Reference for reading and parsing the XLSX output |
| `n8n_9_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator.json` | QTO HTML report | Reference for quantity extraction and reporting |

The file names are DDC's own, including "Conversation" (for "Conversion") and the space in the `n8n_7` name.

These files make the external provenance visible. They are not thesis contributions, and none is executed in the experimental pipeline.

---

## What the Thesis Workflow Does with DDC

The thesis does not run the original DDC workflows. It wraps the DDC IFC Exporter in **Block 1 (Pipeline A)** of [`../thesis/n8n_ifc_dual_pipeline.json`](../thesis/n8n_ifc_dual_pipeline.json), which:

1. builds the expected XLSX path for the input IFC file;
2. reuses that XLSX if it already exists, and otherwise runs `IfcExporter.exe`;
3. stops the run if the conversion fails;
4. reads and parses the XLSX rows;
5. removes spatial rows such as `IfcProject`, `IfcSite`, `IfcBuilding` and `IfcBuildingStorey`; and
6. tags every remaining item as `A_ddc`.

Everything after that is thesis logic:

| Block | Role |
|---|---|
| 0 Configuration | Paths (`path_to_converter`, `project_file`, `project_file_b`, `output_dir`, `script_dir`), `group_by`, BQI weights, α and the coverage threshold |
| 1 Pipeline A | DDC conversion and XLSX parsing, as above |
| 2 Pipeline B | Downloads `extract_ifc.py` and extracts elements, properties, quantities, materials, spatial structure and schema with IfcOpenShell |
| 3 QTO comparison and BQI | GlobalId matching, quantity comparison, element coverage, D1–D4, element BQI, SRCC |
| 4 Risk screening | Exposure, likelihood, consequence, raw risk, uncertainty band, ranking and labels |
| 5 Output generation | HTML risk register, per-element sensitivity JSON and diagnostic outputs |

The adaptation is documented in detail in [`../../docs/ddc-adaptation-notes.md`](../../docs/ddc-adaptation-notes.md).

---

## External versus Thesis Components

| External (DDC) | Thesis |
|---|---|
| DDC IFC Exporter (`IfcExporter.exe`), used as a closed binary | Dual-pipeline architecture and n8n orchestration |
| The nine original workflows in this folder, as reference | IfcOpenShell extraction (`extract_ifc.py`) |
| | BQI framework and rule tables |
| | GlobalId matching, QTO comparison, element coverage and SRCC |
| | Fault injection (F1–F6), including the dual-file configuration |
| | Uncertainty-aware risk screening and reporting |
| | Sensitivity analysis and α characterisation |

---

## Notes on These Files

- **Paths.** The workflows contain the local file paths of their original author and will not run without editing. They are kept unedited as reference copies.
- **Licence.** The files remain subject to DataDrivenConstruction's licence terms; see the DDC repository linked above.
- **Preservation.** Keep the files unchanged. The reproducible thesis workflow is [`../thesis/n8n_ifc_dual_pipeline.json`](../thesis/n8n_ifc_dual_pipeline.json), not the files in this folder.
