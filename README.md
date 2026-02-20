# A/B Testing and Hypothesis Testing on Product Metrics

> Complete end-to-end A/B Testing Statistics Project — FastAPI backend, Vanilla JS frontend, downloadable PDF report. **All files in a single base folder.**

---

## Folder Structure

```
A-B-Testing-and-Hypothesis-Testing-on-Product-Metrics/          ← single base folder (everything here)
├── main.py                  # FastAPI app — run from this folder
├── requirements.txt
├── README.md
├── .gitignore
├── ab_testing/              # Core analysis modules
│   ├── __init__.py
│   ├── data_generator.py
│   ├── hypothesis_tests.py
│   ├── confidence_intervals.py
│   ├── power_analysis.py
│   ├── business_insights.py
│   ├── visualization.py
│   └── report_generator.py
├── datasets/
│   └── ab_test_data.csv
├── outputs/
│   ├── plots/
│   ├── report.json
│   ├── report.txt
│   └── report.pdf
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

---

## How to Run

```bash
cd A-B-Testing-and-Hypothesis-Testing-on-Product-Metrics
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `frontend/index.html` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/generate-data` | Generate 20k-user CSV dataset |
| POST | `/run-analysis` | Run full A/B testing pipeline |
| GET | `/report` | Get report.json |
| GET | `/download-report` | Download PDF report |
| GET | `/plots` | List plot filenames |
| GET | `/plots/{name}` | Serve plot image |

---

## Statistical Methods

- **Two-Proportion Z-Test** — conversion rate comparison
- **Welch's Independent T-Test** — time spent & clicks comparison
- **95% Confidence Intervals** — for all metric differences
- **Cohen's d / Cohen's h** — effect sizes
- **Power Analysis** — minimum sample size at α=0.05, power=0.80

---

## Workflow

1. Click **Generate Dataset** → creates `datasets/ab_test_data.csv`
2. Click **Run Analysis** → runs all stats, plots, reports
3. View results in dashboard
4. Click **Download PDF Report**
