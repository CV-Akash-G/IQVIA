import pandas as pd
import os
import spacy
import re

# Load pre-trained spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Path to the main directory containing subfolders
main_folder_path = (
    "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/RAW"
)

# Load the source mapping Excel file (update the file path accordingly)
source_mapping_file = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Source Master Mapping/Source_master.xlsx"

# Load the Excel file into a DataFrame
source_mapping_df = pd.read_excel(source_mapping_file)

# Debugging: print the first few rows of the source mapping to verify contents
print("Source Mapping DataFrame:")
print(source_mapping_df.head())

# Dictionary to map Source Name to Source ID, Source Type, and File Type
source_mapping = {
    row["Source Name"]: {
        "Source ID": row["Source Id"],
        "Source Type": row["Source Type"],
        "File Type": row["File Type"],
    }
    for _, row in source_mapping_df.iterrows()
}

# Debugging: print the source mapping dictionary keys
print("Available Source Names in Mapping:")
print(source_mapping.keys())


# Function to get source information (ID, Type, and File Type) from the mapping
def get_source_info(source_name):
    # Normalize the case to title case for comparison
    normalized_source_name = source_name.strip()  # Normalize to Title Case
    print(f"Normalized Source Name: {normalized_source_name}")
    return source_mapping.get(normalized_source_name, None)


# Initialize a dictionary to store data by file
file_data = []

# Dictionary to track column names and their sources for comparison
column_sources = {}

# List of common default values (you can expand this list as needed)
default_values = ["yes", "no", "true", "false", "1", "0"]

# List of common currency symbols
currency_symbols = ["$", "€", "£", "¥", "₹"]

# List of common measurement units
measurement_units = ["kg", "lbs", "m", "cm", "inches", "ft", "meter", "km", "mile"]


# Function to calculate maximum length or max value for each column
def get_column_length_and_max_value(column_data):
    if pd.api.types.is_string_dtype(column_data):
        # For string columns, calculate the max length of values
        return column_data.apply(
            lambda x: len(str(x))
        ).max(), None  # return length info
    elif pd.api.types.is_numeric_dtype(column_data):
        # For numeric columns, calculate the max value
        return None, column_data.max()  # return value info
    return (
        "No Data",
        None,
    )  # Return a default value for non-string and non-numeric columns (if any)


# Function to check for Sensitive data (simple pattern check for common sensitive data)
def is_sensitive(column_data):
    sensitive_patterns = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # Email pattern
        r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}",  # Phone number pattern
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
    ]

    column_data_str = column_data.astype(str).str.lower()
    for pattern in sensitive_patterns:
        if column_data_str.str.contains(pattern).any():
            return "Yes"
    return "No"


# Function to check for Encrypted data (e.g., base64 encoded strings or long random strings)
def is_encrypted(column_data):
    column_data_str = column_data.astype(str)
    for value in column_data_str:
        if re.match(r"^[A-Za-z0-9+/=]{8,}$", value):  # Base64 pattern
            return "Yes"
    return "No"


# Function to check for Currency data (columns with currency symbols)
def is_currency(column_data):
    if not pd.api.types.is_string_dtype(
        column_data
    ) and not pd.api.types.is_numeric_dtype(column_data):
        return "No"

    column_data_str = column_data.astype(str)

    # Use spaCy to detect monetary entities
    for value in column_data_str:
        doc = nlp(value)
        for ent in doc.ents:
            if ent.label_ == "MONEY":  # spaCy's label for monetary entities
                return "Yes"

    # Check each value in the column for the presence of any currency symbols
    for value in column_data_str:
        for symbol in currency_symbols:
            if symbol in value:
                return "Yes"
    return "No"


# Function to check for Measurements (using NLP and regex to identify units)
def is_measurement(column_data):
    if not pd.api.types.is_string_dtype(
        column_data
    ) and not pd.api.types.is_numeric_dtype(column_data):
        return "No"

    column_data_str = column_data.astype(str).str.lower()

    # Process each entry in the column using spaCy NLP
    for value in column_data_str:
        doc = nlp(value)  # Process the text with spaCy's NLP model

        # Check if any measurement units are found by spaCy's NER model
        for ent in doc.ents:
            if ent.text in measurement_units:
                return "Yes"

        # Check for the presence of measurement units using regex (for variations)
        for unit in measurement_units:
            if re.search(r"\b" + unit + r"\b", value):
                return "Yes"
    return "No"


# Function to check for Auto Gen: Check if column contains a sequential pattern
def is_auto_gen(column_data):
    if pd.api.types.is_numeric_dtype(column_data):
        diff = column_data.diff().dropna()
        if diff.nunique() == 1 and diff.iloc[0] == 1:
            return "Yes"
    return "No"


# Function to check for Default: Check if column contains default values
def is_default(column_data):
    column_data_lower = column_data.astype(str).str.lower()
    return "Yes" if column_data_lower.isin(default_values).any() else "No"


def get_column_data_type(column_data):
    """Map the pandas dtype to a user-friendly description, with distinction between datetime and date."""
    dtype = column_data.dtype

    if pd.api.types.is_string_dtype(dtype):
        # Attempt to convert the column to datetime if it contains date-like strings
        try:
            # Try parsing date-like strings, assuming the date format is "DD-MM-YYYY"
            if pd.to_datetime(column_data, errors="coerce").notnull().all():
                return "date"  # Treat as date if conversion is successful
        except Exception:
            pass
        return "string"  # For string/text columns
    elif pd.api.types.is_numeric_dtype(dtype):
        if pd.api.types.is_integer_dtype(dtype):
            return "int"  # For integer columns
        elif pd.api.types.is_float_dtype(dtype):
            return "float"  # For float columns
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        # If the column is already in datetime format
        if column_data.dt.time.isnull().all():  # No time part
            return "date"  # For date-only columns
        return "datetime"  # For datetime columns with time information
    elif pd.api.types.is_timedelta64_dtype(dtype):
        return "timedelta"  # For timedelta columns
    elif pd.api.types.is_bool_dtype(dtype):
        return "boolean"  # For boolean columns
    return "unknown"  # In case we can't map the dtype


