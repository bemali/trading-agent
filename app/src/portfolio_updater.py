"""
Background portfolio updater module for the trading agent platform.
This module handles updating stock prices when a user profile is loaded.
"""

import yfinance as yf
from datetime import datetime
from pathlib import Path
import threading

from app.utils.storage import user_dir, read_json, write_json_with_lock
from app.utils.finance import get_current_price

def update_portfolio_in_background(username: str) -> None:
    """
    Start a background thread to update portfolio prices without blocking UI.
    
    Args:
        username: Username whose portfolio to update
    """
    thread = threading.Thread(
        target=update_portfolio_with_fallbacks,
        args=(username,),
        daemon=True  # Make thread a daemon so it doesn't block app exit
    )
    thread.start()

def update_portfolio_with_fallbacks(username: str) -> bool:
    """
    Update the portfolio of a user with current prices and calculated values,
    with proper fallbacks when prices can't be fetched.
    
    Args:
        username: Username whose portfolio to update
        
    Returns:
        True if update was successful, False otherwise
    """
    try:
        # Get user portfolio file path
        portfolio_path = user_dir(username) / "portfolio.json"
        
        # Read current portfolio data
        portfolio = read_json(portfolio_path)
        if not portfolio:
            print(f"No portfolio found for {username}")
            return False
        
        # Current timestamp for update
        timestamp = datetime.now().isoformat()
        
        # Update each stock in portfolio
        for stock in portfolio:
            symbol = stock.get('stock_code')
            if not symbol:
                continue
                
            # Get current price
            current_price = get_current_price(symbol)
            
            # Apply fallbacks if current price can't be fetched:
            # 1. Use existing current_price if available
            # 2. Use purchase_price if no current_price exists
            if current_price is None:
                if 'current_price' in stock and stock['current_price'] is not None:
                    # Use existing price as fallback
                    current_price = stock['current_price']
                    print(f"Using existing price for {symbol}: ${current_price}")
                else:
                    # Use purchase price as fallback if no current price exists
                    current_price = stock.get('purchase_price')
                    print(f"Using purchase price for {symbol}: ${current_price}")
            
            # Skip if we still don't have a valid price
            if current_price is None:
                print(f"No valid price found for {symbol}, skipping")
                continue
                
            # Update stock information
            stock['current_price'] = current_price
            stock['last_updated'] = timestamp
            
            # Calculate value (quantity * current_price)
            quantity = stock.get('quantity', 0)
            stock['value'] = round(quantity * current_price, 2)
            
            # Calculate returns
            purchase_price = stock.get('purchase_price', 0)
            if purchase_price > 0:
                # Total return (current value - purchase value)
                stock['total_return'] = round(stock['value'] - (quantity * purchase_price), 2)
                
                # Percent return ((current - purchase) / purchase * 100)
                stock['percent_return'] = round((current_price - purchase_price) / purchase_price * 100, 2)
        
        # Save updated portfolio
        write_json_with_lock(portfolio_path, portfolio)
        print(f"Portfolio updated successfully for {username}")
        return True
    except Exception as e:
        print(f"Error updating portfolio for {username}: {e}")
        return False
