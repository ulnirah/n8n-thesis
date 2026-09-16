# Risk Rules Table

This document defines the deterministic rules of the thesis **uncertainty-aware risk screening model**, as implemented in workflow nodes 4.1–4.5 and in the verdict logic of the report.

The model is a BIM-only, relative screening framework. It does **not** estimate probabilities of failure and is not calibrated against field deterioration data. Exposure, susceptibility, criticality and material values are ordinal engineering screening parameters, used to produce a reproducible ranking within the analysed model.

```text
IFC properties
      ↓
Exposure E (node 4.1)
      ↓
Likelihood proxy L (node 4.2)
      ↓
Consequence proxy C (node 4.3)
      ↓
R_raw = L × C
      ↓
BQI-dependent uncertainty band (node 4.4)
      ↓
R_lower / R_raw / R_adj
      ↓
Ranking on R_adj and labels (node 4.5)
      ↓
Screening verdict and recommended action (report)
```

---

## 1. Core Risk Formulation

```text
R_raw = min(1, max(0, L × C))
```

where `L` is the likelihood proxy and `C` the consequence proxy. `R_raw` is the deterministic risk estimate before information-quality uncertainty is applied.

---

## 2. Domain Selection

Every lookup table below exists per domain: Building, Bridge, Road and Rail. The domain comes from node 2.5:

- **IFC 4.3 files:** the domain is inferred from the element and spatial types present (for example `IfcBridge`/`IfcBearing` → Bridge, `IfcRoad`/`IfcPavement` → Road). A file with both infrastructure and building indicators is classed as **Mixed** and scored with the Building tables, with a domain warning.
- **IFC 4 files:** IFC 4 has no infrastructure spatial entities, so these files are assigned the **Building** domain.

In the thesis corpus, M1–M7 are scored with the Building tables. This includes M5 and M7 (IFC 4) and M6, the IFC 4.3 bridge, which contains building element types and is therefore classed as Mixed. Only M8, the IFC 4.3 road, is scored with an infrastructure table (Road).

---

## 3. Likelihood Proxy

```text
L = min(1, max(0, E × (S_base + m_mat)))
```

| Symbol | Meaning |
|---|---|
| `E` | Exposure score |
| `S_base` | Susceptibility for the IFC category and domain |
| `m_mat` | Material modifier |

`L` is dimensionless and used for relative screening only.

### 3.1 Exposure

Exposure answers *how exposed is the element?*, kept separate from *how susceptible is this element type?*

`E` is read from a domain table by IFC category. For five envelope types, the Building table holds separate values for internal and external elements, selected with `IsExternal`; all other entries are a single value. Categories not in the table receive the default `E = 0.30`.

**Building**

| IFC Entity | Internal | External |
|---|---:|---:|
| `IfcRoof` | 0.90 | 0.90 |
| `IfcWall`, `IfcWallStandardCase` | 0.45 | 0.40 |
| `IfcWindow` | 0.50 | 0.45 |
| `IfcDoor` | 0.40 | 0.35 |
| `IfcCurtainWall` | 0.60 | 0.55 |

| IFC Entity | Exposure |
|---|---:|
| `IfcChimney` | 0.80 |
| `IfcFooting` | 0.65 |
| `IfcStair`, `IfcStairFlight`, `IfcPile` | 0.60 |
| `IfcColumn`, `IfcColumnStandardCase`, `IfcSlab`, `IfcSlabStandardCase`, `IfcRamp`, `IfcRampFlight` | 0.55 |
| `IfcBeam`, `IfcBeamStandardCase` | 0.50 |
| `IfcPlate` | 0.45 |
| `IfcMember` | 0.40 |
| `IfcCovering`, `IfcRailing` | 0.35 |
| `IfcBuildingElementProxy` | 0.30 |
| `IfcSpace` | 0.20 |
| `IfcFurnishingElement`, `IfcFurniture` | 0.10 |

**Bridge**

