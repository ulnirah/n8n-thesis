# DDC Adaptation Notes

## Purpose

This document records how the original Data-Driven Construction (DDC) IFC workflow was used and adapted as the Pipeline A extraction path in this thesis.

The purpose is to preserve a clear boundary between:

1. the original DDC workflow artefacts,
2. the thesis-specific orchestration and analysis logic, and
3. the external DDC IFC Exporter used as the IFC-to-tabular conversion component.

This distinction is important for reproducibility and attribution. The thesis does not present the original DDC workflow as if it were newly developed here, nor does it claim ownership of the closed-source conversion component.

---

## 1. Role of DDC in the Thesis

The thesis evaluates uncertainty-aware risk screening from imperfect BIM/IFC data using two independent extraction paths.

Pipeline A uses the DDC IFC Exporter to convert an IFC model into a tabular representation.

Pipeline B uses IfcOpenShell through the thesis extraction script.

The two pipelines are then compared downstream using shared identifiers and quantity information. Their agreement contributes to the D4 component of the Building Quality Index (BQI).

Conceptually:

```text
                         IFC model
                            |
             +--------------+--------------+
             |                             |
             v                             v
       Pipeline A                     Pipeline B
       DDC exporter                  IfcOpenShell
             |                             |
             v                             v
      tabular extraction             JSON extraction
             |                             |
             +--------------+--------------+
                            |
                            v
                   QTO comparison
                            |
                            v
                     BQI calculation
                            |
                            v
                     Risk screening
```

The DDC path therefore provides one independent representation of the source model. It is not the complete thesis methodology by itself.

---

## 2. Original DDC Artefacts

The repository contains the original DDC workflow JSON files under:

```text
workflows/ddc-base/
```

These files are retained as reference artefacts.

They are preserved separately from the thesis-specific workflow because the repository should make it possible to distinguish:

- original DDC workflow material,
- external DDC conversion functionality, and
- thesis-authored logic.

The original DDC workflow collection should therefore be treated as upstream reference material rather than as a set of thesis-authored workflows.

The DDC files are not presented here as five independent thesis workflows. The thesis uses the DDC IFC Exporter as one extraction component within a larger integrated workflow.

---

## 3. External DDC IFC Exporter

### 3.1 Function

Pipeline A uses the DDC IFC Exporter to convert an IFC file into an Excel/tabular representation.

In the thesis workflow, this conversion provides the source data used for comparison with Pipeline B.

The exporter is therefore part of the extraction stage only.

It does not determine:

- BQI weights,
- BQI aggregation,
- QTO agreement thresholds,
- SRCC sensitivity analysis,
- risk-score propagation,
- confidence labels,
- model verdicts, or
- final reporting rules.

Those downstream functions belong to the thesis-specific analysis pipeline.

---

### 3.2 Closed component boundary

The DDC IFC Exporter is treated as a closed or externally provided component.

This creates an explicit reproducibility boundary:

```text
IFC source
   |
   v
[DDC IFC Exporter]
   |
   v
tabular extraction
   |
   v
[thesis-controlled comparison and scoring]
```

The exporter affects the extraction result available to the thesis pipeline, but the transformation from extracted data to BQI and risk results is controlled by the thesis workflow and supporting scripts.

Accordingly, the repository does not claim that the DDC exporter itself is fully reproducible from source code within this repository.

The thesis reproducibility claim applies to the logic implemented after the extraction boundary and to the configuration and provenance needed to reproduce the analysis.

---

## 4. Thesis-Specific Adaptation

The thesis adaptation is primarily an integration and analysis layer around the DDC extraction output.

The thesis workflow adds the following functions after extraction:

### 4.1 Normalisation

The extracted DDC representation is transformed into the internal structure required for comparison with Pipeline B.

The workflow identifies common element keys, particularly `GlobalId`, and maps relevant property and quantity information into the comparison structure.

---

### 4.2 Spatial filtering

Spatial or non-target records are filtered before element-level comparison.

The purpose is to ensure that the comparison operates on the intended physical/model elements rather than treating project, site, building, storey, or other structural/spatial records as equivalent analytical elements.

This filtering is part of the thesis pipeline and should not be interpreted as a modification of the original DDC exporter.

---

### 4.3 Pipeline tagging

Records from the two extraction paths are explicitly identified by pipeline.

The workflow uses pipeline labels so that downstream processing can distinguish:

```text
A_ddc
B_ifcopenshell
```

