# BIM Quality Index (BQI)

## 1. Purpose

The **BIM Quality Index (BQI)** is a continuous, weighted, and schema-aware metric developed in this thesis to quantify the quality of information available in IFC models for downstream automated screening.

Unlike a binary validation result, the BQI produces scores on the interval **[0, 1]**, allowing models and individual elements with different degrees and types of information deficiency to be distinguished.

The BQI is evaluated at two levels:

1. **Element level**, where four quality dimensions are scored for each assessed IFC element.
2. **Model level**, where the element-level BQI values are averaged across the valued elements in the model.

The framework is designed for **IFC 4.0.2.1 (IFC 4)** and **IFC 4.3.2.0 (IFC 4.3)**.

---

## 2. BQI Dimensions

The BQI combines four partially overlapping measurement dimensions:

| Dimension | Name | What it measures |
|---|---|---|
| **D1** | Property Completeness | Whether properties required for the element's IFC category are present |
| **D2** | Property Validity | Whether extracted property values are usable rather than empty or invalid |
| **D3** | QTO Coverage | Whether expected quantity fields are present |
| **D4** | Cross-Pipeline Agreement | Whether the two independent extraction pipelines agree on comparable quantities |

The four dimensions should not be interpreted as completely independent evidence sources. They are computed over overlapping data structures, and one defect can therefore influence more than one dimension.

For example, the D2 property-key set includes keys originating from both property sets and quantity sets. Likewise, fallback rules in D1, D3, and D4 depend on whether an element carries bracketed property or quantity data.

---

## 3. Element-Level BQI

For an element \(e\), the BQI is:

```text
BQI_element =
    w1 × D1
  + w2 × D2
  + w3 × D3
  + w4 × D4
```

with:

```text
w1 = 0.35
w2 = 0.25
w3 = 0.20
w4 = 0.20
```

Therefore:

```text
BQI_element =
    0.35 × D1
  + 0.25 × D2
  + 0.20 × D3
  + 0.20 × D4
```

The weights sum to one and preserve the intended ordering:

**Completeness > Validity > QTO Coverage = QTO Agreement**

The numerical weights are **author-defined screening conventions** rather than a direct application of a rank-to-weight conversion method. The Rank-Order Centroid (ROC) scheme is used separately as a sensitivity-analysis benchmark.

---

## 4. Dimension Definitions

### 4.1 D1 — Property Completeness

D1 measures the fraction of properties required for an element's IFC category that are present.

Let:

- `P_req` = required property set for the element's IFC category
- `P_missing` = required properties absent from the element

Then:

```text
D1 = (|P_req| - |P_missing|) / |P_req|
```

For example, the IFC 4 rule for an `IfcWall` requires:

```text
IsExternal
LoadBearing
```

If both are present:

```text
D1 = 2 / 2 = 1.000
```

If one is missing:

```text
D1 = 1 / 2 = 0.500
```

#### Fallback rule

Not every IFC entity type has an explicit rule-table entry.

When no explicit D1 rule exists:

- `D1 = 1.0` if the element carries any bracketed property/quantity data;
- `D1 = 0.0` if it carries no bracketed data.

The zero branch is deliberate and conservative. An element is not considered complete merely because no explicit rule has been defined for its category.

---

### 4.2 D2 — Property Validity

D2 measures the fraction of extracted property values that are usable.

Let:

- `K` = all extracted property keys for the element;
- `K_invalid` = keys whose values are empty, null, `UNSET`, or `N/A`.

Then:

```text
D2 = (|K| - |K_invalid|) / |K|
```

An element with no extracted properties receives:

```text
D2 = 0.0
```

The key set includes extracted keys originating from both property sets and quantity sets because the extraction pipelines expose these values through the same bracketed key namespace.

Examples of invalid values include:

```text
""
null
UNSET
N/A
```

A property slot that exists but has no usable value therefore affects D2 even though the property key itself remains present.

---

### 4.3 D3 — QTO Coverage

D3 measures the fraction of quantity fields expected for an element's IFC category that are present.

Let:

- `Q_exp` = expected quantity fields for the element's IFC category;
- `Q_missing` = expected quantity fields that are absent.

