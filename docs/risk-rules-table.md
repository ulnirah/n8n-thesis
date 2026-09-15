# Risk Rules Table

This document defines the deterministic rules used by the thesis **uncertainty-aware risk screening model**.

The model is a BIM-only, relative screening framework. It does **not** estimate empirical probabilities of failure and is not calibrated against field deterioration data. Likelihood, susceptibility, criticality, exposure, and material values are ordinal engineering screening parameters. Their purpose is to produce a reproducible relative ranking within the analysed model. :contentReference[oaicite:2]{index=2}

The risk-screening chain is:

```text
IFC properties
      ↓
Exposure
      ↓
Likelihood proxy
      ↓
Consequence proxy
      ↓
R_raw
      ↓
BQI-dependent uncertainty band
      ↓
R_lower / R_raw / R_adj
      ↓
Risk ranking and labels
```

---

## 1. Core Risk Formulation

The baseline risk follows a likelihood × consequence formulation:

```text
R_raw = L × C
```

where:

- `L` = likelihood proxy;
- `C` = consequence proxy.

The implementation clamps the result to `[0, 1]`:

```text
R_raw = min(1, max(0, L × C))
```

`R_raw` represents the deterministic risk estimate before information-quality uncertainty is propagated. :contentReference[oaicite:3]{index=3}

---

# 2. Likelihood Proxy

The likelihood proxy is:

```text
L = min(1, max(0, E × (S_base + m_mat)))
```

where:

| Symbol | Meaning |
|---|---|
| `E` | Exposure score |
| `S_base` | Baseline susceptibility for IFC category and domain |
| `m_mat` | Material modifier |

The resulting `L` is dimensionless and is used for **relative screening only**. It must not be interpreted as an empirical failure probability. :contentReference[oaicite:4]{index=4}

---

## 2.1 Exposure

Exposure is derived from the element's location-related information, including:

- `IsExternal`; and
- the available zone/location information.

Exposure is implemented by domain-specific IFC-category lookup tables in the n8n workflow.

The exposure term is deliberately kept separate from susceptibility:

```text
Likelihood = Exposure × (Susceptibility + Material Modifier)
```

This separates the question:

> How exposed is the element?

from:

> How susceptible is this element type under that exposure?

---

## 2.2 Susceptibility Lookup

`S_base` is selected by:

```text
IFC Category + Domain
```

The values are ordinal engineering judgements rather than calibrated probabilities. The lookup values were frozen before the corpus was scored, avoiding post-hoc adjustment of individual results. :contentReference[oaicite:5]{index=5}

### Building

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcBeam` | 0.35 | 0.90 |
| `IfcBeamStandardCase` | 0.35 | 0.90 |
| `IfcBuildingElementProxy` | 0.30 | 0.50 |
| `IfcChimney` | 0.70 | 0.45 |
| `IfcColumn` | 0.35 | 1.00 |
| `IfcColumnStandardCase` | 0.35 | 1.00 |
| `IfcCovering` | 0.55 | 0.40 |
| `IfcCurtainWall` | 0.60 | 0.55 |
| `IfcDoor` | 0.55 | 0.50 |
| `IfcFooting` | 0.30 | 1.00 |
| `IfcFurnishingElement` | 0.20 | 0.10 |
| `IfcFurniture` | 0.20 | 0.10 |
| `IfcMember` | 0.35 | 0.65 |
| `IfcPile` | 0.25 | 1.00 |
| `IfcPlate` | 0.40 | 0.60 |
| `IfcRailing` | 0.40 | 0.35 |
| `IfcRamp` | 0.45 | 0.60 |
| `IfcRampFlight` | 0.45 | 0.60 |
| `IfcRoof` | 0.80 | 0.75 |
| `IfcSlab` | 0.40 | 0.85 |
| `IfcSlabStandardCase` | 0.40 | 0.85 |
| `IfcSpace` | 0.15 | 0.20 |
| `IfcStair` | 0.50 | 0.65 |
| `IfcStairFlight` | 0.50 | 0.65 |
| `IfcWall` | 0.45 | 0.80 |
| `IfcWallStandardCase` | 0.45 | 0.80 |
| `IfcWindow` | 0.65 | 0.50 |

These are the Building-domain susceptibility and criticality values published in Annex II. :contentReference[oaicite:6]{index=6}

### Bridge

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcBearing` | 0.85 | 1.00 |
| `IfcBridgePart` | 0.75 | 0.95 |
| `IfcCivilElement` | 0.60 | 0.80 |
| `IfcColumn` | 0.55 | 0.90 |
| `IfcColumnStandardCase` | 0.55 | 0.90 |
| `IfcCourse` | 0.65 | 0.75 |
| `IfcDeepFoundation` | 0.50 | 0.80 |
| `IfcEarthworksCut` | 0.45 | 0.60 |
| `IfcEarthworksFill` | 0.45 | 0.60 |
| `IfcSlab` | 0.55 | 0.85 |
| `IfcSlabStandardCase` | 0.55 | 0.85 |

