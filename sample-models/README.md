# Sample Models

This folder contains the IFC model corpus used in the thesis experiments.

The corpus consists of eight models selected from the official **buildingSMART Sample Test Files** repository:

- **M1–M7**: valid models used for baseline characterisation, QTO comparison, fault injection, sensitivity analysis, and risk-screening evaluation.
- **M8**: a deliberately retained negative-control model with zero property and quantity data, used to demonstrate the distinction between model breadth (element coverage) and data depth (information quality).

All corpus files were retrieved in 2026. The thesis records the corresponding source commit information and SHA-256 file hashes in **Annex III: Corpus Provenance**.

---

## Corpus Selection

The corpus was selected from the official buildingSMART Sample Test Files repository because the files are:

- openly accessible and citable;
- intended as reference examples of IFC schema use; and
- available in matched IFC 4 / IFC 4.3 design pairs.

The initial screening considered **18 candidate files** using two inclusion criteria:

1. property count > 0; and
2. quantity count > 0.

Seven models satisfied both criteria and were retained as the valid experimental corpus (M1–M7).

One additional model, **M8**, did not satisfy the inclusion criteria because it contains zero property and zero quantity data. Rather than discarding it, the model was intentionally retained as a **negative control** for the breadth–depth analysis.

---

## Model Inventory

| ID | File / Model | IFC Schema | Domain | Elements | Properties | Quantities | Role |
|---|---|---|---|---:|---:|---:|---|
| **M1** | Building-Architecture | IFC 4.0.2.1 (IFC 4) | Building | 14 | 62 | 25 | Valid experimental model |
| **M2** | Building-Architecture | IFC 4.3.2.0 (IFC 4.3) | Building | 14 | 30 | 25 | Valid experimental model |
| **M3** | Building-Structural | IFC 4.0.2.1 (IFC 4) | Building | 16 | 65 | 34 | Valid experimental model |
| **M4** | Building-Structural | IFC 4.3.2.0 (IFC 4.3) | Building | 16 | 34 | 34 | Valid experimental model |
| **M5** | Infra-Bridge | IFC 4.0.2.1 (IFC 4) | Bridge | 57 | 48 | 27 | Valid experimental model |
| **M6** | Infra-Bridge | IFC 4.3.2.0 (IFC 4.3) | Bridge | 68 | 27 | 27 | Valid experimental model |
| **M7** | Infra-Road | IFC 4.0.2.1 (IFC 4) | Road | 55 | 174 | 78 | Valid experimental model |
| **M8** | Infra-Road | IFC 4.3.2.0 (IFC 4.3) | Road | 81 | 0 | 0 | Negative control |

The element count reported here refers to **valued elements**, meaning elements whose IFC type is covered by the thesis scoring rules.

The property count represents the extracted property-key namespace used by the pipeline, including keys originating from both `IfcPropertySet` and `IfcElementQuantity`.

---

## IFC 4 / IFC 4.3 Design Pairs

The corpus deliberately contains four matched design pairs across IFC 4 and IFC 4.3:

| Design | IFC 4 | IFC 4.3 |
|---|---|---|
| Building-Architecture | M1 | M2 |
| Building-Structural | M3 | M4 |
| Infra-Bridge | M5 | M6 |
| Infra-Road | M7 | M8 |

This pairing allows schema-version comparisons while keeping the underlying design domain consistent.

The comparison also revealed substantial differences in information content between some IFC 4 and IFC 4.3 variants. These differences are treated as properties of the source models rather than as extraction artefacts.

---

## Baseline Models

The baseline models are the original, unmodified buildingSMART IFC files.

They form the reference state for:

- dual-pipeline extraction;
- QTO comparison;
- BQI calculation;
- risk screening;
- fault-injection experiments; and
- sensitivity analysis.

Baseline files must remain unchanged throughout the experiments. Faulted variants are generated separately from the baseline inputs so that each experimental condition can be traced back to a known reference model.

The exact original **bSI filenames**, repository provenance, commit information, and SHA-256 hashes are documented in **Annex III: Corpus Provenance** of the thesis.

---

## Fault-Injected Models

Fault injection is performed on the **seven valid models, M1–M7**.

The negative control **M8 is excluded from fault injection** because its zero property and quantity content would prevent several fault mechanisms from manifesting. M8 is instead analysed separately as a breadth–depth negative control.

