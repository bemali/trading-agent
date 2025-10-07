"""
Test module for the news utility.
"""
import sys
import os
import unittest
from app.utils.news import get_news_for_stock

class NewsTest(unittest.TestCase):
    """Test case for news utility functions."""
    
    def test_get_news_for_stock_with_agent(self):
        """Test getting news for a stock symbol using the news agent."""
        # Test with a tech company symbol
        news_items = get_news_for_stock("AAPL", count=2)
        
        # Verify we got some news items
        self.assertIsNotNone(news_items)
        self.assertGreater(len(news_items), 0)
        
        # Verify the structure of the first news item
        first_item = news_items[0]
        self.assertIn("headline", first_item)
        self.assertIn("snippet", first_item)
        self.assertIn("date", first_item)
        self.assertIn("source", first_item)
        self.assertIn("symbol", first_item)
        
        # Verify the symbol is correctly set
        self.assertEqual(first_item["symbol"], "AAPL")
        
        # Test with a finance company symbol
        news_items = get_news_for_stock("JPM", count=1)
        self.assertIsNotNone(news_items)
        self.assertGreater(len(news_items), 0)
        self.assertEqual(news_items[0]["symbol"], "JPM")

if __name__ == "__main__":
    unittest.main()