:contentReference[oaicite:7]{index=7}

### Road

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcCivilElement` | 0.45 | 0.60 |
| `IfcCourse` | 0.70 | 0.75 |
| `IfcEarthworksCut` | 0.55 | 0.70 |
| `IfcEarthworksFill` | 0.55 | 0.70 |
| `IfcKerb` | 0.65 | 0.60 |
| `IfcPavement` | 0.75 | 0.85 |
| `IfcRoadPart` | 0.60 | 0.80 |
| `IfcSign` | 0.40 | 0.40 |
| `IfcSignal` | 0.45 | 0.55 |

:contentReference[oaicite:8]{index=8}

### Rail

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcCivilElement` | 0.50 | 0.65 |
| `IfcEarthworksCut` | 0.50 | 0.60 |
| `IfcEarthworksFill` | 0.50 | 0.60 |
| `IfcFacilityPart` | 0.55 | 0.70 |
| `IfcRail` | 0.78 | 0.95 |
| `IfcSign` | 0.35 | 0.45 |
| `IfcSignal` | 0.65 | 0.80 |
| `IfcTrackElement` | 0.70 | 0.90 |

:contentReference[oaicite:9]{index=9}

---

# 3. Material Modifier

The material modifier is a secondary adjustment to susceptibility.

| Material string contains | Modifier |
|---|---:|
| `wood` or `timber` | +0.15 |
| `masonry` or `brick` | +0.10 |
| `glass` | +0.10 |
| `steel` or `metal` | +0.05 |
| `concrete` or `reinforced` | −0.05 |
| Other / unclassified | 0.00 |

The modifier is bounded between:

```text
−0.05 ≤ m_mat ≤ +0.15
```

The category/domain susceptibility remains the dominant term.

The values are author-defined ordinal adjustments, not material-specific calibrated failure probabilities. :contentReference[oaicite:10]{index=10}

---

# 4. Consequence Proxy

The consequence proxy combines:

1. baseline category/domain criticality; and
2. the relative quantity extent of the element.

The formulation is:

```text
C = Crit_base × (0.7 + 0.3 × q_hat)
```

where:

- `Crit_base` = criticality lookup value;
- `q_hat` = quantity extent normalised within the element's IFC category.

Thus:

```text
70% of consequence = baseline criticality
30% of consequence = relative quantity extent
```

The coefficients `0.7` and `0.3` are author-defined screening parameters. :contentReference[oaicite:11]{index=11}

---

## 4.1 Quantity Extent Normalisation

Quantity extent is normalised **within each IFC category**, rather than across the entire model.

For an element:

```text
q_hat = element_extent / maximum_extent_of_same_category
```

This means, for example:

```text
column → compared against largest column
slab   → compared against largest slab
beam   → compared against largest beam
```

A very large slab therefore does not suppress the relative extent of every smaller element category.

### Fallback hierarchy

If no element of a category has a readable quantity:

1. use the corpus-wide maximum extent as the normalisation denominator;
2. if that is also zero, set:

```text
q_hat = 0
```

In the final case:

