import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def scrape_reverb_r7():
    url = "https://reverb.com/marketplace?query=gibson+les+paul+r7"
    
    # More realistic headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print("Fetching Reverb page...")
    
    # Add a delay to be respectful
    time.sleep(2)
    
    response = requests.get(url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Success! Page title:", soup.title.text if soup.title else "No title")
        return soup
    else:
        print("Still blocked. Let's try a different approach.")
        return None

if __name__ == "__main__":
    soup = scrape_reverb_r7()
