const allItems = $input.all();

let projectFilePath = '';
try {
  projectFilePath = $node['0.1: Config'].json.project_file || '';
} catch(e) {
  projectFilePath = 'Unknown Project';
}
const projectFileName = projectFilePath.split('\\').pop().split('/').pop().replace(/\.[^/.]+$/, '');

const modelSummary  = allItems.find(i => i.json._type === 'bqi_model_summary') || { json: {} };
const riskElements  = allItems.filter(i => i.json._type === 'risk_element');
const qtoSummary    = allItems.find(i => i.json._type === 'qto_summary') || { json: {} };

const modelBQI        = +(modelSummary.json.model_bqi   || 0).toFixed(3);
const modelConf       = modelSummary.json.model_confidence || 'low';
const totalScored     = modelSummary.json.total_elements_scored || allItems.length;
const dist            = modelSummary.json.distribution || { high: 0, medium: 0, low: 0 };
const weights         = modelSummary.json.weights_used || { completeness: 0.35, validity: 0.25, qto_coverage: 0.20, qto_agreement: 0.20 };

const highRisk   = riskElements.filter(i => i.json.risk_label === 'High').length   || dist.high   || 0;
const medRisk    = riskElements.filter(i => i.json.risk_label === 'Medium').length || dist.medium || 0;
const lowRisk    = riskElements.filter(i => i.json.risk_label === 'Low').length    || dist.low    || 0;
const top10      = riskElements
  .sort((a,b) => (b.json.risk_score||0) - (a.json.risk_score||0))
  .slice(0, 10);

const srccResults = qtoSummary.json.srcc_results || [];
const avgSRCC     = srccResults.length
  ? (srccResults.reduce((s,r) => s + (r.SRCC||0), 0) / srccResults.length).toFixed(3)
  : 'N/A';

function confColor(conf) {
  if (conf === 'high')   return '#009a44';
  if (conf === 'medium') return '#ffa726';
  return '#dc3545';
}
function riskColor(label) {
  if (label === 'High')   return '#dc3545';
  if (label === 'Medium') return '#ffa726';
  return '#66bb6a';
}
function bqiBar(score) {
  const pct = Math.round((score||0) * 100);
  const col = score >= 0.7 ? '#009a44' : score >= 0.4 ? '#ffa726' : '#dc3545';
  return `<div style="background:#e0e0e0;height:6px;border-radius:3px;width:80px;display:inline-block;vertical-align:middle;margin-left:8px"><div style="height:100%;width:${pct}%;background:${col};border-radius:3px"></div></div>`;
}

const distData    = JSON.stringify([highRisk, medRisk, lowRisk]);
const bqiWeights  = JSON.stringify(Object.entries(weights).map(([k,v]) => ({ label: k.replace('_',' '), value: +(v*100).toFixed(0) })));
const srccChartData = JSON.stringify(srccResults.slice(0,8).map(r => ({ field: (r.QtoField||'').replace('[Qto_','').replace(']',''), srcc: +(r.SRCC||0).toFixed(3) })));
const top10Data   = JSON.stringify(top10.map(i => ({ id: (i.json.GlobalId||'').slice(0,8), score: +(i.json.risk_score||0).toFixed(3), bqi: +(i.json.bqi_score||0).toFixed(3), label: i.json.risk_label||'Low', type: i.json.Category||i.json._type||'' })));

const riskRows = top10.map((item, idx) => {
  const d = item.json;
  const label = d.risk_label || 'Low';
  return `<tr>
    <td>${idx+1}</td>
    <td style="font-family:monospace;font-size:11px">${(d.GlobalId||'—').slice(0,16)}</td>
    <td>${d.Category || d.ifc_type || '—'}</td>
    <td>${(d.zone || d.location_tag || '—')}</td>
    <td>${(+(d.bqi_score||0)).toFixed(2)} ${bqiBar(d.bqi_score)}</td>
    <td>${d.bqi_confidence || '—'}</td>
    <td>${(+(d.likelihood||0)).toFixed(2)}</td>
    <td>${(+(d.consequence||0)).toFixed(2)}</td>
    <td><strong>${(+(d.risk_score||0)).toFixed(3)}</strong></td>
    <td><span style="display:inline-block;padding:2px 8px;background:${riskColor(label)};color:white;font-size:11px;font-weight:600;border-radius:2px">${label.toUpperCase()}</span></td>
  </tr>`;
}).join('') || `<tr><td colspan="10" style="text-align:center;color:#999;padding:20px">Risk screening stubs (R1–R5) not yet implemented — placeholder data</td></tr>`;

