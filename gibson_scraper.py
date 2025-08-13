import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime 
import time
import re

def scrape_gc_r7():
    url = "https://www.guitarcenter.com/search?Ntt=gibson+les+paul+r7"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    print("Fetching Guitar Center page...")
    time.sleep(2)
    response = requests.get(url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Success! Page title:", soup.title.text if soup.title else "No title")
        return soup
    else:
        print(f"Failed to load page: {response.status_code}")
        return None

def parse_guitar_listings(soup):
    """Extract guitar listings from Guitar Center page"""
    listings = []
    
    # Look for product containers (try multiple selectors)
    product_containers = soup.find_all('div', class_=['product-tile', 'productTile', 'product-item'])
    
    if not product_containers:
        # Try alternative selectors
        product_containers = soup.find_all('div', attrs={'data-testid': 'product-tile'})
    
    print(f"\n🎸 Parsing {len(product_containers)} product containers...")
    
    for i, container in enumerate(product_containers):
        try:
            listing = extract_guitar_info(container)
            if listing:
                listings.append(listing)
                print(f"  ✅ Parsed guitar {i+1}: {listing.get('title', 'Unknown')[:50]}...")
        except Exception as e:
            print(f"  ❌ Error parsing container {i+1}: {e}")
    
    return listings

def extract_guitar_info(container):
    """Extract information from a single product container"""
    guitar = {}
    
    # Extract title/name
    title_selectors = [
        'h3',
        '.product-title',
        '.productTile-title', 
        'a[data-testid="product-tile-title"]',
        '.product-name'
    ]
    
    title_elem = None
    for selector in title_selectors:
        title_elem = container.select_one(selector)
        if title_elem:
            break
    
    if title_elem:
        guitar['title'] = title_elem.get_text().strip()
    
    # Extract price
    price_selectors = [
        '.price',
        '.product-price',
        '.productTile-price',
        '[data-testid="price"]',
        '.sale-price'
    ]
    
    price_elem = None
    for selector in price_selectors:
        price_elem = container.select_one(selector)
        if price_elem:
            break
    
    # Also look for any text with $ in this container
    if not price_elem:
        price_texts = container.find_all(string=lambda text: text and '$' in text and len(text.strip()) < 20)
        if price_texts:
            price_elem = price_texts[0]
    
    if price_elem:
        price_text = price_elem.get_text() if hasattr(price_elem, 'get_text') else str(price_elem)
        guitar['price'] = clean_price(price_text)
        guitar['price_raw'] = price_text.strip()
    
    # Extract product URL
    link_elem = container.find('a', href=True)
    if link_elem:
        href = link_elem.get('href')
        if href:
            # Make it a full URL if it's relative
            if href.startswith('/'):
                href = 'https://www.guitarcenter.com' + href
            guitar['url'] = href
    
    # Look for condition/availability
    condition_keywords = ['new', 'used', 'open box', 'in stock', 'out of stock']
    all_text = container.get_text().lower()
    for keyword in condition_keywords:
        if keyword in all_text:
            guitar['condition'] = keyword.title()
            break
    
    # Extract year from title if present
    if 'title' in guitar:
        year = extract_year_from_title(guitar['title'])
        if year:
            guitar['year'] = year
    
    # Add timestamp
    guitar['scraped_at'] = datetime.now().isoformat()
    
    # Only return if we found at least a title or price
    return guitar if ('title' in guitar or 'price' in guitar) else None

def clean_price(price_text):
    """Clean price text and convert to float"""
    if not price_text:
        return None
    
    # Remove everything except digits, decimal points, and commas
    price_clean = re.sub(r'[^\d.,]', '', str(price_text))
    
    # Remove commas
    price_clean = price_clean.replace(',', '')
    
    try:
        return float(price_clean) if price_clean else None
    except ValueError:
        return None

def extract_year_from_title(title):
    """Extract year from guitar title"""
    # Look for 4-digit years (1950-2030)
    years = re.findall(r'\b(19[5-9]\d|20[0-3]\d)\b', title)
    return years[0] if years else None

def save_listings(listings):
    """Save listings to CSV and JSON"""
    if not listings:
        print("❌ No listings to save")
        return
    
    # Create DataFrame
    df = pd.DataFrame(listings)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"guitar_center_r7_{timestamp}.csv"
    
    # Save to CSV
    df.to_csv(csv_file, index=False)
    print(f"💾 Saved {len(listings)} listings to {csv_file}")
    
    # Print summary
    if 'price' in df.columns:
        prices = df['price'].dropna()
        if len(prices) > 0:
            print(f"\n📊 Price Summary:")
            print(f"  Average: ${prices.mean():,.2f}")
            print(f"  Range: ${prices.min():,.2f} - ${prices.max():,.2f}")
            print(f"  Total guitars found: {len(listings)}")
    
    # Show sample listings
    print(f"\n🎸 Sample listings:")
    for i, listing in enumerate(listings[:3]):
        title = listing.get('title', 'No title')[:50]
        price = f"${listing['price']:,.2f}" if listing.get('price') else 'No price'
        print(f"  {i+1}. {title}... - {price}")
    
    return csv_file

if __name__ == "__main__":
    print("🎸 Guitar Center R7 Tracker Starting...")
    
    soup = scrape_gc_r7()
    if soup:
        listings = parse_guitar_listings(soup)
        save_listings(listings)
    else:
        print("❌ Failed to get page data")
