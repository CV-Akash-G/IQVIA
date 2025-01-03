# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# # Set up Chrome options to disable SSL verification
# chrome_options = Options()
# chrome_options.add_argument("--ignore-certificate-errors")
# chrome_options.add_argument("--incognito")

# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # File to store the output
# output_file = "out.txt"

# # URL of the webpage
# url = "https://www.drugs.com/alpha/u.html"

# # Fetch the page content
# response = requests.get(url)
# if response.status_code == 200:
#     # Parse the page with BeautifulSoup
#     soup = BeautifulSoup(response.content, "html.parser")

#     # Find the list containing the links
#     ul_element = soup.find("ul", class_="ddc-list-column-2")
#     if ul_element:
#         # Extract all <a> tags within the <ul>
#         links = ul_element.find_all("a")

#         # Open the file in write mode
#         with open(output_file, "w") as file:
#             # Write each link to the file
#             for link in links:
#                 href = link.get("href")
#                 full_url = f"https://www.drugs.com{href}"
#                 file.write(full_url + "\n")  # Write URL followed by a newline
#         print(f"Links have been saved to {output_file}")
#     else:
#         print("The specified <ul> element was not found.")
# else:
#     print(f"Failed to fetch the webpage. Status code: {response.status_code}")


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL of the website
base_url = "https://www.drugs.com/drug_information.html"

# Function to extract URLs from a given page and return full URLs
def extract_urls(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract main navigation links
    nav_links = []
    nav_section = soup.find('nav', class_='ddc-paging')
    if nav_section:
        links = nav_section.find_all('a', class_='ddc-paging-item')
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                nav_links.append(full_url)
    return nav_links

# Function to extract subsequent URLs from the second-level navigation
def extract_sub_urls(main_urls):
    all_sub_urls = []
    for url in main_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find secondary navigation links
        sub_section = soup.find('nav', class_='ddc-paging ddc-mgb-2')
        if sub_section:
            sub_links = sub_section.find_all('a', class_='ddc-paging-item')
            for link in sub_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    all_sub_urls.append(full_url)
    return all_sub_urls

# Step 1: Extract main URLs
main_urls = extract_urls(base_url)

# Step 2: Extract secondary URLs
sub_urls = extract_sub_urls(main_urls)

# Save the results to a file
with open("Input_URLS.txt", "w") as file:
    file.write("")
    for url in main_urls:
        file.write(url + "\n")
    
    file.write("")
    for url in sub_urls:
        file.write(url + "\n")

print("Links have been saved to output_links.txt.")




