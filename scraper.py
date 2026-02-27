cat > ~/mini_bank/scraper.py << 'ENDOFFILE'
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os
import threading

# =========================
# CONFIG
# =========================
BASE_URL = "https://www.ptindirectory.com"

STATES = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
    "District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
    "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota",
    "Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
    "New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
    "Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
    "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}
CSV_FILE = "all_states_tax_preparers.csv"
csv_lock = threading.Lock()

def save_csv(row):
    with csv_lock:
        df = pd.DataFrame([row])
        if os.path.exists(CSV_FILE):
            df.to_csv(CSV_FILE, mode="a", index=False, header=False, encoding="utf-8")
        else:
            df.to_csv(CSV_FILE, index=False, encoding="utf-8")
        print(f"Saved: {row['Profile_URL']}")

def scrape_profile(profile_url):
    try:
        resp = requests.get(profile_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        name_tag = soup.select_one("h4 span[itemprop='name']")
        name = name_tag.get_text(strip=True) if name_tag else ""
        owner = ""
        address = ""
        addr_tag = soup.select_one("span[itemprop='address']")
        if addr_tag:
            lines = [x.strip() for x in addr_tag.stripped_strings if x.strip()]
            if lines:
                owner = lines[0]
                if len(lines) > 1:
                    address = ", ".join(lines[1:])
        phone_tag = soup.select_one("span[itemprop='telephone']")
        phone = phone_tag.get_text(strip=True) if phone_tag else "empty"
        website = "empty"
        website_tag = soup.find("a", class_="btn btn-primary", string=lambda x: x and "Visit Website" in x)
        if website_tag:
            href = website_tag.get("href", "").strip()
            if href.startswith("http") and "ptindirectory.com" not in href and "write-client-review" not in href:
                website = href
        row = {"Profile_URL": profile_url, "Name": name, "Ownership": owner, "Address": address, "Phone": phone, "Website": website}
        save_csv(row)
    except Exception as e:
        print(f"Profile error: {profile_url} | {e}")

def scrape_city(city_url):
    try:
        city_resp = requests.get(city_url, headers=HEADERS, timeout=15)
        city_soup = BeautifulSoup(city_resp.text, "html.parser")
        profile_links = city_soup.select("div.col-sm-6.col-md-3 a[href]")
        for a in profile_links:
            profile_url = BASE_URL + a["href"]
            scrape_profile(profile_url)
            time.sleep(0.2)
    except Exception as e:
        print(f"City error: {city_url} | {e}")

def scrape_state(state):
    print(f"State: {state}")
    state_slug = state.lower().replace(" ", "-")
    state_url = f"{BASE_URL}/tax-preparers/{state_slug}"
    try:
        resp = requests.get(state_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        city_urls = []
        for a in soup.select(f"a[href^='/tax-preparers/{state_slug}/']"):
            text = a.get_text(strip=True)
            if re.search(r"\(\d+\)", text):
                city_urls.append(BASE_URL + a["href"])
        city_urls = list(dict.fromkeys(city_urls))
        print(f"Cities found: {len(city_urls)}")
        for city_url in city_urls:
            scrape_city(city_url)
            time.sleep(0.5)
    except Exception as e:
        print(f"State error: {state} | {e}")

if __name__ == "__main__":
    start = time.time()
    for state in STATES:
        scrape_state(state)
    total = (time.time() - start) / 60
    print(f"DONE | CSV: {CSV_FILE} | Time: {total:.2f} minutes")
ENDOFFILE

cd ~/mini_bank
git add scraper.py
git commit -m "Add US tax preparers scraper"
git push origin main