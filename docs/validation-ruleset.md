# Validation Ruleset

This document defines the IFC information-quality rules the thesis workflow applies to extracted data before BQI scoring.

The ruleset is an **external scoring layer**. It does not modify the IFC schema and does not certify general IFC compliance. It asks whether the information the screening workflow needs is present and usable at the point of consumption.

It supports the four BQI dimensions:

- **D1 — Property completeness**
- **D2 — Property validity**
- **D3 — QTO coverage**
- **D4 — Cross-pipeline agreement**

D1–D3 are evaluated on each element's extracted data. D4 is evaluated on the comparison between the two extraction pipelines. Element coverage is a separate check (Section 17).

---

## 1. Scope

The thesis evaluates **IFC 4.0.2.1** (IFC 4) and **IFC 4.3.2.0** (IFC 4.3). IFC 2x3 is out of scope.

The rules apply to physical IFC elements. Spatial hierarchy entities such as `IfcProject`, `IfcSite`, `IfcBuilding` and infrastructure facility containers are removed before scoring (Section 18).

---

## 2. Validation Philosophy

The ruleset does not produce a single pass/fail result. Each element is evaluated along several dimensions:

```text
IFC element
    │
    ├── Required properties ───────► D1 Completeness
    ├── Property values ────────────► D2 Validity
    ├── Expected quantities ────────► D3 QTO Coverage
    └── Pipeline A vs Pipeline B ──► D4 Agreement
```

The dimension scores are combined into the BQI as documented in [`bqi-definition.md`](bqi-definition.md).

Keeping the dimensions separate means a model can be:

- broad in element coverage but empty of information;
- rich in properties but poor in quantities;
- complete in quantities but inconsistent between extraction tools.

---

## 3. Rule Selection by IFC Category

Rules are selected by the IFC `Category` reported by the extraction pipelines, for example `IfcWall`, `IfcSlab`, `IfcBeam`, `IfcColumn`, `IfcDoor`, `IfcWindow`, `IfcRoof` and `IfcSpace`.

IFC 4.3 infrastructure models also contain infrastructure entities such as `IfcBridgePart`, `IfcBearing`, `IfcRoadPart`, `IfcCourse`, `IfcKerb`, `IfcPavement`, `IfcRail`, `IfcTrackElement` and `IfcFacilityPart`. These have no explicit quality rules and are scored through the fallback rules.

The parser detects the IFC schema before downstream scoring. In the thesis release, the same rule table is applied to IFC 4 and IFC 4.3 models; the schema identifier selects the spatial types used in extraction and the domain used for the risk lookup tables (Section 20). Schema-specific rule tables for infrastructure entities are further work.

---

## 4. Required Property Rules

| IFC Category | Required Properties |
|---|---|
| `IfcWall`, `IfcWallStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcSlab`, `IfcSlabStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcBeam`, `IfcBeamStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcColumn`, `IfcColumnStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcRoof` | `IsExternal` |
| `IfcDoor` | `IsExternal`, `FireRating` |
| `IfcWindow` | `IsExternal` |
| `IfcSpace` | `IsExternal`, `GrossPlannedArea` |

These properties were selected from the corresponding `Pset_*Common` definitions as the fields the screening workflow needs. They are not the only properties an entity can validly carry.

---

## 5. Property Matching

The extraction pipelines store properties and quantities as bracketed keys:

```text
[Pset_WallCommon] IsExternal
[Qto_WallBaseQuantities] NetVolume
```

D1 and D3 match the name after the bracketed set prefix and the following space, exactly:

- `[Pset_WallCommon] IsExternal` satisfies `IsExternal`.
- `Area` does not match `NetArea`, and `GrossArea` does not match `NetArea`.

A required field counts as present only if its value is not empty and not null. Matching looks at every bracketed key of the element, whichever property or quantity set it comes from.

---

## 6. D1 — Property Completeness

```text
D1 = (|P_req| − |P_missing|) / |P_req|
```

