# Baseline IFC Models

This folder contains the **clean, unmodified IFC models** used as reference inputs for the thesis computational experiments.

The corpus consists of eight buildingSMART sample models, identified in the thesis as **M1–M8**. Seven models (M1–M7) form the valid experimental corpus, while M8 is retained as a **negative control** because it contains zero property and quantity data.

All baseline models originate from the official [buildingSMART Sample Test Files](https://github.com/buildingSMART/Sample-Test-Files) repository.

---

## Corpus Inventory

| ID | Model | IFC Schema | Domain | Role |
|---|---|---|---|---|
| **M1** | Building-Architecture | IFC 4.0.2.1 | Building | Valid experimental model |
| **M2** | Building-Architecture | IFC 4.3.2.0 | Building | Valid experimental model |
| **M3** | Building-Structural | IFC 4.0.2.1 | Building | Valid experimental model |
| **M4** | Building-Structural | IFC 4.3.2.0 | Building | Valid experimental model |
| **M5** | Infra-Bridge | IFC 4.0.2.1 | Bridge | Valid experimental model |
| **M6** | Infra-Bridge | IFC 4.3.2.0 | Bridge | Valid experimental model |
| **M7** | Infra-Road | IFC 4.0.2.1 | Road | Valid experimental model |
| **M8** | Infra-Road | IFC 4.3.2.0 | Road | Negative control |

The eight models form four matched IFC 4 / IFC 4.3 design pairs:

- **M1 / M2** — Building-Architecture
- **M3 / M4** — Building-Structural
- **M5 / M6** — Infra-Bridge
- **M7 / M8** — Infra-Road

---

## Model Selection

The thesis initially screened 18 candidate buildingSMART sample files using two inclusion criteria:

1. property count > 0; and
2. quantity count > 0.

Seven models satisfied these criteria and were retained as the valid experimental corpus (M1–M7).

**M8** did not satisfy the criteria because it contains zero property and zero quantity data. It was intentionally retained as a negative control for the breadth–depth analysis rather than discarded.

---

## Baseline Counts

| ID | Elements | Properties | Quantities |
|---|---:|---:|---:|
| M1 | 14 | 62 | 25 |
| M2 | 14 | 30 | 25 |
| M3 | 16 | 65 | 34 |
| M4 | 16 | 34 | 34 |
| M5 | 57 | 48 | 27 |
| M6 | 68 | 27 | 27 |
| M7 | 55 | 174 | 78 |
| M8 | 81 | 0 | 0 |

The element count refers to **valued elements**, meaning elements whose IFC type is covered by the thesis scoring rules.

Property and quantity counts correspond to the extracted baseline data used by the thesis pipeline.

---

## Use in the Thesis

The baseline models provide the reference inputs for:

- dual-pipeline IFC extraction;
- quantity take-off comparison;
- BIM Quality Index (BQI) calculation;
- risk screening;
- fault-injection experiments;
- parameter sensitivity analysis; and
- baseline report generation.

M1–M7 are used for the full experimental evaluation.

M8 is **not fault-injected** and is analysed separately as the negative-control case.

---

## Provenance

The thesis records the provenance of each source model, including the corresponding buildingSMART repository information and **SHA-256 file hash**, in:

**Annex III — Corpus Provenance**

The baseline IFC files in this folder should remain **unchanged** throughout the experiments. Fault-injected variants are generated separately under [`../fault-injected/`](../fault-injected/).

Keeping the baseline files immutable ensures that every derived experiment can be traced back to the same reference inputs.
