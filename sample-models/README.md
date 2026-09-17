# Sample Models

This folder contains the IFC corpus used in the thesis experiments: the eight unmodified baseline models and the 126 fault-injected variants generated from them.

```text
sample-models/
├── README.md
├── baseline/          8 original buildingSMART IFC files
└── fault-injected/    126 faulted IFC variants (M1–M7)
```

---

## Source

All eight models come from the official [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) repository (PCERT sample scene), at commit `703fafe1132c1b80bad052123e8b134e93cbad7f`. They were first retrieved on 1 April 2026 and re-retrieved on 8 July 2026 at the same commit (thesis Annex III).

They were chosen because they are:

- openly licensed and citable;
- published by buildingSMART as reference examples of IFC use; and
- available as matched IFC 4 / IFC 4.3 pairs of the same design.

---

## Selection

Eighteen candidate files were assessed against two inclusion criteria (thesis Section 3.1.1):

1. property count > 0; and
2. quantity count > 0.

Seven models met both criteria (M1–M7). A model without property data scores trivially zero, and faults cannot manifest on dimensions that are already at zero.

The IFC 4.3 road model (M8) carries 81 elements but no property or quantity data, so it failed the criteria. It was kept deliberately as a **negative control**, completing the fourth design pair and showing the difference between breadth (element coverage) and depth (information quality).

---

## Model Inventory

| ID | File in `baseline/` | Schema | Design | Elements | Property keys | Quantities | Role |
|---|---|---|---|---:|---:|---:|---|
| M1 | `IFC4-Building-Architecture.ifc` | IFC 4.0.2.1 | Building architecture | 14 | 62 | 25 | Valid |
| M2 | `IFC43-Building-Architecture.ifc` | IFC 4.3.2.0 | Building architecture | 14 | 30 | 25 | Valid |
| M3 | `IFC4-Building-Structural.ifc` | IFC 4.0.2.1 | Building structural | 16 | 65 | 34 | Valid |
| M4 | `IFC43-Building-Structural.ifc` | IFC 4.3.2.0 | Building structural | 16 | 34 | 34 | Valid |
| M5 | `IFC4-Infra-Bridge.ifc` | IFC 4.0.2.1 | Bridge | 57 | 48 | 27 | Valid |
| M6 | `IFC43-Infra-Bridge.ifc` | IFC 4.3.2.0 | Bridge | 68 | 27 | 27 | Valid |
| M7 | `IFC4-Infra-Road.ifc` | IFC 4.0.2.1 | Road | 55 | 174 | 78 | Valid |
| M8 | `IFC43-Infra-Road.ifc` | IFC 4.3.2.0 | Road | 81 | 0 | 0 | Negative control |

**Elements** are the valued elements: all elements scored by the BQI engine, whether against an explicit rule, through the fallback rules, or at zero.

**Property keys** count the extracted key namespace, which includes keys from both `IfcPropertySet` and `IfcElementQuantity`. This is why IFC 4.3 variants whose data sit only in quantity sets, such as M4 and M6, show equal property and quantity counts.

**Design** is what the file represents. The domain used for the risk lookup tables can differ: IFC 4 files are assigned the Building domain, and M6 is classed as Mixed because it also contains walls and slabs, so only M8 is scored with an infrastructure table. See [`../docs/risk-rules-table.md`](../docs/risk-rules-table.md), Section 2.

The large differences in information content between some IFC 4 and IFC 4.3 variants of the same design are properties of the source files, not extraction artefacts (thesis Section 4.1).

---

## Integrity Check

SHA-256 of the baseline files, as listed in thesis Annex III:

| ID | SHA-256 | Size (KB) |
|---|---|---:|
| M1 | `3FF9B10BD00C7B96DDED51E7CA5A6B69EFBEA38B049ADCDD05FCD247DE7E70D5` | 220 |
| M2 | `A42962F9E2068040AC96636B1E7F6117150B6C0E3371F81088721B22796E463F` | 216 |
| M3 | `68BE722391E7AAA53BB9278645A02AA4B6382F13CC07548A1612E9B1DC3DEF67` | 290 |
| M4 | `0343D5222D38E6BE8AC7C31045C692E62C6018C80EA60D2F6023E73B846247AB` | 285 |
| M5 | `3D1273BB60BDA11373E0BCBD8A73C409F49C097B98867573C9493888D8626FCC` | 1,845 |
| M6 | `241E6576A3A554086D3D2AE87415C5BA98A0123D329245810E7D42ECC504C183` | 1,839 |
| M7 | `B0F842B07A41490274F3D8485DD59B9818941B804D1B85F8AFD0BB7969A66502` | 429 |
| M8 | `AFC312BE9931345C381D8D1855DBF9072E13A3F46526D4CF0F9325BDBDA23201` | 407 |

