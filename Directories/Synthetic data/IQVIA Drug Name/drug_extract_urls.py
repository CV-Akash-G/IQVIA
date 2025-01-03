import requests
from bs4 import BeautifulSoup

# Input file containing URLs
input_file = "output_links.txt"

# Output file to store the extracted links
output_file = "output_0.1.txt"

# Function to process a single URL and extract links
def process_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the list containing the links
            ul_element = soup.find("ul", class_="ddc-list-column-2")
            if ul_element:
                # Extract all <a> tags within the <ul>
                links = ul_element.find_all("a")
                return [f"https://www.drugs.com{link.get('href')}" for link in links if link.get("href")]
            else:
                print(f"The specified <ul> element was not found for {url}.")
        else:
            print(f"Failed to fetch the webpage {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    return []

# Main script
try:
    # Open the input file and read URLs
    with open(input_file, "r") as infile:
        urls = [line.strip() for line in infile if line.strip()]  # Strip whitespace and ignore empty lines

    all_links = []
    for url in urls:
        print(f"Processing {url}...")
        links = process_url(url)
        all_links.extend(links)

    # Save all extracted links to the output file
    with open(output_file, "w") as outfile:
        for link in all_links:
            outfile.write(link + "\n")
    
    print(f"All extracted links have been saved to {output_file}.")
except FileNotFoundError:
    print(f"Error: The file {input_file} was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
