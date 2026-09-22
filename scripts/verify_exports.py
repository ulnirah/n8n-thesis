#!/usr/bin/env python3
"""
verify_exports.py

Structural verification of the sensitivity JSON exports produced by the
n8n pipeline. Run it over the folder that contains the four campaign
sub-folders (Baseline, Single File (F1..), Single File (F4, F6),
Dual File (F4, F6)).

    python verify_exports.py "C:/path/to/campaign_root"

For every sensitivity-*.json it checks:
  - the file parses as a JSON list of element records
  - every record carries the four dimension scores and a GlobalId
  - no GlobalId is duplicated within a file
  - the element count matches the model's baseline count
    (F6 runs are expected to have FEWER elements, by design)

It also recomputes the model-level BQI from the element scores and prints it
for every baseline export, for comparison with thesis Table 4.1. Files that
fail a check are listed with the reason, followed by a summary. Nothing is
written to disk.
"""

import json
import sys
from pathlib import Path

# Baseline element count per model, from Table 3.1
BASELINE_N = {
    "IFC4-Building-Architecture": 14,
    "IFC43-Building-Architecture": 14,
    "IFC4-Building-Structural": 16,
    "IFC43-Building-Structural": 16,
    "IFC4-Infra-Bridge": 57,
    "IFC43-Infra-Bridge": 68,
    "IFC4-Infra-Road": 55,
    "IFC43-Infra-Road": 81,
}

WEIGHTS = (0.35, 0.25, 0.20, 0.20)
KEYS = ("score_completeness", "score_validity",
        "score_qto_coverage", "score_qto_agreement")


def model_of(filename):
    """Longest matching model name, so IFC43-... is not matched as IFC4-..."""
    hits = [m for m in BASELINE_N if m in filename]
    return max(hits, key=len) if hits else None


def check(path):
    """Return (ok, model, n, expected, note, bqi)."""
    name = path.name
    model = model_of(name)
    if model is None:
        return False, None, 0, 0, "model not recognised from filename", None

    expected = BASELINE_N[model]
    is_f6 = "F6" in name.upper()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, model, 0, expected, f"unreadable: {exc}", None

    if not isinstance(data, list):
        return False, model, 0, expected, "not a JSON list", None

    n = len(data)
    gids = [e.get("GlobalId") for e in data]
    if any(g is None for g in gids):
        return False, model, n, expected, "record without GlobalId", None
    dup = n - len(set(gids))
    if dup:
        return False, model, n, expected, f"{dup} duplicated GlobalId", None

    missing = [k for k in KEYS if any(k not in e for e in data)]
    if missing:
        return False, model, n, expected, f"missing keys: {', '.join(missing)}", None

    bqi = sum(sum(w * e[k] for w, k in zip(WEIGHTS, KEYS)) for e in data) / n

    if is_f6:
        if n > expected:
            return False, model, n, expected, "F6 run has MORE elements than baseline", bqi
        note = f"F6reduced, {expected - n} element(s) removed" if n < expected else "F6, no element removed"
    else:
        if n != expected:
            return False, model, n, expected, "element count differs from baseline", bqi
        note = ""

    return True, model, n, expected, note, bqi


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    files = sorted(root.rglob("sensitivity-*.json"))

    if not files:
        print(f"No sensitivity-*.json found under {root.resolve()}")
        return 1

    failures = []
    by_folder = {}
    f6_reduced = 0
    f6_total = 0
    shown = False
    baseline_bqi = []

    for path in files:
        if not shown:
            try:
                first = json.loads(path.read_text(encoding="utf-8"))[0]
                print(f"Fields found in {path.name}:")
                print("  " + ", ".join(first.keys()) + "\n")
                shown = True
            except Exception:
                pass
        ok, model, n, expected, note, bqi = check(path)
        folder = path.parent.name
        by_folder[folder] = by_folder.get(folder, 0) + 1
        if "F6" in path.name.upper():
            f6_total += 1
        if note.startswith("F6reduced"):
            f6_reduced += 1
        if not ok:
            failures.append((path, model, n, expected, note))
        elif "__F" not in path.name:
            baseline_bqi.append((model, bqi))

    print(f"Scanned {len(files)} export(s) under {root.resolve()}\n")
    print("Files per folder:")
    for folder, count in sorted(by_folder.items()):
        print(f"  {count:>4}  {folder}")
    print(f"\n{f6_reduced} of {f6_total} F6 run(s) show a reduced element count, as expected by design.")

    if baseline_bqi:
        print("\nModel BQI recomputed from the element scores (baseline exports):")
        for model, bqi in sorted(baseline_bqi):
            print(f"  {model:<30}{bqi:.3f}")

    if failures:
        print(f"\n{len(failures)} file(s) FAILED. First 15:\n")
        for path, model, n, expected, note in failures[:15]:
            print(f"  {path.name}")
            print(f"      model={model} n={n} expected={expected}  {note}")
        return 1

    print("\nAll files passed: valid JSON, no duplicated GlobalId, all four")
    print("dimension scores present, element counts consistent with Table 3.1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
