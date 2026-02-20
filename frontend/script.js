/**
 * script.js
 * A/B Testing Dashboard — Vanilla JavaScript frontend
 */

const API_BASE = "http://127.0.0.1:8000";

// ── DOM Refs ──────────────────────────────────────────────────────────────
const btnGenerate    = document.getElementById("btnGenerate");
const btnAnalyze     = document.getElementById("btnAnalyze");
const btnViewReport  = document.getElementById("btnViewReport");
const btnDownloadPDF = document.getElementById("btnDownloadPDF");
const statusBar      = document.getElementById("statusBar");
const statusText     = document.getElementById("statusText");
const alertBox       = document.getElementById("alertBox");
const jsonModal      = document.getElementById("jsonModal");
const modalBackdrop  = document.getElementById("modalBackdrop");
const modalClose     = document.getElementById("modalClose");
const jsonContent    = document.getElementById("jsonContent");

// ── Sections ──────────────────────────────────────────────────────────────
const datasetSection       = document.getElementById("datasetSection");
const metricsSection       = document.getElementById("metricsSection");
const testsSection         = document.getElementById("testsSection");
const ciSection            = document.getElementById("ciSection");
const powerSection         = document.getElementById("powerSection");
const recommendationSection= document.getElementById("recommendationSection");
const plotsSection         = document.getElementById("plotsSection");

// ── Utilities ─────────────────────────────────────────────────────────────
function showStatus(msg) {
  statusText.textContent = msg;
  statusBar.classList.remove("hidden");
}
function hideStatus() { statusBar.classList.add("hidden"); }

function showAlert(msg, type = "success") {
  alertBox.textContent = msg;
  alertBox.className = `alert alert-${type}`;
  alertBox.classList.remove("hidden");
  setTimeout(() => alertBox.classList.add("hidden"), 5000);
}

function setButtonsDisabled(disabled) {
  [btnGenerate, btnAnalyze, btnViewReport, btnDownloadPDF].forEach(b => b.disabled = disabled);
}

function fmt(val, decimals = 4) {
  if (val === undefined || val === null) return "N/A";
  return Number(val).toFixed(decimals);
}

function pctFmt(val) { return (Number(val) * 100).toFixed(2) + "%"; }

// ── 1. Generate Dataset ───────────────────────────────────────────────────
btnGenerate.addEventListener("click", async () => {
  setButtonsDisabled(true);
  showStatus("Generating 20,000-user synthetic dataset…");
  try {
    const res = await fetch(`${API_BASE}/generate-data`, { method: "POST" });
    if (!res.ok) throw new Error((await res.json()).detail || "Failed");
    const data = await res.json();

    // Show dataset info
    renderDatasetInfo({
      total_rows: data.rows,
      total_columns: data.columns.length,
      columns: data.columns,
      date_range: "Last 30 days",
    });

    showAlert(`✅ Dataset generated: ${data.rows.toLocaleString()} rows, ${data.columns.length} columns`);
  } catch (err) {
    showAlert(`❌ ${err.message}`, "error");
  } finally {
    hideStatus();
    setButtonsDisabled(false);
  }
});

// ── 2. Run Analysis ───────────────────────────────────────────────────────
btnAnalyze.addEventListener("click", async () => {
  setButtonsDisabled(true);
  showStatus("Running full A/B testing pipeline — this may take 15–30 seconds…");
  try {
    const res = await fetch(`${API_BASE}/run-analysis`, { method: "POST" });
    if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
    const data = await res.json();

    renderDatasetInfo(data.dataset_info);
    renderMetrics(data.metrics_summary);
    renderTests(data.hypothesis_tests);
    renderCIs(data.confidence_intervals);
    renderPower(data.power_analysis);
    renderRecommendation(data.business_insights);
    await renderPlots();

    showAlert("✅ Analysis complete! Scroll down to view results.");
  } catch (err) {
    showAlert(`❌ ${err.message}`, "error");
  } finally {
    hideStatus();
    setButtonsDisabled(false);
  }
});

// ── 3. View Report JSON ───────────────────────────────────────────────────
btnViewReport.addEventListener("click", async () => {
  setButtonsDisabled(true);
  showStatus("Loading report JSON…");
  try {
    const res = await fetch(`${API_BASE}/report`);
    if (!res.ok) throw new Error((await res.json()).detail || "Report not found");
    const data = await res.json();
    jsonContent.textContent = JSON.stringify(data, null, 2);
    jsonModal.classList.remove("hidden");
  } catch (err) {
    showAlert(`❌ ${err.message}`, "error");
  } finally {
    hideStatus();
    setButtonsDisabled(false);
  }
});

