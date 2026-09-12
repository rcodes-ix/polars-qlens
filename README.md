# polars-qlens

A lightweight Python package for profiling and analyzing data quality with Polars.

## Overview

`polars-qlens` is a Python package for exploring datasets and evaluating their quality through automated profiling and reporting.

It is designed to make it easier to understand the structure and quality of a dataset before using it for analysis, machine learning, or other data-driven applications.

Built with Polars for fast DataFrame operations and designed to be extensible as the project grows.

## Features

* Dataset profiling with Polars
* Automatic data quality analysis
* Missing value detection and analysis
* Column type analysis
* Numerical and categorical column analysis
* Constant column detection
* Duplicate row detection
* Duplicate column detection
* Inconsistent categorical value detection
* Date column detection
* Invalid date detection
* Outlier detection using the IQR method
* Correlation analysis
* Overall data quality scoring
* HTML quality reports
* JSON quality reports
* Simple Python API
* Extensible project structure

## Installation

Install the latest release from PyPI:

```bash
pip install polars-qlens
```

## Usage

Import `DatasetProfiler` from `qlens`:

```python
from qlens import DatasetProfiler
```

Create a profiler using the path to your CSV dataset:

```python
profiler = DatasetProfiler("data.csv")
```

Load and profile the dataset:

```python
profiler.load_csv()
results = profiler.profile()
```

The profiler analyzes the dataset and returns the results as a Python dictionary.

## Reports

`polars-qlens` supports generating data quality reports in different formats:

* Terminal output for quick inspection
* HTML for human-readable reports
* JSON for programmatic use

Example:

```python
from qlens import DatasetProfiler
from qlens.report import QualityReport

profiler = DatasetProfiler("data.csv")

profiler.load_csv()
results = profiler.profile()

report = QualityReport(results)

report.generate()
report.to_json("quality_report.json")
report.to_html("quality_report.html")
```

The generated files are:

```text
quality_report.html
quality_report.json
```

The HTML report provides a visual overview of the dataset's quality, while the JSON report is useful when the results need to be processed by another program.

## Example Workflow

A typical workflow looks like this:

```text
CSV Dataset
    |
    v
DatasetProfiler
    |
    v
Polars DataFrame
    |
    v
Data Quality Analysis
    |
    +------> Missing Data Analysis
    |
    +------> Column Analysis
    |
    +------> Duplicate Detection
    |
    +------> Category Analysis
    |
    +------> Date Analysis
    |
    +------> Outlier Detection
    |
    +------> Correlation Analysis
    |
    +------> Quality Score
    |
    v
QualityReport
    |
    +------> Terminal
    |
    +------> HTML
    |
    +------> JSON
```

## Analysis

The profiler currently analyzes several aspects of dataset quality.

### Missing Values

Detects missing values in each column and calculates the percentage of missing values.

### Duplicate Rows

Detects duplicate rows in the dataset and reports the total number found.

### Constant Columns

Identifies columns containing only one unique value.

### Inconsistent Categories

Detects categorical values that differ in formatting but represent the same normalized value.

For example:

```text
Addis Ababa
addis ababa
ADDIS ABABA
```

### Duplicate Columns

Detects columns containing identical data.

### Date Analysis

Attempts to identify date columns and detects invalid date values.

### Outliers

Detects numerical outliers using the Interquartile Range (IQR) method.

### Correlations

Identifies strongly correlated numerical column pairs.

### Quality Score

Calculates an overall data quality score based on detected issues.

The score is represented on a scale from:

```text
0 - 100
```

## Requirements

* Python 3.12+
* Polars
* NumPy

Dependencies are installed automatically when `polars-qlens` is installed from PyPI.

## Project Status

`polars-qlens` is currently in the early development stage.

The current release focuses on establishing the core profiling and reporting functionality.

Future versions will expand the analysis capabilities, improve the reporting system, and introduce additional data quality checks.

## Development

Clone the repository:

```bash
git clone https://github.com/rcodes-ix/polars-qlens.git
cd qlens
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```bash
pip install -e .
```

## Project Structure

```text
data-quality-engine/
├── src/
│   └── qlens/
│       ├── __init__.py
│       ├── profiler.py
│       └── report.py
├── .github/
│   └── workflows/
│       └── release.yml
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

## License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.