# Function to handle non-serializable pandas types
def default_serializer(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()  # Convert Timestamp to string in ISO format
    if isinstance(obj, pd.Int64Dtype):
        return int(obj)  # Convert pandas Int64Dtype to native int
    if isinstance(obj, pd.Float64Dtype):
        return float(obj)  # Convert pandas Float64Dtype to native float
    if isinstance(obj, pd.Series):
        return obj.tolist()  # Convert pandas Series to list
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")  # Convert DataFrame to list of dicts
    return str(obj)  # For other types, convert to string if they are not serializable


# Walk through the subfolders and files in the main folder
for subdir, dirs, files in os.walk(main_folder_path):
    # Skip the main folder itself and only process subfolders
    if subdir == main_folder_path:
        continue

    # Extract the Source Name from the subfolder name and normalize it (e.g., title case)
    source_name = os.path.basename(subdir).strip()  # Normalize case

    # Debugging: print the extracted source name
    print(f"Extracted Source Name: {source_name}")

    # Get the Source ID, Source Type, and File Type from the source_mapping dictionary
    source_info = get_source_info(source_name)

    if source_info is None:
        print(
            f"Warning: Source Name '{source_name}' not found in the mapping. Skipping."
        )
        continue

    source_id = source_info["Source ID"]
    source_type = source_info["Source Type"]
    file_type = source_info["File Type"]

    file_id_counter = 1

    for file_name in files:
        print(
            f"Processing file: {file_name}"
        )  # Debugging: print file names being processed

        # Skip if the file is not CSV or Excel
        if not (file_name.endswith(".csv") or file_name.endswith(".xlsx")):
            continue

        file_path = os.path.join(subdir, file_name)
        file_name_without_extension = os.path.splitext(file_name)[
            0
        ]  # File name without extension

        file_id = file_id_counter
        file_id_counter += 1

        if file_name.endswith(".csv"):
            df = pd.read_csv(file_path, nrows=100)
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(file_path, nrows=100)

        for index, column in enumerate(
            df.columns, 1
        ):  # enumerate to get column index starting from 1
            if column not in column_sources:
                column_sources[column] = []
            column_sources[column].append(
                {
                    "source": source_name,
                    "file_name": file_name_without_extension,
                    "file_id": file_id,
                    "column_sequence": index,
                }
            )

            column_length, max_value = get_column_length_and_max_value(df[column])
            data_type = get_column_data_type(df[column])  # Get the actual data type

            is_primary_key = (
                "Yes"
                if df[column].nunique() == len(df[column])
                and df[column].notnull().all()
                else "No"
            )
            is_foreign_key = "No"
            for other_column in df.columns:
                if column != other_column:
                    if df[column].isin(df[other_column]).any():
                        is_foreign_key = "Yes"
                        break

            auto_gen = is_auto_gen(df[column])
            default = is_default(df[column])
            sensitive = is_sensitive(df[column])
            encrypted = is_encrypted(df[column])
            currency = is_currency(df[column])
            measurement = is_measurement(df[column])

            column_data = {
                "Source ID": int(source_id),
                "Source Name": str(source_name),
                "Source Type": str(source_type),
                "File Type": str(file_type),
                "File ID": int(file_id),
                "File Name": str(file_name_without_extension),
                "Column Name": str(column),
                "Column Sequence": int(index),
                "Similar Columns": "",
                "Similar Columns File ID": "",
                "Data Type": data_type,  # Store the actual data type here
                "Is Numeric": "Yes"
                if pd.api.types.is_numeric_dtype(df[column])
                else "No",
                "Is Mandatory": "Yes" if df[column].isnull().sum() == 0 else "No",
                "Is Unique": "Yes" if df[column].nunique() == len(df[column]) else "No",
                "Is Primary Key": "",  # is_primary_key,
                "Is Foreign Key": "",  # is_foreign_key,
                "Lookup Column": "",
                "Auto Gen": auto_gen,
                "Default": default,
                "Sensitive": sensitive,
                "Encrypted": encrypted,
                "Currency": currency,
                "Measurement": measurement,
            }
            # "Column Length": column_length if column_length else max_value,
            file_data.append(column_data)

# After collecting all data, identify similar columns and update the new columns
for column_info in file_data:
    column_name = column_info["Column Name"]
    if column_name in column_sources and len(column_sources[column_name]) > 1:
        column_info["Similar Columns"] = "Yes"
        similar_sources = column_sources[column_name]
        similar_sources_info = [f"{source['file_id']}" for source in similar_sources]
        column_info["Similar Columns File ID"] = "; ".join(similar_sources_info)
    else:
        column_info["Similar Columns"] = "No"
        column_info["Similar Columns File ID"] = "None"

# Convert the collected data into a DataFrame
df_all_data = pd.DataFrame(file_data)

# Save all the data into a single CSV file
df_all_data.to_csv(
    "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Metadata/schemaMaster.csv",
    index=False,
    encoding="utf-8",
)
print("Metadata catalog has been saved")

# Print the first few rows of the DataFrame for a sample file
print(df_all_data.head())
