#!/usr/bin/env python3
"""
Fault-injection analysis: aggregates the per-run sensitivity exports into the
baseline-vs-faulted comparison that the report itself never shows.

=============================================================================
CORRECTED VERSION — two changes vs the July 2026 script. Search "CHANGED".
  C4  KEY COLLISION. The run dictionary was keyed (model, fault, rate), and
      the "_PIPELINE-B-ONLY" part of the filename was a non-capturing group
      that was discarded. F4 and F6 exist in BOTH configurations at the same
      model and rate, so the second run loaded silently overwrote the first.
      The key is now (model, fault, rate, config) and "config" is reported as
      its own CSV column.
  C5  The single-file and dual-file runs of F4/F6 read the SAME variant file,
      so their export filenames were identical and one overwrote the other on
      disk. The Sensitivity Analysis node must append "_DUALFILE" when
      project_file_b is set. This script now recognises that suffix.
=============================================================================

How it fits the experiment:
  1. fault_injection.py generates the faulted IFC files.
  2. You run the n8n pipeline once per file. The Sensitivity Analysis node
     writes sensitivity-<name>.json per run, so the fault tag travels in the
     filename automatically.
  3. This script reads ALL those exports, recomputes Model BQI and the D1-D4
     averages per run, matches each faulted run to its model baseline, and
     writes the comparison table (deltas + selectivity check) as CSV.

Usage:
    python fault_analysis.py "sensitivity-*.json"
Pure standard library.
"""

import csv
import glob
import json
import os
import re
import sys

WEIGHTS = {"w1": 0.35, "w2": 0.25, "w3": 0.20, "w4": 0.20}
DIMS = ["D1", "D2", "D3", "D4"]
FIELD = {"D1": "score_completeness", "D2": "score_validity",
         "D3": "score_qto_coverage", "D4": "score_qto_agreement"}

# CHANGED (C4/C5): the pipeline-B marker and the dual-file marker are now
# CAPTURED rather than discarded, so the two configurations stay distinct.
#   sensitivity-<model>.json                                      -> baseline
#   sensitivity-<model>__F4-r25-s42_PIPELINE-B-ONLY.json          -> single-file
#   sensitivity-<model>__F4-r25-s42_PIPELINE-B-ONLY_DUALFILE.json -> dual-file
RUN_RE = re.compile(
    r"^sensitivity-(?P<model>.+?)"
    r"(?:__(?P<fault>F\d)-r(?P<rate>\d{2})-s(?P<seed>\d+)(?P<heavy>-heavy)?)?"
    r"(?P<bonly>_PIPELINE-B-ONLY)?"
    r"(?P<dual>_DUALFILE)?\.json$"
)


def load_run(path):
    with open(path, encoding="utf-8") as f:
        elements = json.load(f)
    req = list(FIELD.values())
    elements = [e for e in elements if all(k in e and e[k] is not None for k in req)]
    n = len(elements)
    if n == 0:
        return None
    avg = {d: sum(e[FIELD[d]] for e in elements) / n for d in DIMS}
    bqi = (WEIGHTS["w1"] * avg["D1"] + WEIGHTS["w2"] * avg["D2"]
           + WEIGHTS["w3"] * avg["D3"] + WEIGHTS["w4"] * avg["D4"])
    # Report at 3 dp to match the thesis convention. The averages themselves
    # are computed at full precision from full-precision node output.
    return {"n": n, **{d: round(avg[d], 3) for d in DIMS}, "BQI": round(bqi, 3)}


