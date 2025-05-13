import pandas as pd
import requests
from io import StringIO
import urllib3
import warnings
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_sp500_tickers():
    """
    Scrape Wikipedia to get the current list of S&P 500 tickers.
    Returns:
        tickers (list): List of ticker symbols.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    try:
        # Use requests with SSL verification disabled
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Use StringIO to handle the HTML content properly
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        
        # Clean up ticker symbols
        tickers = df['Symbol'].tolist()
        # Some tickers have dots (e.g., BRK.B) which yfinance expects as '-', so convert
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        
        print(f"Successfully retrieved {len(tickers)} S&P 500 tickers")
        csv_dir = os.path.join(os.path.dirname(__file__), 'csv')
        os.makedirs(csv_dir, exist_ok=True)
        pd.Series(tickers).to_csv(os.path.join(csv_dir, 'sp500_tickers.csv'), index=False)
        print("[DEBUG] get_sp500_tickers: List saved to csv/sp500_tickers.csv")
        return tickers
        
    except Exception as e:
        print(f"Error fetching S&P 500 components: {str(e)}")
        # Return a small list of major tickers as fallback
        fallback_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        print(f"Using fallback tickers: {fallback_tickers}")
        pd.Series(fallback_tickers).to_csv('csv/sp500_tickers.csv', index=False)
        print("[DEBUG] get_sp500_tickers: Fallback list saved to csv/sp500_tickers.csv")
        return fallback_tickers