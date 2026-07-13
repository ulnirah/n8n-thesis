#!/usr/bin/env python3
"""
Fault injection for IFC files — validation experiment for the BQI pipeline.
EMJM NORISK thesis: Uncertainty-Aware Risk Screening from Imperfect BIM.

Fault model (Natella et al. framing):
  WHAT  - six fault types, each targeting one BQI dimension:
      F1  remove a required property            -> D1 completeness
      F2  blank a property value to UNSET       -> D2 validity
      F3  remove a quantity field               -> D3 QTO coverage
      F4  perturb quantity magnitudes (+delta)  -> D4 agreement (dual-file, see below)
      F5  remove an entire property set         -> D1 + D2 combined
      F6  remove whole elements                 -> element coverage (dual-file)
  WHERE - elements sampled uniformly at random (fixed seed) from types that
          have scoring rules (walls, slabs, beams, columns, roofs, doors,
          windows, spaces, stairs, footings).
  HOW MUCH - severity = fraction of eligible elements faulted (0.10/0.25/0.50).

DUAL-FILE NOTE (F4, F6): both extraction pipelines read the same file, so a
fault written into that one file changes BOTH pipelines equally and produces
no disagreement. F4 and F6 therefore emit a *variant* file that must be fed
to Pipeline B only, while Pipeline A keeps the original. This simulates
tool/version divergence. F1, F2, F3, F5 are single-file faults (feed the
faulted file to both pipelines as usual).

Every run writes a manifest JSON recording seed, targets, and every change,
so each faulted file is fully traceable in the thesis appendix.

Usage:
  python fault_injection.py model.ifc --fault F1 --rate 0.25 --seed 42 --outdir faulted
  python fault_injection.py model.ifc --all --seed 42 --outdir faulted   (all 6 x 3)

Requires: ifcopenshell (already installed for Pipeline B).
"""

import argparse
import json
import os
import random
import sys

import ifcopenshell

TARGET_TYPES = [
    "IfcWall", "IfcWallStandardCase", "IfcSlab", "IfcSlabStandardCase",
    "IfcBeam", "IfcBeamStandardCase", "IfcColumn", "IfcColumnStandardCase",
    "IfcRoof", "IfcDoor", "IfcWindow", "IfcSpace",
    "IfcStair", "IfcStairFlight", "IfcFooting", "IfcPile",
]

# Properties the BQI marks as required (mirror of Node 3.4 REQUIRED_PROPS)
REQUIRED_PROPS = ["IsExternal", "LoadBearing", "FireRating", "GrossPlannedArea"]

RATES = [0.10, 0.25, 0.50]
INTENSITY = "light"   # set from CLI: light = one field per element, heavy = all fields
QUANTITY_VALUE_ATTRS = ["VolumeValue", "AreaValue", "LengthValue",
                        "CountValue", "WeightValue", "TimeValue"]
F4_DELTA = 0.10   # +10% perturbation on quantity magnitudes


def eligible_elements(f):
    seen, out = set(), []
    for t in TARGET_TYPES:
        try:
            for e in f.by_type(t):
                if e.id() not in seen:
                    seen.add(e.id())
                    out.append(e)
        except RuntimeError:
            pass  # type not in this schema
    return sorted(out, key=lambda e: e.GlobalId)  # deterministic order


def psets_of(element):
    """Yield (rel, IfcPropertySet) pairs attached to the element."""
    for rel in (getattr(element, "IsDefinedBy", None) or []):
        if rel.is_a("IfcRelDefinesByProperties"):
            pd = rel.RelatingPropertyDefinition
            if pd is not None and pd.is_a("IfcPropertySet"):
                yield rel, pd


def qsets_of(element):
    for rel in (getattr(element, "IsDefinedBy", None) or []):
        if rel.is_a("IfcRelDefinesByProperties"):
            pd = rel.RelatingPropertyDefinition
            if pd is not None and pd.is_a("IfcElementQuantity"):
                yield rel, pd


# ---------------------------------------------------------------- fault ops --
def f1_remove_required_property(f, element, log):
    changed = False
    for _, pset in psets_of(element):
        props = list(pset.HasProperties or [])
        for p in list(props):
            if p.is_a("IfcPropertySingleValue") and p.Name in REQUIRED_PROPS:
                removed_name = p.Name          # capture BEFORE remove:
                pset_name = pset.Name          # entity is freed by f.remove()
                pset.HasProperties = tuple(x for x in props if x != p)
                f.remove(p)
                log.append({"gid": element.GlobalId, "pset": pset_name,
                            "removed_property": removed_name})
                if INTENSITY == "light":
                    return True
                changed = True
    return changed if INTENSITY == "heavy" else False


def f2_blank_value(f, element, log):
    changed = False
    for _, pset in psets_of(element):
        for p in (pset.HasProperties or []):
            if p.is_a("IfcPropertySingleValue") and p.NominalValue is not None:
                old = str(p.NominalValue)
                p.NominalValue = None   # UNSET in the STEP file
                log.append({"gid": element.GlobalId, "pset": pset.Name,
                            "blanked_property": p.Name, "old_value": old})
                if INTENSITY == "light":
                    return True
                changed = True
    return changed if INTENSITY == "heavy" else False


