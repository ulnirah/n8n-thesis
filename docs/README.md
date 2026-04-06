# Docs

This folder contains the written documentation that defines the methodological components of this thesis. These are living documents — they will be updated as the thesis progresses.

---

## Documents

| File | Status | Thesis Task | Description |
|------|--------|-------------|-------------|
| `bqi-definition.md` | 🔲 Not started | Task 3 | BQI scoring formula, weight assignments, and confidence label thresholds |
| `risk-rules-table.md` | 🔲 Not started | Task 4 | Likelihood proxy rules, consequence proxy rules, and uncertainty propagation logic |
| `validation-ruleset.md` | 🔲 Not started | Task 2 | IFC validation rules used in the adapted n8n_4 workflow |
| `ddc-adaptation-notes.md` | 🔲 Not started | Task 2 | Detailed notes on what was changed from DDC base workflows and why |

---

## Document Descriptions

### `bqi-definition.md`
Defines the BIM Quality Index (BQI) — the original scoring method developed in this thesis to quantify BIM trustworthiness.

Will include:
- Weighted scoring formula per element
- Aggregation method for model-level score
- List of validation checks and their weights
- Confidence label thresholds (High / Medium / Low)
- Rationale for weight choices

---

### `risk-rules-table.md`
Defines the uncertainty-aware risk screening model — the core original contribution of this thesis.

Will include:
- Likelihood proxy rules (element type, material, location tags → exposure assumptions)
- Consequence proxy rules (element role, criticality category, QTO extent)
- Risk score formula (likelihood × consequence)
- How BQI is incorporated as confidence bounds
- Missing-data penalties

---

### `validation-ruleset.md`
Documents the IFC validation rules implemented in the thesis workflow, adapted from the DDC validation framework for IFC-specific requirements.

Will include:
- Schema compliance checks (IFC4 vs IFC4.3)
- Required property sets per element type
- Naming convention rules
- Unit consistency checks
- Spatial structure checks (IfcRelContainedInSpatialStructure)
- QTO completeness checks (volume, area, length presence)

---

### `ddc-adaptation-notes.md`
Documents exactly what was changed from the DDC base workflows and why, making the boundary between given infrastructure and original contribution explicit.

Will include:
- Side-by-side comparison of DDC original vs thesis adapted nodes
- Reason for each change
- New nodes added and their purpose
- Known limitations of the DDC base that were worked around
