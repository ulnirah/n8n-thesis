# Scripts

This folder contains the Python and PowerShell scripts used alongside the n8n workflow.

Only one script runs **inside** the workflow: `extract_ifc.py`, which is Pipeline B. All the others run **offline**, before the workflow (fault injection) or on its outputs (verification and analysis). The BQI and risk logic itself runs in the workflow's Code nodes, not in these scripts.

---

## Script Inventory

| Script | Runs | Input | Output | Needs |
|---|---|---|---|---|
| `extract_ifc.py` | Inside the workflow (nodes 2.1–2.3) | One IFC file | JSON on standard output | IfcOpenShell |
| `fault_injection.py` | Before the campaign | Baseline IFC | Faulted IFC + manifest JSON | IfcOpenShell |
| `verify_exports.py` | After the campaign | `sensitivity-*.json` | Console report only | Standard library |
| `verify_exports.ps1` | After the campaign | `sensitivity-*.json` | Console report only | Windows PowerShell |
| `harvest_reports.ps1` | After the campaign | `risk-register-*.html` | `report_summary.csv` | Windows PowerShell |
| `fault_analysis.py` | After the campaign | Baseline and faulted `sensitivity-*.json` | `fault_analysis.csv` | Standard library |
| `sensitivity_analysis.py` | After the baselines | Baseline `sensitivity-*.json` | `sensitivity_results.csv` | Standard library |
| `alpha_characterization.py` | After the baselines | Baseline `sensitivity-*.json` | `alpha_characterization.csv` | Standard library |

---

## Requirements

- **Python 3.** Four of the six Python scripts use the standard library only.
- **IfcOpenShell 0.8.5**, for `extract_ifc.py` and `fault_injection.py`:

  ```bash
  pip install ifcopenshell==0.8.5
  ```

- **Windows PowerShell 5.1 or later**, for the two `.ps1` scripts.

No other packages (such as pandas or SciPy) are needed.

---

## `extract_ifc.py` — Pipeline B

Reads an IFC file with IfcOpenShell and prints one JSON document containing:

- `elements`: GlobalId, name, category, description, object type, tag and `is_external`;
- `quantities`: every quantity of every element;
- `properties` (with `--include-properties`): every property of every element, including quantity-set values;
- `materials` (with `--include-materials`): the material name of each element;
- `spatial`: the spatial hierarchy, using the IFC 4 or IFC 4.3 spatial types depending on the detected schema; and
- `metadata`: source file, schema, timestamp and counts.

Only the physical element types listed in `ELEMENT_TYPES` are extracted. `IfcZone` and `IfcSpatialZone` are deliberately left out, and types such as `IfcDiscreteAccessory` are not in the list (see [`../docs/validation-ruleset.md`](../docs/validation-ruleset.md), Section 18).

```bash
python scripts/extract_ifc.py sample-models/baseline/IFC4-Building-Structural.ifc --include-properties --include-materials
```

**How the workflow uses it.** Node 2.1 downloads the script from the `main` branch of this repository, Node 2.2 checks Python, and Node 2.3 runs it with both flags on `project_file_b` (dual-file runs) or `project_file`. On a new machine, edit the download folder in Node 2.1, which contains a fixed Windows path from the original workstation, so that it matches `script_dir` in Node 0.1 Config.

---

## `fault_injection.py` — Faulted Variants

Generates the six fault types (F1–F6) at a chosen rate, with a fixed seed, and writes a manifest JSON next to each variant.

```bash
# all 6 faults × 3 rates for one model
python scripts/fault_injection.py sample-models/baseline/IFC4-Building-Architecture.ifc --all --seed 42 --outdir faulted

# one fault at one rate
python scripts/fault_injection.py sample-models/baseline/IFC4-Building-Architecture.ifc --fault F1 --rate 0.25 --seed 42 --outdir faulted
```

| Option | Meaning | Default |
|---|---|---|
| `--all` | All six faults at 10%, 25% and 50% | — |
| `--fault F1`…`F6` | One fault type | — |
| `--rate` | Share of eligible elements to fault, e.g. `0.25` | — |
| `--seed` | Random seed | `42` |
| `--intensity light\|heavy` | Change the first matching field or all of them (F1–F3) | `light` |
| `--outdir` | Output folder | `faulted` |

F4 and F6 variants get the `_PIPELINE-B-ONLY` suffix. The fault definitions, target selection and a reproducibility check of the committed variants are in [`../sample-models/fault-injected/README.md`](../sample-models/fault-injected/README.md).

---

## `verify_exports.py` and `verify_exports.ps1` — Export Checks

Both scripts perform the same structural checks on every `sensitivity-*.json` found under a folder, recursively:

- the file parses as a JSON list of element records;
- every record has a `GlobalId` and the four dimension scores;
- no `GlobalId` is duplicated within a file;
- the element count matches the model's baseline count from thesis Table 3.1, with fewer elements expected in F6 runs; and
- the model-level BQI recomputed from the element scores.

