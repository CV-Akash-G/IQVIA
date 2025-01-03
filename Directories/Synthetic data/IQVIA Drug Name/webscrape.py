# import json
# import os
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

# # Set up Chrome options to disable SSL verification
# chrome_options = Options()
# chrome_options.add_argument("--ignore-certificate-errors")
# chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-javascript")

# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)
# driver.set_page_load_timeout(20)

# # File containing the URLs
# input_file = "out.txt"

# # File to store the output
# output_file = "drug_details_01.json"

# # List of URLs to scrape
# urls = []

# # Read the URLs from the file
# try:
#     with open(input_file, "r") as file:
#         for line in file:
#             urls.append(line.strip())  # Strip newline characters and add to list
# except FileNotFoundError:
#     print(f"Error: The file {input_file} was not found.")
#     driver.quit()
#     exit()
# except Exception as e:
#     print(f"An error occurred while reading the file: {e}")
#     driver.quit()
#     exit()


# # Function to extract drug details from the page
# def extract_drug_details(url):
#     driver.get(url)

#     # Wait for the page to load
#     wait = WebDriverWait(driver, 10)

#     try:
#         # Wait for the drug name (h1 tag)
#         drug_name_element = wait.until(
#             EC.presence_of_element_located((By.TAG_NAME, "h1"))
#         )
#         drug_name = drug_name_element.text
#     except Exception as e:
#         print(f"Error while fetching drug name from {url}: {e}")
#         drug_name = None

#     # Extract the Generic name and Drug class from the <p class="drug-subtitle">
#     try:
#         drug_subtitle_element = wait.until(
#             EC.presence_of_element_located((By.CLASS_NAME, "drug-subtitle"))
#         )
#         # Extract Generic name
#         generic_name_element = drug_subtitle_element.find_element(
#             By.XPATH, ".//b[text()='Generic name:']/following-sibling::a"
#         )
#         generic_name = generic_name_element.text if generic_name_element else None

#         # Extract Drug class
#         drug_class_element = drug_subtitle_element.find_element(
#             By.XPATH, ".//b[text()='Drug class:']/following-sibling::a"
#         )
#         drug_class = drug_class_element.text if drug_class_element else None
#     except Exception as e:
#         print(f"Error while fetching drug details from {url}: {e}")
#         generic_name, drug_class = None, None

#     # Return the results for this drug
#     return {
#         "Drug Name": drug_name,
#         "Generic Name": generic_name,
#         "Drug Class": drug_class,
#     }


# # Load existing data from the JSON file, if it exists
# existing_data = []
# if os.path.exists(output_file):
#     try:
#         with open(output_file, "r", encoding="utf-8") as json_file:
#             existing_data = json.load(json_file)
#     except json.JSONDecodeError:
#         print(
#             f"Warning: The file '{output_file}' is not a valid JSON file. Starting fresh."
#         )
#     except Exception as e:
#         print(f"An error occurred while reading '{output_file}': {e}")

# # List to store the details of all drugs
# all_drug_details = existing_data  # Start with existing data

# # Loop through each URL and extract drug details
# for url in urls:
#     print(f"Processing {url}...")
#     drug_details = extract_drug_details(url)
#     all_drug_details.append(drug_details)

# # Save the results to the JSON file (append new data)
# try:
#     with open(output_file, "w", encoding="utf-8") as json_file:
#         json.dump(all_drug_details, json_file, ensure_ascii=False, indent=4)
#     print(f"Scraping complete! The drug details have been saved to '{output_file}'.")
# except Exception as e:
#     print(f"An error occurred while saving data to '{output_file}': {e}")

# # Close the browser window
# driver.quit()




import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options to disable SSL verification
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-javascript")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(20)

# File containing the URLs
input_file = "output_0.1.txt"

# File to store the output
output_file = "drug_details_01.json"

# List of URLs to scrape
urls = []

# Read the URLs from the file
try:
    with open(input_file, "r") as file:
        for line in file:
            urls.append(line.strip())  # Strip newline characters and add to list
except FileNotFoundError:
    print(f"Error: The file {input_file} was not found.")
    driver.quit()
    exit()
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    driver.quit()
    exit()

# Function to extract drug details from the page
def extract_drug_details(url):
    try:
        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 10)

        # Fetch drug name
        try:
            drug_name_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            drug_name = drug_name_element.text
        except Exception:
            drug_name = None

        # Fetch generic name and drug class
        try:
            drug_subtitle_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "drug-subtitle")))

            # Extract Generic name
            try:
                generic_name_element = drug_subtitle_element.find_element(By.XPATH, ".//b[text()='Generic name:']/following-sibling::a")
                generic_name = generic_name_element.text
            except Exception:
                generic_name = None

            # Extract Drug class
            try:
                drug_class_element = drug_subtitle_element.find_element(By.XPATH, ".//b[text()='Drug class:']/following-sibling::a")
                drug_class = drug_class_element.text
            except Exception:
                drug_class = None
        except Exception:
            generic_name, drug_class = None, None

        return {
            "Drug Name": drug_name,
            "Generic Name": generic_name,
            "Drug Class": drug_class,
        }
    except Exception as e:
        print(f"Error while processing {url}: {e}")
        return None

# Batch processing setup
batch_size = 10  # Save every 10 URLs
batch = []

# Load existing data from JSON if available
existing_data = []
if os.path.exists(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as json_file:
            existing_data = json.load(json_file)
    except json.JSONDecodeError:
        print(f"Warning: '{output_file}' is not a valid JSON file. Starting fresh.")
    except Exception as e:
        print(f"An error occurred while reading '{output_file}': {e}")

# Start with existing data
all_drug_details = existing_data

# Process each URL
for i, url in enumerate(urls):
    print(f"Processing URL {i + 1}/{len(urls)}: {url}")
    drug_details = extract_drug_details(url)
    if drug_details:  # Only add valid results
        batch.append(drug_details)

    # Save batch to file
    if len(batch) >= batch_size or i == len(urls) - 1:  # Save if batch is full or it's the last URL
        all_drug_details.extend(batch)
        try:
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(all_drug_details, json_file, ensure_ascii=False, indent=4)
            print(f"Batch of {len(batch)} items saved to '{output_file}'.")
        except Exception as e:
            print(f"Error while saving batch to '{output_file}': {e}")
        batch = []  # Reset batch after saving

# Close the browser
driver.quit()
print("Scraping complete. All data saved.")