Then:

```text
D3 = (|Q_exp| - |Q_missing|) / |Q_exp|
```

For example, an `IfcWall` has the following expected quantity fields:

```text
NetVolume
Width
Length
NetSideArea
```

If all four are present:

```text
D3 = 4 / 4 = 1.000
```

If three are present:

```text
D3 = 3 / 4 = 0.750
```

#### Fallback rule

The same conservative fallback used for D1 is applied when an IFC category has no explicit D3 rule:

- `D3 = 1.0` if the element carries any bracketed data;
- `D3 = 0.0` otherwise.

Quantity names are matched exactly after the quantity-set prefix is removed. For example, `GrossArea` does not satisfy a rule expecting `NetArea`.

This deliberately avoids permissive name matching that could overstate QTO coverage.

---

### 4.4 D4 — Cross-Pipeline Agreement

D4 measures agreement between the two independent extraction pipelines:

- **Pipeline A:** DDC-based tabular extraction;
- **Pipeline B:** IfcOpenShell extraction.

The pipelines are matched using IFC `GlobalId`.

For each element, `C_grid` denotes the set of quantity-comparison rows associated with that `GlobalId`.

A comparison is classified as:

- `exact`;
- `negligible`;
- `minor`; or
- `significant`.

Only `exact` and `negligible` comparisons count as agreement.

The D4 score is:

```text
D4 =
|{ c : Match(c) ∈ {exact, negligible} }|
------------------------------------------------
|C_grid|
```

Thus, D4 is the proportion of comparable quantity rows that are classified as agreeing.

#### Quantity comparison thresholds

The quantity-comparison classes use the following fixed boundaries:

| Difference | Classification |
|---|---|
| `< 10^-10` absolute difference | Exact |
| `< 0.01%` relative difference | Negligible |
| `0.01%–<1%` relative difference | Minor |
| `≥ 1%` relative difference | Significant |

For D4, the important boundary is the **0.01% negligible-agreement threshold**. The 1% boundary separates the two disagreement classes and does not directly enter the D4 calculation.

#### No comparison rows

If an element has no comparison rows:

- `D4 = 0.5` when QTO was expected, reflecting absence of evidence;
- otherwise the score falls back to the has-any-data rule.

The 0.5 value is deliberately conservative. Missing comparison evidence is not treated as perfect agreement.

---

## 5. Schema-Conditional Rule Selection

The BQI rules are **schema-aware**.

Separate rule tables are maintained for:

- IFC 4.0.2.1
- IFC 4.3.2.0

The workflow detects the schema identifier from the IFC parser metadata and selects the corresponding rule set dynamically.

This is necessary because IFC 4.3 introduces infrastructure entity types that are not present in the IFC 4 rule set, including examples such as:

- `IfcBearing`
- `IfcCourse`
- `IfcKerb`
- `IfcPavement`

Using a single schema-blind rule table could therefore produce:

- false negatives, where valid schema-specific information is reported missing; or
- false positives, where a property not applicable to a schema version is treated as required.

---

## 6. Required Property Rules

The current explicit `REQUIRED_PROPS` rules are:

| IFC Entity | Required Properties |
|---|---|
| `IfcBeam` | `IsExternal`, `LoadBearing` |
| `IfcBeamStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcColumn` | `IsExternal`, `LoadBearing` |
| `IfcColumnStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcDoor` | `IsExternal`, `FireRating` |
| `IfcRoof` | `IsExternal` |
| `IfcSlab` | `IsExternal`, `LoadBearing` |
| `IfcSlabStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcSpace` | `IsExternal`, `GrossPlannedArea` |
| `IfcWall` | `IsExternal`, `LoadBearing` |
| `IfcWallStandardCase` | `IsExternal`, `LoadBearing` |
| `IfcWindow` | `IsExternal` |

The selection of these properties as mandatory screening criteria is an **author-defined screening decision derived from schema-defined Pset content**. They should not be interpreted as a claim that every listed property is universally mandatory under the IFC schema.

The complete formal rule tables are maintained in the thesis Annex I and versioned repository implementation.

---

