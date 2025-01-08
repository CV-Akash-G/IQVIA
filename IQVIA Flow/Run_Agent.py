import subprocess
import time
import os
import logging

# Set up logging configuration
logging.basicConfig(
    filename="run_sequence.log",  # Log file location
    level=logging.INFO,  # Log level (INFO, DEBUG, ERROR, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
)

logging.info("Script execution started.")

# Step 1: Run the metadata collection script
logging.info("Running metadata collection script (IQ_Agent.py)...")
try:
    subprocess.run(["python", "Catalog_Agent.py"], check=True)
    logging.info("Metadata collection script completed successfully.")
except subprocess.CalledProcessError as e:
    logging.error(f"Error running metadata collection script: {e}")
    raise

# Step 2: Run the Streamlit app (Rules_Feed_Agnent.py)
logging.info("Running Streamlit app (Rules_Feed_Agnent.py)...")
streamlit_process = subprocess.Popen(["streamlit", "run", "Feed_Agnent.py"])

# Step 3: Monitor the signal file to check if the changes were saved in the Streamlit app
signal_file_path = "signal_file.txt"
logging.info(
    f"Waiting for the signal file '{signal_file_path}' to indicate changes have been saved..."
)

while True:
    if os.path.exists(signal_file_path):
        with open(signal_file_path, "r") as f:
            content = f.read().strip()
            if content == "changes_saved":
                logging.info("Changes saved successfully in Streamlit app.")
                break
    time.sleep(15)  # Check every second

# Step 4: Stop the Streamlit process after changes are saved
logging.info("Terminating the Streamlit app...")
streamlit_process.terminate()

# Step 5: Clear the content of the signal file after terminating the Streamlit process
if os.path.exists(signal_file_path):
    with open(signal_file_path, "w") as f:
        f.write("")  # Clear the file content
    logging.info("Signal file content cleared.")

# Step 6: Run the next Python scripts after Streamlit app is terminated
logging.info("Running reports generation script (reports_generation.py)...")
try:
    subprocess.run(["python", "Pattern_Mining_Agent.py"], check=True)
    logging.info("Reports generation script completed successfully.")
except subprocess.CalledProcessError as e:
    logging.error(f"Error running reports generation script: {e}")
    raise

# Step 7: Run the final script (Correction_Agent.py)
logging.info("Running text correction script (Correction_Agent.py)...")
try:
    subprocess.run(["python", "Repair_Agent.py"], check=True)
    logging.info("Text correction script completed successfully.")
except subprocess.CalledProcessError as e:
    logging.error(f"Error running text correction script: {e}")
    raise

logging.info("All steps completed successfully.")


# Step 8: Run the next Python scripts after Streamlit app is terminated
logging.info("Running reports generation script (Curated_Reports_Generation.py)...")
try:
    subprocess.run(["python", "Pattern_Mining_Curated.py"], check=True)
    logging.info("Reports generation script completed successfully.")
except subprocess.CalledProcessError as e:
    logging.error(f"Error running reports generation script: {e}")
    raise