```text
C = 0.7 × Crit_base
```

This is relevant to the M8 negative control, where no quantity data are available. :contentReference[oaicite:12]{index=12}

---

# 5. Raw Risk

After likelihood and consequence are computed:

```text
R_raw = min(1, max(0, L × C))
```

`R_raw` is the unadjusted risk proxy before BQI uncertainty propagation. :contentReference[oaicite:13]{index=13}

---

# 6. BQI-Based Uncertainty Propagation

The BQI is used as a deterministic uncertainty modifier.

Define:

```text
u = α × (1 − BQI)
```

where:

```text
α = 0.55
```

The uncertainty band is then:

```text
R_adj =
min(1, R_raw × (1 + u))

R_lower =
max(0, R_raw × (1 − u))
```

Equivalently:

```text
R_adj =
min(1, R_raw × [1 + α(1 − BQI)])

R_lower =
max(0, R_raw × [1 − α(1 − BQI)])
```

The three reported quantities are therefore:

```text
R_lower
R_raw
R_adj
```

`R_adj` is the **upper bound of the uncertainty band** and is the score used for screening ranking. :contentReference[oaicite:14]{index=14}

---

## 6.1 Interpretation of the Band

The band behaves as follows:

| Data quality | Effect |
|---|---|
| `BQI = 1` | No widening; `R_lower = R_raw = R_adj` |
| `0 < BQI < 1` | Symmetric widening around `R_raw` |
| `BQI = 0` | Maximum widening for the selected `α` |

The band width is:

```text
R_adj − R_lower
```

A narrow band indicates that the element remains risky even with relatively good information.

A wide band indicates that the risk estimate is strongly affected by information uncertainty.

The band is a **deterministic sensitivity envelope**, not a statistical confidence interval. No probabilistic interpretation is intended. :contentReference[oaicite:15]{index=15}

---

## 6.2 Why Ranking Uses `R_adj`

Screening ranks elements using the upper bound:

```text
Ranking score = R_adj
```

The rationale is conservative:

- ranking on `R_raw` would ignore the BQI uncertainty modifier;
- ranking on `R_lower` would incorrectly make poorly known elements appear safer;
- ranking on the midpoint would preserve the raw ordering and therefore remove the decision effect of the symmetric dilation.

Using the upper bound is therefore consistent with a conservative minimax screening interpretation. :contentReference[oaicite:16]{index=16}

---

# 7. Risk Labels

After calculating `R_adj`, the elements are sorted in descending order.

Two dynamic label thresholds are then calculated from the distribution of `R_adj`.

## 7.1 High threshold

```text
T_high = max(P75(R_adj), 0.40)
```

where `P75` is the 75th percentile of the adjusted-risk distribution.

The absolute floor of `0.40` prevents the High category from disappearing on a uniformly low-risk or highly uncertain model.

---

## 7.2 Low threshold

```text
T_low =
min(
    max(P25(R_adj), 0.15),
    T_high − 0.01
)
```

where `P25` is the 25th percentile.

The `0.15` floor prevents the Low threshold from collapsing towards zero.

The `T_high − 0.01` constraint guarantees separation between the two thresholds.

These threshold floors are author-defined screening conventions. :contentReference[oaicite:17]{index=17}

---

## 7.3 Element Labels

For each element:

```text
R_adj ≥ T_high
    → High

T_low ≤ R_adj < T_high
    → Medium

R_adj < T_low
    → Low
```

The label is therefore based on the **BQI-adjusted screening score**, not on `R_raw`.

---

# 8. Model-Level Screening Verdict

The model-level verdict combines:

1. model BQI confidence;
2. cross-pipeline element coverage; and
3. presence of High-risk elements.

The deterministic rule is:

| Condition | Verdict |
|---|---|
| Model confidence **LOW** OR coverage **FAIL** | **DATA UNRELIABLE** |
| Otherwise, model confidence **MEDIUM**, coverage **REVIEW**, or at least one High-risk element | **USE WITH CAUTION** |
| Otherwise | **RELIABLE** |

