import pandas as pd

class DatasetProfiler:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_csv(self):
        self.data = pd.read_csv(self.file_path)
        self.rows, self.columns = self.data.shape
        
        return self.data

    def profile(self):
        self.column_names = self.data.columns
        self.data_types = self.data.dtypes
        self.missing_values = self.data.isna().sum()
        self.nunique = self.data.nunique()
        self.describe = self.data.describe()
        self.duplicated = self.data.duplicated()
        self.nduplicated = self.duplicated.sum()
        self.numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        self.categorical_cols = self.data.select_dtypes(include=['category', 'object', 'string']).columns.tolist()
        self.missing_pct = (self.missing_values / self.rows) * 100
        self.constant_cols = self.nunique[self.nunique == 1].index.tolist()

        self.inconsistent_cat = {}
        
        for column in self.categorical_cols:
            normalized = self.data[column].astype('string').str.lower()
            grouped = (self.data[column].groupby(normalized).unique())

            inconsistencies = {
                value: values.tolist()
                for value, values in grouped.items()
                if len(values) > 1
            }
            if inconsistencies:
                self.inconsistent_cat[column] = inconsistencies

        self.duplicated_columns = self.data.T.duplicated()
        self.duplicated_columns = self.duplicated_columns[
            self.duplicated_columns
        ].index.tolist()

        self.date_cols = []

        for column in self.data.select_dtypes(
            include=['object', 'string', 'category']
        ).columns:
            converted = pd.to_datetime(self.data[column], errors='coerce')
            valid_ratio = converted.notna().sum() / self.data[column].notna().sum()

            if valid_ratio >= 0.8:
                self.date_cols.append(column)

        self.invalid_dates = {}

        for column in self.date_cols:
            converted = pd.to_datetime(self.data[column], errors='coerce')
            invalid_count = converted.isna().sum()

            self.invalid_dates[column] = invalid_count

        self.outlier_cols = [column for column in self.numeric_cols if column != 'id']

        self.outliers = {}
            
        for column in self.outlier_cols:
            q1 = self.data[column].quantile(0.25)
            q3 = self.data[column].quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = ((self.data[column] < lower_bound) | 
                (self.data[column] > upper_bound))
            
            self.outliers[column] = {
                'count': outliers.sum(),
                'rows': self.data.index[outliers].tolist()
            }

        self.corr = self.data[self.outlier_cols].corr()

        self.corr_pairs = []

        for i, cols1 in enumerate(self.corr.columns):
            for j, cols2 in enumerate(self.corr.columns):
                if i < j:
                    corr = self.corr.iloc[i, j]

                    if abs(corr) >= 0.5:
                        self.corr_pairs.append({
                            'columns': (cols1, cols2),
                            'correlation': corr
                        })

        self.quality_breakdown = {
            'missing_values': 0,
            'duplicate_rows': 0,
            'constant_columns': 0,
            'inconsistent_categories': 0,
            'invalid_dates': 0,
            'outliers': 0
        }
        
        # Missing values
        total_cells = self.rows * self.columns
        missing_count = self.missing_values.sum()
        
        missing_penalty = min(
            (missing_count / total_cells) * 100,
            20
        )
        self.quality_breakdown['missing_values'] = float(round(
            missing_penalty, 2
        ))
        
        # Duplicate rows
        duplicate_penalty = min(
            (self.nduplicated / self.rows) * 100,
            15
        )
        self.quality_breakdown['duplicate_rows'] = float(round(
            duplicate_penalty, 2
        ))
        
        # Constant columns
        self.quality_breakdown['constant_columns'] = 0
        
        # Inconsistent categories
        inconsistent_rows = 0
        
        for column, groups in self.inconsistent_cat.items():
            normalized = self.data[column].str.lower()
        
            for canonical_value, values in groups.items():
                affected = (
                    normalized == canonical_value
                ) & (
                    self.data[column] != values[0]
                )
        
                inconsistent_rows += affected.sum()
        
        inconsistent_penalty = min(
            (inconsistent_rows / self.rows) * 100,
            15
        )
        
        self.quality_breakdown['inconsistent_categories'] = float(round(
            inconsistent_penalty, 2
        ))
        
        # Invalid dates
        invalid_date_count = sum(
            self.invalid_dates.values()
        )
        
        invalid_date_penalty = min(
            (invalid_date_count / self.rows) * 100,
            15
        )
        self.quality_breakdown['invalid_dates'] = float(round(
            invalid_date_penalty, 2
        ))
        
        # Outliers
        outlier_count = sum(
            result['count']
            for result in self.outliers.values()
        )
        
        outlier_penalty = min(
            (outlier_count / self.rows) * 100,
            15
        )
        self.quality_breakdown['outliers'] = float(round(
            outlier_penalty, 2
        ))
        
        self.quality_score = float(round(
            100 - sum(self.quality_breakdown.values()),
            2
        ))


        self.analysis_results = {
            'summary': {
                'rows': self.rows,
                'columns': self.columns,
                'duplicate_rows': int(self.nduplicated),
                'quality_score': self.quality_score
            },
            'missing_values': {
                column: int(count)
                for column, count, in self.missing_values.items()
                if count > 0
            },

            'constant_columns': self.constant_cols,
            'inconsistent_categories': self.inconsistent_cat,
            'invalid_dates': {
                column: int(count)
                for column, count in self.invalid_dates.items()
            },
            
            'outliers': {
                column: {
                    'count': int(result['count']),
                    'rows': result['rows']
                }
                for column, result in self.outliers.items()
            },
            'correlations': self.corr_pairs,
            'quality_breakdown': self.quality_breakdown
            
        }