# Validation Ruleset

This document defines the IFC information-quality rules used by the thesis workflow to evaluate the data available for downstream BQI scoring.

The ruleset is an **external scoring layer** applied to extracted IFC data. It does not modify the IFC schema and does not attempt to certify general IFC compliance. Instead, it asks whether the information required by the thesis screening workflow is present and usable at the point of consumption.

The ruleset supports the four BQI dimensions:

- **D1 — Property completeness**
- **D2 — Property validity**
- **D3 — QTO coverage**
- **D4 — Cross-pipeline agreement**

D1–D3 are evaluated from the extracted element data. D4 is evaluated from the comparison between the two independent extraction pipelines.

---

## 1. Scope

The thesis evaluates:

- **IFC 4.0.2.1**, referred to as **IFC 4**
- **IFC 4.3.2.0**, referred to as **IFC 4.3**

IFC 2x3 is outside the scope of the study.

The ruleset is intended for the physical IFC element types relevant to the thesis screening workflow. Spatial hierarchy entities such as `IfcProject`, `IfcSite`, `IfcBuilding`, and infrastructure facility containers are handled separately from scored physical elements.

---

## 2. Validation Philosophy

The ruleset does not produce a single pass/fail result.

Instead, each applicable element is evaluated along several dimensions.

```text
IFC element
    │
    ├── Required properties ───────► D1 Completeness
    │
    ├── Property values ────────────► D2 Validity
    │
    ├── Expected quantities ────────► D3 QTO Coverage
    │
    └── Pipeline A vs Pipeline B ──► D4 Agreement
```

The resulting dimension scores are combined into the BQI according to the rules documented in `bqi-definition.md`.

This separation is intentional. A model can therefore be:

- structurally complete but semantically empty;
- rich in properties but poor in quantities;
- quantitatively complete but inconsistent between extraction tools; or
- broad in element coverage while carrying little usable information.

---

## 3. Rule Selection by IFC Category

Validation rules are associated with the IFC `Category` reported by the extraction pipelines.

Examples include:

```text
IfcWall
IfcSlab
IfcBeam
IfcColumn
IfcDoor
IfcWindow
IfcRoof
IfcSpace
```

For IFC 4.3 infrastructure models, the workflow can also encounter infrastructure-specific entities such as:

```text
IfcBridgePart
IfcBearing
IfcRoadPart
IfcCourse
IfcKerb
IfcPavement
IfcRail
IfcTrackElement
IfcFacilityPart
```

The parser detects the IFC schema before downstream scoring.

Schema-aware processing is required because IFC 4 and IFC 4.3 expose different domain-specific entity structures. The thesis therefore treats the schema identifier as part of the validation context rather than assuming that one universal rule table is appropriate for every IFC version.

---

# 4. Required Property Rules

D1 completeness is based on the required-property set assigned to an IFC category.

The current explicit required-property rules are:

| IFC Category | Required Properties |
|---|---|
| `IfcWall` | `IsExternal`, `LoadBearing` |
| `IfcWallStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcSlab` | `IsExternal`, `LoadBearing` |
| `IfcSlabStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcBeam` | `IsExternal`, `LoadBearing` |
| `IfcBeamStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcColumn` | `IsExternal`, `LoadBearing` |
| `IfcColumnStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcRoof` | `IsExternal` |
| `IfcDoor` | `IsExternal`, `FireRating` |
| `IfcWindow` | `IsExternal` |
| `IfcSpace` | `IsExternal`, `GrossPlannedArea` |

These properties were selected from the relevant IFC property-set definitions as the screening fields required by the thesis implementation.

They should not be interpreted as a claim that these are the only properties that can be validly present on the corresponding IFC entity.

---

## 5. Property Matching

Property names are stored by the extraction pipelines using a bracketed key format such as:

```text
[Pset_WallCommon] IsExternal
[Pset_WallCommon] LoadBearing
```

The validation logic compares the property name after the property-set prefix.

For example:

```text
[Pset_WallCommon] IsExternal
```

satisfies:

```text
IsExternal
```

The matching is exact after extraction of the property name.

This prevents accidental matches such as:

```text
Area
```

being treated as equivalent to:

```text
NetArea
```

---

# 6. D1 — Property Completeness

For an element `e`:

```text
D1 =
(|P_req| − |P_missing|)
-----------------------
|P_req|
```

where:

- `P_req` = required property set for the IFC category;
- `P_missing` = required properties not found with usable values.

Example:

