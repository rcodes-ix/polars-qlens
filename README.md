# dqengine-py

A Python engine for profiling and analyzing data quality.

## Overview

`dqengine-py` is a lightweight Python package for exploring datasets and evaluating their quality through automated profiling and reporting.

It is designed to make it easier to understand the structure and quality of a dataset before using it for analysis, machine learning, or other data-driven applications.

## Features

- Dataset profiling with pandas
- Automatic data quality analysis
- Detection and analysis of missing data
- Column type analysis
- Numerical and categorical column analysis
- Overall data quality scoring
- HTML quality reports
- JSON quality reports
- Simple Python API
- Designed to be extensible as the project grows

## Installation

Install the latest release from PyPI:

```bash
pip install dqengine-py
````

## Usage

Import `dqengine` in your Python project:

```python
from dqengine import DatasetProfiler
```

Load your dataset with pandas and create a profiler:

```python
import pandas as pd
from dqengine import DatasetProfiler

data = pd.read_csv("data.csv")

profiler = DatasetProfiler(data)
profiler.profile()
```

The profiler analyzes the dataset and can be used to generate a data quality report.

## Reports

`dqengine-py` supports generating data quality reports in different formats, including:

* HTML for human-readable reports
* JSON for programmatic use

Example output files:

```text
quality_report.html
quality_report.json
```

The HTML report provides a visual overview of the dataset's quality, while the JSON report is useful when the results need to be processed by another program.

## Example

A typical workflow looks like this:

```text
CSV Dataset
    |
    v
Pandas DataFrame
    |
    v
DatasetProfiler
    |
    v
Data Quality Analysis
    |
    +------> Quality Score
    |
    +------> Column Analysis
    |
    +------> Missing Data Analysis
    |
    +------> Data Statistics
    |
    v
Quality Report
    |
    +------> HTML
    |
    +------> JSON
```

## Requirements

* Python 3.12+
* pandas

## Project Status

`dqengine-py` is currently in the early development stage.

The current `0.1.0` release focuses on establishing the core profiling and reporting functionality. Future versions will expand the analysis capabilities and improve the reporting system.

## Development

Clone the repository:

```bash
git clone https://github.com/rcodes-ix/dqengine.git
cd dqengine
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
dqengine/
├── src/
│   └── dqengine/
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

## Links

* PyPI: [https://pypi.org/project/dqengine-py/](https://pypi.org/project/dqengine-py/)
* GitHub: [https://github.com/rcodes-ix/dqengine](https://github.com/rcodes-ix/dqengine)
* Issues: [https://github.com/rcodes-ix/dqengine/issues](https://github.com/rcodes-ix/dqengine/issues)