This makes the source of each extracted observation explicit during comparison and diagnostic analysis.

---

### 4.4 Cross-pipeline matching

The thesis matches corresponding elements between Pipeline A and Pipeline B using `GlobalId`.

This creates the basis for cross-pipeline QTO comparison.

For each relevant quantity, the workflow evaluates whether the values agree exactly, negligibly, or differ materially.

The comparison is therefore performed after both extraction paths have produced their outputs.

---

### 4.5 QTO comparison

The DDC-derived quantity values are not treated as ground truth.

Instead, they are compared with the corresponding values obtained independently through IfcOpenShell.

The comparison supports the agreement dimension:

\[
D_4 = \frac{N_{\mathrm{agree}}}{N_{\mathrm{comparison}}}
\]

where agreement includes exact or negligible differences according to the thesis-defined comparison rules.

This design is important because neither extraction path is assumed to be an authoritative ground-truth quantity source.

---

## 5. What Was Not Adapted from DDC

The following thesis components are not inherited from the original DDC workflow:

| Thesis component | Status |
|---|---|
| D1 property completeness | Thesis-specific |
| D2 property validity | Thesis-specific |
| D3 QTO coverage | Thesis-specific |
| D4 cross-pipeline agreement | Thesis-specific |
| BQI weights | Thesis-specific |
| BQI aggregation | Thesis-specific |
| QTO agreement thresholds | Thesis-specific |
| SRCC sensitivity analysis | Thesis-specific |
| Fault-injection framework | Thesis-specific |
| Confidence categories | Thesis-specific |
| BQI-driven risk dilation | Thesis-specific |
| Risk ranking | Thesis-specific |
| Model-level verdict | Thesis-specific |
| Deterministic risk-register generation | Thesis-specific |
| n8n orchestration of the full analysis | Thesis-specific |

The DDC contribution is therefore concentrated at the extraction interface used for Pipeline A.

---

## 6. Relationship to the IfcOpenShell Pipeline

The DDC exporter and IfcOpenShell are intentionally used as two independent extraction paths.

Pipeline A:

```text
IFC
  ↓
DDC IFC Exporter
  ↓
tabular representation
```

Pipeline B:

```text
IFC
  ↓
IfcOpenShell
  ↓
thesis extraction script
  ↓
structured JSON
```

The purpose of maintaining two paths is not to establish that one library is correct and the other is incorrect.

Instead, their outputs provide independent observations that can be compared downstream.

This independence is especially important for D4 because a shared transformation error could otherwise appear as agreement.

---

## 7. Single-File and Dual-File Operation

The thesis workflow supports two experimental configurations.

### Single-file configuration

The same IFC variant is provided to both extraction paths:

```text
                    faulted IFC
                    /         \
                   /           \
                  v             v
              Pipeline A    Pipeline B
```

This configuration is used for faults whose effects can be evaluated within each pipeline independently.

---

### Dual-file configuration

For faults designed to test cross-pipeline agreement, the baseline file is supplied to Pipeline A while the faulted variant is supplied to Pipeline B:

```text
                     baseline IFC
                          |
                          v
                    Pipeline A


                  faulted IFC
                       |
                       v
                 Pipeline B
```

This configuration is used for the F4 and F6 experiments described in the thesis.

It allows the injected difference to occur between the two extraction inputs, making an agreement-based effect observable.

Without this separation, a shared mutation can propagate through both consumers and produce artificial agreement.

---

## 8. DDC Output and BQI Interpretation

The DDC output is an observation of model information through one extraction path.

It should not be interpreted as:

- a complete representation of IFC semantics,
- a definitive statement of model quality,
- a ground-truth quantity database, or
- a calibrated measure of physical building reliability.

The BQI instead measures the quality of information that can be extracted and compared at the point of analysis.

Consequently, an agreement between DDC and IfcOpenShell increases confidence in the extracted information but does not prove that both pipelines are correct relative to an external ground truth.

Similarly, disagreement does not automatically identify which pipeline is wrong.

---

## 9. Reproducibility Boundary

The thesis workflow is designed so that the DDC dependency is visible rather than hidden.

The reproducibility chain is:

```text
source IFC
    |
    +--> Pipeline A: DDC IFC Exporter
    |
    +--> Pipeline B: IfcOpenShell + extract_ifc.py
    |
    v
cross-pipeline comparison
    |
    v
BQI
    |
    v
risk screening
    |
    v
risk register / sensitivity outputs
```