- `P_req` = required properties for the IFC category
- `P_missing` = required properties absent, or present with an empty value

Example: `IfcWall` requires `IsExternal` and `LoadBearing`. If both are present, `D1 = 2 / 2 = 1.000`; if one is present, `D1 = 1 / 2 = 0.500`.

---

## 7. D1 Fallback Rule

For a category with no explicit required-property rule:

```text
IF the element has any bracketed property or quantity key:
    D1 = 1.0
ELSE:
    D1 = 0.0
```

This prevents an element from receiving a perfect score merely because no rule exists for its category.

---

## 8. D2 — Property Validity

```text
K  = all bracketed property and quantity keys of the element
D2 = (|K| − |K_invalid|) / |K|
```

`K_invalid` contains the keys whose value is invalid (Section 9).

Example: 7 keys, 1 invalid → `D2 = 6 / 7 = 0.857`.

An element with no bracketed keys receives `D2 = 0.0`, so absence of evidence is not treated as valid information.

---

## 9. Invalid and Valid Values

| Value | Treated as |
|---|---|
| `""` (empty string) | Invalid |
| `null` or missing | Invalid |
| `UNSET` (also `['UNSET']` as exported by IfcOpenShell) | Invalid |
| `N/A` | Invalid |
| `0`, `0.0`, `false` | Valid |

Zero and false are legitimate values and are not confused with absence.

---

## 10. Expected Quantity Rules

| IFC Category | Expected Quantity Fields |
|---|---|
| `IfcWall`, `IfcWallStandardCase` | `NetVolume`, `Width`, `Length`, `NetSideArea` |
| `IfcSlab`, `IfcSlabStandardCase` | `NetVolume`, `Depth`, `NetArea` |
| `IfcBeam`, `IfcBeamStandardCase` | `NetVolume`, `Length` |
| `IfcColumn`, `IfcColumnStandardCase` | `NetVolume`, `Length` |
| `IfcRoof` | `NetVolume` |
| `IfcSpace` | `NetFloorArea`, `GrossFloorArea`, `Height` |
| `IfcDoor` | `Area`, `Height`, `Width` |
| `IfcWindow` | `Area`, `Height`, `Width` |

Most fields come from the corresponding `Qto_*BaseQuantities` definitions. `Qto_RoofBaseQuantities` defines `GrossArea`, `NetArea` and `ProjectedArea` but no volume, so `IfcRoof NetVolume` is an author choice rather than a schema definition.

---

## 11. Quantity Name Normalisation

For the cross-pipeline comparison (D4), Node 3.2 removes the set prefix from every bracketed key, whether it is followed by a space or a dot:

```text
[BaseQuantities] NetVolume          → NetVolume
[Qto_WallBaseQuantities] NetVolume  → NetVolume
```

This lets the same measurement be compared even when the two pipelines report it under different set names. If an element carries the same field name in two sets, the first occurrence is used.

---

## 12. D3 — QTO Coverage

```text
D3 = (|Q_exp| − |Q_missing|) / |Q_exp|
```

- `Q_exp` = expected quantity fields for the IFC category
- `Q_missing` = expected fields not found with a non-empty value

Example: `IfcWall` with `NetVolume`, `Width` and `Length` present but no `NetSideArea` → `D3 = 3 / 4 = 0.750`.

---

## 13. D3 Fallback Rule

For a category with no explicit expected-quantity rule:

```text
IF the element has any bracketed property or quantity key:
    D3 = 1.0
ELSE:
    D3 = 0.0
```

---

## 14. Quantity Value Handling

For the comparison, values are parsed as numbers. A numeric `0` is kept as a valid value, distinct from a missing value.

Two behaviours of the released implementation matter when reading D4:

- A value that does not parse as a number, such as `True` or `UNSET`, is treated as not available for that pipeline (Section 15.1).
- The relative difference is measured against Pipeline A. If Pipeline A returns `0` and Pipeline B a non-zero value, the relative difference is taken as zero, so the row is classified `negligible`.

---

