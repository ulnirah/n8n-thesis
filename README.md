# Uncertainty-Aware Risk Screening from Imperfect Building Information Models

**Thesis repository for the NORISK Erasmus Mundus Joint Master**

**Author:** Aulia Annisa Rahmatillah  
**Programme:** International Master's in Risk Assessment and Management of Civil Infrastructures (NORISK)  
**Institution:** Universitat Politècnica de Catalunya (UPC), Barcelona, Spain  
**Supervisor:** Seyedmilad Komarizadehasl  
**Co-supervisor:** Mahyad Komary  

---

## Overview

This repository contains the computational artefacts of the MSc thesis:

> **Uncertainty-Aware Risk Screening from Imperfect Building Information Models: Schema Validation, Quantity Take-Off Robustness, and Explainable Risk Registers in an n8n Workflow**

BIM-based risk screening usually assumes that the input IFC file is reliable. Real models are often incomplete or inconsistent, and binary pass/fail validation cannot say how far a model falls short or what that does to a risk score.

The thesis introduces the **BIM Quality Index (BQI)**, a continuous, weighted quality score with four dimensions:

| Dimension | Question | Weight |
|---|---|---|
| D1 Completeness | Are the required properties present? | 0.35 |
| D2 Validity | Are the values usable, not empty or UNSET? | 0.25 |
| D3 QTO coverage | Are the expected quantities present? | 0.20 |
| D4 Cross-pipeline agreement | Do two independent extractors agree on the quantities? | 0.20 |

The BQI is computed per element from two independent IFC extraction pipelines and propagated into a risk band. The adjusted upper bound, `R_adj = R_raw × (1 + α(1 − BQI))` with `α = 0.55`, is used for ranking, so elements with poor data are screened conservatively. The whole chain, from IFC input to an explainable HTML risk register, runs in one **n8n** workflow.

---

## Contributions

| # | Contribution | Research gap |
|---|---|---|
| 1 | **BIM Quality Index (BQI):** continuous, four-dimensional, weighted IFC quality score, validated as a measurement instrument | RG1 Binary validation |
| 2 | **Ground-truth-free QTO robustness:** cross-pipeline rank agreement (SRCC) as a quality signal where no reference quantity exists | RG2 QTO extraction variance |
| 3 | **Uncertainty-aware risk screening:** deterministic propagation of input quality into a risk band that carries the screening decision | RG3 Deterministic risk and black-box pipelines |
| 4 | **Open reproducible orchestration:** end-to-end n8n workflow with versioned scripts, released as a citable artefact | RG4 Pipeline orchestration |
| 5 | **Methodological finding:** a fault that targets disagreement between two consumers cannot be simulated by corrupting a file they both read, so multi-tool robustness benchmarks need a dual-file design | — |

Supporting components: controlled fault injection, parameter sensitivity analysis, and the explainable risk register.

---

## Headline Results

- The BQI never increases under injected faults across all **56** model × fault × configuration combinations, and strictly decreases wherever a fault can manifest.
- The targeted dimension is the most affected in all but two model–fault combinations.
- A binary validator gives all **18** faulted files of model M1 the same verdict ("fail"); the BQI separates **15** levels, from 0.309 to 0.466.
- The negative control (M8) has **100%** element coverage but **BQI = 0.000**; the uncertainty band escalates 16 of its 81 elements to High.
- The screening ranking is stable: minimum rank-stability SRCC **≥ 0.908** across 3,500 random weight vectors, and ≥ 0.936 across the α sweep.

---

## Components and Provenance

| Component | Source | Role |
|---|---|---|
| IFC → XLSX conversion | DDC IFC Exporter (external, closed binary) | Pipeline A extraction |
| IfcOpenShell extraction | `scripts/extract_ifc.py` (this thesis) | Pipeline B extraction |
| QTO comparison, BQI, risk screening, reporting | n8n workflow Code nodes (this thesis) | Scoring and screening |
| Fault injection, verification, analyses | `scripts/` (this thesis) | Evaluation |
| Original DDC workflow collection | DataDrivenConstruction | Preserved as reference in `workflows/ddc-base/` |

The thesis does not claim ownership of the DDC IFC Exporter. Adaptation notes are in `docs/ddc-adaptation-notes.md`.

---

## Workflow Architecture

```text
                         IFC input
                            |
              +-------------+-------------+
              |                           |
              v                           v
         Pipeline A                  Pipeline B
     DDC IFC Exporter              IfcOpenShell
        (IFC → XLSX)            (extract_ifc.py → JSON)
              |                           |
              +-------------+-------------+
                            |
              Merge by GlobalId, element coverage
                            |
                   QTO comparison, SRCC
                            |
                   BQI scoring (D1–D4)
                            |
          Risk proxies: likelihood × consequence
                            |
          Uncertainty band from BQI and α = 0.55
                            |
          Ranking on R_adj, High / Medium / Low labels
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          HTML risk register    Sensitivity JSON
```

