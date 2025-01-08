import os
import pandas as pd
import glob
from datetime import datetime
import numpy as np
import re


class DataProfiler:
    def __init__(self):
        """Initialize the DataProfiler"""
        try:
            self.report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.output_dir = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Reports/RAW DQ"

            # Initialize currency validation patterns and indicators
            self.currency_patterns = {
                "USD": r"^\$?\d{1,3}(,\d{3})*(\.\d{2})?$",  # US Dollar format
                "EUR": r"^€?\d{1,3}(,\d{3})*(\.\d{2})?$",  # Euro format
                "GBP": r"^£?\d{1,3}(,\d{3})*(\.\d{2})?$",  # British Pound format
                "INR": r"^₹?\d{1,3}(,\d{3})*(\.\d{2})?$",  # Indian Rupee format
            }

            # Initialize currency indicators list
            self.currency_indicators = [
                "price",
                "amount",
                "cost",
                "fee",
                "charge",
                "payment",
                "salary",
                "wage",
                "income",
                "expense",
                "revenue",
                "$",
                "£",
                "€",
                "₹",
                "usd",
                "eur",
                "gbp",
                "inr",
            ]

            # Create output directory if it doesn't exist
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

        except Exception as e:
            print(f"Error in initialization: {str(e)}")
            self.currency_indicators = []  # Fallback empty list
            self.currency_patterns = {}  # Fallback empty dict
            raise Exception(f"Error initializing DataProfiler: {str(e)}")

    def set_metadata(self, metadata_df):
        """Set metadata after initialization"""
        try:
            # Print original column names for debugging
            print("\nOriginal metadata columns:", metadata_df.columns.tolist())

            # Clean up metadata column names
            metadata_df.columns = metadata_df.columns.str.strip().str.replace(
                "\s+", " ", regex=True
            )

            # Print cleaned column names for debugging
            print("Cleaned metadata columns:", metadata_df.columns.tolist())

            # Clean up the metadata values
            for col in ["Is Mandatory", "Is Unique", "Sensitive", "Encrypted"]:
                if col in metadata_df.columns:
                    # Clean and standardize values
                    metadata_df[col] = (
                        metadata_df[col]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .str.replace("\s+", " ", regex=True)
                    )

                    # Map variations of "Yes" to standardized form
                    yes_variations = ["YES", "Y", "TRUE", "1"]
                    metadata_df[col] = metadata_df[col].apply(
                        lambda x: "YES" if x.upper() in yes_variations else "NO"
                    )

            # Clean up Column Name values
            metadata_df["Column Name"] = (
                metadata_df["Column Name"]
                .astype(str)
                .str.strip()
                .str.replace("\s+", " ", regex=True)
            )

            self.metadata_df = metadata_df

            # Debug print to verify the cleaning
            print("\nUnique values after cleaning:")
            for col in ["Is Mandatory", "Is Unique", "Sensitive", "Encrypted"]:
                if col in metadata_df.columns:
                    print(f"{col}: {metadata_df[col].unique().tolist()}")

        except Exception as e:
            raise Exception(f"Error setting metadata: {str(e)}")

    def is_analyzable_numeric(self, column_name, df):
        """
        Determine if a column should be included in numerical analysis
        """
        # Convert column name to lowercase for easier checking
        col_lower = column_name.lower()

        # Business-specific ID patterns
        business_id_patterns = [
            "customer_id",
            "product_id",
            "order_id",
            "transaction_id",
            "account_id",
            "user_id",
            "employee_id",
            "vendor_id",
            "invoice_id",
            "payment_id",
            "shipment_id",
            "tracking_id",
        ]

        # Check business-specific ID patterns
        for pattern in business_id_patterns:
            if pattern in col_lower:
                return False

        # Technical patterns to exclude
        technical_patterns = [
            "id",
            "code",
            "number",
            "num",
            "identifier",
            "reference",
            "zip",
            "postal",
            "year",
            "month",
            "day",
            "phone",
            "mobile",
            "fax",
            "index",
            "sequence",
            "seq",
            "version",
            "revision",
            "batch",
        ]

        # Check technical patterns
        for pattern in technical_patterns:
            if pattern in col_lower:
                return False

        # Additional checks for specific data patterns
        if df[column_name].nunique() == len(df):  # Unique values = row count
            return False

        # Check if dtype is numeric
        return np.issubdtype(df[column_name].dtype, np.number)

    def check_duplicates(self, df, column):
        """Count duplicates in a column"""
        try:
            # Get count of all duplicated values
            duplicates = df[df[column].duplicated(keep=False)][column]
            unique_duplicates = duplicates.nunique()
            return len(duplicates), unique_duplicates
        except Exception as e:
            print(f"Error checking duplicates for column {column}: {str(e)}")
            return 0, 0

    def check_null(self, df, column):
        """Count null values in a column"""
        try:
            # Check for various types of null values
            null_count = df[column].isnull().sum()  # Standard null
            empty_count = (
                (df[column] == "").sum() if df[column].dtype == object else 0
            )  # Empty string
            space_count = (
                df[column].astype(str).str.isspace()
            ).sum()  # Only whitespace
            na_count = (
                (df[column] == "NA").sum() if df[column].dtype == object else 0
            )  # 'NA' string
            nan_count = (
                (df[column] == "NaN").sum() if df[column].dtype == object else 0
            )  # 'NaN' string
            none_count = (df[column].astype(str) == "None").sum()  # 'None' string

            # Total null-like values
            total_null_count = (
                null_count
                + empty_count
                + space_count
                + na_count
                + nan_count
                + none_count
            )

            print(f"Debug - Null check for {column}:")
            print(f"  - Null: {null_count}")
            print(f"  - Empty: {empty_count}")
            print(f"  - Space: {space_count}")
            print(f"  - NA: {na_count}")
            print(f"  - NaN: {nan_count}")
            print(f"  - None: {none_count}")
            print(f"  - Total: {total_null_count}")

            return total_null_count
        except Exception as e:
            print(f"Error checking nulls for column {column}: {str(e)}")
            return 0

    def check_sensitive(self, df, column):
        """Count sensitive data (e.g., emails, credit cards) in a column"""
        try:
            if df[column].dtype == object:
                # Email pattern
                email_count = (
                    df[column]
                    .str.contains(
                        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",
                        na=False,
                        regex=True,
                    )
                    .sum()
                )

                # Credit card pattern (simplified)
                cc_count = (
                    df[column]
                    .str.contains(
                        r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", na=False, regex=True
                    )
                    .sum()
                )

                # Phone number pattern (simplified)
                phone_count = (
                    df[column]
                    .str.contains(
                        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", na=False, regex=True
                    )
                    .sum()
                )

                return email_count + cc_count + phone_count
            return 0
        except Exception as e:
            print(f"Error checking sensitive data for column {column}: {str(e)}")
            return 0

    def check_encrypted(self, df, column):
        """Check for potentially encrypted values"""
        try:
            if df[column].dtype == object:
                # Check for hex-like strings
                hex_pattern = r"^[A-Fa-f0-9]{32,}$"
                hex_count = (
                    df[column].str.contains(hex_pattern, na=False, regex=True).sum()
                )

                # Check for base64-like strings
                base64_pattern = r"^[A-Za-z0-9+/]{32,}={0,2}$"
                base64_count = (
                    df[column].str.contains(base64_pattern, na=False, regex=True).sum()
                )

                return hex_count + base64_count
            return 0
        except Exception as e:
            print(f"Error checking encryption for column {column}: {str(e)}")
            return 0

    def calculate_descriptive_stats(self, df):
        """Calculate descriptive statistics for appropriate numeric columns"""
        try:
            stats = {}
            # Filter numeric columns and exclude ID-like columns
            numeric_columns = [
                col for col in df.columns if self.is_analyzable_numeric(col, df)
            ]

            print(f"\nAnalyzing numeric columns: {numeric_columns}")

            for col in numeric_columns:
                stats[col] = {
                    "mean": round(df[col].mean(), 2),
                    "median": round(df[col].median(), 2),
                    "std": round(df[col].std(), 2),
                    "min": round(df[col].min(), 2),
                    "max": round(df[col].max(), 2),
                    "q1": round(df[col].quantile(0.25), 2),
                    "q3": round(df[col].quantile(0.75), 2),
                }
            return stats
        except Exception as e:
            print(f"Error calculating descriptive statistics: {str(e)}")
            return {}

    def detect_outliers(self, df):
        """Detect outliers using IQR method for appropriate numeric columns"""
        try:
            outliers = {}
            numeric_columns = [
                col for col in df.columns if self.is_analyzable_numeric(col, df)
            ]

            for col in numeric_columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers[col] = {
                    "count": len(df[(df[col] < lower_bound) | (df[col] > upper_bound)]),
                    "percentage": round(
                        len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
                        / len(df)
                        * 100,
                        2,
                    ),
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                }
            return outliers
        except Exception as e:
            print(f"Error detecting outliers: {str(e)}")
            return {}

    def analyze_correlations(self, df):
        """Calculate correlations between appropriate numeric columns"""
        try:
            numeric_columns = [
                col for col in df.columns if self.is_analyzable_numeric(col, df)
            ]

            if len(numeric_columns) < 2:
                return []

            numeric_df = df[numeric_columns]
            corr_matrix = numeric_df.corr()

            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    correlation = corr_matrix.iloc[i, j]
                    if abs(correlation) > 0.7:
                        strong_correlations.append(
                            {
                                "column1": corr_matrix.columns[i],
                                "column2": corr_matrix.columns[j],
                                "correlation": round(correlation, 2),
                            }
                        )
            return strong_correlations
        except Exception as e:
            print(f"Error analyzing correlations: {str(e)}")
            return []

    def calculate_column_stats(self, df, columns, check_type):
        """Calculate statistics for specified columns"""
        column_stats = []
        total_rows = len(df)

        for col in columns:
            if col in df.columns:
                try:
                    if check_type == "unique":
                        count, unique_count = self.check_duplicates(df, col)
                        detail = f"({unique_count} duplicate values)"
                    elif check_type == "mandatory":
                        count = self.check_null(df, col)
                        detail = f"({count} null values)"
                    elif check_type == "sensitive":
                        count = self.check_sensitive(df, col)
                        detail = "(sensitive values)"
                    elif check_type == "encrypted":
                        count = self.check_encrypted(df, col)
                        detail = "(encrypted values)"
                    else:
                        continue

                    percentage = (count / total_rows) * 100 if total_rows > 0 else 0

                    column_stats.append(
                        {
                            "column": col,
                            "count": count,
                            "percentage": round(percentage, 2),
                            "total_records": total_rows,
                            "detail": detail,
                        }
                    )

                    print(f"Processed {check_type} check for column {col}:")
                    print(f"  - Count: {count}")
                    print(f"  - Percentage: {percentage:.2f}%")
                    print(f"  - Detail: {detail}")

                except Exception as e:
                    print(f"Error processing column {col}: {str(e)}")

        return column_stats

    def generate_recommendations(self, stats, outliers, correlations):
        """Generate recommendations based on analysis"""
        recommendations = []

        # Data quality recommendations
        for col, stat in stats.items():
            # Check for constant values
            if stat["std"] == 0:
                recommendations.append(
                    f"Column '{col}' has no variation (constant values)"
                )

            # Check value ranges for specific columns
            if col == "Quantity" and stat["min"] < 0:
                recommendations.append(f"Negative quantities found in '{col}' column")

            if col.lower().endswith("price") or "($)" in col:
                if stat["min"] < 0:
                    recommendations.append(f"Negative prices found in '{col}' column")
                if stat["max"] == 0:
                    recommendations.append(f"Zero prices found in '{col}' column")

            # Check for reasonable ranges
            if col == "Age" and (stat["min"] < 0 or stat["max"] > 120):
                recommendations.append(
                    f"Potentially invalid age values in '{col}' column"
                )

            # Check for suspicious patterns
            if stat["mean"] == stat["median"] and stat["std"] > 0:
                recommendations.append(
                    f"Unusual distribution in '{col}' - mean equals median but variation exists"
                )

            # Check for extreme values
            if stat["max"] > stat["mean"] + 3 * stat["std"]:
                recommendations.append(
                    f"Column '{col}' has potential high outliers "
                    f"(max: {stat['max']}, mean + 3σ: {stat['mean'] + 3 * stat['std']:.2f})"
                )
            if stat["min"] < stat["mean"] - 3 * stat["std"]:
                recommendations.append(
                    f"Column '{col}' has potential low outliers "
                    f"(min: {stat['min']}, mean - 3σ: {stat['mean'] - 3 * stat['std']:.2f})"
                )

            # Check for skewed distributions
            if stat["mean"] > stat["median"] * 1.5:
                recommendations.append(
                    f"Column '{col}' shows significant right skew "
                    f"(mean: {stat['mean']:.2f}, median: {stat['median']:.2f})"
                )
            elif stat["median"] > stat["mean"] * 1.5:
                recommendations.append(
                    f"Column '{col}' shows significant left skew "
                    f"(mean: {stat['mean']:.2f}, median: {stat['median']:.2f})"
                )

            # Check for large gaps in data ranges
            range_size = stat["max"] - stat["min"]
            iqr = stat["q3"] - stat["q1"]
            if iqr > 0 and range_size > iqr * 10:
                recommendations.append(
                    f"Column '{col}' has large value gaps "
                    f"(range: {range_size:.2f}, IQR: {iqr:.2f})"
                )

        # Outlier recommendations
        for col, outlier in outliers.items():
            if outlier["percentage"] > 10:
                recommendations.append(
                    f"High number of outliers in '{col}' ({outlier['percentage']}% of values) "
                    f"outside [{outlier['lower_bound']}, {outlier['upper_bound']}]"
                )
            elif outlier["percentage"] > 5:
                recommendations.append(
                    f"Moderate number of outliers in '{col}' ({outlier['percentage']}% of values) "
                    f"outside [{outlier['lower_bound']}, {outlier['upper_bound']}]"
                )

        # Correlation recommendations
        for corr in correlations:
            if abs(corr["correlation"]) > 0.95:
                recommendations.append(
                    f"Very strong correlation ({corr['correlation']}) between '{corr['column1']}' and '{corr['column2']}'. "
                    "Consider if both columns are necessary."
                )
            elif abs(corr["correlation"]) > 0.7:
                recommendations.append(
                    f"Strong correlation ({corr['correlation']}) between '{corr['column1']}' and '{corr['column2']}'."
                )

        return recommendations

    def calculate_data_quality_score(self, report_data):
        """Calculate overall data quality score (0-10)"""
        try:
            scores = {}
            weights = {
                "completeness": 0.25,  # Weight for missing/null values
                "uniqueness": 0.20,  # Weight for duplicate checks
                "validity": 0.20,  # Weight for valid value ranges
                "outliers": 0.15,  # Weight for outlier presence
                "consistency": 0.20,  # Weight for data consistency/correlation
            }

            # Convert percentage scores to 10-point scale
            # 1. Completeness Score
            mandatory_stats = report_data.get("mandatory_stats", [])
            if mandatory_stats:
                null_percentages = [stat["percentage"] for stat in mandatory_stats]
                completeness_score = (
                    10 - (sum(null_percentages) / len(null_percentages)) / 10
                )
            else:
                completeness_score = 10
            scores["completeness"] = max(0, min(10, completeness_score))

            # 2. Uniqueness Score
            unique_stats = report_data.get("unique_stats", [])
            if unique_stats:
                duplicate_percentages = [stat["percentage"] for stat in unique_stats]
                uniqueness_score = (
                    10 - (sum(duplicate_percentages) / len(duplicate_percentages)) / 10
                )

            else:
                uniqueness_score = 10
            scores["uniqueness"] = max(0, min(10, uniqueness_score))

            # 3. Validity Score
            outliers = report_data.get("outliers", {})
            if outliers:
                outlier_percentages = [data["percentage"] for data in outliers.values()]
                validity_score = (
                    10 - (sum(outlier_percentages) / len(outlier_percentages)) / 10
                )
            else:
                validity_score = 10
            scores["validity"] = max(0, min(10, validity_score))

            # 4. Outlier Score
            if outliers:
                outlier_score = (
                    10 - (sum(outlier_percentages) / len(outlier_percentages)) / 10
                )
            else:
                outlier_score = 10
            scores["outliers"] = max(0, min(10, outlier_score))

            # 5. Consistency Score
            correlations = report_data.get("correlations", [])
            recommendations = report_data.get("recommendations", [])

            # Penalize for each strong correlation and recommendation
            consistency_penalties = (
                len(correlations) * 0.5  # -0.5 points for each strong correlation
                + len(recommendations) * 0.2  # -0.2 points for each recommendation
            )
            consistency_score = max(0, 10 - consistency_penalties)
            scores["consistency"] = consistency_score

            # Calculate weighted average score (0-10 scale)
            final_score = sum(
                score * weights[metric] for metric, score in scores.items()
            )

            # Generate score details
            score_details = {
                "overall_score": round(final_score, 1),
                "component_scores": {
                    metric: round(score, 1) for metric, score in scores.items()
                },
                "recommendations": self.get_score_recommendations(scores),
            }

            return score_details

        except Exception as e:
            print(f"Error calculating data quality score: {str(e)}")
            return None

    def get_score_recommendations(self, scores):
        """Generate recommendations based on component scores (0-10 scale)"""
        recommendations = []

        if scores["completeness"] < 9:
            recommendations.append("Address missing values in mandatory fields")

        if scores["uniqueness"] < 9:
            recommendations.append("Investigate and resolve duplicate records")

        if scores["validity"] < 9:
            recommendations.append("Review and clean invalid data values")

        if scores["outliers"] < 9:
            recommendations.append("Investigate outliers and extreme values")

        if scores["consistency"] < 9:
            recommendations.append("Review data consistency and correlation patterns")

        return recommendations

    def process_file(self, file_path):
        """Process a single file and generate statistics"""
        try:
            print(f"\nProcessing file: {file_path}")
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]

            # Debug print to show all unique file names in metadata
            print("\nAvailable files in metadata:")
            print(self.metadata_df["File Name"].unique())

            # Filter metadata for this specific file
            file_metadata = self.metadata_df[
                self.metadata_df["File Name"].str.strip().str.lower()
                == file_name_without_ext.lower()
            ]

            if file_metadata.empty:
                print(f"\nWarning: No metadata found for file {file_name_without_ext}")
                print(
                    "Please check if the file name matches exactly with the metadata."
                )
                return None

            print(f"\nFound metadata for file: {file_name_without_ext}")
            print(f"Number of metadata rows: {len(file_metadata)}")

            # Read CSV with all potential null values
            try:
                df = pd.read_csv(
                    file_path,
                    low_memory=False,
                    na_values=["NA", "NaN", "null", "NULL", "None", ""],
                    keep_default_na=True,
                    encoding="utf-8",
                )
            except UnicodeDecodeError:
                df = pd.read_csv(
                    file_path,
                    low_memory=False,
                    na_values=["NA", "NaN", "null", "NULL", "None", ""],
                    keep_default_na=True,
                    encoding="latin1",
                )

            # Calculate basic statistics
            total_rows = len(df)
            total_columns = len(df.columns)
            unique_columns = len(df.columns.unique())

            # Clean up column names in the data file
            df.columns = df.columns.str.strip().str.replace("\s+", " ", regex=True)

            # Remove duplicate columns from DataFrame
            df = df.loc[:, ~df.columns.duplicated()]

            # Debug print actual columns in the file
            print("\nActual columns in file:")
            print(df.columns.tolist())

            # Debug print columns in metadata for this file
            print("\nColumns in metadata for this file:")
            print(file_metadata["Column Name"].tolist())

            # Filter only 'Yes' values and existing columns for this specific file
            mandatory_columns = (
                file_metadata[
                    (file_metadata["Is Mandatory"].str.upper() == "YES")
                    & (file_metadata["Column Name"].isin(df.columns))
                ]["Column Name"]
                .unique()
                .tolist()
            )

            unique_columns_check = (
                file_metadata[
                    (file_metadata["Is Unique"].str.upper() == "YES")
                    & (file_metadata["Column Name"].isin(df.columns))
                ]["Column Name"]
                .unique()
                .tolist()
            )

            sensitive_columns = (
                file_metadata[
                    (file_metadata["Sensitive"].str.upper() == "YES")
                    & (file_metadata["Column Name"].isin(df.columns))
                ]["Column Name"]
                .unique()
                .tolist()
            )

            encrypted_columns = (
                file_metadata[
                    (file_metadata["Encrypted"].str.upper() == "YES")
                    & (file_metadata["Column Name"].isin(df.columns))
                ]["Column Name"]
                .unique()
                .tolist()
            )

            # Calculate advanced statistics
            desc_stats = self.calculate_descriptive_stats(df)
            outliers = self.detect_outliers(df)
            correlations = self.analyze_correlations(df)

            # Get all columns from the metadata for this specific file
            expected_columns = file_metadata["Column Name"].unique().tolist()
            actual_columns = df.columns.tolist()

            # Calculate missing and additional columns
            missing_columns = [
                col for col in expected_columns if col not in actual_columns
            ]
            additional_columns = [
                col for col in actual_columns if col not in expected_columns
            ]

            # Generate recommendations
            recommendations = self.generate_recommendations(
                desc_stats, outliers, correlations
            )

            # Prepare report data
            report_data = {
                "file_name": file_name,
                "file_path": file_path,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "unique_columns": unique_columns,
                "file_metadata": file_metadata,
                "mandatory_stats": self.calculate_column_stats(
                    df, mandatory_columns, "mandatory"
                ),
                "unique_stats": self.calculate_column_stats(
                    df, unique_columns_check, "unique"
                ),
                "sensitive_stats": self.calculate_column_stats(
                    df, sensitive_columns, "sensitive"
                ),
                "encrypted_stats": self.calculate_column_stats(
                    df, encrypted_columns, "encrypted"
                ),
                "descriptive_stats": desc_stats,
                "outliers": outliers,
                "correlations": correlations,
                "recommendations": recommendations,
                "missing_columns": missing_columns,
                "additional_columns": additional_columns,
            }

            # Calculate data quality score
            quality_score = self.calculate_data_quality_score(report_data)
            report_data["quality_score"] = quality_score

            # Generate individual report
            self.generate_individual_report(report_data)
            return report_data

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None

    def generate_html_table(self, data, section_type):
        """Generate HTML table from data"""
        if not data:
            return "<p class='no-data'>No data available for this section</p>"

        html = """
        <table class='data-table'>
            <tr>
                <th>Column Name</th>
                <th>Total Records</th>
                <th>Count</th>
                <th>Percentage</th>
                <th>Details</th>
            </tr>
        """

        for row in data:
            html += f"""
            <tr>
                <td>{row['column']}</td>
                <td>{row['total_records']:,}</td>
                <td>{row['count']:,}</td>
                <td>{row['percentage']:.2f}%</td>
                <td>{row['detail']}</td>
            </tr>
            """
        html += "</table>"
        return html

    def generate_stats_table(self, stats):
        """Generate HTML table for descriptive statistics"""
        if not stats:
            return "<p class='no-data'>No numeric columns available for analysis</p>"

        html = """
        <table class='data-table'>
            <tr>
                <th>Column</th>
                <th>Mean</th>
                <th>Median</th>
                <th>Std Dev</th>
                <th>Min</th>
                <th>Max</th>
                <th>Q1</th>
                <th>Q3</th>
            </tr>
        """

        for col, stat in stats.items():
            html += f"""
            <tr>
                <td>{col}</td>
                <td>{stat['mean']}</td>
                <td>{stat['median']}</td>
                <td>{stat['std']}</td>
                <td>{stat['min']}</td>
                <td>{stat['max']}</td>
                <td>{stat['q1']}</td>
                <td>{stat['q3']}</td>
            </tr>
            """
        html += "</table>"
        return html

    def generate_outliers_table(self, outliers):
        """Generate HTML table for outlier analysis"""
        if not outliers:
            return "<p class='no-data'>No numeric columns available for outlier analysis</p>"

        html = """
        <table class='data-table'>
            <tr>
                <th>Column</th>
                <th>Outlier Count</th>
                <th>Percentage</th>
                <th>Lower Bound</th>
                <th>Upper Bound</th>
            </tr>
        """

        for col, data in outliers.items():
            html += f"""
            <tr>
                <td>{col}</td>
                <td>{data['count']}</td>
                <td>{data['percentage']}%</td>
                <td>{data['lower_bound']}</td>
                <td>{data['upper_bound']}</td>
            </tr>
            """
        html += "</table>"
        return html

    def generate_correlations_table(self, correlations):
        """Generate HTML table for correlation analysis"""
        if not correlations:
            return "<p class='no-data'>No significant correlations found</p>"

        html = """
        <table class='data-table'>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Correlation</th>
            </tr>
        """

        for corr in correlations:
            html += f"""
            <tr>
                <td>{corr['column1']}</td>
                <td>{corr['column2']}</td>
                <td>{corr['correlation']}</td>
            </tr>
            """
        html += "</table>"
        return html

    def generate_recommendations_list(self, recommendations):
        """Generate HTML list for recommendations"""
        if not recommendations:
            return "<p class='no-data'>No specific recommendations generated</p>"

        html = "<ul class='recommendations-list'>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        return html

    def generate_individual_report(self, report_data):
        """Generate individual HTML report for a file"""
        try:
            # Get metadata columns for this file
            file_metadata = report_data["file_metadata"]
            mandatory_columns = file_metadata[
                file_metadata["Is Mandatory"].str.upper() == "YES"
            ]["Column Name"].tolist()
            unique_columns = file_metadata[
                file_metadata["Is Unique"].str.upper() == "YES"
            ]["Column Name"].tolist()
            sensitive_columns = file_metadata[
                file_metadata["Sensitive"].str.upper() == "YES"
            ]["Column Name"].tolist()
            encrypted_columns = file_metadata[
                file_metadata["Encrypted"].str.upper() == "YES"
            ]["Column Name"].tolist()
            currency_columns = file_metadata[
                file_metadata["Currency"].str.upper() == "YES"
            ]["Column Name"].tolist()
            # [col for col in report_data['currency_validation'].keys()] if 'currency_validation' in report_data else []
            missing_columns = report_data.get("missing_columns", [])
            additional_columns = report_data.get("additional_columns", [])

            # Generate HTML report with corrected style
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Data Quality Report</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 20px; 
                        background-color: #f5f5f5;
                    }}
                    .header {{ 
                        background-color: #ffffff; 
                        padding: 20px; 
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin-bottom: 20px;
                    }}
                    .section-header {{ 
                        margin-top: 20px; 
                        padding: 10px; 
                        background-color: #e9ecef;
                        border-radius: 5px;
                    }}
                    .data-table {{ 
                        width: 100%; 
                        border-collapse: collapse; 
                        margin-top: 10px;
                        background-color: #ffffff;
                    }}
                    .data-table th, .data-table td {{ 
                        border: 1px solid #dee2e6; 
                        padding: 12px; 
                        text-align: left; 
                    }}
                    .data-table th {{ 
                        background-color: #f8f9fa;
                        color: #495057;
                    }}
                    .data-table tr:nth-child(even) {{
                        background-color: #f8f9fa;
                    }}
                    .no-data {{ 
                        color: #6c757d; 
                        font-style: italic;
                        padding: 20px;
                        text-align: center;
                    }}
                    .column-list {{ 
                        word-wrap: break-word; 
                        max-width: 500px;
                        color: #495057;
                    }}
                    .score-container {{
                        padding: 20px;
                        background-color: #ffffff;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin: 20px 0;
                    }}
                    .overall-score {{
                        text-align: center;
                        font-size: 24px;
                        color: #2c3e50;
                        margin-bottom: 20px;
                    }}
                    # .score-interpretation {{
                    #     font-style: italic;
                    #     color: #6c757d;
                    #     margin-bottom: 15px;
                    #     text-align: center;
                    # }}
                    .component-scores {{
                        margin-bottom: 20px;
                    }}
                    .score-table {{
                        width: 100%;
                        margin-bottom: 20px;
                        border-collapse: collapse;
                        background-color: #ffffff;
                        table-layout: fixed;
                    }}
                    .score-table th, .score-table td {{
                        border: 1px solid #dee2e6;
                        padding: 12px;
                        text-align: left;
                    }}
                    .score-table th {{
                        background-color: #f8f9fa;
                        color: #495057;
                    }}
                    .score-table th:first-child {{
                        width: 40%;
                    }}
                    .score-table th:last-child {{
                        width: 60%;
                    }}
                    .overall-score {{
                        text-align: center;
                        font-size: 24px;
                        color: #2c3e50;
                        margin: 20px 0;
                        padding: 20px;
                    }}
                    .component-scores h4 {{
                        margin-bottom: 15px;
                        color: #2c3e50;
                    }}
                    .recommendations-list {{
                        list-style-type: disc;
                        margin-left: 20px;
                        color: #495057;
                    }}
                    .analysis-section {{
                        margin: 20px 0;
                        padding: 20px;
                        background-color: #ffffff;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .section-title {{
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}
                    h2 {{
                        color: #2c3e50;
                        margin-top: 0;
                    }}
                    h3 {{
                        color: #2c3e50;
                        margin-top: 0;
                    }}
                    h4 {{
                        color: #2c3e50;
                        margin-top: 0;
                    }}
                </style>
            </head>
            <body>
            """

            # Add header section
            html += f"""
                <div class='header'>
                    <h2>Data Quality Report</h2>
                    <p>File: {report_data['file_name']}</p>
                    <p>Generated: {self.report_timestamp}</p>
                    <table class='data-table'>
                        <tr>
                            <th>Total Rows</th>
                            <td>{report_data['total_rows']:,}</td>
                        </tr>
                        <tr>
                            <th>Total Columns</th>
                            <td>{report_data['total_columns']:,}</td>
                        </tr>
                        <tr>
                            <th>Missing Columns</th>
                            <td class="column-list">{', '.join(missing_columns) if missing_columns else 'None'}</td>
                        </tr>
                        <tr>
                            <th>Additional Columns</th>
                            <td class="column-list">{', '.join(additional_columns) if additional_columns else 'None'}</td>
                        </tr>
                        <tr>
                            <th>Mandatory Columns</th>
                            <td class="column-list">{', '.join(mandatory_columns) if mandatory_columns else 'None'}</td>
                        </tr>
                        <tr>
                            <th>Unique Columns</th>
                            <td class="column-list">{', '.join(unique_columns) if unique_columns else 'None'}</td>
                        </tr>
                        <tr>
                            <th>Sensitive Columns</th>
                            <td class="column-list">{', '.join(sensitive_columns) if sensitive_columns else 'None'}</td>
                        </tr>
                        <tr>
                            <th>Encrypted Columns</th>
                            <td class="column-list">{', '.join(encrypted_columns) if encrypted_columns else 'None'}</td>
                        </tr>
                        <tr>
                            <th>Currency Columns</th>
                            <td class="column-list">{', '.join(currency_columns) if currency_columns else 'None'}</td>
                        </tr>
                    </table>
                </div>
            """

            # Add Data Quality Score section
            if "quality_score" in report_data:
                html += f"""
                    <div class='analysis-section'>
                        <h3 class='section-title'>Data Quality Score</h3>
                        <div class='score-container'>
                            <div class='overall-score'>
                                Overall Score: {report_data['quality_score']['overall_score']:.1f}
                            </div>
                            <div class='component-scores'>
                                <h4>Component Scores:</h4>
                                <table class='score-table'>
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>Score</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                """

                # Add component scores
                for metric, score in report_data["quality_score"][
                    "component_scores"
                ].items():
                    html += f"""
                        <tr>
                            <td>{metric.title()}</td>
                            <td>{score:.1f}</td>
                        </tr>
                    """

                html += """
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                """

            # Add sections for different types of columns
            sections = [
                ("Null Check", report_data.get("mandatory_stats", []), "mandatory"),
                ("Duplicate Check", report_data.get("unique_stats", []), "unique"),
                (
                    "Sensitive Data Check",
                    report_data.get("sensitive_stats", []),
                    "sensitive",
                ),
                (
                    "Encryption Check",
                    report_data.get("encrypted_stats", []),
                    "encrypted",
                ),
            ]

            for section_name, stats, section_type in sections:
                if stats:
                    html += f"""
                        <div class='section-header'>
                            <h3>{section_name}</h3>
                        </div>
                        {self.generate_html_table(stats, section_type)}
                    """

            # Add analysis sections
            html += f"""
                <div class='analysis-section'>
                    <h3 class='section-title'>Descriptive Statistics</h3>
                    {self.generate_stats_table(report_data.get('descriptive_stats', {}))}
                </div>

                <div class='analysis-section'>
                    <h3 class='section-title'>Outlier Analysis</h3>
                    {self.generate_outliers_table(report_data.get('outliers', {}))}
                </div>

                <div class='analysis-section'>
                    <h3 class='section-title'>Correlation Analysis</h3>
                    {self.generate_correlations_table(report_data.get('correlations', []))}
                </div>

                <div class='analysis-section'>
                    <h3 class='section-title'>Recommendations</h3>
                    {self.generate_recommendations_list(report_data.get('recommendations', []))}
                </div>
            """

            html += """
                    </body>
                </html>
            """

            # Save individual report
            filename = f"{self.output_dir}/reports_{report_data['file_name'].replace('.csv', '')}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Individual report generated: {filename}")

        except Exception as e:
            print(f"Error generating report: {str(e)}")
            raise

    def is_currency_column(self, column_name):
        """Check if a column name indicates currency data"""
        column_lower = column_name.lower()
        return any(indicator in column_lower for indicator in self.currency_indicators)

    def validate_currency_format(self, value, expected_currency="USD"):
        """Validate currency format for a given value"""
        if pd.isna(value):
            return True  # Skip null values

        str_value = str(value).strip()
        str_value = (
            str_value.replace("$", "")
            .replace("€", "")
            .replace("£", "")
            .replace("₹", "")
        )
        pattern = self.currency_patterns.get(
            expected_currency, self.currency_patterns["USD"]
        )

        if not re.match(pattern, str_value):
            return False

        try:
            numeric_value = float(str_value.replace(",", ""))
            if numeric_value < 0:
                return False
            return True
        except ValueError:
            return False

    def check_currency_format(self, df, column, expected_currency="USD"):
        """Check currency format compliance for a column"""
        try:
            if df[column].dtype == object or np.issubdtype(df[column].dtype, np.number):
                invalid_count = 0
                negative_count = 0
                zero_count = 0
                total_count = len(df)

                for value in df[column]:
                    if pd.isna(value):
                        continue

                    str_value = str(value).strip()
                    cleaned_value = (
                        str_value.replace("$", "")
                        .replace("€", "")
                        .replace("£", "")
                        .replace("₹", "")
                        .replace(",", "")
                    )

                    try:
                        numeric_value = float(cleaned_value)
                        if numeric_value < 0:
                            negative_count += 1
                        elif numeric_value == 0:
                            zero_count += 1
                        elif not self.validate_currency_format(
                            str_value, expected_currency
                        ):
                            invalid_count += 1
                    except ValueError:
                        invalid_count += 1

                return {
                    "invalid_format": invalid_count,
                    "negative_values": negative_count,
                    "zero_values": zero_count,
                    "total_records": total_count,
                    "invalid_percentage": round((invalid_count / total_count) * 100, 2),
                    "negative_percentage": round(
                        (negative_count / total_count) * 100, 2
                    ),
                    "zero_percentage": round((zero_count / total_count) * 100, 2),
                }
            return None
        except Exception as e:
            print(f"Error checking currency format for column {column}: {str(e)}")
            return None


def main():
    try:
        # Configure paths
        source_root_dir = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/RAW"

        # metadata_file = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Metadata/schemaMaster.csv"
        metadata_file = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/IQVIA FLOW/schemaMaster.csv"

        # Load metadata
        print("Loading metadata file...")
        metadata_df = pd.read_csv(metadata_file)
        print(f"Metadata loaded successfully: {len(metadata_df)} rows")

        # Initialize profiler and set metadata
        profiler = DataProfiler()
        profiler.set_metadata(metadata_df)

        # Process all CSV files
        csv_files = glob.glob(
            os.path.join(source_root_dir, "**", "*.csv"), recursive=True
        )
        print(f"\nFound {len(csv_files)} CSV files to process")

        # Process each file
        for file_path in csv_files:
            profiler.process_file(file_path)

        print("\nAll reports generated successfully!")

    except Exception as e:
        print(f"\nError in main execution: {str(e)}")


if __name__ == "__main__":
    main()