def f3_remove_quantity(f, element, log):
    changed = False
    for _, qset in qsets_of(element):
        qs = list(qset.Quantities or [])
        victims = qs[:1] if INTENSITY == "light" else qs
        for victim in victims:
            name = victim.Name
            qs2 = [x for x in (qset.Quantities or []) if x != victim]
            qset.Quantities = tuple(qs2)
            f.remove(victim)
            log.append({"gid": element.GlobalId, "qset": qset.Name,
                        "removed_quantity": name})
            changed = True
            if INTENSITY == "light":
                return True
    return changed


def f4_perturb_quantities(f, element, log):
    changed = False
    for _, qset in qsets_of(element):
        for q in (qset.Quantities or []):
            for attr in QUANTITY_VALUE_ATTRS:
                if hasattr(q, attr) and getattr(q, attr) is not None:
                    old = float(getattr(q, attr))
                    setattr(q, attr, old * (1 + F4_DELTA))
                    log.append({"gid": element.GlobalId, "qset": qset.Name,
                                "quantity": q.Name, "attr": attr,
                                "old": old, "new": old * (1 + F4_DELTA)})
                    changed = True
    return changed


def f5_remove_pset(f, element, log):
    for rel, pset in psets_of(element):
        name = pset.Name
        n = len(pset.HasProperties or [])
        f.remove(rel)
        f.remove(pset)
        log.append({"gid": element.GlobalId, "removed_pset": name,
                    "properties_lost": n})
        return True
    return False


def f6_remove_element(f, element, log):
    gid, cat = element.GlobalId, element.is_a()
    try:
        import ifcopenshell.api
        ifcopenshell.api.run("root.remove_product", f, product=element)
    except Exception:
        f.remove(element)   # fallback; ifcopenshell tolerates the cleanup
    log.append({"removed_element": gid, "category": cat})
    return True


FAULTS = {
    "F1": (f1_remove_required_property, "remove required property (D1)", False),
    "F2": (f2_blank_value,              "blank value to UNSET (D2)",      False),
    "F3": (f3_remove_quantity,          "remove quantity field (D3)",     False),
    "F4": (f4_perturb_quantities,       "perturb quantities +10% (D4)",   True),
    "F5": (f5_remove_pset,              "remove whole property set (D1+D2)", False),
    "F6": (f6_remove_element,           "remove elements (coverage)",     True),
}


def inject(path, fault, rate, seed, outdir):
    f = ifcopenshell.open(path)
    op, desc, dual_file = FAULTS[fault]
    elems = eligible_elements(f)
    rng = random.Random(seed)
    n_target = max(1, round(len(elems) * rate))
    targets = rng.sample(elems, min(n_target, len(elems)))

    log, applied = [], 0
    for e in targets:
        if op(f, e, log):
            applied += 1

    base = os.path.splitext(os.path.basename(path))[0]
    tag = f"{fault}-r{int(rate*100):02d}-s{seed}" + ("-heavy" if INTENSITY == "heavy" else "")
    suffix = "_PIPELINE-B-ONLY" if dual_file else ""
    out_ifc = os.path.join(outdir, f"{base}__{tag}{suffix}.ifc")
    os.makedirs(outdir, exist_ok=True)
    f.write(out_ifc)

    manifest = {
        "source_file": os.path.basename(path),
        "fault_type": fault, "description": desc,
        "dual_file": dual_file,
        "note": ("Feed this file to Pipeline B only; keep the original for "
                 "Pipeline A.") if dual_file else
                ("Feed this file to both pipelines (replace project_file)."),
        "severity_rate": rate, "seed": seed, "intensity": INTENSITY,
        "eligible_elements": len(elems),
        "elements_targeted": len(targets),
        "faults_applied": applied,
        "changes": log,
    }
    out_manifest = out_ifc.replace(".ifc", ".manifest.json")
    with open(out_manifest, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"{tag}: {applied}/{len(targets)} faults applied "
          f"({len(elems)} eligible) -> {os.path.basename(out_ifc)}")
    return applied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ifc")
    ap.add_argument("--fault", choices=list(FAULTS), help="single fault type")
    ap.add_argument("--rate", type=float, help="single severity, e.g. 0.25")
    ap.add_argument("--all", action="store_true",
                    help="run all 6 fault types x 3 severities")
    ap.add_argument("--intensity", choices=["light", "heavy"], default="light",
                    help="light: one field per targeted element; "
                         "heavy: all matching fields per targeted element")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--outdir", default="faulted")
    args = ap.parse_args()
    global INTENSITY
    INTENSITY = args.intensity

    if args.all:
        for fault in FAULTS:
            for rate in RATES:
                inject(args.ifc, fault, rate, args.seed, args.outdir)
    elif args.fault and args.rate:
        inject(args.ifc, args.fault, args.rate, args.seed, args.outdir)
    else:
        ap.error("use --all, or both --fault and --rate")


if __name__ == "__main__":
    main()
