import streamlit as st
import pandas as pd

# Configure the Streamlit app layout
st.set_page_config(page_title="Excel Data Editor", layout="wide")

# File path to the CSV file
file_path = "C:/Environments/CV-PROJECTS-PERSONAL/CV-Projects/IQVIA V0.1/IQVIA/Directories/Metadata/schemaMaster.csv"

# Load the CSV file
df = pd.read_csv(file_path)

# Define columns to provide toggle functionality
toggle_columns = [
    "Is Numeric",
    "Is Mandatory",
    "Is Unique",
    "Is Primary Key",
    "Is Foreign Key",
    "Auto Gen",
    "Default",
    "Sensitive",
    "Encrypted",
    "Currency",
    "Measurement",
]

# Provide an option for users to edit the specific columns with NaN values
for column in toggle_columns:
    if column in df.columns:
        # Replace NaN values in specified columns with 'Yes' or 'No'
        df[column] = df[column].fillna("No")

# Display the DataFrame as a table, allowing inline editing in the specified columns
edited_df = st.data_editor(df)

# Provide a button to save the updated DataFrame to CSV
if st.button("Save Changes"):
    # Ensure that the edited DataFrame is saved
    edited_df.to_csv(file_path, index=False)
    st.success("Excel file has been updated successfully!")

    # Create a signal file to indicate that changes were saved
    with open("signal_file.txt", "w") as f:
        f.write("changes_saved")

    # Display the updated DataFrame only after saving
    st.write("### Changes made in the DataFrame:")
    st.write(edited_df)
