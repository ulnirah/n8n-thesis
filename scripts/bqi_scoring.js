// ============================================================
// Block 4: BQI (BIM Quality Index) Scoring
// Scores each element on completeness, validity, and QTO trust
// Produces per-element BQI score + confidence label
// ============================================================

const allItems = $input.all();

// Separate item types
const qtoSummary = allItems.find(i => i.json._type === 'qto_summary');
const qtoComparisons = allItems.filter(i => i.json._type === 'qto_comparison');
const elements = allItems.filter(i => i.json._type === 'element');

// Build SRCC lookup from summary
const srccLookup = {};
if (qtoSummary && qtoSummary.json.srcc_results) {
  for (const s of qtoSummary.json.srcc_results) {
    srccLookup[s.QtoField] = s.SRCC;
  }
}

// Build QTO comparison lookup by GlobalId
const qtoByGid = {};
for (const comp of qtoComparisons) {
  const gid = comp.json.GlobalId;
  if (!qtoByGid[gid]) qtoByGid[gid] = [];
  qtoByGid[gid].push(comp.json);
}

// ── BQI Scoring Rules ──
// Each dimension scores 0-1, weighted sum produces final BQI

const WEIGHTS = {
  completeness: 0.35,  // Are required properties present?
  validity: 0.25,      // Are property values valid/non-empty?
  qto_coverage: 0.20,  // Does this element have QTO data?
  qto_agreement: 0.20, // Do pipelines A and B agree on QTO?
};

// Required properties per element type (IFC standard)
const REQUIRED_PROPS = {
  'IfcWall': ['IsExternal', 'LoadBearing'],
  'IfcWallStandardCase': ['IsExternal', 'LoadBearing'],
  'IfcSlab': ['IsExternal', 'LoadBearing'],
  'IfcSlabStandardCase': ['IsExternal', 'LoadBearing'],
  'IfcBeam': ['IsExternal', 'LoadBearing'],
  'IfcColumn': ['IsExternal', 'LoadBearing'],
  'IfcRoof': ['IsExternal'],
  'IfcDoor': ['IsExternal', 'FireRating'],
  'IfcWindow': ['IsExternal'],
  'IfcChimney': [],
  'IfcSpace': ['IsExternal', 'GrossPlannedArea'],
  'IfcFurniture': [],
  'IfcBuildingElementProxy': [],
  'IfcSpatialZone': [],
  'IfcZone': [],
};

// Expected QTO quantities per element type
const EXPECTED_QTO = {
  'IfcWall': ['NetVolume', 'Width', 'Length', 'NetSideArea'],
  'IfcWallStandardCase': ['NetVolume', 'Width', 'Length', 'NetSideArea'],
  'IfcSlab': ['NetVolume', 'Depth', 'NetArea'],
  'IfcSlabStandardCase': ['NetVolume', 'Depth', 'NetArea'],
  'IfcBeam': ['NetVolume', 'Length'],
  'IfcColumn': ['NetVolume', 'Length'],
  'IfcRoof': [],
  'IfcSpace': [],
};