## 15. D4 — Cross-Pipeline Agreement

D4 checks whether two independent extraction pipelines return the same values:

- **Pipeline A:** DDC IFC Exporter
- **Pipeline B:** IfcOpenShell (`scripts/extract_ifc.py`)

Elements are matched on `GlobalId`. For each shared element, Node 3.2 builds one comparison row for every normalised field name found in either pipeline.

### 15.1 Comparison Classes

If both pipelines return a numeric value:

```text
Delta   = Value_B − Value_A
PctDiff = |Delta| / |Value_A| × 100
```

| Condition | Class |
|---|---|
| `|Delta| < 10⁻¹⁰` | `exact` |
| `PctDiff < 0.01%` | `negligible` |
| `0.01% ≤ PctDiff < 1%` | `minor` |
| `PctDiff ≥ 1%` | `significant` |

Otherwise the row is recorded as `only_in_A` or `only_in_B`. This covers fields missing from one pipeline and fields whose values are not numeric in either.

`exact` and `negligible` count as agreement. The 0.01% boundary is therefore the operational agreement threshold; the 1% boundary only separates two disagreement classes.

---

## 16. D4 Calculation

```text
D4 = (rows classified exact or negligible) / (all comparison rows for the element)
```

All other rows, including `only_in_A` and `only_in_B`, count against agreement. Non-numeric property fields such as `IsExternal` are part of the denominator.

Example (thesis worked example, `IfcWall` in M1): 7 rows, of which the 4 quantities agree and the 3 property fields `Status`, `IsExternal` and `LoadBearing` are non-numeric → `D4 = 4 / 7 = 0.571`.

See [`bqi-definition.md`](bqi-definition.md), Sections 4.4 and 12.6, for the consequences of this definition.

### 16.1 No Comparison Rows

```text
IF quantities are expected for the category:
    D4 = 0.5
ELSE:
    D4 = 1.0 if the element has any bracketed key, otherwise 0.0
```

0.5 represents insufficient comparison evidence, not agreement.

---

## 17. Element Coverage

Element coverage is evaluated separately from D1–D4, in Node 3.3, from the two pipelines' `GlobalId` sets:

```text
Coverage (%) = shared GlobalIds / union of GlobalIds × 100
```

It is kept separate from the BQI because an element present in only one pipeline cannot be compared.

### 17.1 Severity Classes

Each unmatched element is classified by type:

| Class | Types |
|---|---|
| **Critical** | `IfcWall`, `IfcSlab`, `IfcBeam`, `IfcColumn` (with StandardCase variants), `IfcRoof`, `IfcDoor`, `IfcWindow`, `IfcSpace`, `IfcStair`, `IfcStairFlight`, `IfcRamp`, `IfcRampFlight`, `IfcFooting`, `IfcPile` |
| **Needs review** | `IfcCovering`, `IfcPlate`, `IfcMember`, `IfcRailing`, `IfcCurtainWall`, `IfcFurnishingElement`, `IfcFurniture`, `IfcBuildingElementProxy`, and any type not listed elsewhere |
| **Probably harmless** | `IfcOpeningElement`, `IfcOpeningStandardCase`, `IfcAnnotation`, `IfcGrid`, `IfcGridAxis`, `IfcVirtualElement` |

### 17.2 Coverage Verdict

| Condition | Verdict |
|---|---|
| At least one **critical** element is unmatched | **FAIL** |
| Otherwise, at least one **needs-review** element is unmatched, or coverage is below 95% | **REVIEW** |
| Otherwise | **PASS** |

The 95% threshold is an author-defined convention and was not swept.

### 17.3 Coverage in the Thesis Corpus

In the committed baseline reports, the unmatched elements are:

| Models | Unmatched elements | Verdict |
|---|---|---|
| M1, M2 (building architecture) | `IfcSpace` (2), `IfcSpatialZone` (1), `IfcFurniture` (1) | FAIL, 77.78% |
| M3, M4 (building structural) | `IfcDiscreteAccessory` (2) | REVIEW, 88.89% |
| M5–M8 | none | PASS, 100% |