// ── 4. Download PDF ───────────────────────────────────────────────────────
btnDownloadPDF.addEventListener("click", () => {
  window.location.href = `${API_BASE}/download-report`;
});

// ── Modal Close ────────────────────────────────────────────────────────────
modalClose.addEventListener("click",   () => jsonModal.classList.add("hidden"));
modalBackdrop.addEventListener("click", () => jsonModal.classList.add("hidden"));

// ── Render: Dataset Info ──────────────────────────────────────────────────
function renderDatasetInfo(info) {
  const items = [
    { label: "Total Users",   value: Number(info.total_rows || 0).toLocaleString() },
    { label: "Columns",       value: info.total_columns || (info.columns || []).length },
    { label: "Date Range",    value: info.date_range || "—" },
    { label: "Groups",        value: "Control / Variant" },
  ];
  document.getElementById("datasetInfo").innerHTML = items.map(i =>
    `<div class="info-item">
       <div class="label">${i.label}</div>
       <div class="value">${i.value}</div>
     </div>`
  ).join("");
  datasetSection.classList.remove("hidden");
}

// ── Render: Metrics ───────────────────────────────────────────────────────
function renderMetrics(summary) {
  if (!summary) return;
  const ctrl = summary.control || {};
  const vrnt = summary.variant || {};
  const diff = summary.differences || {};

  const cards = [
    {
      title: "Conversion Rate",
      control: pctFmt(ctrl.conversion_rate || 0),
      variant: pctFmt(vrnt.conversion_rate || 0),
      diffVal: diff.conversion_rate_diff || 0,
      diffFmt: v => (v * 100 >= 0 ? "+" : "") + (v * 100).toFixed(2) + "%",
    },
    {
      title: "Avg Time Spent (min)",
      control: fmt(ctrl.avg_time_spent, 2) + " min",
      variant: fmt(vrnt.avg_time_spent, 2) + " min",
      diffVal: diff.time_spent_diff || 0,
      diffFmt: v => (v >= 0 ? "+" : "") + v.toFixed(4),
    },
    {
      title: "Avg Clicks",
      control: fmt(ctrl.avg_clicks, 4),
      variant: fmt(vrnt.avg_clicks, 4),
      diffVal: diff.clicks_diff || 0,
      diffFmt: v => (v >= 0 ? "+" : "") + v.toFixed(4),
    },
  ];

  document.getElementById("metricsGrid").innerHTML = cards.map(c => {
    const diffClass = c.diffVal > 0 ? "diff-positive" : c.diffVal < 0 ? "diff-negative" : "diff-neutral";
    const diffArrow = c.diffVal > 0 ? "▲" : c.diffVal < 0 ? "▼" : "—";
    return `
      <div class="metric-card">
        <h3>${c.title}</h3>
        <div class="metric-row">
          <span class="metric-label"><span class="group-tag tag-control">Control</span></span>
          <span class="metric-value">${c.control}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label"><span class="group-tag tag-variant">Variant</span></span>
          <span class="metric-value">${c.variant}</span>
        </div>
        <div class="metric-diff ${diffClass}">${diffArrow} Difference: ${c.diffFmt(c.diffVal)}</div>
      </div>`;
  }).join("");

  metricsSection.classList.remove("hidden");
}

// ── Render: Hypothesis Tests ──────────────────────────────────────────────
function renderTests(tests) {
  if (!tests) return;
  const labels = { conversion_rate: "Conversion Rate (Z-Test)", time_spent: "Time Spent (T-Test)", clicks: "Clicks (T-Test)" };
  document.getElementById("testsGrid").innerHTML = Object.entries(tests).map(([key, t]) => {
    const sigClass = t.significant ? "sig" : "insig";
    const sigText  = t.significant ? "Significant" : "Not Significant";
    return `
      <div class="test-item ${sigClass}">
        <div class="test-header">
          <h4>${labels[key] || key}</h4>
          <span class="sig-badge ${t.significant ? 'yes' : 'no'}">${sigText}</span>
        </div>
        <div class="test-stats">
          <span>Test: <strong>${t.test_type}</strong></span>
          <span>Statistic: <strong>${t.statistic}</strong></span>
          <span>P-Value: <strong>${t.p_value}</strong></span>
          <span>Alpha: <strong>${t.alpha}</strong></span>
        </div>
        <p class="test-interp">${t.interpretation}</p>
      </div>`;
  }).join("");
  testsSection.classList.remove("hidden");
}

