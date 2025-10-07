import sys
import os
from pathlib import Path

# Add parent directory to path to allow importing app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.finance import get_recent_prices

def test_get_recent_prices():
    """Test that get_recent_prices returns correctly formatted price data."""
    # Test with a well-known stock symbol
    symbol = "AAPL"
    prices = get_recent_prices(symbol)
    
    # Check that we got results
    print(f"Retrieved {len(prices)} days of price data for {symbol}")
    
    # Display the first 5 entries (if available)
    for i, price in enumerate(prices[:-5]):
        print(f"Entry {i+1}: {price}")
    
    # Verify format of entries
    if prices:
        for price in prices:
            # Check that each entry contains date and closing_price
            assert '"date":' in price, f"Missing date in: {price}"
            assert '"closing_price":' in price, f"Missing closing_price in: {price}"
            
        print("✓ All entries have the correct format")
    else:
        print("No price data was retrieved. Check your internet connection or the symbol.")

if __name__ == "__main__":
    test_get_recent_prices()
