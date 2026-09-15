# Documentation

This folder contains the methodological and provenance documentation supporting the thesis computational artefacts.

These documents complement the executable workflow and scripts by making the scoring rules, risk-screening assumptions, schema-aware decisions, and external-tool adaptations explicit and auditable.

The documents are intended to remain consistent with the final thesis, particularly:

- the BQI rule tables;
- the risk lookup tables;
- the n8n dual-pipeline workflow;
- the fault-injection methodology; and
- the distinction between external DDC infrastructure and thesis-specific contributions.

---

## Documents

| File | Role | Description |
|---|---|---|
| `bqi-definition.md` | Core methodology | Defines the four BQI dimensions, element-level scoring, model aggregation, weights, and confidence interpretation |
| `risk-rules-table.md` | Core methodology | Defines the deterministic exposure, likelihood, consequence, and uncertainty-aware risk-screening rules |
| `validation-ruleset.md` | Supporting methodology | Documents the schema-aware IFC property and quantity rules used to evaluate information quality |
| `ddc-adaptation-notes.md` | Provenance | Documents how the external DDC infrastructure is incorporated into the thesis Pipeline A and where thesis-specific logic begins |

---

## Document Descriptions

### `bqi-definition.md`

Defines the **BIM Quality Index (BQI)** used in the thesis.

The BQI is a continuous weighted quality measure composed of four dimensions:

- **D1 — Property completeness**
- **D2 — Property validity**
- **D3 — QTO coverage**
- **D4 — Cross-pipeline agreement**

The document should describe:

- element-level dimension scoring;
- model-level aggregation;
- the BQI weighting scheme;
- confidence bands;
- treatment of missing or unavailable information; and
- the relationship between BQI and downstream uncertainty.

The reported baseline weighting is:

| Dimension | Weight |
|---|---:|
| D1 — Completeness | 0.35 |
| D2 — Validity | 0.25 |
| D3 — QTO Coverage | 0.20 |
| D4 — QTO Agreement | 0.20 |

The BQI is computed from the dual-pipeline extraction architecture rather than from a single binary validation verdict.

---

### `risk-rules-table.md`

Defines the deterministic rules used by the uncertainty-aware risk-screening block.

The document should describe:

- exposure rules by IFC element/domain;
- susceptibility and likelihood assumptions;
- consequence / criticality rules;
- the QTO-based extent factor;
- raw risk calculation;
- BQI-dependent uncertainty widening;
- lower and adjusted risk values;
- ranking on the conservative upper edge; and
- deterministic screening labels and recommended actions.

The core risk construction is:

```text
R_raw = Likelihood × Consequence
```

with BQI-dependent widening controlled by:

```text
α(1 − BQI)
```

and the conservative adjusted value:

```text
R_adj = R_raw × [1 + α(1 − BQI)]
```

The reported operating value of the uncertainty coefficient is:

```text
α = 0.55
```

The complete lookup tables and parameter provenance should remain aligned with the thesis risk methodology.

---

### `validation-ruleset.md`

Documents the **schema-aware information-quality rules** used by the BQI implementation.

This document is not intended to reproduce the original DDC validation workflow. It describes the thesis-specific rules that determine whether extracted BIM information is complete, usable, and suitable for downstream quality assessment.

The documentation should cover, where applicable:

- IFC schema-aware rule selection;
- required properties by IFC element type;
- property-value validity;
- expected quantity fields;
- quantity coverage;
- treatment of unsupported or fallback element types;
- material and metadata handling relevant to screening; and
- relationships between the rule tables and the BQI dimensions.

The executable implementation is contained in the thesis workflow and associated extraction/scoring code.

The formal rule tables correspond to the BQI methodology documented in the thesis **Annex I**.

---

### `ddc-adaptation-notes.md`

Documents the relationship between the external **DataDrivenConstruction (DDC)** infrastructure and the thesis-specific implementation.

The document should make the provenance boundary explicit by distinguishing:

**External / adapted infrastructure**

- DDC IFC conversion;
- DDC `IfcExporter`;
- DDC tabular / XLSX extraction pathway;
- selected DDC n8n workflow concepts.

**Thesis-specific implementation**

- dual-pipeline orchestration;
- IfcOpenShell extraction pathway;
- GlobalId-based cross-pipeline matching;
- QTO comparison;
- BQI scoring;
- SRCC analysis;
- element coverage analysis;
- fault-injection methodology;
- uncertainty-aware risk screening;
- sensitivity exports; and
- deterministic reporting.

The notes should document:

- the original DDC component being used;
- how it is incorporated into Pipeline A;
- configuration changes required for the IFC corpus;
- assumptions inherited from the external tool;
- limitations or environment dependencies; and
- where the thesis implementation diverges from the original DDC functionality.

This document provides the provenance bridge between [`workflows/ddc-base/`](../workflows/ddc-base/) and [`workflows/thesis/`](../workflows/thesis/).

---

## Relationship to the Executable Artefacts

The documentation in this folder is descriptive and methodological.

The executable implementation is distributed across:

- [`../workflows/thesis/`](../workflows/thesis/) — integrated n8n workflow;
- [`../scripts/`](../scripts/) — extraction, fault injection, verification, and analysis scripts;
- [`../sample-models/`](../sample-models/) — baseline and fault-injected IFC inputs.

The documentation should therefore be read together with the corresponding executable artefact rather than treated as an independent implementation.

---

## Thesis Mapping

The documentation corresponds broadly to the following methodological components:

| Documentation | Main thesis component |
|---|---|
| `bqi-definition.md` | BQI framework and quality dimensions |
| `risk-rules-table.md` | Risk-screening model and uncertainty propagation |
| `validation-ruleset.md` | Schema-aware scoring and IFC information-quality rules |
| `ddc-adaptation-notes.md` | External-tool provenance and Pipeline A adaptation |

The detailed formal definitions and provenance are preserved in the thesis annexes, while these repository documents provide a practical implementation-oriented reference for reproducing the computational artefacts.

---

## Reproducibility and Versioning

The documentation should be versioned together with the workflow and scripts used for the reported experiments.

For the final thesis release:

- methodological values should match the thesis;
- executable rules should match the documented rules;
- external dependencies should be identified explicitly; and
- the final repository release should preserve the exact versioned state used for the reported results.

The final release tag should therefore be treated as the authoritative snapshot of the thesis computational documentation.
