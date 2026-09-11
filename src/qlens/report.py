import json


class QualityReport:
    def __init__(self, analysis_results):
        self.results = analysis_results

    def generate(self):
        summary = self.results["summary"]

        print("\n")
        print("DATA QUALITY REPORT")
        print("-" * 40)

        print(f"Rows:                 {summary['rows']}")
        print(f"Columns:              {summary['columns']}")
        print(f"Duplicate rows:       {summary['duplicate_rows']}")
        print(f"Quality score:        {summary['quality_score']} / 100")

        print("\nPotential Issues:")

        self._print_missing_values()
        self._print_duplicates()
        self._print_constant_columns()
        self._print_inconsistent_categories()
        self._print_invalid_dates()
        self._print_outliers()
        self._print_correlations()

        self._print_quality_breakdown()
        self._print_quality_score()

    def to_json(self, file_path):
        with open(file_path, "w") as file:
            json.dump(
                self.results,
                file,
                indent=4
            )

    def to_html(self, file_path):
        summary = self.results["summary"]
        score = summary["quality_score"]

        if score >= 90:
            score_class = "score-excellent"
            score_label = "Excellent"
        elif score >= 75:
            score_class = "score-good"
            score_label = "Good"
        elif score >= 60:
            score_class = "score-fair"
            score_label = "Fair"
        elif score >= 40:
            score_class = "score-poor"
            score_label = "Poor"
        else:
            score_class = "score-critical"
            score_label = "Critical"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Data Quality Report</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;

            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            background:
                radial-gradient(
                    circle at 15% 0%,
                    rgba(59, 130, 246, 0.12),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 85% 10%,
                    rgba(139, 92, 246, 0.12),
                    transparent 28%
                ),
                #070b14;

            color: #e5e7eb;

            min-height: 100vh;
        }}

        .container {{
            width: min(1180px, calc(100% - 48px));
            margin: 0 auto;
            padding: 48px 0 70px;
        }}


        .header {{
            margin-bottom: 34px;
        }}

        .eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: 8px;

            margin-bottom: 12px;

            color: #60a5fa;

            font-size: 12px;
            font-weight: 700;

            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}

        .eyebrow::before {{
            content: "";

            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #6366f1;

            box-shadow:
                0 0 12px rgba(99, 102, 241, 0.9);
        }}

        h1 {{
            margin: 0;

            font-size: clamp(32px, 5vw, 46px);
            line-height: 1.05;

            letter-spacing: -0.04em;

            color: #f8fafc;
        }}

        .subtitle {{
            margin: 12px 0 0;

            max-width: 700px;

            color: #94a3b8;

            font-size: 15px;
            line-height: 1.7;
        }}


        .cards {{
            display: grid;

            grid-template-columns:
                repeat(4, minmax(0, 1fr));

            gap: 16px;

            margin-bottom: 28px;
        }}

        .card {{
            position: relative;

            overflow: hidden;

            padding: 22px;

            background:
                linear-gradient(
                    145deg,
                    rgba(20, 29, 48, 0.94),
                    rgba(11, 17, 30, 0.94)
                );

            border: 1px solid #1e293b;

            border-radius: 14px;

            box-shadow:
                0 18px 45px rgba(0, 0, 0, 0.22);

            transition:
                transform 0.2s ease,
                border-color 0.2s ease;
        }}

        .card:hover {{
            transform: translateY(-2px);

            border-color: #334155;
        }}

        .card::after {{
            content: "";

            position: absolute;

            width: 100px;
            height: 100px;

            right: -45px;
            bottom: -50px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(59, 130, 246, 0.15),
                    transparent 70%
                );
        }}

        .card h3 {{
            margin: 0 0 13px;

            color: #64748b;

            font-size: 11px;
            font-weight: 700;

            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}

        .card p {{
            margin: 0;

            color: #f8fafc;

            font-size: 30px;
            font-weight: 700;

            letter-spacing: -0.04em;
        }}

        .score-label {{
            margin-top: 7px !important;

            font-size: 13px !important;

            font-weight: 600 !important;

            letter-spacing: 0 !important;
        }}


        .score-excellent {{
            color: #34d399 !important;
        }}

        .score-good {{
            color: #60a5fa !important;
        }}

        .score-fair {{
            color: #fbbf24 !important;
        }}

        .score-poor {{
            color: #fb7185 !important;
        }}

        .score-critical {{
            color: #f43f5e !important;
        }}


        section {{
            margin-bottom: 18px;

            padding: 24px;

            background:
                rgba(12, 18, 31, 0.88);

            border: 1px solid #1e293b;

            border-radius: 14px;

            box-shadow:
                0 14px 35px rgba(0, 0, 0, 0.16);

            backdrop-filter: blur(10px);
        }}

        section h2 {{
            margin: 0;

            color: #f1f5f9;

            font-size: 17px;
            font-weight: 700;

            letter-spacing: -0.01em;
        }}

        .section-description {{
            margin: 6px 0 0;

            color: #64748b;

            font-size: 13px;
        }}


        .table-wrapper {{
            overflow-x: auto;

            margin-top: 18px;

            border:
                1px solid #1e293b;

            border-radius: 10px;
        }}

        table {{
            width: 100%;

            border-collapse: collapse;

            min-width: 520px;
        }}

        th {{
            padding: 13px 16px;

            background: #101827;

            color: #64748b;

            border-bottom: 1px solid #1e293b;

            font-size: 11px;
            font-weight: 700;

            letter-spacing: 0.08em;

            text-align: left;
            text-transform: uppercase;
        }}

        td {{
            padding: 14px 16px;

            color: #cbd5e1;

            border-bottom: 1px solid #172033;

            font-size: 14px;

            transition:
                background 0.15s ease;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        tbody tr:hover td {{
            background:
                rgba(59, 130, 246, 0.055);
        }}

        td:first-child {{
            color: #e2e8f0;

            font-weight: 500;
        }}


        .warning {{
            color: #fbbf24 !important;

            font-weight: 600;
        }}

        .danger {{
            color: #fb7185 !important;

            font-weight: 600;
        }}

        .good {{
            color: #34d399 !important;

            font-weight: 600;
        }}

        .empty {{
            padding: 24px;

            color: #64748b !important;

            font-size: 13px;

            font-style: italic;

            text-align: center;
        }}


        .badge {{
            display: inline-flex;
            align-items: center;

            padding: 5px 9px;

            border-radius: 6px;

            font-size: 12px;
            font-weight: 600;
        }}

        .badge-warning {{
            color: #fbbf24;

            background:
                rgba(245, 158, 11, 0.10);

            border:
                1px solid rgba(245, 158, 11, 0.18);
        }}

        .badge-danger {{
            color: #fb7185;

            background:
                rgba(244, 63, 94, 0.10);

            border:
                1px solid rgba(244, 63, 94, 0.18);
        }}

        .badge-good {{
            color: #34d399;

            background:
                rgba(52, 211, 153, 0.09);

            border:
                1px solid rgba(52, 211, 153, 0.16);
        }}

        .badge-blue {{
            color: #60a5fa;

            background:
                rgba(59, 130, 246, 0.10);

            border:
                1px solid rgba(59, 130, 246, 0.18);
        }}


        .breakdown {{
            display: grid;

            grid-template-columns:
                repeat(2, minmax(0, 1fr));

            gap: 10px;

            margin-top: 18px;
        }}

        .breakdown-row {{
            display: flex;

            align-items: center;
            justify-content: space-between;

            padding: 14px 16px;

            background:
                #0d1524;

            border:
                1px solid #1b2638;

            border-radius: 9px;
        }}

        .breakdown-row span:first-child {{
            color: #94a3b8;

            font-size: 13px;
        }}

        .penalty {{
            color: #fb7185;

            font-size: 13px;
            font-weight: 700;
        }}


        .score-panel {{
            position: relative;

            overflow: hidden;

            display: flex;

            align-items: center;
            justify-content: space-between;

            gap: 20px;

            margin-bottom: 18px;

            padding: 24px;

            background:
                linear-gradient(
                    135deg,
                    rgba(37, 99, 235, 0.13),
                    rgba(124, 58, 237, 0.12)
                );

            border:
                1px solid rgba(99, 102, 241, 0.25);

            border-radius: 14px;
        }}

        .score-panel::before {{
            content: "";

            position: absolute;

            width: 240px;
            height: 240px;

            right: -80px;
            top: -130px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(99, 102, 241, 0.20),
                    transparent 68%
                );
        }}

        .score-panel-content {{
            position: relative;
            z-index: 1;
        }}

        .score-panel-label {{
            margin: 0 0 7px;

            color: #94a3b8;

            font-size: 11px;
            font-weight: 700;

            letter-spacing: 0.12em;

            text-transform: uppercase;
        }}

        .score-panel-title {{
            margin: 0;

            color: #f8fafc;

            font-size: 20px;
            font-weight: 700;
        }}

        .score-value {{
            position: relative;
            z-index: 1;

            font-size: 34px;
            font-weight: 800;

            letter-spacing: -0.04em;
        }}


        .footer {{
            padding-top: 10px;

            color: #475569;

            font-size: 12px;

            text-align: center;
        }}


        @media (max-width: 900px) {{

            .cards {{
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }}

        }}

        @media (max-width: 650px) {{

            .container {{
                width: min(100% - 28px, 1180px);

                padding-top: 30px;
            }}

            .cards {{
                grid-template-columns: 1fr;
            }}

            .breakdown {{
                grid-template-columns: 1fr;
            }}

            .score-panel {{
                align-items: flex-start;

                flex-direction: column;
            }}

            section {{
                padding: 18px;
            }}

        }}

    </style>
</head>

<body>

<div class="container">

    <header class="header">

        <div class="eyebrow">
            Data Quality Engine
        </div>

        <h1>
            Data Quality Report
        </h1>

        <p class="subtitle">
            Automated profiling and quality analysis of your dataset.
            Review detected issues, statistical signals, and overall data health.
        </p>

    </header>


    <div class="score-panel">

        <div class="score-panel-content">

            <p class="score-panel-label">
                Overall Data Health
            </p>

            <p class="score-panel-title">
                {score_label} quality
            </p>

        </div>

        <div class="score-value {score_class}">
            {score} / 100
        </div>

    </div>


    <div class="cards">

        <div class="card">

            <h3>Rows</h3>

            <p>
                {summary["rows"]}
            </p>

        </div>


        <div class="card">

            <h3>Columns</h3>

            <p>
                {summary["columns"]}
            </p>

        </div>


        <div class="card">

            <h3>Duplicate Rows</h3>

            <p class="{ 'danger' if summary['duplicate_rows'] > 0 else 'good' }">
                {summary["duplicate_rows"]}
            </p>

        </div>


        <div class="card">

            <h3>Quality Score</h3>

            <p class="{score_class}">
                {score}
            </p>

            <p class="score-label {score_class}">
                {score_label}
            </p>

        </div>

    </div>


    <section>

        <h2>Missing Values</h2>

        <p class="section-description">
            Columns containing null or missing values.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Missing Values</th>
                    </tr>
                </thead>

                <tbody>
"""

        if self.results["missing_values"]:

            for column, count in self.results["missing_values"].items():

                html += f"""
                    <tr>
                        <td>{column}</td>
                        <td>
                            <span class="badge badge-warning">
                                {count}
                            </span>
                        </td>
                    </tr>
"""

        else:

            html += """
                    <tr>
                        <td colspan="2" class="empty">
                            No missing values detected.
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Duplicate Rows</h2>

        <p class="section-description">
            Rows that appear more than once in the dataset.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Issue</th>
                        <th>Count</th>
                    </tr>
                </thead>

                <tbody>
"""

        duplicate_count = summary["duplicate_rows"]

        duplicate_class = (
            "badge-warning"
            if duplicate_count > 0
            else "badge-good"
        )

        html += f"""
                    <tr>
                        <td>Duplicate rows</td>
                        <td>
                            <span class="badge {duplicate_class}">
                                {duplicate_count}
                            </span>
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Constant Columns</h2>

        <p class="section-description">
            Columns containing only one unique value.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Column</th>
                    </tr>
                </thead>

                <tbody>
"""

        constant_columns = self.results.get(
            "constant_columns",
            []
        )

        if constant_columns:

            for column in constant_columns:

                html += f"""
                    <tr>
                        <td>
                            <span class="badge badge-warning">
                                {column}
                            </span>
                        </td>
                    </tr>
"""

        else:

            html += """
                    <tr>
                        <td class="empty">
                            No constant columns detected.
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Inconsistent Categories</h2>

        <p class="section-description">
            Category values that appear to represent the same value
            with different formatting or casing.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Values</th>
                    </tr>
                </thead>

                <tbody>
"""

        inconsistent_categories = self.results[
            "inconsistent_categories"
        ]

        if inconsistent_categories:

            for column, groups in inconsistent_categories.items():

                for normalized_value, values in groups.items():

                    html += f"""
                    <tr>
                        <td>{column}</td>
                        <td>
                            <span class="badge badge-warning">
                                {values}
                            </span>
                        </td>
                    </tr>
"""

        else:

            html += """
                    <tr>
                        <td colspan="2" class="empty">
                            No inconsistent categories detected.
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>

    <section>

        <h2>Invalid Dates</h2>

        <p class="section-description">
            Date-like columns containing values that could not be parsed.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Invalid Dates</th>
                    </tr>
                </thead>

                <tbody>
"""

        invalid_dates = self.results["invalid_dates"]

        has_invalid_dates = False

        for column, count in invalid_dates.items():

            if count > 0:

                has_invalid_dates = True

                html += f"""
                    <tr>
                        <td>{column}</td>
                        <td>
                            <span class="badge badge-danger">
                                {count}
                            </span>
                        </td>
                    </tr>
"""

        if not has_invalid_dates:

            html += """
                    <tr>
                        <td colspan="2" class="empty">
                            No invalid dates detected.
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Outliers</h2>

        <p class="section-description">
            Numerical values detected outside the expected IQR range.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Outliers</th>
                    </tr>
                </thead>

                <tbody>
"""

        outliers = self.results["outliers"]

        has_outliers = False

        for column, result in outliers.items():

            if result["count"] > 0:

                has_outliers = True

                html += f"""
                    <tr>
                        <td>{column}</td>
                        <td>
                            <span class="badge badge-danger">
                                {result["count"]}
                            </span>
                        </td>
                    </tr>
"""

        if not has_outliers:

            html += """
                    <tr>
                        <td colspan="2" class="empty">
                            No outliers detected.
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>

    <section>

        <h2>Correlations</h2>

        <p class="section-description">
            Strong relationships detected between numerical columns.
        </p>

        <div class="table-wrapper">

            <table>

                <thead>
                    <tr>
                        <th>Columns</th>
                        <th>Correlation</th>
                    </tr>
                </thead>

                <tbody>
"""

        correlations = self.results.get(
            "correlations",
            []
        )

        if correlations:

            for result in correlations:

                column1, column2 = result["columns"]

                correlation = result["correlation"]

                html += f"""
                    <tr>
                        <td>
                            {column1}
                            <span style="color:#475569;"> / </span>
                            {column2}
                        </td>

                        <td>
                            <span class="badge badge-blue">
                                {correlation:.2f}
                            </span>
                        </td>
                    </tr>
"""

        else:

            html += """
                    <tr>
                        <td colspan="2" class="empty">
                            No strong correlations detected.
                        </td>
                    </tr>
"""

        html += """
                </tbody>

            </table>

        </div>

    </section>

    <section>

        <h2>Quality Breakdown</h2>

        <p class="section-description">
            Penalty applied to the overall data quality score.
        </p>

        <div class="breakdown">
"""

        quality_breakdown = self.results.get(
            "quality_breakdown",
            {}
        )

        for issue, penalty in quality_breakdown.items():

            html += f"""
            <div class="breakdown-row">

                <span>
                    {issue.replace("_", " ").title()}
                </span>

                <span class="penalty">
                    -{penalty}
                </span>

            </div>
"""

        html += """
        </div>

    </section>


    <div class="footer">
        Generated by polars-qlens
    </div>

</div>

</body>
</html>
"""

        with open(file_path, "w") as file:
            file.write(html)

    def _print_missing_values(self):
        missing = self.results["missing_values"]

        if not missing:
            print("  No missing values detected.")
            return

        for column, count in missing.items():
            print(
                f"  {column:<20} -> "
                f"{count} missing value(s)"
            )

    def _print_duplicates(self):
        count = self.results["summary"]["duplicate_rows"]

        if count > 0:
            print(
                f"  duplicate rows       -> {count}"
            )
        else:
            print("  No duplicate rows detected.")

    def _print_constant_columns(self):
        constant_columns = self.results.get(
            "constant_columns",
            []
        )

        if not constant_columns:
            print("  No constant columns detected.")
            return

        for column in constant_columns:
            print(
                f"  {column:<20} -> constant column"
            )

    def _print_inconsistent_categories(self):
        inconsistencies = self.results[
            "inconsistent_categories"
        ]

        if not inconsistencies:
            print("  No inconsistent categories detected.")
            return

        for column, groups in inconsistencies.items():
            for normalized_value, values in groups.items():
                print(
                    f"  {column:<20} -> "
                    f"inconsistent values: {values}"
                )

    def _print_invalid_dates(self):
        invalid_dates = self.results["invalid_dates"]

        found_invalid = False

        for column, count in invalid_dates.items():
            if count > 0:
                found_invalid = True

                print(
                    f"  {column:<20} -> "
                    f"{count} invalid date(s)"
                )

        if not found_invalid:
            print("  No invalid dates detected.")

    def _print_outliers(self):
        outliers = self.results["outliers"]

        found_outliers = False

        for column, result in outliers.items():
            count = result["count"]

            if count > 0:
                found_outliers = True

                print(
                    f"  {column:<20} -> "
                    f"{count} outlier(s)"
                )

        if not found_outliers:
            print("  No outliers detected.")

    def _print_correlations(self):
        correlations = self.results.get(
            "correlations",
            []
        )

        if not correlations:
            print("  No strong correlations detected.")
            return

        for result in correlations:
            column1, column2 = result["columns"]
            correlation = result["correlation"]

            print(
                f"  {column1} / {column2:<20} -> "
                f"correlation: {correlation:.2f}"
            )

    def _print_quality_breakdown(self):
        breakdown = self.results.get(
            "quality_breakdown",
            {}
        )

        print("\nQuality Breakdown:")

        for issue, penalty in breakdown.items():
            print(
                f"  {issue:<25} -> -{penalty}"
            )

    def _print_quality_score(self):
        score = self.results["summary"]["quality_score"]

        print("\nOverall Quality Score:")
        print(f"  {score} / 100")