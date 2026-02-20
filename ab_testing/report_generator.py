"""
report_generator.py
Generates JSON, TXT, and PDF reports from A/B test analysis results.
"""
import json
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT_DIR = Path("outputs")
PLOTS_DIR = OUTPUT_DIR / "plots"


def save_json_report(report_data: dict) -> str:
    """Save analysis results as JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "report.json"
    with open(path, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    return str(path)


def save_txt_report(report_data: dict) -> str:
    """Save a human-readable text summary."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "report.txt"

    metrics = report_data.get("metrics_summary", {})
    tests = report_data.get("hypothesis_tests", {})
    cis = report_data.get("confidence_intervals", {})
    power = report_data.get("power_analysis", {})
    insights = report_data.get("business_insights", {})

    lines = [
        "=" * 70,
        "       A/B TESTING ANALYSIS REPORT",
        f"       Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "── DATASET SUMMARY ──────────────────────────────────────────────────",
        f"  Total Users     : {report_data.get('dataset_info', {}).get('total_rows', 'N/A')}",
        f"  Control Users   : {metrics.get('control', {}).get('n_users', 'N/A')}",
        f"  Variant Users   : {metrics.get('variant', {}).get('n_users', 'N/A')}",
        "",
        "── METRICS SUMMARY ──────────────────────────────────────────────────",
        f"  {'Metric':<25} {'Control':>12} {'Variant':>12} {'Difference':>12}",
        f"  {'-'*62}",
        f"  {'Conversion Rate':<25} {metrics.get('control',{}).get('conversion_rate',0)*100:>11.2f}% "
        f"{metrics.get('variant',{}).get('conversion_rate',0)*100:>11.2f}% "
        f"{metrics.get('differences',{}).get('conversion_rate_diff',0)*100:>11.2f}%",
        f"  {'Avg Time Spent (min)':<25} {metrics.get('control',{}).get('avg_time_spent',0):>12.4f} "
        f"{metrics.get('variant',{}).get('avg_time_spent',0):>12.4f} "
        f"{metrics.get('differences',{}).get('time_spent_diff',0):>12.4f}",
        f"  {'Avg Clicks':<25} {metrics.get('control',{}).get('avg_clicks',0):>12.4f} "
        f"{metrics.get('variant',{}).get('avg_clicks',0):>12.4f} "
        f"{metrics.get('differences',{}).get('clicks_diff',0):>12.4f}",
        "",
        "── HYPOTHESIS TEST RESULTS ──────────────────────────────────────────",
    ]

    for key, result in tests.items():
        sig = "SIGNIFICANT" if result.get("significant") else "NOT SIGNIFICANT"
        lines += [
            f"  Metric   : {key}",
            f"  Test     : {result.get('test_type')}",
            f"  Statistic: {result.get('statistic')}",
            f"  P-value  : {result.get('p_value')}",
            f"  Result   : {sig} (alpha={result.get('alpha')})",
            f"  Notes    : {result.get('interpretation')}",
            "",
        ]

    lines += [
        "── CONFIDENCE INTERVALS (95%) ────────────────────────────────────────",
    ]
    for key, ci in cis.items():
        lines.append(
            f"  {key}: [{ci.get('lower')}, {ci.get('upper')}]  "
            f"Point estimate: {ci.get('point_estimate')}"
        )

    lines += [
        "",
        "── POWER ANALYSIS ───────────────────────────────────────────────────",
        f"  Conversion Rate Uplift: {power.get('conversion_uplift_pct')}%",
        f"  Actual sample per group: {power.get('actual_sample_size_per_group')}",
        f"  Required (conversion): {power.get('conversion_rate', {}).get('required_sample_size_per_group')}",
        f"  Required (time_spent): {power.get('time_spent', {}).get('required_sample_size_per_group')}",
        f"  Required (clicks):     {power.get('clicks', {}).get('required_sample_size_per_group')}",
        "",
        "── BUSINESS INSIGHTS ────────────────────────────────────────────────",
    ]
    for insight in insights.get("insights", []):
        lines.append(f"  • {insight}")

    lines += [
        "",
        "── FINAL RECOMMENDATION ─────────────────────────────────────────────",
        f"  >>> {insights.get('recommendation')} <<<",
        f"  {insights.get('rationale')}",
        "",
        "=" * 70,
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines))
    return str(path)


