# **Detailed Documentation: Data Quality (DQ) Process Automation with GenAI**

## Overview

This Python script automates a sequence of tasks, including metadata collection, running a Streamlit app, monitoring for changes, and executing various report generation and text correction scripts. The script is organized into steps that are executed in sequence, and it logs each step's success or failure into a log file.

## Prerequisites

Before running the script, ensure the following:

- **Python 3.x** installed on your system.
- The required Python packages for the scripts:
  - `subprocess`
  - `time`
  - `os`
  - `logging`
  - Any additional packages that the individual scripts (e.g., `Catalog_Agent.py`, `Feed_Agent.py` `Pattern_Mining_Agent.py`, `Repair_Agent.py`) require.
- **Streamlit** installed to run the Streamlit app:
  `pip install streamlit`
- Ensure the Python scripts (`Catalog_Agent.py`, `Feed_Agnent.py`, etc.) are present in the same directory as this main script or adjust the paths accordingly.

## Script Steps

### 1. **Metadata Collection Script**

- The script runs `Catalog_Agent.py` to collect metadata.
- Logs the success or failure of the script execution.

### 2. **Running Streamlit App**

- The script runs the Streamlit app `Feed_Agnent.py` using `subprocess.Popen`.
- It waits for a signal file (`signal_file.txt`) to indicate that changes have been saved in the Streamlit app.

### 3. **Monitoring Signal File**

- The script monitors the `signal_file.txt` for the message `changes_saved`.
- Once the signal is detected, it logs success and continues the process.

### 4. **Terminating Streamlit App**

- After the changes are confirmed, the script terminates the Streamlit app.
- It clears the content of the signal file.

### 5. **Running Reports Generation Script**

- The script runs `Analyze_Agent.py` to generate reports.
- Logs the success or failure of this script.

### 6. **Running Text Correction Script**

- The script runs `Repair_Agent.py` to perform text corrections on generated data.
- Logs the success or failure of this script.

### 7. **Curated Reports Generation Script**

- The script runs `Pattern_Mining_Curated.py` to generate curated reports.
- Logs the success or failure of this script.

## Log File

All execution steps are logged to a file named `run_sequence.log`. This file contains information about each step, including:

- Date and time of execution.
- Success or failure of each script.
- Error messages if any script fails.

You can use this log file to track the status of the process and troubleshoot any issues.

## Running the Script

To execute the entire sequence, run the following command in the terminal:

`python Run_Agent.py`

## Notes

- The script assumes that all necessary scripts (`Catalog_Agent.py`, `Feed_Agnent.py`, `Pattern_Mining_Agent.py`, `Correction_Agent.py`, `Pattern_Mining_Curated.py`) are located in the same directory or in the directories specified within the script.
- Modify the paths of the scripts if they are located elsewhere.
- Ensure the signal file (`signal_file.txt`) is generated and updated by the Streamlit app (`Feed_Agnent.py`).

## Troubleshooting

- If the Streamlit app doesn’t terminate or the signal file doesn’t update, check the Streamlit app for any issues with saving the changes.
- Review the `run_sequence.log` for specific error messages.