def main(patterns):
    paths = []
    for p in patterns:
        paths.extend(sorted(glob.glob(p)) or [p])

    runs = {}   # (model, fault, rate, config) -> metrics ; fault None = baseline
    collisions = []
    for path in paths:
        m = RUN_RE.match(os.path.basename(path))
        if not m:
            print(f"skip (name not recognized): {path}")
            continue
        metrics = load_run(path)
        if metrics is None:
            print(f"skip (no complete elements): {path}")
            continue
        model = m.group("model")
        fault = m.group("fault")            # None for baseline
        rate = int(m.group("rate")) / 100 if m.group("rate") else 0.0
        # CHANGED (C4): configuration is part of the identity of a run
        config = "dual-file" if m.group("dual") else ("single-file" if fault else "-")
        key = (model, fault, rate, config)
        if key in runs:
            collisions.append(key)
        runs[key] = metrics

    if collisions:
        print("\nWARNING: duplicate run keys detected — later files overwrote earlier ones:")
        for k in collisions:
            print(f"   {k}")

    baselines = {mdl: v for (mdl, f, r, c), v in runs.items() if f is None}
    if not baselines:
        print("WARNING: no baseline export found (a sensitivity-<model>.json "
              "without a fault tag). Deltas cannot be computed.")

    rows = []
    for (model, fault, rate, config), v in sorted(
            runs.items(), key=lambda k: (k[0][0], k[0][1] or "", k[0][3], k[0][2])):
        base = baselines.get(model)
        row = {"model": model, "fault": fault or "baseline", "config": config,
               "rate": rate, "n_elements": v["n"],
               **{d: v[d] for d in DIMS}, "BQI": v["BQI"]}
        if base and fault:
            for d in DIMS:
                row[f"d{d}"] = round(v[d] - base[d], 3)
            row["dBQI"] = round(v["BQI"] - base["BQI"], 3)
            # selectivity: which dimension dropped the most
            drops = {d: base[d] - v[d] for d in DIMS}
            row["most_affected_dim"] = max(drops, key=drops.get) if any(
                x > 1e-9 for x in drops.values()) else "none"
        rows.append(row)

    header = ["model", "fault", "config", "rate", "n_elements", *DIMS, "BQI",
              "dD1", "dD2", "dD3", "dD4", "dBQI", "most_affected_dim"]
    with open("fault_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # console matrix: BQI (delta) per fault x rate, per model
    print(f"\n{'model':<26}{'fault':<8}{'config':<13}{'rate':>6}"
          f"{'BQI':>8}{'dBQI':>8}{'hit dim':>9}{'n':>5}")
    print("-" * 88)
    for r in rows:
        print(f"{r['model'][:25]:<26}{r['fault']:<8}{r['config']:<13}{r['rate']:>6.2f}"
              f"{r['BQI']:>8.3f}{r.get('dBQI', 0) or 0:>8.3f}"
              f"{r.get('most_affected_dim', '-') or '-':>9}{r['n_elements']:>5}")

    # monotonicity check per model+fault+config
    print("\nMonotonicity check (BQI should decrease as rate increases):")
    by_mf = {}
    for r in rows:
        if r["fault"] != "baseline":
            by_mf.setdefault((r["model"], r["fault"], r["config"]), []).append(
                (r["rate"], r["BQI"]))
    violations = 0
    for (model, fault, config), seq in sorted(by_mf.items()):
        seq.sort()
        bqis = [b for _, b in seq]
        mono = all(bqis[i] >= bqis[i + 1] - 1e-9 for i in range(len(bqis) - 1))
        if not mono:
            violations += 1
        print(f"  {model[:28]:<30}{fault} {config:<12}: {'OK' if mono else 'VIOLATION'} "
              f"({' -> '.join(f'{b:.3f}' for b in bqis)})")
    print(f"\n{len(by_mf)} model x fault x config combinations checked, "
          f"{violations} violation(s).")

    # F4 single-file null-result guard: a non-zero dBQI means contamination
    bad = [r for r in rows
           if r["fault"] == "F4" and r["config"] == "single-file"
           and abs(r.get("dBQI", 0) or 0) > 1e-9]
    if bad:
        print("\nWARNING: F4 single-file should give dBQI = 0.000 by design.")
        print("Non-zero values mean Pipeline A read a pre-seeded baseline XLSX")
        print("instead of converting the faulted file. Clear *__F*_ifc.xlsx and re-run:")
        for r in bad:
            print(f"   {r['model']} F4 r{r['rate']:.2f}: dBQI = {r['dBQI']:+.3f}")

    print("\nWritten: fault_analysis.csv")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python fault_analysis.py "sensitivity-*.json"')
        sys.exit(1)
    main(sys.argv[1:])