The workflow has 44 functional nodes in six blocks (0 Configuration, 1 Pipeline A, 2 Pipeline B, 3 QTO comparison and BQI, 4 Risk screening, 5 Output generation). The export is `workflows/thesis/n8n_ifc_dual_pipeline.json`.

---

## Corpus

Eight IFC sample files from the official [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) repository (PCERT sample scene), stored in `sample-models/baseline/`.

| ID | File | Schema | Elements | Baseline BQI |
|---|---|---|---|---|
| M1 | `IFC4-Building-Architecture.ifc` | IFC 4 | 14 | 0.471 |
| M2 | `IFC43-Building-Architecture.ifc` | IFC 4.3 | 14 | 0.350 |
| M3 | `IFC4-Building-Structural.ifc` | IFC 4 | 16 | 0.561 |
| M4 | `IFC43-Building-Structural.ifc` | IFC 4.3 | 16 | 0.413 |
| M5 | `IFC4-Infra-Bridge.ifc` | IFC 4 | 57 | 0.281 |
| M6 | `IFC43-Infra-Bridge.ifc` | IFC 4.3 | 68 | 0.140 |
| M7 | `IFC4-Infra-Road.ifc` | IFC 4 | 55 | 0.462 |
| M8 | `IFC43-Infra-Road.ifc` | IFC 4.3 | 81 | 0.000 |

M1–M7 are the valid models used in the principal experiments. M8 carries no property or quantity data and is retained as the **negative control**. Corpus details are in `sample-models/README.md`.

---

## Fault Injection

Six fault types, each targeting specific BQI dimensions:

| Fault | Mutation | Targeted instrument |
|---|---|---|
| F1 | Remove a required property | D1 |
| F2 | Blank a property value to UNSET | D1 + D2 |
| F3 | Remove a quantity field | D3 |
| F4 | Perturb quantity magnitudes by +10% | D4 |
| F5 | Remove an entire property set | D1 + D2 |
| F6 | Delete whole elements | Element coverage |

Severity is the share of eligible elements faulted (10%, 25%, 50%), sampled with seed 42 from 16 element types: the twelve rule-table types plus `IfcStair`, `IfcStairFlight`, `IfcFooting` and `IfcPile`.

The 126 faulted files (6 faults × 3 severities × 7 models) are stored in `sample-models/fault-injected/`:

- `<model>__F<n>-r<rate>-s42.ifc` for F1, F2, F3 and F5
- `<model>__F<n>-r<rate>-s42_PIPELINE-B-ONLY.ifc` for F4 and F6

### Experimental configurations

| Configuration | Runs | Input |
|---|---|---|
| Baseline | 8 | Unmodified models |
| Single file: F1, F2, F3, F5 | 84 | Faulted file read by both pipelines |
| Single file: F4, F6 | 42 | Faulted file read by both pipelines |
| Dual file: F4, F6 | 42 | Faulted file read by Pipeline B only; Pipeline A reads the original |
| **Total** | **176** | |

When both pipelines read the same perturbed file, they read the same wrong value and still agree, so a disagreement fault is invisible by construction. F4 and F6 therefore need the dual-file configuration to be detected.

---

## Representative Outputs

`examples/` contains the baseline outputs for all eight models:

- `risk-register-<model>-<timestamp>.html`: the explainable risk register
- `sensitivity-<model>.json`: the per-element dataset used by the offline analyses

The full campaign outputs are regenerated during reproduction and are not committed.

---

## Repository Structure

```text
n8n-thesis/
├── README.md
├── docs/
│   ├── README.md
│   ├── bqi-definition.md
│   ├── ddc-adaptation-notes.md
│   ├── risk-rules-table.md
│   └── validation-ruleset.md
├── examples/
│   ├── README.md
│   ├── risk-register-<model>-<timestamp>.html   (8 files)
│   └── sensitivity-<model>.json                 (8 files)
├── sample-models/
│   ├── README.md
│   ├── baseline/                                (8 IFC files)
│   └── fault-injected/                          (126 IFC files)
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
└── workflows/
    ├── README.md
    ├── ddc-base/                                (original DDC workflows)
    └── thesis/
        ├── README.md
        └── n8n_ifc_dual_pipeline.json
```

---

## Scripts

| Script | Purpose |
|---|---|
| `extract_ifc.py` | Pipeline B: extracts elements, properties, quantities, materials, schema and spatial structure with IfcOpenShell |
| `fault_injection.py` | Generates the faulted IFC variants and a JSON manifest per variant |
| `fault_analysis.py` | Compares faulted runs with baselines: deltas, monotonicity and selectivity |
| `sensitivity_analysis.py` | Weight and α perturbation: rank-stability SRCC, label flips, top-10 Jaccard |
| `alpha_characterization.py` | Derives the admissible interval for α and the recommended value |
| `verify_exports.py` | Structural checks on the sensitivity JSON exports |
| `verify_exports.ps1` | PowerShell version of the export checks |
| `harvest_reports.ps1` | Collects verdicts and key figures from the HTML reports into one CSV |