| IFC Entity | Exposure |
|---|---:|
| `IfcBridgePart` | 0.85 |
| `IfcBearing` | 0.80 |
| `IfcCourse` | 0.75 |
| `IfcCivilElement`, `IfcBeam`, `IfcBeamStandardCase` | 0.70 |
| `IfcColumn`, `IfcColumnStandardCase`, `IfcSlab`, `IfcSlabStandardCase` | 0.65 |
| `IfcDeepFoundation` | 0.60 |
| `IfcEarthworksCut`, `IfcEarthworksFill` | 0.50 |

**Road**

| IFC Entity | Exposure |
|---|---:|
| `IfcPavement` | 0.85 |
| `IfcCourse` | 0.80 |
| `IfcRoadPart` | 0.75 |
| `IfcKerb` | 0.70 |
| `IfcEarthworksCut`, `IfcEarthworksFill` | 0.60 |
| `IfcCivilElement` | 0.55 |
| `IfcSignal` | 0.50 |
| `IfcSign` | 0.45 |

**Rail**

| IFC Entity | Exposure |
|---|---:|
| `IfcRail` | 0.80 |
| `IfcTrackElement` | 0.75 |
| `IfcSignal` | 0.70 |
| `IfcFacilityPart` | 0.60 |
| `IfcCivilElement`, `IfcEarthworksCut`, `IfcEarthworksFill` | 0.55 |
| `IfcSign` | 0.40 |

The exposure tables are part of the released workflow; they are not listed in thesis Annex II.

### 3.2 Susceptibility and Criticality

`S_base` and `Crit_base` are looked up by IFC category and domain. The values are ordinal engineering judgements, frozen before the corpus was scored. Categories not in the table receive the defaults `S_base = 0.30` and `Crit_base = 0.50`.

**Building**

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcBeam`, `IfcBeamStandardCase` | 0.35 | 0.90 |
| `IfcBuildingElementProxy` | 0.30 | 0.50 |
| `IfcChimney` | 0.70 | 0.45 |
| `IfcColumn`, `IfcColumnStandardCase` | 0.35 | 1.00 |
| `IfcCovering` | 0.55 | 0.40 |
| `IfcCurtainWall` | 0.60 | 0.55 |
| `IfcDoor` | 0.55 | 0.50 |
| `IfcFooting` | 0.30 | 1.00 |
| `IfcFurnishingElement`, `IfcFurniture` | 0.20 | 0.10 |
| `IfcMember` | 0.35 | 0.65 |
| `IfcPile` | 0.25 | 1.00 |
| `IfcPlate` | 0.40 | 0.60 |
| `IfcRailing` | 0.40 | 0.35 |
| `IfcRamp`, `IfcRampFlight` | 0.45 | 0.60 |
| `IfcRoof` | 0.80 | 0.75 |
| `IfcSlab`, `IfcSlabStandardCase` | 0.40 | 0.85 |
| `IfcSpace` | 0.15 | 0.20 |
| `IfcStair`, `IfcStairFlight` | 0.50 | 0.65 |
| `IfcWall`, `IfcWallStandardCase` | 0.45 | 0.80 |
| `IfcWindow` | 0.65 | 0.50 |

**Bridge**

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcBeam`, `IfcBeamStandardCase` | 0.60 | 0.90 |
| `IfcBearing` | 0.85 | 1.00 |
| `IfcBridgePart` | 0.75 | 0.95 |
| `IfcCivilElement` | 0.60 | 0.80 |
| `IfcColumn`, `IfcColumnStandardCase` | 0.55 | 0.90 |
| `IfcCourse` | 0.65 | 0.75 |
| `IfcDeepFoundation` | 0.50 | 0.80 |
| `IfcEarthworksCut`, `IfcEarthworksFill` | 0.45 | 0.60 |
| `IfcSlab`, `IfcSlabStandardCase` | 0.55 | 0.85 |