// ── Render: Confidence Intervals ──────────────────────────────────────────
function renderCIs(cis) {
  if (!cis) return;
  const labels = { conversion_rate: "Conversion Rate Diff", time_spent: "Time Spent Diff", clicks: "Clicks Diff" };
  document.getElementById("ciGrid").innerHTML = Object.entries(cis).map(([key, ci]) => `
    <div class="ci-card">
      <h4>${labels[key] || key}</h4>
      <div class="ci-range">[${ci.lower} , ${ci.upper}]</div>
      <div class="ci-point">Point estimate: <strong>${ci.point_estimate}</strong> &nbsp;|&nbsp; ${(ci.confidence_level * 100).toFixed(0)}% CI</div>
    </div>`
  ).join("");
  ciSection.classList.remove("hidden");
}

// ── Render: Power Analysis ────────────────────────────────────────────────
function renderPower(power) {
  if (!power) return;
  const sections = [
    { title: "Conversion Rate", data: power.conversion_rate, effect: power.conversion_rate?.effect_size_h, effectLabel: "Effect Size h" },
    { title: "Time Spent",      data: power.time_spent,      effect: power.time_spent?.cohens_d,           effectLabel: "Cohen's d" },
    { title: "Clicks",          data: power.clicks,          effect: power.clicks?.cohens_d,               effectLabel: "Cohen's d" },
  ];
  const extra = `
    <div class="power-card" style="grid-column: span 1;">
      <h4>Summary</h4>
      <div class="power-stat"><span class="k">Conversion Uplift</span><span class="v">${power.conversion_uplift_pct}%</span></div>
      <div class="power-stat"><span class="k">Actual N/Group</span><span class="v">${Number(power.actual_sample_size_per_group).toLocaleString()}</span></div>
    </div>`;

  document.getElementById("powerGrid").innerHTML = sections.map(s => `
    <div class="power-card">
      <h4>${s.title}</h4>
      <div class="power-stat"><span class="k">${s.effectLabel}</span><span class="v">${s.effect ?? "N/A"}</span></div>
      <div class="power-stat"><span class="k">Required N/Group</span><span class="v">${s.data?.required_sample_size_per_group ?? "N/A"}</span></div>
      <div class="power-stat"><span class="k">Power</span><span class="v">${((s.data?.power || 0.8) * 100).toFixed(0)}%</span></div>
    </div>`
  ).join("") + extra;

  powerSection.classList.remove("hidden");
}

// ── Render: Recommendation ────────────────────────────────────────────────
function renderRecommendation(insights) {
  if (!insights) return;
  const rec = insights.recommendation || "MONITOR";
  const cls = rec === "ROLLOUT" ? "rec-rollout" : rec.includes("NOT") ? "rec-no-rollout" : "rec-monitor";
  const emoji = rec === "ROLLOUT" ? "🚀" : rec.includes("NOT") ? "🚫" : "👀";
  document.getElementById("recommendationCard").className = `recommendation-card ${cls}`;
  document.getElementById("recommendationCard").innerHTML = `
    <div class="rec-label">Final Recommendation</div>
    <div class="rec-verdict">${emoji} ${rec}</div>
    <div class="rec-rationale">${insights.rationale}</div>
  `;
  recommendationSection.classList.remove("hidden");
}

// ── Render: Plots ─────────────────────────────────────────────────────────
async function renderPlots() {
  try {
    const res = await fetch(`${API_BASE}/plots`);
    if (!res.ok) return;
    const data = await res.json();
    const names = data.plots || [];

    const captions = {
      "conversion_rate_bar.png":     "Conversion Rate Comparison",
      "time_spent_distribution.png": "Time Spent Distribution",
      "clicks_distribution.png":     "Clicks Distribution",
      "boxplots.png":                "Boxplot Comparison",
      "metrics_comparison.png":      "Metrics Overview",
    };

    document.getElementById("plotsGrid").innerHTML = names.map(name => `
      <div class="plot-card">
        <div class="plot-caption">${captions[name] || name}</div>
        <img src="${API_BASE}/plots/${name}" alt="${name}" loading="lazy" />
      </div>`
    ).join("");

    plotsSection.classList.remove("hidden");
  } catch (_) { /* silently skip */ }
}