To check a file:

```bash
sha256sum baseline/IFC4-Building-Architecture.ifc                      # Linux / macOS
Get-FileHash baseline\IFC4-Building-Architecture.ifc -Algorithm SHA256  # Windows PowerShell
```

The baseline files must not be edited. Every faulted variant is generated from them, so each experimental condition traces back to a known reference file.

---

## Fault Injection

Faults are injected into the seven valid models, M1–M7. M8 is excluded, because with no property or quantity data most faults could not manifest; it is analysed separately.

| Fault | Mutation | Targeted instrument |
|---|---|---|
| F1 | Remove a required property | D1 |
| F2 | Blank a property value to UNSET | D1 + D2 |
| F3 | Remove a quantity field | D3 |
| F4 | Perturb quantity magnitudes by +10% | D4 |
| F5 | Remove an entire property set | D1 + D2 |
| F6 | Delete whole elements | Element coverage |

The variants are generated by [`../scripts/fault_injection.py`](../scripts/fault_injection.py).

### Severity

Each fault is applied at three injection rates: **10%, 25% and 50%** of the eligible elements. Elements are ordered by `GlobalId` and then sampled uniformly with a fixed seed (**42**).

The eligible population is the sixteen types defined in thesis Section 3.5.1: the twelve rule-table types (`IfcWall`, `IfcSlab`, `IfcBeam`, `IfcColumn` with their StandardCase variants, `IfcRoof`, `IfcDoor`, `IfcWindow`, `IfcSpace`) plus `IfcStair`, `IfcStairFlight`, `IfcFooting` and `IfcPile`, which are scored through the fallback rules. `IfcElementAssembly` is not eligible.

### Intensity

All reported results use **light** intensity:

- F1, F2 and F3 change one matching field per target element (heavy mode would change every matching field);
- F4 perturbs every quantity value of the target element;
- F5 removes exactly one property set;
- F6 removes the whole element.

The severity therefore controls how many elements are affected, not how deeply each element is altered.

### Configurations

| Configuration | Faults | Pipeline A reads | Pipeline B reads | Runs |
|---|---|---|---|---:|
| Baseline | — | Baseline | Baseline | 8 |
| Single file | F1, F2, F3, F5 | Faulted | Faulted | 84 |
| Single file | F4, F6 | Faulted | Faulted | 42 |
| Dual file | F4, F6 | Baseline | Faulted | 42 |
| **Total** | | | | **176** |

With a single file, both pipelines read the same perturbed values, so a disagreement fault such as F4 is invisible by construction. The dual-file configuration gives the faulted file to Pipeline B only, which exposes the D4 response to F4 and the coverage response to F6.

The deepest per-dimension analysis in the thesis (Section 4.2) is presented for M1.

---

## Fault-Injected Files

`fault-injected/` contains 126 files, 18 per valid model (6 faults × 3 rates):

```text
<model>__F<n>-r<rate>-s42.ifc                   F1, F2, F3, F5
<model>__F<n>-r<rate>-s42_PIPELINE-B-ONLY.ifc   F4, F6
```

The F4 and F6 files carry the `_PIPELINE-B-ONLY` suffix because they are the variants given to Pipeline B in the dual-file runs; the same files are also used in the single-file runs. Details are in [`fault-injected/README.md`](fault-injected/README.md).

---

## Traceability

`fault_injection.py` writes a JSON manifest next to every variant, recording the baseline model, fault type, rate, seed, selected target elements and the modifications applied. The manifests are regenerated with the variants and are not committed.

Thesis Annex IV reports the per-run SRCC testability and element coverage of the dual-file runs.

```text
Baseline IFC → fault injection → dual extraction → QTO comparison → BQI → risk screening → analysis
```

---

## Derived Files

The IFC files are the only primary inputs. Everything else is a derived artefact that can be regenerated from them with the workflow and scripts:

- DDC-generated XLSX files (`<IFC file name>_ifc.xlsx`, created next to the input file);
- Pipeline B extraction output;
- fault-injection manifests; and
- risk registers and sensitivity exports.

Baseline outputs for all eight models are in [`../examples/`](../examples/).

Before a campaign, delete any old `_ifc.xlsx` conversions of faulted files: Pipeline A reuses an existing XLSX with the expected name instead of converting again (see [`../docs/ddc-adaptation-notes.md`](../docs/ddc-adaptation-notes.md), Section 12.5).

---

## Versions

The thesis cites repository release `v1.0.1` (Annex III). In `v1.0.2` only this README changes; the IFC files are identical.