The fault taxonomy contains six controlled defect classes:

| Fault | Description | Primary Target |
|---|---|---|
| **F1** | Mandatory property deletion | D1: property completeness |
| **F2** | Value emptying to `UNSET` | D1 and D2: completeness and validity |
| **F3** | Quantity field deletion | D3: QTO coverage |
| **F4** | Quantity magnitude perturbation by +10% | D4: cross-pipeline agreement |
| **F5** | Property-set deletion | D1 and D2 |
| **F6** | Element deletion | Element coverage |

The fault variants are generated programmatically using:

`scripts/fault_injection.py`

---

## Fault Severity

Three injection severities are used:

| Severity | Injection Rate |
|---|---:|
| Light | 10% |
| Intermediate | 25% |
| Substantial | 50% |

The injection rate represents the fraction of eligible target elements affected.

Target elements are sampled uniformly using a **fixed random seed (42)** after deterministic ordering by `GlobalId`.

The injection-eligible population covers the sixteen IFC entity types defined in the thesis methodology:

- `IfcWall`
- `IfcWallStandardCase`
- `IfcSlab`
- `IfcSlabStandardCase`
- `IfcBeam`
- `IfcBeamStandardCase`
- `IfcColumn`
- `IfcColumnStandardCase`
- `IfcRoof`
- `IfcDoor`
- `IfcWindow`
- `IfcSpace`
- `IfcStair`
- `IfcStairFlight`
- `IfcFooting`
- `IfcPile`

`IfcElementAssembly` is not part of the injection-eligible population.

---

## Fault Configuration

Two experimental configurations are used.

### Single-file configuration

For **F1, F2, F3, F5, and F6**, the faulted IFC file is supplied to both extraction pipelines.

For F4 in a single-file configuration, both pipelines also receive the same perturbed quantities. Consequently, both pipelines observe the same values and no cross-pipeline disagreement is produced.

### Dual-file configuration

**F4 and F6 are additionally evaluated using a dual-file configuration.**

In this configuration:

- Pipeline A receives the original baseline IFC file.
- Pipeline B receives the fault-injected variant.

This isolates disagreement between the two independent data consumers.

The dual-file configuration is essential for exposing the intended D4 response to F4. F6 is also evaluated in this configuration to examine its effect on element coverage across the two pipelines.

---

## Fault Injection Intensity

The default injection mode used for the reported results is **light mode**.

For F1, F2, and F3:

- light mode changes one matching field per target element;
- heavy mode changes all matching fields.

For F4, every quantity value of the targeted element is perturbed by construction.

For F5, exactly one property set is removed.

For F6, the complete element is removed.

The three severity levels therefore control the **number of affected elements**, rather than the depth of alteration within an individual element.

---

## Experimental Coverage

The seven valid models receive the full fault-injection evaluation:

**7 models × 6 fault types × 3 severity levels = 126 single-file fault variants**

The dual-file F4 and F6 configurations are additionally run across all seven valid models.

The deepest fault-response decomposition is presented for **M1**, which has the healthiest baseline information content and therefore provides the clearest manifestation of the injected defects.

M8 is not part of the fault-injection benchmark.

---

## Traceability

Each generated fault variant is accompanied by provenance information sufficient to identify:

- baseline model;
- fault type;
- injection rate;
- random seed;
- selected target elements; and
- modifications applied.

Fault-injection manifests are documented in **Annex IV: Fault Injection Manifests** of the thesis.

The general computational chain is:

**Baseline IFC → fault injection → dual extraction → QTO comparison → BQI → risk screening → analysis**

---

## Derived Files

The IFC files are the primary corpus inputs.

Other files generated during processing, such as:

- DDC-generated XLSX files;
- Pipeline B JSON extraction files;
- fault-injection manifests; and
- analysis exports

are treated as **derived computational artefacts**.

They can be regenerated from the versioned IFC inputs and repository scripts/workflows and are therefore not treated as independent source models.

Representative final outputs are provided separately under [`../examples/`](../examples/).

---

## Reproducibility

The baseline corpus, fault-injection methodology, workflow definition, and analysis scripts together define the reproducible experimental environment.

For the final thesis release, the repository should preserve the exact versioned state used for the reported experiments through the corresponding Git commit and release tag.
