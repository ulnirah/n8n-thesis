# Documentation

This folder documents the rules, parameters and provenance behind the thesis workflow and scripts. It is a practical reference for reading and reproducing the implementation. The formal definitions are in the thesis, mainly Chapter 3 and Annexes I–III.

---

## Documents

| File | Covers | Thesis reference |
|---|---|---|
| [`bqi-definition.md`](bqi-definition.md) | The BIM Quality Index: four dimensions, element and model scores, weights, confidence bands, worked example | Section 3.3, Annex I |
| [`risk-rules-table.md`](risk-rules-table.md) | Risk screening: likelihood and consequence proxies, lookup tables, uncertainty band, labels, verdict, recommended action | Sections 3.6, 3.7.4, Annex II |
| [`validation-ruleset.md`](validation-ruleset.md) | The property and quantity rules behind D1–D4, quantity comparison classes, element coverage, schema and domain detection | Sections 3.2, 3.3.2, 3.4, 3.7.4, Annex I |
| [`ddc-adaptation-notes.md`](ddc-adaptation-notes.md) | How the external DDC IFC Exporter is used in Pipeline A, and where the thesis logic begins | Sections 3.2, 3.7 |

---

## `bqi-definition.md`

Defines the **BIM Quality Index (BQI)**, a continuous, weighted quality score computed per element from two independent extraction pipelines and averaged to the model.

| Dimension | Question | Weight |
|---|---|---:|
| D1 Completeness | Are the required properties present? | 0.35 |
| D2 Validity | Are the values usable, not empty or UNSET? | 0.25 |
| D3 QTO coverage | Are the expected quantities present? | 0.20 |
| D4 Cross-pipeline agreement | Do the two pipelines agree on the quantities? | 0.20 |

It also covers the fallback rules, the confidence bands (HIGH ≥ 0.85, MEDIUM 0.60–0.85, LOW < 0.60), a worked example, parameter provenance and known limitations.

---

## `risk-rules-table.md`

Defines the deterministic risk-screening rules (workflow nodes 4.1–4.5) and the verdict logic of the report:

```text
R_raw   = L × C
R_adj   = R_raw × [1 + α(1 − BQI)]
R_lower = R_raw × [1 − α(1 − BQI)]

α = 0.55
```

It covers:

- the exposure, susceptibility, criticality and material modifier lookup tables for each domain;
- the quantity-extent normalisation used in the consequence proxy;
- why ranking uses the conservative upper value `R_adj`;
- the High/Medium/Low label thresholds, with their absolute floors of 0.40 and 0.15;
- the model-level screening verdict and the fixed-rule recommended action; and
- defaults, fallbacks and the calibration status of each value.

The lookup values are author-defined ordinal screening parameters, not calibrated failure probabilities.

---

## `validation-ruleset.md`

Documents the rules that decide whether extracted information counts as complete, valid and in agreement. These rules are specific to the thesis; they do not reproduce the original DDC validation workflow.

It covers:

- required properties and expected quantities per IFC category;
- property and quantity name matching;
- the D1–D4 calculations, including fallback behaviour;
- the quantity comparison classes used by D4;
- element coverage and its severity classes (critical, needs review, probably harmless);
- elements excluded from scoring;
- schema and domain detection; and
- rule coverage and limitations.

In the thesis release, one rule table covering twelve building entities is applied to both IFC 4 and IFC 4.3 models. The detected schema selects the spatial types used in extraction and the domain used for the risk lookup tables, and infrastructure entities do not yet carry quality rules (thesis Sections 3.3.4 and 5.5).

---

## `ddc-adaptation-notes.md`

Records the provenance boundary between the external **DataDrivenConstruction (DDC)** tooling and the thesis implementation.

| External (DDC) | Thesis-specific |
|---|---|
| DDC IFC Exporter (IFC → XLSX), used as a closed binary | Dual-pipeline orchestration in n8n |
| Original DDC n8n workflows, kept in [`../workflows/ddc-base/`](../workflows/ddc-base/) | IfcOpenShell extraction (Pipeline B) |
| | GlobalId matching, QTO comparison and SRCC |
| | BQI scoring and element coverage |
| | Fault injection, including the dual-file configuration |
| | Uncertainty-aware risk screening and reporting |

It also describes the normalisation and tagging applied to the DDC output, single-file and dual-file operation, environment dependencies, and practical reproduction notes.

---

## Relationship to the Executable Artefacts

These documents describe the implementation; they do not replace it. Read them together with:

- [`../workflows/thesis/`](../workflows/thesis/): the n8n workflow, where the BQI, risk and reporting logic run in Code nodes;
- [`../scripts/`](../scripts/): extraction, fault injection, verification and analysis scripts; and
- [`../sample-models/`](../sample-models/): baseline and fault-injected IFC inputs.

If a document and the executable artefact disagree, the workflow export and scripts of the tagged release are authoritative for what was run, and the thesis is authoritative for how it is interpreted.

---

## Versioning

The documents are versioned together with the workflow and scripts. The current release is **`v1.0.2`**, which completes the documentation; its computational content is the same as **`v1.0.1`**, the release cited in the thesis (Annex III). All values in these documents (weights, α, thresholds and lookup tables) match the thesis.
