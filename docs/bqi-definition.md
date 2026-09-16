# BIM Quality Index (BQI)

## 1. Purpose

The **BIM Quality Index (BQI)** is a continuous, weighted metric developed in this thesis to quantify the quality of the information available in IFC models for downstream automated screening.

Unlike a binary validation result, the BQI produces scores on the interval **[0, 1]**, so that models and elements with different degrees and types of information deficiency can be distinguished.

The BQI is evaluated at two levels:

1. **Element level**, where four quality dimensions are scored for each assessed IFC element.
2. **Model level**, where the element-level BQI values are averaged across the valued elements of the model.

The framework is applied to **IFC 4.0.2.1 (IFC 4)** and **IFC 4.3.2.0 (IFC 4.3)** models.

---

## 2. BQI Dimensions

The BQI combines four partially overlapping measurement dimensions:

| Dimension | Name | What it measures |
|---|---|---|
| **D1** | Property Completeness | Whether the properties required for the element's IFC category are present |
| **D2** | Property Validity | Whether the extracted property values are usable rather than empty or UNSET |
| **D3** | QTO Coverage | Whether the expected quantity fields are present |
| **D4** | Cross-Pipeline Agreement | Whether the two independent extraction pipelines return the same values |

The four dimensions are not independent evidence sources. They are computed over overlapping data, so one defect can influence more than one dimension.

For example, the D2 key set includes keys from both property sets and quantity sets, and the fallback rules of D1, D3 and D4 depend on whether an element carries any bracketed property or quantity data.

---

## 3. Element-Level BQI

For an element `e`:

```text
BQI_element = w1 × D1 + w2 × D2 + w3 × D3 + w4 × D4
```

with:

```text
w1 = 0.35    w2 = 0.25    w3 = 0.20    w4 = 0.20
```

The weights sum to one and preserve the intended ordering:

**Completeness > Validity > QTO Coverage = Cross-Pipeline Agreement**

The weights are **author-defined screening conventions**, not the output of a rank-to-weight method. The Rank-Order Centroid (ROC) scheme is used separately as a benchmark in the sensitivity analysis (thesis Section 4.4.1).

---

## 4. Dimension Definitions

### 4.1 D1 — Property Completeness

D1 is the fraction of the properties required for the element's IFC category that are present with a non-empty value.

Let:

- `P_req` = required properties for the element's IFC category
- `P_missing` = required properties absent from the element, or present with an empty value

Then:

```text
D1 = (|P_req| − |P_missing|) / |P_req|
```

For example, the rule for `IfcWall` requires `IsExternal` and `LoadBearing`. If both are present, `D1 = 2 / 2 = 1.000`; if one is missing, `D1 = 1 / 2 = 0.500`.

#### Fallback rule

When the element's category has no explicit D1 rule:

- `D1 = 1.0` if the element carries any bracketed property or quantity data;
- `D1 = 0.0` if it carries none.

The zero branch is deliberately conservative: an element is not considered complete merely because no rule exists for its category.

---

### 4.2 D2 — Property Validity

D2 is the fraction of the element's extracted keys whose values are usable.

Let:

- `K` = all bracketed keys of the element (property sets and quantity sets)
- `K_invalid` = keys whose value is empty, null, `UNSET` or `N/A`

Then:

```text
D2 = (|K| − |K_invalid|) / |K|
```

An element with no extracted keys receives `D2 = 0.0`.

A property slot that exists but carries no usable value therefore lowers D2 even though the key itself is present.

---

### 4.3 D3 — QTO Coverage

D3 is the fraction of the quantity fields expected for the element's IFC category that are present.

Let:

- `Q_exp` = expected quantity fields for the element's IFC category
- `Q_missing` = expected quantity fields that are absent

Then:

```text
D3 = (|Q_exp| − |Q_missing|) / |Q_exp|
```

For example, `IfcWall` expects `NetVolume`, `Width`, `Length` and `NetSideArea`. If all four are present, `D3 = 1.000`; if three are present, `D3 = 0.750`.

#### Fallback rule

The same conservative fallback as D1 applies when the category has no explicit D3 rule.

