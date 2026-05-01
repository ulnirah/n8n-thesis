// Input Parsing and Validation
const allItems = $input.all();

const pipelineA = allItems.filter(i => i.json.pipeline === 'A_ddc');
const pipelineB = allItems.filter(i => i.json.pipeline === 'B_ifcopenshell');

if (pipelineA.length === 0 || pipelineB.length === 0) {
  return [{ json: {
    error: 'Missing pipeline data',
    pipelineA_count: pipelineA.length,
    pipelineB_count: pipelineB.length,
  }}];
}

const lookupA = {};
const lookupB = {};
pipelineA.forEach(i => { lookupA[i.json.GlobalId] = i.json; });
pipelineB.forEach(i => { lookupB[i.json.GlobalId] = i.json; });

const sharedGids = Object.keys(lookupA).filter(gid =>  lookupB[gid]);
const onlyA      = Object.keys(lookupA).filter(gid => !lookupB[gid]);
const onlyB      = Object.keys(lookupB).filter(gid => !lookupA[gid]);

// QTO Comparison Per Element
const qtoPattern = /^\[Qto_/;
const comparisons = [];
const allDeltas   = [];

for (const gid of sharedGids) {
  const a = lookupA[gid];
  const b = lookupB[gid];

  const allQtoFields = [...new Set([
    ...Object.keys(a).filter(k => qtoPattern.test(k)),
    ...Object.keys(b).filter(k => qtoPattern.test(k)),
  ])];

  for (const field of allQtoFields) {
    const valA = parseFloat(a[field]);
    const valB = parseFloat(b[field]);
    const hasA = !isNaN(valA);
    const hasB = !isNaN(valB);

    let delta = null, pctDiff = null, match = 'missing';

    if (hasA && hasB) {
      delta   = valB - valA;
      pctDiff = valA !== 0 ? (Math.abs(delta) / Math.abs(valA)) * 100 : 0;
      match   = Math.abs(delta) < 1e-10 ? 'exact'       :
                pctDiff < 0.01          ? 'negligible'  :
                pctDiff < 1.0           ? 'minor'       : 'significant';
      allDeltas.push({ gid, field, valA, valB, delta, pctDiff });
    } else {
      match = hasA ? 'only_in_A' : 'only_in_B';
    }

    comparisons.push({
      GlobalId: gid,
      Name:     a.Name     || b.Name     || '',
      Type:     a.Category || b.Category || '',
      QtoField: field,
      Value_A:  hasA ? valA : null,
      Value_B:  hasB ? valB : null,
      Delta:    delta,
      PctDiff:  pctDiff,
      Match:    match,
    });
  }
}

// Spearman Rank Correlation (SRCC)
function spearmanRank(values) {
  const sorted = values.map((v, i) => ({ val: v, idx: i })).sort((a, b) => a.val - b.val);
  const ranks  = new Array(values.length);
  let i = 0;
  while (i < sorted.length) {
    let j = i;
    while (j < sorted.length && sorted[j].val === sorted[i].val) j++;
    const avgRank = (i + j + 1) / 2;
    for (let k = i; k < j; k++) ranks[sorted[k].idx] = avgRank;
    i = j;
  }
  return ranks;
}

function calcSRCC(ranksA, ranksB) {
  const n = ranksA.length;
  if (n < 3) return null;
  const dSquaredSum = ranksA.reduce((sum, rA, i) => sum + (rA - ranksB[i]) ** 2, 0);
  return 1 - (6 * dSquaredSum) / (n * (n * n - 1));
}

// SRCC Per QTO Field
const qtoGroups = {};
for (const comp of comparisons) {
  if (comp.Value_A !== null && comp.Value_B !== null) {
    if (!qtoGroups[comp.QtoField]) qtoGroups[comp.QtoField] = [];
    qtoGroups[comp.QtoField].push(comp);
  }
}

const srccResults = [];
for (const [field, items] of Object.entries(qtoGroups)) {
  if (items.length < 3) {
    srccResults.push({ QtoField: field, ElementCount: items.length, SRCC: null,
      Note: 'Too few elements for SRCC (need >= 3)' });
    continue;
  }

  const ranksA = spearmanRank(items.map(i => i.Value_A));
  const ranksB = spearmanRank(items.map(i => i.Value_B));
  const srcc   = calcSRCC(ranksA, ranksB);
  const srccR  = srcc !== null ? Math.round(srcc * 10000) / 10000 : null;

  srccResults.push({
    QtoField:    field,
    ElementCount: items.length,
    SRCC:        srccR,
    RankStable:  srcc !== null && srcc >= 0.95,
    Note:        srcc === 1.0  ? 'Perfect rank agreement'              :
                 srcc >= 0.95  ? 'Strong rank agreement'               :
                 srcc >= 0.80  ? 'Moderate — risk rankings may differ' :
                                 'Weak — significant rank instability',
  });
}

// Summary and Output
const totalComps  = comparisons.filter(c => c.Value_A !== null && c.Value_B !== null).length;
const exactMatches = comparisons.filter(c => c.Match === 'exact').length;
const maxDelta    = allDeltas.length > 0
  ? allDeltas.reduce((max, d) => Math.abs(d.delta) > Math.abs(max.delta) ? d : max)
  : null;

const output = [];

output.push({ json: {
  _type:                  'qto_summary',
  total_elements_A:       pipelineA.length,
  total_elements_B:       pipelineB.length,
  shared_elements:        sharedGids.length,
  only_in_A:              onlyA.length,
  only_in_B:              onlyB.length,
  total_qto_comparisons:  totalComps,
  exact_matches:          exactMatches,
  exact_match_pct:        totalComps > 0 ? Math.round((exactMatches / totalComps) * 10000) / 100 : 0,
  max_delta: maxDelta ? {
    element: maxDelta.gid, field: maxDelta.field,
    delta:   maxDelta.delta, pctDiff: maxDelta.pctDiff,
  } : null,
  srcc_results: srccResults,
}});

for (const comp of comparisons) {
  output.push({ json: { _type: 'qto_comparison', ...comp } });
}

return output;
