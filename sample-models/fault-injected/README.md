# Fault-Injected IFC Models

This folder contains **derived IFC variants generated from the baseline corpus** for the fault-injection and robustness experiments reported in the thesis.

Fault injection is performed on the seven valid baseline models **M1–M7**. The negative-control model **M8** is excluded from fault injection because it contains zero property and quantity data and is analysed separately.

Fault variants are generated programmatically using:

`scripts/fault_injection.py`

The purpose of the fault-injected corpus is to evaluate whether the BIM Quality Index (BQI) responds detectably, monotonically, and selectively to controlled information defects.

---

## Fault Taxonomy

The thesis uses six controlled fault types:

| Fault | Description | Primary Target |
|---|---|---|
| **F1** | Mandatory property deletion | D1: Property completeness |
| **F2** | Value emptying to `UNSET` | D1 and D2: Completeness and validity |
| **F3** | Quantity field deletion | D3: QTO coverage |
| **F4** | Quantity magnitude perturbation by +10% | D4: Cross-pipeline agreement |
| **F5** | Property-set deletion | D1 and D2 |
| **F6** | Element deletion | Element coverage |

### F1 — Mandatory Property Deletion

Removes mandatory properties from selected target elements.

The mandatory properties used by the experiment are:

- `IsExternal`
- `LoadBearing`
- `FireRating`
- `GrossPlannedArea`

F1 is intended primarily to reduce **D1 (property completeness)**.

### F2 — Value Emptying to `UNSET`

Sets selected property values to `UNSET`.

This defect affects both completeness and validity because the property slot remains present but contains no usable value. It therefore targets **D1 and D2**.

### F3 — Quantity Field Deletion

Removes a quantity field from the quantity set of selected elements.

F3 targets **D3 (QTO coverage)**.

### F4 — Quantity Magnitude Perturbation

Perturbs quantity magnitudes by **+10%**.

The perturbation is applied to quantity attributes including:

- `VolumeValue`
- `AreaValue`
- `LengthValue`
- `CountValue`
- `WeightValue`
- `TimeValue`

F4 targets **D4 (cross-pipeline agreement)**.

### F5 — Property-Set Deletion

Removes an entire property set and its associated relation.

F5 is a broader property defect than F1 and affects **D1 and D2**.

### F6 — Element Deletion

Removes the selected element completely.

F6 targets **element coverage**, rather than a specific BQI dimension.

---

## Severity Levels

Three injection severities are used:

| Severity | Injection Rate |
|---|---:|
| Light | 10% |
| Intermediate | 25% |
| Substantial | 50% |

The severity controls the **fraction of eligible elements affected**.

Target elements are sampled uniformly using **random seed 42**, after deterministic ordering by `GlobalId`.

---

## Eligible Elements

Fault injection is restricted to the IFC entity types covered by the experimental injection population:

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

`IfcElementAssembly` is not included in the injection-eligible population.

---

## Single-File and Dual-File Configurations

Most fault variants use a **single-file configuration**, where the same faulted IFC file is processed by both extraction pipelines.

This applies to:

- F1
- F2
- F3
- F5
- F6

F4 is also evaluated in a single-file configuration. In that case, both pipelines receive the same perturbed quantities, so cross-pipeline disagreement is not observable and the BQI remains unchanged by construction.

### Dual-file experiments

F4 and F6 are additionally evaluated using a **dual-file configuration**:

```text
Pipeline A → original baseline IFC
Pipeline B → fault-injected IFC variant
```

This configuration is required to expose differences between the two independent data consumers.

For F4, this allows the quantity perturbation to manifest through **D4**.

For F6, the dual-file configuration allows the effect on **element coverage** to be examined across the two pipelines.

---

## Fault-Injection Intensity

The reported experiments use **light mode** as the default injection intensity.

For F1, F2, and F3:

- light mode modifies one matching field per target element;
- heavy mode modifies all matching fields.

For F4, all quantity values of a targeted element are perturbed.

For F5, exactly one property set is removed.

For F6, the entire element is removed.

The severity levels therefore increase the **number of affected elements**, rather than increasing the depth of the modification applied to each element.

---

## Experimental Coverage

The seven valid models are evaluated across:

**7 models × 6 fault types × 3 severity levels = 126 single-file variants**

F4 and F6 also have additional dual-file runs across all seven valid models.

The complete fault-analysis workflow checks BQI behaviour across the resulting model × fault × configuration combinations.

The deepest per-dimension fault analysis in the thesis focuses on **M1**, which has the healthiest baseline information content and therefore provides the clearest manifestation of the injected defects.

---

## Traceability

Each generated fault variant is accompanied by a manifest containing the information required to reproduce and audit the injection, including:

- baseline model;
- fault type;
- injection rate;
- random seed;
- selected target elements; and
- changes applied.

The corresponding fault-injection manifests are documented in:

**Thesis Annex IV — Fault Injection Manifests**

---

## Important Note

These files are **derived experimental inputs**, not independent source models.

They should always be interpreted together with:

- the corresponding baseline IFC model;
- `scripts/fault_injection.py`;
- the recorded injection manifest; and
- the n8n workflow configuration defining how the variant is assigned to the extraction pipelines.

The baseline IFC files remain unchanged.

---

## Reproducibility

The fault-injected corpus can be regenerated from the baseline models using the version-controlled injection script.

Example:

```bash
python scripts/fault_injection.py model.ifc --fault F1 --rate 0.25 --seed 42 --outdir faulted
```

To generate all six fault types:

```bash
python scripts/fault_injection.py model.ifc --all --seed 42 --outdir faulted
```

The generated variants and their manifests provide the controlled experimental inputs used to evaluate BQI detection, monotonicity, selectivity, and downstream robustness.