---

## Requirements

| Component | Version used in the thesis |
|---|---|
| Operating system | Windows (the DDC IFC Exporter is a Windows executable) |
| n8n | 2.7.5 |
| DDC IFC Exporter | 17.1.1.0 |
| IfcOpenShell | 0.8.5 |
| Python | 3.x (the analysis scripts use the standard library only) |
| PowerShell | 5.1 or later, for the `.ps1` scripts |

---

## Reproducing the Study

1. **Get the release.**
   ```bash
   git clone --branch v1.0.2 https://github.com/ulnirah/n8n-thesis.git
   ```

2. **Install IfcOpenShell** for Pipeline B and fault injection.
   ```bash
   pip install ifcopenshell==0.8.5
   ```

3. **Import the workflow** `workflows/thesis/n8n_ifc_dual_pipeline.json` into n8n.

4. **Set the paths in node `0.1 Config`.** The export still contains paths from the original workstation; replace them with your own:

   | Field | Value |
   |---|---|
   | `path_to_converter` | Full path to `IfcExporter.exe` |
   | `project_file` | IFC file read by Pipeline A (and by Pipeline B in single-file runs) |
   | `project_file_b` | Faulted file for Pipeline B; set only for dual-file runs |
   | `output_dir` | Folder for reports and exports |
   | `script_dir` | Local `scripts/` folder |

5. **(Optional) Regenerate the faulted files.**
   ```bash
   python scripts/fault_injection.py sample-models/baseline/IFC4-Building-Architecture.ifc --all --seed 42 --outdir faulted
   ```

6. **Run the four configurations** listed above. Each run writes a `risk-register-*.html` and a `sensitivity-*.json`.

7. **Verify the exports and collect the report results.**
   ```bash
   python scripts/verify_exports.py "<campaign_root>"
   powershell -ExecutionPolicy Bypass -File scripts/harvest_reports.ps1 -Root "<campaign_root>"
   ```

8. **Run the offline analyses** in the folder that holds the sensitivity exports.
   ```bash
   python scripts/fault_analysis.py "sensitivity-*.json"
   python scripts/sensitivity_analysis.py "sensitivity-*.json" --baselines-only
   python scripts/alpha_characterization.py "sensitivity-*.json" --baselines-only
   ```

   The committed files in `examples/` are enough to run `sensitivity_analysis.py` and `alpha_characterization.py` without re-running the pipeline.

---

## Versions

| Tag | Status |
|---|---|
| `v1.0.2` | Release cited in the thesis (Annex III), with SHA-256 hashes of the workflow, scripts and IFC inputs; documentation checked against the final thesis |
| `v1.0.1` | Earlier release with the same workflow, scripts and IFC files; documentation not yet complete |
| `v1.0-thesis` | Early test tag created before the repository was complete; not used for the thesis results |

---

## Scope and Limitations

This repository supports the experiments reported in the thesis and is not a general-purpose BIM validation or risk-management system. In particular:

- The corpus consists of eight public buildingSMART sample files, not project models.
- One building rule table is applied to both IFC 4 and IFC 4.3; infrastructure classes have no quality rule yet.
- IFC 4 files are assigned the building domain for the risk lookup tables, since IFC 4 has no infrastructure spatial entities.
- Pipeline A depends on the Windows-only DDC IFC Exporter.
- Lookup values, the 0.01% QTO agreement tolerance and the 95% coverage threshold are author-defined and were not swept.

The full discussion of assumptions and limitations is in Section 5.5 of the thesis.

---

## External Resources

| Resource | Link |
|---|---|
| buildingSMART Sample-Test-Files (corpus source) | [GitHub](https://github.com/buildingSMART/Sample-Test-Files) |
| DataDrivenConstruction CAD-to-data toolkit (Pipeline A converter and original workflows) | [GitHub](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN) |
| IfcOpenShell | [ifcopenshell.org](https://ifcopenshell.org) |
| n8n | [n8n.io](https://n8n.io) |

---

## Citation

Please cite the thesis:

> Rahmatillah, A. A. (2026). *Uncertainty-Aware Risk Screening from Imperfect Building Information Models: Schema Validation, Quantity Take-Off Robustness, and Explainable Risk Registers in an n8n Workflow* [MSc thesis, Universitat Politècnica de Catalunya]. International Master's in Risk Assessment and Management of Civil Infrastructures (NORISK).

and, when using the code, the software release:

> Rahmatillah, A. A. (2026). *n8n-thesis* (Version v1.0.2) [Computer software]. https://github.com/ulnirah/n8n-thesis

---

## Licence

No licence file is included yet. Until one is added, please contact the author through GitHub before reusing the code. The workflows in `workflows/ddc-base/` remain subject to DataDrivenConstruction's own licence terms.
