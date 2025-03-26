import requests
from bs4 import BeautifulSoup
import re
import json

def fetch_xbrl(url, output_file):
    """
    Step 1: Fetch the iXBRL file from the SEC URL and save it locally.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyPythonBot/1.0; +mailto:vivake@einstream.ai)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an error for non-200 responses
        
        with open(output_file, "wb") as file:
            file.write(response.content)
        
        print(f"Downloaded XBRL file to {output_file}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching XBRL file: {e}")

def extract_hyperlinks(soup):
    """
    Extract hyperlinks and their content as key-value pairs from the given BeautifulSoup object.
    """
    anchor_tags = soup.find_all('a')
    
    hyperlinks = {}
    for tag in anchor_tags:
        href = tag.get('href')
        if href:
            hyperlinks[tag.text.strip()] = href
    
    return hyperlinks

def fetch_html_content(url):
    """
    Fetch the content of an HTML file from a given URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyPythonBot/1.0; +mailto:your_email@example.com)"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML content: {e}")
        return None

def extract_html_content(html_content):
    """
    Extract relevant content from the HTML file using BeautifulSoup.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract the text content of the HTML file
    return soup.get_text(separator='\n', strip=True)

def parse_xbrl(input_file, output_json, base_url):
    """
    Step 2: Parse the downloaded iXBRL file to extract key-value pairs.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        
        xbrl_data = {}  # Extracted key-value pairs
        # Find all tags with relevant namespaces or financial data
        for tag in soup.find_all(True):
            name = tag.get("name")
            tag_name = tag.name
            value = tag.text.strip()
            if (name and ("xbrl" in name.lower() or "us-gaap" in name.lower() or "ifrs" in name.lower() or "dei" in name.lower() or "srt" in name.lower() or "iso4217" in name.lower())) and value:
                key = name if name else tag_name
                xbrl_data[key] = value
            elif (tag_name and ("xbrl" in tag_name.lower() or "us-gaap" in tag_name.lower() or "ifrs" in tag_name.lower() or "dei" in tag_name.lower() or "srt" in tag_name.lower() or "iso4217" in tag_name.lower())) and value:
                key = name if name else tag_name
                xbrl_data[key] = value

        # Extract hyperlinks and add to xbrl_data
        hyperlinks = extract_hyperlinks(soup)
        xbrl_data.update(hyperlinks)

        # Extract additional key-value pairs based on headings
        additional_sections = {
            "Risk Factors": "Risk Factors",
            "Management's Discussion and Analysis (MD&A)": "Management's Discussion and Analysis",
            "Quantitative and Qualitative Disclosures About Market Risk": "Quantitative and Qualitative Disclosures About Market Risk",
            "Executive Compensation": "Executive Compensation",
            "Security Ownership of Certain Beneficial Owners and Management": "Security Ownership of Certain Beneficial Owners and Management",
            "Certain Relationships and Related Transactions": "Certain Relationships and Related Transactions",
            "Legal Proceedings": "Legal Proceedings",
            "Exhibits, Financial Statement Schedules": "Exhibits, Financial Statement Schedules"
        }

        for section, heading in additional_sections.items():
            element = soup.find(text=re.compile(heading, re.IGNORECASE))
            if element:
                parent = element.find_parent()
                if parent:
                    xbrl_data[section] = parent.text.strip()

        # Fetch and extract content from .htm files
        for key, value in xbrl_data.items():
            if value.endswith('.htm'):
                html_url = f"{base_url}/{value}"
                html_content = fetch_html_content(html_url)
                if html_content:
                    extracted_content = extract_html_content(html_content)
                    xbrl_data[key] = extracted_content
            elif value.startswith('#i'):
                full_url = f"{base_url}/{value}"
                xbrl_data[key] = full_url

        # Fetch and extract content for specific sections
        sections_to_fetch = {
            "Legal Proceedings": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000008/aapl-20241228.htm#i248a31500c42474f94fb8d3d2dd90051_160",
            "Part I": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_10",
            "Item 1.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_160",
            "Financial Statements": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_13",
            "Item 2.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_166",
            "Management’s Discussion and Analysis of Financial Condition and Results of Operations": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_70",
            "Item 3.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_169",
            "Item 4.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_172",
            "Part II": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_157",
            "Item 1 A.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_163",
            "Unregistered Sales of Equity Securities and Use of Proceeds": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_166",
            "Defaults Upon Senior Securities": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_169",
            "Mine Safety Disclosures": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_172",
            "Item 5.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_175",
            "Item 6.": f"{base_url}/#i248a31500c42474f94fb8d3d2dd90051_181"
        }

        for section, url in sections_to_fetch.items():
            content = fetch_html_content(url)
            if content:
                xbrl_data[section] = extract_html_content(content)

        # Save the extracted data to a JSON file
        with open(output_json, "w", encoding="utf-8") as json_file:
            json.dump(xbrl_data, json_file, indent=4)
        
        return xbrl_data
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def process_key(key):
    # Remove the text before the colon
    new_key = key.split(':')[-1]
    # Add spaces between words (convert camelCase or PascalCase to words)
    new_key = re.sub(r'(?<!^)(?=[A-Z])', ' ', new_key)
    return new_key

def clean_value(value):
    # Decode escape characters
    if isinstance(value, str):
        value = value.encode().decode('unicode_escape')
    return value

def clean_json(input_file, output_file):
    """
    Step 3: Clean the JSON file by removing the text before the colon in the key names,
    adding spaces between words in the key names, and resolving escape characters in the values.
    """
    try:
        # Load the JSON file
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Process the keys and values
        new_data = {}
        for key, value in data.items():
            new_key = process_key(key)
            new_value = clean_value(value)
            new_data[new_key] = new_value
        
        # Save the modified data back to a JSON file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(new_data, file, indent=4)
        
        print(f"Processed JSON saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """
    Main function orchestrating the process:
    1. Fetch the iXBRL file from the SEC.
    2. Parse the file to extract raw key-value pairs.
    3. Clean and filter the extracted data for relevant financial metrics.
    """
    # Define the SEC iXBRL filing URL
    xbrl_url = "https://www.sec.gov/Archives/edgar/data/0000320193/000032019325000008/aapl-20241228.htm"
    
    # Define file paths
    xbrl_file = "aapl_20241228.html"               # Downloaded iXBRL file
    raw_data_json = "apple_2024_xbrl_data.json"    # Raw extracted data in JSON format
    cleaned_data_json = "cleaned_apple_2024_xbrl_data.json"  # Cleaned data in JSON format
    
    # Fetch the XBRL document
    fetch_xbrl(xbrl_url, xbrl_file)  
    
    # Parse the iXBRL document
    base_url = "https://www.sec.gov/Archives/edgar/data/0000320193/000032019325000008"  # Base URL for .htm files
    xbrl_data = parse_xbrl(xbrl_file, raw_data_json, base_url)

    if xbrl_data:
        print("Financial data extracted and saved to JSON file successfully.")
        # Clean the JSON data
        clean_json(raw_data_json, cleaned_data_json)

if __name__ == "__main__":
    main()