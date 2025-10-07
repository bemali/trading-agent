import yfinance as yf
from datetime import datetime
from pathlib import Path
from app.utils.storage import user_dir, read_json, write_json_with_lock

def get_current_price(symbol: str) -> float:
    """
    Get the current price of a stock by its symbol using yfinance.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        Current price as float or None if symbol not found
    """
    try:
        # Get ticker information
        ticker = yf.Ticker(symbol)
        
        # Get the latest price data
        # Using history with period='1d' to get the most recent day's data
        data = ticker.history(period='1d')
        
        # If data is empty, return None
        if data.empty:
            return None
            
        # Return the latest close price
        return round(data['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def update_portfolio_prices(username: str) -> bool:
    """
    Update the portfolio of a user with current prices and calculated values.
    
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
            if current_price is None:
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
        return True
    except Exception as e:
        print(f"Error updating portfolio for {username}: {e}")
        return False