```text
IfcWall
Required:
    IsExternal
    LoadBearing

Found:
    IsExternal
    LoadBearing

D1 = 2 / 2 = 1.000
```

If only one property is present:

```text
D1 = 1 / 2 = 0.500
```

---

# 7. D1 Fallback Rule

Not every IFC category has an explicit required-property table entry.

When no explicit rule exists, the implementation uses a conservative evidence-based fallback:

```text
IF element has any bracketed property/quantity data:
    D1 = 1.0
ELSE:
    D1 = 0.0
```

The purpose of this rule is to prevent an element from receiving a perfect score merely because the ruleset does not contain an explicit category-specific requirement.

An unsupported category is therefore not automatically treated as fully complete.

---

# 8. D2 — Property Validity

D2 evaluates whether extracted values are usable.

The property-key set is:

```text
K = all extracted bracketed property/quantity keys
```

Invalid values are those whose values are:

```text
empty string
null
UNSET
N/A
```

The score is:

```text
D2 =
(|K| − |K_invalid|)
-------------------
|K|
```

where `K_invalid` is the subset containing invalid values.

Example:

```text
Total extracted values = 7
Invalid values         = 1

D2 = (7 − 1) / 7
   = 0.857
```

An element with no extracted property data receives:

```text
D2 = 0.0
```

This prevents absence of evidence from being interpreted as valid information.

---

# 9. Validity of Special Values

The following values are explicitly treated as invalid:

| Value | Interpretation |
|---|---|
| `""` | Empty |
| `null` | Missing value |
| `UNSET` | IFC value unavailable / unset |
| `N/A` | Explicitly unavailable |

Values such as:

```text
0
false
0.0
```

remain valid values.

In particular, zero must not be confused with absence. This is important for numerical IFC properties and quantities where zero is a legitimate value.

---

# 10. Expected Quantity Rules

D3 QTO coverage uses an expected quantity set for each explicitly supported IFC category.

The current expected quantity rules are:

| IFC Category | Expected Quantity Fields |
|---|---|
| `IfcWall` | `NetVolume`, `Width`, `Length`, `NetSideArea` |
| `IfcWallStandardCase` | `NetVolume`, `Width`, `Length`, `NetSideArea` |
| `IfcSlab` | `NetVolume`, `Depth`, `NetArea` |
| `IfcSlabStandardCase` | `NetVolume`, `Depth`, `NetArea` |
| `IfcBeam` | `NetVolume`, `Length` |
| `IfcBeamStandardCase` | `NetVolume`, `Length` |
| `IfcColumn` | `NetVolume`, `Length` |
| `IfcColumnStandardCase` | `NetVolume`, `Length` |
| `IfcRoof` | `NetVolume` |
| `IfcSpace` | `NetFloorArea`, `GrossFloorArea`, `Height` |
| `IfcDoor` | `Area`, `Height`, `Width` |
| `IfcWindow` | `Area`, `Height`, `Width` |

These fields represent the quantity information selected for the thesis QTO and risk-screening use case. They are not intended to describe every possible quantity available in IFC.

---

# 11. Quantity Matching

Quantities are extracted using keys such as:

```text
[BaseQuantities] NetVolume
[Qto_WallBaseQuantities] NetVolume
```

For comparison and rule matching, the quantity-set prefix is removed.

Thus:

```text
[BaseQuantities] NetVolume
```

and:

```text
[Qto_WallBaseQuantities] NetVolume
```

are both normalised to:

```text
NetVolume
```

This allows semantically corresponding quantities to be compared across extraction pipelines even when their quantity-set names differ.

---

# 12. D3 — QTO Coverage

For an element `e`:

```text
D3 =
(|Q_exp| − |Q_missing|)
-----------------------
|Q_exp|
```

where:

- `Q_exp` = expected quantity fields for the IFC category;
- `Q_missing` = expected quantity fields not found.

Example:

```text
IfcWall

Expected:
    NetVolume
    Width
    Length
    NetSideArea

Present:
    NetVolume
    Width
    Length

D3 = 3 / 4 = 0.750
```

The quantity field must match exactly after normalisation.

For example:

```text
Expected: NetArea
Available: GrossArea
```

does not satisfy the expected field.

---

# 13. D3 Fallback Rule

For an IFC category with no explicit expected-QTO rule:

```text
IF element has any bracketed property/quantity data:
    D3 = 1.0
ELSE:
    D3 = 0.0
```

As with D1, the fallback prevents a missing rule definition from being interpreted as evidence of perfect quality.

---

# 14. Quantity Value Handling

Numeric quantity values are converted to numerical values before comparison.

