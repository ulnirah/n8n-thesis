#!/usr/bin/env python3
"""
Sensitivity analysis for the BQI risk screening pipeline.
EMJM NORISK thesis: Uncertainty-Aware Risk Screening from Imperfect BIM.

Purpose
-------
The BQI weights (w1..w4) and the uncertainty coefficient alpha are expert-set
constants. This script characterizes how sensitive the SCREENING DECISION
(the risk ranking and High/Medium/Low labels) is to those constants.
If rankings stay stable across reasonable parameter ranges, the exact values
are shown to be non-critical for the screening outcome, which is the
justification argument used in the thesis.

Key insight: everything downstream of the per-element inputs
(D1..D4, L, C) is closed-form:
    BQI   = w1*D1 + w2*D2 + w3*D3 + w4*D4
    R_raw = clamp01(L * C)
    R_adj = min(1, R_raw * (1 + alpha * (1 - BQI)))
So one pipeline run per model gives enough data to evaluate ALL parameter
variants offline, without re-running n8n.

Input
-----
A JSON file exported from n8n (see the export node in the accompanying
instructions): a list of objects with at least
    GlobalId, Category,
    score_completeness, score_validity, score_qto_coverage, score_qto_agreement,
    likelihood_score, consequence_score

Usage
-----
    python sensitivity_analysis.py sensitivity_dataset.json
Outputs sensitivity_results.csv and prints a summary table.
Pure standard library. No scipy or pandas required.
"""

import json
import sys
import glob
import os
import csv
import random
from itertools import combinations

# ---------------------------------------------------------------- baseline --
BASE_WEIGHTS = {"w1": 0.35, "w2": 0.25, "w3": 0.20, "w4": 0.20}
BASE_ALPHA   = 0.5

# Label thresholds replicate Node 4.5 (dynamic percentiles with floors)
def label_thresholds(scores):
    s = sorted(scores, reverse=True)
    n = len(s)
    if n == 0:
        return 0.40, 0.15
    high = max(s[int(n * 0.75)] if int(n * 0.75) < n else 0, 0.40)
    low  = min(max(s[int(n * 0.25)] if int(n * 0.25) < n else 0, 0.15), high - 0.01)
    return high, low

def clamp01(x):
    return max(0.0, min(1.0, x))

def compute(elements, weights, alpha):
    """Return list of (GlobalId, R_adj, label) under the given parameters."""
    scored = []
    for e in elements:
        bqi = (weights["w1"] * e["score_completeness"]
             + weights["w2"] * e["score_validity"]
             + weights["w3"] * e["score_qto_coverage"]
             + weights["w4"] * e["score_qto_agreement"])
        r_raw = clamp01(e["likelihood_score"] * e["consequence_score"])
        r_adj = min(1.0, r_raw * (1 + alpha * (1 - bqi)))
        scored.append([e["GlobalId"], r_adj])
    high_t, low_t = label_thresholds([s[1] for s in scored])
    out = []
    for gid, r in scored:
        lbl = "High" if r >= high_t else ("Low" if r <= low_t else "Medium")
        out.append((gid, r, lbl))
    return out

# --------------------------------------------------------------- statistics --
def spearman(rank_a, rank_b):
    """Spearman rank correlation between two {GlobalId: rank} dicts."""
    keys = list(rank_a.keys())
    n = len(keys)
    if n < 2:
        return 1.0
    d2 = sum((rank_a[k] - rank_b[k]) ** 2 for k in keys)
    return 1 - (6 * d2) / (n * (n * n - 1))

def to_ranks(result):
    """result: list of (gid, score, label) -> {gid: rank} with average ranks for ties."""
    ordered = sorted(result, key=lambda t: -t[1])
    ranks, i = {}, 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1][1] == ordered[i][1]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[ordered[k][0]] = avg
        i = j + 1
    return ranks

def compare(baseline, variant):
    rb, rv = to_ranks(baseline), to_ranks(variant)
    srcc = spearman(rb, rv)
    lb = {g: l for g, _, l in baseline}
    lv = {g: l for g, _, l in variant}
    flips = sum(1 for g in lb if lb[g] != lv[g])
    top10_b = {g for g, _, _ in sorted(baseline, key=lambda t: -t[1])[:10]}
    top10_v = {g for g, _, _ in sorted(variant,  key=lambda t: -t[1])[:10]}
    jac = len(top10_b & top10_v) / max(1, len(top10_b | top10_v))
    return srcc, flips, len(lb), jac

