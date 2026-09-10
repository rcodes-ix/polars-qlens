import json


class QualityReport:
    def __init__(self, analysis_results):
        self.results = analysis_results

    def generate(self):
        summary = self.results['summary']

        print('\n')
        print("DATA QUALITY REPORT")
        print("-" * 40)

        print(f"Rows:                 {summary['rows']}")
        print(f"Columns:              {summary['columns']}")

        print("\nPotential Issues:")

        self._print_missing_values()
        self._print_duplicates()
        self._print_inconsistent_categories()
        self._print_invalid_dates()
        self._print_outliers()

        self._print_quality_score()

    def to_json(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(
                self.results,
                file,
                indent=4
            )

    def to_html(self, file_path):
        summary = self.results['summary']

        score = summary['quality_score']

        if score >= 90:
            score_class = 'score-excellent'
            score_label = "Excellent"
        elif score >+ 75:
            score_class = 'score-good'
            score_label = "Good"
        elif score >= 60:
            score_class = 'score-fair'
            score_label = "Fair"
        elif score >= 40:
            score_class = 'score-poor'
            score_label = "Poor"
        else:
            score_class = 'score-critical'
            score_label = "Critical"
    
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
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
                    max-width: 1000px;
                    margin: auto;
                }}
    
                h1 {{
                    margin-bottom: 30px;
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
    
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                    font-size: 20px;
                }}
    
                th {{
                    background: #f3f4f6;
                }}
    
                .warning {{
                    color: #d97706;
                    font-weight: bold;
                    font-size: 18px;
                }}
    
                .danger {{
                    color: #dc2626;
                    font-weight: bold;
                }}
    
                .good {{
                    color: #16a34a;
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
                    <p>{summary['rows']}</p>
                </div>
    
                <div class="card">
                    <h3>Columns</h3>
                    <p>{summary['columns']}</p>
                </div>
    
                <div class="card">
                    <h3>Quality Score</h3>
                    <p class="{score_class}">
                        {summary['quality_score']} / 100
                    </p>

                    <p class="{score_class}">
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
    
        for column, count in self.results['missing_values'].items():
            html += f"""
                    <tr>
                        <td>{column}</td>
                        <td class="warning">{count}</td>
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
    
        duplicate_count = summary['duplicate_rows']
    
        html += f"""
                    <tr>
                        <td>Duplicate rows</td>
                        <td class="warning">{duplicate_count}</td>
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
    
        for column, groups in self.results['inconsistent_categories'].items():
            for normalized_value, values in groups.items():
                html += f"""
                    <tr>
                        <td>{column}</td>
                        <td class="warning">{values}</td>
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
    
        for column, count in self.results['invalid_dates'].items():
    
            if count > 0:
                html += f"""
                    <tr>
                        <td>{column}</td>
                        <td class="danger">{count}</td>
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
    
        for column, result in self.results['outliers'].items():
    
            if result['count'] > 0:
                html += f"""
                    <tr>
                        <td>{column}</td>
                        <td class="danger">{result['count']}</td>
                    </tr>
                """
    
        html += """
                </table>
    
            </section>
    
        </div>
    
        </body>
        </html>
        """
    
        with open(file_path, 'w') as file:
            file.write(html)

    def _print_missing_values(self):
        missing = self.results['missing_values']
    
        for column, count in missing.items():
            print(
                f"  ⚠ {column:<20} → {count} missing value(s)"
            )

    def _print_duplicates(self):
        count = self.results['summary']['duplicate_rows']
    
        if count > 0:
            print(
                f"  ⚠ duplicate rows       → {count}"
            )

    def _print_inconsistent_categories(self):
        inconsistencies = self.results['inconsistent_categories']
    
        for column, groups in inconsistencies.items():
            for normalized_value, values in groups.items():
                print(
                    f"  ⚠ {column:<20} → inconsistent values: "
                    f"{values}"
                )

    def _print_invalid_dates(self):
        invalid_dates = self.results['invalid_dates']
    
        for column, count in invalid_dates.items():
            if count > 0:
                print(
                    f"  ⚠ {column:<20} → {count} invalid date(s)"
                )

    def _print_outliers(self):
        outliers = self.results['outliers']
    
        for column, result in outliers.items():
            count = result['count']
    
            if count > 0:
                print(
                    f"  ⚠ {column:<20} → "
                    f"{count} outlier(s)"
                )

    def _print_quality_score(self):
        score = self.results['summary']['quality_score']
    
        print("\nOverall Quality Score:")
        print(f"  {score} / 100")

    