They print failures and a summary and write nothing to disk. The PowerShell version is a standalone implementation for machines without Python, not a wrapper around the Python script.

```bash
python scripts/verify_exports.py "<campaign_root>"
powershell -ExecutionPolicy Bypass -File scripts/verify_exports.ps1 "<campaign_root>"
```

`<campaign_root>` is the folder holding the run outputs, for example with sub-folders `Baseline`, `Single File (F1..)`, `Single File (F4, F6)` and `Dual File (F4, F6)`. Both default to the current folder.

---

## `harvest_reports.ps1` — Report Summary

Reads every `risk-register-*.html` under a folder and writes one CSV row per run: model, fault, rate, configuration, model BQI, element coverage and its verdict, High and Medium counts, elements scored, average SRCC and screening verdict.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/harvest_reports.ps1 -Root "<campaign_root>" -Out report_summary.csv
```

---

## `fault_analysis.py` — Fault Response

Pairs every faulted run with its baseline by file name, using run identity `(model, fault, rate, configuration)`, and computes from full-precision values:

- ΔBQI and ΔD1–ΔD4 at each rate;
- the most affected dimension and whether it is the targeted one (selectivity);
- a monotonicity check per model, fault and configuration;
- a list of borderline selectivity calls, where the margin over the runner-up is below 0.002;
- the F2 most-affected-dimension tally; and
- a guard for the F4 single-file runs, which must show ΔBQI = 0. A non-zero value means Pipeline A read a stale XLSX instead of converting the faulted file.

```bash
python scripts/fault_analysis.py "sensitivity-*.json"
```

It needs the baseline exports and the faulted-run exports in the same set of files, so it can only be run after the campaign. Output: `fault_analysis.csv`. Thesis Sections 4.2 and 4.3.

---

## `sensitivity_analysis.py` — Ranking Stability

Recomputes BQI, `R_adj` and the High/Medium/Low labels offline from each baseline export, for many parameter variants, and compares every variant with the baseline (weights 0.35/0.25/0.20/0.20, α = 0.55):

| Experiment | Variants per model |
|---|---|
| α sweep: 0.00, 0.25, 0.50, 0.75, 1.00 | 5 |
| Named weight schemes: baseline, equal weights, D4 downweighted, rank-order centroid | 4 |
| Pairwise weight shifts of ±0.05 | 12 |
| Random weight vectors on the simplex (seed 42) | 500 |

For each variant it reports the rank-stability SRCC, the number of label flips and the top-10 Jaccard overlap.

```bash
python scripts/sensitivity_analysis.py "sensitivity-*.json" --baselines-only
```

Output: `sensitivity_results.csv`. Thesis Section 4.4 and Table 4.7. It can be run directly on the files in [`../examples/`](../examples/).

---

## `alpha_characterization.py` — Choosing α

Sweeps α from 0.00 to 1.00 in steps of 0.05 and applies two criteria:

1. **Effectiveness:** α must escalate at least one element to a higher label in at least one model, compared with α = 0.
2. **Information preservation:** at most 5% of the elements in any model may be clamped at `R_adj = 1`.

The admissible interval is where both hold, and the recommended α is its midpoint, rounded to 0.05.

```bash
python scripts/alpha_characterization.py "sensitivity-*.json" --baselines-only
```

Output: `alpha_characterization.csv`, with escalations, clamp fraction and mean band width per model and α. On the files in [`../examples/`](../examples/) it gives the interval [0.10, 1.00] and α = 0.55 reported in thesis Sections 3.6.4 and 4.4.2.

---

## Relationship to the Workflow

```text
sample-models/baseline/*.ifc
        │
        ├── fault_injection.py ──► sample-models/fault-injected/*.ifc
        │
        ▼
n8n workflow  (extract_ifc.py runs inside, as Pipeline B)
        │
        ├── risk-register-*.html ──► harvest_reports.ps1 ──► report_summary.csv
        │
        └── sensitivity-*.json ────► verify_exports.py / .ps1
                                 ├─► fault_analysis.py ──────────► fault_analysis.csv
                                 ├─► sensitivity_analysis.py ────► sensitivity_results.csv
                                 └─► alpha_characterization.py ──► alpha_characterization.csv
```

---

## Notes on the Source Code

- Some scripts contain comments marked `CORRECTED VERSION` or `CHANGED (C1)`–`(C6)`. They record fixes made during development, such as aligning the label percentiles with Node 4.5 and setting α to 0.55. All reported results use the corrected versions.
- Because Node 2.1 downloads `extract_ifc.py` from `main`, any change to that file on `main` affects future workflow runs. To reproduce the thesis exactly, use the script from the thesis release or keep a local copy in `script_dir`.

---

## Versions

The thesis cites release `v1.0.2`, whose script hashes are listed in Annex III. The scripts are identical in `v1.0.1` and `v1.0.2`.
