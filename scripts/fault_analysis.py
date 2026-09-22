#!/usr/bin/env python3
"""
Fault-injection analysis: aggregates the per-run sensitivity exports into the
baseline-vs-faulted comparison that the report itself never shows.

Run identity
------------
A run is identified by (model, fault, rate, configuration). F4 and F6 exist in
both configurations at the same model and rate, so the configuration is kept
as its own CSV column. Dual-file exports carry the "_DUALFILE" suffix, which
the Sensitivity Analysis node appends when project_file_b is set. All
comparisons use full-precision values; rounding is for display only.

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

# The pipeline-B marker and the dual-file marker are captured, so the two
# configurations stay distinct.
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
    # Full precision is carried for every comparison and rounded only for
    # display: deciding most_affected_dim from 3 dp values can swap two
    # dimensions that differ by ~0.001.
    return {"n": n,
            "full": avg, "bqi_full": bqi,
            **{d: round(avg[d], 3) for d in DIMS},
            "BQI": round(bqi, 3)}


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
        # configuration is part of the identity of a run
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
            # deltas and selectivity from full-precision values
            for d in DIMS:
                row[f"d{d}"] = round(v["full"][d] - base["full"][d], 4)
            row["dBQI"] = round(v["bqi_full"] - base["bqi_full"], 4)
            drops = {d: base["full"][d] - v["full"][d] for d in DIMS}
            ranked = sorted(drops.items(), key=lambda kv: -kv[1])
            if ranked[0][1] > 1e-9:
                row["most_affected_dim"] = ranked[0][0]
                row["runner_up_dim"] = ranked[1][0]
                # margin over runner-up: small values mean a borderline call
                row["margin_over_2nd"] = round(ranked[0][1] - ranked[1][1], 5)
            else:
                row["most_affected_dim"] = "none"
                row["runner_up_dim"] = ""
                row["margin_over_2nd"] = ""
        rows.append(row)

    header = ["model", "fault", "config", "rate", "n_elements", *DIMS, "BQI",
              "dD1", "dD2", "dD3", "dD4", "dBQI",
              "most_affected_dim", "runner_up_dim", "margin_over_2nd"]
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

    # borderline selectivity calls: margin over the runner-up < 0.002
    close = [r for r in rows
             if isinstance(r.get("margin_over_2nd"), float)
             and r["margin_over_2nd"] < 0.002]
    if close:
        print("\nBORDERLINE selectivity calls (margin < 0.002 over runner-up).")
        print("Treat these as near-ties rather than decisive calls:")
        for r in close:
            print(f"   {r['model'][:28]:<30}{r['fault']} r{r['rate']:.2f} "
                  f"{r['config']:<12} {r['most_affected_dim']} over "
                  f"{r['runner_up_dim']} by {r['margin_over_2nd']:.5f}")

    # F2 target-dimension tally across manifesting runs
    f2 = [r for r in rows if r["fault"] == "F2"
          and r.get("most_affected_dim") not in (None, "", "none")]
    if f2:
        tally = {}
        for r in f2:
            tally[r["most_affected_dim"]] = tally.get(r["most_affected_dim"], 0) + 1
        print("\nF2 most-affected dimension across all manifesting runs:")
        for d in DIMS:
            if d in tally:
                print(f"   {d}: {tally[d]}")
        print(f"   total manifesting F2 runs: {len(f2)}")

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
