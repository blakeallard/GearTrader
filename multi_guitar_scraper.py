import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
import os

class MultiGuitarTracker:
    def __init__(self):
        self.base_url = "https://www.guitarcenter.com/search?Ntt="
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # =============================================================================
        # Guitar Models Configuration
        # =============================================================================
        self.guitar_models = {
            'gibson_r7': 'gibson+les+paul+r7',
            'gibson_r8': 'gibson+les+paul+r8', 
            'gibson_r9': 'gibson+les+paul+r9',
            'gibson_standard': 'gibson+les+paul+standard',
            'gibson_studio': 'gibson+les+paul+studio',
            'fender_strat': 'fender+stratocaster+american',
            'fender_tele': 'fender+telecaster+american',
            'prs_custom': 'prs+custom+24'
        }
        
        # =============================================================================
        # Data Storage Setup
        # =============================================================================
        if not os.path.exists('guitar_data'):
            os.makedirs('guitar_data')
    
    # =============================================================================
    # Web Scraping Methods
    # =============================================================================
    
    def scrape_guitar_model(self, model_name, search_query):
        """
        Scrape guitar listings for a specific model
        
        Args:
            model_name (str): Name of the guitar model category
            search_query (str): URL-encoded search query
            
        Returns:
            list: List of guitar dictionaries with pricing data
        """
        url = self.base_url + search_query
        
        try:
            print(f"Scraping {model_name}...")
            time.sleep(3)  # Rate limiting for server respect
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Failed to get {model_name}: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = self.parse_guitar_listings(soup, model_name)
            
            print(f"Found {len(listings)} {model_name} guitars")
            return listings
            
        except Exception as e:
            print(f"Error scraping {model_name}: {e}")
            return []
    
    def parse_guitar_listings(self, soup, model_name):
        """
        Extract guitar listings from BeautifulSoup parsed HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            model_name (str): Guitar model category
            
        Returns:
            list: Extracted guitar listing data
        """
        listings = []
        product_containers = soup.find_all('div', class_=['product-tile', 'productTile', 'product-item'])
        
        for container in product_containers:
            try:
                listing = self.extract_guitar_info(container, model_name)
                if listing:
                    listings.append(listing)
            except Exception as e:
                continue  # Skip problematic listings
        
        return listings
    
    def extract_guitar_info(self, container, model_name):
        """
        Extract detailed information from individual guitar listing container
        
        Args:
            container (BeautifulSoup element): HTML container for single guitar
            model_name (str): Guitar model category
            
        Returns:
            dict: Guitar information dictionary or None if extraction fails
        """
        guitar = {'model_category': model_name}
        
        # =============================================================================
        # Title Extraction - Updated to match Guitar Center structure
        # =============================================================================
        title_selectors = ['h1', 'h2', 'h3', 'h4', 'h5']
        
        for selector in title_selectors:
            title_elem = container.find(selector)
            if title_elem:
                guitar['title'] = title_elem.get_text().strip()
                break
        
        # =============================================================================
        # Price Extraction - Look for $ in text nodes
        # =============================================================================
        price_texts = container.find_all(string=lambda text: text and '$' in text and '/' not in text)
        if price_texts:
            for price_text in price_texts:
                price = self.clean_price(price_text)
                if price and price > 100:  # Reasonable guitar price filter
                    guitar['price'] = price
                    guitar['price_raw'] = price_text.strip()
                    break
        
        # =============================================================================
        # URL Extraction
        # =============================================================================
        link_elem = container.find('a', href=True)
        if link_elem:
            href = link_elem.get('href')
            if href and href.startswith('/'):
                guitar['url'] = 'https://www.guitarcenter.com' + href
        
        # =============================================================================
        # Year Extraction from Title
        # =============================================================================
        if 'title' in guitar:
            year = self.extract_year_from_title(guitar['title'])
            if year:
                guitar['year'] = year
        
        # =============================================================================
        # Metadata Addition
        # =============================================================================
        guitar['scraped_at'] = datetime.now().isoformat()
        guitar['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
        guitar['scrape_time'] = datetime.now().strftime('%H:%M:%S')
        
        # Return guitar data only if both title and price were successfully extracted
        return guitar if ('title' in guitar and 'price' in guitar) else None
    # =============================================================================
    # Data Processing Utilities
    # =============================================================================
    
    def clean_price(self, price_text):
        """
        Clean and convert price text to numeric value
        
        Args:
            price_text (str): Raw price text from webpage
            
        Returns:
            float: Cleaned price value or None if conversion fails
        """
        if not price_text:
            return None
        
        # Remove all non-digit characters except decimal points and commas
        price_clean = re.sub(r'[^\d.,]', '', str(price_text))
        price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean) if price_clean else None
        except ValueError:
            return None
    
    def extract_year_from_title(self, title):
        """
        Extract manufacturing year from guitar title using regex
        
        Args:
            title (str): Guitar title text
            
        Returns:
            str: Extracted year or None if no year found
        """
        years = re.findall(r'\b(19[5-9]\d|20[0-3]\d)\b', title)
        return years[0] if years else None
    
    # =============================================================================
    # Main Scraping Orchestration
    # =============================================================================
    
    def scrape_all_models(self):
        """
        Execute scraping for all configured guitar models
        
        Returns:
            list: Combined list of all guitar data across models
        """
        print("Starting Multi-Model Guitar Tracking...")
        print("=" * 60)
        
        all_guitars = []
        model_counts = {}
        
        # Iterate through each guitar model configuration
        for model_name, search_query in self.guitar_models.items():
            guitars = self.scrape_guitar_model(model_name, search_query)
            all_guitars.extend(guitars)
            model_counts[model_name] = len(guitars)
            
            # Save individual model data files
            if guitars:
                self.save_model_data(guitars, model_name)
        
        # Process and save combined dataset
        if all_guitars:
            self.save_combined_data(all_guitars)
            self.print_summary(model_counts, all_guitars)
        
        return all_guitars
    
    # =============================================================================
    # Data Storage Methods
    # =============================================================================
    
    def save_model_data(self, guitars, model_name):
        """
        Save individual model data to timestamped CSV file
        
        Args:
            guitars (list): Guitar data for specific model
            model_name (str): Model category name for filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"guitar_data/{model_name}_{timestamp}.csv"
        
        df = pd.DataFrame(guitars)
        df.to_csv(filename, index=False)
        print(f"Saved {model_name} data: {filename}")
    
    def save_combined_data(self, all_guitars):
        """
        Save combined data from all models and update historical master file
        
        Args:
            all_guitars (list): Complete dataset across all models
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"guitar_data/all_guitars_{timestamp}.csv"
        
        df = pd.DataFrame(all_guitars)
        df.to_csv(filename, index=False)
        
        # =============================================================================
        # Historical Data Management
        # =============================================================================
        master_file = "guitar_data/guitar_price_history.csv"
        if os.path.exists(master_file):
            df_master = pd.read_csv(master_file)
            df_combined = pd.concat([df_master, df], ignore_index=True)
            df_combined.to_csv(master_file, index=False)
        else:
            df.to_csv(master_file, index=False)
        
        print(f"Saved combined data: {filename}")
        print(f"Updated master history: {master_file}")
    
    # =============================================================================
    # Analysis and Reporting Methods
    # =============================================================================
    
    def print_summary(self, model_counts, all_guitars):
        """
        Generate and display comprehensive scraping summary
        
        Args:
            model_counts (dict): Count of guitars found per model
            all_guitars (list): Complete guitar dataset
        """
        print("\nSCRAPING SUMMARY")
        print("=" * 50)
        
        # =============================================================================
        # Model Breakdown Analysis
        # =============================================================================
        for model, count in model_counts.items():
            print(f"  {model:20}: {count:3} guitars")
        
        total_guitars = len(all_guitars)
        print(f"\nTotal guitars found: {total_guitars}")
        
        # =============================================================================
        # Price Analysis
        # =============================================================================
        prices = [g['price'] for g in all_guitars if g.get('price')]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            print(f"Price Analysis:")
            print(f"  Average: ${avg_price:,.2f}")
            print(f"  Range: ${min_price:,.2f} - ${max_price:,.2f}")
        
        # =============================================================================
        # Best Deals by Category
        # =============================================================================
        print(f"\nCheapest in Each Category:")
        models = set(g['model_category'] for g in all_guitars)
        
        for model in models:
            model_guitars = [g for g in all_guitars if g['model_category'] == model and g.get('price')]
            if model_guitars:
                cheapest = min(model_guitars, key=lambda x: x['price'])
                print(f"  {model:20}: ${cheapest['price']:,.2f}")
    
    def analyze_market_trends(self):
        """
        Analyze price trends using historical data if available
        """
        master_file = "guitar_data/guitar_price_history.csv"
        
        if not os.path.exists(master_file):
            print("No historical data yet - run scraper multiple times to see trends!")
            return
        
        df = pd.read_csv(master_file)
        
        print("\nMARKET TRENDS ANALYSIS")
        print("=" * 50)
        
        # =============================================================================
        # Trend Analysis by Model
        # =============================================================================
        df['scrape_date'] = pd.to_datetime(df['scrape_date'])
        
        for model in df['model_category'].unique():
            model_data = df[df['model_category'] == model]
            
            if len(model_data) > 1:
                # Calculate average price by date
                daily_avg = model_data.groupby('scrape_date')['price'].mean()
                
                if len(daily_avg) > 1:
                    trend = "Rising" if daily_avg.iloc[-1] > daily_avg.iloc[0] else "Falling"
                    print(f"  {model:20}: {trend}")

# =============================================================================
# Main Execution Block
# =============================================================================

if __name__ == "__main__":
    tracker = MultiGuitarTracker()
    
    print("GearTrader Multi-Model Tracker")
    print("Tracking: Gibson R7/R8/R9, Standards, Studios, Fender Strats/Teles, PRS Custom")
    print()
    
    # Execute full scraping workflow
    guitars = tracker.scrape_all_models()
    
    # Perform trend analysis if historical data exists
    tracker.analyze_market_trends()
    
    print("\nMulti-model tracking complete!")
    print("Run this daily to build price history and trend analysis!")