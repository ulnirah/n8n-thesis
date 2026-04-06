# Sample Models

This folder contains all IFC models used in the thesis, organized into two subfolders:

- **`baseline/`** — Clean, unmodified IFC files used as the reference starting point for all thesis tasks
- **`fault-injected/`** — Broken variants of the baseline models, generated programmatically for Task 5 (robustness benchmarking)

---

## Baseline Models

All baseline files were sourced from official buildingSMART repositories:
- buildingSMART Sample Test Files (IFC4 & IFC4.3): https://github.com/buildingSMART/Sample-Test-Files
- buildingSMART Community Sample Files: https://github.com/buildingsmart-community/Community-Sample-Test-Files

| File Name | IFC Schema | Model Type | Source | Used In |
|-----------|------------|------------|--------|---------|
| IFC4-Infra-Bridge.ifc | IFC4 | Bridge / Infrastructure | buildingSMART | Tasks 2, 3, 4, 6 |
| IFC4-Infra-Road.ifc | IFC4 | Road / Infrastructure | buildingSMART | Tasks 2, 3, 4, 6 |
| IFC4-Infra-Railway.ifc | IFC4 | Railway / Infrastructure | buildingSMART | Tasks 2, 3, 4 |
| IFC4-Building.ifc | IFC4 | Building | buildingSMART | Tasks 2, 3 |
| IFC4x3-Infra-Bridge.ifc | IFC4.3 | Bridge / Infrastructure | buildingSMART | Tasks 2, 3, 4, 6 |
| IFC4x3-Infra-Road.ifc | IFC4.3 | Road / Infrastructure | buildingSMART | Tasks 2, 3, 4, 6 |
| IFC4x3-Infra-Railway.ifc | IFC4.3 | Railway / Infrastructure | buildingSMART | Tasks 2, 3, 4 |
| IFC4x3-Building.ifc | IFC4.3 | Building | buildingSMART | Tasks 2, 3 |

> **Note:** Update the file names above to match the actual filenames in this folder once confirmed.

---

## Fault-Injected Models

> 🔲 Not yet generated — will be created in Task 5.

Fault-injected variants will be generated using Python (ifcopenshell) by introducing controlled errors into the baseline models. Each variant will correspond to one type of fault.

| Fault Type | Description | Script |
|------------|-------------|--------|
| Missing property sets | Remove required Pset entries from elements | `scripts/fault_inject_missing_psets.py` |
| Unit swap | Change units from metres to feet without converting values | `scripts/fault_inject_unit_swap.py` |
| Classification error | Assign wrong IFC type to elements | `scripts/fault_inject_wrong_type.py` |
| Distorted quantities | Multiply volume/area values by random factor | `scripts/fault_inject_distort_qto.py` |
| Duplicate IDs | Assign same GlobalId to multiple elements | `scripts/fault_inject_duplicate_ids.py` |
| Broken spatial hierarchy | Remove IfcRelContainedInSpatialStructure links | `scripts/fault_inject_spatial.py` |

Naming convention for fault-injected files:
```
[original-filename]_fault_[fault-type].ifc
Example: IFC4-Infra-Bridge_fault_missing_psets.ifc
```
