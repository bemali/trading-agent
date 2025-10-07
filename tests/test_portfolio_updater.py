"""
Test script for the portfolio updater functionality.
"""

import os
import time
from pathlib import Path
import json
import sys

# Ensure the app module is in the path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.src.portfolio_updater import update_portfolio_with_fallbacks, update_portfolio_in_background
from app.utils.storage import user_dir, read_json

def test_update_functionality():
    """Test the portfolio updater functionality."""
    print("Testing portfolio updater functionality...")
    
    # Select a test user
    username = "testuser"
    
    # Create a test portfolio if it doesn't exist
    portfolio_path = user_dir(username) / "portfolio.json"
    
    if not portfolio_path.exists():
        print(f"Creating test portfolio for {username}...")
        test_portfolio = [
            {
                "company_name": "Apple Inc.",
                "stock_code": "AAPL",
                "quantity": 10,
                "purchase_price": 150.00
            },
            {
                "company_name": "Microsoft Corporation",
                "stock_code": "MSFT",
                "quantity": 5,
                "purchase_price": 300.00
            },
            {
                "company_name": "Made Up Company",
                "stock_code": "FAKE",  # This should trigger fallback logic
                "quantity": 20,
                "purchase_price": 50.00
            }
        ]
        
        # Write test portfolio
        with portfolio_path.open('w', encoding='utf-8') as f:
            json.dump(test_portfolio, f, indent=2, ensure_ascii=False)
        
        print("Test portfolio created.")
    else:
        print("Using existing test portfolio.")
    
    # Test direct update function
    print("\nTesting direct update function:")
    success = update_portfolio_with_fallbacks(username)
    if success:
        print("Direct update succeeded.")
    else:
        print("Direct update failed.")
    
    # Display updated portfolio
    portfolio = read_json(portfolio_path)
    if portfolio:
        print("\nUpdated portfolio:")
        for stock in portfolio:
            symbol = stock.get('stock_code', 'Unknown')
            price = stock.get('current_price', 'N/A')
            value = stock.get('value', 'N/A')
            print(f"- {symbol}: Current Price = ${price}, Total Value = ${value}")
    
    # Test background update function
    print("\nTesting background update function:")
    update_portfolio_in_background(username)
    print("Background update initiated.")
    print("Waiting 3 seconds for background thread to complete...")
    time.sleep(3)
    
    # Check if portfolio was updated again
    portfolio = read_json(portfolio_path)
    if portfolio:
        print("\nPortfolio after background update:")
        for stock in portfolio:
            symbol = stock.get('stock_code', 'Unknown')
            price = stock.get('current_price', 'N/A')
            last_updated = stock.get('last_updated', 'Unknown')
            print(f"- {symbol}: Current Price = ${price}, Last Updated = {last_updated}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_update_functionality()
