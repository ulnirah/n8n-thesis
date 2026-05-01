// Input Parsing
const allItems = $input.all();

const qtoSummary = allItems.find(i => i.json._type === 'qto_summary');
const qtoComparisons = allItems.filter(i => i.json._type === 'qto_comparison');
const elements = allItems.filter(i => i.json._type === 'element');

const srccLookup = {};
if (qtoSummary?.json.srcc_results) {
  for (const s of qtoSummary.json.srcc_results) {
    srccLookup[s.QtoField] = s.SRCC;
  }
}

const qtoByGid = {};
for (const comp of qtoComparisons) {
  const gid = comp.json.GlobalId;
  if (!qtoByGid[gid]) qtoByGid[gid] = [];
  qtoByGid[gid].push(comp.json);
}

// Weights and Rules
const WEIGHTS = {
  completeness:  0.35,
  validity:      0.25,
  qto_coverage:  0.20,
  qto_agreement: 0.20,
};

const REQUIRED_PROPS = {
  IfcWall:                  ['IsExternal', 'LoadBearing'],
  IfcWallStandardCase:      ['IsExternal', 'LoadBearing'],
  IfcSlab:                  ['IsExternal', 'LoadBearing'],
  IfcSlabStandardCase:      ['IsExternal', 'LoadBearing'],
  IfcBeam:                  ['IsExternal', 'LoadBearing'],
  IfcColumn:                ['IsExternal', 'LoadBearing'],
  IfcRoof:                  ['IsExternal'],
  IfcDoor:                  ['IsExternal', 'FireRating'],
  IfcWindow:                ['IsExternal'],
  IfcSpace:                 ['IsExternal', 'GrossPlannedArea'],
  IfcChimney:               [],
  IfcFurniture:             [],
  IfcBuildingElementProxy:  [],
  IfcSpatialZone:           [],
  IfcZone:                  [],
};

const EXPECTED_QTO = {
  IfcWall:             ['NetVolume', 'Width', 'Length', 'NetSideArea'],
  IfcWallStandardCase: ['NetVolume', 'Width', 'Length', 'NetSideArea'],
  IfcSlab:             ['NetVolume', 'Depth', 'NetArea'],
  IfcSlabStandardCase: ['NetVolume', 'Depth', 'NetArea'],
  IfcBeam:             ['NetVolume', 'Length'],
  IfcColumn:           ['NetVolume', 'Length'],
  IfcRoof:             [],
  IfcSpace:            [],
};

// Scoring Function
function scoreElement(elem) {
  const type = elem.Category || elem.Type || '';
  const gid  = elem.GlobalId;

  // Completeness
  const required = REQUIRED_PROPS[type] || [];
  const missingProps = required.filter(prop =>
    !Object.keys(elem).some(k => k.includes(prop) && elem[k] != null && elem[k] !== '')
  );
  const completenessScore = required.length > 0
    ? (required.length - missingProps.length) / required.length : 1.0;

  // Validity
  const propKeys = Object.keys(elem).filter(k => k.startsWith('[Pset_'));
  const invalidProps = propKeys.filter(k => {
    const v = elem[k];
    return v === '' || v === null || v === undefined || v === "['UNSET']" || v === 'UNSET' || v === 'N/A';
  });
  const validityScore = propKeys.length > 0
    ? (propKeys.length - invalidProps.length) / propKeys.length : 1.0;

  // QTO Coverage
  const expectedQto = EXPECTED_QTO[type] || [];
  const missingQto = expectedQto.filter(qty =>
    !Object.keys(elem).some(k => k.includes(qty) && elem[k] != null && elem[k] !== '')
  );
  const qtoCoverageScore = expectedQto.length > 0
    ? (expectedQto.length - missingQto.length) / expectedQto.length : 1.0;

  // QTO Agreement
  const qtoComps = qtoByGid[gid] || [];
  const qtoAgreementScore = qtoComps.length > 0
    ? qtoComps.filter(c => c.Match === 'exact' || c.Match === 'negligible').length / qtoComps.length
    : 1.0;

  // Final BQI
  const bqi =
    WEIGHTS.completeness  * completenessScore  +
    WEIGHTS.validity      * validityScore      +
    WEIGHTS.qto_coverage  * qtoCoverageScore   +
    WEIGHTS.qto_agreement * qtoAgreementScore;

  const confidence = bqi >= 0.85 ? 'high' : bqi >= 0.60 ? 'medium' : 'low';

  const penalties = [];
  if (completenessScore  < 0.5) penalties.push('incomplete_properties');
  if (validityScore      < 0.5) penalties.push('invalid_values');
  if (qtoCoverageScore   < 0.5) penalties.push('missing_qto');
  if (qtoAgreementScore  < 0.5) penalties.push('qto_disagreement');
  if (!elem.Material || elem.Material === '') penalties.push('no_material');

  return {
    _type:          'bqi_scored',
    GlobalId:       gid,
    Name:           elem.Name || '',
    Category:       type,
    Material:       elem.Material || '',
    ObjectType:     elem.ObjectType || '',
    bqi_score:      Math.round(bqi * 1000) / 1000,
    bqi_confidence: confidence,
    score_completeness:  Math.round(completenessScore * 100) / 100,
    score_validity:      Math.round(validityScore * 100) / 100,
    score_qto_coverage:  Math.round(qtoCoverageScore * 100) / 100,
    score_qto_agreement: Math.round(qtoAgreementScore * 100) / 100,
    missing_properties: missingProps,
    invalid_properties: invalidProps,
    missing_qto:        missingQto,
    penalties,
    ...Object.fromEntries(Object.entries(elem).filter(([k]) => k.startsWith('[Qto_'))),
    ...Object.fromEntries(Object.entries(elem).filter(([k]) => k.startsWith('[Pset_'))),
  };
}

// Run and Output
const elementsToScore = (() => {
  const b = allItems.filter(i => i.json._type === 'element' && i.json.pipeline === 'B_ifcopenshell');
  return b.length > 0 ? b : allItems.filter(i => i.json._type === 'element' && i.json.pipeline === 'A_ddc');
})();

const output = [];
if (qtoSummary) output.push(qtoSummary);
for (const elem of elementsToScore) output.push({ json: scoreElement(elem.json) });

const scored = output.filter(i => i.json._type === 'bqi_scored');
const avgBqi = scored.length > 0
  ? scored.reduce((s, i) => s + i.json.bqi_score, 0) / scored.length : 0;

output.unshift({ json: {
  _type:                 'bqi_model_summary',
  model_bqi:             Math.round(avgBqi * 1000) / 1000,
  model_confidence:      avgBqi >= 0.85 ? 'high' : avgBqi >= 0.60 ? 'medium' : 'low',
  total_elements_scored: scored.length,
  distribution: {
    high:   scored.filter(i => i.json.bqi_confidence === 'high').length,
    medium: scored.filter(i => i.json.bqi_confidence === 'medium').length,
    low:    scored.filter(i => i.json.bqi_confidence === 'low').length,
  },
  weights_used: WEIGHTS,
}});

return output;