**Road**

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcCivilElement` | 0.45 | 0.60 |
| `IfcCourse` | 0.70 | 0.75 |
| `IfcEarthworksCut`, `IfcEarthworksFill` | 0.55 | 0.70 |
| `IfcKerb` | 0.65 | 0.60 |
| `IfcPavement` | 0.75 | 0.85 |
| `IfcRoadPart` | 0.60 | 0.80 |
| `IfcSign` | 0.40 | 0.40 |
| `IfcSignal` | 0.45 | 0.55 |

**Rail**

| IFC Entity | Susceptibility | Criticality |
|---|---:|---:|
| `IfcCivilElement` | 0.50 | 0.65 |
| `IfcEarthworksCut`, `IfcEarthworksFill` | 0.50 | 0.60 |
| `IfcFacilityPart` | 0.55 | 0.70 |
| `IfcRail` | 0.75¹ | 0.95 |
| `IfcSign` | 0.35 | 0.45 |
| `IfcSignal` | 0.65 | 0.80 |
| `IfcTrackElement` | 0.70 | 0.90 |

¹ Thesis Annex II lists 0.78; the released workflow uses 0.75. No corpus model is scored with the Rail table, so no reported result is affected.

### 3.3 Material Modifier

A secondary adjustment to susceptibility, matched on the element's material string (first match wins):

| Material string contains | Modifier |
|---|---:|
| `wood` or `timber` | +0.15 |
| `masonry` or `brick` | +0.10 |
| `glass` | +0.10 |
| `steel` or `metal` | +0.05 |
| `concrete` or `reinforced` | −0.05 |
| Other or no material | 0.00 |

The modifier is bounded to `−0.05 ≤ m_mat ≤ +0.15`, so the category and domain susceptibility stays the dominant term. The values are author-defined ordinal adjustments, not calibrated material failure rates.

---

## 4. Consequence Proxy

```text
C = Crit_base × (0.7 + 0.3 × q_hat)
```

- `Crit_base` = criticality lookup value (Section 3.2)
- `q_hat` = quantity extent of the element, normalised within its IFC category

Seventy per cent of consequence comes from baseline criticality and thirty per cent from relative extent. Both coefficients are author-defined screening parameters.

### 4.1 Quantity Extent

Node 4.3 reads the extent from the first positive value among these fields, in this order:

```text
[BaseQuantities] GrossVolume
[BaseQuantities] GrossArea
[BaseQuantities] NetFloorArea
[Qto_SpaceBaseQuantities] NetFloorArea
[Dimensions] Volume
[Dimensions] Area
```

(`[BaseQuantities]` fields are accepted with a space or a dot after the bracket.) The extent is then normalised within the element's category:

```text
q_hat = element_extent / maximum_extent_in_same_category
```

so a column is compared with the largest column, not with the largest slab. If no element of the category has a readable extent, the model-wide maximum is used as the denominator, and `q_hat` evaluates to zero for that category.

**Corpus note.** None of the eight corpus models carries any of the fields above; their quantities are stored under element-specific sets such as `Qto_WallBaseQuantities`. `q_hat` is therefore zero for every element in the reported results, and consequence reduces to `C = 0.7 × Crit_base` throughout, not only in the negative control. Rankings within each model are driven by exposure, susceptibility, material and criticality.

---

## 5. BQI-Based Uncertainty Propagation

```text
u       = α × (1 − BQI)

