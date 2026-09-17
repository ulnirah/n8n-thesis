# Baseline IFC Models

This folder contains the eight **original, unmodified IFC files** used as reference inputs for every experiment in the thesis, identified as **M1–M8**.

M1–M7 are the valid experimental models. M8 is the **negative control**: its 81 elements carry no property or quantity data. Corpus selection, element and property counts, and the fault-injection design are described in [`../README.md`](../README.md).

---

## Files

All files come from the official [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) repository at commit `703fafe1132c1b80bad052123e8b134e93cbad7f`, retrieved on 1 April 2026 and re-retrieved on 8 July 2026 at the same commit. Both schema versions of a design share the same source file name, so a schema prefix (`IFC4-` or `IFC43-`) was added.

| ID | File in this folder | Source path in Sample-Test-Files | Schema | Design | Role |
|---|---|---|---|---|---|
| M1 | `IFC4-Building-Architecture.ifc` | `IFC 4.0.2.1 (IFC 4)/PCERT-Sample-Scene/Building-Architecture.ifc` | IFC 4.0.2.1 | Building architecture | Valid |
| M2 | `IFC43-Building-Architecture.ifc` | `IFC 4.3.2.0 (IFC4X3_ADD2)/PCERT-Sample-Scene/Building-Architecture.ifc` | IFC 4.3.2.0 | Building architecture | Valid |
| M3 | `IFC4-Building-Structural.ifc` | `IFC 4.0.2.1 (IFC 4)/PCERT-Sample-Scene/Building-Structural.ifc` | IFC 4.0.2.1 | Building structural | Valid |
| M4 | `IFC43-Building-Structural.ifc` | `IFC 4.3.2.0 (IFC4X3_ADD2)/PCERT-Sample-Scene/Building-Structural.ifc` | IFC 4.3.2.0 | Building structural | Valid |
| M5 | `IFC4-Infra-Bridge.ifc` | `IFC 4.0.2.1 (IFC 4)/PCERT-Sample-Scene/Infra-Bridge.ifc` | IFC 4.0.2.1 | Bridge | Valid |
| M6 | `IFC43-Infra-Bridge.ifc` | `IFC 4.3.2.0 (IFC4X3_ADD2)/PCERT-Sample-Scene/Infra-Bridge.ifc` | IFC 4.3.2.0 | Bridge | Valid |
| M7 | `IFC4-Infra-Road.ifc` | `IFC 4.0.2.1 (IFC 4)/PCERT-Sample-Scene/Infra-Road.ifc` | IFC 4.0.2.1 | Road | Valid |
| M8 | `IFC43-Infra-Road.ifc` | `IFC 4.3.2.0 (IFC4X3_ADD2)/PCERT-Sample-Scene/Infra-Road.ifc` | IFC 4.3.2.0 | Road | Negative control |

The files form four IFC 4 / IFC 4.3 pairs of the same design: M1/M2, M3/M4, M5/M6 and M7/M8.

**Design** is what the file represents. The domain used for the risk lookup tables can differ: IFC 4 files are assigned the Building domain, and M6 is classed as Mixed, so only M8 is scored with an infrastructure table (see [`../../docs/risk-rules-table.md`](../../docs/risk-rules-table.md), Section 2).

---

## Integrity Check

SHA-256 as listed in thesis Annex III:

| ID | SHA-256 |
|---|---|
| M1 | `3FF9B10BD00C7B96DDED51E7CA5A6B69EFBEA38B049ADCDD05FCD247DE7E70D5` |
| M2 | `A42962F9E2068040AC96636B1E7F6117150B6C0E3371F81088721B22796E463F` |
| M3 | `68BE722391E7AAA53BB9278645A02AA4B6382F13CC07548A1612E9B1DC3DEF67` |
| M4 | `0343D5222D38E6BE8AC7C31045C692E62C6018C80EA60D2F6023E73B846247AB` |
| M5 | `3D1273BB60BDA11373E0BCBD8A73C409F49C097B98867573C9493888D8626FCC` |
| M6 | `241E6576A3A554086D3D2AE87415C5BA98A0123D329245810E7D42ECC504C183` |
| M7 | `B0F842B07A41490274F3D8485DD59B9818941B804D1B85F8AFD0BB7969A66502` |
| M8 | `AFC312BE9931345C381D8D1855DBF9072E13A3F46526D4CF0F9325BDBDA23201` |

```bash
sha256sum *.ifc                                                    # Linux / macOS
Get-ChildItem *.ifc | Get-FileHash -Algorithm SHA256               # Windows PowerShell
```

If a hash differs, the file has been changed, and results will not be comparable with the thesis.

---

## Use

The baseline files are the reference inputs for:

- dual-pipeline extraction and QTO comparison;
- BQI calculation and risk screening;
- fault injection (M1–M7 only; M8 is not fault-injected); and
- parameter sensitivity analysis.

Their outputs are in [`../../examples/`](../../examples/).

---

## Rules for This Folder

- **Do not edit or re-save these files.** Opening and saving an IFC file in modelling software changes its content and hash.
- **Keep derived files elsewhere.** Pipeline A writes `<file name>_ifc.xlsx` next to the IFC it converts; delete these conversions, or run from a copy, rather than committing them here.
- **Generate faulted variants from these files only.** Every variant in [`../fault-injected/`](../fault-injected/) traces back to one of them.