Field names are matched exactly after the bracketed set prefix is removed. For example, `GrossArea` does not satisfy a rule expecting `NetArea`. This avoids permissive matching that would overstate coverage.

---

### 4.4 D4 — Cross-Pipeline Agreement

D4 measures agreement between the two independent extraction pipelines:

- **Pipeline A:** DDC IFC Exporter (tabular extraction)
- **Pipeline B:** IfcOpenShell extraction

The pipelines are matched on IFC `GlobalId`.

#### Comparison rows

For each matched element, Node 3.2 builds one comparison row for every bracketed field name found in either pipeline, after removing the set prefix (so `[Qto_WallBaseQuantities] NetVolume` and `[BaseQuantities] NetVolume` are the same field). `C_grid` is the set of rows for that `GlobalId`.

- If both pipelines return a **numeric** value, the row is classified by the difference relative to Pipeline A:

| Difference | Class |
|---|---|
| Absolute difference `< 10⁻¹⁰` | `exact` |
| Relative difference `< 0.01%` | `negligible` |
| Relative difference `0.01%` to `< 1%` | `minor` |
| Relative difference `≥ 1%` | `significant` |

- Otherwise, the row is recorded as `only_in_A` or `only_in_B`. This covers fields missing from one pipeline and fields whose values are not numeric, such as `IsExternal = True` or `Status = UNSET`.

#### Score

```text
D4 = |{ c ∈ C_grid : class(c) ∈ {exact, negligible} }| / |C_grid|
```

Only `exact` and `negligible` rows count as agreement. All other rows, including `only_in_A` and `only_in_B`, count against D4. D4 is therefore the share of an element's bracketed fields on which both pipelines return the same numeric value (see Section 12.6).

For D4, the important boundary is the **0.01% negligible-agreement threshold**. The 1% boundary only separates the two disagreement classes.

#### No comparison rows

If an element has no comparison rows:

- `D4 = 0.5` when quantities were expected for its category, reflecting absence of evidence;
- otherwise the has-any-data fallback applies (`1.0` with data, `0.0` without).

Missing comparison evidence is therefore not treated as perfect agreement.

---

## 5. Rule Tables and Schema Handling

In the thesis release, one `REQUIRED_PROPS` and `EXPECTED_QTO` table, covering twelve building entities, is applied to both IFC 4.0.2.1 and IFC 4.3.2.0 models. Infrastructure entities such as `IfcBearing`, `IfcCourse`, `IfcKerb` and `IfcPavement` do not yet carry quality rules; they are scored through the fallback rules.

The schema identifier is detected from the parser metadata and carried on every item. It currently selects the spatial types used in extraction and the domain used for the risk lookup tables. Schema-specific rule tables are the intended next step: once infrastructure rules are added, a single table could no longer avoid both false negatives (valid IFC 4.3 content not recognised) and false positives (properties not applicable to one version reported missing).

See thesis Sections 3.3.4 and 5.5.

---

## 6. Required Property Rules

| IFC Entity | Required Properties |
|---|---|
| `IfcBeam`, `IfcBeamStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcColumn`, `IfcColumnStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcSlab`, `IfcSlabStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcWall`, `IfcWallStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcRoof` | `IsExternal` |
| `IfcDoor` | `IsExternal`, `FireRating` |
| `IfcWindow` | `IsExternal` |
| `IfcSpace` | `IsExternal`, `GrossPlannedArea` |

The selection of these properties as screening criteria is an **author-defined decision based on buildingSMART Pset content**. It is not a claim that every listed property is mandatory under the IFC schema.

The formal rule tables are in thesis Annex I.

---

## 7. Expected Quantity Rules

| IFC Entity | Expected Quantity Fields |
|---|---|
| `IfcBeam`, `IfcBeamStandardCase` | `NetVolume`, `Length` |
| `IfcColumn`, `IfcColumnStandardCase` | `NetVolume`, `Length` |
| `IfcSlab`, `IfcSlabStandardCase` | `NetVolume`, `Depth`, `NetArea` |
| `IfcWall`, `IfcWallStandardCase` | `NetVolume`, `Width`, `Length`, `NetSideArea` |
| `IfcRoof` | `NetVolume` |
| `IfcDoor` | `Area`, `Height`, `Width` |
| `IfcWindow` | `Area`, `Height`, `Width` |
| `IfcSpace` | `NetFloorArea`, `GrossFloorArea`, `Height` |