R_adj   = min(1, R_raw × (1 + u))
R_lower = max(0, R_raw × (1 − u))
```

with `α = 0.55`, read from node 0.1 Config. (Node 4.4 falls back to 0.5 only if the Config value is missing.)

The node exports `R_lower`, `R_raw`, `R_adj` and the band width `R_adj − R_lower`. `R_adj` is the upper edge of the band and is the score used for ranking.

### 5.1 Interpreting the Band

| Data quality | Effect |
|---|---|
| `BQI = 1` | No widening: `R_lower = R_raw = R_adj` |
| `0 < BQI < 1` | Symmetric widening around `R_raw` |
| `BQI = 0` | Maximum widening for the chosen `α` (factor 1.55 on the upper edge) |

The cap at 1 binds only where `R_raw > 1 / (1 + α) = 0.645`; no element in the corpus reaches that value, so the dilation is strictly proportional in every reported result.

The band is a deterministic sensitivity envelope, not a statistical confidence interval.

### 5.2 Why Ranking Uses `R_adj`

- Ranking on the midpoint (`R_raw`) would ignore data quality, because the band is symmetric around it.
- Ranking on `R_lower` would make the least-known elements look safest.
- Ranking on `R_adj` treats a missed risk as costlier than an unnecessary review: a minimax screening rule.

---

## 6. Risk Labels

Node 4.5 sorts the elements by `R_adj` and derives two thresholds from the model's own score distribution. Percentiles are index-based: the scores are sorted ascending and `P_p = scores[floor(n × p)]`.

```text
T_high = max(P75(R_adj), 0.40)
T_low  = min(max(P25(R_adj), 0.15), T_high − 0.01)
```

| Condition | Label |
|---|---|
| `R_adj ≥ T_high` | High |
| `T_low ≤ R_adj < T_high` | Medium |
| `R_adj < T_low` | Low |

The construction combines a relative and an absolute component:

- the **percentile** terms keep the labels adaptive to each model's distribution;
- the **absolute floors** (0.40 and 0.15) stop a model in which no element carries meaningful risk from labelling its top quarter High anyway;
- the `T_high − 0.01` clamp guarantees the two thresholds cannot cross.

Labels use the BQI-adjusted score, so poor data can escalate an element. In the negative control M8, no raw score exceeds 0.40, but the factor 1.55 lifts the 16 elements with raw scores between 0.258 and 0.40 into High (thesis Section 4.5).

The floors are author-defined conventions and were not swept.

---

## 7. Element Coverage

Coverage is a separate diagnostic, not part of the BQI, computed in node 3.3 from the two pipelines' `GlobalId` sets:

```text
Coverage (%) = shared elements / union of elements × 100
```

The coverage verdict combines this percentage with the type of the unmatched elements:

| Condition | Coverage verdict |
|---|---|
| Any element of a critical type is found by only one pipeline | **FAIL** |
| Otherwise, any other element is unmatched, or coverage is below 95% | **REVIEW** |
| Otherwise | **PASS** |

Critical types are walls, slabs, beams and columns (with their StandardCase variants), roofs, doors, windows, spaces, stairs, stair flights, ramps, ramp flights, footings and piles. Non-physical constructs (openings, annotations, grids, virtual elements) never affect the verdict.

This is why M1 and M2 return FAIL at 77.78% while M3 and M4 return REVIEW at 88.89%. Coverage is kept separate because an element missing from one pipeline cannot contribute a D4 score. The 95% threshold is an author-defined convention and was not swept.

---

## 8. Model-Level Screening Verdict

| Condition | Verdict |
|---|---|
| Model BQI confidence **LOW**, or coverage **FAIL** | **DATA UNRELIABLE** |
| Otherwise, confidence **MEDIUM**, coverage **REVIEW**, or at least one High element | **USE WITH CAUTION** |
| Otherwise | **RELIABLE** |

One failing condition withholds RELIABLE; RELIABLE requires every condition to pass. On the thesis corpus every model returns DATA UNRELIABLE; thesis Table 4.8 shows by construction the inputs under which the other two states fire.

---

## 9. Recommended Action

The report derives a recommended action from fixed rules, based on the band width `R_adj − R_lower` of the top-ranked element:

| Band width | Treated as | Recommended action |
|---|---|---|
| `> 0.15` | Wide | Improve the model data before acting on the ranking; better data would sharpen the score |
| `≤ 0.15` | Narrow | Inspect the element itself; the score is driven by the element rather than by data gaps |

The report also names the missing properties and quantities that would most improve the data.

The 0.15 cut-off is an author-defined convention. Because absolute band width grows with `R_raw`, it separates data-driven from element-driven scores reliably only among elements of comparable raw risk. For example, the top element of M5 has BQI 0.325 but a low raw score (0.173), so its band width is 0.128 and it is reported as narrow.

---

## 10. Defaults and Fallbacks

| Parameter | Value | Applies when |
|---|---:|---|
| Default exposure | 0.30 | Category absent from the exposure table |
| Default susceptibility | 0.30 | Category absent from the susceptibility table |
| Default criticality | 0.50 | Category absent from the criticality table |
| Default consequence | 0.35 (`0.7 × 0.50`) | Element has no category |
| Default likelihood | 0.30 | Element has no category |
| Material modifier | 0.00 | Material absent or not recognised |

---

## 11. Parameter Provenance

| Parameter | Value | Provenance |
|---|---|---|
| Exposure lookup | Per category and domain (Section 3.1) | Author-defined ordinal; not swept |
| Susceptibility and criticality lookup | Annex II | Author-defined ordinal; not swept |
| Material modifier | −0.05 to +0.15 | Author-defined ordinal; not swept |
| Consequence blend | 0.7 / 0.3 | Author-defined convention; not swept |
| `α` | 0.55 | Empirically characterised (thesis Sections 3.6.4, 4.4.2) |
| Label floors | 0.40 / 0.15 | Author-defined convention (Section 3.6.3); not swept |
| Coverage threshold | 95% | Author-defined convention; not swept |
| Recommended-action cut-off | 0.15 band width | Author-defined convention; not swept |
| QTO comparison boundaries | 10⁻¹⁰, 0.01%, 1% | Author-defined constants; not swept |

None of these values is an empirical failure probability or a field-calibrated coefficient.

---

## 12. Sensitivity and Calibration Status

The thesis characterises the sensitivity of the BQI weights, `α` and the confidence-band boundaries (Section 4.4). The lookup tables, material modifier, consequence blend, label floors and coverage threshold were not swept. Calibration against field deterioration data is further work (Section 6.3).

---

## 13. Worked Example

The `IfcWall` element `1AQAupaRP1txwK1AGiN61V` in M1 (thesis Section 3.3.5):

```text
BQI = 0.879    L = 0.180    C = 0.560 (= 0.7 × 0.80)    α = 0.55