function scoreElement(elem) {
  const type = elem.Category || elem.Type || '';
  const gid = elem.GlobalId;
  
  // ── 1. Completeness: required properties present ──
  const required = REQUIRED_PROPS[type] || [];
  let completenessScore = 1.0;
  const missingProps = [];
  
  if (required.length > 0) {
    let found = 0;
    for (const prop of required) {
      // Check if any key contains this property name
      const hasIt = Object.keys(elem).some(k => 
        k.includes(prop) && elem[k] !== '' && elem[k] !== null && elem[k] !== undefined
      );
      if (hasIt) {
        found++;
      } else {
        missingProps.push(prop);
      }
    }
    completenessScore = found / required.length;
  }
  
  // ── 2. Validity: non-empty, non-placeholder values ──
  const propKeys = Object.keys(elem).filter(k => k.startsWith('[Pset_'));
  let validityScore = 1.0;
  const invalidProps = [];
  
  if (propKeys.length > 0) {
    let valid = 0;
    for (const k of propKeys) {
      const val = elem[k];
      const isValid = val !== '' && val !== null && val !== undefined
        && val !== "['UNSET']" && val !== 'UNSET' && val !== 'N/A';
      if (isValid) {
        valid++;
      } else {
        invalidProps.push(k);
      }
    }
    validityScore = valid / propKeys.length;
  }
  
  // ── 3. QTO Coverage: does this element have quantity data? ──
  const expectedQto = EXPECTED_QTO[type] || [];
  let qtoCoverageScore = 1.0;
  const missingQto = [];
  
  if (expectedQto.length > 0) {
    let found = 0;
    for (const qty of expectedQto) {
      const hasIt = Object.keys(elem).some(k => 
        k.includes(qty) && elem[k] !== '' && elem[k] !== null
      );
      if (hasIt) {
        found++;
      } else {
        missingQto.push(qty);
      }
    }
    qtoCoverageScore = found / expectedQto.length;
  } else {
    // No QTO expected for this type — neutral score
    qtoCoverageScore = 1.0;
  }
  
  // ── 4. QTO Agreement: do pipelines agree? ──
  let qtoAgreementScore = 1.0;
  const qtoComps = qtoByGid[gid] || [];
  
  if (qtoComps.length > 0) {
    const matchingComps = qtoComps.filter(c => 
      c.Match === 'exact' || c.Match === 'negligible'
    );
    qtoAgreementScore = matchingComps.length / qtoComps.length;
  }
  
  // ── Weighted BQI Score ──
  const bqi = (
    WEIGHTS.completeness * completenessScore +
    WEIGHTS.validity * validityScore +
    WEIGHTS.qto_coverage * qtoCoverageScore +
    WEIGHTS.qto_agreement * qtoAgreementScore
  );
  
  // ── Confidence Label ──
  let confidence;
  if (bqi >= 0.85) confidence = 'high';
  else if (bqi >= 0.60) confidence = 'medium';
  else confidence = 'low';
  
  // ── Penalty flags for risk screening ──
  const penalties = [];
  if (completenessScore < 0.5) penalties.push('incomplete_properties');
  if (validityScore < 0.5) penalties.push('invalid_values');
  if (qtoCoverageScore < 0.5) penalties.push('missing_qto');
  if (qtoAgreementScore < 0.5) penalties.push('qto_disagreement');
  if (!elem.Material || elem.Material === '') penalties.push('no_material');
  
  return {
    _type: 'bqi_scored',
    GlobalId: gid,
    Name: elem.Name || '',
    Category: type,
    Material: elem.Material || '',
    ObjectType: elem.ObjectType || '',
    
    // BQI scores
    bqi_score: Math.round(bqi * 1000) / 1000,
    bqi_confidence: confidence,
    
    // Sub-scores (for transparency/explainability)
    score_completeness: Math.round(completenessScore * 100) / 100,
    score_validity: Math.round(validityScore * 100) / 100,
    score_qto_coverage: Math.round(qtoCoverageScore * 100) / 100,
    score_qto_agreement: Math.round(qtoAgreementScore * 100) / 100,
    
    // Details for audit trail
    missing_properties: missingProps,
    invalid_properties: invalidProps,
    missing_qto: missingQto,
    penalties: penalties,
    
    // Pass through QTO values for risk screening
    ...Object.fromEntries(
      Object.entries(elem).filter(([k]) => k.startsWith('[Qto_'))
    ),
    
    // Pass through key properties for risk screening
    ...Object.fromEntries(
      Object.entries(elem).filter(([k]) => k.startsWith('[Pset_'))
    ),
  };
}

// ── Score all elements ──
const output = [];

// Pass through the QTO summary
if (qtoSummary) {
  output.push(qtoSummary);
}

// Score elements from Pipeline B (has the most complete data)
const bElements = allItems.filter(i => 
  i.json._type === 'element' && i.json.pipeline === 'B_ifcopenshell'
);

// If no Pipeline B elements, fall back to Pipeline A
const elementsToScore = bElements.length > 0 ? bElements :
  allItems.filter(i => i.json._type === 'element' && i.json.pipeline === 'A_ddc');

for (const elem of elementsToScore) {
  const scored = scoreElement(elem.json);
  output.push({ json: scored });
}

// Model-level BQI summary
const scoredElements = output.filter(i => i.json._type === 'bqi_scored');
const avgBqi = scoredElements.length > 0
  ? scoredElements.reduce((sum, i) => sum + i.json.bqi_score, 0) / scoredElements.length
  : 0;

const bqiDistribution = {
  high: scoredElements.filter(i => i.json.bqi_confidence === 'high').length,
  medium: scoredElements.filter(i => i.json.bqi_confidence === 'medium').length,
  low: scoredElements.filter(i => i.json.bqi_confidence === 'low').length,
};

output.unshift({
  json: {
    _type: 'bqi_model_summary',
    model_bqi: Math.round(avgBqi * 1000) / 1000,
    model_confidence: avgBqi >= 0.85 ? 'high' : avgBqi >= 0.60 ? 'medium' : 'low',
    total_elements_scored: scoredElements.length,
    distribution: bqiDistribution,
    weights_used: WEIGHTS,
  }
});

return output;