The thesis-controlled stages include:

- experimental configuration,
- fault definitions,
- severity levels,
- mutation manifests,
- Pipeline B extraction,
- comparison logic,
- BQI calculation,
- sensitivity analysis,
- risk-screening rules,
- confidence classification, and
- report generation.

The DDC exporter remains an external dependency at the Pipeline A extraction boundary.

---

## 10. Repository Organisation

The repository separates DDC reference material from thesis-specific implementation:

```text
workflows/
├── ddc-base/
│   ├── README.md
│   └── original DDC workflow JSON files
│
└── thesis/
    ├── README.md
    └── n8n_ifc_dual_pipeline_v16.json
```

This separation is deliberate.

`workflows/ddc-base/` preserves the upstream workflow artefacts used as the basis for the extraction path.

`workflows/thesis/` contains the integrated workflow used for the thesis experiments.

The two directories should not be merged because doing so would make provenance and authorship less transparent.

---

## 11. Adaptation Principles

The DDC adaptation follows four principles.

### 11.1 Preserve the upstream boundary

The thesis does not rewrite the DDC exporter or represent its internal implementation as thesis-authored code.

### 11.2 Keep downstream logic deterministic

Once extraction outputs are available, the comparison, BQI, risk, and reporting stages are controlled by explicit rules and configuration.

### 11.3 Record provenance

The thesis records the configuration and software context needed to interpret Pipeline A results, while acknowledging the external exporter dependency.

### 11.4 Avoid ground-truth assumptions

DDC output is treated as one independent observation rather than an unquestioned reference dataset.

---

## 12. Limitations

The DDC adaptation introduces several limitations.

### 12.1 External conversion dependency

Because the DDC IFC Exporter is an external component, its internal implementation is outside the thesis repository.

### 12.2 Extraction-specific behaviour

Differences between Pipeline A and Pipeline B may arise from legitimate differences in schema interpretation, property extraction, quantity handling, or filtering.

Therefore, disagreement should be interpreted as an observable extraction discrepancy rather than automatically as an error.

### 12.3 No independent QTO ground truth

The cross-pipeline comparison establishes agreement between two extraction paths, not absolute correctness against independently measured quantities.

### 12.4 Scope of supported rules

The thesis validation and BQI rules operate on the explicitly defined property and quantity sets. They are not a universal validator for every IFC entity, property set, or infrastructure domain.

---

## 13. Practical Reproduction Notes

To reproduce the thesis workflow:

1. Use the corpus and fault variants described in `sample-models/`.
2. Ensure the DDC IFC Exporter is available for Pipeline A.
3. Use the thesis `n8n_ifc_dual_pipeline` workflow from `workflows/thesis/`.
4. Use the repository's `scripts/extract_ifc.py` for Pipeline B.
5. Apply the configuration defined in the workflow before execution.
6. Preserve the same single-file or dual-file configuration used by the corresponding experiment.
7. Record the resulting workflow configuration, repository commit, and input-file hashes for provenance.

The exact software/version information and experiment provenance should be interpreted together with the thesis methodology and annexes.

---

## 14. Relationship to the Thesis

This document corresponds to the methodological boundary described in the thesis between the external DDC extraction component and the thesis-controlled validation, comparison, scoring, and screening stages.

For the authoritative definitions of the implemented scoring system, use:

- [`bqi-definition.md`](bqi-definition.md)
- [`validation-ruleset.md`](validation-ruleset.md)
- [`risk-rules-table.md`](risk-rules-table.md)

For the experimental corpus and fault construction, use:

- [`../sample-models/README.md`](../sample-models/README.md)
- [`../sample-models/fault-injected/README.md`](../sample-models/fault-injected/README.md)

For the integrated workflow description, use:

- [`../workflows/thesis/README.md`](../workflows/thesis/README.md)

---

## 15. Provenance Statement

The DDC workflow and IFC exporter are treated as external/upstream components of the thesis pipeline.

The repository therefore distinguishes clearly between:

```text
UPSTREAM / EXTERNAL
    DDC workflow
    DDC IFC Exporter
          |
          v
THESIS-CONTROLLED
    normalisation
    matching
    QTO comparison
    BQI
    sensitivity analysis
    risk screening
    reporting
```

This separation is part of the reproducibility design of the thesis.

The goal is not to remove external dependencies, but to make their location, function, and limits explicit.
