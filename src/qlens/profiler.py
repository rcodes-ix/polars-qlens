import polars as pl


class DatasetProfiler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_csv(self):
        self.data = pl.read_csv(self.file_path)

        self.rows = self.data.height
        self.columns = self.data.width

        return self.data

    def profile(self):
        if self.data is None:
            raise ValueError(
                "Dataset has not been loaded. Call load_csv() first."
            )

        
        # Basic Information
        
        self.col_names = self.data.columns
        self.d_types = self.data.schema

        self.missing_values = {
            column: int(self.data[column].null_count())
            for column in self.col_names
        }

        self.n_unique = {
            column: int(self.data[column].n_unique())
            for column in self.col_names
        }

        self.describe = self.data.describe()

        # Duplicate Rows
        
        self.duplicated = self.data.is_duplicated()
        self.n_duplicated = int(self.duplicated.sum())

        # Column Types
        
        numeric_types = {
            pl.Int8,
            pl.Int16,
            pl.Int32,
            pl.Int64,
            pl.UInt8,
            pl.UInt16,
            pl.UInt32,
            pl.UInt64,
            pl.Float32,
            pl.Float64,
        }

        categorical_types = {
            pl.String,
            pl.Categorical,
        }

        self.numeric_cols = [
            column
            for column, dtype in self.data.schema.items()
            if dtype in numeric_types
        ]

        self.categorical_cols = [
            column
            for column, dtype in self.data.schema.items()
            if dtype in categorical_types
        ]

        # Missing Percentages
        
        if self.rows > 0:
            self.missing_pct = {
                column: (count / self.rows) * 100
                for column, count in self.missing_values.items()
            }
        else:
            self.missing_pct = {
                column: 0.0
                for column in self.col_names
            }

        # Constant Columns
        
        self.constant_cols = [
            column
            for column, count in self.n_unique.items()
            if count == 1
        ]

        # Inconsistent Categorical Values
        
        self.inconsistent_cat = {}

        for column in self.categorical_cols:

            non_null_values = (
                self.data
                .select(
                    [
                        pl.col(column),
                        pl.col(column)
                        .cast(pl.String)
                        .str.to_lowercase()
                        .alias("_normalized"),
                    ]
                )
                .drop_nulls()
            )

            groups = (
                non_null_values
                .group_by("_normalized")
                .agg(
                    pl.col(column)
                    .unique()
                    .alias("_values")
                )
            )

            inconsistencies = {}

            for row in groups.iter_rows(named=True):
                normalized_value = row["_normalized"]
                values = row["_values"]

                if len(values) > 1:
                    inconsistencies[normalized_value] = values

            if inconsistencies:
                self.inconsistent_cat[column] = inconsistencies

        # Duplicate Columns
        
        self.duplicated_cols = []

        for index, column in enumerate(self.col_names):
            for previous_column in self.col_names[:index]:

                if self.data[column].equals(
                    self.data[previous_column]
                ):
                    self.duplicated_cols.append(column)
                    break

 
        # Date Columns
        
        self.date_cols = []
        
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]
        
        for column in self.categorical_cols:
        
            non_null_count = (
                self.data[column]
                .drop_nulls()
                .len()
            )
        
            if non_null_count == 0:
                continue
        
            string_column = self.data[column].cast(pl.String)
        
            parsed = None
        
            for date_format in date_formats:
        
                converted = string_column.str.to_datetime(
                    format=date_format,
                    strict=False,
                )
        
                if parsed is None:
                    parsed = converted
                else:
                    parsed = parsed.fill_null(converted)
        
            valid_count = parsed.drop_nulls().len()
        
            valid_ratio = valid_count / non_null_count
        
            if valid_ratio >= 0.8:
                self.date_cols.append(column)
        
        
        # Invalid Dates
        
        self.invalid_dates = {}
        
        for column in self.date_cols:
        
            original = self.data[column].cast(pl.String)
        
            parsed = None
        
            for date_format in date_formats:
        
                converted = original.str.to_datetime(
                    format=date_format,
                    strict=False,
                )
        
                if parsed is None:
                    parsed = converted
                else:
                    parsed = parsed.fill_null(converted)
        
            invalid_count = (
                parsed.is_null()
                .and_(original.is_not_null())
                .sum()
            )
        
            self.invalid_dates[column] = int(invalid_count)

        
        # Outliers
        
        self.outlier_cols = [
            column
            for column in self.numeric_cols
            if column != "id"
        ]

        self.outliers = {}

        for column in self.outlier_cols:

            q1 = self.data[column].quantile(
                0.25,
                interpolation="linear",
            )

            q3 = self.data[column].quantile(
                0.75,
                interpolation="linear",
            )

            if q1 is None or q3 is None:
                self.outliers[column] = {
                    "count": 0,
                    "rows": [],
                }
                continue

            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (
                self.data[column].is_not_null()
                & (
                    (self.data[column] < lower_bound)
                    | (self.data[column] > upper_bound)
                )
            )

            outlier_rows = (
                self.data
                .with_row_index("_row_index")
                .filter(outlier_mask)
                .get_column("_row_index")
                .to_list()
            )

            self.outliers[column] = {
                "count": len(outlier_rows),
                "rows": outlier_rows,
            }

        
        # Correlations

        self.corr_pairs = []

        if len(self.outlier_cols) >= 2:

            self.corr = (
                self.data
                .select(self.outlier_cols)
                .corr()
            )

            for i, column1 in enumerate(self.outlier_cols):

                for j, column2 in enumerate(self.outlier_cols):

                    if i < j:

                        correlation = self.corr[i, j]

                        if correlation is None:
                            continue

                        if abs(correlation) >= 0.5:
                            self.corr_pairs.append(
                                {
                                    "columns": (
                                        column1,
                                        column2,
                                    ),
                                    "correlation": float(
                                        correlation
                                    ),
                                }
                            )

        else:
            self.corr = None

        
        # Quality Breakdown
        
        self.quality_breakdown = {
            "missing_values": 0,
            "duplicate_rows": 0,
            "constant_columns": 0,
            "inconsistent_categories": 0,
            "invalid_dates": 0,
            "outliers": 0,
        }

        
        # Missing Values Penalty
        
        total_cells = self.rows * self.columns

        missing_count = sum(
            self.missing_values.values()
        )

        if total_cells > 0:
            missing_penalty = min(
                (missing_count / total_cells) * 100,
                20,
            )
        else:
            missing_penalty = 0

        self.quality_breakdown["missing_values"] = float(
            round(missing_penalty, 2)
        )

        
        # Duplicate Rows Penalty
        
        if self.rows > 0:
            duplicate_penalty = min(
                (self.n_duplicated / self.rows) * 100,
                15,
            )
        else:
            duplicate_penalty = 0

        self.quality_breakdown["duplicate_rows"] = float(
            round(duplicate_penalty, 2)
        )

        
        # Constant Columns Penalty
        
        if self.columns > 0:
            constant_penalty = min(
                (len(self.constant_cols) / self.columns) * 100,
                10,
            )
        else:
            constant_penalty = 0

        self.quality_breakdown["constant_columns"] = float(
            round(constant_penalty, 2)
        )

        
        # Inconsistent Categories Penalty
        
        inconsistent_rows = 0

        for column, groups in self.inconsistent_cat.items():

            normalized = (
                self.data[column]
                .cast(pl.String)
                .str.to_lowercase()
            )

            for normalized_value, values in groups.items():

                affected = (
                    (normalized == normalized_value)
                    & (
                        self.data[column]
                        != values[0]
                    )
                )

                inconsistent_rows += int(
                    affected
                    .fill_null(False)
                    .sum()
                )

        if self.rows > 0:
            inconsistent_penalty = min(
                (inconsistent_rows / self.rows) * 100,
                15,
            )
        else:
            inconsistent_penalty = 0

        self.quality_breakdown[
            "inconsistent_categories"
        ] = float(
            round(inconsistent_penalty, 2)
        )

        
        # Invalid Dates Penalty
        
        invalid_date_count = sum(
            self.invalid_dates.values()
        )

        if self.rows > 0:
            invalid_date_penalty = min(
                (invalid_date_count / self.rows) * 100,
                15,
            )
        else:
            invalid_date_penalty = 0

        self.quality_breakdown["invalid_dates"] = float(
            round(invalid_date_penalty, 2)
        )

        
        # Outlier Penalty
        
        outlier_count = sum(
            result["count"]
            for result in self.outliers.values()
        )

        if self.rows > 0:
            outlier_penalty = min(
                (outlier_count / self.rows) * 100,
                15,
            )
        else:
            outlier_penalty = 0

        self.quality_breakdown["outliers"] = float(
            round(outlier_penalty, 2)
        )

        # Overall Quality Score

        self.quality_score = float(
            round(
                100
                - sum(
                    self.quality_breakdown.values()
                ),
                2,
            )
        )

        
        # Final Analysis Results

        self.analysis_results = {
            "summary": {
                "rows": self.rows,
                "columns": self.columns,
                "duplicate_rows": int(
                    self.n_duplicated
                ),
                "quality_score": self.quality_score,
            },

            "missing_values": {
                column: int(count)
                for column, count
                in self.missing_values.items()
                if count > 0
            },

            "constant_columns": self.constant_cols,

            "inconsistent_categories": (
                self.inconsistent_cat
            ),

            "invalid_dates": {
                column: int(count)
                for column, count
                in self.invalid_dates.items()
            },

            "outliers": {
                column: {
                    "count": int(result["count"]),
                    "rows": result["rows"],
                }
                for column, result
                in self.outliers.items()
            },

            "correlations": self.corr_pairs,

            "quality_breakdown": (
                self.quality_breakdown
            ),
        }

        return self.analysis_results