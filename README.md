# US Tax Preparers Scraper

A web scraper to extract tax preparer data from all 50 US states from ptindirectory.com.

## Features
- Scrapes all 50 US States
- Extracts Name, Ownership, Address, Phone, Website
- Saves data to CSV file
- Multi-threading support

## Tech Stack
- Python
- BeautifulSoup
- Requests
- Pandas

## Setup
```bash
pip install requests beautifulsoup4 pandas
```

## Run
```bash
python scraper.py
```

## Output
CSV file: `all_states_tax_preparers.csv`

## CSV Columns
- Profile_URL
- Name
- Ownership
- Address
- Phone
- Website
