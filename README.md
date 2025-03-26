# Sherlock - SEC iXBRL Data Extractor

Sherlock is a Python project designed to fetch, parse, and clean iXBRL (Inline eXtensible Business Reporting Language) data from the SEC (Securities and Exchange Commission) filings. The project extracts key financial metrics and other relevant information from the iXBRL files and saves the data in a structured JSON format.

## Features

- Fetch iXBRL files from the SEC website.
- Parse the iXBRL files to extract key-value pairs.
- Extract hyperlinks and their content.
- Fetch and extract content from linked HTML files.
- Clean and filter the extracted data for relevant financial metrics.
- Save the cleaned data in a JSON file.

## Requirements

- Python 3.6+

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/<your-username>/<repository-name>.git
    cd <repository-name>
    ```

2. Set up a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install requests beautifulsoup4 lxml
    ```

## Usage

1. Define the SEC iXBRL filing URL and file paths in the `main.py` file:

    ```python
    xbrl_url = "https://www.sec.gov/Archives/edgar/data/0000320193/000032019325000008/aapl-20241228.htm"
    xbrl_file = "aapl_20241228.html"
    raw_data_json = "apple_2024_xbrl_data.json"
    cleaned_data_json = "cleaned_apple_2024_xbrl_data.json"
    ```

2. Run the `main.py` script to fetch, parse, and clean the iXBRL data:

    ```bash
    python main.py
    ```

3. The extracted and cleaned data will be saved in the specified JSON files.

## Project Structure
