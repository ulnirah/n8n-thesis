# Examples

This folder contains only the **baseline** outputs of the thesis workflow: one explainable risk register (HTML) and one per-element sensitivity dataset (JSON) for each of the eight corpus models. No outputs from fault-injected runs are included.

They let you see what the workflow produces and run the offline analyses without installing n8n or the DDC converter. The full fault-injection campaign is not stored here; it can be regenerated (see [Relationship to the Full Experiment](#relationship-to-the-full-experiment)).

---

## Files

| Model | Design | Risk register | Sensitivity dataset |
|---|---|---|---|
| M1 | IFC 4 · Building Architecture | `risk-register-IFC4-Building-Architecture-2026-07-31-00-53.html` | `sensitivity-IFC4-Building-Architecture.json` |
| M2 | IFC 4.3 · Building Architecture | `risk-register-IFC43-Building-Architecture-2026-07-31-00-53.html` | `sensitivity-IFC43-Building-Architecture.json` |
| M3 | IFC 4 · Building Structural | `risk-register-IFC4-Building-Structural-2026-07-31-00-53.html` | `sensitivity-IFC4-Building-Structural.json` |
| M4 | IFC 4.3 · Building Structural | `risk-register-IFC43-Building-Structural-2026-07-31-00-52.html` | `sensitivity-IFC43-Building-Structural.json` |
| M5 | IFC 4 · Infrastructure Bridge | `risk-register-IFC4-Infra-Bridge-2026-07-31-00-52.html` | `sensitivity-IFC4-Infra-Bridge.json` |
| M6 | IFC 4.3 · Infrastructure Bridge | `risk-register-IFC43-Infra-Bridge-2026-07-31-00-51.html` | `sensitivity-IFC43-Infra-Bridge.json` |
| M7 | IFC 4 · Infrastructure Road | `risk-register-IFC4-Infra-Road-2026-07-31-00-51.html` | `sensitivity-IFC4-Infra-Road.json` |
| M8 | IFC 4.3 · Infrastructure Road | `risk-register-IFC43-Infra-Road-2026-07-31-00-55.html` | `sensitivity-IFC43-Infra-Road.json` |

M8 is the negative control: all its elements are found by both pipelines, but none carries property or quantity data.

---

## Baseline Results

Figures as printed in the committed reports:

| Model | Model BQI | Element coverage | High | Medium | Elements scored | Verdict |
|---|---:|---|---:|---:|---:|---|
| M1 | 0.471 | 77.78% · FAIL | 1 | 1 | 14 | DATA UNRELIABLE |
| M2 | 0.350 | 77.78% · FAIL | 1 | 3 | 14 | DATA UNRELIABLE |
| M3 | 0.561 | 88.89% · REVIEW | 1 | 8 | 16 | DATA UNRELIABLE |
| M4 | 0.413 | 88.89% · REVIEW | 1 | 8 | 16 | DATA UNRELIABLE |
| M5 | 0.281 | 100% · PASS | 0 | 18 | 57 | DATA UNRELIABLE |
| M6 | 0.140 | 100% · PASS | 0 | 25 | 68 | DATA UNRELIABLE |
| M7 | 0.462 | 100% · PASS | 0 | 6 | 55 | DATA UNRELIABLE |
| M8 | 0.000 | 100% · PASS | 16 | 42 | 81 | DATA UNRELIABLE |

Every model is DATA UNRELIABLE because every model BQI is below the MEDIUM boundary of 0.60. The thesis reports these results in Chapter 4 (Tables 4.1 and 4.9).

---

## What a Risk Register Contains

Open any HTML file in a web browser. Each report has four parts (thesis Section 3.7.4 and Annex VI):

1. **Overview:** screening verdict with its reasons, headline figures, and a recommended action derived from fixed rules.
2. **Risk screening results:** elements ranked on `R_adj`, with `R_lower`, `R_raw`, `R_adj`, band width and High/Medium/Low label.
3. **Data quality evidence:** BQI dimensions per element and the missing properties and quantities.
4. **Pipeline cross-check:** element coverage by severity class, quantity comparison and SRCC between the two pipelines.

The screenshots in thesis Figure 4.4 come from an earlier run of M8 and M5 (12 July 2026) and show the same figures as these files.

---

## What a Sensitivity Dataset Contains

Each JSON file is a list with one object per scored element:

| Field | Meaning |
|---|---|
| `GlobalId` | IFC element identifier |
| `Category` | IFC entity type |
| `score_completeness` | D1 |
| `score_validity` | D2 |
| `score_qto_coverage` | D3 |
| `score_qto_agreement` | D4 |
| `likelihood_score` | Likelihood proxy `L` |
| `consequence_score` | Consequence proxy `C` |

The BQI, `R_raw`, the uncertainty band and the labels are not stored; they are recomputed from these fields by the analysis scripts, so the effect of different weights or α can be tested offline.

---

## Using the Examples

Run from this folder, with Python 3 (standard library only):

```bash
python ../scripts/sensitivity_analysis.py "sensitivity-*.json" --baselines-only
python ../scripts/alpha_characterization.py "sensitivity-*.json" --baselines-only
python ../scripts/verify_exports.py .
```

`alpha_characterization.py` on these files reproduces the admissible interval [0.10, 1.00] and the recommended α = 0.55 reported in the thesis (Sections 3.6.4 and 4.4.2). `fault_analysis.py` needs the faulted-run exports as well, so it can only be run after regenerating the campaign.

---

## Reading Notes

- **Coverage on the building models.** The unmatched elements behind the FAIL on M1/M2 (IfcSpace, IfcSpatialZone, IfcFurniture) and the REVIEW on M3/M4 (IfcDiscreteAccessory) are types that Pipeline B does not extract. See [`../docs/validation-ruleset.md`](../docs/validation-ruleset.md), Section 17.3.
- **Consequence values.** No corpus element carries the quantity fields read for the extent term, so every `consequence_score` equals `0.7 × criticality`. See [`../docs/risk-rules-table.md`](../docs/risk-rules-table.md), Section 4.1.
- **SRCC on M8.** The report shows `N/A`, because M8 has no quantity values to rank.
- **D4 values.** `score_qto_agreement` is computed over all of an element's bracketed fields, including non-numeric properties. See [`../docs/bqi-definition.md`](../docs/bqi-definition.md), Sections 4.4 and 12.6.

---

## Relationship to the Full Experiment

These files cover the eight baselines only. The full campaign adds outputs for six fault types at three severities (10%, 25%, 50%) on the seven valid models:

| Fault | Mutation | Targeted instrument |
|---|---|---|
| F1 | Remove a required property | D1 |
| F2 | Blank a property value to UNSET | D1 + D2 |
| F3 | Remove a quantity field | D3 |
| F4 | Perturb quantity magnitudes by +10% | D4 |
| F5 | Remove an entire property set | D1 + D2 |
| F6 | Delete whole elements | Element coverage |

| Configuration | Runs |
|---|---:|
| Baseline | 8 |
| Single file: F1, F2, F3, F5 | 84 |
| Single file: F4, F6 | 42 |
| Dual file: F4, F6 | 42 |
| **Total** | **176** |

The faulted IFC files are in [`../sample-models/fault-injected/`](../sample-models/fault-injected/). The workflow, scripts and experimental design in this repository are sufficient to regenerate every output.

---

## Naming Convention

```text
risk-register-<model>-<YYYY-MM-DD-HH-MM>.html
sensitivity-<model>.json
```

The timestamp identifies the workflow execution that produced the report; all committed reports come from the runs of 31 July 2026.

Faulted runs are not included in this folder. When the campaign is regenerated, their sensitivity exports carry the fault identifier in the model name, which `scripts/fault_analysis.py` uses to pair each run with its baseline:

```text
sensitivity-<model>__F1-r10-s42.json                          single-file run
sensitivity-<model>__F4-r25-s42_PIPELINE-B-ONLY.json          F4/F6 variant, single-file run
sensitivity-<model>__F4-r25-s42_PIPELINE-B-ONLY_DUALFILE.json F4/F6 variant, dual-file run
```

This folder describes repository release `v1.0.2`.