All of these elements are present only in Pipeline A because of the extraction scope of Pipeline B (Section 18): `IfcSpace` and `IfcFurniture` are removed by Node 2.6, and `IfcSpatialZone` and `IfcDiscreteAccessory` are not in the type list of `extract_ifc.py`. The baseline coverage shortfalls therefore reflect differences in the two pipelines' filters, not differences in how the two tools read the same elements. The coverage response to element deletion in the dual-file F6 runs is unaffected, because those deletions act on elements both pipelines extract.

---

## 18. Elements Excluded from Scoring

The two pipelines remove non-element records at different points.

**Pipeline A**, Node 1.9, removes rows whose category is:

```text
IfcProject, IfcSite, IfcBuilding, IfcBuildingStorey, IfcZone,
IfcBridge, IfcRoad, IfcFacility, IfcRailway
```

It also removes rows whose category reads `Advertisement: For an ad-free version…`, a notice row present in the converter output.

**Pipeline B** extracts only the physical element types listed in `scripts/extract_ifc.py`, which excludes `IfcZone` and `IfcSpatialZone`. Spatial entities are extracted separately for context. Node 2.6 then removes metadata items and the categories:

```text
IfcProject, IfcSite, IfcBuilding, IfcBuildingStorey, IfcSpace, IfcFurniture
```

Spatial entities remain available for schema detection, domain inference and spatial context, but are not scored.

---

## 19. Material Information

Pipeline B extracts material names (`extract_ifc.py --include-materials`, as called by Node 2.3), and the material string is carried on each element.

Material is not a BQI dimension. It is used by the risk-screening block as a susceptibility modifier ([`risk-rules-table.md`](risk-rules-table.md), Section 3.3). A missing material is recorded as a diagnostic `no_material` flag on the element, but it does not change the BQI.

---

## 20. Schema and Domain Detection

Node 2.5 reads the IFC schema from the parser metadata.

**IFC 4 files** are assigned the `Building` domain, since IFC 4 has no infrastructure spatial entities.

**IFC 4.3 files** are classified by checking for indicator types:

| Domain | Indicators |
|---|---|
| Rail | `IfcRail`, `IfcTrackElement`, spatial `IfcRailway` |
| Road | `IfcPavement`, `IfcKerb`, spatial `IfcRoad` |
| Bridge | `IfcBearing`, `IfcDeepFoundation`, spatial `IfcBridge` |
| Building | spatial `IfcBuilding`, `IfcWall`, `IfcSlab` |

If more than one domain matches, the model is `Mixed`; if none matches, `Unknown`. `Mixed` models are scored with the Building lookup tables and flagged with a domain warning.

In the corpus, M1–M5 and M7 are Building, M6 (IFC 4.3 bridge, which also contains walls and slabs) is Mixed, and M8 (IFC 4.3 road) is Road.

The domain affects only the risk lookup tables, not the validation rules.

---

## 21. Relationship Between Validation and BQI

```text
Validation rules
       │
       ├── Required properties ──► D1
       ├── Value usability ──────► D2
       ├── Expected quantities ──► D3
       └── Pipeline comparison ──► D4
                                │
                                ▼
                              BQI
```

This document describes the evidence being measured; [`bqi-definition.md`](bqi-definition.md) defines how it is combined.

---

## 22. Rule Coverage

The `REQUIRED_PROPS` and `EXPECTED_QTO` tables cover twelve building entities:

```text
IfcWall, IfcWallStandardCase, IfcSlab, IfcSlabStandardCase,
IfcBeam, IfcBeamStandardCase, IfcColumn, IfcColumnStandardCase,
IfcRoof, IfcDoor, IfcWindow, IfcSpace
```

Other categories are processed with the fallback rules. Across the 240 baseline elements of M1–M7 (thesis Table 5.1):

| Assessment | Elements | Share |
|---|---:|---:|
| Against the rule tables | 114 | 47.5% |
| Through the fallback rules | 29 | 12.1% |
| Zero in all four dimensions | 97 | 40.4% |