Most fields come from the corresponding `Qto_*BaseQuantities` definitions. One exception: `Qto_RoofBaseQuantities` defines `GrossArea`, `NetArea` and `ProjectedArea` but no volume, so the `NetVolume` expectation for `IfcRoof` is an author choice rather than a schema definition.

The rule set is deliberately narrower than the range of IFC entity types in the corpus. Categories without a rule use the fallback behaviour instead of receiving an implicit perfect score.

---

## 8. Model-Level BQI

The model-level score is the arithmetic mean of the element scores:

```text
BQI_model = (1 / N) × Σ BQI_element
```

where `N` is the number of valued elements in the model: all elements scored by the BQI engine, whether against an explicit rule, through the fallback rules, or at zero.

The model BQI therefore represents the mean quality of the assessed element population. Elements are scored first and aggregated afterwards, rather than pooling all property and quantity observations into one global ratio.

---

## 9. Confidence Bands

| BQI | Confidence |
|---:|---|
| `BQI ≥ 0.85` | **HIGH** |
| `0.60 ≤ BQI < 0.85` | **MEDIUM** |
| `BQI < 0.60` | **LOW** |

The same thresholds are applied at element level and at model level. They are **author-defined conventions**, not externally calibrated standards; their effect on the verdict is reported in thesis Section 4.4.3.

The bands are used for interpretation and for the verdict. The continuous BQI value, not the label, is used when propagating information quality into the risk calculation.

---

## 10. Worked Example

Element `1AQAupaRP1txwK1AGiN61V`, an `IfcWall` in model M1 (thesis Section 3.3.5):

| Dimension | Evidence | Score |
|---|---|---|
| D1 | `IsExternal` and `LoadBearing` both present | 2 / 2 = 1.000 |
| D2 | 7 keys, of which `Status` is UNSET | 6 / 7 = 0.857 |
| D3 | All four expected quantities present | 4 / 4 = 1.000 |
| D4 | 7 comparison rows: the 4 quantities agree; `Status`, `IsExternal` and `LoadBearing` are non-numeric | 4 / 7 = 0.571 |

```text
BQI_element = 0.35 × 1.000 + 0.25 × 0.857 + 0.20 × 1.000 + 0.20 × 0.571 = 0.879
```

The element is classified as **HIGH** confidence because `0.879 ≥ 0.85`, even though model M1 scores 0.471 overall.

---

## 11. Relationship to Risk Screening

The BQI is not a risk score. The continuous element-level BQI is carried into the uncertainty-aware risk calculation:

```text
R_raw   = min(1, max(0, L × C))
R_adj   = min(1, R_raw × [1 + α × (1 − BQI)])
R_lower = max(0, R_raw × [1 − α × (1 − BQI)])

α = 0.55
```

The screening ranking uses the conservative upper value `R_adj`. An element with lower BQI receives a wider band; an element with BQI close to 1 receives a narrow one. The full risk rules are in [`risk-rules-table.md`](risk-rules-table.md).

---

## 12. Interpretation and Limitations

### 12.1 The four dimensions partially overlap

D1–D4 are not statistically independent:

- D2 includes keys from quantity sets, so removing a quantity field can change D2 as well as D3.
- Removing an entire property set can trigger or remove fallback behaviour.
- Removing property fields shrinks the D4 denominator, which is why D4 can rise under F1 and F5 (thesis Table 4.3 and Section 4.2.2).

The weights should be read as the relative importance of four measurement criteria, not of four independent evidence channels.

### 12.2 Fallback scores are not equivalent to explicit rule scores

`D1 = 1.0` obtained through the fallback only means that the element carries some bracketed data and has no explicit rule. It is not equivalent to verifying each required property individually.

### 12.3 Fault injection only tests the region covered by the rules

