# import pandas as pd
# import random
# from datetime import datetime, timedelta


# # Function to generate a random date
# def generate_random_date(start_year=2010, end_year=2023):
#     start_date = datetime(start_year, 1, 1)
#     end_date = datetime(end_year, 12, 31)
#     delta = end_date - start_date
#     random_days = random.randint(0, delta.days)
#     random_date = start_date + timedelta(days=random_days)
#     return random_date.strftime("%m/%d/%Y")  # US Date Format (MM/DD/YYYY)


# # Load the CSV file into a pandas DataFrame
# df = pd.read_csv("synthetic_pharmacy_data_v1_cleaned.csv")

# # Replace null or empty values in 'Encounter_Date' with random dates
# df["Encounter_Date"] = df["Encounter_Date"].apply(
#     lambda x: generate_random_date() if pd.isnull(x) or x == "" else x
# )

# # Save the modified DataFrame back to a CSV file (if needed)
# df.to_csv("synthetic_pharmacy_data_v1_cleaned_updated.csv", index=False)

# print("Null values in 'Encounter_Date' have been replaced with random US dates.")