This is a deliberate limitation of the current rules, not an assumption that other categories are irrelevant.

---

## 23. Parameter Provenance

| Rule / Parameter | Value | Provenance |
|---|---|---|
| IFC schemas | IFC 4.0.2.1, IFC 4.3.2.0 | Study scope |
| Required-property membership | Per category | Author-defined selection from `Pset_*Common` definitions |
| Expected-quantity membership | Per category | Author-defined selection from `Qto_*BaseQuantities`; `IfcRoof NetVolume` is not schema-defined |
| Invalid values | Empty, null, UNSET, N/A | Implementation rule |
| D1 and D3 fallback | 1.0 with data, 0.0 without | Author-defined conservative convention |
| D4 fallback | 0.5 when quantities are expected | Author-defined conservative convention |
| Comparison boundaries | 10⁻¹⁰, 0.01%, 1% | Fixed constants in Node 3.2; not swept |
| Coverage severity classes | Section 17.1 | Author-defined |
| Coverage threshold | 95% | Author-defined convention; not swept |

---

## 24. Limitations

This is a **purpose-specific screening ruleset**, not a universal IFC compliance validator.

**Rule coverage is incomplete.** Only twelve building entities have explicit D1 and D3 rules; infrastructure entities rely on the fallback rules.

**Extractable quality is not fitness for purpose.** A high score means the information this workflow needs is present and usable; it does not prove the authoring model is correct or fit for other uses.

**Fallback behaviour limits fault detectability.** A fault on a property or quantity outside the rule tables may leave the BQI unchanged.

**Name matching is strict.** Related but differently named fields remain unmatched.

**D4 counts all bracketed fields.** Non-numeric properties and fields present in only one pipeline count against agreement, so baseline D4 is lower than agreement on quantities alone (Section 16).

**The two pipelines filter differently.** Pipeline B excludes some types that Pipeline A keeps (Section 18), and these differences produce the baseline coverage shortfalls of the building models (Section 17.3). `IfcSpace` carries BQI rules and is a critical coverage type, but is removed from Pipeline B.

**Coverage is separate from BQI.** An element absent from one pipeline is not scored against the other, so breadth differences are examined only through the coverage check.

---

## 25. Repository Implementation

The rules are implemented in Code, Filter and Set nodes of `workflows/thesis/n8n_ifc_dual_pipeline.json`:

| Node | Role |
|---|---|
| 1.9 Filter spatial | Removes non-element rows from Pipeline A |
| 2.5 Detect domain | Schema and domain detection |
| 2.6 Filter elements | Removes metadata and excluded categories from Pipeline B |
| 3.1 Merge A+B | Combines the two pipelines' items |
| 3.2 QTO comparison | Builds and classifies the comparison rows |
| 3.3 Coverage Analysis | Coverage percentage, severity classes and coverage verdict |
| 3.4 BQI Scoring | D1–D4 and element-level BQI |
| 3.5 SRCC Analysis | Cross-pipeline rank correlation per quantity field |

Pipeline B data are produced by `scripts/extract_ifc.py`.

---

## 26. Verification

`scripts/verify_exports.py` checks the sensitivity exports and recomputes the model-level BQI from the exported element scores (`score_completeness`, `score_validity`, `score_qto_coverage`, `score_qto_agreement`). `scripts/fault_analysis.py` checks that controlled defects change the targeted dimensions as expected.

The ruleset is part of the measurement instrument and is versioned together with the workflow.

---

## Canonical Sources

- Thesis Section 3.3: BIM Quality Index, including Section 3.3.4, Rule Tables and Schema Handling
- Thesis Section 3.4: QTO Comparison and SRCC Robustness Protocol
- Thesis Section 3.7.4: Verdict Logic and Report
- Thesis Section 5.5: Threats to Validity and Limitations
- Thesis Annex I: BQI Rule Tables

This document describes the behaviour of repository release `v1.0.2`.
