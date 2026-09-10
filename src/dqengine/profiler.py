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
            col: self.data[col].null_count()
            for col in self.col_names
        }

        self.n_unique = {
            col: self.data[col].n_unique()
            for col in self.col_names
        }

        self.describe = self.data.describe()

        # Duplicate rows

        duplicated_mask = (
            self.data
            .with_row_index("_row_index")
            .is_duplicated()
        )

        self.duplicated = duplicated_mask
        self.n_duplicated = duplicated_mask.sum()

        # Column types

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
            pl.Float64
        }

        string_types = {
            pl.String,
            pl.Utf8,
            pl.Categorical,
        }

        self.numeric_cols = [
            col
            for col, dtype in self.data.schema.items()
            if dtype in numeric_types
        ]

        self.categorical_cols = [
            col
            for col, dtype in self.data.schema.items()
            if dtype in string_types
        ]

        # Missing percetages

        if self.rows > 0:
            self.missing_pct = {
                col: (count / self.rows) * 100
                for col, count in self.missing_values.items()
            }
        else:
            self.missing_pct = {
                col: 0.0
                for col in self.col_names
            }

        # Constant columns

        self.constant_cols = [
            col
            for col, count in self.n_unique.items()
            if count == 1
        ]

        # Inconsistent categorical values

        self.inconsistent_cat = {}

        for col in self.categorical_cols:
            non_null_values = {
                self.data
                .select(
                    [
                        pl.col(col),
                        pl.col(col)
                        .cast(pl.String)
                        .str.to_lowercase()
                        .alias("_normalized")
                    ]
                )
                .drop_nulls()
            }

            groups = (
                non_null_values
                .group_by("_normalized")
                .agg(
                    pl.col(col)
                    .unique()
                    .alias("_values")
                )
            )

            inconsistencies = {}

            for row in groups.iter_rows(named=True):
                canonical_value = row["_normalized"]
                values = row["_values"]

                if len(values) > 1:
                    inconsistencies[canonical_value] = values

            if inconsistencies:
                self.inconsistent_cat[col] = inconsistencies

        # Duplicate columns

        self.duplicated_cols = []

        for i, col in enumerate(self.col_names):
            for previous_col in self.col_names[:i]:
                if self.data[col].equals(
                    self.data[previous_col]
                ):
                    self.duplicated_cols.append(col)
                    break

        # Date columns

        self.date_cols = []

        for col in self.categorical_cols:
            non_null_count = self.data[col].drop_nulls().len()

            if non_null_count == 0:
                continue

            converted = (
                self.data[col]
                .cast(pl.String)
                .str.to_datetime(
                    strict=False,
                    exact=False,
                )
            )

            valid_count = converted.drop_nulls().len()
            valid_ratio = valid_count / non_null_count

            if valid_ratio >= 0.8:
                self.date_cols.append(col)

        # Invalid dates

        self.invalid_dates = {}

        for col in self.date_cols:
            original = self.data[col]

            converted = (
                original
                .cast(pl.String)
                .str.to_datetime(
                    strict=False,
                    exact=False,
                )
            )

            invalid_count = (
                converted.is_null()
                .and_(original.is_not_null())
                .sum()
            )

            self.invalid_dates[col] = int(invalid_count)

        # Outliers

        self.outlier_cols = [
            col
            for col in self.numeric_cols
            if col != "id"
        ]

        self.outliers = {}

        for col in self.outlier_cols:
            q1 = self.data[col].quantile(
                0.25,
                interpolation="linear",
            )

            q3 = self.data[col].quantile(
                0.75,
                interpolation="linear",
            )

            if q1 is None or q3 is None:
                self.outliers[col] = {
                    "count": 0,
                    "rows": [],
                }
                continue

            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (
                self.data[col].is_not_null()
                & (
                    (self.data[col] < lower_bound)
                    | (self.data[col] > upper_bound)
                )
            )

            outlier_rows = (
                self.data
                .with_row_index("_row_index")
                .filter(outlier_mask)
                .get_column("_row_index")
                .to_list()
            )

            outlier_count = len(outlier_rows)

            self.outliers[col] = {
                "count": outlier_count,
                "rows": outlier_rows,
            }

        # Correlations

        if len(self.outlier_cols) >= 2:
            self.corr = self.data.select(
                self.outlier_cols
            ).corr()

            self.corr_pairs = []

            for i, col1 in enumerate(self.outlier_cols):
                for j, col2 in enumerate(self.outlier_cols):

                    if i < j:
                        corr = self.corr[i, j]

                        if corr is not None:
                            if abs(corr) >= 0.5:
                                self.corr_pairs.append(
                                    {
                                        "columns": (
                                            col1,
                                            col2,
                                        ),
                                        "correlation": float(
                                            corr
                                        ),
                                    }
                                )
        else:
            self.corr = None
            self.corr_pairs

        # Quality breakdown

        self.quality_breakdown = {
            "missing_values": 0,
            "duplicate_rows": 0,
            "constant_columns": 0,
            "inconsistent_categories": 0,
            "invalid_dates": 0,
            "outliers": 0,
        }

        # Missing value penality

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

        # Duplicate rows penality

        if self.rows > 0:
            duplicate_penalty = min(
                (self.n_duplicated / self.rows) * 100,
                15,
            
        else:
            duplicate_penalty = 0
    
        self.quality_breakdown["duplicate_rows"] = float(
            round(duplicate_penalty, 2)
        )

        # Constant columns

        self.quality_breakdown["constant_columns"] = 0

        # Inconsistent categories penalty
        
        inconsistent_rows = 0

        for column, groups in self.inconsistent_cat.items():

            normalized = (
                self.data[column]
                .cast(pl.String)
                .str.to_lowercase()
            )

            for canonical_value, values in groups.items():

                affected = (
                    normalized == canonical_value
                ) & (
                    self.data[column] != values[0]
                )

                inconsistent_rows += (
                    affected.fill_null(False).sum()
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

        # Invalid dates penalty

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

        # Outlier penalty

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

        # Overall quality score
        
        self.quality_score = float(
            round(
                100 - sum(
                    self.quality_breakdown.values()
                ),
                2,
            )
        )

        # Final analysis results
        
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
                for column, count in self.missing_values.items()
                if count > 0
            },

            "constant_columns": self.constant_cols,

            "inconsistent_categories": (
                self.inconsistent_cat
            ),

            "invalid_dates": {
                column: int(count)
                for column, count in self.invalid_dates.items()
            },

            "outliers": {
                column: {
                    "count": int(result["count"]),
                    "rows": result["rows"],
                }
                for column, result in self.outliers.items()
            },

            "correlations": self.corr_pairs,

            "quality_breakdown": (
                self.quality_breakdown
            ),
        }

        return self.analysis_results
        
        