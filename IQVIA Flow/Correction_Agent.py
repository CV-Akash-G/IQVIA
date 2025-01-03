import pandas as pd
import os
import json
from fuzzywuzzy import process  # For fuzzy matching
import glob

# Paths
main_folder_path = (
    "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/RAW"
)
source_mapping_file = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Synthetic data/IQVIA Drug Name/drug_details.json"
curated_folder_path = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Curated"

# Load the source mapping JSON file
with open(source_mapping_file, "r") as f:
    source_mapping_data = json.load(f)

# Convert the JSON data to a DataFrame
source_mapping_df = pd.DataFrame(source_mapping_data)

# Extract drug names for fuzzy matching
drug_names = source_mapping_df["Drug Name"].tolist()

# Ensure the Curated folder exists
os.makedirs(curated_folder_path, exist_ok=True)


# Function to convert any date format to MM/DD/YYYY (US format)
def convert_to_us_date(date):
    try:
        # Convert the date to a datetime object
        date_obj = pd.to_datetime(
            date, errors="coerce", dayfirst=False
        )  # dayfirst=False for US format
        if pd.notnull(date_obj):
            return date_obj.strftime("%m/%d/%Y")  # Return date in MM/DD/YYYY format
        else:
            return date  # Return original if date conversion fails
    except Exception as e:
        print(f"Error converting date: {e}")
        return date  # Return original if an error occurs


# Profiler class for outlier detection and correction
class Profiler:
    def process_file(self, file_path):
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path)
        df_corrected = self.handle_outliers(df)

        # Save the corrected DataFrame back to the original file
        df_corrected.to_csv(file_path, index=False)
        print(f"File saved as: {file_path}")

    def handle_outliers(
        self, df, lower_threshold_multiplier=1.5, upper_threshold_multiplier=1.5
    ):
        """
        Function to apply outlier detection and correction using IQR method
        on all numerical columns in the dataframe.
        """
        for column in df.select_dtypes(include=["number"]).columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_threshold = Q1 - lower_threshold_multiplier * IQR
            upper_threshold = Q3 + upper_threshold_multiplier * IQR
            df[column] = df[column].apply(
                lambda x: max(min(x, upper_threshold), lower_threshold)
            )
        return df


def remove_duplicates_from_file(file_path, metadata_df):
    """Remove duplicates from columns marked as unique in metadata"""
    try:
        print(f"\nProcessing file: {file_path}")
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]

        # Filter metadata for this specific file
        file_metadata = metadata_df[
            metadata_df["File Name"].str.strip().str.lower()
            == file_name_without_ext.lower()
        ]

        if file_metadata.empty:
            print(f"No metadata found for file {file_name_without_ext}")
            return None

        # Read the CSV file
        df = pd.read_csv(file_path)
        initial_count = len(df)

        # Get unique columns from metadata
        unique_columns = (
            file_metadata[(file_metadata["Is Unique"].str.upper() == "YES")][
                "Column Name"
            ]
            .unique()
            .tolist()
        )

        if not unique_columns:
            print(f"No unique columns defined in metadata for {file_name}")
            return None

        cleaned_df = df.copy()

        # Process each unique column
        for column in unique_columns:
            if column in df.columns:
                print(f"\nChecking column: {column}")
                # Remove duplicates keeping first occurrence
                cleaned_df = cleaned_df.drop_duplicates(subset=[column], keep="first")
                rows_removed = initial_count - len(cleaned_df)
                print(f"Removed {rows_removed} duplicate rows based on column {column}")
                initial_count = len(cleaned_df)

        # Save cleaned file back to the same file path
        cleaned_df.to_csv(file_path, index=False)
        print(f"Saved cleaned file to: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")


# Process each CSV in the main folder
for root, dirs, files in os.walk(main_folder_path):
    for file in files:
        if file.endswith(".csv"):  # Process only CSV files
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            try:
                # Load the CSV into a DataFrame
                df = pd.read_csv(file_path)

                # Check if the file contains the "Product Name" column
                if "Product Name" in df.columns:
                    # Apply fuzzy matching to correct product names and update the "Product Name" column
                    for idx, row in df.iterrows():
                        product_name = row["Product Name"]
                        closest_match = process.extractOne(product_name, drug_names)
                        if closest_match:
                            matched_name, score = closest_match
                            # Update the "Product Name" column if the match score is above a threshold (e.g., 80)
                            if score > 80:
                                df.at[idx, "Product Name"] = matched_name
                            else:
                                df.at[idx, "Product Name"] = (
                                    product_name  # Keep original if no reliable match
                                )

                # Check if the file contains the "Expiry Date" column
                if "Expiry Date" in df.columns:
                    # Apply date conversion to the "Expiry Date" column
                    for idx, row in df.iterrows():
                        original_date = row["Expiry Date"]
                        corrected_date = convert_to_us_date(original_date)

                        # Print the change if it was corrected
                        if original_date != corrected_date:
                            print(
                                f"Correcting date for row {idx}: '{original_date}' -> '{corrected_date}'"
                            )

                        # Update the Expiry Date column with corrected value
                        df.at[idx, "Expiry Date"] = corrected_date

                # Save the updated CSV to the Curated folder
                relative_path = os.path.relpath(root, main_folder_path)
                save_folder = os.path.join(curated_folder_path, relative_path)
                os.makedirs(save_folder, exist_ok=True)  # Ensure the folder exists
                save_path = os.path.join(save_folder, file)

                # Ensure the changes are written properly to the CSV
                df.to_csv(save_path, index=False)
                print(f"Saved corrected file to: {save_path}")

                # After saving, run the Profiler to handle outliers
                profiler = Profiler()
                profiler.process_file(save_path)

                # Now apply the duplicate removal function to the saved file
                remove_duplicates_from_file(
                    save_path,
                    pd.read_csv(
                        "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Metadata/schemaMaster.csv"
                    ),
                )

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Optional: After processing all files, we can collect a list of the processed files if needed
# Example: Collect a list of all the processed files
processed_files = glob.glob(
    os.path.join(curated_folder_path, "**", "*.csv"), recursive=True
)
print(f"\nProcessed {len(processed_files)} files.")
