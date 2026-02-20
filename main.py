"""
main.py
FastAPI backend for the A/B Testing Dashboard.
"""
import json
import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Module imports
from ab_testing.data_generator import generate_ab_test_data, save_dataset
from ab_testing.hypothesis_tests import run_all_tests
from ab_testing.confidence_intervals import compute_all_cis
from ab_testing.power_analysis import run_power_analysis
from ab_testing.business_insights import compute_metrics_summary, generate_business_insights
from ab_testing.visualization import generate_all_plots
from ab_testing.report_generator import generate_all_reports

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent
DATASET_PATH = BASE_DIR / "datasets" / "ab_test_data.csv"
OUTPUT_DIR   = BASE_DIR / "outputs"
PLOTS_DIR    = OUTPUT_DIR / "plots"
REPORT_JSON  = OUTPUT_DIR / "report.json"
REPORT_PDF   = OUTPUT_DIR / "report.pdf"

# Ensure output directories exist on startup
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "datasets").mkdir(parents=True, exist_ok=True)

# ── App Setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="A/B Testing API",
    description="End-to-end A/B Testing and Hypothesis Testing API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 1. Health Check ────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "A/B Testing API is running"}


# ── 2. Generate Dataset ────────────────────────────────────────────────────
@app.post("/generate-data", tags=["Data"])
def generate_data():
    """
    Generate a synthetic A/B test dataset with 20,000 users and save to CSV.
    """
    try:
        df = generate_ab_test_data(n_users=20000)
        save_dataset(df, str(DATASET_PATH))
        return {
            "status": "success",
            "message": "Dataset generated successfully",
            "rows": len(df),
            "columns": list(df.columns),
            "path": str(DATASET_PATH),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")


# ── 3. Run Full Analysis ───────────────────────────────────────────────────
@app.post("/run-analysis", tags=["Analysis"])
def run_analysis():
    """
    Run the complete A/B testing pipeline:
    - Load dataset
    - Compute metrics
    - Hypothesis tests (Z-test, T-test)
    - Confidence intervals
    - Power analysis
    - Generate plots
    - Generate reports (JSON, TXT, PDF)
    Returns full results as JSON.
    """
    if not DATASET_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset not found. Please call POST /generate-data first.",
        )

    try:
        # Change working directory to backend so relative paths work
        os.chdir(BASE_DIR)

        df = pd.read_csv(DATASET_PATH)

        # Dataset info
        dataset_info = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "date_range": f"{df['date'].min()} to {df['date'].max()}",
        }

        # Core analyses
        metrics = compute_metrics_summary(df)
        tests = run_all_tests(df, alpha=0.05)
        cis = compute_all_cis(df, confidence=0.95)
        power = run_power_analysis(df, alpha=0.05)
        insights = generate_business_insights(metrics, tests, power)

        # Plots
        plot_files = generate_all_plots(df)

        # Assemble full report data
        report_data = {
            "generated_at": str(pd.Timestamp.now()),
            "dataset_info": dataset_info,
            "metrics_summary": metrics,
            "hypothesis_tests": tests,
            "confidence_intervals": cis,
            "power_analysis": power,
            "business_insights": insights,
            "plots_generated": plot_files,
        }

        # Save reports
        report_paths = generate_all_reports(report_data)
        report_data["report_paths"] = report_paths

        return JSONResponse(content=report_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── 4. Get Report JSON ─────────────────────────────────────────────────────
@app.get("/report", tags=["Reports"])
def get_report():
    """Return the saved report.json content."""
    if not REPORT_JSON.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please run POST /run-analysis first.",
        )
    with open(REPORT_JSON) as f:
        data = json.load(f)
    return JSONResponse(content=data)


# ── 5. Download PDF Report ─────────────────────────────────────────────────
@app.get("/download-report", tags=["Reports"])
def download_report():
    """Download the PDF report as a file attachment."""
    if not REPORT_PDF.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF report not found. Please run POST /run-analysis first.",
        )
    return FileResponse(
        path=str(REPORT_PDF),
        media_type="application/pdf",
        filename="ab_testing_report.pdf",
        headers={"Content-Disposition": "attachment; filename=ab_testing_report.pdf"},
    )


# ── 6. Get Plots List ──────────────────────────────────────────────────────
@app.get("/plots", tags=["Plots"])
def list_plots():
    """Return a list of generated plot filenames."""
    if not PLOTS_DIR.exists():
        return {"plots": []}
    files = [f.name for f in PLOTS_DIR.iterdir() if f.suffix == ".png"]
    return {"plots": sorted(files)}


# ── 7. Serve Plot Image ────────────────────────────────────────────────────
@app.get("/plots/{plot_name}", tags=["Plots"])
def get_plot(plot_name: str):
    """Serve a specific plot image by filename."""
    plot_path = PLOTS_DIR / plot_name
    if not plot_path.exists():
        raise HTTPException(status_code=404, detail=f"Plot '{plot_name}' not found.")
    return FileResponse(path=str(plot_path), media_type="image/png")
