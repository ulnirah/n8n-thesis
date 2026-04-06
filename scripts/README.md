# Scripts

This folder contains Python scripts used in the thesis. They handle tasks that are easier to do in Python than in n8n, such as IFC file manipulation, second QTO extraction method, and statistical analysis.

> 🔲 Most scripts are not yet written — they will be added as thesis tasks are completed.

---

## Script Reference

### QTO Extraction (Task 6)

| Script | Status | Purpose |
|--------|--------|---------|
| `qto_ifcopenshell.py` | 🔲 Not started | Extracts QTO from IFC files using ifcopenshell — this is Method 2 for the QTO robustness comparison in Task 6 |
| `qto_comparison.py` | 🔲 Not started | Compares Method 1 (DDC IfcExporter) vs Method 2 (ifcopenshell), computes Spearman rank correlation, saves results to `outputs/qto/` |

---

### Fault Injection (Task 5)

| Script | Status | Purpose |
|--------|--------|---------|
| `fault_inject_missing_psets.py` | 🔲 Not started | Removes required property sets from IFC elements |
| `fault_inject_unit_swap.py` | 🔲 Not started | Swaps unit definitions without converting values |
| `fault_inject_wrong_type.py` | 🔲 Not started | Assigns incorrect IFC type classifications to elements |
| `fault_inject_distort_qto.py` | 🔲 Not started | Multiplies volume/area values by a random distortion factor |
| `fault_inject_duplicate_ids.py` | 🔲 Not started | Assigns duplicate GlobalIds to multiple elements |
| `fault_inject_spatial.py` | 🔲 Not started | Removes IfcRelContainedInSpatialStructure links to break spatial hierarchy |
| `fault_inject_all.py` | 🔲 Not started | Runs all fault injection scripts in sequence on a given baseline model |

---

### BQI Scoring (Task 3)

| Script | Status | Purpose |
|--------|--------|---------|
| `bqi_score.py` | 🔲 Not started | Standalone Python version of the BQI scoring formula — used to verify n8n BQI workflow results |

---

## Dependencies

All Python scripts in this folder require:

```bash
pip install ifcopenshell pandas scipy openpyxl
```

- **ifcopenshell** — IFC file reading and manipulation
- **pandas** — data processing and CSV export
- **scipy** — Spearman rank correlation (`scipy.stats.spearmanr`)
- **openpyxl** — reading/writing Excel files

---

## How to Run

Each script can be run from the command line:

```bash
# Example: Extract QTO from one IFC file using ifcopenshell
python qto_ifcopenshell.py --input ../sample-models/baseline/IFC4-Infra-Bridge.ifc --output ../outputs/qto/

# Example: Run all fault injections on one baseline model
python fault_inject_all.py --input ../sample-models/baseline/IFC4-Infra-Bridge.ifc --output ../sample-models/fault-injected/
```

Detailed usage instructions will be added to each script's docstring as they are written.