const weightRows = Object.entries(weights).map(([k,v]) =>
  `<tr><td>${k.replace(/_/g,' ')}</td><td>${(v*100).toFixed(0)}%</td><td>${bqiBar(v)}</td></tr>`
).join('');

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Uncertainty-Aware Risk Register | ${projectFileName}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"><\/script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,'Helvetica Neue',sans-serif;background:#f5f5f5;color:#2e2e38;font-size:13px;line-height:1.6}
.container{max-width:1200px;margin:0 auto;padding:40px 20px}
.header{border-bottom:3px solid #0061a0;padding-bottom:20px;margin-bottom:30px;background:#fff;padding:24px 30px;border-left:6px solid #0061a0}
.header h1{font-size:26px;font-weight:300;color:#0061a0;margin-bottom:6px}
.header .subtitle{color:#696969;font-size:13px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.kpi-card{background:#fff;border:1px solid #e0e0e0;padding:20px;border-top:4px solid #ccc}
.kpi-card.blue{border-top-color:#0061a0}
.kpi-card.green{border-top-color:#009a44}
.kpi-card.amber{border-top-color:#ffa726}
.kpi-card.red{border-top-color:#dc3545}
.kpi-value{font-size:32px;font-weight:300;color:#0061a0;line-height:1;margin-bottom:6px}
.kpi-label{font-size:11px;color:#696969;text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.kpi-sub{font-size:11px;color:#999;margin-top:4px}
.section{background:#fff;border:1px solid #e0e0e0;margin-bottom:24px}
.section-header{background:#fafafa;padding:14px 20px;border-bottom:1px solid #e0e0e0}
.section-header h2{font-size:15px;font-weight:600;color:#2e2e38;margin:0}
.section-header p{font-size:12px;color:#696969;margin-top:3px}
.section-body{padding:20px}
.charts-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:24px}
.chart-box{background:#fff;border:1px solid #e0e0e0;padding:16px}
.chart-box h3{font-size:13px;font-weight:600;margin-bottom:12px;color:#2e2e38}
.chart-box.wide{grid-column:1/-1}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#f5f5f5;padding:10px 12px;text-align:left;font-weight:600;color:#2e2e38;border-bottom:2px solid #e0e0e0;font-size:11px;text-transform:uppercase;letter-spacing:.4px;white-space:nowrap}
td{padding:10px 12px;border-bottom:1px solid #f0f0f0;color:#4a4a4a;vertical-align:middle}
tr:hover{background:#fafafa}
.conf-badge{display:inline-block;padding:2px 7px;border-radius:2px;font-size:11px;font-weight:600}
.alert-box{border-left:4px solid #ffa726;background:#fff8e1;padding:16px 20px;margin-bottom:24px;font-size:13px}
.alert-box strong{color:#e65100}
.footer{margin-top:40px;padding-top:16px;border-top:1px solid #e0e0e0;text-align:center;color:#999;font-size:11px}
@media(max-width:768px){.charts-grid{grid-template-columns:1fr}.kpi-grid{grid-template-columns:1fr 1fr}}
@media print{body{background:white}.container{padding:10px}}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>Uncertainty-Aware Risk Register</h1>
    <div class="subtitle">
      Project: <strong>${projectFileName}</strong> &nbsp;|&nbsp;
      BIM Quality Index (BQI) + Risk Screening &nbsp;|&nbsp;
      Generated: ${new Date().toLocaleDateString('en-GB', { day:'numeric', month:'long', year:'numeric' })}
    </div>
  </div>

  ${totalScored === 0 ? `
  <div class="alert-box">
    <strong>⚠ Placeholder data:</strong> Risk screening nodes R1–R5 and BQI node C5 are not yet fully implemented.
    The report structure is correct — scores will populate once those nodes are built.
  </div>` : ''}

  <!-- KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi-card blue">
      <div class="kpi-value">${modelBQI}</div>
      <div class="kpi-label">Model BQI Score</div>
      <div class="kpi-sub" style="color:${confColor(modelConf)};font-weight:600">${modelConf.toUpperCase()} confidence</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-value">${highRisk}</div>
      <div class="kpi-label">High-Risk Elements</div>
      <div class="kpi-sub">require immediate attention</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-value">${medRisk}</div>
      <div class="kpi-label">Medium-Risk Elements</div>
      <div class="kpi-sub">monitor closely</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-value">${totalScored}</div>
      <div class="kpi-label">Elements Scored</div>
      <div class="kpi-sub">avg SRCC: ${avgSRCC}</div>
    </div>
  </div>

  <!-- Charts row -->
  <div class="charts-grid">
    <div class="chart-box">
      <h3>Risk distribution</h3>
      <canvas id="riskDist" height="200"></canvas>
    </div>
    <div class="chart-box">
      <h3>BQI weight breakdown</h3>
      <canvas id="bqiWeights" height="200"></canvas>
    </div>
    <div class="chart-box">
      <h3>QTO pipeline agreement (SRCC)</h3>
      <canvas id="srccBar" height="200"></canvas>
    </div>
    <div class="chart-box wide">
      <h3>Top 10 risk elements — risk score vs BQI score</h3>
      <canvas id="riskBqiScatter" height="120"></canvas>
    </div>
  </div>

  <!-- Risk Register Table -->
  <div class="section">
    <div class="section-header">
      <h2>Risk Register — Top 10 Screened Elements</h2>
      <p>Ranked by risk score (Likelihood × Consequence), adjusted by BQI confidence bounds</p>
    </div>
    <div class="section-body" style="padding:0;overflow-x:auto">
      <table>
        <thead>
          <tr>
            <th>#</th><th>GlobalId</th><th>IFC Type</th><th>Zone</th>
            <th>BQI Score</th><th>Confidence</th>
            <th>Likelihood</th><th>Consequence</th><th>Risk Score</th><th>Level</th>
          </tr>
        </thead>
        <tbody>${riskRows}</tbody>
      </table>
    </div>
  </div>

  <!-- BQI Summary + Pipeline comparison -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px">

    <div class="section">
      <div class="section-header">
        <h2>BQI Scoring Weights</h2>
        <p>Dimensions and their contribution to the final BQI score</p>
      </div>
      <div class="section-body" style="padding:0">
        <table>
          <thead><tr><th>Dimension</th><th>Weight</th><th>Contribution</th></tr></thead>
          <tbody>${weightRows}</tbody>
        </table>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>Pipeline A vs B — QTO Comparison</h2>
        <p>Spearman SRCC per quantity field (1.0 = perfect agreement)</p>
      </div>
      <div class="section-body" style="padding:0">
        <table>
          <thead><tr><th>QTO Field</th><th>SRCC</th><th>Agreement</th></tr></thead>
          <tbody>
            ${srccResults.length
              ? srccResults.slice(0,8).map(r => {
                  const srcc = +(r.SRCC||0).toFixed(3);
                  const label = srcc >= 0.8 ? 'Strong' : srcc >= 0.5 ? 'Moderate' : 'Weak';
                  const col   = srcc >= 0.8 ? '#009a44' : srcc >= 0.5 ? '#ffa726' : '#dc3545';
                  return `<tr><td style="font-size:11px;font-family:monospace">${(r.QtoField||'').replace('[Qto_','').replace(']',' ').slice(0,28)}</td><td>${srcc}</td><td><span style="color:${col};font-weight:600">${label}</span></td></tr>`;
                }).join('')
              : `<tr><td colspan="3" style="text-align:center;color:#999;padding:16px">QTO comparison pending — Block 3 not yet run</td></tr>`
            }
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <!-- Footer -->
  <div class="footer">
    <p><strong>Uncertainty-Aware Risk Screening from Imperfect BIM</strong> &nbsp;|&nbsp; EMJM NORISK Thesis &nbsp;|&nbsp; ${new Date().toLocaleString()}</p>
    <p style="margin-top:6px">Pipeline A: DDC Converter &nbsp;|&nbsp; Pipeline B: IfcOpenShell &nbsp;|&nbsp; Orchestrated via n8n v2.7.5</p>
  </div>

</div>
<script>
const distData    = ${distData};
const bqiWeights  = ${bqiWeights};
const srccData    = ${srccChartData};
const top10Data   = ${top10Data};

Chart.defaults.font.family = 'Arial,sans-serif';
Chart.defaults.font.size = 11;

// Risk distribution doughnut
new Chart(document.getElementById('riskDist'), {
  type: 'doughnut',
  data: {
    labels: ['High', 'Medium', 'Low'],
    datasets: [{ data: distData, backgroundColor: ['#dc3545','#ffa726','#66bb6a'], borderColor:'#fff', borderWidth:2 }]
  },
  options: { responsive:true, maintainAspectRatio:false, cutout:'55%',
    plugins:{ legend:{ position:'bottom', labels:{ usePointStyle:true, padding:10 } } } }
});

// BQI weights horizontal bar
new Chart(document.getElementById('bqiWeights'), {
  type: 'bar',
  data: {
    labels: bqiWeights.map(d => d.label),
    datasets: [{ label:'Weight %', data: bqiWeights.map(d => d.value),
      backgroundColor: ['#0061a0','#00a19a','#460073','#009a44'], borderWidth:0 }]
  },
  options: { indexAxis:'y', responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{ display:false } },
    scales:{ x:{ max:50, ticks:{ callback: v => v+'%' } }, y:{ grid:{ display:false } } } }
});

// SRCC bar
if (srccData.length) {
  new Chart(document.getElementById('srccBar'), {
    type: 'bar',
    data: {
      labels: srccData.map(d => d.field.slice(0,14)),
      datasets: [{ label:'SRCC', data: srccData.map(d => d.srcc),
        backgroundColor: srccData.map(d => d.srcc >= 0.8 ? '#009a44' : d.srcc >= 0.5 ? '#ffa726' : '#dc3545'),
        borderWidth:0 }]
    },
    options: { responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{ y:{ min:0, max:1, ticks:{ stepSize:.2 } }, x:{ grid:{ display:false },
        ticks:{ font:{ size:9 } } } } }
  });
} else {
  document.getElementById('srccBar').parentElement.innerHTML += '<p style="color:#999;font-size:12px;text-align:center;padding:20px">Run Block 3 first</p>';
}

// Risk vs BQI scatter
if (top10Data.length) {
  new Chart(document.getElementById('riskBqiScatter'), {
    type: 'scatter',
    data: {
      datasets: [
        { label:'High',   data: top10Data.filter(d=>d.label==='High').map(d=>({x:d.bqi,y:d.score,id:d.id})),   backgroundColor:'#dc3545', pointRadius:6 },
        { label:'Medium', data: top10Data.filter(d=>d.label==='Medium').map(d=>({x:d.bqi,y:d.score,id:d.id})), backgroundColor:'#ffa726', pointRadius:6 },
        { label:'Low',    data: top10Data.filter(d=>d.label==='Low').map(d=>({x:d.bqi,y:d.score,id:d.id})),    backgroundColor:'#66bb6a', pointRadius:6 }
      ]
    },
    options: { responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:'top' }, tooltip:{ callbacks:{ label: ctx => ctx.raw.id+' | BQI:'+ctx.raw.x+' Risk:'+ctx.raw.y } } },
      scales:{
        x:{ min:0, max:1, title:{ display:true, text:'BQI Score (0=poor, 1=complete)' } },
        y:{ min:0, title:{ display:true, text:'Risk Score' } }
      }
    }
  });
}
<\/script>
</body>
</html>`;

return [{
  json: {
    html: html,
    report_type: 'risk-register-bqi',
    project: projectFileName,
    timestamp: new Date().toISOString(),
    summary: {
      model_bqi: modelBQI,
      model_confidence: modelConf,
      total_elements: totalScored,
      high_risk: highRisk,
      medium_risk: medRisk,
      low_risk: lowRisk,
      avg_srcc: avgSRCC
    }
  }
}];