def save_pdf_report(report_data: dict) -> str:
    """Generate a professional PDF report using ReportLab."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "report.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=26, spaceAfter=6, textColor=colors.HexColor("#1A2B4A"),
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=12, textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER, spaceAfter=20,
    )
    h1_style = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=14, textColor=colors.HexColor("#1A2B4A"),
        spaceBefore=16, spaceAfter=6,
        borderPad=4,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=12, textColor=colors.HexColor("#2C5F8A"),
        spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, leading=15, spaceAfter=6, alignment=TA_JUSTIFY,
    )
    rec_green = ParagraphStyle(
        "RecGreen", parent=styles["Normal"],
        fontSize=14, fontName="Helvetica-Bold",
        textColor=colors.white, alignment=TA_CENTER,
    )
    rec_red = ParagraphStyle(
        "RecRed", parent=styles["Normal"],
        fontSize=14, fontName="Helvetica-Bold",
        textColor=colors.white, alignment=TA_CENTER,
    )

    # Helper: table with header row
    def make_table(header: list, rows: list, col_widths=None) -> Table:
        data = [header] + rows
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A2B4A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3FA")]),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    story = []

    # ── TITLE PAGE ────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("A/B Testing Report", title_style))
    story.append(Paragraph("Product Metrics Analysis — Statistical Results & Business Recommendations", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1A2B4A")))
    story.append(Spacer(1, 0.3 * inch))

    # ── DATASET SUMMARY ────────────────────────────────────────────────────
    info = report_data.get("dataset_info", {})
    metrics = report_data.get("metrics_summary", {})
    story.append(Paragraph("1. Dataset Summary", h1_style))
    ds_rows = [
        ["Total Users", str(info.get("total_rows", "N/A"))],
        ["Columns", str(info.get("total_columns", "N/A"))],
        ["Control Users", str(metrics.get("control", {}).get("n_users", "N/A"))],
        ["Variant Users", str(metrics.get("variant", {}).get("n_users", "N/A"))],
        ["Date Range", str(info.get("date_range", "N/A"))],
    ]
    story.append(make_table(["Attribute", "Value"], ds_rows, col_widths=[3 * inch, 4 * inch]))
    story.append(Spacer(1, 0.2 * inch))

    # ── METRICS SUMMARY ────────────────────────────────────────────────────
    story.append(Paragraph("2. Metrics Summary", h1_style))
    ctrl = metrics.get("control", {})
    vrnt = metrics.get("variant", {})
    diff = metrics.get("differences", {})
    m_rows = [
        ["Conversion Rate",
         f"{ctrl.get('conversion_rate', 0)*100:.2f}%",
         f"{vrnt.get('conversion_rate', 0)*100:.2f}%",
         f"{diff.get('conversion_rate_diff', 0)*100:+.2f}%"],
        ["Avg Time Spent (min)",
         f"{ctrl.get('avg_time_spent', 0):.4f}",
         f"{vrnt.get('avg_time_spent', 0):.4f}",
         f"{diff.get('time_spent_diff', 0):+.4f}"],
        ["Avg Clicks",
         f"{ctrl.get('avg_clicks', 0):.4f}",
         f"{vrnt.get('avg_clicks', 0):.4f}",
         f"{diff.get('clicks_diff', 0):+.4f}"],
        ["Avg Session Count",
         f"{ctrl.get('avg_session_count', 0):.4f}",
         f"{vrnt.get('avg_session_count', 0):.4f}",
         "—"],
        ["Total Conversions",
         str(ctrl.get("total_conversions", "N/A")),
         str(vrnt.get("total_conversions", "N/A")),
         "—"],
    ]
    story.append(make_table(
        ["Metric", "Control", "Variant", "Difference"],
        m_rows,
        col_widths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch],
    ))
    story.append(Spacer(1, 0.2 * inch))

    # ── HYPOTHESIS TESTS ───────────────────────────────────────────────────
    story.append(Paragraph("3. Hypothesis Testing Results", h1_style))
    tests = report_data.get("hypothesis_tests", {})
    for metric_key, result in tests.items():
        sig_text = "YES - Significant" if result.get("significant") else "NO - Not Significant"
        sig_color = colors.HexColor("#27AE60") if result.get("significant") else colors.HexColor("#E74C3C")
        t_rows = [
            ["Test Type", result.get("test_type", "")],
            ["Test Statistic", str(result.get("statistic", ""))],
            ["P-Value", str(result.get("p_value", ""))],
            ["Alpha", str(result.get("alpha", 0.05))],
            ["Significant?", sig_text],
        ]
        story.append(Paragraph(f"{metric_key.replace('_', ' ').title()}", h2_style))
        tbl = make_table(["Parameter", "Value"], t_rows, col_widths=[3 * inch, 4 * inch])
        # Color the significance row
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (1, 5), (1, 5), sig_color),
            ("TEXTCOLOR", (1, 5), (1, 5), colors.white),
            ("FONTNAME", (1, 5), (1, 5), "Helvetica-Bold"),
        ]))
        story.append(tbl)
        story.append(Paragraph(result.get("interpretation", ""), body_style))
        story.append(Spacer(1, 0.1 * inch))

    # ── CONFIDENCE INTERVALS ────────────────────────────────────────────
    story.append(Paragraph("4. Confidence Intervals (95%)", h1_style))
    cis = report_data.get("confidence_intervals", {})
    ci_rows = []
    for key, ci in cis.items():
        ci_rows.append([
            key.replace("_", " ").title(),
            str(ci.get("point_estimate")),
            f"[{ci.get('lower')}, {ci.get('upper')}]",
            f"{int(ci.get('confidence_level', 0.95)*100)}%",
        ])
    story.append(make_table(
        ["Metric", "Point Estimate", "95% CI", "Confidence Level"],
        ci_rows,
        col_widths=[2.5 * inch, 1.5 * inch, 2.5 * inch, 1.5 * inch],
    ))
    story.append(Spacer(1, 0.2 * inch))

    # ── POWER ANALYSIS ─────────────────────────────────────────────────
    story.append(Paragraph("5. Power Analysis & Effect Sizes", h1_style))
    power = report_data.get("power_analysis", {})
    pa_rows = [
        ["Conversion Rate Uplift",
         f"{power.get('conversion_uplift_pct', 0):.2f}%",
         str(power.get('conversion_rate', {}).get('effect_size_h', 'N/A')),
         str(power.get('conversion_rate', {}).get('required_sample_size_per_group', 'N/A'))],
        ["Time Spent",
         "—",
         str(power.get('time_spent', {}).get('cohens_d', 'N/A')),
         str(power.get('time_spent', {}).get('required_sample_size_per_group', 'N/A'))],
        ["Clicks",
         "—",
         str(power.get('clicks', {}).get('cohens_d', 'N/A')),
         str(power.get('clicks', {}).get('required_sample_size_per_group', 'N/A'))],
    ]
    story.append(make_table(
        ["Metric", "Uplift / Effect", "Effect Size", "Required N per Group"],
        pa_rows,
        col_widths=[2 * inch, 1.5 * inch, 1.5 * inch, 2 * inch],
    ))
    story.append(Paragraph(
        f"Actual sample size per group: {power.get('actual_sample_size_per_group', 'N/A')}",
        body_style,
    ))
    story.append(Spacer(1, 0.2 * inch))

    # ── PLOTS ──────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("6. Visualizations", h1_style))

    plot_files = [
        ("conversion_rate_bar.png", "Conversion Rate Comparison"),
        ("time_spent_distribution.png", "Time Spent Distribution"),
        ("clicks_distribution.png", "Clicks Distribution"),
        ("boxplots.png", "Boxplot Comparison"),
        ("metrics_comparison.png", "Metrics Comparison"),
    ]

    for fname, caption in plot_files:
        fpath = PLOTS_DIR / fname
        if fpath.exists():
            story.append(Paragraph(caption, h2_style))
            img = RLImage(str(fpath), width=6.5 * inch, height=3.5 * inch)
            story.append(img)
            story.append(Spacer(1, 0.15 * inch))

    # ── BUSINESS INSIGHTS ──────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("7. Business Insights", h1_style))
    insights = report_data.get("business_insights", {})
    for insight in insights.get("insights", []):
        story.append(Paragraph(f"• {insight}", body_style))
    story.append(Spacer(1, 0.2 * inch))

    # ── FINAL RECOMMENDATION ───────────────────────────────────────────────
    story.append(Paragraph("8. Final Recommendation", h1_style))
    rec = insights.get("recommendation", "MONITOR")
    if rec == "ROLLOUT":
        rec_color = colors.HexColor("#27AE60")
    elif rec == "DO NOT ROLLOUT":
        rec_color = colors.HexColor("#E74C3C")
    else:
        rec_color = colors.HexColor("#F39C12")

    rec_table = Table(
        [[Paragraph(f"RECOMMENDATION: {rec}", rec_green if rec == "ROLLOUT" else rec_red)]],
        colWidths=[6.5 * inch],
    )
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rec_color),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [5]),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(insights.get("rationale", ""), body_style))

    doc.build(story)
    return str(path)


def generate_all_reports(report_data: dict) -> dict:
    """Generate JSON, TXT, and PDF reports."""
    json_path = save_json_report(report_data)
    txt_path = save_txt_report(report_data)
    pdf_path = save_pdf_report(report_data)
    return {"json": json_path, "txt": txt_path, "pdf": pdf_path}
