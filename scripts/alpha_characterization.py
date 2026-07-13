#!/usr/bin/env python3
"""
Alpha characterization: derive a justified value of the uncertainty
coefficient alpha from corpus data, instead of asserting it.

There is no external ground truth for alpha, so "optimal" must be defined
against a declared criterion. This script uses two requirements:

  (1) EFFECTIVENESS  - alpha must be large enough that data quality actually
      changes the screening outcome: at least one element in the corpus is
      escalated to a higher risk label compared to alpha = 0 (pure L x C).
  (2) INFORMATION PRESERVATION - alpha must be small enough that R_adj does
      not saturate at the 1.0 cap, which would destroy ranking information:
      the fraction of clamped elements stays <= CLAMP_LIMIT in every model.

The admissible interval is [alpha_min, alpha_max] where alpha_min is the
smallest alpha satisfying (1) corpus-wide and alpha_max is the largest alpha
satisfying (2) corpus-wide. The recommended alpha is the midpoint, rounded
to 0.05. Report the full table in the thesis, not only the recommendation.

Usage:
    python alpha_characterization.py M1.json M2.json ... M7.json
Outputs alpha_characterization.csv and prints per-model and corpus tables.
Pure standard library.
"""

import json
import sys
import glob
import csv

CLAMP_LIMIT = 0.05          # max tolerated fraction of elements clamped at 1.0
ALPHAS = [round(a * 0.05, 2) for a in range(0, 21)]   # 0.00 .. 1.00
WEIGHTS = {"w1": 0.35, "w2": 0.25, "w3": 0.20, "w4": 0.20}

def clamp01(x): return max(0.0, min(1.0, x))

def labels_for(scores):
    """Replicates Node 4.5: dynamic P75/P25 thresholds with floors."""
    s = sorted(scores, reverse=True)
    n = len(s)
    high = max(s[int(n * 0.75)] if int(n * 0.75) < n else 0, 0.40)
    low  = min(max(s[int(n * 0.25)] if int(n * 0.25) < n else 0, 0.15), high - 0.01)
    return ["High" if x >= high else ("Low" if x <= low else "Medium") for x in scores]

LABEL_ORDER = {"Low": 0, "Medium": 1, "High": 2}

def evaluate(elements, alpha):
    r_adj, clamped, bands = [], 0, []
    for e in elements:
        bqi = (WEIGHTS["w1"] * e["score_completeness"] + WEIGHTS["w2"] * e["score_validity"]
             + WEIGHTS["w3"] * e["score_qto_coverage"] + WEIGHTS["w4"] * e["score_qto_agreement"])
        r_raw = clamp01(e["likelihood_score"] * e["consequence_score"])
        w = alpha * (1 - bqi)
        adj = r_raw * (1 + w)
        if adj > 1.0:
            clamped += 1
            adj = 1.0
        r_adj.append(adj)
        bands.append(adj - max(0.0, r_raw * (1 - w)))
    return r_adj, clamped / max(1, len(elements)), (sum(bands) / max(1, len(bands)))

def main(paths):
    corpus = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        req = ["score_completeness", "score_validity", "score_qto_coverage",
               "score_qto_agreement", "likelihood_score", "consequence_score"]
        corpus[p] = [e for e in data if all(k in e and e[k] is not None for k in req)]
        print(f"{p}: {len(corpus[p])} elements")

    rows = []
    # Per-model, per-alpha metrics. Baseline labels are at alpha = 0.
    effective_at = {}   # model -> set of alphas with >= 1 escalation vs alpha 0
    ok_clamp_at  = {}   # model -> set of alphas with clamp fraction <= limit
    for name, elements in corpus.items():
        base_scores, _, _ = evaluate(elements, 0.0)
        base_labels = labels_for(base_scores)
        effective_at[name], ok_clamp_at[name] = set(), set()
        for a in ALPHAS:
            scores, clamp_frac, mean_band = evaluate(elements, a)
            labels = labels_for(scores)
            escalations = sum(1 for lb, lv in zip(base_labels, labels)
                              if LABEL_ORDER[lv] > LABEL_ORDER[lb])
            if escalations >= 1:
                effective_at[name].add(a)
            if clamp_frac <= CLAMP_LIMIT:
                ok_clamp_at[name].add(a)
            rows.append([name, a, escalations, round(clamp_frac, 4), round(mean_band, 4)])

    # Corpus-level admissible interval
    all_alphas = set(ALPHAS)
    # alpha effective corpus-wide: escalates somewhere in EVERY model?
    # Weaker, more realistic requirement: escalates in at least one model.
    effective_any = sorted(a for a in all_alphas if any(a in s for s in effective_at.values()))
    clamp_ok_all  = sorted(a for a in all_alphas if all(a in s for s in ok_clamp_at.values()))

    a_min = effective_any[0] if effective_any else None
    a_max = clamp_ok_all[-1] if clamp_ok_all else None

    with open("alpha_characterization.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "alpha", "label_escalations_vs_alpha0",
                    "clamp_fraction", "mean_band_width"])
        w.writerows(rows)

    print(f"\n{'model':<28}{'alpha':>6}{'escal.':>8}{'clamp%':>8}{'band':>8}")
    print("-" * 60)
    for r in rows:
        if r[1] in (0.0, 0.25, 0.5, 0.55, 0.75, 1.0):   # condensed view
            print(f"{r[0][:27]:<28}{r[1]:>6}{r[2]:>8}{r[3]*100:>7.1f}%{r[4]:>8}")

    print("\n=== Corpus-level result ===")
    print(f"Criterion 1 (effectiveness, >=1 escalation in any model): alpha >= {a_min}")
    print(f"Criterion 2 (clamping <= {CLAMP_LIMIT:.0%} in every model): alpha <= {a_max}")
    if a_min is not None and a_max is not None and a_min <= a_max:
        mid = round(((a_min + a_max) / 2) / 0.05) * 0.05
        print(f"Admissible interval: [{a_min}, {a_max}]  ->  recommended alpha = {mid:.2f} (midpoint)")
    else:
        print("No admissible interval under these criteria; report the table and")
        print("choose alpha by the fault-injection detection criterion instead.")
    print("\nWritten: alpha_characterization.csv")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python alpha_characterization.py dataset1.json [dataset2.json ...]")
        sys.exit(1)
    # Expand wildcards ourselves (Windows cmd/PowerShell do not)
    args = [a for a in sys.argv[1:] if a != "--baselines-only"]
    baselines_only = "--baselines-only" in sys.argv
    paths = []
    for a in args:
        paths.extend(sorted(glob.glob(a)) or [a])
    if baselines_only:
        import os
        paths = [p for p in paths if "__F" not in os.path.basename(p)]
        print(f"baselines only: {len(paths)} files")
    main(paths)