# ------------------------------------------------------------------- main ---
def main(path, all_rows):
    model = os.path.basename(path).replace("sensitivity-", "").replace(".json", "")
    with open(path, encoding="utf-8") as f:
        elements = json.load(f)
    required = ["GlobalId", "score_completeness", "score_validity",
                "score_qto_coverage", "score_qto_agreement",
                "likelihood_score", "consequence_score"]
    elements = [e for e in elements if all(k in e and e[k] is not None for k in required)]
    print(f"Loaded {len(elements)} elements with complete fields.\n")

    baseline = compute(elements, BASE_WEIGHTS, BASE_ALPHA)
    rows = []

    # --- Experiment 1: alpha sweep (weights fixed at baseline) --------------
    for a in [0.0, 0.25, 0.5, 0.75, 1.0]:
        variant = compute(elements, BASE_WEIGHTS, a)
        srcc, flips, n, jac = compare(baseline, variant)
        rows.append(["alpha_sweep", f"alpha={a:.2f}", srcc, flips, n, jac])

    # --- Experiment 2: named weight schemes (alpha fixed at baseline) -------
    schemes = {
        "baseline 0.35/0.25/0.20/0.20": {"w1": 0.35, "w2": 0.25, "w3": 0.20, "w4": 0.20},
        "equal 0.25 each":              {"w1": 0.25, "w2": 0.25, "w3": 0.25, "w4": 0.25},
        # Tests whether D4 (cross-pipeline agreement) deserves its 0.20 weight
        "D4 downweighted 0.40/0.30/0.20/0.10": {"w1": 0.40, "w2": 0.30, "w3": 0.20, "w4": 0.10},
        # Rank-order centroid for 4 ranked criteria (Barron & Barrett 1996)
        "ROC 0.521/0.271/0.146/0.063":  {"w1": 0.5208, "w2": 0.2708, "w3": 0.1458, "w4": 0.0625},
    }
    for name, w in schemes.items():
        variant = compute(elements, w, BASE_ALPHA)
        srcc, flips, n, jac = compare(baseline, variant)
        rows.append(["weight_scheme", name, srcc, flips, n, jac])

    # --- Experiment 3: pairwise +/-0.05 weight shifts ------------------------
    keys = ["w1", "w2", "w3", "w4"]
    for a_k, b_k in combinations(keys, 2):
        for delta in (0.05, -0.05):
            w = dict(BASE_WEIGHTS)
            w[a_k] = round(w[a_k] + delta, 4)
            w[b_k] = round(w[b_k] - delta, 4)
            if min(w.values()) < 0:
                continue
            variant = compute(elements, w, BASE_ALPHA)
            srcc, flips, n, jac = compare(baseline, variant)
            rows.append(["weight_perturbation",
                         f"{a_k}{'+' if delta > 0 else '-'}0.05 {b_k}{'-' if delta > 0 else '+'}0.05",
                         srcc, flips, n, jac])

    # --- Experiment 4: random simplex sampling (global robustness) ----------
    random.seed(42)  # reproducibility
    worst = (2.0, None)   # start above 1 so the first sample always registers
    srccs = []
    for _ in range(500):
        cuts = sorted(random.random() for _ in range(3))
        ws = [cuts[0], cuts[1] - cuts[0], cuts[2] - cuts[1], 1 - cuts[2]]
        w = dict(zip(keys, ws))
        variant = compute(elements, w, BASE_ALPHA)
        srcc, flips, n, jac = compare(baseline, variant)
        srccs.append(srcc)
        if srcc < worst[0]:
            worst = (srcc, w)
    srccs.sort()
    rows.append(["random_simplex_500", "median SRCC", srccs[len(srccs) // 2], "", "", ""])
    rows.append(["random_simplex_500", "5th percentile SRCC", srccs[int(len(srccs) * 0.05)], "", "", ""])
    rows.append(["random_simplex_500",
                 "worst SRCC (w=" + ", ".join(f"{v:.2f}" for v in worst[1].values()) + ")",
                 worst[0], "", "", ""])

    # --- write CSV + print ---------------------------------------------------
    for r in rows:
        all_rows.append([model] + r)

    print(f"{'experiment':<22}{'variant':<42}{'SRCC':>8}{'flips':>7}{'top10 J':>9}")
    print("-" * 88)
    for r in rows:
        srcc = f"{r[2]:.4f}" if isinstance(r[2], float) else r[2]
        jac  = f"{r[5]:.2f}" if isinstance(r[5], float) else r[5]
        print(f"{r[0]:<22}{str(r[1]):<42}{srcc:>8}{str(r[3]):>7}{jac:>9}")
    print("Interpretation guide: SRCC >= 0.95 means the screening ranking is")
    print("effectively unchanged; label_flips shows how many elements would")
    print("change High/Medium/Low class under that parameter choice.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python sensitivity_analysis.py "sensitivity-*.json" [--baselines-only]')
        sys.exit(1)
    args = [a for a in sys.argv[1:] if a != "--baselines-only"]
    baselines_only = "--baselines-only" in sys.argv
    paths = []
    for a in args:
        paths.extend(sorted(glob.glob(a)) or [a])
    if baselines_only:
        paths = [p for p in paths if "__F" not in os.path.basename(p)]
    all_rows = []
    for p in paths:
        print(f"\n########## {p} ##########")
        main(p, all_rows)
    header = ["model", "experiment", "variant", "SRCC_vs_baseline",
              "label_flips", "n_elements", "top10_jaccard"]
    with open("sensitivity_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in all_rows:
            w.writerow([f"{x:.4f}" if isinstance(x, float) else x for x in r])
    print(f"\nWritten: sensitivity_results.csv "
          f"({len(all_rows)} rows across {len(paths)} models — one combined file, "
          f"model in first column; pivot in Excel per model)")
    # corpus-wide worst case for the paper sentence
    srccs = [float(r[3]) for r in all_rows if isinstance(r[3], float) or str(r[3]).replace('.','',1).isdigit()]
    if srccs:
        print(f"Corpus-wide minimum SRCC across all variants: {min(srccs):.4f}")
