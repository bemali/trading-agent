"""
News utility for generating and retrieving news related to stocks.
Uses news_agent.py to fetch real news when available, with static fallback data.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from agents.news_agent import run_workflow

# Sample news headlines and snippets for different stock sectors
TECH_NEWS = [
    {"headline": "New Innovation Breakthrough", "snippet": "Company announces revolutionary technology that could disrupt the market."},
    {"headline": "Strong Quarterly Earnings", "snippet": "Tech giant exceeds expectations with latest financial results."},
    {"headline": "Product Launch Success", "snippet": "Latest product release sees record-breaking adoption rates."},
    {"headline": "Strategic Acquisition", "snippet": "Company acquires promising startup to expand its technological capabilities."},
    {"headline": "R&D Investment", "snippet": "Major investment in research and development signals future growth."}
]

FINANCE_NEWS = [
    {"headline": "Market Rally Continues", "snippet": "Financial institution benefits from ongoing market strength."},
    {"headline": "Interest Rate Impact", "snippet": "Central bank decisions create new opportunities for banking sector."},
    {"headline": "Regulatory Changes", "snippet": "New financial regulations could reshape competitive landscape."},
    {"headline": "Digital Banking Growth", "snippet": "Online services show record engagement as traditional banking evolves."},
    {"headline": "Economic Forecast", "snippet": "Analysts predict strong performance in financial sector."}
]

GENERAL_NEWS = [
    {"headline": "Industry Trends", "snippet": "Company positioned well for emerging market trends."},
    {"headline": "Executive Changes", "snippet": "New leadership appointment could signal strategic shift."},
    {"headline": "Market Share Gains", "snippet": "Company reports increased market share in key segments."},
    {"headline": "Global Expansion", "snippet": "International growth initiatives show promising early results."},
    {"headline": "Analyst Recommendations", "snippet": "Major analysts upgrade outlook citing strong fundamentals."}
]

# Map stock symbols to appropriate news categories
STOCK_CATEGORIES = {
    # Tech companies
    "AAPL": TECH_NEWS,
    "MSFT": TECH_NEWS,
    "GOOGL": TECH_NEWS,
    "META": TECH_NEWS,
    "AMZN": TECH_NEWS,
    "NVDA": TECH_NEWS,
    "AMD": TECH_NEWS,
    
    # Financial companies
    "JPM": FINANCE_NEWS,
    "BAC": FINANCE_NEWS,
    "GS": FINANCE_NEWS,
    "MS": FINANCE_NEWS,
    "C": FINANCE_NEWS,
    
    # Default for any other symbol
    "DEFAULT": GENERAL_NEWS
}

def get_news_for_stock(symbol: str, count: int = 3) -> List[Dict[str, Any]]:
    """
    Get news articles for a specific stock symbol using news_agent.py.
    Falls back to static sample data if the agent fails.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        count: Number of news items to return
        
    Returns:
        List of news items with headlines, snippets, and dates
    """
    try:
        # Attempt to get real news using news_agent
        agent_result = run_workflow(symbol)
        
        if agent_result and "final_verdict" in agent_result and agent_result["final_verdict"]:
            # Process agent result
            now = datetime.now()
            formatted_date = now.strftime("%b %d, %Y at %I:%M %p")
            
            # Create a news item from the agent result
            result = [{
                "headline": f"Latest {symbol} Analysis",
                "snippet": agent_result["final_verdict"],
                "date": formatted_date,
                "source": "Trading Agent News Analysis",
                "symbol": symbol
            }]
            
            # If URLs are available in the agent result, add them
            if "urls" in agent_result and agent_result["urls"]:
                for i, url in enumerate(agent_result["urls"][:min(count-1, len(agent_result["urls"]))]):
                    result.append({
                        "headline": f"Additional Source {i+1}",
                        "snippet": f"Reference link: {url}",
                        "date": formatted_date,
                        "source": "Reference",
                        "symbol": symbol
                    })
            
            return result
    except Exception as e:
        print(f"Error getting news from agent: {e}")
        # Fall back to static news data
    
    # Fallback: Use static news data
    news_category = STOCK_CATEGORIES.get(symbol, STOCK_CATEGORIES["DEFAULT"])
    news_items = random.sample(news_category, min(count, len(news_category)))
    
    now = datetime.now()
    result = []
    for item in news_items:
        # Random date within the past week
        days_ago = random.randint(0, 6)  # 0 to 6 days ago
        hours_ago = random.randint(0, 23)  # 0 to 23 hours ago
        news_date = now - timedelta(days=days_ago, hours=hours_ago)
        
        # Format the date
        formatted_date = news_date.strftime("%b %d, %Y at %I:%M %p")
        
        # Add source
        sources = ["Market Watch", "Financial Times", "Bloomberg", "CNBC", "Reuters"]
        source = random.choice(sources)
        
        result.append({
            "headline": item["headline"],
            "snippet": item["snippet"],
            "date": formatted_date,
            "source": source,
            "symbol": symbol
        })
    
    return result
