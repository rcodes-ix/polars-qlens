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
<html>
<head>
    <meta charset="UTF-8">
    <title>Data Quality Report</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #1f2937;
            margin: 0;
            padding: 40px;
        }}

        .container {{
            max-width: 1100px;
            margin: auto;
        }}

        h1 {{
            margin-bottom: 30px;
        }}

        h2 {{
            margin-top: 0;
        }}

        .cards {{
            display: flex;
            gap: 20px;
            margin-bottom: 35px;
        }}

        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            flex: 1;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #6b7280;
        }}

        .card p {{
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }}

        .score-label {{
            margin-top: 10px !important;
            font-size: 18px !important;
        }}

        .score-excellent {{
            color: #16a34a;
        }}

        .score-good {{
            color: #16a34a;
        }}

        .score-fair {{
            color: #d97706;
        }}

        .score-poor {{
            color: #dc2626;
        }}

        .score-critical {{
            color: #991b1b;
        }}

        section {{
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th,
        td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
            font-size: 16px;
        }}

        th {{
            background: #f3f4f6;
        }}

        .warning {{
            color: #d97706;
            font-weight: bold;
        }}

        .danger {{
            color: #dc2626;
            font-weight: bold;
        }}

        .good {{
            color: #16a34a;
            font-weight: bold;
        }}

        .empty {{
            color: #6b7280;
            font-style: italic;
        }}

        .breakdown {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .breakdown-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: #f9fafb;
            border-radius: 6px;
        }}

        .penalty {{
            color: #dc2626;
            font-weight: bold;
        }}
    </style>
</head>

<body>

<div class="container">

    <h1>Data Quality Report</h1>

    <div class="cards">

        <div class="card">
            <h3>Rows</h3>
            <p>{summary["rows"]}</p>
        </div>

        <div class="card">
            <h3>Columns</h3>
            <p>{summary["columns"]}</p>
        </div>

        <div class="card">
            <h3>Duplicate Rows</h3>
            <p>{summary["duplicate_rows"]}</p>
        </div>

        <div class="card">
            <h3>Quality Score</h3>
            <p class="{score_class}">
                {score} / 100
            </p>
            <p class="score-label {score_class}">
                {score_label}
            </p>
        </div>

    </div>

    <section>

        <h2>Missing Values</h2>

        <table>
            <tr>
                <th>Column</th>
                <th>Missing Values</th>
            </tr>
"""

        if self.results["missing_values"]:
            for column, count in self.results["missing_values"].items():
                html += f"""
            <tr>
                <td>{column}</td>
                <td class="warning">{count}</td>
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
        </table>

    </section>

    <section>

        <h2>Duplicate Rows</h2>

        <table>
            <tr>
                <th>Issue</th>
                <th>Count</th>
            </tr>
"""

        duplicate_count = summary["duplicate_rows"]

        html += f"""
            <tr>
                <td>Duplicate rows</td>
                <td class="{"warning" if duplicate_count > 0 else "good"}">
                    {duplicate_count}
                </td>
            </tr>
"""

        html += """
        </table>

    </section>

    <section>

        <h2>Constant Columns</h2>

        <table>
            <tr>
                <th>Column</th>
            </tr>
"""

        constant_columns = self.results.get(
            "constant_columns",
            []
        )

        if constant_columns:
            for column in constant_columns:
                html += f"""
            <tr>
                <td class="warning">{column}</td>
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
        </table>

    </section>

    <section>

        <h2>Inconsistent Categories</h2>

        <table>
            <tr>
                <th>Column</th>
                <th>Values</th>
            </tr>
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
                <td class="warning">{values}</td>
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
        </table>

    </section>

    <section>

        <h2>Invalid Dates</h2>

        <table>
            <tr>
                <th>Column</th>
                <th>Invalid Dates</th>
            </tr>
"""

        invalid_dates = self.results["invalid_dates"]

        has_invalid_dates = False

        for column, count in invalid_dates.items():
            if count > 0:
                has_invalid_dates = True

                html += f"""
            <tr>
                <td>{column}</td>
                <td class="danger">{count}</td>
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
        </table>

    </section>

    <section>

        <h2>Outliers</h2>

        <table>
            <tr>
                <th>Column</th>
                <th>Outliers</th>
            </tr>
"""

        outliers = self.results["outliers"]

        has_outliers = False

        for column, result in outliers.items():
            if result["count"] > 0:
                has_outliers = True

                html += f"""
            <tr>
                <td>{column}</td>
                <td class="danger">{result["count"]}</td>
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
        </table>

    </section>

    <section>

        <h2>Correlations</h2>

        <table>
            <tr>
                <th>Columns</th>
                <th>Correlation</th>
            </tr>
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
                <td>{column1} / {column2}</td>
                <td class="warning">
                    {correlation:.2f}
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
        </table>

    </section>

    <section>

        <h2>Quality Breakdown</h2>

        <div class="breakdown">
"""

        quality_breakdown = self.results.get(
            "quality_breakdown",
            {}
        )

        for issue, penalty in quality_breakdown.items():
            html += f"""
            <div class="breakdown-row">
                <span>{issue.replace("_", " ").title()}</span>
                <span class="penalty">-{penalty}</span>
            </div>
"""

        html += """
        </div>

    </section>

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
                f"  ⚠ {column:<20} → "
                f"{count} missing value(s)"
            )

    def _print_duplicates(self):
        count = self.results["summary"]["duplicate_rows"]

        if count > 0:
            print(
                f"  ⚠ duplicate rows       → {count}"
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
                f"  ⚠ {column:<20} → constant column"
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
                    f"  ⚠ {column:<20} → "
                    f"inconsistent values: {values}"
                )

    def _print_invalid_dates(self):
        invalid_dates = self.results["invalid_dates"]

        found_invalid = False

        for column, count in invalid_dates.items():
            if count > 0:
                found_invalid = True

                print(
                    f"  ⚠ {column:<20} → "
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
                    f"  ⚠ {column:<20} → "
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
                f"  ⚠ {column1} / {column2:<20} → "
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
                f"  {issue:<25} → -{penalty}"
            )

    def _print_quality_score(self):
        score = self.results["summary"]["quality_score"]

        print("\nOverall Quality Score:")
        print(f"  {score} / 100")