## 7. Expected Quantity Rules

The current explicit `EXPECTED_QTO` rules are:

| IFC Entity | Expected Quantity Fields |
|---|---|
| `IfcBeam` | `NetVolume`, `Length` |
| `IfcBeamStandardCase` | `NetVolume`, `Length` |
| `IfcColumn` | `NetVolume`, `Length` |
| `IfcColumnStandardCase` | `NetVolume`, `Length` |
| `IfcDoor` | `Area`, `Height`, `Width` |
| `IfcRoof` | `NetVolume` |
| `IfcSlab` | `NetVolume`, `Depth`, `NetArea` |
| `IfcSlabStandardCase` | `NetVolume`, `Depth`, `NetArea` |
| `IfcSpace` | `NetFloorArea`, `GrossFloorArea`, `Height` |
| `IfcWall` | `NetVolume`, `Width`, `Length`, `NetSideArea` |
| `IfcWallStandardCase` | `NetVolume`, `Width`, `Length`, `NetSideArea` |
| `IfcWindow` | `Area`, `Height`, `Width` |

The rule set is deliberately narrower than the complete population of IFC entity types in the corpus. Unsupported categories use the documented fallback behaviour rather than receiving an implicit perfect score.

---

## 8. Model-Level BQI

Once every valued element has an element-level BQI, the model-level score is calculated as the arithmetic mean:

```text
BQI_model =
1/N × Σ BQI_element
```

where:

- `N` = number of valued elements in the model;
- `BQI_element` = element-level BQI.

The model BQI therefore represents the mean quality of the assessed element population.

This is different from aggregating all property or quantity observations into one global ratio. The framework intentionally scores individual elements first and aggregates those scores afterwards.

---

## 9. Confidence Bands

BQI scores are mapped to three confidence bands for communication:

| BQI | Confidence |
|---:|---|
| `BQI ≥ 0.85` | **HIGH** |
| `0.60 ≤ BQI < 0.85` | **MEDIUM** |
| `BQI < 0.60` | **LOW** |

The same thresholds are applied at:

- element level; and
- model level.

These thresholds are **author-defined engineering conventions**, not externally calibrated universal standards.

They are used for interpretation and verdict communication. The continuous BQI value itself, rather than the confidence label, is used when propagating information quality into the uncertainty-aware risk calculation.

---

## 10. Worked Example

For one `IfcWall` element in model M1:

```text
D1 = 1.000
D2 = 0.857
D3 = 1.000
D4 = 0.571
```

Using the baseline weights:

```text
BQI_element =
    0.35 × 1.000
  + 0.25 × 0.857
  + 0.20 × 1.000
  + 0.20 × 0.571

BQI_element = 0.879
```

The element is therefore classified as:

```text
HIGH confidence
```

because:

```text
0.879 ≥ 0.85
```

The same element can nevertheless belong to a model with a substantially lower model-level BQI because model BQI is the mean across all valued elements.

---

## 11. Relationship to Risk Screening

BQI is not itself a risk score.

Instead, the continuous element-level BQI is carried forward into the uncertainty-aware risk calculation.

The risk-screening block uses:

```text
R_raw = Likelihood × Consequence
```

and widens the result according to:

```text
widening = α × (1 − BQI)
```

producing:

```text
R_adj =
R_raw × [1 + α × (1 − BQI)]

R_lower =
R_raw × [1 − α × (1 − BQI)]
```

The reported screening ranking uses the conservative upper value `R_adj`.

The operating value used in the thesis is:

```text
α = 0.55
```

Therefore, an element with lower BQI receives a wider uncertainty band while an element with BQI approaching 1 receives a narrower band.

---

## 12. Interpretation and Limitations

### 12.1 The four dimensions are partially overlapping

D1–D4 are not statistically independent.

Examples:

- D2 includes keys originating from Qto data.
- Removing a quantity field can therefore influence D2 as well as D3.
- Removing an entire Pset can change whether fallback logic is triggered.
- A single defect can therefore affect several dimensions.

The weights should consequently be interpreted as relative importance assigned to four measurement criteria, not as four independent evidence channels.

---

