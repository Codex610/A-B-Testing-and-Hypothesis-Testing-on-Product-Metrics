# A/B Testing and Hypothesis Testing on Product Metrics

> A complete end-to-end A/B Testing Statistics Project with a **FastAPI backend**, **Vanilla JS frontend**, and **downloadable PDF report**.

---

## Project Overview

This project simulates a real-world A/B testing workflow:

- Generates a **synthetic dataset** of 20,000 users split into Control and Variant groups
- Runs **Two-Proportion Z-test** (conversion rate) and **Independent T-tests** (time spent, clicks)
- Computes **95% Confidence Intervals** for all metric differences
- Performs **Power Analysis** with minimum sample size calculations
- Generates **business insights** and a final **Rollout Recommendation**
- Produces **5 visualizations** (bar chart, distributions, boxplots)
- Creates a **professional PDF report** you can download

---

## Folder Structure

```
ab_testing_project/
├── backend/
│   ├── main.py                        # FastAPI app
│   ├── requirements.txt
│   ├── ab_testing/
│   │   ├── __init__.py
│   │   ├── data_generator.py          # Synthetic data
│   │   ├── hypothesis_tests.py        # Z-test + T-test
│   │   ├── confidence_intervals.py    # 95% CIs
│   │   ├── power_analysis.py          # Cohen's d, power
│   │   ├── business_insights.py       # Metrics + recommendation
│   │   ├── visualization.py           # 5 matplotlib plots
│   │   └── report_generator.py        # JSON + TXT + PDF
│   ├── datasets/
│   │   └── ab_test_data.csv           # Generated dataset
│   └── outputs/
│       ├── plots/                     # PNG visualizations
│       ├── report.json
│       ├── report.txt
│       └── report.pdf
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

---

## How to Run

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

### 2. Frontend

Open `frontend/index.html` directly in a browser, or use VS Code Live Server.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`                | Health check |
| POST   | `/generate-data`   | Generate 20k user CSV dataset |
| POST   | `/run-analysis`    | Run full A/B testing pipeline |
| GET    | `/report`          | Get report.json content |
| GET    | `/download-report` | Download PDF report |
| GET    | `/plots`           | List plot filenames |
| GET    | `/plots/{name}`    | Serve a plot image |

---

## Usage Workflow

1. Click **Generate Dataset** → creates `datasets/ab_test_data.csv`
2. Click **Run Analysis** → runs all statistical tests, plots, and reports
3. View results in the dashboard: metrics, p-values, confidence intervals, recommendation
4. Click **View Report JSON** to inspect raw JSON
5. Click **Download PDF Report** to save the full professional PDF

---

## Statistical Methods Explained

### Two-Proportion Z-Test
Tests whether two proportions (conversion rates) are significantly different.  
**H₀**: p_control = p_variant  
**H₁**: p_control ≠ p_variant  
Uses `statsmodels.stats.proportion.proportions_ztest`.

### Independent T-Test (Welch's)
Tests whether the means of two independent groups differ significantly.  
Used for continuous metrics: `time_spent` and `clicks`.  
Welch's variant does not assume equal variances.

### Confidence Intervals
The 95% CI for the difference tells us the range within which the true difference lies with 95% confidence. If the CI excludes 0, the difference is statistically significant.

### Power Analysis
Determines the minimum sample size needed to detect a true effect given:
- **Alpha (α)** = 0.05 (Type I error rate)
- **Power (1-β)** = 0.80 (probability of detecting a real effect)
- **Effect size**: Cohen's d (continuous) or Cohen's h (proportions)

### Cohen's d
Effect size for continuous metrics:  
`d = |mean₁ - mean₂| / pooled_std`  
- Small: 0.2, Medium: 0.5, Large: 0.8

---

## Example API Response (truncated)

```json
{
  "metrics_summary": {
    "control": { "conversion_rate": 0.12, "avg_time_spent": 7.52 },
    "variant": { "conversion_rate": 0.148, "avg_time_spent": 8.91 }
  },
  "hypothesis_tests": {
    "conversion_rate": {
      "test_type": "Two-Proportion Z-Test",
      "p_value": 0.000023,
      "significant": true
    }
  },
  "business_insights": {
    "recommendation": "ROLLOUT",
    "rationale": "Multiple metrics show statistically significant improvement..."
  }
}
```

---

## Downloading the PDF Report

After running analysis, click **Download PDF Report** in the dashboard  
or navigate to: `http://127.0.0.1:8000/download-report`

The PDF contains: title page, dataset summary, metrics table, hypothesis test results, confidence intervals, power analysis, all 5 charts, business insights, and highlighted final recommendation.