This is intentionally asymmetric: one failing condition is sufficient to withhold the RELIABLE verdict, while RELIABLE requires every condition to pass. :contentReference[oaicite:18]{index=18}

---

# 9. Element Coverage

Element coverage is kept as a separate diagnostic rather than being folded into BQI.

Coverage is calculated from the two pipelines' `GlobalId` sets:

```text
Coverage (%) =
shared elements
----------------------------- × 100
union of elements
```

The operational threshold is:

```text
95%
```

The threshold is an author-defined convention and was not swept in the reported sensitivity analysis. :contentReference[oaicite:19]{index=19}

Coverage is conceptually distinct from:

- D3, which asks whether expected quantity fields are present **within an element**;
- D4, which asks whether comparable quantity values **agree** between pipelines.

This separation is important because an element absent from one pipeline cannot contribute an element-level D4 score. The thesis therefore retains element coverage as an independent screening instrument.

---

# 10. Recommended Action

The report assigns a deterministic recommended action based on the uncertainty-band width of the highest-ranked element.

### Wide uncertainty band

Recommended action:

> Repair or improve BIM data before acting on the risk ranking.

Interpretation:

The element's apparent priority may be substantially affected by missing or unreliable information.

### Narrow uncertainty band

Recommended action:

> Inspect the identified element itself.

Interpretation:

The ranking is less sensitive to BIM information uncertainty, so attention can focus on the physical or functional risk represented by the element.

The report prints the reason for the recommendation so that the action is auditable rather than generated from a free-form language model. :contentReference[oaicite:20]{index=20}

---

# 11. Default Values and Fallbacks

The following defaults are used where no explicit lookup entry is available:

| Parameter | Default |
|---|---:|
| Default susceptibility | 0.30 |
| Default criticality | 0.50 |
| Default consequence when no readable extent | `0.7 × 0.50 = 0.35` |
| Unknown material modifier | 0.00 |
| `α` | 0.55 |
| High threshold floor | 0.40 |
| Low threshold floor | 0.15 |
| Element coverage threshold | 95% |

The published Annex II specifies the default susceptibility as `0.30` and the default criticality as `0.50 × 0.7` when an entity is absent from the domain table. :contentReference[oaicite:21]{index=21}

Unknown categories are treated conservatively rather than being given artificially high scores.

---

# 12. Parameter Provenance

The risk parameters have different origins and should not be interpreted as if they all had the same evidential status.

| Parameter | Value / Source | Provenance |
|---|---|---|
| Exposure lookup | Domain/category rules | Author-defined ordinal screening value |
| Susceptibility lookup | Annex II | Author-defined ordinal screening value |
| Criticality lookup | Annex II | Author-defined ordinal screening value |
| Material modifier | Material rules | Author-defined ordinal adjustment |
| Consequence blend | `0.7 / 0.3` | Author-defined screening convention |
| BQI coefficient `α` | `0.55` | Empirically characterised |
| High threshold floor | `0.40` | Author-defined convention |
| Low threshold floor | `0.15` | Author-defined convention |
| Coverage threshold | `95%` | Author-defined convention |
| QTO agreement tolerances | `10^-10`, `0.01%`, `1%` | Author-defined fixed thresholds |

None of the lookup values should be described as empirical failure probabilities or calibrated field-data coefficients. The thesis explicitly characterises them as ordinal screening parameters. :contentReference[oaicite:22]{index=22}

---

# 13. Sensitivity and Calibration Status

The thesis characterises the sensitivity of:

- BQI weights;
- `α`; and
- confidence-band boundaries.

The lookup values for exposure, susceptibility, criticality, and material modifiers were **not** independently swept.

The thesis therefore treats the lookup tables as a transparent, version-controlled engineering judgement rather than as empirically calibrated risk probabilities.

Calibration against field deterioration data is identified as future work. :contentReference[oaicite:23]{index=23}

---

# 14. Worked Example

For the worked `IfcWall` example in M1:

```text
BQI = 0.879
Likelihood proxy L = 0.180
Consequence proxy C = 0.560
α = 0.55
```

Raw risk:

```text
R_raw = 0.180 × 0.560
      ≈ 0.101
```

Relative uncertainty half-width:

```text
α(1 − BQI)
= 0.55 × (1 − 0.879)
≈ 0.067
```

Adjusted upper value:

```text
R_adj ≈ 0.108
```

Lower value:

```text
R_lower ≈ 0.094
```

The reported band width is approximately:

```text
0.108 − 0.094 = 0.014
```

The thesis reports the full-precision calculation as approximately `0.013` after rounding/display effects. :contentReference[oaicite:24]{index=24}

---

# 15. Interpretation Boundaries

The risk model should be interpreted carefully.

### It is a screening model, not a failure-probability model

`L` and `C` are proxies used for relative ranking.

They are not estimates of empirical probability of failure or loss.

### It is model-relative

The quantity extent is normalised within category, and the risk labels use percentile thresholds. Results should therefore primarily be interpreted within the analysed model.

### It is deterministic

Given the same IFC data, rule tables, configuration, and workflow version, the same risk outputs are produced.

### BQI affects uncertainty, not the raw physical proxy

The workflow deliberately computes:

```text
R_raw = L × C
```

before applying the BQI-based widening.

BQI therefore communicates uncertainty in the information supporting the score rather than directly pretending that poor data means a physically larger likelihood or consequence.

---

# 16. Repository Implementation

The risk rules are implemented in:

`workflows/thesis/n8n_ifc_dual_pipeline.json`

The main stages are:

```text
4.1: Exposure
        ↓
4.2: Likelihood
        ↓
4.3: Consequence
        ↓
4.4: Risk score
        ↓
4.5: Rank & label
```

### Node 4.1 — Exposure

Maps IFC category/domain and location-related information to the exposure score.

### Node 4.2 — Likelihood

Calculates:

```text
L = E × (S_base + m_mat)
```

with clamping to `[0, 1]`.

### Node 4.3 — Consequence

Calculates:

```text
C = Crit_base × (0.7 + 0.3 × q_hat)
```

### Node 4.4 — Risk score

Calculates:

```text
R_raw
R_lower
R_adj
uncertainty_band
```

using `α = 0.55`.

### Node 4.5 — Rank & label

Sorts elements by `R_adj`, calculates the percentile-based thresholds, and assigns:

```text
High / Medium / Low
```

The final HTML report then combines these element-level results with BQI, coverage, and SRCC evidence.

---

# 17. Verification

The risk-screening results are checked through the repository's downstream analysis and verification outputs.

The thesis also demonstrates internal consistency using a worked element example and independently checks the exported sensitivity data.

The final workflow keeps the calculation path deterministic from:

```text
IFC properties
    ↓
L, C
    ↓
R_raw
    ↓
BQI propagation
    ↓
R_lower / R_adj
    ↓
ranking
    ↓
risk label
    ↓
screening verdict
```

The workflow therefore contains no generative component between extracted data and the final risk score. :contentReference[oaicite:25]{index=25}

---

# 18. Limitations

The principal limitations of the current risk rules are:

1. The lookup values are ordinal engineering judgements rather than field-calibrated probabilities.
2. The exposure, susceptibility, and criticality lookup values were not independently swept.
3. The quantity-comparison thresholds are fixed parameters.
4. The element coverage threshold of 95% was not swept.
5. The risk model is intended for relative screening rather than cross-project probability calibration.
6. The small synthetic corpus does not support statistical claims about industrial asset populations.

The thesis identifies calibration on real project data and extension of the lookup/rule coverage as further developments. :contentReference[oaicite:26]{index=26}

---

## Canonical Sources

The formal risk-screening methodology is defined in:

- **Thesis Chapter 3, Section 3.6 — Uncertainty-Aware Risk Screening**
- **Section 3.7.4 — Verdict Logic and Report**
- **Thesis Annex II — Risk Lookup Tables**

The corresponding executable implementation is:

`workflows/thesis/n8n_ifc_dual_pipeline.json`

The repository document should remain synchronized with the workflow version associated with the final thesis release.