### 12.2 Fallback scores are not equivalent to explicit rule scores

An element receiving:

```text
D1 = 1.0
```

through the fallback rule is not equivalent to an element for which all explicitly expected properties were individually verified.

The fallback means only that the element carries some bracketed data and no explicit category rule is available.

This distinction is important when interpreting both baseline results and fault-injection experiments.

---

### 12.3 Fault injection only tests the region covered by the rules

Faults such as mandatory-property deletion can only manifest where the corresponding named properties are measurable.

Consequently, a fault may produce no change when the affected element relies on fallback scoring or when the relevant dimension is already at its floor.

This is a property of the measurement instrument and rule coverage, not evidence that the underlying IFC model is unaffected.

---

### 12.4 No per-dimension floor is imposed

The confidence bands operate on the aggregate BQI.

Consequently, an element can theoretically have a zero score on one dimension while remaining above a confidence threshold if the other dimensions are sufficiently high.

For example, because D1 has weight 0.35, an element with `D1 = 0` could theoretically still obtain a BQI of 0.65 if the remaining dimensions were all 1.0.

The current implementation does not impose a minimum dimension-specific floor.

---

### 12.5 Exact quantity-name matching

D1 and D3 use exact field-name matching after the quantity/property-set prefix is removed.

For example:

```text
Expected: NetArea
Available: GrossArea
```

does not constitute a match.

This conservative choice prevents loose name matching from artificially inflating quality scores. However, it means that part of a low D3 score can reflect authoring or naming conventions rather than the complete absence of the underlying geometric quantity.

---

## 13. Parameter Provenance

| Parameter | Value | Provenance |
|---|---:|---|
| D1–D4 definitions | — | Derived from IFC information structures and buildingSMART Pset/Qto definitions |
| Required-property membership | Per IFC category | Author-defined selection from schema-defined sets |
| Expected-QTO membership | Per IFC category | Author-defined selection from schema-defined sets |
| D1 weight | 0.35 | Author-defined ordering / sensitivity-characterised |
| D2 weight | 0.25 | Author-defined ordering / sensitivity-characterised |
| D3 weight | 0.20 | Author-defined ordering / sensitivity-characterised |
| D4 weight | 0.20 | Author-defined ordering / sensitivity-characterised |
| D1/D3 fallback | 1.0 / 0.0 | Author-defined conservative convention |
| D4 fallback | 0.5 when QTO was expected | Author-defined conservative convention |
| HIGH threshold | 0.85 | Author-defined convention |
| MEDIUM threshold | 0.60 | Author-defined convention |
| QTO negligible threshold | 0.01% | Author-defined |
| `α` | 0.55 | Empirically characterised in the thesis |

---

## 14. Repository Implementation

The BQI is implemented in the thesis n8n workflow:

`workflows/thesis/n8n_ifc_dual_pipeline.json`

The main BQI processing occurs in:

```text
Block 3 — QTO Comparison + BQI Scoring
```

The workflow:

1. merges Pipeline A and Pipeline B using `GlobalId`;
2. compares QTO fields;
3. evaluates element coverage;
4. scores D1–D4;
5. computes element-level BQI;
6. aggregates model-level BQI; and
7. passes the BQI into the risk-screening block.

The per-element BQI dimensions are also exported in the sensitivity JSON for independent offline verification.

---

## 15. Verification

The BQI implementation is verified through several independent checks.

The repository verification scripts recompute model-level BQI from the exported element-level dimension scores and reproduce the reported model values to three decimal places.

This provides a consistency check between:

```text
Element-level D1–D4
        ↓
Equation 3.1
        ↓
BQI_element
        ↓
Equation 3.2
        ↓
BQI_model
```

The fault-analysis workflow additionally evaluates BQI detectability and monotonicity across the controlled fault-injection experiments.

---

## 16. Canonical Sources

The formal methodological definition of the BQI is given in:

- **Thesis Chapter 3, Section 3.3 — BQI**
- **Thesis Annex I — BQI Rule Tables**

This repository document is an implementation-oriented companion to those definitions.

The executable workflow and rule implementation should remain consistent with the version of the thesis associated with the repository release.
