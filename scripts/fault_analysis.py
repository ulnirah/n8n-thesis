#!/usr/bin/env python3
"""
Fault-injection analysis: aggregates the per-run sensitivity exports into the
baseline-vs-faulted comparison that the report itself never shows.

How it fits the experiment:
  1. fault_injection.py generates the faulted IFC files (with names like
     model__F1-r25-s42.ifc).
  2. You run the n8n pipeline once per file. The Sensitivity Analysis node
     writes sensitivity-<name>.json per run, so the fault tag travels in the
     filename automatically.
  3. This script reads ALL those exports, recomputes Model BQI and the D1-D4
     averages per run, matches each faulted run to its model baseline, and
     writes the comparison table (deltas + selectivity check) as CSV.

The CSV is the data behind the paper's fault-response figure: open it in
Excel and chart BQI vs severity per fault type.

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

# sensitivity-<model>__F3-r25-s42[_PIPELINE-B-ONLY].json  -> (model, F3, 0.25)
RUN_RE = re.compile(
    r"^sensitivity-(?P<model>.+?)"
    r"(?:__(?P<fault>F\d)-r(?P<rate>\d{2})-s(?P<seed>\d+)(?P<heavy>-heavy)?)?"
    r"(?:_PIPELINE-B-ONLY)?\.json$"
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
    return {"n": n, **{d: round(avg[d], 4) for d in DIMS}, "BQI": round(bqi, 4)}


def main(patterns):
    paths = []
    for p in patterns:
        paths.extend(sorted(glob.glob(p)) or [p])

    runs = {}   # (model, fault, rate) -> metrics ; fault None = baseline
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
        runs[(model, fault, rate)] = metrics

    baselines = {mdl: v for (mdl, f, r), v in runs.items() if f is None}
    if not baselines:
        print("WARNING: no baseline export found (a sensitivity-<model>.json "
              "without a fault tag). Deltas cannot be computed.")

    rows = []
    for (model, fault, rate), v in sorted(runs.items(),
                                          key=lambda k: (k[0][0], k[0][1] or "", k[0][2])):
        base = baselines.get(model)
        row = {"model": model, "fault": fault or "baseline", "rate": rate,
               "n_elements": v["n"], **{d: v[d] for d in DIMS}, "BQI": v["BQI"]}
        if base and fault:
            for d in DIMS:
                row[f"d{d}"] = round(v[d] - base[d], 4)
            row["dBQI"] = round(v["BQI"] - base["BQI"], 4)
            # selectivity: which dimension dropped the most
            drops = {d: base[d] - v[d] for d in DIMS}
            row["most_affected_dim"] = max(drops, key=drops.get) if any(
                x > 1e-9 for x in drops.values()) else "none"
        rows.append(row)

    header = ["model", "fault", "rate", "n_elements", *DIMS, "BQI",
              "dD1", "dD2", "dD3", "dD4", "dBQI", "most_affected_dim"]
    with open("fault_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # console matrix: BQI (delta) per fault x rate, per model
    print(f"\n{'model':<28}{'fault':<10}{'rate':>6}{'BQI':>9}{'dBQI':>9}{'hit dim':>9}{'n':>5}")
    print("-" * 78)
    for r in rows:
        print(f"{r['model'][:27]:<28}{r['fault']:<10}{r['rate']:>6.2f}"
              f"{r['BQI']:>9.4f}{r.get('dBQI', 0) or 0:>9.4f}"
              f"{r.get('most_affected_dim', '-') or '-':>9}{r['n_elements']:>5}")

    # quick criteria check per model+fault: monotonic in severity?
    print("\nMonotonicity check (BQI should decrease as rate increases):")
    by_mf = {}
    for r in rows:
        if r["fault"] != "baseline":
            by_mf.setdefault((r["model"], r["fault"]), []).append((r["rate"], r["BQI"]))
    for (model, fault), seq in sorted(by_mf.items()):
        seq.sort()
        bqis = [b for _, b in seq]
        mono = all(bqis[i] >= bqis[i + 1] - 1e-9 for i in range(len(bqis) - 1))
        print(f"  {model[:30]:<32}{fault}: {'OK' if mono else 'VIOLATION'} "
              f"({' -> '.join(f'{b:.3f}' for b in bqis)})")
    print("\nWritten: fault_analysis.csv (chart BQI vs rate per fault type in Excel)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python fault_analysis.py "sensitivity-*.json"')
        sys.exit(1)
    main(sys.argv[1:])