A value of:

```text
0
```

is preserved as a valid numerical value.

The implementation therefore distinguishes:

```text
0
```

from:

```text
missing
```

or:

```text
null
```

This distinction is necessary because zero can be a legitimate quantity value.

---

# 15. D4 — Cross-Pipeline Agreement

D4 is not a conventional single-file validation rule.

It evaluates whether two independent extraction pipelines agree on comparable quantities.

The thesis uses:

```text
Pipeline A
DDC-based extraction

Pipeline B
IfcOpenShell extraction
```

Elements are matched using:

```text
GlobalId
```

For each shared element, quantity fields are normalised and compared.

---

## 15.1 Quantity Comparison Classes

For a quantity existing in both pipelines:

```text
Delta = Value_B − Value_A
```

and the relative difference is calculated against Pipeline A:

```text
PctDiff =
|Delta|
-------
|Value_A|
× 100
```

The comparison classification is:

| Condition | Classification |
|---|---|
| `|Delta| < 10^-10` | `exact` |
| `PctDiff < 0.01%` | `negligible` |
| `0.01% ≤ PctDiff < 1%` | `minor` |
| `PctDiff ≥ 1%` | `significant` |

For D4:

```text
exact
```

and:

```text
negligible
```

count as agreement.

The `minor` and `significant` classes count as disagreement.

The `1%` boundary therefore separates disagreement severity, while the `0.01%` boundary determines the operational agreement threshold.

---

# 16. D4 Calculation

For an element:

```text
D4 =
number of exact or negligible comparisons
------------------------------------------
total comparable quantity comparisons
```

For example:

```text
8 comparable quantity fields
6 exact/negligible
2 disagreement

D4 = 6 / 8
   = 0.750
```

---

## 16.1 No Comparison Rows

If no comparison rows are available for an element:

```text
IF quantities were expected:
    D4 = 0.5
ELSE:
    use the evidence-based fallback
```

The `0.5` value is a conservative middle score.

It represents:

> insufficient comparison evidence

rather than:

> complete agreement

This prevents an absence of comparison data from being interpreted as perfect cross-pipeline agreement.

---

# 17. Element Coverage

Element coverage is evaluated separately from D1–D4.

The workflow constructs the sets of `GlobalId` values from:

- Pipeline A; and
- Pipeline B.

The coverage measure is:

```text
Coverage =
shared GlobalIds
---------------
union of GlobalIds
× 100
```

The configured screening threshold is:

```text
95%
```

This measure is intentionally separate from BQI because an element that exists in one pipeline but not the other cannot receive a conventional element-level D4 comparison.

---

## 17.1 Coverage Severity

Missing elements are classified into three groups:

### Critical

Element categories whose absence can materially affect quantities or structural risk screening.

### Needs Review

Secondary or ambiguous categories where a mismatch should be investigated.

### Probably Harmless

Non-physical or annotation-level entities whose absence does not materially change the quantity or risk calculation.

Unknown types default conservatively to:

```text
needs_review
```

---

# 18. Elements Excluded from Scoring

The workflow excludes project and spatial hierarchy records from the element-level analysis.

Examples include:

```text
IfcProject
IfcSite
IfcBuilding
IfcBuildingStorey
IfcZone
IfcBridge
IfcRoad
IfcFacility
IfcRailway
```

These entities are useful for:

- schema detection;
- domain inference;
- spatial context; and
- infrastructure classification.

They are not treated as ordinary physical risk-screening elements.

---

# 19. Material Information

Material names are extracted by Pipeline B and retained in the element data.

Material information is not itself a BQI dimension.

Instead, it is consumed downstream by the risk-screening model as a modifier of susceptibility.

Therefore:

```text
Material presence
    ≠
automatic BQI penalty
```

The absence of a readable material is recorded as a diagnostic penalty in the current workflow, but material itself is not one of the four BQI scoring dimensions.

---

# 20. Schema and Domain Detection

The workflow detects:

```text
IFC schema
```

from parser metadata.

For IFC 4.3, characteristic entity and spatial types are then used to infer the domain:

```text
Building
Bridge
Road
Rail
Mixed
Unknown
```

Examples of domain indicators include:

### Rail

```text
IfcRail
IfcTrackElement
IfcRailway
```

### Road

```text
IfcPavement
IfcKerb
IfcRoadPart
IfcRoad
```

### Bridge

```text
IfcBearing
IfcDeepFoundation
IfcBridgePart
IfcBridge
```

### Building

```text
IfcBuilding
IfcWall
IfcSlab
```