R_raw          = 0.180 × 0.560           = 0.101
u              = 0.55 × (1 − 0.879)      = 0.067
R_adj          = 0.101 × 1.067           = 0.108
R_lower        = 0.101 × 0.933           = 0.094
band width     = 2 × R_raw × u           = 0.013
```

The band width computed at full precision is 0.013; subtracting the rounded bounds gives 0.014.

---

## 14. Interpretation Boundaries

**A screening model, not a failure-probability model.** `L` and `C` are proxies for relative ranking, not estimates of failure probability or loss.

**Model-relative.** Extent is normalised within category and labels use the model's own percentiles, so results are interpreted within the analysed model.

**Deterministic.** The same IFC data, rule tables, configuration and workflow version produce the same scores, bands and labels. There is no generative component between the extracted data and the risk register.

**BQI affects uncertainty, not the physical proxy.** `R_raw = L × C` is computed first; BQI only widens the band around it. Poor data is reported as uncertainty, not as a physically larger likelihood or consequence.

---

## 15. Repository Implementation

All rules are in `workflows/thesis/n8n_ifc_dual_pipeline.json`:

| Node | Step |
|---|---|
| 2.5 Detect domain | Infers the domain used to select the lookup tables |
| 3.3 Coverage Analysis | Coverage percentage and coverage verdict |
| 4.1 Exposure | `E` from the exposure table and `IsExternal` |
| 4.2 Likelihood | `S_base`, material modifier and `L` |
| 4.3 Consequence | `Crit_base`, extent normalisation and `C` |
| 4.4 Risk score | `R_raw`, `R_adj`, `R_lower`, band width |
| 4.5 Rank & label | Ranking, thresholds and High/Medium/Low labels |
| 5.1 Generate HTML | Verdict, recommended action and report |

The per-element `likelihood_score`, `consequence_score` and BQI dimension scores are exported in the sensitivity JSON, so every band and label can be recomputed offline (`scripts/sensitivity_analysis.py`, `scripts/alpha_characterization.py`).

---

## 16. Limitations

1. The lookup values are ordinal engineering judgements, not field-calibrated probabilities.
2. The lookup tables, material modifier, consequence blend, label floors and coverage threshold were not swept.
3. Exposure depends on `IsExternal` and category only.
4. The quantity-extent term reads a fixed list of generic quantity fields; in the corpus it never contributes (Section 4.1).
5. Only M8 is scored with an infrastructure table; M1–M7 use the Building tables (Section 2).
6. The model supports relative screening within a model, not probability calibration across projects.
7. The eight-model corpus does not support statistical claims about real asset populations.

---

## Canonical Sources

- Thesis Section 3.6: Uncertainty-Aware Risk Screening
- Thesis Section 3.7.4: Verdict Logic and Report
- Thesis Annex II: Risk Lookup Tables

This document describes the behaviour of repository release `v1.0.2`.