A fault such as required-property deletion can only manifest where the named properties are measured. It may produce no change when the element relies on fallback scoring, or when the dimension is already at its floor. This is a property of the instrument's rule coverage, not evidence that the model is unaffected.

### 12.4 No per-dimension floor is imposed

The confidence bands act on the aggregate BQI. Because D1 has weight 0.35, an element with `D1 = 0` and perfect scores elsewhere reaches `BQI = 0.65`, which is MEDIUM. In this corpus, 25 elements with the profile `(0, 1, 1, 1)` in M2, M4, M5 and M6 score exactly 0.650 (thesis Sections 4.1 and 5.5).

### 12.5 Exact field-name matching

D1 and D3 match field names exactly after the set prefix is removed, so `GrossArea` does not satisfy `NetArea`. This prevents loose matching from inflating scores, but part of a low score can reflect naming conventions rather than the absence of the underlying quantity.

### 12.6 What D4 counts

D4 is computed over every bracketed field of the element, not only over quantities that both pipelines return as numbers. Non-numeric fields (for example `IsExternal`, `LoadBearing`, `Status`) and fields present in only one pipeline always count against agreement. As a result:

- baseline D4 is lower than the agreement on quantities alone, and depends on how many non-numeric properties an element carries;
- D4 still responds to F4 as designed, because F4 changes numeric quantity values only.

When Pipeline A returns `0` and Pipeline B a non-zero value, the relative difference is taken as zero, so the row is classified `negligible`.

The thesis text (Section 3.4.1) describes one-pipeline fields as excluded from the comparison; the behaviour described here is what the released workflow computes and what all reported D4 values reflect.

---

## 13. Parameter Provenance

| Parameter | Value | Provenance |
|---|---|---|
| D1–D4 definitions | — | Based on IFC information structures and buildingSMART Pset/Qto definitions |
| Required-property membership | Per IFC category | Author-defined selection from schema-defined sets |
| Expected-QTO membership | Per IFC category | Author-defined selection; `IfcRoof NetVolume` is not schema-defined |
| Weights w1–w4 | 0.35, 0.25, 0.20, 0.20 | Author-defined ordering; ranking stability characterised (Section 4.4.1) |
| D1/D3 fallback | 1.0 / 0.0 | Author-defined conservative convention |
| D4 fallback | 0.5 when QTO expected | Author-defined conservative convention |
| HIGH / MEDIUM thresholds | 0.85 / 0.60 | Author-defined convention; sensitivity reported (Section 4.4.3) |
| Comparison class boundaries | 10⁻¹⁰, 0.01%, 1% | Author-defined constants in Node 3.2; not swept (Section 5.5) |
| `α` | 0.55 | Empirically characterised (Sections 3.6.4, 4.4.2) |

---

## 14. Repository Implementation

The BQI is implemented in Block 3 of `workflows/thesis/n8n_ifc_dual_pipeline.json`:

| Node | Step |
|---|---|
| 3.1 | Merge Pipeline A and Pipeline B items by `GlobalId` |
| 3.2 | Build the comparison rows and classify them |
| 3.3 | Element coverage analysis and coverage verdict |
| 3.4 | Score D1–D4 and the element-level BQI |
| 3.5 | Cross-pipeline SRCC per quantity field |

The element-level scores are passed to the risk-screening block (Block 4) and exported per element in the sensitivity JSON (`score_completeness`, `score_validity`, `score_qto_coverage`, `score_qto_agreement`).

---

## 15. Verification

`scripts/verify_exports.py` checks every sensitivity export and recomputes the model-level BQI from the exported element scores:

```text
Element D1–D4 → Equation 3.1 → BQI_element → Equation 3.2 → BQI_model
```

The recomputed values can be compared with thesis Table 4.1. `scripts/fault_analysis.py` evaluates detection, monotonicity and selectivity across the fault-injection runs.

---

## 16. Canonical Sources

- Thesis Chapter 3, Section 3.3: BQI
- Thesis Section 3.4: QTO comparison and SRCC protocol
- Thesis Annex I: BQI rule tables

This document is an implementation-oriented companion to those definitions and describes the behaviour of repository release `v1.0.2`.