A model containing indicators from more than one domain is classified as:

```text
Mixed
```

when the detection logic identifies multiple domain matches.

---

# 21. Relationship Between Validation and BQI

The validation rules produce the evidence used by BQI.

```text
Validation rules
       │
       ├── Required properties ──► D1
       ├── Value usability ──────► D2
       ├── Expected QTO ─────────► D3
       └── Pipeline comparison ──► D4
                                │
                                ▼
                              BQI
```

The BQI calculation and weighting are documented separately in:

`docs/bqi-definition.md`

This separation is intentional. The validation rules describe the evidence being measured, while the BQI document defines how those measurements are combined.

---

# 22. Rule Coverage

The explicit `REQUIRED_PROPS` and `EXPECTED_QTO` tables currently cover twelve IFC categories:

```text
IfcWall
IfcWallStandardCase
IfcSlab
IfcSlabStandardCase
IfcBeam
IfcBeamStandardCase
IfcColumn
IfcColumnStandardCase
IfcRoof
IfcDoor
IfcWindow
IfcSpace
```

Other IFC categories can still be processed by the workflow, but they rely on the documented fallback behaviour when no explicit completeness or QTO rule exists.

This is a deliberate limitation of the current implementation rather than an assumption that unsupported categories are irrelevant.

---

# 23. Parameter Provenance

| Rule / Parameter | Value / Definition | Provenance |
|---|---|---|
| IFC schemas | IFC 4.0.2.1 / IFC 4.3.2.0 | Study scope |
| Required-property membership | Per IFC Category | Author-defined selection from schema-defined property sets |
| Expected-QTO membership | Per IFC Category | Author-defined selection from schema-defined quantity sets |
| Invalid values | Empty, null, UNSET, N/A | Implementation rule |
| D1 fallback | 1.0 if data present, otherwise 0.0 | Author-defined conservative convention |
| D3 fallback | 1.0 if data present, otherwise 0.0 | Author-defined conservative convention |
| D4 fallback | 0.5 when comparison is expected but unavailable | Author-defined conservative convention |
| Exact tolerance | `10^-10` | Fixed implementation constant |
| Negligible threshold | `0.01%` | Fixed implementation constant |
| Significant threshold | `1%` | Fixed implementation constant |
| Coverage threshold | `95%` | Author-defined screening convention |

These parameters are version-controlled with the workflow.

---

# 24. Limitations

The validation ruleset should be interpreted as a **purpose-specific screening ruleset**, not a universal IFC compliance validator.

### Rule coverage is incomplete

Only twelve IFC categories have explicit D1 and D3 rule tables.

### Extractable quality is not fitness-for-purpose

A high score means that the information required by this downstream workflow is present and usable. It does not prove that the original authoring model was correct or that the model is fit for every other application.

### Fallback behaviour can limit fault detectability

A fault targeting a property or quantity outside the explicit rule tables may have little or no effect on BQI.

### Quantity-name matching is intentionally strict

Semantically related but differently named quantities can remain unmatched.

### Coverage is separate from BQI

An element absent from one pipeline is not scored as a normal shared element, so breadth differences must be examined through the coverage instrument.

---

# 25. Repository Implementation

The validation logic is implemented primarily in:

`workflows/thesis/n8n_ifc_dual_pipeline.json`

Key workflow stages include:

```text
2.5: Detect domain
2.6: Filter elements
3.2: QTO comparison
3.3: Coverage Analysis
3.4: BQI Scoring
3.5: SRCC Analysis
```

The extracted IFC data used by Pipeline B are produced by:

`scripts/extract_ifc.py`

The corresponding BQI and risk calculations are externalised in the version-controlled workflow rather than embedded in the IFC files themselves.

---

# 26. Verification

The repository's verification scripts can be used to check the consistency of the exported scoring data.

In particular, the exported element-level scores should support reconstruction of:

```text
D1
D2
D3
D4
BQI_element
BQI_model
```

The fault-analysis workflow then evaluates whether controlled information defects produce the expected change in the measured dimensions.

The validation ruleset should therefore be treated as part of the measurement instrument and versioned together with the workflow.

---

## Canonical Sources

The methodological definition of the validation rules appears in:

- **Thesis Chapter 3, Section 3.3 — BQI**
- **Section 3.3.4 — Schema-Conditional Rule Selection**
- **Annex I — BQI Rule Tables**

The corresponding executable implementation is:

`workflows/thesis/n8n_ifc_dual_pipeline.json`

The rules in this document should remain synchronized with the workflow and with the repository release associated with the final thesis.
